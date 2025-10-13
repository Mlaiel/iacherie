/**
 * WEBSOCKET REACT HOOKS
 * Custom React hooks for WebSocket integration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { getWebSocketManager } from './WebSocketManager';
import { CHANNELS, EVENTS } from './channels';

type MessageHandler = (data: any) => void;

/**
 * Hook to subscribe to a specific WebSocket channel and event
 */
export function useWebSocketChannel(
  channel: string,
  event: string,
  handler: MessageHandler,
  enabled: boolean = true
) {
  const handlerRef = useRef(handler);

  // Update ref when handler changes
  useEffect(() => {
    handlerRef.current = handler;
  }, [handler]);

  useEffect(() => {
    if (!enabled) return;

    const ws = getWebSocketManager();
    
    // Wrap handler to use ref
    const wrappedHandler = (data: any) => {
      handlerRef.current(data);
    };

    const unsubscribe = ws.subscribe(channel, event, wrappedHandler);

    return () => {
      unsubscribe();
    };
  }, [channel, event, enabled]);
}

/**
 * Hook to get WebSocket connection status
 */
export function useWebSocketStatus() {
  const [status, setStatus] = useState({
    connected: false,
    connecting: false,
    reconnectAttempts: 0,
  });

  useEffect(() => {
    const ws = getWebSocketManager();

    // Initial status
    setStatus(ws.getStatus());

    // Update on connection changes
    const unsubscribeOpen = ws.onOpen(() => {
      setStatus(ws.getStatus());
    });

    const unsubscribeClose = ws.onClose(() => {
      setStatus(ws.getStatus());
    });

    // Poll status periodically
    const interval = setInterval(() => {
      setStatus(ws.getStatus());
    }, 1000);

    return () => {
      unsubscribeOpen();
      unsubscribeClose();
      clearInterval(interval);
    };
  }, []);

  return status;
}

/**
 * Hook to send messages via WebSocket
 */
export function useWebSocketSend() {
  const send = useCallback((channel: string, event: string, data: any) => {
    const ws = getWebSocketManager();
    ws.send(channel, event, data);
  }, []);

  return send;
}

/**
 * Hook for crawlers real-time updates
 */
export function useCrawlersWebSocket() {
  const [updates, setUpdates] = useState<any[]>([]);

  useWebSocketChannel(CHANNELS.CRAWLERS, EVENTS.STATUS_CHANGED, (data) => {
    setUpdates((prev) => [...prev, { type: 'status_changed', data, timestamp: Date.now() }]);
  });

  useWebSocketChannel(CHANNELS.CRAWLERS, EVENTS.CRAWLER_PROGRESS, (data) => {
    setUpdates((prev) => [...prev, { type: 'progress', data, timestamp: Date.now() }]);
  });

  return {
    updates,
    clearUpdates: () => setUpdates([]),
  };
}

/**
 * Hook for generators real-time updates
 */
export function useGeneratorsWebSocket() {
  const [generations, setGenerations] = useState<Map<string, any>>(new Map());

  useWebSocketChannel(CHANNELS.GENERATORS, EVENTS.GENERATION_STARTED, (data) => {
    setGenerations((prev) => {
      const next = new Map(prev);
      next.set(data.id, { ...data, status: 'generating', progress: 0 });
      return next;
    });
  });

  useWebSocketChannel(CHANNELS.GENERATORS, EVENTS.GENERATION_PROGRESS, (data) => {
    setGenerations((prev) => {
      const next = new Map(prev);
      const item = next.get(data.id);
      if (item) {
        next.set(data.id, { ...item, progress: data.progress });
      }
      return next;
    });
  });

  useWebSocketChannel(CHANNELS.GENERATORS, EVENTS.GENERATION_COMPLETED, (data) => {
    setGenerations((prev) => {
      const next = new Map(prev);
      const item = next.get(data.id);
      if (item) {
        next.set(data.id, { ...item, status: 'completed', progress: 100 });
      }
      return next;
    });
  });

  useWebSocketChannel(CHANNELS.GENERATORS, EVENTS.GENERATION_FAILED, (data) => {
    setGenerations((prev) => {
      const next = new Map(prev);
      const item = next.get(data.id);
      if (item) {
        next.set(data.id, { ...item, status: 'error' });
      }
      return next;
    });
  });

  return {
    generations: Array.from(generations.values()),
    getGeneration: (id: string) => generations.get(id),
    clearGeneration: (id: string) => {
      setGenerations((prev) => {
        const next = new Map(prev);
        next.delete(id);
        return next;
      });
    },
  };
}

