from backend.app.services.embedding_service import EmbeddingService


def test_embedding_dimensions():
    service = EmbeddingService()

    embeddings = service.embed_texts(
        ["This is a test document."]
    )

    assert len(embeddings) == 1
    assert len(embeddings[0]) > 0


def test_embedding_is_normalized():
    service = EmbeddingService()

    embedding = service.embed_query(
        "What is this document about?"
    )

    magnitude = sum(value * value for value in embedding) ** 0.5

    assert abs(magnitude - 1.0) < 0.01