import logging
from typing import Annotated, List, Optional
from fastapi import Depends
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection
from clients.mongo_client import get_mongo_client
from models.models import User
from exceptions.custom_exceptions import DatabaseError

logger = logging.getLogger(__name__)

class UserDAO:
    def __init__(self, client: Annotated[MongoClient, Depends(get_mongo_client)]):
        self.db: Database = client.get_database("chat-bot")
        self.collection: Collection = self.db['users']
        logger.debug("Connected to user collection")

    def create_user(self, user: User) -> str:
        try:
            result = self.collection.insert_one(user.model_dump(by_alias=True))
            logger.info(f"User created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError("Failed to create user")

    def get_user(self, user_id: str) -> Optional[User]:
        try:
            user_data = self.collection.find_one({"_id": user_id})
            return User(**user_data) if user_data else None
        except PyMongoError as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise DatabaseError(f"Failed to get user {user_id}")

    def update_user(self, user_id: str, user: User) -> bool:
        try:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$set": user.model_dump()}
            )
            return result.matched_count > 0   
        except PyMongoError as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise DatabaseError(f"Failed to update user {user_id}")

    def delete_user(self, user_id: str) -> bool:
        try:
            result = self.collection.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user {user_id}")

    def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        try:
            users = self.collection.find().skip(skip).limit(limit)
            return [User(**user) for user in users]
        except PyMongoError as e:
            logger.error(f"Failed to list users: {e}")
            raise DatabaseError("Failed to list users")

    def add_conversation_to_user(self, user_id: str, conversation_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$push": {"conversations": conversation_id}}
            )
            return result.matched_count > 0   
        
        except PyMongoError as e:
            logger.error(f"Failed to add conversation {conversation_id} to user {user_id}: {e}")
            raise DatabaseError(f"Failed to add conversation to user {user_id}")

    def remove_conversation_from_user(self, user_id: str, conversation_id: str) -> bool:
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$pull": {"conversations": conversation_id}}
            )
            return result.matched_count > 0   

        except PyMongoError as e:
            logger.error(f"Failed to remove conversation {conversation_id} from user {user_id}: {e}")
            raise DatabaseError(f"Failed to remove conversation from user {user_id}")
