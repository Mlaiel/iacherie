/**
 * Mobile Services - Export Module
 * 
 * Centralized exports for all mobile-specific services providing
 * backend integration, device features, and business logic for the Ainflue platform.
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

// Core API Services
export { default as MobileAPIService } from './MobileAPIService';
export { default as OfflineStorageService } from './OfflineStorageService';
export { default as SyncService } from './SyncService';

// Communication Services
export { default as PushNotificationService } from './PushNotificationService';

// Device Services
export { default as BiometricService } from './BiometricService';
export { default as CameraService } from './CameraService';
export { default as AudioService } from './AudioService';
export { default as LocationService } from './LocationService';

// Service Types
export * from './types';