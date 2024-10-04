from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
  role: Optional[str] = Field(default="user", description="The role of the message")
  message_id: Optional[str] = Field(default=str(uuid.uuid4()), description="The ID of the message")
  content: str

class Conversation(BaseModel):
  user_id: Optional[str] = Field(exclude=True, description="The ID of the user")
  # The ID of the conversation; setting the alias to _id allows the field to be used as the MongoDB _id field
  conversation_id: Optional[str] = Field(default=None, description="The ID of the conversation", alias="_id")
  messages: Optional[List[ChatMessage]] = Field(default=[], description="The messages in the conversation")

  # Allows us to set conversation_id if not already set and cluster by user_id
  @model_validator(mode='after')
  def validate_conversation_id(self) -> str:
    if not self.conversation_id:
      self.conversation_id = f"{self.user_id}-{str(uuid.uuid4())}"
    if not self.user_id:
      self.user_id = self.conversation_id.split("-")[0]
    if not self.conversation_id and not self.user_id:
      raise ValueError("conversation_id or user_id must be set")
    return self

class User(BaseModel):
  user_id: str = Field(alias="_id")
  conversations: Optional[List[Conversation]] = Field(default=[], description="The conversations of the user")

