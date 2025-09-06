/**
 * @fileoverview Revenue Engine - Core revenue management and tracking
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { RevenueStream } from '@/core/types';
import { MONETIZATION_CONSTANTS } from '@/core/constants';
import { RevenueType, Currency, PaymentStatus } from '@/core/enums';

interface RevenueEngineProps {
  onRevenueUpdate?: (revenue: RevenueStream) => void;
  onRevenueCreate?: (revenue: Partial<RevenueStream>) => void;
  className?: string;
}

export const RevenueEngine: React.FC<RevenueEngineProps> = ({
  onRevenueUpdate,
  onRevenueCreate,
  className = '',
}) => {
  const [revenueStreams, setRevenueStreams] = useState<RevenueStream[]>([]);
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [monthlyGrowth, setMonthlyGrowth] = useState(0);
  const [loading, setLoading] = useState(false);

  // Calculate metrics
  const calculateMetrics = useCallback(() => {
    const active = revenueStreams.filter(stream => stream.status === 'active');
    const total = active.reduce((sum, stream) => sum + stream.amount, 0);
    setTotalRevenue(total);

    // Simulate growth calculation
    setMonthlyGrowth(Math.random() * 20 - 5); // -5% to +15%
  }, [revenueStreams]);

  useEffect(() => {
    calculateMetrics();
  }, [calculateMetrics]);

  const createRevenueStream = useCallback(async (type: string, amount: number) => {
    setLoading(true);
    try {
      const newStream: RevenueStream = {
        id: `revenue_${Date.now()}`,
        contentId: 'sample_content',
        type: type as any,
        amount,
        currency: Currency.USD,
        frequency: type === 'subscription' ? 'monthly' : 'one-time',
        status: 'active',
      };

      setRevenueStreams(prev => [...prev, newStream]);
      onRevenueCreate?.(newStream);
    } catch (error) {
      console.error('Failed to create revenue stream:', error);
    } finally {
      setLoading(false);
    }
  }, [onRevenueCreate]);

  const updateRevenueStream = useCallback(async (id: string, updates: Partial<RevenueStream>) => {
    setLoading(true);
    try {
      setRevenueStreams(prev =>
        prev.map(stream =>
          stream.id === id ? { ...stream, ...updates } : stream
        )
      );
      
      const updatedStream = revenueStreams.find(s => s.id === id);
      if (updatedStream) {
        onRevenueUpdate?.({ ...updatedStream, ...updates });
      }
    } catch (error) {
      console.error('Failed to update revenue stream:', error);
    } finally {
      setLoading(false);
    }
  }, [revenueStreams, onRevenueUpdate]);

  const formatCurrency = useCallback((amount: number, currency: Currency = Currency.USD) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);
  }, []);

  const getRevenueTypeIcon = (type: string) => {
    switch (type) {
      case 'subscription':
        return '👥';
      case 'one_time_purchase':
        return '🛒';
      case 'licensing':
        return '📄';
      case 'advertising':
        return '📺';
      default:
        return '💰';
    }
  };

  return (
    <div className={`revenue-engine ${className}`}>
      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(totalRevenue)}
              </p>
            </div>
            <div className="text-2xl">💰</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Streams</p>
              <p className="text-2xl font-bold text-gray-900">
                {revenueStreams.filter(s => s.status === 'active').length}
              </p>
            </div>
            <div className="text-2xl">🔄</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Growth</p>
              <p className={`text-2xl font-bold ${
                monthlyGrowth >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {monthlyGrowth >= 0 ? '+' : ''}{monthlyGrowth.toFixed(1)}%
              </p>
            </div>
            <div className="text-2xl">
              {monthlyGrowth >= 0 ? '📈' : '📉'}
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Types */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Quick Setup</h3>
          <p className="text-sm text-gray-500">Create new revenue streams</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['subscription', 'one_time_purchase', 'licensing', 'advertising'].map((type) => (
              <button
                key={type}
                onClick={() => createRevenueStream(type, 10)}
                disabled={loading}
                className="flex flex-col items-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors disabled:opacity-50"
              >
                <div className="text-2xl mb-2">{getRevenueTypeIcon(type)}</div>
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {type.replace('_', ' ')}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Revenue Streams List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Revenue Streams</h3>
          <p className="text-sm text-gray-500">Manage your income sources</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Frequency
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
              {revenueStreams.map((stream) => (
                <tr key={stream.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg mr-2">{getRevenueTypeIcon(stream.type)}</span>
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {stream.type.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(stream.amount, stream.currency as Currency)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                    {stream.frequency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stream.status === 'active' 
                        ? 'bg-green-100 text-green-800'
                        : stream.status === 'inactive'
                        ? 'bg-gray-100 text-gray-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {stream.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => updateRevenueStream(stream.id, { 
                        status: stream.status === 'active' ? 'inactive' : 'active' 
                      })}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      {stream.status === 'active' ? 'Pause' : 'Activate'}
                    </button>
                    <button
                      onClick={() => {
                        setRevenueStreams(prev => prev.filter(s => s.id !== stream.id));
                      }}
                      className="text-red-600 hover:text-red-900"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
              {revenueStreams.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No revenue streams yet. Create your first one above!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};