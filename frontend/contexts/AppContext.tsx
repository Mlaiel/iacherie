/**
 * App Context - Main application context
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { createContext, useContext, ReactNode, useReducer, useCallback } from 'react';

// Types for the global state
interface User {
  id: string;
  email: string;
  name: string;
  plan: 'free' | 'pro' | 'enterprise';
  subscription_status: 'active' | 'inactive' | 'expired';
}

interface ContentItem {
  id: string;
  name: string;
  type: 'audio' | 'video' | 'image' | 'text';
  status: 'uploading' | 'processing' | 'protected' | 'failed';
  fingerprint_id?: string;
  protection_level: 'basic' | 'advanced' | 'enterprise';
  created_at: string;
  size: number;
}

interface DashboardMetrics {
  total_content: number;
  protected_files: number;
  monthly_revenue: number;
  active_monitoring: number;
  violations_detected: number;
  violations_resolved: number;
}

interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  content: ContentItem[];
  metrics: DashboardMetrics;
  notifications: Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    message: string;
    timestamp: string;
  }>;
  theme: 'light' | 'dark';
}

type AppAction = 
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'ADD_CONTENT'; payload: ContentItem }
  | { type: 'UPDATE_CONTENT'; payload: { id: string; updates: Partial<ContentItem> } }
  | { type: 'REMOVE_CONTENT'; payload: string }
  | { type: 'SET_METRICS'; payload: DashboardMetrics }
  | { type: 'ADD_NOTIFICATION'; payload: { type: 'info' | 'success' | 'warning' | 'error'; message: string } }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'TOGGLE_THEME' }
  | { type: 'RESET_STATE' };

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  uploadContent: (files: File[]) => Promise<void>;
  deleteContent: (contentId: string) => Promise<void>;
  refreshMetrics: () => Promise<void>;
  addNotification: (type: 'info' | 'success' | 'warning' | 'error', message: string) => void;
  removeNotification: (id: string) => void;
  toggleTheme: () => void;
}

// Initial state
const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  content: [],
  metrics: {
    total_content: 0,
    protected_files: 0,
    monthly_revenue: 0,
    active_monitoring: 0,
    violations_detected: 0,
    violations_resolved: 0,
  },
  notifications: [],
  theme: 'light',
};

// Reducer function
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: action.payload !== null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    case 'ADD_CONTENT':
      return {
        ...state,
        content: [...state.content, action.payload],
      };
    
    case 'UPDATE_CONTENT':
      return {
        ...state,
        content: state.content.map(item =>
          item.id === action.payload.id
            ? { ...item, ...action.payload.updates }
            : item
        ),
      };
    
    case 'REMOVE_CONTENT':
      return {
        ...state,
        content: state.content.filter(item => item.id !== action.payload),
      };
    
    case 'SET_METRICS':
      return {
        ...state,
        metrics: action.payload,
      };
    
    case 'ADD_NOTIFICATION':
      const notification = {
        id: Math.random().toString(36).substr(2, 9),
        type: action.payload.type,
        message: action.payload.message,
        timestamp: new Date().toISOString(),
      };
      return {
        ...state,
        notifications: [notification, ...state.notifications.slice(0, 4)],
      };
    
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload),
      };
    
    case 'TOGGLE_THEME':
      return {
        ...state,
        theme: state.theme === 'light' ? 'dark' : 'light',
      };
    
    case 'RESET_STATE':
      return initialState;
    
    default:
      return state;
  }
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions implementation would go here
  const login = useCallback(async (email: string, _password: string): Promise<boolean> => {
    // Implementation from original providers.tsx
    return true;
  }, []);

  const logout = useCallback(() => {
    dispatch({ type: 'SET_USER', payload: null });
    dispatch({ type: 'RESET_STATE' });
  }, []);

  const uploadContent = useCallback(async (files: File[]): Promise<void> => {
    // Implementation
  }, []);

  const deleteContent = useCallback(async (contentId: string): Promise<void> => {
    // Implementation
  }, []);

  const refreshMetrics = useCallback(async (): Promise<void> => {
    // Implementation
  }, []);

  const addNotification = useCallback((type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    dispatch({ type: 'ADD_NOTIFICATION', payload: { type, message } });
  }, []);

  const removeNotification = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  }, []);

  const toggleTheme = useCallback(() => {
    dispatch({ type: 'TOGGLE_THEME' });
  }, []);

  const value: AppContextType = {
    state,
    dispatch,
    login,
    logout,
    uploadContent,
    deleteContent,
    refreshMetrics,
    addNotification,
    removeNotification,
    toggleTheme,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}

export type { User, ContentItem, DashboardMetrics, AppState, AppAction, AppContextType };