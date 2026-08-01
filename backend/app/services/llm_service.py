"""
LLM Service
Wraps Google Gemini for RAG-based Q&A with streamed responses.
Builds a grounded prompt from retrieved Qdrant context chunks and
yields answer tokens for Server-Sent Events (SSE) streaming.
"""
import json
from typing import List, Dict, Any, AsyncIterator
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import logger


genai.configure(api_key=settings.GEMINI_API_KEY)

_CHAT_MODEL = "gemini-2.5-flash"

_SYSTEM_PROMPT = """\
You are a highly precise academic research assistant. 
Answer questions exclusively based on the provided research paper excerpts below. 
If the answer cannot be found in the provided context, explicitly state that.
Always reference the specific paper and page number when citing information.
Keep answers clear, concise, and academically rigorous.
"""


def _build_context_block(retrieved_chunks: List[Dict[str, Any]], doc_filenames: Dict[str, str]) -> str:
    """
    Formats retrieved Qdrant chunks into a numbered context block for the prompt.

    Args:
        retrieved_chunks: List of { score, text, page, doc_id } dicts from Qdrant.
        doc_filenames: Map of doc_id → filename for human-readable citations.

    Returns:
        Formatted multi-line context string.
    """
    lines = ["=== RESEARCH PAPER CONTEXT ==="]
    for i, chunk in enumerate(retrieved_chunks, start=1):
        filename = doc_filenames.get(chunk["doc_id"], f"Document {chunk['doc_id']}")
        lines.append(
            f"\n[Context {i}] Source: {filename}, Page {chunk['page']}\n"
            f"{chunk['text']}\n"
            f"{'─' * 60}"
        )
    return "\n".join(lines)


async def stream_rag_answer(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    doc_filenames: Dict[str, str],
) -> AsyncIterator[str]:
    """
    Streams a Gemini RAG answer token-by-token as SSE data chunks.

    Each yielded string is a JSON-encoded SSE event payload:
      - `{"type": "token", "content": "..."}`  — streamed text token
      - `{"type": "done"}`                      — stream complete signal
      - `{"type": "error", "content": "..."}`   — error signal

    Args:
        query: The user's research question.
        retrieved_chunks: Ranked context chunks from Qdrant.
        doc_filenames: Map of doc_id → filename for citation rendering.

    Yields:
        JSON-encoded SSE data strings (to be wrapped by the FastAPI endpoint).
    """
    context_block = _build_context_block(retrieved_chunks, doc_filenames)

    full_prompt = (
        f"{_SYSTEM_PROMPT}\n\n"
        f"{context_block}\n\n"
        f"=== QUESTION ===\n{query}\n\n"
        f"=== ANSWER ==="
    )

    try:
        model = genai.GenerativeModel(_CHAT_MODEL)
        response = model.generate_content(full_prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield json.dumps({"type": "token", "content": chunk.text})

        yield json.dumps({"type": "done"})

    except Exception as e:
        logger.error(f"LLM streaming error: {str(e)}", exc_info=True)
        yield json.dumps({"type": "error", "content": "The AI model encountered an error. Please try again."})
