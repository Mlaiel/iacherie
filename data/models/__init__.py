"""
Data Models module __init__.py
=============================

Professional data models and schemas for IA Influencer Agent platform.
Complete enterprise-level data models for content management, user analytics,
fingerprinting, revenue tracking, content protection, and licensing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

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
"""

# Import all data models
from .content_model import ContentModel, ContentType, ContentStatus, ContentVisibility
from .user_model import UserModel, UserType, UserStatus, SubscriptionTier
from .fingerprint_model import FingerprintModel, FingerprintType, FingerprintAlgorithm, FingerprintStatus, MatchConfidenceLevel
from .revenue_model import RevenueModel, RevenueSource, RevenueStatus, PaymentMethod, RevenuePeriod
from .analytics_model import AnalyticsModel, AnalyticsType, MetricType, TimeGranularity
from .protection_model import ProtectionModel, ProtectionType, ViolationType, SeverityLevel, ProtectionStatus, EnforcementAction
from .licensing_model import LicensingModel, LicenseType, LicenseCategory, UsageType, LicenseStatus, PaymentStructure

# Export all models and enums
# Import additional utilities
try:
    from .index import ModelManager, ModelQueryBuilder, model_manager
    from .validators import (
        ValidationError, ValidationResult, ModelDataValidator,
        validate_user, validate_content, validate_revenue, validate_analytics
    )
    from .migrations import MigrationManager, SchemaValidator
    UTILITIES_AVAILABLE = True
except ImportError as e:
    UTILITIES_AVAILABLE = False
    print(f"Some utilities not available: {e}")

# Export all for easy access
__all__ = [
    # Models
    'ContentModel', 'UserModel', 'FingerprintModel', 'RevenueModel',
    'AnalyticsModel', 'ProtectionModel', 'LicensingModel',
    
    # Enums
    'ContentType', 'ContentStatus', 'ContentVisibility',
    'UserType', 'UserStatus', 'SubscriptionTier',
    'FingerprintType', 'FingerprintAlgorithm', 'FingerprintStatus', 'MatchConfidenceLevel',
    'RevenueSource', 'RevenueStatus', 'PaymentMethod', 'RevenuePeriod',
    'AnalyticsType', 'MetricType', 'TimeGranularity',
    'ProtectionType', 'ViolationType', 'SeverityLevel', 'ProtectionStatus', 'EnforcementAction',
    'LicenseType', 'LicenseCategory', 'UsageType', 'LicenseStatus', 'PaymentStructure',
    
    # Core Utilities
    'MODEL_REGISTRY', 'RELATIONSHIP_MAPPINGS',
    'get_model_by_table_name', 'get_all_models', 'get_model_relationships'
]

# Add utilities to exports if available
if UTILITIES_AVAILABLE:
    __all__.extend([
        # Management & Query Tools
        'ModelManager', 'ModelQueryBuilder', 'model_manager',
        
        # Validation Tools
        'ValidationError', 'ValidationResult', 'ModelDataValidator',
        'validate_user', 'validate_content', 'validate_revenue', 'validate_analytics',
        
        # Migration Tools
        'MigrationManager', 'SchemaValidator'
    ])

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"

# Model metadata for introspection
MODEL_REGISTRY = {
    'content': ContentModel,
    'users': UserModel,
    'fingerprints': FingerprintModel,
    'revenue': RevenueModel,
    'analytics': AnalyticsModel,
    'protection': ProtectionModel,
    'licensing': LicensingModel
}

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
    """Get all registered models"""
    return list(MODEL_REGISTRY.values())

def get_model_relationships():
    """Get model relationship information"""
    return RELATIONSHIP_MAPPINGS
