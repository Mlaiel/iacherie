/**
 * Gamification Dashboard - Ultra-Advanced Enterprise System
 * 
 * This component provides the main gamification dashboard with comprehensive
 * user progress tracking, achievement display, and engagement metrics.
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
  GamificationDashboardData, 
  Achievement, 
  Challenge, 
  LeaderboardEntry,
  Reward
} from '../gamification/types';
import { gamificationStyles, tierIcons, challengeIcons } from '../gamification/gamification.styles';
import { 
  TrophyIcon, 
  ChartBarIcon, 
  FireIcon, 
  StarIcon,
  UsersIcon,
  GiftIcon,
  CalendarIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface GamificationDashboardProps {
  userId: string;
  className?: string;
  onChallengeClick?: (challenge: Challenge) => void;
  onAchievementClick?: (achievement: Achievement) => void;
  onLeaderboardClick?: () => void;
  onRewardClick?: (reward: Reward) => void;
}

const GamificationDashboard: React.FC<GamificationDashboardProps> = ({
  userId,
  className,
  onChallengeClick,
  onAchievementClick,
  onLeaderboardClick,
  onRewardClick
}) => {
  const [dashboardData, setDashboardData] = useState<GamificationDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/gamification/dashboard/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData, refreshKey]);

  const refreshDashboard = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  const calculateLevelProgress = (userProgress: UserProgress): number => {
    const currentLevelXP = Math.pow(userProgress.level, 2) * 1000;
    const nextLevelXP = Math.pow(userProgress.level + 1, 2) * 1000;
    const progressInLevel = userProgress.experiencePoints - currentLevelXP;
    const xpRequiredForNext = nextLevelXP - currentLevelXP;
    return Math.min((progressInLevel / xpRequiredForNext) * 100, 100);
  };

  const getRankChange = (entry: LeaderboardEntry): string => {
    if (entry.change > 0) return `↗️ +${entry.change}`;
    if (entry.change < 0) return `↘️ ${entry.change}`;
    return '➡️ 0';
  };

  const formatTimeRemaining = (endDate: Date): string => {
    const now = new Date();
    const diff = endDate.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h remaining`;
    return `${hours}h remaining`;
  };

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-7xl mx-auto p-6">
          <div className="space-y-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className={clsx(gamificationStyles.container.section)}>
                <div className={clsx(gamificationStyles.loading.skeleton, "h-8 w-48 mb-4")} />
                <div className={clsx(gamificationStyles.loading.skeleton, "h-32 w-full")} />
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
        <div className="max-w-7xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Failed to Load Dashboard
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={refreshDashboard}
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

  if (!dashboardData) {
    return null;
  }

  const { userProgress, activeChallenges, recentAchievements, leaderboardPosition, availableRewards, upcomingCompetitions } = dashboardData;
  const levelProgress = calculateLevelProgress(userProgress);

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <div className={gamificationStyles.utils.flexBetween}>
            <div>
              <h1 className={gamificationStyles.typography.heading.primary}>
                Creator Dashboard
              </h1>
              <p className={gamificationStyles.typography.body.regular}>
                Track your progress and achievements across the platform
              </p>
            </div>
            <button
              onClick={refreshDashboard}
              className={gamificationStyles.buttons.ghost}
              title="Refresh Dashboard"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* User Progress Overview */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.secondary, "flex items-center")}>
            <StarIcon className="w-6 h-6 mr-2 text-yellow-500" />
            Your Progress
          </h2>
          <div className={gamificationStyles.grid.cols4}>
            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Current Level</div>
              <div className={clsx(gamificationStyles.stats.value, "flex items-center")}>
                {userProgress.level}
                <span className="text-lg ml-2">🎖️</span>
              </div>
              <div className="mt-2">
                <div className={gamificationStyles.progress.label}>
                  Progress to Level {userProgress.level + 1}
                </div>
                <div className={gamificationStyles.progress.container}>
                  <div 
                    className={gamificationStyles.progress.bar}
                    style={{ width: `${levelProgress}%` }}
                  />
                </div>
                <div className={clsx(gamificationStyles.typography.body.small, "mt-1")}>
                  {levelProgress.toFixed(1)}% Complete
                </div>
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Experience Points</div>
              <div className={clsx(gamificationStyles.stats.value, "flex items-center")}>
                {userProgress.experiencePoints.toLocaleString()}
                <span className="text-lg ml-2">⚡</span>
              </div>
              <div className={clsx(gamificationStyles.typography.body.small, "mt-1")}>
                Total earned across platform
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Global Rank</div>
              <div className={clsx(gamificationStyles.stats.value, "flex items-center")}>
                #{userProgress.rank}
                <span className="text-lg ml-2">🏆</span>
              </div>
              <div className={clsx(gamificationStyles.typography.body.small, "mt-1")}>
                {getRankChange(leaderboardPosition)}
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Achievements</div>
              <div className={clsx(gamificationStyles.stats.value, "flex items-center")}>
                {userProgress.achievementsUnlocked.length}
                <span className="text-lg ml-2">🎯</span>
              </div>
              <div className={clsx(gamificationStyles.typography.body.small, "mt-1")}>
                Unlocked milestones
              </div>
            </div>
          </div>
        </div>

        <div className={gamificationStyles.grid.cols3}>
          {/* Active Challenges */}
          <div className={gamificationStyles.container.section}>
            <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "flex items-center")}>
              <FireIcon className="w-5 h-5 mr-2 text-orange-500" />
              Active Challenges
            </h3>
            <div className="space-y-3">
              {activeChallenges.slice(0, 3).map((challenge) => (
                <div
                  key={challenge.id}
                  className={clsx(
                    gamificationStyles.container.compactCard,
                    "cursor-pointer hover:scale-105 transition-transform"
                  )}
                  onClick={() => onChallengeClick?.(challenge)}
                >
                  <div className={gamificationStyles.utils.flexBetween}>
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">
                        {challengeIcons[challenge.type]}
                      </span>
                      <div>
                        <div className={clsx(gamificationStyles.typography.body.regular, "font-medium")}>
                          {challenge.title}
                        </div>
                        <div className={gamificationStyles.typography.body.small}>
                          {formatTimeRemaining(challenge.endDate)}
                        </div>
                      </div>
                    </div>
                    <div className={clsx(
                      gamificationStyles.challengeTypes[challenge.type].bg,
                      gamificationStyles.challengeTypes[challenge.type].text,
                      "px-2 py-1 rounded-full text-xs font-medium"
                    )}>
                      {challenge.type}
                    </div>
                  </div>
                </div>
              ))}
              {activeChallenges.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🎯</div>
                  <div className={gamificationStyles.typography.body.small}>
                    No active challenges
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recent Achievements */}
          <div className={gamificationStyles.container.section}>
            <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "flex items-center")}>
              <TrophyIcon className="w-5 h-5 mr-2 text-yellow-500" />
              Recent Achievements
            </h3>
            <div className="space-y-3">
              {recentAchievements.slice(0, 3).map((achievement) => (
                <div
                  key={achievement.id}
                  className={clsx(
                    gamificationStyles.container.compactCard,
                    "cursor-pointer hover:scale-105 transition-transform"
                  )}
                  onClick={() => onAchievementClick?.(achievement)}
                >
                  <div className="flex items-center">
                    <div className={clsx(
                      "w-12 h-12 rounded-full flex items-center justify-center text-xl mr-3",
                      gamificationStyles.achievementTiers[achievement.tier].bg
                    )}>
                      {tierIcons[achievement.tier]}
                    </div>
                    <div>
                      <div className={clsx(gamificationStyles.typography.body.regular, "font-medium")}>
                        {achievement.title}
                      </div>
                      <div className={gamificationStyles.typography.body.small}>
                        {achievement.tier.toUpperCase()} Achievement
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {recentAchievements.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🏆</div>
                  <div className={gamificationStyles.typography.body.small}>
                    No recent achievements
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Available Rewards */}
          <div className={gamificationStyles.container.section}>
            <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "flex items-center")}>
              <GiftIcon className="w-5 h-5 mr-2 text-purple-500" />
              Available Rewards
            </h3>
            <div className="space-y-3">
              {availableRewards.slice(0, 3).map((reward) => (
                <div
                  key={reward.id}
                  className={clsx(
                    gamificationStyles.container.compactCard,
                    "cursor-pointer hover:scale-105 transition-transform"
                  )}
                  onClick={() => onRewardClick?.(reward)}
                >
                  <div className={gamificationStyles.utils.flexBetween}>
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">{reward.icon}</span>
                      <div>
                        <div className={clsx(gamificationStyles.typography.body.regular, "font-medium")}>
                          {reward.title}
                        </div>
                        <div className={gamificationStyles.typography.body.small}>
                          {reward.cost} points
                        </div>
                      </div>
                    </div>
                    <button className={gamificationStyles.buttons.primary}>
                      Claim
                    </button>
                  </div>
                </div>
              ))}
              {availableRewards.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🎁</div>
                  <div className={gamificationStyles.typography.body.small}>
                    No rewards available
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className={clsx(gamificationStyles.container.section, "mt-6")}>
          <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Quick Actions
          </h3>
          <div className={gamificationStyles.grid.cols4}>
            <button 
              onClick={onLeaderboardClick}
              className={clsx(
                gamificationStyles.container.card,
                "text-center hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-r from-blue-500 to-purple-600 text-white"
              )}
            >
              <ChartBarIcon className="w-8 h-8 mx-auto mb-2" />
              <div className="font-medium">View Leaderboards</div>
            </button>

            <button className={clsx(
              gamificationStyles.container.card,
              "text-center hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-r from-green-500 to-teal-600 text-white"
            )}>
              <UsersIcon className="w-8 h-8 mx-auto mb-2" />
              <div className="font-medium">Join Competitions</div>
            </button>

            <button className={clsx(
              gamificationStyles.container.card,
              "text-center hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-r from-orange-500 to-red-600 text-white"
            )}>
              <CalendarIcon className="w-8 h-8 mx-auto mb-2" />
              <div className="font-medium">Browse Challenges</div>
            </button>

            <button className={clsx(
              gamificationStyles.container.card,
              "text-center hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-r from-purple-500 to-pink-600 text-white"
            )}>
              <ArrowTrendingUpIcon className="w-8 h-8 mx-auto mb-2" />
              <div className="font-medium">View Analytics</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GamificationDashboard;