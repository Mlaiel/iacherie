"""Intelligent Streaming Optimizer - AI-powered Streaming Performance Optimization
============================================================================

Enterprise-grade intelligent streaming optimization engine providing automated
performance tuning, adaptive quality control, resource optimization, and
predictive streaming enhancements based on AI and machine learning.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/intelligent_streaming_optimizer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

BUSINESS LOGIC INTEGRATION:
Performance Analysis → AI Optimization → Adaptive Control → Predictive Enhancement
"""

import asyncio
import json
import uuid
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class OptimizationType(str, Enum):
    """Types of streaming optimizations."""
    QUALITY_OPTIMIZATION = "quality_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    ENCODING_OPTIMIZATION = "encoding_optimization"
    ADAPTIVE_BITRATE = "adaptive_bitrate"
    LATENCY_OPTIMIZATION = "latency_optimization"
    THROUGHPUT_OPTIMIZATION = "throughput_optimization"


class OptimizationStrategy(str, Enum):
    """Optimization strategies."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"
    REAL_TIME = "real_time"
    BATCH = "batch"


class PerformanceMetric(str, Enum):
    """Performance metrics for optimization."""
    BITRATE = "bitrate"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    QUALITY_SCORE = "quality_score"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_UTILIZATION = "network_utilization"
    FRAME_RATE = "frame_rate"
    RESOLUTION = "resolution"
    COMPRESSION_RATIO = "compression_ratio"


class OptimizationMode(str, Enum):
    """Optimization execution modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONTINUOUS = "continuous"


@dataclass
class OptimizationConfig:
    """Configuration for streaming optimization."""
    optimization_type: OptimizationType
    strategy: OptimizationStrategy
    mode: OptimizationMode
    target_metrics: Dict[PerformanceMetric, float] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    enable_adaptive: bool = True
    enable_predictive: bool = True
    optimization_interval: int = 30  # seconds
    performance_threshold: float = 0.8
    quality_threshold: float = 0.85


@dataclass
class PerformanceProfile:
    """Performance profile for optimization analysis."""
    profile_id: str
    session_id: str
    current_metrics: Dict[PerformanceMetric, float]
    historical_metrics: Dict[PerformanceMetric, List[float]]
    performance_score: float
    bottlenecks: List[str]
    optimization_opportunities: Dict[str, float]
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    prediction_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OptimizationResult:
    """Result of streaming optimization operation."""
    optimization_id: str
    session_id: str
    optimization_type: OptimizationType
    strategy_used: OptimizationStrategy
    performance_before: Dict[PerformanceMetric, float]
    performance_after: Dict[PerformanceMetric, float]
    improvement_percentage: Dict[PerformanceMetric, float]
    optimization_actions: List[str]
    success_score: float
    execution_time: float
    resource_impact: Dict[str, Any] = field(default_factory=dict)
    side_effects: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AdaptiveSettings:
    """Adaptive streaming settings."""
    enable_quality_adaptation: bool = True
    enable_bitrate_adaptation: bool = True
    enable_resolution_adaptation: bool = True
    adaptation_sensitivity: float = 0.7
    adaptation_speed: str = "medium"  # slow, medium, fast
    quality_levels: List[str] = field(default_factory=lambda: ["low", "medium", "high", "ultra"])
    bitrate_levels: List[int] = field(default_factory=lambda: [500, 1000, 2000, 4000])  # kbps
    resolution_levels: List[str] = field(default_factory=lambda: ["480p", "720p", "1080p", "1440p"])


