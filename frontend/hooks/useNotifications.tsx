'use client';

import { useAppContext } from '@/app/providers';
import { useCallback } from 'react';

export function useNotifications() {
  const { state, addNotification, removeNotification } = useAppContext();

  const notifications = state.notifications;

  const notify = useCallback((type: 'info' | 'success' | 'warning' | 'error', message: string) => {
    addNotification(type, message);
  }, [addNotification]);

  const dismiss = useCallback((id: string) => {
    removeNotification(id);
  }, [removeNotification]);

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