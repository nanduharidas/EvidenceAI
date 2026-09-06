from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from backend.app.services.pdf_service import extract_pdf_text
from backend.app.services.chunk_service import create_chunks
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore
from pydantic import BaseModel
from backend.app.services.document_service import (
    generate_document_id,
    create_safe_filename,
    load_documents,
    create_document_record,
    add_document,
    get_document,
    delete_document_record,
)
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import RAGService

app = FastAPI(
    title="Evidence API",
    description="AI-powered document Q&A with evidence-based citations",
    version="0.1.0",
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

embedding_service = EmbeddingService()
vector_store = VectorStore()
llm_service = LLMService()

rag_service = RAGService(
    embedding_service=embedding_service,
    vector_store=vector_store,
    llm_service=llm_service,
)

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post("/ask")
def ask_question(request: QuestionRequest):
    return rag_service.answer_question(
        question=request.question,
        top_k=request.top_k,
    )

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
    return {
        "status": "healthy",
    }

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF and extract its text page by page.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    safe_filename = create_safe_filename(file.filename)
    file_path = UPLOAD_DIR / safe_filename

    contents = await file.read()

    document_id = generate_document_id(
    file.filename,
    contents,
    )

    file_path.write_bytes(contents)

    pages = extract_pdf_text(str(file_path))

    chunks = create_chunks(
        pages=pages,
        document_id=document_id,
        document_name=safe_filename,
    )

    chunk_texts = [chunk.text for chunk in chunks]

    embeddings = embedding_service.embed_texts(chunk_texts)

    vector_store.add_chunks(
        chunk_ids=[chunk.chunk_id for chunk in chunks],
        texts=chunk_texts,
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": document_id,
                "document": chunk.document,
                "page": chunk.page,
            }
            for chunk in chunks
        ],
    )
    document_record = create_document_record(
        document_id=document_id,
        filename=safe_filename,
        pages=len(pages),
        chunks=len(chunks),
    )

    add_document(document_record)

    return {
    "document_id": document_id,
    "filename": safe_filename,
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

@app.get("/documents")
def list_documents():
    return {
        "documents": load_documents(),
    }

@app.get("/documents/{document_id}")
def get_document_details(document_id: str):
    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document

@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    filename = document["filename"]
    file_path = UPLOAD_DIR / filename

    if file_path.exists():
        file_path.unlink()

    vector_store.collection.delete(
        where={"document_id": document_id}
    )

    delete_document_record(document_id)

    return {
        "document_id": document_id,
        "status": "deleted",
    }

