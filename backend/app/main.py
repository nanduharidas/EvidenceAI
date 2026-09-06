from fastapi import FastAPI

app = FastAPI(
    title="EvidenceAI API",
    description="AI-powered document Q&A with evidence-based citations",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "EvidenceAI",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
