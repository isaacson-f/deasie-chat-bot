from typing import Annotated, Collection, List
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
# from pymongo.collection import Collection
from clients.mongo_client import get_db
from models.models import User
import logging

logger = logging.getLogger(__name__)

class UserDAO:
    def __init__(self, db: Annotated[Database, Depends(get_db)]):
        self.db = db
        self.collection: Collection = self.db['users']
        logger.debug(f"Connected to user collection")


    def create_user(self, user: User) -> str:
        self.db.get_collection("")
        result = self.collection(user.model_dump())
        return str(result.inserted_id)

    # Returns None if user not found
    def get_user(self, user_id: str) -> User:
        logger.info(f"Getting user with ID: {user_id}")
        user_data = self.collection.find_one({"_id": user_id})
        if user_data:
            return User(**user_data)
        return None

    def update_user(self, user_id: str, user: User) -> bool:
        result = self.collection.update_one(
            {"_id": user_id},
            {"$set": user.model_dump()}
        )
        return result.modified_count > 0

    def delete_user(self, user_id: str) -> bool:
        result = self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        users = self.collection.find().skip(skip).limit(limit)
        return [User(**user) for user in users]

    def add_conversation_to_user(self, user_id: str, conversation_id: str) -> bool:
        result = self.collection.update_one(
            {"user_id": user_id},
            {"$push": {"conversations": conversation_id}}
        )
        return result.modified_count > 0

    def remove_conversation_from_user(self, user_id: str, conversation_id: str) -> bool:
        result = self.collection.update_one(
            {"user_id": user_id},
            {"$pull": {"conversations": conversation_id}}
        )
        return result.modified_count > 0
