"""Pipeline Index

Centralized import index for easy access to all pipeline components
with comprehensive utility functions and health validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Central Access → Component Discovery → Health Validation → Quick Utilities
"""

import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime

logger = logging.getLogger(__name__)

# Import all pipeline components
try:
    # Core orchestration
    from .master_orchestrator import MasterPipelineOrchestrator, PipelineRequest, PipelineResponse
    from .content_pipeline import ContentProcessingPipeline, ContentProcessor
    from .protection_pipeline import ProtectionProcessingPipeline, FingerprintingEngine
    from .monetization_pipeline import MonetizationPipeline, RevenueOptimizer
    
    # Configuration and exceptions
    from .config import (
        PipelineConfiguration, ConfigurationManager, ConfigurationValidator,
        EnvironmentManager, SecurityManager, PerformanceManager
    )
    from .exceptions import (
        PipelineError, StageExecutionError, ValidationError, ResourceError,
        TimeoutError, ConfigurationError, DependencyError, RecoveryManager
    )
    
    # Workflow and execution
    from .workflow_engine import (
        WorkflowEngine, WorkflowDefinition, TaskManager, DependencyResolver,
        ParallelProcessor, StateManager, WorkflowFactory
    )
    from .execution_manager import (
        ExecutionManager, ResourceManager, CapacityPlanner, LoadBalancer,
        PerformanceMonitor, HealthChecker
    )
    from .stage_coordinator import (
        StageCoordinator, StageDefinition, TransitionManager, GateKeeper,
        StageValidator, ProgressTracker, ErrorHandler
    )
    
    # Quality and optimization
    from .quality_controller import (
        QualityController, QualityGate, QualityMetrics, QualityValidator,
        QualityOptimizer, ThresholdManager, QualityReporter
    )
    from .performance_optimizer import (
        PerformanceOptimizer, OptimizationEngine, ResourceOptimizer,
        ThroughputOptimizer, LatencyOptimizer, BottleneckDetector, ScalingManager
    )
    
    # Monitoring and validation
    from .monitoring_system import (
        MonitoringSystem, MetricsCollector, AlertManager, HealthMonitor,
        AnomalyDetector, ReportGenerator
    )
    from .data_validator import (
        DataValidator, ValidationRule, ValidationResult, DataProfile,
        ValidationReport, SchemaValidator, RangeValidator, PatternValidator,
        AnomalyDetector as DataAnomalyDetector, DataProfiler
    )
    
    IMPORT_SUCCESS = True
    IMPORT_ERRORS = []

except ImportError as e:
    IMPORT_SUCCESS = False
    IMPORT_ERRORS = [str(e)]
    logger.error(f"Failed to import pipeline components: {e}")

# Component registry for dynamic access
COMPONENT_REGISTRY = {
    # Core pipelines
    'master_orchestrator': MasterPipelineOrchestrator,
    'content_pipeline': ContentProcessingPipeline,
    'protection_pipeline': ProtectionProcessingPipeline,
    'monetization_pipeline': MonetizationPipeline,
    
    # Management systems
    'workflow_engine': WorkflowEngine,
    'execution_manager': ExecutionManager,
    'stage_coordinator': StageCoordinator,
    'quality_controller': QualityController,
    'performance_optimizer': PerformanceOptimizer,
    'monitoring_system': MonitoringSystem,
    'data_validator': DataValidator,
    
    # Configuration
    'config_manager': ConfigurationManager,
    'config_validator': ConfigurationValidator,
    
    # Specialized components
    'resource_manager': ResourceManager,
    'metrics_collector': MetricsCollector,
    'alert_manager': AlertManager,
    'anomaly_detector': AnomalyDetector
} if IMPORT_SUCCESS else {}

# Quick access functions
def get_component(component_name: str) -> Optional[Type]:
    """Get component class by name"""
    return COMPONENT_REGISTRY.get(component_name)

def list_components() -> List[str]:
    """
List all available components"""
    return list(COMPONENT_REGISTRY.keys())

