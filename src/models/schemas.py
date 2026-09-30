from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="User question")
    chat_history: Optional[list] = Field(default=None, description="Previous chat history")
    
    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty")
        return v


class SourceDocument(BaseModel):
    content: str
    source: str
    chunk_index: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
    query: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentResponse(BaseModel):
    filename: str
    size: Optional[int] = None
    upload_date: Optional[str] = None
    status: str = "success"
    message: str = ""


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    documents_count: int = 0
    vector_chunks_count: int = 0
