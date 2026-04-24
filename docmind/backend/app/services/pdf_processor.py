import fitz  # PyMuPDF
import tiktoken
import uuid
import asyncer # Note: asyncer to run blocking fitz code
import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.config import settings
from app.models.schemas import DocumentChunk

class PDFMetadata(BaseModel):
    title: str
    author: str
    page_count: int
    file_size: int

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=self.count_tokens
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    async def process_pdf(self, file_path: str, document_id: str) -> List[DocumentChunk]:
        return await asyncio.to_thread(self._process_pdf_sync, file_path, document_id)

    def _process_pdf_sync(self, file_path: str, document_id: str) -> List[DocumentChunk]:
        doc = fitz.open(file_path)
        chunks = []
        total_pages = len(doc)
        
        for i in range(total_pages):
            page = doc[i]
            text = page.get_text()
            if not text.strip():
                continue
            
            page_chunks = self.text_splitter.split_text(text)
            for chunk_index, chunk_text in enumerate(page_chunks):
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_text,
                    page_number=i + 1,
                    chunk_index=chunk_index,
                    metadata={
                        "document_id": document_id,
                        "page_number": i + 1,
                        "chunk_index": chunk_index,
                        "total_pages": total_pages
                    }
                )
                chunks.append(chunk)
                
        doc.close()
        return chunks

    def extract_metadata(self, file_path: str) -> PDFMetadata:
        doc = fitz.open(file_path)
        metadata = doc.metadata
        page_count = len(doc)
        import os
        file_size = os.path.getsize(file_path)
        
        result = PDFMetadata(
            title=metadata.get("title", ""),
            author=metadata.get("author", ""),
            page_count=page_count,
            file_size=file_size
        )
        doc.close()
        return result
