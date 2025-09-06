/**
 * Analytics - Real-time dashboard analytics component
 * 
 * Comprehensive analytics dashboard with real-time metrics,
 * interactive charts, and performance insights
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  CurrencyDollarIcon,
  UsersIcon,
  PlayIcon,
  ArrowDownTrayIcon,
  ClockIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  CalendarIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

export interface AnalyticsMetric {
  id: string;
  name: string;
  value: number;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  unit?: string;
  period: string;
}

export interface ChartData {
  label: string;
  value: number;
  timestamp: Date;
  platform?: string;
  type?: string;
}

export interface PlatformStats {
  platform: string;
  views: number;
  engagement: number;
  revenue: number;
  growth: number;
  color: string;
}

export interface GeographicData {
  country: string;
  views: number;
  percentage: number;
}

export interface AnalyticsProps {
  metrics?: AnalyticsMetric[];
  chartData?: ChartData[];
  platformStats?: PlatformStats[];
  geographicData?: GeographicData[];
  isRealTime?: boolean;
  onRefresh?: () => void;
  onExport?: (format: string) => void;
  className?: string;
}

const timeRanges = [
  { id: '1h', name: 'Last Hour', value: '1h' },
  { id: '24h', name: 'Last 24 Hours', value: '24h' },
  { id: '7d', name: 'Last 7 Days', value: '7d' },
  { id: '30d', name: 'Last 30 Days', value: '30d' },
  { id: '90d', name: 'Last 90 Days', value: '90d' }
];

const platforms = [
  { name: 'YouTube', color: 'bg-red-500', icon: PlayIcon },
  { name: 'Instagram', color: 'bg-pink-500', icon: HeartIcon },
  { name: 'TikTok', color: 'bg-black', icon: PlayIcon },
  { name: 'Spotify', color: 'bg-green-500', icon: PlayIcon },
  { name: 'Twitter', color: 'bg-blue-500', icon: ShareIcon }
];

const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

const formatPercentage = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
};

const getTrendIcon = (changeType: string) => {
  switch (changeType) {
    case 'increase': return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />;
    case 'decrease': return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />;
    default: return <InformationCircleIcon className="w-4 h-4 text-gray-500" />;
  }
};

const getMetricIcon = (metricName: string) => {
  const name = metricName.toLowerCase();
  if (name.includes('view')) return EyeIcon;
  if (name.includes('engagement') || name.includes('like')) return HeartIcon;
  if (name.includes('share')) return ShareIcon;
  if (name.includes('revenue') || name.includes('earn')) return CurrencyDollarIcon;
  if (name.includes('follower') || name.includes('subscriber')) return UsersIcon;
  if (name.includes('play') || name.includes('watch')) return PlayIcon;
  if (name.includes('download')) return ArrowDownTrayIcon;
  return ChartBarIcon;
};

// Mock real-time data generator
const generateRealTimeData = (): ChartData => ({
  label: new Date().toLocaleTimeString(),
  value: Math.floor(Math.random() * 1000) + 100,
  timestamp: new Date(),
  platform: platforms[Math.floor(Math.random() * platforms.length)].name
});

export const Analytics: React.FC<AnalyticsProps> = ({
  metrics = [],
  chartData = [],
  platformStats = [],
  geographicData = [],
  isRealTime = true,
  onRefresh,
  onExport,
  className = ''
}) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [selectedMetric, setSelectedMetric] = useState('views');
  const [realtimeData, setRealtimeData] = useState<ChartData[]>([]);
  const [isLiveUpdating, setIsLiveUpdating] = useState(isRealTime);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Real-time data simulation
  useEffect(() => {
    if (!isLiveUpdating) return;

    const interval = setInterval(() => {
      setRealtimeData(prev => {
        const newData = generateRealTimeData();
        const updated = [...prev, newData];
        // Keep only last 20 data points
        return updated.slice(-20);
      });
      setLastUpdate(new Date());
    }, 3000);

    return () => clearInterval(interval);
  }, [isLiveUpdating]);

  const defaultMetrics: AnalyticsMetric[] = [
    {
      id: 'total_views',
      name: 'Total Views',
      value: 2458631,
      change: 12.5,
      changeType: 'increase',
      period: '24h'
    },
    {
      id: 'engagement_rate',
      name: 'Engagement Rate',
      value: 4.7,
      change: -0.3,
      changeType: 'decrease',
      unit: '%',
      period: '24h'
    },
    {
      id: 'revenue',
      name: 'Revenue',
      value: 15420,
      change: 8.2,
      changeType: 'increase',
      unit: '$',
      period: '24h'
    },
    {
      id: 'new_followers',
      name: 'New Followers',
      value: 1247,
      change: 15.8,
      changeType: 'increase',
      period: '24h'
    }
  ];

  const defaultPlatformStats: PlatformStats[] = [
    { platform: 'YouTube', views: 1250000, engagement: 5.2, revenue: 8500, growth: 12.3, color: 'bg-red-500' },
    { platform: 'Instagram', views: 890000, engagement: 6.8, revenue: 4200, growth: 18.5, color: 'bg-pink-500' },
    { platform: 'TikTok', views: 2100000, engagement: 8.4, revenue: 1800, growth: 45.2, color: 'bg-black' },
    { platform: 'Spotify', views: 450000, engagement: 3.2, revenue: 900, growth: 8.7, color: 'bg-green-500' }
  ];

  const displayMetrics = metrics.length > 0 ? metrics : defaultMetrics;
  const displayPlatformStats = platformStats.length > 0 ? platformStats : defaultPlatformStats;

  const totalViews = displayPlatformStats.reduce((sum, stat) => sum + stat.views, 0);
  const totalRevenue = displayPlatformStats.reduce((sum, stat) => sum + stat.revenue, 0);

  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md border p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <ChartBarIcon className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>Real-time content performance insights</span>
                {isLiveUpdating && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-green-600">Live</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">
              Last update: {lastUpdate.toLocaleTimeString()}
            </div>
            <button
              onClick={() => setIsLiveUpdating(!isLiveUpdating)}
              className={`px-3 py-1 rounded-md text-sm font-medium ${
                isLiveUpdating 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {isLiveUpdating ? 'Live' : 'Paused'}
            </button>
            <button
              onClick={onRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <ArrowPathIcon className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => onExport?.('pdf')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
            >
              <ArrowDownTrayIcon className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="bg-white rounded-lg shadow-md border p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="w-5 h-5 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Time Range:</span>
          </div>
          <div className="flex space-x-1">
            {timeRanges.map((range) => (
              <button
                key={range.id}
                onClick={() => setSelectedTimeRange(range.value)}
                className={`px-3 py-1 text-sm rounded-md font-medium transition-colors ${
                  selectedTimeRange === range.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {range.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {displayMetrics.map((metric) => {
          const IconComponent = getMetricIcon(metric.name);
          return (
            <div key={metric.id} className="bg-white rounded-lg shadow-md border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <IconComponent className="w-6 h-6 text-gray-600" />
                </div>
                <div className="flex items-center space-x-1">
                  {getTrendIcon(metric.changeType)}
                  <span className={`text-sm font-medium ${
                    metric.changeType === 'increase' ? 'text-green-600' :
                    metric.changeType === 'decrease' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {formatPercentage(metric.change)}
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{metric.name}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metric.unit === '$' && formatCurrency(metric.value)}
                  {metric.unit === '%' && `${metric.value}%`}
                  {!metric.unit && formatNumber(metric.value)}
                </p>
                <p className="text-xs text-gray-500 mt-1">vs previous {metric.period}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-time Chart */}
      {isLiveUpdating && realtimeData.length > 0 && (
        <div className="bg-white rounded-lg shadow-md border p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Real-time Activity</h3>
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Live updates every 3 seconds</span>
            </div>
          </div>
          <div className="h-64 flex items-end space-x-1">
            {realtimeData.map((data, index) => (
              <div
                key={index}
                className="flex-1 bg-blue-500 rounded-t-sm relative group"
                style={{ height: `${(data.value / 1000) * 100}%` }}
              >
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  {data.value} views at {data.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Platform Performance */}
        <div className="bg-white rounded-lg shadow-md border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Performance</h3>
          <div className="space-y-4">
            {displayPlatformStats.map((stat) => (
              <div key={stat.platform} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 ${stat.color} rounded-full`} />
                  <div>
                    <p className="font-medium text-gray-900">{stat.platform}</p>
                    <p className="text-sm text-gray-500">{formatNumber(stat.views)} views</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">{stat.engagement}%</span>
                    <span className="text-xs text-gray-500">engagement</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-600">{formatPercentage(stat.growth)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device & Geography Stats */}
        <div className="bg-white rounded-lg shadow-md border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Audience Insights</h3>
          
          {/* Device Distribution */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Device Types</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <DevicePhoneMobileIcon className="w-4 h-4 text-blue-500" />
                  <span className="text-sm text-gray-900">Mobile</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '65%' }} />
                  </div>
                  <span className="text-sm text-gray-600">65%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ComputerDesktopIcon className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-gray-900">Desktop</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '35%' }} />
                  </div>
                  <span className="text-sm text-gray-600">35%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Top Countries */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Top Countries</h4>
            <div className="space-y-2">
              {[
                { country: 'United States', percentage: 35.2 },
                { country: 'United Kingdom', percentage: 18.7 },
                { country: 'Canada', percentage: 12.4 },
                { country: 'Australia', percentage: 8.9 },
                { country: 'Germany', percentage: 6.8 }
              ].map((item) => (
                <div key={item.country} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <GlobeAltIcon className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-900">{item.country}</span>
                  </div>
                  <span className="text-sm text-gray-600">{item.percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="bg-white rounded-lg shadow-md border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="p-4 bg-blue-100 rounded-lg mb-3">
              <EyeIcon className="w-8 h-8 text-blue-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(totalViews)}</p>
            <p className="text-sm text-gray-600">Total Views</p>
          </div>
          <div className="text-center">
            <div className="p-4 bg-green-100 rounded-lg mb-3">
              <CurrencyDollarIcon className="w-8 h-8 text-green-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalRevenue)}</p>
            <p className="text-sm text-gray-600">Total Revenue</p>
          </div>
          <div className="text-center">
            <div className="p-4 bg-purple-100 rounded-lg mb-3">
              <ArrowTrendingUpIcon className="w-8 h-8 text-purple-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {displayPlatformStats.reduce((avg, stat) => avg + stat.growth, 0) / displayPlatformStats.length || 0}%
            </p>
            <p className="text-sm text-gray-600">Average Growth</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;