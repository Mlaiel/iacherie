/**
 * Achievement Panel - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive achievement tracking and display with
 * progress visualization and unlock notifications.
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
  Achievement, 
  AchievementTier,
  ApiResponse,
  PaginatedResponse,
  FilterOptions
} from '../gamification/types';
import { gamificationStyles, tierIcons } from '../gamification/gamification.styles';
import { 
  TrophyIcon,
  LockClosedIcon,
  CheckCircleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  StarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface AchievementPanelProps {
  userId: string;
  className?: string;
  onAchievementClick?: (achievement: Achievement) => void;
  showUnlockedOnly?: boolean;
  showProgress?: boolean;
  maxDisplay?: number;
}

const AchievementPanel: React.FC<AchievementPanelProps> = ({
  userId,
  className,
  onAchievementClick,
  showUnlockedOnly = false,
  showProgress = true,
  maxDisplay = 50
}) => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTier, setSelectedTier] = useState<AchievementTier | ''>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [viewMode, setViewMode] = useState<'all' | 'unlocked' | 'locked'>('all');
  const [sortBy, setSortBy] = useState<'title' | 'tier' | 'progress' | 'unlocked'>('tier');

  const fetchAchievements = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const queryParams = new URLSearchParams({
        userId,
        limit: maxDisplay.toString(),
        ...(selectedTier && { tier: selectedTier }),
        ...(selectedCategory && { category: selectedCategory }),
        ...(searchQuery && { search: searchQuery }),
        ...(showUnlockedOnly && { unlockedOnly: 'true' })
      });

      const response = await fetch(`/api/gamification/achievements?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch achievements: ${response.statusText}`);
      }

      const result: ApiResponse<PaginatedResponse<Achievement>> = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch achievements');
      }

      setAchievements(result.data!.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Achievement fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, maxDisplay, selectedTier, selectedCategory, searchQuery, showUnlockedOnly]);

  useEffect(() => {
    fetchAchievements();
  }, [fetchAchievements]);

  const getFilteredAchievements = () => {
    let filtered = achievements.filter(achievement => {
      // Text search
      if (searchQuery && !achievement.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !achievement.description.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // View mode filter
      if (viewMode === 'unlocked' && !achievement.isUnlocked) return false;
      if (viewMode === 'locked' && achievement.isUnlocked) return false;

      return true;
    });

    // Sort achievements
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'tier':
          const tierOrder = {
            [AchievementTier.BRONZE]: 1,
            [AchievementTier.SILVER]: 2,
            [AchievementTier.GOLD]: 3,
            [AchievementTier.PLATINUM]: 4,
            [AchievementTier.DIAMOND]: 5
          };
          return tierOrder[b.tier] - tierOrder[a.tier];
        case 'progress':
          const progressA = a.maxProgress > 0 ? a.progress / a.maxProgress : 0;
          const progressB = b.maxProgress > 0 ? b.progress / b.maxProgress : 0;
          return progressB - progressA;
        case 'unlocked':
          if (a.isUnlocked === b.isUnlocked) {
            return a.unlockedAt && b.unlockedAt 
              ? new Date(b.unlockedAt).getTime() - new Date(a.unlockedAt).getTime()
              : 0;
          }
          return a.isUnlocked ? -1 : 1;
        default:
          return 0;
      }
    });

    return filtered;
  };

  const getProgressPercentage = (achievement: Achievement): number => {
    if (achievement.maxProgress === 0) return achievement.isUnlocked ? 100 : 0;
    return Math.min((achievement.progress / achievement.maxProgress) * 100, 100);
  };

  const formatUnlockedDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  const getAchievementStats = () => {
    const total = achievements.length;
    const unlocked = achievements.filter(a => a.isUnlocked).length;
    const inProgress = achievements.filter(a => !a.isUnlocked && a.progress > 0).length;
    
    const tierCounts = achievements.reduce((acc, a) => {
      if (a.isUnlocked) {
        acc[a.tier] = (acc[a.tier] || 0) + 1;
      }
      return acc;
    }, {} as Record<AchievementTier, number>);

    return { total, unlocked, inProgress, tierCounts };
  };

  const stats = getAchievementStats();
  const filteredAchievements = getFilteredAchievements();
  const categories = Array.from(new Set(achievements.map(a => a.category)));

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols3}>
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-6 w-32 mb-3"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-full mb-2"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-3/4 mb-4"} />
                <div className={gamificationStyles.loading.skeleton + " h-2 w-full"} />
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
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Failed to Load Achievements
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={fetchAchievements}
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
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <TrophyIcon className="w-8 h-8 mr-3 text-yellow-500" />
            Achievement Gallery
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Track your progress and unlock achievements as you grow your creator journey
          </p>
        </div>

        {/* Statistics Overview */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Your Achievement Progress
          </h2>
          <div className={gamificationStyles.grid.cols4}>
            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Total Achievements</div>
              <div className={clsx(gamificationStyles.stats.value, "text-blue-600")}>
                {stats.unlocked} / {stats.total}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                {((stats.unlocked / stats.total) * 100).toFixed(1)}% Complete
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>In Progress</div>
              <div className={clsx(gamificationStyles.stats.value, "text-orange-600")}>
                {stats.inProgress}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Partially completed
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Rare Achievements</div>
              <div className={clsx(gamificationStyles.stats.value, "text-purple-600")}>
                {(stats.tierCounts[AchievementTier.PLATINUM] || 0) + (stats.tierCounts[AchievementTier.DIAMOND] || 0)}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Platinum & Diamond
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Achievement Score</div>
              <div className={clsx(gamificationStyles.stats.value, "text-yellow-600")}>
                {Object.entries(stats.tierCounts).reduce((score, [tier, count]) => {
                  const tierValues = {
                    [AchievementTier.BRONZE]: 1,
                    [AchievementTier.SILVER]: 2,
                    [AchievementTier.GOLD]: 5,
                    [AchievementTier.PLATINUM]: 10,
                    [AchievementTier.DIAMOND]: 25
                  };
                  return score + (tierValues[tier as AchievementTier] * count);
                }, 0)}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Weighted by rarity
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search achievements..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={clsx(gamificationStyles.forms.input, "pl-10")}
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex gap-3">
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                <option value="all">All Achievements</option>
                <option value="unlocked">Unlocked Only</option>
                <option value="locked">Locked Only</option>
              </select>

              <select
                value={selectedTier}
                onChange={(e) => setSelectedTier(e.target.value as AchievementTier | '')}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Tiers</option>
                <option value={AchievementTier.BRONZE}>Bronze</option>
                <option value={AchievementTier.SILVER}>Silver</option>
                <option value={AchievementTier.GOLD}>Gold</option>
                <option value={AchievementTier.PLATINUM}>Platinum</option>
                <option value={AchievementTier.DIAMOND}>Diamond</option>
              </select>

              {categories.length > 0 && (
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className={gamificationStyles.forms.select}
                >
                  <option value="">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              )}

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                <option value="tier">Sort by Tier</option>
                <option value="title">Sort by Name</option>
                <option value="progress">Sort by Progress</option>
                <option value="unlocked">Sort by Status</option>
              </select>
            </div>
          </div>
        </div>

        {/* Achievements Grid */}
        <div className={gamificationStyles.grid.cols3}>
          {filteredAchievements.map((achievement) => {
            const progressPercentage = getProgressPercentage(achievement);
            const isNearCompletion = !achievement.isUnlocked && progressPercentage > 75;

            return (
              <div
                key={achievement.id}
                className={clsx(
                  gamificationStyles.container.card,
                  "cursor-pointer transition-all duration-300",
                  achievement.isUnlocked ? "hover:shadow-lg ring-1 ring-green-200" : "opacity-75 hover:opacity-90",
                  isNearCompletion && "ring-2 ring-yellow-400 animate-pulse"
                )}
                onClick={() => onAchievementClick?.(achievement)}
              >
                {/* Header */}
                <div className={gamificationStyles.utils.flexBetween + " mb-3"}>
                  <div className={clsx(
                    "flex items-center justify-center w-12 h-12 rounded-full text-2xl",
                    gamificationStyles.achievementTiers[achievement.tier].bg,
                    achievement.isUnlocked ? "" : "grayscale"
                  )}>
                    {achievement.isUnlocked ? (
                      tierIcons[achievement.tier]
                    ) : (
                      <LockClosedIcon className="w-6 h-6 text-slate-400" />
                    )}
                  </div>
                  <div className="text-right">
                    {achievement.isUnlocked ? (
                      <CheckCircleIcon className="w-6 h-6 text-green-500" />
                    ) : (
                      <div className={clsx(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        gamificationStyles.achievementTiers[achievement.tier].bg,
                        gamificationStyles.achievementTiers[achievement.tier].text
                      )}>
                        {achievement.tier.toUpperCase()}
                      </div>
                    )}
                  </div>
                </div>

                {/* Content */}
                <h3 className={clsx(
                  gamificationStyles.typography.body.large,
                  "font-semibold mb-2",
                  !achievement.isUnlocked && "text-slate-500"
                )}>
                  {achievement.title}
                </h3>
                <p className={clsx(
                  gamificationStyles.typography.body.small,
                  "mb-3",
                  !achievement.isUnlocked && "text-slate-400"
                )}>
                  {achievement.description}
                </p>

                {/* Progress */}
                {showProgress && achievement.maxProgress > 0 && (
                  <div className="mb-3">
                    <div className={gamificationStyles.utils.flexBetween + " mb-1"}>
                      <span className={gamificationStyles.typography.body.small}>
                        Progress
                      </span>
                      <span className={clsx(
                        gamificationStyles.typography.body.small,
                        "font-medium"
                      )}>
                        {achievement.progress} / {achievement.maxProgress}
                      </span>
                    </div>
                    <div className={gamificationStyles.progress.container}>
                      <div 
                        className={clsx(
                          gamificationStyles.progress.bar,
                          achievement.isUnlocked && "bg-gradient-to-r from-green-500 to-emerald-600"
                        )}
                        style={{ width: `${progressPercentage}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Unlock Date */}
                {achievement.isUnlocked && achievement.unlockedAt && (
                  <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                    <div className={clsx(
                      gamificationStyles.typography.body.small,
                      "flex items-center text-green-600 dark:text-green-400"
                    )}>
                      <ClockIcon className="w-4 h-4 mr-1" />
                      Unlocked {formatUnlockedDate(achievement.unlockedAt)}
                    </div>
                  </div>
                )}

                {/* Rewards Preview */}
                {achievement.rewards && Object.keys(achievement.rewards).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                    <div className={clsx(
                      gamificationStyles.typography.body.small,
                      "flex items-center"
                    )}>
                      <StarIcon className="w-4 h-4 mr-1 text-yellow-500" />
                      <span>
                        {achievement.rewards.xp && `${achievement.rewards.xp} XP`}
                        {achievement.rewards.currency && ` • ${achievement.rewards.currency} coins`}
                        {achievement.rewards.badge && ` • Badge`}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* No Results */}
        {!loading && filteredAchievements.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏆</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Achievements Found
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Try adjusting your search criteria or start completing activities to unlock achievements.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AchievementPanel;