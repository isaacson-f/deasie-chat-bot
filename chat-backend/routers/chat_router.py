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


@router.websocket("/{user_id}")
async def websocket(websocket: WebSocket, 
                    chat_service: Annotated[ChatService, Depends(ChatService)], 
                    user_service: Annotated[UserService, Depends(UserService)],
                    user_id: Annotated[str, Path()]):
    try:
        cur_user = user_service.get_user(user_id)
        if cur_user == None:
            logger.info(f"User {user_id} not found, creating...")
            user = User(_id=user_id)
            cur_user = await user_service.create_user(user)
        
        # Check if conversation exists, if not create it
        conversations = chat_service.get_conversations_by_user(user_id)
        if len(conversations) == 0:
            conversation = chat_service.create_conversation(user_id)
        else:
            conversation = conversations[0]
        await websocket.accept()
        await websocket.send_text("######CONVERSATIONS######")
        if len(conversations) > 5:
            for past_convo in conversations[-5:]:
                # send the conversation id
                await websocket.send_text(past_convo.conversation_id)
                # send the first message in the conversation
                if len(past_convo.messages) > 0:
                    await websocket.send_text(past_convo.messages[0].content)
        else:
            for past_convo in conversations:
                # send the conversation id
                await websocket.send_text(past_convo.conversation_id)
                # send the first message in the conversation
                if len(past_convo.messages) > 0:
                    await websocket.send_text(past_convo.messages[0].content)        
            await websocket.send_text("######ALL_CONVERSATIONS######")
        #begin the chat loop
        while True:
            data = await websocket.receive_text()
            # Switch conversations if the client sends the switch command
            if data == "#####SWITCH_CONVERSATION######":
                conversation_id = await websocket.receive_text()
                conversation = chat_service.get_conversation_by_id(conversation_id)
                if conversation == None:
                  logger.error(f"Conversation {conversation_id} not found")
                  await websocket.send_text("######CONVERSATION_NOT_FOUND######")
                  continue
                await websocket.send_text("######CONVERSATION_FOUND######")
                for message in conversation.messages:
                  await websocket.send_text(message.content)
                await websocket.send_text("######CONVERSATION_SWITCHED######")
                continue

            # Send the message to the chatbot and get the response
            chats = chat_service.chat(data, conversation_history=conversation.messages)
            full_message = ""
            chunks = []
            await websocket.send_text("######START######")
            async for chat in chats:
                await websocket.send_text(chat)
                full_message = chat
            user_message = ChatMessage(role="user", content=data)
            bot_reply = ChatMessage(role="bot", content=full_message)
            conversation.messages.append(user_message)
            conversation.messages.append(bot_reply)
            chat_service.add_message_to_conversation(conversation.conversation_id, user_message)
            chat_service.add_message_to_conversation(conversation.conversation_id, bot_reply)
            await websocket.send_text("######END######")
    except WebSocketException as e:
        logger.error(f"WebSocketException: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        logger.error(f"Exception: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        