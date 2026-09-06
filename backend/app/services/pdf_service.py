import pymupdf

def extract_pdf_text(file_path: str) -> list[dict]:
    """
    Extract text from a PDF while preserving page-level metadata.

    Returns:
        A list of dictionaries containing:
        - page number
        - extracted text
    """
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append(
            {
                "page": page_number,
                "text":text,
            }
        )
    document.close()
    return pages