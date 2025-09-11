/**
 * 🎮 Gamification Components - Central Export Hub
 * 
 * @fileoverview Re-exports all gamification components from business layer
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// Main gamification components
export { default as GamificationDashboard } from '@/business/gamification/main/GamificationDashboard';
export { default as RewardSystem } from '@/business/gamification/main/RewardSystem';
export { default as EngagementMetrics } from '@/business/gamification/main/EngagementMetrics';
export { default as RewardStore } from '@/business/gamification/main/RewardStore';

// Achievement components
export { default as AchievementPanel } from '@/business/gamification/achievements_components/AchievementPanel';
export { default as BadgeCollection } from '@/business/gamification/achievements_components/BadgeCollection';
export { default as ProgressTracker } from '@/business/gamification/achievements_components/ProgressTracker';

// Social components
export { default as SocialCompetitions } from '@/business/gamification/social_components/SocialCompetitions';
export { default as LeaderboardComponent } from '@/business/gamification/social_components/LeaderboardComponent';
export { default as VirtualEconomy } from '@/business/gamification/social_components/VirtualEconomy';

// Challenge components (if they exist)
export { default as ChallengeCreator } from '@/business/gamification/challenges_components/ChallengeCreator';
export { default as ChallengeInterface } from '@/business/gamification/challenges_components/ChallengeInterface';
export { default as CompetitionCalendar } from '@/business/gamification/challenges_components/CompetitionCalendar';