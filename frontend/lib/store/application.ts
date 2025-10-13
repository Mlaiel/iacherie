/**
 * Global Application Store - Production Grade
 * Using Zustand with TypeScript and Immer for immutable updates
 * @module lib/store/application
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

/**
 * Application theme
 */
export type Theme = 'light' | 'dark' | 'system';

/**
 * Notification types
 */
export enum NotificationLevel {
  INFO = 'INFO',
  SUCCESS = 'SUCCESS',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
}

/**
 * Notification entity
 */
export interface Notification {
  id: string;
  level: NotificationLevel;
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  actionLabel?: string;
  actionUrl?: string;
}

/**
 * Modal state
 */
interface ModalState {
  isOpen: boolean;
  component: React.ComponentType<any> | null;
  props: Record<string, any>;
}

/**
 * Application state
 */
interface ApplicationState {
  // Theme
  theme: Theme;
  setTheme: (theme: Theme) => void;
  
  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Notifications
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  
  // Modal
  modal: ModalState;
  openModal: (component: React.ComponentType<any>, props?: Record<string, any>) => void;
  closeModal: () => void;
  
  // Loading states
  loadingStates: Record<string, boolean>;
  setLoading: (key: string, loading: boolean) => void;
  isLoading: (key: string) => boolean;
  
  // Global search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  
  // Feature flags
  featureFlags: Record<string, boolean>;
  setFeatureFlag: (flag: string, enabled: boolean) => void;
  isFeatureEnabled: (flag: string) => boolean;
}

/**
 * Create application store
 */
export const useApplicationStore = create<ApplicationState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Theme
        theme: 'system',
        setTheme: (theme) => {
          set((state) => {
            state.theme = theme;
          });
        },
        
        // Sidebar
        sidebarCollapsed: false,
        toggleSidebar: () => {
          set((state) => {
            state.sidebarCollapsed = !state.sidebarCollapsed;
          });
        },
        setSidebarCollapsed: (collapsed) => {
          set((state) => {
            state.sidebarCollapsed = collapsed;
          });
        },
        
        // Notifications
        notifications: [],
        addNotification: (notification) => {
          set((state) => {
            state.notifications.unshift({
              ...notification,
              id: `notif-${Date.now()}-${Math.random()}`,
              timestamp: Date.now(),
              read: false,
            });
            
            // Keep only last 50 notifications
            if (state.notifications.length > 50) {
              state.notifications = state.notifications.slice(0, 50);
            }
          });
        },
        markNotificationRead: (id) => {
          set((state) => {
            const notification = state.notifications.find((n) => n.id === id);
            if (notification) {
              notification.read = true;
            }
          });
        },
        removeNotification: (id) => {
          set((state) => {
            state.notifications = state.notifications.filter((n) => n.id !== id);
          });
        },
        clearAllNotifications: () => {
          set((state) => {
            state.notifications = [];
          });
        },
        
        // Modal
        modal: {
          isOpen: false,
          component: null,
          props: {},
        },
        openModal: (component, props = {}) => {
          set((state) => {
            state.modal = {
              isOpen: true,
              component,
              props,
            };
          });
        },
        closeModal: () => {
          set((state) => {
            state.modal = {
              isOpen: false,
              component: null,
              props: {},
            };
          });
        },
        
        // Loading states
        loadingStates: {},
        setLoading: (key, loading) => {
          set((state) => {
            state.loadingStates[key] = loading;
          });
        },
        isLoading: (key) => {
          return get().loadingStates[key] ?? false;
        },
        
        // Global search
        searchQuery: '',
        setSearchQuery: (query) => {
          set((state) => {
            state.searchQuery = query;
          });
        },
        
        // Feature flags
        featureFlags: {
          'ai-agents': true,
          'blockchain': true,
          'real-time-collaboration': true,
          'video-generation': true,
          'audio-synthesis': true,
        },
        setFeatureFlag: (flag, enabled) => {
          set((state) => {
            state.featureFlags[flag] = enabled;
          });
        },
        isFeatureEnabled: (flag) => {
          return get().featureFlags[flag] ?? false;
        },
      })),
      {
        name: 'iacherie-application-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          featureFlags: state.featureFlags,
        }),
      }
    ),
    { name: 'ApplicationStore' }
  )
);
