/**
 * Professional Dashboard Component
 * 
 * Main enterprise dashboard with real backend connections
 * Connects to 53+ AI agents and 680+ microservices
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Brain, 
  Cpu, 
  Database, 
  Globe, 
  Users, 
  TrendingUp, 
  Shield, 
  Server,
  BarChart3,
  Zap,
  DollarSign,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface SystemMetrics {
  totalAgents: number;
  activeMicroservices: number;
  realTimeConnections: number;
  dataProcessed: string;
  revenue24h: string;
  activeUsers: number;
  contentGenerated: number;
  collaborationsActive: number;
  aiTasksProcessed: number;
  platformUptime: string;
  lastUpdate: string;
}

interface ModuleStatus {
  status: 'active' | 'degraded' | 'down';
  agents?: number;
  tasks?: number;
  processed?: number;
  renders?: number;
  rooms?: number;
  transactions?: number;
  dataPoints?: number;
  threats?: number;
  optimizations?: number;
}

interface DashboardData {
  enterprise: SystemMetrics;
  modules: Record<string, ModuleStatus>;
  performance: {
    uptime: number;
    memory_usage: number;
    cpu_usage: number;
    throughput: string;
    latency: string;
    errorRate: string;
    cacheHitRate: string;
  };
  realTime: {
    timestamp: string;
    connectionType: string;
    simulation: boolean;
    enterprise: boolean;
  };
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setConnectionStatus('connecting');
        const response = await fetch('/api/monitoring', {
          cache: 'no-store',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        if (result.success && result.data) {
          setDashboardData(result.data);
          setConnectionStatus('connected');
        } else {
          throw new Error('Invalid data format');
        }
      } catch (error) {
        console.error('Dashboard data fetch error:', error);
        setConnectionStatus('disconnected');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'down': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'down': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900">Loading Enterprise Dashboard</h2>
          <p className="text-gray-600 mt-2">Connecting to 53+ AI agents...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">Connection Error</h2>
          <p className="text-gray-600 mt-2">Unable to connect to enterprise backend</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const { enterprise, modules, performance, realTime } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Enterprise Dashboard</h1>
                <p className="text-sm text-gray-600">
                  Real-time monitoring - {enterprise.totalAgents} AI Agents - {enterprise.activeMicroservices} Microservices
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className={`flex items-center px-3 py-2 rounded-full text-sm font-medium ${
                connectionStatus === 'connected' 
                  ? 'bg-green-100 text-green-800' 
                  : connectionStatus === 'disconnected'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                <div className={`h-2 w-2 rounded-full mr-2 ${
                  connectionStatus === 'connected' 
                    ? 'bg-green-500 animate-pulse' 
                    : connectionStatus === 'disconnected'
                    ? 'bg-red-500'
                    : 'bg-yellow-500 animate-spin'
                }`}></div>
                {connectionStatus === 'connected' ? 'Online' : 
                 connectionStatus === 'disconnected' ? 'Offline' : 'Connecting...'}
              </div>
              
              <div className="text-xs text-gray-500">
                Updated: {new Date(realTime.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active AI Agents</p>
                <p className="text-3xl font-bold text-blue-600">{enterprise.totalAgents}</p>
              </div>
              <Brain className="h-12 w-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Microservices</p>
                <p className="text-3xl font-bold text-green-600">{enterprise.activeMicroservices}</p>
              </div>
              <Server className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Users</p>
                <p className="text-3xl font-bold text-purple-600">{enterprise.activeUsers.toLocaleString()}</p>
              </div>
              <Users className="h-12 w-12 text-purple-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Revenue 24h</p>
                <p className="text-3xl font-bold text-yellow-600">{enterprise.revenue24h}</p>
              </div>
              <DollarSign className="h-12 w-12 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Performance Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Zap className="h-5 w-5 text-blue-500 mr-2" />
              System Performance
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Uptime</span>
                <span className="font-medium text-green-600">{enterprise.platformUptime}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Latency</span>
                <span className="font-medium">{performance.latency}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Throughput</span>
                <span className="font-medium">{performance.throughput}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="font-medium text-green-600">{performance.errorRate}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 text-green-500 mr-2" />
              Real-time Activity
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Connections</span>
                <span className="font-medium">{enterprise.realTimeConnections}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Content Generated</span>
                <span className="font-medium">{enterprise.contentGenerated}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Collaborations</span>
                <span className="font-medium">{enterprise.collaborationsActive}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">AI Tasks</span>
                <span className="font-medium">{enterprise.aiTasksProcessed}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Database className="h-5 w-5 text-purple-500 mr-2" />
              Data & Storage
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Data Processed</span>
                <span className="font-medium">{enterprise.dataProcessed}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Cache Hit Rate</span>
                <span className="font-medium text-green-600">{performance.cacheHitRate}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">CPU Usage</span>
                <span className="font-medium">{performance.cpu_usage.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Memory Usage</span>
                <span className="font-medium">{performance.memory_usage.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modules Status */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Activity className="h-5 w-5 text-blue-500 mr-2" />
            Enterprise Modules Status
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(modules).map(([moduleName, moduleData]) => (
              <div 
                key={moduleName}
                className={`p-4 rounded-lg border ${getStatusColor(moduleData.status)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium capitalize">{moduleName.replace(/([A-Z])/g, ' $1')}</h4>
                  {getStatusIcon(moduleData.status)}
                </div>
                
                <div className="text-sm space-y-1">
                  {moduleData.agents && (
                    <div className="flex justify-between">
                      <span>Agents:</span>
                      <span className="font-medium">{moduleData.agents}</span>
                    </div>
                  )}
                  {moduleData.tasks && (
                    <div className="flex justify-between">
                      <span>Tasks:</span>
                      <span className="font-medium">{moduleData.tasks}</span>
                    </div>
                  )}
                  {moduleData.processed && (
                    <div className="flex justify-between">
                      <span>Processed:</span>
                      <span className="font-medium">{moduleData.processed}</span>
                    </div>
                  )}
                  {moduleData.rooms && (
                    <div className="flex justify-between">
                      <span>Rooms:</span>
                      <span className="font-medium">{moduleData.rooms}</span>
                    </div>
                  )}
                  {moduleData.transactions && (
                    <div className="flex justify-between">
                      <span>Transactions:</span>
                      <span className="font-medium">{moduleData.transactions}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}