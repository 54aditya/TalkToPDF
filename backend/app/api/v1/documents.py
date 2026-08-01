import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import settings
from app.core.exceptions import ValidationException, NotFoundException
from app.database.connection import get_mongodb
from app.database.repository import DocumentRepository
from app.workers.tasks import process_document_task
from app.services.qdrant_service import delete_collection
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=dict, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    """Uploads a PDF, saves it to disk, saves metadata in MongoDB, and schedules background parsing."""
    if not file.filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise ValidationException("Only PDF documents are supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{os.path.basename(file.filename)}"
    storage_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    logger.info(f"Uploading file: {file.filename} saving to {storage_path}")
    try:
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to write file to disk: {str(e)}")
        raise ValidationException("Could not write document to file storage.")
    finally:
        await file.close()

    file_size = os.path.getsize(storage_path)

    repo = DocumentRepository(db)
    doc_data = {
        "filename": file.filename,
        "file_size": file_size,
        "storage_path": storage_path,
        "status": "pending",
        "page_count": None,
        "summary": None,
    }
    
    created_doc = await repo.create(doc_data)
    doc_id = created_doc["_id"]

    try:
        process_document_task.delay(doc_id)
        logger.info(f"Scheduled background parser for document {doc_id}")
    except Exception as e:
        logger.error(f"Failed to queue background celery task for {doc_id}: {str(e)}")
        await repo.update(doc_id, {"status": "failed"})

    return {
        "message": "File uploaded and parsing task scheduled.",
        "document": created_doc
    }


@router.get("", response_model=List[dict])
async def list_documents(db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Retrieves all publications uploaded by the user."""
    repo = DocumentRepository(db)
    return await repo.get_all()


@router.get("/{document_id}", response_model=dict)
async def get_document(document_id: str, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Retrieves processing status and metadata details for a specific document."""
    repo = DocumentRepository(db)
    doc = await repo.get_by_id(document_id)
    if not doc:
        raise NotFoundException(f"Document with ID {document_id} not found.")
    return doc


@router.delete("/{document_id}", status_code=200)
async def delete_document(document_id: str, db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Deletes a document, its corresponding disk storage, and database records."""
    repo = DocumentRepository(db)
    doc = await repo.get_by_id(document_id)
    if not doc:
        raise NotFoundException(f"Document with ID {document_id} not found.")

    storage_path = doc.get("storage_path")
    if storage_path and os.path.exists(storage_path):
        try:
            os.remove(storage_path)
            logger.info(f"Deleted storage file at {storage_path}")
        except Exception as e:
            logger.error(f"Failed to delete disk storage file: {str(e)}")

    deleted = await repo.delete(document_id)
    
    try:
        delete_collection(document_id)
        logger.info(f"Deleted Qdrant collection for document {document_id}")
    except Exception as e:
        logger.warning(f"Failed to delete Qdrant collection for document {document_id}: {str(e)}")
    
    return {"message": "Document successfully deleted.", "document_id": document_id}
