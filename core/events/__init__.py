"""IA-Influencer-Agent - Events Management System
Module: backend/core/events/__init__.py
Architecture: Core Events System for Content Creation and Protection
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Système central de gestion d'événements pour la plateforme IA-Influencer-Agent.
    Gère les événements métier, notifications temps réel, et orchestration des workflows.
    Support événements : upload contenu, protection, monétisation, collaboration.
"""
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
import logging

# Configuration logging
logger = logging.getLogger(__name__)

# Imports des composants principaux
from .event_bus import EventBus, Event
from .event_dispatcher import EventDispatcher, EventHandler
from .event_store import EventStore, EventStream
from .event_publisher import EventPublisher, NotificationService
from .event_aggregator import EventAggregator, EventProcessor
from .event_scheduler import EventScheduler, DelayedEventHandler
from .event_types import (
    EventType,
    ContentEvent,
    ProtectionEvent,
    MonetizationEvent,
    CollaborationEvent,
    SystemEvent
)
from .event_middleware import (
    EventMiddleware,
    AuthenticationMiddleware,
    ValidationMiddleware,
    LoggingMiddleware,
    MetricsMiddleware
)
from .webhook_manager import WebhookManager, WebhookProcessor
from .notification_channels import (
    NotificationChannel,
    EmailChannel,
    WebSocketChannel,
    PushNotificationChannel,
    SlackChannel
)
from .event_metrics import (
    EventMetricsManager,
    MetricCollector,
    EventMetricsCollector,
    SystemMetricsCollector,
    BusinessMetricsCollector,
    AlertManager,
    MetricType,
    AlertSeverity,
    event_metrics_manager
)
from .event_workflows import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStep,
    WorkflowStatus,
    StepType,
    initialize_workflow_engine,
    create_content_processing_workflow,
    create_violation_response_workflow
)
from .event_replication import (
    EventReplicationManager,
    ReplicationTarget,
    ReplicationStrategy,
    ReplicationStatus,
    ReplicationConnector,
    DatabaseReplicationConnector,
    APIReplicationConnector,
    WebSocketReplicationConnector,
    RedisReplicationConnector,
    initialize_replication_manager
)
from .event_resilience import (
    EventResilienceManager,
    CircuitBreaker,
    Bulkhead,
    RetryManager,
    TimeoutManager,
    ResilienceDecorator,
    CircuitBreakerConfig,
    BulkheadConfig,
    RetryConfig,
    TimeoutConfig,
    CircuitState,
    BulkheadState,
    RetryPolicy,
    initialize_resilience_manager
)

# Imports des nouveaux modules avancés
from .event_schemas import (
    EventSchemaRegistry,
    SchemaValidator,
    JsonSchemaValidator,
    AvroSchemaValidator,
    SchemaMetadata,
    SchemaValidationResult,
    SchemaMigration,
    SchemaFormat,
    SchemaVersion,
    CompatibilityMode,
    SchemaStorage,
    InMemorySchemaStorage,
    PLATFORM_EVENT_SCHEMAS,
    create_default_schema_registry,
    register_platform_schemas
)

from .event_storage import (
    EventStorageInterface,
    PostgreSQLEventStorage,
    RedisEventStorage,
    HybridEventStorage,
    EventArchiver,
    StorageConfiguration,
    StorageBackend,
    CompressionType,
    StoragePolicy,
    StorageMetrics,
    EventQuery,
    ArchivalRequest,
    create_default_storage,
    create_hybrid_storage
)

from .index import (
    EventSystemManager,
    EventSystemConfig,
    DEFAULT_EVENT_SYSTEM_CONFIG,
    create_event_system,
    get_default_event_system
)

# Export des classes principales
__all__ = [
    # Core Event System
    "EventBus",
    "Event",
    "EventDispatcher", 
    "EventHandler",
    "EventStore",
    "EventStream",
    "EventPublisher",
    "NotificationService",
    "EventAggregator",
    "EventProcessor",
    "EventScheduler",
    "DelayedEventHandler",
    
    # Event Types
    "EventType",
    "ContentEvent",
    "ProtectionEvent", 
    "MonetizationEvent",
    "CollaborationEvent",
    "SystemEvent",
    
    # Middleware
    "EventMiddleware",
    "AuthenticationMiddleware",
    "ValidationMiddleware", 
    "LoggingMiddleware",
    "MetricsMiddleware",
    
    # Webhooks & Notifications
    "WebhookManager",
    "WebhookProcessor",
    "NotificationChannel",
    "EmailChannel",
    "WebSocketChannel",
    "PushNotificationChannel",
    "SlackChannel",
    
    # Metrics & Analytics
    "EventMetricsManager",
    "MetricCollector",
    "EventMetricsCollector",
    "SystemMetricsCollector",
    "BusinessMetricsCollector",
    "AlertManager",
    "MetricType",
    "AlertSeverity",
    "event_metrics_manager",
    
    # Workflows
    "WorkflowEngine",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowStep",
    "WorkflowStatus",
    "StepType",
    "initialize_workflow_engine",
    "create_content_processing_workflow",
    "create_violation_response_workflow",
    
    # Replication
    "EventReplicationManager",
    "ReplicationTarget",
    "ReplicationStrategy",
    "ReplicationStatus",
    "ReplicationConnector",
    "DatabaseReplicationConnector",
    "APIReplicationConnector",
    "WebSocketReplicationConnector",
    "RedisReplicationConnector",
    "initialize_replication_manager",
    
    # Resilience
    "EventResilienceManager",
    "CircuitBreaker",
    "Bulkhead",
    "RetryManager",
    "TimeoutManager",
    "ResilienceDecorator",
    "CircuitBreakerConfig",
    "BulkheadConfig",
    "RetryConfig",
    "TimeoutConfig",
    "CircuitState",
    "BulkheadState",
    "RetryPolicy",
    "initialize_resilience_manager",
]

# Configuration par défaut
DEFAULT_EVENT_CONFIG = {
    "max_retries": 3,
    "retry_delay": 5,
    "timeout": 30,
    "batch_size": 100,
    "enable_persistence": True,
    "enable_metrics": True,
    "enable_webhooks": True,
}

logger.info("Events Management System initialized - IA-Influencer-Agent v%s", __version__)
