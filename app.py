import os
import time
from pathlib import Path
import streamlit as st


import requests
import httpx
import json
from dotenv import load_dotenv, find_dotenv
from src.auth.firebase_auth import init_firebase, sign_in, verify_token
from src.utils.tenant_helper import extract_tenant_id

# Load environment variables — searches current dir and all parent dirs for .env
load_dotenv(find_dotenv(usecwd=True), override=True)

# Import from src structure
from src.utils.logger import get_logger
from src.utils.exceptions import LLMError
from src.config.settings import settings
from src.utils.ui_helpers import display_error_message

# Import observability modules
from src.observability import (
    configure_langsmith,
    is_langsmith_enabled,
)

try:
    from langsmith import traceable as ls_traceable
except ImportError:
    # Fallback: no-op decorator if langsmith not installed
    def ls_traceable(**kwargs):
        def decorator(func):
            return func

        return decorator


# Initialize logger
logger = get_logger(__name__, log_to_file=True)

# API Configuration
# Use 127.0.0.1 instead of localhost to avoid IPv6 issues on some Windows setups
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
HEALTH_URL = f"{os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')}/health"


@st.cache_resource
def init_globals():
    """Check API connectivity and initialize front-end observability."""
    # Configure LangSmith observability (optional for UI side)
    configure_langsmith(project_name="medical-chatbot", enable_tracing=True)

    # Check API health with retries to account for slow backend startup (GCS sync, model loading)
    max_retries = 15
    retry_delay = 3
    connected = False

    with st.status("🔌 Connecting to backend...", expanded=True) as status:
        for i in range(max_retries):
            try:
                response = requests.get(HEALTH_URL, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Connected to FastAPI backend")
                    status.update(
                        label="✅ Connected to medical-chatbot API", state="complete"
                    )
                    connected = True
                    break
                else:
                    status.write(
                        f"⚠️ Backend status {response.status_code}, retrying {i + 1}/{max_retries}..."
                    )
            except requests.exceptions.ConnectionError:
                if i < max_retries - 1:
                    status.write(
                        f"⏳ Waiting for backend to start... ({i + 1}/{max_retries})"
                    )
                    time.sleep(retry_delay)
                else:
                    status.update(
                        label="❌ Connection failed after multiple retries",
                        state="error",
                    )
            except Exception as e:
                status.update(label=f"❌ Unexpected error: {e}", state="error")
                break

    if not connected:
        st.error(
            "🔌 **Backend Connection Error**: The medical chatbot API is not responding. Please ensure the uvicorn server is running."
        )
        st.stop()


@st.cache_resource
def get_validator():
    """Cache the content validator to avoid re-initializing on every rerun."""
    from src.content_analyzer.validator import ContentValidator
    from src.content_analyzer.config import ValidationConfig

    return ContentValidator(ValidationConfig(enable_prompt_injection_detection=True))


# Constants
MAX_QUERY_LENGTH = 1000


# Configuration from settings
DB_FAISS_PATH = settings.vectorstore_path if settings else "vectorstore/db_faiss"
DEFAULT_MODEL = settings.default_llm_model if settings else "llama-3.1-8b-instant"
DEFAULT_EMBEDDING_MODEL = (
    settings.embedding_model if settings else "sentence-transformers/all-MiniLM-L6-v2"
)
MAX_RETRIES = settings.max_retries if settings else 3
MAX_QUERY_LENGTH = 1000


@st.cache_data
def get_rag_prompt() -> str:
    """Load the prompt template."""
    prompt_path = Path("src/prompts/medical_assistant.txt")
    if not prompt_path.exists():
        logger.error(f"Prompt template not found at {prompt_path}")
        return "Answer the following medical questions using the context provided.\nContext: {context}\nQuestion: {question}"

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()
    return prompt_content


def call_rag_api(query: str, history: list, id_token: str):
    """Call the FastAPI backend for streaming RAG response."""
    with httpx.stream(
        "POST",
        f"{API_BASE_URL}/query",
        json={"query": query, "history": history},
        headers={"Authorization": f"Bearer {id_token}"},
        timeout=None,
    ) as response:
        if response.status_code != 200:
            error_detail = response.read().decode()
            try:
                msg = json.loads(error_detail).get("detail", error_detail)
            except:
                msg = error_detail
            raise LLMError(f"API Error: {msg}")

        for chunk in response.iter_text():
            if chunk:
                if chunk.startswith("[METADATA]:"):
                    try:
                        meta_str = chunk.replace("[METADATA]:", "").strip()
                        metadata = json.loads(meta_str)
                        st.session_state["last_run_id"] = metadata.get("run_id")
                        continue  # Skip to next chunk (the actual text)
                    except:
                        pass

                if chunk.startswith("[SOURCES]:"):
                    try:
                        sources_str = chunk.replace("[SOURCES]:", "").strip()
                        st.session_state["last_sources"] = json.loads(sources_str)
                        continue  # Skip to next chunk
                    except:
                        pass

                yield chunk


def rebuild_vectorstore_via_api(pdf_files: list, id_token: str) -> tuple:
    """Send PDFs to API for remote indexing and poll for status."""
    files = []
    for pdf in pdf_files:
        files.append(("files", (pdf["name"], pdf["bytes"], "application/pdf")))

    try:
        # 1. Start the task
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=30,
        )

        if response.status_code != 200:
            return False, f"Upload failed ({response.status_code}): {response.text}"

        res_json = response.json()
        task_id = res_json.get("task_id")

        if not task_id:
            return True, res_json.get("message", "Success (but no task ID returned)")

        # 2. Polling loop
        status_container = st.empty()
        while True:
            status_response = requests.get(
                f"{API_BASE_URL}/upload/status/{task_id}",
                headers={"Authorization": f"Bearer {id_token}"},
                timeout=10,
            )

            if status_response.status_code != 200:
                return False, f"Status check failed: {status_response.text}"

            status_data = status_response.json()
            status = status_data["status"]
            message = status_data.get("message", "Processing...")

            if status == "completed":
                status_container.success(f"✅ {message}")
                return True, message
            elif status == "failed":
                status_container.error(f"❌ {message}")
                return False, message
            else:
                status_container.info(f"⏳ {message}")
                time.sleep(2)  # Poll every 2 seconds

    except Exception as e:
        return False, f"Async processing failed: {str(e)}"


