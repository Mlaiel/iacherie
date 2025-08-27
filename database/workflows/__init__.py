"""
Workflow Automation Database Module

Enterprise workflow automation system with AI-powered optimization,
process orchestration, and intelligent task management for 
multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

# Core workflow components
from .workflow_engine import (
    Workflow,
    WorkflowExecution,
    WorkflowTask,
    WorkflowTemplate,
    ProcessOrchestrator,
    WorkflowEngine,
    WorkflowStatus,
    TaskStatus,
    TriggerType,
    TaskType,
    WorkflowContext
)

# Automation rules engine
from .automation_rules import (
    AutomationRule,
    RuleExecution,
    RuleTemplate,
    AutomationRulesEngine,
    MLRuleOptimizer,
    RuleType,
    ConditionOperator,
    ActionType,
    RuleStatus,
    RuleCondition,
    RuleAction
)

# Publishing pipeline system
from .publishing_pipeline import (
    PublishingPipeline,
    PublishingJob,
    PlatformPublication,
    ContentOptimizationJob,
    PublishingPipelineManager,
    AISchedulingOptimizer,
    QualityValidator,
    PipelineStatus,
    ContentStatus,
    PlatformType,
    OptimizationType,
    SchedulingStrategy,
    PlatformConfig,
    ContentOptimization
)

# Approval system
from .approval_system import (
    ApprovalWorkflow,
    ApprovalRequest,
    ApprovalStep,
    ApprovalDecision,
    ApprovalDelegate,
    ApprovalSystemManager,
    NotificationService,
    AIApprovalEvaluator,
    ComplianceChecker,
    ApprovalType,
    ApprovalStatus,
    ApprovalPriority,
    ApproverRole,
    ApprovalCriteria,
    ApprovalAction
)

# Collaboration workflows
from .collaboration_workflows import (
    CollaborationWorkflow,
    CollaborationParticipant,
    CollaborationContent,
    CollaborationMilestone,
    CollaborationRevenueShare,
    AICreatorMatcher,
    CollaborationWorkflowManager,
    RevenueShareCalculator,
    CollaborationNotificationService,
    CollaborationType,
    CollaborationStatus,
    ParticipantRole,
    ContributionType,
    RevenueShareType
)

# Performance analytics
from .performance_analytics import (
    WorkflowPerformanceMetric,
    ContentPerformanceMetric,
    PerformanceDashboard,
    PerformanceAlert,
    PerformanceBenchmark,
    PerformanceAnalyticsEngine,
    AIInsightsEngine,
    AlertManager,
    BenchmarkAnalyzer,
    MetricType,
    MetricCategory,
    AggregationPeriod,
    AlertSeverity,
    TrendDirection
)

# Template management
from .template_management import (
    WorkflowTemplateMarketplace,
    WorkflowTemplateParameter,
    WorkflowConfiguration,
    TemplateUsageHistory,
    TemplateReview,
    WorkflowTemplateManager,
    AITemplateGenerator,
    ConfigurationManager,
    MarketplaceManager,
    TemplateCategory,
    TemplateComplexity,
    TemplateStatus,
    ParameterType,
    ConfigurationScope
)

# Content distribution
from .content_distribution import (
    ContentDistributionWorkflow,
    PlatformPublication,
    ContentSynchronization,
    PlatformAdaptationRule,
    CrossPlatformAnalytics,
    ContentDistributionManager,
    ContentProcessor,
    DistributionScheduler,
    CrossPlatformAnalyticsEngine,
    DistributionStrategy,
    ContentAdaptationType,
    DistributionStatus,
    PlatformStatus,
    SynchronizationType
)

__all__ = [
    # Workflow Engine
    'Workflow',
    'WorkflowExecution', 
    'WorkflowTask',
    'WorkflowTemplate',
    'ProcessOrchestrator',
    'WorkflowEngine',
    'WorkflowStatus',
    'TaskStatus',
    'TriggerType',
    'TaskType',
    'WorkflowContext',
    
    # Automation Rules
    'AutomationRule',
    'RuleExecution',
    'RuleTemplate', 
    'AutomationRulesEngine',
    'MLRuleOptimizer',
    'RuleType',
    'ConditionOperator',
    'ActionType',
    'RuleStatus',
    'RuleCondition',
    'RuleAction',
    
    # Publishing Pipeline
    'PublishingPipeline',
    'PublishingJob',
    'PlatformPublication',
    'ContentOptimizationJob',
    'PublishingPipelineManager',
    'AISchedulingOptimizer',
    'QualityValidator',
    'PipelineStatus',
    'ContentStatus',
    'PlatformType',
    'OptimizationType',
    'SchedulingStrategy',
    'PlatformConfig',
    'ContentOptimization',
    
    # Approval System
    'ApprovalWorkflow',
    'ApprovalRequest',
    'ApprovalStep',
    'ApprovalDecision',
    'ApprovalDelegate',
    'ApprovalSystemManager',
    'NotificationService',
    'AIApprovalEvaluator',
    'ComplianceChecker',
    'ApprovalType',
    'ApprovalStatus',
    'ApprovalPriority',
    'ApproverRole',
    'ApprovalCriteria',
    'ApprovalAction',
    
    # Collaboration Workflows
    'CollaborationWorkflow',
    'CollaborationParticipant',
    'CollaborationContent',
    'CollaborationMilestone',
    'CollaborationRevenueShare',
    'AICreatorMatcher',
    'CollaborationWorkflowManager',
    'RevenueShareCalculator',
    'CollaborationNotificationService',
    'CollaborationType',
    'CollaborationStatus',
    'ParticipantRole',
    'ContributionType',
    'RevenueShareType',
    
    # Performance Analytics
    'WorkflowPerformanceMetric',
    'ContentPerformanceMetric',
    'PerformanceDashboard',
    'PerformanceAlert',
    'PerformanceBenchmark',
    'PerformanceAnalyticsEngine',
    'AIInsightsEngine',
    'AlertManager',
    'BenchmarkAnalyzer',
    'MetricType',
    'MetricCategory',
    'AggregationPeriod',
    'AlertSeverity',
    'TrendDirection',
    
    # Template Management
    'WorkflowTemplateMarketplace',
    'WorkflowTemplateParameter',
    'WorkflowConfiguration',
    'TemplateUsageHistory',
    'TemplateReview',
    'WorkflowTemplateManager',
    'AITemplateGenerator',
    'ConfigurationManager',
    'MarketplaceManager',
    'TemplateCategory',
    'TemplateComplexity',
    'TemplateStatus',
    'ParameterType',
    'ConfigurationScope',
    
    # Content Distribution
    'ContentDistributionWorkflow',
    'PlatformPublication',
    'ContentSynchronization',
    'PlatformAdaptationRule',
    'CrossPlatformAnalytics',
    'ContentDistributionManager',
    'ContentProcessor',
    'DistributionScheduler',
    'CrossPlatformAnalyticsEngine',
    'DistributionStrategy',
    'ContentAdaptationType',
    'DistributionStatus',
    'PlatformStatus',
    'SynchronizationType'
]
