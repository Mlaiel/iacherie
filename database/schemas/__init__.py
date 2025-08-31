"""Database Schemas Module Initialization

This module provides comprehensive Pydantic schemas for the IA Influencer Agent platform,
covering all aspects of content protection, monetization, and platform management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""
# Content management schemas
from .content_schemas import (
    # Enums
    ContentTypeEnum,
    ContentStatusEnum,
    ContentFormatEnum,
    ContentQualityEnum,
    FingerprintTypeEnum,
    SearchScopeEnum,
    
    # Main schemas
    ContentFingerprintCreateSchema,
    ContentFingerprintResponseSchema,
    ContentMetadataSchema,
    ContentSearchSchema,
    ContentVersionSchema,
    ContentBatchProcessingSchema,
    
    # Media-specific schemas
    AudioMetadataSchema,
    VideoMetadataSchema,
    ImageMetadataSchema,
    TextMetadataSchema
)

# Protection and security schemas
from .protection_schemas import (
    # Enums
    ProtectionStatusEnum,
    ThreatTypeEnum,
    ThreatSeverityEnum,
    ProtectionActionEnum,
    EvidenceTypeEnum,
    
    # Main schemas
    ProtectionAlertCreateSchema,
    ProtectionAlertResponseSchema,
    ThreatIntelligenceSchema,
    EvidenceCollectionSchema,
    SecurityMonitoringSchema,
    
    # Specialized schemas
    ThreatDetectionConfigSchema,
    ProtectionPolicySchema,
    SecurityIncidentSchema
)

# Monetization schemas
from .monetization_schemas import (
    # Enums
    RevenueTypeEnum,
    PaymentStatusEnum,
    PaymentMethodEnum,
    CurrencyEnum,
    MonetizationModelEnum,
    
    # Main schemas
    RevenueTrackingCreateSchema,
    RevenueTrackingResponseSchema,
    PaymentProcessingSchema,
    MonetizationRuleSchema,
    
    # Financial schemas
    RevenueAnalyticsSchema,
    PaymentMethodSchema,
    PayoutConfigurationSchema
)

# Platform integration schemas
from .platform_schemas import (
    # Enums
    PlatformTypeEnum,
    IntegrationStatusEnum,
    DistributionStatusEnum,
    SyncStatusEnum,
    APICapabilityEnum,
    
    # Main schemas
    PlatformIntegrationCreateSchema,
    PlatformIntegrationResponseSchema,
    ContentDistributionSchema,
    PlatformAnalyticsSchema,
    
    # Integration schemas
    OAuth2ConfigurationSchema,
    APIConfigurationSchema,
    PlatformCredentialsSchema
)

# Licensing and rights management schemas
from .licensing_schemas import (
    # Enums
    LicenseTypeEnum,
    LicenseStatusEnum,
    UsageTypeEnum,
    RightsTypeEnum,
    ComplianceStatusEnum,
    
    # Main schemas
    LicensingAgreementCreateSchema,
    LicensingAgreementResponseSchema,
    RoyaltyStructureSchema,
    UsageRestrictionsSchema,
    
    # Rights management schemas
    IntellectualPropertySchema,
    ComplianceReportSchema,
    LicenseTermsSchema
)

# Collaboration schemas
from .collaboration_schemas import (
    # Enums
    CollaborationStatusEnum,
    CollaborationTypeEnum,
    InvitationStatusEnum,
    RoleTypeEnum,
    SkillLevelEnum,
    
    # Main schemas
    CollaborationRequestCreateSchema,
    CollaborationRequestResponseSchema,
    CollaboratorProfileSchema,
    RevenueShareAgreementSchema,
    
    # Collaboration features
    CollaborationMatchingSchema,
    ProjectCollaborationSchema,
    CollaborationFeedbackSchema
)

# AI analytics schemas
from .ai_analytics_schemas import (
    # Enums
    AnalyticsTypeEnum,
    ModelTypeEnum,
    InsightTypeEnum,
    PredictionTypeEnum,
    DataSourceTypeEnum,
    
    # Main schemas
    ContentAnalyticsSchema,
    MLModelPerformanceSchema,
    PredictiveInsightSchema,
    MarketIntelligenceSchema,
    
    # AI features
    UserBehaviorAnalysisSchema,
    ContentOptimizationSchema,
    TrendAnalysisSchema
)

# User management schemas
from .user_management_schemas import (
    # Enums
    UserRoleEnum,
    UserStatusEnum,
    SubscriptionTierEnum,
    VerificationStatusEnum,
    PreferenceTypeEnum,
    
    # Main schemas
    UserCreateSchema,
    UserResponseSchema,
    UserPreferencesSchema,
    SubscriptionSchema,
    
    # User features
    UserProfileSchema,
    UserVerificationSchema,
    UserActivitySchema
)

# Notification schemas
from .notification_schemas import (
    # Enums
    NotificationTypeEnum,
    NotificationPriorityEnum,
    NotificationChannelEnum,
    NotificationStatusEnum,
    MessageTypeEnum,
    MessageStatusEnum,
    AttachmentTypeEnum,
    
    # Main schemas
    NotificationCreateSchema,
    NotificationResponseSchema,
    MessageCreateSchema,
    MessageResponseSchema,
    
    # Communication features
    CommunicationPreferencesSchema,
    NotificationTemplateSchema,
    MessageAttachmentSchema,
    ConversationThreadSchema,
    NotificationBatchSchema,
    CommunicationAnalyticsSchema
)

# Advanced analytics and reporting schemas
from .analytics_schemas import (
    # Enums
    ReportTypeEnum,
    ReportFormatEnum,
    AnalyticsPeriodEnum,
    MetricTypeEnum,
    AggregationTypeEnum,
    TrendDirectionEnum,
    DashboardTypeEnum,
    VisualizationTypeEnum,
    
    # Main schemas
    ReportCreateSchema,
    ReportResponseSchema,
    DashboardCreateSchema,
    DashboardResponseSchema,
    
    # Analytics features
    MetricDefinitionSchema,
    KPISchema,
    AnalyticsDataPointSchema,
    ReportParametersSchema,
    DashboardWidgetSchema,
    AnalyticsInsightSchema,
    AnalyticsExportSchema
)

# Audit and compliance schemas
from .audit_schemas import (
    # Enums
    AuditEventTypeEnum,
    ComplianceFrameworkEnum,
    ComplianceStatusEnum,
    RiskLevelEnum,
    DataCategoryEnum,
    
    # Main schemas
    AuditTrailSchema,
    ComplianceAssessmentSchema,
    PrivacyImpactAssessmentSchema,
    DataSubjectRequestSchema,
    ComplianceReportSchema,
    RetentionPolicySchema
)

# Performance monitoring schemas
from .performance_schemas import (
    # Enums
    MetricTypeEnum as PerformanceMetricTypeEnum,
    AlertThresholdTypeEnum,
    PerformanceStatusEnum,
    ServiceComponentEnum,
    MetricAggregationEnum,
    
    # Main schemas
    PerformanceMetricSchema,
    PerformanceAggregateSchema,
    AlertRuleSchema,
    PerformanceAlertSchema,
    ServiceHealthSchema,
    PerformanceBenchmarkSchema,
    CapacityPlanningSchema
)

# Validation utilities and schemas
from .validation_schemas import (
    # Utility classes
    ValidationUtilities,
    
    # Validation schemas
    ContentValidationSchema,
    PlatformValidationSchema,
    SecurityValidationSchema,
    BusinessValidationSchema,
    ComprehensiveValidationSchema,
    
    # Validator decorators
    validate_email_field,
    validate_hash_field,
    validate_url_field,
    validate_percentage_field,
    validate_confidence_field
)


# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Comprehensive database schemas for IA Influencer Agent platform"


# Schema registry for dynamic access
SCHEMA_REGISTRY = {
    # Content schemas
    "content_fingerprint_create": ContentFingerprintCreateSchema,
    "content_fingerprint_response": ContentFingerprintResponseSchema,
    "content_metadata": ContentMetadataSchema,
    "content_search": ContentSearchSchema,
    "content_version": ContentVersionSchema,
    "content_batch_processing": ContentBatchProcessingSchema,
    
    # Protection schemas
    "protection_alert_create": ProtectionAlertCreateSchema,
    "protection_alert_response": ProtectionAlertResponseSchema,
    "threat_intelligence": ThreatIntelligenceSchema,
    "evidence_collection": EvidenceCollectionSchema,
    "security_monitoring": SecurityMonitoringSchema,
    
    # Monetization schemas
    "revenue_tracking_create": RevenueTrackingCreateSchema,
    "revenue_tracking_response": RevenueTrackingResponseSchema,
    "payment_processing": PaymentProcessingSchema,
    "monetization_rule": MonetizationRuleSchema,
    
    # Platform schemas
    "platform_integration_create": PlatformIntegrationCreateSchema,
    "platform_integration_response": PlatformIntegrationResponseSchema,
    "content_distribution": ContentDistributionSchema,
    "platform_analytics": PlatformAnalyticsSchema,
    
    # Licensing schemas
    "licensing_agreement_create": LicensingAgreementCreateSchema,
    "licensing_agreement_response": LicensingAgreementResponseSchema,
    "royalty_structure": RoyaltyStructureSchema,
    "usage_restrictions": UsageRestrictionsSchema,
    
    # Collaboration schemas
    "collaboration_request_create": CollaborationRequestCreateSchema,
    "collaboration_request_response": CollaborationRequestResponseSchema,
    "collaborator_profile": CollaboratorProfileSchema,
    "revenue_share_agreement": RevenueShareAgreementSchema,
    
    # AI analytics schemas
    "content_analytics": ContentAnalyticsSchema,
    "ml_model_performance": MLModelPerformanceSchema,
    "predictive_insight": PredictiveInsightSchema,
    "market_intelligence": MarketIntelligenceSchema,
    
    # User management schemas
    "user_create": UserCreateSchema,
    "user_response": UserResponseSchema,
    "user_preferences": UserPreferencesSchema,
    "subscription": SubscriptionSchema,
    
    # Notification schemas
    "notification_create": NotificationCreateSchema,
    "notification_response": NotificationResponseSchema,
    "message_create": MessageCreateSchema,
    "message_response": MessageResponseSchema,
    
    # Analytics schemas
    "report_create": ReportCreateSchema,
    "report_response": ReportResponseSchema,
    "dashboard_create": DashboardCreateSchema,
    "dashboard_response": DashboardResponseSchema,
}


def get_schema(schema_name: str):
    """    Retrieve a schema class by name from the registry.
    
    Args:
        schema_name: Name of the schema to retrieve
        
    Returns:
        Schema class if found, None otherwise
    """


    return SCHEMA_REGISTRY.get(schema_name)


def list_schemas():
    """    List all available schemas in the registry.
    
    Returns:
        List of schema names
    """


    return list(SCHEMA_REGISTRY.keys())


def get_schema_info(schema_name: str):
    """    Get information about a specific schema.
    
    Args:
        schema_name: Name of the schema
        
    Returns:
        Dictionary containing schema information
    """    schema_class = get_schema(schema_name)
    if not schema_class:
        return None
        
    return {
        "name": schema_name,
        "class": schema_class.__name__,
        "module": schema_class.__module__,
        "fields": list(schema_class.__fields__.keys()),
        "description": schema_class.__doc__
    }


# Export all schemas and utilities
__all__ = [
    # Schema registry utilities
    "SCHEMA_REGISTRY",
    "get_schema",
    "list_schemas",
    "get_schema_info",
    
    # Content schemas
    "ContentFingerprintCreateSchema",
    "ContentFingerprintResponseSchema",
    "ContentMetadataSchema",
    "ContentSearchSchema",
    "ContentVersionSchema",
    "ContentBatchProcessingSchema",
    "AudioMetadataSchema",
    "VideoMetadataSchema",
    "ImageMetadataSchema",
    "TextMetadataSchema",
    
    # Protection schemas
    "ProtectionAlertCreateSchema",
    "ProtectionAlertResponseSchema",
    "ThreatIntelligenceSchema",
    "EvidenceCollectionSchema",
    "SecurityMonitoringSchema",
    "ThreatDetectionConfigSchema",
    "ProtectionPolicySchema",
    "SecurityIncidentSchema",
    
    # Monetization schemas
    "RevenueTrackingCreateSchema",
    "RevenueTrackingResponseSchema",
    "PaymentProcessingSchema",
    "MonetizationRuleSchema",
    "RevenueAnalyticsSchema",
    "PaymentMethodSchema",
    "PayoutConfigurationSchema",
    
    # Platform schemas
    "PlatformIntegrationCreateSchema",
    "PlatformIntegrationResponseSchema",
    "ContentDistributionSchema",
    "PlatformAnalyticsSchema",
    "OAuth2ConfigurationSchema",
    "APIConfigurationSchema",
    "PlatformCredentialsSchema",
    
    # Licensing schemas
    "LicensingAgreementCreateSchema",
    "LicensingAgreementResponseSchema",
    "RoyaltyStructureSchema",
    "UsageRestrictionsSchema",
    "IntellectualPropertySchema",
    "ComplianceReportSchema",
    "LicenseTermsSchema",
    
    # Collaboration schemas
    "CollaborationRequestCreateSchema",
    "CollaborationRequestResponseSchema",
    "CollaboratorProfileSchema",
    "RevenueShareAgreementSchema",
    "CollaborationMatchingSchema",
    "ProjectCollaborationSchema",
    "CollaborationFeedbackSchema",
    
    # AI analytics schemas
    "ContentAnalyticsSchema",
    "MLModelPerformanceSchema",
    "PredictiveInsightSchema",
    "MarketIntelligenceSchema",
    "UserBehaviorAnalysisSchema",
    "ContentOptimizationSchema",
    "TrendAnalysisSchema",
    
    # User management schemas
    "UserCreateSchema",
    "UserResponseSchema",
    "UserPreferencesSchema",
    "SubscriptionSchema",
    "UserProfileSchema",
    "UserVerificationSchema",
    "UserActivitySchema",
    
    # Notification schemas
    "NotificationCreateSchema",
    "NotificationResponseSchema",
    "MessageCreateSchema",
    "MessageResponseSchema",
    "CommunicationPreferencesSchema",
    "NotificationTemplateSchema",
    "MessageAttachmentSchema",
    "ConversationThreadSchema",
    "NotificationBatchSchema",
    "CommunicationAnalyticsSchema",
    
    # Audit schemas
    "AuditTrailSchema",
    "ComplianceAssessmentSchema",
    "PrivacyImpactAssessmentSchema",
    "DataSubjectRequestSchema",
    "ComplianceReportSchema",
    "RetentionPolicySchema",
    
    # Performance schemas
    "PerformanceMetricSchema",
    "PerformanceAggregateSchema",
    "AlertRuleSchema",
    "PerformanceAlertSchema",
    "ServiceHealthSchema",
    "PerformanceBenchmarkSchema",
    "CapacityPlanningSchema",
    
    # Validation schemas
    "ContentValidationSchema",
    "PlatformValidationSchema",
    "SecurityValidationSchema",
    "BusinessValidationSchema",
    "ComprehensiveValidationSchema",
    "ValidationUtilities",
    
    # Additional enums
    "AuditEventTypeEnum",
    "ComplianceFrameworkEnum",
    "PerformanceMetricTypeEnum",
    "AlertThresholdTypeEnum",
    "ServiceComponentEnum"
]

from .content_schemas import (
    ContentFingerprintSchema,
    ContentFingerprintCreateSchema,
    ContentFingerprintResponseSchema,
    ContentFingerprintUpdateSchema
)
from .protection_schemas import (
    ProtectionAlertSchema,
    ProtectionAlertCreateSchema,
    ProtectionAlertResponseSchema,
    ProtectionAlertUpdateSchema
)
from .monetization_schemas import (
    RevenueTrackingSchema,
    RevenueTrackingCreateSchema,
    RevenueTrackingResponseSchema,
    MonetizationRuleSchema
)
from .platform_schemas import (
    PlatformIntegrationSchema,
    PlatformIntegrationCreateSchema,
    PlatformIntegrationResponseSchema
)
from .licensing_schemas import (
    LicensingAgreementSchema,
    LicensingAgreementCreateSchema,
    LicensingAgreementResponseSchema
)
from .collaboration_schemas import (
    CollaborationRequestSchema,
    CollaborationRequestCreateSchema,
    CollaborationRequestResponseSchema
)

__all__ = [
    # Content schemas
    "ContentFingerprintSchema",
    "ContentFingerprintCreateSchema", 
    "ContentFingerprintResponseSchema",
    "ContentFingerprintUpdateSchema",
    # Protection schemas
    "ProtectionAlertSchema",
    "ProtectionAlertCreateSchema",
    "ProtectionAlertResponseSchema",
    "ProtectionAlertUpdateSchema",
    # Monetization schemas
    "RevenueTrackingSchema",
    "RevenueTrackingCreateSchema",
    "RevenueTrackingResponseSchema",
    "MonetizationRuleSchema",
    # Platform schemas
    "PlatformIntegrationSchema",
    "PlatformIntegrationCreateSchema",
    "PlatformIntegrationResponseSchema",
    # Licensing schemas
    "LicensingAgreementSchema",
    "LicensingAgreementCreateSchema", 
    "LicensingAgreementResponseSchema",
    # Collaboration schemas
    "CollaborationRequestSchema",
    "CollaborationRequestCreateSchema",
    "CollaborationRequestResponseSchema"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
