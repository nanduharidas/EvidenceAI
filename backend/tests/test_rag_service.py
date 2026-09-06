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

def test_irrelevant_results_are_filtered():
    class IrrelevantVectorStore:
        def search(self, query_embedding, top_k):
            return {
                "documents": [["Unrelated text."]],
                "metadatas": [
                    [
                        {
                            "document_id": "test-document",
                            "document": "test.pdf",
                            "page": 1,
                        }
                    ]
                ],
                "distances": [[0.8]],
            }

    class LLMShouldNotBeCalled:
        def generate_answer(self, question, context):
            raise AssertionError(
                "LLM should not be called when no relevant evidence exists"
            )

    rag_service = RAGService(
        embedding_service=FakeEmbeddingService(),
        vector_store=IrrelevantVectorStore(),
        llm_service=LLMShouldNotBeCalled(),
        max_retrieval_distance=0.45,
    )

    result = rag_service.answer_question(
        question="An unrelated question",
    )

    assert result["sources"] == []
    assert result["distances"] == []
    assert result["answer"] == (
        "I could not find relevant evidence "
        "in the uploaded documents."
    )

def test_only_relevant_results_are_sent_to_llm():
    class MixedVectorStore:
        def search(self, query_embedding, top_k):
            return {
                "documents": [
                    [
                        "Relevant evidence.",
                        "Irrelevant evidence.",
                    ]
                ],
                "metadatas": [
                    [
                        {
                            "document_id": "test-document",
                            "document": "test.pdf",
                            "page": 2,
                        },
                        {
                            "document_id": "test-document",
                            "document": "test.pdf",
                            "page": 8,
                        },
                    ]
                ],
                "distances": [[0.25, 0.70]],
            }

    class ContextCheckingLLM:
        def generate_answer(self, question, context):
            assert "Relevant evidence." in context
            assert "Irrelevant evidence." not in context

            return "The answer is supported [1]."

    rag_service = RAGService(
        embedding_service=FakeEmbeddingService(),
        vector_store=MixedVectorStore(),
        llm_service=ContextCheckingLLM(),
        max_retrieval_distance=0.45,
    )

    result = rag_service.answer_question(
        question="Relevant question",
    )

    assert len(result["sources"]) == 1
    assert result["sources"][0]["text"] == "Relevant evidence."
    assert result["distances"] == [0.25]