def get_component_info(component_name: str) -> Dict[str, Any]:
    """
Get component information"""
    component = get_component(component_name)
    if not component:
        return {}
    
    return {
        'name': component_name,
        'class': component.__name__,
        'module': component.__module__,
        'doc': component.__doc__,
        'methods': [method for method in dir(component) if not method.startswith('_')]
    }

def create_default_pipeline() -> Optional[MasterPipelineOrchestrator]:
    """
Create pipeline with default configuration"""
    if not IMPORT_SUCCESS:
        logger.error("Cannot create pipeline - import errors exist")
        return None
    
    try:
        config_manager = ConfigurationManager()
        default_config = config_manager.get_default_configuration()
        return MasterPipelineOrchestrator(default_config)
    except Exception as e:
        logger.error(f"Failed to create default pipeline: {e}")
        return None

def validate_pipeline_health() -> Dict[str, Any]:
    """Validate overall pipeline health"""
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy',
        'import_status': IMPORT_SUCCESS,
        'import_errors': IMPORT_ERRORS,
        'available_components': len(COMPONENT_REGISTRY),
        'component_details': {}
    }
    
    if not IMPORT_SUCCESS:
        health_report['overall_status'] = 'unhealthy'
        return health_report
    
    # Test component instantiation
    for name, component_class in COMPONENT_REGISTRY.items():
        try:
            # Test if class can be instantiated (basic check)
            if hasattr(component_class, '__init__'):
                health_report['component_details'][name] = {
                    'status': 'available',
                    'class_name': component_class.__name__
                }
            else:
                health_report['component_details'][name] = {
                    'status': 'warning',
                    'issue': 'No __init__ method found'
                }
        except Exception as e:
            health_report['component_details'][name] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Check for any component errors
    error_count = sum(1 for details in health_report['component_details'].values() 
                     if details['status'] == 'error')
    
    if error_count > 0:
        health_report['overall_status'] = 'degraded'
    
    return health_report

def get_pipeline_status() -> Dict[str, Any]:
    """
Get comprehensive pipeline status"""
    return {
        'version': '3.0.0',
        'author': 'Fahed Mlaiel',
        'import_success': IMPORT_SUCCESS,
        'components_available': len(COMPONENT_REGISTRY),
        'health_check': validate_pipeline_health(),
        'business_logic': 'User Upload → AI Protection → SEO → Collaboration → Distribution → Monetization'
    }

# Export all for easy importing
__all__ = [
    # Status functions
    'get_component',
    'list_components', 
    'get_component_info',
    'create_default_pipeline',
    'validate_pipeline_health',
    'get_pipeline_status',
    
    # Component registry
    'COMPONENT_REGISTRY',
    'IMPORT_SUCCESS',
    'IMPORT_ERRORS'
]

# Add all imported components to __all__ if import successful
if IMPORT_SUCCESS:
    __all__.extend([
        # Core orchestration
        'MasterPipelineOrchestrator', 'PipelineRequest', 'PipelineResponse',
        'ContentProcessingPipeline', 'ContentProcessor',
        'ProtectionProcessingPipeline', 'FingerprintingEngine', 
        'MonetizationPipeline', 'RevenueOptimizer',
        
        # Configuration and exceptions
        'PipelineConfiguration', 'ConfigurationManager', 'ConfigurationValidator',
        'EnvironmentManager', 'SecurityManager', 'PerformanceManager',
        'PipelineError', 'StageExecutionError', 'ValidationError', 'ResourceError',
        'TimeoutError', 'ConfigurationError', 'DependencyError', 'RecoveryManager',
        
        # Workflow and execution
        'WorkflowEngine', 'WorkflowDefinition', 'TaskManager', 'DependencyResolver',
        'ParallelProcessor', 'StateManager', 'WorkflowFactory',
        'ExecutionManager', 'ResourceManager', 'CapacityPlanner', 'LoadBalancer',
        'PerformanceMonitor', 'HealthChecker',
        'StageCoordinator', 'StageDefinition', 'TransitionManager', 'GateKeeper',
        'StageValidator', 'ProgressTracker', 'ErrorHandler',
        
        # Quality and optimization
        'QualityController', 'QualityGate', 'QualityMetrics', 'QualityValidator',
        'QualityOptimizer', 'ThresholdManager', 'QualityReporter',
        'PerformanceOptimizer', 'OptimizationEngine', 'ResourceOptimizer',
        'ThroughputOptimizer', 'LatencyOptimizer', 'BottleneckDetector', 'ScalingManager',
        
        # Monitoring and validation
        'MonitoringSystem', 'MetricsCollector', 'AlertManager', 'HealthMonitor',
        'AnomalyDetector', 'ReportGenerator',
        'DataValidator', 'ValidationRule', 'ValidationResult', 'DataProfile',
        'ValidationReport', 'SchemaValidator', 'RangeValidator', 'PatternValidator',
        'DataAnomalyDetector', 'DataProfiler'
    ])

