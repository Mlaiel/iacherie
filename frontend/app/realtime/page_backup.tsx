/**
 * Real-Time Dashboard Page - Live Analytics and Monitoring
 * 
 * Provides comprehensive real-time analytics for content creators
 * Integrates with existing backend analytics infrastructure
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React from 'react';
import { RealTimeAnalytics } from '@/components/dashboard_analytics/RealTimeAnalytics';
import { LiveMetricsGrid } from './LiveMetricsGrid';
import { ActivityStream } from './ActivityStream';
import { PerformanceChart } from './PerformanceChart';

export default function RealTimePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Temps Réel</h1>
          <p className="mt-2 text-lg text-gray-600">
            Surveillez vos performances en temps réel avec des métriques live
          </p>
        </div>

        {/* Main Analytics Component */}
        <div className="mb-8">
          <RealTimeAnalytics />
        </div>

        {/* Additional Real-Time Modules */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <LiveMetricsGrid />
          <ActivityStream />
        </div>

        {/* Performance Chart */}
        <div className="mb-8">
          <PerformanceChart />
        </div>
      </div>
    </div>
  );
}