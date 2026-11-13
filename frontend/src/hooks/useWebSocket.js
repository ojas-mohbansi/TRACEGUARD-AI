import { useState, useEffect } from 'react';
import wsService from '../services/websocket';

export function useWebSocket(eventType = null, onMessageCallback = null) {
  const [status, setStatus] = useState('disconnected');
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    // Connect on mount
    wsService.connect();

    const unsubStatus = wsService.onStatusChange((newStatus) => {
      setStatus(newStatus);
    });

    let unsubMessage = null;
    if (eventType) {
      unsubMessage = wsService.on(eventType, (data) => {
        setLastMessage(data);
        if (onMessageCallback) {
          onMessageCallback(data);
        }
      });
    }

    return () => {
      unsubStatus();
      if (unsubMessage) {
        unsubMessage();
      }
    };
  }, [eventType, onMessageCallback]);

  const send = (data) => wsService.send(data);

  return { status, lastMessage, send, ws: wsService };
}
