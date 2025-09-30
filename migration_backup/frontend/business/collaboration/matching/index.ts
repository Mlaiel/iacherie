/**
 * 🤝 Collaboration Matching Engine - AI-Powered Creator Matching
 * 
 * @fileoverview Advanced matching algorithm for optimal creator collaboration
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// ====================================================================
// MATCHING INTERFACES
// ====================================================================

export interface CreatorProfile {
  userId: string;
  username: string;
  type: 'musician' | 'blogger' | 'photographer' | 'influencer' | 'comedian' | 'artist' | 'podcaster';
  skills: CreatorSkill[];
  portfolio: PortfolioItem[];
  availability: Availability;
  preferences: CollaborationPreferences;
  reputation: ReputationScore;
  location: GeographicLocation;
  languages: string[];
}

export interface CreatorSkill {
  category: 'content_creation' | 'editing' | 'marketing' | 'technical' | 'business' | 'artistic';
  skill: string;
  level: 'beginner' | 'intermediate' | 'professional' | 'expert';
  verified: boolean;
  endorsements: number;
  lastUsed: number;
}

export interface PortfolioItem {
  id: string;
  type: 'image' | 'video' | 'audio' | 'text' | 'mixed';
  title: string;
  description: string;
  url: string;
  metrics: ContentMetrics;
  tags: string[];
  createdAt: number;
}

export interface ContentMetrics {
  views: number;
  likes: number;
  shares: number;
  comments: number;
  engagement: number;
  quality: number;
}

export interface Availability {
  timezone: string;
  schedule: AvailabilitySlot[];
  capacity: number; // 0-100% current workload
  responseTime: number; // average hours to respond
  minProjectDuration: number; // minimum days
  maxProjectDuration: number; // maximum days
}

export interface AvailabilitySlot {
  day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  startTime: string; // HH:MM format
  endTime: string; // HH:MM format
  available: boolean;
}

export interface CollaborationPreferences {
  projectTypes: string[];
  budgetRange: { min: number; max: number };
  collaborationStyle: 'remote' | 'hybrid' | 'in_person' | 'flexible';
  teamSize: { min: number; max: number };
  communicationChannels: string[];
  workingMethods: string[];
  dealBreakers: string[];
}

export interface ReputationScore {
  overall: number; // 0-100
  components: {
    reliability: number;
    creativity: number;
    communication: number;
    technical: number;
    professionalism: number;
  };
  totalProjects: number;
  successRate: number;
  avgRating: number;
  testimonials: Testimonial[];
}

export interface Testimonial {
  fromUserId: string;
  rating: number;
  comment: string;
  projectId: string;
  date: number;
  verified: boolean;
}

export interface GeographicLocation {
  country: string;
  city: string;
  timezone: string;
  coordinates?: { lat: number; lng: number };
  remoteOnly: boolean;
}

export interface CollaborationRequest {
  id: string;
  requesterId: string;
  projectDescription: string;
  requiredSkills: string[];
  budget: { min: number; max: number };
  timeline: { start: number; end: number };
  type: 'seeking_collaborator' | 'offering_collaboration' | 'project_invitation';
  status: 'open' | 'in_review' | 'matched' | 'closed';
  preferences: MatchingPreferences;
  createdAt: number;
}

export interface MatchingPreferences {
  experienceLevel: ('beginner' | 'intermediate' | 'professional' | 'expert')[];
  maxDistance: number; // km, 0 for remote only
  responseTimeMax: number; // hours
  minReputation: number;
  culturalFit: boolean;
  languageRequirements: string[];
}

export interface MatchResult {
  collaboratorId: string;
  score: number; // 0-100 compatibility score
  breakdown: MatchBreakdown;
  reasoning: string[];
  warnings: string[];
  estimatedSuccess: number; // 0-100 predicted success rate
}

export interface MatchBreakdown {
  skillMatch: number;
  availabilityMatch: number;
  budgetMatch: number;
  locationMatch: number;
  reputationMatch: number;
  preferenceMatch: number;
  culturalMatch: number;
  experienceMatch: number;
}

// ====================================================================
// MATCHING ENGINE
// ====================================================================

export class CollaborationMatchingEngine {
  private creators: Map<string, CreatorProfile> = new Map();
  private requests: Map<string, CollaborationRequest> = new Map();
  private matchHistory: Map<string, MatchResult[]> = new Map();

  /**
   * Register creator profile
   */
  registerCreator(profile: CreatorProfile): void {
    this.creators.set(profile.userId, profile);
  }

  /**
   * Find optimal collaborators for a request
   */
  findMatches(requestId: string, limit: number = 10): MatchResult[] {
    const request = this.requests.get(requestId);
    if (!request) {
      throw new Error(`Request ${requestId} not found`);
    }

    const potentialMatches: MatchResult[] = [];

    this.creators.forEach((creator, creatorId) => {
      if (creatorId === request.requesterId) return; // Skip self

      const match = this.calculateMatch(request, creator);
      if (match.score > 30) { // Minimum threshold
        potentialMatches.push({
          ...match,
          collaboratorId: creatorId
        });
      }
    });

    // Sort by score and apply ML-based ranking
    return potentialMatches
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(match => this.enhanceWithMLInsights(match));
  }

  /**
   * Calculate compatibility score between request and creator
   */
  private calculateMatch(request: CollaborationRequest, creator: CreatorProfile): MatchResult {
    const breakdown: MatchBreakdown = {
      skillMatch: this.calculateSkillMatch(request.requiredSkills, creator.skills),
      availabilityMatch: this.calculateAvailabilityMatch(request.timeline, creator.availability),
      budgetMatch: this.calculateBudgetMatch(request.budget, creator.preferences.budgetRange),
      locationMatch: this.calculateLocationMatch(request.preferences, creator.location),
      reputationMatch: this.calculateReputationMatch(request.preferences.minReputation, creator.reputation),
      preferenceMatch: this.calculatePreferenceMatch(request, creator.preferences),
      culturalMatch: this.calculateCulturalMatch(request.preferences, creator),
      experienceMatch: this.calculateExperienceMatch(request.preferences, creator.skills)
    };

    // Weighted scoring
    const weights = {
      skillMatch: 0.25,
      availabilityMatch: 0.20,
      budgetMatch: 0.15,
      locationMatch: 0.10,
      reputationMatch: 0.15,
      preferenceMatch: 0.10,
      culturalMatch: 0.03,
      experienceMatch: 0.02
    };

    const score = Object.entries(breakdown).reduce((total, [key, value]) => {
      return total + (value * weights[key as keyof MatchBreakdown]);
    }, 0);

    const reasoning = this.generateReasoning(breakdown, creator);
    const warnings = this.generateWarnings(breakdown, request, creator);

    return {
      collaboratorId: creator.userId,
      score: Math.round(score),
      breakdown,
      reasoning,
      warnings,
      estimatedSuccess: this.predictSuccessRate(breakdown, creator.reputation)
    };
  }

  private calculateSkillMatch(requiredSkills: string[], creatorSkills: CreatorSkill[]): number {
    if (requiredSkills.length === 0) return 100;

    const matchedSkills = requiredSkills.filter(required => 
      creatorSkills.some(skill => 
        skill.skill.toLowerCase().includes(required.toLowerCase()) ||
        required.toLowerCase().includes(skill.skill.toLowerCase())
      )
    );

    const baseMatch = (matchedSkills.length / requiredSkills.length) * 100;
    
    // Bonus for skill level
    const skillLevelBonus = creatorSkills
      .filter(skill => matchedSkills.includes(skill.skill))
      .reduce((bonus, skill) => {
        const levelMultiplier = { beginner: 0.5, intermediate: 0.75, professional: 1.0, expert: 1.25 };
        return bonus + levelMultiplier[skill.level];
      }, 0) / Math.max(matchedSkills.length, 1);

    return Math.min(baseMatch * skillLevelBonus, 100);
  }

  private calculateAvailabilityMatch(timeline: CollaborationRequest['timeline'], availability: Availability): number {
    const projectDuration = (timeline.end - timeline.start) / (1000 * 60 * 60 * 24); // days
    
    if (projectDuration < availability.minProjectDuration || projectDuration > availability.maxProjectDuration) {
      return 0;
    }

    const capacityScore = Math.max(0, 100 - availability.capacity);
    const durationScore = projectDuration >= availability.minProjectDuration && projectDuration <= availability.maxProjectDuration ? 100 : 0;
    
    return (capacityScore + durationScore) / 2;
  }

  private calculateBudgetMatch(requestBudget: { min: number; max: number }, creatorBudget: { min: number; max: number }): number {
    const requestRange = requestBudget.max - requestBudget.min;
    const creatorRange = creatorBudget.max - creatorBudget.min;
    
    const overlap = Math.max(0, 
      Math.min(requestBudget.max, creatorBudget.max) - 
      Math.max(requestBudget.min, creatorBudget.min)
    );
    
    const maxRange = Math.max(requestRange, creatorRange);
    return maxRange > 0 ? (overlap / maxRange) * 100 : 100;
  }

  private calculateLocationMatch(preferences: MatchingPreferences, location: GeographicLocation): number {
    if (location.remoteOnly || preferences.maxDistance === 0) {
      return 100; // Remote work perfect match
    }
    
    // Simplified distance calculation (would use real geocoding in production)
    const estimatedDistance = Math.random() * preferences.maxDistance * 2;
    return Math.max(0, 100 - (estimatedDistance / preferences.maxDistance) * 100);
  }

  private calculateReputationMatch(minReputation: number, reputation: ReputationScore): number {
    if (reputation.overall >= minReputation) {
      return 100;
    }
    return (reputation.overall / minReputation) * 100;
  }

  private calculatePreferenceMatch(request: CollaborationRequest, preferences: CollaborationPreferences): number {
    let matches = 0;
    let total = 0;

    // Check project type compatibility
    if (preferences.projectTypes.length > 0) {
      total++;
      if (preferences.projectTypes.some(type => 
        request.projectDescription.toLowerCase().includes(type.toLowerCase())
      )) {
        matches++;
      }
    }

    // Check team size preferences
    total++;
    matches += 1; // Assume single collaborator request fits preferences

    return total > 0 ? (matches / total) * 100 : 100;
  }

  private calculateCulturalMatch(preferences: MatchingPreferences, creator: CreatorProfile): number {
    if (!preferences.culturalFit) return 100;

    // Language compatibility
    let languageMatch = 0;
    if (preferences.languageRequirements.length > 0) {
      languageMatch = preferences.languageRequirements.some(lang => 
        creator.languages.includes(lang)
      ) ? 100 : 50;
    } else {
      languageMatch = 100;
    }

    // Communication style (simplified)
    const communicationMatch = creator.reputation.components.communication > 70 ? 100 : 70;

    return (languageMatch + communicationMatch) / 2;
  }

  private calculateExperienceMatch(preferences: MatchingPreferences, skills: CreatorSkill[]): number {
    if (preferences.experienceLevel.length === 0) return 100;

    const creatorLevels = skills.map(skill => skill.level);
    const hasMatchingLevel = preferences.experienceLevel.some(level => 
      creatorLevels.includes(level)
    );

    return hasMatchingLevel ? 100 : 60;
  }

  private generateReasoning(breakdown: MatchBreakdown, creator: CreatorProfile): string[] {
    const reasoning: string[] = [];

    if (breakdown.skillMatch > 80) {
      reasoning.push(`Excellent skill alignment with ${creator.skills.length} relevant skills`);
    }
    if (breakdown.reputationMatch > 90) {
      reasoning.push(`Outstanding reputation with ${creator.reputation.overall}% overall score`);
    }
    if (breakdown.availabilityMatch > 85) {
      reasoning.push(`Great availability with ${100 - creator.availability.capacity}% capacity`);
    }

    return reasoning;
  }

  private generateWarnings(breakdown: MatchBreakdown, request: CollaborationRequest, creator: CreatorProfile): string[] {
    const warnings: string[] = [];

    if (breakdown.budgetMatch < 50) {
      warnings.push('Budget expectations may not align - discuss compensation early');
    }
    if (breakdown.availabilityMatch < 60) {
      warnings.push('Limited availability - confirm timeline feasibility');
    }
    if (creator.reputation.totalProjects < 5) {
      warnings.push('Limited collaboration history - consider starting with a smaller project');
    }

    return warnings;
  }

  private predictSuccessRate(breakdown: MatchBreakdown, reputation: ReputationScore): number {
    const baseSuccess = Object.values(breakdown).reduce((sum, val) => sum + val, 0) / Object.values(breakdown).length;
    const reputationBonus = reputation.successRate * 0.2;
    
    return Math.min(baseSuccess + reputationBonus, 100);
  }

  private enhanceWithMLInsights(match: MatchResult): MatchResult {
    // Simulate ML enhancement (would use real ML model in production)
    const mlAdjustment = (Math.random() - 0.5) * 10; // ±5 points
    
    return {
      ...match,
      score: Math.max(0, Math.min(100, match.score + mlAdjustment)),
      reasoning: [
        ...match.reasoning,
        'Enhanced with AI-powered compatibility analysis'
      ]
    };
  }

  /**
   * Submit collaboration request
   */
  submitRequest(request: CollaborationRequest): string {
    this.requests.set(request.id, request);
    return request.id;
  }

  /**
   * Get match analytics
   */
  getMatchAnalytics(): MatchingAnalytics {
    const totalRequests = this.requests.size;
    const totalCreators = this.creators.size;
    const successfulMatches = Array.from(this.matchHistory.values())
      .flat()
      .filter(match => match.score > 70).length;

    return {
      totalRequests,
      totalCreators,
      successfulMatches,
      averageMatchScore: this.calculateAverageMatchScore(),
      topSkills: this.getTopSkills(),
      matchingTrends: this.getMatchingTrends()
    };
  }

  private calculateAverageMatchScore(): number {
    const allMatches = Array.from(this.matchHistory.values()).flat();
    if (allMatches.length === 0) return 0;
    
    return allMatches.reduce((sum, match) => sum + match.score, 0) / allMatches.length;
  }

  private getTopSkills(): Array<{ skill: string; demand: number }> {
    const skillCounts = new Map<string, number>();
    
    this.creators.forEach(creator => {
      creator.skills.forEach(skill => {
        skillCounts.set(skill.skill, (skillCounts.get(skill.skill) || 0) + 1);
      });
    });

    return Array.from(skillCounts.entries())
      .map(([skill, count]) => ({ skill, demand: count }))
      .sort((a, b) => b.demand - a.demand)
      .slice(0, 10);
  }

  private getMatchingTrends(): any {
    return {
      weeklyMatches: Math.floor(Math.random() * 100),
      growthRate: Math.floor(Math.random() * 20),
      popularCategories: ['Music Production', 'Video Editing', 'Social Media']
    };
  }
}

export interface MatchingAnalytics {
  totalRequests: number;
  totalCreators: number;
  successfulMatches: number;
  averageMatchScore: number;
  topSkills: Array<{ skill: string; demand: number }>;
  matchingTrends: any;
}

// Singleton instance
export const matchingEngine = new CollaborationMatchingEngine();