from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.schemas import DocumentChunk
import os
import faiss
from langchain_community.vectorstores import FAISS as LangchainFAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document as LangchainDocument
from app.core.config import Settings, settings

# Ensure embeddings service is imported (will create next)
from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY
    )

class SearchResult(Dict):
    pass  # We can also map to SourceChunk later depending on usage.

class VectorStoreBase(ABC):
    @abstractmethod
    async def add_documents(self, chunks: List[DocumentChunk]) -> None:
        pass

    @abstractmethod
    async def similarity_search(self, query: str, k: int, filter: dict) -> List[Any]:
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        pass

class FAISSVectorStore(VectorStoreBase):
    def __init__(self, config: Settings):
        self.config = config
        self.embeddings = get_embeddings()
        self.index_path = config.FAISS_INDEX_PATH
        self.store = None
        self.load()

    def load(self):
        if os.path.exists(self.index_path) and os.path.isdir(self.index_path):
            try:
                self.store = LangchainFAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception:
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
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
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.store.save_local(self.index_path)

    async def add_documents(self, chunks: List[DocumentChunk]) -> None:
        import asyncio
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
            await asyncio.to_thread(self.store.add_documents, docs)
            await asyncio.to_thread(self.save)

    async def similarity_search(self, query: str, k: int, filter: dict) -> List[Any]:
        import asyncio
        def search_sync():
            # FAISS in langchain supports filter function or dict
            return self.store.similarity_search_with_score(
                query, 
                k=k, 
                filter=filter
            )
        results = await asyncio.to_thread(search_sync)
        return results

    async def delete_document(self, document_id: str) -> None:
        import asyncio
        def delete_sync():
            # In FAISS we have to manually filter out OR rebuild the index.
            # A simple approach: keep documents not matching the ID and rebuild.
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
        import asyncio
        
        async def embed_and_upsert():
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
            # Upsert in batches
            LangchainPinecone.from_documents(
                docs,
                self.embeddings,
                index_name=self.config.PINECONE_INDEX
            )
        await embed_and_upsert()

    async def similarity_search(self, query: str, k: int, filter: dict) -> List[Any]:
        import asyncio
        def search_sync():
            from langchain_community.vectorstores import Pinecone as LangchainPinecone
            vectorstore = LangchainPinecone.from_existing_index(
                self.config.PINECONE_INDEX, 
                self.embeddings
            )
            return vectorstore.similarity_search_with_score(query, k=k, filter=filter)
        return await asyncio.to_thread(search_sync)

    async def delete_document(self, document_id: str) -> None:
        import asyncio
        def delete_sync():
            # Pinecone allows delete by metadata
            # but langchain might not expose this directly easily. We loop or use pinecone client.
            self.index.delete(filter={"document_id": {"$eq": document_id}})
        await asyncio.to_thread(delete_sync)

def get_vector_store(config: Settings) -> VectorStoreBase:
    if config.VECTOR_STORE_TYPE == "pinecone" and config.PINECONE_INDEX and config.PINECONE_API_KEY:
        return PineconeVectorStore(config)
    return FAISSVectorStore(config)
