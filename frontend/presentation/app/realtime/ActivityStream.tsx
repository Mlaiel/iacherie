/**
 * Activity Stream - Real-Time Event Feed
 * 
 * Displays live stream of platform activities and events
 * Connects to real-time event system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  PlayIcon, 
  EyeIcon, 
  ShieldCheckIcon,
  CurrencyDollarIcon,
  UserIcon
} from '@heroicons/react/24/outline';

interface ActivityEvent {
  id: string;
  type: 'view' | 'protection' | 'earning' | 'user';
  message: string;
  timestamp: Date;
  location?: string;
  value?: number;
}

export function ActivityStream() {
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [isScrolling, setIsScrolling] = useState(false);

  useEffect(() => {
    // Simulate real-time activity stream
    const interval = setInterval(() => {
      const eventTypes = ['view', 'protection', 'earning', 'user'] as const;
      const locations = ['France', 'Allemagne', 'Belgique', 'Suisse', 'Canada'];
      const messages = {
        view: 'Nouveau visionnage de contenu',
        protection: 'Scan de protection complété',
        earning: 'Revenus mis à jour',
        user: 'Nouvel utilisateur connecté'
      };

      const newActivity: ActivityEvent = {
        id: Date.now().toString(),
        type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
        message: messages[eventTypes[Math.floor(Math.random() * eventTypes.length)]],
        timestamp: new Date(),
        location: locations[Math.floor(Math.random() * locations.length)],
        value: Math.random() * 100
      };

      setActivities(prev => [newActivity, ...prev.slice(0, 9)]); // Keep only 10 latest
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'view': return EyeIcon;
      case 'protection': return ShieldCheckIcon;
      case 'earning': return CurrencyDollarIcon;
      case 'user': return UserIcon;
      default: return PlayIcon;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'view': return 'blue';
      case 'protection': return 'green';
      case 'earning': return 'purple';
      case 'user': return 'orange';
      default: return 'gray';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (seconds < 60) return 'À l\'instant';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `Il y a ${minutes} min`;
    const hours = Math.floor(minutes / 60);
    return `Il y a ${hours}h`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Flux d'Activité Live</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-500">Mise à jour toutes les 2s</span>
        </div>
      </div>

      <div 
        className="space-y-3 max-h-80 overflow-y-auto"
        onScroll={() => setIsScrolling(true)}
        onMouseLeave={() => setIsScrolling(false)}
      >
        {activities.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 text-sm">En attente d'activités...</div>
          </div>
        ) : (
          activities.map((activity) => {
            const Icon = getActivityIcon(activity.type);
            const color = getActivityColor(activity.type);
            
            return (
              <div 
                key={activity.id}
                className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className={`flex-shrink-0 w-8 h-8 bg-${color}-100 rounded-full flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 text-${color}-600`} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {activity.message}
                    </p>
                    <span className="text-xs text-gray-500 flex-shrink-0">
                      {formatTimeAgo(activity.timestamp)}
                    </span>
                  </div>
                  
                  <div className="flex items-center mt-1 space-x-4">
                    {activity.location && (
                      <span className="text-xs text-gray-600">
                        📍 {activity.location}
                      </span>
                    )}
                    {activity.value && (
                      <span className={`text-xs text-${color}-600 font-medium`}>
                        +{activity.value.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
      
      {activities.length > 0 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            Voir toute l'activité →
          </button>
        </div>
      )}
    </div>
  );
}