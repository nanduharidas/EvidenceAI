import pytest

from backend.app.services.rag_service import validate_citations


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

    with pytest.raises(ValueError):
        validate_citations(answer, source_count=3)


def test_no_citations():
    answer = "The document does not provide enough information."

    result = validate_citations(answer, source_count=3)

    assert result == answer