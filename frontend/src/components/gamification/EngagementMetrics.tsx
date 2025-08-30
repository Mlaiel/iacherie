/**
 * Engagement Metrics - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive engagement analytics with
 * real-time metrics visualization and trend analysis.
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
import { EngagementMetrics, ApiResponse } from './types';
import { gamificationStyles } from './gamification.styles';
import { ChartBarIcon, UsersIcon, ClockIcon, TrendingUpIcon } from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import clsx from 'clsx';

interface EngagementMetricsProps {
  userId: string;
  className?: string;
  timeframe?: 'week' | 'month' | 'quarter' | 'year';
}

interface MetricsData {
  date: string;
  dailyActiveUsers: number;
  challengeCompletionRate: number;
  achievementUnlockRate: number;
  socialInteractionRate: number;
  sessionDuration: number;
}

const EngagementMetricsComponent: React.FC<EngagementMetricsProps> = ({
  userId,
  className,
  timeframe = 'month'
}) => {
  const [metrics, setMetrics] = useState<EngagementMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<MetricsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<keyof MetricsData>('dailyActiveUsers');

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const [currentResponse, historyResponse] = await Promise.all([
        fetch(`/api/gamification/metrics/engagement?userId=${userId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        }),
        fetch(`/api/gamification/metrics/history?userId=${userId}&timeframe=${timeframe}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
      ]);

      const [currentResult, historyResult] = await Promise.all([
        currentResponse.json() as Promise<ApiResponse<EngagementMetrics>>,
        historyResponse.json() as Promise<ApiResponse<MetricsData[]>>
      ]);

      if (currentResult.success) setMetrics(currentResult.data!);
      if (historyResult.success) setHistoricalData(historyResult.data!);
    } catch (err) {
      console.error('Failed to fetch engagement metrics:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, timeframe]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  const formatMetricValue = (value: number, metric: string) => {
    if (metric.includes('Rate')) return `${value.toFixed(1)}%`;
    if (metric.includes('Duration')) return `${Math.round(value)}min`;
    return value.toLocaleString();
  };

  const getMetricColor = (metric: keyof MetricsData) => {
    const colors = {
      dailyActiveUsers: '#3B82F6',
      challengeCompletionRate: '#10B981',
      achievementUnlockRate: '#8B5CF6',
      socialInteractionRate: '#F59E0B',
      sessionDuration: '#EF4444'
    };
    return colors[metric] || '#6B7280';
  };

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-7xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className="space-y-6">
            <div className={gamificationStyles.loading.skeleton + " h-64 w-full"} />
            <div className={gamificationStyles.grid.cols4}>
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className={gamificationStyles.loading.skeleton + " h-20"} />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <ChartBarIcon className="w-8 h-8 mr-3 text-blue-500" />
            Engagement Analytics
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Monitor user engagement and platform performance metrics
          </p>
        </div>

        {metrics && (
          <>
            {/* Current Metrics Overview */}
            <div className={clsx(gamificationStyles.container.section, "mb-6")}>
              <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
                Current Performance
              </h2>
              <div className={gamificationStyles.grid.cols4}>
                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Daily Active Users</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-blue-600 flex items-center")}>
                    <UsersIcon className="w-6 h-6 mr-2" />
                    {metrics.dailyActiveUsers.toLocaleString()}
                  </div>
                  <div className={gamificationStyles.typography.body.small}>
                    Weekly: {metrics.weeklyActiveUsers.toLocaleString()}
                  </div>
                </div>

                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Avg Session Duration</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-green-600 flex items-center")}>
                    <ClockIcon className="w-6 h-6 mr-2" />
                    {Math.round(metrics.averageSessionDuration)}m
                  </div>
                  <div className={gamificationStyles.typography.body.small}>
                    User engagement time
                  </div>
                </div>

                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>Challenge Completion</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-purple-600")}>
                    {metrics.challengeCompletionRate.toFixed(1)}%
                  </div>
                  <div className={gamificationStyles.typography.body.small}>
                    Success rate
                  </div>
                </div>

                <div className={gamificationStyles.stats.card}>
                  <div className={gamificationStyles.stats.label}>User Retention</div>
                  <div className={clsx(gamificationStyles.stats.value, "text-orange-600")}>
                    {metrics.userRetentionRate.toFixed(1)}%
                  </div>
                  <div className={gamificationStyles.typography.body.small}>
                    30-day retention
                  </div>
                </div>
              </div>
            </div>

            {/* Trend Visualization */}
            <div className={clsx(gamificationStyles.container.section, "mb-6")}>
              <div className={gamificationStyles.utils.flexBetween + " mb-4"}>
                <h2 className={gamificationStyles.typography.heading.tertiary}>
                  Engagement Trends
                </h2>
                <select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value as keyof MetricsData)}
                  className={gamificationStyles.forms.select}
                >
                  <option value="dailyActiveUsers">Daily Active Users</option>
                  <option value="challengeCompletionRate">Challenge Completion Rate</option>
                  <option value="achievementUnlockRate">Achievement Unlock Rate</option>
                  <option value="socialInteractionRate">Social Interaction Rate</option>
                  <option value="sessionDuration">Session Duration</option>
                </select>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis 
                      dataKey="date" 
                      className="text-xs text-slate-500"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis 
                      className="text-xs text-slate-500"
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip 
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className={clsx(gamificationStyles.container.card, "shadow-lg")}>
                              <p className={gamificationStyles.typography.body.small}>
                                {label}
                              </p>
                              <p className={gamificationStyles.typography.body.regular}>
                                {selectedMetric}: {formatMetricValue(payload[0].value as number, selectedMetric)}
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey={selectedMetric}
                      stroke={getMetricColor(selectedMetric)}
                      fill={getMetricColor(selectedMetric)}
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Detailed Metrics */}
            <div className={gamificationStyles.grid.cols2}>
              <div className={gamificationStyles.container.section}>
                <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
                  Content Quality Trends
                </h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metrics.contentQualityTrend.map((value, index) => ({ 
                      day: index + 1, 
                      quality: value 
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Line 
                        type="monotone" 
                        dataKey="quality" 
                        stroke="#06B6D4" 
                        strokeWidth={2}
                        dot={{ fill: '#06B6D4' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className={gamificationStyles.container.section}>
                <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
                  Platform Health Score
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className={gamificationStyles.utils.flexBetween + " mb-2"}>
                      <span className={gamificationStyles.typography.body.regular}>
                        User Engagement
                      </span>
                      <span className={gamificationStyles.typography.body.regular + " font-bold"}>
                        {metrics.socialInteractionRate.toFixed(1)}%
                      </span>
                    </div>
                    <div className={gamificationStyles.progress.container}>
                      <div 
                        className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                        style={{ width: `${metrics.socialInteractionRate}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className={gamificationStyles.utils.flexBetween + " mb-2"}>
                      <span className={gamificationStyles.typography.body.regular}>
                        Achievement Rate
                      </span>
                      <span className={gamificationStyles.typography.body.regular + " font-bold"}>
                        {metrics.achievementUnlockRate.toFixed(1)}%
                      </span>
                    </div>
                    <div className={gamificationStyles.progress.container}>
                      <div 
                        className="h-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full"
                        style={{ width: `${metrics.achievementUnlockRate}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className={gamificationStyles.utils.flexBetween + " mb-2"}>
                      <span className={gamificationStyles.typography.body.regular}>
                        Collaboration Rate
                      </span>
                      <span className={gamificationStyles.typography.body.regular + " font-bold"}>
                        {metrics.collaborationParticipationRate.toFixed(1)}%
                      </span>
                    </div>
                    <div className={gamificationStyles.progress.container}>
                      <div 
                        className="h-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full"
                        style={{ width: `${metrics.collaborationParticipationRate}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EngagementMetricsComponent;