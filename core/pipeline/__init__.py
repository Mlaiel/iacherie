"""Core Pipeline Module

Ultra-advanced pipeline orchestration system for IA Influencer Agent platform.
Implements complete business workflow: User Upload → AI Protection → SEO → Collaboration → Distribution → Monetization

Project: IA Influencer Agent + Protection Platform
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

Contact mlaiel@live.de for licensing inquiries only.
"""
from .master_orchestrator import (
    MasterPipelineOrchestrator,
    PipelineRequest,
    PipelineResponse,
    PipelineStatus,
    PipelineStage,
    ExecutionContext,
    StageResult,
    WorkflowMetrics
)

from .content_pipeline import (
    ContentProcessingPipeline,
    ContentPipelineStage,
    ContentProcessor,
    ProcessingResult,
    ContentMetrics,
    QualityGate,
    ValidationGate,
    OptimizationGate
)

from .protection_pipeline import (
    ProtectionProcessingPipeline,
    FingerprintingEngine,
    ProtectionStage,
    ProtectionResult,
    ThreatDetection,
    SecurityGate,
    ComplianceValidator
)

from .monetization_pipeline import (
    MonetizationPipeline,
    RevenueEngine,
    MonetizationStage,
    RevenueCalculator,
    PayoutProcessor,
    LicensingEngine,
    RevenueOptimizer
)

from .distribution_pipeline import (
    DistributionPipeline,
    PlatformDistributor,
    DistributionStage,
    PlatformAdapter,
    DistributionOptimizer,
    DeliveryValidator,
    PerformanceTracker
)

from .workflow_engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowExecutor,
    TaskManager,
    DependencyResolver,
    ParallelProcessor,
    StateManager,
    RecoveryManager
)

from .execution_manager import (
    ExecutionManager,
    ExecutionContext,
    ResourceManager,
    CapacityPlanner,
    LoadBalancer,
    PerformanceMonitor,
    HealthChecker
)

from .stage_coordinator import (
    StageCoordinator,
    StageDefinition,
    TransitionManager,
    GateKeeper,
    StageValidator,
    ProgressTracker,
    ErrorHandler
)

from .data_validator import (
    DataValidator,
    ValidationRule,
    ValidationResult,
    DataProfile,
    ValidationReport,
    BaseValidator,
    SchemaValidator,
    RangeValidator,
    PatternValidator,
    AnomalyDetector,
    DataProfiler,
    ValidationType,
    DataType,
    ValidationLevel,
    ValidationStatus,
    CorrectionAction
)

from .quality_controller import (
    QualityController,
    QualityGate,
    QualityMetrics,
    QualityValidator,
    QualityOptimizer,
    ThresholdManager,
    QualityReporter
)

from .performance_optimizer import (
    PerformanceOptimizer,
    OptimizationEngine,
    ResourceOptimizer,
    ThroughputOptimizer,
    LatencyOptimizer,
    BottleneckDetector,
    ScalingManager
)

from .monitoring_system import (
    PipelineMonitor,
    MetricsCollector,
    AlertManager,
    HealthMonitor,
    PerformanceTracker,
    AnomalyDetector,
    ReportGenerator
)

from .exceptions import (
    PipelineError,
    StageExecutionError,
    ValidationError,
    ResourceError,
    TimeoutError,
    ConfigurationError,
    DependencyError
)

from .config import (
    PipelineConfig,
    StageConfig,
    ResourceConfig,
    MonitoringConfig,
    OptimizationConfig,
    SecurityConfig
)

# Export main components
__all__ = [
    # Master orchestrator
    'MasterPipelineOrchestrator',
    'PipelineRequest',
    'PipelineResponse',
    'PipelineStatus',
    'PipelineStage',
    'ExecutionContext',
    'StageResult',
    'WorkflowMetrics',
    
    # Content pipeline
    'ContentProcessingPipeline',
    'ContentPipelineStage',
    'ContentProcessor',
    'ProcessingResult',
    'ContentMetrics',
    'QualityGate',
    'ValidationGate',
    'OptimizationGate',
    
    # Protection pipeline
    'ProtectionProcessingPipeline',
    'FingerprintingEngine',
    'ProtectionStage',
    'ProtectionResult',
    'ThreatDetection',
    'SecurityGate',
    'ComplianceValidator',
    
    # Monetization pipeline
    'MonetizationPipeline',
    'RevenueEngine',
    'MonetizationStage',
    'RevenueCalculator',
    'PayoutProcessor',
    'LicensingEngine',
    'RevenueOptimizer',
    
    # Distribution pipeline
    'DistributionPipeline',
    'PlatformDistributor',
    'DistributionStage',
    'PlatformAdapter',
    'DistributionOptimizer',
    'DeliveryValidator',
    'PerformanceTracker',
    
    # Workflow engine
    'WorkflowEngine',
    'WorkflowDefinition',
    'WorkflowExecutor',
    'TaskManager',
    'DependencyResolver',
    'ParallelProcessor',
    'StateManager',
    'RecoveryManager',
    
    # Execution management
    'ExecutionManager',
    'ResourceManager',
    'CapacityPlanner',
    'LoadBalancer',
    'PerformanceMonitor',
    'HealthChecker',
    
    # Stage coordination
    'StageCoordinator',
    'StageDefinition',
    'TransitionManager',
    'GateKeeper',
    'StageValidator',
    'ProgressTracker',
    'ErrorHandler',
    
    # Quality control
    'QualityController',
    'QualityMetrics',
    'QualityValidator',
    'QualityOptimizer',
    'ThresholdManager',
    'QualityReporter',
    
    # Performance optimization
    'PerformanceOptimizer',
    'OptimizationEngine',
    'ResourceOptimizer',
    'ThroughputOptimizer',
    'LatencyOptimizer',
    'BottleneckDetector',
    'ScalingManager',
    
    # Monitoring
    'PipelineMonitor',
    'MetricsCollector',
    'AlertManager',
    'HealthMonitor',
    'AnomalyDetector',
    'ReportGenerator',
    
    # Configuration and exceptions
    'PipelineConfig',
    'StageConfig',
    'ResourceConfig',
    'MonitoringConfig',
    'OptimizationConfig',
    'SecurityConfig',
    'PipelineError',
    'StageExecutionError',
    'ValidationError',
    'ResourceError',
    'TimeoutError',
    'ConfigurationError',
    'DependencyError',
    
    # Data validation
    'DataValidator',
    'ValidationRule',
    'ValidationResult',
    'DataProfile',
    'ValidationReport',
    'BaseValidator',
    'SchemaValidator',
    'RangeValidator',
    'PatternValidator',
    'AnomalyDetector',
    'DataProfiler',
    'ValidationType',
    'DataType',
    'ValidationLevel',
    'ValidationStatus',
    'CorrectionAction'
]

# Pipeline version and metadata
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Ultra-advanced pipeline orchestration system for IA Influencer Agent platform"
