import json
from typing import List, AsyncGenerator, Dict, Any
from app.models.schemas import ChatMessage, RAGResponse, SourceChunk
from app.services.vector_store import VectorStoreBase, SearchResult
from app.core.config import settings
from groq import AsyncGroq

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

class RAGChain:
    def __init__(self, vector_store: VectorStoreBase):
        self.vector_store = vector_store

    async def _get_context_and_sources(self, query: str, document_ids: List[str]) -> tuple[str, List[SourceChunk]]:
        # Retrieve chunks
        if len(document_ids) == 0:
            return "", []
        
        # If multiple document_ids, we can use an 'in' filter, depends on vector store logic
        # For simplicity, if langchain filtering supports {"document_id": {"$in": document_ids}}
        # But we'll just search and manually filter if store doesn't support $in natively or pass dict
        filter_dict = None
        if len(document_ids) > 0:
            if settings.VECTOR_STORE_TYPE == "faiss":
                filter_dict = lambda md: md.get("document_id") in document_ids
            else:
                filter_dict = {"document_id": {"$in": document_ids}}
                
        results = await self.vector_store.similarity_search(query, k=settings.TOP_K_RESULTS, filter=filter_dict)
        
        sources = []
        context_parts = []
        
        for doc, score in results:
            page_num = doc.metadata.get("page_number", 0)
            doc_id = doc.metadata.get("document_id", "")
            
            context_parts.append(f"[Page {page_num}]:\n{doc.page_content}")
            
            sources.append(SourceChunk(
                document_id=doc_id,
                filename=doc.metadata.get("filename", f"Doc {doc_id}"),
                content=doc.page_content,
                page_number=page_num,
                score=float(score)
            ))
            
        context_str = "\n\n".join(context_parts)
        return context_str, sources

    def _build_messages(self, query: str, context_str: str, chat_history: List[ChatMessage]) -> List[dict]:
        system_prompt = (
            "You are a helpful assistant that answers questions based ONLY on the provided document context. "
            "Always cite the source page numbers like [Page X]. If the answer is not in the context, say so clearly."
        )
        messages = [{"role": "system", "content": f"{system_prompt}\n\nCONTEXT:\n{context_str}"}]
        
        # Add last 10 messages
        for msg in chat_history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
            
        messages.append({"role": "user", "content": query})
        return messages

    async def astream_answer(
        self,
        query: str,
        document_ids: List[str],
        chat_history: List[ChatMessage],
        session_id: str
    ) -> AsyncGenerator[str, None]:
        
        context_str, sources = await self._get_context_and_sources(query, document_ids)
        messages = self._build_messages(query, context_str, chat_history)

        try:
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                stream=True
            )
            
            async for chunk in response:
                token = chunk.choices[0].delta.content
                if token:
                    # Clean up newlines for SSE event stream formatting
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                    
            sources_json = [s.model_dump() for s in sources]
            yield f"data: [SOURCES]{json.dumps(sources_json)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    async def get_answer(self, query: str, document_ids: List[str], chat_history: List[ChatMessage]) -> RAGResponse:
        context_str, sources = await self._get_context_and_sources(query, document_ids)
        messages = self._build_messages(query, context_str, chat_history)
        
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            stream=False
        )
        
        answer = response.choices[0].message.content or ""
        return RAGResponse(answer=answer, sources=sources)
