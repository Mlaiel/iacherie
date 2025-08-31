"""Schedulers Module Initialization
===============================

Unified initialization and export module for all crawler scheduling systems.
Provides comprehensive scheduler orchestration and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture système et coordination intelligente
- Backend Senior: Infrastructure et orchestration des services
- ML Engineer: Algorithmes d'optimisation et apprentissage automatique
- DBA Expert: Gestion des données et performance
- Sécurité: Contrôle d'accès et protection des systèmes
- Microservices: Architecture distribuée et communication
- Audio/Vidéo: Traitement de contenu multimédia
- DevOps: Déploiement et monitoring avancé
- IA Prompt Engineer: Optimisation des interactions

Business Logic Integration:
Creator content upload → Scheduler coordination → AI processing → 
Protection layer → Multi-platform distribution → Performance optimization → 
Revenue maximization → User satisfaction → Business growth → Market leadership
"""from .main_scheduler import (
    MainScheduler,
    SchedulerType,
    SchedulingStrategy,
    TaskState,
    SchedulerConfiguration,
    TaskRequest,
    SchedulingDecision,
    SchedulerMetrics,
    SystemMetrics,
    BaseSchedulerInterface
)

from .priority_scheduler import (
    PriorityScheduler,
    ScheduledTask,
    TaskPriority,
    PriorityStrategy,
    BusinessContext,
    PriorityMetrics
)

from .intelligent_scheduler import (
    IntelligentScheduler,
    IntelligentTask,
    LearningMode,
    PredictionModel,
    PerformanceHistory,
    ModelMetrics
)

from .time_scheduler import (
    TimeBasedScheduler,
    TimedTask,
    CronSchedule,
    TimeZoneStrategy,
    PlatformTiming,
    CollaborationWindow,
    TimeMetrics
)

from .resource_scheduler import (
    ResourceScheduler,
    ResourceTask,
    ResourcePool,
    ResourceMetrics,
    AllocationStrategy,
    ScalingPolicy,
    ResourceConstraint
)

from .adaptive_scheduler import (
    AdaptiveScheduler,
    AdaptationStrategy,
    LearningMode as AdaptiveLearningMode,
    OptimizationObjective,
    PerformancePattern,
    AdaptationDecision,
    LearningState,
    ReinforcementState
)

from .batch_scheduler import (
    BatchScheduler,
    BatchProcessor,
    ContentFingerprintingProcessor,
    ProtectionMonitoringProcessor,
    BatchJob,
    BatchConfiguration,
    BatchMetrics,
    ProcessingMode,
    BatchPriority,
    JobStatus,
    ResourceAllocation
)

from .event_driven_scheduler import (
    EventDrivenScheduler,
    EventHandler,
    ContentProtectionEventHandler,
    BusinessEventHandler,
    Event,
    EventRule,
    EventTrigger,
    EventType,
    EventPriority,
    EventAction,
    EventConfiguration,
    EventMetrics
)

