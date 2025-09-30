"""
🤖 AI/ML Performance Hub - Surveillance Intelligence Artificielle Enterprise
============================================================================

Hub spécialisé ultra-avancé pour la surveillance performance des modèles IA/ML Creator Economy.
Monitoring enterprise, détection anomalies, optimisation automatique, analytics prédictifs.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/ (NIVEAU 2)
Responsabilité: Performance IA enterprise, monitoring modèles ML, optimisation Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

# Core orchestrator
from .index import (
    AIMLPerformanceHub,
    ModelMetrics,
    ModelPerformanceAlert,
    InferenceLatencyOptimizer
)

# Critical Priority Components
from .model_inference_performance_monitor import (
    ModelInferencePerformanceMonitor,
    InferenceMetrics,
    ThroughputMetrics,
    ResourceUtilization,
    CreatorTier,
    ContentModality,
    InferenceType
)

from .gpu_utilization_analyzer import (
    GPUUtilizationAnalyzer,
    GPUDevice,
    GPUWorkload,
    GPUPerformanceMetrics,
    CreatorGPUUsage,
    GPUType,
    WorkloadType
)

from .latency_distribution_analyzer import (
    LatencyDistributionAnalyzer,
    LatencyMeasurement,
    LatencyDistribution,
    SLACompliance,
    LatencyAnomalyAlert,
    LatencyComponent,
    GeographicRegion,
    ServiceType
)

from .throughput_capacity_monitor import (
    ThroughputCapacityMonitor,
    ThroughputMetrics,
    CapacityMetrics,
    CreatorUsageMetrics,
    AutoScalingTrigger,
    PeakLoadAnalysis,
    LoadPattern
)

from .model_drift_detection_engine import (
    ModelDriftDetectionEngine,
    DriftMeasurement,
    DriftAlert,
    ModelBehaviorPattern,
    RetrainingRecommendation,
    DriftType,
    DriftSeverity,
    DetectionMethod,
    FeatureStatistics
)

# Medium Priority Components (New)
from .batch_processing_performance_analyzer import (
    BatchProcessingPerformanceAnalyzer,
    BatchJob,
    BatchMetrics,
    QueueAnalytics,
    BatchOptimizationRecommendation,
    ParallelProcessingMetrics,
    BatchProcessingType,
    BatchStatus,
    OptimizationStrategy
)

from .model_serving_scalability_manager import (
    ModelServingScalabilityManager,
    ModelInstance,
    ScalingMetrics,
    LoadBalancingMetrics,
    CanaryDeploymentMetrics,
    ScalabilityRecommendation,
    ModelServingFramework,
    ScalingStrategy,
    LoadBalancingAlgorithm,
    DeploymentStrategy
)

from .ai_workload_distribution_controller import (
    AIWorkloadDistributionController,
    AICluster,
    WorkloadRequest,
    RoutingDecision,
    LoadDistributionMetrics,
    WorkloadMigration,
    PeakShavingRecommendation,
    WorkloadType,
    RoutingStrategy,
    ClusterType
)

from .performance_anomaly_detection_system import (
    PerformanceAnomalyDetectionSystem,
    PerformanceMetric,
    AnomalyDetection,
    AnomalyPattern,
    RootCauseAnalysis,
    AnomalyAlert,
    AnomalyType,
    AnomalySeverity,
    DetectionMethod
)

from .creator_ai_usage_analytics_engine import (
    CreatorAIUsageAnalyticsEngine,
    CreatorProfile,
    AIUsageSession,
    ROIAnalytics,
    ContentType,
    AIFeatureType
)

from .model_performance_benchmarking_suite import (
    ModelPerformanceBenchmarkingSuite,
    ModelConfiguration,
    BenchmarkResult,
    CrossModelComparison,
    IndustryBenchmark,
    RegressionTestResult,
    BenchmarkSuite,
    BenchmarkType,
    ModelFramework as BenchmarkModelFramework,
    ContentDomain
)

# High Priority Components
from .training_pipeline_performance_tracker import (
    TrainingPipelinePerformanceTracker,
    TrainingMetrics,
    ConvergenceAnalysis,
    ResourceEfficiencyMetrics,
    TrainingComparison,
    TrainingPhase,
    ModelFramework,
    TrainingType,
    CreatorContentType
)

from .memory_optimization_controller import (
    MemoryOptimizationController,
    MemoryUsageMetrics,
    MemoryOptimizationAction,
    MemoryPoolConfiguration,
    OOMPreventionAlert,
    MemoryType,
    OptimizationStrategy,
    MemoryPressureLevel,
    CreatorTierMemory
)

from .prediction_accuracy_validator import (
    PredictionAccuracyValidator,
    PredictionAccuracyMetrics,
    ValidationReport,
    AccuracyAlert,
    ConfidenceCalibration,
    PredictionType,
    AccuracyThreshold,
    ValidationMethod,
    CreatorContentCategory
)

from .resource_allocation_optimizer import (
    ResourceAllocationOptimizer,
    ResourceUnit,
    AllocationRequest,
    ResourceAllocation,
    OptimizationResult,
    ResourcePool,
    ResourceType,
    AllocationStrategy,
    CreatorTierPriority,
    ResourceStatus,
    WorkloadType
)

from .real_time_inference_metrics_collector import (
    RealTimeInferenceMetricsCollector,
    InferenceMetric,
    StreamingWindow,
    HotPathMetrics,
    EdgeInferenceMetrics,
    AlertThreshold,
    MetricType,
    AggregationMethod,
    MetricPriority,
    CreatorInteractionType
)

from .feature_importance_tracker import (
    FeatureImportanceTracker,
    FeatureImportanceScore,
    FeatureType,
    ImportanceMethod,
    CreatorContentDomain,
    FeatureRelevanceLevel
)

__all__ = [
    # Core orchestrator
    'AIMLPerformanceHub',
    'ModelMetrics',
    'ModelPerformanceAlert',
    'InferenceLatencyOptimizer',
    
    # Model Inference Performance Monitor
    'ModelInferencePerformanceMonitor',
    'InferenceMetrics',
    'ThroughputMetrics',
    'ResourceUtilization',
    
    # GPU Utilization Analyzer
    'GPUUtilizationAnalyzer',
    'GPUDevice',
    'GPUWorkload',
    'GPUPerformanceMetrics',
    'CreatorGPUUsage',
    'GPUType',
    'WorkloadType',
    
    # Latency Distribution Analyzer
    'LatencyDistributionAnalyzer',
    'LatencyMeasurement',
    'LatencyDistribution',
    'SLACompliance',
    'LatencyAnomalyAlert',
    'LatencyComponent',
    'GeographicRegion',
    
    # Throughput Capacity Monitor
    'ThroughputCapacityMonitor',
    'CapacityMetrics',
    'CreatorUsageMetrics',
    'AutoScalingTrigger',
    'PeakLoadAnalysis',
    'LoadPattern',
    
    # Model Drift Detection Engine
    'ModelDriftDetectionEngine',
    'DriftMeasurement',
    'DriftAlert',
    'ModelBehaviorPattern',
    'RetrainingRecommendation',
    'DriftType',
    'DriftSeverity',
    'DetectionMethod',
    'FeatureStatistics',
    
    # Medium Priority Components (New)
    'BatchProcessingPerformanceAnalyzer',
    'BatchJob',
    'BatchMetrics',
    'QueueAnalytics',
    'BatchOptimizationRecommendation',
    'ParallelProcessingMetrics',
    'BatchProcessingType',
    'BatchStatus',
    'OptimizationStrategy',
    
    'ModelServingScalabilityManager',
    'ModelInstance',
    'ScalingMetrics',
    'LoadBalancingMetrics',
    'CanaryDeploymentMetrics',
    'ScalabilityRecommendation',
    'ModelServingFramework',
    'ScalingStrategy',
    'LoadBalancingAlgorithm',
    'DeploymentStrategy',
    
    'AIWorkloadDistributionController',
    'AICluster',
    'WorkloadRequest',
    'RoutingDecision',
    'LoadDistributionMetrics',
    'WorkloadMigration',
    'PeakShavingRecommendation',
    'WorkloadType',
    'RoutingStrategy',
    'ClusterType',
    
    'PerformanceAnomalyDetectionSystem',
    'PerformanceMetric',
    'AnomalyDetection',
    'AnomalyPattern',
    'RootCauseAnalysis',
    'AnomalyAlert',
    'AnomalyType',
    'AnomalySeverity',
    'DetectionMethod',
    
    'CreatorAIUsageAnalyticsEngine',
    'CreatorProfile',
    'AIUsageSession',
    'ROIAnalytics',
    'ContentType',
    'AIFeatureType',
    
    'ModelPerformanceBenchmarkingSuite',
    'ModelConfiguration',
    'BenchmarkResult',
    'CrossModelComparison',
    'IndustryBenchmark',
    'RegressionTestResult',
    'BenchmarkSuite',
    'BenchmarkType',
    'BenchmarkModelFramework',
    'ContentDomain',
    
    # Training Pipeline Performance Tracker
    'TrainingPipelinePerformanceTracker',
    'TrainingMetrics',
    'ConvergenceAnalysis',
    'ResourceEfficiencyMetrics',
    'TrainingComparison',
    'TrainingPhase',
    'ModelFramework',
    'TrainingType',
    'CreatorContentType',
    
    # Memory Optimization Controller
    'MemoryOptimizationController',
    'MemoryUsageMetrics',
    'MemoryOptimizationAction',
    'MemoryPoolConfiguration',
    'OOMPreventionAlert',
    'MemoryType',
    'MemoryPressureLevel',
    'CreatorTierMemory',
    
    # Prediction Accuracy Validator
    'PredictionAccuracyValidator',
    'PredictionAccuracyMetrics',
    'ValidationReport',
    'AccuracyAlert',
    'ConfidenceCalibration',
    'PredictionType',
    'AccuracyThreshold',
    'ValidationMethod',
    'CreatorContentCategory',
    
    # Resource Allocation Optimizer
    'ResourceAllocationOptimizer',
    'ResourceUnit',
    'AllocationRequest',
    'ResourceAllocation',
    'OptimizationResult',
    'ResourcePool',
    'ResourceType',
    'AllocationStrategy',
    'CreatorTierPriority',
    'ResourceStatus',
    
    # Real-Time Inference Metrics Collector
    'RealTimeInferenceMetricsCollector',
    'InferenceMetric',
    'StreamingWindow',
    'HotPathMetrics',
    'EdgeInferenceMetrics',
    'AlertThreshold',
    'MetricType',
    'AggregationMethod',
    'MetricPriority',
    'CreatorInteractionType',
    
    # Feature Importance Tracker
    'FeatureImportanceTracker',
    'FeatureImportanceScore',
    'FeatureType',
    'ImportanceMethod',
    'CreatorContentDomain',
    'FeatureRelevanceLevel',
    
    # Common enums
    'CreatorTier',
    'ContentModality',
    'InferenceType',
    'ServiceType'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production-Ready Enterprise"
__architecture__ = "AI/ML Performance Hub Creator Economy"