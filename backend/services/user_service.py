from typing import Annotated, List
from fastapi import Depends
from exceptions.custom_exceptions import UserNotFoundError
from models.models import User
from daos.user_dao import UserDAO

import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_dao: Annotated[UserDAO, Depends(UserDAO)]):
        self.user_dao = user_dao

    def create_user(self, user: User) -> str:
        logger.info(f"Creating user with ID: {user.user_id}")
        return self.user_dao.create_user(user)

    def get_user(self, user_id: str) -> User:
        logger.info(f"Getting user with ID: {user_id}")
        return self.user_dao.get_user(user_id)

    def update_user(self, user_id: str, user: User) -> User:
        logger.info(f"Updating user with ID: {user_id}")
        user = self.user_dao.update_user(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def delete_user(self, user_id: str) -> bool:
        logger.info(f"Deleting user with ID: {user_id}")
        return self.user_dao.delete_user(user_id)

    def list_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        logger.info(f"Listing users with skip: {skip} and limit: {limit}")
        return self.user_dao.list_users(skip, limit)

    def add_conversation_to_user(self, user_id: str, conversation_id: str) -> bool:
        logger.info(f"Adding conversation with ID: {conversation_id} to user with ID: {user_id}")
        user = self.user_dao.add_conversation_to_user(user_id, conversation_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    def remove_conversation_from_user(self, user_id: str, conversation_id: str) -> User:
        logger.info(f"Removing conversation with ID: {conversation_id} from user with ID: {user_id}")
        user = self.user_dao.remove_conversation_from_user(user_id, conversation_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