@dataclass
class PredictiveInsight:
    """Predictive insights for optimization."""
    insight_id: str
    prediction_type: str
    predicted_metric: PerformanceMetric
    current_value: float
    predicted_value: float
    confidence_score: float
    time_horizon: int  # minutes
    triggers: List[str]
    recommended_actions: List[str]
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StreamingOptimizationRecord(Base):
    """Database model for streaming optimization records."""
    __tablename__ = "streaming_optimizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    optimization_type = Column(String(50), nullable=False)
    strategy_used = Column(String(30), nullable=False)
    performance_before = Column(JSON, nullable=False)
    performance_after = Column(JSON, nullable=False)
    improvement_metrics = Column(JSON)
    optimization_actions = Column(JSON)
    success_score = Column(Float, default=0.0)
    execution_time = Column(Float, default=0.0)
    resource_impact = Column(JSON)
    recommendations = Column(JSON)
    config_used = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class PerformanceProfileRecord(Base):
    """Database model for performance profiles."""
    __tablename__ = "performance_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    current_metrics = Column(JSON, nullable=False)
    historical_metrics = Column(JSON)
    performance_score = Column(Float, nullable=False)
    bottlenecks = Column(JSON)
    optimization_opportunities = Column(JSON)
    trend_analysis = Column(JSON)
    prediction_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class IntelligentStreamingOptimizer:
    """Enterprise intelligent streaming optimizer for automated performance enhancement."""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.is_running = False
        self.optimization_queue = asyncio.Queue()
        self.active_optimizations = {}
        self.performance_profiles = {}
        self.optimization_history = {}
        self.predictive_models = {}
        
    async def start_optimizer(self):
        """Start the intelligent streaming optimizer."""
        try:
            self.is_running = True
            
            # Initialize optimization components
            await self._initialize_optimization_engine()
            
            # Start background optimization tasks
            asyncio.create_task(self._optimization_worker())
            asyncio.create_task(self._performance_monitor())
            asyncio.create_task(self._adaptive_controller())
            asyncio.create_task(self._predictive_analyzer())
            
            logger.info("Intelligent Streaming Optimizer started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start intelligent streaming optimizer: {e}")
            raise
    
    async def stop_optimizer(self):
        """Stop the intelligent streaming optimizer."""
        try:
            self.is_running = False
            
            # Cancel active optimizations
            for optimization in self.active_optimizations.values():
                if hasattr(optimization, 'cancel'):
                    optimization.cancel()
            
            logger.info("Intelligent Streaming Optimizer stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop intelligent streaming optimizer: {e}")
    
    async def optimize_streaming_session(
        self, 
        session_id: str, 
        config: OptimizationConfig,
        current_metrics: Dict[PerformanceMetric, float]
    ) -> OptimizationResult:
        """Optimize streaming session performance."""
        try:
            optimization_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Create performance profile
            profile = await self._create_performance_profile(session_id, current_metrics)
            
            # Analyze optimization opportunities
            optimization_plan = await self._analyze_optimization_opportunities(profile, config)
            
            # Execute optimization strategy
            optimization_actions = await self._execute_optimization_strategy(
                session_id, optimization_plan, config
            )
            
            # Measure performance after optimization
            optimized_metrics = await self._measure_performance_metrics(session_id)
            
            # Calculate improvement
            improvement = await self._calculate_improvement_metrics(
                current_metrics, optimized_metrics
            )
            
            # Calculate success score
            success_score = await self._calculate_optimization_success(improvement, config)
            
            # Create optimization result
            result = OptimizationResult(
                optimization_id=optimization_id,
                session_id=session_id,
                optimization_type=config.optimization_type,
                strategy_used=config.strategy,
                performance_before={metric: value for metric, value in current_metrics.items()},
                performance_after={metric: value for metric, value in optimized_metrics.items()},
                improvement_percentage=improvement,
                optimization_actions=optimization_actions,
                success_score=success_score,
                execution_time=(datetime.now() - start_time).total_seconds(),
                recommendations=await self._generate_optimization_recommendations(profile, result)
            )
            
            # Save optimization record
            await self._save_optimization_record(result, config)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize streaming session: {e}")
            raise
    
    async def enable_adaptive_optimization(
        self, 
        session_id: str, 
        adaptive_config: AdaptiveSettings
    ) -> bool:
        """Enable adaptive optimization for streaming session."""
        try:
            # Configure adaptive settings
            adaptive_data = {
                'session_id': session_id,
                'config': asdict(adaptive_config),
                'enabled': True,
                'last_adaptation': datetime.now(timezone.utc).isoformat(),
                'adaptation_count': 0
            }
            
            # Store adaptive configuration
            await self.redis.setex(
                f"streaming:adaptive:{session_id}",
                3600,  # 1 hour
                json.dumps(adaptive_data)
            )
            
            # Start adaptive monitoring for this session
            asyncio.create_task(self._monitor_adaptive_session(session_id, adaptive_config))
            
            logger.info(f"Adaptive optimization enabled for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable adaptive optimization: {e}")
            return False
    
    async def generate_predictive_insights(
        self, 
        session_id: str, 
        time_horizon_minutes: int = 30
    ) -> List[PredictiveInsight]:
        """Generate predictive insights for streaming optimization."""
        try:
            # Get historical performance data
            historical_data = await self._get_historical_performance_data(session_id)
            
            insights = []
            
            # Generate latency prediction
            latency_insight = await self._predict_latency_trends(
                historical_data, time_horizon_minutes
            )
            if latency_insight:
                insights.append(latency_insight)
            
            # Generate quality prediction
            quality_insight = await self._predict_quality_degradation(
                historical_data, time_horizon_minutes
            )
            if quality_insight:
                insights.append(quality_insight)
            
            # Generate resource usage prediction
            resource_insight = await self._predict_resource_bottlenecks(
                historical_data, time_horizon_minutes
            )
            if resource_insight:
                insights.append(resource_insight)
            
            # Generate viewer experience prediction
            experience_insight = await self._predict_viewer_experience(
                historical_data, time_horizon_minutes
            )
            if experience_insight:
                insights.append(experience_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate predictive insights: {e}")
            return []
    
    async def apply_real_time_optimization(
        self, 
        session_id: str, 
        performance_trigger: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply real-time optimization based on performance triggers."""
        try:
            optimization_result = {}
            
            # Analyze performance trigger
            trigger_analysis = await self._analyze_performance_trigger(performance_trigger)
            
            # Determine optimization strategy
            strategy = await self._determine_real_time_strategy(trigger_analysis)
            
            # Apply immediate optimizations
            if strategy == "immediate_quality_adjustment":
                optimization_result = await self._apply_quality_adjustment(session_id, trigger_analysis)
            elif strategy == "network_optimization":
                optimization_result = await self._apply_network_optimization(session_id, trigger_analysis)
            elif strategy == "resource_reallocation":
                optimization_result = await self._apply_resource_reallocation(session_id, trigger_analysis)
            elif strategy == "encoding_optimization":
                optimization_result = await self._apply_encoding_optimization(session_id, trigger_analysis)
            
            # Log optimization application
            logger.info(f"Applied real-time optimization '{strategy}' to session {session_id}")
            
            return {
                'strategy_applied': strategy,
                'trigger_analysis': trigger_analysis,
                'optimization_result': optimization_result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to apply real-time optimization: {e}")
            return {}
    
    async def _create_performance_profile(
        self, 
        session_id: str, 
        current_metrics: Dict[PerformanceMetric, float]
    ) -> PerformanceProfile:
        """Create comprehensive performance profile."""
        try:
            profile_id = str(uuid.uuid4())
            
            # Get historical metrics
            historical_metrics = await self._get_historical_metrics(session_id)
            
            # Calculate performance score
            performance_score = await self._calculate_performance_score(current_metrics)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_performance_bottlenecks(current_metrics)
            
            # Find optimization opportunities
            opportunities = await self._find_optimization_opportunities(
                current_metrics, historical_metrics
            )
            
            # Perform trend analysis
            trend_analysis = await self._analyze_performance_trends(historical_metrics)
            
            # Generate prediction data
            prediction_data = await self._generate_prediction_data(
                current_metrics, historical_metrics
            )
            
            profile = PerformanceProfile(
                profile_id=profile_id,
                session_id=session_id,
                current_metrics=current_metrics,
                historical_metrics=historical_metrics,
                performance_score=performance_score,
                bottlenecks=bottlenecks,
                optimization_opportunities=opportunities,
                trend_analysis=trend_analysis,
                prediction_data=prediction_data
            )
            
            # Cache profile
            self.performance_profiles[session_id] = profile
            
            # Save to database
            await self._save_performance_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create performance profile: {e}")
            raise
    
    async def _analyze_optimization_opportunities(
        self, 
        profile: PerformanceProfile, 
        config: OptimizationConfig
    ) -> Dict[str, Any]:
        """Analyze optimization opportunities based on performance profile."""
        optimization_plan = {
            'priority_optimizations': [],
            'secondary_optimizations': [],
            'predicted_improvements': {},
            'resource_requirements': {},
            'risk_assessment': {}
        }
        
        # Analyze based on bottlenecks
        for bottleneck in profile.bottlenecks:
            if bottleneck == "high_latency":
                optimization_plan['priority_optimizations'].append({
                    'type': 'latency_optimization',
                    'strategy': 'reduce_encoding_complexity',
                    'expected_improvement': 0.25
                })
            elif bottleneck == "low_quality_score":
                optimization_plan['priority_optimizations'].append({
                    'type': 'quality_optimization',
                    'strategy': 'enhance_encoding_parameters',
                    'expected_improvement': 0.20
                })
            elif bottleneck == "high_cpu_usage":
                optimization_plan['priority_optimizations'].append({
                    'type': 'resource_optimization',
                    'strategy': 'enable_hardware_acceleration',
                    'expected_improvement': 0.30
                })
        
        # Analyze optimization opportunities
        for opportunity, potential in profile.optimization_opportunities.items():
            if potential > 0.15:  # Significant opportunity
                optimization_plan['secondary_optimizations'].append({
                    'type': opportunity,
                    'potential_improvement': potential,
                    'implementation_complexity': 'medium'
                })
        
        return optimization_plan
    
    async def _execute_optimization_strategy(
        self, 
        session_id: str, 
        optimization_plan: Dict[str, Any], 
        config: OptimizationConfig
    ) -> List[str]:
        """Execute optimization strategy based on plan."""
        executed_actions = []
        
        try:
            # Execute priority optimizations first
            for optimization in optimization_plan['priority_optimizations']:
                action = await self._execute_optimization_action(
                    session_id, optimization, config
                )
                if action:
                    executed_actions.append(action)
            
            # Execute secondary optimizations if strategy allows
            if config.strategy in [OptimizationStrategy.AGGRESSIVE, OptimizationStrategy.ADAPTIVE]:
                for optimization in optimization_plan['secondary_optimizations']:
                    action = await self._execute_optimization_action(
                        session_id, optimization, config
                    )
                    if action:
                        executed_actions.append(action)
            
            return executed_actions
            
        except Exception as e:
            logger.error(f"Failed to execute optimization strategy: {e}")
            return executed_actions
    
    async def _execute_optimization_action(
        self, 
        session_id: str, 
        optimization: Dict[str, Any], 
        config: OptimizationConfig
    ) -> Optional[str]:
        """Execute individual optimization action."""
        try:
            optimization_type = optimization.get('type')
            strategy = optimization.get('strategy')
            
            if optimization_type == 'latency_optimization':
                return await self._optimize_latency(session_id, strategy)
            elif optimization_type == 'quality_optimization':
                return await self._optimize_quality(session_id, strategy)
            elif optimization_type == 'resource_optimization':
                return await self._optimize_resources(session_id, strategy)
            elif optimization_type == 'network_optimization':
                return await self._optimize_network(session_id, strategy)
            elif optimization_type == 'encoding_optimization':
                return await self._optimize_encoding(session_id, strategy)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to execute optimization action: {e}")
            return None
    
    async def _optimize_latency(self, session_id: str, strategy: str) -> str:
        """Optimize streaming latency."""
        if strategy == "reduce_encoding_complexity":
            # Simulate latency optimization
            await self._update_encoding_settings(session_id, {
                'preset': 'ultrafast',
                'tune': 'zerolatency',
                'profile': 'baseline'
            })
            return "Reduced encoding complexity for lower latency"
        
        elif strategy == "optimize_buffer_settings":
            await self._update_buffer_settings(session_id, {
                'buffer_size': 'small',
                'keyframe_interval': 1
            })
            return "Optimized buffer settings for reduced latency"
        
        return "Applied generic latency optimization"
    
    async def _optimize_quality(self, session_id: str, strategy: str) -> str:
        """Optimize streaming quality."""
        if strategy == "enhance_encoding_parameters":
            await self._update_encoding_settings(session_id, {
                'preset': 'slow',
                'crf': 20,
                'profile': 'high'
            })
            return "Enhanced encoding parameters for better quality"
        
        elif strategy == "increase_bitrate":
            await self._update_bitrate_settings(session_id, {
                'target_bitrate': '4000k',
                'max_bitrate': '6000k'
            })
            return "Increased bitrate for improved quality"
        
        return "Applied generic quality optimization"
    
    async def _optimize_resources(self, session_id: str, strategy: str) -> str:
        """Optimize resource usage."""
        if strategy == "enable_hardware_acceleration":
            await self._enable_hardware_acceleration(session_id)
            return "Enabled hardware acceleration for CPU optimization"
        
        elif strategy == "optimize_memory_usage":
            await self._optimize_memory_settings(session_id)
            return "Optimized memory usage settings"
        
        return "Applied generic resource optimization"
    
    async def _optimize_network(self, session_id: str, strategy: str) -> str:
        """Optimize network performance."""
        if strategy == "adaptive_bitrate":
            await self._enable_adaptive_bitrate(session_id)
            return "Enabled adaptive bitrate streaming"
        
        elif strategy == "optimize_cdn_routing":
            await self._optimize_cdn_routing(session_id)
            return "Optimized CDN routing for better network performance"
        
        return "Applied generic network optimization"
    
    async def _optimize_encoding(self, session_id: str, strategy: str) -> str:
        """Optimize encoding settings."""
        if strategy == "balance_quality_performance":
            await self._balance_encoding_settings(session_id)
            return "Balanced encoding settings for optimal quality/performance ratio"
        
        return "Applied generic encoding optimization"
    
    async def _measure_performance_metrics(self, session_id: str) -> Dict[PerformanceMetric, float]:
        """Measure current performance metrics after optimization."""
        # Simulate performance measurement
        return {
            PerformanceMetric.BITRATE: 3500.0,
            PerformanceMetric.LATENCY: 1.2,
            PerformanceMetric.THROUGHPUT: 95.0,
            PerformanceMetric.QUALITY_SCORE: 0.92,
            PerformanceMetric.CPU_USAGE: 65.0,
            PerformanceMetric.MEMORY_USAGE: 58.0,
            PerformanceMetric.NETWORK_UTILIZATION: 78.0,
            PerformanceMetric.FRAME_RATE: 30.0
        }
    
    async def _calculate_improvement_metrics(
        self, 
        before: Dict[PerformanceMetric, float], 
        after: Dict[PerformanceMetric, float]
    ) -> Dict[PerformanceMetric, float]:
        """Calculate improvement percentages."""
        improvements = {}
        
        for metric in before.keys():
            if metric in after:
                before_value = before[metric]
                after_value = after[metric]
                
                # Calculate improvement (positive is better)
                if metric in [PerformanceMetric.LATENCY, PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE]:
                    # Lower is better for these metrics
                    improvement = (before_value - after_value) / before_value * 100
                else:
                    # Higher is better for these metrics
                    improvement = (after_value - before_value) / before_value * 100
                
                improvements[metric] = improvement
        
        return improvements
    
    async def _calculate_optimization_success(
        self, 
        improvements: Dict[PerformanceMetric, float], 
        config: OptimizationConfig
    ) -> float:
        """Calculate optimization success score."""
        success_scores = []
        
        for metric, improvement in improvements.items():
            if metric in config.target_metrics:
                target = config.target_metrics[metric]
                if improvement >= target:
                    success_scores.append(1.0)
                else:
                    success_scores.append(improvement / target)
            else:
                # General scoring based on improvement
                if improvement > 10:
                    success_scores.append(1.0)
                elif improvement > 5:
                    success_scores.append(0.8)
                elif improvement > 0:
                    success_scores.append(0.6)
                else:
                    success_scores.append(0.2)
        
        return statistics.mean(success_scores) if success_scores else 0.5
    
    async def _generate_optimization_recommendations(
        self, 
        profile: PerformanceProfile, 
        result: OptimizationResult
    ) -> List[str]:
        """Generate recommendations based on optimization results."""
        recommendations = []
        
        # Analyze success and failures
        avg_improvement = statistics.mean(result.improvement_percentage.values())
        
        if avg_improvement < 5:
            recommendations.append("Consider more aggressive optimization strategies")
        
        if result.success_score < 0.7:
            recommendations.append("Review optimization targets and adjust thresholds")
        
        # Specific recommendations based on metrics
        for metric, improvement in result.improvement_percentage.items():
            if improvement < 0:
                if metric == PerformanceMetric.LATENCY:
                    recommendations.append("Latency increased - consider reverting encoding optimizations")
                elif metric == PerformanceMetric.QUALITY_SCORE:
                    recommendations.append("Quality decreased - balance performance vs quality settings")
        
        # Future optimization suggestions
        if profile.performance_score > 0.9:
            recommendations.append("Excellent performance - consider enabling predictive optimizations")
        elif profile.performance_score < 0.6:
            recommendations.append("Poor performance - schedule comprehensive optimization review")
        
        return recommendations
    
    async def _save_optimization_record(self, result: OptimizationResult, config: OptimizationConfig):
        """Save optimization record to database."""
        try:
            record = StreamingOptimizationRecord(
                id=result.optimization_id,
                session_id=result.session_id,
                optimization_type=result.optimization_type.value,
                strategy_used=result.strategy_used.value,
                performance_before={k.value: v for k, v in result.performance_before.items()},
                performance_after={k.value: v for k, v in result.performance_after.items()},
                improvement_metrics={k.value: v for k, v in result.improvement_percentage.items()},
                optimization_actions=result.optimization_actions,
                success_score=result.success_score,
                execution_time=result.execution_time,
                resource_impact=result.resource_impact,
                recommendations=result.recommendations,
                config_used=asdict(config)
            )
            
            self.db.add(record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save optimization record: {e}")
    
    async def _save_performance_profile(self, profile: PerformanceProfile):
        """Save performance profile to database."""
        try:
            record = PerformanceProfileRecord(
                id=profile.profile_id,
                session_id=profile.session_id,
                current_metrics={k.value: v for k, v in profile.current_metrics.items()},
                historical_metrics={k.value: v for k, v in profile.historical_metrics.items()},
                performance_score=profile.performance_score,
                bottlenecks=profile.bottlenecks,
                optimization_opportunities=profile.optimization_opportunities,
                trend_analysis=profile.trend_analysis,
                prediction_data=profile.prediction_data
            )
            
            self.db.add(record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save performance profile: {e}")
    
    # Helper methods for optimization actions
    async def _update_encoding_settings(self, session_id: str, settings: Dict[str, Any]):
        """Update encoding settings for session."""
        await self.redis.hset(f"streaming:encoding:{session_id}", mapping=settings)
    
    async def _update_buffer_settings(self, session_id: str, settings: Dict[str, Any]):
        """Update buffer settings for session."""
        await self.redis.hset(f"streaming:buffer:{session_id}", mapping=settings)
    
    async def _update_bitrate_settings(self, session_id: str, settings: Dict[str, Any]):
        """Update bitrate settings for session."""
        await self.redis.hset(f"streaming:bitrate:{session_id}", mapping=settings)
    
    async def _enable_hardware_acceleration(self, session_id: str):
        """Enable hardware acceleration for session."""
        await self.redis.hset(f"streaming:hardware:{session_id}", "acceleration", "enabled")
    
    async def _optimize_memory_settings(self, session_id: str):
        """Optimize memory settings for session."""
        await self.redis.hset(f"streaming:memory:{session_id}", mapping={
            "buffer_pool_size": "optimized",
            "garbage_collection": "aggressive"
        })
    
    async def _enable_adaptive_bitrate(self, session_id: str):
        """Enable adaptive bitrate streaming."""
        await self.redis.hset(f"streaming:adaptive:{session_id}", "bitrate", "enabled")
    
    async def _optimize_cdn_routing(self, session_id: str):
        """Optimize CDN routing for session."""
        await self.redis.hset(f"streaming:cdn:{session_id}", "routing", "optimized")
    
    async def _balance_encoding_settings(self, session_id: str):
        """Balance encoding settings for optimal performance."""
        await self.redis.hset(f"streaming:encoding:{session_id}", mapping={
            "preset": "medium",
            "crf": "23",
            "tune": "balanced"
        })
    
    # Background task methods
    async def _optimization_worker(self):
        """Background worker for optimization tasks."""
        while self.is_running:
            try:
                # Process optimization queue
                optimization_task = await asyncio.wait_for(
                    self.optimization_queue.get(),
                    timeout=30
                )
                
                # Execute optimization
                await self._process_optimization_task(optimization_task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Optimization worker error: {e}")
                await asyncio.sleep(10)
    
    async def _performance_monitor(self):
        """Monitor performance across all sessions."""
        while self.is_running:
            try:
                # Get active sessions
                active_sessions = await self.redis.keys("streaming:session:*")
                
                for session_key in active_sessions:
                    session_id = session_key.split(":")[-1]
                    
                    # Collect performance metrics
                    metrics = await self._collect_session_metrics(session_id)
                    
                    # Check if optimization is needed
                    if await self._needs_performance_optimization(metrics):
                        await self._queue_optimization_task(session_id, metrics)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _adaptive_controller(self):
        """Control adaptive optimization for sessions."""
        while self.is_running:
            try:
                # Get sessions with adaptive optimization enabled
                adaptive_sessions = await self.redis.keys("streaming:adaptive:*")
                
                for session_key in adaptive_sessions:
                    session_id = session_key.split(":")[-1]
                    
                    # Check if adaptation is needed
                    await self._check_adaptive_optimization(session_id)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Adaptive controller error: {e}")
                await asyncio.sleep(30)
    
    async def _predictive_analyzer(self):
        """Analyze trends and generate predictive insights."""
        while self.is_running:
            try:
                # Generate predictive insights for active sessions
                active_sessions = await self.redis.keys("streaming:session:*")
                
                for session_key in active_sessions:
                    session_id = session_key.split(":")[-1]
                    
                    # Generate insights
                    insights = await self.generate_predictive_insights(session_id)
                    
                    # Apply proactive optimizations if needed
                    for insight in insights:
                        if insight.confidence_score > 0.8:
                            await self._apply_proactive_optimization(session_id, insight)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Predictive analyzer error: {e}")
                await asyncio.sleep(600)
    
    # Utility methods (simplified implementations)
    async def _initialize_optimization_engine(self):
        """Initialize optimization engine components."""
        logger.info("Optimization engine initialized")
    
    async def _get_historical_metrics(self, session_id: str) -> Dict[PerformanceMetric, List[float]]:
        """Get historical performance metrics."""
        # Simulate historical metrics
        return {
            PerformanceMetric.LATENCY: [2.1, 1.8, 1.9, 2.0, 1.7],
            PerformanceMetric.QUALITY_SCORE: [0.82, 0.85, 0.81, 0.88, 0.86],
            PerformanceMetric.CPU_USAGE: [75, 72, 78, 74, 71]
        }
    
    async def _calculate_performance_score(self, metrics: Dict[PerformanceMetric, float]) -> float:
        """Calculate overall performance score."""
        # Simplified performance scoring
        quality_score = metrics.get(PerformanceMetric.QUALITY_SCORE, 0.5) * 0.3
        latency_score = max(0, (3.0 - metrics.get(PerformanceMetric.LATENCY, 3.0)) / 3.0) * 0.3
        cpu_score = max(0, (100 - metrics.get(PerformanceMetric.CPU_USAGE, 100)) / 100) * 0.2
        throughput_score = metrics.get(PerformanceMetric.THROUGHPUT, 50) / 100 * 0.2
        
        return quality_score + latency_score + cpu_score + throughput_score
    
    async def _identify_performance_bottlenecks(self, metrics: Dict[PerformanceMetric, float]) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        if metrics.get(PerformanceMetric.LATENCY, 0) > 2.0:
            bottlenecks.append("high_latency")
        if metrics.get(PerformanceMetric.QUALITY_SCORE, 1.0) < 0.8:
            bottlenecks.append("low_quality_score")
        if metrics.get(PerformanceMetric.CPU_USAGE, 0) > 80:
            bottlenecks.append("high_cpu_usage")
        if metrics.get(PerformanceMetric.MEMORY_USAGE, 0) > 85:
            bottlenecks.append("high_memory_usage")
        
        return bottlenecks
    
    async def _find_optimization_opportunities(
        self, 
        current: Dict[PerformanceMetric, float], 
        historical: Dict[PerformanceMetric, List[float]]
    ) -> Dict[str, float]:
        """Find optimization opportunities."""
        opportunities = {}
        
        # Compare current vs historical averages
        for metric, values in historical.items():
            if values and metric in current:
                avg_historical = statistics.mean(values)
                current_value = current[metric]
                
                if metric == PerformanceMetric.LATENCY:
                    if current_value > avg_historical * 1.2:
                        opportunities["latency_optimization"] = 0.25
                elif metric == PerformanceMetric.QUALITY_SCORE:
                    if current_value < avg_historical * 0.9:
                        opportunities["quality_optimization"] = 0.20
        
        return opportunities


def create_intelligent_streaming_optimizer(
    redis_client: redis.Redis, 
    db_session: Session
) -> IntelligentStreamingOptimizer:
    """Factory function to create Intelligent Streaming Optimizer instance."""
    return IntelligentStreamingOptimizer(redis_client, db_session)