/**
 * Gamification Main Page - App Router format
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
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

export default function GamificationPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'progress' | 'achievements' | 'rewards' | 'competitions' | 'badges'>('dashboard');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <GamificationDashboard
            userId="current-user"
            onChallengeClick={() => {}}
            onAchievementClick={() => {}}
            onLeaderboardClick={() => router.push('/gamification/leaderboards')}
            onRewardClick={() => {}}
          />
        );
      default:
        return <div>Gamification content</div>;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Gamification Dashboard</h1>
      {renderActiveTab()}
    </div>
  );
}