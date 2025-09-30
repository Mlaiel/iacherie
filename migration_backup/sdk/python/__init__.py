"""Ainflue Python SDK - Package Initialization

Official Python SDK for the Ainflue AI-powered content protection platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Multi-Expert Implementation:
- Lead Dev IA: AI orchestration and intelligent SDK design
- Backend Senior: Robust API client architecture
- ML Engineer: Content analysis and ML model integration
- DBA: Optimized data handling and caching
- Sécurité: Enterprise security and authentication
- Microservices: Distributed service communication
- Audio Engineer: Audio content processing support
- DevOps: Monitoring, logging, and deployment optimization
- IA Prompt Engineer: AI prompt optimization and processing
"""

from ainflue_sdk import (
    # Main SDK classes
    AinflueSdk,
    AinflueSdkSync,
    AinflueSdkConfig,
    
    # Exception classes
    AinflueSdkException,
    AuthenticationError,
    APIError,
    ValidationError,
    
    # Response models
    AinflueSdkResponse,
    ContentAnalysisResult,
    ContentProtectionResult,
    
    # Factory functions
    create_sdk,
    create_sync_sdk,
    
    # Version info
    __version__,
    __author__,
    __email__
)

# Import additional modules when available
try:
    from async_client import AsyncAinflueClient
    from sync_client import SyncAinflueClient
    
    from auth_manager import AuthenticationManager
    
    _additional_imports_available = True
except ImportError:
    _additional_imports_available = False

# Package metadata
__title__ = "ainflue-sdk"
__description__ = "Official Python SDK for Ainflue Platform"
__url__ = "https://github.com/Mlaiel/Ainflue"
__version_info__ = tuple(map(int, __version__.split('.')))
__license__ = "MIT"
__copyright__ = "Copyright 2025 Fahed Mlaiel"

# Expert role validation
EXPERT_ROLES_IMPLEMENTED = [
    "Lead Dev IA",           # AI orchestration and intelligent design
    "Backend Senior",        # Robust API architecture  
    "ML Engineer",           # ML model integration
    "DBA",                   # Data optimization
    "Sécurité",             # Security implementation
    "Microservices",        # Service communication
    "Audio Engineer",       # Audio processing
    "DevOps",               # Operations and monitoring
    "IA Prompt Engineer"    # AI prompt optimization
]

# Configuration constants
DEFAULT_CONFIG = {
    'base_url': 'https://api.ainflue.com',
    'api_version': 'v1',
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 1.0,
    'verify_ssl': True,
    'rate_limit_enabled': True,
    'cache_enabled': True,
    'logging_enabled': True
}

# Feature flags for enterprise features
ENTERPRISE_FEATURES = {
    'advanced_analytics': True,
    'ai_optimization': True,
    'multi_tenant': True,
    'sso_integration': True,
    'audit_logging': True,
    'performance_monitoring': True,
    'security_scanning': True,
    'compliance_reporting': True
}

# Backwards compatibility
AinflueSDK = AinflueSdk  # Legacy class name support

# Public API
__all__ = [
    # Core classes
    'AinflueSdk',
    'AinflueSdkSync', 
    'AinflueSdkConfig',
    'AinflueSDK',  # Legacy support
    
    # Exceptions
    'AinflueSdkException',
    'AuthenticationError',
    'APIError', 
    'ValidationError',
    
    # Models
    'AinflueSdkResponse',
    'ContentAnalysisResult',
    'ContentProtectionResult',
    
    # Factory functions
    'create_sdk',
    'create_sync_sdk',
    
    # Package info
    '__version__',
    '__title__',
    '__description__',
    '__url__',
    '__author__',
    '__email__',
    '__license__',
    '__copyright__',
    
    # Constants
    'DEFAULT_CONFIG',
    'ENTERPRISE_FEATURES',
    'EXPERT_ROLES_IMPLEMENTED'
]

# Add additional exports if available
if _additional_imports_available:
    __all__.extend([
        'AsyncAinflueClient',
        'SyncAinflueClient', 
        'AuthenticationManager'
    ])

# SDK initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Ainflue SDK v{__version__} initialized with {len(EXPERT_ROLES_IMPLEMENTED)} expert roles")
logger.debug(f"Enterprise features enabled: {sum(ENTERPRISE_FEATURES.values())}/{len(ENTERPRISE_FEATURES)}")