"""
Performance Orchestrator - Platform Core Enterprise Architecture
Performance optimization coordination for Ainflue AI Creator Platform

© 2025 Fahed Mlaiel. All rights reserved.
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import statistics
import psutil

# Platform Core Imports
from ..utils.base_classes import EnterpriseComponent
from ..utils.exceptions import PerformanceError, ValidationError
from ..utils.metrics import MetricsCollector
from ..security.auth_manager import AuthenticationManager

logger = logging.getLogger(__name__)

class OptimizationLevel(Enum):
    """Performance optimization levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"

class PerformanceMetricType(Enum):
    """Performance metric types."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DATABASE_PERFORMANCE = "database_performance"
    CACHE_HIT_RATE = "cache_hit_rate"
    CONCURRENT_USERS = "concurrent_users"

class AlertSeverity(Enum):
    """Performance alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric_type: PerformanceMetricType
    warning_threshold: float
    critical_threshold: float
    unit: str
    duration: int = 300  # 5 minutes
    enabled: bool = True

@dataclass
class OptimizationRule:
    """Performance optimization rule."""
    name: str
    condition: str
    action: str
    priority: int
    optimization_level: OptimizationLevel
    cooldown_period: int = 300  # 5 minutes
    max_executions: int = 5
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Performance alert."""
    id: str
    metric_type: PerformanceMetricType
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    service: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class OptimizationResult:
    """Optimization execution result."""
    rule_name: str
    executed_at: datetime
    success: bool
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement: Dict[str, float]
    errors: List[str] = field(default_factory=list)

class PerformanceOrchestrator(EnterpriseComponent):
    """
    Enterprise performance optimization coordination system.
    
    Features:
    - Performance optimization coordination
    - Resource utilization monitoring
    - Bottleneck detection and resolution
    - Performance tuning automation
    - Real-time performance analysis
    - Predictive performance management
    - Automated scaling decisions
    - Performance SLA monitoring
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.performance_thresholds: Dict[str, PerformanceThreshold] = {}
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.optimization_history: List[OptimizationResult] = []
        self.metrics_collector = MetricsCollector("performance_orchestrator")
        self.auth_manager = AuthenticationManager()
        
        # Performance data storage
        self.performance_data: Dict[str, List[Dict[str, Any]]] = {}
        self.baseline_metrics: Dict[str, float] = {}
        
        # Configuration
        self.monitoring_interval = config.get("monitoring_interval", 30)  # 30 seconds
        self.data_retention_hours = config.get("data_retention_hours", 24)
        self.optimization_enabled = config.get("optimization_enabled", True)
        self.max_concurrent_optimizations = config.get("max_concurrent_optimizations", 3)
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Initialize default optimization rules
        self._initialize_default_optimization_rules()
        
        logger.info("PerformanceOrchestrator initialized successfully")

    async def start_monitoring(self) -> None:
        """Start performance monitoring."""
        try:
            logger.info("Starting performance monitoring")
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            # Start optimization loop
            if self.optimization_enabled:
                asyncio.create_task(self._optimization_loop())
            
            # Start cleanup loop
            asyncio.create_task(self._cleanup_loop())
            
            self.metrics_collector.increment("monitoring_started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            raise PerformanceError(f"Monitoring startup failed: {str(e)}")

    async def add_performance_threshold(
        self,
        threshold: PerformanceThreshold,
        user_id: str = None
    ) -> None:
        """Add a performance threshold."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_performance_config(user_id):
                raise ValidationError(f"User {user_id} not authorized for performance configuration")
            
            threshold_id = f"{threshold.metric_type.value}_{int(time.time())}"
            self.performance_thresholds[threshold_id] = threshold
            
            logger.info(f"Performance threshold added: {threshold_id}")
            self.metrics_collector.increment("thresholds_added")
            
        except Exception as e:
            logger.error(f"Failed to add performance threshold: {str(e)}")
            raise PerformanceError(f"Threshold addition failed: {str(e)}")

    async def add_optimization_rule(
        self,
        rule: OptimizationRule,
        user_id: str = None
    ) -> None:
        """Add an optimization rule."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_performance_config(user_id):
                raise ValidationError(f"User {user_id} not authorized for performance configuration")
            
            # Validate rule
            await self._validate_optimization_rule(rule)
            
            self.optimization_rules[rule.name] = rule
            
            logger.info(f"Optimization rule added: {rule.name}")
            self.metrics_collector.increment("optimization_rules_added")
            
        except Exception as e:
            logger.error(f"Failed to add optimization rule: {str(e)}")
            raise PerformanceError(f"Optimization rule addition failed: {str(e)}")

    async def collect_performance_metrics(
        self,
        service: str,
        metrics: Dict[PerformanceMetricType, float]
    ) -> None:
        """Collect performance metrics for a service."""
        try:
            timestamp = datetime.now()
            
            # Store metrics
            if service not in self.performance_data:
                self.performance_data[service] = []
            
            metric_entry = {
                "timestamp": timestamp,
                "metrics": {metric_type.value: value for metric_type, value in metrics.items()}
            }
            
            self.performance_data[service].append(metric_entry)
            
            # Check thresholds
            await self._check_thresholds(service, metrics, timestamp)
            
            # Update baseline if needed
            await self._update_baseline_metrics(service, metrics)
            
            self.metrics_collector.increment("metrics_collected")
            
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {str(e)}")
            raise PerformanceError(f"Metrics collection failed: {str(e)}")

    async def analyze_performance_trends(
        self,
        service: str,
        metric_type: PerformanceMetricType,
        time_window: int = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """Analyze performance trends for a service."""
        try:
            if service not in self.performance_data:
                return {"error": "No data available for service"}
            
            # Get data within time window
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            relevant_data = [
                entry for entry in self.performance_data[service]
                if entry["timestamp"] >= cutoff_time and metric_type.value in entry["metrics"]
            ]
            
            if not relevant_data:
                return {"error": "No data available for time window"}
            
            # Extract metric values
            values = [entry["metrics"][metric_type.value] for entry in relevant_data]
            
            # Calculate statistics
            analysis = {
                "service": service,
                "metric_type": metric_type.value,
                "time_window": time_window,
                "data_points": len(values),
                "min_value": min(values),
                "max_value": max(values),
                "avg_value": statistics.mean(values),
                "median_value": statistics.median(values),
                "std_deviation": statistics.stdev(values) if len(values) > 1 else 0,
                "trend": await self._calculate_trend(values),
                "anomalies": await self._detect_anomalies(values),
                "recommendations": await self._generate_recommendations(service, metric_type, values)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {str(e)}")
            raise PerformanceError(f"Trend analysis failed: {str(e)}")

    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        try:
            dashboard = {
                "overview": {
                    "total_services": len(self.performance_data),
                    "active_alerts": len(self.active_alerts),
                    "optimization_rules": len(self.optimization_rules),
                    "optimizations_executed": len(self.optimization_history),
                    "monitoring_status": "active"
                },
                "alerts": [
                    {
                        "id": alert.id,
                        "metric_type": alert.metric_type.value,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "service": alert.service,
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in list(self.active_alerts.values())[:10]  # Latest 10 alerts
                ],
                "recent_optimizations": [
                    {
                        "rule_name": result.rule_name,
                        "executed_at": result.executed_at.isoformat(),
                        "success": result.success,
                        "improvement": result.improvement
                    }
                    for result in self.optimization_history[-10:]  # Latest 10 optimizations
                ],
                "system_metrics": await self._get_system_metrics(),
                "performance_summary": await self._get_performance_summary()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get performance dashboard: {str(e)}")
            raise PerformanceError(f"Dashboard generation failed: {str(e)}")

    async def trigger_optimization(
        self,
        service: str,
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Manually trigger performance optimization."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_performance_optimization(user_id):
                raise ValidationError(f"User {user_id} not authorized for performance optimization")
            
            logger.info(f"Manual optimization triggered for service: {service}")
            
            # Get current metrics
            current_metrics = await self._get_current_metrics(service)
            
            # Find applicable optimization rules
            applicable_rules = [
                rule for rule in self.optimization_rules.values()
                if rule.enabled and rule.optimization_level == optimization_level
            ]
            
            if not applicable_rules:
                return {"error": "No applicable optimization rules found"}
            
            # Execute optimizations
            results = []
            for rule in applicable_rules:
                result = await self._execute_optimization_rule(service, rule, current_metrics)
                results.append(result)
                
                if result.success:
                    self.optimization_history.append(result)
            
            successful_optimizations = [r for r in results if r.success]
            
            response = {
                "service": service,
                "optimization_level": optimization_level.value,
                "rules_executed": len(results),
                "successful_optimizations": len(successful_optimizations),
                "results": [
                    {
                        "rule_name": r.rule_name,
                        "success": r.success,
                        "improvement": r.improvement,
                        "errors": r.errors
                    }
                    for r in results
                ]
            }
            
            self.metrics_collector.increment("manual_optimizations_triggered")
            return response
            
        except Exception as e:
            logger.error(f"Failed to trigger optimization: {str(e)}")
            raise PerformanceError(f"Optimization trigger failed: {str(e)}")

    async def get_optimization_recommendations(
        self,
        service: str
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations for a service."""
        try:
            if service not in self.performance_data:
                return []
            
            recommendations = []
            
            # Analyze recent performance data
            recent_data = self.performance_data[service][-100:]  # Last 100 data points
            
            for metric_type in PerformanceMetricType:
                metric_values = [
                    entry["metrics"].get(metric_type.value, 0)
                    for entry in recent_data
                    if metric_type.value in entry["metrics"]
                ]
                
                if metric_values:
                    recommendation = await self._generate_metric_recommendation(
                        service, metric_type, metric_values
                    )
                    if recommendation:
                        recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {str(e)}")
            raise PerformanceError(f"Recommendation generation failed: {str(e)}")

    # Private Methods
    
    def _initialize_default_thresholds(self) -> None:
        """Initialize default performance thresholds."""
        default_thresholds = [
            PerformanceThreshold(
                metric_type=PerformanceMetricType.RESPONSE_TIME,
                warning_threshold=1000,  # 1 second
                critical_threshold=3000,  # 3 seconds
                unit="ms"
            ),
            PerformanceThreshold(
                metric_type=PerformanceMetricType.ERROR_RATE,
                warning_threshold=0.05,  # 5%
                critical_threshold=0.10,  # 10%
                unit="percentage"
            ),
            PerformanceThreshold(
                metric_type=PerformanceMetricType.CPU_USAGE,
                warning_threshold=0.75,  # 75%
                critical_threshold=0.90,  # 90%
                unit="percentage"
            ),
            PerformanceThreshold(
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                warning_threshold=0.80,  # 80%
                critical_threshold=0.95,  # 95%
                unit="percentage"
            )
        ]
        
        for threshold in default_thresholds:
            threshold_id = f"{threshold.metric_type.value}_default"
            self.performance_thresholds[threshold_id] = threshold

    def _initialize_default_optimization_rules(self) -> None:
        """Initialize default optimization rules."""
        default_rules = [
            OptimizationRule(
                name="high_cpu_scale_up",
                condition="cpu_usage > 0.80",
                action="scale_up",
                priority=1,
                optimization_level=OptimizationLevel.MODERATE
            ),
            OptimizationRule(
                name="high_memory_cleanup",
                condition="memory_usage > 0.85",
                action="cleanup_memory",
                priority=2,
                optimization_level=OptimizationLevel.MODERATE
            ),
            OptimizationRule(
                name="slow_response_cache_optimization",
                condition="response_time > 2000",
                action="optimize_cache",
                priority=3,
                optimization_level=OptimizationLevel.CONSERVATIVE
            ),
            OptimizationRule(
                name="high_error_rate_circuit_breaker",
                condition="error_rate > 0.10",
                action="enable_circuit_breaker",
                priority=1,
                optimization_level=OptimizationLevel.AGGRESSIVE
            )
        ]
        
        for rule in default_rules:
            self.optimization_rules[rule.name] = rule

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        while True:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                
                # Store system metrics
                await self.collect_performance_metrics("system", system_metrics)
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)

    async def _optimization_loop(self) -> None:
        """Continuous optimization loop."""
        while True:
            try:
                if self.optimization_enabled:
                    await self._run_automatic_optimizations()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Optimization loop error: {str(e)}")
                await asyncio.sleep(60)

    async def _cleanup_loop(self) -> None:
        """Cleanup loop for old data and resolved alerts."""
        while True:
            try:
                await self._cleanup_resolved_alerts()
                await self._cleanup_old_optimization_history()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {str(e)}")
                await asyncio.sleep(3600)

    async def _collect_system_metrics(self) -> Dict[PerformanceMetricType, float]:
        """Collect system performance metrics."""
        try:
            metrics = {}
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics[PerformanceMetricType.CPU_USAGE] = cpu_percent / 100.0
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics[PerformanceMetricType.MEMORY_USAGE] = memory.percent / 100.0
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics[PerformanceMetricType.DISK_IO] = disk_io.read_bytes + disk_io.write_bytes
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                metrics[PerformanceMetricType.NETWORK_IO] = network_io.bytes_sent + network_io.bytes_recv
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return {}

    async def _check_thresholds(
        self,
        service: str,
        metrics: Dict[PerformanceMetricType, float],
        timestamp: datetime
    ) -> None:
        """Check metrics against thresholds and generate alerts."""
        for threshold_id, threshold in self.performance_thresholds.items():
            if not threshold.enabled:
                continue
            
            metric_value = metrics.get(threshold.metric_type)
            if metric_value is None:
                continue
            
            # Check for threshold violations
            severity = None
            if metric_value >= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
            elif metric_value >= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
            
            if severity:
                alert_id = f"{service}_{threshold.metric_type.value}_{int(time.time())}"
                alert = PerformanceAlert(
                    id=alert_id,
                    metric_type=threshold.metric_type,
                    severity=severity,
                    message=f"{threshold.metric_type.value} is {metric_value} {threshold.unit}, exceeding {severity.value} threshold of {threshold.warning_threshold if severity == AlertSeverity.WARNING else threshold.critical_threshold} {threshold.unit}",
                    value=metric_value,
                    threshold=threshold.warning_threshold if severity == AlertSeverity.WARNING else threshold.critical_threshold,
                    timestamp=timestamp,
                    service=service
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                
                logger.warning(f"Performance alert generated: {alert.message}")
                self.metrics_collector.increment(f"alerts_{severity.value}")

    async def _update_baseline_metrics(
        self,
        service: str,
        metrics: Dict[PerformanceMetricType, float]
    ) -> None:
        """Update baseline metrics for comparison."""
        for metric_type, value in metrics.items():
            baseline_key = f"{service}_{metric_type.value}"
            
            if baseline_key not in self.baseline_metrics:
                self.baseline_metrics[baseline_key] = value
            else:
                # Use exponential moving average
                alpha = 0.1  # Smoothing factor
                self.baseline_metrics[baseline_key] = (
                    alpha * value + (1 - alpha) * self.baseline_metrics[baseline_key]
                )

    async def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metric values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        recent_avg = statistics.mean(values[-len(values)//3:])  # Last 1/3 of values
        older_avg = statistics.mean(values[:len(values)//3])    # First 1/3 of values
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    async def _detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values."""
        if len(values) < 10:
            return []
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        anomalies = []
        for i, value in enumerate(values):
            # Simple z-score based anomaly detection
            z_score = abs(value - mean_val) / std_val if std_val > 0 else 0
            
            if z_score > 3:  # 3 standard deviations
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": z_score,
                    "severity": "high" if z_score > 4 else "medium"
                })
        
        return anomalies

    async def _generate_recommendations(
        self,
        service: str,
        metric_type: PerformanceMetricType,
        values: List[float]
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        if not values:
            return recommendations
        
        avg_value = statistics.mean(values)
        trend = await self._calculate_trend(values)
        
        # Response time recommendations
        if metric_type == PerformanceMetricType.RESPONSE_TIME:
            if avg_value > 2000:  # 2 seconds
                recommendations.append("Consider implementing caching strategies")
                recommendations.append("Optimize database queries")
                if trend == "increasing":
                    recommendations.append("Response time is increasing - investigate performance bottlenecks")
        
        # CPU usage recommendations
        elif metric_type == PerformanceMetricType.CPU_USAGE:
            if avg_value > 0.8:  # 80%
                recommendations.append("Consider scaling up or out")
                recommendations.append("Profile application for CPU-intensive operations")
                if trend == "increasing":
                    recommendations.append("CPU usage is trending up - consider proactive scaling")
        
        # Memory usage recommendations
        elif metric_type == PerformanceMetricType.MEMORY_USAGE:
            if avg_value > 0.8:  # 80%
                recommendations.append("Investigate memory leaks")
                recommendations.append("Optimize memory usage patterns")
                recommendations.append("Consider increasing memory allocation")
        
        # Error rate recommendations
        elif metric_type == PerformanceMetricType.ERROR_RATE:
            if avg_value > 0.05:  # 5%
                recommendations.append("Investigate error patterns")
                recommendations.append("Implement circuit breaker patterns")
                recommendations.append("Review error handling and logging")
        
        return recommendations

    async def _get_current_metrics(self, service: str) -> Dict[str, float]:
        """Get current metrics for a service."""
        if service not in self.performance_data or not self.performance_data[service]:
            return {}
        
        latest_entry = self.performance_data[service][-1]
        return latest_entry["metrics"]

    async def _execute_optimization_rule(
        self,
        service: str,
        rule: OptimizationRule,
        current_metrics: Dict[str, float]
    ) -> OptimizationResult:
        """Execute an optimization rule."""
        result = OptimizationResult(
            rule_name=rule.name,
            executed_at=datetime.now(),
            success=False,
            before_metrics=current_metrics.copy(),
            after_metrics={},
            improvement={}
        )
        
        try:
            # Simulate optimization execution
            await asyncio.sleep(1)
            
            # Get metrics after optimization (simulated improvement)
            after_metrics = current_metrics.copy()
            
            # Apply simulated improvements based on action
            if rule.action == "scale_up":
                after_metrics["cpu_usage"] = current_metrics.get("cpu_usage", 0) * 0.8
                after_metrics["response_time"] = current_metrics.get("response_time", 0) * 0.9
            elif rule.action == "cleanup_memory":
                after_metrics["memory_usage"] = current_metrics.get("memory_usage", 0) * 0.85
            elif rule.action == "optimize_cache":
                after_metrics["response_time"] = current_metrics.get("response_time", 0) * 0.7
                after_metrics["cache_hit_rate"] = min(1.0, current_metrics.get("cache_hit_rate", 0.5) * 1.2)
            elif rule.action == "enable_circuit_breaker":
                after_metrics["error_rate"] = current_metrics.get("error_rate", 0) * 0.5
            
            # Calculate improvement
            improvement = {}
            for metric, before_value in current_metrics.items():
                after_value = after_metrics.get(metric, before_value)
                if before_value > 0:
                    improvement_pct = ((before_value - after_value) / before_value) * 100
                    improvement[metric] = improvement_pct
            
            result.success = True
            result.after_metrics = after_metrics
            result.improvement = improvement
            
            logger.info(f"Optimization rule executed successfully: {rule.name}")
            
        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Optimization rule execution failed: {str(e)}")
        
        return result

    async def _run_automatic_optimizations(self) -> None:
        """Run automatic optimizations based on current conditions."""
        for service in self.performance_data:
            current_metrics = await self._get_current_metrics(service)
            if not current_metrics:
                continue
            
            # Check each optimization rule
            for rule in self.optimization_rules.values():
                if not rule.enabled:
                    continue
                
                # Check if rule condition is met (simplified evaluation)
                if await self._evaluate_rule_condition(rule, current_metrics):
                    result = await self._execute_optimization_rule(service, rule, current_metrics)
                    if result.success:
                        self.optimization_history.append(result)
                        logger.info(f"Automatic optimization executed: {rule.name}")

    async def _evaluate_rule_condition(
        self,
        rule: OptimizationRule,
        metrics: Dict[str, float]
    ) -> bool:
        """Evaluate if optimization rule condition is met."""
        try:
            # Simplified condition evaluation
            condition = rule.condition.lower()
            
            if "cpu_usage" in condition and "cpu_usage" in metrics:
                cpu_value = metrics["cpu_usage"]
                if "> 0.80" in condition and cpu_value > 0.80:
                    return True
                elif "> 0.75" in condition and cpu_value > 0.75:
                    return True
            
            if "memory_usage" in condition and "memory_usage" in metrics:
                memory_value = metrics["memory_usage"]
                if "> 0.85" in condition and memory_value > 0.85:
                    return True
                elif "> 0.80" in condition and memory_value > 0.80:
                    return True
            
            if "response_time" in condition and "response_time" in metrics:
                response_time = metrics["response_time"]
                if "> 2000" in condition and response_time > 2000:
                    return True
                elif "> 1000" in condition and response_time > 1000:
                    return True
            
            if "error_rate" in condition and "error_rate" in metrics:
                error_rate = metrics["error_rate"]
                if "> 0.10" in condition and error_rate > 0.10:
                    return True
                elif "> 0.05" in condition and error_rate > 0.05:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to evaluate rule condition: {str(e)}")
            return False

    async def _validate_optimization_rule(self, rule: OptimizationRule) -> None:
        """Validate optimization rule configuration."""
        if not rule.name:
            raise ValidationError("Rule name is required")
        
        if not rule.condition:
            raise ValidationError("Rule condition is required")
        
        if not rule.action:
            raise ValidationError("Rule action is required")
        
        if rule.priority < 1:
            raise ValidationError("Rule priority must be positive")

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}

    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all services."""
        try:
            summary = {
                "total_services": len(self.performance_data),
                "metrics_collected": sum(len(data) for data in self.performance_data.values()),
                "average_response_time": 0,
                "average_cpu_usage": 0,
                "average_memory_usage": 0,
                "total_errors": 0
            }
            
            if self.performance_data:
                # Calculate averages (simplified)
                all_response_times = []
                all_cpu_usage = []
                all_memory_usage = []
                
                for service_data in self.performance_data.values():
                    for entry in service_data[-10:]:  # Last 10 entries
                        metrics = entry["metrics"]
                        if "response_time" in metrics:
                            all_response_times.append(metrics["response_time"])
                        if "cpu_usage" in metrics:
                            all_cpu_usage.append(metrics["cpu_usage"])
                        if "memory_usage" in metrics:
                            all_memory_usage.append(metrics["memory_usage"])
                
                if all_response_times:
                    summary["average_response_time"] = statistics.mean(all_response_times)
                if all_cpu_usage:
                    summary["average_cpu_usage"] = statistics.mean(all_cpu_usage)
                if all_memory_usage:
                    summary["average_memory_usage"] = statistics.mean(all_memory_usage)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {str(e)}")
            return {}

    async def _generate_metric_recommendation(
        self,
        service: str,
        metric_type: PerformanceMetricType,
        values: List[float]
    ) -> Optional[Dict[str, Any]]:
        """Generate recommendation for a specific metric."""
        if not values:
            return None
        
        avg_value = statistics.mean(values)
        recommendations = await self._generate_recommendations(service, metric_type, values)
        
        if not recommendations:
            return None
        
        return {
            "service": service,
            "metric_type": metric_type.value,
            "current_value": avg_value,
            "recommendations": recommendations,
            "priority": "high" if avg_value > 0.8 else "medium",
            "estimated_improvement": "20-40%" if len(recommendations) > 2 else "10-20%"
        }

    async def _cleanup_old_data(self) -> None:
        """Clean up old performance data."""
        cutoff_time = datetime.now() - timedelta(hours=self.data_retention_hours)
        
        for service in self.performance_data:
            self.performance_data[service] = [
                entry for entry in self.performance_data[service]
                if entry["timestamp"] >= cutoff_time
            ]

    async def _cleanup_resolved_alerts(self) -> None:
        """Clean up resolved alerts."""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep resolved alerts for 24 hours
        
        # Remove old resolved alerts from history
        self.alert_history = [
            alert for alert in self.alert_history
            if not alert.resolved or alert.resolution_time >= cutoff_time
        ]

    async def _cleanup_old_optimization_history(self) -> None:
        """Clean up old optimization history."""
        cutoff_time = datetime.now() - timedelta(hours=self.data_retention_hours)
        
        self.optimization_history = [
            result for result in self.optimization_history
            if result.executed_at >= cutoff_time
        ]

    async def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status."""
        return {
            "status": "healthy",
            "monitoring_active": True,
            "optimization_enabled": self.optimization_enabled,
            "services_monitored": len(self.performance_data),
            "active_alerts": len(self.active_alerts),
            "optimization_rules": len(self.optimization_rules),
            "metrics": await self.metrics_collector.get_summary()
        }

    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        try:
            # Stop monitoring loops
            logger.info("PerformanceOrchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")