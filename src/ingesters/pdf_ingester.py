"""
Main script to create vector store from PDF documents
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from medical_chatbot.config.settings import settings
from medical_chatbot.ingesters import PDFIngester
from medical_chatbot.model import VectorStoreManager
from medical_chatbot.utils.logger import get_logger
from medical_chatbot.utils.exceptions import (
    DocumentLoadError,
    EmbeddingError,
    VectorStoreError
)

logger = get_logger(__name__, "ingestion.log")


def main():
    """Main function to create vector store"""
    
    print("=" * 60)
    print("MEDICAL CHATBOT - VECTOR STORE CREATION")
    print("=" * 60)
    print()
    
    try:
        # Create necessary directories
        settings.create_directories()
        
        # Step 1: Ingest PDFs
        print("📄 Step 1: Loading and processing PDF files...")
        logger.info("Starting PDF ingestion")
        
        ingester = PDFIngester()
        chunks = ingester.ingest()
        
        print(f"✅ Processed {len(chunks)} text chunks")
        print()
        
        # Step 2: Create vector store
        print("💾 Step 2: Creating FAISS vector store...")
        logger.info("Creating vector store")
        
        vs_manager = VectorStoreManager()
        vectorstore = vs_manager.create_vectorstore(chunks)
        
        print("✅ Vector store created")
        print()
        
        # Step 3: Save vector store
        print("💾 Step 3: Saving vector store to disk...")
        vs_manager.save_vectorstore(vectorstore)
        
        print(f"✅ Vector store saved to {settings.VECTORSTORE_PATH}")
        print()
        
        # Success summary
        print("=" * 60)
        print("✅ SUCCESS! Vector store created successfully")
        print("=" * 60)
        print()
        print("📊 Summary:")
        print(f"  - Text Chunks: {len(chunks)}")
        print(f"  - Vector Store: {settings.VECTORSTORE_PATH}")
        print(f"  - Embedding Model: {settings.EMBEDDING_MODEL}")
        print()
        print("🚀 You can now run the chatbot:")
        print("   streamlit run app.py")
        print()
        
        logger.info("Vector store creation completed successfully")
        return 0
        
    except (DocumentLoadError, EmbeddingError, VectorStoreError) as e:
        print()
        print("=" * 60)
        print("❌ ERROR OCCURRED")
        print("=" * 60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()
        print("💡 Check logs/ingestion.log for detailed error information")
        print()
        
        logger.error(f"Vector store creation failed: {str(e)}", exc_info=True)
        return 1
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
