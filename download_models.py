from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder


def download_models():
    """
    Pre-downloads and caches the specific HuggingFace models used by the app.
    This should be run during the Docker build process to avoid runtime delays.
    """
    print("🚀 Pre-downloading models to cache...")

    # 1. Primary Embedding Model
    print("🧬 Downloading BGE-Base embeddings...")
    HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # 2. Secondary Embedding Model
    print("🧬 Downloading MiniLM embeddings...")
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 3. Cross-Encoder Model
    print("🎯 Downloading Cross-Encoder re-ranker...")
    CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    print("✅ All models downloaded and cached successfully!")


if __name__ == "__main__":
    download_models()