from .campaign_scheduler import (
    CampaignScheduler,
    Campaign,
    CampaignContent,
    CampaignSchedule,
    CampaignConfiguration,
    CampaignExecution,
    CampaignMetrics,
    PlatformConfiguration,
    CampaignOrchestrator,
    ContentProtectionOrchestrator,
    RevenueOptimizationOrchestrator,
    CampaignType,
    CampaignStatus,
    CampaignPriority,
    PlatformType,
    ContentPhase,
    TimingStrategy
)

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class SchedulerFactory:
    """    Factory class for creating and managing scheduler instances.
    
    Provides centralized scheduler creation, configuration, and lifecycle management.
    """    
    _instances: Dict[str, Any] = {}
    _configurations: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_main_scheduler(
        cls,
        name: str = "default",
        configuration: Optional[SchedulerConfiguration] = None
    ) -> MainScheduler:
        """Create or get main scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = MainScheduler(configuration)
        cls._instances[name] = scheduler
        cls._configurations[name] = configuration.__dict__ if configuration else {}
        
        logger.info(f"Created main scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_priority_scheduler(
        cls,
        name: str = "priority_default",
        **kwargs
    ) -> PriorityScheduler:
        """Create priority scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = PriorityScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created priority scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_intelligent_scheduler(
        cls,
        name: str = "intelligent_default",
        **kwargs
    ) -> IntelligentScheduler:
        """Create intelligent scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = IntelligentScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created intelligent scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_time_scheduler(
        cls,
        name: str = "time_default",
        **kwargs
    ) -> TimeBasedScheduler:
        """Create time-based scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = TimeBasedScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created time-based scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_resource_scheduler(
        cls,
        name: str = "resource_default",
        **kwargs
    ) -> ResourceScheduler:
        """Create resource scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = ResourceScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created resource scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_adaptive_scheduler(
        cls,
        name: str = "adaptive_default",
        **kwargs
    ) -> AdaptiveScheduler:
        """Create adaptive scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = AdaptiveScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created adaptive scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_batch_scheduler(
        cls,
        name: str = "batch_default",
        **kwargs
    ) -> BatchScheduler:
        """Create batch scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = BatchScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created batch scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_event_driven_scheduler(
        cls,
        name: str = "event_default",
        **kwargs
    ) -> EventDrivenScheduler:
        """Create event-driven scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = EventDrivenScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created event-driven scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def create_campaign_scheduler(
        cls,
        name: str = "campaign_default",
        **kwargs
    ) -> CampaignScheduler:
        """Create campaign scheduler instance."""        if name in cls._instances:
            return cls._instances[name]
        
        scheduler = CampaignScheduler(**kwargs)
        cls._instances[name] = scheduler
        cls._configurations[name] = kwargs
        
        logger.info(f"Created campaign scheduler instance: {name}")
        return scheduler
    
    @classmethod
    def get_instance(cls, name: str) -> Optional[Any]:
        """Get scheduler instance by name."""        return cls._instances.get(name)
    
    @classmethod
    def list_instances(cls) -> List[str]:
        """List all scheduler instance names."""        return list(cls._instances.keys())
    
    @classmethod
    async def initialize_all(cls) -> None:
        """Initialize all created scheduler instances."""        for name, scheduler in cls._instances.items():
            try:
                if hasattr(scheduler, 'initialize'):
                    await scheduler.initialize()
                logger.info(f"Initialized scheduler: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize scheduler {name}: {e}")
    
    @classmethod
    async def stop_all(cls) -> None:
        """Stop all scheduler instances."""        for name, scheduler in cls._instances.items():
            try:
                if hasattr(scheduler, 'stop'):
                    await scheduler.stop()
                logger.info(f"Stopped scheduler: {name}")
            except Exception as e:
                logger.error(f"Failed to stop scheduler {name}: {e}")
        
        cls._instances.clear()
        cls._configurations.clear()
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get status of all scheduler instances."""        status = {
            'total_instances': len(cls._instances),
            'instances': {},
            'configurations': cls._configurations.copy()
        }
        
        for name, scheduler in cls._instances.items():
            instance_status = {
                'type': type(scheduler).__name__,
                'created_at': getattr(scheduler, '_created_at', None),
                'is_running': getattr(scheduler, 'is_running', False)
            }
            
            # Try to get additional status information
            try:
                if hasattr(scheduler, 'get_status'):
                    instance_status.update(scheduler.get_status())
            except Exception as e:
                instance_status['status_error'] = str(e)
            
            status['instances'][name] = instance_status
        
        return status


class SchedulerManager:
    """    High-level scheduler management interface.
    
    Provides simplified API for common scheduler operations and orchestration.
    """    
    def __init__(self):
        """Initialize scheduler manager."""        self.main_scheduler: Optional[MainScheduler] = None
        self.is_initialized = False
        
    async def initialize(
        self,
        configuration: Optional[SchedulerConfiguration] = None
    ) -> None:
        """Initialize scheduler system."""        try:
            # Create main scheduler
            self.main_scheduler = SchedulerFactory.create_main_scheduler(
                configuration=configuration
            )
            
            # Initialize the main scheduler
            await self.main_scheduler.initialize()
            
            self.is_initialized = True
            logger.info("Scheduler manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Scheduler manager initialization failed: {e}")
            raise
    
    async def schedule_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        priority: float = 0.5,
        deadline: Optional[datetime] = None,
        business_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> SchedulingDecision:
        """        Schedule a task with simplified interface.
        
        Args:
            task_type: Type of task to schedule
            data: Task data
            priority: Task priority (0.0 to 1.0)
            deadline: Optional deadline
            business_context: Business context information
            **kwargs: Additional task parameters
            
        Returns:
            Scheduling decision with execution details
        """        if not self.is_initialized or not self.main_scheduler:
            raise RuntimeError("Scheduler manager not initialized")
        
        # Create task request
        task_request = TaskRequest(
            task_id=f"task_{int(datetime.utcnow().timestamp() * 1000)}",
            task_type=task_type,
            priority=priority,
            data=data,
            deadline=deadline,
            business_context=business_context or {},
            **kwargs
        )
        
        # Schedule through main scheduler
        return await self.main_scheduler.schedule_task(task_request)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""        if not self.is_initialized or not self.main_scheduler:
            return {
                'initialized': False,
                'error': 'Scheduler manager not initialized'
            }
        
        # Get main scheduler status
        main_status = await self.main_scheduler.get_system_status()
        
        # Get factory status
        factory_status = SchedulerFactory.get_status()
        
        return {
            'initialized': self.is_initialized,
            'main_scheduler': main_status,
            'factory': factory_status,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def stop(self) -> None:
        """Stop scheduler system."""        if self.main_scheduler:
            await self.main_scheduler.stop()
        
        await SchedulerFactory.stop_all()
        
        self.is_initialized = False
        self.main_scheduler = None
        
        logger.info("Scheduler manager stopped")


# Global scheduler manager instance
_scheduler_manager: Optional[SchedulerManager] = None


async def get_scheduler_manager() -> SchedulerManager:
    """Get global scheduler manager instance."""    global _scheduler_manager
    
    if _scheduler_manager is None:
        _scheduler_manager = SchedulerManager()
    
    return _scheduler_manager


async def initialize_schedulers(
    configuration: Optional[SchedulerConfiguration] = None
) -> SchedulerManager:
    """    Initialize the global scheduler system.
    
    Args:
        configuration: Optional scheduler configuration
        
    Returns:
        Initialized scheduler manager
    """    manager = await get_scheduler_manager()
    
    if not manager.is_initialized:
        await manager.initialize(configuration)
    
    return manager


async def schedule_task(
    task_type: str,
    data: Dict[str, Any],
    priority: float = 0.5,
    deadline: Optional[datetime] = None,
    business_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> SchedulingDecision:
    """    Convenient function to schedule a task.
    
    Args:
        task_type: Type of task to schedule
        data: Task data
        priority: Task priority (0.0 to 1.0)
        deadline: Optional deadline
        business_context: Business context information
        **kwargs: Additional task parameters
        
    Returns:
        Scheduling decision
    """    manager = await get_scheduler_manager()
    return await manager.schedule_task(
        task_type=task_type,
        data=data,
        priority=priority,
        deadline=deadline,
        business_context=business_context,
        **kwargs
    )


async def get_system_status() -> Dict[str, Any]:
    """Get comprehensive scheduler system status."""    manager = await get_scheduler_manager()
    return await manager.get_system_status()


async def stop_schedulers() -> None:
    """Stop the global scheduler system."""    manager = await get_scheduler_manager()
    await manager.stop()


# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All rights reserved"

# Export all public classes and functions
__all__ = [
    # Main scheduler classes
    'MainScheduler',
    'SchedulerType',
    'SchedulingStrategy',
    'TaskState',
    'SchedulerConfiguration',
    'TaskRequest',
    'SchedulingDecision',
    'SchedulerMetrics',
    'SystemMetrics',
    'BaseSchedulerInterface',
    
    # Priority scheduler
    'PriorityScheduler',
    'ScheduledTask',
    'TaskPriority',
    'PriorityStrategy',
    'BusinessContext',
    'PriorityMetrics',
    
    # Intelligent scheduler
    'IntelligentScheduler',
    'IntelligentTask',
    'LearningMode',
    'PredictionModel',
    'PerformanceHistory',
    'ModelMetrics',
    
    # Time-based scheduler
    'TimeBasedScheduler',
    'TimedTask',
    'CronSchedule',
    'TimeZoneStrategy',
    'PlatformTiming',
    'CollaborationWindow',
    'TimeMetrics',
    
    # Resource scheduler
    'ResourceScheduler',
    'ResourceTask',
    'ResourcePool',
    'ResourceMetrics',
    'AllocationStrategy',
    'ScalingPolicy',
    'ResourceConstraint',
    
    # Adaptive scheduler
    'AdaptiveScheduler',
    'AdaptationStrategy',
    'AdaptiveLearningMode',
    'OptimizationObjective',
    'PerformancePattern',
    'AdaptationDecision',
    'LearningState',
    'ReinforcementState',
    
    # Batch scheduler
    'BatchScheduler',
    'BatchProcessor',
    'ContentFingerprintingProcessor',
    'ProtectionMonitoringProcessor',
    'BatchJob',
    'BatchConfiguration',
    'BatchMetrics',
    'ProcessingMode',
    'BatchPriority',
    'JobStatus',
    'ResourceAllocation',
    
    # Event-driven scheduler
    'EventDrivenScheduler',
    'EventHandler',
    'ContentProtectionEventHandler',
    'BusinessEventHandler',
    'Event',
    'EventRule',
    'EventTrigger',
    'EventType',
    'EventPriority',
    'EventAction',
    'EventConfiguration',
    'EventMetrics',
    
    # Campaign scheduler
    'CampaignScheduler',
    'Campaign',
    'CampaignContent',
    'CampaignSchedule',
    'CampaignConfiguration',
    'CampaignExecution',
    'CampaignMetrics',
    'PlatformConfiguration',
    'CampaignOrchestrator',
    'ContentProtectionOrchestrator',
    'RevenueOptimizationOrchestrator',
    'CampaignType',
    'CampaignStatus',
    'CampaignPriority',
    'PlatformType',
    'ContentPhase',
    'TimingStrategy',
    
    # Factory and management
    'SchedulerFactory',
    'SchedulerManager',
    
    # Convenience functions
    'get_scheduler_manager',
    'initialize_schedulers',
    'schedule_task',
    'get_system_status',
    'stop_schedulers',
    
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]


# Module-level configuration
DEFAULT_CONFIGURATION = SchedulerConfiguration(
    enabled_schedulers={
        SchedulerType.PRIORITY,
        SchedulerType.INTELLIGENT,
        SchedulerType.TIME_BASED,
        SchedulerType.RESOURCE_AWARE,
        SchedulerType.ADAPTIVE
    },
    primary_strategy=SchedulingStrategy.BALANCED,
    fallback_strategy=SchedulingStrategy.PERFORMANCE_OPTIMIZED,
    coordination_interval=60,
    health_check_interval=30,
    task_timeout=3600,
    max_concurrent_tasks=100,
    enable_cross_scheduler_optimization=True,
    enable_predictive_scaling=True,
    enable_business_intelligence=True,
    performance_monitoring_enabled=True,
    auto_recovery_enabled=True
)


# Logging configuration
def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the scheduler module."""    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scheduler.log')
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


# Initialize logging
configure_logging()

logger.info("Scheduler module initialized successfully")
logger.info(f"Available scheduler types: {[st.value for st in SchedulerType]}")
logger.info(f"Available scheduling strategies: {[ss.value for ss in SchedulingStrategy]}")
logger.info("Business logic integration: Creator content → AI processing → Protection → Multi-platform distribution → Revenue optimization")
