"""🚀 Enterprise CQRS Module - Complete Architecture
===================================================
Module: events/cqrs/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE CQRS COMPLETE ARCHITECTURE
Complete Command Query Responsibility Segregation implementation
- Advanced command and query buses with enterprise features
- Intelligent dispatchers with load balancing and optimization
- Handler registries with dependency injection and middleware
- Read model projector with multi-storage support
- Eventual consistency manager with reconciliation
- Comprehensive middleware pipeline
- Materialized view management
- Cross-aggregate query engine

This module provides a complete, production-ready CQRS architecture
optimized for high-performance, scalable enterprise applications.
"""

# Core CQRS Components
from .command_bus import (
    Command,
    CommandResult,
    CommandStatus,
    CommandHandler,
    EnterpriseCommandBus,
    get_command_bus,
    reset_command_bus
)

from .query_bus import (
    Query,
    QueryResult,
    QueryStatus,
    QueryHandler,
    CacheLevel,
    EnterpriseQueryBus,
    get_query_bus,
    reset_query_bus
)

# Intelligent Dispatchers
from .command_dispatcher import (
    DispatchStrategy,
    HandlerState,
    HandlerInstance,
    DispatchRule,
    CommandWorkflow,
    EnterpriseCommandDispatcher,
    get_command_dispatcher,
    reset_command_dispatcher
)

from .query_dispatcher import (
    QueryRoutingStrategy,
    ReadModelState,
    ReadModelInstance,
    QueryRoutingRule,
    EnterpriseQueryDispatcher,
    get_query_dispatcher,
    reset_query_dispatcher
)

# Handler Registries
from .command_handler_registry import (
    HandlerLifecycle,
    MiddlewarePhase,
    HandlerMetadata,
    HandlerInstance as CommandHandlerInstance,
    command_handler,
    EnterpriseCommandHandlerRegistry,
    get_command_handler_registry,
    reset_command_handler_registry
)

from .query_handler_registry import (
    QueryHandlerState,
    CacheStrategy,
    QueryHandlerMetadata,
    QueryHandlerInstance,
    query_handler,
    EnterpriseQueryHandlerRegistry,
    get_query_handler_registry,
    reset_query_handler_registry
)

# Read Model Projector
from .read_model_projector import (
    ProjectionMode,
    ReadModelType,
    ProjectionState,
    ReadModelSchema,
    ProjectionDefinition,
    EventProjector,
    ReadModelStore,
    InMemoryReadModelStore,
    EnterpriseReadModelProjector,
    get_read_model_projector,
    reset_read_model_projector,
    create_default_in_memory_store
)

# Eventual Consistency Manager
from .eventual_consistency_manager import (
    ConsistencyLevel,
    ConsistencyState,
    ReconciliationStrategy,
    ConsistencyRule,
    ConsistencyViolation,
    AggregateSnapshot,
    EnterpriseEventualConsistencyManager,
    get_consistency_manager,
    reset_consistency_manager
)

# Middleware Pipeline
from .cqrs_middleware import (
    MiddlewareExecutionPhase,
    AuthenticationResult,
    AuthorizationResult,
    MiddlewareContext,
    AuthenticationContext,
    BaseMiddleware,
    AuthenticationMiddleware,
    AuthorizationMiddleware,
    ValidationMiddleware,
    MetricsMiddleware,
    RateLimitingMiddleware,
    AuditLoggingMiddleware,
    ErrorHandlingMiddleware,
    CQRSMiddlewarePipeline,
    get_default_middleware_pipeline,
    reset_default_middleware_pipeline
)

# Materialized View Manager
from .materialized_view_manager import (
    MaterializedViewType,
    RefreshStrategy,
    ViewState,
    MaterializedViewDefinition,
    MaterializedViewInstance,
    ViewStorageBackend,
    InMemoryViewBackend,
    EnterpriseMaterializedViewManager,
    get_materialized_view_manager,
    reset_materialized_view_manager
)

# Cross-Aggregate Query Engine
from .cross_aggregate_query_engine import (
    JoinType,
    AggregationFunction,
    QueryExecutionStrategy,
    AggregateSource,
    JoinCondition,
    AggregationSpec,
    CrossAggregateQuery,
    QueryExecutionPlan,
    QueryExecutionResult,
    AggregateDataProvider,
    EnterpriseCrossAggregateQueryEngine,
    get_cross_aggregate_query_engine,
    reset_cross_aggregate_query_engine,
    create_user_orders_query
)

# Convenience imports for common usage patterns
__all__ = [
    # Core CQRS
    "Command", "CommandResult", "CommandStatus", "CommandHandler",
    "Query", "QueryResult", "QueryStatus", "QueryHandler",
    "EnterpriseCommandBus", "EnterpriseQueryBus",
    
    # Dispatchers
    "EnterpriseCommandDispatcher", "EnterpriseQueryDispatcher",
    "DispatchStrategy", "QueryRoutingStrategy",
    
    # Handler Registries
    "EnterpriseCommandHandlerRegistry", "EnterpriseQueryHandlerRegistry",
    "command_handler", "query_handler",
    
    # Read Model Projector
    "EnterpriseReadModelProjector", "EventProjector", "ReadModelStore",
    "ProjectionDefinition", "ReadModelSchema",
    
    # Eventual Consistency
    "EnterpriseEventualConsistencyManager", "ConsistencyRule", "ConsistencyLevel",
    
    # Middleware
    "CQRSMiddlewarePipeline", "BaseMiddleware", "MiddlewareContext",
    
    # Materialized Views
    "EnterpriseMaterializedViewManager", "MaterializedViewDefinition",
    
    # Cross-Aggregate Queries
    "EnterpriseCrossAggregateQueryEngine", "CrossAggregateQuery",
    
    # Singleton accessors
    "get_command_bus", "get_query_bus",
    "get_command_dispatcher", "get_query_dispatcher",
    "get_command_handler_registry", "get_query_handler_registry",
    "get_read_model_projector", "get_consistency_manager",
    "get_default_middleware_pipeline", "get_materialized_view_manager",
    "get_cross_aggregate_query_engine"
]

