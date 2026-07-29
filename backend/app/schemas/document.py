from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    filename: str
    file_size: int
    status: str = "pending"  # pending, processing, processed, failed
    page_count: Optional[int] = None
    summary: Optional[str] = None


class DocumentCreate(DocumentBase):
    storage_path: str


class DocumentResponse(DocumentBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            # Handle object ID parsing or datetime mapping if needed
        }
