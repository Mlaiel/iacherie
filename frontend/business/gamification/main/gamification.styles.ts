/**
 * Gamification System Styles - Ultra-Advanced Enterprise Design System
 * 
 * This module provides comprehensive styling utilities for the gamification system
 * with professional design patterns and accessibility compliance.
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

import { AchievementTier, ChallengeType } from './types';

export const gamificationStyles = {
  // Container Classes
  container: {
    main: "min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-900 transition-colors duration-300",
    section: "bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 transition-all duration-300 hover:shadow-xl",
    card: "bg-white dark:bg-slate-800 rounded-lg shadow-md border border-slate-200 dark:border-slate-700 p-4 transition-all duration-300 hover:shadow-lg",
    compactCard: "bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 p-3 transition-all duration-300 hover:shadow-md"
  },

  // Typography
  typography: {
    heading: {
      primary: "text-3xl font-bold text-slate-900 dark:text-white mb-6",
      secondary: "text-2xl font-semibold text-slate-800 dark:text-slate-200 mb-4",
      tertiary: "text-xl font-medium text-slate-700 dark:text-slate-300 mb-3"
    },
    body: {
      large: "text-lg text-slate-700 dark:text-slate-300",
      regular: "text-base text-slate-600 dark:text-slate-400",
      small: "text-sm text-slate-500 dark:text-slate-500",
      caption: "text-xs text-slate-400 dark:text-slate-600"
    }
  },

  // Achievement Tier Colors
  achievementTiers: {
    [AchievementTier.BRONZE]: {
      bg: "bg-gradient-to-r from-amber-600 to-orange-600",
      text: "text-amber-700 dark:text-amber-300",
      border: "border-amber-500",
      shadow: "shadow-amber-500/20",
      glow: "ring-amber-500/50"
    },
    [AchievementTier.SILVER]: {
      bg: "bg-gradient-to-r from-slate-400 to-slate-600",
      text: "text-slate-700 dark:text-slate-300",
      border: "border-slate-500",
      shadow: "shadow-slate-500/20",
      glow: "ring-slate-500/50"
    },
    [AchievementTier.GOLD]: {
      bg: "bg-gradient-to-r from-yellow-400 to-yellow-600",
      text: "text-yellow-700 dark:text-yellow-300",
      border: "border-yellow-500",
      shadow: "shadow-yellow-500/20",
      glow: "ring-yellow-500/50"
    },
    [AchievementTier.PLATINUM]: {
      bg: "bg-gradient-to-r from-indigo-400 to-purple-600",
      text: "text-indigo-700 dark:text-indigo-300",
      border: "border-indigo-500",
      shadow: "shadow-indigo-500/20",
      glow: "ring-indigo-500/50"
    },
    [AchievementTier.DIAMOND]: {
      bg: "bg-gradient-to-r from-cyan-400 to-blue-600",
      text: "text-cyan-700 dark:text-cyan-300",
      border: "border-cyan-500",
      shadow: "shadow-cyan-500/20",
      glow: "ring-cyan-500/50"
    }
  },

  // Challenge Type Colors
  challengeTypes: {
    [ChallengeType.DAILY]: {
      bg: "bg-green-100 dark:bg-green-900/30",
      text: "text-green-800 dark:text-green-300",
      border: "border-green-300 dark:border-green-700",
      icon: "text-green-600 dark:text-green-400"
    },
    [ChallengeType.WEEKLY]: {
      bg: "bg-blue-100 dark:bg-blue-900/30",
      text: "text-blue-800 dark:text-blue-300",
      border: "border-blue-300 dark:border-blue-700",
      icon: "text-blue-600 dark:text-blue-400"
    },
    [ChallengeType.MONTHLY]: {
      bg: "bg-purple-100 dark:bg-purple-900/30",
      text: "text-purple-800 dark:text-purple-300",
      border: "border-purple-300 dark:border-purple-700",
      icon: "text-purple-600 dark:text-purple-400"
    },
    [ChallengeType.SEASONAL]: {
      bg: "bg-orange-100 dark:bg-orange-900/30",
      text: "text-orange-800 dark:text-orange-300",
      border: "border-orange-300 dark:border-orange-700",
      icon: "text-orange-600 dark:text-orange-400"
    },
    [ChallengeType.SPECIAL]: {
      bg: "bg-pink-100 dark:bg-pink-900/30",
      text: "text-pink-800 dark:text-pink-300",
      border: "border-pink-300 dark:border-pink-700",
      icon: "text-pink-600 dark:text-pink-400"
    }
  },

  // Progress Bars
  progress: {
    container: "w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden",
    bar: "h-3 bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out",
    label: "text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
  },

  // Buttons
  buttons: {
    primary: "inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
    secondary: "inline-flex items-center px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
    success: "inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
    warning: "inline-flex items-center px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
    danger: "inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
    ghost: "inline-flex items-center px-4 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
  },

  // Badges
  badges: {
    new: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    featured: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    limited: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    rare: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300"
  },

  // Statistics
  stats: {
    container: "grid gap-4 sm:gap-6",
    card: "bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700",
    label: "text-sm font-medium text-slate-600 dark:text-slate-400",
    value: "text-2xl font-bold text-slate-900 dark:text-white",
    change: {
      positive: "text-green-600 dark:text-green-400",
      negative: "text-red-600 dark:text-red-400",
      neutral: "text-slate-600 dark:text-slate-400"
    }
  },

  // Leaderboard
  leaderboard: {
    podium: {
      first: "bg-gradient-to-br from-yellow-400 to-yellow-600 text-white",
      second: "bg-gradient-to-br from-slate-400 to-slate-600 text-white",
      third: "bg-gradient-to-br from-amber-600 to-orange-600 text-white"
    },
    rank: {
      top3: "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white",
      regular: "w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-sm font-medium text-slate-600 dark:text-slate-400"
    }
  },

  // Animations
  animations: {
    fadeIn: "animate-in fade-in duration-300",
    slideIn: "animate-in slide-in-from-bottom-4 duration-300",
    scaleIn: "animate-in zoom-in-95 duration-200",
    pulse: "animate-pulse",
    bounce: "animate-bounce",
    spin: "animate-spin"
  },

  // Loading States
  loading: {
    skeleton: "animate-pulse bg-slate-200 dark:bg-slate-700 rounded",
    spinner: "inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
  },

  // Form Elements
  forms: {
    input: "block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-800 dark:text-white",
    select: "block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-800 dark:text-white",
    textarea: "block w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-slate-800 dark:text-white resize-none",
    checkbox: "h-4 w-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500",
    radio: "h-4 w-4 text-blue-600 border-slate-300 focus:ring-blue-500"
  },

  // Responsive Grid
  grid: {
    cols1: "grid grid-cols-1 gap-4",
    cols2: "grid grid-cols-1 md:grid-cols-2 gap-4",
    cols3: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
    cols4: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4",
    cols6: "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
  },

  // Utility Classes
  utils: {
    centerContent: "flex items-center justify-center",
    flexBetween: "flex items-center justify-between",
    textTruncate: "truncate",
    srOnly: "sr-only",
    visuallyHidden: "absolute -inset-px",
    focusRing: "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
  }
};

export const tierIcons = {
  [AchievementTier.BRONZE]: "🥉",
  [AchievementTier.SILVER]: "🥈",
  [AchievementTier.GOLD]: "🥇",
  [AchievementTier.PLATINUM]: "💎",
  [AchievementTier.DIAMOND]: "💍"
};

export const challengeIcons = {
  [ChallengeType.DAILY]: "📅",
  [ChallengeType.WEEKLY]: "📋",
  [ChallengeType.MONTHLY]: "🗓️",
  [ChallengeType.SEASONAL]: "🌟",
  [ChallengeType.SPECIAL]: "✨"
};

export const difficultyColors = {
  1: "text-green-600 dark:text-green-400",
  2: "text-yellow-600 dark:text-yellow-400",
  3: "text-orange-600 dark:text-orange-400",
  4: "text-red-600 dark:text-red-400",
  5: "text-purple-600 dark:text-purple-400"
};

export const getDifficultyLabel = (difficulty: number): string => {
  const labels = {
    1: "Beginner",
    2: "Intermediate",
    3: "Professional",
    4: "Expert",
    5: "Master"
  };
  return labels[difficulty as keyof typeof labels] || "Unknown";
};