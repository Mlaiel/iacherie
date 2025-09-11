/**
 * Virtual Economy - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive virtual economy management with
 * currency tracking and transaction history.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { VirtualEconomyStats, ApiResponse } from '../types';
import { gamificationStyles } from '../gamification.styles';
import { CurrencyDollarIcon, ChartBarIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';

interface VirtualEconomyProps {
  userId: string;
  className?: string;
}

interface Transaction {
  id: string;
  type: 'earned' | 'spent';
  amount: number;
  description: string;
  timestamp: Date;
}

const VirtualEconomy: React.FC<VirtualEconomyProps> = ({ userId, className }) => {
  const [stats, setStats] = useState<VirtualEconomyStats | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchEconomyData = useCallback(async () => {
    try {
      setLoading(true);
      const [statsResponse, transactionsResponse] = await Promise.all([
        fetch(`/api/gamification/economy/stats?userId=${userId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        }),
        fetch(`/api/gamification/economy/transactions?userId=${userId}&limit=10`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
      ]);

      const [statsResult, transactionsResult] = await Promise.all([
        statsResponse.json() as Promise<ApiResponse<VirtualEconomyStats>>,
        transactionsResponse.json() as Promise<ApiResponse<Transaction[]>>
      ]);

      if (statsResult.success) setStats(statsResult.data!);
      if (transactionsResult.success) setTransactions(transactionsResult.data!);
    } catch (err) {
      console.error('Failed to fetch economy data:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchEconomyData();
  }, [fetchEconomyData]);

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols3}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-20 w-full"} />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <CurrencyDollarIcon className="w-8 h-8 mr-3 text-green-500" />
            Virtual Economy
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Track your virtual currency and economy participation
          </p>
        </div>

        {stats && (
          <>
            <div className={clsx(gamificationStyles.container.section, "mb-6")}>
              <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
                Economy Overview
              </h2>
              <div className={gamificationStyles.grid.cols3}>
                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Your Balance</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-green-600")}>
                    {stats.userSpendingPower.toLocaleString()}
                  </div>
                  <div className={gamificationStyles.typography.body.small}>Virtual coins</div>
                </div>

                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Daily Transactions</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-blue-600")}>
                    {stats.dailyTransactions.toLocaleString()}
                  </div>
                  <div className={gamificationStyles.typography.body.small}>Platform-wide</div>
                </div>

                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Economy Health</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-purple-600")}>
                    {stats.economyHealthScore.toFixed(1)}%
                  </div>
                  <div className={gamificationStyles.typography.body.small}>Health score</div>
                </div>
              </div>
            </div>

            <div className={clsx(gamificationStyles.container.section, "mb-6")}>
              <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
                Recent Transactions
              </h3>
              <div className="space-y-2">
                {transactions.map((transaction) => (
                  <div key={transaction.id} className={clsx(
                    gamificationStyles.container.compactCard,
                    "flex items-center justify-between"
                  )}>
                    <div className="flex items-center">
                      <div className={clsx(
                        "w-10 h-10 rounded-full flex items-center justify-center mr-3",
                        transaction.type === 'earned' ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"
                      )}>
                        {transaction.type === 'earned' ? '+' : '-'}
                      </div>
                      <div>
                        <div className={gamificationStyles.typography.body.regular}>
                          {transaction.description}
                        </div>
                        <div className={gamificationStyles.typography.body.small}>
                          {new Date(transaction.timestamp).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className={clsx(
                      gamificationStyles.typography.body.regular,
                      "font-bold",
                      transaction.type === 'earned' ? "text-green-600" : "text-red-600"
                    )}>
                      {transaction.type === 'earned' ? '+' : '-'}{transaction.amount.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VirtualEconomy;