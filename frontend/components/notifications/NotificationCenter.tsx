/**
 * 🔔 Notification Center - Persistent Notification Management
 * 
 * @fileoverview Comprehensive notification center with history and filtering
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Lead Dev IA + UX Expert + Backend Senior
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  BellIcon,
  XMarkIcon,
  CheckIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/solid';
import { useNotifications } from '../../core/api/hooks';

// === NOTIFICATION CENTER INTERFACES ===

interface NotificationFilter {
  type?: 'all' | 'info' | 'warning' | 'error' | 'success';
  status?: 'all' | 'read' | 'unread';
  searchTerm?: string;
}

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

// === NOTIFICATION CENTER COMPONENT ===

export function NotificationCenter({ isOpen, onClose, className = '' }: NotificationCenterProps) {
  const { 
    notifications, 
    unreadCount, 
    isConnected, 
    markAsRead, 
    markAllAsRead 
  } = useNotifications();

  const [filter, setFilter] = useState<NotificationFilter>({
    type: 'all',
    status: 'all',
    searchTerm: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  // Filter notifications based on current filter settings
  const filteredNotifications = useMemo(() => {
    return notifications.filter(notification => {
      // Type filter
      if (filter.type !== 'all' && notification.type !== filter.type) {
        return false;
      }

      // Status filter
      if (filter.status === 'read' && !notification.isRead) {
        return false;
      }
      if (filter.status === 'unread' && notification.isRead) {
        return false;
      }

      // Search filter
      if (filter.searchTerm) {
        const searchLower = filter.searchTerm.toLowerCase();
        return (
          notification.title.toLowerCase().includes(searchLower) ||
          notification.message.toLowerCase().includes(searchLower)
        );
      }

      return true;
    });
  }, [notifications, filter]);

  // Handle clicking outside to close
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info':
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins}min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    return date.toLocaleDateString('fr-FR');
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Notification Panel */}
      <div className={`
        fixed right-0 top-0 h-full w-96 bg-white dark:bg-gray-900 
        shadow-2xl z-50 transform transition-transform duration-300
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        ${className}
      `}>
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BellIcon className="h-6 w-6 text-gray-900 dark:text-gray-100" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Notifications
              </h2>
              {unreadCount > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[1.5rem] text-center">
                  {unreadCount}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {/* Connection Status */}
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} title={isConnected ? 'Connecté' : 'Déconnecté'} />
              
              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <FunnelIcon className="h-5 w-5 text-gray-500" />
              </button>
              
              {/* Close Button */}
              <button
                onClick={onClose}
                className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <XMarkIcon className="h-5 w-5 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Mark All Read Button */}
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Marquer tout comme lu
            </button>
          )}
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="border-b border-gray-200 dark:border-gray-700 p-4 space-y-3">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                value={filter.searchTerm || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, searchTerm: e.target.value }))}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                         bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                         focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Type Filter */}
            <select
              value={filter.type}
              onChange={(e) => setFilter(prev => ({ ...prev, type: e.target.value as any }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Tous les types</option>
              <option value="info">Information</option>
              <option value="success">Succès</option>
              <option value="warning">Avertissement</option>
              <option value="error">Erreur</option>
            </select>

            {/* Status Filter */}
            <select
              value={filter.status}
              onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value as any }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md 
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="unread">Non lues</option>
              <option value="read">Lues</option>
            </select>
          </div>
        )}

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-gray-500 dark:text-gray-400">
              <BellIcon className="h-8 w-8 mb-2" />
              <p className="text-sm">Aucune notification</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredNotifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={() => markAsRead(notification.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// === NOTIFICATION ITEM COMPONENT ===

interface NotificationItemProps {
  notification: any;
  onMarkAsRead: () => void;
}

function NotificationItem({ notification, onMarkAsRead }: NotificationItemProps) {
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info':
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins}min`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    return date.toLocaleDateString('fr-FR');
  };

  const handleClick = () => {
    if (!notification.isRead) {
      onMarkAsRead();
    }
    
    if (notification.actionUrl) {
      window.open(notification.actionUrl, '_blank');
    }
  };

  return (
    <div 
      className={`
        p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors
        ${!notification.isRead ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
      `}
      onClick={handleClick}
    >
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-1">
          {getNotificationIcon(notification.type)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className={`text-sm font-medium ${
                !notification.isRead 
                  ? 'text-gray-900 dark:text-gray-100' 
                  : 'text-gray-600 dark:text-gray-400'
              }`}>
                {notification.title}
              </p>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                {notification.message}
              </p>
            </div>

            {/* Unread indicator */}
            {!notification.isRead && (
              <div className="flex-shrink-0 ml-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-2 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
            <span>{formatTimestamp(notification.timestamp)}</span>
            {notification.actionUrl && (
              <span className="text-blue-500">→ Voir détails</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// === NOTIFICATION BELL ICON WITH BADGE ===

interface NotificationBellProps {
  onClick: () => void;
  className?: string;
}

export function NotificationBell({ onClick, className = '' }: NotificationBellProps) {
  const { unreadCount, isConnected } = useNotifications();

  return (
    <button
      onClick={onClick}
      className={`relative p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${className}`}
      title="Notifications"
    >
      <BellIcon className="h-6 w-6 text-gray-700 dark:text-gray-300" />
      
      {/* Unread Badge */}
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[1.25rem] text-center">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {/* Connection Status */}
      <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white dark:border-gray-900 ${
        isConnected ? 'bg-green-500' : 'bg-red-500'
      }`} />
    </button>
  );
}

export default NotificationCenter;