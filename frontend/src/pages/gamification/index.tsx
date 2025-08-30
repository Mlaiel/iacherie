/**
 * Gamification Main Page - Ultra-Advanced Enterprise System
 * 
 * This page provides the main gamification interface with comprehensive
 * dashboard and navigation to all gamification features.
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

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  GamificationDashboard,
  ProgressTracker,
  AchievementPanel,
  RewardSystem,
  SocialCompetitions,
  BadgeCollection
} from '@/components/gamification';
import { Challenge, Achievement, Reward, Competition } from '@/components/gamification/types';
import { gamificationStyles } from '@/components/gamification/gamification.styles';
import { 
  TrophyIcon,
  ChartBarIcon,
  StarIcon,
  GiftIcon,
  UsersIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface GamificationPageProps {
  params?: { userId?: string };
}

const GamificationPage: React.FC<GamificationPageProps> = ({ params }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'progress' | 'achievements' | 'rewards' | 'competitions' | 'badges'>('dashboard');
  const [userId, setUserId] = useState<string>('');
  const [userPoints, setUserPoints] = useState<number>(5420);
  const [userCurrency, setUserCurrency] = useState<number>(1250);

  useEffect(() => {
    // Get user ID from params or authentication context
    const currentUserId = params?.userId || 'current-user-id';
    setUserId(currentUserId);
  }, [params]);

  const handleChallengeClick = (challenge: Challenge) => {
    router.push(`/gamification/challenges?id=${challenge.id}`);
  };

  const handleAchievementClick = (achievement: Achievement) => {
    console.log('Achievement clicked:', achievement);
    // Could open a modal or navigate to achievement details
  };

  const handleLeaderboardClick = () => {
    router.push('/gamification/leaderboards');
  };

  const handleRewardClick = (reward: Reward) => {
    console.log('Reward clicked:', reward);
    // Could open reward details modal
  };

  const handleRewardRedeem = async (rewardId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/gamification/rewards/${rewardId}/redeem`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ userId })
      });

      if (response.ok) {
        // Update user currency/points
        const result = await response.json();
        if (result.success) {
          setUserPoints(prev => prev - (result.pointsCost || 0));
          setUserCurrency(prev => prev - (result.currencyCost || 0));
          return true;
        }
      }
      return false;
    } catch (err) {
      console.error('Failed to redeem reward:', err);
      return false;
    }
  };

  const handleCompetitionJoin = async (competitionId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/gamification/competitions/${competitionId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ userId })
      });

      return response.ok;
    } catch (err) {
      console.error('Failed to join competition:', err);
      return false;
    }
  };

  const handleCompetitionDetails = (competition: Competition) => {
    console.log('Competition details:', competition);
    // Could open competition details modal or navigate
  };

  const tabs = [
    {
      id: 'dashboard' as const,
      label: 'Dashboard',
      icon: TrophyIcon,
      description: 'Overview of your progress'
    },
    {
      id: 'progress' as const,
      label: 'Progress',
      icon: ChartBarIcon,
      description: 'Track your growth'
    },
    {
      id: 'achievements' as const,
      label: 'Achievements',
      icon: StarIcon,
      description: 'Unlock milestones'
    },
    {
      id: 'rewards' as const,
      label: 'Rewards',
      icon: GiftIcon,
      description: 'Redeem your points'
    },
    {
      id: 'competitions' as const,
      label: 'Competitions',
      icon: UsersIcon,
      description: 'Compete with others'
    },
    {
      id: 'badges' as const,
      label: 'Badges',
      icon: ShieldCheckIcon,
      description: 'Showcase achievements'
    }
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <GamificationDashboard
            userId={userId}
            onChallengeClick={handleChallengeClick}
            onAchievementClick={handleAchievementClick}
            onLeaderboardClick={handleLeaderboardClick}
            onRewardClick={handleRewardClick}
          />
        );
      case 'progress':
        return (
          <ProgressTracker
            userId={userId}
            timeframe="month"
            showProjections={true}
            showComparisons={false}
          />
        );
      case 'achievements':
        return (
          <AchievementPanel
            userId={userId}
            onAchievementClick={handleAchievementClick}
            showUnlockedOnly={false}
            showProgress={true}
            maxDisplay={50}
          />
        );
      case 'rewards':
        return (
          <RewardSystem
            userId={userId}
            userPoints={userPoints}
            userCurrency={userCurrency}
            onRewardRedeem={handleRewardRedeem}
            onRewardDetails={handleRewardClick}
            showRedeemed={true}
          />
        );
      case 'competitions':
        return (
          <SocialCompetitions
            userId={userId}
            onCompetitionJoin={handleCompetitionJoin}
            onCompetitionDetails={handleCompetitionDetails}
            showCompleted={false}
          />
        );
      case 'badges':
        return (
          <BadgeCollection
            userId={userId}
            showEarnedOnly={false}
          />
        );
      default:
        return null;
    }
  };

  if (!userId) {
    return (
      <div className={gamificationStyles.container.main}>
        <div className="max-w-2xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className={gamificationStyles.loading.spinner + " w-8 h-8 mx-auto mb-4"} />
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Loading Gamification System...
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Preparing your creator journey dashboard
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={gamificationStyles.container.main}>
      <div className="max-w-7xl mx-auto">
        {/* Navigation Tabs */}
        <div className="border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 sticky top-0 z-10">
          <div className="px-6">
            <nav className="flex space-x-8 overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={clsx(
                      "flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors duration-200",
                      activeTab === tab.id
                        ? "border-blue-500 text-blue-600 dark:text-blue-400"
                        : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300"
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Description */}
        <div className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-3">
            <p className={clsx(gamificationStyles.typography.body.small, "text-slate-600 dark:text-slate-400")}>
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </div>

        {/* Active Tab Content */}
        <div className="min-h-screen">
          {renderActiveTab()}
        </div>
      </div>
    </div>
  );
};

export default GamificationPage;