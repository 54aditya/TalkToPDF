"""
Session Repository
CRUD operations for chat sessions stored in MongoDB.
Each session holds document references and a message history.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import DatabaseException


class SessionRepository:
    """Encapsulates CRUD operations for chat sessions in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["sessions"]

    def _serialize(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, document_ids: List[str], title: str) -> Dict[str, Any]:
        try:
            session = {
                "title": title,
                "document_ids": document_ids,
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await self.collection.insert_one(session)
            session["_id"] = str(result.inserted_id)
            return session
        except Exception as e:
            raise DatabaseException(f"Failed to create session: {str(e)}")

    async def get_all(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.collection.find({}, {"messages": 0}).sort("updated_at", -1)
            docs = await cursor.to_list(length=50)
            return [self._serialize(d) for d in docs]
        except Exception as e:
            raise DatabaseException(f"Failed to fetch sessions: {str(e)}")

    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            if not ObjectId.is_valid(session_id):
                return None
            doc = await self.collection.find_one({"_id": ObjectId(session_id)})
            return self._serialize(doc) if doc else None
        except Exception as e:
            raise DatabaseException(f"Failed to fetch session: {str(e)}")

    async def add_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        try:
            if not ObjectId.is_valid(session_id):
                return False
            result = await self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseException(f"Failed to add message: {str(e)}")

    async def delete(self, session_id: str) -> bool:
        try:
            if not ObjectId.is_valid(session_id):
                return False
            result = await self.collection.delete_one({"_id": ObjectId(session_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseException(f"Failed to delete session: {str(e)}")