def render_admin_dashboard():
    """Display analytics visualizations for admins."""
    from src.utils.analytics import analytics_manager
    import pandas as pd

    st.header("📊 Usage Analytics Dashboard")
    st.markdown("---")

    with st.spinner("Fetching data..."):
        # This will fetch both GCS and local fallback logs
        events = analytics_manager.get_all_events()

    if not events:
        st.warning("No analytics data found yet. Start chatting to generate logs!")
        return

    df = pd.DataFrame(events)
    # Convert timestamp string to datetime objects for plotting
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ── Key Metrics ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Queries", len(df))
    with col2:
        avg_time = df["response_time_sec"].mean()
        st.metric("Avg Response Time", f"{avg_time:.2f}s")
    with col3:
        error_count = df["is_error"].sum()
        error_rate = (error_count / len(df)) * 100
        st.metric("Error Rate", f"{error_rate:.1f}%")
    with col4:
        total_tokens = int(df["token_count"].sum())
        st.metric("Total Tokens", f"{total_tokens:,}")

    st.divider()

    # ── Timeline View ────────────────────────────────────────────────────────
    st.subheader("📈 Activity Timeline")
    # Resample to hourly buckets
    try:
        df_timeline = (
            df.set_index("timestamp").resample("H").size().reset_index(name="Queries")
        )
        st.bar_chart(df_timeline, x="timestamp", y="Queries", use_container_width=True)
    except Exception:
        st.info("Not enough data points for a timeline yet.")

    # ── Popular Topics & Sources ─────────────────────────────────────────────
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🔍 Common Terms")
        # Very basic keyword count
        stop_words = {
            "what",
            "is",
            "the",
            "how",
            "to",
            "for",
            "of",
            "and",
            "a",
            "in",
            "with",
            "my",
        }
        words = []
        for q in df["query"]:
            words.extend(
                [w.lower().strip("?") for w in q.split() if w.lower() not in stop_words]
            )
        if words:
            word_counts = pd.Series(words).value_counts().head(10).reset_index()
            word_counts.columns = ["Topic", "Count"]
            st.dataframe(word_counts, hide_index=True, use_container_width=True)
        else:
            st.caption("No keywords extracted.")

    with right_col:
        st.subheader("📄 Top Sources")
        all_sources = []
        for s_list in df.get("sources", []):
            if isinstance(s_list, list):
                all_sources.extend(s_list)
        if all_sources:
            source_counts = pd.Series(all_sources).value_counts().head(10).reset_index()
            source_counts.columns = ["Document", "Citations"]
            st.dataframe(source_counts, hide_index=True, use_container_width=True)
        else:
            st.caption("No sources cited yet.")

    # ── Raw Data ─────────────────────────────────────────────────────────────
    st.divider()
    with st.expander("📝 View Raw Logs"):
        st.dataframe(
            df.sort_values("timestamp", ascending=False), use_container_width=True
        )


