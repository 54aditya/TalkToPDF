from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import DatabaseException


class DocumentRepository:
    """Encapsulates CRUD operations for Documents in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["documents"]

    def _serialize_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Converts MongoDB ObjectId to string for api responses."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            doc_data = {
                **data,
                "created_at": data.get("created_at") or datetime.utcnow(),
                "updated_at": data.get("updated_at") or datetime.utcnow(),
            }
            result = await self.collection.insert_one(doc_data)
            doc_data["_id"] = str(result.inserted_id)

            return doc_data
        except Exception as e:
            raise DatabaseException(f"Failed to create document: {str(e)}")

    async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            if not ObjectId.is_valid(doc_id):
                return None
            doc = await self.collection.find_one({"_id": ObjectId(doc_id)})
            return self._serialize_id(doc) if doc else None
        except Exception as e:
            raise DatabaseException(f"Failed to fetch document: {str(e)}")

    async def get_all(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find(query or {})
            docs = await cursor.to_list(length=100)
            return [self._serialize_id(doc) for doc in docs]
        except Exception as e:
            raise DatabaseException(f"Failed to fetch documents: {str(e)}")

    async def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        try:
            if not ObjectId.is_valid(doc_id):
                return False
            update_data = {**data, "updated_at": datetime.utcnow()}
            result = await self.collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseException(f"Failed to update document: {str(e)}")

    async def delete(self, doc_id: str) -> bool:
        try:
            if not ObjectId.is_valid(doc_id):
                return False
            result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseException(f"Failed to delete document: {str(e)}")
