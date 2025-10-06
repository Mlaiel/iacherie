/**
 * STATUS MONITOR COMPONENT
 * Real-time monitoring of crawler status with WebSocket updates
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, AlertCircle, CheckCircle2, Clock, TrendingUp } from 'lucide-react';

interface StatusMetrics {
  total: number;
  active: number;
  inactive: number;
  pending: number;
  error: number;
  totalCrawled: number;
  crawlRate: number; // items per minute
}

export function StatusMonitor() {
  const [metrics, setMetrics] = useState<StatusMetrics>({
    total: 3231,
    active: 1247,
    inactive: 1856,
    pending: 89,
    error: 39,
    totalCrawled: 1547892,
    crawlRate: 2456
  });

  // TODO: Connect to WebSocket for real-time updates
  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalCrawled: prev.totalCrawled + Math.floor(Math.random() * 100),
        crawlRate: 2400 + Math.floor(Math.random() * 200)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const stats = [
    {
      label: 'Active',
      value: metrics.active,
      icon: Activity,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10'
    },
    {
      label: 'Inactive',
      value: metrics.inactive,
      icon: Clock,
      color: 'text-gray-500',
      bgColor: 'bg-gray-500/10'
    },
    {
      label: 'Pending',
      value: metrics.pending,
      icon: AlertCircle,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10'
    },
    {
      label: 'Errors',
      value: metrics.error,
      icon: AlertCircle,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10'
    }
  ];

  return (
    <div className="space-y-4">
      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{stat.label}</span>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
              </div>
            </div>
            <p className="text-2xl font-bold">{stat.value.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">
              {((stat.value / metrics.total) * 100).toFixed(1)}% of total
            </p>
          </Card>
        ))}
      </div>

      {/* Real-time Metrics */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Real-time Metrics</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Crawled */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-500">Total Items Crawled</span>
            </div>
            <p className="text-3xl font-bold text-blue-500">
              {metrics.totalCrawled.toLocaleString()}
            </p>
          </div>

          {/* Crawl Rate */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <span className="text-sm text-gray-500">Crawl Rate</span>
            </div>
            <p className="text-3xl font-bold text-green-500">
              {metrics.crawlRate.toLocaleString()}
              <span className="text-sm text-gray-500 ml-2">items/min</span>
            </p>
          </div>

          {/* Health Score */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-purple-500" />
              <span className="text-sm text-gray-500">System Health</span>
            </div>
            <div className="flex items-center gap-2">
              <p className="text-3xl font-bold text-purple-500">
                {(((metrics.active + metrics.inactive) / metrics.total) * 100).toFixed(1)}%
              </p>
              <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
                Healthy
              </Badge>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
            <span>Active Crawlers</span>
            <span>{metrics.active} / {metrics.total}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(metrics.active / metrics.total) * 100}%` }}
            />
          </div>
        </div>
      </Card>
    </div>
  );
}
