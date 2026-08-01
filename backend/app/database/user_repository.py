"""
User Repository
Handles MongoDB CRUD operations for user accounts.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import DatabaseException


class UserRepository:
    """Encapsulates CRUD operations for Users in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["users"]

    def _serialize(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, name: str, email: str, hashed_password: str) -> Dict[str, Any]:
        try:
            user_data = {
                "name": name,
                "email": email.lower(),
                "hashed_password": hashed_password,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await self.collection.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            return user_data
        except Exception as e:
            raise DatabaseException(f"Failed to create user: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await self.collection.find_one({"email": email.lower()})
            return self._serialize(doc) if doc else None
        except Exception as e:
            raise DatabaseException(f"Failed to fetch user by email: {str(e)}")

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            if not ObjectId.is_valid(user_id):
                return None
            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            return self._serialize(doc) if doc else None
        except Exception as e:
            raise DatabaseException(f"Failed to fetch user by ID: {str(e)}")
