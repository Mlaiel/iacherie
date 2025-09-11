/**
 * 📊 Advanced Analytics Dashboard - Enterprise Business Intelligence
 * 
 * @fileoverview Real-time analytics dashboard with ML-powered insights
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  UsersIcon,
  EyeIcon,
  CloudArrowUpIcon,
  BoltIcon,
  ShieldCheckIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

// === ANALYTICS TYPES ===

export interface MetricDefinition {
  id: string;
  name: string;
  description: string;
  category: 'revenue' | 'engagement' | 'performance' | 'content' | 'user' | 'technical';
  unit: 'currency' | 'percentage' | 'count' | 'time' | 'bytes' | 'rate';
  format: 'number' | 'currency' | 'percentage' | 'duration' | 'bytes';
  aggregation: 'sum' | 'average' | 'max' | 'min' | 'count' | 'unique';
  isKPI: boolean;
  target?: number;
  thresholds: MetricThreshold[];
}

export interface MetricThreshold {
  level: 'critical' | 'warning' | 'good' | 'excellent';
  operator: 'gt' | 'gte' | 'lt' | 'lte' | 'eq';
  value: number;
  color: string;
}

export interface DataPoint {
  timestamp: number;
  value: number;
  metadata?: Record<string, any>;
}

export interface MetricData {
  metricId: string;
  timeRange: TimeRange;
  data: DataPoint[];
  currentValue: number;
  previousValue: number;
  change: number;
  changePercentage: number;
  trend: 'up' | 'down' | 'stable';
  status: 'critical' | 'warning' | 'good' | 'excellent';
}

export interface TimeRange {
  start: number;
  end: number;
  granularity: 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';
}

export interface DashboardConfig {
  id: string;
  name: string;
  description?: string;
  layout: DashboardLayout;
  widgets: DashboardWidget[];
  filters: DashboardFilter[];
  refreshInterval: number; // seconds
  isRealtime: boolean;
  permissions: string[];
  createdAt: number;
  updatedAt: number;
}

export interface DashboardLayout {
  type: 'grid' | 'flex' | 'custom';
  columns: number;
  rows: number;
  gap: number;
  responsive: boolean;
}

export interface DashboardWidget {
  id: string;
  type: 'chart' | 'kpi' | 'table' | 'map' | 'text' | 'iframe';
  title: string;
  description?: string;
  position: WidgetPosition;
  size: WidgetSize;
  config: WidgetConfig;
  dataSources: string[];
  refreshRate?: number;
  isVisible: boolean;
}

export interface WidgetPosition {
  x: number;
  y: number;
  z?: number;
}

export interface WidgetSize {
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface WidgetConfig {
  chartType?: 'line' | 'bar' | 'pie' | 'doughnut' | 'area' | 'scatter' | 'heatmap';
  colors?: string[];
  showLegend?: boolean;
  showGrid?: boolean;
  animations?: boolean;
  customCSS?: string;
  interactivity?: WidgetInteractivity;
}

export interface WidgetInteractivity {
  clickEnabled: boolean;
  hoverEnabled: boolean;
  zoomEnabled: boolean;
  drillDownEnabled: boolean;
  exportEnabled: boolean;
}

export interface DashboardFilter {
  id: string;
  name: string;
  type: 'select' | 'multiselect' | 'date' | 'daterange' | 'text' | 'number';
  options?: FilterOption[];
  defaultValue?: any;
  required: boolean;
  applies: string[]; // widget IDs
}

export interface FilterOption {
  value: any;
  label: string;
  description?: string;
}

export interface AnalyticsInsight {
  id: string;
  type: 'anomaly' | 'trend' | 'correlation' | 'forecast' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  actionable: boolean;
  actions?: InsightAction[];
  relatedMetrics: string[];
  createdAt: number;
  validUntil?: number;
}

export interface InsightAction {
  id: string;
  title: string;
  description: string;
  type: 'optimize' | 'investigate' | 'alert' | 'automate';
  effort: 'low' | 'medium' | 'high';
  expectedImpact: string;
}

export interface RealtimeEvent {
  id: string;
  type: 'metric_update' | 'alert' | 'insight' | 'user_action' | 'system_event';
  source: string;
  data: any;
  timestamp: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

// === ANALYTICS CONTEXT ===

interface AnalyticsContextValue {
  dashboards: DashboardConfig[];
  currentDashboard: DashboardConfig | null;
  metrics: Record<string, MetricData>;
  insights: AnalyticsInsight[];
  realtimeEvents: RealtimeEvent[];
  isLoading: boolean;
  isRealtime: boolean;
  selectedTimeRange: TimeRange;
  setTimeRange: (range: TimeRange) => void;
  setDashboard: (dashboardId: string) => void;
  addWidget: (widget: DashboardWidget) => void;
  updateWidget: (widgetId: string, updates: Partial<DashboardWidget>) => void;
  removeWidget: (widgetId: string) => void;
  exportDashboard: (format: 'pdf' | 'png' | 'json') => Promise<Blob>;
  getMetricData: (metricId: string, timeRange: TimeRange) => Promise<MetricData>;
  generateInsights: () => Promise<AnalyticsInsight[]>;
  subscribeToRealtime: (callback: (event: RealtimeEvent) => void) => () => void;
}

const AnalyticsContext = createContext<AnalyticsContextValue | null>(null);

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

// === ANALYTICS PROVIDER ===

interface AnalyticsProviderProps {
  children: React.ReactNode;
  apiEndpoint?: string;
  websocketUrl?: string;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({
  children,
  apiEndpoint = '/api/v1/analytics',
  websocketUrl = 'ws://localhost:8000/ws/analytics'
}) => {
  const [dashboards, setDashboards] = useState<DashboardConfig[]>(DEFAULT_DASHBOARDS);
  const [currentDashboard, setCurrentDashboard] = useState<DashboardConfig | null>(DEFAULT_DASHBOARDS[0]);
  const [metrics, setMetrics] = useState<Record<string, MetricData>>({});
  const [insights, setInsights] = useState<AnalyticsInsight[]>([]);
  const [realtimeEvents, setRealtimeEvents] = useState<RealtimeEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRealtime, setIsRealtime] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>({
    start: Date.now() - 24 * 60 * 60 * 1000, // Last 24 hours
    end: Date.now(),
    granularity: 'hour'
  });

  const setTimeRange = useCallback((range: TimeRange) => {
    setSelectedTimeRange(range);
    // Refresh metrics with new time range
    refreshMetrics(range);
  }, []);

  const setDashboard = useCallback((dashboardId: string) => {
    const dashboard = dashboards.find(d => d.id === dashboardId);
    if (dashboard) {
      setCurrentDashboard(dashboard);
      refreshMetrics(selectedTimeRange);
    }
  }, [dashboards, selectedTimeRange]);

  const refreshMetrics = useCallback(async (timeRange: TimeRange) => {
    if (!currentDashboard) return;

    setIsLoading(true);
    try {
      // Mock API call to fetch metrics
      const metricsData: Record<string, MetricData> = {};
      
      for (const widget of currentDashboard.widgets) {
        for (const metricId of widget.dataSources) {
          const mockData = generateMockMetricData(metricId, timeRange);
          metricsData[metricId] = mockData;
        }
      }
      
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to refresh metrics:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDashboard]);

  const addWidget = useCallback((widget: DashboardWidget) => {
    if (!currentDashboard) return;

    const updatedDashboard = {
      ...currentDashboard,
      widgets: [...currentDashboard.widgets, widget],
      updatedAt: Date.now()
    };

    setCurrentDashboard(updatedDashboard);
    setDashboards(prev => prev.map(d => 
      d.id === currentDashboard.id ? updatedDashboard : d
    ));
  }, [currentDashboard]);

  const updateWidget = useCallback((widgetId: string, updates: Partial<DashboardWidget>) => {
    if (!currentDashboard) return;

    const updatedDashboard = {
      ...currentDashboard,
      widgets: currentDashboard.widgets.map(w => 
        w.id === widgetId ? { ...w, ...updates } : w
      ),
      updatedAt: Date.now()
    };

    setCurrentDashboard(updatedDashboard);
    setDashboards(prev => prev.map(d => 
      d.id === currentDashboard.id ? updatedDashboard : d
    ));
  }, [currentDashboard]);

  const removeWidget = useCallback((widgetId: string) => {
    if (!currentDashboard) return;

    const updatedDashboard = {
      ...currentDashboard,
      widgets: currentDashboard.widgets.filter(w => w.id !== widgetId),
      updatedAt: Date.now()
    };

    setCurrentDashboard(updatedDashboard);
    setDashboards(prev => prev.map(d => 
      d.id === currentDashboard.id ? updatedDashboard : d
    ));
  }, [currentDashboard]);

  const exportDashboard = useCallback(async (format: 'pdf' | 'png' | 'json'): Promise<Blob> => {
    // Mock export functionality
    const data = format === 'json' ? 
      JSON.stringify(currentDashboard, null, 2) : 
      'Mock dashboard export data';
    
    return new Blob([data], { 
      type: format === 'json' ? 'application/json' : 
            format === 'pdf' ? 'application/pdf' : 'image/png'
    });
  }, [currentDashboard]);

  const getMetricData = useCallback(async (metricId: string, timeRange: TimeRange): Promise<MetricData> => {
    // Mock API call
    return generateMockMetricData(metricId, timeRange);
  }, []);

  const generateInsights = useCallback(async (): Promise<AnalyticsInsight[]> => {
    // Mock insights generation
    const mockInsights: AnalyticsInsight[] = [
      {
        id: 'insight_1',
        type: 'anomaly',
        title: 'Unusual Traffic Spike Detected',
        description: 'Website traffic increased by 340% in the last 2 hours, significantly above normal patterns.',
        confidence: 0.92,
        impact: 'high',
        actionable: true,
        actions: [
          {
            id: 'action_1',
            title: 'Scale Infrastructure',
            description: 'Increase server capacity to handle the traffic surge',
            type: 'automate',
            effort: 'low',
            expectedImpact: 'Prevent system overload and maintain performance'
          }
        ],
        relatedMetrics: ['website_traffic', 'server_response_time'],
        createdAt: Date.now() - 300000
      },
      {
        id: 'insight_2',
        type: 'recommendation',
        title: 'Optimize Content Upload Times',
        description: 'Content upload times have increased by 25% over the past week. Consider implementing compression.',
        confidence: 0.85,
        impact: 'medium',
        actionable: true,
        actions: [
          {
            id: 'action_2',
            title: 'Enable Compression',
            description: 'Implement automatic file compression for uploads',
            type: 'optimize',
            effort: 'medium',
            expectedImpact: 'Reduce upload times by 30-40%'
          }
        ],
        relatedMetrics: ['upload_time', 'file_size'],
        createdAt: Date.now() - 600000
      }
    ];

    setInsights(mockInsights);
    return mockInsights;
  }, []);

  const subscribeToRealtime = useCallback((callback: (event: RealtimeEvent) => void) => {
    // Mock real-time subscription
    const interval = setInterval(() => {
      const mockEvent: RealtimeEvent = {
        id: `event_${Date.now()}`,
        type: 'metric_update',
        source: 'analytics_engine',
        data: {
          metricId: 'active_users',
          value: Math.floor(Math.random() * 1000) + 500
        },
        timestamp: Date.now(),
        priority: 'medium'
      };
      
      callback(mockEvent);
      setRealtimeEvents(prev => [...prev.slice(-19), mockEvent]); // Keep last 20 events
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Load initial data
  useEffect(() => {
    refreshMetrics(selectedTimeRange);
    generateInsights();
  }, [selectedTimeRange, refreshMetrics, generateInsights]);

  const contextValue: AnalyticsContextValue = {
    dashboards,
    currentDashboard,
    metrics,
    insights,
    realtimeEvents,
    isLoading,
    isRealtime,
    selectedTimeRange,
    setTimeRange,
    setDashboard,
    addWidget,
    updateWidget,
    removeWidget,
    exportDashboard,
    getMetricData,
    generateInsights,
    subscribeToRealtime
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
};

// === ANALYTICS COMPONENTS ===

interface AnalyticsDashboardProps {
  className?: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ className }) => {
  return (
    <AnalyticsProvider>
      <div className={`min-h-screen bg-gray-50 ${className}`}>
        <DashboardHeader />
        <div className="flex">
          <DashboardSidebar />
          <div className="flex-1">
            <DashboardFilters />
            <DashboardGrid />
          </div>
        </div>
        <InsightsPanel />
      </div>
    </AnalyticsProvider>
  );
};

const DashboardHeader: React.FC = () => {
  const { currentDashboard, dashboards, setDashboard, exportDashboard } = useAnalytics();

  const handleExport = async (format: 'pdf' | 'png' | 'json') => {
    try {
      const blob = await exportDashboard(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <ChartBarIcon className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Analytics Dashboard</h1>
          {currentDashboard && (
            <p className="text-sm text-gray-500">{currentDashboard.name}</p>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <select
          value={currentDashboard?.id || ''}
          onChange={(e) => setDashboard(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {dashboards.map(dashboard => (
            <option key={dashboard.id} value={dashboard.id}>
              {dashboard.name}
            </option>
          ))}
        </select>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleExport('json')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export JSON
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
          >
            Export PDF
          </button>
        </div>
      </div>
    </div>
  );
};

const DashboardSidebar: React.FC = () => {
  const { insights, realtimeEvents } = useAnalytics();

  return (
    <div className="w-80 bg-white border-r border-gray-200 p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
          <div className="space-y-3">
            {insights.slice(0, 3).map(insight => (
              <div
                key={insight.id}
                className={`p-3 rounded-lg border-l-4 ${
                  insight.impact === 'critical' ? 'border-red-500 bg-red-50' :
                  insight.impact === 'high' ? 'border-orange-500 bg-orange-50' :
                  insight.impact === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                  'border-blue-500 bg-blue-50'
                }`}
              >
                <h4 className="font-medium text-gray-900 text-sm">{insight.title}</h4>
                <p className="text-xs text-gray-600 mt-1">{insight.description}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">
                    {Math.round(insight.confidence * 100)}% confidence
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    insight.impact === 'critical' ? 'bg-red-100 text-red-800' :
                    insight.impact === 'high' ? 'bg-orange-100 text-orange-800' :
                    insight.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {insight.impact}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Real-time Events</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {realtimeEvents.slice(-5).map(event => (
              <div key={event.id} className="p-2 bg-gray-50 rounded text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{event.type}</span>
                  <span className="text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-gray-600 mt-1">
                  {JSON.stringify(event.data, null, 2).slice(0, 100)}...
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const DashboardFilters: React.FC = () => {
  const { selectedTimeRange, setTimeRange } = useAnalytics();

  const timeRangeOptions = [
    { label: 'Last Hour', value: { hours: 1 } },
    { label: 'Last 24 Hours', value: { hours: 24 } },
    { label: 'Last 7 Days', value: { days: 7 } },
    { label: 'Last 30 Days', value: { days: 30 } },
    { label: 'Last 90 Days', value: { days: 90 } }
  ];

  const handleTimeRangeChange = (option: typeof timeRangeOptions[0]) => {
    const now = Date.now();
    const start = now - (
      'hours' in option.value && option.value.hours ? option.value.hours * 60 * 60 * 1000 :
      'days' in option.value && option.value.days ? option.value.days * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000
    );

    setTimeRange({
      start,
      end: now,
      granularity: 'hours' in option.value && option.value.hours && option.value.hours <= 24 ? 'hour' : 'day'
    });
  };

  return (
    <div className="bg-white border-b border-gray-200 p-4">
      <div className="flex items-center space-x-4">
        <label className="text-sm font-medium text-gray-700">Time Range:</label>
        <select
          onChange={(e) => {
            const option = timeRangeOptions[parseInt(e.target.value)];
            handleTimeRangeChange(option);
          }}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {timeRangeOptions.map((option, index) => (
            <option key={index} value={index}>
              {option.label}
            </option>
          ))}
        </select>

        <div className="text-sm text-gray-500">
          {new Date(selectedTimeRange.start).toLocaleDateString()} - {new Date(selectedTimeRange.end).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

const DashboardGrid: React.FC = () => {
  const { currentDashboard, metrics, isLoading } = useAnalytics();

  if (!currentDashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">No dashboard selected</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {currentDashboard.widgets.map(widget => (
          <AnalyticsWidget key={widget.id} widget={widget} data={metrics[widget.dataSources[0]]} />
        ))}
      </div>
    </div>
  );
};

interface AnalyticsWidgetProps {
  widget: DashboardWidget;
  data?: MetricData;
}

const AnalyticsWidget: React.FC<AnalyticsWidgetProps> = ({ widget, data }) => {
  const getIcon = () => {
    switch (widget.dataSources[0]) {
      case 'revenue': return <CurrencyDollarIcon className="w-6 h-6" />;
      case 'users': return <UsersIcon className="w-6 h-6" />;
      case 'views': return <EyeIcon className="w-6 h-6" />;
      case 'uploads': return <CloudArrowUpIcon className="w-6 h-6" />;
      case 'performance': return <BoltIcon className="w-6 h-6" />;
      case 'security': return <ShieldCheckIcon className="w-6 h-6" />;
      default: return <ChartBarIcon className="w-6 h-6" />;
    }
  };

  const formatValue = (value: number) => {
    if (widget.dataSources[0] === 'revenue') {
      return `$${value.toLocaleString()}`;
    }
    if (widget.dataSources[0] === 'performance') {
      return `${value}ms`;
    }
    return value.toLocaleString();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{widget.title}</h3>
        <div className="text-blue-600">{getIcon()}</div>
      </div>
      
      {data && (
        <>
          <div className="text-3xl font-bold text-gray-900 mb-2">
            {formatValue(data.currentValue)}
          </div>
          
          <div className={`flex items-center text-sm ${
            data.trend === 'up' ? 'text-green-600' :
            data.trend === 'down' ? 'text-red-600' : 'text-gray-600'
          }`}>
            {data.trend === 'up' ? (
              <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
            ) : data.trend === 'down' ? (
              <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
            ) : null}
            <span>
              {data.changePercentage >= 0 ? '+' : ''}{data.changePercentage.toFixed(1)}%
            </span>
            <span className="text-gray-500 ml-2">vs previous period</span>
          </div>
          
          <div className={`mt-3 text-xs px-2 py-1 rounded inline-block ${
            data.status === 'excellent' ? 'bg-green-100 text-green-800' :
            data.status === 'good' ? 'bg-blue-100 text-blue-800' :
            data.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {data.status.toUpperCase()}
          </div>
        </>
      )}
    </div>
  );
};

const InsightsPanel: React.FC = () => {
  const { insights } = useAnalytics();

  return (
    <div className="fixed bottom-0 right-0 w-96 max-h-64 bg-white border border-gray-200 rounded-tl-lg shadow-lg z-50">
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">AI Insights</h3>
      </div>
      <div className="p-4 space-y-3 max-h-48 overflow-y-auto">
        {insights.map(insight => (
          <div key={insight.id} className="text-sm">
            <h4 className="font-medium text-gray-900">{insight.title}</h4>
            <p className="text-gray-600 text-xs mt-1">{insight.description}</p>
            {insight.actionable && insight.actions && (
              <button className="text-blue-600 text-xs mt-2 hover:text-blue-800">
                View Actions →
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// === UTILITY FUNCTIONS ===

function generateMockMetricData(metricId: string, timeRange: TimeRange): MetricData {
  const dataPoints: DataPoint[] = [];
  const pointCount = Math.floor((timeRange.end - timeRange.start) / getGranularityMs(timeRange.granularity));
  
  let baseValue = getBaseValueForMetric(metricId);
  
  for (let i = 0; i < pointCount; i++) {
    const timestamp = timeRange.start + (i * getGranularityMs(timeRange.granularity));
    const variation = (Math.random() - 0.5) * 0.2; // ±10% variation
    const value = Math.max(0, baseValue * (1 + variation));
    
    dataPoints.push({ timestamp, value });
    baseValue = value; // Trend continuation
  }

  const currentValue = dataPoints[dataPoints.length - 1]?.value || 0;
  const previousValue = dataPoints[dataPoints.length - 2]?.value || currentValue;
  const change = currentValue - previousValue;
  const changePercentage = previousValue > 0 ? (change / previousValue) * 100 : 0;

  return {
    metricId,
    timeRange,
    data: dataPoints,
    currentValue,
    previousValue,
    change,
    changePercentage,
    trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable',
    status: currentValue > baseValue * 1.2 ? 'excellent' :
             currentValue > baseValue * 1.1 ? 'good' :
             currentValue > baseValue * 0.9 ? 'warning' : 'critical'
  };
}

function getGranularityMs(granularity: TimeRange['granularity']): number {
  switch (granularity) {
    case 'minute': return 60 * 1000;
    case 'hour': return 60 * 60 * 1000;
    case 'day': return 24 * 60 * 60 * 1000;
    case 'week': return 7 * 24 * 60 * 60 * 1000;
    case 'month': return 30 * 24 * 60 * 60 * 1000;
    case 'year': return 365 * 24 * 60 * 60 * 1000;
    default: return 60 * 60 * 1000;
  }
}

function getBaseValueForMetric(metricId: string): number {
  const baseValues: Record<string, number> = {
    revenue: 25000,
    users: 1250,
    views: 15000,
    uploads: 350,
    performance: 180,
    security: 5
  };
  return baseValues[metricId] || 1000;
}

// === DEFAULT DATA ===

const DEFAULT_DASHBOARDS: DashboardConfig[] = [
  {
    id: 'main-dashboard',
    name: 'Main Analytics Dashboard',
    description: 'Overview of key business metrics',
    layout: {
      type: 'grid',
      columns: 4,
      rows: 3,
      gap: 6,
      responsive: true
    },
    widgets: [
      {
        id: 'revenue-widget',
        type: 'kpi',
        title: 'Revenue',
        position: { x: 0, y: 0 },
        size: { width: 1, height: 1 },
        config: { chartType: 'line', colors: ['#10B981'] },
        dataSources: ['revenue'],
        isVisible: true
      },
      {
        id: 'users-widget',
        type: 'kpi',
        title: 'Active Users',
        position: { x: 1, y: 0 },
        size: { width: 1, height: 1 },
        config: { chartType: 'line', colors: ['#3B82F6'] },
        dataSources: ['users'],
        isVisible: true
      },
      {
        id: 'views-widget',
        type: 'kpi',
        title: 'Content Views',
        position: { x: 2, y: 0 },
        size: { width: 1, height: 1 },
        config: { chartType: 'line', colors: ['#8B5CF6'] },
        dataSources: ['views'],
        isVisible: true
      },
      {
        id: 'uploads-widget',
        type: 'kpi',
        title: 'Content Uploads',
        position: { x: 3, y: 0 },
        size: { width: 1, height: 1 },
        config: { chartType: 'line', colors: ['#F59E0B'] },
        dataSources: ['uploads'],
        isVisible: true
      }
    ],
    filters: [],
    refreshInterval: 30,
    isRealtime: true,
    permissions: ['admin', 'analyst'],
    createdAt: Date.now() - 86400000,
    updatedAt: Date.now()
  }
];

export default AnalyticsDashboard;