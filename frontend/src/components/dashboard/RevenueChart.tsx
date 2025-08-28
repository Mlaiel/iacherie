'use client';

import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  AreaChart,
  Area
} from 'recharts';

interface RevenueData {
  month: string;
  revenue: number;
  projectedRevenue: number;
  violations: number;
  recoveredRevenue: number;
}

const mockRevenueData: RevenueData[] = [
  { month: 'Jan', revenue: 18500, projectedRevenue: 20000, violations: 12, recoveredRevenue: 2800 },
  { month: 'Feb', revenue: 22000, projectedRevenue: 21000, violations: 8, recoveredRevenue: 3200 },
  { month: 'Mar', revenue: 19800, projectedRevenue: 19500, violations: 15, recoveredRevenue: 2400 },
  { month: 'Apr', revenue: 25600, projectedRevenue: 24000, violations: 6, recoveredRevenue: 4100 },
  { month: 'May', revenue: 28900, projectedRevenue: 26500, violations: 9, recoveredRevenue: 3800 },
  { month: 'Jun', revenue: 31200, projectedRevenue: 29000, violations: 4, recoveredRevenue: 5200 },
  { month: 'Jul', revenue: 33800, projectedRevenue: 32000, violations: 7, recoveredRevenue: 4600 },
  { month: 'Aug', revenue: 36500, projectedRevenue: 35000, violations: 3, recoveredRevenue: 6100 },
];

export function RevenueChart() {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Revenue Analytics</h3>
          <p className="text-sm text-gray-600">Monthly revenue tracking and violation recovery</p>
        </div>
        <div className="flex space-x-2">
          <button className="px-3 py-1 text-xs font-medium text-gray-500 bg-gray-100 rounded-md hover:bg-gray-200">
            6M
          </button>
          <button className="px-3 py-1 text-xs font-medium text-white bg-primary-600 rounded-md">
            1Y
          </button>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={mockRevenueData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="recoveredGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="month" 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip 
              formatter={(value: number, name: string) => {
                const formatValue = name.includes('Revenue') ? `$${value.toLocaleString()}` : value;
                return [formatValue, name];
              }}
              labelStyle={{ color: '#374151' }}
              contentStyle={{ 
                backgroundColor: '#ffffff', 
                border: '1px solid #e5e7eb', 
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#6366f1"
              fillOpacity={1}
              fill="url(#revenueGradient)"
              strokeWidth={2}
              name="Actual Revenue"
            />
            <Area
              type="monotone"
              dataKey="recoveredRevenue"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#recoveredGradient)"
              strokeWidth={2}
              name="Recovered Revenue"
            />
            <Line
              type="monotone"
              dataKey="projectedRevenue"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Projected Revenue"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Revenue Metrics Summary */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            ${(mockRevenueData[mockRevenueData.length - 1].revenue / 1000).toFixed(1)}k
          </div>
          <div className="text-sm text-gray-600">Current Month</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            ${mockRevenueData.reduce((sum, data) => sum + data.recoveredRevenue, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Recovered</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {mockRevenueData.reduce((sum, data) => sum + data.violations, 0)}
          </div>
          <div className="text-sm text-gray-600">Total Violations</div>
        </div>
      </div>
    </div>
  );
}