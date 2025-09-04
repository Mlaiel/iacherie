/**
 * Analytics Widget - Embeddable Analytics Component
 * 
 * Displays key analytics metrics in a compact embeddable format
 * Can be embedded on external websites
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  EyeIcon, 
  ChartBarIcon, 
  ArrowTrendingUpIcon 
} from '@heroicons/react/24/outline';

interface AnalyticsWidgetProps {
  apiKey: string;
  userId: string;
  showTitle?: boolean;
  data?: any;
}

interface AnalyticsData {
  totalViews: number;
  todayViews: number;
  growthRate: number;
  lastUpdated: string;
}

export function AnalyticsWidget({ apiKey, userId, showTitle = true, data }: AnalyticsWidgetProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    totalViews: 0,
    todayViews: 0,
    growthRate: 0,
    lastUpdated: new Date().toISOString()
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        if (data) {
          // Use provided data
          setAnalytics(data);
          setIsLoading(false);
          return;
        }

        if (!apiKey || !userId) {
          throw new Error('API Key et User ID requis');
        }

        // Simulate API call (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data for demonstration
        setAnalytics({
          totalViews: 45678,
          todayViews: 1234,
          growthRate: 12.5,
          lastUpdated: new Date().toISOString()
        });
        
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur de chargement');
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [apiKey, userId, data]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-gray-600">Chargement...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-500 text-sm">
          <ChartBarIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
          {error}
        </div>
      </div>
    );
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="p-4">
      {showTitle && (
        <div className="flex items-center space-x-2 mb-4">
          <ChartBarIcon className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Analytics Ainflue</h3>
        </div>
      )}

      <div className="space-y-4">
        {/* Total Views */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <EyeIcon className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">Vues totales</span>
          </div>
          <span className="font-semibold text-gray-900">
            {analytics.totalViews.toLocaleString()}
          </span>
        </div>

        {/* Today's Views */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-blue-100 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <span className="text-sm text-gray-600">Aujourd'hui</span>
          </div>
          <span className="font-semibold text-blue-600">
            +{analytics.todayViews.toLocaleString()}
          </span>
        </div>

        {/* Growth Rate */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">Croissance</span>
          </div>
          <span className="font-semibold text-green-600">
            +{analytics.growthRate}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Progrès journalier</span>
            <span>{Math.min(100, (analytics.todayViews / 2000) * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, (analytics.todayViews / 2000) * 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Last Updated */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-100">
          Mis à jour: {formatTime(analytics.lastUpdated)}
        </div>

        {/* Powered by Ainflue */}
        <div className="text-xs text-gray-400 text-center">
          <span>Powered by </span>
          <a 
            href="https://ainflue.com" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Ainflue
          </a>
        </div>
      </div>
    </div>
  );
}