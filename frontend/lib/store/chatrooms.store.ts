/**
 * 💬 CHATROOMS STORE - REAL-TIME CHAT WITH WEBSOCKET
 * ====================================================
 * Production-ready chatroom management with WebSocket integration
 * 
 * Features:
 * - Full CRUD operations with backend API
 * - Real-time messaging via WebSocket
 * - Typing indicators
 * - User presence tracking
 * - Message history
 * - Room participants
 * 
 * @author Fahed Mlaiel
 * @date 2025-10-06
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { backendAPI } from '../api/backend-client';

// ============================================================================
// TYPES
// ============================================================================

export interface Chatroom {
  id: string;
  name: string;
  type: 'text' | 'audio' | 'video' | 'collaboration';
  description?: string;
  status: 'active' | 'inactive';
  participants: string[];
  created_at: string;
  updated_at: string;
  stats: {
    messages: number;
    active_users: number;
    total_participants: number;
  };
}

export interface Message {
  id: string;
  room_id: string;
  user: string;
  user_id: string;
  content: string;
  timestamp: string;
  type: 'text' | 'image' | 'file';
}

export interface ChatroomsFilters {
  search?: string;
  type?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export interface ChatroomsState {
  // Data
  items: Chatroom[];
  selectedItem: Chatroom | null;
  messages: Map<string, Message[]>; // room_id -> messages
  participants: Map<string, any[]>; // room_id -> participants
  
  // UI State
  loading: boolean;
  error: string | null;
  
  // Filters & Pagination
  filters: ChatroomsFilters;
  total: number;
  
  // WebSocket State
  ws: WebSocket | null;
  connected: boolean;
  currentRoomId: string | null;
  
  // Actions - CRUD
  fetchItems: () => Promise<void>;
  fetchItem: (id: string) => Promise<void>;
  createItem: (data: Partial<Chatroom>) => Promise<Chatroom>;
  updateItem: (id: string, data: Partial<Chatroom>) => Promise<Chatroom>;
  deleteItem: (id: string) => Promise<void>;
  setFilters: (filters: Partial<ChatroomsFilters>) => void;
  clearFilters: () => void;
  selectItem: (item: Chatroom | null) => void;
  
  // Actions - WebSocket
  joinRoom: (roomId: string, userId: string, username: string) => void;
  leaveRoom: () => void;
  sendMessage: (content: string) => void;
  fetchMessages: (roomId: string) => Promise<void>;
  fetchParticipants: (roomId: string) => Promise<void>;
  sendTyping: () => void;
  
  // Utilities
  clearError: () => void;
  reset: () => void;
}

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialState = {
  items: [],
  selectedItem: null,
  messages: new Map(),
  participants: new Map(),
  loading: false,
  error: null,
  filters: {
    limit: 50,
    offset: 0,
  },
  total: 0,
  ws: null,
  connected: false,
  currentRoomId: null,
};

// ============================================================================
// STORE
// ============================================================================

export const useChatroomsStore = create<ChatroomsState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,
      
      // ======================================================================
      // FETCH ITEMS - REAL API CALL! 🚀
      // ======================================================================
      fetchItems: async () => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.listChatrooms(get().filters);
          
          set({
            items: response.items,
            total: response.total,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch chatrooms',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // FETCH SINGLE ITEM - REAL API CALL! 🚀
      // ======================================================================
      fetchItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.getChatroom(id);
          
          set({
            selectedItem: response.data,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch chatroom',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // CREATE ITEM - REAL API CALL! 🚀
      // ======================================================================
      createItem: async (data: Partial<Chatroom>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.createChatroom(data);
          const newItem = response.data;
          
          set((state) => {
            state.items.unshift(newItem);
            state.total += 1;
            state.loading = false;
          });
          
          return newItem;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create chatroom',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // UPDATE ITEM - REAL API CALL! 🚀
      // ======================================================================
      updateItem: async (id: string, data: Partial<Chatroom>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.updateChatroom(id, data);
          const updatedItem = response.data;
          
          set((state) => {
            const index = state.items.findIndex(i => i.id === id);
            if (index !== -1) {
              state.items[index] = { ...state.items[index], ...updatedItem };
            }
            if (state.selectedItem?.id === id) {
              state.selectedItem = { ...state.selectedItem, ...updatedItem };
            }
            state.loading = false;
          });
          
          return updatedItem;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update chatroom',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // DELETE ITEM - REAL API CALL! 🚀
      // ======================================================================
      deleteItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          await backendAPI.deleteChatroom(id);
          
          set((state) => {
            state.items = state.items.filter(i => i.id !== id);
            state.total -= 1;
            if (state.selectedItem?.id === id) {
              state.selectedItem = null;
            }
            state.loading = false;
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete chatroom',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // WEBSOCKET - JOIN ROOM 🔌
      // ======================================================================
      joinRoom: (roomId: string, userId: string, username: string) => {
        const { ws, currentRoomId } = get();
        
        // Leave current room if any
        if (ws && currentRoomId) {
          get().leaveRoom();
        }
        
        // Create WebSocket connection
        const wsUrl = `ws://localhost:8000/api/chatrooms/ws/${roomId}?user_id=${userId}&username=${encodeURIComponent(username)}`;
        const newWs = new WebSocket(wsUrl);
        
        newWs.onopen = () => {
          console.log(`✅ Connected to room ${roomId}`);
          set({ connected: true, currentRoomId: roomId });
        };
        
        newWs.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          // Handle different message types
          switch (data.type) {
            case 'message':
              set((state) => {
                const roomMessages = state.messages.get(roomId) || [];
                const newMessages = [...roomMessages, {
                  id: `msg-${Date.now()}`,
                  room_id: roomId,
                  user: data.user,
                  user_id: data.user_id,
                  content: data.content,
                  timestamp: data.timestamp,
                  type: data.message_type || 'text'
                }];
                state.messages.set(roomId, newMessages);
              });
              break;
              
            case 'user_joined':
              set((state) => {
                const roomParticipants = state.participants.get(roomId) || [];
                state.participants.set(roomId, [...roomParticipants, data.user]);
              });
              console.log(`👋 ${data.user.username} joined`);
              break;
              
            case 'user_left':
              set((state) => {
                const roomParticipants = state.participants.get(roomId) || [];
                state.participants.set(
                  roomId,
                  roomParticipants.filter(p => p.id !== data.user.id)
                );
              });
              console.log(`👋 ${data.user.username} left`);
              break;
              
            case 'user_typing':
              // Handle typing indicator
              console.log(`✍️ ${data.user.username} is typing...`);
              break;
              
            case 'message_sent':
              // Confirmation message
              console.log(`✅ Message sent: ${data.message_id}`);
              break;
          }
        };
        
        newWs.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          set({ error: 'WebSocket connection error', connected: false });
        };
        
        newWs.onclose = () => {
          console.log('🔌 WebSocket closed');
          set({ connected: false, ws: null, currentRoomId: null });
        };
        
        set({ ws: newWs });
      },
      
      // ======================================================================
      // WEBSOCKET - LEAVE ROOM 🚪
      // ======================================================================
      leaveRoom: () => {
        const { ws } = get();
        if (ws) {
          ws.close();
          set({ ws: null, connected: false, currentRoomId: null });
        }
      },
      
      // ======================================================================
      // WEBSOCKET - SEND MESSAGE 💬
      // ======================================================================
      sendMessage: (content: string) => {
        const { ws, connected } = get();
        
        if (!connected || !ws) {
          console.error('❌ Not connected to room');
          return;
        }
        
        ws.send(JSON.stringify({
          content,
          type: 'text'
        }));
      },
      
      // ======================================================================
      // FETCH MESSAGES - REAL API CALL! 🚀
      // ======================================================================
      fetchMessages: async (roomId: string) => {
        try {
          const response = await backendAPI.getChatroomMessages(roomId);
          
          set((state) => {
            state.messages.set(roomId, response.data.messages);
          });
        } catch (error) {
          console.error('❌ Failed to fetch messages:', error);
        }
      },
      
      // ======================================================================
      // FETCH PARTICIPANTS - REAL API CALL! 🚀
      // ======================================================================
      fetchParticipants: async (roomId: string) => {
        try {
          const response = await backendAPI.getChatroomParticipants(roomId);
          
          set((state) => {
            state.participants.set(roomId, response.data.participants);
          });
        } catch (error) {
          console.error('❌ Failed to fetch participants:', error);
        }
      },
      
      // ======================================================================
      // SEND TYPING INDICATOR ✍️
      // ======================================================================
      sendTyping: () => {
        const { currentRoomId } = get();
        if (!currentRoomId) return;
        
        // Send typing indicator via API (optional)
        backendAPI.sendTypingIndicator(currentRoomId).catch(console.error);
      },
      
      // ======================================================================
      // FILTERS
      // ======================================================================
      setFilters: (filters: Partial<ChatroomsFilters>) => {
        set((state) => {
          state.filters = { ...state.filters, ...filters };
        });
        get().fetchItems();
      },
      
      clearFilters: () => {
        set((state) => {
          state.filters = initialState.filters;
        });
        get().fetchItems();
      },
      
      // ======================================================================
      // SELECTION
      // ======================================================================
      selectItem: (item: Chatroom | null) => {
        set({ selectedItem: item });
      },
      
      // ======================================================================
      // UTILITIES
      // ======================================================================
      clearError: () => {
        set({ error: null });
      },
      
      reset: () => {
        get().leaveRoom();
        set(initialState);
      },
    })),
    { name: 'ChatroomsStore' }
  )
);

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to use chatrooms items
 */