def main():
    """Main application function with comprehensive error handling"""

    # Page configuration
    st.set_page_config(page_title="Medical Chatbot", page_icon="🏥", layout="centered")

    # Initialize global singletons once per server process
    init_globals()
    input_validator = get_validator()

    # --- Firebase Authentication ---
    try:
        init_firebase()
    except EnvironmentError as e:
        st.error(f"Firebase configuration error: {e}")
        st.stop()

    # If not logged in yet, show login form
    if not st.session_state.get("id_token"):
        st.title("🏥 Medical Chatbot")
        st.subheader("🔐 Please sign in to continue")
        with st.form("login_form"):
            email = st.text_input("📧 Email address")
            password = st.text_input("🔒 Password", type="password")
            submitted = st.form_submit_button("➡️ Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Please enter both email and password.")
                st.stop()
            try:
                creds = sign_in(email, password)
                user_info = verify_token(creds["id_token"])
                st.session_state["id_token"] = creds["id_token"]
                st.session_state["user_email"] = user_info["email"]
                st.session_state["is_admin"] = user_info["is_admin"]
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        st.stop()
    # --------------------------------

    # --- Navigation ---
    app_mode = "💬 Chat"
    if st.session_state.get("is_admin"):
        with st.sidebar:
            st.subheader("🕹️ Admin Console")
            app_mode = st.radio(
                "Navigation", ["💬 Chat", "📊 Admin Dashboard"], key="nav_radio"
            )
            st.divider()

    if app_mode == "📊 Admin Dashboard":
        st.title("🛡️ Admin Console")
        render_admin_dashboard()
        # Sidebar with info (still show logout etc)
        with st.sidebar:
            render_sidebar_info()
        return

    st.title("🏥 Medical Chatbot")
    st.markdown("*Ask me anything about medical topics from the knowledge base*")

    # Initialize session state (Thin Client)
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.info("Initialized new thin-client chat session")

    # Thin clients don't need local LLM/Vectorstore initialization
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        logger.info("Thin client initialized")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available for assistant messages
            if (
                message["role"] == "assistant"
                and "sources" in message
                and message["sources"]
            ):
                with st.expander("📚 View Sources"):
                    for src in message["sources"]:
                        st.markdown(f"- 📄 **{src['file']}** (Page {src['page']})")

    # Chat input — check for retry first, then new input
    retry_query = st.session_state.pop("retry_query", None)
    user_query = retry_query or st.chat_input("💬 Ask your medical question here...")
    if user_query:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)

        # 🛡️ INPUT VALIDATION 🛡️
        if len(user_query) > MAX_QUERY_LENGTH:
            st.warning(
                f"⚠️ **Query too long**: Please keep your question under {MAX_QUERY_LENGTH} characters."
            )
            st.stop()

        is_safe, issues = input_validator.validate(user_query)
        if not is_safe:
            # Display warning and stop
            with st.chat_message("assistant"):
                st.warning(
                    "⚠️ **Security Warning**: Your query was flagged for potentially unsafe content (PII, Toxic language, or Prompt Injection)."
                )
                for issue in issues:
                    st.caption(f"- {issue.description}")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_query})

        # Process query and generate response (Via API)
        try:
            start_time = time.time()
            with st.chat_message("assistant"):
                # Convert session history to API message format
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]  # Exclude latest
                ]

                # Call streaming API
                st.session_state["last_sources"] = []
                answer_placeholder = st.empty()
                full_response = st.write_stream(
                    call_rag_api(user_query, history, st.session_state.id_token)
                )
                answer = full_response

                # Show sources immediately after streaming
                current_sources = st.session_state.get("last_sources", [])
                if current_sources:
                    with st.expander("📚 View Sources"):
                        for src in current_sources:
                            st.markdown(f"- 📄 **{src['file']}** (Page {src['page']})")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": st.session_state.get("last_sources", []),
                }
            )
            elapsed = round(time.time() - start_time, 1)
            st.caption(f"⏱️ Response generated via API in {elapsed}s")

            # 📝 FB FEEDBACK 📝
            if st.session_state.get("last_run_id"):
                feedback = st.feedback(
                    "thumbs", key=f"fb_{st.session_state.last_run_id}"
                )
                if feedback is not None:
                    score = 1.0 if feedback == 1 else 0.0
                    try:
                        f_res = requests.post(
                            f"{API_BASE_URL}/feedback",
                            json={
                                "run_id": st.session_state.last_run_id,
                                "score": score,
                            },
                            headers={
                                "Authorization": f"Bearer {st.session_state.id_token}"
                            },
                            timeout=5,
                        )
                        if f_res.status_code == 200:
                            st.toast("✅ Feedback recorded in LangSmith!")
                    except:
                        pass

            logger.info(f"Query processed successfully in {elapsed}s")

        except LLMError as e:
            error_info = display_error_message(e, "LLMError")
            with st.chat_message("assistant"):
                st.warning(f"⚠️ {error_info['suggestion']}")
                if st.button("🔄 Retry", key=f"retry_{len(st.session_state.messages)}"):
                    st.session_state.retry_query = user_query
                    st.rerun()
        except Exception as e:
            error_info = display_error_message(e, "default")
            with st.chat_message("assistant"):
                st.warning(f"⚠️ {error_info['suggestion']}")
                if st.button("🔄 Retry", key=f"retry_{len(st.session_state.messages)}"):
                    st.session_state.retry_query = user_query
                    st.rerun()

        st.session_state.messages.append({"role": "user", "content": user_query})

    # Sidebar with info
    render_sidebar_info()


