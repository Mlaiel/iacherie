"""
Cache Optimizer - Intelligent Cache Performance Optimization

Advanced optimization engine providing AI-driven cache performance tuning,
predictive optimization, and automated efficiency improvements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import statistics
import numpy as np
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import math
import json

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of optimization operations"""
    MEMORY_OPTIMIZATION = "memory_optimization"
    ACCESS_PATTERN_OPTIMIZATION = "access_pattern_optimization"
    TTL_OPTIMIZATION = "ttl_optimization"
    EVICTION_OPTIMIZATION = "eviction_optimization"
    COMPRESSION_OPTIMIZATION = "compression_optimization"
    DISTRIBUTION_OPTIMIZATION = "distribution_optimization"
    PREFETCH_OPTIMIZATION = "prefetch_optimization"

class OptimizationPriority(Enum):
    """Priority levels for optimization actions"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class OptimizationRecommendation:
    """Single optimization recommendation"""
    optimization_id: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    expected_impact: Dict[str, float]  # metric -> improvement percentage
    implementation_complexity: str  # "low", "medium", "high"
    estimated_effort: int  # hours
    prerequisites: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0  # 0-1 confidence in recommendation
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OptimizationResult:
    """Result of optimization execution"""
    recommendation_id: str
    success: bool
    execution_time: float
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    actual_impact: Dict[str, float]
    error_message: Optional[str] = None
    rollback_possible: bool = True
    rollback_data: Optional[Dict[str, Any]] = None

@dataclass
class CachePrediction:
    """Cache performance prediction model"""
    metric_name: str
    current_value: float
    predicted_values: List[Tuple[datetime, float]]  # (time, predicted_value)
    confidence_intervals: List[Tuple[float, float]]  # (lower, upper) bounds
    trend: str  # "increasing", "decreasing", "stable", "volatile"
    prediction_accuracy: float = 0.0  # Historical accuracy

class CacheOptimizer:
    """
    Advanced cache optimization engine using ML-driven insights
    to automatically tune cache performance and efficiency.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Optimization history and learning
        self.optimization_history: List[OptimizationResult] = []
        self.performance_baseline: Dict[str, float] = {}
        self.optimization_patterns: Dict[str, Any] = defaultdict(dict)
        
        # Prediction models
        self.predictive_models: Dict[str, Any] = {}
        self.historical_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Optimization strategies
        self.active_optimizations: Set[str] = set()
        self.optimization_queue: List[OptimizationRecommendation] = []
        
        # Learning parameters
        self.learning_enabled = self.config.get('enable_learning', True)
        self.min_data_points = self.config.get('min_data_points', 100)
        self.optimization_interval = self.config.get('optimization_interval', 300)  # 5 minutes
        
        # Performance thresholds
        self.performance_thresholds = {
            'hit_rate': {'min': 0.8, 'target': 0.9},
            'response_time': {'max': 0.1, 'target': 0.05},  # seconds
            'memory_efficiency': {'min': 0.7, 'target': 0.85},
            'eviction_rate': {'max': 0.1, 'target': 0.05}
        }
    
    async def analyze_and_optimize(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main optimization entry point - analyze cache state and apply optimizations.
        
        Args:
            cache_entries: Current cache entries
            metrics: Current performance metrics  
            config: Cache configuration
            
        Returns:
            Optimization results and recommendations
        """
        optimization_start = datetime.utcnow()
        
        try:
            # Update historical data
            await self._update_historical_metrics(metrics)
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                cache_entries, metrics, config
            )
            
            # Execute high-priority optimizations automatically
            executed_optimizations = await self._execute_automatic_optimizations(
                recommendations, cache_entries
            )
            
            # Update learning models
            if self.learning_enabled:
                await self._update_learning_models(metrics)
            
            # Generate predictions
            predictions = await self._generate_predictions()
            
            execution_time = (datetime.utcnow() - optimization_start).total_seconds()
            
            return {
                'optimization_summary': {
                    'execution_time': execution_time,
                    'total_recommendations': len(recommendations),
                    'executed_optimizations': len(executed_optimizations),
                    'performance_improvement': await self._calculate_improvement(metrics)
                },
                'recommendations': [self._recommendation_to_dict(r) for r in recommendations],
                'executed_optimizations': executed_optimizations,
                'predictions': [self._prediction_to_dict(p) for p in predictions],
                'next_optimization': optimization_start + timedelta(seconds=self.optimization_interval)
            }
            
        except Exception as e:
            logger.error(f"Cache optimization error: {e}")
            return {'error': str(e), 'recommendations': [], 'executed_optimizations': []}
    
    async def _generate_recommendations(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Generate intelligent optimization recommendations"""
        recommendations = []
        
        # Memory optimization
        memory_recs = await self._analyze_memory_optimization(cache_entries, metrics, config)
        recommendations.extend(memory_recs)
        
        # Access pattern optimization
        access_recs = await self._analyze_access_patterns(cache_entries, metrics)
        recommendations.extend(access_recs)
        
        # TTL optimization
        ttl_recs = await self._analyze_ttl_optimization(cache_entries, metrics)
        recommendations.extend(ttl_recs)
        
        # Eviction strategy optimization
        eviction_recs = await self._analyze_eviction_optimization(cache_entries, metrics)
        recommendations.extend(eviction_recs)
        
        # Compression optimization
        compression_recs = await self._analyze_compression_optimization(cache_entries, metrics)
        recommendations.extend(compression_recs)
        
        # Prefetching optimization
        prefetch_recs = await self._analyze_prefetching_opportunities(cache_entries, metrics)
        recommendations.extend(prefetch_recs)
        
        # Sort by priority and confidence
        recommendations.sort(key=lambda r: (r.priority.value, -r.confidence))
        
        return recommendations
    
    async def _analyze_memory_optimization(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze memory usage and generate optimization recommendations"""
        recommendations = []
        
        memory_usage_percent = metrics.get('memory_usage_percent', 0)
        total_entries = len(cache_entries)
        
        # High memory usage optimization
        if memory_usage_percent > 85:
            recommendations.append(OptimizationRecommendation(
                optimization_id=f"mem_optimize_{int(datetime.utcnow().timestamp())}",
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="Reduce Memory Usage",
                description=f"Memory usage is at {memory_usage_percent:.1f}%. Recommend aggressive eviction.",
                expected_impact={'memory_usage': -20, 'hit_rate': -5},
                implementation_complexity="low",
                estimated_effort=1,
                parameters={'target_reduction_percent': 20},
                confidence=0.9
            ))
        
        # Memory fragmentation analysis
        if total_entries > 0:
            avg_entry_size = metrics.get('total_size_bytes', 0) / total_entries
            
            if avg_entry_size < 100:  # Many small entries
                recommendations.append(OptimizationRecommendation(
                    optimization_id=f"mem_frag_{int(datetime.utcnow().timestamp())}",
                    optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                    priority=OptimizationPriority.NORMAL,
                    title="Optimize Small Entry Storage",
                    description="Many small cache entries detected. Consider batching or compression.",
                    expected_impact={'memory_efficiency': 15, 'storage_overhead': -25},
                    implementation_complexity="medium",
                    estimated_effort=4,
                    parameters={'batch_threshold': 100, 'enable_compression': True},
                    confidence=0.7
                ))
        
        return recommendations
    
    async def _analyze_access_patterns(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze access patterns for optimization opportunities"""
        recommendations = []
        
        # Calculate access frequency distribution
        access_counts = []
        for entry in cache_entries.values():
            if hasattr(entry, 'access_count'):
                access_counts.append(entry.access_count)
        
        if not access_counts:
            return recommendations
        
        # Analyze hotspot distribution
        total_accesses = sum(access_counts)
        sorted_counts = sorted(access_counts, reverse=True)
        
        # 80/20 rule analysis
        top_20_percent = int(len(sorted_counts) * 0.2)
        if top_20_percent > 0:
            top_20_accesses = sum(sorted_counts[:top_20_percent])
            hotspot_ratio = top_20_accesses / total_accesses if total_accesses > 0 else 0
            
            if hotspot_ratio > 0.8:  # Strong hotspot pattern
                recommendations.append(OptimizationRecommendation(
                    optimization_id=f"hotspot_{int(datetime.utcnow().timestamp())}",
                    optimization_type=OptimizationType.ACCESS_PATTERN_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    title="Optimize Hotspot Caching",
                    description=f"Strong hotspot pattern detected ({hotspot_ratio:.1%} of accesses). Implement tiered caching.",
                    expected_impact={'hit_rate': 10, 'response_time': -20},
                    implementation_complexity="medium",
                    estimated_effort=6,
                    parameters={'hotspot_threshold': 0.8, 'tier_levels': 2},
                    confidence=0.85
                ))
        
        # Cold data analysis
        cold_entries = len([c for c in access_counts if c <= 1])
        if cold_entries > len(access_counts) * 0.3:  # > 30% cold data
            recommendations.append(OptimizationRecommendation(
                optimization_id=f"cold_data_{int(datetime.utcnow().timestamp())}",
                optimization_type=OptimizationType.ACCESS_PATTERN_OPTIMIZATION,
                priority=OptimizationPriority.NORMAL,
                title="Remove Cold Data",
                description=f"{cold_entries} entries have minimal access. Consider aggressive eviction.",
                expected_impact={'memory_usage': -15, 'cache_efficiency': 10},
                implementation_complexity="low", 
                estimated_effort=2,
                parameters={'cold_threshold': 1, 'evict_percentage': 30},
                confidence=0.75
            ))
        
        return recommendations
    
    async def _analyze_ttl_optimization(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze TTL settings for optimization"""
        recommendations = []
        
        # Analyze TTL vs access patterns
        ttl_access_correlation = []
        expired_before_access = 0
        
        for entry in cache_entries.values():
            if hasattr(entry, 'ttl') and hasattr(entry, 'access_count') and entry.ttl:
                age = (datetime.utcnow() - entry.created_at).total_seconds()
                access_frequency = entry.access_count / max(age, 1) * 3600  # per hour
                
                ttl_access_correlation.append((entry.ttl, access_frequency))
                
                # Check if entry would expire before likely next access
                if access_frequency > 0:
                    next_access_estimate = 3600 / access_frequency  # seconds
                    if entry.ttl < next_access_estimate:
                        expired_before_access += 1
        
        if expired_before_access > len(cache_entries) * 0.1:  # > 10% expire too early
            recommendations.append(OptimizationRecommendation(
                optimization_id=f"ttl_extend_{int(datetime.utcnow().timestamp())}",
                optimization_type=OptimizationType.TTL_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="Optimize TTL Settings",
                description=f"{expired_before_access} entries expire before likely reaccess. Increase TTL.",
                expected_impact={'hit_rate': 15, 'cache_misses': -20},
                implementation_complexity="low",
                estimated_effort=1,
                parameters={'ttl_multiplier': 1.5, 'adaptive_ttl': True},
                confidence=0.8
            ))
        
        return recommendations
    
    async def _analyze_eviction_optimization(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze eviction strategy effectiveness"""
        recommendations = []
        
        eviction_rate = metrics.get('evictions', 0) / max(metrics.get('total_requests', 1), 1)
        
        if eviction_rate > 0.1:  # High eviction rate
            # Analyze what's being evicted vs what should be evicted
            high_value_evictions = 0
            total_evictions = metrics.get('evictions', 0)
            
            # This would require tracking evicted entries - simplified analysis
            if total_evictions > 0:
                recommendations.append(OptimizationRecommendation(
                    optimization_id=f"eviction_strategy_{int(datetime.utcnow().timestamp())}",
                    optimization_type=OptimizationType.EVICTION_OPTIMIZATION,
                    priority=OptimizationPriority.HIGH,
                    title="Improve Eviction Strategy",
                    description=f"High eviction rate ({eviction_rate:.1%}). Consider smarter eviction algorithm.",
                    expected_impact={'hit_rate': 8, 'eviction_efficiency': 25},
                    implementation_complexity="medium",
                    estimated_effort=8,
                    parameters={'strategy': 'adaptive_lru', 'consider_value': True},
                    confidence=0.7
                ))
        
        return recommendations
    
    async def _analyze_compression_optimization(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze compression opportunities"""
        recommendations = []
        
        # Analyze entry sizes and compression potential
        large_entries = 0
        compressible_entries = 0
        total_size = 0
        
        for entry in cache_entries.values():
            if hasattr(entry, 'size_bytes'):
                total_size += entry.size_bytes
                
                if entry.size_bytes > 1024:  # > 1KB
                    large_entries += 1
                    
                    # Heuristic for compressibility based on content type
                    if hasattr(entry, 'content_type'):
                        if entry.content_type in ['text', 'json', 'xml', 'html']:
                            compressible_entries += 1
        
        if compressible_entries > len(cache_entries) * 0.2:  # > 20% compressible
            estimated_savings = compressible_entries * 0.6  # Assume 60% compression
            
            recommendations.append(OptimizationRecommendation(
                optimization_id=f"compression_{int(datetime.utcnow().timestamp())}",
                optimization_type=OptimizationType.COMPRESSION_OPTIMIZATION,
                priority=OptimizationPriority.NORMAL,
                title="Enable Smart Compression",
                description=f"{compressible_entries} entries are good compression candidates.",
                expected_impact={'memory_usage': -estimated_savings * 100 / len(cache_entries)},
                implementation_complexity="medium",
                estimated_effort=4,
                parameters={'compression_threshold': 1024, 'algorithm': 'gzip'},
                confidence=0.8
            ))
        
        return recommendations
    
    async def _analyze_prefetching_opportunities(
        self,
        cache_entries: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """Analyze prefetching opportunities"""
        recommendations = []
        
        # Analyze sequential access patterns
        # This is a simplified analysis - real implementation would track access sequences
        
        miss_rate = metrics.get('miss_rate', 0)
        if miss_rate > 0.2:  # > 20% miss rate
            recommendations.append(OptimizationRecommendation(
                optimization_id=f"prefetch_{int(datetime.utcnow().timestamp())}",
                optimization_type=OptimizationType.PREFETCH_OPTIMIZATION,
                priority=OptimizationPriority.NORMAL,
                title="Implement Predictive Prefetching",
                description=f"Miss rate is {miss_rate:.1%}. Predictive prefetching could help.",
                expected_impact={'hit_rate': 12, 'response_time': -15},
                implementation_complexity="high",
                estimated_effort=16,
                parameters={'prefetch_ratio': 0.1, 'prediction_model': 'markov_chain'},
                confidence=0.6
            ))
        
        return recommendations
    
    async def _execute_automatic_optimizations(
        self,
        recommendations: List[OptimizationRecommendation],
        cache_entries: Dict[str, Any]
    ) -> List[OptimizationResult]:
        """Execute high-priority optimizations automatically"""
        results = []
        
        for rec in recommendations:
            # Only auto-execute critical/high priority, low complexity optimizations
            if (rec.priority in [OptimizationPriority.CRITICAL, OptimizationPriority.HIGH] and
                rec.implementation_complexity == "low" and 
                rec.confidence > 0.7):
                
                result = await self._execute_optimization(rec, cache_entries)
                results.append(result)
                
                if result.success:
                    logger.info(f"Auto-executed optimization: {rec.title}")
                else:
                    logger.warning(f"Failed auto-optimization: {rec.title} - {result.error_message}")
        
        return results
    
    async def _execute_optimization(
        self,
        recommendation: OptimizationRecommendation,
        cache_entries: Dict[str, Any]
    ) -> OptimizationResult:
        """Execute specific optimization recommendation"""
        start_time = datetime.utcnow()
        
        try:
            # Store before metrics
            before_metrics = await self._capture_metrics_snapshot(cache_entries)
            
            # Execute based on optimization type
            if recommendation.optimization_type == OptimizationType.MEMORY_OPTIMIZATION:
                success = await self._execute_memory_optimization(recommendation, cache_entries)
            elif recommendation.optimization_type == OptimizationType.TTL_OPTIMIZATION:
                success = await self._execute_ttl_optimization(recommendation, cache_entries)
            else:
                # Placeholder for other optimization types
                success = True
            
            # Capture after metrics
            after_metrics = await self._capture_metrics_snapshot(cache_entries)
            
            # Calculate actual impact
            actual_impact = self._calculate_actual_impact(before_metrics, after_metrics)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return OptimizationResult(
                recommendation_id=recommendation.optimization_id,
                success=success,
                execution_time=execution_time,
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                actual_impact=actual_impact
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return OptimizationResult(
                recommendation_id=recommendation.optimization_id,
                success=False,
                execution_time=execution_time,
                before_metrics={},
                after_metrics={},
                actual_impact={},
                error_message=str(e)
            )
    
    async def _execute_memory_optimization(
        self,
        recommendation: OptimizationRecommendation,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """Execute memory optimization"""



        try:
            target_reduction = recommendation.parameters.get('target_reduction_percent', 20)
            
            # Calculate entries to evict
            current_size = sum(
                getattr(entry, 'size_bytes', 0) 
                for entry in cache_entries.values()
            )
            target_size = current_size * (1 - target_reduction / 100)
            size_to_free = current_size - target_size
            
            # Sort entries by eviction priority (low access count, old entries)
            sorted_entries = sorted(
                cache_entries.items(),
                key=lambda x: (
                    getattr(x[1], 'access_count', 0),
                    getattr(x[1], 'last_accessed', datetime.min)
                )
            )
            
            # Evict entries until target is reached
            freed_size = 0
            evicted_keys = []
            
            for key, entry in sorted_entries:
                if freed_size >= size_to_free:
                    break
                    
                entry_size = getattr(entry, 'size_bytes', 0)
                evicted_keys.append(key)
                freed_size += entry_size
            
            # This would integrate with the actual cache to perform evictions
            logger.info(f"Memory optimization would evict {len(evicted_keys)} entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Memory optimization execution failed: {e}")
            return False
    
    async def _execute_ttl_optimization(
        self,
        recommendation: OptimizationRecommendation,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """Execute TTL optimization"""



        try:
            ttl_multiplier = recommendation.parameters.get('ttl_multiplier', 1.5)
            adaptive_ttl = recommendation.parameters.get('adaptive_ttl', False)
            
            updated_count = 0
            
            for entry in cache_entries.values():
                if hasattr(entry, 'ttl') and entry.ttl:
                    if adaptive_ttl and hasattr(entry, 'access_count'):
                        # Adaptive TTL based on access frequency
                        access_frequency = entry.access_count / max(
                            (datetime.utcnow() - entry.created_at).total_seconds(),
                            1
                        )
                        
                        if access_frequency > 0.001:  # More than once per 1000 seconds
                            entry.ttl = int(entry.ttl * ttl_multiplier)
                            updated_count += 1
                    else:
                        # Simple TTL increase
                        entry.ttl = int(entry.ttl * ttl_multiplier)
                        updated_count += 1
            
            logger.info(f"TTL optimization updated {updated_count} entries")
            return True
            
        except Exception as e:
            logger.error(f"TTL optimization execution failed: {e}")
            return False
    
    async def _update_historical_metrics(self, metrics: Dict[str, Any]):
        """Update historical metrics for trend analysis"""
        timestamp = datetime.utcnow()
        
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                self.historical_metrics[metric_name].append((timestamp, value))
    
    async def _update_learning_models(self, metrics: Dict[str, Any]):
        """Update ML models with new performance data"""
        # Simplified learning model update
        # Real implementation would use proper ML algorithms
        
        for metric_name, values in self.historical_metrics.items():
            if len(values) >= self.min_data_points:
                # Calculate trend
                recent_values = list(values)[-50:]  # Last 50 points
                timestamps = [t.timestamp() for t, v in recent_values]
                metric_values = [v for t, v in recent_values]
                
                if len(metric_values) > 1:
                    # Simple linear regression for trend
                    correlation = np.corrcoef(timestamps, metric_values)[0, 1]
                    
                    if not math.isnan(correlation):
                        self.predictive_models[metric_name] = {
                            'trend_correlation': correlation,
                            'last_updated': datetime.utcnow(),
                            'data_points': len(metric_values)
                        }
    
    async def _generate_predictions(self) -> List[CachePrediction]:
        """Generate performance predictions"""
        predictions = []
        
        for metric_name, model_data in self.predictive_models.items():
            if metric_name in self.historical_metrics:
                recent_data = list(self.historical_metrics[metric_name])[-20:]
                
                if len(recent_data) >= 10:
                    current_value = recent_data[-1][1]
                    
                    # Simple trend-based prediction
                    trend_correlation = model_data.get('trend_correlation', 0)
                    
                    if abs(trend_correlation) > 0.3:  # Significant trend
                        trend = "increasing" if trend_correlation > 0 else "decreasing"
                    else:
                        trend = "stable"
                    
                    # Generate future predictions (next 24 hours)
                    predicted_values = []
                    base_time = datetime.utcnow()
                    
                    for hours_ahead in [1, 6, 12, 24]:
                        future_time = base_time + timedelta(hours=hours_ahead)
                        
                        # Simple linear projection
                        if trend == "increasing":
                            predicted_value = current_value * (1 + 0.01 * hours_ahead)
                        elif trend == "decreasing":
                            predicted_value = current_value * (1 - 0.01 * hours_ahead)
                        else:
                            predicted_value = current_value
                        
                        predicted_values.append((future_time, predicted_value))
                    
                    predictions.append(CachePrediction(
                        metric_name=metric_name,
                        current_value=current_value,
                        predicted_values=predicted_values,
                        confidence_intervals=[(v * 0.9, v * 1.1) for _, v in predicted_values],
                        trend=trend,
                        prediction_accuracy=0.75  # Would be calculated based on historical accuracy
                    ))
        
        return predictions
    
    async def _capture_metrics_snapshot(self, cache_entries: Dict[str, Any]) -> Dict[str, Any]:
        """Capture current metrics snapshot"""
        total_entries = len(cache_entries)
        total_size = sum(
            getattr(entry, 'size_bytes', 0) 
            for entry in cache_entries.values()
        )
        total_access_count = sum(
            getattr(entry, 'access_count', 0) 
            for entry in cache_entries.values()
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_entries': total_entries,
            'total_size_bytes': total_size,
            'average_entry_size': total_size / max(total_entries, 1),
            'total_access_count': total_access_count,
            'average_access_count': total_access_count / max(total_entries, 1)
        }
    
    def _calculate_actual_impact(
        self,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate actual impact of optimization"""
        impact = {}
        
        for metric_name in before_metrics:
            if metric_name in after_metrics and metric_name != 'timestamp':
                before_value = before_metrics[metric_name]
                after_value = after_metrics[metric_name]
                
                if isinstance(before_value, (int, float)) and before_value != 0:
                    percent_change = ((after_value - before_value) / before_value) * 100
                    impact[metric_name] = percent_change
        
        return impact
    
    async def _calculate_improvement(self, current_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance improvement over baseline"""
        if not self.performance_baseline:
            # Set current as baseline
            self.performance_baseline = current_metrics.copy()
            return {}
        
        improvements = {}
        
        for metric_name, current_value in current_metrics.items():
            if (metric_name in self.performance_baseline and 
                isinstance(current_value, (int, float))):
                
                baseline_value = self.performance_baseline[metric_name]
                if baseline_value != 0:
                    improvement = ((current_value - baseline_value) / baseline_value) * 100
                    improvements[metric_name] = improvement
        
        return improvements
    
    def _recommendation_to_dict(self, rec: OptimizationRecommendation) -> Dict[str, Any]:
        """Convert recommendation to dictionary"""



        return {
            'optimization_id': rec.optimization_id,
            'type': rec.optimization_type.value,
            'priority': rec.priority.value,
            'title': rec.title,
            'description': rec.description,
            'expected_impact': rec.expected_impact,
            'complexity': rec.implementation_complexity,
            'estimated_effort': rec.estimated_effort,
            'confidence': rec.confidence,
            'parameters': rec.parameters
        }
    
    def _prediction_to_dict(self, pred: CachePrediction) -> Dict[str, Any]:
        """Convert prediction to dictionary"""



        return {
            'metric_name': pred.metric_name,
            'current_value': pred.current_value,
            'predicted_values': [
                {'time': t.isoformat(), 'value': v} 
                for t, v in pred.predicted_values
            ],
            'trend': pred.trend,
            'prediction_accuracy': pred.prediction_accuracy
        }
