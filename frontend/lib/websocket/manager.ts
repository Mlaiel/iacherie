/**
 * WebSocket Connection Manager - Production Grade
 * Handles reconnection, heartbeat, message queuing
 * @module lib/websocket/manager
 */

import { generateId } from '@/lib/utils';

/**
 * WebSocket connection states
 */
export enum WebSocketState {
  CONNECTING = 'CONNECTING',
  CONNECTED = 'CONNECTED',
  DISCONNECTING = 'DISCONNECTING',
  DISCONNECTED = 'DISCONNECTED',
  RECONNECTING = 'RECONNECTING',
  ERROR = 'ERROR',
}

/**
 * WebSocket message types
 */
export interface WebSocketMessage<T = any> {
  id: string;
  type: string;
  payload: T;
  timestamp: number;
}

/**
 * WebSocket event handlers
 */
interface WebSocketEventHandlers {
  onConnected?: () => void;
  onDisconnected?: () => void;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onReconnecting?: (attempt: number) => void;
}

/**
 * WebSocket Manager Configuration
 */
interface WebSocketManagerConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  messageQueueSize?: number;
  protocols?: string[];
}

/**
 * Production WebSocket Manager
 */
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private state: WebSocketState = WebSocketState.DISCONNECTED;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private handlers: WebSocketEventHandlers = {};
  private messageHandlers = new Map<string, Set<(data: any) => void>>();
  
  constructor(private config: WebSocketManagerConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      messageQueueSize: 100,
      ...config,
    };
  }
  
  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.state === WebSocketState.CONNECTED) {
        resolve();
        return;
      }
      
      this.state = WebSocketState.CONNECTING;
      
      try {
        this.ws = new WebSocket(this.config.url, this.config.protocols);
        
        this.ws.onopen = () => {
          this.state = WebSocketState.CONNECTED;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          this.handlers.onConnected?.();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          const message = this.parseMessage(event.data);
          if (message) {
            this.handleMessage(message);
          }
        };
        
        this.ws.onerror = (error) => {
          this.state = WebSocketState.ERROR;
          this.handlers.onError?.(error);
          reject(error);
        };
        
        this.ws.onclose = () => {
          this.state = WebSocketState.DISCONNECTED;
          this.stopHeartbeat();
          this.handlers.onDisconnected?.();
          this.attemptReconnect();
        };
      } catch (error) {
        this.state = WebSocketState.ERROR;
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.state = WebSocketState.DISCONNECTING;
    this.clearReconnectTimer();
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.state = WebSocketState.DISCONNECTED;
  }
  
  /**
   * Send message through WebSocket
   */
  send<T = any>(type: string, payload: T): void {
    const message: WebSocketMessage<T> = {
      id: generateId(),
      type,
      payload,
      timestamp: Date.now(),
    };
    
    if (this.state === WebSocketState.CONNECTED && this.ws) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.queueMessage(message);
    }
  }
  
  /**
   * Subscribe to message type
   */
  on<T = any>(type: string, handler: (data: T) => void): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(type);
        }
      }
    };
  }
  
  /**
   * Set event handlers
   */
  setHandlers(handlers: WebSocketEventHandlers): void {
    this.handlers = { ...this.handlers, ...handlers };
  }
  
  /**
   * Get current connection state
   */
  getState(): WebSocketState {
    return this.state;
  }
  
  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.state === WebSocketState.CONNECTED;
  }
  
  /**
   * Parse incoming message
   */
  private parseMessage(data: string): WebSocketMessage | null {
    try {
      return JSON.parse(data);
    } catch {
      console.error('Failed to parse WebSocket message:', data);
      return null;
    }
  }
  
  /**
   * Handle incoming message
   */
  private handleMessage(message: WebSocketMessage): void {
    this.handlers.onMessage?.(message);
    
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach((handler) => handler(message.payload));
    }
  }
  
  /**
   * Queue message for later sending
   */
  private queueMessage(message: WebSocketMessage): void {
    this.messageQueue.push(message);
    if (this.messageQueue.length > this.config.messageQueueSize!) {
      this.messageQueue.shift();
    }
  }
  
  /**
   * Flush queued messages
   */
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0 && this.ws) {
      const message = this.messageQueue.shift()!;
      this.ws.send(JSON.stringify(message));
    }
  }
  
  /**
   * Start heartbeat ping/pong
   */
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.state === WebSocketState.CONNECTED) {
        this.send('heartbeat', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }
  
  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (
      this.reconnectAttempts >= this.config.maxReconnectAttempts! ||
      this.state === WebSocketState.DISCONNECTING
    ) {
      return;
    }
    
    this.reconnectAttempts++;
    this.state = WebSocketState.RECONNECTING;
    this.handlers.onReconnecting?.(this.reconnectAttempts);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(() => {
        // Reconnect failed, will retry automatically
      });
    }, this.config.reconnectInterval! * Math.min(this.reconnectAttempts, 5));
  }
  
  /**
   * Clear reconnect timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

/**
 * Create WebSocket manager instance
 */
export function createWebSocketManager(
  config: WebSocketManagerConfig
): WebSocketManager {
  return new WebSocketManager(config);
}
