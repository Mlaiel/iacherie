/**
 * Mobile Component Types - TypeScript Definitions
 * 
 * Comprehensive type definitions for mobile-specific components
 * used throughout the Ainflue mobile application.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { ViewStyle, TextStyle } from 'react-native';

// Base Component Props
export interface BaseMobileComponentProps {
  style?: ViewStyle;
  testID?: string;
  accessibilityLabel?: string;
  onError?: (error: Error) => void;
}

// Touch Interaction Types
export interface TouchGestureData {
  x: number;
  y: number;
  timestamp: number;
  force?: number;
  gestureType: 'tap' | 'long_press' | 'swipe' | 'pinch' | 'rotate';
  direction?: 'up' | 'down' | 'left' | 'right';
}

export interface GestureControlProps extends BaseMobileComponentProps {
  onGesture: (gesture: TouchGestureData) => void;
  enabledGestures: string[];
  sensitivity?: number;
}

// Voice Command Types
export interface VoiceCommandData {
  command: string;
  confidence: number;
  timestamp: number;
  language: string;
}

export interface VoiceCommandProps extends BaseMobileComponentProps {
  onCommand: (command: VoiceCommandData) => void;
  supportedCommands: string[];
  language?: string;
  enabled?: boolean;
}

// Camera Capture Types
export interface CameraSettings {
  quality: 'low' | 'medium' | 'high' | '4k';
  format: 'jpg' | 'png' | 'raw';
  flashMode: 'auto' | 'on' | 'off';
  focusMode: 'auto' | 'manual';
  aspectRatio: '4:3' | '16:9' | '1:1';
}

export interface CapturedMedia {
  uri: string;
  type: 'image' | 'video';
  duration?: number;
  size: number;
  metadata: {
    width: number;
    height: number;
    timestamp: number;
    location?: {
      latitude: number;
      longitude: number;
    };
  };
}

export interface CameraCaptureProps extends BaseMobileComponentProps {
  onCapture: (media: CapturedMedia) => void;
  settings: CameraSettings;
  mode: 'photo' | 'video' | 'both';
  maxDuration?: number;
}

// Audio Recording Types
export interface AudioSettings {
  quality: 'low' | 'medium' | 'high' | 'lossless';
  format: 'mp3' | 'wav' | 'aac' | 'flac';
  sampleRate: 44100 | 48000 | 96000;
  bitRate: 128 | 256 | 320;
  channels: 1 | 2;
}

export interface AudioRecording {
  uri: string;
  duration: number;
  size: number;
  format: string;
  metadata: {
    timestamp: number;
    peakLevel: number;
    averageLevel: number;
  };
}

export interface AudioRecorderProps extends BaseMobileComponentProps {
  onRecordingComplete: (recording: AudioRecording) => void;
  settings: AudioSettings;
  maxDuration?: number;
  enablePauseResume?: boolean;
}

// Sync and Offline Types
export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSyncTime?: Date;
  pendingItems: number;
  failedItems: number;
  syncProgress?: number;
}

export interface SyncStatusProps extends BaseMobileComponentProps {
  status: SyncStatus;
  onRetrySync?: () => void;
  showDetails?: boolean;
}

export interface OfflineData {
  id: string;
  type: 'content' | 'profile' | 'settings' | 'analytics';
  data: any;
  timestamp: Date;
  size: number;
  syncPriority: 'low' | 'medium' | 'high';
}

export interface OfflineModeProps extends BaseMobileComponentProps {
  isOffline: boolean;
  offlineData: OfflineData[];
  storageQuota: number;
  usedStorage: number;
  onDataManagement?: () => void;
}

// Gamification Types
export interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly' | 'special';
  category: 'creation' | 'engagement' | 'collaboration' | 'growth';
  requirements: {
    target: number;
    metric: string;
    timeframe: number;
  };
  rewards: {
    points: number;
    badges?: string[];
    unlocks?: string[];
  };
  progress: number;
  startDate: Date;
  endDate: Date;
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
}

export interface LeaderboardEntry {
  userId: string;
  username: string;
  avatar?: string;
  rank: number;
  score: number;
  level: number;
  achievements: string[];
  trend: 'up' | 'down' | 'stable';
}

export interface GamificationProps extends BaseMobileComponentProps {
  challenges: Challenge[];
  leaderboard: LeaderboardEntry[];
  userStats: {
    level: number;
    points: number;
    rank: number;
    completedChallenges: number;
  };
  onChallengeAccept?: (challengeId: string) => void;
}

// AI Assistant Types
export interface AIConversation {
  id: string;
  messages: AIMessage[];
  context: 'creative' | 'technical' | 'business' | 'general';
  createdAt: Date;
  updatedAt: Date;
}

export interface AIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: {
    type: 'image' | 'audio' | 'video' | 'document';
    uri: string;
    name: string;
  }[];
  suggestions?: string[];
}

export interface AIAssistantProps extends BaseMobileComponentProps {
  conversation: AIConversation;
  onSendMessage: (message: string, attachments?: any[]) => void;
  onSuggestionSelect: (suggestion: string) => void;
  isTyping?: boolean;
  capabilities: string[];
}

// Remix Studio Types
export interface RemixProject {
  id: string;
  name: string;
  type: 'audio' | 'video' | 'image' | 'text';
  originalContent: {
    uri: string;
    type: string;
    metadata: any;
  };
  modifications: RemixModification[];
  exportOptions: ExportOptions;
  collaborators: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface RemixModification {
  id: string;
  type: 'filter' | 'effect' | 'edit' | 'ai_enhancement';
  parameters: Record<string, any>;
  timestamp: Date;
  previewUri?: string;
}

export interface ExportOptions {
  format: string;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  resolution?: string;
  frameRate?: number;
  bitRate?: number;
  metadata: {
    title?: string;
    description?: string;
    tags?: string[];
  };
}

export interface RemixStudioProps extends BaseMobileComponentProps {
  project: RemixProject;
  onProjectUpdate: (project: RemixProject) => void;
  onExport: (options: ExportOptions) => void;
  availableEffects: string[];
  isProcessing?: boolean;
}

// Analytics Types
export interface MobileAnalyticsData {
  usage: {
    dailyActiveTime: number;
    screenViews: Record<string, number>;
    featuresUsed: string[];
    crashes: number;
    errors: number;
  };
  performance: {
    loadTimes: Record<string, number>;
    memoryUsage: number;
    batteryImpact: number;
    networkUsage: number;
  };
  engagement: {
    contentCreated: number;
    collaborations: number;
    challengesCompleted: number;
    socialShares: number;
  };
  revenue: {
    earnings: number;
    transactions: number;
    conversionRate: number;
  };
}

export interface AnalyticsProps extends BaseMobileComponentProps {
  data: MobileAnalyticsData;
  timeframe: '24h' | '7d' | '30d' | '90d';
  onTimeframeChange: (timeframe: string) => void;
  onExportData?: () => void;
}

// Touch Interface Types
export interface TouchOptimizedProps extends BaseMobileComponentProps {
  children: React.ReactNode;
  hapticFeedback?: boolean;
  gestureEnabled?: boolean;
  touchableOpacity?: number;
  minimumHitArea?: number;
}

// Export Types
export interface ExportProgress {
  id: string;
  type: 'content' | 'project' | 'analytics';
  progress: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  startTime: Date;
  estimatedCompletion?: Date;
  outputUri?: string;
  error?: string;
}

export interface ExporterProps extends BaseMobileComponentProps {
  exports: ExportProgress[];
  onStartExport: (item: any, options: ExportOptions) => void;
  onCancelExport: (exportId: string) => void;
  onRetryExport: (exportId: string) => void;
}