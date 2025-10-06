/**
 * WEBSOCKET PROVIDER
 * React provider to initialize WebSocket connection and channels
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { getWebSocketManager, WebSocketManager } from './WebSocketManager';
import { setupWebSocketChannels } from './channels';

interface WebSocketContextValue {
  ws: WebSocketManager;
  connected: boolean;
  connecting: boolean;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export interface WebSocketProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
  showConnectionStatus?: boolean;
}

export function WebSocketProvider({
  children,
  autoConnect = true,
  showConnectionStatus = true,
}: WebSocketProviderProps) {
  const [ws] = useState(() => getWebSocketManager());
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    // Setup all channels
    setupWebSocketChannels();

    // Update connection status
    const updateStatus = () => {
      const status = ws.getStatus();
      setConnected(status.connected);
      setConnecting(status.connecting);
    };

    // Listen to connection events
    const unsubscribeOpen = ws.onOpen(() => {
      updateStatus();
    });

    const unsubscribeClose = ws.onClose(() => {
      updateStatus();
    });

    // Auto-connect if enabled
    if (autoConnect) {
      ws.connect();
    }

    // Initial status
    updateStatus();

    // Cleanup
    return () => {
      unsubscribeOpen();
      unsubscribeClose();
    };
  }, [ws, autoConnect]);

  return (
    <WebSocketContext.Provider value={{ ws, connected, connecting }}>
      {children}
      
      {/* Connection Status Indicator */}
      {showConnectionStatus && (
        <div className="fixed bottom-4 right-4 z-50">
          {connecting && (
            <div className="bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 animate-pulse">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-sm font-medium">Connecting...</span>
            </div>
          )}
          
          {!connecting && !connected && (
            <div className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-sm font-medium">Disconnected</span>
            </div>
          )}
          
          {connected && (
            <div className="bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 opacity-0 hover:opacity-100 transition-opacity">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Connected</span>
            </div>
          )}
        </div>
      )}
    </WebSocketContext.Provider>
  );
}

/**
 * Hook to access WebSocket context
 */
export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  
  return context;
}
