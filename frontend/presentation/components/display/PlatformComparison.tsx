/**
 * Platform Comparison - Cross-platform performance comparison
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  EyeIcon,
  UsersIcon
} from '@heroicons/react/24/outline';

interface PlatformData {
  name: string;
  icon: string;
  color: string;
  metrics: {
    views: number;
    followers: number;
    engagement: number;
    revenue: number;
    growth: number;
    avgWatchTime: number;
  };
  contentTypes: {
    video: number;
    image: number;
    audio: number;
    text: number;
  };
}

const PlatformComparison: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = React.useState<'views' | 'revenue' | 'engagement' | 'growth'>('views');
  const [timeframe, setTimeframe] = React.useState<'7d' | '30d' | '90d'>('30d');

  const platformData: PlatformData[] = [
    {
      name: 'YouTube',
      icon: '🎥',
      color: 'bg-red-500',
      metrics: {
        views: 847532,
        followers: 25840,
        engagement: 8.7,
        revenue: 4250,
        growth: 12.5,
        avgWatchTime: 6.2
      },
      contentTypes: { video: 85, image: 5, audio: 8, text: 2 }
    },
    {
      name: 'Instagram',
      icon: '📸',
      color: 'bg-pink-500',
      metrics: {
        views: 342156,
        followers: 18750,
        engagement: 12.3,
        revenue: 2890,
        growth: 18.7,
        avgWatchTime: 2.1
      },
      contentTypes: { video: 45, image: 50, audio: 2, text: 3 }
    },
    {
      name: 'TikTok',
      icon: '🎭',
      color: 'bg-black',
      metrics: {
        views: 1204567,
        followers: 34200,
        engagement: 15.8,
        revenue: 1950,
        growth: 28.3,
        avgWatchTime: 1.8
      },
      contentTypes: { video: 95, image: 3, audio: 1, text: 1 }
    },
    {
      name: 'LinkedIn',
      icon: '💼',
      color: 'bg-blue-600',
      metrics: {
        views: 89456,
        followers: 8940,
        engagement: 6.2,
        revenue: 3450,
        growth: 7.8,
        avgWatchTime: 4.5
      },
      contentTypes: { video: 25, image: 15, audio: 5, text: 55 }
    },
    {
      name: 'Twitter',
      icon: '🐦',
      color: 'bg-blue-400',
      metrics: {
        views: 156789,
        followers: 12450,
        engagement: 4.9,
        revenue: 890,
        growth: -2.3,
        avgWatchTime: 0.8
      },
      contentTypes: { video: 20, image: 30, audio: 5, text: 45 }
    }
  ];

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getMetricValue = (platform: PlatformData, metric: string) => {
    switch (metric) {
      case 'views': return platform.metrics.views;
      case 'revenue': return platform.metrics.revenue;
      case 'engagement': return platform.metrics.engagement;
      case 'growth': return platform.metrics.growth;
      default: return 0;
    }
  };

  const getMaxValue = (metric: string) => {
    return Math.max(...platformData.map(p => getMetricValue(p, metric)));
  };

  const getGrowthIcon = (growth: number) => {
    if (growth > 0) return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
    if (growth < 0) return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
    return <div className="h-4 w-4"></div>;
  };

  const getGrowthColor = (growth: number) => {
    if (growth > 0) return 'text-green-600';
    if (growth < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const totalMetrics = platformData.reduce((acc, platform) => ({
    views: acc.views + platform.metrics.views,
    revenue: acc.revenue + platform.metrics.revenue,
    followers: acc.followers + platform.metrics.followers,
    avgEngagement: acc.avgEngagement + platform.metrics.engagement
  }), { views: 0, revenue: 0, followers: 0, avgEngagement: 0 });

  totalMetrics.avgEngagement = totalMetrics.avgEngagement / platformData.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Platform Comparison</h2>
          <p className="text-gray-600">Compare performance across different platforms</p>
        </div>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
          className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <EyeIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(totalMetrics.views)}
              </p>
              <p className="text-sm text-gray-600">Total Views</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(totalMetrics.revenue)}
              </p>
              <p className="text-sm text-gray-600">Total Revenue</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <UsersIcon className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(totalMetrics.followers)}
              </p>
              <p className="text-sm text-gray-600">Total Followers</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-orange-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {totalMetrics.avgEngagement.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Avg Engagement</p>
            </div>
          </div>
        </div>
      </div>

      {/* Metric Selector */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compare by Metric</h3>
        <div className="flex space-x-4 mb-6">
          {[
            { key: 'views', label: 'Views', icon: EyeIcon },
            { key: 'revenue', label: 'Revenue', icon: CurrencyDollarIcon },
            { key: 'engagement', label: 'Engagement', icon: ChartBarIcon },
            { key: 'growth', label: 'Growth', icon: ArrowTrendingUpIcon }
          ].map(metric => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key as typeof selectedMetric)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                selectedMetric === metric.key
                  ? 'bg-blue-100 text-blue-800 border border-blue-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <metric.icon className="h-4 w-4" />
              <span>{metric.label}</span>
            </button>
          ))}
        </div>

        {/* Platform Comparison Chart */}
        <div className="space-y-4">
          {platformData.map(platform => {
            const value = getMetricValue(platform, selectedMetric);
            const maxValue = getMaxValue(selectedMetric);
            const percentage = (value / maxValue) * 100;
            
            return (
              <div key={platform.name} className="flex items-center space-x-4">
                <div className="flex items-center space-x-3 w-32">
                  <span className="text-2xl">{platform.icon}</span>
                  <span className="font-medium text-gray-900">{platform.name}</span>
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${platform.color}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-20">
                      {selectedMetric === 'revenue' 
                        ? formatCurrency(value)
                        : selectedMetric === 'engagement' || selectedMetric === 'growth'
                        ? `${value}%`
                        : formatNumber(value)
                      }
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detailed Platform Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {platformData.map(platform => (
          <div key={platform.name} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{platform.icon}</span>
                <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
              </div>
              <div className="flex items-center space-x-1">
                {getGrowthIcon(platform.metrics.growth)}
                <span className={`text-sm font-medium ${getGrowthColor(platform.metrics.growth)}`}>
                  {platform.metrics.growth > 0 ? '+' : ''}{platform.metrics.growth}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Views</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatNumber(platform.metrics.views)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Revenue</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(platform.metrics.revenue)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Followers</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatNumber(platform.metrics.followers)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Engagement</p>
                <p className="text-lg font-semibold text-gray-900">
                  {platform.metrics.engagement}%
                </p>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Content Distribution</p>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="text-center">
                  <div className="w-full bg-red-100 rounded h-2 mb-1">
                    <div 
                      className="bg-red-500 rounded h-2" 
                      style={{ width: `${platform.contentTypes.video}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-600">Video {platform.contentTypes.video}%</span>
                </div>
                <div className="text-center">
                  <div className="w-full bg-blue-100 rounded h-2 mb-1">
                    <div 
                      className="bg-blue-500 rounded h-2" 
                      style={{ width: `${platform.contentTypes.image}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-600">Image {platform.contentTypes.image}%</span>
                </div>
                <div className="text-center">
                  <div className="w-full bg-green-100 rounded h-2 mb-1">
                    <div 
                      className="bg-green-500 rounded h-2" 
                      style={{ width: `${platform.contentTypes.audio}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-600">Audio {platform.contentTypes.audio}%</span>
                </div>
                <div className="text-center">
                  <div className="w-full bg-purple-100 rounded h-2 mb-1">
                    <div 
                      className="bg-purple-500 rounded h-2" 
                      style={{ width: `${platform.contentTypes.text}%` }}
                    ></div>
                  </div>
                  <span className="text-gray-600">Text {platform.contentTypes.text}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Platform Insights */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h4 className="font-medium text-yellow-900 mb-3">Platform Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-yellow-700">
          <div>
            <h5 className="font-medium mb-2">Best Performing:</h5>
            <ul className="space-y-1">
              <li>• TikTok shows highest growth rate (+28.3%)</li>
              <li>• Instagram has best engagement (12.3%)</li>
              <li>• YouTube generates most revenue</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-2">Optimization Tips:</h5>
            <ul className="space-y-1">
              <li>• Focus video content on TikTok/YouTube</li>
              <li>• Use Instagram for visual content</li>
              <li>• LinkedIn ideal for professional content</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlatformComparison;