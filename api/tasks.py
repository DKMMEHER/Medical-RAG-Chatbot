import time
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.rag.engine import rebuild_vectorstore_from_pdfs

logger = get_logger(__name__)

def process_pdf_indexing_task(
    task_id: str,
    pdf_data: List[Dict[str, Any]],
    embedding_model: Any,
    gcs_handler: Any,
    state: Dict[str, Any],
    tenant_id: str
):
    """
    Background task to process PDF indexing.
    Updates the global state['tasks'] with progress.
    """
    try:
        logger.info(f"⏳ Task {task_id}: Starting background indexing for {len(pdf_data)} files")
        state["tasks"][task_id] = {"status": "processing", "message": "Extracting text and generating embeddings..."}
        
        # Call the engine
        ok, msg, chunks, final_db = rebuild_vectorstore_from_pdfs(
            pdf_data, embedding_model, gcs_handler, mode="add"
        )
        
        if ok:
            # Update global state with new vectorstore if merged/rebuilt
            if final_db:
                # Rebuild BM25 retriever to stay in sync with new index
                from src.rag.engine import build_bm25_retriever
                bm25 = build_bm25_retriever(final_db)
                
                state["tenant_data"][tenant_id] = {
                    "vectorstore": final_db,
                    "bm25_retriever": bm25
                }
                logger.info(f"🔍 BM25 retriever and vectorstore updated for tenant: {tenant_id}")
            
            state["tasks"][task_id] = {
                "status": "completed",
                "message": f"Successfully indexed {len(pdf_data)} files into {chunks} chunks.",
                "result": {"chunks_indexed": chunks}
            }
            logger.info(f"✅ Task {task_id}: Completed successfully")
        else:
            state["tasks"][task_id] = {
                "status": "failed",
                "message": msg
            }
            logger.error(f"❌ Task {task_id}: Failed - {msg}")
            
    except Exception as e:
        error_msg = f"Unexpected error in background task: {str(e)}"
        state["tasks"][task_id] = {
            "status": "failed",
            "message": error_msg
        }
        logger.error(f"❌ Task {task_id}: {error_msg}")
