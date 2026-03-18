# 🏥 Medical RAG Chatbot

[![CI - Tests & Coverage](https://github.com/DKMMEHER/Medical-RAG-Chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/DKMMEHER/Medical-RAG-Chatbot/actions/workflows/ci.yml)
[![CD - Cloud Run](https://github.com/DKMMEHER/Medical-RAG-Chatbot/actions/workflows/cd.yml/badge.svg)](https://github.com/DKMMEHER/Medical-RAG-Chatbot/actions/workflows/cd.yml)

A **production-grade, multi-tenant Medical RAG Chatbot** deployed on Google Cloud Run. Organizations upload their own medical PDFs, which are indexed into a private FAISS vector store. Users query those documents in real time using an LLM, with enterprise features including Firebase authentication, RBAC, hybrid search, cross-encoder re-ranking, PII detection, and full CI/CD.

---

## ✨ Features

| Category | Feature |
|---|---|
| 🧠 **RAG Pipeline** | 3-stage: Broad retrieval → Hybrid FAISS+BM25 → CrossEncoder re-ranking |
| 📄 **PDF Ingestion** | Semantic chunking (meaning-based, not fixed-size) via `SemanticChunker` |
| 🔐 **Authentication** | Firebase JWT — email/password login, token verification on every request |
| 👮 **RBAC** | Admin vs Standard user roles via Firebase custom claims |
| 🏢 **Multi-Tenancy** | Isolated vectorstore and GCS storage per organization |
| 🛡️ **Output Safety** | 5-layer guardrails: PII (Regex + NER + Presidio) + Toxic + Hallucination + Disclaimer |
| 📡 **FastAPI Backend** | Async REST API with streaming responses and background task processing |
| ☁️ **Cloud Storage** | FAISS index persisted to Google Cloud Storage — survives container restarts |
| 📊 **Observability** | LangSmith tracing for every query, retrieval, guardrail, and feedback event |
| 📈 **Analytics** | Per-user and per-tenant usage tracking with Admin dashboard |
| ⏱️ **Rate Limiting** | Per-user query rate limits (configurable for standard vs admin roles) |
| 🤖 **Multi-LLM** | Switch between Groq, OpenAI, Gemini, Claude, Mistral, Cohere, Ollama via config |
| 🧬 **Multi-Embedding** | Ensemble embedding strategy (BGE + MiniLM) for improved retrieval |
| 🔁 **CI/CD** | GitHub Actions: Ruff lint + pytest (57% coverage) + auto-deploy to Cloud Run |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLOUD RUN                            │
│                                                             │
│  ┌─────────────────┐        ┌─────────────────────────┐    │
│  │   Streamlit UI  │  HTTP  │    FastAPI Backend       │    │
│  │   (port 8080)   │◄──────►│    (port 8000)           │    │
│  │                 │        │  /api/v1/query  (stream) │    │
│  │  • Login Page   │        │  /api/v1/upload          │    │
│  │  • Chat UI      │        │  /health  /ready         │    │
│  │  • PDF Upload   │        │                          │    │
│  │  • Admin Panel  │        └──────────┬───────────────┘    │
│  └─────────────────┘                   │                    │
└───────────────────────────────────────┼────────────────────┘
                                        │
              ┌─────────────────────────┼──────────────────┐
              │                         │                  │
     ┌────────▼────────┐  ┌────────────▼──────┐  ┌───────▼──────┐
     │  Firebase Auth  │  │   FAISS Vectorstore│  │  LangSmith   │
     │  (JWT tokens,   │  │   (GCS-synced,     │  │  (Tracing,   │
     │  custom claims) │  │   per-tenant)      │  │  Feedback)   │
     └─────────────────┘  └───────────────────┘  └──────────────┘
```

---

## 🧠 RAG Pipeline (3-Stage)

```
User Query
    │
    ▼
[Stage 1] Broad Retrieval (k=20)
    ├── FAISS similarity_search  (dense semantic embeddings)
    └── BM25Retriever            (keyword matches)
    └── EnsembleRetriever        (60% FAISS + 40% BM25)
    │
    ▼
[Stage 2] CrossEncoder Re-ranking (top 5)
    └── cross-encoder/ms-marco-MiniLM-L-6-v2
    │   Reads (query, document) pairs together — much more accurate
    ▼
[Stage 3] Context Assembly → LLM → OutputGuardrails → User
```

---

## 🛡️ Output Guardrails (5 Layers)

Every LLM response passes through validation before being shown to the user:

| Layer | Method | Action |
|-------|--------|--------|
| **PII — Regex** | SSN, email, phone, credit card patterns | Block response |
| **PII — NER** | spaCy named entity detection (persons, orgs) | Block response |
| **PII — Presidio** | Microsoft Presidio ML-based detection | Block response |
| **Toxic Content** | Keyword list + Detoxify ML model | Block response |
| **Hallucination** | Detects overconfident language patterns | Warn (log) |
| **Medical Disclaimer** | Detects medical advice without disclaimer | Auto-inject disclaimer |

---

## 🏢 Multi-Tenancy

Each organization gets completely isolated resources:

- **GCS**: `gs://bucket/tenants/{tenant_id}/faiss-index/`
- **API State**: In-memory `state["tenant_data"][tenant_id]` → `{vectorstore, bm25_retriever}`
- Tenant ID is derived from the user's Firebase organization claim
- No cross-tenant data access is possible

---

## 🔐 Authentication & RBAC

- **Login**: Firebase email/password → returns signed JWT
- **Every API call**: JWT validated by FastAPI's `verify_token()` via Firebase Admin SDK
- **Roles**:
  - `Standard User` — Chat, upload PDFs for their tenant, view own history
  - `Admin` — Admin Dashboard, view all users, promote users, system analytics
- **Promotion**: Run `set_admin_claim.py` once (sets Firebase custom claim `admin: True`)
- **Rate Limiting**: Per-user query limits enforced via `src/utils/rate_limiter.py`

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv) package manager

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
GROQ_API_KEY=your_groq_api_key

# Firebase (required for auth)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Optional: LangSmith observability
LANGSMITH_API_KEY=ls_your_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=medical-chatbot

# Optional: Google Cloud Storage for FAISS persistence
GCS_BUCKET_NAME=your_bucket_name
```

### 3. Build the Vector Store

Place your PDF files in `data/`, then run:

```bash
uv run python create_vectorstore.py
```

### 4. Run Both Services

```bash
# Terminal 1 — FastAPI backend
uv run uvicorn api.main:app --reload --port 8000

# Terminal 2 — Streamlit frontend
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## ⚙️ Configuration

All settings in **`src/config/config.yaml`**.

### Switch LLM Provider

```yaml
active_llm: "groq"  # groq | openai | openai_gpt4 | gemini | claude | mistral | ollama
```

### Supported Providers

| Key | Provider | Model |
|-----|----------|-------|
| `groq` | Groq | llama-3.1-8b-instant |
| `groq_llama_70b` | Groq | llama-3.1-70b-versatile |
| `openai` | OpenAI | gpt-4o-mini |
| `openai_gpt4` | OpenAI | gpt-4o |
| `gemini` | Google | gemini-pro |
| `claude` | Anthropic | claude-3-5-sonnet |
| `mistral` | Mistral AI | mistral-large |
| `cohere` | Cohere | command-r-plus |
| `ollama` | Local | llama3 |

### Embedding Strategy

```yaml
embedding:
  strategy: "ensemble"    # single | ensemble | hybrid
  primary:
    model: "BAAI/bge-base-en-v1.5"
  secondary:
    model: "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🗂️ Project Structure

```
Medical-RAG-Chatbot/
├── app.py                        # Streamlit frontend (Login, Chat, Upload, Admin)
├── create_vectorstore.py         # One-time PDF → FAISS index creation
├── check_admins.py               # Utility: list all Firebase users and roles
├── set_admin_claim.py            # Utility: promote a user to Admin role
├── start.sh                      # Container startup: launches FastAPI then Streamlit
├── Dockerfile                    # Cloud Run container definition
├── data/                         # Place your PDF documents here
├── vectorstore/                  # Generated FAISS vector store (git-ignored)
├── api/
│   ├── main.py                   # FastAPI app: startup, lifespan, health endpoints
│   ├── tasks.py                  # Background PDF processing tasks
│   └── routes/
│       └── chat.py               # /query (streaming), /upload, /feedback
├── src/
│   ├── rag/
│   │   └── engine.py             # RAG core: hybrid retrieval, re-ranking, guardrails
│   ├── auth/
│   │   └── firebase_auth.py      # Firebase JWT init, verify_token, sign_in
│   ├── content_analyzer/
│   │   ├── output_guardrails.py  # 5-layer LLM output safety validation
│   │   ├── pii_detector.py       # Regex-based PII detection
│   │   ├── pii_detector_presidio.py  # Presidio ML PII detection
│   │   ├── toxic_detector.py     # Keyword toxic content filter
│   │   ├── toxic_detector_ml.py  # Detoxify ML toxic detection
│   │   ├── ner_detector.py       # spaCy NER entity detection
│   │   ├── validator.py          # Input validation (prompt injection, length)
│   │   └── config.py             # ValidationConfig, ValidationIssue dataclasses
│   ├── model/
│   │   └── llm_factory.py        # Multi-provider LLM factory pattern
│   ├── storage/
│   │   └── gcs_handler.py        # Google Cloud Storage FAISS sync
│   ├── observability/
│   │   ├── tracing.py            # @trace_retrieval decorator, LangSmith setup
│   │   ├── langsmith_config.py   # LangSmith configuration
│   │   └── monitoring.py         # Monitoring utilities
│   ├── utils/
│   │   ├── analytics.py          # Usage event tracking
│   │   ├── rate_limiter.py       # Per-user rate limiting
│   │   ├── tenant_helper.py      # Multi-tenancy helpers
│   │   ├── chat_helper.py        # Chat history utilities
│   │   ├── logger.py             # Centralized logging
│   │   └── exceptions.py         # Custom exception hierarchy
│   ├── multi_embedding.py        # Ensemble embedding strategies
│   └── prompts/
│       └── medical_assistant.txt # System prompt with medical + security rules
├── tests/
│   ├── unit/
│   │   └── test_rag_engine.py    # 200 unit tests for RAG pipeline
│   ├── integration/
│   │   ├── conftest.py           # Shared fixtures (mocked embeddings, vectorstores)
│   │   └── test_rag_pipeline_integration.py
│   ├── evaluation/               # RAGAS evaluation scripts
│   ├── giskard/                  # Giskard AI safety tests
│   └── promptfoo/                # Promptfoo LLM adversarial tests
├── .github/
│   └── workflows/
│       ├── ci.yml                # Ruff lint + pytest + 45% coverage gate
│       ├── cd.yml                # Auto-deploy to Cloud Run on main push
│       ├── quality.yml           # Pre-commit quality checks
│       └── evaluation.yml        # RAG quality evaluation
├── pyproject.toml                # Dependencies (managed by uv)
├── pytest.ini                    # Test configuration
└── .pre-commit-config.yaml       # Ruff + format + end-of-file hooks
```

---

## 🧪 Testing

```bash
# Run all tests with coverage report
uv run pytest tests/unit/ tests/integration/ -v --cov=src --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/ -v

# Run with coverage threshold
uv run pytest tests/ --cov=src --cov-fail-under=45
```

**Current status: 200/200 tests passing | 57% coverage**

---

## 📊 Observability (LangSmith)

Set `LANGSMITH_API_KEY` in `.env` to enable full tracing:

- Every query traced: retrieval → re-ranking → LLM → guardrails
- User 👍 / 👎 feedback stored back to LangSmith runs
- Structured metadata: `tenant_id`, `user_email`, `session_id`, token usage
- View at [https://smith.langchain.com](https://smith.langchain.com)

---

## ☁️ Cloud Deployment (Google Cloud Run)

Deployment is fully automated via GitHub Actions on every push to `main`.

**Manual deploy:**
```bash
gcloud run deploy medical-chatbot \
  --source . \
  --region us-central1 \
  --port 8080 \
  --memory 4Gi \
  --cpu 2 \
  --allow-unauthenticated
```

**Required GitHub Secrets:**

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT` | Google Cloud project ID |
| `GCP_REGION` | Deployment region (e.g. `us-central1`) |
| `GCP_CREDENTIALS` | Service account JSON |
| `GCS_BUCKET_NAME` | GCS bucket for FAISS index |
| `GROQ_API_KEY` | Groq API key |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `FIREBASE_API_KEY` | Firebase Web API key |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase Admin service account JSON |

---

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes (default LLM) | Groq API key |
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key |
| `FIREBASE_API_KEY` | Yes | Firebase Web API key |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Yes | Firebase Admin credentials |
| `GCS_BUCKET_NAME` | No (local dev) | GCS bucket for FAISS persistence |
| `LANGSMITH_API_KEY` | No | LangSmith observability |
| `ADMIN_USER_UID` | For admin setup | Firebase UID to promote to Admin |

---

## 📄 License

[MIT](LICENSE)
