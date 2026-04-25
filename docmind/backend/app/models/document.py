import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum
from app.db.database import Base
import enum

class DocumentStatus(str, enum.Enum):
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class Document(Base):
    __tablename__ = "documents"

    # Use String for UUID — works with both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String, index=True)
    original_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.uploading)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
