/**
 * @fileoverview Application configuration settings
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2024-2025 Fahed Mlaiel - All Rights Reserved
 */

export const APP_CONFIG = {
  name: 'Ainflue Platform',
  version: '2.0.0',
  description: 'Professional Multi-Format Content Creation & AI-Powered Distribution Platform',
  author: 'Fahed Mlaiel',
  email: 'mlaiel@live.de',
  
  // Environment settings
  environment: process.env.NODE_ENV || 'development',
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
  
  // Application URLs
  baseUrl: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
  
  // Feature flags
  features: {
    aiProcessing: true,
    collaboration: true,
    monetization: true,
    analytics: true,
    gamification: true,
  },
  
  // UI Configuration
  ui: {
    maxFileSize: 100 * 1024 * 1024, // 100MB
    supportedFormats: ['mp4', 'mp3', 'jpg', 'png', 'gif', 'pdf'],
    maxFilesPerUpload: 10,
    theme: {
      primary: '#3b82f6',
      secondary: '#10b981',
      accent: '#f59e0b',
    },
  },
} as const;