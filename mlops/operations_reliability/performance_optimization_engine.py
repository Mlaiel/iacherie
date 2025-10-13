"""
🛡️ MLOps Operations & Reliability - Performance Optimization Engine
====================================================================

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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise performance optimization engine for Creator Economy automated optimization.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import numpy as np
from collections import defaultdict, deque


class OptimizationType(Enum):
    """Types of performance optimizations"""
    DATABASE_QUERY = "database_query"
    CACHE_STRATEGY = "cache_strategy"
    CDN_CONFIGURATION = "cdn_configuration"
    RESOURCE_ALLOCATION = "resource_allocation"
    NETWORK_OPTIMIZATION = "network_optimization"
    ALGORITHM_TUNING = "algorithm_tuning"
    MEMORY_MANAGEMENT = "memory_management"
    CPU_OPTIMIZATION = "cpu_optimization"
    IO_OPTIMIZATION = "io_optimization"
    LOAD_BALANCING = "load_balancing"


class CreatorWorkloadType(Enum):
    """Creator workload types for optimization"""
    VIDEO_PROCESSING = "video_processing"
    AUDIO_PROCESSING = "audio_processing"
    IMAGE_PROCESSING = "image_processing"
    CONTENT_DELIVERY = "content_delivery"
    SOCIAL_SHARING = "social_sharing"
    ANALYTICS_PROCESSING = "analytics_processing"
    REAL_TIME_STREAMING = "real_time_streaming"
    BATCH_PROCESSING = "batch_processing"


class OptimizationPriority(Enum):
    """Optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Performance metric types"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_PERFORMANCE = "database_performance"
    USER_SATISFACTION = "user_satisfaction"


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    service_id: str
    creator_tier: str
    workload_type: CreatorWorkloadType
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRule:
    """Performance optimization rule"""
    rule_id: str
    name: str
    optimization_type: OptimizationType
    trigger_conditions: Dict[str, Any]
    optimization_actions: List[Dict[str, Any]]
    priority: OptimizationPriority
    creator_impact_threshold: float
    enabled: bool = True


