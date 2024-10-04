import logging
import os
from typing import Annotated, AsyncGenerator, Dict, Generator, List
from fastapi import Depends, HTTPException
from openai import AsyncOpenAI, OpenAI
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
    self.openai_client: AsyncOpenAI = openai_client
    # map of the user_id to the conversation
    self.user_cache: Dict[str, List[Conversation]] = {}


  async def chat(self, message: str, conversation_history: List[ChatMessage]) -> AsyncGenerator[str, None]:
    response = await self.openai_client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "system", "content": f"You are a helpful chat assistant that only responds in markdown. Format the response as markdown. This means coding blocks should be formatted with ``````. Make sure to use the correct syntax for the language, closing all tags. You must respond in proper markdown. The user does not need to know that you are responding in markdown, they only need to read the formatted response. Do not tell them the format is markdown or the answer is formatted in any way. The user's previous messages and responses are {conversation_history}. Use this as context to answer the user's question, as this is a follow up to the conversation."},
        {"role": "user", "content": message}
      ],
      stream=True
    )
    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content is not None:
            all_content += content
            yield all_content
        # if chunk.choices[0].delta.content is not None:
        #     try:
        #       yield chunk.choices[0].delta.content
        #     except UnicodeEncodeError:
        #       logger.error(f"UnicodeEncodeError: {chunk.choices[0].delta.content}")
  
  #TODO: Error handling if user doesn't exist
  def create_conversation(self, user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    user = self.user_dao.get_user(user_id)
    if not user:
      raise HTTPException(status_code=404, detail="User not found")
    conversation_id = self.conversation_dao.create_conversation(conversation)
    conversation.conversation_id = conversation_id
    self.user_cache[user_id] = [conversation]
    return conversation
  
  def get_conversations(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
    if user_id not in self.user_cache:
      return self.conversation_dao.get_conversations_by_user_id(user_id, skip, limit)
    else:
      return self.user_cache[user_id]

  def get_recent_conversation_by_user(self, user_id: str) -> Conversation:
    if self.user_cache.get(user_id,-1) == -1:
      logger.info(f"User {user_id} not found in cache, getting from database...")
      conversations: List[Conversation] = self.conversation_dao.get_conversations_by_user_id(user_id)
      if len(conversations) == 0:
        logger.info(f"No conversations for user {user_id} not found in cache or database")
        return None
      return conversations[0]
    else:
      if len(self.user_cache[user_id]) == 0:
        return self.user_cache[user_id][0]
      logger.info(f"No conversations for user {user_id} not found in cache or database")
      return None

  def add_message_to_conversation(self, conversation_id: str, message: ChatMessage) -> bool:
    user_id = conversation_id.split("-")[0]
    if user_id not in self.user_cache:
      logger.info(f"User {user_id} not found in cache, getting from database...")
      conversation = self.conversation_dao.get_conversation(conversation_id)
      self.user_cache[user_id] = [conversation]
    else:
      conversations = self.user_cache[user_id]
      for conversation in conversations:
        if conversation.conversation_id == conversation_id:
          logger.info(f"Conversation {conversation_id} found in cache")
          conversation.messages.append(message)
          return self.conversation_dao.add_message_to_conversation(conversation_id, message)
      logger.info(f"Conversation {conversation_id} not found in cache, getting from database...")
      conversation = self.conversation_dao.get_conversation(conversation_id)
      self.user_cache[user_id] = [conversation]
    conversation.messages.append(message)
    return self.conversation_dao.add_message_to_conversation(conversation_id, message)
  
  def remove_message_from_conversation(self, conversation_id: str, message_id: str):
    return self.conversation_dao.remove_message_from_conversation(conversation_id, message_id)

  def delete_conversation(self, conversation_id: str) -> bool:
    return self.conversation_dao.delete_conversation(conversation_id)

