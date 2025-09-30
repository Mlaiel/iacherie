"""Performance Optimization Engine - System Performance Optimization
==================================================================

Intelligent performance monitoring and optimization with automated tuning,
resource optimization, and performance anomaly detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import statistics

import redis.asyncio as redis


class OptimizationType(Enum):
    """Performance optimization types."""
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_OPTIMIZATION = "index_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"


@dataclass
class PerformanceMetric:
    """Performance metric definition."""
    id: str
    name: str
    metric_type: str
    threshold_warning: float
    threshold_critical: float
    optimization_target: float
    unit: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    id: str
    optimization_type: OptimizationType
    title: str
    description: str
    impact_estimate: str
    implementation_effort: str
    actions: List[str]
    priority: int  # 1-5, 1 being highest
    estimated_improvement: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    implemented: bool = False


class PerformanceOptimizationEngine:
    """Intelligent performance monitoring and optimization system."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Redis setup
        self.redis_url = redis_url
        self.redis_client = None
        
        # Performance tracking
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.current_values: Dict[str, float] = {}
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        
        # Optimization state
        self.monitoring_active = False
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.engine_metrics = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'average_improvement': 0.0,
            'recommendations_generated': 0
        }
        
        # Setup built-in metrics
        self._setup_built_in_metrics()
    
    async def initialize(self):
        """Initialize the optimization engine."""
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("Performance optimization engine initialized")
    
    def _setup_built_in_metrics(self):
        """Setup built-in performance metrics."""
        # Query response time
        query_time_metric = PerformanceMetric(
            id="query_response_time",
            name="Query Response Time",
            metric_type="timer",
            threshold_warning=1000.0,  # 1 second
            threshold_critical=5000.0,  # 5 seconds
            optimization_target=500.0,  # 500ms
            unit="ms"
        )
        
        # CPU utilization
        cpu_metric = PerformanceMetric(
            id="cpu_utilization",
            name="CPU Utilization",
            metric_type="gauge",
            threshold_warning=80.0,
            threshold_critical=95.0,
            optimization_target=70.0,
            unit="%"
        )
        
        # Memory usage
        memory_metric = PerformanceMetric(
            id="memory_usage",
            name="Memory Usage",
            metric_type="gauge",
            threshold_warning=85.0,
            threshold_critical=95.0,
            optimization_target=75.0,
            unit="%"
        )
        
        # Throughput
        throughput_metric = PerformanceMetric(
            id="throughput",
            name="Requests Per Second",
            metric_type="rate",
            threshold_warning=100.0,  # Below 100 RPS is warning
            threshold_critical=50.0,   # Below 50 RPS is critical
            optimization_target=500.0,  # Target 500 RPS
            unit="req/s"
        )
        
        # Register metrics
        for metric in [query_time_metric, cpu_metric, memory_metric, throughput_metric]:
            self.metrics[metric.id] = metric
    
    async def update_metric(self, metric_id: str, value: float):
        """Update a performance metric value."""
        if metric_id not in self.metrics:
            self.logger.warning(f"Unknown metric: {metric_id}")
            return
        
        self.current_values[metric_id] = value
        
        # Store in Redis for persistence
        if self.redis_client:
            await self.redis_client.setex(
                f"perf_metric:{metric_id}",
                300,  # 5 minutes
                json.dumps({
                    'value': value,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
        
        # Check if optimization is needed
        await self._check_optimization_triggers(metric_id, value)
    
    async def _check_optimization_triggers(self, metric_id: str, value: float):
        """Check if metric value triggers optimization recommendations."""
        metric = self.metrics[metric_id]
        
        # Check thresholds
        if value >= metric.threshold_critical:
            await self._generate_critical_optimization(metric_id, value)
        elif value >= metric.threshold_warning:
            await self._generate_warning_optimization(metric_id, value)
        elif value > metric.optimization_target * 1.2:  # 20% above target
            await self._generate_proactive_optimization(metric_id, value)
    
    async def _generate_critical_optimization(self, metric_id: str, value: float):
        """Generate critical optimization recommendation."""
        metric = self.metrics[metric_id]
        
        if metric_id == "query_response_time":
            recommendation = OptimizationRecommendation(
                id=str(uuid.uuid4()),
                optimization_type=OptimizationType.QUERY_OPTIMIZATION,
                title="Critical Query Performance Issue",
                description=f"Query response time is {value}ms, exceeding critical threshold of {metric.threshold_critical}ms",
                impact_estimate="high",
                implementation_effort="medium",
                actions=[
                    "Analyze slow query logs",
                    "Add missing indexes",
                    "Optimize query execution plans",
                    "Consider query caching"
                ],
                priority=1,
                estimated_improvement=50.0
            )
        
        elif metric_id == "cpu_utilization":
            recommendation = OptimizationRecommendation(
                id=str(uuid.uuid4()),
                optimization_type=OptimizationType.RESOURCE_OPTIMIZATION,
                title="Critical CPU Usage",
                description=f"CPU utilization is {value}%, exceeding critical threshold of {metric.threshold_critical}%",
                impact_estimate="high",
                implementation_effort="high",
                actions=[
                    "Scale up compute resources",
                    "Optimize CPU-intensive processes",
                    "Implement load balancing",
                    "Profile application performance"
                ],
                priority=1,
                estimated_improvement=30.0
            )
        
        else:
            # Generic critical optimization
            recommendation = OptimizationRecommendation(
                id=str(uuid.uuid4()),
                optimization_type=OptimizationType.RESOURCE_OPTIMIZATION,
                title=f"Critical {metric.name} Performance",
                description=f"{metric.name} value {value} exceeds critical threshold",
                impact_estimate="high",
                implementation_effort="medium",
                actions=["Investigate root cause", "Apply immediate fixes"],
                priority=1,
                estimated_improvement=25.0
            )
        
        await self._store_recommendation(recommendation)
    
    async def _generate_warning_optimization(self, metric_id: str, value: float):
        """Generate warning-level optimization recommendation."""
        metric = self.metrics[metric_id]
        
        recommendation = OptimizationRecommendation(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.RESOURCE_OPTIMIZATION,
            title=f"Performance Warning: {metric.name}",
            description=f"{metric.name} value {value} exceeds warning threshold of {metric.threshold_warning}",
            impact_estimate="medium",
            implementation_effort="low",
            actions=[
                "Monitor trend closely",
                "Plan optimization actions",
                "Review resource allocation"
            ],
            priority=3,
            estimated_improvement=15.0
        )
        
        await self._store_recommendation(recommendation)
    
    async def _generate_proactive_optimization(self, metric_id: str, value: float):
        """Generate proactive optimization recommendation."""
        metric = self.metrics[metric_id]
        
        recommendation = OptimizationRecommendation(
            id=str(uuid.uuid4()),
            optimization_type=OptimizationType.RESOURCE_OPTIMIZATION,
            title=f"Proactive Optimization: {metric.name}",
            description=f"{metric.name} is above optimal target, consider optimization",
            impact_estimate="low",
            implementation_effort="low",
            actions=[
                "Review current configuration",
                "Fine-tune parameters",
                "Consider preventive measures"
            ],
            priority=4,
            estimated_improvement=10.0
        )
        
        await self._store_recommendation(recommendation)
    
    async def _store_recommendation(self, recommendation: OptimizationRecommendation):
        """Store optimization recommendation."""
        # Avoid duplicate recommendations
        existing_similar = [
            r for r in self.recommendations.values()
            if (r.optimization_type == recommendation.optimization_type and
                not r.implemented and
                (datetime.utcnow() - r.created_at).total_seconds() < 3600)  # Within 1 hour
        ]
        
        if len(existing_similar) >= 2:  # Max 2 similar recommendations per hour
            return
        
        self.recommendations[recommendation.id] = recommendation
        self.engine_metrics['recommendations_generated'] += 1
        
        self.logger.info(f"Generated optimization recommendation: {recommendation.title}")
    
    async def get_recommendations(self, priority_filter: Optional[int] = None) -> List[OptimizationRecommendation]:
        """Get optimization recommendations."""
        recommendations = list(self.recommendations.values())
        
        if priority_filter:
            recommendations = [r for r in recommendations if r.priority <= priority_filter]
        
        # Sort by priority and creation time
        recommendations.sort(key=lambda r: (r.priority, r.created_at))
        
        return recommendations
    
    async def implement_optimization(self, recommendation_id: str) -> bool:
        """Mark optimization as implemented."""
        if recommendation_id not in self.recommendations:
            return False
        
        recommendation = self.recommendations[recommendation_id]
        recommendation.implemented = True
        
        # Track optimization
        self.engine_metrics['total_optimizations'] += 1
        self.engine_metrics['successful_optimizations'] += 1
        
        # Update average improvement
        total_opts = self.engine_metrics['successful_optimizations']
        current_avg = self.engine_metrics['average_improvement']
        self.engine_metrics['average_improvement'] = (
            (current_avg * (total_opts - 1) + recommendation.estimated_improvement) / total_opts
        )
        
        # Store in optimization history
        self.optimization_history.append({
            'recommendation_id': recommendation_id,
            'optimization_type': recommendation.optimization_type.value,
            'estimated_improvement': recommendation.estimated_improvement,
            'implemented_at': datetime.utcnow().isoformat()
        })
        
        self.logger.info(f"Implemented optimization: {recommendation.title}")
        return True
    
    async def analyze_performance_trends(self, metric_id: str, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends for a metric."""
        if metric_id not in self.metrics:
            return {}
        
        # This would analyze historical data from Redis/database
        # For now, return mock trend analysis
        
        current_value = self.current_values.get(metric_id, 0.0)
        metric = self.metrics[metric_id]
        
        return {
            'metric_id': metric_id,
            'metric_name': metric.name,
            'current_value': current_value,
            'target_value': metric.optimization_target,
            'trend': 'stable',  # Would be calculated from historical data
            'prediction_24h': current_value * 1.05,  # Mock prediction
            'recommendation': 'Monitor closely' if current_value > metric.optimization_target else 'Performance within target'
        }
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics_summary': {},
            'recommendations_summary': {
                'total': len(self.recommendations),
                'by_priority': {},
                'by_type': {}
            },
            'optimization_summary': self.engine_metrics.copy(),
            'trends': {}
        }
        
        # Metrics summary
        for metric_id, metric in self.metrics.items():
            current_value = self.current_values.get(metric_id, 0.0)
            status = "optimal"
            
            if current_value >= metric.threshold_critical:
                status = "critical"
            elif current_value >= metric.threshold_warning:
                status = "warning"
            elif current_value > metric.optimization_target:
                status = "suboptimal"
            
            report['metrics_summary'][metric_id] = {
                'name': metric.name,
                'current_value': current_value,
                'target_value': metric.optimization_target,
                'status': status,
                'unit': metric.unit
            }
        
        # Recommendations summary
        active_recommendations = [r for r in self.recommendations.values() if not r.implemented]
        
        for rec in active_recommendations:
            # By priority
            priority = rec.priority
            report['recommendations_summary']['by_priority'][priority] = (
                report['recommendations_summary']['by_priority'].get(priority, 0) + 1
            )
            
            # By type
            opt_type = rec.optimization_type.value
            report['recommendations_summary']['by_type'][opt_type] = (
                report['recommendations_summary']['by_type'].get(opt_type, 0) + 1
            )
        
        return report
    
    def get_engine_metrics(self) -> Dict[str, Any]:
        """Get optimization engine metrics."""
        return {
            **self.engine_metrics,
            'registered_metrics': len(self.metrics),
            'current_recommendations': len([r for r in self.recommendations.values() if not r.implemented]),
            'optimization_history_count': len(self.optimization_history)
        }


# Example usage
if __name__ == "__main__":
    async def main():
        engine = PerformanceOptimizationEngine(
            redis_url="redis://localhost:6379"
        )
        
        await engine.initialize()
        
        # Simulate performance metrics
        await engine.update_metric("query_response_time", 1500.0)  # Warning level
        await engine.update_metric("cpu_utilization", 97.0)       # Critical level
        await engine.update_metric("memory_usage", 75.0)          # Optimal
        await engine.update_metric("throughput", 45.0)            # Critical level
        
        # Get recommendations
        recommendations = await engine.get_recommendations(priority_filter=2)
        print(f"High priority recommendations: {len(recommendations)}")
        
        for rec in recommendations:
            print(f"- {rec.title}: {rec.description}")
        
        # Generate performance report
        report = await engine.generate_performance_report()
        print(f"\nPerformance report: {json.dumps(report, indent=2)}")
        
        # Implement an optimization
        if recommendations:
            await engine.implement_optimization(recommendations[0].id)
        
        # Get engine metrics
        metrics = engine.get_engine_metrics()
        print(f"\nEngine metrics: {metrics}")
    
    asyncio.run(main())