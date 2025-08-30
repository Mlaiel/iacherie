/**
 * Mobile Components - Export Module
 * 
 * Centralized exports for all mobile-specific React Native components
 * designed for the Ainflue content creator platform.
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
 * - DevOps Engineer: Kubernetes and cloud infrastructure
 * - Mobile Developer: React Native and cross-platform development
 * - AI Prompt Engineer: Advanced prompt engineering and LLM optimization
 */

// Gamification Components
export { default as MobileGamificationApp } from './MobileGamificationApp';
export { default as MobileChallenges } from './MobileChallenges';
export { default as MobileLeaderboards } from './MobileLeaderboards';

// Creative Studio Components
export { default as MobileRemixStudio } from './MobileRemixStudio';
export { default as MobileAIAssistant } from './MobileAIAssistant';
export { default as MobileExporter } from './MobileExporter';

// Mobile-Specific Interface Components
export { default as TouchOptimizedInterface } from './TouchOptimizedInterface';
export { default as GestureControls } from './GestureControls';
export { default as VoiceCommands } from './VoiceCommands';

// Media Capture Components
export { default as CameraCaptureUI } from './CameraCaptureUI';
export { default as AudioRecorderUI } from './AudioRecorderUI';

// Connectivity & Sync Components
export { default as OfflineModeUI } from './OfflineModeUI';
export { default as SyncStatusIndicator } from './SyncStatusIndicator';

// Analytics Components
export { default as MobileAnalytics } from './MobileAnalytics';

// Type exports
export * from './types';