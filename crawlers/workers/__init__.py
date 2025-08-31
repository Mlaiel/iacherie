"""Workers Management System - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Workers Module Initialization
Responsibility: Module exports, component registry, and system initialization
Technologies: Python Module System, Component Registration, Factory Patterns
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ARCHITECTURE WORKERS:
Crawler Worker → Worker Pool → Queue Processor → Resource Manager → 
Task Orchestrator → Event Processor → Notification Engine → Background Processor
"""
from typing import Dict, Any, List, Optional, Type
import logging
from enum import Enum

# Core Worker Components
from .crawler_worker import (
    CrawlerWorker,
    CrawlerTask,
    TaskResult,
    TaskStatus,
    TaskPriority,
    WorkerStatus,
    WorkerCapabilities,
    ContentType,
    ExtractionRule,
    ValidationRule,
    get_crawler_worker,
    initialize_crawler_worker,
    shutdown_crawler_worker
)

from .worker_pool import (
    WorkerPool,
    PoolStatus,
    PoolConfiguration,
    PerformanceMetrics,
    get_worker_pool,
    initialize_worker_pool,
    shutdown_worker_pool
)

from .background_processor import (
    BackgroundProcessor,
    ProcessorConfig,
    BackgroundJob,
    JobStatus,
    JobPriority,
    get_background_processor,
    initialize_background_processor,
    shutdown_background_processor
)

from .queue_processor import (
    QueueProcessor,
    QueueConfiguration,
    QueueMessage,
    MessagePriority,
    QueueStatus,
    CircuitBreakerState,
    ProcessingStrategy,
    CompressionType,
    EncryptionType,
    get_queue_processor,
    initialize_queue_processor,
    shutdown_queue_processor
)

from .resource_manager import (
    ResourceManager,
    ResourceType,
    AllocationStrategy,
    ResourceAllocation,
    ResourceLimits,
    PerformanceThresholds,
    ScalingPolicy,
    AutoScalingConfig,
    get_resource_manager,
    initialize_resource_manager,
    shutdown_resource_manager
)

from .event_processor import (
    EventProcessor,
    WorkerEvent,
    EventType,
    EventPriority,
    EventMetadata,
    EventFilter,
    EventHandler,
    EventSubscription,
    get_event_processor,
    initialize_event_processor,
    shutdown_event_processor
)

from .notification_engine import (
    NotificationEngine,
    NotificationChannel,
    NotificationPriority,
    NotificationTemplate,
    NotificationStatus,
    NotificationHistory,
    DeliveryChannel,
    EmailChannel,
    WebhookChannel,
    WebSocketChannel,
    get_notification_engine,
    initialize_notification_engine,
    shutdown_notification_engine
)

from .task_orchestrator import (
    TaskOrchestrator,
    WorkflowDefinition,
    TaskDefinition,
    WorkflowExecution,
    TaskExecution,
    WorkflowStatus,
    TaskType,
    DependencyType,
    ExecutionStrategy,
    get_task_orchestrator,
    initialize_task_orchestrator,
    shutdown_task_orchestrator
)

# Advanced Specialized Workers
from .content_protection_worker import (
    ContentProtectionWorker,
    ContentType as ProtectionContentType,
    ProtectionLevel,
    FingerprintType,
    DetectionStatus,
    ContentFingerprint,
    PiracyDetection,
    ProtectionTask,
    get_content_protection_worker,
    initialize_content_protection_worker,
    shutdown_content_protection_worker
)

from .revenue_analytics_worker import (
    RevenueAnalyticsWorker,
    Platform,
    RevenueType,
    RevenueStatus,
    AnalyticsType,
    RevenueEntry,
    PlatformMetrics,
    RevenueAnalyticsTask,
    RevenueReport,
    get_revenue_analytics_worker,
    initialize_revenue_analytics_worker,
    shutdown_revenue_analytics_worker
)

