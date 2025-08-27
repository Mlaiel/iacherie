"""
Advanced Queue Management System - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Management Suite - Enterprise Crawler Queue Orchestration
Responsibility: Complete queue management ecosystem for distributed crawler operations
Technologies: Multi-Queue Systems, Priority Management, Worker Orchestration, Analytics
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

SYSTÈME COMPLET DE GESTION DES QUEUES:
- CrawlerQueueManager: Gestion intelligente des queues de crawling
- QueueWorkersManager: Orchestration des workers et load balancing
- DynamicPriorityManager: Priorisation dynamique avec IA
- CrawlerQueueOrchestrator: Orchestrateur central unifié
- QueueAnalyticsEngine: Analytics avancés et insights performance

LOGIQUE MÉTIER:
Request → Queue routing → Priority analysis → Worker assignment → 
Load balancing → Execution → Monitoring → Analytics → Optimization
"""

from .crawler_queue_manager import (
    CrawlerQueueManager,
    CrawlerTask,
    CrawlerQueueConfig,
    CrawlerPriority,
    PlatformType,
    CrawlerQueueType,
    CrawlerMetrics,
    create_crawler_queue_manager
)

from .queue_workers import (
    QueueWorkersManager,
    CrawlerWorker,
    WorkerConfig,
    WorkerStatus,
    WorkerType,
    WorkerMetrics,
    WorkerCapacity,
    create_workers_manager
)

from .priority_manager import (
    DynamicPriorityManager,
    PriorityCalculator,
    PriorityFactors,
    PriorityScore,
    BusinessImpact,
    UrgencyLevel,
    create_priority_manager
)

from .queue_orchestrator import (
    CrawlerQueueOrchestrator,
    OrchestrationConfig,
    OrchestrationMetrics,
    OrchestrationStatus,
    create_queue_orchestrator
)

from .queue_analytics import (
    QueueAnalyticsEngine,
    AnalyticsTimeframe,
    MetricType,
    AnalyticsDataPoint,
    PerformanceInsight,
    AnalyticsReport,
    create_analytics_engine
)

from .task_distribution_engine import (
    TaskDistributionEngine,
    MLDistributionPredictor,
    DistributionStrategy,
    TaskComplexity,
    ResourceType,
    AgentCapability,
    TaskResource,
    DistributionResult,
    LoadBalancingMetrics,
    create_task_distribution_engine
)

from .realtime_queue_monitor import (
    RealtimeQueueMonitor,
    AnomalyDetector,
    PredictiveAnalyzer,
    MonitoringConfig,
    MonitoringLevel,
    AlertSeverity,
    MetricType as MonitoringMetricType,
    AlertCondition,
    MetricDataPoint,
    AlertRule,
    MonitoringAlert,
    PerformanceSnapshot,
    create_realtime_queue_monitor
)

from .queue_health_diagnostics import (
    QueueHealthDiagnostics,
    ComponentHealthAnalyzer,
    RootCauseAnalyzer,
    AutomatedRecoveryEngine,
    DiagnosticConfig,
    HealthStatus,
    DiagnosticCategory,
    RecoveryStrategy,
    DiagnosticSeverity,
    HealthMetric,
    DiagnosticIssue,
    RecoveryAction,
    RecoveryPlan,
    HealthReport,
    create_queue_health_diagnostics
)

from .queue_performance_optimizer import (
    QueuePerformanceOptimizer,
    MLPerformancePredictor,
    OptimizationStrategy,
    OptimizationScope,
    OptimizationTechnique,
    PerformanceMetric,
    OptimizationOpportunity,
    OptimizationPlan,
    OptimizationResult,
    create_queue_performance_optimizer
)

from .queue_coordination_engine import (
    QueueCoordinationEngine,
    CrossQueueLoadBalancer,
    QueueNode,
    CoordinationTask,
    ResourceAllocation,
    CoordinationPlan,
    CoordinationMode,
    SynchronizationType,
    ResourceSharingMode,
    PriorityResolutionStrategy,
    create_queue_coordination_engine
)

# Import system index and management functions
from .index import (
    QueueSystemManager,
    initialize_queue_system,
    get_system_status,
    perform_health_check,
    optimize_performance,
    shutdown_system,
    get_system_manager
)

# Import configuration management
from .queue_config import (
    EnvironmentType,
    ResourceTier,
    SecurityProfile,
    SystemResources,
    QueueConfiguration,
    QueueConfigurationManager,
    create_queue_configuration_manager
)

# Import examples and testing
from .example_usage import (
    QueueSystemDemo,
    SimpleUsageExample,
    ProductionDeploymentExample,
    run_all_examples
)

from .test_queue_system import (
    TestResult,
    BenchmarkResult,
    QueueSystemTestSuite,
    run_queue_system_tests
)