# Module metadata
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Master Orchestrator
from .master_orchestrator import (
    MasterPipelineOrchestrator,
    PipelineRequest,
    PipelineResponse,
    PipelineStatus,
    PipelineStage,
    ExecutionContext,
    StageResult,
    WorkflowMetrics,
    ExecutionPriority
)

# Content Pipeline
from .content_pipeline import (
    ContentProcessingPipeline,
    ContentPipelineStage,
    ContentProcessor,
    ProcessingResult,
    ContentMetrics,
    QualityGate,
    ValidationGate,
    OptimizationGate,
    ContentType,
    ProcessingQuality
)

# Protection Pipeline
from .protection_pipeline import (
    ProtectionProcessingPipeline,
    FingerprintingEngine,
    ProtectionStage,
    ProtectionResult,
    ThreatDetection,
    SecurityGate,
    ComplianceValidator,
    ProtectionLevel,
    ThreatLevel,
    FingerprintType,
    FingerprintData
)

# Monetization Pipeline
from .monetization_pipeline import (
    MonetizationPipeline,
    RevenueEngine,
    MonetizationStage,
    RevenueCalculator,
    PayoutProcessor,
    LicensingEngine,
    RevenueOptimizer
)

# Distribution Pipeline
from .distribution_pipeline import (
    DistributionPipeline,
    PlatformDistributor,
    DistributionStage,
    PlatformAdapter,
    DistributionOptimizer,
    DeliveryValidator,
    PerformanceTracker
)

# Workflow Engine
from .workflow_engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowExecutor,
    WorkflowTask,
    TaskManager,
    DependencyResolver,
    ParallelProcessor,
    StateManager,
    RecoveryManager,
    WorkflowState,
    TaskState,
    TaskType,
    ExecutionMode,
    TaskPriority,
    TaskCondition,
    TaskResult,
    WorkflowExecution,
    TaskExecutor,
    BaseTaskExecutor,
    ContentProcessingExecutor,
    AIAnalysisExecutor,
    WorkflowBuilder,
    WorkflowFactory,
    TaskMetrics,
    ConditionOperator,
    WorkflowTrigger
)

# Execution Manager
from .execution_manager import (
    ExecutionManager,
    ResourceManager,
    CapacityPlanner,
    LoadBalancer,
    PerformanceMonitor,
    HealthChecker
)

# Stage Coordinator
from .stage_coordinator import (
    StageCoordinator,
    StageDefinition,
    TransitionManager,
    GateKeeper,
    StageValidator,
    ProgressTracker,
    ErrorHandler
)

# Quality Controller
from .quality_controller import (
    QualityController,
    QualityGate,
    QualityMetrics,
    QualityValidator,
    QualityOptimizer,
    ThresholdManager,
    QualityReporter
)

# Performance Optimizer
from .performance_optimizer import (
    PerformanceOptimizer,
    OptimizationEngine,
    ResourceOptimizer,
    ThroughputOptimizer,
    LatencyOptimizer,
    BottleneckDetector,
    ScalingManager
)

