#!/bin/bash
set -e

echo "🚀 Starting Medical RAG Chatbot services..."

# Start FastAPI backend on port 8000 in the background
echo "🔧 Starting FastAPI backend on port 8000..."
.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Start Streamlit on port 8080 in the background
echo "🌐 Starting Streamlit on port 8080..."
.venv/bin/streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false &
STREAMLIT_PID=$!

# Wait for either process to exit
# If one crashes (e.g., uvicorn fails to start), wait -n will release and the container will exit
wait -n

echo "❌ A service exited unexpectedly. Terminating container."
exit 1
