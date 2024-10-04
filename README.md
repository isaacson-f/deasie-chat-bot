# deasie-chat-bot

**Note: The capability of switching between conversations is still in progress, but the infrastructure to easily add this feature is in place on the backend.**

## Getting Started

To start this project, follow these steps:

1. Clone the repository
2. Install dependencies for both backend and frontend
3. Start the backend server (details found in chat-backend/README.md)
4. Start the frontend application (details found in chat-frontend/README.md)

## Project Requirements

This project incorporates the following requirements:

### Backend (FastAPI with WebSockets)

- WebSocket server implementation using FastAPI
- Real-time message handling
- Basic natural language processing for understanding and responding to user inputs
- Conversation context maintenance for coherent responses
- Proper error handling and logging

### Frontend (React)

- Single-page application using React
- Real-time chat interface with message history
- Input field for user messages
- Display of bot responses with appropriate formatting
- Streaming of bot responses
- React hooks for state management
- WebSocket connection to the backend

## Architecture

The project is divided into two main parts:

1. Backend: A FastAPI application that handles WebSocket connections and processes chat messages.
2. Frontend: A React application that provides the user interface for the chat bot.

Both parts communicate in real-time using WebSocket connections, ensuring a smooth and responsive chat experience.

## Future Enhancements

- Implementation of conversation switching functionality, leveraging the existing infrastructure.
- Adding in feedback mechanisms for users to rate the accuracy and helpfulness of the chatbot's responses.
- Integrating additional error handling on the frontend to provide better feedback to the user.
- Adding multimodal inputs for the chatbot, such as images or voice, to enhance the user experience.