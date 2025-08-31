"""Database Models Module

Enterprise-grade SQLAlchemy database models for the IA Influencer Agent + Content Protection Platform.
Comprehensive content protection, fingerprinting, monetization, and collaboration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Import all model classes with their enums
from .content_fingerprints import (
    ContentFingerprint,
    ContentType,
    FingerprintAlgorithm,
    ProcessingStatus,
    QualityLevel
)

from .protection_alerts import (
    ProtectionAlert,
    AlertType,
    AlertSeverity,
    AlertStatus,
    DetectionMethod,
    AutomatedAction,
    EvidenceType,
    ThreatLevel
)

# NEW ADVANCED MODELS - Ultra Industrial Features
from .blockchain_rights import (
    BlockchainRights,
    ViolationReport,
    LicenseAutomation,
    BlockchainNetwork,
    RightsType,
    SmartContractStatus
)

from .cross_platform_monitoring import (
    PlatformMonitoring,
    ScanResult,
    ViolationDetection,
    MonitoringPlatform,
    MonitoringStatus,
    DetectionMethod as MonitoringDetectionMethod,
    ResponseAction
)

from .ai_revenue_analytics import (
    AIRevenueAnalytics,
    OptimizationExperiment,
    PredictionValidation,
    PredictionModel,
    AnalyticsScope,
    OptimizationTarget,
    MarketTrend
)

from .advanced_team_collaboration import (
    CreatorCollaboration,
    CollaborationTeamMember,
    CollaborationApplication,
    AICollaborationMatch,
    ProjectUpdate,
    CollaborationType,
    CollaborationStatus,
    TeamRole,
    SkillLevel,
    MatchingCriteria
)

from .revenue_tracking import (
    RevenueTracking,
    RevenueType,
    RevenueSource,
    RevenueStatus,
    Currency,
    PaymentMethod,
    TaxStatus
)

from .user_content import (
    UserContent,
    ContentType as UserContentType,
    ContentStatus,
    ContentGenre,
    ContentMood,
    QualityLevel as ContentQualityLevel,
    PrivacyLevel,
    ContentCategory as UserContentCategory
)

from .platform_integrations import (
    PlatformIntegration,
    Platform,
    IntegrationStatus,
    IntegrationType,
    AuthMethod,
    DataSyncStatus,
    HealthStatus,
    RateLimitStatus
)

from .licensing_agreements import (
    LicensingAgreement,
    LicenseType,
    LicenseStatus,
    UsageRight,
    RevenueModel,
    TerritoryScope,
    ComplianceStatus,
    RenewalStatus
)

from .audit_logs import (
    AuditLog,
    ActionType,
    EntityType,
    SecurityClassification,
    LogLevel,
    ComplianceCategory,
    AccessType
)

from .content_metadata import (
    ContentMetadata,
    MetadataType,
    MetadataSchema,
    MetadataStatus,
    ExtractorType,
    ValidationStatus,
    ConfidenceLevel
)

from .monetization_rules import (
    MonetizationRule,
    RuleType,
    RuleStatus,
    TriggerType,
    ConditionOperator,
    ActionType as MonetizationActionType,
    OptimizationGoal
)

from .collaboration_requests import (
    CollaborationRequest,
    CollaborationType,
    RequestStatus,
    Priority,
    CollaborationScope,
    RevenueShareType
)

# Import new ultra-industrial models according to business logic requirements
from .digital_rights import (
    DigitalRights,
    RightsType,
    BlockchainNetwork,
    ContractType,
    VerificationLevel as RightsVerificationLevel,
    EnforcementStatus,
    LegalJurisdiction
)

from .intelligent_matching import (
    IntelligentMatching,
    MatchingType,
    MatchingAlgorithm,
    MatchingStatus,
    ConfidenceLevel as MatchingConfidenceLevel,
    SynergyType,
    CollaborationType as MatchingCollaborationType
)

from .multi_platform_distribution import (
    MultiPlatformDistribution,
    DistributionPlatform,
    ContentFormat as DistributionContentFormat,
    DistributionStatus as MultiDistributionStatus,
    OptimizationStrategy,
    PostingStrategy
)

from .seo_optimization import (
    SEOOptimization,
    SearchEngine,
    OptimizationType as SEOOptimizationType,
    KeywordDifficulty,
    SearchIntent,
    OptimizationStatus as SEOOptimizationStatus,
    ContentType as SEOContentType
)

# Import existing comprehensive models
from .ai_analysis import (
    AIAnalysis,
    AnalysisType,
    ModelType,
    AnalysisStatus,
    QualityScore,
    ConfidenceScore,
    TrendDirection,
    SentimentType,
    PersonalityTrait,
    EmotionType,
    ContentComplexity,
    LanguageCode,
    ModelProvider
)

from .content_distribution import (
    ContentDistribution,
    Platform as DistributionPlatform,
    DistributionStatus,
    DistributionType,
    ScheduleType,
    OptimizationType,
    TargetAudience,
    GeographicRegion,
    AgeGroup,
    Gender,
    PerformanceMetric,
    TestType,
    SyncStatus
)

from .creator_profiles import (
    CreatorProfile,
    CreatorType,
    CreatorStatus,
    CareerLevel,
    SkillCategory,
    ProficiencyLevel,
    CollaborationPreference,
    AudienceLocation,
    ContentSpecialty,
    SocialPlatform,
    VerificationStatus,
    MonetizationMethod,
    CommunicationPreference,
    WorkingStyle,
    ProjectType,
    BudgetRange
)

from .engagement_metrics import (
    EngagementMetrics,
    MetricType,
    Platform as EngagementPlatform,
    MetricStatus,
    AudienceSegment,
    ContentFormat,
    EngagementType,
    AudienceAge,
    AudienceGender,
    PerformanceTier,
    TrendPattern,
    SeasonalPattern,
    OptimalTime,
    ContentTheme
)

from .notification_settings import (
    NotificationSettings,
    NotificationType,
    DeliveryChannel,
    NotificationPriority,
    NotificationStatus,
    FrequencyType,
    TimeWindow,
    UserTimezone,
    DeliveryStatus,
    ContentCategory as NotificationContentCategory,
    AlertThreshold,
    EscalationLevel,
    ChannelPreference
)

from .payment_transactions import (
    PaymentTransaction,
    TransactionType,
    TransactionStatus,
    PaymentProvider,
    PaymentMethod as TransactionPaymentMethod,
    Currency as TransactionCurrency,
    FraudRiskLevel,
    ComplianceStatus as TransactionComplianceStatus,
    RevenueCategory,
    RefundReason,
    DisputeReason,
    ReconciliationStatus,
    TaxCategory,
    ProcessingStage
)

from .protection_policies import (
    ProtectionPolicy,
    PolicyType,
    PolicyStatus,
    TriggerCondition,
    ActionType as PolicyActionType,
    SeverityLevel,
    DetectionMethod as PolicyDetectionMethod,
    ResponseType,
    EscalationLevel as PolicyEscalationLevel,
    LegalAction,
    Platform as PolicyPlatform,
    ContentType as PolicyContentType,
    GeographicScope,
    ComplianceFramework,
    EnforcementStage
)

from .social_integrations import (
    SocialIntegration,
    Platform as SocialPlatform,
    IntegrationStatus as SocialIntegrationStatus,
    AuthType,
    PermissionScope,
    SyncFrequency,
    DataType,
    HealthStatus as SocialHealthStatus,
    RateLimitStatus as SocialRateLimitStatus,
    APIVersion,
    FeatureSupport,
    ErrorCategory,
    RetryStrategy
)

from .subscription_plans import (
    SubscriptionPlan,
    PlanTier,
    BillingCycle,
    PlanStatus,
    PricingModel,
    DiscountType,
    FeatureCategory,
    UsageMetric,
    TrialType,
    CancellationReason,
    UpgradeReason,
    PaymentMethod as SubscriptionPaymentMethod,
    Currency as SubscriptionCurrency,
    TaxType,
    ComplianceRequirement
)

from .user_permissions import (
    UserPermissions,
    PermissionType,
    ResourceType,
    RoleType,
    PermissionScope,
    AccessLevel,
    PermissionStatus
)

from .team_management import (
    TeamManagement,
    TeamMember,
    TeamInvitation,
    TeamType,
    TeamStatus,
    MemberRole,
    MemberStatus,
    InvitationStatus,
    PermissionLevel,
    TeamVisibility
)

from .workspace_management import (
    WorkspaceManagement,
    WorkspaceProject,
    WorkspaceType,
    WorkspaceStatus,
    AccessLevel as WorkspaceAccessLevel,
    ResourceType as WorkspaceResourceType,
    UsageStatus,
    EnvironmentType,
    BackupStatus
)

from .billing_management import (
    BillingManagement,
    BillingInvoice,
    BillingStatus,
    InvoiceStatus,
    PaymentStatus,
    PaymentMethod as BillingPaymentMethod,
    Currency as BillingCurrency,
    BillingCycle as BillingCycleType,
    InvoiceType,
    TaxType as BillingTaxType,
    DiscountType as BillingDiscountType,
    ComplianceStandard
)

# Base declarative class
Base = declarative_base()

# All model classes for easy import
__all__ = [
    # Base classes
    'Base',
    
    # Content Fingerprints
    'ContentFingerprint',
    'ContentType',
    'FingerprintAlgorithm',
    'FingerprintStatus',
    'QualityLevel',
    'ContentCategory',
    
    # Protection Alerts
    'ProtectionAlert',
    'AlertType',
    'AlertSeverity',
    'AlertStatus',
    'DetectionMethod',
    'AutomatedAction',
    'EvidenceType',
    'ThreatLevel',
    
    # Revenue Tracking
    'RevenueTracking',
    'RevenueType',
    'RevenueSource',
    'RevenueStatus',
    'Currency',
    'PaymentMethod',
    'TaxStatus',
    
    # User Content
    'UserContent',
    'UserContentType',
    'ContentStatus',
    'ContentGenre',
    'ContentMood',
    'ContentQualityLevel',
    'PrivacyLevel',
    'UserContentCategory',
    
    # Platform Integrations
    'PlatformIntegration',
    'Platform',
    'IntegrationStatus',
    'IntegrationType',
    'AuthMethod',
    'DataSyncStatus',
    'HealthStatus',
    'RateLimitStatus',
    
    # Licensing Agreements
    'LicensingAgreement',
    'LicenseType',
    'LicenseStatus',
    'UsageRight',
    'RevenueModel',
    'TerritoryScope',
    'ComplianceStatus',
    'RenewalStatus',
    
    # Audit Logs
    'AuditLog',
    'ActionType',
    'EntityType',
    'SecurityClassification',
    'LogLevel',
    'ComplianceCategory',
    'AccessType',
    
    # Content Metadata
    'ContentMetadata',
    'MetadataType',
    'MetadataSchema',
    'MetadataStatus',
    'ExtractorType',
    'ValidationStatus',
    'ConfidenceLevel',
    
    # Monetization Rules
    'MonetizationRule',
    'RuleType',
    'RuleStatus',
    'TriggerType',
    'ConditionOperator',
    'MonetizationActionType',
    'OptimizationGoal',
    
    # Collaboration Requests
    'CollaborationRequest',
    'CollaborationType',
    'RequestStatus',
    'Priority',
    'CollaborationScope',
    'RevenueShareType',
    
    # AI Analysis Models
    'AIAnalysis',
    'AnalysisType',
    'ModelType',
    'AnalysisStatus',
    'QualityScore',
    'ConfidenceScore',
    'TrendDirection',
    'SentimentType',
    'PersonalityTrait',
    'EmotionType',
    'ContentComplexity',
    'LanguageCode',
    'ModelProvider',
    
    # Content Distribution Models
    'ContentDistribution',
    'DistributionPlatform',
    'DistributionStatus',
    'DistributionType',
    'ScheduleType',
    'OptimizationType',
    'TargetAudience',
    'GeographicRegion',
    'AgeGroup',
    'Gender',
    'PerformanceMetric',
    'TestType',
    'SyncStatus',
    
    # Creator Profile Models
    'CreatorProfile',
    'CreatorType',
    'CreatorStatus',
    'CareerLevel',
    'SkillCategory',
    'ProficiencyLevel',
    'CollaborationPreference',
    'AudienceLocation',
    'ContentSpecialty',
    'SocialPlatform',
    'VerificationStatus',
    'MonetizationMethod',
    'CommunicationPreference',
    'WorkingStyle',
    'ProjectType',
    'BudgetRange',
    
    # Engagement Metrics Models
    'EngagementMetrics',
    'MetricType',
    'EngagementPlatform',
    'MetricStatus',
    'AudienceSegment',
    'ContentFormat',
    'EngagementType',
    'AudienceAge',
    'AudienceGender',
    'PerformanceTier',
    'TrendPattern',
    'SeasonalPattern',
    'OptimalTime',
    'ContentTheme',
    
    # Notification Settings Models
    'NotificationSettings',
    'NotificationType',
    'DeliveryChannel',
    'NotificationPriority',
    'NotificationStatus',
    'FrequencyType',
    'TimeWindow',
    'UserTimezone',
    'DeliveryStatus',
    'NotificationContentCategory',
    'AlertThreshold',
    'EscalationLevel',
    'ChannelPreference',
    
    # Payment Transaction Models
    'PaymentTransaction',
    'TransactionType',
    'TransactionStatus',
    'PaymentProvider',
    'TransactionPaymentMethod',
    'TransactionCurrency',
    'FraudRiskLevel',
    'TransactionComplianceStatus',
    'RevenueCategory',
    'RefundReason',
    'DisputeReason',
    'ReconciliationStatus',
    'TaxCategory',
    'ProcessingStage',
    
    # Protection Policy Models
    'ProtectionPolicy',
    'PolicyType',
    'PolicyStatus',
    'TriggerCondition',
    'PolicyActionType',
    'SeverityLevel',
    'PolicyDetectionMethod',
    'ResponseType',
    'PolicyEscalationLevel',
    'LegalAction',
    'PolicyPlatform',
    'PolicyContentType',
    'GeographicScope',
    'ComplianceFramework',
    'EnforcementStage',
    
    # Social Integration Models
    'SocialIntegration',
    'SocialPlatform',
    'SocialIntegrationStatus',
    'AuthType',
    'PermissionScope',
    'SyncFrequency',
    'DataType',
    'SocialHealthStatus',
    'SocialRateLimitStatus',
    'APIVersion',
    'FeatureSupport',
    'ErrorCategory',
    'RetryStrategy',
    
    # Subscription Plan Models
    'SubscriptionPlan',
    'PlanTier',
    'BillingCycle',
    'PlanStatus',
    'PricingModel',
    'DiscountType',
    'FeatureCategory',
    'UsageMetric',
    'TrialType',
    'CancellationReason',
    'UpgradeReason',
    'SubscriptionPaymentMethod',
    'SubscriptionCurrency',
    'TaxType',
    'ComplianceRequirement',
    
    # User Permission Models
    'UserPermissions',
    'PermissionType',
    'ResourceType',
    'RoleType',
    'PermissionScope',
    'AccessLevel',
    'PermissionStatus',
    
    # Team Management Models
    'TeamManagement',
    'TeamMember',
    'TeamInvitation',
    'TeamType',
    'TeamStatus',
    'MemberRole',
    'MemberStatus',
    'InvitationStatus',
    'PermissionLevel',
    'TeamVisibility',
    
    # Workspace Management Models
    'WorkspaceManagement',
    'WorkspaceProject',
    'WorkspaceType',
    'WorkspaceStatus',
    'WorkspaceAccessLevel',
    'WorkspaceResourceType',
    'UsageStatus',
    'EnvironmentType',
    'BackupStatus',
    
    # Billing Management Models
    'BillingManagement',
    'BillingInvoice',
    'BillingStatus',
    'InvoiceStatus',
    'PaymentStatus',
    'BillingPaymentMethod',
    'BillingCurrency',
    'BillingCycleType',
    'InvoiceType',
    'BillingTaxType',
    'BillingDiscountType',
    'ComplianceStandard',
    
    # NEW ULTRA-INDUSTRIAL MODELS (Business Logic Compliant)
    # Digital Rights Management
    'DigitalRights',
    'RightsType',
    'BlockchainNetwork',
    'ContractType',
    'RightsVerificationLevel',
    'EnforcementStatus',
    'LegalJurisdiction',
    
    # Intelligent Matching System
    'IntelligentMatching',
    'MatchingType',
    'MatchingAlgorithm',
    'MatchingStatus',
    'MatchingConfidenceLevel',
    'SynergyType',
    'MatchingCollaborationType',
    
    # Multi-Platform Distribution
    'MultiPlatformDistribution',
    'DistributionPlatform',
    'DistributionContentFormat',
    'MultiDistributionStatus',
    'OptimizationStrategy',
    'PostingStrategy',
    
    # SEO Optimization
    'SEOOptimization',
    'SearchEngine',
    'SEOOptimizationType',
    'KeywordDifficulty',
    'SearchIntent',
    'SEOOptimizationStatus',
    'SEOContentType'
]

# Model registry for dynamic access (UPDATED WITH NEW MODELS)
MODEL_REGISTRY = {
    'content_fingerprints': ContentFingerprint,
    'protection_alerts': ProtectionAlert,
    'revenue_tracking': RevenueTracking,
    'user_content': UserContent,
    'platform_integrations': PlatformIntegration,
    'licensing_agreements': LicensingAgreement,
    'audit_logs': AuditLog,
    'content_metadata': ContentMetadata,
    'monetization_rules': MonetizationRule,
    'collaboration_requests': CollaborationRequest,
    'ai_analysis': AIAnalysis,
    'content_distribution': ContentDistribution,
    'creator_profiles': CreatorProfile,
    'engagement_metrics': EngagementMetrics,
    'notification_settings': NotificationSettings,
    'payment_transactions': PaymentTransaction,
    'protection_policies': ProtectionPolicy,
    'social_integrations': SocialIntegration,
    'subscription_plans': SubscriptionPlan,
    'user_permissions': UserPermissions,
    'team_management': TeamManagement,
    'team_members': TeamMember,
    'team_invitations': TeamInvitation,
    'workspace_management': WorkspaceManagement,
    'workspace_projects': WorkspaceProject,
    
    # NEW ULTRA-INDUSTRIAL MODELS
    'digital_rights': DigitalRights,
    'intelligent_matching': IntelligentMatching,
    'multi_platform_distribution': MultiPlatformDistribution,
    'seo_optimization': SEOOptimization,
    'billing_management': BillingManagement,
    'billing_invoices': BillingInvoice
}

def get_model_class(model_name: str):
    """Get model class by name"""


    return MODEL_REGISTRY.get(model_name)

def get_all_models():
    """Get all model classes"""


    return list(MODEL_REGISTRY.values())

def create_all_tables(engine):
    """Create all database tables"""    Base.metadata.create_all(bind=engine)

def drop_all_tables(engine):
    """Drop all database tables"""    Base.metadata.drop_all(bind=engine)

def create_session_factory(database_url: str):
    """Create database session factory"""    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return scoped_session(SessionLocal), engine

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
