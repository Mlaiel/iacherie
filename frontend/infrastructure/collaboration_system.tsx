/**
 * 🔗 Real-time Collaboration System - Advanced Multi-User Workspace
 * 
 * @fileoverview Enterprise real-time collaboration with WebSocket, presence, and synchronization
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useEffect, useCallback, createContext, useContext, useRef } from 'react';

// === COLLABORATION TYPES ===

export interface CollaborationUser {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen: number;
  cursor?: CursorPosition;
  selection?: SelectionRange;
  permissions: Permission[];
}

export interface CursorPosition {
  x: number;
  y: number;
  elementId?: string;
  color?: string;
}

export interface SelectionRange {
  start: number;
  end: number;
  elementId: string;
  color?: string;
}

export interface Permission {
  resource: string;
  actions: ('read' | 'write' | 'delete' | 'share' | 'admin')[];
  conditions?: PermissionCondition[];
}

export interface PermissionCondition {
  type: 'time' | 'location' | 'content_type' | 'custom';
  value: any;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than';
}

export interface CollaborationSession {
  id: string;
  workspaceId: string;
  resourceId: string;
  resourceType: 'document' | 'project' | 'media' | 'canvas' | 'code';
  participants: CollaborationUser[];
  createdAt: number;
  lastActivity: number;
  isActive: boolean;
  metadata?: {
    title?: string;
    description?: string;
    version?: string;
    lockStatus?: LockStatus;
  };
}

export interface LockStatus {
  isLocked: boolean;
  lockedBy?: string;
  lockedAt?: number;
  lockType: 'exclusive' | 'section' | 'element';
  lockScope?: string;
}

export interface CollaborationEvent {
  id: string;
  type: 'user_joined' | 'user_left' | 'cursor_moved' | 'selection_changed' | 'content_changed' | 'comment_added' | 'lock_acquired' | 'lock_released';
  userId: string;
  sessionId: string;
  timestamp: number;
  data: any;
  syncRequired?: boolean;
}

export interface ContentOperation {
  id: string;
  type: 'insert' | 'delete' | 'replace' | 'move' | 'format';
  position: number | { start: number; end: number };
  content?: any;
  userId: string;
  timestamp: number;
  parentOperationId?: string;
}

export interface Comment {
  id: string;
  content: string;
  authorId: string;
  position: CommentPosition;
  timestamp: number;
  resolved: boolean;
  replies: CommentReply[];
  mentions: string[];
}

export interface CommentPosition {
  elementId?: string;
  x?: number;
  y?: number;
  range?: { start: number; end: number };
}

export interface CommentReply {
  id: string;
  content: string;
  authorId: string;
  timestamp: number;
}

// === WEBSOCKET MANAGER ===

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  enableCompression: boolean;
  enableBinaryMessages: boolean;
}

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageQueue: any[] = [];
  private connectionState: 'connecting' | 'connected' | 'disconnected' | 'reconnecting' = 'disconnected';
  private eventHandlers: Map<string, Function[]> = new Map();

  constructor(config: WebSocketConfig) {
    this.config = config;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.connectionState = 'connecting';
        this.ws = new WebSocket(this.config.url, this.config.protocols);
        
        this.ws.onopen = () => {
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          this.connectionState = 'disconnected';
          this.stopHeartbeat();
          this.emit('disconnected', event);
          
          if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.reconnect();
          }
        };

        this.ws.onerror = (error) => {
          this.emit('error', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.connectionState = 'disconnected';
  }

  send(message: any): void {
    if (this.connectionState === 'connected' && this.ws) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  private handleMessage(data: any): void {
    switch (data.type) {
      case 'heartbeat':
        this.send({ type: 'heartbeat_ack' });
        break;
      case 'collaboration_event':
        this.emit('collaboration_event', data.payload);
        break;
      case 'user_presence':
        this.emit('user_presence', data.payload);
        break;
      case 'content_operation':
        this.emit('content_operation', data.payload);
        break;
      case 'comment':
        this.emit('comment', data.payload);
        break;
      default:
        this.emit('message', data);
    }
  }

  private reconnect(): void {
    this.connectionState = 'reconnecting';
    this.reconnectAttempts++;
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.config.maxReconnectAttempts) {
        this.connect().catch(() => {
          // Will retry again if needed
        });
      }
    }, this.config.reconnectInterval * this.reconnectAttempts);
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'heartbeat', timestamp: Date.now() });
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  getConnectionState(): string {
    return this.connectionState;
  }
}

// === COLLABORATION CONTEXT ===

interface CollaborationContextValue {
  session: CollaborationSession | null;
  currentUser: CollaborationUser | null;
  participants: CollaborationUser[];
  comments: Comment[];
  operations: ContentOperation[];
  isConnected: boolean;
  joinSession: (sessionId: string, user: CollaborationUser) => Promise<void>;
  leaveSession: () => void;
  updateCursor: (position: CursorPosition) => void;
  updateSelection: (selection: SelectionRange) => void;
  sendOperation: (operation: Omit<ContentOperation, 'id' | 'userId' | 'timestamp'>) => void;
  addComment: (comment: Omit<Comment, 'id' | 'authorId' | 'timestamp' | 'replies'>) => void;
  resolveComment: (commentId: string) => void;
  acquireLock: (scope: string, type?: LockStatus['lockType']) => Promise<boolean>;
  releaseLock: (scope: string) => void;
  hasPermission: (resource: string, action: string) => boolean;
}

const CollaborationContext = createContext<CollaborationContextValue | null>(null);

export const useCollaboration = () => {
  const context = useContext(CollaborationContext);
  if (!context) {
    throw new Error('useCollaboration must be used within a CollaborationProvider');
  }
  return context;
};

// === COLLABORATION PROVIDER ===

interface CollaborationProviderProps {
  children: React.ReactNode;
  websocketUrl: string;
  onError?: (error: any) => void;
}

export const CollaborationProvider: React.FC<CollaborationProviderProps> = ({
  children,
  websocketUrl,
  onError
}) => {
  const [session, setSession] = useState<CollaborationSession | null>(null);
  const [currentUser, setCurrentUser] = useState<CollaborationUser | null>(null);
  const [participants, setParticipants] = useState<CollaborationUser[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [operations, setOperations] = useState<ContentOperation[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const wsManager = useRef<WebSocketManager | null>(null);

  useEffect(() => {
    wsManager.current = new WebSocketManager({
      url: websocketUrl,
      reconnectInterval: 1000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      enableCompression: true,
      enableBinaryMessages: false
    });

    wsManager.current.on('connected', () => {
      setIsConnected(true);
    });

    wsManager.current.on('disconnected', () => {
      setIsConnected(false);
    });

    wsManager.current.on('error', (error: any) => {
      onError?.(error);
    });

    wsManager.current.on('collaboration_event', handleCollaborationEvent);
    wsManager.current.on('user_presence', handleUserPresence);
    wsManager.current.on('content_operation', handleContentOperation);
    wsManager.current.on('comment', handleComment);

    return () => {
      wsManager.current?.disconnect();
    };
  }, [websocketUrl, onError]);

  const handleCollaborationEvent = useCallback((event: CollaborationEvent) => {
    switch (event.type) {
      case 'user_joined':
        setParticipants(prev => {
          const existing = prev.find(p => p.id === event.data.user.id);
          if (existing) {
            return prev.map(p => p.id === event.data.user.id ? event.data.user : p);
          }
          return [...prev, event.data.user];
        });
        break;
      case 'user_left':
        setParticipants(prev => prev.filter(p => p.id !== event.data.userId));
        break;
      case 'cursor_moved':
        setParticipants(prev => prev.map(p => 
          p.id === event.userId 
            ? { ...p, cursor: event.data.cursor }
            : p
        ));
        break;
      case 'selection_changed':
        setParticipants(prev => prev.map(p => 
          p.id === event.userId 
            ? { ...p, selection: event.data.selection }
            : p
        ));
        break;
    }
  }, []);

  const handleUserPresence = useCallback((presenceData: any) => {
    setParticipants(prev => prev.map(p => 
      p.id === presenceData.userId 
        ? { ...p, status: presenceData.status, lastSeen: presenceData.timestamp }
        : p
    ));
  }, []);

  const handleContentOperation = useCallback((operation: ContentOperation) => {
    setOperations(prev => [...prev, operation]);
  }, []);

  const handleComment = useCallback((comment: Comment) => {
    setComments(prev => [...prev, comment]);
  }, []);

  const joinSession = useCallback(async (sessionId: string, user: CollaborationUser) => {
    try {
      await wsManager.current?.connect();
      
      wsManager.current?.send({
        type: 'join_session',
        sessionId,
        user
      });

      setCurrentUser(user);
      setSession({
        id: sessionId,
        workspaceId: 'default',
        resourceId: 'default',
        resourceType: 'document',
        participants: [user],
        createdAt: Date.now(),
        lastActivity: Date.now(),
        isActive: true
      });

    } catch (error) {
      onError?.(error);
    }
  }, [onError]);

  const leaveSession = useCallback(() => {
    if (session && currentUser) {
      wsManager.current?.send({
        type: 'leave_session',
        sessionId: session.id,
        userId: currentUser.id
      });
    }

    wsManager.current?.disconnect();
    setSession(null);
    setCurrentUser(null);
    setParticipants([]);
    setComments([]);
    setOperations([]);
  }, [session, currentUser]);

  const updateCursor = useCallback((position: CursorPosition) => {
    if (session && currentUser) {
      wsManager.current?.send({
        type: 'cursor_update',
        sessionId: session.id,
        userId: currentUser.id,
        cursor: position
      });
    }
  }, [session, currentUser]);

  const updateSelection = useCallback((selection: SelectionRange) => {
    if (session && currentUser) {
      wsManager.current?.send({
        type: 'selection_update',
        sessionId: session.id,
        userId: currentUser.id,
        selection
      });
    }
  }, [session, currentUser]);

  const sendOperation = useCallback((operation: Omit<ContentOperation, 'id' | 'userId' | 'timestamp'>) => {
    if (session && currentUser) {
      const fullOperation: ContentOperation = {
        ...operation,
        id: `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        userId: currentUser.id,
        timestamp: Date.now()
      };

      wsManager.current?.send({
        type: 'content_operation',
        sessionId: session.id,
        operation: fullOperation
      });

      setOperations(prev => [...prev, fullOperation]);
    }
  }, [session, currentUser]);

  const addComment = useCallback((comment: Omit<Comment, 'id' | 'authorId' | 'timestamp' | 'replies'>) => {
    if (session && currentUser) {
      const fullComment: Comment = {
        ...comment,
        id: `comment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        authorId: currentUser.id,
        timestamp: Date.now(),
        replies: []
      };

      wsManager.current?.send({
        type: 'add_comment',
        sessionId: session.id,
        comment: fullComment
      });

      setComments(prev => [...prev, fullComment]);
    }
  }, [session, currentUser]);

  const resolveComment = useCallback((commentId: string) => {
    wsManager.current?.send({
      type: 'resolve_comment',
      sessionId: session?.id,
      commentId
    });

    setComments(prev => prev.map(c => 
      c.id === commentId ? { ...c, resolved: true } : c
    ));
  }, [session]);

  const acquireLock = useCallback(async (scope: string, type: LockStatus['lockType'] = 'exclusive'): Promise<boolean> => {
    return new Promise((resolve) => {
      if (session && currentUser) {
        const requestId = `lock_${Date.now()}`;
        
        const handleLockResponse = (response: any) => {
          if (response.requestId === requestId) {
            wsManager.current?.off('lock_response', handleLockResponse);
            resolve(response.granted);
          }
        };

        wsManager.current?.on('lock_response', handleLockResponse);
        
        wsManager.current?.send({
          type: 'acquire_lock',
          sessionId: session.id,
          userId: currentUser.id,
          scope,
          lockType: type,
          requestId
        });

        // Timeout after 5 seconds
        setTimeout(() => {
          wsManager.current?.off('lock_response', handleLockResponse);
          resolve(false);
        }, 5000);
      } else {
        resolve(false);
      }
    });
  }, [session, currentUser]);

  const releaseLock = useCallback((scope: string) => {
    if (session && currentUser) {
      wsManager.current?.send({
        type: 'release_lock',
        sessionId: session.id,
        userId: currentUser.id,
        scope
      });
    }
  }, [session, currentUser]);

  const hasPermission = useCallback((resource: string, action: string): boolean => {
    if (!currentUser) return false;
    
    return currentUser.permissions.some(permission => 
      permission.resource === resource && 
      permission.actions.includes(action as any)
    );
  }, [currentUser]);

  const contextValue: CollaborationContextValue = {
    session,
    currentUser,
    participants,
    comments,
    operations,
    isConnected,
    joinSession,
    leaveSession,
    updateCursor,
    updateSelection,
    sendOperation,
    addComment,
    resolveComment,
    acquireLock,
    releaseLock,
    hasPermission
  };

  return (
    <CollaborationContext.Provider value={contextValue}>
      {children}
    </CollaborationContext.Provider>
  );
};

// === COLLABORATION COMPONENTS ===

interface UserPresenceIndicatorProps {
  users: CollaborationUser[];
  maxVisible?: number;
  className?: string;
}

export const UserPresenceIndicator: React.FC<UserPresenceIndicatorProps> = ({
  users,
  maxVisible = 5,
  className
}) => {
  const visibleUsers = users.slice(0, maxVisible);
  const hiddenCount = users.length - maxVisible;

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className="flex -space-x-2">
        {visibleUsers.map(user => (
          <div
            key={user.id}
            className="relative"
            title={`${user.name} (${user.status})`}
          >
            <div className="w-8 h-8 rounded-full bg-gray-300 border-2 border-white overflow-hidden">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
                  {user.name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
              user.status === 'online' ? 'bg-green-500' :
              user.status === 'away' ? 'bg-yellow-500' :
              user.status === 'busy' ? 'bg-red-500' : 'bg-gray-400'
            }`} />
          </div>
        ))}
      </div>
      
      {hiddenCount > 0 && (
        <div className="w-8 h-8 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center text-xs font-medium text-gray-600">
          +{hiddenCount}
        </div>
      )}
      
      <span className="text-sm text-gray-600">
        {users.length} participant{users.length !== 1 ? 's' : ''}
      </span>
    </div>
  );
};

interface CollaborationStatusProps {
  className?: string;
}

export const CollaborationStatus: React.FC<CollaborationStatusProps> = ({ className }) => {
  const { isConnected, session, participants } = useCollaboration();

  return (
    <div className={`flex items-center space-x-3 p-3 bg-white border rounded-lg ${className}`}>
      <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className="text-sm font-medium text-gray-900">
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
      {session && (
        <UserPresenceIndicator users={participants} maxVisible={3} />
      )}
    </div>
  );
};

export default CollaborationProvider;