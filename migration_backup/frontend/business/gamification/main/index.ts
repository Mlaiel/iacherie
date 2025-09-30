/**
 * Gamification Components - Ultra-Advanced Enterprise System
 * 
 * This module provides comprehensive gamification component exports with
 * enterprise-grade architecture and professional structure.
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

// Core Types and Interfaces
export * from './types';

// Styling System
export { gamificationStyles, tierIcons, challengeIcons, difficultyColors, getDifficultyLabel } from './gamification.styles';

// Import all components first
import GamificationDashboard from './GamificationDashboard';
import ChallengeInterface from '../challenges_components/ChallengeInterface';
import LeaderboardComponent from '../social_components/LeaderboardComponent';
import SocialCompetitions from '../social_components/SocialCompetitions';
import AchievementPanel from '../achievements_components/AchievementPanel';
import RewardSystem from './RewardSystem';
import ProgressTracker from '../achievements_components/ProgressTracker';
import BadgeCollection from '../achievements_components/BadgeCollection';
import VirtualEconomy from '../social_components/VirtualEconomy';
import ChallengeCreator from '../challenges_components/ChallengeCreator';
import CompetitionCalendar from '../challenges_components/CompetitionCalendar';
import EngagementMetrics from './EngagementMetrics';
import RewardStore from './RewardStore';

// Export all components
export { 
  GamificationDashboard,
  ChallengeInterface,
  LeaderboardComponent,
  SocialCompetitions,
  AchievementPanel,
  RewardSystem,
  ProgressTracker,
  BadgeCollection,
  VirtualEconomy,
  ChallengeCreator,
  CompetitionCalendar,
  EngagementMetrics,
  RewardStore
};

// Re-export component prop types for external usage - Defined inline for type safety
export interface GamificationDashboardProps {
  userId: string;
  className?: string;
  onChallengeClick?: (challenge: any) => void;
  onAchievementClick?: (achievement: any) => void;
  onLeaderboardClick?: () => void;
  onRewardClick?: (reward: any) => void;
}

export interface ChallengeInterfaceProps {
  userId: string;
  className?: string;
  onChallengeJoin?: (challengeId: string) => Promise<void>;
  onChallengeLeave?: (challengeId: string) => Promise<void>;
  onChallengeDetails?: (challenge: any) => void;
}

export interface LeaderboardComponentProps {
  userId: string;
  className?: string;
  initialTimeframe?: 'daily' | 'weekly' | 'monthly' | 'all_time';
  initialCategory?: string;
  onUserSelect?: (userId: string) => void;
  showUserHighlight?: boolean;
  maxEntries?: number;
}

export interface AchievementPanelProps {
  userId: string;
  className?: string;
  onAchievementClick?: (achievement: any) => void;
  showUnlockedOnly?: boolean;
  showProgress?: boolean;
  maxDisplay?: number;
}

export interface RewardSystemProps {
  userId: string;
  userPoints: number;
  userCurrency: number;
  className?: string;
  onRewardRedeem?: (rewardId: string) => Promise<boolean>;
  onRewardDetails?: (reward: any) => void;
  showRedeemed?: boolean;
}

export interface ProgressTrackerProps {
  userId: string;
  className?: string;
  timeframe?: 'week' | 'month' | 'quarter' | 'year';
  showProjections?: boolean;
  showComparisons?: boolean;
}

export interface SocialCompetitionsProps {
  userId: string;
  className?: string;
  onCompetitionJoin?: (competitionId: string) => Promise<boolean>;
  onCompetitionDetails?: (competition: any) => void;
  showCompleted?: boolean;
}

// Utility functions for gamification system
export const GamificationUtils = {
  /**
   * Calculate level from experience points
   */
  calculateLevel: (experiencePoints: number): number => {
    return Math.floor(Math.sqrt(experiencePoints / 1000)) + 1;
  },

  /**
   * Calculate experience points needed for next level
   */
  calculateExperienceToNextLevel: (currentLevel: number): number => {
    const nextLevelXP = Math.pow(currentLevel, 2) * 1000;
    return nextLevelXP;
  },

  /**
   * Format large numbers with abbreviations
   */
  formatNumber: (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  },

  /**
   * Calculate progress percentage
   */
  calculateProgress: (current: number, target: number): number => {
    if (target === 0) return 0;
    return Math.min((current / target) * 100, 100);
  },

  /**
   * Format time duration
   */
  formatDuration: (milliseconds: number): string => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  },

  /**
   * Validate user eligibility for challenges
   */
  checkChallengeEligibility: (userLevel: number, requiredLevel: number): boolean => {
    return userLevel >= requiredLevel;
  },

  /**
   * Calculate tier score for achievements
   */
  calculateTierScore: (tier: string): number => {
    const tierValues = {
      bronze: 1,
      silver: 2,
      gold: 5,
      platinum: 10,
      diamond: 25
    };
    return tierValues[tier.toLowerCase() as keyof typeof tierValues] || 0;
  }
};

// Default export for convenience
export default {
  GamificationDashboard,
  ChallengeInterface,
  LeaderboardComponent,
  AchievementPanel,
  RewardSystem,
  ProgressTracker,
  SocialCompetitions,
  BadgeCollection,
  VirtualEconomy,
  ChallengeCreator,
  CompetitionCalendar,
  EngagementMetrics,
  RewardStore,
  Utils: GamificationUtils
};