from dataclasses import dataclass

@dataclass
class DocumentChunk:
    chunk_id: str
    document: str
    page: int
    text: str

def create_chunks(
        pages: list[dict],
        document_name: str,
        chunk_size: int = 1000,
        overlap: int = 150,
) -> list[DocumentChunk]:
    """
    Split page-level PDF text into overlapping chunks.

    Each chunk retains its document and page metadata.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    for page_data in pages:
        page_number = page_data["page"]
        text = page_data["text"].strip()

        if not text:
            continue

        start = 0
        chunk_number = 1

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{page_number}-{chunk_number:03d}",
                        document=document_name,
                        page=page_number,
                        text=chunk_text,
                    )
                )
            if end > len(text):
                break

            start = end - overlap
            chunk_number += 1
    return chunks