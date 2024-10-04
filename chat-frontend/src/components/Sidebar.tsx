import React, { useState, useEffect } from 'react';
import styles from './Sidebar.module.scss';
import useWebSocket from 'react-use-websocket';

interface Conversation {
  id: string;
  title: string;
}

interface SidebarProps {
  userId: string;
}

const Sidebar: React.FC<SidebarProps> = ({userId}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const { sendMessage, lastMessage } = useWebSocket(`ws://127.0.0.1:8000/api/chat/${userId}`, {
    share: true,
    onOpen: () => {
      console.log('WebSocket connection opened.');
    },
    onMessage: (message) => {

    },
    onClose: () => {
      console.log('WebSocket connection closed.');
    },
  });

  const updateConversations = (message: MessageEvent) => {
    const messageData = message.data;
    if (messageData === '######START######') {
      setConversations(prevConversations => [{
        id: Date.now().toString(),
        title: '',
      }, ...prevConversations]);
    }
  }
  useEffect(() => {
    // Dummy data for past conversations
    const dummyConversations: Conversation[] = [
      { id: '1', title: 'React Hooks Discussion' },
      { id: '2', title: 'State Management Techniques' },
      { id: '3', title: 'CSS-in-JS vs. Traditional CSS' },
      { id: '4', title: 'Performance Optimization in React' },
      { id: '5', title: 'TypeScript Best Practices' }
    ];
    setConversations(dummyConversations);
  }, []);
  const removeConversation = (id: string) => {
    setConversations(conversations.filter(conv => conv.id !== id));
  };

  return (
    <div className={styles.sidebar}>
      <h2>Past Conversations</h2>
      <ul className={styles.conversationList}>
        {conversations.map(conv => (
          <li key={conv.id} className={styles.conversationItem}>
            <span>{conv.title}</span>
            <button
              className={styles.removeButton}
              onClick={() => removeConversation(conv.id)}
            >
              ×
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
