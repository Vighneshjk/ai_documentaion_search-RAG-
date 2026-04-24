import os
import shutil
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.schemas import DocumentResponse
from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreBase
from app.api.deps import get_vector_store_depend
import logging

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger("docmind")

pdf_processor = PDFProcessor()

async def process_document_task(document_id: uuid.UUID, file_path: str, vector_store: VectorStoreBase):
    from app.db.database import AsyncSessionLocal
    logger.info(f"Starting formatting task for document {document_id}")
    try:
        async with AsyncSessionLocal() as session:
            # 1. Processing chunks
            chunks = await pdf_processor.process_pdf(file_path, str(document_id))
            
            # 2. Add embeddings to vector store
            await vector_store.add_documents(chunks)
            
            # 3. Update document status
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.chunk_count = len(chunks)
                doc.status = DocumentStatus.ready
                await session.commit()
                logger.info(f"Document {document_id} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        async with AsyncSessionLocal() as session:
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            doc = result.scalar_one_or_none()
            if doc:
                doc.status = DocumentStatus.failed
                doc.error_message = str(e)
                await session.commit()

@router.post("/upload", response_model=DocumentResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStoreBase = Depends(get_vector_store_depend)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")
        
    document_id = uuid.uuid4()
    doc_dir = os.path.join(settings.UPLOAD_DIR, str(document_id))
    os.makedirs(doc_dir, exist_ok=True)
    file_path = os.path.join(doc_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB.")
        
    try:
        metadata = pdf_processor.extract_metadata(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Invalid PDF file: {e}")

    new_doc = Document(
        id=document_id,
        filename=file.filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        page_count=metadata.page_count,
        status=DocumentStatus.processing
    )
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    background_tasks.add_task(process_document_task, document_id, file_path, vector_store)
    
    return new_doc

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Document)
    if status:
        query = query.where(Document.status == status)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Document).where(Document.id == uuid.UUID(document_id))
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStoreBase = Depends(get_vector_store_depend)
):
    query = select(Document).where(Document.id == uuid.UUID(document_id))
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await db.delete(doc)
    await db.commit()
    
    # Clean up files
    doc_dir = os.path.dirname(doc.file_path)
    if os.path.exists(doc_dir):
        shutil.rmtree(doc_dir, ignore_errors=True)
        
    # Clean up vector store
    await vector_store.delete_document(document_id)
    
    return {"message": "Document deleted"}
