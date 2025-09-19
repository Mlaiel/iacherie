/**
 * 👥 Presence Indicators - Active User Display
 * 
 * @fileoverview Visual indicators for active collaborators
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role UX Expert + Collaboration Specialist
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React from 'react';
import { useCollaboration, CollaboratorPresence } from './CollaborationProvider';

// === PRESENCE INDICATOR INTERFACES ===

interface PresenceIndicatorProps {
  maxVisible?: number;
  showNames?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// === MAIN PRESENCE INDICATOR COMPONENT ===

export function PresenceIndicator({ 
  maxVisible = 5, 
  showNames = true, 
  size = 'md',
  className = '' 
}: PresenceIndicatorProps) {
  const { activeUsers, currentUser, isConnected } = useCollaboration();

  // Filter out current user from display
  const otherUsers = Object.values(activeUsers).filter(
    user => user.userId !== currentUser?.userId && user.status === 'online'
  );

  const visibleUsers = otherUsers.slice(0, maxVisible);
  const hiddenCount = Math.max(0, otherUsers.length - maxVisible);

  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm', 
    lg: 'w-10 h-10 text-base'
  };

  if (!isConnected) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        <span className="text-sm text-gray-500">Déconnecté</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Connection Status */}
      <div className="w-2 h-2 bg-green-500 rounded-full" title="Connecté" />

      {/* Active Users Avatars */}
      <div className="flex -space-x-2">
        {visibleUsers.map((user) => (
          <UserAvatar
            key={user.userId}
            user={user}
            size={size}
            sizeClasses={sizeClasses[size]}
            showTooltip={true}
          />
        ))}
        
        {/* Hidden Users Count */}
        {hiddenCount > 0 && (
          <div 
            className={`
              ${sizeClasses[size]} bg-gray-200 dark:bg-gray-700 
              border-2 border-white dark:border-gray-900 rounded-full 
              flex items-center justify-center font-medium text-gray-600 dark:text-gray-300
            `}
            title={`+${hiddenCount} autres utilisateurs`}
          >
            +{hiddenCount}
          </div>
        )}
      </div>

      {/* Names List (if enabled and few users) */}
      {showNames && otherUsers.length > 0 && otherUsers.length <= 3 && (
        <div className="flex flex-col text-xs text-gray-600 dark:text-gray-400">
          {otherUsers.map(user => (
            <div key={user.userId} className="flex items-center space-x-1">
              <span>{user.userName}</span>
              {user.isTyping && <span className="animate-pulse">✏️</span>}
            </div>
          ))}
        </div>
      )}

      {/* Summary text for many users */}
      {showNames && otherUsers.length > 3 && (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {otherUsers.length} utilisateurs actifs
        </span>
      )}
    </div>
  );
}

// === USER AVATAR COMPONENT ===

interface UserAvatarProps {
  user: CollaboratorPresence;
  size: 'sm' | 'md' | 'lg';
  sizeClasses: string;
  showTooltip?: boolean;
  onClick?: () => void;
}

function UserAvatar({ user, size, sizeClasses, showTooltip = false, onClick }: UserAvatarProps) {
  const statusColors = {
    online: 'bg-green-500',
    away: 'bg-yellow-500',
    busy: 'bg-red-500',
    offline: 'bg-gray-500'
  };

  const getUserColor = (userId: string): string => {
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500',
      'bg-yellow-500', 'bg-indigo-500', 'bg-red-500', 'bg-teal-500'
    ];
    const hash = userId.split('').reduce((acc, char) => char.charCodeAt(0) + acc, 0);
    return colors[hash % colors.length];
  };

  const tooltipContent = showTooltip ? (
    <div>
      <div className="font-medium">{user.userName}</div>
      <div className="text-xs text-gray-300">
        {user.status === 'online' ? 'En ligne' : 
         user.status === 'away' ? 'Absent' :
         user.status === 'busy' ? 'Occupé' : 'Hors ligne'}
      </div>
      {user.currentLocation && (
        <div className="text-xs text-gray-400">📍 {user.currentLocation}</div>
      )}
      {user.isTyping && (
        <div className="text-xs text-blue-300">✏️ En train d'écrire...</div>
      )}
    </div>
  ) : null;

  return (
    <div className="relative group">
      <div 
        className={`
          ${sizeClasses} ${getUserColor(user.userId)}
          border-2 border-white dark:border-gray-900 rounded-full
          flex items-center justify-center font-medium text-white
          cursor-pointer hover:scale-110 transition-transform
          ${onClick ? 'hover:ring-2 hover:ring-blue-300' : ''}
        `}
        onClick={onClick}
        title={showTooltip ? user.userName : undefined}
      >
        {user.userAvatar ? (
          <img 
            src={user.userAvatar} 
            alt={user.userName}
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          <span className="uppercase">
            {user.userName.charAt(0)}
          </span>
        )}
        
        {/* Status Indicator */}
        <div 
          className={`
            absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-900
            ${statusColors[user.status]}
          `}
        />
        
        {/* Typing Indicator */}
        {user.isTyping && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse border border-white" />
        )}
      </div>

      {/* Tooltip */}
      {showTooltip && tooltipContent && (
        <div className="
          absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2
          opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none
          bg-gray-900 text-white text-sm rounded-md px-3 py-2 whitespace-nowrap
          z-50 shadow-lg
        ">
          {tooltipContent}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </div>
  );
}

// === TYPING INDICATOR COMPONENT ===

export function TypingIndicator() {
  const { activeUsers, currentUser } = useCollaboration();

  const typingUsers = Object.values(activeUsers).filter(
    user => user.userId !== currentUser?.userId && user.isTyping
  );

  if (typingUsers.length === 0) return null;

  const renderTypingText = () => {
    if (typingUsers.length === 1) {
      return `${typingUsers[0].userName} est en train d'écrire...`;
    } else if (typingUsers.length === 2) {
      return `${typingUsers[0].userName} et ${typingUsers[1].userName} sont en train d'écrire...`;
    } else {
      return `${typingUsers.length} personnes sont en train d'écrire...`;
    }
  };

  return (
    <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <span>{renderTypingText()}</span>
    </div>
  );
}

// === COLLABORATION STATUS BAR ===

export function CollaborationStatusBar() {
  const { activeUsers, currentUser, isConnected, currentRoom } = useCollaboration();
  
  const userCount = Object.keys(activeUsers).length;
  const onlineCount = Object.values(activeUsers).filter(user => user.status === 'online').length;

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <PresenceIndicator maxVisible={8} showNames={false} size="sm" />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {onlineCount} en ligne{userCount > onlineCount && ` • ${userCount - onlineCount} hors ligne`}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {currentRoom && (
            <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
              Salle: {currentRoom}
            </span>
          )}
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
      </div>
      
      <TypingIndicator />
    </div>
  );
}

export default PresenceIndicator;