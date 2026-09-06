import hashlib
from pathlib import Path


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