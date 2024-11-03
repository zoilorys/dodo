from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field

class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    PROCESSED = "PROCESSED"

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: DocumentStatus = Field(default=DocumentStatus.PENDING)
    name: str = Field(default=None, nullable=False)
    path: str = Field(default=None, nullable=False)
