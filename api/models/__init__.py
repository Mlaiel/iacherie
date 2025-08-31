"""IA Influencer Agent Platform - Data Models Package
ORM models for content, creator, asset tracking, rights protection and monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .base import BaseModel, TimestampMixin, UUIDMixin, AuditMixin, SoftDeleteMixin
from .user_models import User, UserProfile, UserSettings, UserSession, UserVerification
from .creator_models import Creator, CreatorProfile, CreatorStatistics, CreatorSubscription
from .content_models import Content, ContentMetadata, ContentVersion, ContentTag
from .media_models import MediaFile, MediaProcessing, MediaTransform, MediaAnalysis
from .protection_models import (
    ContentProtection, Fingerprint, WatermarkRecord, ProtectionLog,
    ViolationReport, TakedownRequest, LegalAction
)
from .collaboration_models import (
    Collaboration, CollaborationRequest, CollaborationAgreement,
    CollaborationRevenue, CollaborationMessage
)
from .project_models import Project, ProjectMember, ProjectTask, ProjectMilestone
from .copyright_models import Copyright, CopyrightClaim, CopyrightTransfer, CopyrightLicense
from .license_models import License, LicenseAgreement, LicenseUsage, LicenseRevenue
from .revenue_models import (
    Revenue, RevenueStream, RevenueShare, PaymentRecord,
    RoyaltyCalculation, RevenueReport
)
from .distribution_models import (
    Distribution, DistributionChannel, DistributionMetrics,
    PlatformIntegration, ContentDelivery
)
from .analytics_models import (
    Analytics, PerformanceMetrics, AudienceInsights,
    EngagementMetrics, TrendAnalysis, PredictiveAnalytics
)
from .monitoring_models import (
    MonitoringJob, CrawlerResult, AlertRule, NotificationEvent,
    SystemHealth, PerformanceLog
)
# AI Models Import
from .ai_models import (
    AIModel, AITraining, AIInference, AIFingerprint, VectorEmbedding,
    SimilarityMatch, ContentAnalysis
)

# Support Models Import
from .support_models import (
    # License Models
    License, LicenseAgreement, LicenseUsage, LicenseRevenue,
    # Revenue Models
    Revenue, RevenueStream, RevenueShare, PaymentRecord, RoyaltyCalculation, RevenueReport,
    # Distribution Models
    Distribution, DistributionChannel, DistributionMetrics, PlatformIntegration, ContentDelivery,
    # Analytics Models
    Analytics, PerformanceMetrics, AudienceInsights, EngagementMetrics, TrendAnalysis, PredictiveAnalytics,
    # Monitoring Models
    MonitoringJob, CrawlerResult, AlertRule, NotificationEvent, SystemHealth, PerformanceLog,
    # Notification Models
    Notification, NotificationTemplate, NotificationLog,
    # Audit Models
    AuditLog, SecurityEvent, ComplianceRecord
)
from .notification_models import Notification, NotificationTemplate, NotificationLog
from .audit_models import AuditLog, SecurityEvent, ComplianceRecord

__all__ = [
    # Base Models
    'BaseModel', 'UUIDMixin', 'TimestampMixin', 'SoftDeleteMixin', 'AuditMixin',
    'MetadataMixin', 'StatusMixin', 'PerformanceMetricsMixin',
    
    # User Models
    'User', 'UserProfile', 'UserSettings', 'UserSession', 'UserVerification',
    
    # Creator Models
    'Creator', 'CreatorProfile', 'CreatorStatistics', 'CreatorSubscription',
    
    # Content Models
    'Content', 'ContentMetadata', 'ContentVersion', 'ContentTag',
    
    # Media Models
    'MediaFile', 'MediaProcessing', 'MediaTransform', 'MediaAnalysis',
    
    # Protection Models
    'ContentProtection', 'Fingerprint', 'WatermarkRecord', 'ProtectionLog',
    'ViolationReport', 'TakedownRequest', 'LegalAction',
    
    # Collaboration Models
    'Collaboration', 'CollaborationRequest', 'CollaborationAgreement',
    'CollaborationRevenue', 'CollaborationMessage',
    
    # Project Models
    'Project', 'ProjectMember', 'ProjectTask', 'ProjectMilestone',
    
    # Copyright Models
    'Copyright', 'CopyrightClaim', 'CopyrightTransfer', 'CopyrightLicense',
    
    # AI Models
    'AIModel', 'AITraining', 'AIInference', 'AIFingerprint', 'VectorEmbedding',
    'SimilarityMatch', 'ContentAnalysis',
    
    # License Models
    'License', 'LicenseAgreement', 'LicenseUsage', 'LicenseRevenue',
    
    # Revenue Models
    'Revenue', 'RevenueStream', 'RevenueShare', 'PaymentRecord',
    'RoyaltyCalculation', 'RevenueReport',
    
    # Distribution Models
    'Distribution', 'DistributionChannel', 'DistributionMetrics',
    'PlatformIntegration', 'ContentDelivery',
    
    # Analytics Models
    'Analytics', 'PerformanceMetrics', 'AudienceInsights', 'EngagementMetrics',
    'TrendAnalysis', 'PredictiveAnalytics',
    
    # Monitoring Models
    'MonitoringJob', 'CrawlerResult', 'AlertRule', 'NotificationEvent',
    'SystemHealth', 'PerformanceLog',
    
    # Notification Models
    'Notification', 'NotificationTemplate', 'NotificationLog',
    
    # Audit Models
    'AuditLog', 'SecurityEvent', 'ComplianceRecord',
]
