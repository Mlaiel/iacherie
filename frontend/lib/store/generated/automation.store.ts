/**
 * AUTOMATION STORE
 * Automation workflows (3,305 workflows with triggers, actions, scheduling)
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

export interface Workflow {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'pending' | 'error';
  created_at: string;
  updated_at: string;
  [key: string]: any;
}

export interface AutomationFilters {
  search?: string;
  status?: string;
  category?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface AutomationState {
  // Data
  items: Workflow[];
  selectedItem: Workflow | null;
  
  // UI State
  loading: boolean;
  error: string | null;
  
  // Filters & Pagination
  filters: AutomationFilters;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
  
  // Actions
  fetchItems: () => Promise<void>;
  fetchItem: (id: string) => Promise<void>;
  createItem: (data: Partial<Workflow>) => Promise<Workflow>;
  updateItem: (id: string, data: Partial<Workflow>) => Promise<Workflow>;
  deleteItem: (id: string) => Promise<void>;
  setFilters: (filters: Partial<AutomationFilters>) => void;
  clearFilters: () => void;
  selectItem: (item: Workflow | null) => void;
  
  // WebSocket handlers
  onItemCreated: (item: Workflow) => void;
  onItemUpdated: (item: Workflow) => void;
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

export const useAutomationStore = create<AutomationState>()(
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
          // const response = await apiAPI.listAutomation(get().filters);
          
          // Mock data for now
          const response = {
            items: [],
            total: 3305,
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
          // const item = await apiAPI.getAutomation(id);
          
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
      createItem: async (data: Partial<Workflow>) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const newItem = await apiAPI.createAutomation(data);
          
          // Mock for now
          const newItem = {
            id: String(Date.now()),
            ...data,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          } as Workflow;
          
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
      updateItem: async (id: string, data: Partial<Workflow>) => {
        set({ loading: true, error: null });
        
        try {
          // TODO: Replace with actual API call
          // const updatedItem = await apiAPI.updateAutomation(id, data);
          
          // Mock for now
          const updatedItem = {
            ...get().items.find(i => i.id === id),
            ...data,
            updated_at: new Date().toISOString(),
          } as Workflow;
          
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
          // await apiAPI.deleteAutomation(id);
          
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
      setFilters: (filters: Partial<AutomationFilters>) => {
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
      selectItem: (item: Workflow | null) => {
        set({ selectedItem: item });
      },
      
      // ======================================================================
      // WEBSOCKET HANDLERS
      // ======================================================================
      onItemCreated: (item: Workflow) => {
        set((state) => {
          state.items.unshift(item);
          state.total += 1;
        });
      },
      
      onItemUpdated: (item: Workflow) => {
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
    { name: 'AutomationStore' }
  )
);

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to use automation items
 */
export const useAutomationItems = () => {
  const items = useAutomationStore((state) => state.items);
  const loading = useAutomationStore((state) => state.loading);
  const error = useAutomationStore((state) => state.error);
  const fetchItems = useAutomationStore((state) => state.fetchItems);
  
  return { items, loading, error, fetchItems };
};

/**
 * Hook to use selected automation item
 */
export const useSelectedWorkflow = () => {
  const selectedItem = useAutomationStore((state) => state.selectedItem);
  const selectItem = useAutomationStore((state) => state.selectItem);
  
  return { selectedItem, selectItem };
};

/**
 * Hook to use automation filters
 */
export const useAutomationFilters = () => {
  const filters = useAutomationStore((state) => state.filters);
  const setFilters = useAutomationStore((state) => state.setFilters);
  const clearFilters = useAutomationStore((state) => state.clearFilters);
  
  return { filters, setFilters, clearFilters };
};
