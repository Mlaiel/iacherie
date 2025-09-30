/**
 * 🔄 REACT CONTEXT TEMPLATE - ENTERPRISE STATE MANAGEMENT
 * ========================================================
 * 
 * Enterprise-grade React Context template with:
 * - TypeScript support and strict typing
 * - Performance optimizations
 * - Error handling and validation
 * - Developer tools integration
 * - Creator Economy specialized contexts
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { 
  createContext, 
  useContext, 
  useReducer, 
  useState, 
  useCallback, 
  useMemo, 
  ReactNode, 
  useEffect 
} from 'react';

// Base Context Template
export interface BaseContextState {
  loading: boolean;
  error: string | null;
  data: any;
}

export interface BaseContextActions {
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setData: (data: any) => void;
  reset: () => void;
}

export interface BaseContextValue extends BaseContextState, BaseContextActions {}

// Generic Context Creator
export function createContextProvider<T extends BaseContextState, A extends BaseContextActions>(
  name: string,
  initialState: T,
  reducer: (state: T, action: any) => T
) {
  const Context = createContext<(T & A) | undefined>(undefined);

  function Provider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);

    const actions = useMemo(() => ({
      setLoading: (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }),
      setError: (error: string | null) => dispatch({ type: 'SET_ERROR', payload: error }),
      setData: (data: any) => dispatch({ type: 'SET_DATA', payload: data }),
      reset: () => dispatch({ type: 'RESET' })
    }), []);

    const value = useMemo(() => ({
      ...state,
      ...actions
    }), [state, actions]);

    return React.createElement(Context.Provider, { value }, children);
  }

  function useContextHook() {
    const context = useContext(Context);
    if (context === undefined) {
      throw new Error(`${name} must be used within a ${name}Provider`);
    }
    return context;
  }

  return { Provider, useContext: useContextHook, Context };
}

// Theme Context
export interface ThemeState {
  theme: 'light' | 'dark' | 'auto';
  colors: Record<string, string>;
  typography: Record<string, any>;
  spacing: Record<string, string>;
  breakpoints: Record<string, string>;
}

export interface ThemeActions {
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  updateColors: (colors: Partial<Record<string, string>>) => void;
  resetTheme: () => void;
}

const initialThemeState: ThemeState = {
  theme: 'light',
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8',
    light: '#f8f9fa',
    dark: '#343a40'
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      md: '1rem',
      lg: '1.25rem',
      xl: '1.5rem'
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '3rem'
  },
  breakpoints: {
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px'
  }
};

function themeReducer(state: ThemeState, action: any): ThemeState {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'UPDATE_COLORS':
      return { ...state, colors: { ...state.colors, ...action.payload } };
    case 'RESET_THEME':
      return initialThemeState;
    default:
      return state;
  }
}

export const {
  Provider: ThemeProvider,
  useContext: useTheme,
  Context: ThemeContext
} = createContextProvider<ThemeState, ThemeActions>('Theme', initialThemeState, themeReducer);

// Creator Context for Creator Economy features
export interface CreatorState {
  creator: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    tier: 'basic' | 'pro' | 'enterprise';
    verified: boolean;
  } | null;
  content: {
    totalPosts: number;
    totalViews: number;
    totalRevenue: number;
    recentPosts: any[];
  };
  collaborations: {
    active: any[];
    pending: any[];
    requests: any[];
  };
  analytics: {
    views: number[];
    engagement: number[];
    revenue: number[];
  };
  settings: {
    privacy: 'public' | 'private' | 'unlisted';
    monetization: boolean;
    collaborationAllowed: boolean;
    notifications: boolean;
  };
}

export interface CreatorActions {
  setCreator: (creator: CreatorState['creator']) => void;
  updateContent: (content: Partial<CreatorState['content']>) => void;
  addCollaboration: (collaboration: any) => void;
  updateAnalytics: (analytics: Partial<CreatorState['analytics']>) => void;
  updateSettings: (settings: Partial<CreatorState['settings']>) => void;
  logout: () => void;
}

const initialCreatorState: CreatorState = {
  creator: null,
  content: {
    totalPosts: 0,
    totalViews: 0,
    totalRevenue: 0,
    recentPosts: []
  },
  collaborations: {
    active: [],
    pending: [],
    requests: []
  },
  analytics: {
    views: [],
    engagement: [],
    revenue: []
  },
  settings: {
    privacy: 'public',
    monetization: false,
    collaborationAllowed: true,
    notifications: true
  }
};

function creatorReducer(state: CreatorState, action: any): CreatorState {
  switch (action.type) {
    case 'SET_CREATOR':
      return { ...state, creator: action.payload };
    case 'UPDATE_CONTENT':
      return { ...state, content: { ...state.content, ...action.payload } };
    case 'ADD_COLLABORATION':
      return {
        ...state,
        collaborations: {
          ...state.collaborations,
          active: [...state.collaborations.active, action.payload]
        }
      };
    case 'UPDATE_ANALYTICS':
      return { ...state, analytics: { ...state.analytics, ...action.payload } };
    case 'UPDATE_SETTINGS':
      return { ...state, settings: { ...state.settings, ...action.payload } };
    case 'LOGOUT':
      return initialCreatorState;
    default:
      return state;
  }
}

export const {
  Provider: CreatorProvider,
  useContext: useCreator,
  Context: CreatorContext
} = createContextProvider<CreatorState, CreatorActions>('Creator', initialCreatorState, creatorReducer);

// App Context combining multiple contexts
export interface AppState {
  user: {
    id: string;
    name: string;
    email: string;
    role: 'creator' | 'viewer' | 'admin';
  } | null;
  ui: {
    sidebarOpen: boolean;
    loading: boolean;
    notifications: any[];
  };
  preferences: {
    language: string;
    timezone: string;
    currency: string;
  };
}

const initialAppState: AppState = {
  user: null,
  ui: {
    sidebarOpen: false,
    loading: false,
    notifications: []
  },
  preferences: {
    language: 'en',
    timezone: 'UTC',
    currency: 'USD'
  }
};

function appReducer(state: AppState, action: any): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'TOGGLE_SIDEBAR':
      return { ...state, ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen } };
    case 'SET_LOADING':
      return { ...state, ui: { ...state.ui, loading: action.payload } };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: [...state.ui.notifications, action.payload]
        }
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: state.ui.notifications.filter(n => n.id !== action.payload)
        }
      };
    case 'UPDATE_PREFERENCES':
      return { ...state, preferences: { ...state.preferences, ...action.payload } };
    default:
      return state;
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialAppState);

  const actions = useMemo(() => ({
    setUser: (user: AppState['user']) => dispatch({ type: 'SET_USER', payload: user }),
    toggleSidebar: () => dispatch({ type: 'TOGGLE_SIDEBAR' }),
    setLoading: (loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }),
    addNotification: (notification: any) => dispatch({ type: 'ADD_NOTIFICATION', payload: notification }),
    removeNotification: (id: string) => dispatch({ type: 'REMOVE_NOTIFICATION', payload: id }),
    updatePreferences: (preferences: Partial<AppState['preferences']>) => 
      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences })
  }), []);

  const value = useMemo(() => ({
    ...state,
    ...actions
  }), [state, actions]);

  // Auto-remove notifications after 5 seconds
  useEffect(() => {
    const notifications = state.ui.notifications;
    if (notifications.length > 0) {
      const latestNotification = notifications[notifications.length - 1];
      if (latestNotification.autoRemove !== false) {
        const timer = setTimeout(() => {
          dispatch({ type: 'REMOVE_NOTIFICATION', payload: latestNotification.id });
        }, 5000);
        return () => clearTimeout(timer);
      }
    }
  }, [state.ui.notifications]);

  return React.createElement(AppContext.Provider, { value }, children);
}

const AppContext = createContext<ReturnType<typeof useMemo> | undefined>(undefined);

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

// Combined Provider for all contexts
export function CombinedProvider({ children }: { children: ReactNode }) {
  return React.createElement(
    ThemeProvider,
    {},
    React.createElement(
      CreatorProvider,
      {},
      React.createElement(
        AppProvider,
        {},
        children
      )
    )
  );
}

// Context debugging utilities
export function useContextDebugger<T>(context: T, contextName: string) {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`🔍 ${contextName} Context Updated:`, context);
    }
  }, [context, contextName]);
}

// Performance monitoring for context updates
export function useContextPerformance(contextName: string) {
  const renderCountRef = React.useRef(0);
  const lastUpdateRef = React.useRef(Date.now());

  useEffect(() => {
    renderCountRef.current++;
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdateRef.current;
    lastUpdateRef.current = now;

    if (process.env.NODE_ENV === 'development') {
      console.log(`⚡ ${contextName} Context Performance:`, {
        renderCount: renderCountRef.current,
        timeSinceLastUpdate: `${timeSinceLastUpdate}ms`
      });
    }
  });
}

export default {
  ThemeProvider,
  useTheme,
  CreatorProvider,
  useCreator,
  AppProvider,
  useApp,
  CombinedProvider,
  createContextProvider,
  useContextDebugger,
  useContextPerformance
};