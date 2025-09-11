/**
 * ⚡ Real-time Manager - Enterprise Real-time Communication Hub
 * 
 * @fileoverview Advanced real-time communication and WebSocket management
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { useState, useCallback, useEffect, useRef } from 'react';

// ====================================================================
// REAL-TIME INTERFACES
// ====================================================================

export interface RealtimeManagerState {
  isConnected: boolean;
  connectionQuality: 'excellent' | 'good' | 'poor' | 'disconnected';
  activeChannels: RealtimeChannel[];
  subscribers: Map<string, RealtimeSubscriber[]>;
  messageQueue: QueuedMessage[];
  metrics: RealtimeMetrics;
  presence: PresenceData;
}

export interface RealtimeChannel {
  id: string;
  name: string;
  type: 'public' | 'private' | 'presence';
  subscribers: number;
  lastActivity: number;
  messageCount: number;
  encryption: boolean;
  compression: boolean;
}

export interface RealtimeSubscriber {
  id: string;
  userId: string;
  channelId: string;
  permissions: string[];
  joinedAt: number;
  lastSeen: number;
  metadata: Record<string, any>;
}

export interface QueuedMessage {
  id: string;
  channelId: string;
  type: string;
  payload: any;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

export interface RealtimeMetrics {
  messagesPerSecond: number;
  bytesPerSecond: number;
  latency: number;
  uptime: number;
  reconnections: number;
  errorRate: number;
  totalMessages: number;
  totalBytes: number;
}

export interface PresenceData {
  users: PresenceUser[];
  totalUsers: number;
  activeUsers: number;
  channels: Record<string, ChannelPresence>;
}

export interface PresenceUser {
  userId: string;
  username: string;
  avatar?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen: number;
  location?: {
    channel: string;
    page: string;
    activity: string;
  };
  metadata: Record<string, any>;
}

export interface ChannelPresence {
  userCount: number;
  users: string[];
  lastUpdate: number;
}

export interface RealtimeMessage {
  id: string;
  channelId: string;
  senderId: string;
  senderName: string;
  type: MessageType;
  content: any;
  timestamp: number;
  metadata?: MessageMetadata;
  reactions?: MessageReaction[];
  replies?: RealtimeMessage[];
}

export type MessageType = 
  | 'text'
  | 'image' 
  | 'video'
  | 'audio'
  | 'file'
  | 'system'
  | 'notification'
  | 'typing'
  | 'presence'
  | 'collaboration'
  | 'ai-suggestion'
  | 'status-update'
  | 'error';

export interface MessageMetadata {
  edited?: boolean;
  editedAt?: number;
  deleted?: boolean;
  deletedAt?: number;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  expires?: number;
  encrypted?: boolean;
  threadId?: string;
  replyTo?: string;
  mentions?: string[];
  attachments?: MessageAttachment[];
}

export interface MessageAttachment {
  id: string;
  type: 'image' | 'video' | 'audio' | 'file';
  url: string;
  name: string;
  size: number;
  mimeType: string;
  thumbnail?: string;
}

export interface MessageReaction {
  emoji: string;
  users: string[];
  count: number;
  timestamp: number;
}

// ====================================================================
// REAL-TIME MANAGER IMPLEMENTATION
// ====================================================================

export class RealtimeManager {
  private websocket: WebSocket | null = null;
  private config: RealtimeConfig;
  private channels: Map<string, RealtimeChannel>;
  private subscribers: Map<string, RealtimeSubscriber[]>;
  private messageQueue: QueuedMessage[];
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private isReconnecting: boolean = false;
  private eventHandlers: Map<string, Function[]>;
  private metrics: RealtimeMetrics;
  private presenceData: PresenceData;

  constructor(config: RealtimeConfig) {
    this.config = config;
    this.channels = new Map();
    this.subscribers = new Map();
    this.messageQueue = [];
    this.eventHandlers = new Map();
    this.metrics = this.initializeMetrics();
    this.presenceData = this.initializePresence();

    this.connect();
  }

  /**
   * Establish WebSocket connection
   */
  private async connect(): Promise<void> {
    try {
      const wsUrl = this.buildWebSocketUrl();
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = this.handleOpen.bind(this);
      this.websocket.onmessage = this.handleMessage.bind(this);
      this.websocket.onclose = this.handleClose.bind(this);
      this.websocket.onerror = this.handleError.bind(this);

    } catch (error) {
      console.error('Failed to establish WebSocket connection:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket connection opened
   */
  private handleOpen(event: Event): void {
    console.log('WebSocket connection established');
    this.reconnectAttempts = 0;
    this.isReconnecting = false;
    
    this.startHeartbeat();
    this.authenticate();
    this.processMessageQueue();
    
    this.emit('connection:open', { timestamp: Date.now() });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data);
      this.updateMetrics('message_received', event.data.length);
      
      switch (message.type) {
        case 'message':
          this.handleChannelMessage(message);
          break;
        case 'presence':
          this.handlePresenceUpdate(message);
          break;
        case 'system':
          this.handleSystemMessage(message);
          break;
        case 'ping':
          this.handlePing(message);
          break;
        case 'pong':
          this.handlePong(message);
          break;
        case 'error':
          this.handleServerError(message);
          break;
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket connection closed
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket connection closed:', event.code, event.reason);
    
    this.stopHeartbeat();
    this.emit('connection:close', { 
      code: event.code, 
      reason: event.reason, 
      timestamp: Date.now() 
    });

    if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket errors
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.updateMetrics('error');
    this.emit('connection:error', { error: event, timestamp: Date.now() });
  }

  /**
   * Authenticate with the server
   */
  private authenticate(): void {
    const authMessage = {
      type: 'auth',
      token: this.config.authToken,
      userId: this.config.userId,
      metadata: {
        userAgent: navigator.userAgent,
        timestamp: Date.now(),
        version: this.config.version || '1.0.0'
      }
    };

    this.send(authMessage);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.websocket?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval || 30000);
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
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.isReconnecting) return;
    
    this.isReconnecting = true;
    this.reconnectAttempts++;
    
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect();
    }, delay);
  }

  // ====================================================================
  // CHANNEL MANAGEMENT
  // ====================================================================

  /**
   * Subscribe to a channel
   */
  public subscribe(channelId: string, options: SubscribeOptions = {}): string {
    const subscriptionId = this.generateSubscriptionId();
    
    const subscriber: RealtimeSubscriber = {
      id: subscriptionId,
      userId: this.config.userId,
      channelId,
      permissions: options.permissions || ['read'],
      joinedAt: Date.now(),
      lastSeen: Date.now(),
      metadata: options.metadata || {}
    };

    // Add to local subscribers
    if (!this.subscribers.has(channelId)) {
      this.subscribers.set(channelId, []);
    }
    this.subscribers.get(channelId)!.push(subscriber);

    // Send subscription request to server
    const subscribeMessage = {
      type: 'subscribe',
      channelId,
      subscriptionId,
      options
    };

    this.send(subscribeMessage);
    
    return subscriptionId;
  }

  /**
   * Unsubscribe from a channel
   */
  public unsubscribe(subscriptionId: string): boolean {
    for (const [channelId, subscribers] of this.subscribers.entries()) {
      const index = subscribers.findIndex(sub => sub.id === subscriptionId);
      if (index !== -1) {
        subscribers.splice(index, 1);
        
        // Clean up empty channel
        if (subscribers.length === 0) {
          this.subscribers.delete(channelId);
        }

        // Send unsubscribe message to server
        this.send({
          type: 'unsubscribe',
          subscriptionId,
          channelId
        });

        return true;
      }
    }
    return false;
  }

  /**
   * Send message to channel
   */
  public sendMessage(channelId: string, content: any, type: MessageType = 'text'): string {
    const messageId = this.generateMessageId();
    
    const message: RealtimeMessage = {
      id: messageId,
      channelId,
      senderId: this.config.userId,
      senderName: this.config.username || 'Unknown',
      type,
      content,
      timestamp: Date.now()
    };

    const queuedMessage: QueuedMessage = {
      id: messageId,
      channelId,
      type: 'channel_message',
      payload: message,
      priority: 'normal',
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries: 3
    };

    if (this.isConnected()) {
      this.send({
        ...message,
        messageType: 'message'  // Use different property name to avoid conflict
      });
    } else {
      this.messageQueue.push(queuedMessage);
    }

    return messageId;
  }

  // ====================================================================
  // PRESENCE MANAGEMENT
  // ====================================================================

  /**
   * Update user presence
   */
  public updatePresence(status: PresenceUser['status'], metadata?: Record<string, any>): void {
    const presenceUpdate = {
      type: 'presence_update',
      userId: this.config.userId,
      status,
      metadata: {
        ...metadata,
        timestamp: Date.now()
      }
    };

    this.send(presenceUpdate);
  }

  /**
   * Get channel presence
   */
  public getChannelPresence(channelId: string): ChannelPresence | null {
    return this.presenceData.channels[channelId] || null;
  }

  /**
   * Get user presence
   */
  public getUserPresence(userId: string): PresenceUser | null {
    return this.presenceData.users.find(user => user.userId === userId) || null;
  }

  // ====================================================================
  // MESSAGE HANDLERS
  // ====================================================================

  private handleChannelMessage(message: any): void {
    const realtimeMessage: RealtimeMessage = {
      id: message.id,
      channelId: message.channelId,
      senderId: message.senderId,
      senderName: message.senderName,
      type: message.type,
      content: message.content,
      timestamp: message.timestamp,
      metadata: message.metadata,
      reactions: message.reactions,
      replies: message.replies
    };

    this.emit(`channel:${message.channelId}:message`, realtimeMessage);
    this.emit('message', realtimeMessage);
  }

  private handlePresenceUpdate(message: any): void {
    const { userId, status, metadata } = message;
    
    // Update local presence data
    const userIndex = this.presenceData.users.findIndex(user => user.userId === userId);
    if (userIndex !== -1) {
      this.presenceData.users[userIndex] = {
        ...this.presenceData.users[userIndex],
        status,
        lastSeen: Date.now(),
        metadata: { ...this.presenceData.users[userIndex].metadata, ...metadata }
      };
    } else {
      this.presenceData.users.push({
        userId,
        username: metadata.username || 'Unknown',
        avatar: metadata.avatar,
        status,
        lastSeen: Date.now(),
        metadata
      });
    }

    this.emit('presence:update', { userId, status, metadata });
  }

  private handleSystemMessage(message: any): void {
    switch (message.subtype) {
      case 'channel_joined':
        this.handleChannelJoined(message);
        break;
      case 'channel_left':
        this.handleChannelLeft(message);
        break;
      case 'user_banned':
        this.handleUserBanned(message);
        break;
      default:
        this.emit('system', message);
    }
  }

  private handleChannelJoined(message: any): void {
    const channel: RealtimeChannel = {
      id: message.channelId,
      name: message.channelName,
      type: message.channelType,
      subscribers: message.subscriberCount,
      lastActivity: Date.now(),
      messageCount: 0,
      encryption: message.encryption || false,
      compression: message.compression || false
    };

    this.channels.set(message.channelId, channel);
    this.emit('channel:joined', channel);
  }

  private handleChannelLeft(message: any): void {
    this.channels.delete(message.channelId);
    this.subscribers.delete(message.channelId);
    this.emit('channel:left', { channelId: message.channelId });
  }

  private handleUserBanned(message: any): void {
    // Remove user from all channels
    for (const subscribers of this.subscribers.values()) {
      const index = subscribers.findIndex(sub => sub.userId === message.userId);
      if (index !== -1) {
        subscribers.splice(index, 1);
      }
    }

    this.emit('user:banned', { userId: message.userId, reason: message.reason });
  }

  private handlePing(message: any): void {
    this.send({ type: 'pong', timestamp: Date.now() });
  }

  private handlePong(message: any): void {
    const latency = Date.now() - message.timestamp;
    this.metrics.latency = latency;
    this.updateMetrics('pong', 0, { latency });
  }

  private handleServerError(message: any): void {
    console.error('Server error:', message);
    this.emit('error', message);
  }

  // ====================================================================
  // UTILITY METHODS
  // ====================================================================

  private buildWebSocketUrl(): string {
    const protocol = this.config.secure ? 'wss:' : 'ws:';
    const params = new URLSearchParams({
      token: this.config.authToken,
      userId: this.config.userId,
      version: this.config.version || '1.0.0'
    });

    return `${protocol}//${this.config.host}:${this.config.port}${this.config.path}?${params}`;
  }

  private send(message: any): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      const serialized = JSON.stringify(message);
      this.websocket.send(serialized);
      this.updateMetrics('message_sent', serialized.length);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  }

  private processMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send({
          type: message.type,
          ...message.payload
        });
      }
    }
  }

  private isConnected(): boolean {
    return this.websocket?.readyState === WebSocket.OPEN;
  }

  private generateSubscriptionId(): string {
    return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // ====================================================================
  // EVENT SYSTEM
  // ====================================================================

  public on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  public off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  // ====================================================================
  // METRICS
  // ====================================================================

  private initializeMetrics(): RealtimeMetrics {
    return {
      messagesPerSecond: 0,
      bytesPerSecond: 0,
      latency: 0,
      uptime: Date.now(),
      reconnections: 0,
      errorRate: 0,
      totalMessages: 0,
      totalBytes: 0
    };
  }

  private initializePresence(): PresenceData {
    return {
      users: [],
      totalUsers: 0,
      activeUsers: 0,
      channels: {}
    };
  }

  private updateMetrics(event: string, bytes: number = 0, data?: any): void {
    switch (event) {
      case 'message_sent':
      case 'message_received':
        this.metrics.totalMessages++;
        this.metrics.totalBytes += bytes;
        break;
      case 'error':
        this.metrics.errorRate += 0.01;
        break;
      case 'pong':
        if (data?.latency) {
          this.metrics.latency = data.latency;
        }
        break;
    }
  }

  // ====================================================================
  // PUBLIC API
  // ====================================================================

  public getState(): RealtimeManagerState {
    return {
      isConnected: this.isConnected(),
      connectionQuality: this.getConnectionQuality(),
      activeChannels: Array.from(this.channels.values()),
      subscribers: this.subscribers,
      messageQueue: this.messageQueue,
      metrics: this.metrics,
      presence: this.presenceData
    };
  }

  private getConnectionQuality(): 'excellent' | 'good' | 'poor' | 'disconnected' {
    if (!this.isConnected()) return 'disconnected';
    
    if (this.metrics.latency < 100) return 'excellent';
    if (this.metrics.latency < 300) return 'good';
    return 'poor';
  }

  public disconnect(): void {
    if (this.websocket) {
      this.websocket.close(1000, 'Client disconnecting');
    }
    this.stopHeartbeat();
  }

  public getMetrics(): RealtimeMetrics {
    return { ...this.metrics };
  }

  public getChannels(): RealtimeChannel[] {
    return Array.from(this.channels.values());
  }
}

