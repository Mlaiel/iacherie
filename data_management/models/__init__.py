"""
🗄️ Data Models Module - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/models/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Data Models - Ultra Enterprise Production-Ready
Responsibility: Advanced data models for multi-format creators with AI protection and monetization
==================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC MODELS PIPELINE:
Creator Registration → Content Upload → AI Validation → Metadata Extraction → 
Vector Indexing → Protection Activation → Analytics Processing → Revenue Optimization
"""

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

# Core Content Models
from .content_model import (
    ContentModel, ContentMetadata, ContentFingerprint,
    ContentType, ContentStatus, ContentQuality, ContentOriginality,
    DistributionStatus, MonetizationStatus,
    validate_content_type, generate_content_path, calculate_content_hash
)

# Creator Models
from .creator_model import (
    CreatorModel, CreatorProfile, CreatorSettings,
    CreatorType, CreatorStatus, SubscriptionTier, VerificationLevel, CreatorTier,
    generate_username, validate_creator_email, calculate_creator_score
)

# Analytics Models
from .analytics_model import AnalyticsModel, MetricsModel, RevenueModel

# Fingerprint Models
from .fingerprint_model import (
    FingerPrintModel, AudioFingerprint, VideoFingerprint,
    FingerprintType, FingerprintAlgorithm, FingerprintQuality, SimilarityThreshold
)

# Protection Models
from .protection_model import ProtectionModel, ViolationModel, TakedownModel

# Monetization Models
from .monetization_model import (
    MonetizationModel, RevenueTrackingModel, PaymentModel,
    RevenueSource, PaymentMethod, PaymentStatus, TaxStatus, RevenueCategory,
    calculate_revenue_projection, optimize_payout_schedule
)

# Collaboration Models
from .collaboration_model import CollaborationModel, MatchingModel, ProjectModel

# Licensing Models
from .licensing_model import LicensingModel, LicenseTerms, RoyaltyStructure, LicenseType, LicenseStatus

# Platform Models
from .platform_model import PlatformModel, IntegrationModel, APIModel

# Audit Models
from .audit_model import AuditModel, LogModel, EventModel

# Governance Models
from .governance_model import GovernanceModel, ComplianceModel, PolicyModel

__all__ = [
    # Content Models
    "ContentModel", "ContentMetadata", "ContentFingerprint",
    "ContentType", "ContentStatus", "ContentQuality", "ContentOriginality",
    "DistributionStatus", "MonetizationStatus",
    "validate_content_type", "generate_content_path", "calculate_content_hash",
    
    # Creator Models
    "CreatorModel", "CreatorProfile", "CreatorSettings",
    "CreatorType", "CreatorStatus", "SubscriptionTier", "VerificationLevel", "CreatorTier",
    "generate_username", "validate_creator_email", "calculate_creator_score",
    
    # Analytics Models
    "AnalyticsModel", "MetricsModel", "RevenueModel",
    
    # Fingerprint Models
    "FingerPrintModel", "AudioFingerprint", "VideoFingerprint",
    "FingerprintType", "FingerprintAlgorithm", "FingerprintQuality", "SimilarityThreshold",
    
    # Protection Models
    "ProtectionModel", "ViolationModel", "TakedownModel",
    
    # Monetization Models
    "MonetizationModel", "RevenueTrackingModel", "PaymentModel",
    "RevenueSource", "PaymentMethod", "PaymentStatus", "TaxStatus", "RevenueCategory",
    "calculate_revenue_projection", "optimize_payout_schedule",
    
    # Collaboration Models
    "CollaborationModel", "MatchingModel", "ProjectModel",
    
    # Platform Models
    "PlatformModel", "IntegrationModel", "APIModel",
    
    # Audit Models
    "AuditModel", "LogModel", "EventModel",
    
    # Governance Models
    "GovernanceModel", "ComplianceModel", "PolicyModel"
]

# Model registry for dynamic access
MODEL_REGISTRY = {
    "content": ContentModel,
    "creator": CreatorModel,
    "analytics": AnalyticsModel,
    "fingerprint": FingerPrintModel,
    "protection": ProtectionModel,
    "monetization": MonetizationModel,
    "collaboration": CollaborationModel,
    "licensing": LicensingModel,
    "platform": PlatformModel,
    "audit": AuditModel,
    "governance": GovernanceModel
}

def get_model(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name.lower())

def list_available_models():
    """List all available model names"""
    return list(MODEL_REGISTRY.keys())

# Export all models
__all__ = [
    "ProtectionModel", "ViolationModel", "TakedownModel",
    
    # Monetization Models
    "MonetizationModel", "RevenueTrackingModel", "PaymentModel",
    
    # Collaboration Models
    "CollaborationModel", "MatchingModel", "ProjectModel",
    
    # Platform Models
    "PlatformModel", "IntegrationModel", "APIModel",
    
    # Audit Models
    "AuditModel", "LogModel", "EventModel",
    
    # Governance Models
    "GovernanceModel", "ComplianceModel", "PolicyModel"
]
