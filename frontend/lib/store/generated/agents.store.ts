/**
 * AGENTS STORE
 * Agents management (3,054 agents: Business, Technical, Creative, Protection, Specialized)
 * 
 * Auto-generated Zustand store with:
 * - Full CRUD operations
 * - WebSocket integration
 * - TanStack Query compatibility
 * - Immer for immutability
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
// // import { apiAPI } // DISABLED // DISABLED from '@/lib/api/generated';

// ============================================================================
// TYPES
// ============================================================================

export interface Agent {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending' | 'error';
  created_at: string;
  updated_at: string;
  [key: string]: any;
}

export interface AgentsFilters {
  search?: string;
  status?: string;
  category?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface AgentsState {
  // Data
  items: Agent[];
  selectedItem: Agent | null;
  
  // UI State
  loading: boolean;
  error: string | null;
  
  // Filters & Pagination
  filters: AgentsFilters;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
  
  // Actions
  fetchItems: () => Promise<void>;
  fetchItem: (id: string) => Promise<void>;
  createItem: (data: Partial<Agent>) => Promise<Agent>;
  updateItem: (id: string, data: Partial<Agent>) => Promise<Agent>;
  deleteItem: (id: string) => Promise<void>;
  setFilters: (filters: Partial<AgentsFilters>) => void;
  clearFilters: () => void;
  selectItem: (item: Agent | null) => void;
  
  // WebSocket handlers
  onItemCreated: (item: Agent) => void;
  onItemUpdated: (item: Agent) => void;
  onItemDeleted: (id: string) => void;
  onStatusChanged: (id: string, status: string) => void;
  
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
  loading: false,
  error: null,
  filters: {
    limit: 50,
    offset: 0,
    sort_order: 'desc' as const,
  },
  total: 0,
  hasNext: false,
  hasPrev: false,
};

// ============================================================================
// STORE
// ============================================================================

export const useAgentsStore = create<AgentsState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,
      
      // ======================================================================
      // FETCH ITEMS
      // ======================================================================
      fetchItems: async () => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const response = await apiAPI.listAgents(get().filters);
          
          // Mock data for now
          const response = {
            items: [],
            total: 3054,
            hasNext: false,
            hasPrev: false,
          };
          
          set({
            items: response.items,
            total: response.total,
            hasNext: response.hasNext,
            hasPrev: response.hasPrev,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch items',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // FETCH SINGLE ITEM
      // ======================================================================
      fetchItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const item = await apiAPI.getAgents(id);
          
          // Mock for now
          const item = null;
          
          set({
            selectedItem: item,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch item',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // CREATE ITEM
      // ======================================================================
      createItem: async (data: Partial<Agent>) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const newItem = await apiAPI.createAgents(data);
          
          // Mock for now
          const newItem = {
            id: String(Date.now()),
            ...data,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          } as Agent;
          
          set((state) => {
            state.items.unshift(newItem);
            state.total += 1;
            state.loading = false;
          });
          
          return newItem;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create item',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // UPDATE ITEM
      // ======================================================================
      updateItem: async (id: string, data: Partial<Agent>) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const updatedItem = await apiAPI.updateAgents(id, data);
          
          // Mock for now
          const updatedItem = {
            ...get().items.find(i => i.id === id),
            ...data,
            updated_at: new Date().toISOString(),
          } as Agent;
          
          set((state) => {
            const index = state.items.findIndex(i => i.id === id);
            if (index !== -1) {
              state.items[index] = updatedItem;
            }
            if (state.selectedItem?.id === id) {
              state.selectedItem = updatedItem;
            }
            state.loading = false;
          });
          
          return updatedItem;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update item',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // DELETE ITEM
      // ======================================================================
      deleteItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // await apiAPI.deleteAgents(id);
          
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
            error: error instanceof Error ? error.message : 'Failed to delete item',
            loading: false,
          });
          throw error;
        }
      },
      
      // ======================================================================
      // FILTERS
      // ======================================================================
      setFilters: (filters: Partial<AgentsFilters>) => {
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
      selectItem: (item: Agent | null) => {
        set({ selectedItem: item });
      },
      
      // ======================================================================
      // WEBSOCKET HANDLERS
      // ======================================================================
      onItemCreated: (item: Agent) => {
        set((state) => {
          state.items.unshift(item);
          state.total += 1;
        });
      },
      
      onItemUpdated: (item: Agent) => {
        set((state) => {
          const index = state.items.findIndex(i => i.id === item.id);
          if (index !== -1) {
            state.items[index] = item;
          }
          if (state.selectedItem?.id === item.id) {
            state.selectedItem = item;
          }
        });
      },
      
      onItemDeleted: (id: string) => {
        set((state) => {
          state.items = state.items.filter(i => i.id !== id);
          state.total -= 1;
          if (state.selectedItem?.id === id) {
            state.selectedItem = null;
          }
        });
      },
      
      onStatusChanged: (id: string, status: string) => {
        set((state) => {
          const item = state.items.find(i => i.id === id);
          if (item) {
            item.status = status as any;
          }
          if (state.selectedItem?.id === id) {
            state.selectedItem.status = status as any;
          }
        });
      },
      
      // ======================================================================
      // UTILITIES
      // ======================================================================
      clearError: () => {
        set({ error: null });
      },
      
      reset: () => {
        set(initialState);
      },
    })),
    { name: 'AgentsStore' }
  )
);

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to use agents items
 */
export const useAgentsItems = () => {
  const items = useAgentsStore((state) => state.items);
  const loading = useAgentsStore((state) => state.loading);
  const error = useAgentsStore((state) => state.error);
  const fetchItems = useAgentsStore((state) => state.fetchItems);
  
  return { items, loading, error, fetchItems };
};

/**
 * Hook to use selected agents item
 */
export const useSelectedAgent = () => {
  const selectedItem = useAgentsStore((state) => state.selectedItem);
  const selectItem = useAgentsStore((state) => state.selectItem);
  
  return { selectedItem, selectItem };
};

/**
 * Hook to use agents filters
 */
export const useAgentsFilters = () => {
  const filters = useAgentsStore((state) => state.filters);
  const setFilters = useAgentsStore((state) => state.setFilters);
  const clearFilters = useAgentsStore((state) => state.clearFilters);
  
  return { filters, setFilters, clearFilters };
};
