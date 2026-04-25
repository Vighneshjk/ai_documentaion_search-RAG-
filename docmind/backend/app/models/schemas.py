from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.document import DocumentStatus

class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    page_count: int
    chunk_count: int
    status: DocumentStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[dict]] = None
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    query: str
    document_ids: List[str]
    session_id: str
    history: List[ChatMessage]

class SourceChunk(BaseModel):
    document_id: str
    filename: str
    content: str
    page_number: int
    score: float

class RAGResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    page_number: int
    chunk_index: int
    metadata: dict
