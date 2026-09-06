from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    document_id: str
    filename: str
    created_at: datetime