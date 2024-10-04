import React from 'react';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import styles from './App.module.scss';

function App() {
  return (
    <div className={styles.app}>
      <div className={styles.header}>
        ChatGeneric
      </div>
      <div className={styles.body}>
        {(() => {
          const getCookie = (name: string) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop()?.split(';').shift();
          };

          const generateHash = () => {
            return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
          };

          let userId = getCookie('user_id');
          let conversations = [{
            id: '1',
            title: 'React Hooks'
          }];
          if (!userId) {
            userId = generateHash();
            document.cookie = `user_id=${userId}; path=/; max-age=31536000`;
          }
          return (
            <>
              <div className={styles.sidebar}>
                <Sidebar {...conversations}/>
              </div>
              <div className={styles.chat}>
                <Chat userId={userId.toString()} />
              </div>
            </>
          );
        })()}
      </div>
    </div>
  );
}

export default App;
