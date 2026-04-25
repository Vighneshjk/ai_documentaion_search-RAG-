import pytest
from unittest.mock import MagicMock, patch
from app.services.rag_chain import RAGChain

@pytest.mark.asyncio
async def test_rag_chain_query(mock_vector_store):
    # Mock settings and LLM
    with patch("app.services.rag_chain.settings") as mock_settings:
        mock_settings.LLM_MODEL = "gpt-4o"
        mock_settings.OPENAI_API_KEY = "test-key"
        
        # Initialize RAG chain with mock vector store
        chain = RAGChain(mock_vector_store)
        
        # Mock the stream_query or query method if needed
        # For now, let's just test that it's initialized correctly
        assert chain.vector_store == mock_vector_store

