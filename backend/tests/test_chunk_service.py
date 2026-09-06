import pytest
from backend.app.services.chunk_service import create_chunks

def test_create_chunks_preserves_page_metadata():
    pages = [
        {
            "page": 1,
            "text": "A" * 2500,
        }
    ]

    chunks = create_chunks(
        pages=pages,
        document_name="test.pdf",
        chunk_size=1000,
        overlap=100,
    )

    assert len(chunks) > 1
    assert all(chunk.document == "test.pdf" for chunk in chunks)
    assert all(chunk.page == 1 for chunk in chunks)

def test_empty_pages_are_skipped():
    pages = [
        {
            "page": 1,
            "text": "",
        },
        {
            "page": 2,
            "text": "Hello world",
        },
    ]

    chunks = create_chunks(
        pages=pages,
        document_name="test.pdf",
    )

    assert len(chunks) == 1
    assert chunks[0].page == 2


def test_invalid_overlap_raises_error():
    pages = [
        {
            "page": 1,
            "text": "Hello world",
        }
    ]

    with pytest.raises(ValueError):
        create_chunks(
            pages=pages,
            document_name="test.pdf",
            chunk_size=100,
            overlap=100,
        )