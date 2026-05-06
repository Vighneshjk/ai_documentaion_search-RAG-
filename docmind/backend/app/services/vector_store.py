from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.schemas import DocumentChunk
import os
import faiss
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document as LangchainDocument
from app.core.config import Settings, settings

from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )

class SearchResult(Dict):
    pass

class VectorStoreBase(ABC):
    @abstractmethod
    async def add_documents(self, chunks: List[DocumentChunk]) -> None:
        pass

    @abstractmethod
    async def similarity_search(self, query: str, k: int, filter=None) -> List[Any]:
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        pass

class FAISSVectorStore(VectorStoreBase):
    def __init__(self, config: Settings):
        self.config = config
        self.index_path = config.FAISS_INDEX_PATH
        self.store = None
        self._embeddings = None  # lazy-loaded to avoid calling OpenAI at startup

    @property
    def embeddings(self):
        """Lazy-load embeddings so OpenAI is NOT called at server startup."""
        if self._embeddings is None:
            self._embeddings = get_embeddings()
        return self._embeddings

    def _ensure_store(self):
        """Load or create the FAISS store. Called lazily before first use."""
        if self.store is not None:
            return
        if os.path.exists(self.index_path) and os.path.isdir(self.index_path):
            try:
                self.store = LangchainFAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return
            except Exception:
                pass
        # Build a fresh empty FAISS index
        self._init_empty()

    def _init_empty(self):
        """Create a fresh in-memory FAISS index with the correct embedding dimension."""
        sample_embedding = self.embeddings.embed_query("hello")
        dim = len(sample_embedding)
        index = faiss.IndexFlatL2(dim)
        self.store = LangchainFAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

    def save(self):
        os.makedirs(self.index_path, exist_ok=True)
        self.store.save_local(self.index_path)

    async def add_documents(self, chunks: List[DocumentChunk]) -> None:
        import asyncio
        def add_sync():
            self._ensure_store()
            docs = [
                LangchainDocument(
                    page_content=chunk.content,
                    metadata={
                        "document_id": chunk.document_id,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "id": chunk.id
                    }
                ) for chunk in chunks
            ]
            if docs:
                self.store.add_documents(docs)
                self.save()
        await asyncio.to_thread(add_sync)

    async def similarity_search(self, query: str, k: int, filter=None) -> List[Any]:
        import asyncio
        def search_sync():
            self._ensure_store()
            if callable(filter):
                return self.store.similarity_search_with_score(query, k=k, filter=filter)
            elif isinstance(filter, dict):
                doc_ids = filter.get("document_id", {}).get("$in", [])
                return self.store.similarity_search_with_score(
                    query, k=k,
                    filter=lambda md: md.get("document_id") in doc_ids
                )
            else:
                return self.store.similarity_search_with_score(query, k=k)
        return await asyncio.to_thread(search_sync)

    async def delete_document(self, document_id: str) -> None:
        import asyncio
        def delete_sync():
            self._ensure_store()
            current_docs = list(self.store.docstore._dict.values())
            remaining_docs = [doc for doc in current_docs if doc.metadata.get("document_id") != document_id]
            self._init_empty()
            if remaining_docs:
                self.store.add_documents(remaining_docs)
            self.save()
        await asyncio.to_thread(delete_sync)


class PineconeVectorStore(VectorStoreBase):
    def __init__(self, config: Settings):
        self.config = config
        from pinecone import Pinecone
        self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = self.pc.Index(config.PINECONE_INDEX)
        self.embeddings = get_embeddings()

    async def add_documents(self, chunks: List[DocumentChunk]) -> None:
        from langchain_community.vectorstores import Pinecone as LangchainPinecone
        docs = [
            LangchainDocument(
                page_content=chunk.content,
                metadata={
                    "document_id": chunk.document_id,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "id": chunk.id
                }
            ) for chunk in chunks
        ]
        LangchainPinecone.from_documents(docs, self.embeddings, index_name=self.config.PINECONE_INDEX)

    async def similarity_search(self, query: str, k: int, filter=None) -> List[Any]:
        import asyncio
        def search_sync():
            from langchain_community.vectorstores import Pinecone as LangchainPinecone
            vectorstore = LangchainPinecone.from_existing_index(self.config.PINECONE_INDEX, self.embeddings)
            return vectorstore.similarity_search_with_score(query, k=k, filter=filter)
        return await asyncio.to_thread(search_sync)

    async def delete_document(self, document_id: str) -> None:
        import asyncio
        def delete_sync():
            self.index.delete(filter={"document_id": {"$eq": document_id}})
        await asyncio.to_thread(delete_sync)


def get_vector_store(config: Settings) -> VectorStoreBase:
    if config.VECTOR_STORE_TYPE == "pinecone" and config.PINECONE_INDEX and config.PINECONE_API_KEY:
        return PineconeVectorStore(config)
    return FAISSVectorStore(config)
