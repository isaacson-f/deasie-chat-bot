import React, { useState, useEffect, useCallback } from 'react';
import styles from './Chat.module.scss';
import { getMessages } from '../clients/chatClient';
import useWebSocket from 'react-use-websocket';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  isHtml: boolean;
}

interface ChatProps {
  userId: string;
  conversationId: string;
}

const Chat: React.FC<ChatProps> = ({userId, conversationId}) => {

  const { sendMessage, readyState, lastMessage } = useWebSocket(`ws://127.0.0.1:8000/api/chat/${userId}/conversation/${conversationId}`);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [currentBotMessage, setCurrentBotMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (lastMessage !== null) {
      const messageData = lastMessage.data;
      if (messageData === '######START######') {
        console.log('start');
        setMessages(prevMessages => [{
          id: Date.now().toString(),
          content: '',
          sender: 'bot',
          isHtml: true
        }, ...prevMessages]);
        setLoading(true);
        // Start a new bot message
        setCurrentBotMessage('');
      } else if (messageData === '######END######') {
        console.log('end');
        // Finalize the bot message and add it to the messages list
        setLoading(false);
        const newMessage: Message = {
          id: Date.now().toString(),
          content: currentBotMessage,
          sender: 'bot',
          isHtml: true
        };
        // setMessages(prevMessages => [newMessage, ...prevMessages]);
        setCurrentBotMessage('');
      }
      else {
        console.log(messageData);
          // Append the new chunk to the current bot message
          setMessages(prevMessages => {
            const updatedMessages = [...prevMessages];
            if (updatedMessages.length > 0) {
              updatedMessages[0] = {
                ...updatedMessages[0],
                content: updatedMessages[0].content + messageData
              };
            }
            return updatedMessages;
          });
          console.log(`Updated content: ${messages[0]?.content}`);
          setCurrentBotMessage(prev => prev + messageData);
      }
      console.log(currentBotMessage);
    }
  }, [lastMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      const userMessage: Message = { 
        id: Date.now().toString(), 
        content: input, 
        sender: 'user',
        isHtml: false
      };
      setMessages(prevMessages => [userMessage, ...prevMessages]);
      setInput('');
    }
  };

  const LoadingIndicator = () => (
    <div className={styles.loadingIndicator}>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
    </div>
  );

  return (
    <div className={styles.chat}>
      <div className={styles.messageList}>
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
          >
            {index === 0 && loading ? (
              <LoadingIndicator />
            ) : message.isHtml ? (
              <div dangerouslySetInnerHTML={{ __html: message.content }} />
            ) : (
              message.content
            )}
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
