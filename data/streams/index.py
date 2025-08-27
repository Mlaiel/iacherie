"""
Data Streams Module Index for IA Influencer Agent Platform
=========================================================

Professional enterprise-grade data streaming infrastructure index providing
centralized access to all stream management components, utilities, and services.

This module serves as the main entry point for all data streaming operations
including real-time content processing, AI-powered protection monitoring,
revenue tracking, and cross-platform data synchronization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, Type
import logging

# Core Stream Components
from .manager import (
    DataStreamManager,
    StreamType,
    StreamStatus, 
    StreamEvent,
    StreamMetrics
)

from .processor import (
    RealTimeProcessor,
    ProcessingJob,
    ProcessingPriority,
    ProcessingStage,
    ProcessingMetrics,
    ProcessingResult,
    ContentFormat
)

from .events import (
    EventStreamer,
    EventType,
    EventPriority,
    EventConfig,
    EventHandler,
    EventMetrics,
    EventFilterChain
)

from .revenue import (
    RevenueStreamer,
    RevenueSource,
    RevenueType,
    CurrencyCode,
    PaymentStatus,
    RevenueMetrics,
    PaymentProcessor
)

from .platform import (
    PlatformStreamer,
    PlatformType,
    PlatformConfig,
    PlatformConnector,
    PlatformMetrics,
    SyncStatus
)

from .analytics import (
    StreamAnalytics,
    AnalyticsType,
    MetricType,
    AnalyticsEngine,
    TrendAnalyzer,
    PredictiveModel
)

from .monitoring import (
    StreamMonitor,
    HealthStatus,
    AlertType,
    AlertSeverity,
    MonitoringConfig,
    PerformanceTracker
)

from .buffer import (
    StreamBuffer,
    BufferType,
    BufferConfig,
    BufferStats,
    CompressionType,
    EvictionPolicy
)

from .queue import (
    StreamQueue,
    QueuePriority,
    QueueConfig,
    MessageStatus,
    QueueMetrics,
    DeadLetterQueue
)

from .scheduler import (
    StreamScheduler,
    TaskPriority,
    SchedulerConfig,
    TaskStatus,
    ScheduledTask,
    CronExpression
)

from .connector import (
    StreamConnector,
    ConnectorType,
    ConnectorConfig,
    ConnectionStatus,
    ConnectorMetrics,
    DataSource
)

# Package metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"
__license__ = "Proprietary"

# Team specialties
__team_specialties__ = [
    "Lead Developer IA",
    "Senior Backend Engineer", 
    "ML Engineer",
    "Database Administrator",
    "Security Specialist",
    "Microservices Architect",
    "Audio Processing Expert",
    "DevOps Engineer",
    "IA Prompt Engineer"
]

# Module configuration
logger = logging.getLogger(__name__)


class StreamsModuleConfig:
    """
    Centralized configuration for the data streams module
    """
    
    # Performance settings
    DEFAULT_WORKERS = 16
    MAX_QUEUE_SIZE = 10000
    DEFAULT_BUFFER_SIZE_MB = 512
    DEFAULT_TTL_SECONDS = 3600
    
    # Processing settings
    MAX_RETRY_ATTEMPTS = 3
    PROCESSING_TIMEOUT = 300
    BATCH_SIZE = 100
    
    # Monitoring settings
    METRICS_INTERVAL = 30
    HEALTH_CHECK_INTERVAL = 60
    ALERT_THRESHOLD = 0.95
    
    # Security settings
    ENCRYPTION_ENABLED = True
    ACCESS_CONTROL_ENABLED = True
    AUDIT_LOGGING_ENABLED = True


class StreamsRegistry:
    """
    Registry for managing active stream components and their lifecycle
    """
    
    def __init__(self):
        self._managers: Dict[str, DataStreamManager] = {}
        self._processors: Dict[str, RealTimeProcessor] = {}
        self._streamers: Dict[str, Any] = {}
        self._monitors: Dict[str, StreamMonitor] = {}
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the streams registry"""
        if self._initialized:
            return
            
        logger.info("Initializing Streams Registry...")
        
        try:
            # Initialize core components
            await self._initialize_managers()
            await self._initialize_processors()
            await self._initialize_monitors()
            
            self._initialized = True
            logger.info("Streams Registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Streams Registry: {e}")
            raise
            
    async def register_manager(self, name: str, manager: DataStreamManager) -> None:
        """Register a data stream manager"""
        if not isinstance(manager, DataStreamManager):
            raise ValueError("Manager must be instance of DataStreamManager")
            
        self._managers[name] = manager
        await manager.initialize()
        logger.info(f"Registered stream manager: {name}")
        
    async def register_processor(self, name: str, processor: RealTimeProcessor) -> None:
        """Register a real-time processor"""
        if not isinstance(processor, RealTimeProcessor):
            raise ValueError("Processor must be instance of RealTimeProcessor")
            
        self._processors[name] = processor
        await processor.initialize()
        logger.info(f"Registered processor: {name}")
        
    async def register_streamer(self, name: str, streamer: Any) -> None:
        """Register a specialized streamer (events, revenue, platform, etc.)"""
        self._streamers[name] = streamer
        
        if hasattr(streamer, 'initialize'):
            await streamer.initialize()
            
        logger.info(f"Registered streamer: {name}")
        
    async def register_monitor(self, name: str, monitor: StreamMonitor) -> None:
        """Register a stream monitor"""
        if not isinstance(monitor, StreamMonitor):
            raise ValueError("Monitor must be instance of StreamMonitor")
            
        self._monitors[name] = monitor
        await monitor.initialize()
        logger.info(f"Registered monitor: {name}")
        
    def get_manager(self, name: str) -> Optional[DataStreamManager]:
        """Get registered stream manager by name"""
        return self._managers.get(name)
        
    def get_processor(self, name: str) -> Optional[RealTimeProcessor]:
        """Get registered processor by name"""
        return self._processors.get(name)
        
    def get_streamer(self, name: str) -> Optional[Any]:
        """Get registered streamer by name"""
        return self._streamers.get(name)
        
    def get_monitor(self, name: str) -> Optional[StreamMonitor]:
        """Get registered monitor by name"""
        return self._monitors.get(name)
        
    def list_components(self) -> Dict[str, List[str]]:
        """List all registered components"""
        return {
            "managers": list(self._managers.keys()),
            "processors": list(self._processors.keys()),
            "streamers": list(self._streamers.keys()),
            "monitors": list(self._monitors.keys())
        }
        
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all components"""
        health_status = {}
        
        # Check managers
        for name, manager in self._managers.items():
            try:
                if hasattr(manager, 'health_check'):
                    health_status[f"manager_{name}"] = await manager.health_check()
                else:
                    health_status[f"manager_{name}"] = True
            except Exception:
                health_status[f"manager_{name}"] = False
                
        # Check processors
        for name, processor in self._processors.items():
            try:
                if hasattr(processor, 'health_check'):
                    health_status[f"processor_{name}"] = await processor.health_check()
                else:
                    health_status[f"processor_{name}"] = True
            except Exception:
                health_status[f"processor_{name}"] = False
                
        # Check streamers
        for name, streamer in self._streamers.items():
            try:
                if hasattr(streamer, 'health_check'):
                    health_status[f"streamer_{name}"] = await streamer.health_check()
                else:
                    health_status[f"streamer_{name}"] = True
            except Exception:
                health_status[f"streamer_{name}"] = False
                
        # Check monitors
        for name, monitor in self._monitors.items():
            try:
                if hasattr(monitor, 'health_check'):
                    health_status[f"monitor_{name}"] = await monitor.health_check()
                else:
                    health_status[f"monitor_{name}"] = True
            except Exception:
                health_status[f"monitor_{name}"] = False
                
        return health_status
        
    async def shutdown(self) -> None:
        """Gracefully shutdown all components"""
        logger.info("Shutting down Streams Registry...")
        
        # Shutdown monitors first
        for name, monitor in self._monitors.items():
            try:
                if hasattr(monitor, 'shutdown'):
                    await monitor.shutdown()
                logger.info(f"Shutdown monitor: {name}")
            except Exception as e:
                logger.error(f"Error shutting down monitor {name}: {e}")
                
        # Shutdown processors
        for name, processor in self._processors.items():
            try:
                if hasattr(processor, 'shutdown'):
                    await processor.shutdown()
                logger.info(f"Shutdown processor: {name}")
            except Exception as e:
                logger.error(f"Error shutting down processor {name}: {e}")
                
        # Shutdown streamers
        for name, streamer in self._streamers.items():
            try:
                if hasattr(streamer, 'shutdown'):
                    await streamer.shutdown()
                logger.info(f"Shutdown streamer: {name}")
            except Exception as e:
                logger.error(f"Error shutting down streamer {name}: {e}")
                
        # Shutdown managers last
        for name, manager in self._managers.items():
            try:
                if hasattr(manager, 'shutdown'):
                    await manager.shutdown()
                logger.info(f"Shutdown manager: {name}")
            except Exception as e:
                logger.error(f"Error shutting down manager {name}: {e}")
                
        self._initialized = False
        logger.info("Streams Registry shutdown completed")
        
    async def _initialize_managers(self) -> None:
        """Initialize default stream managers"""
        # Default stream manager
        default_manager = DataStreamManager()
        await self.register_manager("default", default_manager)
        
    async def _initialize_processors(self) -> None:
        """Initialize default processors"""
        # Default real-time processor
        default_processor = RealTimeProcessor(
            max_workers=StreamsModuleConfig.DEFAULT_WORKERS
        )
        await self.register_processor("default", default_processor)
        
    async def _initialize_monitors(self) -> None:
        """Initialize default monitors"""
        # Default stream monitor
        default_monitor = StreamMonitor()
        await self.register_monitor("default", default_monitor)


# Global registry instance
streams_registry = StreamsRegistry()


# Convenience functions for easy access
async def get_default_manager() -> DataStreamManager:
    """Get the default stream manager"""
    if not streams_registry._initialized:
        await streams_registry.initialize()
    return streams_registry.get_manager("default")


async def get_default_processor() -> RealTimeProcessor:
    """Get the default processor"""
    if not streams_registry._initialized:
        await streams_registry.initialize()
    return streams_registry.get_processor("default")


async def create_stream_components() -> Dict[str, Any]:
    """Create a full set of stream components for a new application"""
    components = {}
    
    # Create manager
    components["manager"] = DataStreamManager()
    await components["manager"].initialize()
    
    # Create processor
    components["processor"] = RealTimeProcessor()
    await components["processor"].initialize()
    
    # Create event streamer
    components["events"] = EventStreamer()
    await components["events"].initialize()
    
    # Create revenue streamer
    components["revenue"] = RevenueStreamer()
    await components["revenue"].initialize()
    
    # Create platform streamer
    components["platform"] = PlatformStreamer()
    await components["platform"].initialize()
    
    # Create analytics
    components["analytics"] = StreamAnalytics()
    await components["analytics"].initialize()
    
    # Create monitor
    components["monitor"] = StreamMonitor()
    await components["monitor"].initialize()
    
    # Create buffer
    components["buffer"] = StreamBuffer(BufferConfig())
    await components["buffer"].initialize()
    
    # Create queue
    components["queue"] = StreamQueue()
    await components["queue"].initialize()
    
    # Create scheduler
    components["scheduler"] = StreamScheduler()
    await components["scheduler"].initialize()
    
    # Create connector
    components["connector"] = StreamConnector()
    await components["connector"].initialize()
    
    return components


# Export all public components
__all__ = [
    # Core Classes
    "DataStreamManager",
    "RealTimeProcessor", 
    "EventStreamer",
    "RevenueStreamer",
    "PlatformStreamer",
    "StreamAnalytics",
    "StreamMonitor",
    "StreamBuffer",
    "StreamQueue",
    "StreamScheduler",
    "StreamConnector",
    
    # Enums
    "StreamType",
    "StreamStatus",
    "ProcessingPriority",
    "ProcessingStage",
    "ContentFormat",
    "EventType",
    "EventPriority",
    "RevenueSource",
    "RevenueType",
    "CurrencyCode",
    "PlatformType",
    "BufferType",
    "CompressionType",
    "QueuePriority",
    "MessageStatus",
    "TaskPriority",
    "ConnectorType",
    "HealthStatus",
    "AlertType",
    
    # Data Classes
    "StreamEvent",
    "ProcessingJob",
    "ProcessingResult",
    "BufferConfig",
    "QueueConfig",
    "SchedulerConfig",
    "ConnectorConfig",
    
    # Metrics Classes
    "StreamMetrics",
    "ProcessingMetrics", 
    "EventMetrics",
    "RevenueMetrics",
    "PlatformMetrics",
    "BufferStats",
    "QueueMetrics",
    "ConnectorMetrics",
    
    # Registry & Configuration
    "StreamsRegistry",
    "StreamsModuleConfig",
    "streams_registry",
    
    # Convenience Functions
    "get_default_manager",
    "get_default_processor",
    "create_stream_components",
]


# Module initialization
def get_module_info() -> Dict[str, Any]:
    """Get module information and metadata"""
    return {
        "name": "Data Streams Management Module",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "copyright": __copyright__,
        "license": __license__,
        "team_specialties": __team_specialties__,
        "components": len(__all__),
        "description": "Professional enterprise-grade data streaming infrastructure",
        "features": [
            "Real-time content processing",
            "AI-powered protection monitoring", 
            "Revenue tracking and analytics",
            "Cross-platform synchronization",
            "High-performance buffering",
            "Distributed queue management",
            "Intelligent task scheduling",
            "Universal connector framework",
            "Advanced monitoring and alerting",
            "Event-driven architecture"
        ]
    }


# Initialize logging
logger.info(f"Data Streams Module v{__version__} loaded successfully")
logger.info(f"Author: {__author__} ({__email__})")
logger.info(f"Components available: {len(__all__)}")

# Legal notice logging
logger.warning("⚠️  LEGAL WARNING: This code is proprietary and protected by copyright.")
logger.warning("📧 Contact mlaiel@live.de for licensing inquiries.")