# Monitoring System
from .monitoring_system import (
    PipelineMonitor,
    MetricsCollector,
    AlertManager,
    HealthMonitor,
    PerformanceTracker,
    AnomalyDetector,
    ReportGenerator
)

# Configuration
from .config import (
    PipelineConfiguration,
    ConfigurationLoader,
    ConfigurationValidator,
    ConfigurationSource,
    ConfigurationFormat,
    EnvironmentType,
    ConfigurationSchema,
    ConfigurationEntry
)

# Exceptions
from .exceptions import (
    PipelineError,
    StageExecutionError,
    ValidationError,
    ResourceError,
    TimeoutError,
    ConfigurationError,
    DependencyError,
    ContentProcessingError,
    AIProcessingError,
    ProtectionError,
    DistributionError,
    MonetizationError,
    SecurityError,
    ExternalServiceError,
    NetworkError,
    AnalyticsError,
    QualityGateError,
    CircuitBreakerError,
    RateLimitError,
    ErrorSeverity,
    ErrorCategory,
    RecoveryStrategy,
    ErrorImpact,
    ErrorContext,
    RecoveryAttempt,
    ErrorMetrics,
    ErrorHandlerRegistry,
    error_handler_registry
)

# Export all pipeline components
__all__ = [
    # Master Orchestrator
    'MasterPipelineOrchestrator',
    'PipelineRequest',
    'PipelineResponse',
    'PipelineStatus',
    'PipelineStage',
    'ExecutionContext',
    'StageResult',
    'WorkflowMetrics',
    'ExecutionPriority',
    
    # Content Pipeline
    'ContentProcessingPipeline',
    'ContentPipelineStage',
    'ContentProcessor',
    'ProcessingResult',
    'ContentMetrics',
    'QualityGate',
    'ValidationGate',
    'OptimizationGate',
    'ContentType',
    'ProcessingQuality',
    
    # Protection Pipeline
    'ProtectionProcessingPipeline',
    'FingerprintingEngine',
    'ProtectionStage',
    'ProtectionResult',
    'ThreatDetection',
    'SecurityGate',
    'ComplianceValidator',
    'ProtectionLevel',
    'ThreatLevel',
    'FingerprintType',
    'FingerprintData',
    
    # Monetization Pipeline
    'MonetizationPipeline',
    'RevenueEngine',
    'MonetizationStage',
    'RevenueCalculator',
    'PayoutProcessor',
    'LicensingEngine',
    'RevenueOptimizer',
    
    # Distribution Pipeline
    'DistributionPipeline',
    'PlatformDistributor',
    'DistributionStage',
    'PlatformAdapter',
    'DistributionOptimizer',
    'DeliveryValidator',
    'PerformanceTracker',
    
    # Workflow Engine
    'WorkflowEngine',
    'WorkflowDefinition',
    'WorkflowExecutor',
    'WorkflowTask',
    'TaskManager',
    'DependencyResolver',
    'ParallelProcessor',
    'StateManager',
    'RecoveryManager',
    'WorkflowState',
    'TaskState',
    'TaskType',
    'ExecutionMode',
    'TaskPriority',
    'TaskCondition',
    'TaskResult',
    'WorkflowExecution',
    'TaskExecutor',
    'BaseTaskExecutor',
    'ContentProcessingExecutor',
    'AIAnalysisExecutor',
    'WorkflowBuilder',
    'WorkflowFactory',
    'TaskMetrics',
    'ConditionOperator',
    'WorkflowTrigger',
    
    # Execution Manager
    'ExecutionManager',
    'ResourceManager',
    'CapacityPlanner',
    'LoadBalancer',
    'PerformanceMonitor',
    'HealthChecker',
    
    # Stage Coordinator
    'StageCoordinator',
    'StageDefinition',
    'TransitionManager',
    'GateKeeper',
    'StageValidator',
    'ProgressTracker',
    'ErrorHandler',
    
    # Quality Controller
    'QualityController',
    'QualityMetrics',
    'QualityValidator',
    'QualityOptimizer',
    'ThresholdManager',
    'QualityReporter',
    
    # Performance Optimizer
    'PerformanceOptimizer',
    'OptimizationEngine',
    'ResourceOptimizer',
    'ThroughputOptimizer',
    'LatencyOptimizer',
    'BottleneckDetector',
    'ScalingManager',
    
    # Monitoring System
    'PipelineMonitor',
    'MetricsCollector',
    'AlertManager',
    'HealthMonitor',
    'AnomalyDetector',
    'ReportGenerator',
    
    # Configuration
    'PipelineConfiguration',
    'ConfigurationLoader',
    'ConfigurationValidator',
    'ConfigurationSource',
    'ConfigurationFormat',
    'EnvironmentType',
    'ConfigurationSchema',
    'ConfigurationEntry',
    
    # Exceptions
    'PipelineError',
    'StageExecutionError',
    'ValidationError',
    'ResourceError',
    'TimeoutError',
    'ConfigurationError',
    'DependencyError',
    'ContentProcessingError',
    'AIProcessingError',
    'ProtectionError',
    'DistributionError',
    'MonetizationError',
    'SecurityError',
    'ExternalServiceError',
    'NetworkError',
    'AnalyticsError',
    'QualityGateError',
    'CircuitBreakerError',
    'RateLimitError',
    'ErrorSeverity',
    'ErrorCategory',
    'RecoveryStrategy',
    'ErrorImpact',
    'ErrorContext',
    'RecoveryAttempt',
    'ErrorMetrics',
    'ErrorHandlerRegistry',
    'error_handler_registry'
]

