'use client';

import { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

interface RevenueData {
  month: string;
  revenue: number;
  growth: number;
}

export function RevenueChart() {
  const [data, setData] = useState<RevenueData[]>([]);
  const [viewType, setViewType] = useState<'line' | 'bar'>('line');

  useEffect(() => {
    // Mock revenue data
    const mockData: RevenueData[] = [
      { month: 'Jan', revenue: 18500, growth: 8.2 },
      { month: 'Feb', revenue: 19200, growth: 3.8 },
      { month: 'Mar', revenue: 21100, growth: 9.9 },
      { month: 'Apr', revenue: 20800, growth: -1.4 },
      { month: 'May', revenue: 22400, growth: 7.7 },
      { month: 'Jun', revenue: 24580, growth: 9.7 },
    ];
    setData(mockData);
  }, []);

  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Revenue Overview</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewType('line')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              viewType === 'line'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Line
          </button>
          <button
            onClick={() => setViewType('bar')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              viewType === 'bar'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Bar
          </button>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          {viewType === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="month" 
                axisLine={false}
                tickLine={false}
                className="text-gray-600"
              />
              <YAxis 
                tickFormatter={formatCurrency}
                axisLine={false}
                tickLine={false}
                className="text-gray-600"
              />
              <Tooltip
                formatter={[formatCurrency, 'Revenue']}
                labelStyle={{ color: '#374151' }}
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
              />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke="#2563eb" 
                strokeWidth={3}
                dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#2563eb' }}
              />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="month" 
                axisLine={false}
                tickLine={false}
                className="text-gray-600"
              />
              <YAxis 
                tickFormatter={formatCurrency}
                axisLine={false}
                tickLine={false}
                className="text-gray-600"
              />
              <Tooltip
                formatter={[formatCurrency, 'Revenue']}
                labelStyle={{ color: '#374151' }}
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
              />
              <Bar 
                dataKey="revenue" 
                fill="#2563eb" 
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">Total Revenue</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(data.reduce((sum, item) => sum + item.revenue, 0))}
          </p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">Average Growth</p>
          <p className="text-lg font-semibold text-green-600">
            {data.length > 0 ? (data.reduce((sum, item) => sum + item.growth, 0) / data.length).toFixed(1) : 0}%
          </p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">Best Month</p>
          <p className="text-lg font-semibold text-gray-900">
            {data.length > 0 ? data.reduce((max, item) => item.revenue > max.revenue ? item : max).month : 'N/A'}
          </p>
        </div>
      </div>
    </div>
  );
}