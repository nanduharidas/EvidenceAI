import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


CONVERSATIONS_FILE = Path("data/conversations.json")


def load_conversations() -> list[dict]:
    if not CONVERSATIONS_FILE.exists():
        return []

    return json.loads(
        CONVERSATIONS_FILE.read_text(encoding="utf-8")
    )


def save_conversations(conversations: list[dict]) -> None:
    CONVERSATIONS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CONVERSATIONS_FILE.write_text(
        json.dumps(conversations, indent=2),
        encoding="utf-8",
    )


def create_conversation() -> dict:
    now = datetime.now(timezone.utc).isoformat()

    conversation = {
        "conversation_id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }

    conversations = load_conversations()
    conversations.append(conversation)
    save_conversations(conversations)

    return conversation


def get_conversation(conversation_id: str) -> dict | None:
    conversations = load_conversations()

    return next(
        (
            conversation
            for conversation in conversations
            if conversation["conversation_id"] == conversation_id
        ),
        None,
    )


def add_message(
    conversation_id: str,
    question: str,
    response: dict,
) -> dict:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["conversation_id"] == conversation_id:
            conversation["messages"].append(
                {
                    "question": question,
                    "answer": response["answer"],
                    "sources": response["sources"],
                    "distances": response["distances"],
                }
            )

            conversation["updated_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            save_conversations(conversations)

            return conversation

    raise ValueError(
        f"Conversation not found: {conversation_id}"
    )