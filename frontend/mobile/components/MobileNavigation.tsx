/**
 * Mobile Navigation Component
 * 
 * Bottom navigation bar optimized for mobile touch interfaces
 * Provides quick access to main app features
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState } from 'react';
import { 
  HomeIcon,
  ChartBarIcon,
  PlayIcon,
  ShieldCheckIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  PlayIcon as PlayIconSolid,
  ShieldCheckIcon as ShieldCheckIconSolid,
  UserIcon as UserIconSolid
} from '@heroicons/react/24/solid';

export function MobileNavigation() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Accueil',
      icon: HomeIcon,
      iconActive: HomeIconSolid,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: ChartBarIcon,
      iconActive: ChartBarIconSolid,
    },
    {
      id: 'content',
      label: 'Contenu',
      icon: PlayIcon,
      iconActive: PlayIconSolid,
    },
    {
      id: 'protection',
      label: 'Protection',
      icon: ShieldCheckIcon,
      iconActive: ShieldCheckIconSolid,
    },
    {
      id: 'profile',
      label: 'Profil',
      icon: UserIcon,
      iconActive: UserIconSolid,
    }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
      <div className="flex justify-around items-center h-16 px-2">
        {navigationItems.map((item) => {
          const Icon = activeTab === item.id ? item.iconActive : item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center justify-center px-2 py-1 rounded-lg transition-colors ${
                isActive 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
              }`}
            >
              <Icon className="h-6 w-6 mb-1" />
              <span className="text-xs font-medium">{item.label}</span>
              
              {/* Active indicator */}
              {isActive && (
                <div className="absolute -top-1 w-8 h-1 bg-blue-600 rounded-full"></div>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}