from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conversation:
    conversation_id: str
    created_at: datetime
    updated_at: datetime