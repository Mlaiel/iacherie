/**
 * Monetization - Revenue management and monetization interface
 * 
 * Comprehensive monetization dashboard with revenue tracking,
 * payment methods, subscription management, and financial analytics
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  CurrencyDollarIcon,
  CreditCardIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  ChartBarIcon,
  GiftIcon,
  UserGroupIcon,
  StarIcon,
  CheckCircleIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  ArrowPathIcon,
  EyeIcon,
  PlayIcon,
  HeartIcon,
  ShareIcon,
  CogIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

export interface RevenueStream {
  id: string;
  name: string;
  type: 'subscription' | 'ads' | 'sponsorship' | 'merchandise' | 'tips' | 'licensing';
  amount: number;
  currency: string;
  period: 'monthly' | 'weekly' | 'daily' | 'one-time';
  status: 'active' | 'paused' | 'pending' | 'cancelled';
  growth: number;
  lastPayment: Date;
  platform?: string;
}

export interface PaymentMethod {
  id: string;
  type: 'bank_account' | 'credit_card' | 'paypal' | 'crypto' | 'wire';
  name: string;
  details: string;
  isDefault: boolean;
  status: 'active' | 'pending' | 'expired' | 'suspended';
  addedAt: Date;
}

export interface Transaction {
  id: string;
  amount: number;
  currency: string;
  type: 'earning' | 'payout' | 'fee' | 'refund';
  description: string;
  platform: string;
  status: 'completed' | 'pending' | 'failed' | 'cancelled';
  date: Date;
  reference?: string;
}

export interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  currency: string;
  period: string;
  features: string[];
  subscribers: number;
  revenue: number;
  isPopular?: boolean;
}

export interface MonetizationProps {
  revenueStreams?: RevenueStream[];
  paymentMethods?: PaymentMethod[];
  transactions?: Transaction[];
  subscriptionTiers?: SubscriptionTier[];
  onSetupPayment?: (method: Partial<PaymentMethod>) => void;
  onCreateTier?: (tier: Partial<SubscriptionTier>) => void;
  onRequestPayout?: (amount: number, methodId: string) => void;
  onUpdateSettings?: (settings: any) => void;
  className?: string;
}

const revenueTypes = {
  subscription: { name: 'Subscriptions', icon: UserGroupIcon, color: 'blue' },
  ads: { name: 'Ad Revenue', icon: EyeIcon, color: 'green' },
  sponsorship: { name: 'Sponsorships', icon: StarIcon, color: 'purple' },
  merchandise: { name: 'Merchandise', icon: GiftIcon, color: 'orange' },
  tips: { name: 'Tips & Donations', icon: HeartIcon, color: 'red' },
  licensing: { name: 'Licensing', icon: CreditCardIcon, color: 'indigo' }
};

const paymentTypeIcons = {
  bank_account: BanknotesIcon,
  credit_card: CreditCardIcon,
  paypal: CurrencyDollarIcon,
  crypto: CurrencyDollarIcon,
  wire: BanknotesIcon
};

const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

const formatPercentage = (value: number): string => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
};

const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);

  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  return `${diffMonths}mo ago`;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': case 'completed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'paused': case 'suspended': return 'bg-gray-100 text-gray-800';
    case 'cancelled': case 'failed': case 'expired': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export const Monetization: React.FC<MonetizationProps> = ({
  revenueStreams = [],
  paymentMethods = [],
  transactions = [],
  subscriptionTiers = [],
  onSetupPayment,
  onCreateTier,
  onRequestPayout,
  onUpdateSettings,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'revenue' | 'payments' | 'tiers' | 'analytics'>('overview');
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showTierModal, setShowTierModal] = useState(false);
  const [totalEarnings, setTotalEarnings] = useState(0);

  // Mock data
  const defaultRevenueStreams: RevenueStream[] = [
    {
      id: '1',
      name: 'Premium Subscriptions',
      type: 'subscription',
      amount: 4250,
      currency: 'USD',
      period: 'monthly',
      status: 'active',
      growth: 12.5,
      lastPayment: new Date(Date.now() - 86400000),
      platform: 'YouTube'
    },
    {
      id: '2',
      name: 'YouTube Ad Revenue',
      type: 'ads',
      amount: 1890,
      currency: 'USD',
      period: 'monthly',
      status: 'active',
      growth: 8.3,
      lastPayment: new Date(Date.now() - 172800000),
      platform: 'YouTube'
    },
    {
      id: '3',
      name: 'Brand Sponsorships',
      type: 'sponsorship',
      amount: 2500,
      currency: 'USD',
      period: 'monthly',
      status: 'active',
      growth: 25.7,
      lastPayment: new Date(Date.now() - 604800000),
      platform: 'Instagram'
    },
    {
      id: '4',
      name: 'Merchandise Sales',
      type: 'merchandise',
      amount: 850,
      currency: 'USD',
      period: 'monthly',
      status: 'active',
      growth: -5.2,
      lastPayment: new Date(Date.now() - 86400000)
    }
  ];

  const defaultPaymentMethods: PaymentMethod[] = [
    {
      id: '1',
      type: 'bank_account',
      name: 'Primary Bank Account',
      details: '****1234',
      isDefault: true,
      status: 'active',
      addedAt: new Date(Date.now() - 2592000000)
    },
    {
      id: '2',
      type: 'paypal',
      name: 'PayPal Account',
      details: 'user@example.com',
      isDefault: false,
      status: 'active',
      addedAt: new Date(Date.now() - 1296000000)
    }
  ];

  const defaultTransactions: Transaction[] = [
    {
      id: '1',
      amount: 4250,
      currency: 'USD',
      type: 'earning',
      description: 'Premium Subscriptions - January',
      platform: 'YouTube',
      status: 'completed',
      date: new Date(Date.now() - 86400000)
    },
    {
      id: '2',
      amount: 3800,
      currency: 'USD',
      type: 'payout',
      description: 'Monthly Payout',
      platform: 'Platform',
      status: 'completed',
      date: new Date(Date.now() - 172800000)
    },
    {
      id: '3',
      amount: 2500,
      currency: 'USD',
      type: 'earning',
      description: 'Brand Partnership - TechCorp',
      platform: 'Instagram',
      status: 'pending',
      date: new Date(Date.now() - 259200000)
    }
  ];

  const defaultTiers: SubscriptionTier[] = [
    {
      id: '1',
      name: 'Essential',
      price: 9.99,
      currency: 'USD',
      period: 'month',
      features: ['Ad-free content', 'Early access', 'Standard support'],
      subscribers: 1250,
      revenue: 12487.50
    },
    {
      id: '2',
      name: 'Premium',
      price: 19.99,
      currency: 'USD',
      period: 'month',
      features: ['All Essential features', 'Exclusive content', 'Priority support', '1-on-1 sessions'],
      subscribers: 680,
      revenue: 13592.32,
      isPopular: true
    },
    {
      id: '3',
      name: 'VIP',
      price: 49.99,
      currency: 'USD',
      period: 'month',
      features: ['All Premium features', 'Custom content', 'Direct messaging', 'Merchandise'],
      subscribers: 125,
      revenue: 6248.75
    }
  ];

  const displayStreams = revenueStreams.length > 0 ? revenueStreams : defaultRevenueStreams;
  const displayPayments = paymentMethods.length > 0 ? paymentMethods : defaultPaymentMethods;
  const displayTransactions = transactions.length > 0 ? transactions : defaultTransactions;
  const displayTiers = subscriptionTiers.length > 0 ? subscriptionTiers : defaultTiers;

  // Calculate totals
  useEffect(() => {
    const total = displayStreams.reduce((sum, stream) => sum + stream.amount, 0);
    setTotalEarnings(total);
  }, [displayStreams]);

  const monthlyRevenue = displayStreams
    .filter(stream => stream.period === 'monthly')
    .reduce((sum, stream) => sum + stream.amount, 0);

  const pendingPayouts = displayTransactions
    .filter(tx => tx.type === 'payout' && tx.status === 'pending')
    .reduce((sum, tx) => sum + tx.amount, 0);

  const totalSubscribers = displayTiers.reduce((sum, tier) => sum + tier.subscribers, 0);

  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md border p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CurrencyDollarIcon className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Monetization Center</h1>
              <p className="text-gray-600">Manage your revenue streams and financial settings</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => onRequestPayout?.(monthlyRevenue, displayPayments[0]?.id)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
            >
              <BanknotesIcon className="w-4 h-4" />
              <span>Request Payout</span>
            </button>
            <button
              onClick={() => setShowPaymentModal(true)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
            >
              <PlusIcon className="w-4 h-4" />
              <span>Add Payment</span>
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Earnings</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalEarnings)}</p>
              <div className="flex items-center space-x-1 mt-1">
                <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-600">+12.3% this month</span>
              </div>
            </div>
            <CurrencyDollarIcon className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(monthlyRevenue)}</p>
              <div className="flex items-center space-x-1 mt-1">
                <ArrowTrendingUpIcon className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-blue-600">+8.7% vs last month</span>
              </div>
            </div>
            <ChartBarIcon className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Payouts</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(pendingPayouts)}</p>
              <p className="text-sm text-gray-500 mt-1">Processing in 1-3 days</p>
            </div>
            <ArrowPathIcon className="w-8 h-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Subscribers</p>
              <p className="text-2xl font-bold text-gray-900">{totalSubscribers.toLocaleString()}</p>
              <div className="flex items-center space-x-1 mt-1">
                <ArrowTrendingUpIcon className="w-4 h-4 text-purple-500" />
                <span className="text-sm text-purple-600">+15.2% this month</span>
              </div>
            </div>
            <UserGroupIcon className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow-md border">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'revenue', name: 'Revenue Streams', icon: CurrencyDollarIcon },
              { id: 'payments', name: 'Payment Methods', icon: CreditCardIcon },
              { id: 'tiers', name: 'Subscription Tiers', icon: StarIcon },
              { id: 'analytics', name: 'Analytics', icon: ArrowTrendingUpIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Revenue Breakdown */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Breakdown</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(revenueTypes).map(([type, config]) => {
                    const streams = displayStreams.filter(s => s.type === type);
                    const total = streams.reduce((sum, s) => sum + s.amount, 0);
                    if (total === 0) return null;

                    return (
                      <div key={type} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <config.icon className={`w-5 h-5 text-${config.color}-500`} />
                            <span className="font-medium text-gray-900">{config.name}</span>
                          </div>
                          <span className="text-lg font-bold text-gray-900">{formatCurrency(total)}</span>
                        </div>
                        <div className="space-y-1">
                          {streams.map(stream => (
                            <div key={stream.id} className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">{stream.name}</span>
                              <div className="flex items-center space-x-2">
                                <span className="text-gray-900">{formatCurrency(stream.amount)}</span>
                                <span className={`text-xs ${stream.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {formatPercentage(stream.growth)}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Recent Transactions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
                <div className="space-y-3">
                  {displayTransactions.slice(0, 5).map((transaction) => (
                    <div key={transaction.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          transaction.type === 'earning' ? 'bg-green-500' :
                          transaction.type === 'payout' ? 'bg-blue-500' :
                          transaction.type === 'fee' ? 'bg-red-500' : 'bg-gray-500'
                        }`} />
                        <div>
                          <p className="font-medium text-gray-900">{transaction.description}</p>
                          <p className="text-sm text-gray-500">{transaction.platform} • {formatTimeAgo(transaction.date)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-medium ${
                          transaction.type === 'earning' ? 'text-green-600' :
                          transaction.type === 'payout' ? 'text-blue-600' : 'text-red-600'
                        }`}>
                          {transaction.type === 'earning' ? '+' : '-'}{formatCurrency(transaction.amount)}
                        </p>
                        <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(transaction.status)}`}>
                          {transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Revenue Streams Tab */}
          {activeTab === 'revenue' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Revenue Streams</h3>
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2">
                  <PlusIcon className="w-4 h-4" />
                  <span>Add Stream</span>
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Revenue Stream
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Growth
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {displayStreams.map((stream) => {
                      const config = revenueTypes[stream.type];
                      return (
                        <tr key={stream.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <config.icon className={`w-5 h-5 text-${config.color}-500 mr-3`} />
                              <div>
                                <div className="text-sm font-medium text-gray-900">{stream.name}</div>
                                <div className="text-sm text-gray-500">{stream.platform}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm text-gray-900">{config.name}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{formatCurrency(stream.amount)}</div>
                            <div className="text-sm text-gray-500">per {stream.period}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className={`flex items-center space-x-1 ${
                              stream.growth >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {stream.growth >= 0 ? 
                                <ArrowTrendingUpIcon className="w-4 h-4" /> : 
                                <ArrowTrendingDownIcon className="w-4 h-4" />
                              }
                              <span className="text-sm font-medium">{formatPercentage(stream.growth)}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(stream.status)}`}>
                              {stream.status.charAt(0).toUpperCase() + stream.status.slice(1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button className="text-green-600 hover:text-green-900 mr-3">
                              Configure
                            </button>
                            <button className="text-red-600 hover:text-red-900">
                              Disable
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Payment Methods Tab */}
          {activeTab === 'payments' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Payment Methods</h3>
                <button
                  onClick={() => setShowPaymentModal(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
                >
                  <PlusIcon className="w-4 h-4" />
                  <span>Add Payment Method</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {displayPayments.map((method) => {
                  const IconComponent = paymentTypeIcons[method.type];
                  return (
                    <div key={method.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-gray-100 rounded-lg">
                            <IconComponent className="w-6 h-6 text-gray-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{method.name}</h4>
                            <p className="text-sm text-gray-500">{method.details}</p>
                          </div>
                        </div>
                        {method.isDefault && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                            Default
                          </span>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(method.status)}`}>
                            {method.status.charAt(0).toUpperCase() + method.status.slice(1)}
                          </span>
                          <span className="text-sm text-gray-500">Added {formatTimeAgo(method.addedAt)}</span>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-blue-600 hover:text-blue-700 text-sm">
                            Edit
                          </button>
                          <button className="text-red-600 hover:text-red-700 text-sm">
                            Remove
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Subscription Tiers Tab */}
          {activeTab === 'tiers' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Subscription Tiers</h3>
                <button
                  onClick={() => setShowTierModal(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
                >
                  <PlusIcon className="w-4 h-4" />
                  <span>Create Tier</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {displayTiers.map((tier) => (
                  <div key={tier.id} className={`border-2 rounded-lg p-6 relative ${
                    tier.isPopular ? 'border-green-500' : 'border-gray-200'
                  }`}>
                    {tier.isPopular && (
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                        <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                          Most Popular
                        </span>
                      </div>
                    )}

                    <div className="text-center mb-6">
                      <h4 className="text-xl font-bold text-gray-900 mb-2">{tier.name}</h4>
                      <div className="text-3xl font-bold text-gray-900">
                        {formatCurrency(tier.price)}
                        <span className="text-lg font-normal text-gray-500">/{tier.period}</span>
                      </div>
                    </div>

                    <ul className="space-y-3 mb-6">
                      {tier.features.map((feature, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <CheckCircleIcon className="w-5 h-5 text-green-500" />
                          <span className="text-sm text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>Subscribers</span>
                        <span className="font-medium">{tier.subscribers.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                        <span>Monthly Revenue</span>
                        <span className="font-medium">{formatCurrency(tier.revenue)}</span>
                      </div>

                      <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        Edit Tier
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Revenue Analytics</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-lg p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Revenue by Platform</h4>
                  <div className="space-y-4">
                    {['YouTube', 'Instagram', 'TikTok', 'Spotify'].map((platform, index) => {
                      const revenue = [4250, 2890, 1650, 980][index];
                      const percentage = (revenue / 9770) * 100;
                      return (
                        <div key={platform} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">{platform}</span>
                          <div className="flex items-center space-x-3">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-900">{formatCurrency(revenue)}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Growth Trends</h4>
                  <div className="space-y-4">
                    {[
                      { metric: 'Subscription Growth', value: '+12.5%', color: 'text-green-600' },
                      { metric: 'Average Revenue per User', value: '+$4.20', color: 'text-blue-600' },
                      { metric: 'Churn Rate', value: '-2.1%', color: 'text-green-600' },
                      { metric: 'Monthly Recurring Revenue', value: '+$890', color: 'text-green-600' }
                    ].map((item) => (
                      <div key={item.metric} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">{item.metric}</span>
                        <span className={`text-sm font-medium ${item.color}`}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Monetization;