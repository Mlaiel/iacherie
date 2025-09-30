/**
 * 🔔 Toast Notification System - Real-time Notifications
 * 
 * @fileoverview WebSocket-powered toast notifications with auto-dismiss
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Lead Dev IA + UX Expert + Security Specialist
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  XMarkIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../../core/api/hooks';

// === NOTIFICATION INTERFACES ===

export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number; // Auto-dismiss after milliseconds (0 = manual dismiss only)
  persistent?: boolean; // Don't auto-dismiss
  actionLabel?: string;
  actionUrl?: string;
  onAction?: () => void;
  timestamp: Date;
}

interface ToastContextType {
  notifications: ToastNotification[];
  showToast: (notification: Omit<ToastNotification, 'id' | 'timestamp'>) => string;
  dismissToast: (id: string) => void;
  dismissAll: () => void;
}

// === NOTIFICATION CONTEXT ===

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast(): ToastContextType {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// === TOAST PROVIDER ===

interface ToastProviderProps {
  children: ReactNode;
  maxToasts?: number;
  defaultDuration?: number;
}

export function ToastProvider({ 
  children, 
  maxToasts = 5, 
  defaultDuration = 5000 
}: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastNotification[]>([]);
  
  // ✅ WEBSOCKET INTEGRATION - Real-time notifications from backend
  const { notifications: wsNotifications, isConnected } = useNotifications();

  const showToast = useCallback((
    notification: Omit<ToastNotification, 'id' | 'timestamp'>
  ): string => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newToast: ToastNotification = {
      id,
      timestamp: new Date(),
      duration: defaultDuration,
      ...notification
    };

    setToasts(prev => {
      const updated = [newToast, ...prev];
      return updated.slice(0, maxToasts); // Limit number of toasts
    });

    console.log('🔔 ToastProvider: New toast notification', newToast);

    // Auto-dismiss logic
    if (!notification.persistent && (notification.duration ?? defaultDuration) > 0) {
      setTimeout(() => {
        dismissToast(id);
      }, notification.duration ?? defaultDuration);
    }

    return id;
  }, [defaultDuration, maxToasts]);

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
    console.log('🔔 ToastProvider: Dismissed toast', id);
  }, []);

  const dismissAll = useCallback(() => {
    setToasts([]);
    console.log('🔔 ToastProvider: Dismissed all toasts');
  }, []);

  // ✅ WEBSOCKET NOTIFICATIONS - Convert WebSocket notifications to toasts
  useEffect(() => {
    if (wsNotifications.length > 0) {
      const latestNotification = wsNotifications[0];
      
      // Convert WebSocket notification to toast
      if (!latestNotification.isRead) {
        showToast({
          type: latestNotification.type,
          title: latestNotification.title,
          message: latestNotification.message,
          actionLabel: latestNotification.actionUrl ? 'Voir' : undefined,
          actionUrl: latestNotification.actionUrl,
          persistent: latestNotification.persistent,
          duration: latestNotification.persistent ? 0 : defaultDuration
        });
      }
    }
  }, [wsNotifications, showToast, defaultDuration]);

  const contextValue: ToastContextType = {
    notifications: toasts,
    showToast,
    dismissToast,
    dismissAll
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

// === TOAST CONTAINER COMPONENT ===

function ToastContainer() {
  const { notifications, dismissToast } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((toast) => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onDismiss={() => dismissToast(toast.id)}
        />
      ))}
    </div>
  );
}

// === TOAST ITEM COMPONENT ===

interface ToastItemProps {
  toast: ToastNotification;
  onDismiss: () => void;
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const [isVisible, setIsVisible] = useState(false);

  // Entrance animation
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(onDismiss, 300); // Wait for exit animation
  };

  const handleAction = () => {
    if (toast.onAction) {
      toast.onAction();
    } else if (toast.actionUrl) {
      window.open(toast.actionUrl, '_blank');
    }
    handleDismiss();
  };

  // Icon and color mapping
  const getToastStyles = (type: ToastNotification['type']) => {
    switch (type) {
      case 'success':
        return {
          icon: CheckCircleIcon,
          iconColor: 'text-green-400',
          bgColor: 'bg-green-50 dark:bg-green-900/20',
          borderColor: 'border-green-200 dark:border-green-800'
        };
      case 'error':
        return {
          icon: XCircleIcon,
          iconColor: 'text-red-400',
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          borderColor: 'border-red-200 dark:border-red-800'
        };
      case 'warning':
        return {
          icon: ExclamationTriangleIcon,
          iconColor: 'text-yellow-400',
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          borderColor: 'border-yellow-200 dark:border-yellow-800'
        };
      case 'info':
      default:
        return {
          icon: InformationCircleIcon,
          iconColor: 'text-blue-400',
          bgColor: 'bg-blue-50 dark:bg-blue-900/20',
          borderColor: 'border-blue-200 dark:border-blue-800'
        };
    }
  };

  const styles = getToastStyles(toast.type);
  const Icon = styles.icon;

  return (
    <div 
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        ${styles.bgColor} ${styles.borderColor}
        border rounded-lg shadow-lg p-4 min-w-80 max-w-sm
      `}
    >
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className="flex-shrink-0">
          <Icon className={`h-5 w-5 ${styles.iconColor}`} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {toast.title}
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {toast.message}
          </p>
          
          {/* Action Button */}
          {(toast.actionLabel || toast.actionUrl) && (
            <div className="mt-3">
              <button
                onClick={handleAction}
                className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              >
                {toast.actionLabel || 'Voir'}
              </button>
            </div>
          )}
        </div>

        {/* Dismiss Button */}
        <div className="flex-shrink-0">
          <button
            onClick={handleDismiss}
            className="rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Timestamp */}
      <div className="mt-2 text-xs text-gray-400 dark:text-gray-500">
        {toast.timestamp.toLocaleTimeString()}
      </div>
    </div>
  );
}

// === UTILITY HOOKS ===

// Quick toast helpers
export function useToastHelpers() {
  const { showToast } = useToast();

  const showSuccess = useCallback((title: string, message: string) => {
    return showToast({ type: 'success', title, message });
  }, [showToast]);

  const showError = useCallback((title: string, message: string, persistent: boolean = false) => {
    return showToast({ type: 'error', title, message, persistent });
  }, [showToast]);

  const showWarning = useCallback((title: string, message: string) => {
    return showToast({ type: 'warning', title, message });
  }, [showToast]);

  const showInfo = useCallback((title: string, message: string) => {
    return showToast({ type: 'info', title, message });
  }, [showToast]);

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
}

export default ToastProvider;