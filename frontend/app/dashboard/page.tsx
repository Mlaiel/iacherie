/**
 * 📊 Dashboard Page - Enterprise Creator Analytics Dashboard
 * 
 * @fileoverview Advanced dashboard for content creators with real-time analytics
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React from 'react';
import { 
  ChartBarIcon, 
  PlayIcon, 
  EyeIcon, 
  HeartIcon,
  ShareIcon,
  CurrencyDollarIcon 
} from '@heroicons/react/24/outline';

interface DashboardMetrics {
  totalViews: number;
  totalLikes: number;
  totalShares: number;
  revenue: number;
  activeContent: number;
  engagement: number;
}

export default function DashboardPage() {
  const metrics: DashboardMetrics = {
    totalViews: 2547692,
    totalLikes: 89524,
    totalShares: 12847,
    revenue: 15847.32,
    activeContent: 127,
    engagement: 94.7
  };

  const recentContent = [
    {
      id: '1',
      title: 'AI-Generated Music Track #47',
      type: 'audio',
      views: 12847,
      revenue: 847.32,
      status: 'monetized'
    },
    {
      id: '2', 
      title: 'Creative Photography Portfolio',
      type: 'image',
      views: 8924,
      revenue: 456.78,
      status: 'protected'
    },
    {
      id: '3',
      title: 'Video Blog: AI in Content Creation',
      type: 'video',
      views: 15673,
      revenue: 923.45,
      status: 'viral'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Creator Dashboard</h1>
          <p className="text-gray-600 mt-2">Monitor your content performance and revenue</p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Total Views"
            value={metrics.totalViews.toLocaleString()}
            icon={<EyeIcon className="h-6 w-6" />}
            trend="+12.5%"
            color="blue"
          />
          <MetricCard
            title="Engagement"
            value={`${metrics.engagement}%`}
            icon={<HeartIcon className="h-6 w-6" />}
            trend="+8.3%"
            color="red"
          />
          <MetricCard
            title="Revenue"
            value={`$${metrics.revenue.toLocaleString()}`}
            icon={<CurrencyDollarIcon className="h-6 w-6" />}
            trend="+23.1%"
            color="green"
          />
          <MetricCard
            title="Active Content"
            value={metrics.activeContent.toString()}
            icon={<PlayIcon className="h-6 w-6" />}
            trend="+5.7%"
            color="purple"
          />
          <MetricCard
            title="Total Shares"
            value={metrics.totalShares.toLocaleString()}
            icon={<ShareIcon className="h-6 w-6" />}
            trend="+15.2%"
            color="indigo"
          />
          <MetricCard
            title="Analytics Score"
            value="94.7"
            icon={<ChartBarIcon className="h-6 w-6" />}
            trend="+2.1%"
            color="cyan"
          />
        </div>

        {/* Recent Content */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Content Performance</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Content
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Views
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentContent.map((content) => (
                  <tr key={content.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {content.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {content.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {content.views.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      ${content.revenue}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        content.status === 'monetized' ? 'bg-green-100 text-green-800' :
                        content.status === 'protected' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {content.status}
                      </span>
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
}

interface MetricCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend: string;
  color: string;
}

function MetricCard({ title, value, icon, trend, color }: MetricCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    red: 'text-red-600 bg-red-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    indigo: 'text-indigo-600 bg-indigo-100',
    cyan: 'text-cyan-600 bg-cyan-100'
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-green-600 font-medium">{trend}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}