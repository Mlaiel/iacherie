/**
 * Revenue Charts - Visual revenue analytics and reporting
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  CurrencyDollarIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarDaysIcon,
  ArrowPathIcon,
  DocumentChartBarIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

interface RevenueData {
  month: string;
  total: number;
  youtube: number;
  spotify: number;
  licensing: number;
  directSales: number;
}

interface PlatformRevenue {
  platform: string;
  current: number;
  previous: number;
  growth: number;
  color: string;
}

const RevenueCharts: React.FC = () => {
  const [revenueData, setRevenueData] = React.useState<RevenueData[]>([]);
  const [platformData, setPlatformData] = React.useState<PlatformRevenue[]>([]);
  const [timeframe, setTimeframe] = React.useState<'6m' | '1y' | '2y'>('1y');
  const [loading, setLoading] = React.useState(true);
  const [totalRevenue, setTotalRevenue] = React.useState(0);
  const [monthlyGrowth, setMonthlyGrowth] = React.useState(0);

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const data: RevenueData[] = [
        { month: 'Jul 2023', total: 15420, youtube: 7200, spotify: 4800, licensing: 2200, directSales: 1220 },
        { month: 'Aug 2023', total: 16890, youtube: 7800, spotify: 5100, licensing: 2500, directSales: 1490 },
        { month: 'Sep 2023', total: 18230, youtube: 8400, spotify: 5400, licensing: 2700, directSales: 1730 },
        { month: 'Oct 2023', total: 19650, youtube: 9100, spotify: 5700, licensing: 2900, directSales: 1950 },
        { month: 'Nov 2023', total: 21100, youtube: 9800, spotify: 6000, licensing: 3100, directSales: 2200 },
        { month: 'Dec 2023', total: 23450, youtube: 10900, spotify: 6500, licensing: 3400, directSales: 2650 },
        { month: 'Jan 2024', total: 24580, youtube: 11200, spotify: 6800, licensing: 3600, directSales: 2980 }
      ];

      setRevenueData(data);
      setTotalRevenue(data[data.length - 1].total);
      
      // Calculate growth
      const currentMonth = data[data.length - 1].total;
      const previousMonth = data[data.length - 2].total;
      setMonthlyGrowth(((currentMonth - previousMonth) / previousMonth) * 100);

      setPlatformData([
        {
          platform: 'YouTube',
          current: 11200,
          previous: 10900,
          growth: 2.75,
          color: 'bg-red-500'
        },
        {
          platform: 'Spotify',
          current: 6800,
          previous: 6500,
          growth: 4.62,
          color: 'bg-green-500'
        },
        {
          platform: 'Licensing',
          current: 3600,
          previous: 3400,
          growth: 5.88,
          color: 'bg-blue-500'
        },
        {
          platform: 'Direct Sales',
          current: 2980,
          previous: 2650,
          growth: 12.45,
          color: 'bg-purple-500'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, [timeframe]);

  const maxRevenue = Math.max(...revenueData.map(d => d.total));

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Revenue Charts</h1>
            <p className="text-gray-600">Comprehensive revenue analytics and trends</p>
          </div>
          <div className="flex space-x-3">
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value as '6m' | '1y' | '2y')}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="6m">Last 6 Months</option>
              <option value="1y">Last Year</option>
              <option value="2y">Last 2 Years</option>
            </select>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center">
              <DocumentChartBarIcon className="h-5 w-5 mr-2" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Current Month Revenue</p>
              <p className="text-2xl font-bold text-gray-900">${totalRevenue.toLocaleString()}</p>
              <div className="flex items-center mt-1">
                {monthlyGrowth >= 0 ? (
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm ml-1 ${monthlyGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {monthlyGrowth >= 0 ? '+' : ''}{monthlyGrowth.toFixed(1)}%
                </span>
              </div>
            </div>
            <CurrencyDollarIcon className="h-12 w-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">YTD Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                ${revenueData.slice(-12).reduce((sum, d) => sum + d.total, 0).toLocaleString()}
              </p>
            </div>
            <BanknotesIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Monthly Growth</p>
              <p className="text-2xl font-bold text-gray-900">+8.2%</p>
            </div>
            <ArrowTrendingUpIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Best Month</p>
              <p className="text-lg font-bold text-gray-900">Jan 2024</p>
              <p className="text-sm text-gray-500">${totalRevenue.toLocaleString()}</p>
            </div>
            <CalendarDaysIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Trend Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Revenue Trend</h3>
            <button className="text-gray-400 hover:text-gray-600">
              <ArrowPathIcon className="h-5 w-5" />
            </button>
          </div>

          <div className="h-80 flex items-end justify-between space-x-2">
            {revenueData.map((data, index) => (
              <div key={index} className="flex flex-col items-center flex-1 group">
                <div
                  className="bg-gradient-to-t from-blue-500 to-blue-400 rounded-t w-full min-h-[20px] hover:from-blue-600 hover:to-blue-500 transition-colors cursor-pointer relative"
                  style={{ height: `${(data.total / maxRevenue) * 100}%` }}
                >
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    ${data.total.toLocaleString()}
                  </div>
                </div>
                <span className="text-xs text-gray-600 mt-2 transform -rotate-45 origin-left whitespace-nowrap">
                  {data.month}
                </span>
              </div>
            ))}
          </div>

          {/* Revenue breakdown for latest month */}
          <div className="mt-6 pt-6 border-t">
            <h4 className="font-medium text-gray-900 mb-3">Current Month Breakdown</h4>
            <div className="space-y-2">
              {[
                { name: 'YouTube', value: revenueData[revenueData.length - 1]?.youtube || 0, color: 'bg-red-500' },
                { name: 'Spotify', value: revenueData[revenueData.length - 1]?.spotify || 0, color: 'bg-green-500' },
                { name: 'Licensing', value: revenueData[revenueData.length - 1]?.licensing || 0, color: 'bg-blue-500' },
                { name: 'Direct Sales', value: revenueData[revenueData.length - 1]?.directSales || 0, color: 'bg-purple-500' }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded ${item.color}`}></div>
                    <span className="text-sm text-gray-700">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    ${item.value.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Platform Performance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Platform Performance</h3>

          <div className="space-y-6">
            {platformData.map((platform, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded ${platform.color}`}></div>
                    <span className="font-medium text-gray-900">{platform.platform}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      ${platform.current.toLocaleString()}
                    </div>
                    <div className={`text-sm flex items-center ${
                      platform.growth >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {platform.growth >= 0 ? (
                        <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-3 w-3 mr-1" />
                      )}
                      {platform.growth >= 0 ? '+' : ''}{platform.growth}%
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${platform.color}`}
                    style={{ width: `${(platform.current / totalRevenue) * 100}%` }}
                  ></div>
                </div>

                <div className="flex justify-between text-xs text-gray-500">
                  <span>
                    Previous: ${platform.previous.toLocaleString()}
                  </span>
                  <span>
                    {((platform.current / totalRevenue) * 100).toFixed(1)}% of total
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Growth Summary */}
          <div className="mt-6 pt-6 border-t">
            <h4 className="font-medium text-gray-900 mb-3">Growth Summary</h4>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <div className="flex items-center">
                <ArrowTrendingUpIcon className="h-5 w-5 text-green-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-green-800">
                    Strong growth across all platforms
                  </p>
                  <p className="text-xs text-green-600">
                    Direct Sales leading with +12.45% growth
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Projections */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Revenue Projections</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Next Month Forecast</h4>
            <p className="text-2xl font-bold text-blue-600">
              ${Math.round(totalRevenue * 1.05).toLocaleString()}
            </p>
            <p className="text-sm text-gray-600">+5% projected growth</p>
          </div>

          <div className="text-center p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Quarterly Target</h4>
            <p className="text-2xl font-bold text-green-600">
              ${Math.round(totalRevenue * 3 * 1.08).toLocaleString()}
            </p>
            <p className="text-sm text-gray-600">8% growth target</p>
          </div>

          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Annual Goal</h4>
            <p className="text-2xl font-bold text-purple-600">
              ${Math.round(totalRevenue * 12 * 1.15).toLocaleString()}
            </p>
            <p className="text-sm text-gray-600">15% annual growth</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RevenueCharts;