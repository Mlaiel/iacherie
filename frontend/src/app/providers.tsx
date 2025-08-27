'use client';

import { createContext, useContext, ReactNode } from 'react';

interface AppContextType {
  // Add global state here
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function Providers({ children }: { children: ReactNode }) {
  const value: AppContextType = {
    // Initialize global state
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