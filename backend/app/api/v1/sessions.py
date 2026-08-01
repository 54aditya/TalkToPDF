"""
Sessions API Router
Manages persistent chat session CRUD.

POST   /sessions                    — Creates a new session for given documents
GET    /sessions                    — Lists all sessions (no messages)
GET    /sessions/{session_id}       — Gets a session with full message history
POST   /sessions/{session_id}/messages — Appends a message to a session
DELETE /sessions/{session_id}       — Deletes a session
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundException
from app.database.connection import get_mongodb
from app.database.session_repository import SessionRepository
from app.database.repository import DocumentRepository
from app.schemas.session import SessionCreateRequest, AddMessageRequest
from app.core.logging import logger


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", status_code=201)
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """Creates a new chat session linked to one or more documents."""
    doc_repo = DocumentRepository(db)
    filenames = []
    for doc_id in payload.document_ids:
        doc = await doc_repo.get_by_id(doc_id)
        if doc:
            filenames.append(doc["filename"].replace(".pdf", ""))

    title = payload.title or (", ".join(filenames[:2]) or "New Research Session")

    repo = SessionRepository(db)
    session = await repo.create(document_ids=payload.document_ids, title=title)
    logger.info(f"Created session: {session['_id']} — '{title}'")
    return session


@router.get("")
async def list_sessions(db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Lists all chat sessions (without message content for performance)."""
    repo = SessionRepository(db)
    return await repo.get_all()


@router.get("/{session_id}")
async def get_session(session_id: str, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Returns a single session including the full message history."""
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session:
        raise NotFoundException(f"Session {session_id} not found.")
    return session


@router.post("/{session_id}/messages", status_code=201)
async def add_message(
    session_id: str,
    payload: AddMessageRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """Appends a user or assistant message to an existing session."""
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session:
        raise NotFoundException(f"Session {session_id} not found.")

    message = {
        "role": payload.role,
        "content": payload.content,
        "citations": payload.citations,
        "created_at": datetime.utcnow(),
    }
    await repo.add_message(session_id, message)
    return {"message": "Message added.", "session_id": session_id}


@router.delete("/{session_id}", status_code=200)
async def delete_session(session_id: str, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Deletes a chat session and all its messages."""
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    if not session:
        raise NotFoundException(f"Session {session_id} not found.")
    await repo.delete(session_id)
    return {"message": "Session deleted.", "session_id": session_id}
