import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStoreBase

@pytest.fixture
def mock_pdf_processor():
    processor = MagicMock(spec=PDFProcessor)
    processor.process_pdf = AsyncMock(return_value=[])
    processor.extract_metadata = MagicMock()
    return processor

@pytest.fixture
def mock_vector_store():
    store = MagicMock(spec=VectorStoreBase)
    store.add_documents = AsyncMock()
    store.similarity_search = AsyncMock(return_value=[])
    store.delete_document = AsyncMock()
    return store

