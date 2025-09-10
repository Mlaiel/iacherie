/**
 * 📊 Dashboard Interface - Enterprise Dashboard Management
 * 
 * @fileoverview Advanced dashboard interface with real-time metrics and AI insights
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  PlayIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  CogIcon,
  BellIcon
} from '@heroicons/react/24/outline';

// ====================================================================
// DASHBOARD INTERFACES
// ====================================================================

export interface DashboardState {
  metrics: DashboardMetrics;
  widgets: DashboardWidget[];
  layout: DashboardLayout;
  filters: DashboardFilters;
  realTimeData: RealtimeMetrics;
  loading: boolean;
  error: string | null;
}

export interface DashboardMetrics {
  overview: OverviewMetrics;
  content: ContentMetrics;
  engagement: EngagementMetrics;
  revenue: RevenueMetrics;
  audience: AudienceMetrics;
  performance: PerformanceMetrics;
}

export interface OverviewMetrics {
  totalContent: number;
  totalViews: number;
  totalEngagement: number;
  totalRevenue: number;
  growthRate: number;
  activeUsers: number;
  conversionRate: number;
}

export interface ContentMetrics {
  published: number;
  draft: number;
  scheduled: number;
  processing: number;
  topPerforming: ContentItem[];
  recentUploads: ContentItem[];
  contentByType: Record<string, number>;
}

export interface ContentItem {
  id: string;
  title: string;
  type: 'video' | 'audio' | 'image' | 'text';
  views: number;
  engagement: number;
  revenue: number;
  publishedAt: number;
  thumbnail?: string;
}

export interface EngagementMetrics {
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  engagementRate: number;
  averageWatchTime: number;
  topEngagingContent: ContentItem[];
  engagementTrends: TrendData[];
}

export interface TrendData {
  date: string;
  value: number;
  change: number;
  label: string;
}

export interface RevenueMetrics {
  totalEarnings: number;
  monthlyRecurring: number;
  oneTimePayments: number;
  averageOrderValue: number;
  revenueBySource: Record<string, number>;
  revenueByPlatform: Record<string, number>;
  revenueTrends: TrendData[];
}

export interface AudienceMetrics {
  totalFollowers: number;
  newFollowers: number;
  followerGrowthRate: number;
  demographics: Demographics;
  topCountries: CountryData[];
  audienceRetention: number;
}

export interface Demographics {
  ageGroups: Record<string, number>;
  genders: Record<string, number>;
  interests: Record<string, number>;
  devices: Record<string, number>;
}

export interface CountryData {
  country: string;
  code: string;
  followers: number;
  percentage: number;
}

export interface PerformanceMetrics {
  loadTime: number;
  uptime: number;
  errorRate: number;
  apiLatency: number;
  cacheHitRate: number;
  systemHealth: 'healthy' | 'degraded' | 'critical';
}

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  position: WidgetPosition;
  config: WidgetConfig;
  data: any;
  loading: boolean;
  error?: string;
}

export type WidgetType = 
  | 'metric-card'
  | 'line-chart'
  | 'bar-chart'
  | 'pie-chart'
  | 'table'
  | 'list'
  | 'heatmap'
  | 'gauge'
  | 'progress'
  | 'activity-feed'
  | 'content-grid'
  | 'revenue-chart'
  | 'audience-map';

export interface WidgetSize {
  width: number; // Grid columns (1-12)
  height: number; // Grid rows
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface WidgetPosition {
  x: number;
  y: number;
  z?: number; // Layer order
}

export interface WidgetConfig {
  refreshInterval?: number; // seconds
  autoRefresh?: boolean;
  showHeader?: boolean;
  showFooter?: boolean;
  interactive?: boolean;
  exportable?: boolean;
  customizable?: boolean;
  theme?: 'light' | 'dark' | 'auto';
  [key: string]: any;
}

export interface DashboardLayout {
  id: string;
  name: string;
  isDefault: boolean;
  gridSize: { columns: number; rows: number };
  widgets: string[];
  responsive: boolean;
  breakpoints: Record<string, LayoutBreakpoint>;
}

export interface LayoutBreakpoint {
  minWidth: number;
  columns: number;
  margin: [number, number];
  padding: [number, number];
}

export interface DashboardFilters {
  dateRange: DateRange;
  platforms: string[];
  contentTypes: string[];
  metrics: string[];
  customFilters: Record<string, any>;
}

export interface DateRange {
  start: Date;
  end: Date;
  preset?: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom';
}

export interface RealtimeMetrics {
  activeUsers: number;
  liveViews: number;
  currentRevenue: number;
  systemLoad: number;
  alerts: SystemAlert[];
  lastUpdate: number;
}

export interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  actionable: boolean;
  action?: AlertAction;
}

export interface AlertAction {
  label: string;
  type: 'button' | 'link';
  url?: string;
  handler?: () => void;
}

// ====================================================================
// DASHBOARD INTERFACE COMPONENT
// ====================================================================

export interface DashboardInterfaceProps {
  userId: string;
  config?: DashboardConfig;
  onMetricSelect?: (metric: string) => void;
  onWidgetAction?: (widgetId: string, action: string) => void;
  className?: string;
}

export interface DashboardConfig {
  defaultLayout: string;
  refreshInterval: number;
  enableRealtimeUpdates: boolean;
  enableCustomization: boolean;
  theme: 'light' | 'dark' | 'auto';
  locale: string;
  timezone: string;
}

const DashboardInterface: React.FC<DashboardInterfaceProps> = ({
  userId,
  config = getDefaultConfig(),
  onMetricSelect,
  onWidgetAction,
  className = ''
}) => {
  const [state, setState] = useState<DashboardState>(getInitialState());
  const [selectedTimeRange, setSelectedTimeRange] = useState<DateRange>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
    preset: 'month'
  });

  // ====================================================================
  // DATA FETCHING
  // ====================================================================

  const fetchDashboardData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockMetrics = generateMockMetrics();
      const mockWidgets = generateMockWidgets();

      setState(prev => ({
        ...prev,
        metrics: mockMetrics,
        widgets: mockWidgets,
        loading: false
      }));

    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load dashboard data'
      }));
    }
  }, [userId, selectedTimeRange]);

  // ====================================================================
  // REAL-TIME UPDATES
  // ====================================================================

  useEffect(() => {
    fetchDashboardData();

    if (config.enableRealtimeUpdates) {
      const interval = setInterval(fetchDashboardData, config.refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [fetchDashboardData, config]);

  // ====================================================================
  // RENDER METHODS
  // ====================================================================

  const renderMetricCard = (title: string, value: string | number, icon: React.ReactNode, trend?: number) => (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend >= 0 ? <TrendingUpIcon className="w-4 h-4 mr-1" /> : <TrendingDownIcon className="w-4 h-4 mr-1" />}
              {Math.abs(trend)}%
            </div>
          )}
        </div>
        <div className="p-3 bg-blue-50 rounded-lg">
          {icon}
        </div>
      </div>
    </div>
  );

  const renderTopContent = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Top Performing Content</h3>
      <div className="space-y-4">
        {state.metrics.content.topPerforming.slice(0, 5).map((item, index) => (
          <div key={item.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
              {index + 1}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
              <p className="text-sm text-gray-500">{item.type} • {formatNumber(item.views)} views</p>
            </div>
            <div className="flex-shrink-0 text-right">
              <p className="text-sm font-medium text-gray-900">${formatNumber(item.revenue)}</p>
              <p className="text-sm text-gray-500">{item.engagement}% engagement</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRevenueChart = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Revenue Trends</h3>
      <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">Revenue chart placeholder</p>
      </div>
    </div>
  );

  const renderAudienceInsights = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Audience Insights</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">Top Countries</h4>
          <div className="space-y-2">
            {state.metrics.audience.topCountries.slice(0, 3).map(country => (
              <div key={country.code} className="flex justify-between">
                <span className="text-sm text-gray-900">{country.country}</span>
                <span className="text-sm text-gray-500">{country.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">Age Groups</h4>
          <div className="space-y-2">
            {Object.entries(state.metrics.audience.demographics.ageGroups).slice(0, 3).map(([age, percentage]) => (
              <div key={age} className="flex justify-between">
                <span className="text-sm text-gray-900">{age}</span>
                <span className="text-sm text-gray-500">{percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderActivityFeed = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {state.realTimeData.alerts.slice(0, 5).map(alert => (
          <div key={alert.id} className="flex items-start space-x-3">
            <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
              alert.type === 'success' ? 'bg-green-500' :
              alert.type === 'warning' ? 'bg-yellow-500' :
              alert.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
            }`} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">{alert.title}</p>
              <p className="text-sm text-gray-500">{alert.message}</p>
              <p className="text-xs text-gray-400 mt-1">{formatTime(alert.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // ====================================================================
  // MAIN RENDER
  // ====================================================================

  if (state.loading) {
    return (
      <div className={`dashboard-interface ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className={`dashboard-interface ${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Dashboard</h3>
          <p className="text-red-600">{state.error}</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`dashboard-interface space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-4">
          <select
            value={selectedTimeRange.preset}
            onChange={(e) => setSelectedTimeRange(prev => ({ ...prev, preset: e.target.value as any }))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <BellIcon className="w-6 h-6" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <CogIcon className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {renderMetricCard(
          'Total Views',
          formatNumber(state.metrics.overview.totalViews),
          <EyeIcon className="w-6 h-6 text-blue-500" />,
          12.5
        )}
        {renderMetricCard(
          'Total Revenue',
          `$${formatNumber(state.metrics.overview.totalRevenue)}`,
          <CurrencyDollarIcon className="w-6 h-6 text-green-500" />,
          8.3
        )}
        {renderMetricCard(
          'Engagement',
          `${state.metrics.overview.totalEngagement}%`,
          <HeartIcon className="w-6 h-6 text-pink-500" />,
          -2.1
        )}
        {renderMetricCard(
          'Active Users',
          formatNumber(state.metrics.overview.activeUsers),
          <UsersIcon className="w-6 h-6 text-purple-500" />,
          15.7
        )}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {renderTopContent()}
        {renderRevenueChart()}
        {renderAudienceInsights()}
      </div>

      {/* Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderActivityFeed()}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors">
              <CloudArrowUpIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Upload Content</p>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors">
              <DocumentTextIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Create Post</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

function getDefaultConfig(): DashboardConfig {
  return {
    defaultLayout: 'standard',
    refreshInterval: 60,
    enableRealtimeUpdates: true,
    enableCustomization: true,
    theme: 'light',
    locale: 'en-US',
    timezone: 'UTC'
  };
}

function getInitialState(): DashboardState {
  return {
    metrics: {
      overview: {
        totalContent: 0,
        totalViews: 0,
        totalEngagement: 0,
        totalRevenue: 0,
        growthRate: 0,
        activeUsers: 0,
        conversionRate: 0
      },
      content: {
        published: 0,
        draft: 0,
        scheduled: 0,
        processing: 0,
        topPerforming: [],
        recentUploads: [],
        contentByType: {}
      },
      engagement: {
        totalLikes: 0,
        totalComments: 0,
        totalShares: 0,
        engagementRate: 0,
        averageWatchTime: 0,
        topEngagingContent: [],
        engagementTrends: []
      },
      revenue: {
        totalEarnings: 0,
        monthlyRecurring: 0,
        oneTimePayments: 0,
        averageOrderValue: 0,
        revenueBySource: {},
        revenueByPlatform: {},
        revenueTrends: []
      },
      audience: {
        totalFollowers: 0,
        newFollowers: 0,
        followerGrowthRate: 0,
        demographics: {
          ageGroups: {},
          genders: {},
          interests: {},
          devices: {}
        },
        topCountries: [],
        audienceRetention: 0
      },
      performance: {
        loadTime: 0,
        uptime: 0,
        errorRate: 0,
        apiLatency: 0,
        cacheHitRate: 0,
        systemHealth: 'healthy'
      }
    },
    widgets: [],
    layout: {
      id: 'default',
      name: 'Default Layout',
      isDefault: true,
      gridSize: { columns: 12, rows: 20 },
      widgets: [],
      responsive: true,
      breakpoints: {}
    },
    filters: {
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
        preset: 'month'
      },
      platforms: [],
      contentTypes: [],
      metrics: [],
      customFilters: {}
    },
    realTimeData: {
      activeUsers: 0,
      liveViews: 0,
      currentRevenue: 0,
      systemLoad: 0,
      alerts: [],
      lastUpdate: 0
    },
    loading: true,
    error: null
  };
}

function generateMockMetrics(): DashboardMetrics {
  return {
    overview: {
      totalContent: 1247,
      totalViews: 2847295,
      totalEngagement: 8.7,
      totalRevenue: 45280,
      growthRate: 12.5,
      activeUsers: 18493,
      conversionRate: 3.2
    },
    content: {
      published: 1203,
      draft: 28,
      scheduled: 16,
      processing: 4,
      topPerforming: [
        {
          id: '1',
          title: 'AI Music Generation Tutorial',
          type: 'video',
          views: 125000,
          engagement: 12.5,
          revenue: 2800,
          publishedAt: Date.now() - 24 * 60 * 60 * 1000
        },
        {
          id: '2',
          title: 'Building Your Creator Brand',
          type: 'audio',
          views: 98000,
          engagement: 15.2,
          revenue: 1900,
          publishedAt: Date.now() - 48 * 60 * 60 * 1000
        }
      ],
      recentUploads: [],
      contentByType: {
        video: 520,
        audio: 380,
        image: 240,
        text: 107
      }
    },
    engagement: {
      totalLikes: 284920,
      totalComments: 48572,
      totalShares: 19284,
      engagementRate: 8.7,
      averageWatchTime: 142,
      topEngagingContent: [],
      engagementTrends: []
    },
    revenue: {
      totalEarnings: 45280,
      monthlyRecurring: 12500,
      oneTimePayments: 32780,
      averageOrderValue: 24.80,
      revenueBySource: {
        subscriptions: 12500,
        tips: 8900,
        sales: 23880
      },
      revenueByPlatform: {
        youtube: 18500,
        spotify: 12200,
        instagram: 8900,
        tiktok: 5680
      },
      revenueTrends: []
    },
    audience: {
      totalFollowers: 284730,
      newFollowers: 2847,
      followerGrowthRate: 15.7,
      demographics: {
        ageGroups: {
          '18-24': 32,
          '25-34': 45,
          '35-44': 18,
          '45+': 5
        },
        genders: {
          'Male': 58,
          'Female': 39,
          'Other': 3
        },
        interests: {
          'Music': 78,
          'Technology': 65,
          'Gaming': 52
        },
        devices: {
          'Mobile': 68,
          'Desktop': 25,
          'Tablet': 7
        }
      },
      topCountries: [
        { country: 'United States', code: 'US', followers: 95840, percentage: 33.7 },
        { country: 'United Kingdom', code: 'UK', followers: 42920, percentage: 15.1 },
        { country: 'Canada', code: 'CA', followers: 28470, percentage: 10.0 }
      ],
      audienceRetention: 87.5
    },
    performance: {
      loadTime: 847,
      uptime: 99.8,
      errorRate: 0.02,
      apiLatency: 145,
      cacheHitRate: 94.2,
      systemHealth: 'healthy'
    }
  };
}

function generateMockWidgets(): DashboardWidget[] {
  return [
    {
      id: 'overview-metrics',
      type: 'metric-card',
      title: 'Overview Metrics',
      size: { width: 12, height: 2 },
      position: { x: 0, y: 0 },
      config: { autoRefresh: true, refreshInterval: 60 },
      data: {},
      loading: false
    }
  ];
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

function formatTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return `${Math.floor(diff / 86400000)}d ago`;
}

export default DashboardInterface;