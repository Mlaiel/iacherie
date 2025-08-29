/**
 * Analytics View - Comprehensive analytics dashboard
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarDaysIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface AnalyticsData {
  revenue: { month: string; amount: number }[];
  contentViews: { month: string; views: number }[];
  platformDistribution: { platform: string; percentage: number; color: string }[];
  topPerformingContent: { name: string; views: number; revenue: number }[];
}

const AnalyticsView: React.FC = () => {
  const [data, setData] = React.useState<AnalyticsData | null>(null);
  const [timeframe, setTimeframe] = React.useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setData({
        revenue: [
          { month: 'Jan', amount: 12000 },
          { month: 'Feb', amount: 15000 },
          { month: 'Mar', amount: 18000 },
          { month: 'Apr', amount: 22000 },
          { month: 'May', amount: 19000 },
          { month: 'Jun', amount: 24580 }
        ],
        contentViews: [
          { month: 'Jan', views: 125000 },
          { month: 'Feb', views: 145000 },
          { month: 'Mar', views: 162000 },
          { month: 'Apr', views: 198000 },
          { month: 'May', views: 178000 },
          { month: 'Jun', views: 215000 }
        ],
        platformDistribution: [
          { platform: 'YouTube', percentage: 45, color: 'bg-red-500' },
          { platform: 'Spotify', percentage: 25, color: 'bg-green-500' },
          { platform: 'SoundCloud', percentage: 15, color: 'bg-orange-500' },
          { platform: 'Apple Music', percentage: 10, color: 'bg-gray-700' },
          { platform: 'Others', percentage: 5, color: 'bg-blue-500' }
        ],
        topPerformingContent: [
          { name: 'Track_Final_Master.mp3', views: 125000, revenue: 3200 },
          { name: 'Album_Intro_Video.mp4', views: 98000, revenue: 2800 },
          { name: 'Behind_Scenes.mp4', views: 87000, revenue: 2100 },
          { name: 'Acoustic_Version.mp3', views: 76000, revenue: 1900 }
        ]
      });
      setLoading(false);
    }, 1000);
  }, [timeframe]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics View</h1>
            <p className="text-gray-600">Comprehensive insights into your content performance</p>
          </div>
          
          {/* Timeframe Selector */}
          <div className="flex space-x-2">
            {(['7d', '30d', '90d', '1y'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setTimeframe(period)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  timeframe === period
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period === '7d' ? '7 Days' : period === '30d' ? '30 Days' : period === '90d' ? '90 Days' : '1 Year'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">$24,580</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-600 ml-1">+12.5%</span>
              </div>
            </div>
            <ChartBarIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Views</p>
              <p className="text-2xl font-bold text-gray-900">215K</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-600 ml-1">+8.3%</span>
              </div>
            </div>
            <GlobeAltIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg. Revenue/View</p>
              <p className="text-2xl font-bold text-gray-900">$0.114</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-600 ml-1">+3.8%</span>
              </div>
            </div>
            <ChartBarIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Growth Rate</p>
              <p className="text-2xl font-bold text-gray-900">18.2%</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
                <span className="text-sm text-red-600 ml-1">-2.1%</span>
              </div>
            </div>
            <CalendarDaysIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
          <div className="h-64 flex items-end justify-between space-x-2">
            {data?.revenue.map((item, index) => (
              <div key={index} className="flex flex-col items-center flex-1">
                <div
                  className="bg-blue-500 rounded-t w-full"
                  style={{ height: `${(item.amount / 25000) * 100}%` }}
                ></div>
                <span className="text-xs text-gray-600 mt-2">{item.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Platform Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Distribution</h3>
          <div className="space-y-4">
            {data?.platformDistribution.map((platform, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded ${platform.color}`}></div>
                  <span className="text-sm font-medium text-gray-700">{platform.platform}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${platform.color}`}
                      style={{ width: `${platform.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-10 text-right">{platform.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performing Content */}
        <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Content</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Content</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Views</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Revenue</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Performance</th>
                </tr>
              </thead>
              <tbody>
                {data?.topPerformingContent.map((content, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="font-medium text-gray-900">{content.name}</div>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{content.views.toLocaleString()}</td>
                    <td className="py-3 px-4 text-gray-600">${content.revenue.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="h-2 rounded-full bg-green-500"
                            style={{ width: `${(content.views / 125000) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">
                          {Math.round((content.views / 125000) * 100)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsView;