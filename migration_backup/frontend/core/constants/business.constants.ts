/**
 * @fileoverview Business domain constants
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

// Content constants
export const CONTENT_CONSTANTS = {
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
  SUPPORTED_FORMATS: {
    IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
    VIDEO: ['mp4', 'avi', 'mov', 'mkv', 'webm'],
    AUDIO: ['mp3', 'wav', 'flac', 'aac', 'ogg'],
    DOCUMENT: ['pdf', 'doc', 'docx', 'txt', 'rtf'],
  },
  PROCESSING_STATES: [
    'pending',
    'uploading',
    'processing',
    'completed',
    'failed',
  ] as const,
  MAX_TAGS: 20,
  MAX_TITLE_LENGTH: 200,
  MAX_DESCRIPTION_LENGTH: 2000,
} as const;

// Protection constants
export const PROTECTION_CONSTANTS = {
  FINGERPRINT_ALGORITHMS: [
    'perceptual-hash',
    'chromaprint',
    'visual-similarity',
    'audio-fingerprint',
  ] as const,
  COPYRIGHT_LICENSES: [
    'all-rights-reserved',
    'creative-commons-by',
    'creative-commons-by-sa',
    'creative-commons-by-nc',
    'creative-commons-by-nd',
    'public-domain',
  ] as const,
  INFRINGEMENT_CONFIDENCE_THRESHOLD: 0.85,
  HASH_LENGTH: 64,
} as const;

// Monetization constants
export const MONETIZATION_CONSTANTS = {
  REVENUE_TYPES: [
    'subscription',
    'purchase',
    'licensing',
    'advertising',
    'commission',
  ] as const,
  SUPPORTED_CURRENCIES: ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'] as const,
  MIN_PRICE: 0.01,
  MAX_PRICE: 999999.99,
  PLATFORM_FEE_PERCENTAGE: 5, // 5% platform fee
  PAYOUT_THRESHOLD: 50, // Minimum $50 for payout
} as const;

// Collaboration constants
export const COLLABORATION_CONSTANTS = {
  MAX_COLLABORATORS: 10,
  PROJECT_STATUSES: ['draft', 'active', 'completed', 'archived'] as const,
  SKILL_CATEGORIES: [
    'video-editing',
    'audio-production',
    'graphic-design',
    'photography',
    'writing',
    'marketing',
    'programming',
    'animation',
  ] as const,
  MIN_RATING: 1,
  MAX_RATING: 5,
  MATCHING_ALGORITHM_WEIGHTS: {
    skills: 0.4,
    rating: 0.3,
    experience: 0.2,
    availability: 0.1,
  },
} as const;