"""⚡ Real-Time Performance Profiler
==================================

Advanced real-time performance profiling system for the Ainflue Creator Economy platform.
Provides live profiling dashboard, real-time bottleneck detection, and dynamic optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import uuid

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class RealTimeMetricType(Enum):
    """Types of real-time metrics"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DATABASE_CONNECTIONS = "database_connections"
    CACHE_HIT_RATE = "cache_hit_rate"
    QUEUE_DEPTH = "queue_depth"
    USER_SESSIONS = "user_sessions"
    CONCURRENT_USERS = "concurrent_users"
    REVENUE_RATE = "revenue_rate"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationStrategy(Enum):
    """Real-time optimization strategies"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    LOAD_BALANCE = "load_balance"
    CACHE_WARMING = "cache_warming"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMITING = "rate_limiting"
    RESOURCE_REALLOCATION = "resource_reallocation"
    AUTOMATIC_FAILOVER = "automatic_failover"


@dataclass
class RealTimeMetric:
    """Real-time metric data point"""
    metric_id: str
    metric_type: RealTimeMetricType
    component_name: str
    
    # Metric value
    value: float
    unit: str
    
    # Thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    
    # Context
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Trend analysis
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable"
    trend_strength: float = 0.0  # 0-1
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RealTimeAlert:
    """Real-time alert"""
    alert_id: str
    metric_type: RealTimeMetricType
    component_name: str
    severity: AlertSeverity
    
    # Alert details
    message: str
    current_value: float
    threshold_value: float
    
    # Impact analysis
    business_impact: str
    technical_impact: str
    user_impact: str
    
    # Recommendations
    immediate_actions: List[str]
    optimization_suggestions: List[str]
    
    # Status
    acknowledged: bool = False
    resolved: bool = False
    auto_resolved: bool = False
    
    # Timing
    first_occurrence: datetime = field(default_factory=datetime.utcnow)
    last_occurrence: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HotPath:
    """Hot path identification"""
    path_id: str
    component_chain: List[str]
    
    # Performance characteristics
    execution_frequency: int
    average_response_time_ms: float
    resource_consumption: Dict[str, float]
    
    # Optimization potential
    optimization_score: float  # 0-100
    bottleneck_points: List[str]
    optimization_opportunities: List[str]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DynamicOptimization:
    """Dynamic optimization action"""
    optimization_id: str
    strategy: OptimizationStrategy
    target_component: str
    
    # Optimization details
    trigger_condition: str
    optimization_parameters: Dict[str, Any]
    expected_improvement: Dict[str, float]
    
    # Execution
    executed: bool = False
    execution_time: Optional[datetime] = None
    execution_duration_ms: Optional[float] = None
    
    # Results
    success: bool = False
    actual_improvement: Optional[Dict[str, float]] = None
    side_effects: List[str] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RealTimeProfiler:
    """Advanced real-time performance profiler"""
    
    def __init__(self,
                 sampling_interval_ms: int = 100,
                 dashboard_update_interval_ms: int = 1000,
                 max_history_size: int = 50000,
                 enable_auto_optimization: bool = True,
                 enable_hot_path_detection: bool = True):
        """
        Initialize real-time profiler
        
        Args:
            sampling_interval_ms: Metric sampling interval in milliseconds
            dashboard_update_interval_ms: Dashboard update interval in milliseconds
            max_history_size: Maximum number of metrics to store
            enable_auto_optimization: Enable automatic optimization
            enable_hot_path_detection: Enable hot path detection
        """
        self.sampling_interval_ms = sampling_interval_ms
        self.dashboard_update_interval_ms = dashboard_update_interval_ms
        self.max_history_size = max_history_size
        self.enable_auto_optimization = enable_auto_optimization
        self.enable_hot_path_detection = enable_hot_path_detection
        
        # Real-time data storage
        self.metrics_buffer: deque = deque(maxlen=max_history_size)
        self.current_metrics: Dict[str, RealTimeMetric] = {}
        self.metric_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Alerting system
        self.active_alerts: Dict[str, RealTimeAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # Hot path detection
        self.hot_paths: Dict[str, HotPath] = {}
        self.execution_traces: deque = deque(maxlen=100000)
        
        # Optimization system
        self.optimization_history: deque = deque(maxlen=1000)
        self.pending_optimizations: List[DynamicOptimization] = []
        
        # Streaming connections (WebSocket clients)
        self.streaming_clients: Set[Any] = set()
        
        # Component registration
        self.registered_components: Dict[str, Dict[str, Any]] = {}
        
        # Performance thresholds
        self.thresholds = {
            RealTimeMetricType.RESPONSE_TIME: {"warning": 500.0, "critical": 1000.0},
            RealTimeMetricType.ERROR_RATE: {"warning": 1.0, "critical": 5.0},
            RealTimeMetricType.CPU_USAGE: {"warning": 70.0, "critical": 90.0},
            RealTimeMetricType.MEMORY_USAGE: {"warning": 80.0, "critical": 95.0},
            RealTimeMetricType.CACHE_HIT_RATE: {"warning": 80.0, "critical": 60.0},
            RealTimeMetricType.QUEUE_DEPTH: {"warning": 100, "critical": 500}
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.sampling_task: Optional[asyncio.Task] = None
        self.dashboard_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("RealTimeProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'realtime_metric_value': Gauge(
                'ainflue_realtime_metric_value',
                'Real-time metric values',
                ['metric_type', 'component', 'unit']
            ),
            'realtime_alerts': Gauge(
                'ainflue_realtime_alerts_active',
                'Number of active real-time alerts',
                ['severity', 'component']
            ),
            'hot_paths': Gauge(
                'ainflue_hot_paths_detected',
                'Number of detected hot paths',
                ['component']
            ),
            'dynamic_optimizations': Counter(
                'ainflue_dynamic_optimizations_total',
                'Total dynamic optimizations performed',
                ['strategy', 'component', 'success']
            ),
            'streaming_clients': Gauge(
                'ainflue_realtime_streaming_clients',
                'Number of active streaming clients'
            )
        }
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            logger.warning("Real-time monitoring already running")
            return
        
        self.is_monitoring = True
        
        # Start sampling task
        self.sampling_task = asyncio.create_task(self._sampling_loop())
        
        # Start dashboard update task
        self.dashboard_task = asyncio.create_task(self._dashboard_update_loop())
        
        # Start optimization task if enabled
        if self.enable_auto_optimization:
            self.optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        # Cancel tasks
        for task in [self.sampling_task, self.dashboard_task, self.optimization_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Real-time monitoring stopped")
    
    async def register_component(self, 
                                component_name: str, 
                                component_type: str,
                                metric_types: List[RealTimeMetricType],
                                thresholds: Optional[Dict[RealTimeMetricType, Dict[str, float]]] = None):
        """Register a component for real-time monitoring"""
        with self._lock:
            self.registered_components[component_name] = {
                "type": component_type,
                "metric_types": metric_types,
                "thresholds": thresholds or {},
                "registered_at": datetime.utcnow()
            }
        
        logger.info(f"Component registered for real-time monitoring: {component_name}")
    
    async def add_metric(self, metric: RealTimeMetric):
        """Add a real-time metric"""
        # Apply thresholds if not set
        if metric.warning_threshold is None or metric.critical_threshold is None:
            component_thresholds = self.registered_components.get(metric.component_name, {}).get("thresholds", {})
            metric_thresholds = component_thresholds.get(metric.metric_type, self.thresholds.get(metric.metric_type, {}))
            
            metric.warning_threshold = metric.warning_threshold or metric_thresholds.get("warning")
            metric.critical_threshold = metric.critical_threshold or metric_thresholds.get("critical")
        
        # Calculate trend
        metric = await self._calculate_trend(metric)
        
        # Store metric
        with self._lock:
            self.metrics_buffer.append(metric)
            self.current_metrics[f"{metric.component_name}_{metric.metric_type.value}"] = metric
            
            # Update trend data
            trend_key = f"{metric.component_name}_{metric.metric_type.value}"
            self.metric_trends[trend_key].append(metric.value)
            if len(self.metric_trends[trend_key]) > 100:  # Keep last 100 values
                self.metric_trends[trend_key] = self.metric_trends[trend_key][-100:]
        
        # Update Prometheus metrics
        self.prometheus_metrics['realtime_metric_value'].labels(
            metric_type=metric.metric_type.value,
            component=metric.component_name,
            unit=metric.unit
        ).set(metric.value)
        
        # Check for alerts
        await self._check_alerts(metric)
        
        # Hot path detection
        if self.enable_hot_path_detection:
            await self._detect_hot_paths(metric)
        
        # Trigger optimizations
        if self.enable_auto_optimization:
            await self._trigger_optimizations(metric)
    
    async def _calculate_trend(self, metric: RealTimeMetric) -> RealTimeMetric:
        """Calculate trend for metric"""
        trend_key = f"{metric.component_name}_{metric.metric_type.value}"
        
        with self._lock:
            recent_values = self.metric_trends.get(trend_key, [])
            
            if len(recent_values) >= 5:  # Need at least 5 points for trend
                # Simple linear regression for trend
                n = len(recent_values)
                x_vals = list(range(n))
                y_vals = recent_values
                
                # Calculate slope
                x_mean = sum(x_vals) / n
                y_mean = sum(y_vals) / n
                
                numerator = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
                denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
                
                if denominator != 0:
                    slope = numerator / denominator
                    
                    # Determine trend direction and strength
                    if abs(slope) < 0.1:
                        metric.trend_direction = "stable"
                        metric.trend_strength = 0.0
                    elif slope > 0:
                        metric.trend_direction = "increasing"
                        metric.trend_strength = min(1.0, abs(slope) / max(y_vals))
                    else:
                        metric.trend_direction = "decreasing"
                        metric.trend_strength = min(1.0, abs(slope) / max(y_vals))
        
        return metric
    
    async def _check_alerts(self, metric: RealTimeMetric):
        """Check if metric triggers alerts"""
        alert_key = f"{metric.component_name}_{metric.metric_type.value}"
        current_time = datetime.utcnow()
        
        # Determine if alert should be triggered
        alert_triggered = False
        severity = None
        threshold_value = None
        
        if metric.critical_threshold is not None and metric.value >= metric.critical_threshold:
            alert_triggered = True
            severity = AlertSeverity.CRITICAL
            threshold_value = metric.critical_threshold
        elif metric.warning_threshold is not None and metric.value >= metric.warning_threshold:
            alert_triggered = True
            severity = AlertSeverity.HIGH
            threshold_value = metric.warning_threshold
        
        if alert_triggered:
            # Create or update alert
            if alert_key in self.active_alerts:
                # Update existing alert
                alert = self.active_alerts[alert_key]
                alert.last_occurrence = current_time
                alert.current_value = metric.value
                if alert.severity != severity:
                    alert.severity = severity
                    logger.warning(f"Alert severity changed: {alert_key} - {severity.value}")
            else:
                # Create new alert
                alert = RealTimeAlert(
                    alert_id=f"alert_{int(time.time())}",
                    metric_type=metric.metric_type,
                    component_name=metric.component_name,
                    severity=severity,
                    message=f"{metric.metric_type.value} exceeded threshold: {metric.value} {metric.unit}",
                    current_value=metric.value,
                    threshold_value=threshold_value,
                    business_impact=self._assess_business_impact(metric),
                    technical_impact=self._assess_technical_impact(metric),
                    user_impact=self._assess_user_impact(metric),
                    immediate_actions=self._get_immediate_actions(metric),
                    optimization_suggestions=self._get_optimization_suggestions(metric)
                )
                
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                
                # Update Prometheus metrics
                self.prometheus_metrics['realtime_alerts'].labels(
                    severity=severity.value,
                    component=metric.component_name
                ).inc()
                
                logger.warning(f"New alert triggered: {alert.message}")
        else:
            # Check if existing alert should be resolved
            if alert_key in self.active_alerts:
                alert = self.active_alerts[alert_key]
                alert.resolved = True
                alert.auto_resolved = True
                alert.resolution_time = current_time
                
                del self.active_alerts[alert_key]
                
                # Update Prometheus metrics
                self.prometheus_metrics['realtime_alerts'].labels(
                    severity=alert.severity.value,
                    component=metric.component_name
                ).dec()
                
                logger.info(f"Alert auto-resolved: {alert_key}")
    
    def _assess_business_impact(self, metric: RealTimeMetric) -> str:
        """Assess business impact of metric threshold breach"""
        impact_map = {
            RealTimeMetricType.RESPONSE_TIME: "User experience degradation, potential revenue loss",
            RealTimeMetricType.ERROR_RATE: "Service reliability issues, customer satisfaction impact",
            RealTimeMetricType.CPU_USAGE: "System performance bottleneck, scaling needed",
            RealTimeMetricType.MEMORY_USAGE: "Memory pressure, potential service instability",
            RealTimeMetricType.REVENUE_RATE: "Direct revenue impact, immediate attention required"
        }
        return impact_map.get(metric.metric_type, "Performance impact on Creator Economy platform")
    
    def _assess_technical_impact(self, metric: RealTimeMetric) -> str:
        """Assess technical impact of metric threshold breach"""
        impact_map = {
            RealTimeMetricType.RESPONSE_TIME: "Increased latency affecting user interactions",
            RealTimeMetricType.ERROR_RATE: "Service failures requiring investigation",
            RealTimeMetricType.CPU_USAGE: "High CPU utilization affecting system performance",
            RealTimeMetricType.MEMORY_USAGE: "Memory pressure risking system stability",
            RealTimeMetricType.CACHE_HIT_RATE: "Poor cache performance affecting response times"
        }
        return impact_map.get(metric.metric_type, "Technical performance degradation")
    
    def _assess_user_impact(self, metric: RealTimeMetric) -> str:
        """Assess user impact of metric threshold breach"""
        impact_map = {
            RealTimeMetricType.RESPONSE_TIME: "Slow page loads and delayed interactions",
            RealTimeMetricType.ERROR_RATE: "Failed requests and service unavailability",
            RealTimeMetricType.CPU_USAGE: "Sluggish application performance",
            RealTimeMetricType.MEMORY_USAGE: "Potential application crashes or freezes",
            RealTimeMetricType.USER_SESSIONS: "Reduced platform engagement"
        }
        return impact_map.get(metric.metric_type, "Degraded user experience")
    
    def _get_immediate_actions(self, metric: RealTimeMetric) -> List[str]:
        """Get immediate actions for metric threshold breach"""
        actions_map = {
            RealTimeMetricType.RESPONSE_TIME: [
                "Check for database slow queries",
                "Review application logs for errors",
                "Monitor resource utilization",
                "Consider scaling up resources"
            ],
            RealTimeMetricType.ERROR_RATE: [
                "Investigate error logs immediately",
                "Check service health endpoints",
                "Verify external dependencies",
                "Consider enabling circuit breakers"
            ],
            RealTimeMetricType.CPU_USAGE: [
                "Scale up CPU resources",
                "Identify CPU-intensive processes",
                "Implement load balancing",
                "Consider horizontal scaling"
            ],
            RealTimeMetricType.MEMORY_USAGE: [
                "Increase memory allocation",
                "Check for memory leaks",
                "Restart affected services if necessary",
                "Monitor garbage collection"
            ]
        }
        return actions_map.get(metric.metric_type, ["Investigate performance issue", "Monitor system health"])
    
    def _get_optimization_suggestions(self, metric: RealTimeMetric) -> List[str]:
        """Get optimization suggestions for metric"""
        suggestions_map = {
            RealTimeMetricType.RESPONSE_TIME: [
                "Implement response caching",
                "Optimize database queries",
                "Use CDN for static assets",
                "Implement lazy loading"
            ],
            RealTimeMetricType.ERROR_RATE: [
                "Implement retry logic with exponential backoff",
                "Add circuit breaker patterns",
                "Improve error handling",
                "Enhance monitoring and alerting"
            ],
            RealTimeMetricType.CACHE_HIT_RATE: [
                "Review cache key strategies",
                "Optimize cache TTL settings",
                "Implement cache warming",
                "Consider cache partitioning"
            ]
        }
        return suggestions_map.get(metric.metric_type, ["Review component performance", "Consider optimization opportunities"])
    
    async def _detect_hot_paths(self, metric: RealTimeMetric):
        """Detect hot paths based on metric patterns"""
        if metric.metric_type == RealTimeMetricType.RESPONSE_TIME:
            # Simplified hot path detection
            if metric.value > 100.0:  # Threshold for hot path
                path_id = f"hotpath_{metric.component_name}_{int(time.time())}"
                
                hot_path = HotPath(
                    path_id=path_id,
                    component_chain=[metric.component_name],
                    execution_frequency=1,  # Simplified
                    average_response_time_ms=metric.value,
                    resource_consumption={"cpu": 0.0, "memory": 0.0},
                    optimization_score=min(100.0, metric.value / 10.0),
                    bottleneck_points=[metric.component_name],
                    optimization_opportunities=[
                        "Optimize component performance",
                        "Consider caching strategies",
                        "Review algorithm efficiency"
                    ]
                )
                
                self.hot_paths[path_id] = hot_path
                
                # Update Prometheus metrics
                self.prometheus_metrics['hot_paths'].labels(
                    component=metric.component_name
                ).inc()
    
    async def _trigger_optimizations(self, metric: RealTimeMetric):
        """Trigger automatic optimizations based on metrics"""
        if metric.value > (metric.critical_threshold or float('inf')):
            # Create optimization based on metric type
            optimization = None
            
            if metric.metric_type == RealTimeMetricType.CPU_USAGE and metric.value > 90.0:
                optimization = DynamicOptimization(
                    optimization_id=f"opt_{int(time.time())}",
                    strategy=OptimizationStrategy.SCALE_UP,
                    target_component=metric.component_name,
                    trigger_condition=f"CPU usage > 90%: {metric.value}%",
                    optimization_parameters={"scale_factor": 1.5, "target_cpu": 70.0},
                    expected_improvement={"cpu_reduction_percent": 30.0}
                )
            
            elif metric.metric_type == RealTimeMetricType.RESPONSE_TIME and metric.value > 1000.0:
                optimization = DynamicOptimization(
                    optimization_id=f"opt_{int(time.time())}",
                    strategy=OptimizationStrategy.CACHE_WARMING,
                    target_component=metric.component_name,
                    trigger_condition=f"Response time > 1000ms: {metric.value}ms",
                    optimization_parameters={"cache_size": "increased", "warming_strategy": "proactive"},
                    expected_improvement={"response_time_reduction_percent": 40.0}
                )
            
            if optimization:
                self.pending_optimizations.append(optimization)
                logger.info(f"Optimization triggered: {optimization.strategy.value} for {optimization.target_component}")
    
    async def _sampling_loop(self):
        """Background sampling loop"""
        while self.is_monitoring:
            try:
                # Sample system metrics
                await self._sample_system_metrics()
                
                # Sleep for sampling interval
                await asyncio.sleep(self.sampling_interval_ms / 1000.0)
                
            except Exception as e:
                logger.error(f"Error in sampling loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _dashboard_update_loop(self):
        """Background dashboard update loop"""
        while self.is_monitoring:
            try:
                # Update streaming clients
                await self._update_streaming_clients()
                
                # Sleep for dashboard update interval
                await asyncio.sleep(self.dashboard_update_interval_ms / 1000.0)
                
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _optimization_loop(self):
        """Background optimization execution loop"""
        while self.is_monitoring:
            try:
                # Execute pending optimizations
                await self._execute_pending_optimizations()
                
                # Sleep for optimization check interval
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _sample_system_metrics(self):
        """Sample system-level metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_metric = RealTimeMetric(
                metric_id=f"cpu_{int(time.time() * 1000)}",
                metric_type=RealTimeMetricType.CPU_USAGE,
                component_name="system",
                value=psutil.cpu_percent(),
                unit="percent"
            )
            await self.add_metric(cpu_metric)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_metric = RealTimeMetric(
                metric_id=f"memory_{int(time.time() * 1000)}",
                metric_type=RealTimeMetricType.MEMORY_USAGE,
                component_name="system",
                value=memory.percent,
                unit="percent"
            )
            await self.add_metric(memory_metric)
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.warning(f"Error sampling system metrics: {e}")
    
    async def _update_streaming_clients(self):
        """Update streaming dashboard clients"""
        if not self.streaming_clients:
            return
        
        try:
            # Prepare dashboard data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    key: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "trend_direction": metric.trend_direction,
                        "trend_strength": metric.trend_strength
                    }
                    for key, metric in self.current_metrics.items()
                },
                "alerts": [
                    {
                        "id": alert.alert_id,
                        "component": alert.component_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "current_value": alert.current_value
                    }
                    for alert in self.active_alerts.values()
                ],
                "hot_paths": len(self.hot_paths),
                "pending_optimizations": len(self.pending_optimizations)
            }
            
            # Send to all connected clients (would be WebSocket connections)
            for client in list(self.streaming_clients):
                try:
                    # In a real implementation, this would send via WebSocket
                    # await client.send_json(dashboard_data)
                    pass
                except Exception as e:
                    logger.warning(f"Failed to update streaming client: {e}")
                    self.streaming_clients.discard(client)
            
            # Update Prometheus metrics
            self.prometheus_metrics['streaming_clients'].set(len(self.streaming_clients))
            
        except Exception as e:
            logger.error(f"Error updating streaming clients: {e}")
    
    async def _execute_pending_optimizations(self):
        """Execute pending optimizations"""
        if not self.pending_optimizations:
            return
        
        # Execute one optimization at a time
        optimization = self.pending_optimizations.pop(0)
        
        try:
            start_time = time.time()
            
            # Execute optimization based on strategy
            success = await self._execute_optimization(optimization)
            
            end_time = time.time()
            optimization.executed = True
            optimization.execution_time = datetime.utcnow()
            optimization.execution_duration_ms = (end_time - start_time) * 1000
            optimization.success = success
            
            # Store in history
            self.optimization_history.append(optimization)
            
            # Update Prometheus metrics
            self.prometheus_metrics['dynamic_optimizations'].labels(
                strategy=optimization.strategy.value,
                component=optimization.target_component,
                success=str(success).lower()
            ).inc()
            
            if success:
                logger.info(f"Optimization executed successfully: {optimization.optimization_id}")
            else:
                logger.warning(f"Optimization failed: {optimization.optimization_id}")
            
        except Exception as e:
            optimization.success = False
            optimization.side_effects.append(f"Execution error: {str(e)}")
            logger.error(f"Error executing optimization {optimization.optimization_id}: {e}")
    
    async def _execute_optimization(self, optimization: DynamicOptimization) -> bool:
        """Execute a specific optimization"""
        try:
            if optimization.strategy == OptimizationStrategy.SCALE_UP:
                # Simulate scaling up
                await asyncio.sleep(0.1)
                logger.info(f"Scaling up {optimization.target_component}")
                return True
            
            elif optimization.strategy == OptimizationStrategy.CACHE_WARMING:
                # Simulate cache warming
                await asyncio.sleep(0.05)
                logger.info(f"Cache warming for {optimization.target_component}")
                return True
            
            elif optimization.strategy == OptimizationStrategy.LOAD_BALANCE:
                # Simulate load balancing
                await asyncio.sleep(0.02)
                logger.info(f"Load balancing for {optimization.target_component}")
                return True
            
            # Default case
            return False
            
        except Exception as e:
            logger.error(f"Error in optimization execution: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        with self._lock:
            return {
                "current_metrics": {
                    key: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "trend_direction": metric.trend_direction,
                        "trend_strength": metric.trend_strength,
                        "warning_threshold": metric.warning_threshold,
                        "critical_threshold": metric.critical_threshold,
                        "timestamp": metric.timestamp.isoformat()
                    }
                    for key, metric in self.current_metrics.items()
                },
                "active_alerts": [
                    {
                        "id": alert.alert_id,
                        "component": alert.component_name,
                        "metric_type": alert.metric_type.value,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "current_value": alert.current_value,
                        "threshold_value": alert.threshold_value,
                        "business_impact": alert.business_impact,
                        "immediate_actions": alert.immediate_actions,
                        "first_occurrence": alert.first_occurrence.isoformat(),
                        "last_occurrence": alert.last_occurrence.isoformat() if alert.last_occurrence else None
                    }
                    for alert in self.active_alerts.values()
                ],
                "hot_paths": [
                    {
                        "id": hot_path.path_id,
                        "components": hot_path.component_chain,
                        "frequency": hot_path.execution_frequency,
                        "avg_response_time_ms": hot_path.average_response_time_ms,
                        "optimization_score": hot_path.optimization_score,
                        "bottlenecks": hot_path.bottleneck_points,
                        "opportunities": hot_path.optimization_opportunities
                    }
                    for hot_path in self.hot_paths.values()
                ],
                "recent_optimizations": [
                    {
                        "id": opt.optimization_id,
                        "strategy": opt.strategy.value,
                        "component": opt.target_component,
                        "executed": opt.executed,
                        "success": opt.success,
                        "execution_time": opt.execution_time.isoformat() if opt.execution_time else None,
                        "expected_improvement": opt.expected_improvement,
                        "actual_improvement": opt.actual_improvement
                    }
                    for opt in list(self.optimization_history)[-10:]  # Last 10
                ],
                "summary": {
                    "total_metrics": len(self.current_metrics),
                    "active_alerts": len(self.active_alerts),
                    "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]),
                    "hot_paths": len(self.hot_paths),
                    "pending_optimizations": len(self.pending_optimizations),
                    "streaming_clients": len(self.streaming_clients),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    async def add_streaming_client(self, client: Any):
        """Add a streaming dashboard client"""
        self.streaming_clients.add(client)
        logger.info(f"Streaming client connected, total: {len(self.streaming_clients)}")
    
    async def remove_streaming_client(self, client: Any):
        """Remove a streaming dashboard client"""
        self.streaming_clients.discard(client)
        logger.info(f"Streaming client disconnected, total: {len(self.streaming_clients)}")


def create_real_time_profiler(
    sampling_interval_ms: int = 100,
    dashboard_update_interval_ms: int = 1000,
    enable_auto_optimization: bool = True,
    enable_hot_path_detection: bool = True,
    start_monitoring: bool = False
) -> RealTimeProfiler:
    """
    Factory function to create real-time profiler
    
    Args:
        sampling_interval_ms: Metric sampling interval in milliseconds
        dashboard_update_interval_ms: Dashboard update interval in milliseconds
        enable_auto_optimization: Enable automatic optimization
        enable_hot_path_detection: Enable hot path detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        RealTimeProfiler: Configured real-time profiler instance
    """
    profiler = RealTimeProfiler(
        sampling_interval_ms=sampling_interval_ms,
        dashboard_update_interval_ms=dashboard_update_interval_ms,
        enable_auto_optimization=enable_auto_optimization,
        enable_hot_path_detection=enable_hot_path_detection
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_real_time_profiling():
    """Example of real-time profiling for Creator Economy"""
    profiler = create_real_time_profiler(start_monitoring=True)
    
    # Register components
    await profiler.register_component(
        "creator_dashboard",
        "web_service",
        [RealTimeMetricType.RESPONSE_TIME, RealTimeMetricType.CPU_USAGE, RealTimeMetricType.USER_SESSIONS]
    )
    
    await profiler.register_component(
        "content_processor",
        "background_service",
        [RealTimeMetricType.CPU_USAGE, RealTimeMetricType.MEMORY_USAGE, RealTimeMetricType.QUEUE_DEPTH]
    )
    
    # Simulate metrics
    for i in range(10):
        # Dashboard response time
        response_time_metric = RealTimeMetric(
            metric_id=f"response_{i}",
            metric_type=RealTimeMetricType.RESPONSE_TIME,
            component_name="creator_dashboard",
            value=200.0 + (i * 50),  # Increasing response time
            unit="ms"
        )
        await profiler.add_metric(response_time_metric)
        
        # Content processor queue depth
        queue_metric = RealTimeMetric(
            metric_id=f"queue_{i}",
            metric_type=RealTimeMetricType.QUEUE_DEPTH,
            component_name="content_processor",
            value=50 + (i * 20),  # Increasing queue depth
            unit="items"
        )
        await profiler.add_metric(queue_metric)
        
        await asyncio.sleep(0.2)
    
    # Wait a bit for processing
    await asyncio.sleep(2)
    
    # Get dashboard data
    dashboard_data = profiler.get_dashboard_data()
    
    print("Real-time profiling dashboard:")
    print(f"- Total metrics: {dashboard_data['summary']['total_metrics']}")
    print(f"- Active alerts: {dashboard_data['summary']['active_alerts']}")
    print(f"- Critical alerts: {dashboard_data['summary']['critical_alerts']}")
    print(f"- Hot paths: {dashboard_data['summary']['hot_paths']}")
    print(f"- Pending optimizations: {dashboard_data['summary']['pending_optimizations']}")
    
    print("\nActive alerts:")
    for alert in dashboard_data['active_alerts']:
        print(f"- {alert['component']}: {alert['message']} (Severity: {alert['severity']})")
    
    print("\nRecent optimizations:")
    for opt in dashboard_data['recent_optimizations']:
        print(f"- {opt['strategy']} for {opt['component']}: {'Success' if opt['success'] else 'Failed'}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_real_time_profiling())