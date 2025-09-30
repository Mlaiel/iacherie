/**
 * Performance Chart - Real-Time Analytics Visualization
 * 
 * Interactive chart component for real-time performance data
 * Uses Recharts for responsive visualizations
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline';

interface ChartDataPoint {
  time: string;
  viewers: number;
  revenue: number;
  engagement: number;
}

export function PerformanceChart() {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [chartType, setChartType] = useState<'line' | 'area'>('area');
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('1h');

  useEffect(() => {
    // Initialize with some historical data
    const initialData: ChartDataPoint[] = [];
    const now = new Date();
    
    for (let i = 20; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 3 * 60000); // 3-minute intervals
      initialData.push({
        time: time.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        viewers: Math.floor(Math.random() * 100) + 50,
        revenue: Math.random() * 20 + 10,
        engagement: Math.floor(Math.random() * 100) + 30
      });
    }
    
    setChartData(initialData);

    // Simulate real-time updates
    const interval = setInterval(() => {
      const now = new Date();
      const newDataPoint: ChartDataPoint = {
        time: now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        viewers: Math.floor(Math.random() * 100) + 50,
        revenue: Math.random() * 20 + 10,
        engagement: Math.floor(Math.random() * 100) + 30
      };

      setChartData(prev => [...prev.slice(1), newDataPoint]); // Keep last 21 points
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{`Heure: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className={`text-sm text-${entry.color === '#8884d8' ? 'blue' : entry.color === '#82ca9d' ? 'green' : 'purple'}-600`}>
              {entry.name}: {entry.name === 'Revenue' ? `€${entry.value.toFixed(2)}` : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <ChartBarIcon className="h-6 w-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Performance en Temps Réel</h3>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Time Range Selector */}
          <div className="flex items-center space-x-2">
            <ClockIcon className="h-4 w-4 text-gray-500" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as '1h' | '6h' | '24h')}
              className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1h">1 heure</option>
              <option value="6h">6 heures</option>
              <option value="24h">24 heures</option>
            </select>
          </div>

          {/* Chart Type Toggle */}
          <div className="flex rounded-md overflow-hidden border border-gray-300">
            <button
              onClick={() => setChartType('area')}
              className={`px-3 py-1 text-xs font-medium ${
                chartType === 'area'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Area
            </button>
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1 text-xs font-medium ${
                chartType === 'line'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Line
            </button>
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'area' ? (
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                tickMargin={8}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tickMargin={8}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="viewers"
                stackId="1"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.6}
                name="Viewers"
              />
              <Area
                type="monotone"
                dataKey="engagement"
                stackId="2"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.6}
                name="Engagement"
              />
            </AreaChart>
          ) : (
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                tickMargin={8}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tickMargin={8}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="viewers"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                name="Viewers"
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                name="Revenue"
              />
              <Line
                type="monotone"
                dataKey="engagement"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                name="Engagement"
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-xs text-gray-500">Viewers Actuels</div>
          <div className="text-lg font-semibold text-blue-600">
            {chartData.length > 0 ? chartData[chartData.length - 1].viewers : 0}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Revenus/h</div>
          <div className="text-lg font-semibold text-green-600">
            €{chartData.length > 0 ? chartData[chartData.length - 1].revenue.toFixed(2) : '0.00'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Engagement</div>
          <div className="text-lg font-semibold text-purple-600">
            {chartData.length > 0 ? chartData[chartData.length - 1].engagement : 0}%
          </div>
        </div>
      </div>
    </div>
  );
}