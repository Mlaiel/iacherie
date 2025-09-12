/**
 * 🏆 Gamification Achievements Enterprise - Creator Motivation System
 * 
 * @fileoverview Advanced achievement and progression system for content creators
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

export interface Achievement {
  id: string;
  name: string;
  description: string;
  category: AchievementCategory;
  type: AchievementType;
  rarity: AchievementRarity;
  requirements: AchievementRequirement[];
  rewards: AchievementReward[];
  icon: string;
  badge: string;
  points: number;
  isSecret: boolean;
  isRepeatable: boolean;
  prerequisites?: string[]; // Other achievement IDs
  metadata: AchievementMetadata;
  createdAt: number;
  updatedAt: number;
}

export type AchievementCategory = 
  | 'content_creation' 
  | 'audience_engagement' 
  | 'collaboration' 
  | 'monetization' 
  | 'platform_mastery' 
  | 'community_building' 
  | 'technical_skills' 
  | 'creativity' 
  | 'consistency' 
  | 'innovation';

export type AchievementType = 
  | 'milestone' 
  | 'streak' 
  | 'threshold' 
  | 'completion' 
  | 'challenge' 
  | 'social' 
  | 'seasonal' 
  | 'special_event';

export type AchievementRarity = 
  | 'common' 
  | 'uncommon' 
  | 'rare' 
  | 'epic' 
  | 'legendary' 
  | 'mythic';

export interface AchievementRequirement {
  type: 'metric' | 'action' | 'condition' | 'timeframe';
  metric?: string; // e.g., 'views', 'likes', 'uploads'
  operator: 'equals' | 'greater_than' | 'less_than' | 'between' | 'exists';
  value: number | string | { min: number; max: number };
  timeframe?: {
    duration: number; // milliseconds
    window: 'rolling' | 'fixed';
    startDate?: number;
  };
}

export interface AchievementReward {
  type: 'points' | 'badge' | 'title' | 'feature_unlock' | 'premium_time' | 'currency' | 'boost';
  value: number | string;
  duration?: number; // For temporary rewards
  description: string;
}

export interface AchievementMetadata {
  difficulty: number; // 1-10
  estimatedTime: number; // minutes to complete
  completionRate: number; // percentage of users who complete
  tags: string[];
  seasonalEvent?: string;
  version: string;
}

export interface UserAchievement {
  achievementId: string;
  userId: string;
  progress: AchievementProgress;
  unlockedAt?: number;
  claimed: boolean;
  claimedAt?: number;
  notified: boolean;
  streak?: StreakData;
}

export interface AchievementProgress {
  current: number;
  required: number;
  percentage: number;
  milestones: ProgressMilestone[];
  lastUpdated: number;
}

export interface ProgressMilestone {
  threshold: number;
  reached: boolean;
  reachedAt?: number;
  reward?: AchievementReward;
}

export interface StreakData {
  count: number;
  startDate: number;
  lastActivityDate: number;
  longestStreak: number;
  broken: boolean;
  brokenAt?: number;
}

export interface LeaderboardEntry {
  userId: string;
  userName: string;
  rank: number;
  points: number;
  achievementsCount: number;
  rareAchievements: number;
  avatar?: string;
  badges: string[];
  level: number;
}

export interface CreatorLevel {
  level: number;
  name: string;
  minPoints: number;
  maxPoints: number;
  benefits: LevelBenefit[];
  icon: string;
  color: string;
}

export interface LevelBenefit {
  type: 'feature' | 'discount' | 'priority' | 'exclusive' | 'boost';
  name: string;
  description: string;
  value?: number;
  permanent: boolean;
}

export interface Challenge {
  id: string;
  name: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly' | 'seasonal' | 'special';
  category: AchievementCategory;
  requirements: AchievementRequirement[];
  rewards: AchievementReward[];
  startDate: number;
  endDate: number;
  participantsCount: number;
  completionsCount: number;
  isActive: boolean;
  difficulty: number;
}

export interface UserChallenge {
  challengeId: string;
  userId: string;
  startedAt: number;
  progress: AchievementProgress;
  completed: boolean;
  completedAt?: number;
  rewards: AchievementReward[];
  claimed: boolean;
}

/**
 * Gamification Achievements Engine
 * Advanced achievement and progression system
 */