def render_sidebar_info():
    """Renders the common sidebar information and logout button."""
    with st.sidebar:
        # Auth info & Logout
        user_email = st.session_state.get("user_email", "")
        # Extract and format org name
        tenant_id = extract_tenant_id(user_email)
        org_name = tenant_id.replace("-", " ").title()

        st.markdown(f"👤 **{user_email}**")
        st.markdown(f"🏢 **Org: {org_name}**")
        if st.session_state.get("is_admin", False):
            st.caption("🛡️ Admin User")
        else:
            st.caption("👥 Standard User")
        if st.button("🚪 Logout", use_container_width=True):
            for key in [
                "id_token",
                "user_email",
                "is_admin",
                "messages",
                "initialized",
                "vectorstore",
                "llm",
                "config",
                "rate_limit_data",
            ]:
                st.session_state.pop(key, None)
            st.rerun()
        st.divider()

        st.subheader("📊 Usage")
        st.info("Quota is managed per user by the backend API.")

        st.header("ℹ️ About")

        # Dynamically show active LLM info from settings
        active_llm_name = "Unknown"
        active_provider = "Unknown"
        if settings and settings.config:
            _active = settings.config.get("active_llm", "groq")
            _llm_cfg = settings.config.get("llms", {}).get(_active, {})
            active_llm_name = _active.upper()
            active_provider = _llm_cfg.get("provider", _active).capitalize()

        st.markdown(f"""
        This chatbot uses:
        - 🧠 RAG (Retrieval-Augmented Generation)
        - 📚 FAISS Vector Database
        - 🤖 **{active_llm_name}** ({active_provider} API)
        - 🔍 Hybrid Search (FAISS + BM25)
        - 🎯 Cross-Encoder Re-ranking
        """)

        # Show observability status
        if is_langsmith_enabled():
            st.success("📊 LangSmith Observability: **Enabled**")
            st.caption("All interactions are being traced for quality monitoring")
        else:
            st.info("📊 LangSmith Observability: **Disabled**")
            st.caption("Set LANGSMITH_API_KEY to enable tracing")

        st.divider()

        # ── Knowledge Base section ──────────────────────────────────────────
        st.header("📚 Knowledge Base")

        # Status info (Simplfied for thin client)
        st.info("💡 Knowledge base is managed by the FastAPI backend.")
        st.caption("Admins can upload new PDFs to update the shared index.")

        st.divider()

        # ── PDF Upload UI ───────────────────────────────────────────────────
        if not st.session_state.get("is_admin", False):
            st.info("🔒 Knowledge Base updates are restricted to administrators.")
            return

        st.subheader("⬆️ Update Knowledge Base")
        st.caption(
            "Upload medical PDFs to add to or rebuild the knowledge base. "
            "Changes take effect immediately after indexing."
        )

        uploaded_files = st.file_uploader(
            "Drop PDF files here",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="pdf_uploader",
        )

        # Cache uploaded file bytes in session state immediately so they
        # survive the Streamlit rerun triggered by the button click.
        # Without this, st.file_uploader data is lost on Cloud Run reruns.
        if uploaded_files:
            st.session_state["cached_pdfs"] = [
                {"name": f.name, "bytes": f.getbuffer().tobytes()}
                for f in uploaded_files
            ]
        elif "cached_pdfs" not in st.session_state:
            st.session_state["cached_pdfs"] = []

        cached = st.session_state.get("cached_pdfs", [])

        if cached:
            st.caption(f"📄 {len(cached)} file(s) selected")
            col_add, col_rebuild = st.columns(2)

            with col_add:
                if st.button(
                    "⚡ Add to Index",
                    help="Merge these PDFs into the existing index",
                    use_container_width=True,
                    key="btn_add_index",
                ):
                    with st.spinner("Embedding and indexing PDFs via API..."):
                        ok, msg = rebuild_vectorstore_via_api(
                            cached, st.session_state.id_token
                        )
                    if ok:
                        st.success(msg)
                        logger.info(msg)
                        st.session_state.pop("cached_pdfs", None)
                        st.rerun()
                    else:
                        st.error(msg)

            with col_rebuild:
                if st.button(
                    "🔄 Rebuild All",
                    help="Delete existing index and rebuild from these PDFs only",
                    use_container_width=True,
                    key="btn_rebuild_index",
                ):
                    st.warning(
                        "Rebuild mode via API will be implemented as 'add' for now."
                    )
                    with st.spinner("Embedding and indexing PDFs via API..."):
                        ok, msg = rebuild_vectorstore_via_api(
                            cached, st.session_state.id_token
                        )
                    if ok:
                        st.success(msg)
                        logger.info(msg)
                        st.session_state.pop("cached_pdfs", None)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.caption("No files selected yet.")

        st.divider()

        st.header("📊 Stats")
        st.metric("Messages", len(st.session_state.messages))

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            logger.info("Chat history cleared")
            st.rerun()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}", exc_info=True)
        st.error("A critical error occurred. Please check the logs.")
