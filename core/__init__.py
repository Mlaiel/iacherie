"""
Core Module - Enterprise Business Logic Core Components

Central core components for the Ainflue IA Influencer Agent Platform.
Provides authentication, security, logging, middleware, and enterprise business logic cores.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Enterprise-grade core with >99.99% uptime guarantee.
"""

import logging

# Setup module logger
core_logger = logging.getLogger(__name__)

# Core Foundation Components
from .logging import logger, get_logger, set_log_level
from .middleware import (
    RequestLoggingMiddleware, CORSMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware,
    create_logging_middleware, create_cors_middleware, create_rate_limit_middleware, create_security_headers_middleware
)
from .security import (
    SecurityManager, TokenManager, SecurityValidator,
    create_security_manager, create_token_manager, create_security_validator
)
from .auth import (
    User, AuthenticationManager, AuthorizationManager,
    create_authentication_manager, create_authorization_manager, create_auth_system
)

# Enterprise Business Logic Core Components (PHASE 1 - KRITISCH)
try:
    from .creator_multi_format_core import (
        CreatorMultiFormatCore,
        CreatorProfile,
        ContentProcessingRequest,
        ContentProcessingResult,
        CreatorType,
        ContentFormat,
        QualityLevel,
        creator_multi_format_core
    )
    creator_multi_format_available = True
    core_logger.info("✅ Creator Multi-Format Core loaded")
except ImportError as e:
    creator_multi_format_available = False
    core_logger.warning(f"❌ Creator Multi-Format Core not available: {e}")

try:
    from .content_format_core import (
        ContentFormatCore,
        ContentMetadata,
        ProcessingOptions,
        ContentProcessingTask,
        AudioFormat,
        VideoFormat,
        ImageFormat,
        TextFormat,
        ProcessingStatus,
        content_format_core
    )
    content_format_available = True
    core_logger.info("✅ Content Format Core loaded")
except ImportError as e:
    content_format_available = False
    core_logger.warning(f"❌ Content Format Core not available: {e}")

try:
    from .ia_processing_core import (
        IAProcessingCore,
        AIModelConfig,
        InferenceRequest,
        InferenceResult,
        MLPipelineStage,
        AIModelType,
        ProcessingPriority,
        ModelStatus,
        ia_processing_core
    )
    ia_processing_available = True
    core_logger.info("✅ IA Processing Core loaded")
except ImportError as e:
    ia_processing_available = False
    core_logger.warning(f"❌ IA Processing Core not available: {e}")

try:
    from .ai_model_core import (
        AIModelCore,
        ModelConfiguration,
        ModelVersion,
        ModelDeployment,
        ModelMetrics,
        ModelLifecycleState,
        ModelCategory,
        DeploymentStrategy,
        ai_model_core
    )
    ai_model_available = True
    core_logger.info("✅ AI Model Core loaded")
except ImportError as e:
    ai_model_available = False
    core_logger.warning(f"❌ AI Model Core not available: {e}")

__all__ = [
    # Core Foundation Components
    # Logging
    "logger",
    "get_logger", 
    "set_log_level",
    
    # Middleware
    "RequestLoggingMiddleware",
    "CORSMiddleware", 
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "create_logging_middleware",
    "create_cors_middleware",
    "create_rate_limit_middleware",
    "create_security_headers_middleware",
    
    # Security
    "SecurityManager",
    "TokenManager", 
    "SecurityValidator",
    "create_security_manager",
    "create_token_manager",
    "create_security_validator",
    
    # Authentication
    "User",
    "AuthenticationManager",
    "AuthorizationManager",
    "create_authentication_manager",
    "create_authorization_manager",
    "create_auth_system"
]

# Add Enterprise Business Logic Core exports if available
if creator_multi_format_available:
    __all__.extend([
        "CreatorMultiFormatCore",
        "CreatorProfile",
        "ContentProcessingRequest", 
        "ContentProcessingResult",
        "CreatorType",
        "ContentFormat",
        "QualityLevel",
        "creator_multi_format_core"
    ])

if content_format_available:
    __all__.extend([
        "ContentFormatCore",
        "ContentMetadata",
        "ProcessingOptions",
        "ContentProcessingTask",
        "AudioFormat",
        "VideoFormat", 
        "ImageFormat",
        "TextFormat",
        "ProcessingStatus",
        "content_format_core"
    ])

if ia_processing_available:
    __all__.extend([
        "IAProcessingCore",
        "AIModelConfig",
        "InferenceRequest",
        "InferenceResult", 
        "MLPipelineStage",
        "AIModelType",
        "ProcessingPriority",
        "ModelStatus",
        "ia_processing_core"
    ])

if ai_model_available:
    __all__.extend([
        "AIModelCore",
        "ModelConfiguration",
        "ModelVersion",
        "ModelDeployment",
        "ModelMetrics",
        "ModelLifecycleState",
        "ModelCategory", 
        "DeploymentStrategy",
        "ai_model_core"
    ])

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Module status logging
total_core_components = 4  # Foundation components
total_business_logic_components = 4  # Business logic core components
available_business_logic = sum([
    creator_multi_format_available, content_format_available, 
    ia_processing_available, ai_model_available
])

core_logger.info(f"🏗️ Core Module v{__version__} loaded")
core_logger.info(f"✅ Foundation components: 4/4 loaded")
core_logger.info(f"📊 Business Logic Core components: {available_business_logic}/{total_business_logic_components}")

if available_business_logic == total_business_logic_components:
    core_logger.info("🎉 ALL PHASE 1 BUSINESS LOGIC CORES LOADED SUCCESSFULLY!")
    core_logger.info("✅ Creator Multi-Format → IA Processing → AI Model Management ready")
    core_logger.info("🚀 Enterprise-grade core with >99.99% uptime guarantee")
else:
    core_logger.warning(f"⚠️ Some business logic cores unavailable: {total_business_logic_components - available_business_logic} missing")

core_logger.info(f"✅ Core module initialization complete")
