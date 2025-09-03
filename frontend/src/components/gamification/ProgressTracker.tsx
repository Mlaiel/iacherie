/**
 * Progress Tracker - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive progress visualization with advanced
 * analytics and intelligent progress forecasting.
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
import { 
  UserProgress,
  Achievement,
  Challenge,
  ApiResponse 
} from './types';
import { gamificationStyles } from './gamification.styles';
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
  StarIcon,
  FireIcon,
  ArrowPathIcon,
  ClockIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import clsx from 'clsx';

interface ProgressTrackerProps {
  userId: string;
  className?: string;
  timeframe?: 'week' | 'month' | 'quarter' | 'year';
  showProjections?: boolean;
  showComparisons?: boolean;
}

interface ProgressData {
  date: string;
  experiencePoints: number;
  level: number;
  challengesCompleted: number;
  achievementsUnlocked: number;
  collaborations: number;
  contentQuality: number;
  engagementScore: number;
}

interface ProgressMetrics {
  currentLevel: number;
  experiencePoints: number;
  experienceToNextLevel: number;
  nextLevelProgress: number;
  totalAchievements: number;
  recentAchievements: number;
  activeChallenges: number;
  completedChallenges: number;
  collaborationScore: number;
  contentQualityScore: number;
  engagementScore: number;
  currentStreak: number;
  longestStreak: number;
  weeklyGrowth: number;
  monthlyGrowth: number;
}

interface Milestone {
  id: string;
  title: string;
  description: string;
  targetValue: number;
  currentValue: number;
  category: string;
  deadline?: Date;
  isCompleted: boolean;
  reward?: string;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  userId,
  className,
  timeframe = 'month',
  showProjections = true,
  showComparisons = false
}) => {
  const [progressData, setProgressData] = useState<ProgressData[]>([]);
  const [metrics, setMetrics] = useState<ProgressMetrics | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<keyof ProgressData>('experiencePoints');
  const [refreshing, setRefreshing] = useState(false);

  const fetchProgressData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [progressResponse, metricsResponse, milestonesResponse] = await Promise.all([
        fetch(`/api/gamification/progress/history?userId=${userId}&timeframe=${timeframe}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        }),
        fetch(`/api/gamification/progress/metrics?userId=${userId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        }),
        fetch(`/api/gamification/progress/milestones?userId=${userId}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
      ]);

      if (!progressResponse.ok || !metricsResponse.ok || !milestonesResponse.ok) {
        throw new Error('Failed to fetch progress data');
      }

      const [progressResult, metricsResult, milestonesResult] = await Promise.all([
        progressResponse.json() as Promise<ApiResponse<ProgressData[]>>,
        metricsResponse.json() as Promise<ApiResponse<ProgressMetrics>>,
        milestonesResponse.json() as Promise<ApiResponse<Milestone[]>>
      ]);

      if (!progressResult.success || !metricsResult.success || !milestonesResult.success) {
        throw new Error('Failed to load progress data');
      }

      setProgressData(progressResult.data!);
      setMetrics(metricsResult.data!);
      setMilestones(milestonesResult.data!);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Progress fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, timeframe]);

  useEffect(() => {
    fetchProgressData();
  }, [fetchProgressData]);

  const refreshData = async () => {
    setRefreshing(true);
    await fetchProgressData();
    setRefreshing(false);
  };

  const calculateGrowthRate = (data: ProgressData[], metric: keyof ProgressData): number => {
    if (data.length < 2) return 0;
    const recent = data[data.length - 1];
    const previous = data[data.length - 2];
    const currentValue = recent[metric] as number;
    const previousValue = previous[metric] as number;
    
    if (previousValue === 0) return currentValue > 0 ? 100 : 0;
    return ((currentValue - previousValue) / previousValue) * 100;
  };

  const predictNextWeekValue = (data: ProgressData[], metric: keyof ProgressData): number => {
    if (data.length < 3) return data[data.length - 1]?.[metric] as number || 0;
    
    // Simple linear regression for prediction
    const recentData = data.slice(-7); // Last 7 days
    const values = recentData.map(d => d[metric] as number);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const trend = values[values.length - 1] - values[0];
    
    return Math.max(0, avg + trend);
  };

  const formatMetricValue = (value: number, metric: keyof ProgressData): string => {
    switch (metric) {
      case 'experiencePoints':
        return value.toLocaleString();
      case 'contentQuality':
      case 'engagementScore':
        return `${value.toFixed(1)}%`;
      default:
        return value.toString();
    }
  };

  const getMetricColor = (metric: keyof ProgressData): string => {
    const colors: Record<string, string> = {
      experiencePoints: '#3B82F6',
      level: '#10B981',
      challengesCompleted: '#F59E0B',
      achievementsUnlocked: '#8B5CF6',
      collaborations: '#EF4444',
      contentQuality: '#06B6D4',
      engagementScore: '#84CC16'
    };
    return colors[metric] || '#6B7280';
  };

  const getStreakColor = (streak: number): string => {
    if (streak >= 30) return 'text-purple-600';
    if (streak >= 14) return 'text-blue-600';
    if (streak >= 7) return 'text-green-600';
    return 'text-slate-600';
  };

  const formatTimeRemaining = (deadline: Date): string => {
    const now = new Date();
    const diff = deadline.getTime() - now.getTime();
    
    if (diff <= 0) return 'Overdue';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h`;
  };

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-7xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className="space-y-6">
            <div className={gamificationStyles.loading.skeleton + " h-64 w-full"} />
            <div className={gamificationStyles.grid.cols3}>
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className={gamificationStyles.container.card}>
                  <div className={gamificationStyles.loading.skeleton + " h-6 w-32 mb-3"} />
                  <div className={gamificationStyles.loading.skeleton + " h-8 w-20"} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-7xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Failed to Load Progress Data
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={fetchProgressData}
                className={clsx(gamificationStyles.buttons.primary, "mt-4")}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const growthRate = calculateGrowthRate(progressData, selectedMetric);
  const prediction = predictNextWeekValue(progressData, selectedMetric);

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className={gamificationStyles.utils.flexBetween}>
            <div>
              <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
                <ChartBarIcon className="w-8 h-8 mr-3 text-blue-500" />
                Progress Analytics
              </h1>
              <p className={gamificationStyles.typography.body.regular}>
                Track your creator journey with detailed analytics and insights
              </p>
            </div>
            <button
              onClick={refreshData}
              disabled={refreshing}
              className={clsx(
                gamificationStyles.buttons.ghost,
                refreshing && "opacity-50 cursor-not-allowed"
              )}
            >
              {refreshing ? (
                <ArrowPathIcon className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <ArrowPathIcon className="w-5 h-5 mr-2" />
              )}
              Refresh
            </button>
          </div>
        </div>

        {/* Key Metrics Overview */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Current Progress Overview
          </h2>
          <div className={gamificationStyles.grid.cols4}>
            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Current Level</div>
              <div className={clsx(gamificationStyles.stats.value, "text-green-600 flex items-center")}>
                <StarIcon className="w-6 h-6 mr-2" />
                {metrics.currentLevel}
              </div>
              <div className="mt-2">
                <div className={gamificationStyles.progress.container}>
                  <div 
                    className={gamificationStyles.progress.bar}
                    style={{ width: `${metrics.nextLevelProgress}%` }}
                  />
                </div>
                <div className={gamificationStyles.typography.body.small + " mt-1"}>
                  {metrics.experienceToNextLevel.toLocaleString()} XP to next level
                </div>
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Experience Points</div>
              <div className={clsx(gamificationStyles.stats.value, "text-blue-600 flex items-center")}>
                <BoltIcon className="w-6 h-6 mr-2" />
                {metrics.experiencePoints.toLocaleString()}
              </div>
              <div className={clsx(
                gamificationStyles.typography.body.small,
                metrics.weeklyGrowth >= 0 ? "text-green-600" : "text-red-600"
              )}>
                {metrics.weeklyGrowth >= 0 ? '+' : ''}{metrics.weeklyGrowth.toFixed(1)}% this week
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Active Streak</div>
              <div className={clsx(
                gamificationStyles.stats.value,
                getStreakColor(metrics.currentStreak),
                "flex items-center"
              )}>
                <FireIcon className="w-6 h-6 mr-2" />
                {metrics.currentStreak}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Best: {metrics.longestStreak} days
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Achievements</div>
              <div className={clsx(gamificationStyles.stats.value, "text-purple-600")}>
                {metrics.totalAchievements}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                {metrics.recentAchievements} unlocked this month
              </div>
            </div>
          </div>
        </div>

        {/* Progress Chart */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className={gamificationStyles.utils.flexBetween + " mb-4"}>
            <h2 className={gamificationStyles.typography.heading.tertiary}>
              Progress Trends
            </h2>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value as keyof ProgressData)}
              className={gamificationStyles.forms.select}
            >
              <option value="experiencePoints">Experience Points</option>
              <option value="level">Level Progress</option>
              <option value="challengesCompleted">Challenges Completed</option>
              <option value="achievementsUnlocked">Achievements Unlocked</option>
              <option value="collaborations">Collaborations</option>
              <option value="contentQuality">Content Quality</option>
              <option value="engagementScore">Engagement Score</option>
            </select>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={progressData}>
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

          {/* Growth and Prediction */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={gamificationStyles.container.compactCard}>
              <div className={gamificationStyles.typography.body.small}>Growth Rate</div>
              <div className={clsx(
                gamificationStyles.typography.body.large,
                "font-bold flex items-center",
                growthRate >= 0 ? "text-green-600" : "text-red-600"
              )}>
                <ArrowTrendingUpIcon className="w-5 h-5 mr-1" />
                {growthRate >= 0 ? '+' : ''}{growthRate.toFixed(1)}%
              </div>
            </div>

            {showProjections && (
              <div className={gamificationStyles.container.compactCard}>
                <div className={gamificationStyles.typography.body.small}>Next Week Prediction</div>
                <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-blue-600")}>
                  {formatMetricValue(prediction, selectedMetric)}
                </div>
              </div>
            )}

            <div className={gamificationStyles.container.compactCard}>
              <div className={gamificationStyles.typography.body.small}>Current Value</div>
              <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-slate-800")}>
                {formatMetricValue(
                  progressData[progressData.length - 1]?.[selectedMetric] as number || 0, 
                  selectedMetric
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Performance Scores */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Performance Scores
          </h2>
          <div className={gamificationStyles.grid.cols3}>
            <div className={gamificationStyles.container.card}>
              <div className={gamificationStyles.typography.body.regular + " font-medium mb-2"}>
                Content Quality Score
              </div>
              <div className="mb-3">
                <div className={gamificationStyles.progress.container}>
                  <div 
                    className="h-3 bg-gradient-to-r from-cyan-500 to-blue-600 transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${metrics.contentQualityScore}%` }}
                  />
                </div>
              </div>
              <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-cyan-600")}>
                {metrics.contentQualityScore.toFixed(1)}%
              </div>
            </div>

            <div className={gamificationStyles.container.card}>
              <div className={gamificationStyles.typography.body.regular + " font-medium mb-2"}>
                Engagement Score
              </div>
              <div className="mb-3">
                <div className={gamificationStyles.progress.container}>
                  <div 
                    className="h-3 bg-gradient-to-r from-green-500 to-emerald-600 transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${metrics.engagementScore}%` }}
                  />
                </div>
              </div>
              <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-green-600")}>
                {metrics.engagementScore.toFixed(1)}%
              </div>
            </div>

            <div className={gamificationStyles.container.card}>
              <div className={gamificationStyles.typography.body.regular + " font-medium mb-2"}>
                Collaboration Score
              </div>
              <div className="mb-3">
                <div className={gamificationStyles.progress.container}>
                  <div 
                    className="h-3 bg-gradient-to-r from-purple-500 to-pink-600 transition-all duration-500 ease-out rounded-full"
                    style={{ width: `${metrics.collaborationScore}%` }}
                  />
                </div>
              </div>
              <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-purple-600")}>
                {metrics.collaborationScore.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* Milestones */}
        {milestones.length > 0 && (
          <div className={gamificationStyles.container.section}>
            <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
              Current Milestones
            </h2>
            <div className="space-y-3">
              {milestones.slice(0, 5).map((milestone) => {
                const progress = milestone.targetValue > 0 
                  ? (milestone.currentValue / milestone.targetValue) * 100 
                  : 0;
                
                return (
                  <div key={milestone.id} className={gamificationStyles.container.compactCard}>
                    <div className={gamificationStyles.utils.flexBetween + " mb-2"}>
                      <div>
                        <div className={clsx(
                          gamificationStyles.typography.body.regular,
                          "font-medium",
                          milestone.isCompleted && "text-green-600"
                        )}>
                          {milestone.title}
                        </div>
                        <div className={gamificationStyles.typography.body.small}>
                          {milestone.description}
                        </div>
                      </div>
                      {milestone.deadline && !milestone.isCompleted && (
                        <div className="text-right">
                          <div className={gamificationStyles.typography.body.small}>
                            <ClockIcon className="w-4 h-4 inline mr-1" />
                            {formatTimeRemaining(milestone.deadline)}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="mb-2">
                      <div className={gamificationStyles.utils.flexBetween + " mb-1"}>
                        <span className={gamificationStyles.typography.body.small}>
                          Progress
                        </span>
                        <span className={gamificationStyles.typography.body.small}>
                          {milestone.currentValue} / {milestone.targetValue}
                        </span>
                      </div>
                      <div className={gamificationStyles.progress.container}>
                        <div 
                          className={clsx(
                            "h-2 transition-all duration-500 ease-out rounded-full",
                            milestone.isCompleted 
                              ? "bg-gradient-to-r from-green-500 to-emerald-600"
                              : "bg-gradient-to-r from-blue-500 to-purple-600"
                          )}
                          style={{ width: `${Math.min(progress, 100)}%` }}
                        />
                      </div>
                    </div>

                    {milestone.reward && (
                      <div className={clsx(
                        gamificationStyles.typography.body.small,
                        "text-yellow-600 flex items-center"
                      )}>
                        <StarIcon className="w-4 h-4 mr-1" />
                        Reward: {milestone.reward}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracker;