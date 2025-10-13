/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

export interface Location {
  lat: number;
  lng: number;
}

export interface CaseReport {
  id: string;
  type: 'homeless' | 'animal' | 'medical' | 'emergency' | 'other';
  location: Location;
  address?: string;
  description: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in-progress' | 'helped' | 'closed';
  reportedAt: string;
  tags: string[];
  photos?: string[];
  media?: string[]; // URLs des fichiers uploadés
  volunteerId?: string;
  resolvedAt?: string;
}

export interface Volunteer {
  id: string;
  name?: string;
  notificationRadius: number; // in kilometers
  availableCategories: ('homeless' | 'animal')[];
  isAvailable: boolean;
}

export interface NotificationPreferences {
  enabled: boolean;
  radius: number;
  categories: ('homeless' | 'animal')[];
  urgencyLevels: ('low' | 'medium' | 'high')[];
  quietHours: {
    enabled: boolean;
    start: string; // HH:MM format
    end: string;   // HH:MM format
  };
}

export interface UserProfile {
  id: string;
  volunteer: Volunteer;
  notifications: NotificationPreferences;
  language: string;
  accessibilitySettings: {
    screenReader: boolean;
    voiceInput: boolean;
    highContrast: boolean;
    largeText: boolean;
  };
}

export interface VolunteerActivity {
  id: string;
  volunteerId: string;
  caseId: string;
  action: 'helped' | 'started-helping' | 'reported' | 'updated';
  timestamp: string;
  location?: Location;
  notes?: string;
  duration?: number; // time spent helping in minutes
  resourcesProvided?: string[]; // food, blankets, medical, etc.
}

export interface VolunteerProfile {
  id: string;
  name: string;
  email?: string;
  avatarUrl?: string;
  joinedAt: string;
  bio?: string;
  skills: string[]; // medical training, translation, etc.
  availableHours: {
    days: string[]; // monday, tuesday, etc.
    startTime: string;
    endTime: string;
  };
  preferences: {
    maxDistance: number;
    preferredCategories: ('homeless' | 'animal')[];
    notificationSettings: NotificationPreferences;
  };
  verification: {
    isVerified: boolean;
    verifiedAt?: string;
    verificationMethod?: 'phone' | 'email' | 'government-id';
  };
  stats: VolunteerStats;
}

export interface VolunteerStats {
  totalCasesHelped: number;
  totalReports: number;
  totalHoursVolunteered: number;
  peopleHelped: number;
  animalsHelped: number;
  activeStreakDays: number;
  averageResponseTime: number; // in minutes
  mostActiveCategory: 'homeless' | 'animal' | null;
  badges: Badge[];
  rating: number; // 1-5 stars from community feedback
  reviewCount: number;
}

export interface ImpactStats {
  totalCasesHelped: number;
  totalReports: number;
  peopleHelped: number;
  animalsHelped: number;
  activeStreak: number; // consecutive days with activity
  averageResponseTime: number; // in minutes
  mostActiveCategory: 'homeless' | 'animal' | null;
  weeklyGoal: number;
  weeklyProgress: number;
}

export interface CommunityStats {
  totalVolunteers: number;
  activeCases: number;
  casesResolvedToday: number;
  casesResolvedThisWeek: number;
  casesResolvedThisMonth: number;
  averageResolutionTime: number;
  topVolunteers: Array<{
    id: string;
    name: string;
    casesHelped: number;
  }>;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  earnedAt: string;
  category: 'milestone' | 'skill' | 'dedication' | 'impact';
}

export interface VolunteerReview {
  id: string;
  reviewerId: string;
  volunteerId: string;
  caseId: string;
  rating: number; // 1-5 stars
  comment?: string;
  timestamp: string;
  anonymous: boolean;
}