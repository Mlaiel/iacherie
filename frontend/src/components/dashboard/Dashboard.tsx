'use client';

import { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  CurrencyDollarIcon,
  EyeIcon,
  UsersIcon,
  DocumentDuplicateIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import { MetricCard } from './MetricCard';
import { ProtectionStatus } from './ProtectionStatus';
import { RecentActivity } from './RecentActivity';
import { RevenueChart } from './RevenueChart';

interface DashboardStats {
  totalContent: number;
  protectedFiles: number;
  monthlyRevenue: number;
  activeMonitoring: number;
  totalViolations: number;
  resolvedViolations: number;
  revenueGrowth: number;
  contentGrowth: number;
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalContent: 0,
    protectedFiles: 0,
    monthlyRevenue: 0,
    activeMonitoring: 0,
    totalViolations: 0,
    resolvedViolations: 0,
    revenueGrowth: 0,
    contentGrowth: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const fetchStats = async () => {
      try {
        // In real implementation, this would call the backend API
        // const response = await fetch('/api/dashboard/stats');
        // const data = await response.json();
        
        // Mock data for demonstration
        const mockData: DashboardStats = {
          totalContent: 1247,
          protectedFiles: 1198,
          monthlyRevenue: 24580,
          activeMonitoring: 892,
          totalViolations: 43,
          resolvedViolations: 38,
          revenueGrowth: 12.5,
          contentGrowth: 8.3,
        };
        
        setStats(mockData);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Ainflue Dashboard</h1>
              <p className="text-gray-600">AI-Powered Content Protection & Monetization</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="btn-primary">
                Upload Content
              </button>
              <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">FM</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-6 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Content"
            value={stats.totalContent.toLocaleString()}
            icon={DocumentDuplicateIcon}
            trend={stats.contentGrowth}
            trendDirection="up"
            color="blue"
          />
          <MetricCard
            title="Protected Files"
            value={stats.protectedFiles.toLocaleString()}
            icon={ShieldCheckIcon}
            trend={((stats.protectedFiles / stats.totalContent) * 100).toFixed(1)}
            trendDirection="up"
            color="green"
            suffix="%"
          />
          <MetricCard
            title="Monthly Revenue"
            value={`$${stats.monthlyRevenue.toLocaleString()}`}
            icon={CurrencyDollarIcon}
            trend={stats.revenueGrowth}
            trendDirection="up"
            color="purple"
          />
          <MetricCard
            title="Active Monitoring"
            value={stats.activeMonitoring.toLocaleString()}
            icon={EyeIcon}
            trend={((stats.activeMonitoring / stats.protectedFiles) * 100).toFixed(1)}
            trendDirection="up"
            color="indigo"
            suffix="% coverage"
          />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts and Analytics */}
          <div className="lg:col-span-2 space-y-6">
            <RevenueChart />
            <ProtectionStatus 
              totalViolations={stats.totalViolations}
              resolvedViolations={stats.resolvedViolations}
            />
          </div>

          {/* Right Column - Recent Activity and Quick Actions */}
          <div className="space-y-6">
            <RecentActivity />
            
            {/* Quick Actions */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full btn-primary text-left">
                  <DocumentDuplicateIcon className="w-5 h-5 inline mr-2" />
                  Upload New Content
                </button>
                <button className="w-full btn-secondary text-left">
                  <EyeIcon className="w-5 h-5 inline mr-2" />
                  Monitor Platforms
                </button>
                <button className="w-full btn-secondary text-left">
                  <ChartBarIcon className="w-5 h-5 inline mr-2" />
                  View Analytics
                </button>
                <button className="w-full btn-secondary text-left">
                  <UsersIcon className="w-5 h-5 inline mr-2" />
                  Find Collaborators
                </button>
              </div>
            </div>

            {/* System Status */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API Status</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Operational
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Fingerprinting Engine</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Monitoring System</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Scanning
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">AI Processing</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    Processing
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}