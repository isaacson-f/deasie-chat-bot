import useWebSocket from "react-use-websocket";

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
  }
  // const { sendMessage, readyState, lastMessage } = useWebSocket('ws://localhost:8080/conversation');
  
  export const getMessages = async (): Promise<Message[]> => {
    // Simulating API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: '1', text: 'Hello! How can I help you today?', sender: 'bot' },
        ]);
      }, 500);
    });
  };
  
  // export const sendMessage = async (message: string): Promise<Message> => {
  //   return new Promise((resolve) => {
  //     const { sendMessage, lasreadyState } = websocket;

  //     if (readyState === WebSocket.OPEN) {
  //       sendMessage(JSON.stringify({ type: 'message', content: message }));

  //       const messageHandler = (event: MessageEvent) => {
  //         const response = JSON.parse(event.data);
  //         if (response.type === 'message') {
  //           resolve({
  //             id: Date.now().toString(),
  //             text: response.content,
  //             sender: 'bot',
  //           });
  //         }
  //       };

  //       websocket.getWebSocket().addEventListener('message', messageHandler);
  //     } else {
  //       console.error('WebSocket connection is not open');
  //       resolve({
  //         id: Date.now().toString(),
  //         text: 'Sorry, the connection is not available. Please try again later.',
  //         sender: 'bot',
  //       });
  //     }
  //   });
  // };