# Version information
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise CQRS Architecture - Ultra Advanced Industrial Implementation"


def get_cqrs_architecture_info() -> dict:
    """Get comprehensive information about the CQRS architecture"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "command_bus": "Enterprise command processing with circuit breaker, rate limiting, and retry logic",
            "query_bus": "Enterprise query processing with multi-level caching and performance optimization",
            "command_dispatcher": "Intelligent command routing with load balancing and transaction coordination",
            "query_dispatcher": "Intelligent query routing with geographic affinity and cache optimization",
            "command_handler_registry": "Advanced handler management with dependency injection and middleware",
            "query_handler_registry": "Query handler management with intelligent caching and performance monitoring",
            "read_model_projector": "Multi-storage read model projection with real-time and batch processing",
            "eventual_consistency_manager": "Cross-aggregate consistency management with reconciliation",
            "cqrs_middleware": "Comprehensive middleware pipeline for auth, validation, and monitoring",
            "materialized_view_manager": "Advanced materialized view management for high-performance queries",
            "cross_aggregate_query_engine": "Complex queries spanning multiple aggregates with optimization"
        },
        "features": [
            "Enterprise-grade scalability and performance",
            "Advanced caching strategies with intelligent invalidation",
            "Real-time performance monitoring and adaptive optimization",
            "Geographic distribution and consistency management",
            "Circuit breaker patterns and fault tolerance",
            "Comprehensive security and audit logging",
            "Multi-storage backend support",
            "Intelligent query optimization and routing",
            "Event sourcing integration",
            "Microservices-ready architecture"
        ],
        "architecture_patterns": [
            "Command Query Responsibility Segregation (CQRS)",
            "Event Sourcing",
            "Saga Pattern",
            "Circuit Breaker",
            "Bulkhead Isolation",
            "Cache-Aside",
            "Materialized View",
            "Event-Driven Architecture",
            "Microservices",
            "Domain-Driven Design (DDD)"
        ]
    }


def setup_default_cqrs_infrastructure():
    """Setup default CQRS infrastructure with recommended configuration"""
    
    # Initialize core buses
    command_bus = get_command_bus()
    query_bus = get_query_bus()
    
    # Initialize dispatchers
    command_dispatcher = get_command_dispatcher()
    query_dispatcher = get_query_dispatcher()
    
    # Initialize handler registries
    command_handler_registry = get_command_handler_registry()
    query_handler_registry = get_query_handler_registry()
    
    # Initialize read model projector
    read_model_projector = get_read_model_projector()
    
    # Initialize consistency manager
    consistency_manager = get_consistency_manager()
    
    # Initialize middleware pipeline
    middleware_pipeline = get_default_middleware_pipeline()
    
    # Initialize materialized view manager
    materialized_view_manager = get_materialized_view_manager()
    
    # Initialize cross-aggregate query engine
    cross_aggregate_engine = get_cross_aggregate_query_engine()
    
    return {
        "command_bus": command_bus,
        "query_bus": query_bus,
        "command_dispatcher": command_dispatcher,
        "query_dispatcher": query_dispatcher,
        "command_handler_registry": command_handler_registry,
        "query_handler_registry": query_handler_registry,
        "read_model_projector": read_model_projector,
        "consistency_manager": consistency_manager,
        "middleware_pipeline": middleware_pipeline,
        "materialized_view_manager": materialized_view_manager,
        "cross_aggregate_engine": cross_aggregate_engine
    }


async def shutdown_cqrs_infrastructure():
    """Gracefully shutdown all CQRS components"""
    
    # Shutdown components in reverse dependency order
    components = [
        get_cross_aggregate_query_engine(),
        get_materialized_view_manager(),
        get_consistency_manager(),
        get_read_model_projector(),
        get_query_handler_registry(),
        get_command_handler_registry(),
        get_query_dispatcher(),
        get_command_dispatcher(),
        get_query_bus(),
        get_command_bus()
    ]
    
    for component in components:
        if hasattr(component, 'shutdown'):
            try:
                await component.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down {type(component).__name__}: {e}")
    
    # Reset all singletons
    reset_cross_aggregate_query_engine()
    reset_materialized_view_manager()
    reset_consistency_manager()
    reset_read_model_projector()
    reset_query_handler_registry()
    reset_command_handler_registry()
    reset_query_dispatcher()
    reset_command_dispatcher()
    reset_query_bus()
    reset_command_bus()
    reset_default_middleware_pipeline()


# Module-level logger
import logging
logger = logging.getLogger(__name__)

# Log module initialization
logger.info("🚀 Enterprise CQRS Module Initialized - Ultra Advanced Industrial Architecture v3.0.0")
logger.info("✅ All CQRS components loaded and ready for enterprise-grade operations")