from typing import List, Optional
from pydantic import BaseModel


class ChatQueryRequest(BaseModel):
    """Payload for a RAG chat query."""
    query: str
    document_ids: List[str]
    top_k: int = 5
    session_id: Optional[str] = None


class CitationSchema(BaseModel):
    """A single chunk citation returned alongside an AI answer."""
    doc_id: str
    filename: str
    page: int
    snippet: str
    score: float


class ChatQueryResponse(BaseModel):
    """Non-streaming response schema (used when streaming is not requested)."""
    answer: str
    citations: List[CitationSchema]
    session_id: Optional[str] = None