@dataclass
class OptimizationResult:
    """Result of an optimization action"""
    optimization_id: str
    rule_id: str
    service_id: str
    optimization_type: OptimizationType
    applied_at: datetime
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement_percentage: float
    creator_impact: float
    cost_impact: float
    rollback_possible: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison"""
    service_id: str
    workload_type: CreatorWorkloadType
    baseline_metrics: Dict[MetricType, float]
    percentile_metrics: Dict[MetricType, Dict[str, float]]  # p50, p95, p99
    established_at: datetime
    sample_size: int


class PerformanceOptimizationEngine:
    """
    Enterprise performance optimization engine for Creator Economy automated optimization.
    
    Provides intelligent performance monitoring, bottleneck detection,
    and automated optimization for creator workloads.
    """
    
    def __init__(self):
        """Initialize performance optimization engine"""
        self.logger = logging.getLogger(__name__)
        self.optimization_rules = {}
        self.performance_metrics = defaultdict(deque)
        self.baselines = {}
        self.optimization_history = []
        self.active_optimizations = {}
        self.anomaly_detectors = {}
        
        # Performance thresholds
        self.performance_thresholds = {
            MetricType.RESPONSE_TIME: 2000.0,  # 2 seconds
            MetricType.THROUGHPUT: 100.0,  # 100 RPS minimum
            MetricType.ERROR_RATE: 1.0,  # 1% maximum
            MetricType.CPU_UTILIZATION: 80.0,  # 80% maximum
            MetricType.MEMORY_USAGE: 85.0,  # 85% maximum
            MetricType.CACHE_HIT_RATE: 80.0,  # 80% minimum
            MetricType.USER_SATISFACTION: 8.0  # 8.0/10 minimum
        }
        
        # Initialize default optimization rules
        self._setup_default_optimization_rules()
        
        self.logger.info("PerformanceOptimizationEngine initialized")
    
    def _setup_default_optimization_rules(self):
        """Setup default optimization rules"""
        default_rules = [
            OptimizationRule(
                rule_id="slow_database_queries",
                name="Optimize Slow Database Queries",
                optimization_type=OptimizationType.DATABASE_QUERY,
                trigger_conditions={
                    "database_response_time_ms": "> 1000",
                    "query_frequency": "> 10/minute"
                },
                optimization_actions=[
                    {"action": "add_index", "table": "auto_detect"},
                    {"action": "query_rewrite", "type": "join_optimization"},
                    {"action": "connection_pooling", "pool_size": "auto"}
                ],
                priority=OptimizationPriority.HIGH,
                creator_impact_threshold=5.0
            ),
            OptimizationRule(
                rule_id="cache_miss_optimization",
                name="Improve Cache Hit Rate",
                optimization_type=OptimizationType.CACHE_STRATEGY,
                trigger_conditions={
                    "cache_hit_rate": "< 70",
                    "cache_misses_per_minute": "> 100"
                },
                optimization_actions=[
                    {"action": "cache_warming", "strategy": "predictive"},
                    {"action": "cache_ttl_optimization", "method": "adaptive"},
                    {"action": "cache_partitioning", "strategy": "user_based"}
                ],
                priority=OptimizationPriority.MEDIUM,
                creator_impact_threshold=3.0
            ),
            OptimizationRule(
                rule_id="cdn_optimization",
                name="CDN Performance Optimization",
                optimization_type=OptimizationType.CDN_CONFIGURATION,
                trigger_conditions={
                    "cdn_response_time_ms": "> 500",
                    "cdn_hit_rate": "< 80"
                },
                optimization_actions=[
                    {"action": "edge_cache_config", "strategy": "creator_location_based"},
                    {"action": "compression_optimization", "types": ["gzip", "brotli"]},
                    {"action": "cache_headers_optimization", "policy": "aggressive"}
                ],
                priority=OptimizationPriority.HIGH,
                creator_impact_threshold=8.0
            ),
            OptimizationRule(
                rule_id="memory_optimization",
                name="Memory Usage Optimization",
                optimization_type=OptimizationType.MEMORY_MANAGEMENT,
                trigger_conditions={
                    "memory_usage_percentage": "> 85",
                    "gc_frequency": "> 10/minute"
                },
                optimization_actions=[
                    {"action": "memory_pool_optimization", "strategy": "adaptive"},
                    {"action": "gc_tuning", "algorithm": "g1gc"},
                    {"action": "object_reuse", "pattern": "pool_based"}
                ],
                priority=OptimizationPriority.CRITICAL,
                creator_impact_threshold=2.0
            ),
            OptimizationRule(
                rule_id="load_balancer_optimization",
                name="Load Balancer Optimization",
                optimization_type=OptimizationType.LOAD_BALANCING,
                trigger_conditions={
                    "load_imbalance_ratio": "> 2.0",
                    "server_utilization_variance": "> 30"
                },
                optimization_actions=[
                    {"action": "algorithm_switch", "to": "least_connections"},
                    {"action": "health_check_optimization", "interval": "adaptive"},
                    {"action": "sticky_session_optimization", "strategy": "creator_based"}
                ],
                priority=OptimizationPriority.HIGH,
                creator_impact_threshold=6.0
            )
        ]
        
        for rule in default_rules:
            self.optimization_rules[rule.rule_id] = rule
    
    async def collect_performance_metrics(
        self,
        service_id: str,
        metrics: List[PerformanceMetric]
    ) -> bool:
        """
        Collect performance metrics for analysis
        
        Args:
            service_id: Service identifier
            metrics: List of performance metrics
            
        Returns:
            True if metrics collected successfully
        """
        try:
            for metric in metrics:
                # Store metric with timestamp-based key
                key = f"{service_id}_{metric.metric_type.value}"
                self.performance_metrics[key].append(metric)
                
                # Keep only last 1000 metrics per key
                if len(self.performance_metrics[key]) > 1000:
                    self.performance_metrics[key].popleft()
            
            # Update baselines if needed
            await self._update_performance_baselines(service_id, metrics)
            
            # Check for optimization opportunities
            await self._evaluate_optimization_opportunities(service_id, metrics)
            
            self.logger.debug(f"Collected {len(metrics)} performance metrics for {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {str(e)}")
            raise
    
    async def _update_performance_baselines(
        self,
        service_id: str,
        metrics: List[PerformanceMetric]
    ):
        """Update performance baselines for services"""
        # Group metrics by workload type
        workload_metrics = defaultdict(list)
        for metric in metrics:
            workload_metrics[metric.workload_type].append(metric)
        
        for workload_type, workload_metric_list in workload_metrics.items():
            baseline_key = f"{service_id}_{workload_type.value}"
            
            # Calculate baseline metrics
            metric_aggregates = {}
            percentile_aggregates = {}
            
            # Group by metric type
            by_type = defaultdict(list)
            for metric in workload_metric_list:
                by_type[metric.metric_type].append(metric.value)
            
            for metric_type, values in by_type.items():
                if values:
                    metric_aggregates[metric_type] = statistics.mean(values)
                    percentile_aggregates[metric_type] = {
                        'p50': statistics.median(values),
                        'p95': np.percentile(values, 95) if len(values) > 1 else values[0],
                        'p99': np.percentile(values, 99) if len(values) > 1 else values[0]
                    }
            
            # Create or update baseline
            if metric_aggregates:
                baseline = PerformanceBaseline(
                    service_id=service_id,
                    workload_type=workload_type,
                    baseline_metrics=metric_aggregates,
                    percentile_metrics=percentile_aggregates,
                    established_at=datetime.now(),
                    sample_size=len(workload_metric_list)
                )
                
                self.baselines[baseline_key] = baseline
    
    async def _evaluate_optimization_opportunities(
        self,
        service_id: str,
        metrics: List[PerformanceMetric]
    ):
        """Evaluate if optimization rules should be triggered"""
        for rule_id, rule in self.optimization_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule conditions are met
            if await self._check_rule_conditions(rule, service_id, metrics):
                await self._trigger_optimization(rule, service_id, metrics)
    
    async def _check_rule_conditions(
        self,
        rule: OptimizationRule,
        service_id: str,
        metrics: List[PerformanceMetric]
    ) -> bool:
        """Check if optimization rule conditions are met"""
        try:
            # Convert metrics to evaluation context
            metric_values = {}
            for metric in metrics:
                key = f"{metric.metric_type.value}"
                if key not in metric_values:
                    metric_values[key] = []
                metric_values[key].append(metric.value)
            
            # Calculate aggregates for condition evaluation
            eval_context = {}
            for key, values in metric_values.items():
                if values:
                    eval_context[key] = statistics.mean(values)
                    eval_context[f"{key}_max"] = max(values)
                    eval_context[f"{key}_min"] = min(values)
            
            # Evaluate each condition
            for condition_key, condition_value in rule.trigger_conditions.items():
                if condition_key not in eval_context:
                    continue
                
                current_value = eval_context[condition_key]
                
                # Parse condition
                if isinstance(condition_value, str):
                    if condition_value.startswith(">"):
                        threshold = float(condition_value[1:].strip())
                        if current_value <= threshold:
                            return False
                    elif condition_value.startswith("<"):
                        threshold = float(condition_value[1:].strip())
                        if current_value >= threshold:
                            return False
                    elif condition_value.startswith("="):
                        threshold = float(condition_value[1:].strip())
                        if abs(current_value - threshold) > 0.01:
                            return False
                else:
                    # Direct comparison
                    if current_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rule conditions: {str(e)}")
            return False
    
    async def _trigger_optimization(
        self,
        rule: OptimizationRule,
        service_id: str,
        metrics: List[PerformanceMetric]
    ):
        """Trigger an optimization based on rule"""
        optimization_id = f"opt_{int(time.time())}_{rule.rule_id}"
        
        # Check if similar optimization is already running
        active_key = f"{service_id}_{rule.optimization_type.value}"
        if active_key in self.active_optimizations:
            self.logger.debug(f"Optimization already active for {active_key}")
            return
        
        try:
            # Collect before metrics
            before_metrics = await self._collect_current_metrics(service_id)
            
            # Apply optimization
            self.active_optimizations[active_key] = optimization_id
            optimization_success = await self._apply_optimization(rule, service_id)
            
            if optimization_success:
                # Wait for changes to take effect
                await asyncio.sleep(30)
                
                # Collect after metrics
                after_metrics = await self._collect_current_metrics(service_id)
                
                # Calculate improvement
                improvement = self._calculate_improvement(before_metrics, after_metrics)
                creator_impact = self._estimate_creator_impact(improvement, rule)
                cost_impact = self._estimate_cost_impact(rule, improvement)
                
                # Create optimization result
                result = OptimizationResult(
                    optimization_id=optimization_id,
                    rule_id=rule.rule_id,
                    service_id=service_id,
                    optimization_type=rule.optimization_type,
                    applied_at=datetime.now(),
                    before_metrics=before_metrics,
                    after_metrics=after_metrics,
                    improvement_percentage=improvement,
                    creator_impact=creator_impact,
                    cost_impact=cost_impact,
                    rollback_possible=True,
                    metadata={
                        'rule_name': rule.name,
                        'actions_applied': len(rule.optimization_actions)
                    }
                )
                
                self.optimization_history.append(result)
                
                self.logger.info(f"Applied optimization {optimization_id}: "
                               f"{improvement:.1f}% improvement")
            
        except Exception as e:
            self.logger.error(f"Error applying optimization {optimization_id}: {str(e)}")
        finally:
            # Remove from active optimizations
            if active_key in self.active_optimizations:
                del self.active_optimizations[active_key]
    
    async def _apply_optimization(
        self,
        rule: OptimizationRule,
        service_id: str
    ) -> bool:
        """Apply optimization actions"""
        try:
            for action in rule.optimization_actions:
                action_type = action.get("action")
                
                if rule.optimization_type == OptimizationType.DATABASE_QUERY:
                    success = await self._apply_database_optimization(action, service_id)
                elif rule.optimization_type == OptimizationType.CACHE_STRATEGY:
                    success = await self._apply_cache_optimization(action, service_id)
                elif rule.optimization_type == OptimizationType.CDN_CONFIGURATION:
                    success = await self._apply_cdn_optimization(action, service_id)
                elif rule.optimization_type == OptimizationType.MEMORY_MANAGEMENT:
                    success = await self._apply_memory_optimization(action, service_id)
                elif rule.optimization_type == OptimizationType.LOAD_BALANCING:
                    success = await self._apply_load_balancer_optimization(action, service_id)
                else:
                    success = await self._apply_generic_optimization(action, service_id)
                
                if not success:
                    self.logger.warning(f"Failed to apply action: {action_type}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying optimization: {str(e)}")
            return False
    
    async def _apply_database_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply database optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying database optimization: {action_type} for {service_id}")
        
        # Simulate database optimization
        await asyncio.sleep(1)  # Simulate time to apply
        return True
    
    async def _apply_cache_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply cache optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying cache optimization: {action_type} for {service_id}")
        
        # Simulate cache optimization
        await asyncio.sleep(0.5)
        return True
    
    async def _apply_cdn_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply CDN optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying CDN optimization: {action_type} for {service_id}")
        
        # Simulate CDN optimization
        await asyncio.sleep(2)
        return True
    
    async def _apply_memory_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply memory optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying memory optimization: {action_type} for {service_id}")
        
        # Simulate memory optimization
        await asyncio.sleep(1.5)
        return True
    
    async def _apply_load_balancer_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply load balancer optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying load balancer optimization: {action_type} for {service_id}")
        
        # Simulate load balancer optimization
        await asyncio.sleep(1)
        return True
    
    async def _apply_generic_optimization(
        self,
        action: Dict[str, Any],
        service_id: str
    ) -> bool:
        """Apply generic optimization"""
        action_type = action.get("action")
        self.logger.info(f"Applying generic optimization: {action_type} for {service_id}")
        
        # Simulate generic optimization
        await asyncio.sleep(0.5)
        return True
    
    async def _collect_current_metrics(self, service_id: str) -> Dict[str, float]:
        """Collect current performance metrics for comparison"""
        current_metrics = {}
        
        # Simulate collecting current metrics
        current_metrics = {
            'response_time_ms': np.random.uniform(200, 800),
            'throughput_rps': np.random.uniform(80, 150),
            'error_rate_percent': np.random.uniform(0, 3),
            'cpu_utilization_percent': np.random.uniform(40, 90),
            'memory_usage_percent': np.random.uniform(50, 85),
            'cache_hit_rate_percent': np.random.uniform(70, 95)
        }
        
        return current_metrics
    
    def _calculate_improvement(
        self,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float]
    ) -> float:
        """Calculate overall improvement percentage"""
        improvements = []
        
        # Calculate improvement for each metric
        for metric_name in before_metrics:
            if metric_name in after_metrics:
                before_value = before_metrics[metric_name]
                after_value = after_metrics[metric_name]
                
                # Determine if lower or higher is better
                if metric_name in ['response_time_ms', 'error_rate_percent', 'cpu_utilization_percent', 'memory_usage_percent']:
                    # Lower is better
                    if before_value > 0:
                        improvement = ((before_value - after_value) / before_value) * 100
                        improvements.append(improvement)
                else:
                    # Higher is better
                    if before_value > 0:
                        improvement = ((after_value - before_value) / before_value) * 100
                        improvements.append(improvement)
        
        # Return average improvement
        return statistics.mean(improvements) if improvements else 0.0
    
    def _estimate_creator_impact(
        self,
        improvement: float,
        rule: OptimizationRule
    ) -> float:
        """Estimate creator impact of optimization"""
        # Base impact on optimization type
        base_impact = {
            OptimizationType.DATABASE_QUERY: 3.0,
            OptimizationType.CACHE_STRATEGY: 2.0,
            OptimizationType.CDN_CONFIGURATION: 5.0,
            OptimizationType.MEMORY_MANAGEMENT: 1.5,
            OptimizationType.LOAD_BALANCING: 4.0,
            OptimizationType.NETWORK_OPTIMIZATION: 3.5,
            OptimizationType.CPU_OPTIMIZATION: 2.5
        }.get(rule.optimization_type, 2.0)
        
        # Scale by improvement percentage
        impact = base_impact * (improvement / 100) if improvement > 0 else 0
        
        return max(0, min(100, impact))
    
    def _estimate_cost_impact(
        self,
        rule: OptimizationRule,
        improvement: float
    ) -> float:
        """Estimate cost impact of optimization"""
        # Cost impact varies by optimization type
        cost_factors = {
            OptimizationType.DATABASE_QUERY: -0.1,  # Negative = cost savings
            OptimizationType.CACHE_STRATEGY: -0.05,
            OptimizationType.CDN_CONFIGURATION: 0.02,  # Positive = cost increase
            OptimizationType.MEMORY_MANAGEMENT: -0.08,
            OptimizationType.LOAD_BALANCING: 0.01,
            OptimizationType.CPU_OPTIMIZATION: -0.12
        }.get(rule.optimization_type, 0.0)
        
        return cost_factors * improvement
    
    async def create_custom_optimization_rule(
        self,
        rule: OptimizationRule
    ) -> bool:
        """
        Create a custom optimization rule
        
        Args:
            rule: Optimization rule to create
            
        Returns:
            True if rule created successfully
        """
        try:
            # Validate rule
            if not rule.rule_id or rule.rule_id in self.optimization_rules:
                raise ValueError("Rule ID must be unique and non-empty")
            
            if not rule.trigger_conditions:
                raise ValueError("Rule must have trigger conditions")
            
            if not rule.optimization_actions:
                raise ValueError("Rule must have optimization actions")
            
            # Store rule
            self.optimization_rules[rule.rule_id] = rule
            
            self.logger.info(f"Created custom optimization rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating optimization rule: {str(e)}")
            raise
    
    async def get_optimization_recommendations(
        self,
        service_id: str,
        workload_type: Optional[CreatorWorkloadType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get performance optimization recommendations
        
        Args:
            service_id: Service to analyze
            workload_type: Optional workload type filter
            
        Returns:
            List of optimization recommendations
        """
        try:
            recommendations = []
            
            # Analyze current performance metrics
            recent_metrics = await self._get_recent_metrics(service_id, workload_type)
            
            if not recent_metrics:
                return recommendations
            
            # Check against baselines
            baseline_key = f"{service_id}_{workload_type.value}" if workload_type else service_id
            baseline = self.baselines.get(baseline_key)
            
            # Analyze each metric type
            for metric_type, threshold in self.performance_thresholds.items():
                metric_values = [m.value for m in recent_metrics if m.metric_type == metric_type]
                
                if not metric_values:
                    continue
                
                avg_value = statistics.mean(metric_values)
                
                # Check if metric exceeds threshold
                needs_optimization = False
                if metric_type in [MetricType.RESPONSE_TIME, MetricType.ERROR_RATE, 
                                 MetricType.CPU_UTILIZATION, MetricType.MEMORY_USAGE]:
                    needs_optimization = avg_value > threshold
                else:
                    needs_optimization = avg_value < threshold
                
                if needs_optimization:
                    recommendation = {
                        'metric_type': metric_type.value,
                        'current_value': avg_value,
                        'threshold': threshold,
                        'severity': self._calculate_severity(avg_value, threshold, metric_type),
                        'suggested_optimizations': self._get_suggested_optimizations(metric_type),
                        'expected_improvement': self._estimate_expected_improvement(metric_type, avg_value, threshold),
                        'creator_impact_risk': self._calculate_optimization_risk(metric_type)
                    }
                    recommendations.append(recommendation)
            
            # Sort by severity
            recommendations.sort(key=lambda x: ['low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True)
            
            self.logger.info(f"Generated {len(recommendations)} optimization recommendations for {service_id}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {str(e)}")
            raise
    
    async def _get_recent_metrics(
        self,
        service_id: str,
        workload_type: Optional[CreatorWorkloadType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[PerformanceMetric]:
        """Get recent performance metrics"""
        cutoff_time = datetime.now() - time_window
        recent_metrics = []
        
        for key, metrics in self.performance_metrics.items():
            if service_id in key:
                for metric in metrics:
                    if metric.timestamp >= cutoff_time:
                        if workload_type is None or metric.workload_type == workload_type:
                            recent_metrics.append(metric)
        
        return recent_metrics
    
    def _calculate_severity(
        self,
        current_value: float,
        threshold: float,
        metric_type: MetricType
    ) -> str:
        """Calculate severity of performance issue"""
        if metric_type in [MetricType.RESPONSE_TIME, MetricType.ERROR_RATE, 
                          MetricType.CPU_UTILIZATION, MetricType.MEMORY_USAGE]:
            # Higher is worse
            ratio = current_value / threshold
            if ratio > 2.0:
                return 'critical'
            elif ratio > 1.5:
                return 'high'
            elif ratio > 1.2:
                return 'medium'
            else:
                return 'low'
        else:
            # Lower is worse
            ratio = threshold / current_value if current_value > 0 else float('inf')
            if ratio > 2.0:
                return 'critical'
            elif ratio > 1.5:
                return 'high'
            elif ratio > 1.2:
                return 'medium'
            else:
                return 'low'
    
    def _get_suggested_optimizations(self, metric_type: MetricType) -> List[str]:
        """Get suggested optimizations for metric type"""
        suggestions = {
            MetricType.RESPONSE_TIME: [
                "Database query optimization",
                "Cache implementation",
                "CDN configuration",
                "Load balancer tuning"
            ],
            MetricType.THROUGHPUT: [
                "Connection pooling",
                "Async processing",
                "Load balancer optimization",
                "Resource scaling"
            ],
            MetricType.ERROR_RATE: [
                "Error handling improvement",
                "Retry logic optimization",
                "Circuit breaker implementation",
                "Health check tuning"
            ],
            MetricType.CPU_UTILIZATION: [
                "Algorithm optimization",
                "Parallel processing",
                "Resource allocation",
                "Code profiling"
            ],
            MetricType.MEMORY_USAGE: [
                "Memory pool optimization",
                "Garbage collection tuning",
                "Object lifecycle management",
                "Cache size optimization"
            ],
            MetricType.CACHE_HIT_RATE: [
                "Cache warming strategy",
                "TTL optimization",
                "Cache partitioning",
                "Eviction policy tuning"
            ]
        }
        
        return suggestions.get(metric_type, ["General performance optimization"])
    
    def _estimate_expected_improvement(
        self,
        metric_type: MetricType,
        current_value: float,
        threshold: float
    ) -> float:
        """Estimate expected improvement percentage"""
        if metric_type in [MetricType.RESPONSE_TIME, MetricType.ERROR_RATE]:
            # Target is to reduce to threshold
            if current_value > threshold:
                return ((current_value - threshold) / current_value) * 100
        else:
            # Target is to increase to threshold
            if current_value < threshold:
                return ((threshold - current_value) / current_value) * 100
        
        return 0.0
    
    def _calculate_optimization_risk(self, metric_type: MetricType) -> str:
        """Calculate risk level of optimization"""
        risk_levels = {
            MetricType.RESPONSE_TIME: "low",
            MetricType.THROUGHPUT: "medium",
            MetricType.ERROR_RATE: "low",
            MetricType.CPU_UTILIZATION: "medium",
            MetricType.MEMORY_USAGE: "high",
            MetricType.CACHE_HIT_RATE: "low",
            MetricType.DATABASE_PERFORMANCE: "high"
        }
        
        return risk_levels.get(metric_type, "medium")
    
    async def generate_performance_report(
        self,
        service_id: Optional[str] = None,
        time_range: timedelta = timedelta(days=1)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            service_id: Specific service to report on (None for all)
            time_range: Time range for report data
            
        Returns:
            Comprehensive performance report
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'time_range': str(time_range),
                'services': {},
                'optimization_summary': {},
                'recommendations': []
            }
            
            # Get optimization history for time range
            cutoff_time = datetime.now() - time_range
            recent_optimizations = [
                opt for opt in self.optimization_history
                if opt.applied_at >= cutoff_time
            ]
            
            # Filter by service if specified
            if service_id:
                recent_optimizations = [
                    opt for opt in recent_optimizations
                    if opt.service_id == service_id
                ]
            
            # Calculate optimization summary
            total_optimizations = len(recent_optimizations)
            successful_optimizations = len([opt for opt in recent_optimizations if opt.improvement_percentage > 0])
            avg_improvement = statistics.mean([opt.improvement_percentage for opt in recent_optimizations]) if recent_optimizations else 0
            total_creator_impact = sum(opt.creator_impact for opt in recent_optimizations)
            
            report['optimization_summary'] = {
                'total_optimizations': total_optimizations,
                'successful_optimizations': successful_optimizations,
                'success_rate': (successful_optimizations / total_optimizations * 100) if total_optimizations > 0 else 0,
                'average_improvement': avg_improvement,
                'total_creator_impact': total_creator_impact,
                'optimization_types': list(set(opt.optimization_type.value for opt in recent_optimizations))
            }
            
            # Get service-specific data
            services_to_report = [service_id] if service_id else list(set(opt.service_id for opt in recent_optimizations))
            
            for svc_id in services_to_report:
                service_optimizations = [opt for opt in recent_optimizations if opt.service_id == svc_id]
                service_metrics = await self._get_recent_metrics(svc_id, None, time_range)
                
                service_report = {
                    'service_id': svc_id,
                    'optimization_count': len(service_optimizations),
                    'average_improvement': statistics.mean([opt.improvement_percentage for opt in service_optimizations]) if service_optimizations else 0,
                    'creator_impact': sum(opt.creator_impact for opt in service_optimizations),
                    'performance_metrics': self._summarize_metrics(service_metrics),
                    'active_rules': len([rule for rule in self.optimization_rules.values() if rule.enabled])
                }
                
                report['services'][svc_id] = service_report
            
            # Generate recommendations
            for svc_id in services_to_report:
                svc_recommendations = await self.get_optimization_recommendations(svc_id)
                report['recommendations'].extend([
                    {**rec, 'service_id': svc_id} for rec in svc_recommendations
                ])
            
            self.logger.info(f"Generated performance report for {len(services_to_report)} services")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            raise
    
    def _summarize_metrics(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Summarize performance metrics"""
        if not metrics:
            return {}
        
        summary = {}
        
        # Group by metric type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric.metric_type].append(metric.value)
        
        for metric_type, values in by_type.items():
            if values:
                summary[metric_type.value] = {
                    'average': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'median': statistics.median(values),
                    'count': len(values)
                }
        
        return summary
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get performance optimization engine status"""
        return {
            'engine_name': 'PerformanceOptimizationEngine',
            'version': '1.0.0',
            'status': 'active',
            'optimization_rules': len(self.optimization_rules),
            'active_optimizations': len(self.active_optimizations),
            'optimization_history': len(self.optimization_history),
            'services_monitored': len(set(key.split('_')[0] for key in self.performance_metrics.keys())),
            'supported_optimization_types': [opt_type.value for opt_type in OptimizationType],
            'supported_workload_types': [workload.value for workload in CreatorWorkloadType]
        }


# Export main classes and enums
__all__ = [
    'PerformanceOptimizationEngine',
    'OptimizationType',
    'CreatorWorkloadType',
    'OptimizationPriority',
    'MetricType',
    'PerformanceMetric',
    'OptimizationRule',
    'OptimizationResult',
    'PerformanceBaseline'
]