from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    role: str
    content: str
    citations: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionCreateRequest(BaseModel):
    document_ids: List[str]
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    document_ids: List[str]
    messages: List[MessageSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class AddMessageRequest(BaseModel):
    role: str
    content: str
    citations: List[dict] = []
