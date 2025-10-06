/**
 * WEBSOCKET MODULE
 * Centralized exports for WebSocket system
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

// Core manager
export { WebSocketManager, getWebSocketManager, useWebSocket } from './WebSocketManager';

// Provider
export { WebSocketProvider, useWebSocketContext } from './WebSocketProvider';
export type { WebSocketProviderProps } from './WebSocketProvider';

// Channels and events
export { setupWebSocketChannels, CHANNELS, EVENTS } from './channels';

// Hooks
export {
  useWebSocketChannel,
  useWebSocketStatus,
  useWebSocketSend,
  useCrawlersWebSocket,
  useGeneratorsWebSocket,
  useChatroomWebSocket,
  useAnalyticsWebSocket,
  useNotificationsWebSocket,
  useAutomationWebSocket,
} from './hooks';

// Types
export type { MessageHandler } from './WebSocketManager';
