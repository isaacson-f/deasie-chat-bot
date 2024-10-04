import logging
from typing import Annotated, List
from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, FastAPI, Path, Query, WebSocket, WebSocketException, status
from fastapi.websockets import WebSocketState

from models.models import ChatMessage, Conversation, User
from services.chat_service import ChatService
from services.user_service import UserService


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

logger = logging.getLogger(__name__)



async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@router.websocket("/{user_id}")
async def websocket(websocket: WebSocket, 
                    chat_service: Annotated[ChatService, Depends(ChatService)], 
                    user_service: Annotated[UserService, Depends(UserService)],
                    user_id: Annotated[str, Path()],
                    conversation_id: Annotated[str, Path()]):
    
    cur_user = await user_service.get_user(user_id)
    if cur_user == None:
        logger.info(f"User {user_id} not found, creating...")
        user = User(_id=user_id)
        cur_user = await user_service.create_user(user)

    # Check if conversation exists, if not create it
    conversation = chat_service.get_recent_conversation_by_user(user_id)
    if not conversation:
        conversation = chat_service.create_conversation(user_id)
    
    await websocket.accept()
    while True:
        # Check if user exists, if not create it
        data = await websocket.receive_text()
        logger.info(f"Received data: {data}")
        chats = chat_service.chat(data, conversation_history=conversation.messages)
        full_message = ""
        chunks = []
        await websocket.send_text("######START######")
        async for chat in chats:
            await websocket.send_text(chat)
            full_message += chat
        conversation.messages.append(ChatMessage(role="user", content=data))
        conversation.messages.append(ChatMessage(role="bot", content=full_message))
        await websocket.send_text("######END######")
        
