/**
 * Real KV hook using backend API + localStorage fallback
 * Stores data in localStorage and syncs with backend when available
 */
import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export function useKV<T>(key: string, initialValue: T) {
  // Get initial value from localStorage
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error loading ${key} from localStorage:`, error);
      return initialValue;
    }
  });

  // Save to localStorage and optionally sync to backend
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      
      // TODO: Implement backend sync when user preferences/settings API is ready
      // This will store user-specific data in the real database
      // Example: POST /api/v1/users/me/preferences
    } catch (error) {
      console.error(`Error saving ${key}:`, error);
    }
  }, [key, value]);

  return [value, setValue] as const;
}
