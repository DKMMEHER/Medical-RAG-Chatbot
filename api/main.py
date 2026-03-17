from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config.settings import settings
from src.auth.firebase_auth import init_firebase, verify_token
from src.storage.gcs_handler import GCSHandler
from src.content_analyzer.output_guardrails import OutputGuardrails
from src.content_analyzer.validator import ContentValidator
from src.content_analyzer.config import ValidationConfig
from src.model.llm_factory import create_llm
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.utils.logger import get_logger
from api.models.schemas import HealthStatus, ReadyResponse
import os

logger = get_logger(__name__, log_to_file=True)

# Global state
state = {
    "tasks": {},  # Stores background task status
    "tenant_data": {},  # Stores {tenant_id: {"vectorstore": FAISS, "bm25_retriever": BM25}}
    "user_rate_limits": {},  # Stores {user_email: {"rate_limit_data": ...}}
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("🚀 Starting FastAPI backend...")

    # 0. LangSmith Tracing
    from src.observability import configure_langsmith

    configure_langsmith()

    # 1. Firebase
    try:
        init_firebase()
        logger.info("🔥 Firebase initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")

    # 2. Models (Embeddings FIRST, then LLM)
    try:
        # Initialize Embeddings (required by vectorstore)
        embedding_model_name = (
            settings.embedding_model
            if settings
            else "sentence-transformers/all-MiniLM-L6-v2"
        )
        state["embeddings"] = HuggingFaceEmbeddings(model_name=embedding_model_name)
        logger.info(f"🧬 Embeddings initialized: {embedding_model_name}")

        # Initialize LLM (Use the key 'groq', not 'llama-3.1-8b-instant')
        active_llm_key = (
            settings.config.get("active_llm", "groq") if settings else "groq"
        )
        state["llm"] = create_llm(active_llm_key)
        logger.info(f"🤖 LLM initialized using key: {active_llm_key}")

        # Initialize Cross-Encoder for re-ranking
        from sentence_transformers import CrossEncoder
        from src.rag.engine import RERANK_MODEL

        state["cross_encoder"] = CrossEncoder(RERANK_MODEL)
        logger.info(f"🎯 Cross-Encoder re-ranker initialized: {RERANK_MODEL}")
    except Exception as e:
        logger.error(f"Failed to initialize Models: {e}")
        state.setdefault("cross_encoder", None)  # Graceful fallback — no re-ranking

    # 3. Vectorstore
    try:
        gcs_instance = GCSHandler(
            bucket_name=settings.gcs_bucket_name if settings else None,
            index_prefix=settings.gcs_index_prefix if settings else "faiss-index",
        )
        state["gcs_handler"] = gcs_instance

        db_path = settings.vectorstore_path if settings else "vectorstore/db_faiss"

        # Ensure embeddings exist before loading
        if "embeddings" not in state:
            logger.error("❌ Cannot load Vectorstore: Embeddings not initialized")
        else:
            if gcs_instance.gcs_enabled:
                logger.info(f"☁️ Syncing Vectorstore from GCS to {db_path}...")
                success = gcs_instance.download_faiss_index(db_path)
                if success:
                    state["vectorstore"] = FAISS.load_local(
                        db_path,
                        state["embeddings"],
                        allow_dangerous_deserialization=True,
                    )
                    logger.info("✅ Vectorstore synced and loaded from GCS")
                else:
                    logger.info(
                        "ℹ️ GCS index not found or download failed, checking local..."
                    )

            if "vectorstore" not in state and os.path.exists(db_path):
                state["vectorstore"] = FAISS.load_local(
                    db_path, state["embeddings"], allow_dangerous_deserialization=True
                )
                logger.info("📂 Vectorstore loaded from local storage")

        if "vectorstore" not in state:
            logger.warning(
                "⚠️ No Vectorstore found. Root functionality will be limited."
            )
        else:
            # Build BM25 retriever from loaded vectorstore docs
            from src.rag.engine import build_bm25_retriever

            state["bm25_retriever"] = build_bm25_retriever(state["vectorstore"])
            logger.info("🔍 BM25 retriever built from vectorstore docs")
    except Exception as e:
        logger.error(f"Failed to load Vectorstore: {e}")

    # 4. Security & Guardrails
    state["guardrails"] = OutputGuardrails(
        enable_pii_check=True,
        enable_toxic_check=True,
        enable_hallucination_check=True,
        require_medical_disclaimer=True,
        block_on_pii=True,
        block_on_toxic=True,
    )
    state["input_validator"] = ContentValidator(
        ValidationConfig(enable_prompt_injection_detection=True)
    )
    logger.info("🛡️ Security Layer initialized")

    yield
    # --- Shutdown ---
    logger.info("🛑 Shutting down FastAPI backend...")


async def get_tenant_data(tenant_id: str):
    """
    Lazy-loads or returns cached vectorstore/retriever for a specific tenant.
    """
    if tenant_id in state["tenant_data"]:
        return state["tenant_data"][tenant_id]

    logger.info(f"🏢 Loading data for tenant: {tenant_id}")

    # Check if embeddings are ready
    if "embeddings" not in state:
        logger.error("❌ Cannot load Tenant Vectorstore: Embeddings not initialized")
        return None

    try:
        from src.rag.engine import build_bm25_retriever

        # Initialize GCS handler for this specific tenant
        gcs = GCSHandler(
            bucket_name=settings.gcs_bucket_name if settings else None,
            index_prefix=settings.gcs_index_prefix if settings else "faiss-index",
            tenant_id=tenant_id,
        )

        db_path = os.path.join(settings.vectorstore_path, "tenants", tenant_id)

        vectorstore = None
        if gcs.gcs_enabled:
            logger.info(
                f"☁️ Syncing Tenant Vectorstore ({tenant_id}) from GCS to {db_path}..."
            )
            success = gcs.download_faiss_index(db_path)
            if success:
                vectorstore = FAISS.load_local(
                    db_path, state["embeddings"], allow_dangerous_deserialization=True
                )
                logger.info(f"✅ Tenant Vectorstore ({tenant_id}) loaded from GCS")

        if not vectorstore and os.path.exists(db_path):
            vectorstore = FAISS.load_local(
                db_path, state["embeddings"], allow_dangerous_deserialization=True
            )
            logger.info(
                f"📂 Tenant Vectorstore ({tenant_id}) loaded from local storage"
            )

        if vectorstore:
            bm25 = build_bm25_retriever(vectorstore)
            state["tenant_data"][tenant_id] = {
                "vectorstore": vectorstore,
                "bm25_retriever": bm25,
            }
            return state["tenant_data"][tenant_id]

        # --- Fallback to Global (Original) Index ---
        logger.info(
            "🌐 Tenant index missing. Attempting fallback to Global Knowledge Base..."
        )
        gcs_global = GCSHandler(
            bucket_name=settings.gcs_bucket_name if settings else None,
            index_prefix=settings.gcs_index_prefix if settings else "faiss-index",
            tenant_id=None,  # No tenant prefix for global
        )
        global_db_path = (
            settings.vectorstore_path if settings else "vectorstore/db_faiss"
        )

        global_vectorstore = None
        if gcs_global.gcs_enabled:
            success = gcs_global.download_faiss_index(global_db_path)
            if success:
                global_vectorstore = FAISS.load_local(
                    global_db_path,
                    state["embeddings"],
                    allow_dangerous_deserialization=True,
                )

        if not global_vectorstore and os.path.exists(global_db_path):
            global_vectorstore = FAISS.load_local(
                global_db_path,
                state["embeddings"],
                allow_dangerous_deserialization=True,
            )

        if global_vectorstore:
            logger.info(f"✅ Loaded Global Knowledge Base as fallback for {tenant_id}")
            bm25_global = build_bm25_retriever(global_vectorstore)
            return {"vectorstore": global_vectorstore, "bm25_retriever": bm25_global}

        logger.warning(f"⚠️ No Vectorstore (Tenant or Global) found for: {tenant_id}")
        return None

    except Exception as e:
        logger.error(f"Failed to load vectorstore for tenant {tenant_id}: {e}")
        return None


app = FastAPI(title="Medical Chatbot API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Streamlit's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


async def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)):
    """Verifies the Firebase ID Token passed in the Authorization header."""
    try:
        user_info = verify_token(auth.credentials)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Medical Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthStatus)