export class GamificationAchievementsEngine {
  private achievements = new Map<string, Achievement>();
  private userAchievements = new Map<string, UserAchievement[]>(); // userId -> achievements
  private leaderboards = new Map<string, LeaderboardEntry[]>();
  private challenges = new Map<string, Challenge>();
  private userChallenges = new Map<string, UserChallenge[]>(); // userId -> challenges
  private levels: CreatorLevel[] = [];

  /**
   * Initialize achievement system
   */
  async initialize(): Promise<void> {
    await this.loadDefaultAchievements();
    await this.loadCreatorLevels();
    await this.loadActiveChallenges();
    await this.updateLeaderboards();
  }

  /**
   * Track user activity and update achievements
   */
  async trackActivity(
    userId: string,
    activityType: string,
    value: number,
    metadata?: Record<string, any>
  ): Promise<void> {
    const userAchievements = this.userAchievements.get(userId) || [];
    const newUnlocks: string[] = [];

    // Check all achievements for progress updates
    for (const achievement of this.achievements.values()) {
      let userAchievement = userAchievements.find(ua => ua.achievementId === achievement.id);
      
      if (!userAchievement) {
        userAchievement = {
          achievementId: achievement.id,
          userId,
          progress: {
            current: 0,
            required: this.calculateRequiredValue(achievement.requirements),
            percentage: 0,
            milestones: [],
            lastUpdated: Date.now(),
          },
          claimed: false,
          notified: false,
        };
        userAchievements.push(userAchievement);
      }

      // Skip if already unlocked
      if (userAchievement.unlockedAt) continue;

      // Check if activity matches achievement requirements
      const progressUpdate = await this.calculateProgressUpdate(
        achievement,
        userAchievement,
        activityType,
        value,
        metadata
      );

      if (progressUpdate > 0) {
        userAchievement.progress.current += progressUpdate;
        userAchievement.progress.percentage = Math.min(
          100,
          (userAchievement.progress.current / userAchievement.progress.required) * 100
        );
        userAchievement.progress.lastUpdated = Date.now();

        // Check for milestone rewards
        this.checkMilestones(userAchievement, achievement);

        // Check if achievement is now complete
        if (userAchievement.progress.current >= userAchievement.progress.required) {
          userAchievement.unlockedAt = Date.now();
          newUnlocks.push(achievement.id);

          // Update streak data if applicable
          if (achievement.type === 'streak') {
            this.updateStreakData(userAchievement, true);
          }
        }
      }
    }

    // Update user achievements
    this.userAchievements.set(userId, userAchievements);

    // Process new unlocks
    if (newUnlocks.length > 0) {
      await this.processAchievementUnlocks(userId, newUnlocks);
    }

    // Update challenges
    await this.updateChallengeProgress(userId, activityType, value, metadata);
  }

  /**
   * Get user's achievements
   */
  getUserAchievements(userId: string): UserAchievement[] {
    return this.userAchievements.get(userId) || [];
  }

  /**
   * Get user's unlocked achievements only
   */
  getUserUnlockedAchievements(userId: string): UserAchievement[] {
    const userAchievements = this.getUserAchievements(userId);
    return userAchievements.filter(ua => ua.unlockedAt);
  }

