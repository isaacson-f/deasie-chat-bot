import React, { useState, useEffect, useCallback, useRef } from 'react';
import styles from './Chat.module.scss';
import Markdown from 'react-markdown';
import { getMessages } from '../clients/chatClient';
import useWebSocket from 'react-use-websocket';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
}

interface ChatProps {
  userId: string;
  conversationId: string;
}

const Chat: React.FC<ChatProps> = ({userId, conversationId}) => {

  const { sendMessage, readyState, lastMessage } = useWebSocket(`ws://127.0.0.1:8000/api/chat/${userId}`, {
    onOpen: () => {
      console.log('WebSocket connection opened.');
    },
    onMessage: (message) => {
      updateMessages(message);
    },
    onClose: () => {
      console.log('WebSocket connection closed.');
    },
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const currentBotMessage = useRef('test');
  const [botMessage, setBotMessage] = useState('beginning');
  const [loading, setLoading] = useState(false);

  const updateMessages = useCallback(async(message: MessageEvent) => {
    const messageData = message.data;
    if (messageData === '######START######') {
      setLoading(true);
      // Start a new bot message
      setMessages(prevMessages => [{
        id: Date.now().toString(),
        content: '',
        sender: 'bot',
      }, ...prevMessages]);
      currentBotMessage.current = '';
      setBotMessage('');
    } else if (messageData === '######END######') {
      // Finalize the bot message and add it to the messages list
      setLoading(false);
      setBotMessage('');
      currentBotMessage.current = '';
    }
    else {
      console.log(messages.map(message => message.sender));
        // Append the new chunk to the current bot message
        currentBotMessage.current = messageData;
        if (messages[0].sender === 'bot') {
          messages[0].content = currentBotMessage.current;
        }
        setBotMessage(currentBotMessage.current);
    }
  }, [lastMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      const userMessage: Message = { 
        id: Date.now().toString(), 
        content: input, 
        sender: 'user',
      };
      setMessages(prevMessages => [userMessage, ...prevMessages]);
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className={styles.chat}>
      <div className={styles.messageList}>
        {messages.map(message => (
          <div
            key={message.id}
            className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
          >
            <Markdown>{message.content}</Markdown>
          </div>
        ))}
      </div>
      <div className={styles.inputFormContainer}>
        <form className={styles.inputForm} onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className={styles.input}
            disabled={loading}
          />
          <button type="submit" className={styles.sendButton}>Send</button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
