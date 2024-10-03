import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)

from typing import Annotated, List
from bson import ObjectId
from fastapi import Depends
from pymongo.database import Database
from pymongo.collection import Collection
from clients.mongo_client import get_mongo_client
from models.models import ChatMessage, Conversation

class ConversationDAO:
    def __init__(self, client: Annotated[MongoClient, Depends(get_mongo_client)]):
        self.db = client.get_database("chat-bot")
        self.collection: Collection = self.db['conversations']
        logger.debug(f"Connected to conversation collection")

    def create_conversation(self, conversation: Conversation) -> str:
        result = self.collection.insert_one(conversation.model_dump(by_alias=True))
        return str(result.inserted_id)
    
    def get_conversation_by_user_id(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
        conversation_cursor = self.collection.find({"_id": {"$regex": f"^{user_id}-"}}).skip(skip).limit(limit)
        conversations = []
        for data in conversation_cursor:
            conversations.append(Conversation(**data))
        return conversations

    def get_conversation(self, conversation_id: str) -> Conversation:
        conversation_data = self.collection.find_one({"_id": conversation_id})
        if conversation_data:
            return Conversation(**conversation_data)
        return None

    def update_conversation(self, conversation_id: str, messages: List[ChatMessage]) -> bool:
        result = self.collection.update_one(
            {"_id": conversation_id},
            {"$set": {"messages": [message.model_dump() for message in messages]}}
        )
        return result.modified_count > 0

    def add_message_to_conversation(self, conversation_id: str, message: ChatMessage) -> bool:
        result = self.collection.update_one(
            {"_id": conversation_id},
            {"$push": {"messages": message.model_dump()}}
        )
        return result.modified_count > 0
    
    def remove_message_from_conversation(self, conversation_id: str, message_id: str) -> bool:
        result = self.collection.update_one(
            {"_id": conversation_id},
            {"$pull": {"messages": {"_id": message_id}}}
        )
        return result.modified_count > 0

    def delete_conversation(self, conversation_id: str) -> bool:
        result = self.collection.delete_one({"_id": conversation_id})
        return result.deleted_count > 0

    def list_conversations(self, skip: int = 0, limit: int = 10) -> List[Conversation]:
        conversations = self.collection.find().skip(skip).limit(limit)
        return [Conversation(**conv) for conv in conversations]
