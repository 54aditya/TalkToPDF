"""
Chat API Router
Provides RAG-powered Q&A over uploaded research documents.

POST /chat/query — Streams Gemini answers grounded in Qdrant vector search.
GET  /chat/context/{document_id} — Returns doc metadata for the chat header.
"""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from qdrant_client import AsyncQdrantClient

from app.core.exceptions import NotFoundException
from app.database.connection import get_mongodb, get_qdrant
from app.database.repository import DocumentRepository
from app.schemas.chat import ChatQueryRequest
from app.services.embedding_service import embed_query
from app.services.qdrant_service import search_similar_chunks
from app.services.llm_service import stream_rag_answer
from app.core.logging import logger


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query")
async def query_documents(
    request: ChatQueryRequest,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
):
    """
    Performs RAG (Retrieval-Augmented Generation) against one or more documents.

    Flow:
        1. Validate that all requested document IDs exist and are 'processed'
        2. Embed the user query using Gemini text-embedding-004
        3. Search Qdrant across all document collections for top-K relevant chunks
        4. Build a grounded prompt and stream Gemini's answer as SSE

    The response is a Server-Sent Events stream. Each event is a JSON line:
        data: {"type": "citations", "data": [...]}
        data: {"type": "token", "content": "..."}
        data: {"type": "done"}
    """
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document_id must be provided.")

    repo = DocumentRepository(db)
    doc_filenames: dict[str, str] = {}

    for doc_id in request.document_ids:
        doc = await repo.get_by_id(doc_id)
        if not doc:
            raise NotFoundException(f"Document {doc_id} not found.")
        if doc["status"] != "processed":
            raise HTTPException(
                status_code=422,
                detail=f"Document '{doc['filename']}' is not yet processed (status: {doc['status']}). Please wait."
            )
        doc_filenames[doc_id] = doc["filename"]

    logger.info(f"Embedding query: '{request.query[:80]}...'")
    try:
        query_vector = embed_query(request.query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding service unavailable: {str(e)}")

    retrieved_chunks = await search_similar_chunks(
        qdrant_client=qdrant,
        doc_ids=request.document_ids,
        query_vector=query_vector,
        top_k=request.top_k,
    )

    if not retrieved_chunks:
        async def empty_stream():
            yield f"data: {json.dumps({'type': 'token', 'content': 'No relevant content found in the selected documents.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    citations = [
        {
            "doc_id": chunk["doc_id"],
            "filename": doc_filenames.get(chunk["doc_id"], "Unknown"),
            "page": chunk["page"],
            "snippet": chunk["text"][:300],
            "score": round(chunk["score"], 4),
        }
        for chunk in retrieved_chunks
    ]

    async def event_stream():
        yield f"data: {json.dumps({'type': 'citations', 'data': citations})}\n\n"

        async for sse_payload in stream_rag_answer(request.query, retrieved_chunks, doc_filenames):
            yield f"data: {sse_payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/context/{document_id}")
async def get_document_context(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """Returns metadata for a document used to populate the chat header."""
    repo = DocumentRepository(db)
    doc = await repo.get_by_id(document_id)
    if not doc:
        raise NotFoundException(f"Document {document_id} not found.")
    return {
        "_id": doc["_id"],
        "filename": doc["filename"],
        "page_count": doc.get("page_count"),
        "summary": doc.get("summary"),
        "status": doc["status"],
    }
