import pytest
import os
from app.services.pdf_processor import PDFProcessor

@pytest.mark.asyncio
async def test_pdf_processing_basic():
    processor = PDFProcessor()
    test_pdf = os.path.join(os.path.dirname(__file__), "test_sample.pdf")
    
    # Test metadata extraction
    metadata = processor.extract_metadata(test_pdf)
    assert metadata.page_count == 1
    assert isinstance(metadata.title, str)
    
    # Test processing
    chunks = await processor.process_pdf(test_pdf, "test-doc-id")
    assert len(chunks) > 0
    assert chunks[0].content == "Hello world! This is a test PDF."
    assert chunks[0].document_id == "test-doc-id"

