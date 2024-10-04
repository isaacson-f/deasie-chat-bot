import logging
import os
from typing import Annotated, AsyncGenerator, Dict, Generator, List
from fastapi import Depends, HTTPException
from openai import AsyncOpenAI, OpenAI, RateLimitError, InternalServerError, BadRequestError
from clients.chat_client import get_openai_client
from daos.conversation_dao import ConversationDAO
from daos.user_dao import UserDAO
from exceptions.custom_exceptions import ConversationNotFoundError, UserNotFoundError
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
    self.rate_limit_error_count = 0

  async def chat(self, message: str, conversation_history: List[ChatMessage]) -> AsyncGenerator[str, None]:
    try:
      messages = []
      num_history_messages = 0
      if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
      for past_message in conversation_history:
        if past_message.role == "bot":
          messages.append({"role": "system", "content": past_message.content})
        else:
          messages.append({"role": "user", "content": past_message.content})
        num_history_messages += 1
      messages.append({"role": "system", "content": f"You are a helpful chat assistant that only responds in markdown. Format the response as markdown. This means coding blocks should be formatted with ``````. Make sure to use the correct syntax for the language, closing all tags. You must respond in proper markdown. The user does not need to know that you are responding in markdown, they only need to read the formatted response. Do not tell them the format is markdown or the answer is formatted in any way. Use the previous conversation history to answer the user's question, as this is a follow up to the conversation."})
      messages.append({"role": "user", "content": message})
      logger.info(f"Messages: {messages}")
      response = await self.openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        stream=True
        )
      all_content = ""
      async for chunk in response:
          content = chunk.choices[0].delta.content
          if content is not None:
              all_content += content
              yield all_content
    except RateLimitError as e:
      self.rate_limit_error_count += 1
      logger.error(f"Error in chat: {e}")
      raise RateLimitError(f"Rate limit exceeded")
    except InternalServerError as e:
      logger.error(f"Error in chat: {e}")
      raise InternalServerError(f"Internal server error")
    except BadRequestError as e:
      logger.error(f"Error in chat: {e}")
      raise BadRequestError(f"Bad request")
  
  #TODO: Error handling if user doesn't exist
  def create_conversation(self, user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    user = self.user_dao.get_user(user_id)
    if not user:
      raise UserNotFoundError(f"User {user_id} not found")
    conversation_id = self.conversation_dao.create_conversation(conversation)
    conversation.conversation_id = conversation_id
    self.user_cache[user_id] = [conversation]
    return conversation
  
  def get_conversations_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
    if user_id not in self.user_cache:
      logger.info(f"User {user_id} not found in cache, getting from database...")
      conversations = self.conversation_dao.get_conversations_by_user_id(user_id, skip, limit)
      if len(conversations) == 0:
        raise UserNotFoundError(f"No conversations for user {user_id} found in cache or database")
      self.user_cache[user_id] = conversations
    else:
      return self.user_cache[user_id]

  def get_recent_conversation_by_user(self, user_id: str) -> Conversation:
    if self.user_cache.get(user_id,-1) == -1:
      logger.info(f"User {user_id} not found in cache, getting from database...")
      conversations: List[Conversation] = self.conversation_dao.get_conversations_by_user_id(user_id)
      if len(conversations) == 0:
        raise UserNotFoundError(f"No conversations for user {user_id} found in cache or database")
      return conversations[0]
    else:
      if len(self.user_cache[user_id]) == 0:
        return self.user_cache[user_id][0]
      logger.info(f"No conversations for user {user_id} found in cache or database")
      return None

  def add_message_to_conversation(self, conversation_id: str, message: ChatMessage) -> bool:
    user_id = conversation_id.split("-")[0]
    # check if user that started this conversation is in the cache
    if user_id not in self.user_cache:
      # if not in cache, get from database
      logger.info(f"User {user_id} not found in cache, getting from database...")
      user = self.user_dao.get_user(user_id)
      if user is None:
        raise UserNotFoundError(f"User {user_id} not found for conversation {conversation_id}")
    else:
      # if the user is in the cache, check if the conversation is in the cache
      conversations = self.user_cache[user_id]
      for user_convo in conversations:
        if user_convo.conversation_id == conversation_id:
          logger.info(f"Conversation {conversation_id} found in cache, adding message...")
          user_convo.messages.append(message)
          conversation = user_convo
      logger.info(f"Conversation {conversation_id} not found in cache, getting from database...")
      if conversation is None:
        # conversation not in cache, get from database
        conversation = self.conversation_dao.get_conversation(conversation_id)
        if conversation is None:
          raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
      self.user_cache[user_id] = [conversation]
      conversation.messages.append(message)
      return self.conversation_dao.add_message_to_conversation(conversation_id, message)

