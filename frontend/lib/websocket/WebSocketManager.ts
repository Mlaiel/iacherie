/**
 * WEBSOCKET MANAGER
 * Centralized WebSocket manager for real-time updates across all modules
 * 
 * Features:
 * - Automatic reconnection
 * - Multiple channels (crawlers, generators, agents, chat, analytics, notifications)
 * - Event-driven architecture
 * - Heartbeat monitoring
 * - Store integration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

/**
 * Message handler type
 */
export type MessageHandler = (data: any) => void;
type ErrorHandler = (error: Error) => void;
type ConnectionHandler = () => void;

export interface WebSocketConfig {
  url?: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export interface WebSocketMessage {
  channel: string;
  event: string;
  data: any;
  timestamp: number;
}

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  
  // Event handlers
  private messageHandlers = new Map<string, Set<MessageHandler>>();
  private errorHandlers = new Set<ErrorHandler>();
  private openHandlers = new Set<ConnectionHandler>();
  private closeHandlers = new Set<ConnectionHandler>();
  
  // Connection state
  private isConnecting = false;
  private isConnected = false;
  private shouldReconnect = true;

  constructor(config: WebSocketConfig = {}) {
    this.config = {
      url: config.url || this.getWebSocketUrl(),
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      heartbeatInterval: config.heartbeatInterval || 30000,
    };
  }

  /**
   * Get WebSocket URL based on environment
   */
  private getWebSocketUrl(): string {
    if (typeof window === 'undefined') {
      return 'ws://localhost:8000/ws';
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = process.env.NEXT_PUBLIC_WS_PORT || '8000';
    
    return `${protocol}//${host}:${port}/ws`;
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.isConnecting || this.isConnected) {
      console.log('[WebSocket] Already connecting or connected');
      return;
    }

    this.isConnecting = true;
    console.log(`[WebSocket] Connecting to ${this.config.url}...`);

    try {
      this.ws = new WebSocket(this.config.url);
      this.setupEventListeners();
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.handleError(error as Error);
      this.scheduleReconnect();
    }
  }

  /**
   * Setup WebSocket event listeners
   */
  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.isConnecting = false;
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      this.startHeartbeat();
      this.openHandlers.forEach(handler => handler());
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('[WebSocket] Failed to parse message:', error);
      }
    };

    this.ws.onerror = (event) => {
      console.error('[WebSocket] Error:', event);
      const error = new Error('WebSocket error');
      this.handleError(error);
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] Disconnected:', event.code, event.reason);
      this.isConnected = false;
      this.isConnecting = false;
      
      this.stopHeartbeat();
      this.closeHandlers.forEach(handler => handler());
      
      if (this.shouldReconnect) {
        this.scheduleReconnect();
      }
    };
  }

  /**
   * Handle incoming message
   */
  private handleMessage(message: WebSocketMessage): void {
    const channelKey = `${message.channel}:${message.event}`;
    const handlers = this.messageHandlers.get(channelKey);
    
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.data);
        } catch (error) {
          console.error('[WebSocket] Handler error:', error);
        }
      });
    }
  }

  /**
   * Handle error
   */
  private handleError(error: Error): void {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (err) {
        console.error('[WebSocket] Error handler failed:', err);
      }
    });
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached');
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    const delay = this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts);
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.config.maxReconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
        this.send('system', 'ping', {});
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Send message to server
   */
  send(channel: string, event: string, data: any): void {
    if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Cannot send message, not connected');
      return;
    }

    const message: WebSocketMessage = {
      channel,
      event,
      data,
      timestamp: Date.now(),
    };

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('[WebSocket] Failed to send message:', error);
      this.handleError(error as Error);
    }
  }

  /**
   * Subscribe to channel events
   */
  subscribe(channel: string, event: string, handler: MessageHandler): () => void {
    const channelKey = `${channel}:${event}`;
    
    if (!this.messageHandlers.has(channelKey)) {
      this.messageHandlers.set(channelKey, new Set());
    }
    
    this.messageHandlers.get(channelKey)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(channelKey);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(channelKey);
        }
      }
    };
  }

  /**
   * Subscribe to errors
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    return () => this.errorHandlers.delete(handler);
  }

  /**
   * Subscribe to connection open
   */
  onOpen(handler: ConnectionHandler): () => void {
    this.openHandlers.add(handler);
    return () => this.openHandlers.delete(handler);
  }

  /**
   * Subscribe to connection close
   */
  onClose(handler: ConnectionHandler): () => void {
    this.closeHandlers.add(handler);
    return () => this.closeHandlers.delete(handler);
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    console.log('[WebSocket] Disconnecting...');
    this.shouldReconnect = false;
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
    this.isConnecting = false;
  }

  /**
   * Get connection status
   */
  getStatus(): {
    connected: boolean;
    connecting: boolean;
    reconnectAttempts: number;
  } {
    return {
      connected: this.isConnected,
      connecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts,
    };
  }
}

// Singleton instance
let wsManagerInstance: WebSocketManager | null = null;

/**
 * Get WebSocket manager singleton
 */
export function getWebSocketManager(): WebSocketManager {
  if (!wsManagerInstance) {
    wsManagerInstance = new WebSocketManager();
    
    // Auto-connect in browser
    if (typeof window !== 'undefined') {
      wsManagerInstance.connect();
    }
  }
  
  return wsManagerInstance;
}

/**
 * React hook for WebSocket
 */
export function useWebSocket() {
  return getWebSocketManager();
}
