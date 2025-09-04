/**
 * Creator Dashboard - Main dashboard interface for content creators
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  CloudArrowUpIcon,
  CurrencyDollarIcon,
  UsersIcon,
  CogIcon 
} from '@heroicons/react/24/outline';

interface DashboardStats {
  totalContent: number;
  protectedFiles: number;
  monthlyRevenue: number;
  activeCollaborations: number;
  weeklyUploads: number;
}

const CreatorDashboard: React.FC = () => {
  const [stats, setStats] = React.useState<DashboardStats | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStats({
        totalContent: 1247,
        protectedFiles: 1198,
        monthlyRevenue: 24580,
        activeCollaborations: 12,
        weeklyUploads: 38
      });
      setLoading(false);
    }, 1000);
  }, []);

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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Creator Dashboard</h1>
        <p className="text-gray-600">Manage your content, protection, and monetization</p>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Content</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalContent.toLocaleString()}</p>
            </div>
            <CloudArrowUpIcon className="h-12 w-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Protected Files</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.protectedFiles.toLocaleString()}</p>
            </div>
            <ShieldCheckIcon className="h-12 w-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">${stats?.monthlyRevenue.toLocaleString()}</p>
            </div>
            <CurrencyDollarIcon className="h-12 w-12 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Dashboard Sections Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Analytics View */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <ChartBarIcon className="h-8 w-8 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Analytics View</h3>
          </div>
          <p className="text-gray-600 mb-4">View detailed analytics and performance metrics for your content.</p>
          <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
            View Analytics
          </button>
        </div>

        {/* Protection Center */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <ShieldCheckIcon className="h-8 w-8 text-green-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Protection Center</h3>
          </div>
          <p className="text-gray-600 mb-4">Monitor and manage content protection and copyright violations.</p>
          <button className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors">
            Open Protection
          </button>
        </div>

        {/* Collaboration Hub */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <UsersIcon className="h-8 w-8 text-purple-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Collaboration Hub</h3>
          </div>
          <p className="text-gray-600 mb-4">Manage collaborations and team access to your content.</p>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-500">Active Collaborations</span>
            <span className="font-semibold text-purple-600">{stats?.activeCollaborations}</span>
          </div>
          <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors">
            Manage Team
          </button>
        </div>

        {/* Monetization Panel */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <CurrencyDollarIcon className="h-8 w-8 text-yellow-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Monetization Panel</h3>
          </div>
          <p className="text-gray-600 mb-4">Configure monetization settings and track revenue streams.</p>
          <button className="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors">
            Manage Revenue
          </button>
        </div>

        {/* Upload Center */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <CloudArrowUpIcon className="h-8 w-8 text-indigo-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Upload Content</h3>
          </div>
          <p className="text-gray-600 mb-4">Upload and process new content with AI protection.</p>
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-500">Weekly Uploads</span>
            <span className="font-semibold text-indigo-600">{stats?.weeklyUploads}</span>
          </div>
          <button className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors">
            Upload Files
          </button>
        </div>

        {/* Settings Manager */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <CogIcon className="h-8 w-8 text-gray-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Settings Manager</h3>
          </div>
          <p className="text-gray-600 mb-4">Configure platform settings and preferences.</p>
          <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors">
            Open Settings
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <span className="text-sm text-gray-600">New content uploaded: &quot;Track_2024_Final.mp3&quot;</span>
            <span className="text-xs text-gray-400">2 hours ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <span className="text-sm text-gray-600">Copyright violation detected and resolved</span>
            <span className="text-xs text-gray-400">4 hours ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <span className="text-sm text-gray-600">Revenue payment processed: $1,250</span>
            <span className="text-xs text-gray-400">1 day ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatorDashboard;