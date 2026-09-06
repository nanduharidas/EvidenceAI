from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from backend.app.services.pdf_service import extract_pdf_text
from backend.app.services.chunk_service import create_chunks

app = FastAPI(
    title="Evidence API",
    description="AI-powered document Q&A with evidence-based citations",
    version="0.1.0",
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def root():
    return {
        "name": "EvidenceAI",
        "status": "running",
        "version": "0.1.0",
    }

@app.get("/health")
def health():
    return{"status":"healthy"}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF and extract its text page by page.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename procided",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()

    file_path.write_bytes(contents)

    pages = extract_pdf_text(str(file_path))

    chunks = create_chunks(
        pages=pages,
        document_name=file.filename
    )

    return{
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "content": [
            {
                "chunk_id": chunk.chunk_id,
                "document": chunk.document,
                "page": chunk.page,
                "text": chunk.text,
            }
            for chunk in chunks
        ],
    }