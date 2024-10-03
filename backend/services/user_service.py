from typing import Annotated, List
from fastapi import Depends
from models.models import User
from daos.users_dao import UserDAO

import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_dao: Annotated[UserDAO, Depends(UserDAO)]):
        self.user_dao = user_dao

    async def create_user(self, user: User) -> str:
        return self.user_dao.create_user(user)

    async def get_user(self, user_id: str) -> User:
        logger.info(f"Getting user with ID: {user_id}")
        return self.user_dao.get_user(user_id)

    async def update_user(self, user_id: str, user: User) -> bool:
        return self.user_dao.update_user(user_id, user)

    async def delete_user(self, user_id: str) -> bool:
        return self.user_dao.delete_user(user_id)

    async def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        return self.user_dao.list_users(skip, limit)

    async def add_conversation_to_user(self, user_id: str, conversation_id: str) -> bool:
        return self.user_dao.add_conversation_to_user(user_id, conversation_id)

    async def remove_conversation_from_user(self, user_id: str, conversation_id: str) -> bool:
        return self.user_dao.remove_conversation_from_user(user_id, conversation_id)
