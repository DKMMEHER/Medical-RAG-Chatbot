from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from api.models.schemas import QueryRequest, FeedbackRequest
from api.main import state, get_current_user
from src.utils.chat_helper import format_chat_history
from src.utils.llm_helper import stream_llm_tokens
from src.utils.rate_limiter import RateLimiter
from src.utils.logger import get_logger
import json
import asyncio
import os
import time
from src.utils.analytics import analytics_manager
from datetime import datetime
from src.utils.tenant_helper import extract_tenant_id
from api.main import state, get_current_user, get_tenant_data

router = APIRouter()
logger = get_logger(__name__)

# Initialize rate limiter
rate_limiter = RateLimiter(limit=20, window_minutes=60)

from langsmith import traceable

@traceable(name="generate_chat_stream", tags=["rag", "medical"])
async def generate_chat_stream(query: str, history_str: str, user_email: str):
    """Generator for token streaming with guardrails validation at the end."""
    start_time = time.time()
    token_count = 0
    retrieved_docs = []
    sources = []
    is_error = False

    try:
        llm = state.get("llm")
        guardrails = state.get("guardrails")
        input_validator = state.get("input_validator")
        
        # --- Multi-tenancy ---
        tenant_id = extract_tenant_id(user_email)
        tenant_data = await get_tenant_data(tenant_id)
        
        if tenant_data:
            vectorstore = tenant_data["vectorstore"]
            bm25_retriever = tenant_data["bm25_retriever"]
        else:
            vectorstore = None
            bm25_retriever = None

        # 0. Pass Run ID to frontend for feedback
        from src.observability import get_current_run_id
        run_id = get_current_run_id()
        if run_id:
            yield f"[METADATA]:{json.dumps({'run_id': run_id})}\n"

        if not llm or not vectorstore:
            yield "❌ System not fully initialized. Please ensure the vectorstore and LLM are ready."
            return

        # 1. Input Validation
        is_safe, issues = input_validator.validate(query)
        if not is_safe:
            issue_desc = ", ".join([i.description for i in issues])
            yield f"⚠️ **Unsafe input detected**: {issue_desc}"
            return

        # 2. Retrieval
        from src.rag.engine import prepare_rag_context
        from src.config.settings import settings
        
        prompt_template = settings.prompt_template if settings else ""
        if not prompt_template:
            yield f"❌ **Error**: Prompt template not found."
            return

        formatted_prompt, retrieved_docs = prepare_rag_context(
            query, vectorstore, prompt_template, history_str,
            bm25_retriever=bm25_retriever,   # Hybrid search if available
            cross_encoder=state.get("cross_encoder"),      # Re-ranking if available
        )

        # 2.5 Stream Sources Metadata
        temp_sources = []
        for doc in retrieved_docs:
            source_path = doc.metadata.get("source", "Unknown")
            source_info = {
                "file": os.path.basename(source_path),
                "page": doc.metadata.get("page", 0) + 1  # Convert 0-indexed to 1-indexed
            }
            if source_info not in temp_sources:
                temp_sources.append(source_info)
        
        sources.extend(temp_sources)
        if sources:
            yield f"[SOURCES]:{json.dumps(sources)}\n"

        # 3. Streaming Response
        full_answer = ""
        async for token in stream_llm_tokens_async(llm, formatted_prompt):
            full_answer += token
            token_count += 1
            yield token
            # Tiny sleep to ensure streaming feel
            await asyncio.sleep(0.01)

        # 4. Guardrails (Wait for full answer)
        from src.rag.engine import validate_response
        is_safe_out, final_out = validate_response(
            full_answer, query, retrieved_docs, guardrails
        )
        
        if not is_safe_out:
            yield "\n\n⚠️ **Security Warning**: Output blocked by guardrails."

    except Exception as e:
        logger.error(f"Error in generate_chat_stream: {e}", exc_info=True)
        is_error = True
        yield f"\n\n❌ **System Error**: An unexpected error occurred while generating the response: {str(e)}"
    finally:
        # Log analytics at the end
        duration = time.time() - start_time
        analytics_manager.log_chat_event({
            "timestamp": datetime.now().isoformat(),
            "user_email": user_email,
            "query": query,
            "response_time_sec": round(duration, 2),
            "token_count": token_count,
            "sources": [s["file"] for s in sources],
            "is_error": is_error
        })

async def stream_llm_tokens_async(llm, prompt):
    """Async generator that yields tokens using LangChain's .astream() method."""
    try:
        async for chunk in llm.astream(prompt):
            # LangChain chat models yield AIMessageChunk objects
            if hasattr(chunk, "content"):
                yield chunk.content
            else:
                yield str(chunk)
    except Exception as e:
        logger.error(f"Error in astream: {e}")
        raise

@router.post("/query")
async def query_rag(request: QueryRequest, user=Depends(get_current_user)):
    """Primary endpoint for medical RAG queries with streaming."""
    
    # 1. Rate Limiting (Skip for admins)
    if not user["is_admin"]:
        email = user["email"]
        if "user_rate_limits" not in state:
            state["user_rate_limits"] = {}
        if email not in state["user_rate_limits"]:
            state["user_rate_limits"][email] = {}
            
        rate_store = state["user_rate_limits"][email]
        
        if rate_limiter.is_limited(rate_store):
            _, reset_mins = rate_limiter.get_status(rate_store)
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Try again in {reset_mins} minutes."
            )
        # Increment here
        rate_limiter.increment(rate_store)

    # 2. Format history
    history_str = format_chat_history([m.dict() for m in request.history])
    
    # 3. Stream
    return StreamingResponse(
        generate_chat_stream(request.query, history_str, user["email"]),
        media_type="text/plain"
    )

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, user=Depends(get_current_user)):
    """Capture user feedback and sync with LangSmith."""
    from src.observability import create_feedback
    
    success = create_feedback(
        run_id=request.run_id,
        key="user_feedback",
        score=request.score,
        comment=request.comment
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to log feedback to LangSmith")
        
    return {"success": True, "message": "Feedback recorded"}
