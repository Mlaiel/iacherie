import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url: string) => {
  const [data, setData] = useState<any>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const ws = useRef<WebSocket | null>(null);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    ws.current = new WebSocket(url);
    
    ws.current.onopen = () => setReadyState(WebSocket.OPEN);
    ws.current.onclose = () => setReadyState(WebSocket.CLOSED);
    ws.current.onmessage = (event) => {
      try {
        setData(JSON.parse(event.data));
      } catch {
        setData(event.data);
      }
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return { data, readyState, sendMessage };
};