/**
 * Hook for chatroom messages
 */
export function useChatroomWebSocket(roomId?: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const send = useWebSocketSend();

  useWebSocketChannel(
    CHANNELS.CHATROOMS,
    EVENTS.MESSAGE,
    (data) => {
      if (!roomId || data.room_id === roomId) {
        setMessages((prev) => [...prev, data]);
      }
    },
    !!roomId
  );

  useWebSocketChannel(
    CHANNELS.CHATROOMS,
    EVENTS.USER_JOINED,
    (data) => {
      if (!roomId || data.room_id === roomId) {
        setUsers((prev) => [...prev, data.user]);
      }
    },
    !!roomId
  );

  useWebSocketChannel(
    CHANNELS.CHATROOMS,
    EVENTS.USER_LEFT,
    (data) => {
      if (!roomId || data.room_id === roomId) {
        setUsers((prev) => prev.filter((u) => u.id !== data.user.id));
      }
    },
    !!roomId
  );

  const sendMessage = useCallback(
    (message: string) => {
      if (!roomId) return;
      send(CHANNELS.CHATROOMS, EVENTS.MESSAGE, {
        room_id: roomId,
        message,
      });
    },
    [roomId, send]
  );

  return {
    messages,
    users,
    sendMessage,
    clearMessages: () => setMessages([]),
  };
}

/**
 * Hook for analytics real-time updates
 */
export function useAnalyticsWebSocket() {
  const [metrics, setMetrics] = useState<any>(null);

  useWebSocketChannel(CHANNELS.ANALYTICS, EVENTS.METRICS_UPDATE, (data) => {
    setMetrics(data);
  });

  useWebSocketChannel(CHANNELS.ANALYTICS, EVENTS.REAL_TIME_DATA, (data) => {
    setMetrics((prev: any) => ({
      ...prev,
      realTimeData: data,
    }));
  });

  return metrics;
}

/**
 * Hook for notifications
 */
export function useNotificationsWebSocket(onNotification?: (notification: any) => void) {
  const [notifications, setNotifications] = useState<any[]>([]);

  useWebSocketChannel(CHANNELS.NOTIFICATIONS, EVENTS.NEW_NOTIFICATION, (data) => {
    setNotifications((prev) => [data, ...prev]);
    onNotification?.(data);
  });

  return {
    notifications,
    clearNotifications: () => setNotifications([]),
    dismissNotification: (id: string) => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    },
  };
}

/**
 * Hook for automation workflows
 */
export function useAutomationWebSocket() {
  const [workflows, setWorkflows] = useState<Map<string, any>>(new Map());

  useWebSocketChannel(CHANNELS.AUTOMATION, EVENTS.WORKFLOW_STARTED, (data) => {
    setWorkflows((prev) => {
      const next = new Map(prev);
      next.set(data.id, { ...data, status: 'running' });
      return next;
    });
  });

  useWebSocketChannel(CHANNELS.AUTOMATION, EVENTS.WORKFLOW_COMPLETED, (data) => {
    setWorkflows((prev) => {
      const next = new Map(prev);
      const item = next.get(data.id);
      if (item) {
        next.set(data.id, { ...item, status: 'completed' });
      }
      return next;
    });
  });

  useWebSocketChannel(CHANNELS.AUTOMATION, EVENTS.WORKFLOW_FAILED, (data) => {
    setWorkflows((prev) => {
      const next = new Map(prev);
      const item = next.get(data.id);
      if (item) {
        next.set(data.id, { ...item, status: 'error', error: data.error });
      }
      return next;
    });
  });

  return {
    workflows: Array.from(workflows.values()),
    getWorkflow: (id: string) => workflows.get(id),
  };
}
