/**
 * Monetization Panel - Revenue management and monetization settings
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  CurrencyDollarIcon, 
  CreditCardIcon,
  ChartBarIcon,
  GlobeAltIcon,
  CogIcon,
  PlusIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

interface RevenueStream {
  id: string;
  platform: string;
  type: 'subscription' | 'ads' | 'licensing' | 'direct';
  monthlyRevenue: number;
  growth: number;
  status: 'active' | 'pending' | 'inactive';
}

interface PaymentMethod {
  id: string;
  type: 'bank' | 'paypal' | 'crypto';
  name: string;
  details: string;
  isDefault: boolean;
  status: 'verified' | 'pending' | 'failed';
}

const MonetizationPanel: React.FC = () => {
  const [revenueStreams, setRevenueStreams] = React.useState<RevenueStream[]>([]);
  const [paymentMethods, setPaymentMethods] = React.useState<PaymentMethod[]>([]);
  const [totalRevenue, setTotalRevenue] = React.useState(0);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate API calls
    setTimeout(() => {
      const streams = [
        {
          id: '1',
          platform: 'YouTube',
          type: 'ads' as const,
          monthlyRevenue: 8500,
          growth: 15.2,
          status: 'active' as const
        },
        {
          id: '2',
          platform: 'Spotify',
          type: 'subscription' as const,
          monthlyRevenue: 6200,
          growth: 8.7,
          status: 'active' as const
        },
        {
          id: '3',
          platform: 'Direct Licensing',
          type: 'licensing' as const,
          monthlyRevenue: 4500,
          growth: 22.1,
          status: 'active' as const
        },
        {
          id: '4',
          platform: 'Patreon',
          type: 'direct' as const,
          monthlyRevenue: 3200,
          growth: -2.3,
          status: 'active' as const
        }
      ];

      setRevenueStreams(streams);
      setTotalRevenue(streams.reduce((sum, stream) => sum + stream.monthlyRevenue, 0));

      setPaymentMethods([
        {
          id: '1',
          type: 'bank',
          name: 'Chase Bank',
          details: '****1234',
          isDefault: true,
          status: 'verified'
        },
        {
          id: '2',
          type: 'paypal',
          name: 'PayPal',
          details: 'user@example.com',
          isDefault: false,
          status: 'verified'
        },
        {
          id: '3',
          type: 'crypto',
          name: 'Bitcoin Wallet',
          details: '3J98t...5JKZ',
          isDefault: false,
          status: 'pending'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

  const getStreamTypeIcon = (type: string) => {
    switch (type) {
      case 'ads': return <ChartBarIcon className="h-6 w-6 text-red-500" />;
      case 'subscription': return <CreditCardIcon className="h-6 w-6 text-blue-500" />;
      case 'licensing': return <GlobeAltIcon className="h-6 w-6 text-green-500" />;
      case 'direct': return <BanknotesIcon className="h-6 w-6 text-purple-500" />;
      default: return <CurrencyDollarIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getPaymentIcon = (type: string) => {
    switch (type) {
      case 'bank': return <BanknotesIcon className="h-6 w-6 text-blue-500" />;
      case 'paypal': return <CreditCardIcon className="h-6 w-6 text-blue-600" />;
      case 'crypto': return <CurrencyDollarIcon className="h-6 w-6 text-orange-500" />;
      default: return <CreditCardIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'verified': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Monetization Panel</h1>
            <p className="text-gray-600">Manage your revenue streams and payment settings</p>
          </div>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors flex items-center">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Revenue Stream
          </button>
        </div>
      </div>

      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">${totalRevenue.toLocaleString()}</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-600 ml-1">+12.8%</span>
              </div>
            </div>
            <CurrencyDollarIcon className="h-12 w-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Streams</p>
              <p className="text-2xl font-bold text-gray-900">{revenueStreams.filter(s => s.status === 'active').length}</p>
            </div>
            <ChartBarIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Best Performing</p>
              <p className="text-lg font-bold text-gray-900">
                {revenueStreams.sort((a, b) => b.monthlyRevenue - a.monthlyRevenue)[0]?.platform}
              </p>
              <p className="text-sm text-gray-500">
                ${revenueStreams.sort((a, b) => b.monthlyRevenue - a.monthlyRevenue)[0]?.monthlyRevenue.toLocaleString()}
              </p>
            </div>
            <ArrowTrendingUpIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average Growth</p>
              <p className="text-2xl font-bold text-gray-900">
                {(revenueStreams.reduce((sum, s) => sum + s.growth, 0) / revenueStreams.length).toFixed(1)}%
              </p>
            </div>
            <ChartBarIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Revenue Streams */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Revenue Streams</h3>
            <button className="text-green-600 hover:text-green-700 text-sm font-medium">
              Optimize Streams
            </button>
          </div>

          <div className="space-y-4">
            {revenueStreams.map((stream) => (
              <div key={stream.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    {getStreamTypeIcon(stream.type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{stream.platform}</h4>
                      <p className="text-sm text-gray-500 capitalize">{stream.type}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(stream.status)}`}>
                    {stream.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <span className="text-sm text-gray-600">Monthly Revenue</span>
                    <div className="font-semibold text-lg text-gray-900">
                      ${stream.monthlyRevenue.toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Growth</span>
                    <div className={`font-semibold text-lg flex items-center ${
                      stream.growth >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stream.growth >= 0 ? '+' : ''}{stream.growth}%
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View Details
                  </button>
                  <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                    Configure
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Payment Methods</h3>
            <button className="text-green-600 hover:text-green-700 text-sm font-medium">
              Add Payment Method
            </button>
          </div>

          <div className="space-y-4">
            {paymentMethods.map((method) => (
              <div key={method.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    {getPaymentIcon(method.type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{method.name}</h4>
                      <p className="text-sm text-gray-500">{method.details}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {method.isDefault && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        DEFAULT
                      </span>
                    )}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(method.status)}`}>
                      {method.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  {!method.isDefault && method.status === 'verified' && (
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      Set as Default
                    </button>
                  )}
                  <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                    Edit
                  </button>
                  {!method.isDefault && (
                    <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                      Remove
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Payment Schedule */}
          <div className="mt-6 pt-6 border-t">
            <h4 className="font-medium text-gray-900 mb-3">Payment Schedule</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p>• Monthly payouts on the 15th of each month</p>
              <p>• Minimum payout threshold: $100</p>
              <p>• Processing time: 3-5 business days</p>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-6">
          <CogIcon className="h-6 w-6 text-gray-600 mr-3" />
          <h3 className="text-lg font-semibold text-gray-900">Monetization Settings</h3>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Revenue Sharing</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span className="text-sm text-gray-700">Enable platform revenue sharing</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span className="text-sm text-gray-700">Auto-optimize ad placements</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                <span className="text-sm text-gray-700">Premium content subscriptions</span>
              </label>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Tax Settings</h4>
            <div className="space-y-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tax Country</label>
                <select className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm">
                  <option>United States</option>
                  <option>United Kingdom</option>
                  <option>Germany</option>
                  <option>Canada</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tax ID</label>
                <input 
                  type="text" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  placeholder="Enter tax ID"
                />
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Notifications</h4>
            <div className="space-y-2">
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span className="text-sm text-gray-700">Revenue milestone alerts</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span className="text-sm text-gray-700">Payment confirmations</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                <span className="text-sm text-gray-700">Monthly revenue reports</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonetizationPanel;