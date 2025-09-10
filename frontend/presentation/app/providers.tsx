'use client';

import React, { createContext, useContext, ReactNode, useReducer, useCallback } from 'react';
import { toast } from 'react-hot-toast';

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
  protection_level: 'standard' | 'professional' | 'enterprise';
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
        notifications: [notification, ...state.notifications.slice(0, 4)], // Keep only 5 notifications
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

export function Providers({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Mock API functions (in real app, these would call actual APIs)
  const login = useCallback(async (email: string, _password: string): Promise<boolean> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      const mockUser: User = {
        id: '1',
        email,
        name: email.split('@')[0],
        plan: 'pro',
        subscription_status: 'active',
      };
      
      dispatch({ type: 'SET_USER', payload: mockUser });
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'success', message: 'Login successful' } });
      
      return true;
    } catch (_error) {
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'error', message: 'Login failed' } });
      return false;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const logout = useCallback(() => {
    dispatch({ type: 'SET_USER', payload: null });
    dispatch({ type: 'RESET_STATE' });
    dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'info', message: 'Logged out successfully' } });
  }, []);

  const uploadContent = useCallback(async (files: File[]): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      for (const file of files) {
        const contentItem: ContentItem = {
          id: Math.random().toString(36).substr(2, 9),
          name: file.name,
          type: file.type.startsWith('audio/') ? 'audio' :
                file.type.startsWith('video/') ? 'video' :
                file.type.startsWith('image/') ? 'image' : 'text',
          status: 'uploading',
          protection_level: 'standard',
          created_at: new Date().toISOString(),
          size: file.size,
        };
        
        dispatch({ type: 'ADD_CONTENT', payload: contentItem });
        
        // Simulate upload and processing
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        dispatch({ 
          type: 'UPDATE_CONTENT', 
          payload: { 
            id: contentItem.id, 
            updates: { 
              status: 'processing',
              fingerprint_id: `fp_${Math.random().toString(36).substr(2, 9)}`
            } 
          } 
        });
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        dispatch({ 
          type: 'UPDATE_CONTENT', 
          payload: { 
            id: contentItem.id, 
            updates: { status: 'protected' } 
          } 
        });
      }
      
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'success', message: `${files.length} file(s) uploaded and protected` } });
      
      // Refresh metrics after upload
      await refreshMetrics();
      
    } catch (_error) {
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'error', message: 'Upload failed' } });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const deleteContent = useCallback(async (contentId: string): Promise<void> => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      dispatch({ type: 'REMOVE_CONTENT', payload: contentId });
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'success', message: 'Content deleted successfully' } });
      
      // Refresh metrics after deletion
      await refreshMetrics();
      
    } catch (_error) {
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'error', message: 'Failed to delete content' } });
    }
  }, []);

  const refreshMetrics = useCallback(async (): Promise<void> => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockMetrics: DashboardMetrics = {
        total_content: state.content.length,
        protected_files: state.content.filter(c => c.status === 'protected').length,
        monthly_revenue: Math.floor(Math.random() * 50000) + 10000,
        active_monitoring: Math.floor(state.content.length * 0.8),
        violations_detected: Math.floor(Math.random() * 20) + 5,
        violations_resolved: Math.floor(Math.random() * 15) + 3,
      };
      
      dispatch({ type: 'SET_METRICS', payload: mockMetrics });
      
    } catch (_error) {
      dispatch({ type: 'ADD_NOTIFICATION', payload: { type: 'error', message: 'Failed to refresh metrics' } });
    }
  }, [state.content]);

  const addNotification = useCallback((type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    dispatch({ type: 'ADD_NOTIFICATION', payload: { type, message } });
    
    // Also show toast notification
    switch (type) {
      case 'success':
        toast.success(message);
        break;
      case 'error':
        toast.error(message);
        break;
      case 'warning':
        toast(message, { icon: '⚠️' });
        break;
      default:
        toast(message);
    }
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
    throw new Error('useAppContext must be used within a Providers component');
  }
  return context;
}