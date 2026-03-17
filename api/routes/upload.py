from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from api.models.schemas import UploadResponse, TaskStatusResponse
from api.main import state, get_current_user
from src.utils.logger import get_logger
from api.tasks import process_pdf_indexing_task
from src.utils.tenant_helper import extract_tenant_id
from src.storage.gcs_handler import GCSHandler
import uuid
from typing import List

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_pdfs(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    user=Depends(get_current_user),
):
    """Endpoint for admins to upload and index new medical documents asynchronously."""

    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Only admins can upload documents.")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    pdf_data = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        content = await file.read()
        pdf_data.append({"name": file.filename, "bytes": content})

    if not pdf_data:
        raise HTTPException(status_code=400, detail="No valid PDF files found.")

    # 1. Generate Task ID
    task_id = str(uuid.uuid4())
    state["tasks"][task_id] = {
        "status": "processing",
        "message": "Queued for indexing...",
    }

    # 2. Extract models/params for task
    embedding_model = state.get("embeddings")

    # 2.5 Multi-tenancy: Create a tenant-aware GCS handler
    tenant_id = extract_tenant_id(user["email"])
    gcs_handler = GCSHandler(
        bucket_name=settings.gcs_bucket_name if settings else None,
        index_prefix=settings.gcs_index_prefix if settings else "faiss-index",
        tenant_id=tenant_id,
    )

    # 3. Launch background task
    background_tasks.add_task(
        process_pdf_indexing_task,
        task_id,
        pdf_data,
        embedding_model,
        gcs_handler,
        state,
        tenant_id,  # Pass tenant_id to the task
    )

    return {
        "success": True,
        "message": "Files received. Indexing started in the background.",
        "task_id": task_id,
    }


@router.get("/upload/status/{task_id}", response_model=TaskStatusResponse)
async def get_upload_status(task_id: str, user=Depends(get_current_user)):
    """Check the status of a background indexing task."""
    task = state["tasks"].get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task_id,
        "status": task["status"],
        "message": task.get("message"),
        "result": task.get("result"),
    }
