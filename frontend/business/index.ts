/**
 * 🏢 Business Logic Module - Enterprise Business Domain Exports
 * 
 * @fileoverview Central export point for all business logic modules
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// Core Business Orchestrators
export * from './seo_engine';
export * from './ai_orchestrator';
export * from './upload_orchestrator';
export * from './remix_studio_engine';

// New Enterprise Orchestrators (Level 4 Compliance)
export { 
  ProcessingOrchestrator, 
  processingOrchestrator, 
  useAIProcessing,
  type AIProcessingRequest,
  type ProcessingResult,
  type ProcessingParameters
} from './processing_orchestrator';

export { 
  AnalyticsOrchestrator, 
  analyticsOrchestrator, 
  useContentAnalytics,
  type ContentAnalytics,
  type PerformanceMetrics,
  type EngagementMetrics
} from './analytics_orchestrator';

export { 
  WorkflowOrchestrator, 
  workflowOrchestrator, 
  useWorkflow,
  type WorkflowDefinition,
  type WorkflowExecution,
  ContentPublicationWorkflow,
  UserOnboardingWorkflow
} from './workflow_orchestrator';

// Content business logic exports
export * from './content';

// Content protection exports
export * from './protection';

// Monetization exports
export * from './monetization';

// Collaboration exports
export * from './collaboration';

// Gamification exports
export * from './gamification';

// Distribution exports
export * from './distribution';

// Business Types
export * from '../core/business_types';