/**
 * Performance Metrics - Content performance analytics
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ChartBarIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UsersIcon
} from '@heroicons/react/24/outline';

interface MetricData {
  label: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

interface ContentMetrics {
  id: string;
  title: string;
  type: 'video' | 'image' | 'audio' | 'text';
  views: number;
  likes: number;
  shares: number;
  engagementRate: number;
  revenue: number;
  publishDate: string;
}

const PerformanceMetrics: React.FC = () => {
  const [timeframe, setTimeframe] = React.useState<'7d' | '30d' | '90d' | '1y'>('30d');
  
  const overallMetrics: MetricData[] = [
    { label: 'Total Views', value: 1247832, change: 12.5, trend: 'up' },
    { label: 'Engagement Rate', value: 8.7, change: -2.3, trend: 'down' },
    { label: 'Average Watch Time', value: 4.2, change: 15.8, trend: 'up' },
    { label: 'Subscriber Growth', value: 2847, change: 23.4, trend: 'up' }
  ];

  const contentMetrics: ContentMetrics[] = [
    {
      id: '1',
      title: 'AI Tutorial: Getting Started',
      type: 'video',
      views: 85432,
      likes: 4521,
      shares: 892,
      engagementRate: 6.8,
      revenue: 2340,
      publishDate: '2025-01-05'
    },
    {
      id: '2',
      title: 'Photography Tips & Tricks',
      type: 'image',
      views: 34521,
      likes: 2105,
      shares: 234,
      engagementRate: 7.2,
      revenue: 890,
      publishDate: '2025-01-03'
    },
    {
      id: '3',
      title: 'Podcast Episode #12',
      type: 'audio',
      views: 12456,
      likes: 456,
      shares: 89,
      engagementRate: 4.9,
      revenue: 340,
      publishDate: '2025-01-01'
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4"></div>;
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getContentIcon = (type: ContentMetrics['type']) => {
    switch (type) {
      case 'video':
        return <div className="w-3 h-3 bg-red-500 rounded"></div>;
      case 'image':
        return <div className="w-3 h-3 bg-blue-500 rounded"></div>;
      case 'audio':
        return <div className="w-3 h-3 bg-green-500 rounded"></div>;
      case 'text':
        return <div className="w-3 h-3 bg-purple-500 rounded"></div>;
      default:
        return <div className="w-3 h-3 bg-gray-500 rounded"></div>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Performance Metrics</h2>
          <p className="text-gray-600">Track your content performance and engagement</p>
        </div>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
          className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {overallMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">{metric.label}</h3>
              {getTrendIcon(metric.trend)}
            </div>
            <div className="flex items-baseline space-x-2">
              <p className="text-2xl font-bold text-gray-900">
                {metric.label.includes('Rate') || metric.label.includes('Time') 
                  ? `${metric.value}${metric.label.includes('Rate') ? '%' : 'min'}`
                  : formatNumber(metric.value)
                }
              </p>
              <span className={`text-sm font-medium ${getChangeColor(metric.change)}`}>
                {metric.change > 0 ? '+' : ''}{metric.change}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Performance Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2" />
          Performance Trends
        </h3>
        <div className="h-64 flex items-end justify-between space-x-2">
          {[65, 78, 82, 71, 89, 95, 88, 92].map((value, index) => (
            <div key={index} className="flex flex-col items-center flex-1">
              <div
                className="bg-blue-500 rounded-t w-full"
                style={{ height: `${value}%` }}
              ></div>
              <span className="text-xs text-gray-600 mt-2">
                {timeframe === '7d' ? `Day ${index + 1}` : `Week ${index + 1}`}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Content Performance */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Top Performing Content</h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {contentMetrics.map(content => (
            <div key={content.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getContentIcon(content.type)}
                  <div>
                    <h4 className="font-medium text-gray-900">{content.title}</h4>
                    <p className="text-sm text-gray-500">
                      Published {formatDate(content.publishDate)} • {content.type}
                    </p>
                  </div>
                </div>
                <span className="text-sm font-medium text-green-600">
                  {formatCurrency(content.revenue)}
                </span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="flex items-center space-x-2">
                  <EyeIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {formatNumber(content.views)}
                    </p>
                    <p className="text-xs text-gray-500">Views</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <HeartIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {formatNumber(content.likes)}
                    </p>
                    <p className="text-xs text-gray-500">Likes</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <ShareIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {formatNumber(content.shares)}
                    </p>
                    <p className="text-xs text-gray-500">Shares</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <UsersIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {content.engagementRate}%
                    </p>
                    <p className="text-xs text-gray-500">Engagement</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {Math.floor(Math.random() * 10 + 3)}m
                    </p>
                    <p className="text-xs text-gray-500">Avg. Time</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Insights */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="font-medium text-blue-900 mb-3">Performance Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700">
          <div>
            <h5 className="font-medium mb-2">Top Performing:</h5>
            <ul className="space-y-1">
              <li>• Video content shows highest engagement</li>
              <li>• Tuesday uploads perform 23% better</li>
              <li>• Educational content drives more revenue</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-2">Recommendations:</h5>
            <ul className="space-y-1">
              <li>• Increase video content production</li>
              <li>• Focus on tutorial formats</li>
              <li>• Optimize upload timing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;