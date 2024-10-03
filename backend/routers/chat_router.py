import logging
from typing import Annotated, List
from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, FastAPI, Path, Query, WebSocket, WebSocketException, status

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


@router.websocket("/{user_id}/conversation/{conversation_id}")
async def websocket(websocket: WebSocket, 
                    chat_service: Annotated[ChatService, Depends(ChatService)], 
                    user_service: Annotated[UserService, Depends(UserService)],
                    user_id: Annotated[str, Path()],
                    conversation_id: Annotated[str, Path()]
                    ):
    await websocket.accept()
    # Check if user exists, if not create it
    logger.info(f"User ID: {user_id}")
    logger.info(f"Conversation ID: {conversation_id}")
    cur_user = await user_service.get_user(user_id)
    if not await cur_user:
        await user_service.create_user(user_id)
    
    # Check if conversation exists, if not create it
    conversation = chat_service.get_conversation(conversation_id)
    if not conversation:
        conversation = chat_service.create_conversation(user_id)
    data = await websocket.receive_text()
    # chats = chat_service.chat(data, conversation_history=conversation.messages)
    # for chat in chats:
    await websocket.send_text(data)
    await websocket.close()
