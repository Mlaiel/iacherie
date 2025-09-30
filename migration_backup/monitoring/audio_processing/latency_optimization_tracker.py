"""
Ainflue Platform - Latency Optimization Tracker
===============================================

Advanced tracking and optimization of latency across the entire audio
processing pipeline, ensuring real-time performance requirements are met
for streaming and interactive applications.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class LatencyStage(Enum):
    """Audio processing pipeline stages for latency tracking."""
    NETWORK_INGRESS = "network_ingress"
    INPUT_VALIDATION = "input_validation"
    FORMAT_DETECTION = "format_detection"
    AUDIO_DECODE = "audio_decode"
    SOURCE_SEPARATION = "source_separation"
    EFFECT_PROCESSING = "effect_processing"
    LOUDNESS_NORMALIZATION = "loudness_normalization"
    FORMAT_CONVERSION = "format_conversion"
    AUDIO_ENCODE = "audio_encode"
    METADATA_PROCESSING = "metadata_processing"
    QUALITY_ANALYSIS = "quality_analysis"
    NETWORK_EGRESS = "network_egress"
    TOTAL_PIPELINE = "total_pipeline"

class LatencyCategory(Enum):
    """Latency performance categories."""
    EXCELLENT = "excellent"      # < 50ms
    GOOD = "good"               # 50-100ms
    ACCEPTABLE = "acceptable"   # 100-200ms
    POOR = "poor"               # 200-500ms
    CRITICAL = "critical"       # > 500ms

class OptimizationStrategy(Enum):
    """Latency optimization strategies."""
    PARALLEL_PROCESSING = "parallel_processing"
    CACHING = "caching"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    HARDWARE_ACCELERATION = "hardware_acceleration"
    NETWORK_OPTIMIZATION = "network_optimization"
    BUFFER_OPTIMIZATION = "buffer_optimization"
    THREAD_POOLING = "thread_pooling"
    MEMORY_OPTIMIZATION = "memory_optimization"

@dataclass
class LatencyMeasurement:
    """Individual latency measurement."""
    measurement_id: str
    audio_file_id: str
    stage: LatencyStage
    latency_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    queue_wait_time_ms: float
    processing_time_ms: float
    throughput_mbps: float
    optimization_applied: Optional[OptimizationStrategy]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LatencyProfile:
    """Complete latency profile for an audio processing operation."""
    profile_id: str
    audio_file_id: str
    file_size_mb: float
    audio_duration_seconds: float
    measurements: List[LatencyMeasurement]
    total_latency_ms: float
    latency_category: LatencyCategory
    bottleneck_stage: Optional[LatencyStage]
    optimization_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class LatencyOptimizationTracker:
    """
    Enterprise latency optimization tracking system.
    
    Features:
    - Real-time latency monitoring across all pipeline stages
    - Bottleneck identification and analysis
    - Automatic optimization strategy recommendations
    - Performance trend analysis and forecasting
    - SLA compliance monitoring
    - Resource utilization correlation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.latency_profiles: deque = deque(maxlen=10000)
        self.stage_history: Dict[LatencyStage, deque] = {
            stage: deque(maxlen=1000) for stage in LatencyStage
        }
        self.optimization_history: List[Dict[str, Any]] = []
        self._initialize_thresholds()
        self._initialize_optimization_engine()
        
        logger.info("Latency Optimization Tracker initialized")
    
    def _initialize_thresholds(self):
        """Initialize latency thresholds and targets."""
        self.thresholds = {
            # Stage-specific latency targets (ms)
            'stage_targets': {
                LatencyStage.NETWORK_INGRESS: 20,
                LatencyStage.INPUT_VALIDATION: 5,
                LatencyStage.FORMAT_DETECTION: 10,
                LatencyStage.AUDIO_DECODE: 50,
                LatencyStage.SOURCE_SEPARATION: 200,
                LatencyStage.EFFECT_PROCESSING: 100,
                LatencyStage.LOUDNESS_NORMALIZATION: 50,
                LatencyStage.FORMAT_CONVERSION: 100,
                LatencyStage.AUDIO_ENCODE: 80,
                LatencyStage.METADATA_PROCESSING: 10,
                LatencyStage.QUALITY_ANALYSIS: 30,
                LatencyStage.NETWORK_EGRESS: 20,
                LatencyStage.TOTAL_PIPELINE: 500
            },
            # Overall latency categories (ms)
            'categories': {
                LatencyCategory.EXCELLENT: 50,
                LatencyCategory.GOOD: 100,
                LatencyCategory.ACCEPTABLE: 200,
                LatencyCategory.POOR: 500
            },
            # SLA requirements
            'sla_targets': {
                'p95_latency_ms': 200,
                'p99_latency_ms': 500,
                'average_latency_ms': 100,
                'timeout_threshold_ms': 1000
            }
        }
    
    def _initialize_optimization_engine(self):
        """Initialize the optimization recommendation engine."""
        self.optimization_rules = {
            LatencyStage.SOURCE_SEPARATION: {
                'high_latency_threshold': 300,
                'strategies': [
                    OptimizationStrategy.PARALLEL_PROCESSING,
                    OptimizationStrategy.HARDWARE_ACCELERATION,
                    OptimizationStrategy.ALGORITHM_OPTIMIZATION
                ]
            },
            LatencyStage.FORMAT_CONVERSION: {
                'high_latency_threshold': 150,
                'strategies': [
                    OptimizationStrategy.CACHING,
                    OptimizationStrategy.HARDWARE_ACCELERATION,
                    OptimizationStrategy.BUFFER_OPTIMIZATION
                ]
            },
            LatencyStage.NETWORK_INGRESS: {
                'high_latency_threshold': 50,
                'strategies': [
                    OptimizationStrategy.NETWORK_OPTIMIZATION,
                    OptimizationStrategy.CACHING,
                    OptimizationStrategy.BUFFER_OPTIMIZATION
                ]
            },
            LatencyStage.NETWORK_EGRESS: {
                'high_latency_threshold': 50,
                'strategies': [
                    OptimizationStrategy.NETWORK_OPTIMIZATION,
                    OptimizationStrategy.BUFFER_OPTIMIZATION
                ]
            }
        }
    
    async def start_latency_tracking(self, audio_file_id: str, 
                                   file_size_mb: float,
                                   audio_duration_seconds: float) -> str:
        """Start latency tracking for an audio processing operation."""
        profile_id = str(uuid.uuid4())
        
        # Initialize tracking state
        tracking_state = {
            'profile_id': profile_id,
            'audio_file_id': audio_file_id,
            'file_size_mb': file_size_mb,
            'audio_duration_seconds': audio_duration_seconds,
            'measurements': [],
            'start_time': time.time(),
            'stage_start_times': {}
        }
        
        # Store tracking state (in production, this would use proper state management)
        if not hasattr(self, '_tracking_states'):
            self._tracking_states = {}
        self._tracking_states[profile_id] = tracking_state
        
        logger.info(f"Started latency tracking: {profile_id} for audio {audio_file_id}")
        return profile_id
    
    async def record_stage_latency(self, profile_id: str, stage: LatencyStage,
                                 start_time: float, end_time: float,
                                 cpu_usage: float = 0.0, memory_usage_mb: float = 0.0,
                                 queue_wait_time_ms: float = 0.0,
                                 throughput_mbps: float = 0.0,
                                 optimization_applied: Optional[OptimizationStrategy] = None) -> str:
        """Record latency measurement for a specific stage."""
        if not hasattr(self, '_tracking_states') or profile_id not in self._tracking_states:
            logger.error(f"No tracking state found for profile {profile_id}")
            return ""
        
        tracking_state = self._tracking_states[profile_id]
        measurement_id = str(uuid.uuid4())
        
        latency_ms = (end_time - start_time) * 1000
        processing_time_ms = latency_ms - queue_wait_time_ms
        
        measurement = LatencyMeasurement(
            measurement_id=measurement_id,
            audio_file_id=tracking_state['audio_file_id'],
            stage=stage,
            latency_ms=latency_ms,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            queue_wait_time_ms=queue_wait_time_ms,
            processing_time_ms=processing_time_ms,
            throughput_mbps=throughput_mbps,
            optimization_applied=optimization_applied
        )
        
        tracking_state['measurements'].append(measurement)
        self.stage_history[stage].append(measurement)
        
        # Check for performance issues
        await self._check_stage_performance(measurement)
        
        logger.debug(f"Recorded stage latency: {stage.value} = {latency_ms:.1f}ms")
        return measurement_id
    
    async def complete_latency_tracking(self, profile_id: str) -> Dict[str, Any]:
        """Complete latency tracking and generate optimization recommendations."""
        if not hasattr(self, '_tracking_states') or profile_id not in self._tracking_states:
            logger.error(f"No tracking state found for profile {profile_id}")
            return {}
        
        tracking_state = self._tracking_states[profile_id]
        end_time = time.time()
        total_latency_ms = (end_time - tracking_state['start_time']) * 1000
        
        # Analyze latency profile
        latency_category = self._categorize_latency(total_latency_ms)
        bottleneck_stage = self._identify_bottleneck(tracking_state['measurements'])
        optimization_recommendations = await self._generate_optimization_recommendations(
            tracking_state['measurements'], bottleneck_stage
        )
        
        # Create complete latency profile
        profile = LatencyProfile(
            profile_id=profile_id,
            audio_file_id=tracking_state['audio_file_id'],
            file_size_mb=tracking_state['file_size_mb'],
            audio_duration_seconds=tracking_state['audio_duration_seconds'],
            measurements=tracking_state['measurements'],
            total_latency_ms=total_latency_ms,
            latency_category=latency_category,
            bottleneck_stage=bottleneck_stage,
            optimization_recommendations=optimization_recommendations
        )
        
        self.latency_profiles.append(profile)
        
        # Clean up tracking state
        del self._tracking_states[profile_id]
        
        logger.info(f"Completed latency tracking: {profile_id} "
                   f"(total={total_latency_ms:.1f}ms, category={latency_category.value})")
        
        return {
            'profile_id': profile_id,
            'total_latency_ms': total_latency_ms,
            'latency_category': latency_category.value,
            'bottleneck_stage': bottleneck_stage.value if bottleneck_stage else None,
            'optimization_recommendations': optimization_recommendations
        }
    
    def _categorize_latency(self, total_latency_ms: float) -> LatencyCategory:
        """Categorize overall latency performance."""
        if total_latency_ms <= self.thresholds['categories'][LatencyCategory.EXCELLENT]:
            return LatencyCategory.EXCELLENT
        elif total_latency_ms <= self.thresholds['categories'][LatencyCategory.GOOD]:
            return LatencyCategory.GOOD
        elif total_latency_ms <= self.thresholds['categories'][LatencyCategory.ACCEPTABLE]:
            return LatencyCategory.ACCEPTABLE
        elif total_latency_ms <= self.thresholds['categories'][LatencyCategory.POOR]:
            return LatencyCategory.POOR
        else:
            return LatencyCategory.CRITICAL
    
    def _identify_bottleneck(self, measurements: List[LatencyMeasurement]) -> Optional[LatencyStage]:
        """Identify the stage with the highest latency."""
        if not measurements:
            return None
        
        # Find measurement with highest latency
        bottleneck_measurement = max(measurements, key=lambda m: m.latency_ms)
        return bottleneck_measurement.stage
    
    async def _generate_optimization_recommendations(self, measurements: List[LatencyMeasurement],
                                                   bottleneck_stage: Optional[LatencyStage]) -> List[str]:
        """Generate optimization recommendations based on performance analysis."""
        recommendations = []
        
        if bottleneck_stage and bottleneck_stage in self.optimization_rules:
            rule = self.optimization_rules[bottleneck_stage]
            bottleneck_measurement = next(
                (m for m in measurements if m.stage == bottleneck_stage), None
            )
            
            if (bottleneck_measurement and 
                bottleneck_measurement.latency_ms > rule['high_latency_threshold']):
                
                for strategy in rule['strategies']:
                    recommendations.append(
                        f"Apply {strategy.value} to {bottleneck_stage.value} stage"
                    )
        
        # General recommendations based on overall performance
        total_latency = sum(m.latency_ms for m in measurements)
        if total_latency > self.thresholds['sla_targets']['p95_latency_ms']:
            recommendations.append("Consider parallel processing for multiple stages")
            recommendations.append("Implement request batching for better throughput")
        
        # Resource-based recommendations
        high_cpu_measurements = [m for m in measurements if m.cpu_usage_percent > 80]
        if high_cpu_measurements:
            recommendations.append("Optimize CPU-intensive algorithms or add CPU resources")
        
        high_memory_measurements = [m for m in measurements if m.memory_usage_mb > 1000]
        if high_memory_measurements:
            recommendations.append("Implement memory optimization or increase available memory")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _check_stage_performance(self, measurement: LatencyMeasurement):
        """Check individual stage performance against thresholds."""
        stage_target = self.thresholds['stage_targets'].get(measurement.stage)
        
        if stage_target and measurement.latency_ms > stage_target * 2:
            logger.warning(f"Critical latency in {measurement.stage.value}: "
                          f"{measurement.latency_ms:.1f}ms (target: {stage_target}ms)")
        elif stage_target and measurement.latency_ms > stage_target:
            logger.info(f"High latency in {measurement.stage.value}: "
                       f"{measurement.latency_ms:.1f}ms (target: {stage_target}ms)")
    
    def get_latency_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive latency statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_profiles = [
            profile for profile in self.latency_profiles
            if profile.timestamp >= cutoff_time
        ]
        
        if not recent_profiles:
            return {"message": f"No latency data in last {hours} hours"}
        
        # Overall statistics
        total_latencies = [p.total_latency_ms for p in recent_profiles]
        avg_latency = statistics.mean(total_latencies)
        p95_latency = statistics.quantiles(total_latencies, n=20)[18] if len(total_latencies) >= 20 else max(total_latencies)
        p99_latency = statistics.quantiles(total_latencies, n=100)[98] if len(total_latencies) >= 100 else max(total_latencies)
        
        # Category distribution
        category_counts = {}
        for category in LatencyCategory:
            category_counts[category.value] = len([
                p for p in recent_profiles if p.latency_category == category
            ])
        
        # Stage-specific statistics
        stage_stats = {}
        for stage in LatencyStage:
            if stage == LatencyStage.TOTAL_PIPELINE:
                continue
                
            stage_measurements = []
            for profile in recent_profiles:
                stage_measurement = next(
                    (m for m in profile.measurements if m.stage == stage), None
                )
                if stage_measurement:
                    stage_measurements.append(stage_measurement.latency_ms)
            
            if stage_measurements:
                stage_stats[stage.value] = {
                    'avg_latency_ms': statistics.mean(stage_measurements),
                    'max_latency_ms': max(stage_measurements),
                    'min_latency_ms': min(stage_measurements),
                    'measurement_count': len(stage_measurements),
                    'target_ms': self.thresholds['stage_targets'].get(stage, 0)
                }
        
        # Bottleneck analysis
        bottleneck_counts = {}
        for profile in recent_profiles:
            if profile.bottleneck_stage:
                stage_name = profile.bottleneck_stage.value
                bottleneck_counts[stage_name] = bottleneck_counts.get(stage_name, 0) + 1
        
        # SLA compliance
        sla_compliance = {
            'p95_compliant': p95_latency <= self.thresholds['sla_targets']['p95_latency_ms'],
            'p99_compliant': p99_latency <= self.thresholds['sla_targets']['p99_latency_ms'],
            'avg_compliant': avg_latency <= self.thresholds['sla_targets']['average_latency_ms'],
            'p95_actual_ms': p95_latency,
            'p99_actual_ms': p99_latency,
            'avg_actual_ms': avg_latency
        }
        
        return {
            'period_hours': hours,
            'total_operations': len(recent_profiles),
            'latency_statistics': {
                'average_ms': avg_latency,
                'p95_ms': p95_latency,
                'p99_ms': p99_latency,
                'min_ms': min(total_latencies),
                'max_ms': max(total_latencies)
            },
            'category_distribution': category_counts,
            'stage_performance': stage_stats,
            'bottleneck_analysis': bottleneck_counts,
            'sla_compliance': sla_compliance
        }
    
    def get_optimization_opportunities(self) -> Dict[str, Any]:
        """Identify optimization opportunities across the system."""
        if not self.latency_profiles:
            return {"message": "No latency data available for analysis"}
        
        # Analyze recent profiles for patterns
        recent_profiles = list(self.latency_profiles)[-1000:]  # Last 1000 operations
        
        # Find consistently slow stages
        stage_performance = defaultdict(list)
        for profile in recent_profiles:
            for measurement in profile.measurements:
                stage_performance[measurement.stage].append(measurement.latency_ms)
        
        slow_stages = []
        for stage, latencies in stage_performance.items():
            if len(latencies) >= 10:  # Enough data points
                avg_latency = statistics.mean(latencies)
                target_latency = self.thresholds['stage_targets'].get(stage, 0)
                
                if target_latency > 0 and avg_latency > target_latency * 1.5:
                    slow_stages.append({
                        'stage': stage.value,
                        'avg_latency_ms': avg_latency,
                        'target_latency_ms': target_latency,
                        'performance_ratio': avg_latency / target_latency,
                        'sample_count': len(latencies)
                    })
        
        # Find optimization strategies that have been effective
        effective_optimizations = []
        for profile in recent_profiles:
            optimized_measurements = [
                m for m in profile.measurements 
                if m.optimization_applied is not None
            ]
            
            for measurement in optimized_measurements:
                # Compare with baseline performance for same stage
                baseline_measurements = [
                    m for m in stage_performance[measurement.stage]
                    if m != measurement.latency_ms  # Exclude current measurement
                ]
                
                if baseline_measurements:
                    baseline_avg = statistics.mean(baseline_measurements)
                    if measurement.latency_ms < baseline_avg * 0.8:  # 20% improvement
                        effective_optimizations.append({
                            'strategy': measurement.optimization_applied.value,
                            'stage': measurement.stage.value,
                            'improvement_percent': (1 - measurement.latency_ms / baseline_avg) * 100
                        })
        
        return {
            'slow_stages': sorted(slow_stages, key=lambda x: x['performance_ratio'], reverse=True),
            'effective_optimizations': effective_optimizations,
            'recommendations': self._generate_system_wide_recommendations(slow_stages),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_system_wide_recommendations(self, slow_stages: List[Dict[str, Any]]) -> List[str]:
        """Generate system-wide optimization recommendations."""
        recommendations = []
        
        if len(slow_stages) >= 3:
            recommendations.append("Consider system-wide performance optimization")
            recommendations.append("Review resource allocation and scaling policies")
        
        # Check for specific patterns
        cpu_intensive_stages = [
            LatencyStage.SOURCE_SEPARATION, 
            LatencyStage.EFFECT_PROCESSING,
            LatencyStage.FORMAT_CONVERSION
        ]
        
        slow_cpu_stages = [
            s for s in slow_stages 
            if any(stage.value == s['stage'] for stage in cpu_intensive_stages)
        ]
        
        if len(slow_cpu_stages) >= 2:
            recommendations.append("Consider CPU optimization or hardware acceleration")
        
        network_stages = [LatencyStage.NETWORK_INGRESS, LatencyStage.NETWORK_EGRESS]
        slow_network_stages = [
            s for s in slow_stages
            if any(stage.value == s['stage'] for stage in network_stages)
        ]
        
        if slow_network_stages:
            recommendations.append("Investigate network optimization opportunities")
        
        return recommendations

# Global latency optimization tracker instance
latency_optimization_tracker = LatencyOptimizationTracker()

# Export main components
__all__ = [
    'LatencyOptimizationTracker',
    'LatencyMeasurement',
    'LatencyProfile',
    'LatencyStage',
    'LatencyCategory',
    'OptimizationStrategy',
    'latency_optimization_tracker'
]