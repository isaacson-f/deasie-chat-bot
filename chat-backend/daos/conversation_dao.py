import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Annotated, List, Optional
from fastapi import Depends
from pymongo.database import Database
from pymongo.collection import Collection
from clients.mongo_client import get_mongo_client
from models.models import ChatMessage, Conversation
from exceptions.custom_exceptions import DatabaseError

logger = logging.getLogger(__name__)

class ConversationDAO:
    def __init__(self, client: Annotated[MongoClient, Depends(get_mongo_client)]):
        self.db = client.get_database("chat-bot")
        self.collection: Collection = self.db['conversations']

    def create_conversation(self, conversation: Conversation) -> str:
        try:
            logger.info(f"Creating conversation: {conversation.conversation_id}")
            result = self.collection.insert_one(conversation.model_dump(by_alias=True))
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Failed to create conversation: {e}")
            raise DatabaseError("Failed to create conversation")
    
    def get_conversations_by_user_id(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
        try:
            conversation_cursor = self.collection.find({"_id": {"$regex": f"^{user_id}-"}}).skip(skip).limit(limit)
            conversations = [Conversation(**data, user_id=user_id) for data in conversation_cursor]
            return conversations
        except PyMongoError as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            raise DatabaseError(f"Failed to get conversations for user {user_id}")

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        try:
            logger.info(f"Getting conversation {conversation_id}")
            conversation_data = self.collection.find_one({"_id": conversation_id})
            return Conversation(**conversation_data) if conversation_data else None
        except PyMongoError as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise DatabaseError(f"Failed to get conversation {conversation_id}")

    def update_conversation(self, conversation_id: str, messages: List[ChatMessage]) -> bool:
        try:
            logger.info(f"Updating conversation {conversation_id}")
            result = self.collection.update_one(
                {"_id": conversation_id},
                {"$set": {"messages": [message.model_dump(by_alias=True) for message in messages]}}
            )
            return result.matched_count > 0   
        except PyMongoError as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            raise DatabaseError(f"Failed to update conversation {conversation_id}")

    def add_message_to_conversation(self, conversation_id: str, message: ChatMessage) -> bool:
        try:
            logger.info(f"Adding message to conversation {conversation_id}")
            result = self.collection.update_one(
                {"_id": conversation_id},
                {"$push": {"messages": message.model_dump(by_alias=True)}}
            )

            return result.matched_count > 0
        except PyMongoError as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            raise DatabaseError(f"Failed to add message to conversation {conversation_id}")
    
    def remove_message_from_conversation(self, conversation_id: str, message_id: str) -> bool:
        try:
            logger.info(f"Removing message {message_id} from conversation {conversation_id}")
            result = self.collection.update_one(
                {"_id": conversation_id},
                {"$pull": {"messages": {"_id": message_id}}}
            )
            return result.matched_count > 0   
        except PyMongoError as e:
            logger.error(f"Failed to remove message {message_id} from conversation {conversation_id}: {e}")
            raise DatabaseError(f"Failed to remove message from conversation {conversation_id}")


    def list_conversations(self, skip: int = 0, limit: int = 10) -> List[Conversation]:
        try:
            logger.info(f"Listing conversations")
            conversations = self.collection.find().skip(skip).limit(limit)
            return [Conversation(**conv) for conv in conversations]
        except PyMongoError as e:
            logger.error(f"Failed to list conversations: {e}")
            raise DatabaseError("Failed to list conversations")
