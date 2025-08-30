/**
 * Leaderboard Component - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive leaderboard visualization with
 * real-time ranking updates and competitive analytics.
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
  Leaderboard, 
  LeaderboardEntry,
  ApiResponse 
} from './types';
import { gamificationStyles } from './gamification.styles';
import { 
  TrophyIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
  UserIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

export interface LeaderboardComponentProps {
  userId: string;
  className?: string;
  initialTimeframe?: 'daily' | 'weekly' | 'monthly' | 'all_time';
  initialCategory?: string;
  onUserSelect?: (userId: string) => void;
  showUserHighlight?: boolean;
  maxEntries?: number;
}

const LeaderboardComponent: React.FC<LeaderboardComponentProps> = ({
  userId,
  className,
  initialTimeframe = 'weekly',
  initialCategory = 'global',
  onUserSelect,
  showUserHighlight = true,
  maxEntries = 50
}) => {
  const [leaderboards, setLeaderboards] = useState<Leaderboard[]>([]);
  const [currentLeaderboard, setCurrentLeaderboard] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState(initialTimeframe);
  const [category, setCategory] = useState(initialCategory);
  const [refreshing, setRefreshing] = useState(false);

  const fetchLeaderboards = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/gamification/leaderboards?timeframe=${timeframe}&category=${category}&limit=${maxEntries}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch leaderboards: ${response.statusText}`);
      }

      const result: ApiResponse<Leaderboard[]> = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch leaderboards');
      }

      const leaderboardData = result.data!;
      setLeaderboards(leaderboardData);
      
      // Find the current leaderboard based on filters
      const current = leaderboardData.find(l => 
        l.timeframe === timeframe && l.category === category
      ) || leaderboardData[0];
      
      setCurrentLeaderboard(current);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Leaderboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [timeframe, category, maxEntries]);

  useEffect(() => {
    fetchLeaderboards();
  }, [fetchLeaderboards]);

  const refreshLeaderboard = async () => {
    setRefreshing(true);
    await fetchLeaderboards();
    setRefreshing(false);
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
    if (change < 0) return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
    return <MinusIcon className="w-4 h-4 text-slate-400" />;
  };

  const getChangeText = (change: number) => {
    if (change > 0) return `+${change}`;
    if (change < 0) return change.toString();
    return '0';
  };

  const formatScore = (score: number): string => {
    if (score >= 1000000) return `${(score / 1000000).toFixed(1)}M`;
    if (score >= 1000) return `${(score / 1000).toFixed(1)}K`;
    return score.toString();
  };

  const formatLastUpdated = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const categories = [
    { value: 'global', label: 'Global' },
    { value: 'content_creators', label: 'Content Creators' },
    { value: 'musicians', label: 'Musicians' },
    { value: 'bloggers', label: 'Bloggers' },
    { value: 'photographers', label: 'Photographers' },
    { value: 'influencers', label: 'Influencers' },
    { value: 'comedians', label: 'Comedians' }
  ];

  const timeframes = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'all_time', label: 'All Time' }
  ];

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-4xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className="space-y-3">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className={clsx(gamificationStyles.container.card, "flex items-center space-x-4")}>
                <div className={gamificationStyles.loading.skeleton + " w-8 h-8 rounded-full"} />
                <div className={gamificationStyles.loading.skeleton + " w-12 h-12 rounded-full"} />
                <div className="flex-1">
                  <div className={gamificationStyles.loading.skeleton + " h-4 w-32 mb-2"} />
                  <div className={gamificationStyles.loading.skeleton + " h-3 w-24"} />
                </div>
                <div className={gamificationStyles.loading.skeleton + " w-16 h-6"} />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-4xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Failed to Load Leaderboard
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={fetchLeaderboards}
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

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className={gamificationStyles.utils.flexBetween}>
            <div>
              <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
                <TrophyIcon className="w-8 h-8 mr-3 text-yellow-500" />
                Leaderboards
              </h1>
              <p className={gamificationStyles.typography.body.regular}>
                Compete with creators worldwide and track your ranking progress
              </p>
            </div>
            <button
              onClick={refreshLeaderboard}
              disabled={refreshing}
              className={clsx(
                gamificationStyles.buttons.ghost,
                refreshing && "opacity-50 cursor-not-allowed"
              )}
              title="Refresh Leaderboard"
            >
              {refreshing ? (
                <div className={gamificationStyles.loading.spinner} />
              ) : (
                '🔄'
              )}
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className={clsx(gamificationStyles.typography.body.small, "block mb-2")}>
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className={gamificationStyles.forms.select}
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className={clsx(gamificationStyles.typography.body.small, "block mb-2")}>
                Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                {timeframes.map(tf => (
                  <option key={tf.value} value={tf.value}>
                    {tf.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {currentLeaderboard ? (
          <>
            {/* Leaderboard Info */}
            <div className={clsx(gamificationStyles.container.section, "mb-6")}>
              <div className={gamificationStyles.utils.flexBetween}>
                <div>
                  <h2 className={gamificationStyles.typography.heading.secondary}>
                    {currentLeaderboard.title}
                  </h2>
                  <p className={gamificationStyles.typography.body.small}>
                    {currentLeaderboard.description}
                  </p>
                </div>
                <div className="text-right">
                  <div className={gamificationStyles.typography.body.small}>
                    Last Updated
                  </div>
                  <div className={clsx(gamificationStyles.typography.body.regular, "flex items-center")}>
                    <ClockIcon className="w-4 h-4 mr-1" />
                    {formatLastUpdated(currentLeaderboard.lastUpdated)}
                  </div>
                </div>
              </div>
            </div>

            {/* Podium (Top 3) */}
            {currentLeaderboard.entries.length >= 3 && (
              <div className={clsx(gamificationStyles.container.section, "mb-6")}>
                <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "text-center mb-6")}>
                  🏆 Top Champions 🏆
                </h3>
                <div className="flex justify-center items-end space-x-4">
                  {/* Second Place */}
                  <div className="text-center">
                    <div className={clsx(
                      gamificationStyles.leaderboard.podium.second,
                      "w-20 h-16 rounded-t-lg flex items-center justify-center text-2xl font-bold mb-2"
                    )}>
                      2
                    </div>
                    <div className="w-20">
                      <div className="w-12 h-12 bg-slate-300 rounded-full mx-auto mb-2 flex items-center justify-center">
                        <UserIcon className="w-6 h-6 text-slate-600" />
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "truncate")}>
                        {currentLeaderboard.entries[1]?.username || 'Unknown'}
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "text-slate-500")}>
                        {formatScore(currentLeaderboard.entries[1]?.score || 0)}
                      </div>
                    </div>
                  </div>

                  {/* First Place */}
                  <div className="text-center">
                    <div className={clsx(
                      gamificationStyles.leaderboard.podium.first,
                      "w-24 h-20 rounded-t-lg flex items-center justify-center text-3xl font-bold mb-2"
                    )}>
                      1
                    </div>
                    <div className="w-24">
                      <div className="w-16 h-16 bg-yellow-300 rounded-full mx-auto mb-2 flex items-center justify-center">
                        <UserIcon className="w-8 h-8 text-yellow-700" />
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.regular, "font-bold truncate")}>
                        {currentLeaderboard.entries[0]?.username || 'Unknown'}
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "text-yellow-700")}>
                        {formatScore(currentLeaderboard.entries[0]?.score || 0)}
                      </div>
                    </div>
                  </div>

                  {/* Third Place */}
                  <div className="text-center">
                    <div className={clsx(
                      gamificationStyles.leaderboard.podium.third,
                      "w-20 h-12 rounded-t-lg flex items-center justify-center text-xl font-bold mb-2"
                    )}>
                      3
                    </div>
                    <div className="w-20">
                      <div className="w-12 h-12 bg-amber-300 rounded-full mx-auto mb-2 flex items-center justify-center">
                        <UserIcon className="w-6 h-6 text-amber-700" />
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "truncate")}>
                        {currentLeaderboard.entries[2]?.username || 'Unknown'}
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "text-slate-500")}>
                        {formatScore(currentLeaderboard.entries[2]?.score || 0)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Full Leaderboard */}
            <div className={gamificationStyles.container.section}>
              <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "flex items-center mb-4")}>
                <ChartBarIcon className="w-5 h-5 mr-2" />
                Full Rankings
              </h3>
              <div className="space-y-2">
                {currentLeaderboard.entries.map((entry, index) => (
                  <div
                    key={entry.userId}
                    className={clsx(
                      gamificationStyles.container.compactCard,
                      "flex items-center space-x-4 transition-all duration-200",
                      entry.isCurrentUser && showUserHighlight && "ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20",
                      onUserSelect && "cursor-pointer hover:shadow-md"
                    )}
                    onClick={() => onUserSelect?.(entry.userId)}
                  >
                    {/* Rank */}
                    <div className={clsx(
                      "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold",
                      entry.rank <= 3 ? gamificationStyles.leaderboard.rank.top3 : gamificationStyles.leaderboard.rank.regular,
                      entry.rank === 1 && gamificationStyles.leaderboard.podium.first,
                      entry.rank === 2 && gamificationStyles.leaderboard.podium.second,
                      entry.rank === 3 && gamificationStyles.leaderboard.podium.third
                    )}>
                      {getRankIcon(entry.rank)}
                    </div>

                    {/* Avatar */}
                    <div className="flex-shrink-0">
                      {entry.avatar ? (
                        <img
                          src={entry.avatar}
                          alt={entry.username}
                          className="w-10 h-10 rounded-full"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center">
                          <UserIcon className="w-5 h-5 text-slate-500" />
                        </div>
                      )}
                    </div>

                    {/* User Info */}
                    <div className="flex-1 min-w-0">
                      <div className={clsx(
                        gamificationStyles.typography.body.regular,
                        "font-medium truncate",
                        entry.isCurrentUser && "text-blue-700 dark:text-blue-300"
                      )}>
                        {entry.username}
                        {entry.isCurrentUser && (
                          <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            You
                          </span>
                        )}
                      </div>
                      <div className={gamificationStyles.typography.body.small}>
                        Level {entry.level} • {entry.achievementCount} achievements
                      </div>
                    </div>

                    {/* Score */}
                    <div className="flex-shrink-0 text-right">
                      <div className={clsx(gamificationStyles.typography.body.regular, "font-bold")}>
                        {formatScore(entry.score)}
                      </div>
                      <div className={clsx(gamificationStyles.typography.body.small, "flex items-center justify-end")}>
                        {getChangeIcon(entry.change)}
                        <span className="ml-1">{getChangeText(entry.change)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📊</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Leaderboard Data
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Leaderboard data is not available for the selected criteria.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaderboardComponent;