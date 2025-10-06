/**
 * WEBSOCKET CHANNELS
 * Predefined channels for all modules
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

import { getWebSocketManager } from './WebSocketManager';
import { 
  useCrawlersStore,
  useStudiosStore,
  useGeneratorsStore,
  useAgentsStore,
  useChatroomsStore,
  useAutomationStore,
  useAnalyticsStore,
  useMonetizationStore
} from '@/lib/store/generated';

/**
 * Setup WebSocket integration with Zustand stores
 */
export function setupWebSocketChannels() {
  const ws = getWebSocketManager();

  // ============================================================================
  // CRAWLERS CHANNEL
  // ============================================================================
  
  // Crawler created
  ws.subscribe('crawlers', 'created', (data) => {
    useCrawlersStore.getState().onItemCreated(data);
  });

  // Crawler updated
  ws.subscribe('crawlers', 'updated', (data) => {
    useCrawlersStore.getState().onItemUpdated(data);
  });

  // Crawler deleted
  ws.subscribe('crawlers', 'deleted', (data) => {
    useCrawlersStore.getState().onItemDeleted(data.id);
  });

  // Crawler status changed
  ws.subscribe('crawlers', 'status_changed', (data) => {
    useCrawlersStore.getState().onStatusChanged(data.id, data.status);
  });

  // Crawler progress update
  ws.subscribe('crawlers', 'progress', (data) => {
    const store = useCrawlersStore.getState();
    const items = store.items;
    const index = items.findIndex(i => i.id === data.id);
    if (index !== -1) {
      items[index].progress = data.progress;
      store.onItemUpdated(items[index]);
    }
  });

  // ============================================================================
  // STUDIOS CHANNEL
  // ============================================================================
  
  ws.subscribe('studios', 'created', (data) => {
    useStudiosStore.getState().onItemCreated(data);
  });

  ws.subscribe('studios', 'updated', (data) => {
    useStudiosStore.getState().onItemUpdated(data);
  });

  ws.subscribe('studios', 'deleted', (data) => {
    useStudiosStore.getState().onItemDeleted(data.id);
  });

  ws.subscribe('studios', 'status_changed', (data) => {
    useStudiosStore.getState().onStatusChanged(data.id, data.status);
  });

  // ============================================================================
  // GENERATORS CHANNEL
  // ============================================================================
  
  ws.subscribe('generators', 'created', (data) => {
    useGeneratorsStore.getState().onItemCreated(data);
  });

  ws.subscribe('generators', 'updated', (data) => {
    useGeneratorsStore.getState().onItemUpdated(data);
  });

  ws.subscribe('generators', 'deleted', (data) => {
    useGeneratorsStore.getState().onItemDeleted(data.id);
  });

  ws.subscribe('generators', 'generation_started', (data) => {
    useGeneratorsStore.getState().onStatusChanged(data.id, 'generating');
  });

  ws.subscribe('generators', 'generation_progress', (data) => {
    const store = useGeneratorsStore.getState();
    const items = store.items;
    const index = items.findIndex(i => i.id === data.id);
    if (index !== -1) {
      items[index].progress = data.progress;
      store.onItemUpdated(items[index]);
    }
  });

  ws.subscribe('generators', 'generation_completed', (data) => {
    useGeneratorsStore.getState().onStatusChanged(data.id, 'completed');
  });

  ws.subscribe('generators', 'generation_failed', (data) => {
    useGeneratorsStore.getState().onStatusChanged(data.id, 'error');
  });

  // ============================================================================
  // AGENTS CHANNEL
  // ============================================================================
  
  ws.subscribe('agents', 'created', (data) => {
    useAgentsStore.getState().onItemCreated(data);
  });

  ws.subscribe('agents', 'updated', (data) => {
    useAgentsStore.getState().onItemUpdated(data);
  });

  ws.subscribe('agents', 'deleted', (data) => {
    useAgentsStore.getState().onItemDeleted(data.id);
  });

  ws.subscribe('agents', 'status_changed', (data) => {
    useAgentsStore.getState().onStatusChanged(data.id, data.status);
  });

  // ============================================================================
  // CHATROOMS CHANNEL
  // ============================================================================
  
  ws.subscribe('chatrooms', 'created', (data) => {
    useChatroomsStore.getState().onItemCreated(data);
  });

  ws.subscribe('chatrooms', 'updated', (data) => {
    useChatroomsStore.getState().onItemUpdated(data);
  });

  ws.subscribe('chatrooms', 'deleted', (data) => {
    useChatroomsStore.getState().onItemDeleted(data.id);
  });

  ws.subscribe('chatrooms', 'message', (data) => {
    // Handle new chat message
    console.log('[WebSocket] Chat message:', data);
  });

  ws.subscribe('chatrooms', 'user_joined', (data) => {
    console.log('[WebSocket] User joined:', data);
  });

  ws.subscribe('chatrooms', 'user_left', (data) => {
    console.log('[WebSocket] User left:', data);
  });

  // ============================================================================
  // AUTOMATION CHANNEL
  // ============================================================================
  
  ws.subscribe('automation', 'created', (data) => {
    useAutomationStore.getState().onItemCreated(data);
  });

  ws.subscribe('automation', 'updated', (data) => {
    useAutomationStore.getState().onItemUpdated(data);
  });

  ws.subscribe('automation', 'deleted', (data) => {
    useAutomationStore.getState().onItemDeleted(data.id);
  });

  ws.subscribe('automation', 'workflow_started', (data) => {
    useAutomationStore.getState().onStatusChanged(data.id, 'running');
  });

  ws.subscribe('automation', 'workflow_completed', (data) => {
    useAutomationStore.getState().onStatusChanged(data.id, 'completed');
  });

  ws.subscribe('automation', 'workflow_failed', (data) => {
    useAutomationStore.getState().onStatusChanged(data.id, 'error');
  });

  // ============================================================================
  // ANALYTICS CHANNEL
  // ============================================================================
  
  ws.subscribe('analytics', 'metrics_update', (data) => {
    // Update analytics store with new metrics
    const store = useAnalyticsStore.getState();
    store.onItemCreated(data);
  });

  ws.subscribe('analytics', 'real_time_data', (data) => {
    console.log('[WebSocket] Real-time analytics:', data);
  });

  // ============================================================================
  // MONETIZATION CHANNEL
  // ============================================================================
  
  ws.subscribe('monetization', 'transaction_created', (data) => {
    useMonetizationStore.getState().onItemCreated(data);
  });

  ws.subscribe('monetization', 'payment_received', (data) => {
    console.log('[WebSocket] Payment received:', data);
  });

  ws.subscribe('monetization', 'subscription_updated', (data) => {
    console.log('[WebSocket] Subscription updated:', data);
  });

  // ============================================================================
  // NOTIFICATIONS CHANNEL
  // ============================================================================
  
  ws.subscribe('notifications', 'new', (data) => {
    // Show toast notification
    console.log('[WebSocket] New notification:', data);
    
    // You can integrate with a toast library here
    if (typeof window !== 'undefined') {
      // Example: window.showToast?.(data.message, data.type);
    }
  });

  // ============================================================================
  // SYSTEM CHANNEL
  // ============================================================================
  
  ws.subscribe('system', 'pong', () => {
    // Heartbeat response
  });

  ws.subscribe('system', 'error', (data) => {
    console.error('[WebSocket] System error:', data);
  });

  ws.subscribe('system', 'maintenance', (data) => {
    console.warn('[WebSocket] Maintenance mode:', data);
  });

  // ============================================================================
  // CONNECTION HANDLERS
  // ============================================================================
  
  ws.onOpen(() => {
    console.log('[WebSocket] Connected - All channels ready');
  });

  ws.onClose(() => {
    console.log('[WebSocket] Disconnected - Will retry...');
  });

  ws.onError((error) => {
    console.error('[WebSocket] Connection error:', error);
  });

  console.log('[WebSocket] All channels setup complete');
}

