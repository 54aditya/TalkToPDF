import time
from bson import ObjectId
import pymongo
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.core.logging import logger


@celery_app.task(name="app.workers.tasks.process_document_task")
def process_document_task(doc_id: str) -> str:
    """Background task to extract PDF text, generate embeddings, and index in Qdrant."""
    logger.info(f"Starting background processing for document: {doc_id}")

    # Connect synchronously to MongoDB inside Celery worker
    client = pymongo.MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    collection = db["documents"]

    try:
        # 1. Update status to 'processing'
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": "processing"}}
        )
        logger.info(f"Document {doc_id} status set to 'processing'")

        # 2. Simulate PDF parsing & embedding creation (Phase 5-7 work stub)
        time.sleep(5) 

        # 3. Update status to 'processed'
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {
                "$set": {
                    "status": "processed",
                    "page_count": 10,  # Stub page count
                    "summary": "This is a placeholder summary generated during document upload extraction."
                }
            }
        )
        logger.info(f"Document {doc_id} successfully parsed and indexed.")
        return f"Successfully processed document {doc_id}"

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {str(e)}", exc_info=True)
        # Set status to 'failed'
        collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": "failed"}}
        )
        raise e
    finally:
        client.close()
