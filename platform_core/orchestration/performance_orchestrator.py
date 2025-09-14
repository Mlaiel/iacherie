"""
Performance Orchestrator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Performance Orchestrator - Enterprise Core Component
Performance optimization coordination system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive performance coordination capabilities including:
- Performance optimization coordination
- Resource utilization monitoring
- Bottleneck detection and resolution
- Performance tuning automation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import statistics
from collections import deque, defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMetricType(Enum):
    """Performance metric types"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    QUEUE_LENGTH = "queue_length"
    CONNECTION_COUNT = "connection_count"
    CACHE_HIT_RATE = "cache_hit_rate"


class PerformanceStatus(Enum):
    """Performance status levels"""
    OPTIMAL = "optimal"
    GOOD = "good"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    FAILING = "failing"


class OptimizationType(Enum):
    """Performance optimization types"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    CACHE_OPTIMIZATION = "cache_optimization"
    DATABASE_OPTIMIZATION = "database_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    CPU_OPTIMIZATION = "cpu_optimization"


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    service_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_type: PerformanceMetricType
    warning_threshold: float
    critical_threshold: float
    duration_seconds: int = 60
    enabled: bool = True


@dataclass
class PerformanceProfile:
    """Service performance profile"""
    service_id: str
    thresholds: List[PerformanceThreshold]
    optimization_enabled: bool = True
    auto_scaling_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BottleneckDetection:
    """Bottleneck detection result"""
    bottleneck_id: str
    service_id: str
    metric_type: PerformanceMetricType
    severity: PerformanceStatus
    detected_at: datetime
    description: str
    impact_score: float
    suggested_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationAction:
    """Performance optimization action"""
    action_id: str
    service_id: str
    optimization_type: OptimizationType
    parameters: Dict[str, Any]
    estimated_impact: float
    priority: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PerformanceReport:
    """Performance analysis report"""
    report_id: str
    service_id: Optional[str]
    generated_at: datetime
    time_range: Tuple[datetime, datetime]
    overall_status: PerformanceStatus
    metrics_summary: Dict[str, Any]
    bottlenecks: List[BottleneckDetection]
    optimizations: List[OptimizationAction]
    recommendations: List[str]


class PerformanceOrchestrator:
    """
    Enterprise Performance Orchestrator
    
    Manages comprehensive performance monitoring, optimization, and coordination
    across all platform services with intelligent bottleneck detection and
    automated optimization capabilities.
    """
    
    def __init__(self) -> None:
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.metrics_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.active_bottlenecks: Dict[str, BottleneckDetection] = {}
        self.optimization_queue: List[OptimizationAction] = []
        self.performance_history: List[PerformanceReport] = []
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "bottleneck_detected": [],
            "bottleneck_resolved": [],
            "optimization_applied": [],
            "threshold_exceeded": [],
            "performance_degraded": []
        }
        
        # Configuration
        self.monitoring_interval = 30  # seconds
        self.metrics_retention_hours = 24
        self.optimization_cooldown = timedelta(minutes=5)
        self.auto_optimization_enabled = True
        self.bottleneck_detection_enabled = True
        
        # Performance baselines
        self.performance_baselines: Dict[str, Dict[PerformanceMetricType, float]] = {}
        
        logger.info("Performance Orchestrator initialized")
    
    async def register_service(self, profile: PerformanceProfile) -> bool:
        """Register a service for performance monitoring"""
        try:
            self.performance_profiles[profile.service_id] = profile
            
            # Initialize metrics store
            if profile.service_id not in self.metrics_store:
                self.metrics_store[profile.service_id] = deque(maxlen=10000)
            
            # Start monitoring
            if profile.service_id not in self.monitoring_tasks:
                await self._start_monitoring(profile.service_id)
            
            logger.info(f"Service registered for performance monitoring: {profile.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {profile.service_id}: {e}")
            return False
    
    async def record_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric"""
        try:
            # Store metric
            self.metrics_store[metric.service_id].append(metric)
            
            # Check thresholds
            await self._check_thresholds(metric)
            
            # Update baselines
            await self._update_baseline(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    async def detect_bottlenecks(self, service_id: Optional[str] = None) -> List[BottleneckDetection]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        services_to_check = [service_id] if service_id else self.performance_profiles.keys()
        
        for svc_id in services_to_check:
            if svc_id not in self.metrics_store:
                continue
            
            # Analyze recent metrics
            recent_metrics = list(self.metrics_store[svc_id])[-100:]  # Last 100 metrics
            
            if not recent_metrics:
                continue
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_type[metric.metric_type].append(metric)
            
            # Detect bottlenecks for each metric type
            for metric_type, metrics in metrics_by_type.items():
                bottleneck = await self._analyze_bottleneck(svc_id, metric_type, metrics)
                if bottleneck:
                    bottlenecks.append(bottleneck)
        
        # Store newly detected bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck.bottleneck_id not in self.active_bottlenecks:
                self.active_bottlenecks[bottleneck.bottleneck_id] = bottleneck
                await self._trigger_event("bottleneck_detected", bottleneck.bottleneck_id)
        
        return bottlenecks
    
    async def optimize_performance(self, service_id: str) -> List[OptimizationAction]:
        """Generate and apply performance optimizations"""
        profile = self.performance_profiles.get(service_id)
        if not profile or not profile.optimization_enabled:
            return []
        
        optimizations = []
        
        try:
            # Analyze current performance
            current_metrics = await self._get_current_metrics(service_id)
            bottlenecks = await self.detect_bottlenecks(service_id)
            
            # Generate optimization actions
            for bottleneck in bottlenecks:
                actions = await self._generate_optimization_actions(bottleneck, current_metrics)
                optimizations.extend(actions)
            
            # Apply optimizations if auto-optimization is enabled
            if self.auto_optimization_enabled:
                for action in optimizations:
                    await self._apply_optimization(action)
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Performance optimization failed for {service_id}: {e}")
            return []
    
    async def generate_performance_report(
        self,
        service_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""
        if not time_range:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            time_range = (start_time, end_time)
        
        report_id = str(uuid.uuid4())
        
        # Gather metrics
        metrics_summary = await self._generate_metrics_summary(service_id, time_range)
        
        # Detect bottlenecks
        bottlenecks = await self.detect_bottlenecks(service_id)
        
        # Generate optimizations
        optimizations = []
        if service_id:
            optimizations = await self.optimize_performance(service_id)
        
        # Determine overall status
        overall_status = await self._calculate_overall_status(metrics_summary, bottlenecks)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_summary, bottlenecks)
        
        report = PerformanceReport(
            report_id=report_id,
            service_id=service_id,
            generated_at=datetime.utcnow(),
            time_range=time_range,
            overall_status=overall_status,
            metrics_summary=metrics_summary,
            bottlenecks=bottlenecks,
            optimizations=optimizations,
            recommendations=recommendations
        )
        
        self.performance_history.append(report)
        
        return report
    
    async def get_service_metrics(
        self,
        service_id: str,
        metric_type: Optional[PerformanceMetricType] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PerformanceMetric]:
        """Get service performance metrics"""
        if service_id not in self.metrics_store:
            return []
        
        metrics = list(self.metrics_store[service_id])
        
        # Filter by metric type
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # Filter by time range
        if time_range:
            start_time, end_time = time_range
            metrics = [m for m in metrics if start_time <= m.timestamp <= end_time]
        
        return metrics
    
    async def get_performance_status(self, service_id: str) -> Dict[str, Any]:
        """Get current performance status"""
        current_metrics = await self._get_current_metrics(service_id)
        bottlenecks = [b for b in self.active_bottlenecks.values() if b.service_id == service_id]
        
        # Calculate status
        status = PerformanceStatus.OPTIMAL
        if bottlenecks:
            max_severity = max(b.severity for b in bottlenecks)
            status = max_severity
        
        return {
            "service_id": service_id,
            "status": status.value,
            "current_metrics": {
                metric_type.value: values[-1] if values else 0
                for metric_type, values in current_metrics.items()
            },
            "active_bottlenecks": len(bottlenecks),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def set_performance_threshold(
        self,
        service_id: str,
        threshold: PerformanceThreshold
    ) -> bool:
        """Set performance threshold for service"""
        profile = self.performance_profiles.get(service_id)
        if not profile:
            return False
        
        # Update or add threshold
        for i, existing_threshold in enumerate(profile.thresholds):
            if existing_threshold.metric_type == threshold.metric_type:
                profile.thresholds[i] = threshold
                break
        else:
            profile.thresholds.append(threshold)
        
        profile.updated_at = datetime.utcnow()
        logger.info(f"Performance threshold updated for {service_id}: {threshold.metric_type.value}")
        return True
    
    async def enable_auto_optimization(self, service_id: str, enabled: bool = True) -> bool:
        """Enable/disable auto-optimization for service"""
        profile = self.performance_profiles.get(service_id)
        if not profile:
            return False
        
        profile.optimization_enabled = enabled
        profile.updated_at = datetime.utcnow()
        
        logger.info(f"Auto-optimization {'enabled' if enabled else 'disabled'} for {service_id}")
        return True
    
    async def add_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Add event handler"""
        if event_type not in self.event_handlers:
            return False
        
        self.event_handlers[event_type].append(handler)
        return True
    
    # Private methods
    
    async def _start_monitoring(self, service_id -> None: str) -> None:
        """Start monitoring task for service"""
        async def monitoring_loop() -> None:
            while True:
                try:
                    if service_id not in self.performance_profiles:
                        break
                    
                    # Collect metrics (simulated)
                    await self._collect_system_metrics(service_id)
                    
                    # Check for bottlenecks
                    if self.bottleneck_detection_enabled:
                        await self.detect_bottlenecks(service_id)
                    
                    await asyncio.sleep(self.monitoring_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Monitoring error for {service_id}: {e}")
                    await asyncio.sleep(self.monitoring_interval)
        
        task = asyncio.create_task(monitoring_loop())
        self.monitoring_tasks[service_id] = task
    
    async def _collect_system_metrics(self, service_id -> None: str) -> None:
        """Collect system metrics (simulated)"""
        import random
        
        # Simulate metric collection
        metrics = [
            PerformanceMetric(
                PerformanceMetricType.CPU_USAGE,
                random.uniform(10, 90),
                datetime.utcnow(),
                service_id
            ),
            PerformanceMetric(
                PerformanceMetricType.MEMORY_USAGE,
                random.uniform(20, 80),
                datetime.utcnow(),
                service_id
            ),
            PerformanceMetric(
                PerformanceMetricType.RESPONSE_TIME,
                random.uniform(50, 500),
                datetime.utcnow(),
                service_id
            )
        ]
        
        for metric in metrics:
            await self.record_metric(metric)
    
    async def _check_thresholds(self, metric -> None: PerformanceMetric) -> None:
        """Check if metric exceeds thresholds"""
        profile = self.performance_profiles.get(metric.service_id)
        if not profile:
            return
        
        for threshold in profile.thresholds:
            if threshold.metric_type != metric.metric_type or not threshold.enabled:
                continue
            
            if metric.value >= threshold.critical_threshold:
                await self._trigger_event("threshold_exceeded", 
                                          f"{metric.service_id}:{metric.metric_type.value}:critical")
            elif metric.value >= threshold.warning_threshold:
                await self._trigger_event("threshold_exceeded", 
                                          f"{metric.service_id}:{metric.metric_type.value}:warning")
    
    async def _update_baseline(self, metric -> None: PerformanceMetric) -> None:
        """Update performance baseline"""
        if metric.service_id not in self.performance_baselines:
            self.performance_baselines[metric.service_id] = {}
        
        # Simple exponential moving average
        current_baseline = self.performance_baselines[metric.service_id].get(metric.metric_type, metric.value)
        alpha = 0.1  # Smoothing factor
        new_baseline = alpha * metric.value + (1 - alpha) * current_baseline
        
        self.performance_baselines[metric.service_id][metric.metric_type] = new_baseline
    
    async def _analyze_bottleneck(
        self,
        service_id: str,
        metric_type: PerformanceMetricType,
        metrics: List[PerformanceMetric]
    ) -> Optional[BottleneckDetection]:
        """Analyze metrics for bottlenecks"""
        if len(metrics) < 10:  # Need sufficient data
            return None
        
        values = [m.value for m in metrics]
        
        # Calculate statistics
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        recent_avg = statistics.mean(values[-5:])  # Last 5 measurements
        
        # Get baseline
        baseline = self.performance_baselines.get(service_id, {}).get(metric_type, mean_value)
        
        # Detect significant deviation
        threshold_multiplier = 2.0
        if recent_avg > baseline * threshold_multiplier or recent_avg > mean_value + 2 * std_dev:
            severity = PerformanceStatus.CRITICAL if recent_avg > baseline * 3 else PerformanceStatus.DEGRADED
            
            bottleneck_id = f"{service_id}:{metric_type.value}:{int(datetime.utcnow().timestamp())}"
            
            return BottleneckDetection(
                bottleneck_id=bottleneck_id,
                service_id=service_id,
                metric_type=metric_type,
                severity=severity,
                detected_at=datetime.utcnow(),
                description=f"High {metric_type.value}: {recent_avg:.2f} (baseline: {baseline:.2f})",
                impact_score=min((recent_avg / baseline) * 100, 100),
                suggested_actions=self._get_suggested_actions(metric_type, severity)
            )
        
        return None
    
    def _get_suggested_actions(self, metric_type: PerformanceMetricType, severity: PerformanceStatus) -> List[str]:
        """Get suggested actions for bottleneck"""
        actions = {
            PerformanceMetricType.CPU_USAGE: [
                "Scale out to more instances",
                "Optimize CPU-intensive operations",
                "Enable CPU auto-scaling"
            ],
            PerformanceMetricType.MEMORY_USAGE: [
                "Increase memory allocation",
                "Optimize memory usage",
                "Enable memory-based scaling"
            ],
            PerformanceMetricType.RESPONSE_TIME: [
                "Add caching layer",
                "Optimize database queries",
                "Scale out application instances"
            ]
        }
        
        return actions.get(metric_type, ["Monitor and investigate further"])
    
    async def _generate_optimization_actions(
        self,
        bottleneck: BottleneckDetection,
        current_metrics: Dict[PerformanceMetricType, List[float]]
    ) -> List[OptimizationAction]:
        """Generate optimization actions for bottleneck"""
        actions = []
        
        if bottleneck.metric_type == PerformanceMetricType.CPU_USAGE:
            if bottleneck.severity in [PerformanceStatus.CRITICAL, PerformanceStatus.DEGRADED]:
                actions.append(OptimizationAction(
                    action_id=str(uuid.uuid4()),
                    service_id=bottleneck.service_id,
                    optimization_type=OptimizationType.SCALE_OUT,
                    parameters={"target_instances": 2},
                    estimated_impact=30.0,
                    priority=1
                ))
        
        elif bottleneck.metric_type == PerformanceMetricType.MEMORY_USAGE:
            actions.append(OptimizationAction(
                action_id=str(uuid.uuid4()),
                service_id=bottleneck.service_id,
                optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
                parameters={"increase_memory": "25%"},
                estimated_impact=25.0,
                priority=2
            ))
        
        elif bottleneck.metric_type == PerformanceMetricType.RESPONSE_TIME:
            actions.append(OptimizationAction(
                action_id=str(uuid.uuid4()),
                service_id=bottleneck.service_id,
                optimization_type=OptimizationType.CACHE_OPTIMIZATION,
                parameters={"enable_caching": True},
                estimated_impact=40.0,
                priority=1
            ))
        
        return actions
    
    async def _apply_optimization(self, action: OptimizationAction) -> bool:
        """Apply optimization action"""
        try:
            logger.info(f"Applying optimization: {action.optimization_type.value} for {action.service_id}")
            
            # In a real implementation, this would trigger actual optimizations
            # For now, we simulate the action
            await asyncio.sleep(1)
            
            await self._trigger_event("optimization_applied", action.action_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization {action.action_id}: {e}")
            return False
    
    async def _get_current_metrics(self, service_id: str) -> Dict[PerformanceMetricType, List[float]]:
        """Get current metrics for service"""
        if service_id not in self.metrics_store:
            return {}
        
        recent_metrics = list(self.metrics_store[service_id])[-50:]  # Last 50 metrics
        
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
        
        return dict(metrics_by_type)
    
    async def _generate_metrics_summary(
        self,
        service_id: Optional[str],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Generate metrics summary for report"""
        summary = {}
        
        services = [service_id] if service_id else self.performance_profiles.keys()
        
        for svc_id in services:
            metrics = await self.get_service_metrics(svc_id, time_range=time_range)
            
            if not metrics:
                continue
            
            metrics_by_type = defaultdict(list)
            for metric in metrics:
                metrics_by_type[metric.metric_type].append(metric.value)
            
            svc_summary = {}
            for metric_type, values in metrics_by_type.items():
                svc_summary[metric_type.value] = {
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
            
            summary[svc_id] = svc_summary
        
        return summary
    
    async def _calculate_overall_status(
        self,
        metrics_summary: Dict[str, Any],
        bottlenecks: List[BottleneckDetection]
    ) -> PerformanceStatus:
        """Calculate overall performance status"""
        if not bottlenecks:
            return PerformanceStatus.OPTIMAL
        
        # Find worst severity
        worst_severity = max(b.severity for b in bottlenecks)
        return worst_severity
    
    async def _generate_recommendations(
        self,
        metrics_summary: Dict[str, Any],
        bottlenecks: List[BottleneckDetection]
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if bottlenecks:
            recommendations.append("Address active bottlenecks to improve performance")
            
            cpu_bottlenecks = [b for b in bottlenecks if b.metric_type == PerformanceMetricType.CPU_USAGE]
            if cpu_bottlenecks:
                recommendations.append("Consider horizontal scaling for CPU-bound services")
            
            memory_bottlenecks = [b for b in bottlenecks if b.metric_type == PerformanceMetricType.MEMORY_USAGE]
            if memory_bottlenecks:
                recommendations.append("Optimize memory usage or increase memory allocation")
            
            response_time_bottlenecks = [b for b in bottlenecks if b.metric_type == PerformanceMetricType.RESPONSE_TIME]
            if response_time_bottlenecks:
                recommendations.append("Implement caching and optimize database queries")
        else:
            recommendations.append("Performance is optimal - maintain current configuration")
        
        return recommendations
    
    async def _trigger_event(self, event_type -> None: str, event_data -> None: str) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
performance_orchestrator = PerformanceOrchestrator()


# Convenience functions
async def register_service(
    service_id: str,
    thresholds: Optional[List[PerformanceThreshold]] = None
) -> bool:
    """Register service for performance monitoring"""
    profile = PerformanceProfile(
        service_id=service_id,
        thresholds=thresholds or []
    )
    return await performance_orchestrator.register_service(profile)


async def record_metric(
    service_id: str,
    metric_type: PerformanceMetricType,
    value: float
) -> bool:
    """Record performance metric"""
    metric = PerformanceMetric(
        metric_type=metric_type,
        value=value,
        timestamp=datetime.utcnow(),
        service_id=service_id
    )
    return await performance_orchestrator.record_metric(metric)


async def get_performance_report(service_id: Optional[str] = None) -> PerformanceReport:
    """Generate performance report"""
    return await performance_orchestrator.generate_performance_report(service_id)


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Register a service
        await register_service("api-service")
        
        # Record some metrics
        await record_metric("api-service", PerformanceMetricType.CPU_USAGE, 75.0)
        await record_metric("api-service", PerformanceMetricType.MEMORY_USAGE, 60.0)
        await record_metric("api-service", PerformanceMetricType.RESPONSE_TIME, 250.0)
        
        # Generate report
        report = await get_performance_report("api-service")
        print(f"Performance Report: {report.overall_status.value}")
        print(f"Bottlenecks: {len(report.bottlenecks)}")
        print(f"Recommendations: {report.recommendations}")
    
    asyncio.run(main())