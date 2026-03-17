from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Message(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class QueryRequest(BaseModel):
    query: str = Field(..., example="What are the symptoms of type 2 diabetes?")
    history: Optional[List[Message]] = Field(default_factory=list)

class SourceDocument(BaseModel):
    content: str
    metadata: Dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    elapsed_time: float

class UploadResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    chunks_indexed: Optional[int] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str # 'processing', 'completed', 'failed'
    message: Optional[str] = None
    result: Optional[Dict] = None

class HealthStatus(BaseModel):
    status: str
    version: str
    components: Dict[str, str]

class ReadyResponse(BaseModel):
    status: str
    is_ready: bool
    components: Dict[str, bool]
    message: Optional[str] = None

class FeedbackRequest(BaseModel):
    run_id: str
    score: float # 1.0 for thumbs up, 0.0 for thumbs down
    comment: Optional[str] = None
