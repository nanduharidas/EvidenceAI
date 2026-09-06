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