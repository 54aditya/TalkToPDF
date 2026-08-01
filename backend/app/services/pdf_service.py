"""
PDF Processing Service
Handles PDF text extraction using PyMuPDF (fitz) and chunking
text into overlapping windows suitable for vector embedding.
"""
import fitz
from typing import List, Tuple
from dataclasses import dataclass
from app.core.logging import logger


@dataclass
class TextChunk:
    """A single text chunk extracted from a PDF."""
    text: str
    page: int
    chunk_index: int


def extract_text_from_pdf(storage_path: str) -> Tuple[List[Tuple[int, str]], int]:
    """
    Opens a PDF and extracts raw text per page.

    Args:
        storage_path: Absolute path to the stored PDF file.

    Returns:
        A tuple of (pages, page_count) where pages is a list of (page_number, text) tuples.

    Raises:
        ValueError: If the file cannot be opened or is not a valid PDF.
    """
    try:
        doc = fitz.open(storage_path)
        page_count = len(doc)
        pages = []
        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                pages.append((page_num + 1, text))
        doc.close()
        logger.info(f"Extracted text from {page_count} pages in {storage_path}")
        return pages, page_count
    except Exception as e:
        logger.error(f"Failed to extract text from PDF '{storage_path}': {str(e)}")
        raise ValueError(f"Could not process PDF file: {str(e)}")


def chunk_pages(
    pages: List[Tuple[int, str]],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[TextChunk]:
    """
    Splits page text into overlapping fixed-size character chunks.

    Each chunk carries page provenance metadata so citations can be
    reconstructed from the vector store at query time.

    Args:
        pages: List of (page_number, text) tuples from extract_text_from_pdf.
        chunk_size: Maximum character count per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        List of TextChunk objects ordered by page → chunk_index.
    """
    chunks: List[TextChunk] = []
    chunk_index = 0

    for page_num, page_text in pages:
        text = " ".join(page_text.split())
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(
                    TextChunk(
                        text=chunk_text,
                        page=page_num,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
            start += chunk_size - chunk_overlap

    logger.info(f"Generated {len(chunks)} text chunks from {len(pages)} pages")
    return chunks
