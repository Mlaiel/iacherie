"""IA Influencer Agent Platform - Comprehensive Schemas Module
Professional-grade Pydantic schemas for complete business logic coverage

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

This module provides industrial-grade schemas following the complete business logic flow:
Creator → Upload → AI Processing → Protection → Collaboration → Distribution → Monetization

Architecture Overview:
├── Base Schemas (foundation)
├── User & Creator Management
├── Content & Media Processing  
├── AI Protection & Fingerprinting
├── Collaboration & Partnerships
├── Revenue & Monetization
├── Distribution & Platforms
├── SEO & Marketing Optimization
├── Analytics & Business Intelligence
├── Monitoring & Surveillance
├── AI & Machine Learning
├── Blockchain & NFT Integration
└── Admin & System Management
"""

# Foundation schemas
from .base import (
    BaseSchema, TimestampSchema, UUIDSchema, AuditSchema,
    PaginatedResponse, ApiResponse, ValidationError
)

# Core business schemas
from .user import (
    UserCreate, UserUpdate, UserOut, UserProfile, 
    UserSettings, UserSession, UserAuthentication,
    UserVerification, PasswordReset, PasswordChange, PasswordResetConfirm,
    TwoFactorSetup, TwoFactorVerify
)

from .creator import (
    CreatorCreate, CreatorUpdate, CreatorOut, CreatorProfile,
    CreatorVerification, CreatorStatistics, CreatorSubscription,
    CollaborationPreferences, MonetizationPreferences
)

from .content import (
    ContentUpload, ContentUpdate, ContentOut, ContentMetadata,
    ContentSearch, ContentAnalysis, ContentVersion, ContentTag,
    ContentBulkOperation, ContentExport
)

from .media import (
    MediaFileUpload, MediaFileOut, MediaProcessing, MediaTransform,
    AudioProcessing, VideoProcessing, ImageProcessing, MediaAnalysis,
    MediaStreamingConfig, MediaBackup
)

from .protection import (
    ProtectionRequest, ProtectionOut, FingerprintCreate, FingerprintOut,
    WatermarkRequest, WatermarkOut, ViolationReport, TakedownRequest,
    LegalAction, SecurityScan, ThreatAnalysis
)

from .collaboration import (
    CollaborationRequest, CollaborationOut, CollaborationAgreement,
    CollaborationRevenue, PartnerMatching, CollaborationMessage,
    ProjectCollaboration, CollaborationFeedback, CollaborationAnalytics
)

from .copyright import (
    CopyrightCreate, CopyrightOut, CopyrightClaim, CopyrightTransfer,
    LicenseAgreement, LicenseUsage, RightsManagement, IntellectualProperty
)

from .revenue import (
    RevenueCreate, RevenueOut, RevenueStream, RevenueShare,
    PaymentRecord, RoyaltyCalculation, MonetizationReport, FinancialAnalytics
)

from .distribution import (
    DistributionRequest, DistributionOut, PlatformIntegration,
    ContentDelivery, DistributionMetrics, PlatformAnalytics,
    MultiPlatformSync, DistributionCampaign
)

# Advanced business intelligence schemas
from .seo import (
    SEOAnalysis, SEOOptimization, KeywordResearch, ContentOptimization,
    SocialMediaStrategy, MarketingCampaign, InfluencerMetrics,
    ContentPerformancePrediction
)

from .analytics import (
    AnalyticsReport, ContentAnalytics, AudienceInsights, RevenueAnalytics,
    CompetitiveIntelligence, PlatformPerformance, BusinessIntelligenceDashboard
)

from .monitoring import (
    MonitoringConfiguration, ContentViolation, SurveillanceReport,
    SystemMonitoring, TrendAnalysis, AlertConfiguration, CrawlerConfiguration
)

from .ai import (
    AIModelConfiguration, AIProcessingRequest, AIProcessingResult,
    MLPipeline, ContentIntelligence, AIRecommendationEngine,
    NeuralNetworkConfiguration
)

from .blockchain import (
    BlockchainNetwork, SmartContract, NFTCollection, NFTToken,
    CryptoWallet, BlockchainTransaction, CryptoPayment, DeFiIntegration
)

