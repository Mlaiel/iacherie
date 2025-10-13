/**
 * 👥 Real-time Collaboration System - Presence & Live Editing
 * 
 * @fileoverview WebSocket-powered collaboration with presence indicators
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Lead Dev IA + Collaboration Expert + WebSocket Specialist
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useWebSocket } from '../../core/api/hooks';

// === COLLABORATION INTERFACES ===

export interface CollaboratorPresence {
  userId: string;
  userName: string;
  userAvatar?: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen: Date;
  currentLocation?: string; // Current page/section
  isTyping?: boolean;
  cursor?: {
    x: number;
    y: number;
    elementId?: string;
  };
}

export interface CollaborationMessage {
  type: 'presence_update' | 'cursor_move' | 'selection_change' | 'typing_start' | 'typing_stop' | 'user_join' | 'user_leave';
  userId: string;
  timestamp: string;
  data: any;
}

export interface ActiveUsers {
  [userId: string]: CollaboratorPresence;
}

interface CollaborationContextType {
  activeUsers: ActiveUsers;
  currentUser: CollaboratorPresence | null;
  isConnected: boolean;
  updatePresence: (updates: Partial<CollaboratorPresence>) => void;
  sendCursorUpdate: (x: number, y: number, elementId?: string) => void;
  setTypingStatus: (isTyping: boolean) => void;
  joinRoom: (roomId: string) => void;
  leaveRoom: () => void;
  currentRoom: string | null;
}

// === COLLABORATION CONTEXT ===

const CollaborationContext = createContext<CollaborationContextType | undefined>(undefined);

export function useCollaboration(): CollaborationContextType {
  const context = useContext(CollaborationContext);
  if (context === undefined) {
    throw new Error('useCollaboration must be used within a CollaborationProvider');
  }
  return context;
}

// === COLLABORATION PROVIDER ===

interface CollaborationProviderProps {
  children: ReactNode;
  userId: string;
  userName: string;
  userAvatar?: string;
}

export function CollaborationProvider({ 
  children, 
  userId, 
  userName, 
  userAvatar 
}: CollaborationProviderProps) {
  const [activeUsers, setActiveUsers] = useState<ActiveUsers>({});
  const [currentUser, setCurrentUser] = useState<CollaboratorPresence | null>(null);
  const [currentRoom, setCurrentRoom] = useState<string | null>(null);

  const wsUrl = process.env.NEXT_PUBLIC_CHAT_WS || 'ws://localhost:8000/ws/collaboration';
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const { isConnected, lastMessage, sendMessage } = useWebSocket(wsUrl, {
    authToken: authToken || undefined,
    autoReconnect: true,
    heartbeatInterval: 15000
  });

  // Initialize current user
  useEffect(() => {
    if (userId && userName) {
      const user: CollaboratorPresence = {
        userId,
        userName,
        userAvatar,
        status: 'online',
        lastSeen: new Date(),
        currentLocation: window.location.pathname
      };
      setCurrentUser(user);
      
      // Update active users with current user
      setActiveUsers(prev => ({
        ...prev,
        [userId]: user
      }));
    }
  }, [userId, userName, userAvatar]);

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    const message: CollaborationMessage = lastMessage;
    
    switch (message.type) {
      case 'presence_update':
        setActiveUsers(prev => ({
          ...prev,
          [message.userId]: {
            ...prev[message.userId],
            ...message.data,
            lastSeen: new Date(message.timestamp)
          }
        }));
        break;

      case 'user_join':
        setActiveUsers(prev => ({
          ...prev,
          [message.userId]: {
            ...message.data,
            lastSeen: new Date(message.timestamp)
          }
        }));
        console.log('👥 User joined collaboration:', message.data.userName);
        break;

      case 'user_leave':
        setActiveUsers(prev => {
          const updated = { ...prev };
          delete updated[message.userId];
          return updated;
        });
        console.log('👥 User left collaboration:', message.userId);
        break;

      case 'cursor_move':
        setActiveUsers(prev => ({
          ...prev,
          [message.userId]: {
            ...prev[message.userId],
            cursor: message.data.cursor,
            lastSeen: new Date(message.timestamp)
          }
        }));
        break;

      case 'typing_start':
      case 'typing_stop':
        setActiveUsers(prev => ({
          ...prev,
          [message.userId]: {
            ...prev[message.userId],
            isTyping: message.type === 'typing_start',
            lastSeen: new Date(message.timestamp)
          }
        }));
        break;
    }
  }, [lastMessage]);

  // Update presence information
  const updatePresence = useCallback((updates: Partial<CollaboratorPresence>) => {
    if (!currentUser) return;

    const updatedUser = {
      ...currentUser,
      ...updates,
      lastSeen: new Date()
    };

    setCurrentUser(updatedUser);
    setActiveUsers(prev => ({
      ...prev,
      [userId]: updatedUser
    }));

    // Send presence update to other users
    sendMessage({
      type: 'presence_update',
      userId,
      data: updates
    });
  }, [currentUser, userId, sendMessage]);

  // Send cursor position update
  const sendCursorUpdate = useCallback((x: number, y: number, elementId?: string) => {
    if (!isConnected || !currentRoom) return;

    const cursor = { x, y, elementId };
    
    sendMessage({
      type: 'cursor_move',
      userId,
      data: { cursor }
    });

    // Update local state
    setActiveUsers(prev => ({
      ...prev,
      [userId]: {
        ...prev[userId],
        cursor,
        lastSeen: new Date()
      }
    }));
  }, [isConnected, currentRoom, userId, sendMessage]);

  // Set typing status
  const setTypingStatus = useCallback((isTyping: boolean) => {
    if (!isConnected || !currentRoom) return;

    sendMessage({
      type: isTyping ? 'typing_start' : 'typing_stop',
      userId,
      data: { isTyping }
    });
  }, [isConnected, currentRoom, userId, sendMessage]);

  // Join collaboration room
  const joinRoom = useCallback((roomId: string) => {
    if (!isConnected || !currentUser) return;

    setCurrentRoom(roomId);
    
    sendMessage({
      type: 'user_join',
      userId,
      data: {
        ...currentUser,
        roomId
      }
    });

    console.log('👥 Joined collaboration room:', roomId);
  }, [isConnected, currentUser, userId, sendMessage]);

  // Leave collaboration room
  const leaveRoom = useCallback(() => {
    if (!isConnected || !currentRoom) return;

    sendMessage({
      type: 'user_leave',
      userId,
      data: { roomId: currentRoom }
    });

    setCurrentRoom(null);
    setActiveUsers({}); // Clear other users when leaving room
    
    console.log('👥 Left collaboration room');
  }, [isConnected, currentRoom, userId, sendMessage]);

  // Track mouse movement for cursor sharing
  useEffect(() => {
    if (!isConnected || !currentRoom) return;

    let lastUpdate = 0;
    const THROTTLE_MS = 100; // Throttle cursor updates

    const handleMouseMove = (event: MouseEvent) => {
      const now = Date.now();
      if (now - lastUpdate < THROTTLE_MS) return;
      
      lastUpdate = now;
      
      const target = event.target as HTMLElement;
      const elementId = target.id || target.className || undefined;
      
      sendCursorUpdate(event.clientX, event.clientY, elementId);
    };

    document.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [isConnected, currentRoom, sendCursorUpdate]);

  // Update presence when location changes
  useEffect(() => {
    updatePresence({ currentLocation: window.location.pathname });
  }, [updatePresence]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      const status = document.hidden ? 'away' : 'online';
      updatePresence({ status });
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [updatePresence]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (currentRoom) {
        leaveRoom();
      }
    };
  }, [currentRoom, leaveRoom]);

  const contextValue: CollaborationContextType = {
    activeUsers,
    currentUser,
    isConnected,
    updatePresence,
    sendCursorUpdate,
    setTypingStatus,
    joinRoom,
    leaveRoom,
    currentRoom
  };

  return (
    <CollaborationContext.Provider value={contextValue}>
      {children}
      <CollaborationOverlay />
    </CollaborationContext.Provider>
  );
}

// === COLLABORATION OVERLAY (CURSORS & INDICATORS) ===

function CollaborationOverlay() {
  const { activeUsers, currentUser } = useCollaboration();

  return (
    <>
      {/* Remote Cursors */}
      {Object.values(activeUsers)
        .filter(user => user.userId !== currentUser?.userId && user.cursor)
        .map(user => (
          <RemoteCursor
            key={user.userId}
            user={user}
            x={user.cursor!.x}
            y={user.cursor!.y}
          />
        ))}
    </>
  );
}