  /**
   * Get user's achievement statistics
   */
  getUserStats(userId: string): {
    totalPoints: number;
    achievementsUnlocked: number;
    achievementsTotal: number;
    completionRate: number;
    rareAchievements: number;
    level: CreatorLevel;
    nextLevel?: CreatorLevel;
    pointsToNextLevel: number;
  } {
    const userAchievements = this.getUserAchievements(userId);
    const unlockedAchievements = userAchievements.filter(ua => ua.unlockedAt);
    
    const totalPoints = unlockedAchievements.reduce((sum, ua) => {
      const achievement = this.achievements.get(ua.achievementId);
      return sum + (achievement?.points || 0);
    }, 0);

    const rareAchievements = unlockedAchievements.filter(ua => {
      const achievement = this.achievements.get(ua.achievementId);
      return achievement && ['rare', 'epic', 'legendary', 'mythic'].includes(achievement.rarity);
    }).length;

    const level = this.getUserLevel(totalPoints);
    const nextLevel = this.levels.find(l => l.level === level.level + 1);
    const pointsToNextLevel = nextLevel ? nextLevel.minPoints - totalPoints : 0;

    return {
      totalPoints,
      achievementsUnlocked: unlockedAchievements.length,
      achievementsTotal: this.achievements.size,
      completionRate: (unlockedAchievements.length / this.achievements.size) * 100,
      rareAchievements,
      level,
      nextLevel,
      pointsToNextLevel,
    };
  }

  /**
   * Get leaderboard
   */
  getLeaderboard(category?: string, limit: number = 100): LeaderboardEntry[] {
    const leaderboard = this.leaderboards.get(category || 'global') || [];
    return leaderboard.slice(0, limit);
  }

  /**
   * Claim achievement rewards
   */
  async claimRewards(userId: string, achievementId: string): Promise<AchievementReward[]> {
    const userAchievements = this.userAchievements.get(userId) || [];
    const userAchievement = userAchievements.find(ua => ua.achievementId === achievementId);
    
    if (!userAchievement || !userAchievement.unlockedAt || userAchievement.claimed) {
      throw new Error('Achievement not available for claiming');
    }

    const achievement = this.achievements.get(achievementId);
    if (!achievement) throw new Error('Achievement not found');

    userAchievement.claimed = true;
    userAchievement.claimedAt = Date.now();
    
    this.userAchievements.set(userId, userAchievements);

    // Process rewards
    await this.processRewards(userId, achievement.rewards);

    return achievement.rewards;
  }

  /**
   * Get active challenges
   */
  getActiveChallenges(): Challenge[] {
    const now = Date.now();
    return Array.from(this.challenges.values()).filter(
      challenge => challenge.isActive && challenge.startDate <= now && challenge.endDate > now
    );
  }

  /**
   * Join challenge
   */
  async joinChallenge(userId: string, challengeId: string): Promise<void> {
    const challenge = this.challenges.get(challengeId);
    if (!challenge || !challenge.isActive) {
      throw new Error('Challenge not available');
    }

    const userChallenges = this.userChallenges.get(userId) || [];
    const existingChallenge = userChallenges.find(uc => uc.challengeId === challengeId);
    
    if (existingChallenge) {
      throw new Error('Already participating in this challenge');
    }

    const userChallenge: UserChallenge = {
      challengeId,
      userId,
      startedAt: Date.now(),
      progress: {
        current: 0,
        required: this.calculateRequiredValue(challenge.requirements),
        percentage: 0,
        milestones: [],
        lastUpdated: Date.now(),
      },
      completed: false,
      rewards: challenge.rewards,
      claimed: false,
    };

    userChallenges.push(userChallenge);
    this.userChallenges.set(userId, userChallenges);

    // Update challenge participation count
    challenge.participantsCount++;
    this.challenges.set(challengeId, challenge);
  }

