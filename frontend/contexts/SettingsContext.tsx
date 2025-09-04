/**
 * Settings Context - Application settings context
 */

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';

interface AppSettings {
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    violations: boolean;
  };
  privacy: {
    analytics: boolean;
    publicProfile: boolean;
  };
  display: {
    density: 'compact' | 'comfortable' | 'spacious';
    animations: boolean;
  };
}

interface SettingsContextType {
  settings: AppSettings;
  updateSettings: (updates: Partial<AppSettings>) => void;
  resetSettings: () => void;
  isLoading: boolean;
}

const defaultSettings: AppSettings = {
  language: 'en',
  timezone: 'UTC',
  notifications: {
    email: true,
    push: false,
    violations: true,
  },
  privacy: {
    analytics: false,
    publicProfile: false,
  },
  display: {
    density: 'comfortable',
    animations: true,
  },
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load settings from localStorage or API
    const saved = localStorage.getItem('appSettings');
    if (saved) {
      try {
        setSettings({ ...defaultSettings, ...JSON.parse(saved) });
      } catch (error) {
        console.error('Failed to parse saved settings');
      }
    }
    setIsLoading(false);
  }, []);

  const updateSettings = (updates: Partial<AppSettings>) => {
    const newSettings = { ...settings, ...updates };
    setSettings(newSettings);
    localStorage.setItem('appSettings', JSON.stringify(newSettings));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    localStorage.removeItem('appSettings');
  };

  return (
    <SettingsContext.Provider value={{
      settings,
      updateSettings,
      resetSettings,
      isLoading,
    }}>
      {children}
    </SettingsContext.Provider>
  );
}

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