from .admin import (
    AdminUser, SystemConfiguration, AuditLog, UserManagement,
    SystemHealth, BackupConfiguration, ComplianceReport, PlatformSettings
)

# Export all schemas for easy access
__all__ = [
    # Foundation
    "BaseSchema", "TimestampSchema", "UUIDSchema", "AuditSchema",
    "PaginatedResponse", "ApiResponse", "ValidationError",
    
    # User Management
    "UserCreate", "UserUpdate", "UserOut", "UserProfile", 
    "UserSettings", "UserSession", "UserAuthentication",
    "UserVerification", "PasswordReset", "PasswordChange", "PasswordResetConfirm",
    "TwoFactorSetup", "TwoFactorVerify",
    
    # Creator Management
    "CreatorCreate", "CreatorUpdate", "CreatorOut", "CreatorProfile",
    "CreatorVerification", "CreatorStatistics", "CreatorSubscription",
    "CollaborationPreferences", "MonetizationPreferences",
    
    # Content Management
    "ContentUpload", "ContentUpdate", "ContentOut", "ContentMetadata",
    "ContentSearch", "ContentAnalysis", "ContentVersion", "ContentTag",
    "ContentBulkOperation", "ContentExport",
    
    # Media Processing
    "MediaFileUpload", "MediaFileOut", "MediaProcessing", "MediaTransform",
    "AudioProcessing", "VideoProcessing", "ImageProcessing", "MediaAnalysis",
    "MediaStreamingConfig", "MediaBackup",
    
    # Protection & Fingerprinting
    "ProtectionRequest", "ProtectionOut", "FingerprintCreate", "FingerprintOut",
    "WatermarkRequest", "WatermarkOut", "ViolationReport", "TakedownRequest",
    "LegalAction", "SecurityScan", "ThreatAnalysis",
    
    # Collaboration
    "CollaborationRequest", "CollaborationOut", "CollaborationAgreement",
    "CollaborationRevenue", "PartnerMatching", "CollaborationMessage",
    "ProjectCollaboration", "CollaborationFeedback", "CollaborationAnalytics",
    
    # Copyright & Licensing
    "CopyrightCreate", "CopyrightOut", "CopyrightClaim", "CopyrightTransfer",
    "LicenseAgreement", "LicenseUsage", "RightsManagement", "IntellectualProperty",
    
    # Revenue & Monetization
    "RevenueCreate", "RevenueOut", "RevenueStream", "RevenueShare",
    "PaymentRecord", "RoyaltyCalculation", "MonetizationReport", "FinancialAnalytics",
    
    # Distribution & Platforms
    "DistributionRequest", "DistributionOut", "PlatformIntegration",
    "ContentDelivery", "DistributionMetrics", "PlatformAnalytics",
    "MultiPlatformSync", "DistributionCampaign",
    
    # SEO & Marketing
    "SEOAnalysis", "SEOOptimization", "KeywordResearch", "ContentOptimization",
    "SocialMediaStrategy", "MarketingCampaign", "InfluencerMetrics",
    "ContentPerformancePrediction",
    
    # Analytics & BI
    "AnalyticsReport", "ContentAnalytics", "AudienceInsights", "RevenueAnalytics",
    "CompetitiveIntelligence", "PlatformPerformance", "BusinessIntelligenceDashboard",
    
    # Monitoring & Surveillance
    "MonitoringConfiguration", "ContentViolation", "SurveillanceReport",
    "SystemMonitoring", "TrendAnalysis", "AlertConfiguration", "CrawlerConfiguration",
    
    # AI & Machine Learning
    "AIModelConfiguration", "AIProcessingRequest", "AIProcessingResult",
    "MLPipeline", "ContentIntelligence", "AIRecommendationEngine",
    "NeuralNetworkConfiguration",
    
    # Blockchain & NFT
    "BlockchainNetwork", "SmartContract", "NFTCollection", "NFTToken",
    "CryptoWallet", "BlockchainTransaction", "CryptoPayment", "DeFiIntegration",
    
    # Admin & System Management
    "AdminUser", "SystemConfiguration", "AuditLog", "UserManagement",
    "SystemHealth", "BackupConfiguration", "ComplianceReport", "PlatformSettings",
]
