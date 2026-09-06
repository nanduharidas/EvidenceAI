import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


DOCUMENTS_FILE = Path("data/documents.json")


def generate_document_id(filename: str, content: bytes) -> str:
    """
    Generate a deterministic document ID from the file content.

    The same file content produces the same ID.
    """

    file_hash = hashlib.sha256(content).hexdigest()

    return file_hash[:16]


def create_safe_filename(filename: str) -> str:
    """
    Remove path components and return a safe filename.
    """

    return Path(filename).name


def load_documents() -> list[dict]:
    """
    Load the document registry from disk.
    """

    if not DOCUMENTS_FILE.exists():
        return []

    return json.loads(
        DOCUMENTS_FILE.read_text(encoding="utf-8")
    )


def save_documents(documents: list[dict]) -> None:
    """
    Save the document registry to disk.
    """

    DOCUMENTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DOCUMENTS_FILE.write_text(
        json.dumps(documents, indent=2),
        encoding="utf-8",
    )


def create_document_record(
    document_id: str,
    filename: str,
    pages: int,
    chunks: int,
) -> dict:
    """
    Create a document registry record.
    """

    return {
        "document_id": document_id,
        "filename": filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
        "chunks": chunks,
    }


def add_document(record: dict) -> None:
    documents = load_documents()

    existing_document = next(
        (
            document
            for document in documents
            if document["document_id"] == record["document_id"]
        ),
        None,
    )

    if existing_document is not None:
        return

    documents.append(record)
    save_documents(documents)

def get_document(document_id: str) -> dict | None:
    """
    Find a document by ID.
    """

    documents = load_documents()

    return next(
        (
            document
            for document in documents
            if document["document_id"] == document_id
        ),
        None,
    )


def delete_document_record(document_id: str) -> bool:
    """
    Remove a document from the registry.

    Returns True when a document was removed.
    """

    documents = load_documents()

    remaining_documents = [
        document
        for document in documents
        if document["document_id"] != document_id
    ]

    if len(remaining_documents) == len(documents):
        return False

    save_documents(remaining_documents)

    return True