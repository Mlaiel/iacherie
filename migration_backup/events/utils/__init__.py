"""Events Utils Module - Ultra-Advanced Enterprise Suite

Ultra-advanced utility classes and functions for the Ainflue events system.
Complete enterprise-grade event processing utilities with business intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core monitoring (enhanced)
from .monitoring import MetricsCollector

# Ultra-advanced event processing engines
from .event_serialization_engine import (
    EventSerializationEngine,
    SerializationFormat,
    CompressionAlgorithm,
    CompressionConfig,
    SerializedEvent,
    SerializationMetrics
)

from .event_validation_framework import (
    EventValidationFramework,
    ValidationContext,
    EventValidationResult,
    BusinessValidationResult,
    ValidationSeverity,
    ValidationLayer,
    BusinessRuleViolation
)

from .event_transformation_pipeline import (
    EventTransformationPipeline,
    TransformationContext,
    TransformedEvent,
    TransformationType,
    TransformationPriority,
    TransformationRegistry,
    BusinessAnalysis,
    SchemaMapper,
    BaseTransformation
)

from .performance_optimization_toolkit import (
    PerformanceOptimizationToolkit,
    OptimizationLevel,
    ResourceLimits,
    CacheConfig,
    PerformanceMetrics,
    OptimizationResult
)

from .event_correlation_analyzer import (
    EventCorrelationAnalyzer,
    CorrelationType,
    CorrelationRule,
    EventCorrelation,
    CorrelationInsight
)

from .business_metrics_aggregator import (
    BusinessMetricsAggregator,
    MetricType,
    AggregationPeriod,
    MetricDefinition,
    MetricValue,
    AggregatedMetric,
    BusinessAlert
)

from .event_debugging_inspector import (
    EventDebuggingInspector,
    InspectionLevel,
    DebugTrace,
    InspectionReport
)

from .event_routing_coordinator import (
    EventRoutingCoordinator,
    RoutingStrategy,
    ServiceHealth,
    RoutingRule,
    ServiceEndpoint,
    RoutingDecision,
    RoutingMetrics
)

from .event_lifecycle_manager import (
    EventLifecycleManager,
    EventState,
    LifecycleAction,
    EventLifecycle,
    LifecycleRule
)

from .event_compression_optimizer import (
    EventCompressionOptimizer,
    CompressionAlgorithm,
    CompressionLevel,
    CompressionResult,
    CompressionStrategy
)

# Export all classes for maximum accessibility
__all__ = [
    # Core monitoring
    'MetricsCollector',
    
    # Event Serialization Engine
    'EventSerializationEngine',
    'SerializationFormat',
    'CompressionAlgorithm', 
    'CompressionConfig',
    'SerializedEvent',
    'SerializationMetrics',
    
    # Event Validation Framework
    'EventValidationFramework',
    'ValidationContext',
    'EventValidationResult',
    'BusinessValidationResult',
    'ValidationSeverity',
    'ValidationLayer',
    'BusinessRuleViolation',
    
    # Event Transformation Pipeline
    'EventTransformationPipeline',
    'TransformationContext',
    'TransformedEvent',
    'TransformationType',
    'TransformationPriority',
    'TransformationRegistry',
    'BusinessAnalysis',
    'SchemaMapper',
    'BaseTransformation',
    
    # Performance Optimization Toolkit
    'PerformanceOptimizationToolkit',
    'OptimizationLevel',
    'ResourceLimits',
    'CacheConfig',
    'PerformanceMetrics',
    'OptimizationResult',
    
    # Event Correlation Analyzer
    'EventCorrelationAnalyzer',
    'CorrelationType',
    'CorrelationRule',
    'EventCorrelation',
    'CorrelationInsight',
    
    # Business Metrics Aggregator
    'BusinessMetricsAggregator',
    'MetricType',
    'AggregationPeriod',
    'MetricDefinition',
    'MetricValue',
    'AggregatedMetric',
    'BusinessAlert',
    
    # Event Debugging Inspector
    'EventDebuggingInspector',
    'InspectionLevel',
    'DebugTrace',
    'InspectionReport',
    
    # Event Routing Coordinator
    'EventRoutingCoordinator',
    'RoutingStrategy',
    'ServiceHealth',
    'RoutingRule',
    'ServiceEndpoint',
    'RoutingDecision',
    'RoutingMetrics',
    
    # Event Lifecycle Manager
    'EventLifecycleManager',
    'EventState',
    'LifecycleAction',
    'EventLifecycle',
    'LifecycleRule',
    
    # Event Compression Optimizer
    'EventCompressionOptimizer',
    'CompressionLevel',
    'CompressionResult',
    'CompressionStrategy'
]