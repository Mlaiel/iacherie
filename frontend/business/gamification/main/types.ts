/**
 * Gamification System Types - Ultra-Advanced Enterprise System
 * 
 * This module provides comprehensive TypeScript types for the gamification system
 * with enterprise-grade type safety and professional structure.
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

export enum AchievementTier {
  BRONZE = 'bronze',
  SILVER = 'silver',
  GOLD = 'gold',
  PLATINUM = 'platinum',
  DIAMOND = 'diamond'
}

export enum ChallengeType {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  SEASONAL = 'seasonal',
  SPECIAL = 'special'
}

export enum ChallengeStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  PENDING = 'pending'
}

export enum RewardType {
  EXPERIENCE_POINTS = 'experience_points',
  VIRTUAL_CURRENCY = 'virtual_currency',
  BADGE = 'badge',
  PREMIUM_FEATURE = 'premium_feature',
  COLLABORATION_BOOST = 'collaboration_boost',
  REVENUE_MULTIPLIER = 'revenue_multiplier'
}

export interface UserProgress {
  userId: string;
  level: number;
  experiencePoints: number;
  achievementsUnlocked: string[];
  challengesCompleted: string[];
  rank: number;
  totalRewardsEarned: number;
  currentStreak: number;
  longestStreak: number;
  collaborationScore: number;
  contentQualityScore: number;
  engagementScore: number;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  tier: AchievementTier;
  icon: string;
  requirements: Record<string, any>;
  rewards: Record<string, any>;
  isUnlocked: boolean;
  unlockedAt?: Date;
  progress: number;
  maxProgress: number;
  category: string;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  type: ChallengeType;
  status: ChallengeStatus;
  startDate: Date;
  endDate: Date;
  requirements: Record<string, any>;
  rewards: Record<string, any>;
  participants: string[];
  completedBy: string[];
  difficulty: number;
  estimatedTime: string;
  category: string;
  maxParticipants?: number;
}

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  username: string;
  avatar: string;
  score: number;
  level: number;
  achievementCount: number;
  change: number; // Change in rank since last update
  isCurrentUser: boolean;
}

export interface Leaderboard {
  id: string;
  title: string;
  description: string;
  entries: LeaderboardEntry[];
  lastUpdated: Date;
  timeframe: 'daily' | 'weekly' | 'monthly' | 'all_time';
  category: string;
}

export interface Reward {
  id: string;
  type: RewardType;
  title: string;
  description: string;
  value: number;
  icon: string;
  rarity: AchievementTier;
  cost?: number;
  currency?: string;
  expiresAt?: Date;
  isRedeemable: boolean;
  isLimited: boolean;
  remainingQuantity?: number;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: AchievementTier;
  earnedAt?: Date;
  isRare: boolean;
  category: string;
}

export interface Competition {
  id: string;
  title: string;
  description: string;
  startDate: Date;
  endDate: Date;
  participants: string[];
  winners: string[];
  prizes: Reward[];
  rules: string[];
  category: string;
  status: 'upcoming' | 'active' | 'completed' | 'cancelled';
  maxParticipants?: number;
  entryFee?: number;
  prizePool: number;
}

export interface EngagementMetrics {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  averageSessionDuration: number;
  challengeCompletionRate: number;
  achievementUnlockRate: number;
  collaborationParticipationRate: number;
  contentQualityTrend: number[];
  userRetentionRate: number;
  socialInteractionRate: number;
}

export interface VirtualEconomyStats {
  totalCurrencyInCirculation: number;
  averageCurrencyPerUser: number;
  dailyTransactions: number;
  popularItems: string[];
  economyHealthScore: number;
  inflationRate: number;
  userSpendingPower: number;
}

export interface GamificationDashboardData {
  userProgress: UserProgress;
  activeChallenges: Challenge[];
  recentAchievements: Achievement[];
  leaderboardPosition: LeaderboardEntry;
  availableRewards: Reward[];
  upcomingCompetitions: Competition[];
  engagementMetrics: EngagementMetrics;
  recommendations: string[];
}

export interface ChallengeCreatorData {
  title: string;
  description: string;
  type: ChallengeType;
  duration: number;
  requirements: Record<string, any>;
  rewards: Record<string, any>;
  category: string;
  difficulty: number;
  maxParticipants?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface FilterOptions {
  category?: string;
  difficulty?: number;
  timeframe?: string;
  status?: string;
  tier?: AchievementTier;
  type?: ChallengeType;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}