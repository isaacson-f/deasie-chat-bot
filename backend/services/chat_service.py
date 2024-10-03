import logging
import os
from typing import Annotated, Generator, List
from fastapi import Depends, HTTPException
from openai import OpenAI
from clients.chat_client import get_openai_client
from daos.conversation_dao import ConversationDAO
from daos.users_dao import UserDAO
from models.models import ChatMessage, Conversation, User
from util import value_from_validation_error
from dotenv import load_dotenv
from pydantic import ValidationError
load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
  def __init__(self, conversation_dao: Annotated[ConversationDAO, Depends(ConversationDAO)], user_dao: Annotated[UserDAO, Depends(UserDAO)], openai_client: Annotated[OpenAI, Depends(get_openai_client)]):
    self.conversation_dao: ConversationDAO = conversation_dao
    self.user_dao: UserDAO = user_dao
    self.openai_client: OpenAI = openai_client

  def chat(self, message: str, conversation_history: List[ChatMessage]) -> Generator[str, None, None]:
    
    response = self.openai_client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "system", "content": f"You are a helpful chat assistant that only responds in html. Format the response as html. This means coding blocks should be formatted with <code></code>. Make sure to use the correct syntax for the language, closing all tags. You must respond in proper html. The user's previous messages and responses are {conversation_history}. Use this as context to answer the user's question, as this is a follow up to the conversation."},
        {"role": "user", "content": message}
      ],
      stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            try:
              yield chunk.choices[0].delta.content
            except UnicodeEncodeError:
              logger.error(f"UnicodeEncodeError: {chunk.choices[0].delta.content}")
  
  #TODO: Error handling if user doesn't exist
  def create_conversation(self, user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    user = self.user_dao.get_user(user_id)
    if not user:
      raise HTTPException(status_code=404, detail="User not found")
    conversation_id = self.conversation_dao.create_conversation(conversation)
    conversation.conversation_id = conversation_id
    return conversation
  
  def get_conversations(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
    return self.conversation_dao.get_conversation_by_user_id(user_id, skip, limit)

  def get_conversation(self, conversation_id: str) -> Conversation:
    return self.conversation_dao.get_conversation(conversation_id)

  def add_message_to_conversation(self, conversation_id: str, message: ChatMessage) -> bool:
    return self.conversation_dao.add_message_to_conversation(conversation_id, message)
  
  def remove_message_from_conversation(self, conversation_id: str, message_id: str):
    return self.conversation_dao.remove_message_from_conversation(conversation_id, message_id)

  def delete_conversation(self, conversation_id: str) -> bool:
    return self.conversation_dao.delete_conversation(conversation_id)

