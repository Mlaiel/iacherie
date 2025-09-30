/**
 * Mobile Components Index - Professional Component Exports
 * 
 * Centralized exports for all mobile-optimized React Native components
 * designed for professional content creation and cross-platform distribution.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

// Gamification Components
export { default as MobileGamificationApp } from './MobileGamificationApp';
export { default as MobileChallenges } from './MobileChallenges';
export { default as MobileLeaderboards } from './MobileLeaderboards';

// Content Creation & Processing
export { default as MobileRemixStudio } from './MobileRemixStudio';
export { default as MobileAIAssistant } from './MobileAIAssistant';
export { default as MobileExporter } from './MobileExporter';

// Touch-Optimized Interface Components
export { default as TouchOptimizedInterface } from './TouchOptimizedInterface';
export { default as GestureControls } from './GestureControls';
export { default as VoiceCommands } from './VoiceCommands';

// Media Capture Components
export { default as CameraCaptureUI } from './CameraCaptureUI';
export { default as AudioRecorderUI } from './AudioRecorderUI';

// Offline & Sync Components
export { default as OfflineModeUI } from './OfflineModeUI';
export { default as SyncStatusIndicator } from './SyncStatusIndicator';

// Analytics & Monitoring
export { default as MobileAnalytics } from './MobileAnalytics';

// Component Type Definitions
export type {
  MobileGamificationProps,
  MobileChallengeProps,
  MobileLeaderboardProps,
  TouchOptimizedProps,
  GestureControlProps,
  VoiceCommandProps,
  CameraCaptureProps,
  AudioRecorderProps,
  OfflineModeProps,
  SyncStatusProps,
  MobileAnalyticsProps
} from './types';

// Component Configuration
export { 
  defaultMobileConfig,
  touchGestureConfig,
  voiceCommandConfig,
  mediaQualityConfig,
  offlineConfig
} from './config';

// Utility Hooks for Mobile Components
export {
  useMobileGestures,
  useMobileMedia,
  useMobileSync,
  useMobileAnalytics,
  useTouchOptimization
} from './hooks';