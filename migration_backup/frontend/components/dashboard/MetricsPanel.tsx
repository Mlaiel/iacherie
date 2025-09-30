/**
 * 🎯 METRICS PANEL COMPONENT
 * Panneau de métriques temps réel pour les services
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle,
  CheckCircle2,
  Clock,
  Zap,
  Database,
  Network,
  Cpu,
  HardDrive
} from 'lucide-react';

interface MetricDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

interface RealTimeMetrics {
  cpu: MetricDataPoint[];
  memory: MetricDataPoint[];
  network: MetricDataPoint[];
  requests: MetricDataPoint[];
  errors: MetricDataPoint[];
  latency: MetricDataPoint[];
  uptime: number;
  status: 'healthy' | 'warning' | 'critical';
}

interface MetricsPanelProps {
  serviceId: string;
  serviceName: string;
  realTime?: boolean;
  refreshInterval?: number;
  showControls?: boolean;
  className?: string;
}

// Couleurs pour les graphiques
const COLORS = {
  primary: '#3B82F6',
  secondary: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  purple: '#8B5CF6',
  teal: '#14B8A6'
};

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#14B8A6'];

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  serviceId,
  serviceName,
  realTime = true,
  refreshInterval = 5000,
  showControls = true,
  className = ''
}) => {
  const [metrics, setMetrics] = useState<RealTimeMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [autoRefresh, setAutoRefresh] = useState(realTime);

  // Génération de données de test (en attente de l'API réelle)
  const generateTestData = (): RealTimeMetrics => {
    const now = new Date();
    const points = 20;
    
    const generateTimeSeries = (baseValue: number, variance: number) => {
      return Array.from({ length: points }, (_, i) => {
        const timestamp = new Date(now.getTime() - (points - i) * 60000);
        const value = Math.max(0, Math.min(100, 
          baseValue + (Math.random() - 0.5) * variance
        ));
        return {
          timestamp: timestamp.toISOString(),
          value: Math.round(value * 100) / 100
        };
      });
    };

    return {
      cpu: generateTimeSeries(45, 30),
      memory: generateTimeSeries(60, 20),
      network: generateTimeSeries(25, 40),
      requests: generateTimeSeries(150, 100).map(p => ({
        ...p,
        value: Math.round(p.value * 10)
      })),
      errors: generateTimeSeries(5, 10).map(p => ({
        ...p,
        value: Math.round(p.value)
      })),
      latency: generateTimeSeries(120, 80).map(p => ({
        ...p,
        value: Math.round(p.value)
      })),
      uptime: 99.7,
      status: 'healthy' as const
    };
  };

  // Chargement des métriques
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Simulation d'appel API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // TODO: Remplacer par l'appel API réel
        // const response = await fetch(`/api/metrics/${serviceId}?range=${selectedTimeRange}`);
        // const data = await response.json();
        
        const data = generateTestData();
        setMetrics(data);
      } catch (err) {
        setError('Erreur lors du chargement des métriques');
        console.error('Metrics fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
  }, [serviceId, selectedTimeRange]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(async () => {
      try {
        const data = generateTestData();
        setMetrics(data);
      } catch (err) {
        console.error('Auto-refresh error:', err);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  // Formatage des données pour les graphiques
  const formatChartData = (data: MetricDataPoint[]) => {
    return data.map(point => ({
      ...point,
      time: new Date(point.timestamp).toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }));
  };

  // Calcul des tendances
  const calculateTrend = (data: MetricDataPoint[]) => {
    if (data.length < 2) return 0;
    const recent = data.slice(-5);
    const older = data.slice(-10, -5);
    const recentAvg = recent.reduce((sum, p) => sum + p.value, 0) / recent.length;
    const olderAvg = older.reduce((sum, p) => sum + p.value, 0) / older.length;
    return ((recentAvg - olderAvg) / olderAvg) * 100;
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5 animate-spin" />
            <span>Chargement des métriques...</span>
          </CardTitle>
        </CardHeader>
      </Card>
    );
  }

  if (error || !metrics) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span>Erreur de chargement</span>
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => window.location.reload()}>
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  const cpuTrend = calculateTrend(metrics.cpu);
  const memoryTrend = calculateTrend(metrics.memory);
  const latencyTrend = calculateTrend(metrics.latency);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header avec contrôles */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5" />
                <span>Métriques - {serviceName}</span>
              </CardTitle>
              <CardDescription>
                Monitoring en temps réel des performances
              </CardDescription>
            </div>
            
            {showControls && (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={metrics.status === 'healthy' ? 'default' : 'destructive'}
                    className="flex items-center space-x-1"
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{metrics.status}</span>
                  </Badge>
                </div>
                
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                >
                  <option value="15m">15 minutes</option>
                  <option value="1h">1 heure</option>
                  <option value="6h">6 heures</option>
                  <option value="24h">24 heures</option>
                </select>

                <Button
                  variant={autoRefresh ? "default" : "outline"}
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className="flex items-center space-x-1"
                >
                  <Clock className="w-4 h-4" />
                  <span>{autoRefresh ? 'Auto' : 'Manuel'}</span>
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.cpu[metrics.cpu.length - 1]?.value.toFixed(1)}%
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {cpuTrend > 0 ? (
                <TrendingUp className="w-3 h-3 text-red-500 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
              )}
              <span>{Math.abs(cpuTrend).toFixed(1)}% depuis 5min</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.memory[metrics.memory.length - 1]?.value.toFixed(1)}%
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {memoryTrend > 0 ? (
                <TrendingUp className="w-3 h-3 text-red-500 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
              )}
              <span>{Math.abs(memoryTrend).toFixed(1)}% depuis 5min</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Requests</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.requests[metrics.requests.length - 1]?.value || 0}/min
            </div>
            <div className="text-xs text-muted-foreground">
              {metrics.errors[metrics.errors.length - 1]?.value || 0} erreurs
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Latency</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.latency[metrics.latency.length - 1]?.value || 0}ms
            </div>
            <div className="flex items-center text-xs text-muted-foreground">
              {latencyTrend > 0 ? (
                <TrendingUp className="w-3 h-3 text-red-500 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
              )}
              <span>{Math.abs(latencyTrend).toFixed(1)}% depuis 5min</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Graphiques détaillés */}
      <Tabs defaultValue="performance" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="traffic">Trafic</TabsTrigger>
          <TabsTrigger value="errors">Erreurs</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>CPU & Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={formatChartData(metrics.cpu)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke={COLORS.primary} 
                      name="CPU %" 
                      strokeWidth={2}
                    />
                    <Line 
                      type="monotone" 
                      data={formatChartData(metrics.memory)}
                      dataKey="value" 
                      stroke={COLORS.secondary} 
                      name="Memory %" 
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Network & Latency</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={formatChartData(metrics.network)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke={COLORS.teal} 
                      fill={COLORS.teal}
                      fillOpacity={0.3}
                      name="Network MB/s"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="traffic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Requests per Minute</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={formatChartData(metrics.requests)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Bar 
                    dataKey="value" 
                    fill={COLORS.primary}
                    name="Requests/min"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Error Tracking</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={formatChartData(metrics.errors)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={COLORS.danger} 
                    name="Errors" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MetricsPanel;