async def health():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "components": {
            "firebase": "connected",
            "llm": "ready" if "llm" in state else "error",
            "vectorstore": "ready" if "vectorstore" in state else "missing",
        },
    }


@app.get("/stats")
async def stats(user=Depends(get_current_user)):
    return {
        "user": user["email"],
        "is_admin": user["is_admin"],
        "index_size": state["vectorstore"].index.ntotal
        if "vectorstore" in state
        else 0,
    }


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "version": "1.0.0", "components": {"api": "up"}}


@app.get("/ready", response_model=ReadyResponse)
async def readiness_check():
    """Deep readiness probe checking core components."""
    checks = {
        "firebase": False,
        "llm": False,
        "embeddings": "embeddings" in state,
        "vectorstore": "vectorstore" in state,
    }

    # 1. Firebase check (simple check if initialized)
    try:
        from firebase_admin import get_app

        get_app()
        checks["firebase"] = True
    except:
        pass

    # 2. LLM check
    if "llm" in state and state["llm"] is not None:
        checks["llm"] = True

    is_ready = all(checks.values())

    if not is_ready:
        missing = [k for k, v in checks.items() if not v]
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "is_ready": False,
                "components": checks,
                "message": f"Waiting for components: {', '.join(missing)}",
            },
        )

    return {"status": "ready", "is_ready": True, "components": checks}


# Import routes here to avoid circular imports if needed
from api.routes import chat, upload

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
