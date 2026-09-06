from backend.app.services import conversation_service


def test_create_conversation(tmp_path, monkeypatch):
    conversations_file = tmp_path / "conversations.json"

    monkeypatch.setattr(
        conversation_service,
        "CONVERSATIONS_FILE",
        conversations_file,
    )

    conversation = conversation_service.create_conversation()

    assert conversation["conversation_id"]
    assert conversation["created_at"]
    assert conversation["updated_at"]
    assert conversation["messages"] == []

    assert conversations_file.exists()


def test_get_conversation(tmp_path, monkeypatch):
    conversations_file = tmp_path / "conversations.json"

    monkeypatch.setattr(
        conversation_service,
        "CONVERSATIONS_FILE",
        conversations_file,
    )

    created = conversation_service.create_conversation()

    result = conversation_service.get_conversation(
        created["conversation_id"]
    )

    assert result == created


def test_add_message(tmp_path, monkeypatch):
    conversations_file = tmp_path / "conversations.json"

    monkeypatch.setattr(
        conversation_service,
        "CONVERSATIONS_FILE",
        conversations_file,
    )

    conversation = conversation_service.create_conversation()

    response = {
        "answer": "There are 6 encoder layers. [1]",
        "sources": [
            {
                "id": 1,
                "document_id": "test-document",
                "document": "test.pdf",
                "page": 3,
                "text": "The encoder is composed of N = 6 identical layers.",
            }
        ],
        "distances": [0.2],
    }

    updated = conversation_service.add_message(
        conversation_id=conversation["conversation_id"],
        question="How many encoder layers are there?",
        response=response,
    )

    assert len(updated["messages"]) == 1
    assert updated["messages"][0]["question"] == (
        "How many encoder layers are there?"
    )
    assert updated["messages"][0]["answer"] == (
        "There are 6 encoder layers. [1]"
    )
    assert updated["messages"][0]["sources"] == response["sources"]
    assert updated["messages"][0]["distances"] == [0.2]


def test_get_missing_conversation(tmp_path, monkeypatch):
    conversations_file = tmp_path / "conversations.json"

    monkeypatch.setattr(
        conversation_service,
        "CONVERSATIONS_FILE",
        conversations_file,
    )

    result = conversation_service.get_conversation(
        "does-not-exist"
    )

    assert result is None