# Main factory function for complete queue system
async def create_complete_queue_system(
    max_workers: int = 50,
    max_queue_size: int = 10000,
    analytics_retention_days: int = 90,
    enable_monitoring: bool = True,
    enable_diagnostics: bool = True,
    enable_auto_recovery: bool = True,
    core_queue_manager=None
):
    """
    Create complete integrated queue management system with all components
    
    Returns:
        Dict with all initialized components:
        - orchestrator: Main orchestrator
        - queue_manager: Queue manager
        - workers_manager: Workers manager  
        - priority_manager: Priority manager
        - analytics_engine: Analytics engine
        - distribution_engine: Task distribution engine
        - monitor: Real-time monitoring system
        - diagnostics: Health diagnostics system
    """
    
    # Create orchestrator with configuration
    from .queue_orchestrator import OrchestrationConfig
    
    config = OrchestrationConfig(
        max_workers=max_workers,
        max_queue_size=max_queue_size,
        auto_scaling_enabled=True
    )
    
    orchestrator = create_queue_orchestrator(config)
    
    # Initialize orchestrator (this creates all other components)
    if await orchestrator.initialize(core_queue_manager):
        
        # Create analytics engine
        analytics_engine = create_analytics_engine(analytics_retention_days)
        await analytics_engine.initialize()
        
        # Create advanced distribution engine
        distribution_engine = create_task_distribution_engine(
            strategy=DistributionStrategy.ML_PREDICTED,
            enable_prediction=True
        )
        
        # Create real-time monitoring if enabled
        monitor = None
        if enable_monitoring:
            monitor_config = MonitoringConfig(
                monitoring_level=MonitoringLevel.COMPREHENSIVE,
                collection_interval_seconds=30,
                alert_evaluation_interval_seconds=60,
                auto_recovery_enabled=enable_auto_recovery,
                predictive_alerts_enabled=True,
                anomaly_detection_enabled=True
            )
            
            monitor = create_realtime_queue_monitor(
                config=monitor_config,
                queue_manager=orchestrator.queue_manager,
                distribution_engine=distribution_engine
            )
            
            await monitor.initialize()
            await monitor.start_monitoring()
        
        # Create health diagnostics if enabled
        diagnostics = None
        if enable_diagnostics:
            diagnostics_config = DiagnosticConfig(
                diagnostic_interval_seconds=300,
                auto_recovery_enabled=enable_auto_recovery,
                enable_predictive_diagnostics=True,
                enable_root_cause_analysis=True
            )
            
            diagnostics = create_queue_health_diagnostics(
                config=diagnostics_config,
        queue_manager=orchestrator.queue_manager,
        distribution_engine=distribution_engine,
        monitor=monitor
    )
    
    await diagnostics.start_diagnostics()

# Create performance optimizer if enabled
optimizer = None
if enable_auto_recovery:
    from .queue_performance_optimizer import create_queue_performance_optimizer, OptimizationStrategy
    
    optimizer = create_queue_performance_optimizer(
        optimization_strategy=OptimizationStrategy.BALANCED_PERFORMANCE,
        enable_ml_prediction=True,
        optimization_interval_seconds=300
    )
    
    await optimizer.initialize(
        queue_manager=orchestrator.queue_manager,
        distribution_engine=distribution_engine
    )
    
    # Start continuous optimization
    await optimizer.start_continuous_optimization()

# Create security manager
security_manager = None
if enable_monitoring:  # Security enabled with monitoring
    from .queue_security_manager import create_queue_security_manager, SecurityLevel
    
    security_manager = create_queue_security_manager(
        security_level=SecurityLevel.ENHANCED,
        enable_encryption=True,
        enable_threat_detection=True
    )
    
    await security_manager.initialize()

# Create coordination engine
coordination_engine = None
if enable_monitoring:  # Coordination enabled with monitoring
    from .queue_coordination_engine import create_queue_coordination_engine, CoordinationMode
    
    coordination_engine = create_queue_coordination_engine(
        coordination_mode=CoordinationMode.COOPERATIVE,
        synchronization_type=SynchronizationType.LOOSE,
        resource_sharing_mode=ResourceSharingMode.DYNAMIC_SHARING
    )
    
    await coordination_engine.initialize()
    
    # Register queue nodes
    await coordination_engine.register_queue_node(
        node_id="primary_orchestrator",
        queue_manager=orchestrator.queue_manager,
        node_type="primary",
        capabilities=["crawler", "analytics", "protection"]
    )        return {
            "orchestrator": orchestrator,
            "queue_manager": orchestrator.queue_manager,
            "workers_manager": orchestrator.workers_manager,
            "priority_manager": orchestrator.priority_manager,
            "analytics_engine": analytics_engine,
            "distribution_engine": distribution_engine,
            "monitor": monitor,
            "diagnostics": diagnostics,
            "optimizer": optimizer,
            "security_manager": security_manager,
            "coordination_engine": coordination_engine,
            "status": "initialized",
            "features": {
                "monitoring_enabled": enable_monitoring,
                "diagnostics_enabled": enable_diagnostics,
                "auto_recovery_enabled": enable_auto_recovery,
                "ml_distribution": True,
                "predictive_analytics": True,
                "performance_optimization": optimizer is not None,
                "security_protection": security_manager is not None,
                "queue_coordination": coordination_engine is not None
            }
        }
    else:
        return {
            "status": "failed",
            "error": "Failed to initialize queue system"
        }

