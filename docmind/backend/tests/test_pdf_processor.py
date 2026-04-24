import pytest
from app.services.pdf_processor import PDFProcessor

@pytest.mark.asyncio
async def test_pdf_processing_basic():
    processor = PDFProcessor()
    assert processor is not None
    # Real tests would use a sample pdf fixture
