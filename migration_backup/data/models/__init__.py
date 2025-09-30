"""Data Models module __init__.py
=============================

Professional data models and schemas for IA Influencer Agent platform.
Complete enterprise-level data models for content management, user analytics,
fingerprinting, revenue tracking, content protection, and licensing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

🚀 TEAM SPECIALISTS:
• Lead Dev IA + Backend Senior: Fahed Mlaiel
• ML Engineer + Audio Specialist: Advanced AI Processing
• DevOps + Infrastructure: Enterprise Deployment
• DBA + Data Engineer: High-Performance Database Architecture
• Security Specialist: Multi-Layer Protection Systems
• Microservices Architect: Scalable Service Architecture
• IA Prompt Engineer: Advanced AI Integration
"""# Import all data models from consolidated modules
try:
    from .enterprise_content_models import (
        ContentModel, ContentType, ContentStatus, ContentVisibility,
        UserModel, UserType, UserStatus, SubscriptionTier,
        AnalyticsModel, AnalyticsType, MetricType, TimeGranularity
    )
    CONTENT_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Content models import failed: {e}")
    CONTENT_MODELS_AVAILABLE = False

try:
    from .ai_fingerprinting_protection_models import (
        FingerprintModel, FingerprintType, FingerprintAlgorithm, FingerprintStatus, MatchConfidenceLevel,
        ProtectionModel, ProtectionType, ViolationType, SeverityLevel, ProtectionStatus, EnforcementAction
    )
    FINGERPRINT_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Fingerprint models import failed: {e}")
    FINGERPRINT_MODELS_AVAILABLE = False

try:
    from .monetization_licensing_models import (
        RevenueModel, RevenueSource, RevenueStatus, PaymentMethod, RevenuePeriod,
        LicensingModel, LicenseType, LicenseCategory, UsageType, LicenseStatus, PaymentStructure
    )
    MONETIZATION_MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Monetization models import failed: {e}")
    MONETIZATION_MODELS_AVAILABLE = False

# Export all models and enums
# Import additional utilities from consolidated infrastructure
try:
    from .index import ModelManager, ModelQueryBuilder, model_manager
    INDEX_AVAILABLE = True
except ImportError as e:
    print(f"Index import failed: {e}")
    INDEX_AVAILABLE = False

try:
    from .data_infrastructure_utilities import (
        ValidationError, ValidationResult, ModelDataValidator,
        validate_user, validate_content, validate_revenue, validate_analytics,
        MigrationManager, SchemaValidator, ExampleDataGenerator
    )
    UTILITIES_AVAILABLE = True
except ImportError as e:
    UTILITIES_AVAILABLE = False
    print(f"Some utilities not available: {e}")

# Export all for easy access
__all__ = []

# Add models if available
if CONTENT_MODELS_AVAILABLE:
    __all__.extend([
        'ContentModel', 'UserModel', 'AnalyticsModel',
        'ContentType', 'ContentStatus', 'ContentVisibility',
        'UserType', 'UserStatus', 'SubscriptionTier',
        'AnalyticsType', 'MetricType', 'TimeGranularity'
    ])

if FINGERPRINT_MODELS_AVAILABLE:
    __all__.extend([
        'FingerprintModel', 'ProtectionModel',
        'FingerprintType', 'FingerprintAlgorithm', 'FingerprintStatus', 'MatchConfidenceLevel',
        'ProtectionType', 'ViolationType', 'SeverityLevel', 'ProtectionStatus', 'EnforcementAction'
    ])

if MONETIZATION_MODELS_AVAILABLE:
    __all__.extend([
        'RevenueModel', 'LicensingModel',
        'RevenueSource', 'RevenueStatus', 'PaymentMethod', 'RevenuePeriod',
        'LicenseType', 'LicenseCategory', 'UsageType', 'LicenseStatus', 'PaymentStructure'
    ])

# Core utilities and availability flags always available
__all__.extend([
    'MODEL_REGISTRY', 'RELATIONSHIP_MAPPINGS',
    'get_model_by_table_name', 'get_all_models', 'get_model_relationships',
    'CONTENT_MODELS_AVAILABLE', 'FINGERPRINT_MODELS_AVAILABLE', 
    'MONETIZATION_MODELS_AVAILABLE', 'INDEX_AVAILABLE', 'UTILITIES_AVAILABLE'
])

# Add utilities if available
if INDEX_AVAILABLE:
    __all__.extend([
        'ModelManager', 'ModelQueryBuilder', 'model_manager'
    ])

if UTILITIES_AVAILABLE:
    __all__.extend([
        'ValidationError', 'ValidationResult', 'ModelDataValidator',
        'validate_user', 'validate_content', 'validate_revenue', 'validate_analytics',
        'MigrationManager', 'SchemaValidator', 'ExampleDataGenerator'
    ])

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel - All Rights Reserved"

# Model metadata for introspection (only add if models are available)
MODEL_REGISTRY = {}
if CONTENT_MODELS_AVAILABLE:
    MODEL_REGISTRY.update({
        'content': ContentModel,
        'users': UserModel,
        'analytics': AnalyticsModel
    })

if FINGERPRINT_MODELS_AVAILABLE:
    MODEL_REGISTRY.update({
        'fingerprints': FingerprintModel,
        'protection': ProtectionModel
    })

if MONETIZATION_MODELS_AVAILABLE:
    MODEL_REGISTRY.update({
        'revenue': RevenueModel,
        'licensing': LicensingModel
    })

# Relationship mappings for ORM
RELATIONSHIP_MAPPINGS = {
    'user_content': 'One user can have many content items',
    'content_fingerprints': 'One content item can have multiple fingerprints',
    'content_analytics': 'One content item has many analytics records',
    'content_revenue': 'One content item can generate multiple revenue streams',
    'content_protection': 'One content item can have multiple protection records',
    'content_licenses': 'One content item can have multiple licenses',
    'user_analytics': 'One user has comprehensive analytics',
    'user_revenue': 'One user has multiple revenue records',
    'user_protection': 'One user has multiple protection cases',
    'user_fingerprints': 'One user has multiple content fingerprints',
    'user_licenses': 'One user can create multiple licenses',
    'fingerprint_protection': 'One fingerprint can trigger multiple protection alerts'
}

def get_model_by_table_name(table_name: str):
    """Get model class by table name"""
    return MODEL_REGISTRY.get(table_name)

def get_all_models():
    """
Get all registered models"""
    return list(MODEL_REGISTRY.values())

def get_model_relationships():
    """
Get model relationship information"""
    return RELATIONSHIP_MAPPINGS
