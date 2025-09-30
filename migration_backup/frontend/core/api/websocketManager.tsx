/**
 * 🔌 WebSocket Manager - Real-time Communication Hub
 * 
 * @fileoverview Enterprise WebSocket client for real-time features
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Lead Dev IA + Backend Senior + DevOps Expert
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { EventEmitter } from 'events';

// === WEBSOCKET INTERFACES ===

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  connectionTimeout?: number;
  enableLogging?: boolean;
}

export interface WebSocketMessage {
  id: string;
  type: string;
  timestamp: string;
  data: any;
  service?: string;
  priority?: 'low' | 'normal' | 'high' | 'critical';
}

export interface ConnectionState {
  status: 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';
  error?: string;
  reconnectAttempt?: number;
  lastConnected?: Date;
}

// === WEBSOCKET MANAGER CLASS ===

export class WebSocketManager extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private connectionState: ConnectionState;
  private messageQueue: WebSocketMessage[] = [];
  private isAuthenticated = false;
  private authToken: string | null = null;

  constructor(config: WebSocketConfig) {
    super();
    
    this.config = {
      protocols: [],
      reconnectAttempts: 5,
      reconnectInterval: 3000,
      heartbeatInterval: 30000,
      connectionTimeout: 10000,
      enableLogging: true,
      ...config
    };

    this.connectionState = {
      status: 'disconnected'
    };
  }

  /**
   * Connect to WebSocket server
   */
  public connect(authToken?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.authToken = authToken || this.authToken;
      this.updateConnectionState({ status: 'connecting' });

      try {
        const wsUrl = this.authToken 
          ? `${this.config.url}?token=${this.authToken}`
          : this.config.url;

        this.ws = new WebSocket(wsUrl, this.config.protocols);

        // Connection timeout
        const timeoutId = setTimeout(() => {
          if (this.ws?.readyState === WebSocket.CONNECTING) {
            this.ws?.close();
            reject(new Error('Connection timeout'));
          }
        }, this.config.connectionTimeout);

        this.ws.onopen = () => {
          clearTimeout(timeoutId);
          this.onOpen();
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.onMessage(event);
        };

        this.ws.onclose = (event) => {
          clearTimeout(timeoutId);
          this.onClose(event);
        };

        this.ws.onerror = (event) => {
          clearTimeout(timeoutId);
          this.onError(event);
          reject(new Error('WebSocket connection error'));
        };

      } catch (error) {
        this.updateConnectionState({ 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Unknown error' 
        });
        reject(error);
      }
    });
  }

  /**
   * Send message to WebSocket server
   */
  public send(message: Omit<WebSocketMessage, 'id' | 'timestamp'>): boolean {
    const fullMessage: WebSocketMessage = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      ...message
    };

    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(fullMessage));
        this.log('Message sent:', fullMessage);
        return true;
      } catch (error) {
        this.log('Send error:', error);
        return false;
      }
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(fullMessage);
      this.log('Message queued (connection not ready):', fullMessage);
      return false;
    }
  }

  /**
   * Subscribe to specific message types
   */
  public subscribe(messageType: string, callback: (data: any) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === messageType) {
        callback(message.data);
      }
    };

    this.on('message', handler);

    // Return unsubscribe function
    return () => {
      this.off('message', handler);
    };
  }

  /**
   * Disconnect WebSocket
   */
  public disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.updateConnectionState({ status: 'disconnected' });
    this.messageQueue = [];
  }

  /**
   * Get current connection state
   */
  public getConnectionState(): ConnectionState {
    return { ...this.connectionState };
  }

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // === PRIVATE METHODS ===

  private onOpen(): void {
    this.updateConnectionState({ 
      status: 'connected',
      lastConnected: new Date()
    });

    this.isAuthenticated = !!this.authToken;
    this.startHeartbeat();
    this.processMessageQueue();

    this.log('WebSocket connected');
    this.emit('connected');
  }

  private onMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      this.log('Message received:', message);
      
      // Handle system messages
      if (message.type === 'heartbeat') {
        this.send({ type: 'heartbeat_ack', data: {} });
        return;
      }

      if (message.type === 'auth_required') {
        this.emit('auth_required', message.data);
        return;
      }

      if (message.type === 'auth_success') {
        this.isAuthenticated = true;
        this.emit('authenticated', message.data);
        return;
      }

      // Emit message event
      this.emit('message', message);
      this.emit(`message:${message.type}`, message);

    } catch (error) {
      this.log('Message parse error:', error);
      this.emit('error', new Error('Failed to parse WebSocket message'));
    }
  }

  private onClose(event: CloseEvent): void {
    this.updateConnectionState({ status: 'disconnected' });
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    this.log('WebSocket closed:', event.code, event.reason);
    this.emit('disconnected', { code: event.code, reason: event.reason });

    // Attempt to reconnect if not manually closed
    if (event.code !== 1000 && this.config.reconnectAttempts > 0) {
      this.attemptReconnect();
    }
  }

  private onError(event: Event): void {
    const error = 'WebSocket error occurred';
    this.updateConnectionState({ status: 'error', error });
    
    this.log('WebSocket error:', event);
    this.emit('error', new Error(error));
  }

  private attemptReconnect(): void {
    if (this.connectionState.reconnectAttempt! >= this.config.reconnectAttempts) {
      this.log('Max reconnection attempts reached');
      return;
    }

    const attempt = (this.connectionState.reconnectAttempt || 0) + 1;
    this.updateConnectionState({ 
      status: 'reconnecting', 
      reconnectAttempt: attempt 
    });

    this.log(`Attempting to reconnect (${attempt}/${this.config.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(async () => {
      try {
        await this.connect();
        this.connectionState.reconnectAttempt = 0;
      } catch (error) {
        this.log('Reconnection failed:', error);
        this.attemptReconnect();
      }
    }, this.config.reconnectInterval * attempt); // Exponential backoff
  }

  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'heartbeat', data: { timestamp: Date.now() } });
      }
    }, this.config.heartbeatInterval);
  }

  private processMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift()!;
      this.ws!.send(JSON.stringify(message));
      this.log('Queued message sent:', message);
    }
  }

  private updateConnectionState(updates: Partial<ConnectionState>): void {
    this.connectionState = { ...this.connectionState, ...updates };
    this.emit('stateChange', this.connectionState);
  }

  private generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private log(...args: any[]): void {
    if (this.config.enableLogging) {
      console.log('[WebSocketManager]', ...args);
    }
  }
}

// === WEBSOCKET HOOK ===

import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseWebSocketOptions extends WebSocketConfig {
  onConnect?: () => void;
  onDisconnect?: (event: { code: number; reason: string }) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  autoConnect?: boolean;
}

export interface UseWebSocketReturn {
  connectionState: ConnectionState;
  send: (message: Omit<WebSocketMessage, 'id' | 'timestamp'>) => boolean;
  connect: (authToken?: string) => Promise<void>;
  disconnect: () => void;
  subscribe: (messageType: string, callback: (data: any) => void) => () => void;
  isConnected: boolean;
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    status: 'disconnected'
  });

  const wsManager = useRef<WebSocketManager | null>(null);
  const authTokenRef = useRef<string | null>(null);

  // Initialize WebSocket manager
  useEffect(() => {
    wsManager.current = new WebSocketManager(options);

    const manager = wsManager.current;

    // Event listeners
    manager.on('stateChange', setConnectionState);
    
    if (options.onConnect) {
      manager.on('connected', options.onConnect);
    }
    
    if (options.onDisconnect) {
      manager.on('disconnected', options.onDisconnect);
    }
    
    if (options.onMessage) {
      manager.on('message', options.onMessage);
    }
    
    if (options.onError) {
      manager.on('error', options.onError);
    }

    // Auto connect if specified
    if (options.autoConnect) {
      manager.connect(authTokenRef.current || undefined).catch(console.error);
    }

    return () => {
      manager.disconnect();
      manager.removeAllListeners();
    };
  }, [options.url]);

  const connect = useCallback(async (authToken?: string) => {
    if (authToken) {
      authTokenRef.current = authToken;
    }
    return wsManager.current?.connect(authToken);
  }, []);

  const disconnect = useCallback(() => {
    wsManager.current?.disconnect();
  }, []);

  const send = useCallback((message: Omit<WebSocketMessage, 'id' | 'timestamp'>) => {
    return wsManager.current?.send(message) || false;
  }, []);

  const subscribe = useCallback((messageType: string, callback: (data: any) => void) => {
    return wsManager.current?.subscribe(messageType, callback) || (() => {});
  }, []);

  return {
    connectionState,
    send,
    connect,
    disconnect,
    subscribe,
    isConnected: connectionState.status === 'connected'
  };
}

// === WEBSOCKET CONTEXT ===

import React, { createContext, useContext } from 'react';

interface WebSocketContextValue {
  wsManager: WebSocketManager | null;
  connectionState: ConnectionState;
  connect: (authToken?: string) => Promise<void>;
  disconnect: () => void;
  send: (message: Omit<WebSocketMessage, 'id' | 'timestamp'>) => boolean;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
}

interface WebSocketProviderProps {
  children: React.ReactNode;
  config: WebSocketConfig;
}

export function WebSocketProvider({ children, config }: WebSocketProviderProps) {
  const wsHook = useWebSocket({ ...config, autoConnect: false });
  const wsManagerRef = useRef<WebSocketManager | null>(null);

  // Initialize WebSocket manager
  useEffect(() => {
    wsManagerRef.current = new WebSocketManager(config);
  }, [config]);

  const value: WebSocketContextValue = {
    wsManager: wsManagerRef.current,
    connectionState: wsHook.connectionState,
    connect: wsHook.connect,
    disconnect: wsHook.disconnect,
    send: wsHook.send
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export default WebSocketManager;