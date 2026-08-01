"""
Embedding Service
Wraps the Google Gemini text-embedding-004 model to produce dense
vector representations of text chunks for semantic search in Qdrant.
"""
from typing import List
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger


genai.configure(api_key=settings.GEMINI_API_KEY)

EMBEDDING_DIMENSION = 768
EMBEDDING_MODEL = "models/gemini-embedding-001"
_BATCH_SIZE = 100


def embed_texts(texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
    """
    Generates dense embeddings for a list of text strings using Gemini.

    Internally batches requests to stay within the API's per-call limit.

    Args:
        texts: List of text strings to embed.
        task_type: Gemini task type hint. Use 'RETRIEVAL_DOCUMENT' for
                   indexing and 'RETRIEVAL_QUERY' for query-time embedding.

    Returns:
        List of float vectors, one per input text, each of length EMBEDDING_DIMENSION.

    Raises:
        RuntimeError: If the Gemini API call fails.
    """
    if not texts:
        return []

    all_embeddings: List[List[float]] = []

    import time
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        
        retries = 6
        delay = 2.0
        success = False
        
        for attempt in range(retries):
            try:
                result = genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=batch,
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIMENSION,
                )
                all_embeddings.extend(result["embedding"])
                success = True
                break
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg or "resource" in err_msg or "exhausted" in err_msg:
                    logger.warning(
                        f"Gemini Rate Limit hit for batch {i // _BATCH_SIZE}. "
                        f"Retrying in {delay}s... (Attempt {attempt+1}/{retries})"
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(f"Gemini embedding API call failed for batch {i // _BATCH_SIZE}: {str(e)}")
                    raise RuntimeError(f"Embedding generation failed: {str(e)}")
                    
        if not success:
            logger.error(f"Gemini embedding rate limit retries exhausted for batch {i // _BATCH_SIZE}")
            raise RuntimeError("Embedding generation failed: Rate limit retry attempts exhausted.")

    logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
    return all_embeddings


def embed_query(query: str) -> List[float]:
    """
    Embeds a single query string using the RETRIEVAL_QUERY task type.

    Args:
        query: The user's search query.

    Returns:
        A single float vector of length EMBEDDING_DIMENSION.
    """
    result = embed_texts([query], task_type="RETRIEVAL_QUERY")
    return result[0]
