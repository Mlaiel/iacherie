/**
 * 🕷️ CRAWLERS STORE - SOLID FOUNDATION
 * ======================================
 * Zustand store avec connexion RÉELLE au backend
 * 
 * @author Fahed Mlaiel
 * @date 2025-10-05
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { backendAPI, type Crawler, type ListFilters } from '../api/backend-client';

// ============================================================================
// TYPES
// ============================================================================

interface CrawlersState {
  // Data
  items: Crawler[];
  selectedItem: Crawler | null;
  
  // UI State
  loading: boolean;
  error: string | null;
  
  // Filters & Pagination
  filters: ListFilters;
  total: number;
  hasNext: boolean;
  hasPrev: boolean;
  
  // Actions
  fetchItems: () => Promise<void>;
  fetchItem: (id: string) => Promise<void>;
  createItem: (data: Partial<Crawler>) => Promise<Crawler | null>;
  updateItem: (id: string, data: Partial<Crawler>) => Promise<Crawler | null>;
  deleteItem: (id: string) => Promise<void>;
  setFilters: (filters: Partial<ListFilters>) => void;
  clearFilters: () => void;
  selectItem: (item: Crawler | null) => void;
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
  },
  total: 0,
  hasNext: false,
  hasPrev: false,
};

// ============================================================================
// STORE
// ============================================================================

export const useCrawlersStore = create<CrawlersState>()(
  devtools(
    immer((set, get) => ({
      ...initialState,
      
      // ======================================================================
      // FETCH ITEMS - VRAI APPEL API
      // ======================================================================
      fetchItems: async () => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.listCrawlers(get().filters);
          
          set({
            items: response.items,
            total: response.total,
            hasNext: response.hasNext,
            hasPrev: response.hasPrev,
            loading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch crawlers',
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
          const response = await backendAPI.getCrawler(id);
          
          if (response.data) {
            set({
              selectedItem: response.data,
              loading: false,
            });
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch crawler',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // CREATE ITEM
      // ======================================================================
      createItem: async (data: Partial<Crawler>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.createCrawler(data);
          
          if (response.data) {
            set((state) => {
              state.items.unshift(response.data!);
              state.total += 1;
              state.loading = false;
            });
            
            return response.data;
          }
          
          return null;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create crawler',
            loading: false,
          });
          return null;
        }
      },
      
      // ======================================================================
      // UPDATE ITEM
      // ======================================================================
      updateItem: async (id: string, data: Partial<Crawler>) => {
        set({ loading: true, error: null });
        
        try {
          const response = await backendAPI.updateCrawler(id, data);
          
          if (response.data) {
            set((state) => {
              const index = state.items.findIndex(i => i.id === id);
              if (index !== -1) {
                state.items[index] = response.data!;
              }
              if (state.selectedItem?.id === id) {
                state.selectedItem = response.data!;
              }
              state.loading = false;
            });
            
            return response.data;
          }
          
          return null;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update crawler',
            loading: false,
          });
          return null;
        }
      },
      
      // ======================================================================
      // DELETE ITEM
      // ======================================================================
      deleteItem: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          await backendAPI.deleteCrawler(id);
          
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
            error: error instanceof Error ? error.message : 'Failed to delete crawler',
            loading: false,
          });
        }
      },
      
      // ======================================================================
      // FILTERS
      // ======================================================================
      setFilters: (filters: Partial<ListFilters>) => {
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
      selectItem: (item: Crawler | null) => {
        set({ selectedItem: item });
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
    { name: 'CrawlersStore' }
  )
);

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to use crawlers items
 */
export const useCrawlersItems = () => {
  const items = useCrawlersStore((state) => state.items);
  const loading = useCrawlersStore((state) => state.loading);
  const error = useCrawlersStore((state) => state.error);
  const fetchItems = useCrawlersStore((state) => state.fetchItems);
  
  return { items, loading, error, fetchItems };
};

/**
 * Hook to use selected crawler
 */
export const useSelectedCrawler = () => {
  const selectedItem = useCrawlersStore((state) => state.selectedItem);
  const selectItem = useCrawlersStore((state) => state.selectItem);
  
  return { selectedItem, selectItem };
};

/**
 * Hook to use crawlers filters
 */
export const useCrawlersFilters = () => {
  const filters = useCrawlersStore((state) => state.filters);
  const setFilters = useCrawlersStore((state) => state.setFilters);
  const clearFilters = useCrawlersStore((state) => state.clearFilters);
  
  return { filters, setFilters, clearFilters };
};
