from backend.app.services import document_service
from backend.app.services.document_service import (
    generate_document_id,
    create_safe_filename,
)


def test_document_id_is_deterministic():
    content = b"hello world"

    first_id = generate_document_id(
        "test.pdf",
        content,
    )

    second_id = generate_document_id(
        "test.pdf",
        content,
    )

    assert first_id == second_id


def test_different_content_creates_different_id():
    first_id = generate_document_id(
        "test.pdf",
        b"hello",
    )

    second_id = generate_document_id(
        "test.pdf",
        b"goodbye",
    )

    assert first_id != second_id


def test_filename_path_is_removed():
    filename = create_safe_filename(
        "../../secret/test.pdf"
    )

    assert filename == "test.pdf"


def test_add_document_does_not_create_duplicate(tmp_path, monkeypatch):
    test_documents_file = tmp_path / "documents.json"

    monkeypatch.setattr(
        document_service,
        "DOCUMENTS_FILE",
        test_documents_file,
    )

    record = {
        "document_id": "test-document-id",
        "filename": "test.pdf",
        "created_at": "2026-09-06T00:00:00+00:00",
        "pages": 1,
        "chunks": 1,
    }

    document_service.add_document(record)
    document_service.add_document(record)

    documents = document_service.load_documents()

    matching_documents = [
        document
        for document in documents
        if document["document_id"] == "test-document-id"
    ]

    assert len(matching_documents) == 1