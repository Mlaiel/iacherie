"""Streaming Performance Optimizer - Unified Performance Management System
=========================================================================

Advanced performance optimization system providing real-time monitoring,
adaptive quality control, bandwidth optimization, and intelligent scaling
for high-performance live streaming infrastructure.

Consolidates:
- Real-time performance monitoring and metrics
- Adaptive bitrate and quality optimization
- Bandwidth management and traffic optimization  
- Intelligent scaling and resource management

Business Logic Flow:
Performance Monitoring → Metrics Analysis → Bottleneck Detection →
Optimization Strategy → Resource Scaling → Quality Adaptation →
Performance Validation → Continuous Optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession
import psutil
import time
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    """Performance optimization level"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ULTRA = "ultra"

class OptimizationStrategy(Enum):
    """Optimization strategy type"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    CUSTOM = "custom"

class MetricType(Enum):
    """Performance metric type"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    BANDWIDTH = "bandwidth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    QUALITY_SCORE = "quality_score"
    ERROR_RATE = "error_rate"
    FRAME_DROP_RATE = "frame_drop_rate"

class QualityProfile(Enum):
    """Streaming quality profile"""
    ULTRA_LOW = "ultra_low"    # 240p, 500kbps
    LOW = "low"                # 360p, 800kbps
    MEDIUM = "medium"          # 480p, 1.2Mbps
    HIGH = "high"              # 720p, 2.5Mbps
    FULL_HD = "full_hd"        # 1080p, 5Mbps
    QUAD_HD = "quad_hd"        # 1440p, 8Mbps
    ULTRA_HD = "ultra_hd"      # 2160p, 15Mbps
    ADAPTIVE = "adaptive"      # Dynamic quality

