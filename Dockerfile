# Use official Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY . /app/

# Pre-download models to bake them into the image
# This prevents Cloud Run startup timeouts during model downloads.
RUN uv run python download_models.py

# Copy Streamlit config (critical for WebSocket support on Cloud Run)
COPY .streamlit /app/.streamlit

# Expose the port Streamlit uses on Cloud Run
EXPOSE 8080

# Configure Streamlit via ENV
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# GCS bucket name for FAISS persistence (injected by Cloud Run at deploy time)
ENV GCS_BUCKET_NAME=""

# Run the application via start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