// ====================================================================
// CONFIGURATION INTERFACES
// ====================================================================

export interface RealtimeConfig {
  host: string;
  port: number;
  path: string;
  secure: boolean;
  authToken: string;
  userId: string;
  username?: string;
  heartbeatInterval?: number;
  reconnectAttempts?: number;
  version?: string;
}

export interface SubscribeOptions {
  permissions?: string[];
  metadata?: Record<string, any>;
  presence?: boolean;
  history?: number;
}

// ====================================================================
// REACT HOOK
// ====================================================================

export const useRealtimeManager = (config: RealtimeConfig) => {
  const [state, setState] = useState<RealtimeManagerState | null>(null);
  const managerRef = useRef<RealtimeManager | null>(null);

  useEffect(() => {
    managerRef.current = new RealtimeManager(config);
    
    const updateState = () => {
      if (managerRef.current) {
        setState(managerRef.current.getState());
      }
    };

    // Set up event listeners
    managerRef.current.on('connection:open', updateState);
    managerRef.current.on('connection:close', updateState);
    managerRef.current.on('connection:error', updateState);
    managerRef.current.on('channel:joined', updateState);
    managerRef.current.on('channel:left', updateState);
    managerRef.current.on('presence:update', updateState);

    updateState();
    const interval = setInterval(updateState, 5000);

    return () => {
      clearInterval(interval);
      if (managerRef.current) {
        managerRef.current.disconnect();
      }
    };
  }, [config]);

  const subscribe = useCallback((channelId: string, options?: SubscribeOptions) => {
    return managerRef.current?.subscribe(channelId, options) || '';
  }, []);

  const unsubscribe = useCallback((subscriptionId: string) => {
    return managerRef.current?.unsubscribe(subscriptionId) || false;
  }, []);

  const sendMessage = useCallback((channelId: string, content: any, type?: MessageType) => {
    return managerRef.current?.sendMessage(channelId, content, type) || '';
  }, []);

  const updatePresence = useCallback((status: PresenceUser['status'], metadata?: Record<string, any>) => {
    managerRef.current?.updatePresence(status, metadata);
  }, []);

  const on = useCallback((event: string, handler: Function) => {
    managerRef.current?.on(event, handler);
  }, []);

  const off = useCallback((event: string, handler: Function) => {
    managerRef.current?.off(event, handler);
  }, []);

  return {
    state,
    subscribe,
    unsubscribe,
    sendMessage,
    updatePresence,
    on,
    off,
    manager: managerRef.current
  };
};

export default RealtimeManager;