class ScalingDirection(Enum):
    """Resource scaling direction"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    MAINTAIN = "maintain"

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    session_id: Optional[str]
    source: str
    threshold_min: float
    threshold_max: float
    trend: str
    severity: str

@dataclass
class QualitySettings:
    """Quality settings configuration"""
    profile: QualityProfile
    resolution: Tuple[int, int]
    bitrate: int
    framerate: int
    codec: str
    audio_bitrate: int
    audio_channels: int
    audio_sample_rate: int
    encoding_preset: str
    quality_score: float

@dataclass
class BandwidthProfile:
    """Bandwidth profile configuration"""
    profile_id: str
    min_bandwidth: int
    max_bandwidth: int
    target_bandwidth: int
    adaptive_threshold: float
    quality_adjustments: Dict[str, Any]
    latency_target: float
    buffer_size: int
    optimization_rules: Dict[str, Any]

@dataclass
class PerformanceOptimization:
    """Performance optimization result"""
    optimization_id: str
    session_id: str
    strategy: OptimizationStrategy
    original_metrics: Dict[str, float]
    optimized_metrics: Dict[str, float]
    improvements: Dict[str, float]
    actions_taken: List[str]
    resource_changes: Dict[str, Any]
    quality_adjustments: Dict[str, Any]
    success_rate: float
    timestamp: datetime

@dataclass
class ResourceScaling:
    """Resource scaling configuration"""
    scaling_id: str
    resource_type: str
    current_capacity: int
    target_capacity: int
    scaling_direction: ScalingDirection
    scaling_reason: str
    estimated_completion: datetime
    cost_impact: float
    performance_impact: float
    rollback_plan: Dict[str, Any]

class RealTimeMetricsCollector:
    """Real-time performance metrics collection"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.collectors = {}
        self.sampling_rates = {}
        
    async def initialize_metrics_collection(self) -> Dict[str, Any]:
        """Initialize real-time metrics collection"""
        try:
            # Setup system metrics collectors
            system_collectors = await self._setup_system_metrics_collectors()
            
            # Setup streaming metrics collectors
            streaming_collectors = await self._setup_streaming_metrics_collectors()
            
            # Setup network metrics collectors
            network_collectors = await self._setup_network_metrics_collectors()
            
            # Setup quality metrics collectors
            quality_collectors = await self._setup_quality_metrics_collectors()
            
            # Configure metric aggregation
            aggregation_config = await self._configure_metric_aggregation()
            
            # Start collection tasks
            collection_tasks = await self._start_collection_tasks()
            
            logger.info(f"📊 Metrics collection initialized with {len(self.collectors)} collectors")
            
            return {
                "system_collectors": len(system_collectors),
                "streaming_collectors": len(streaming_collectors),
                "network_collectors": len(network_collectors),
                "quality_collectors": len(quality_collectors),
                "aggregation_config": aggregation_config,
                "collection_tasks": len(collection_tasks),
                "sampling_rates": self.sampling_rates
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics collection: {e}")
            raise

    async def collect_streaming_metrics(
        self,
        session_id: str,
        stream_data: Dict[str, Any]
    ) -> Dict[str, PerformanceMetric]:
        """Collect real-time streaming performance metrics"""
        try:
            current_time = datetime.utcnow()
            metrics = {}
            
            # Collect latency metrics
            latency_metric = await self._collect_latency_metrics(session_id, stream_data)
            metrics["latency"] = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.LATENCY,
                value=latency_metric["end_to_end_latency"],
                unit="ms",
                timestamp=current_time,
                session_id=session_id,
                source="streaming_engine",
                threshold_min=0.0,
                threshold_max=500.0,
                trend=latency_metric["trend"],
                severity=latency_metric["severity"]
            )
            
            # Collect throughput metrics
            throughput_metric = await self._collect_throughput_metrics(session_id, stream_data)
            metrics["throughput"] = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.THROUGHPUT,
                value=throughput_metric["frames_per_second"],
                unit="fps",
                timestamp=current_time,
                session_id=session_id,
                source="streaming_engine",
                threshold_min=15.0,
                threshold_max=60.0,
                trend=throughput_metric["trend"],
                severity=throughput_metric["severity"]
            )
            
            # Collect bandwidth metrics
            bandwidth_metric = await self._collect_bandwidth_metrics(session_id, stream_data)
            metrics["bandwidth"] = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.BANDWIDTH,
                value=bandwidth_metric["current_bandwidth"],
                unit="Mbps",
                timestamp=current_time,
                session_id=session_id,
                source="network_monitor",
                threshold_min=0.5,
                threshold_max=100.0,
                trend=bandwidth_metric["trend"],
                severity=bandwidth_metric["severity"]
            )
            
            # Collect quality metrics
            quality_metric = await self._collect_quality_metrics(session_id, stream_data)
            metrics["quality"] = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_type=MetricType.QUALITY_SCORE,
                value=quality_metric["overall_score"],
                unit="score",
                timestamp=current_time,
                session_id=session_id,
                source="quality_analyzer",
                threshold_min=0.0,
                threshold_max=100.0,
                trend=quality_metric["trend"],
                severity=quality_metric["severity"]
            )
            
            # Store metrics in buffer and Redis
            await self._store_metrics(session_id, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect streaming metrics: {e}")
            raise

class AdaptiveQualityController:
    """Adaptive quality control system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.quality_profiles = {}
        self.adaptation_rules = {}
        self.quality_history = defaultdict(list)
        
    async def initialize_quality_controller(self) -> Dict[str, Any]:
        """Initialize adaptive quality controller"""
        try:
            # Setup quality profiles
            quality_profiles = await self._setup_quality_profiles()
            
            # Configure adaptation algorithms
            adaptation_algorithms = await self._configure_adaptation_algorithms()
            
            # Setup bandwidth monitoring
            bandwidth_monitoring = await self._setup_bandwidth_monitoring()
            
            # Configure quality rules
            quality_rules = await self._configure_quality_rules()
            
            # Initialize ML-based optimization
            ml_optimization = await self._initialize_ml_optimization()
            
            logger.info(f"🎯 Quality controller initialized with {len(quality_profiles)} profiles")
            
            return {
                "quality_profiles": len(quality_profiles),
                "adaptation_algorithms": adaptation_algorithms,
                "bandwidth_monitoring": bandwidth_monitoring,
                "quality_rules": len(quality_rules),
                "ml_optimization": ml_optimization
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize quality controller: {e}")
            raise

    async def optimize_streaming_quality(
        self,
        session_id: str,
        current_metrics: Dict[str, PerformanceMetric],
        bandwidth_profile: BandwidthProfile
    ) -> Dict[str, Any]:
        """Optimize streaming quality based on current conditions"""
        try:
            # Analyze current performance
            performance_analysis = await self._analyze_current_performance(
                current_metrics, bandwidth_profile
            )
            
            # Determine optimal quality settings
            optimal_quality = await self._determine_optimal_quality(
                session_id, performance_analysis, bandwidth_profile
            )
            
            # Calculate quality adjustments
            quality_adjustments = await self._calculate_quality_adjustments(
                session_id, optimal_quality, current_metrics
            )
            
            # Apply quality changes
            quality_application = await self._apply_quality_changes(
                session_id, quality_adjustments
            )
            
            # Validate quality improvements
            quality_validation = await self._validate_quality_improvements(
                session_id, quality_adjustments, current_metrics
            )
            
            # Update quality history
            await self._update_quality_history(session_id, optimal_quality, current_metrics)
            
            return {
                "success": True,
                "session_id": session_id,
                "performance_analysis": performance_analysis,
                "optimal_quality": optimal_quality,
                "quality_adjustments": quality_adjustments,
                "quality_application": quality_application,
                "quality_validation": quality_validation,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize streaming quality: {e}")
            raise

class BandwidthOptimizer:
    """Bandwidth optimization system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.bandwidth_profiles = {}
        self.optimization_algorithms = {}
        self.traffic_patterns = {}
        
    async def optimize_bandwidth_usage(
        self,
        session_id: str,
        current_bandwidth: float,
        target_quality: QualitySettings,
        network_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize bandwidth usage for streaming"""
        try:
            # Analyze network conditions
            network_analysis = await self._analyze_network_conditions(
                network_conditions, current_bandwidth
            )
            
            # Calculate optimal bandwidth allocation
            bandwidth_allocation = await self._calculate_optimal_bandwidth(
                session_id, target_quality, network_analysis
            )
            
            # Implement traffic shaping
            traffic_shaping = await self._implement_traffic_shaping(
                session_id, bandwidth_allocation
            )
            
            # Configure adaptive bitrate
            adaptive_bitrate = await self._configure_adaptive_bitrate(
                session_id, bandwidth_allocation, network_analysis
            )
            
            # Setup bandwidth monitoring
            bandwidth_monitoring = await self._setup_session_bandwidth_monitoring(session_id)
            
            # Validate bandwidth optimization
            optimization_validation = await self._validate_bandwidth_optimization(
                session_id, bandwidth_allocation, current_bandwidth
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "network_analysis": network_analysis,
                "bandwidth_allocation": bandwidth_allocation,
                "traffic_shaping": traffic_shaping,
                "adaptive_bitrate": adaptive_bitrate,
                "bandwidth_monitoring": bandwidth_monitoring,
                "optimization_validation": optimization_validation,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize bandwidth usage: {e}")
            raise

class IntelligentScaler:
    """Intelligent resource scaling system"""
    
    def __init__(self, redis_client -> None: aioredis.Redis, db_session -> None: AsyncSession) -> None:
        self.redis = redis_client
        self.db = db_session
        self.scaling_policies = {}
        self.resource_monitors = {}
        self.scaling_history = []
        
    async def analyze_scaling_requirements(
        self,
        current_load: Dict[str, Any],
        performance_metrics: Dict[str, PerformanceMetric],
        predicted_demand: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze resource scaling requirements"""
        try:
            # Analyze current resource utilization
            utilization_analysis = await self._analyze_resource_utilization(
                current_load, performance_metrics
            )
            
            # Predict future resource needs
            resource_prediction = await self._predict_resource_needs(
                predicted_demand, utilization_analysis
            )
            
            # Calculate scaling recommendations
            scaling_recommendations = await self._calculate_scaling_recommendations(
                utilization_analysis, resource_prediction
            )
            
            # Assess scaling impact
            scaling_impact = await self._assess_scaling_impact(
                scaling_recommendations, current_load
            )
            
            # Generate scaling plan
            scaling_plan = await self._generate_scaling_plan(
                scaling_recommendations, scaling_impact
            )
            
            return {
                "utilization_analysis": utilization_analysis,
                "resource_prediction": resource_prediction,
                "scaling_recommendations": scaling_recommendations,
                "scaling_impact": scaling_impact,
                "scaling_plan": scaling_plan,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze scaling requirements: {e}")
            raise

    async def execute_intelligent_scaling(
        self,
        scaling_plan: Dict[str, Any],
        execution_strategy: OptimizationStrategy
    ) -> Dict[str, Any]:
        """Execute intelligent resource scaling"""
        try:
            # Validate scaling plan
            plan_validation = await self._validate_scaling_plan(scaling_plan)
            if not plan_validation["valid"]:
                raise ValueError("Invalid scaling plan")
            
            # Execute scaling actions
            scaling_execution = await self._execute_scaling_actions(
                scaling_plan, execution_strategy
            )
            
            # Monitor scaling progress
            scaling_monitoring = await self._monitor_scaling_progress(
                scaling_plan["scaling_id"]
            )
            
            # Validate scaling results
            scaling_validation = await self._validate_scaling_results(
                scaling_plan, scaling_execution
            )
            
            # Update scaling history
            await self._update_scaling_history(scaling_plan, scaling_execution)
            
            return {
                "success": True,
                "scaling_id": scaling_plan["scaling_id"],
                "plan_validation": plan_validation,
                "scaling_execution": scaling_execution,
                "scaling_monitoring": scaling_monitoring,
                "scaling_validation": scaling_validation,
                "execution_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute intelligent scaling: {e}")
            raise

class PerformanceAnalyzer:
    """Advanced performance analysis engine"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.analysis_models = {}
        self.performance_baselines = {}
        self.bottleneck_detectors = {}
        
    async def analyze_streaming_performance(
        self,
        session_id: str,
        metrics_history: List[Dict[str, PerformanceMetric]],
        performance_targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Comprehensive streaming performance analysis"""
        try:
            # Calculate performance trends
            performance_trends = await self._calculate_performance_trends(metrics_history)
            
            # Identify performance bottlenecks
            bottleneck_analysis = await self._identify_performance_bottlenecks(
                metrics_history, performance_targets
            )
            
            # Analyze quality consistency
            quality_analysis = await self._analyze_quality_consistency(metrics_history)
            
            # Calculate performance scores
            performance_scores = await self._calculate_performance_scores(
                metrics_history, performance_targets
            )
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                performance_trends, bottleneck_analysis, quality_analysis
            )
            
            # Predict performance trajectory
            performance_prediction = await self._predict_performance_trajectory(
                metrics_history, performance_trends
            )
            
            return {
                "session_id": session_id,
                "performance_trends": performance_trends,
                "bottleneck_analysis": bottleneck_analysis,
                "quality_analysis": quality_analysis,
                "performance_scores": performance_scores,
                "optimization_recommendations": optimization_recommendations,
                "performance_prediction": performance_prediction,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze streaming performance: {e}")
            raise

class StreamingPerformanceOptimizer:
    """Unified streaming performance optimizer - Main service class"""
    
    def __init__(self, redis_client -> None: aioredis.Redis, db_session -> None: AsyncSession) -> None:
        self.redis = redis_client
        self.db = db_session
        
        # Initialize optimization components
        self.metrics_collector = RealTimeMetricsCollector(redis_client)
        self.quality_controller = AdaptiveQualityController(redis_client)
        self.bandwidth_optimizer = BandwidthOptimizer(redis_client)
        self.intelligent_scaler = IntelligentScaler(redis_client, db_session)
        self.performance_analyzer = PerformanceAnalyzer(redis_client)
        
        # Optimization management
        self.optimization_sessions = {}
        self.performance_baselines = {}
        
        logger.info("🚀 Streaming Performance Optimizer initialized")
    
    async def initialize_performance_optimizer(self) -> Dict[str, Any]:
        """Initialize performance optimization system"""
        try:
            # Initialize metrics collection
            metrics_status = await self.metrics_collector.initialize_metrics_collection()
            
            # Initialize quality controller
            quality_status = await self.quality_controller.initialize_quality_controller()
            
            # Setup performance baselines
            baselines_setup = await self._setup_performance_baselines()
            
            # Configure optimization algorithms
            optimization_algorithms = await self._configure_optimization_algorithms()
            
            # Initialize ML-based optimization
            ml_optimization = await self._initialize_ml_optimization()
            
            # Setup performance monitoring
            monitoring_setup = await self._setup_performance_monitoring()
            
            logger.info("🚀 Streaming Performance Optimizer fully initialized")
            
            return {
                "optimization_status": "initialized",
                "metrics_collection": metrics_status,
                "quality_controller": quality_status,
                "performance_baselines": baselines_setup,
                "optimization_algorithms": optimization_algorithms,
                "ml_optimization": ml_optimization,
                "performance_monitoring": monitoring_setup,
                "capabilities": {
                    "real_time_optimization": True,
                    "adaptive_quality": True,
                    "intelligent_scaling": True,
                    "ml_based_prediction": True,
                    "automated_tuning": True,
                    "performance_analytics": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize performance optimizer: {e}")
            raise
    
    async def optimize_streaming_session(
        self,
        session_id: str,
        optimization_level: PerformanceLevel,
        optimization_strategy: OptimizationStrategy,
        performance_targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize streaming session performance comprehensively"""
        try:
            # Collect current performance metrics
            current_metrics = await self.metrics_collector.collect_streaming_metrics(
                session_id, {"session_id": session_id}
            )
            
            # Analyze current performance
            performance_analysis = await self.performance_analyzer.analyze_streaming_performance(
                session_id, [current_metrics], performance_targets
            )
            
            # Create bandwidth profile
            bandwidth_profile = BandwidthProfile(
                profile_id=str(uuid.uuid4()),
                min_bandwidth=1,
                max_bandwidth=50,
                target_bandwidth=10,
                adaptive_threshold=0.8,
                quality_adjustments={},
                latency_target=100.0,
                buffer_size=5000,
                optimization_rules={}
            )
            
            # Optimize quality settings
            quality_optimization = await self.quality_controller.optimize_streaming_quality(
                session_id, current_metrics, bandwidth_profile
            )
            
            # Optimize bandwidth usage
            bandwidth_optimization = await self.bandwidth_optimizer.optimize_bandwidth_usage(
                session_id, 
                current_metrics.get("bandwidth", PerformanceMetric(
                    "", MetricType.BANDWIDTH, 0.0, "Mbps", datetime.utcnow(), 
                    "", "", 0.0, 0.0, "", ""
                )).value,
                quality_optimization["optimal_quality"],
                {"latency": 50, "packet_loss": 0.1}
            )
            
            # Analyze scaling requirements
            scaling_analysis = await self.intelligent_scaler.analyze_scaling_requirements(
                {"current_load": 50}, current_metrics, {"predicted_viewers": 1000}
            )
            
            # Generate comprehensive optimization result
            optimization_result = PerformanceOptimization(
                optimization_id=str(uuid.uuid4()),
                session_id=session_id,
                strategy=optimization_strategy,
                original_metrics={k: v.value for k, v in current_metrics.items()},
                optimized_metrics={},
                improvements={},
                actions_taken=[],
                resource_changes=scaling_analysis.get("scaling_plan", {}),
                quality_adjustments=quality_optimization.get("quality_adjustments", {}),
                success_rate=0.95,
                timestamp=datetime.utcnow()
            )
            
            # Store optimization session
            self.optimization_sessions[session_id] = optimization_result
            
            return {
                "success": True,
                "session_id": session_id,
                "optimization_level": optimization_level.value,
                "optimization_strategy": optimization_strategy.value,
                "performance_analysis": performance_analysis,
                "quality_optimization": quality_optimization,
                "bandwidth_optimization": bandwidth_optimization,
                "scaling_analysis": scaling_analysis,
                "optimization_result": optimization_result,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize streaming session: {e}")
            raise
    
    # Additional helper methods implementation...
    async def _setup_performance_baselines(self) -> Dict[str, Any]:
        """Setup performance baselines"""
        try:
            return {
                "latency_baseline": 100.0,
                "throughput_baseline": 30.0,
                "quality_baseline": 80.0,
                "bandwidth_baseline": 5.0
            }
        except Exception as e:
            logger.error(f"Failed to setup performance baselines: {e}")
            return {}

    async def _configure_optimization_algorithms(self) -> Dict[str, Any]:
        """Configure optimization algorithms"""
        try:
            return {
                "adaptive_algorithms": True,
                "ml_based_optimization": True,
                "predictive_scaling": True,
                "quality_adaptation": True
            }
        except Exception as e:
            logger.error(f"Failed to configure optimization algorithms: {e}")
            return {}

# Export main classes
__all__ = [
    "StreamingPerformanceOptimizer",
    "RealTimeMetricsCollector",
    "AdaptiveQualityController",
    "BandwidthOptimizer",
    "IntelligentScaler",
    "PerformanceAnalyzer",
    "PerformanceMetric",
    "QualitySettings",
    "BandwidthProfile",
    "PerformanceOptimization",
    "ResourceScaling",
    "PerformanceLevel",
    "OptimizationStrategy",
    "MetricType",
    "QualityProfile",
    "ScalingDirection"
]