/**
 * Channel names for easy reference
 */
export const CHANNELS = {
  CRAWLERS: 'crawlers',
  STUDIOS: 'studios',
  GENERATORS: 'generators',
  AGENTS: 'agents',
  CHATROOMS: 'chatrooms',
  AUTOMATION: 'automation',
  ANALYTICS: 'analytics',
  MONETIZATION: 'monetization',
  NOTIFICATIONS: 'notifications',
  SYSTEM: 'system',
} as const;

/**
 * Event names for easy reference
 */
export const EVENTS = {
  // Common events
  CREATED: 'created',
  UPDATED: 'updated',
  DELETED: 'deleted',
  STATUS_CHANGED: 'status_changed',
  
  // Crawler events
  CRAWLER_PROGRESS: 'progress',
  
  // Generator events
  GENERATION_STARTED: 'generation_started',
  GENERATION_PROGRESS: 'generation_progress',
  GENERATION_COMPLETED: 'generation_completed',
  GENERATION_FAILED: 'generation_failed',
  
  // Chatroom events
  MESSAGE: 'message',
  USER_JOINED: 'user_joined',
  USER_LEFT: 'user_left',
  
  // Automation events
  WORKFLOW_STARTED: 'workflow_started',
  WORKFLOW_COMPLETED: 'workflow_completed',
  WORKFLOW_FAILED: 'workflow_failed',
  
  // Analytics events
  METRICS_UPDATE: 'metrics_update',
  REAL_TIME_DATA: 'real_time_data',
  
  // Monetization events
  TRANSACTION_CREATED: 'transaction_created',
  PAYMENT_RECEIVED: 'payment_received',
  SUBSCRIPTION_UPDATED: 'subscription_updated',
  
  // Notification events
  NEW_NOTIFICATION: 'new',
  
  // System events
  PING: 'ping',
  PONG: 'pong',
  ERROR: 'error',
  MAINTENANCE: 'maintenance',
} as const;