from .ml_task_router import (
    MLTaskRouter,
    TaskCategory,
    RoutingStrategy,
    WorkerCapability,
    TaskFeatures,
    WorkerProfile,
    RoutingDecision,
    TaskClassifierNN,
    PerformancePredictorNN,
    get_ml_task_router,
    initialize_ml_task_router,
    shutdown_ml_task_router
)

from .web_surveillance_worker import (
    WebSurveillanceWorker,
    SurveillanceScope,
    MonitoringFrequency,
    AlertSeverity,
    SurveillanceTarget,
    SurveillanceResult,
    SurveillanceTask,
    get_web_surveillance_worker,
    initialize_web_surveillance_worker,
    shutdown_web_surveillance_worker
)

from .monetization_task_router import (
    MonetizationTaskRouter,
    MonetizationTaskType,
    PlatformPriority,
    RevenueUrgency,
    MonetizationTask,
    MonetizationWorkerProfile,
    RoutingDecision as MonetizationRoutingDecision,
    get_monetization_task_router,
    initialize_monetization_task_router,
    shutdown_monetization_task_router
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. Tous droits réservés."

logger = logging.getLogger(__name__)


class WorkerComponentType(Enum):
    """Worker component types"""    CRAWLER_WORKER = "crawler_worker"
    WORKER_POOL = "worker_pool"
    QUEUE_PROCESSOR = "queue_processor"
    RESOURCE_MANAGER = "resource_manager"
    EVENT_PROCESSOR = "event_processor"
    NOTIFICATION_ENGINE = "notification_engine"
    TASK_ORCHESTRATOR = "task_orchestrator"
    BACKGROUND_PROCESSOR = "background_processor"


class WorkerSystemStatus(Enum):
    """Worker system status"""    INITIALIZING = "initializing"
    RUNNING = "running"
    SCALING = "scaling"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"
    ERROR = "error"


# Unified initialization functions
async def initialize_workers(system_config: Dict[str, Any] = None) -> bool:
    """Initialize the complete worker system"""    try:
        logger.info("🚀 Initializing IA-Influencer-Agent Worker System...")
        
        config = system_config or {}
        
        # Initialize core components
        success = True
        
        # Initialize crawler workers
        if config.get('enable_crawler_workers', True):
            success &= await initialize_crawler_worker()
        
        # Initialize worker pool
        if config.get('enable_worker_pool', True):
            success &= await initialize_worker_pool()
        
        # Initialize queue processor
        if config.get('enable_queue_processor', True):
            success &= await initialize_queue_processor()
        
        # Initialize resource manager
        if config.get('enable_resource_manager', True):
            success &= await initialize_resource_manager()
        
        # Initialize event processor
        if config.get('enable_event_processor', True):
            success &= await initialize_event_processor()
        
        # Initialize notification engine
        if config.get('enable_notification_engine', True):
            success &= await initialize_notification_engine()
        
        # Initialize task orchestrator
        if config.get('enable_task_orchestrator', True):
            success &= await initialize_task_orchestrator()
        
        # Initialize background processor
        if config.get('enable_background_processor', True):
            success &= await initialize_background_processor()
        
        # Initialize content protection worker
        if config.get('enable_content_protection_worker', True):
            success &= await initialize_content_protection_worker()
        
        # Initialize revenue analytics worker
        if config.get('enable_revenue_analytics_worker', True):
            success &= await initialize_revenue_analytics_worker()
        
        # Initialize ML task router
        if config.get('enable_ml_task_router', True):
            success &= await initialize_ml_task_router()
        
        # Initialize web surveillance worker
        if config.get('enable_web_surveillance_worker', True):
            success &= await initialize_web_surveillance_worker()
        
        # Initialize monetization task router
        if config.get('enable_monetization_task_router', True):
            success &= await initialize_monetization_task_router()
        
        if success:
            logger.info("✅ IA-Influencer-Agent Worker System initialized successfully")
        else:
            logger.error("❌ Some worker components failed to initialize")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize worker system: {e}")
        return False


async def shutdown_workers() -> bool:
    """Gracefully shutdown the worker system"""    try:
        logger.info("🛑 Shutting down IA-Influencer-Agent Worker System...")
        
        # Shutdown components in reverse order
        await shutdown_monetization_task_router()
        await shutdown_web_surveillance_worker()
        await shutdown_ml_task_router()
        await shutdown_revenue_analytics_worker()
        await shutdown_content_protection_worker()
        await shutdown_background_processor()
        await shutdown_task_orchestrator()
        await shutdown_notification_engine()
        await shutdown_event_processor()
        await shutdown_resource_manager()
        await shutdown_queue_processor()
        await shutdown_worker_pool()
        await shutdown_crawler_worker()
        
        logger.info("✅ IA-Influencer-Agent Worker System shutdown complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to shutdown worker system: {e}")
        return False


async def get_workers_status() -> Dict[str, Any]:
    """Get comprehensive status of all worker components"""    try:
        status = {
            "system_version": __version__,
            "components": {},
            "overall_health": True,
            "active_components": 0,
            "total_components": 13
        }
        
        # Check each component
        components = [
            ("crawler_worker", get_crawler_worker),
            ("worker_pool", get_worker_pool),
            ("queue_processor", get_queue_processor),
            ("resource_manager", get_resource_manager),
            ("event_processor", get_event_processor),
            ("notification_engine", get_notification_engine),
            ("task_orchestrator", get_task_orchestrator),
            ("background_processor", get_background_processor),
            ("content_protection_worker", get_content_protection_worker),
            ("revenue_analytics_worker", get_revenue_analytics_worker),
            ("ml_task_router", get_ml_task_router),
            ("web_surveillance_worker", get_web_surveillance_worker),
            ("monetization_task_router", get_monetization_task_router)
        ]
        
        for comp_name, get_func in components:
            try:
                component = get_func()
                if component:
                    status["components"][comp_name] = {
                        "status": "active",
                        "healthy": True
                    }
                    status["active_components"] += 1
                else:
                    status["components"][comp_name] = {
                        "status": "inactive",
                        "healthy": False
                    }
                    status["overall_health"] = False
                    
            except Exception as e:
                status["components"][comp_name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
                status["overall_health"] = False
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get workers status: {e}")
        return {"error": str(e)}


# Module exports
__all__ = [
    # Core Components
    "CrawlerWorker",
    "WorkerPool", 
    "BackgroundProcessor",
    "QueueProcessor",
    "ResourceManager",
    "EventProcessor",
    "NotificationEngine",
    "TaskOrchestrator",
    
    # Advanced Specialized Workers
    "ContentProtectionWorker",
    "RevenueAnalyticsWorker",
    "MLTaskRouter",
    "WebSurveillanceWorker",
    "MonetizationTaskRouter",
    
    # Data models - Worker
    "CrawlerTask",
    "TaskResult",
    "TaskStatus",
    "TaskPriority",
    "WorkerStatus",
    "WorkerCapabilities",
    "ContentType",
    "ExtractionRule",
    "ValidationRule",
    
    # Data models - Pool
    "PoolStatus",
    "PoolConfiguration",
    "PerformanceMetrics",
    
    # Data models - Background Processor
    "ProcessorConfig",
    "BackgroundJob",
    "JobStatus",
    "JobPriority",
    
    # Data models - Queue Processor
    "QueueConfiguration",
    "QueueMessage",
    "MessagePriority",
    "QueueStatus",
    "CircuitBreakerState",
    "ProcessingStrategy",
    "CompressionType",
    "EncryptionType",
    
    # Data models - Resource Manager
    "ResourceType",
    "AllocationStrategy",
    "ResourceAllocation",
    "ResourceLimits",
    "PerformanceThresholds",
    "ScalingPolicy",
    "AutoScalingConfig",
    
    # Data models - Event Processor
    "WorkerEvent",
    "EventType",
    "EventPriority",
    "EventMetadata",
    "EventFilter",
    "EventHandler",
    "EventSubscription",
    
    # Data models - Notification Engine
    "NotificationChannel",
    "NotificationPriority",
    "NotificationTemplate",
    "NotificationStatus",
    "NotificationHistory",
    "DeliveryChannel",
    "EmailChannel",
    "WebhookChannel",
    "WebSocketChannel",
    
    # Data models - Task Orchestrator
    "WorkflowDefinition",
    "TaskDefinition",
    "WorkflowExecution",
    "TaskExecution",
    "WorkflowStatus",
    "TaskType",
    "DependencyType",
    "ExecutionStrategy",
    
    # Data models - Content Protection Worker
    "ProtectionContentType",
    "ProtectionLevel",
    "FingerprintType",
    "DetectionStatus",
    "ContentFingerprint",
    "PiracyDetection",
    "ProtectionTask",
    
    # Data models - Revenue Analytics Worker
    "Platform",
    "RevenueType",
    "RevenueStatus",
    "AnalyticsType",
    "RevenueEntry",
    "PlatformMetrics",
    "RevenueAnalyticsTask",
    "RevenueReport",
    
    # Data models - ML Task Router
    "TaskCategory",
    "RoutingStrategy",
    "WorkerCapability",
    "TaskFeatures",
    "WorkerProfile",
    "RoutingDecision",
    "TaskClassifierNN",
    "PerformancePredictorNN",
    
    # Data models - Web Surveillance Worker
    "SurveillanceScope",
    "MonitoringFrequency", 
    "AlertSeverity",
    "SurveillanceTarget",
    "SurveillanceResult",
    "SurveillanceTask",
    
    # Data models - Monetization Task Router
    "MonetizationTaskType",
    "PlatformPriority",
    "RevenueUrgency",
    "MonetizationTask",
    "MonetizationWorkerProfile",
    "MonetizationRoutingDecision",
    
    # Enums
    "WorkerComponentType",
    "WorkerSystemStatus",
    
    # Factory functions
    "get_crawler_worker",
    "get_worker_pool",
    "get_background_processor",
    "get_queue_processor",
    "get_resource_manager",
    "get_event_processor",
    "get_notification_engine",
    "get_task_orchestrator",
    "get_content_protection_worker",
    "get_revenue_analytics_worker",
    "get_ml_task_router",
    "get_web_surveillance_worker",
    "get_monetization_task_router",
    
    # Lifecycle management
    "initialize_workers",
    "shutdown_workers",
    "get_workers_status",
    
    # Individual component lifecycle
    "initialize_crawler_worker",
    "initialize_worker_pool",
    "initialize_background_processor",
    "initialize_queue_processor",
    "initialize_resource_manager",
    "initialize_event_processor",
    "initialize_notification_engine",
    "initialize_task_orchestrator",
    "initialize_content_protection_worker",
    "initialize_revenue_analytics_worker",
    "initialize_ml_task_router",
    "initialize_web_surveillance_worker",
    "initialize_monetization_task_router",
    "shutdown_crawler_worker",
    "shutdown_worker_pool",
    "shutdown_background_processor",
    "shutdown_queue_processor",
    "shutdown_resource_manager",
    "shutdown_event_processor",
    "shutdown_notification_engine",
    "shutdown_task_orchestrator",
    "shutdown_content_protection_worker",
    "shutdown_revenue_analytics_worker",
    "shutdown_ml_task_router",
    "shutdown_web_surveillance_worker",
    "shutdown_monetization_task_router",
    
    # Module Metadata
    "__version__",
    "__author__",
    "__email__",
    "__copyright__"
]


# Module initialization message
logger.info(f"📦 IA-Influencer-Agent Workers Module v{__version__} loaded")
logger.info(f"👤 Author: {__author__} ({__email__})")
logger.info(f"⚖️ {__copyright__}")
logger.info(f"🔧 Available Components: {len(__all__)} exports")
