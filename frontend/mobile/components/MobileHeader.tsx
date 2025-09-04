/**
 * Mobile Header Component
 * 
 * Fixed header for mobile interface with status indicators
 * Shows connection status and notifications
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React from 'react';
import { 
  BellIcon,
  Cog6ToothIcon,
  WifiIcon,
  NoSymbolIcon
} from '@heroicons/react/24/outline';

interface MobileHeaderProps {
  isOnline: boolean;
}

export function MobileHeader({ isOnline }: MobileHeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
      <div className="flex items-center justify-between px-4 h-14">
        {/* Logo/Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">A</span>
          </div>
          <span className="font-semibold text-gray-900">Ainflue</span>
        </div>

        {/* Status and Actions */}
        <div className="flex items-center space-x-3">
          {/* Connection Status */}
          <div className="flex items-center space-x-1">
            {isOnline ? (
              <>
                <WifiIcon className="h-4 w-4 text-green-500" />
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </>
            ) : (
              <>
                <NoSymbolIcon className="h-4 w-4 text-red-500" />
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              </>
            )}
          </div>

          {/* Notifications */}
          <button className="relative p-1 text-gray-600 hover:text-blue-600">
            <BellIcon className="h-6 w-6" />
            {/* Notification Badge */}
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-medium">3</span>
            </div>
          </button>

          {/* Settings */}
          <button className="p-1 text-gray-600 hover:text-blue-600">
            <Cog6ToothIcon className="h-6 w-6" />
          </button>
        </div>
      </div>
    </header>
  );
}