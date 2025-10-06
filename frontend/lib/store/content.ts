/**
 * Content Management Store - Production Grade
 * Manages content creation, processing, and lifecycle
 * @module lib/store/content
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

/**
 * Content types
 */
export enum ContentType {
  TEXT = 'TEXT',
  IMAGE = 'IMAGE',
  AUDIO = 'AUDIO',
  VIDEO = 'VIDEO',
  DOCUMENT = 'DOCUMENT',
}

/**
 * Content processing status
 */
export enum ProcessingStatus {
  QUEUED = 'QUEUED',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

/**
 * Content entity
 */
export interface Content {
  id: string;
  type: ContentType;
  title: string;
  description?: string;
  status: ProcessingStatus;
  progress: number;
  url?: string;
  thumbnailUrl?: string;
  metadata: {
    size?: number;
    duration?: number;
    dimensions?: { width: number; height: number };
    format?: string;
    aiGenerated?: boolean;
    model?: string;
    prompt?: string;
  };
  tags: string[];
  createdAt: number;
  updatedAt: number;
  createdBy: string;
}

/**
 * Content filter options
 */
export interface ContentFilters {
  type?: ContentType;
  status?: ProcessingStatus;
  tags?: string[];
  dateFrom?: number;
  dateTo?: number;
  searchQuery?: string;
}

/**
 * Content state
 */
interface ContentState {
  // Content items
  items: Content[];
  selectedIds: Set<string>;
  filters: ContentFilters;
  
  // Actions
  addContent: (content: Content) => void;
  updateContent: (id: string, updates: Partial<Content>) => void;
  removeContent: (id: string) => void;
  bulkRemoveContent: (ids: string[]) => void;
  
  // Selection
  selectContent: (id: string) => void;
  deselectContent: (id: string) => void;
  toggleContentSelection: (id: string) => void;
  selectAll: () => void;
  deselectAll: () => void;
  
  // Filters
  setFilters: (filters: ContentFilters) => void;
  clearFilters: () => void;
  
  // Queries
  getContentById: (id: string) => Content | undefined;
  getFilteredContent: () => Content[];
  getSelectedContent: () => Content[];
  getContentByType: (type: ContentType) => Content[];
  getContentByStatus: (status: ProcessingStatus) => Content[];
}

/**
 * Create content store
 */
export const useContentStore = create<ContentState>()(
  devtools(
    immer((set, get) => ({
      // Initial state
      items: [],
      selectedIds: new Set(),
      filters: {},
      
      // Add content
      addContent: (content) => {
        set((state) => {
          state.items.unshift(content);
        });
      },
      
      // Update content
      updateContent: (id, updates) => {
        set((state) => {
          const content = state.items.find((item) => item.id === id);
          if (content) {
            Object.assign(content, updates);
            content.updatedAt = Date.now();
          }
        });
      },
      
      // Remove content
      removeContent: (id) => {
        set((state) => {
          state.items = state.items.filter((item) => item.id !== id);
          state.selectedIds.delete(id);
        });
      },
      
      // Bulk remove
      bulkRemoveContent: (ids) => {
        set((state) => {
          state.items = state.items.filter((item) => !ids.includes(item.id));
          ids.forEach((id) => state.selectedIds.delete(id));
        });
      },
      
      // Select content
      selectContent: (id) => {
        set((state) => {
          state.selectedIds.add(id);
        });
      },
      
      // Deselect content
      deselectContent: (id) => {
        set((state) => {
          state.selectedIds.delete(id);
        });
      },
      
      // Toggle selection
      toggleContentSelection: (id) => {
        set((state) => {
          if (state.selectedIds.has(id)) {
            state.selectedIds.delete(id);
          } else {
            state.selectedIds.add(id);
          }
        });
      },
      
      // Select all
      selectAll: () => {
        set((state) => {
          const filtered = get().getFilteredContent();
          filtered.forEach((item) => state.selectedIds.add(item.id));
        });
      },
      
      // Deselect all
      deselectAll: () => {
        set((state) => {
          state.selectedIds.clear();
        });
      },
      
      // Set filters
      setFilters: (filters) => {
        set((state) => {
          state.filters = filters;
        });
      },
      
      // Clear filters
      clearFilters: () => {
        set((state) => {
          state.filters = {};
        });
      },
      
      // Get content by ID
      getContentById: (id) => {
        return get().items.find((item) => item.id === id);
      },
      
      // Get filtered content
      getFilteredContent: () => {
        const { items, filters } = get();
        
        return items.filter((item) => {
          if (filters.type && item.type !== filters.type) return false;
          if (filters.status && item.status !== filters.status) return false;
          if (filters.tags && !filters.tags.some((tag) => item.tags.includes(tag))) return false;
          if (filters.dateFrom && item.createdAt < filters.dateFrom) return false;
          if (filters.dateTo && item.createdAt > filters.dateTo) return false;
          if (filters.searchQuery) {
            const query = filters.searchQuery.toLowerCase();
            if (
              !item.title.toLowerCase().includes(query) &&
              !item.description?.toLowerCase().includes(query) &&
              !item.tags.some((tag) => tag.toLowerCase().includes(query))
            ) {
              return false;
            }
          }
          return true;
        });
      },
      
      // Get selected content
      getSelectedContent: () => {
        const { items, selectedIds } = get();
        return items.filter((item) => selectedIds.has(item.id));
      },
      
      // Get content by type
      getContentByType: (type) => {
        return get().items.filter((item) => item.type === type);
      },
      
      // Get content by status
      getContentByStatus: (status) => {
        return get().items.filter((item) => item.status === status);
      },
    })),
    { name: 'ContentStore' }
  )
);
