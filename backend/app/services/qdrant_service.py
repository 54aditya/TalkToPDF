"""
Qdrant Vector Database Service
Manages creation, upsertion, search, and deletion of vector collections
in Qdrant — one collection per uploaded research document.
"""
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    ScoredPoint,
)
from app.core.config import settings
from app.core.logging import logger
from app.services.embedding_service import EMBEDDING_DIMENSION


def _get_sync_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)



def collection_name(doc_id: str) -> str:
    """Returns the Qdrant collection name for a given document ID."""
    return f"doc_{doc_id}"



def create_collection(doc_id: str) -> None:
    """
    Creates a new Qdrant collection for a document if it doesn't already exist.

    Args:
        doc_id: The MongoDB ObjectId string for the document.
    """
    client = _get_sync_client()
    name = collection_name(doc_id)
    try:
        existing = [c.name for c in client.get_collections().collections]
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {name}")
        else:
            logger.info(f"Qdrant collection already exists: {name}")
    finally:
        client.close()


def upsert_chunks(
    doc_id: str,
    chunk_texts: List[str],
    embeddings: List[List[float]],
    pages: List[int],
) -> None:
    """
    Upserts text chunk vectors into the document's Qdrant collection.

    Each point is stored with payload containing the source text and page
    number so it can be surfaced as a citation at query time.

    Args:
        doc_id: The document's MongoDB ObjectId string.
        chunk_texts: List of raw text strings (one per chunk).
        embeddings: Corresponding embedding vectors (same length as chunk_texts).
        pages: Corresponding 1-indexed page numbers (same length as chunk_texts).
    """
    client = _get_sync_client()
    name = collection_name(doc_id)
    try:
        points = [
            PointStruct(
                id=i,
                vector=embeddings[i],
                payload={
                    "doc_id": doc_id,
                    "text": chunk_texts[i],
                    "page": pages[i],
                },
            )
            for i in range(len(chunk_texts))
        ]

        if not points:
            logger.warning(f"No points to upsert for document {doc_id}")
            return

        client.upsert(collection_name=name, points=points)
        logger.info(f"Upserted {len(points)} vectors into collection {name}")
    finally:
        client.close()


def delete_collection(doc_id: str) -> None:
    """
    Deletes the entire Qdrant collection for a document.

    Called when a document is deleted from the system to prevent orphaned vectors.

    Args:
        doc_id: The document's MongoDB ObjectId string.
    """
    client = _get_sync_client()
    name = collection_name(doc_id)
    try:
        existing = [c.name for c in client.get_collections().collections]
        if name in existing:
            client.delete_collection(collection_name=name)
            logger.info(f"Deleted Qdrant collection: {name}")
        else:
            logger.warning(f"Qdrant collection {name} not found; skipping delete")
    finally:
        client.close()



async def search_similar_chunks(
    qdrant_client,
    doc_ids: List[str],
    query_vector: List[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Searches multiple document collections for chunks similar to the query vector.

    Args:
        qdrant_client: An AsyncQdrantClient instance (injected by FastAPI).
        doc_ids: List of document IDs to search across.
        query_vector: The embedded query vector.
        top_k: Number of top results to return per document collection.

    Returns:
        A list of result dicts sorted by score descending, each containing:
        { score, text, page, doc_id }
    """
    results: List[Dict[str, Any]] = []

    for doc_id in doc_ids:
        name = collection_name(doc_id)
        try:
            response = await qdrant_client.query_points(
                collection_name=name,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )
            for point in response.points:
                results.append(
                    {
                        "score": point.score,
                        "text": point.payload.get("text", ""),
                        "page": point.payload.get("page", 0),
                        "doc_id": doc_id,
                    }
                )
        except Exception as e:
            logger.warning(f"Qdrant search failed for collection {name}: {str(e)}")

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