# Export all classes and functions
__all__ = [
    # Core managers
    "CrawlerQueueManager",
    "QueueWorkersManager", 
    "DynamicPriorityManager",
    "CrawlerQueueOrchestrator",
    "QueueAnalyticsEngine",
    
    # Advanced engines
    "TaskDistributionEngine",
    "MLDistributionPredictor",
    "RealtimeQueueMonitor",
    "AnomalyDetector",
    "PredictiveAnalyzer",
    "QueueHealthDiagnostics",
    "ComponentHealthAnalyzer",
    "RootCauseAnalyzer",
    "AutomatedRecoveryEngine",
    
    # New advanced engines
    "QueuePerformanceOptimizer",
    "MLPerformancePredictor",
    "QueueSecurityManager",
    "ThreatDetectionEngine",
    "EncryptionManager",
    "QueueCoordinationEngine",
    "CrossQueueLoadBalancer",
    
    # Task and config classes
    "CrawlerTask",
    "CrawlerQueueConfig",
    "WorkerConfig",
    "OrchestrationConfig",
    "MonitoringConfig",
    "DiagnosticConfig",
    "SecurityConfiguration",
    
    # New advanced classes
    "PerformanceMetric",
    "OptimizationOpportunity",
    "OptimizationPlan",
    "OptimizationResult",
    "SecurityEvent",
    "SecurityToken",
    "SecurityAudit",
    "QueueNode",
    "CoordinationTask",
    "ResourceAllocation",
    "CoordinationPlan",
    
    # Distribution classes
    "AgentCapability",
    "TaskResource",
    "DistributionResult",
    "LoadBalancingMetrics",
    
    # Monitoring classes
    "MetricDataPoint",
    "AlertRule",
    "MonitoringAlert",
    "PerformanceSnapshot",
    
    # Diagnostic classes
    "HealthMetric",
    "DiagnosticIssue",
    "RecoveryAction",
    "RecoveryPlan",
    "HealthReport",
    
    # Enums
    "CrawlerPriority",
    "PlatformType", 
    "CrawlerQueueType",
    "WorkerStatus",
    "WorkerType",
    "BusinessImpact",
    "UrgencyLevel",
    "OrchestrationStatus",
    "AnalyticsTimeframe",
    "MetricType",
    
    # Distribution enums
    "DistributionStrategy",
    "TaskComplexity",
    "ResourceType",
    
    # Monitoring enums
    "MonitoringLevel",
    "AlertSeverity",
    "MonitoringMetricType",
    "AlertCondition",
    
    # Diagnostic enums
    "HealthStatus",
    "DiagnosticCategory",
    "RecoveryStrategy",
    "DiagnosticSeverity",
    
    # New optimization enums
    "OptimizationStrategy",
    "OptimizationScope",
    "OptimizationTechnique",
    
    # New security enums
    "SecurityLevel",
    "ThreatSeverity",
    "SecurityEventType",
    "AccessPermission",
    
    # New coordination enums
    "CoordinationMode",
    "SynchronizationType",
    "ResourceSharingMode",
    "PriorityResolutionStrategy",
    
    # Data classes
    "CrawlerMetrics",
    "WorkerMetrics",
    "WorkerCapacity", 
    "PriorityFactors",
    "PriorityScore",
    "OrchestrationMetrics",
    "AnalyticsDataPoint",
    "PerformanceInsight",
    "AnalyticsReport",
    
    # Worker classes
    "CrawlerWorker",
    "PriorityCalculator",
    
    # Factory functions
    "create_crawler_queue_manager",
    "create_workers_manager",
    "create_priority_manager", 
    "create_queue_orchestrator",
    "create_analytics_engine",
    "create_task_distribution_engine",
    "create_realtime_queue_monitor",
    "create_queue_health_diagnostics",
    "create_queue_performance_optimizer",
    "create_queue_security_manager",
    "create_queue_coordination_engine",
    "create_complete_queue_system",
    
    # System management functions
    "QueueSystemManager",
    "initialize_queue_system",
    "get_system_status",
    "perform_health_check",
    "optimize_performance",
    "shutdown_system",
    "get_system_manager",
    
    # Configuration management
    "EnvironmentType",
    "ResourceTier",
    "SecurityProfile",
    "SystemResources",
    "QueueConfiguration",
    "QueueConfigurationManager",
    "create_queue_configuration_manager",
    
    # Examples and demonstrations
    "QueueSystemDemo",
    "SimpleUsageExample",
    "ProductionDeploymentExample",
    "run_all_examples",
    
    # Testing framework
    "TestResult",
    "BenchmarkResult",
    "QueueSystemTestSuite",
    "run_queue_system_tests"
]
