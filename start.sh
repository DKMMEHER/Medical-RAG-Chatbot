#!/bin/bash
set -e

echo "🚀 Starting Medical RAG Chatbot services..."

# Start FastAPI backend on port 8000 in the background
echo "🔧 Starting FastAPI backend on port 8000..."
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Wait for FastAPI to be ready (max 90 seconds)
echo "⏳ Waiting for FastAPI to be ready..."
BACKEND_READY=false
for i in $(seq 1 45); do
    if curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI backend is ready!"
        BACKEND_READY=true
        break
    fi
    echo "   Attempt $i/45 — waiting..."
    sleep 2
done

if [ "$BACKEND_READY" != "true" ]; then
    echo "❌ FastAPI backend failed to start within 90s. Exiting."
    # Kill the uvicorn process if it's still hanging
    kill $UVICORN_PID || true
    exit 1
fi

# Start Streamlit on port 8080 in the foreground (Cloud Run requires this)
echo "🌐 Starting Streamlit on port 8080..."
exec uv run streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
