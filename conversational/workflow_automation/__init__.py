"""Workflow Automation Module - IA Influencer Agent

Enterprise-grade conversational workflow automation system for multi-format content creators
with advanced AI-powered automation, intelligent task orchestration, context-aware triggers,
and comprehensive business logic automation.

Project: IA Influencer Agent + Protection Platform
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

Contact mlaiel@live.de for licensing inquiries only.
"""from .automation_engine import (
    AutomationEngine,
    WorkflowOrchestrator,
    TaskAutomator,
    ConversationalAutomation,
    IntelligentScheduler,
    AutomationMetrics,
    WorkflowValidator,
    PerformanceOptimizer
)

from .business_process_automation import (
    BusinessProcessEngine,
    ContentWorkflowManager,
    ProtectionAutomation,
    MonetizationWorkflows,
    CollaborationAutomation,
    CreatorOnboardingWorkflow,
    ContentDistributionWorkflow,
    RevenueOptimizationEngine,
    ComplianceAutomation,
    QualityAssuranceWorkflow
)

from .conversation_workflows import (
    ConversationWorkflowManager,
    DialogueAutomation,
    ResponseAutomation,
    ContextAwareWorkflows,
    MultimodalWorkflows,
    ConversationAnalytics,
    IntentBasedAutomation,
    EmotionalIntelligenceWorkflow,
    PersonalizationEngine,
    ConversationSecurityWorkflow
)

from .trigger_management import (
    TriggerEngine,
    EventTriggerManager,
    ConversationalTriggers,
    ContentTriggers,
    BusinessTriggers,
    TimeTriggers,
    ConditionalTriggers,
    WebhookTriggers,
    UserActionTriggers,
    SystemTriggers,
    ThresholdTriggers
)

from .workflow_intelligence import (
    WorkflowIntelligence,
    AdaptiveWorkflows,
    PredictiveAutomation,
    LearningWorkflows,
    OptimizationEngine,
    WorkflowAnalytics,
    PerformancePrediction,
    AutomationInsights,
    IntelligentRecommendations,
    WorkflowAI
)

from .integration_automation import (
    IntegrationAutomator,
    PlatformWorkflows,
    APIAutomation,
    CrossPlatformSync,
    ExternalServiceOrchestrator,
    SocialMediaIntegration,
    PaymentGatewayIntegration,
    CloudStorageIntegration,
    AnalyticsIntegration,
    NotificationIntegration
)

from .performance_optimization import (
    WorkflowOptimizer,
    PerformanceAnalytics,
    AutoscalingManager,
    ResourceManager,
    EfficiencyEngine,
    LoadBalancer,
    CacheOptimizer,
    DatabaseOptimizer,
    MemoryManager,
    ProcessingOptimizer
)

from .index import (
    WorkflowAutomationOrchestrator,
    create_workflow_orchestrator,
    execute_content_workflow
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Automation Engine
    "AutomationEngine",
    "WorkflowOrchestrator", 
    "TaskAutomator",
    "ConversationalAutomation",
    "IntelligentScheduler",
    "AutomationMetrics",
    "WorkflowValidator",
    "PerformanceOptimizer",
    
    # Business Process Automation
    "BusinessProcessEngine",
    "ContentWorkflowManager",
    "ProtectionAutomation",
    "MonetizationWorkflows",
    "CollaborationAutomation",
    "CreatorOnboardingWorkflow",
    "ContentDistributionWorkflow",
    "RevenueOptimizationEngine",
    "ComplianceAutomation",
    "QualityAssuranceWorkflow",
    
    # Conversation Workflows
    "ConversationWorkflowManager",
    "DialogueAutomation",
    "ResponseAutomation",
    "ContextAwareWorkflows",
    "MultimodalWorkflows",
    "ConversationAnalytics",
    "IntentBasedAutomation",
    "EmotionalIntelligenceWorkflow",
    "PersonalizationEngine",
    "ConversationSecurityWorkflow",
    
    # Trigger Management
    "TriggerEngine",
    "EventTriggerManager",
    "ConversationalTriggers",
    "ContentTriggers",
    "BusinessTriggers",
    "TimeTriggers",
    "ConditionalTriggers",
    "WebhookTriggers",
    "UserActionTriggers",
    "SystemTriggers",
    "ThresholdTriggers",
    
    # Workflow Intelligence
    "WorkflowIntelligence",
    "AdaptiveWorkflows",
    "PredictiveAutomation",
    "LearningWorkflows",
    "OptimizationEngine",
    "WorkflowAnalytics",
    "PerformancePrediction",
    "AutomationInsights",
    "IntelligentRecommendations",
    "WorkflowAI",
    
    # Integration Automation
    "IntegrationAutomator",
    "PlatformWorkflows",
    "APIAutomation",
    "CrossPlatformSync",
    "ExternalServiceOrchestrator",
    "SocialMediaIntegration",
    "PaymentGatewayIntegration",
    "CloudStorageIntegration",
    "AnalyticsIntegration",
    "NotificationIntegration",
    
    # Performance Optimization
    "WorkflowOptimizer",
    "PerformanceAnalytics",
    "AutoscalingManager",
    "ResourceManager",
    "EfficiencyEngine",
    "LoadBalancer",
    "CacheOptimizer", 
    "DatabaseOptimizer",
    "MemoryManager",
    "ProcessingOptimizer",
    
    # Main Orchestrator
    "WorkflowAutomationOrchestrator",
    "create_workflow_orchestrator",
    "execute_content_workflow"
]