  // Private helper methods
  private async loadDefaultAchievements(): Promise<void> {
    const defaultAchievements: Achievement[] = [
      {
        id: 'first_upload',
        name: 'First Steps',
        description: 'Upload your first piece of content',
        category: 'content_creation',
        type: 'milestone',
        rarity: 'common',
        requirements: [
          {
            type: 'metric',
            metric: 'uploads',
            operator: 'greater_than',
            value: 0,
          },
        ],
        rewards: [
          { type: 'points', value: 100, description: '100 Creator Points' },
          { type: 'badge', value: 'first_creator', description: 'First Creator Badge' },
        ],
        icon: '🚀',
        badge: 'first_creator',
        points: 100,
        isSecret: false,
        isRepeatable: false,
        metadata: {
          difficulty: 1,
          estimatedTime: 5,
          completionRate: 95,
          tags: ['beginner', 'milestone'],
          version: '1.0',
        },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
      {
        id: 'viral_sensation',
        name: 'Viral Sensation',
        description: 'Get 1 million views on a single piece of content',
        category: 'audience_engagement',
        type: 'threshold',
        rarity: 'legendary',
        requirements: [
          {
            type: 'metric',
            metric: 'single_content_views',
            operator: 'greater_than',
            value: 1000000,
          },
        ],
        rewards: [
          { type: 'points', value: 10000, description: '10,000 Creator Points' },
          { type: 'title', value: 'Viral Creator', description: 'Viral Creator Title' },
          { type: 'feature_unlock', value: 'premium_analytics', description: 'Premium Analytics Access' },
        ],
        icon: '🌟',
        badge: 'viral_creator',
        points: 10000,
        isSecret: false,
        isRepeatable: false,
        metadata: {
          difficulty: 10,
          estimatedTime: 0, // Can't estimate
          completionRate: 0.1,
          tags: ['viral', 'legendary', 'views'],
          version: '1.0',
        },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
      {
        id: 'consistency_master',
        name: 'Consistency Master',
        description: 'Upload content every day for 30 days',
        category: 'consistency',
        type: 'streak',
        rarity: 'epic',
        requirements: [
          {
            type: 'action',
            operator: 'equals',
            value: 30,
            timeframe: {
              duration: 30 * 24 * 60 * 60 * 1000, // 30 days
              window: 'rolling',
            },
          },
        ],
        rewards: [
          { type: 'points', value: 5000, description: '5,000 Creator Points' },
          { type: 'boost', value: 'upload_boost_30d', description: '30-day Upload Boost' },
        ],
        icon: '📈',
        badge: 'consistency_master',
        points: 5000,
        isSecret: false,
        isRepeatable: true,
        metadata: {
          difficulty: 8,
          estimatedTime: 43200, // 30 days in minutes
          completionRate: 5,
          tags: ['consistency', 'streak', 'dedication'],
          version: '1.0',
        },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      },
    ];

    for (const achievement of defaultAchievements) {
      this.achievements.set(achievement.id, achievement);
    }
  }

  private async loadCreatorLevels(): Promise<void> {
    this.levels = [
      {
        level: 1,
        name: 'Novice Creator',
        minPoints: 0,
        maxPoints: 999,
        benefits: [
          { type: 'feature', name: 'Basic Analytics', description: 'Access to basic content analytics', permanent: true },
        ],
        icon: '🌱',
        color: '#90EE90',
      },
      {
        level: 2,
        name: 'Rising Star',
        minPoints: 1000,
        maxPoints: 4999,
        benefits: [
          { type: 'feature', name: 'Advanced Editor', description: 'Access to advanced content editor', permanent: true },
          { type: 'discount', name: 'Premium Features', description: '10% discount on premium features', value: 10, permanent: true },
        ],
        icon: '⭐',
        color: '#FFD700',
      },
      {
        level: 3,
        name: 'Established Creator',
        minPoints: 5000,
        maxPoints: 14999,
        benefits: [
          { type: 'priority', name: 'Support Priority', description: 'Priority customer support', permanent: true },
          { type: 'exclusive', name: 'Beta Features', description: 'Early access to beta features', permanent: true },
        ],
        icon: '🏆',
        color: '#FF6B6B',
      },
      {
        level: 4,
        name: 'Elite Creator',
        minPoints: 15000,
        maxPoints: 49999,
        benefits: [
          { type: 'feature', name: 'White Label', description: 'White label content options', permanent: true },
          { type: 'discount', name: 'All Services', description: '25% discount on all services', value: 25, permanent: true },
        ],
        icon: '💎',
        color: '#4ECDC4',
      },
      {
        level: 5,
        name: 'Legendary Creator',
        minPoints: 50000,
        maxPoints: Number.MAX_SAFE_INTEGER,
        benefits: [
          { type: 'exclusive', name: 'VIP Access', description: 'VIP access to all platform features', permanent: true },
          { type: 'feature', name: 'Personal Manager', description: 'Dedicated account manager', permanent: true },
        ],
        icon: '👑',
        color: '#8A2BE2',
      },
    ];
  }

  private async loadActiveChallenges(): Promise<void> {
    const now = Date.now();
    const weekStart = now - (now % (7 * 24 * 60 * 60 * 1000));
    
    const weeklyChallenge: Challenge = {
      id: 'weekly_uploads',
      name: 'Weekly Creator',
      description: 'Upload 7 pieces of content this week',
      type: 'weekly',
      category: 'content_creation',
      requirements: [
        {
          type: 'metric',
          metric: 'uploads',
          operator: 'greater_than',
          value: 6,
          timeframe: {
            duration: 7 * 24 * 60 * 60 * 1000,
            window: 'fixed',
            startDate: weekStart,
          },
        },
      ],
      rewards: [
        { type: 'points', value: 1000, description: '1,000 Bonus Points' },
        { type: 'boost', value: 'visibility_boost', description: 'Content Visibility Boost' },
      ],
      startDate: weekStart,
      endDate: weekStart + (7 * 24 * 60 * 60 * 1000),
      participantsCount: 0,
      completionsCount: 0,
      isActive: true,
      difficulty: 6,
    };

    this.challenges.set(weeklyChallenge.id, weeklyChallenge);
  }

  private calculateRequiredValue(requirements: AchievementRequirement[]): number {
    // Simplified calculation - take the first numeric requirement
    for (const req of requirements) {
      if (typeof req.value === 'number') {
        return req.value;
      }
    }
    return 1;
  }

  private async calculateProgressUpdate(
    achievement: Achievement,
    userAchievement: UserAchievement,
    activityType: string,
    value: number,
    metadata?: Record<string, any>
  ): Promise<number> {
    let progressUpdate = 0;

    for (const requirement of achievement.requirements) {
      if (requirement.type === 'metric' && requirement.metric === activityType) {
        if (requirement.operator === 'greater_than') {
          progressUpdate = value;
        } else if (requirement.operator === 'equals' && value === requirement.value) {
          progressUpdate = 1;
        }
      } else if (requirement.type === 'action') {
        progressUpdate = 1;
      }
    }

    return progressUpdate;
  }

  private checkMilestones(userAchievement: UserAchievement, achievement: Achievement): void {
    // Check for 25%, 50%, 75% milestones
    const milestones = [25, 50, 75];
    
    for (const threshold of milestones) {
      const existing = userAchievement.progress.milestones.find(m => m.threshold === threshold);
      
      if (!existing && userAchievement.progress.percentage >= threshold) {
        userAchievement.progress.milestones.push({
          threshold,
          reached: true,
          reachedAt: Date.now(),
          reward: {
            type: 'points',
            value: achievement.points * (threshold / 100) * 0.1,
            description: `${threshold}% Progress Bonus`,
          },
        });
      }
    }
  }

  private updateStreakData(userAchievement: UserAchievement, success: boolean): void {
    if (!userAchievement.streak) {
      userAchievement.streak = {
        count: 0,
        startDate: Date.now(),
        lastActivityDate: Date.now(),
        longestStreak: 0,
        broken: false,
      };
    }

    if (success) {
      userAchievement.streak.count++;
      userAchievement.streak.lastActivityDate = Date.now();
      userAchievement.streak.longestStreak = Math.max(
        userAchievement.streak.longestStreak,
        userAchievement.streak.count
      );
    } else {
      userAchievement.streak.broken = true;
      userAchievement.streak.brokenAt = Date.now();
      userAchievement.streak.count = 0;
    }
  }

  private async processAchievementUnlocks(userId: string, achievementIds: string[]): Promise<void> {
    // Process achievement unlocks (notifications, rewards, etc.)
    for (const achievementId of achievementIds) {
      const achievement = this.achievements.get(achievementId);
      if (achievement) {
        console.log(`Achievement unlocked for user ${userId}: ${achievement.name}`);
      }
    }

    // Update leaderboards
    await this.updateLeaderboards();
  }

  private async updateChallengeProgress(
    userId: string,
    activityType: string,
    value: number,
    metadata?: Record<string, any>
  ): Promise<void> {
    const userChallenges = this.userChallenges.get(userId) || [];
    
    for (const userChallenge of userChallenges) {
      if (userChallenge.completed) continue;

      const challenge = this.challenges.get(userChallenge.challengeId);
      if (!challenge || !challenge.isActive) continue;

      // Check if activity matches challenge requirements
      const progressUpdate = await this.calculateProgressUpdate(
        challenge as any, // Type compatibility
        userChallenge as any,
        activityType,
        value,
        metadata
      );

      if (progressUpdate > 0) {
        userChallenge.progress.current += progressUpdate;
        userChallenge.progress.percentage = Math.min(
          100,
          (userChallenge.progress.current / userChallenge.progress.required) * 100
        );
        userChallenge.progress.lastUpdated = Date.now();

        // Check if challenge is complete
        if (userChallenge.progress.current >= userChallenge.progress.required) {
          userChallenge.completed = true;
          userChallenge.completedAt = Date.now();

          // Update challenge completion count
          challenge.completionsCount++;
          this.challenges.set(challenge.id, challenge);
        }
      }
    }

    this.userChallenges.set(userId, userChallenges);
  }

  private getUserLevel(points: number): CreatorLevel {
    for (let i = this.levels.length - 1; i >= 0; i--) {
      if (points >= this.levels[i].minPoints) {
        return this.levels[i];
      }
    }
    return this.levels[0];
  }

  private async updateLeaderboards(): Promise<void> {
    const leaderboard: LeaderboardEntry[] = [];
    
    for (const [userId, userAchievements] of this.userAchievements) {
      const unlockedAchievements = userAchievements.filter(ua => ua.unlockedAt);
      
      const totalPoints = unlockedAchievements.reduce((sum, ua) => {
        const achievement = this.achievements.get(ua.achievementId);
        return sum + (achievement?.points || 0);
      }, 0);

      const rareAchievements = unlockedAchievements.filter(ua => {
        const achievement = this.achievements.get(ua.achievementId);
        return achievement && ['rare', 'epic', 'legendary', 'mythic'].includes(achievement.rarity);
      }).length;

      const level = this.getUserLevel(totalPoints);
      
      leaderboard.push({
        userId,
        userName: `User ${userId}`, // Would come from user service
        rank: 0, // Will be set after sorting
        points: totalPoints,
        achievementsCount: unlockedAchievements.length,
        rareAchievements,
        badges: unlockedAchievements.map(ua => 
          this.achievements.get(ua.achievementId)?.badge
        ).filter(Boolean) as string[],
        level: level.level,
      });
    }

    // Sort by points and assign ranks
    leaderboard.sort((a, b) => b.points - a.points);
    leaderboard.forEach((entry, index) => {
      entry.rank = index + 1;
    });

    this.leaderboards.set('global', leaderboard);
  }

  private async processRewards(userId: string, rewards: AchievementReward[]): Promise<void> {
    // Process rewards (would integrate with user service, currency system, etc.)
    for (const reward of rewards) {
      console.log(`Processing reward for user ${userId}: ${reward.type} - ${reward.value}`);
    }
  }
}

export const gamificationAchievementsEngine = new GamificationAchievementsEngine();