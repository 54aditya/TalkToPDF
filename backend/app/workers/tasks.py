"""
Celery Background Tasks
Implements the real document processing pipeline:
  1. Extract text from PDF using PyMuPDF
  2. Chunk text into overlapping windows
  3. Embed chunks with Gemini text-embedding-004
  4. Index vectors + payloads into Qdrant
  5. Generate a document summary via Gemini
  6. Persist page_count and summary back to MongoDB
"""
import pymongo
from bson import ObjectId
import google.generativeai as genai

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.logging import logger
from app.services.pdf_service import extract_text_from_pdf, chunk_pages
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import create_collection, upsert_chunks


genai.configure(api_key=settings.GEMINI_API_KEY)


def _generate_summary(pages_text: str) -> str:
    """Uses Gemini Flash to produce a short summary of the document."""
    try:
        excerpt = pages_text[:8000]
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            f"Write a concise 3-sentence academic summary of the following research paper excerpt:\n\n{excerpt}"
        )
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Summary generation failed: {str(e)}")
        return "Summary not available."


@celery_app.task(name="app.workers.tasks.process_document_task", bind=True, max_retries=3)
def process_document_task(self, doc_id: str) -> str:
    """
    Full document processing pipeline as a Celery background task.

    Steps:
        1. Mark document as 'processing' in MongoDB
        2. Extract text from PDF pages using PyMuPDF
        3. Chunk text with overlap
        4. Generate Gemini embeddings for all chunks
        5. Create Qdrant collection and upsert vectors
        6. Generate a summary with Gemini Flash
        7. Update MongoDB with page_count, summary, and status='processed'
    """
    logger.info(f"Starting background processing for document: {doc_id}")

    client = pymongo.MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    collection = db["documents"]

    try:
        doc = collection.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            logger.error(f"Document {doc_id} not found in MongoDB; aborting task.")
            return f"Aborted: document {doc_id} not found."

        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": "processing"}},
        )
        logger.info(f"Document {doc_id} status → 'processing'")

        storage_path: str = doc["storage_path"]

        pages, page_count = extract_text_from_pdf(storage_path)
        if not pages:
            raise ValueError("No readable text found in the PDF.")

        chunks = chunk_pages(pages, chunk_size=800, chunk_overlap=100)
        chunk_texts = [c.text for c in chunks]
        chunk_pages_list = [c.page for c in chunks]

        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = embed_texts(chunk_texts, task_type="RETRIEVAL_DOCUMENT")

        create_collection(doc_id)
        upsert_chunks(doc_id, chunk_texts, embeddings, chunk_pages_list)

        full_text = " ".join([text for _, text in pages])
        summary = _generate_summary(full_text)

        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "processed",
                    "page_count": page_count,
                    "summary": summary,
                }
            },
        )
        logger.info(f"Document {doc_id} successfully processed: {page_count} pages, {len(chunks)} chunks.")
        return f"Successfully processed document {doc_id}"

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {str(e)}", exc_info=True)
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": "failed"}},
        )
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

    finally:
        client.close()
