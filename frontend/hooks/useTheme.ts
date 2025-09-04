import { useContext } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

export const useTheme = (): ThemeContextType => {
  // This would normally use a ThemeContext
  // For now, return a basic implementation
  return {
    theme: 'light',
    toggleTheme: () => {},
  };
};