// === REMOTE CURSOR COMPONENT ===

interface RemoteCursorProps {
  user: CollaboratorPresence;
  x: number;
  y: number;
}

function RemoteCursor({ user, x, y }: RemoteCursorProps) {
  const cursorColor = getUserColor(user.userId);

  return (
    <div 
      className="fixed pointer-events-none z-50 transition-all duration-100"
      style={{ 
        left: x, 
        top: y,
        transform: 'translate(-2px, -2px)'
      }}
    >
      {/* Cursor Arrow */}
      <svg 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill="none"
        className="drop-shadow-lg"
      >
        <path
          d="M5.65 5.65L18.35 12L12.7 13.3L11.4 18.95L5.65 5.65Z"
          fill={cursorColor}
          stroke="white"
          strokeWidth="1"
        />
      </svg>

      {/* User Name Label */}
      <div 
        className="absolute top-6 left-2 px-2 py-1 text-xs font-medium text-white rounded-md shadow-lg whitespace-nowrap"
        style={{ backgroundColor: cursorColor }}
      >
        {user.userName}
        {user.isTyping && (
          <span className="ml-1 animate-pulse">✏️</span>
        )}
      </div>
    </div>
  );
}

// === UTILITY FUNCTIONS ===

function getUserColor(userId: string): string {
  // Generate consistent color for user based on their ID
  const colors = [
    '#EF4444', '#F97316', '#F59E0B', '#84CC16', 
    '#22C55E', '#10B981', '#06B6D4', '#3B82F6',
    '#6366F1', '#8B5CF6', '#A855F7', '#EC4899'
  ];
  
  const hash = userId.split('').reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc);
  }, 0);
  
  return colors[Math.abs(hash) % colors.length];
}

export default CollaborationProvider;