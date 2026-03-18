#!/bin/bash
set -e

echo "🚀 Starting Medical RAG Chatbot services..."

# Start FastAPI backend on port 8000 in the background
echo "🔧 Starting FastAPI backend on port 8000..."
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Wait for FastAPI to be ready (max 60 seconds)
echo "⏳ Waiting for FastAPI to be ready..."
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI backend is ready!"
        break
    fi
    echo "   Attempt $i/30 — waiting..."
    sleep 2
done

# Start Streamlit on port 8080 in the foreground (Cloud Run requires this)
echo "🌐 Starting Streamlit on port 8080..."
exec uv run streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
