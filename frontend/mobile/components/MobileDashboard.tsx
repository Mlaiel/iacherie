/**
 * Mobile Dashboard Component
 * 
 * Mobile-optimized dashboard with swipeable cards and touch interactions
 * Displays key metrics and quick actions for mobile users
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
  ArrowTrendingUpIcon,
  PlusIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

interface DashboardMetrics {
  views: number;
  revenue: number;
  protection: number;
  growth: number;
}

export function MobileDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    views: 0,
    revenue: 0,
    protection: 0,
    growth: 0
  });

  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    // Simulate loading metrics
    const timer = setTimeout(() => {
      setMetrics({
        views: 12450,
        revenue: 384.50,
        protection: 98,
        growth: 15.3
      });
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 1000));
    setMetrics(prev => ({
      views: prev.views + Math.floor(Math.random() * 100),
      revenue: prev.revenue + Math.random() * 10,
      protection: Math.max(95, Math.min(100, prev.protection + Math.random() * 2 - 1)),
      growth: prev.growth + Math.random() * 2 - 1
    }));
    setIsRefreshing(false);
  };

  const quickActions = [
    { icon: PlusIcon, label: 'Upload', color: 'blue' },
    { icon: PlayIcon, label: 'Stream', color: 'red' },
    { icon: ShieldCheckIcon, label: 'Protect', color: 'green' },
    { icon: ArrowTrendingUpIcon, label: 'Analyze', color: 'purple' }
  ];

  return (
    <div className="p-4 space-y-6">
      {/* Pull to Refresh */}
      <div 
        className="flex justify-center pt-2"
        onTouchStart={(e) => {
          // Simple pull-to-refresh implementation
          const startY = e.touches[0].clientY;
          const handleTouchMove = (e: TouchEvent) => {
            const currentY = e.touches[0].clientY;
            if (currentY - startY > 100 && !isRefreshing) {
              handleRefresh();
            }
          };
          document.addEventListener('touchmove', handleTouchMove);
          document.addEventListener('touchend', () => {
            document.removeEventListener('touchmove', handleTouchMove);
          }, { once: true });
        }}
      >
        {isRefreshing && (
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        )}
      </div>

      {/* Welcome Section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <h1 className="text-xl font-bold mb-2">Bonjour! 👋</h1>
        <p className="text-blue-100 text-sm">
          Voici votre performance d'aujourd'hui
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <EyeIcon className="h-8 w-8 text-blue-600" />
            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +12%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.views.toLocaleString()}</p>
          <p className="text-sm text-gray-600">Vues totales</p>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +8%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">€{metrics.revenue.toFixed(2)}</p>
          <p className="text-sm text-gray-600">Revenus</p>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <ShieldCheckIcon className="h-8 w-8 text-purple-600" />
            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
              Optimal
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.protection}%</p>
          <p className="text-sm text-gray-600">Protection</p>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <ArrowTrendingUpIcon className="h-8 w-8 text-orange-600" />
            <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
              +{metrics.growth.toFixed(1)}%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.growth.toFixed(1)}%</p>
          <p className="text-sm text-gray-600">Croissance</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-900 mb-4">Actions Rapides</h3>
        <div className="grid grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className={`flex flex-col items-center p-3 rounded-xl bg-${action.color}-50 hover:bg-${action.color}-100 transition-colors`}
            >
              <action.icon className={`h-6 w-6 text-${action.color}-600 mb-2`} />
              <span className="text-xs font-medium text-gray-700">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-900 mb-4">Activité Récente</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Nouveau contenu protégé</span>
            <span className="text-xs text-gray-400 ml-auto">Il y a 2h</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Revenus mis à jour</span>
            <span className="text-xs text-gray-400 ml-auto">Il y a 4h</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Analyse complétée</span>
            <span className="text-xs text-gray-400 ml-auto">Il y a 6h</span>
          </div>
        </div>
      </div>
    </div>
  );
}