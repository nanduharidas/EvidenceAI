from backend.app.services.rag_service import (
    RAGService,
    validate_citations,
)


class FakeEmbeddingService:
    def embed_query(self, question):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def search(self, query_embedding, top_k):
        return {
            "documents": [
                [
                    "The encoder contains six identical layers.",
                    "The decoder also contains six identical layers.",
                ]
            ],
            "metadatas": [
                [
                    {
                        "document_id": "test-document",
                        "document": "test.pdf",
                        "page": 3,
                    },
                    {
                        "document_id": "test-document",
                        "document": "test.pdf",
                        "page": 4,
                    },
                ]
            ],
            "distances": [[0.2, 0.4]],
        }


class FakeLLMService:
    def generate_answer(self, question, context):
        return "The encoder contains six identical layers [1]."


def test_valid_citations():
    answer = "The Transformer uses attention [1]."
    result = validate_citations(answer, source_count=3)

    assert result == answer


def test_multiple_valid_citations():
    answer = "The encoder uses self-attention [1][2]."
    result = validate_citations(answer, source_count=3)

    assert result == answer


def test_invalid_citation():
    answer = "The Transformer uses attention [4]."

    try:
        validate_citations(answer, source_count=3)
        assert False
    except ValueError:
        pass


def test_no_citations():
    answer = "The document does not provide enough information."

    result = validate_citations(answer, source_count=3)

    assert result == answer


def test_sources_include_supporting_text():
    rag_service = RAGService(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
        llm_service=FakeLLMService(),
    )

    result = rag_service.answer_question(
        question="How many encoder layers are there?",
        top_k=2,
    )

    assert result["answer"] == (
        "The encoder contains six identical layers [1]."
    )

    assert result["sources"] == [
        {
            "id": 1,
            "document_id": "test-document",
            "document": "test.pdf",
            "page": 3,
            "text": "The encoder contains six identical layers.",
        },
        {
            "id": 2,
            "document_id": "test-document",
            "document": "test.pdf",
            "page": 4,
            "text": "The decoder also contains six identical layers.",
        },
    ]

    assert result["distances"] == [0.2, 0.4]