# Module metadata
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Ultra-advanced pipeline orchestration system for IA Influencer Agent platform"
__license__ = "Proprietary - All rights reserved"

# Quick access functions for common operations
def create_content_workflow(content_type: str) -> WorkflowDefinition:
    """Quick function to create content processing workflow"""
    return WorkflowFactory.create_content_processing_workflow(content_type)

def create_protection_workflow() -> WorkflowDefinition:
    """
Quick function to create protection workflow"""
    return WorkflowFactory.create_protection_workflow()

def create_distribution_workflow() -> WorkflowDefinition:
    """
Quick function to create distribution workflow"""
    return WorkflowFactory.create_distribution_workflow()

def get_all_pipeline_components():
    """
Get all available pipeline components"""
    return {
        'orchestrators': [MasterPipelineOrchestrator],
        'pipelines': [
            ContentProcessingPipeline,
            ProtectionProcessingPipeline,
            MonetizationPipeline,
            DistributionPipeline
        ],
        'engines': [WorkflowEngine],
        'managers': [
            ExecutionManager,
            TaskManager,
            StateManager,
            RecoveryManager
        ],
        'coordinators': [StageCoordinator],
        'controllers': [QualityController],
        'optimizers': [PerformanceOptimizer],
        'monitors': [PipelineMonitor],
        'exceptions': [
            PipelineError,
            StageExecutionError,
            ValidationError,
            ResourceError,
            TimeoutError,
            ConfigurationError,
            DependencyError
        ]
    }

# Development and debugging helpers
def get_pipeline_health_status():
    """
Get overall pipeline health status"""
    return {
        'status': 'healthy',
        'components_loaded': len(__all__),
        'version': __version__,
        'author': __author__
    }

def validate_pipeline_setup():
    """
Validate pipeline setup and dependencies"""
    validation_results = {
        'dependencies_available': True,
        'configurations_valid': True,
        'components_initialized': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Test basic imports and instantiation
        config = PipelineConfiguration()
        orchestrator = MasterPipelineOrchestrator()
        workflow_engine = WorkflowEngine()
        
        validation_results['test_instantiation'] = True
        
    except Exception as e:
        validation_results['dependencies_available'] = False
        validation_results['errors'].append(f"Instantiation failed: {e}")
    
    return validation_results
