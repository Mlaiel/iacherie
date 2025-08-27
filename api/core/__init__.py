"""
Enterprise-grade core infrastructure for IA Influencer Agent.
Professional foundation with comprehensive business logic support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

# Core configuration and database
from .config import settings
from .db import SessionLocal, get_db
from .logging import configure_logging
from .security import api_key_auth

# Enterprise systems
from .exceptions import (
    BaseApplicationException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ContentNotFoundException,
    ExternalServiceException,
    DatabaseException,
    ValidationException,
    RateLimitException,
    ContentProtectionException,
    FingerprintException,
    ErrorCode,
    convert_to_http_exception,
    get_error_message
)

from .container import (
    ServiceContainer,
    IServiceContainer,
    ServiceLifetime,
    ServiceLocator,
    register_singleton,
    register_transient,
    register_scoped,
    register_factory,
    register_instance,
    resolve,
    get_container,
    create_scope,
    Injectable,
    injectable,
    service
)

from .events import (
    DomainEvent,
    EventPriority,
    EventStatus,
    IEventHandler,
    IEventStore,
    EventBus,
    ContentUploadedEvent,
    FingerprintGeneratedEvent,
    ContentProtectedEvent,
    InfringementDetectedEvent,
    RevenueGeneratedEvent,
    get_event_bus,
    publish_event,
    event_handler
)

from .cache import (
    CacheStrategy,
    CacheLevel,
    ICacheProvider,
    InMemoryCache,
    MultiLevelCache,
    CacheManager,
    get_cache_manager,
    get_memory_cache,
    get_multi_level_cache
)

from .context import (
    RequestContext,
    UserContext,
    RequestMetadata,
    BusinessContext,
    ContextManager,
    ContextMiddleware,
    get_context_manager,
    get_current_context,
    set_current_context,
    get_correlation_id,
    get_user_id,
    get_tenant_id,
    is_authenticated,
    has_role,
    has_permission,
    with_business_operation
)

from .metrics import (
    MetricType,
    MetricUnit,
    IMetricsCollector,
    InMemoryMetricsCollector,
    MetricsRegistry,
    BusinessMetrics,
    get_metrics_collector,
    get_metrics_registry,
    get_business_metrics,
    timing_decorator,
    counter_decorator
)

from .health import (
    HealthStatus,
    ComponentType,
    HealthCheckResult,
    SystemHealthStatus,
    IHealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
    ExternalAPIHealthCheck,
    StorageHealthCheck,
    HealthCheckManager,
    SimpleHealthCheck,
    get_health_manager,
    register_health_check,
    check_system_health,
    check_component_health
)

from .rate_limit import (
    RateLimitAlgorithm,
    RateLimitScope,
    RateLimitConfig,
    RateLimitResult,
    IRateLimitStorage,
    InMemoryRateLimitStorage,
    TokenBucketRateLimit,
    RateLimiter,
    get_rate_limiter,
    check_rate_limit,
    rate_limit
)

__all__ = [
    # Core infrastructure
    "settings",
    "SessionLocal",
    "get_db",
    "configure_logging",
    "api_key_auth",
    
    # Exception handling
    "BaseApplicationException",
    "AuthenticationException",
    "AuthorizationException",
    "BusinessLogicException",
    "ContentNotFoundException",
    "ExternalServiceException",
    "DatabaseException",
    "ValidationException",
    "RateLimitException",
    "ContentProtectionException",
    "FingerprintException",
    "ErrorCode",
    "convert_to_http_exception",
    "get_error_message",
    
    # Dependency injection
    "ServiceContainer",
    "IServiceContainer",
    "ServiceLifetime",
    "ServiceLocator",
    "register_singleton",
    "register_transient",
    "register_scoped",
    "register_factory",
    "register_instance",
    "resolve",
    "get_container",
    "create_scope",
    "Injectable",
    "injectable",
    "service",
    
    # Event handling
    "DomainEvent",
    "EventPriority",
    "EventStatus",
    "IEventHandler",
    "IEventStore",
    "EventBus",
    "ContentUploadedEvent",
    "FingerprintGeneratedEvent",
    "ContentProtectedEvent",
    "InfringementDetectedEvent",
    "RevenueGeneratedEvent",
    "get_event_bus",
    "publish_event",
    "event_handler",
    
    # Caching system
    "CacheStrategy",
    "CacheLevel",
    "ICacheProvider",
    "InMemoryCache",
    "MultiLevelCache",
    "CacheManager",
    "get_cache_manager",
    "get_memory_cache",
    "get_multi_level_cache",
    
    # Request context
    "RequestContext",
    "UserContext",
    "RequestMetadata",
    "BusinessContext",
    "ContextManager",
    "ContextMiddleware",
    "get_context_manager",
    "get_current_context",
    "set_current_context",
    "get_correlation_id",
    "get_user_id",
    "get_tenant_id",
    "is_authenticated",
    "has_role",
    "has_permission",
    "with_business_operation",
    
    # Metrics and monitoring
    "MetricType",
    "MetricUnit",
    "IMetricsCollector",
    "InMemoryMetricsCollector",
    "MetricsRegistry",
    "BusinessMetrics",
    "get_metrics_collector",
    "get_metrics_registry",
    "get_business_metrics",
    "timing_decorator",
    "counter_decorator",
    
    # Health monitoring
    "HealthStatus",
    "ComponentType",
    "HealthCheckResult",
    "SystemHealthStatus",
    "IHealthCheck",
    "DatabaseHealthCheck",
    "RedisHealthCheck",
    "ExternalAPIHealthCheck",
    "StorageHealthCheck",
    "HealthCheckManager",
    "SimpleHealthCheck",
    "get_health_manager",
    "register_health_check",
    "check_system_health",
    "check_component_health",
    
    # Rate limiting
    "RateLimitAlgorithm",
    "RateLimitScope",
    "RateLimitConfig",
    "RateLimitResult",
    "IRateLimitStorage",
    "InMemoryRateLimitStorage",
    "TokenBucketRateLimit",
    "RateLimiter",
    "get_rate_limiter",
    "check_rate_limit",
    "rate_limit",
]
