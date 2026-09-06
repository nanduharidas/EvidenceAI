from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from backend.app.services.pdf_service import extract_pdf_text
from backend.app.services.chunk_service import create_chunks
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore
from pydantic import BaseModel

app = FastAPI(
    title="Evidence API",
    description="AI-powered document Q&A with evidence-based citations",
    version="0.1.0",
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

embedding_service = EmbeddingService()
vector_store = VectorStore()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
def search_documents(request: SearchRequest):
    query_embedding = embedding_service.embed_query(
        request.query
    )

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=request.top_k,
    )

    return results
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

    chunk_texts = [chunk.text for chunk in chunks]

    embeddings = embedding_service.embed_texts(chunk_texts)

    vector_store.add_chunks(
        chunk_ids=[chunk.chunk_id for chunk in chunks],
        texts=chunk_texts,
        embeddings=embeddings,
        metadatas=[
            {
                "document": chunk.document,
                "page": chunk.page,
            }
            for chunk in chunks
        ],
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

