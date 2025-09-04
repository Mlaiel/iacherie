'use client';

import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  CurrencyDollarIcon,
  EyeIcon,
  UsersIcon,
  DocumentDuplicateIcon,
  CalendarIcon,
  PhotoIcon,
  InformationCircleIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import { MetricCard } from './MetricCard';
import { ProtectionStatus } from './ProtectionStatus';
import { RecentActivity } from './RecentActivity';
import { RevenueChart } from './RevenueChart';
import { RealTimeAnalytics } from './RealTimeAnalytics';
import { ContentPreview } from './ContentPreview';
import { VisualPortfolioManagement } from './VisualPortfolio';
import { ContentPlanningCalendar } from './ContentCalendar';
import { useContent } from '@/hooks/useContent';
import { useNotifications } from '@/hooks/useNotifications';

export function Dashboard() {
  const { metrics, isLoading, refreshMetrics } = useContent();
  const { notifications } = useNotifications();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="px-6 py-8 space-y-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Professional Creator Dashboard</h1>
        <p className="text-gray-600">AI-Powered Content Protection, Analytics & Professional Management</p>
      </div>

      {/* Real-Time Analytics Section */}
      <RealTimeAnalytics />

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Content"
          value={metrics.total_content.toLocaleString()}
          icon={DocumentDuplicateIcon}
          trend={8.3}
          trendDirection="up"
          color="blue"
        />
        <MetricCard
          title="Protected Files"
          value={metrics.protected_files.toLocaleString()}
          icon={ShieldCheckIcon}
          trend={Math.round((metrics.protected_files / Math.max(metrics.total_content, 1)) * 100)}
          trendDirection="up"
          color="green"
          suffix="% protected"
        />
        <MetricCard
          title="Monthly Revenue"
          value={`$${metrics.monthly_revenue.toLocaleString()}`}
          icon={CurrencyDollarIcon}
          trend={12.5}
          trendDirection="up"
          color="purple"
        />
        <MetricCard
          title="Active Monitoring"
          value={metrics.active_monitoring.toLocaleString()}
          icon={EyeIcon}
          trend={Math.round((metrics.active_monitoring / Math.max(metrics.protected_files, 1)) * 100)}
          trendDirection="up"
          color="indigo"
          suffix="% coverage"
        />
      </div>

      {/* Professional Dashboard Features Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Content Preview with Metadata */}
        <ContentPreview />
        
        {/* Charts and Analytics */}
        <div className="space-y-6">
          <RevenueChart />
          <ProtectionStatus 
            totalViolations={metrics.violations_detected}
            resolvedViolations={metrics.violations_resolved}
          />
        </div>
      </div>

      {/* Visual Portfolio Management */}
      <VisualPortfolioManagement />

      {/* Content Planning Calendar */}
      <ContentPlanningCalendar />

      {/* Main Dashboard Grid - Sidebar Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Recent Activity */}
        <div className="lg:col-span-2">
          <RecentActivity />
        </div>

        {/* Right Column - Notifications and Quick Actions */}
        <div className="space-y-6">
          {/* Notifications Panel */}
          {notifications.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Notifications</h3>
              <div className="space-y-3">
                {notifications.slice(0, 3).map((notification) => (
                  <div key={notification.id} className={`p-3 rounded-lg text-sm border-l-4 ${
                    notification.type === 'success' ? 'bg-green-50 border-green-400 text-green-700' :
                    notification.type === 'error' ? 'bg-red-50 border-red-400 text-red-700' :
                    notification.type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-700' :
                    'bg-blue-50 border-blue-400 text-blue-700'
                  }`}>
                    <p>{notification.message}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(notification.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Professional Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Professional Actions</h3>
            <div className="space-y-3">
              <button 
                className="w-full btn-primary text-left"
                onClick={() => window.location.href = '/upload'}
              >
                <DocumentDuplicateIcon className="w-5 h-5 inline mr-2" />
                Upload Multi-Format Content
              </button>
              <button 
                className="w-full btn-secondary text-left"
                onClick={refreshMetrics}
              >
                <BoltIcon className="w-5 h-5 inline mr-2" />
                Refresh Real-Time Analytics
              </button>
              <button className="w-full btn-secondary text-left">
                <InformationCircleIcon className="w-5 h-5 inline mr-2" />
                Content Metadata Preview
              </button>
              <button className="w-full btn-secondary text-left">
                <PhotoIcon className="w-5 h-5 inline mr-2" />
                Portfolio Management
              </button>
              <button className="w-full btn-secondary text-left">
                <CalendarIcon className="w-5 h-5 inline mr-2" />
                Content Planning Calendar
              </button>
              <button className="w-full btn-secondary text-left">
                <ChartBarIcon className="w-5 h-5 inline mr-2" />
                Advanced Analytics
              </button>
              <button className="w-full btn-secondary text-left">
                <UsersIcon className="w-5 h-5 inline mr-2" />
                Collaboration Hub
              </button>
            </div>
          </div>

          {/* Professional System Status */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Professional System Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Real-Time Analytics Engine</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <BoltIcon className="w-3 h-3 mr-1" />
                  Live
                </span>
              </div>
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
                <span className="text-sm text-gray-600">Content Monitoring System</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Scanning
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Portfolio Management</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <PhotoIcon className="w-3 h-3 mr-1" />
                  Ready
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Calendar Sync</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <CalendarIcon className="w-3 h-3 mr-1" />
                  Synchronized
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
    </div>
  );
}