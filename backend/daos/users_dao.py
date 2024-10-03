from typing import Annotated, Collection, List
from bson import ObjectId
from fastapi import Depends
from pymongo import MongoClient
from pymongo.database import Database
# from pymongo.collection import Collection
from clients.mongo_client import get_mongo_client
from models.models import User
import logging

logger = logging.getLogger(__name__)

class UserDAO:
    def __init__(self, client: Annotated[MongoClient, Depends(get_mongo_client)]):
        self.db: Database = client.get_database("chat-bot")
        self.collection: Collection = self.db['users']
        logger.debug(f"Connected to user collection")


    def create_user(self, user: User) -> str:
        logger.info(f"Creating user: {user}")
        result = self.collection.insert_one(user.model_dump(by_alias=True))
        logger.info(f"User created with ID: {result.inserted_id}")
        return str(result.inserted_id)

    # Returns None if user not found
    def get_user(self, user_id: str) -> User:
        logger.info(f"Getting user with ID: {user_id}")
        user_data = self.collection.find_one({"_id": user_id})
        if user_data:
            logger.info(f"User found: {user_data}")
            return User(**user_data)
        logger.info(f"User {user_id} not found")
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
