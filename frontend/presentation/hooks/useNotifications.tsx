'use client';

import { useCallback } from 'react';

export function useNotifications() {
  // Mock implementation for now - replace with actual provider when ready
  const notifications: any[] = [];

  const notify = useCallback((type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    console.log(`[${type.toUpperCase()}] ${message}`);
  }, []);

  const dismiss = useCallback((id: string) => {
    console.log(`Dismiss notification: ${id}`);
  }, []);

  const success = useCallback((message: string) => {
    notify('success', message);
  }, [notify]);

  const error = useCallback((message: string) => {
    notify('error', message);
  }, [notify]);

  const warning = useCallback((message: string) => {
    notify('warning', message);
  }, [notify]);

  const info = useCallback((message: string) => {
    notify('info', message);
  }, [notify]);

  return {
    notifications,
    notify,
    dismiss,
    success,
    error,
    warning,
    info,
  };
}