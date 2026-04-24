from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest, RAGResponse
from app.services.vector_store import VectorStoreBase
from app.services.rag_chain import RAGChain
from app.api.deps import get_vector_store_depend
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.document import Document, DocumentStatus
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

async def validate_documents(document_ids: list[str], db: AsyncSession):
    for doc_id in document_ids:
        query = select(Document).where(Document.id == uuid.UUID(doc_id))
        result = await db.execute(query)
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        if doc.status != DocumentStatus.ready:
            raise HTTPException(status_code=400, detail=f"Document {doc_id} is not ready for querying")

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStoreBase = Depends(get_vector_store_depend)
):
    await validate_documents(request.document_ids, db)
    
    rag_chain = RAGChain(vector_store)
    
    generator = rag_chain.astream_answer(
        query=request.query,
        document_ids=request.document_ids,
        chat_history=request.history,
        session_id=request.session_id
    )
    
    return StreamingResponse(
        generator, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("", response_model=RAGResponse)
async def chat_sync(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStoreBase = Depends(get_vector_store_depend)
):
    await validate_documents(request.document_ids, db)
    
    rag_chain = RAGChain(vector_store)
    
    return await rag_chain.get_answer(
        query=request.query,
        document_ids=request.document_ids,
        chat_history=request.history
    )
