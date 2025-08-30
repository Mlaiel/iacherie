/**
 * Reward Store - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive reward marketplace with
 * advanced filtering and purchase management.
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
import { Reward, RewardType, AchievementTier, ApiResponse, PaginatedResponse } from './types';
import { gamificationStyles } from './gamification.styles';
import { 
  ShoppingCartIcon, 
  StarIcon, 
  FireIcon, 
  GiftIcon,
  SparklesIcon,
  ClockIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface RewardStoreProps {
  userId: string;
  userPoints: number;
  userCurrency: number;
  className?: string;
  onPurchase?: (rewardId: string) => Promise<boolean>;
  onRewardDetails?: (reward: Reward) => void;
}

const RewardStore: React.FC<RewardStoreProps> = ({
  userId,
  userPoints,
  userCurrency,
  className,
  onPurchase,
  onRewardDetails
}) => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<RewardType | ''>('');
  const [filterRarity, setFilterRarity] = useState<AchievementTier | ''>('');
  const [sortBy, setSortBy] = useState<'cost' | 'rarity' | 'popularity'>('cost');
  const [showAffordableOnly, setShowAffordableOnly] = useState(false);

  const fetchRewards = useCallback(async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams({
        available: 'true',
        ...(filterType && { type: filterType }),
        ...(filterRarity && { rarity: filterRarity }),
        sort: sortBy,
        affordableOnly: showAffordableOnly.toString()
      });

      const response = await fetch(`/api/gamification/store/rewards?${queryParams}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });

      const result: ApiResponse<PaginatedResponse<Reward>> = await response.json();
      if (result.success) setRewards(result.data!.items);
    } catch (err) {
      console.error('Failed to fetch store rewards:', err);
    } finally {
      setLoading(false);
    }
  }, [filterType, filterRarity, sortBy, showAffordableOnly]);

  useEffect(() => {
    fetchRewards();
  }, [fetchRewards]);

  const handlePurchase = async (reward: Reward) => {
    if (!onPurchase || purchasing || !canAfford(reward)) return;

    try {
      setPurchasing(reward.id);
      const success = await onPurchase(reward.id);
      if (success) {
        // Update local state
        setRewards(prev => prev.map(r => 
          r.id === reward.id && r.isLimited && r.remainingQuantity
            ? { ...r, remainingQuantity: r.remainingQuantity - 1 }
            : r
        ));
      }
    } catch (err) {
      console.error('Failed to purchase reward:', err);
    } finally {
      setPurchasing(null);
    }
  };

  const canAfford = (reward: Reward): boolean => {
    if (!reward.cost) return true;
    return reward.currency === 'points' ? userPoints >= reward.cost : userCurrency >= reward.cost;
  };

  const isPopular = (reward: Reward): boolean => {
    // This would be determined by backend analytics
    return Math.random() > 0.7; // Simulated for demo
  };

  const isNewReward = (reward: Reward): boolean => {
    // Check if reward was added in the last 7 days
    return true; // Simulated for demo
  };

  const getRewardTypeIcon = (type: RewardType) => {
    switch (type) {
      case RewardType.EXPERIENCE_POINTS:
        return <SparklesIcon className="w-5 h-5" />;
      case RewardType.VIRTUAL_CURRENCY:
        return <CurrencyDollarIcon className="w-5 h-5" />;
      case RewardType.BADGE:
        return <StarIcon className="w-5 h-5" />;
      case RewardType.PREMIUM_FEATURE:
        return <FireIcon className="w-5 h-5" />;
      default:
        return <GiftIcon className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols3}>
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-48 w-full mb-3"} />
                <div className={gamificationStyles.loading.skeleton + " h-6 w-32 mb-2"} />
                <div className={gamificationStyles.loading.skeleton + " h-10 w-full"} />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const featuredRewards = rewards.filter(r => isPopular(r) || isNewReward(r)).slice(0, 3);
  const regularRewards = rewards.filter(r => !featuredRewards.includes(r));

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <ShoppingCartIcon className="w-8 h-8 mr-3 text-purple-500" />
            Reward Marketplace
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Discover and purchase exclusive rewards with your earned points and currency
          </p>
        </div>

        {/* User Balance */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Your Balance
          </h2>
          <div className={gamificationStyles.grid.cols2}>
            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Available Points</div>
              <div className={clsx(gamificationStyles.stats.value, "text-blue-600 flex items-center")}>
                <SparklesIcon className="w-6 h-6 mr-2" />
                {userPoints.toLocaleString()}
              </div>
            </div>
            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Virtual Currency</div>
              <div className={clsx(gamificationStyles.stats.value, "text-green-600 flex items-center")}>
                <CurrencyDollarIcon className="w-6 h-6 mr-2" />
                {userCurrency.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex gap-3 flex-wrap">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as RewardType | '')}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Types</option>
                <option value={RewardType.EXPERIENCE_POINTS}>Experience Points</option>
                <option value={RewardType.VIRTUAL_CURRENCY}>Virtual Currency</option>
                <option value={RewardType.BADGE}>Badges</option>
                <option value={RewardType.PREMIUM_FEATURE}>Premium Features</option>
                <option value={RewardType.COLLABORATION_BOOST}>Collaboration Boost</option>
                <option value={RewardType.REVENUE_MULTIPLIER}>Revenue Multiplier</option>
              </select>

              <select
                value={filterRarity}
                onChange={(e) => setFilterRarity(e.target.value as AchievementTier | '')}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Rarities</option>
                <option value={AchievementTier.BRONZE}>Bronze</option>
                <option value={AchievementTier.SILVER}>Silver</option>
                <option value={AchievementTier.GOLD}>Gold</option>
                <option value={AchievementTier.PLATINUM}>Platinum</option>
                <option value={AchievementTier.DIAMOND}>Diamond</option>
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                <option value="cost">Sort by Cost</option>
                <option value="rarity">Sort by Rarity</option>
                <option value="popularity">Sort by Popularity</option>
              </select>
            </div>

            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showAffordableOnly}
                  onChange={(e) => setShowAffordableOnly(e.target.checked)}
                  className={gamificationStyles.forms.checkbox}
                />
                <span className={clsx(gamificationStyles.typography.body.small, "ml-2")}>
                  Show only affordable
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Featured Rewards */}
        {featuredRewards.length > 0 && (
          <div className={clsx(gamificationStyles.container.section, "mb-6")}>
            <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4 flex items-center")}>
              <FireIcon className="w-6 h-6 mr-2 text-orange-500" />
              Featured Rewards
            </h2>
            <div className={gamificationStyles.grid.cols3}>
              {featuredRewards.map((reward) => (
                <div
                  key={reward.id}
                  className={clsx(
                    gamificationStyles.container.card,
                    "cursor-pointer transition-all duration-300 hover:shadow-lg ring-2 ring-orange-200"
                  )}
                  onClick={() => onRewardDetails?.(reward)}
                >
                  <div className="relative">
                    {isNewReward(reward) && (
                      <div className={clsx(gamificationStyles.badges.new, "absolute top-0 right-0")}>
                        New!
                      </div>
                    )}
                    {isPopular(reward) && (
                      <div className={clsx(gamificationStyles.badges.featured, "absolute top-0 left-0")}>
                        Popular
                      </div>
                    )}
                  </div>

                  <div className={clsx(
                    "w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center text-3xl",
                    gamificationStyles.achievementTiers[reward.rarity].bg
                  )}>
                    {reward.icon}
                  </div>

                  <h3 className={clsx(gamificationStyles.typography.body.large, "font-semibold text-center mb-2")}>
                    {reward.title}
                  </h3>
                  <p className={clsx(gamificationStyles.typography.body.small, "text-center mb-4")}>
                    {reward.description}
                  </p>

                  <div className="text-center mb-4">
                    <div className={clsx(gamificationStyles.typography.body.large, "font-bold text-orange-600")}>
                      {reward.cost?.toLocaleString() || 'Free'} {reward.currency || 'points'}
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePurchase(reward);
                    }}
                    disabled={purchasing === reward.id || !canAfford(reward)}
                    className={clsx(
                      gamificationStyles.buttons.primary,
                      "w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700",
                      !canAfford(reward) && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    {purchasing === reward.id ? (
                      <>
                        <div className={gamificationStyles.loading.spinner + " mr-2"} />
                        Purchasing...
                      </>
                    ) : canAfford(reward) ? (
                      <>
                        <ShoppingCartIcon className="w-4 h-4 mr-2" />
                        Purchase
                      </>
                    ) : (
                      'Insufficient Balance'
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Regular Rewards */}
        <div className={gamificationStyles.container.section}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            All Rewards
          </h2>
          <div className={gamificationStyles.grid.cols3}>
            {regularRewards.map((reward) => {
              const affordable = canAfford(reward);
              const isPurchasing = purchasing === reward.id;

              return (
                <div
                  key={reward.id}
                  className={clsx(
                    gamificationStyles.container.card,
                    "cursor-pointer transition-all duration-300",
                    affordable ? "hover:shadow-lg" : "opacity-75"
                  )}
                  onClick={() => onRewardDetails?.(reward)}
                >
                  <div className={gamificationStyles.utils.flexBetween + " mb-3"}>
                    <div className={clsx(
                      "flex items-center justify-center w-12 h-12 rounded-full text-2xl",
                      gamificationStyles.achievementTiers[reward.rarity].bg
                    )}>
                      {reward.icon}
                    </div>
                    <div className="text-right">
                      <div className={clsx(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        gamificationStyles.achievementTiers[reward.rarity].bg,
                        gamificationStyles.achievementTiers[reward.rarity].text
                      )}>
                        {reward.rarity.toUpperCase()}
                      </div>
                    </div>
                  </div>

                  <h3 className={clsx(gamificationStyles.typography.body.regular, "font-semibold mb-2")}>
                    {reward.title}
                  </h3>
                  <p className={clsx(gamificationStyles.typography.body.small, "mb-3")}>
                    {reward.description}
                  </p>

                  <div className="flex items-center justify-between text-sm mb-3">
                    <span className="text-slate-500 flex items-center">
                      {getRewardTypeIcon(reward.type)}
                      <span className="ml-1">Type:</span>
                    </span>
                    <span className="font-medium capitalize">
                      {reward.type.replace('_', ' ')}
                    </span>
                  </div>

                  {reward.cost && (
                    <div className="mb-3 text-center">
                      <div className={clsx(
                        gamificationStyles.typography.body.large,
                        "font-bold",
                        affordable ? "text-green-600" : "text-red-600"
                      )}>
                        {reward.cost.toLocaleString()} {reward.currency || 'points'}
                      </div>
                    </div>
                  )}

                  {reward.isLimited && reward.remainingQuantity !== undefined && (
                    <div className="mb-3 text-center">
                      <div className={clsx(
                        gamificationStyles.typography.body.small,
                        "text-orange-600"
                      )}>
                        Only {reward.remainingQuantity} left!
                      </div>
                    </div>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePurchase(reward);
                    }}
                    disabled={isPurchasing || !affordable}
                    className={clsx(
                      gamificationStyles.buttons.primary,
                      "w-full",
                      !affordable && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    {isPurchasing ? (
                      <>
                        <div className={gamificationStyles.loading.spinner + " mr-2"} />
                        Purchasing...
                      </>
                    ) : affordable ? (
                      <>
                        <ShoppingCartIcon className="w-4 h-4 mr-2" />
                        Purchase
                      </>
                    ) : (
                      'Insufficient Balance'
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {rewards.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🛍️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Rewards Available
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Check back later for new rewards and special offers.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RewardStore;