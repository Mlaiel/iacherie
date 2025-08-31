"""IA Influencer Agent Platform - Comprehensive Schemas Module
Professional-grade Pydantic schemas for complete business logic coverage

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

This module provides industrial-grade schemas following the complete business logic flow:
Creator → Upload → AI Processing → Protection → Collaboration → Distribution → Monetization

Architecture Overview:
 Base Schemas (foundation)
 User & Creator Management
 Content & Media Processing  
 AI Protection & Fingerprinting
 Collaboration & Partnerships
 Revenue & Monetization
 Distribution & Platforms
 SEO & Marketing Optimization
 Analytics & Business Intelligence
 Monitoring & Surveillance
 AI & Machine Learning
 Blockchain & NFT Integration
 Admin & System Management
"""
# Foundation schemas
from .base import (
    BaseSchema, TimestampSchema, UUIDSchema, AuditSchema,
    PaginatedResponse, ApiResponse, ValidationError
)

# Core business schemas
from .user import (
    UserCreate, UserUpdate, UserOut, UserProfile, UserPreferences,
    UserSettings, UserSubscription, UserSession, TwoFactorAuth,
    UserVerification, UserStatistics, LoginRequest, PasswordReset
)

from .creator import (
    CreatorCreate, CreatorUpdate, CreatorOut, CreatorProfile,
    CreatorVerification, CreatorStatistics, CreatorSubscription,
    CreatorPortfolio, CreatorCollaboration, CreatorEarnings,
    VerificationRequest, BrandPartnership
)

from .content import (
    ContentUpload, ContentUpdate, ContentOut, ContentMetadata,
    ContentSearch, ContentFilter, ContentAnalysis, ContentOptimization,
    ContentSchedule, ContentTemplate, ContentSeries, ContentCategory,
    ContentTags, ContentEngagement
)

from .media import (
    MediaFileUpload, MediaFileOut, MediaProcessing, MediaTransformation,
    AudioProcessing, VideoProcessing, ImageProcessing, MediaOptimization,
    MediaMetadata, MediaStorage, ThumbnailGeneration, MediaCompression,
    StreamingConfiguration, MediaDelivery
)

from .protection import (
    ProtectionRequest, ProtectionOut, FingerprintCreate, FingerprintOut,
    WatermarkRequest, WatermarkOut, ViolationReport, TakedownRequest,
    CopyrightClaim, ProtectionAlert, ProtectionStatistics,
    AntiPiracyConfiguration, ContentAuthenticity, RightsManagement
)

from .collaboration import (
    CollaborationRequest, CollaborationUpdate, CollaborationOut,
    CollaborationAgreement, PartnerSearch, PartnerMatching,
    CollaborationRevenue, ProjectManagement, TeamManagement,
    CollaborationContract, NegotiationTerms, CollaborationAnalytics
)

from .copyright import (
    CopyrightCreate, CopyrightUpdate, CopyrightOut, LicenseAgreement,
    CopyrightTransfer, RoyaltyStructure, IntellectualProperty,
    LegalDocumentation, CopyrightDispute, FairUse,
    RightsManagement, LicensingTerms
)

from .revenue import (
    RevenueCreate, RevenueUpdate, RevenueOut, RevenueStream,
    PaymentRecord, PaymentMethod, MonetizationReport,
    FinancialAnalytics, TaxInformation, PayoutSchedule,
    RevenueSharing, SubscriptionTier, PricingModel
)

from .distribution import (
    DistributionRequest, DistributionUpdate, DistributionOut,
    PlatformIntegration, ContentDelivery, MultiPlatformSync,
    DistributionSchedule, DistributionMetrics, PlatformConfiguration,
    ContentOptimization, AudienceTargeting, DistributionCampaign
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
    "UserCreate", "UserUpdate", "UserOut", "UserProfile", "UserPreferences",
    "UserSettings", "UserSubscription", "UserSession", "TwoFactorAuth",
    "UserVerification", "UserStatistics", "LoginRequest", "PasswordReset",
    
    # Creator Management
    "CreatorCreate", "CreatorUpdate", "CreatorOut", "CreatorProfile",
    "CreatorVerification", "CreatorStatistics", "CreatorSubscription",
    "CreatorPortfolio", "CreatorCollaboration", "CreatorEarnings",
    "VerificationRequest", "BrandPartnership",
    
    # Content Management
    "ContentUpload", "ContentUpdate", "ContentOut", "ContentMetadata",
    "ContentSearch", "ContentFilter", "ContentAnalysis", "ContentOptimization",
    "ContentSchedule", "ContentTemplate", "ContentSeries", "ContentCategory",
    "ContentTags", "ContentEngagement",
    
    # Media Processing
    "MediaFileUpload", "MediaFileOut", "MediaProcessing", "MediaTransformation",
    "AudioProcessing", "VideoProcessing", "ImageProcessing", "MediaOptimization",
    "MediaMetadata", "MediaStorage", "ThumbnailGeneration", "MediaCompression",
    "StreamingConfiguration", "MediaDelivery",
    
    # Protection & Fingerprinting
    "ProtectionRequest", "ProtectionOut", "FingerprintCreate", "FingerprintOut",
    "WatermarkRequest", "WatermarkOut", "ViolationReport", "TakedownRequest",
    "CopyrightClaim", "ProtectionAlert", "ProtectionStatistics",
    "AntiPiracyConfiguration", "ContentAuthenticity", "RightsManagement",
    
    # Collaboration
    "CollaborationRequest", "CollaborationUpdate", "CollaborationOut",
    "CollaborationAgreement", "PartnerSearch", "PartnerMatching",
    "CollaborationRevenue", "ProjectManagement", "TeamManagement",
    "CollaborationContract", "NegotiationTerms", "CollaborationAnalytics",
    
    # Copyright & Licensing
    "CopyrightCreate", "CopyrightUpdate", "CopyrightOut", "LicenseAgreement",
    "CopyrightTransfer", "RoyaltyStructure", "IntellectualProperty",
    "LegalDocumentation", "CopyrightDispute", "FairUse",
    "RightsManagement", "LicensingTerms",
    
    # Revenue & Monetization
    "RevenueCreate", "RevenueUpdate", "RevenueOut", "RevenueStream",
    "PaymentRecord", "PaymentMethod", "MonetizationReport",
    "FinancialAnalytics", "TaxInformation", "PayoutSchedule",
    "RevenueSharing", "SubscriptionTier", "PricingModel",
    
    # Distribution & Platforms
    "DistributionRequest", "DistributionUpdate", "DistributionOut",
    "PlatformIntegration", "ContentDelivery", "MultiPlatformSync",
    "DistributionSchedule", "DistributionMetrics", "PlatformConfiguration",
    "ContentOptimization", "AudienceTargeting", "DistributionCampaign",
    
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