export const useChatroomsItems = () => {
  const items = useChatroomsStore((state) => state.items);
  const loading = useChatroomsStore((state) => state.loading);
  const error = useChatroomsStore((state) => state.error);
  const fetchItems = useChatroomsStore((state) => state.fetchItems);
  
  return { items, loading, error, fetchItems };
};

/**
 * Hook to use selected chatroom
 */
export const useSelectedChatroom = () => {
  const selectedItem = useChatroomsStore((state) => state.selectedItem);
  const selectItem = useChatroomsStore((state) => state.selectItem);
  
  return { selectedItem, selectItem };
};

/**
 * Hook to use chatroom WebSocket
 */
export const useChatroomConnection = () => {
  const connected = useChatroomsStore((state) => state.connected);
  const currentRoomId = useChatroomsStore((state) => state.currentRoomId);
  const joinRoom = useChatroomsStore((state) => state.joinRoom);
  const leaveRoom = useChatroomsStore((state) => state.leaveRoom);
  const sendMessage = useChatroomsStore((state) => state.sendMessage);
  
  return { connected, currentRoomId, joinRoom, leaveRoom, sendMessage };
};

/**
 * Hook to use room messages
 */
export const useChatroomMessages = (roomId: string | null) => {
  const messages = useChatroomsStore((state) => 
    roomId ? state.messages.get(roomId) || [] : []
  );
  const fetchMessages = useChatroomsStore((state) => state.fetchMessages);
  
  return { messages, fetchMessages };
};

/**
 * Hook to use room participants
 */
export const useChatroomParticipants = (roomId: string | null) => {
  const participants = useChatroomsStore((state) => 
    roomId ? state.participants.get(roomId) || [] : []
  );
  const fetchParticipants = useChatroomsStore((state) => state.fetchParticipants);
  
  return { participants, fetchParticipants };
};
