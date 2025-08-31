"""Handlers Module
==============

Professional handler systems for crawler operations and content processing.
Provides enterprise-grade handling for events, responses, errors, retries, content, and data.

Handler Components:
- ContentHandler: Multi-format content processing and fingerprint preparation
- EventHandler: Real-time event management with Redis queue and priority handling
- ResponseHandler: API response processing, validation, and normalization
- ErrorHandler: Comprehensive error handling with classification and recovery
- RetryHandler: Intelligent retry mechanisms with adaptive backoff strategies
- DataHandler: Data processing, validation, transformation, and storage

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""
# Import all handlers
from .content_handler import (
    ContentHandler,
    ContentTypeDetector,
    ContentProcessor,
    create_content_handler
)
from .event_handler import (
    EventHandler,
    AsyncEventHandler,
    SyncEventHandler,
    EventDispatcher,
    EventQueue,
    EventRegistry,
    Event,
    EventType,
    EventPriority,
    create_event_dispatcher,
    create_content_event,
    create_platform_event
)
from .response_handler import (
    ResponseHandler,
    ResponseValidator,
    ResponseNormalizer,
    ResponseProcessor,
    PlatformResponse,
    YouTubeResponseModel,
    InstagramResponseModel,
    TikTokResponseModel,
    FingerprintResponseModel,
    ResponseType,
    ResponseStatus,
    create_response_handler
)
from .error_handler import (
    ErrorHandler,
    ErrorClassifier,
    ErrorRecoveryManager,
    ErrorAggregator,
    ErrorDetails,
    ErrorContext,
    ErrorCategory,
    ErrorSeverity,
    ErrorAction,
    create_error_handler,
    create_error_context
)
from .retry_handler import (
    RetryHandler,
    RetryExecutor,
    RetryPolicyManager,
    AdaptiveRetryManager,
    CircuitBreaker,
    BackoffCalculator,
    RetryConfig,
    RetryResult,
    RetryStrategy,
    CircuitBreakerState,
    create_retry_handler,
    create_retry_config
)
from .data_handler import (
    DataHandler,
    DataTransformer,
    DataValidator,
    DataStorage,
    ContentMetadataModel,
    FinancialDataModel,
    AnalyticsDataModel,
    DataType,
    DataFormat,
    DataOperation,
    DataSchema,
    DataMetrics,
    create_data_handler
)

# Export all public components
__all__ = [
    # Content Handler
    'ContentHandler',
    'ContentTypeDetector', 
    'ContentProcessor',
    'create_content_handler',
    
    # Event Handler
    'EventHandler',
    'AsyncEventHandler',
    'SyncEventHandler',
    'EventDispatcher',
    'EventQueue',
    'EventRegistry',
    'Event',
    'EventType',
    'EventPriority',
    'create_event_dispatcher',
    'create_content_event',
    'create_platform_event',
    
    # Response Handler
    'ResponseHandler',
    'ResponseValidator',
    'ResponseNormalizer',
    'ResponseProcessor',
    'PlatformResponse',
    'YouTubeResponseModel',
    'InstagramResponseModel',
    'TikTokResponseModel',
    'FingerprintResponseModel',
    'ResponseType',
    'ResponseStatus',
    'create_response_handler',
    
    # Error Handler
    'ErrorHandler',
    'ErrorClassifier',
    'ErrorRecoveryManager',
    'ErrorAggregator',
    'ErrorDetails',
    'ErrorContext',
    'ErrorCategory',
    'ErrorSeverity',
    'ErrorAction',
    'create_error_handler',
    'create_error_context',
    
    # Retry Handler
    'RetryHandler',
    'RetryExecutor',
    'RetryPolicyManager',
    'AdaptiveRetryManager',
    'CircuitBreaker',
    'BackoffCalculator',
    'RetryConfig',
    'RetryResult',
    'RetryStrategy',
    'CircuitBreakerState',
    'create_retry_handler',
    'create_retry_config',
    
    # Data Handler
    'DataHandler',
    'DataTransformer',
    'DataValidator',
    'DataStorage',
    'ContentMetadataModel',
    'FinancialDataModel',
    'AnalyticsDataModel',
    'DataType',
    'DataFormat',
    'DataOperation',
    'DataSchema',
    'DataMetrics',
    'create_data_handler'
]

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
