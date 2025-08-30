/**
 * Reward System - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive reward management with real-time
 * redemption tracking and intelligent reward recommendations.
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
  Reward, 
  RewardType,
  AchievementTier,
  ApiResponse,
  PaginatedResponse
} from './types';
import { gamificationStyles } from './gamification.styles';
import { 
  GiftIcon,
  SparklesIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

export interface RewardSystemProps {
  userId: string;
  userPoints: number;
  userCurrency: number;
  className?: string;
  onRewardRedeem?: (rewardId: string) => Promise<boolean>;
  onRewardDetails?: (reward: Reward) => void;
  showRedeemed?: boolean;
}

interface RedemptionHistory {
  id: string;
  rewardId: string;
  redeemedAt: Date;
  cost: number;
  status: 'completed' | 'pending' | 'failed';
}

const RewardSystem: React.FC<RewardSystemProps> = ({
  userId,
  userPoints,
  userCurrency,
  className,
  onRewardRedeem,
  onRewardDetails,
  showRedeemed = false
}) => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [redemptionHistory, setRedemptionHistory] = useState<RedemptionHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [redeemingId, setRedeemingId] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<RewardType | ''>('');
  const [selectedRarity, setSelectedRarity] = useState<AchievementTier | ''>('');
  const [sortBy, setSortBy] = useState<'cost' | 'rarity' | 'expiry' | 'title'>('cost');
  const [showOnlyAffordable, setShowOnlyAffordable] = useState(false);

  const fetchRewards = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [rewardsResponse, historyResponse] = await Promise.all([
        fetch(`/api/gamification/rewards?userId=${userId}&available=true`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        }),
        fetch(`/api/gamification/rewards/history?userId=${userId}&limit=20`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        })
      ]);

      if (!rewardsResponse.ok || !historyResponse.ok) {
        throw new Error('Failed to fetch rewards data');
      }

      const [rewardsResult, historyResult] = await Promise.all([
        rewardsResponse.json() as Promise<ApiResponse<PaginatedResponse<Reward>>>,
        historyResponse.json() as Promise<ApiResponse<RedemptionHistory[]>>
      ]);

      if (!rewardsResult.success || !historyResult.success) {
        throw new Error('Failed to load rewards data');
      }

      setRewards(rewardsResult.data!.items);
      setRedemptionHistory(historyResult.data!);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Rewards fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchRewards();
  }, [fetchRewards]);

  const handleRewardRedeem = async (reward: Reward) => {
    if (!onRewardRedeem || redeemingId || !canAfford(reward)) return;

    try {
      setRedeemingId(reward.id);
      const success = await onRewardRedeem(reward.id);
      
      if (success) {
        // Update local state
        setRewards(prev => prev.map(r => 
          r.id === reward.id && r.isLimited && r.remainingQuantity
            ? { ...r, remainingQuantity: r.remainingQuantity - 1 }
            : r
        ));
        
        // Add to redemption history
        const newRedemption: RedemptionHistory = {
          id: `temp_${Date.now()}`,
          rewardId: reward.id,
          redeemedAt: new Date(),
          cost: reward.cost || 0,
          status: 'completed'
        };
        setRedemptionHistory(prev => [newRedemption, ...prev]);
      }
    } catch (err) {
      console.error('Failed to redeem reward:', err);
    } finally {
      setRedeemingId(null);
    }
  };

  const canAfford = (reward: Reward): boolean => {
    if (!reward.cost) return true;
    return reward.currency === 'points' ? userPoints >= reward.cost : userCurrency >= reward.cost;
  };

  const isExpiringSoon = (reward: Reward): boolean => {
    if (!reward.expiresAt) return false;
    const now = new Date();
    const expiry = new Date(reward.expiresAt);
    const hoursUntilExpiry = (expiry.getTime() - now.getTime()) / (1000 * 60 * 60);
    return hoursUntilExpiry <= 24 && hoursUntilExpiry > 0;
  };

  const isExpired = (reward: Reward): boolean => {
    if (!reward.expiresAt) return false;
    return new Date() > new Date(reward.expiresAt);
  };

  const getFilteredRewards = () => {
    let filtered = rewards.filter(reward => {
      // Type filter
      if (selectedType && reward.type !== selectedType) return false;
      
      // Rarity filter
      if (selectedRarity && reward.rarity !== selectedRarity) return false;
      
      // Affordable filter
      if (showOnlyAffordable && !canAfford(reward)) return false;
      
      // Expired filter
      if (isExpired(reward)) return false;

      return true;
    });

    // Sort rewards
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'cost':
          return (a.cost || 0) - (b.cost || 0);
        case 'rarity':
          const rarityOrder = {
            [AchievementTier.BRONZE]: 1,
            [AchievementTier.SILVER]: 2,
            [AchievementTier.GOLD]: 3,
            [AchievementTier.PLATINUM]: 4,
            [AchievementTier.DIAMOND]: 5
          };
          return rarityOrder[b.rarity] - rarityOrder[a.rarity];
        case 'expiry':
          if (!a.expiresAt && !b.expiresAt) return 0;
          if (!a.expiresAt) return 1;
          if (!b.expiresAt) return -1;
          return new Date(a.expiresAt).getTime() - new Date(b.expiresAt).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

    return filtered;
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
        return <CheckCircleIcon className="w-5 h-5" />;
      case RewardType.COLLABORATION_BOOST:
        return <GiftIcon className="w-5 h-5" />;
      case RewardType.REVENUE_MULTIPLIER:
        return <CurrencyDollarIcon className="w-5 h-5" />;
      default:
        return <GiftIcon className="w-5 h-5" />;
    }
  };

  const formatTimeRemaining = (expiresAt: Date): string => {
    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h`;
  };

  const filteredRewards = getFilteredRewards();
  const totalRedeemed = redemptionHistory.filter(r => r.status === 'completed').length;
  const totalSpent = redemptionHistory
    .filter(r => r.status === 'completed')
    .reduce((sum, r) => sum + r.cost, 0);

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols3}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-6 w-32 mb-3"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-full mb-2"} />
                <div className={gamificationStyles.loading.skeleton + " h-10 w-full"} />
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
                Failed to Load Rewards
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={fetchRewards}
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
            <GiftIcon className="w-8 h-8 mr-3 text-purple-500" />
            Reward Center
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Redeem your points and currency for exclusive rewards and premium features
          </p>
        </div>

        {/* User Balance & Stats */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <h2 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
            Your Balance & Activity
          </h2>
          <div className={gamificationStyles.grid.cols4}>
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

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Total Redeemed</div>
              <div className={clsx(gamificationStyles.stats.value, "text-purple-600")}>
                {totalRedeemed}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Lifetime rewards
              </div>
            </div>

            <div className={gamificationStyles.stats.card}>
              <div className={gamificationStyles.stats.label}>Total Spent</div>
              <div className={clsx(gamificationStyles.stats.value, "text-orange-600")}>
                {totalSpent.toLocaleString()}
              </div>
              <div className={gamificationStyles.typography.body.small}>
                Points & currency
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex gap-3 flex-wrap">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value as RewardType | '')}
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
                value={selectedRarity}
                onChange={(e) => setSelectedRarity(e.target.value as AchievementTier | '')}
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
                <option value="expiry">Sort by Expiry</option>
                <option value="title">Sort by Name</option>
              </select>
            </div>

            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showOnlyAffordable}
                  onChange={(e) => setShowOnlyAffordable(e.target.checked)}
                  className={gamificationStyles.forms.checkbox}
                />
                <span className={clsx(gamificationStyles.typography.body.small, "ml-2")}>
                  Show only affordable
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Rewards Grid */}
        <div className={gamificationStyles.grid.cols3}>
          {filteredRewards.map((reward) => {
            const affordable = canAfford(reward);
            const expiringSoon = isExpiringSoon(reward);
            const expired = isExpired(reward);
            const isRedeeming = redeemingId === reward.id;

            return (
              <div
                key={reward.id}
                className={clsx(
                  gamificationStyles.container.card,
                  "transition-all duration-300",
                  affordable ? "hover:shadow-lg cursor-pointer" : "opacity-50",
                  expiringSoon && "ring-2 ring-yellow-400",
                  expired && "grayscale"
                )}
                onClick={() => onRewardDetails?.(reward)}
              >
                {/* Header */}
                <div className={gamificationStyles.utils.flexBetween + " mb-3"}>
                  <div className={clsx(
                    "flex items-center justify-center w-12 h-12 rounded-full",
                    gamificationStyles.achievementTiers[reward.rarity].bg
                  )}>
                    <span className="text-2xl">{reward.icon}</span>
                  </div>
                  <div className="text-right">
                    {expiringSoon && (
                      <div className={clsx(gamificationStyles.badges.limited, "mb-1")}>
                        ⏰ Expiring Soon
                      </div>
                    )}
                    {reward.isLimited && (
                      <div className={gamificationStyles.badges.limited}>
                        Limited
                      </div>
                    )}
                  </div>
                </div>

                {/* Content */}
                <h3 className={clsx(gamificationStyles.typography.body.large, "font-semibold mb-2")}>
                  {reward.title}
                </h3>
                <p className={clsx(gamificationStyles.typography.body.small, "mb-3")}>
                  {reward.description}
                </p>

                {/* Metadata */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 flex items-center">
                      {getRewardTypeIcon(reward.type)}
                      <span className="ml-1">Type:</span>
                    </span>
                    <span className="font-medium capitalize">
                      {reward.type.replace('_', ' ')}
                    </span>
                  </div>

                  {reward.cost && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">Cost:</span>
                      <span className={clsx(
                        "font-bold",
                        affordable ? "text-green-600" : "text-red-600"
                      )}>
                        {reward.cost.toLocaleString()} {reward.currency || 'points'}
                      </span>
                    </div>
                  )}

                  {reward.isLimited && reward.remainingQuantity !== undefined && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">Remaining:</span>
                      <span className={clsx(
                        "font-medium",
                        reward.remainingQuantity > 10 ? "text-green-600" : "text-red-600"
                      )}>
                        {reward.remainingQuantity} left
                      </span>
                    </div>
                  )}

                  {reward.expiresAt && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500 flex items-center">
                        <ClockIcon className="w-4 h-4 mr-1" />
                        Expires:
                      </span>
                      <span className={clsx(
                        "font-medium",
                        expiringSoon ? "text-yellow-600" : "text-slate-700"
                      )}>
                        {formatTimeRemaining(reward.expiresAt)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Action Button */}
                <div className="mt-auto">
                  {expired ? (
                    <button
                      disabled
                      className={clsx(gamificationStyles.buttons.secondary, "w-full cursor-not-allowed opacity-60")}
                    >
                      Expired
                    </button>
                  ) : !affordable ? (
                    <button
                      disabled
                      className={clsx(gamificationStyles.buttons.secondary, "w-full cursor-not-allowed opacity-60")}
                    >
                      Insufficient Balance
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRewardRedeem(reward);
                      }}
                      disabled={isRedeeming || !reward.isRedeemable}
                      className={clsx(
                        gamificationStyles.buttons.primary,
                        "w-full",
                        isRedeeming && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      {isRedeeming ? (
                        <>
                          <div className={gamificationStyles.loading.spinner + " mr-2"} />
                          Redeeming...
                        </>
                      ) : (
                        <>
                          <GiftIcon className="w-4 h-4 mr-2" />
                          Redeem Now
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Recent Redemptions */}
        {showRedeemed && redemptionHistory.length > 0 && (
          <div className={clsx(gamificationStyles.container.section, "mt-8")}>
            <h3 className={clsx(gamificationStyles.typography.heading.tertiary, "mb-4")}>
              Recent Redemptions
            </h3>
            <div className="space-y-2">
              {redemptionHistory.slice(0, 5).map((redemption) => {
                const reward = rewards.find(r => r.id === redemption.rewardId);
                
                return (
                  <div
                    key={redemption.id}
                    className={clsx(
                      gamificationStyles.container.compactCard,
                      "flex items-center justify-between"
                    )}
                  >
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                        {reward ? (
                          <span className="text-lg">{reward.icon}</span>
                        ) : (
                          <GiftIcon className="w-5 h-5 text-purple-600" />
                        )}
                      </div>
                      <div>
                        <div className={gamificationStyles.typography.body.regular}>
                          {reward?.title || 'Unknown Reward'}
                        </div>
                        <div className={gamificationStyles.typography.body.small}>
                          {new Date(redemption.redeemedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={clsx(
                        gamificationStyles.typography.body.regular,
                        "font-medium text-purple-600"
                      )}>
                        -{redemption.cost.toLocaleString()}
                      </div>
                      <div className={clsx(
                        "text-xs px-2 py-1 rounded-full",
                        redemption.status === 'completed' && "bg-green-100 text-green-800",
                        redemption.status === 'pending' && "bg-yellow-100 text-yellow-800",
                        redemption.status === 'failed' && "bg-red-100 text-red-800"
                      )}>
                        {redemption.status}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* No Results */}
        {!loading && filteredRewards.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎁</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Rewards Available
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                No rewards match your current criteria. Try adjusting your filters or check back later for new rewards.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RewardSystem;