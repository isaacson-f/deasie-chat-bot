import React, { useState, useEffect } from 'react';
import styles from './Sidebar.module.scss';

interface Conversation {
  id: string;
  title: string;
}

const Sidebar: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    // Dummy data for past conversations
    const dummyConversations: Conversation[] = [
      { id: '1', title: 'React Hooks' },
      { id: '2', title: 'TypeScript Basics' },
      { id: '3', title: 'CSS Modules' },
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
