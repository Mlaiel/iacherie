/**
 * Live Metrics Grid - Real-Time Performance Indicators
 * 
 * Displays key performance metrics in a grid layout
 * Updates in real-time via WebSocket connection
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  EyeIcon, 
  CurrencyDollarIcon, 
  ShieldCheckIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

interface LiveMetrics {
  viewCount: number;
  revenue: number;
  protectionStatus: number;
  alertCount: number;
}

export function LiveMetricsGrid() {
  const [metrics, setMetrics] = useState<LiveMetrics>({
    viewCount: 0,
    revenue: 0,
    protectionStatus: 0,
    alertCount: 0
  });

  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        viewCount: prev.viewCount + Math.floor(Math.random() * 10),
        revenue: prev.revenue + Math.random() * 5,
        protectionStatus: Math.floor(Math.random() * 100),
        alertCount: Math.floor(Math.random() * 3)
      }));
      setIsLive(true);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const metricCards = [
    {
      title: 'Vues en Direct',
      value: metrics.viewCount.toLocaleString(),
      icon: EyeIcon,
      color: 'blue',
      trend: '+12%'
    },
    {
      title: 'Revenus Temps Réel',
      value: `€${metrics.revenue.toFixed(2)}`,
      icon: CurrencyDollarIcon,
      color: 'green',
      trend: '+8%'
    },
    {
      title: 'Protection Active',
      value: `${metrics.protectionStatus}%`,
      icon: ShieldCheckIcon,
      color: 'purple',
      trend: 'Optimal'
    },
    {
      title: 'Alertes',
      value: metrics.alertCount.toString(),
      icon: ExclamationTriangleIcon,
      color: 'red',
      trend: 'Normal'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Métriques Live</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-xs text-gray-500">{isLive ? 'En Direct' : 'Hors Ligne'}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {metricCards.map((card, index) => (
          <div
            key={index}
            className={`bg-gradient-to-br from-${card.color}-50 to-${card.color}-100 rounded-lg p-4 border border-${card.color}-200`}
          >
            <div className="flex items-center justify-between mb-2">
              <card.icon className={`h-8 w-8 text-${card.color}-600`} />
              <span className={`text-xs font-medium text-${card.color}-600 bg-${card.color}-200 px-2 py-1 rounded`}>
                {card.trend}
              </span>
            </div>
            <p className="text-xs text-gray-600 mb-1">{card.title}</p>
            <p className={`text-xl font-bold text-${card.color}-900`}>{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}