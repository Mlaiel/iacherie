"""API Monitoring Manager - Comprehensive API Health & Performance Monitoring
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides advanced monitoring capabilities for API performance,
health checks, error tracking, and alerting systems.
"""import asyncio
import aiohttp
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class MonitoringLevel(Enum):
    """Monitoring levels"""    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"

class AlertSeverity(Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(Enum):
    """Metric types for monitoring"""    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    LATENCY_P95 = "latency_p95"
    LATENCY_P99 = "latency_p99"

@dataclass
class APIMetric:
    """API performance metric"""    api_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class HealthCheckConfig:
    """Health check configuration"""    api_name: str
    endpoint: str
    method: str = "HEAD"
    expected_status_codes: List[int] = field(default_factory=lambda: [200, 204])
    timeout_seconds: int = 10
    interval_seconds: int = 60
    failure_threshold: int = 3
    success_threshold: int = 1
    custom_headers: Dict[str, str] = field(default_factory=dict)
    validate_response: Optional[Callable[[aiohttp.ClientResponse], bool]] = None

@dataclass
class AlertRule:
    """Alert rule configuration"""    rule_name: str
    api_name: str
    metric_type: MetricType
    threshold: float
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    duration_minutes: int = 5  # How long condition must persist
    severity: AlertSeverity = AlertSeverity.MEDIUM
    cooldown_minutes: int = 30  # Minimum time between alerts
    enabled: bool = True

@dataclass
class Alert:
    """Alert notification"""    alert_id: str
    rule_name: str
    api_name: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceTracker:
    """Tracks API performance metrics"""    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.last_request_time: Dict[str, datetime] = {}
        self.error_details: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def record_request(self, api_name: str, response_time: float, success: bool, 
                      status_code: Optional[int] = None, error_message: Optional[str] = None):
        """Record API request metrics"""        self.response_times[api_name].append(response_time)
        self.request_counts[api_name] += 1
        self.last_request_time[api_name] = datetime.utcnow()
        
        if success:
            self.success_counts[api_name] += 1
        else:
            self.error_counts[api_name] += 1
            # Store error details
            error_info = {
                'timestamp': datetime.utcnow(),
                'status_code': status_code,
                'error_message': error_message,
                'response_time': response_time
            }
            self.error_details[api_name].append(error_info)
            # Keep only last 100 errors per API
            if len(self.error_details[api_name]) > 100:
                self.error_details[api_name] = self.error_details[api_name][-100:]
    
    def get_metrics(self, api_name: str, time_window_minutes: int = 60) -> Dict[str, float]:
        """Get performance metrics for API within time window"""        now = datetime.utcnow()
        cutoff_time = now - timedelta(minutes=time_window_minutes)
        
        # Filter recent response times
        recent_times = []
        for i, timestamp in enumerate(self.last_request_time.get(api_name, [])):
            if timestamp >= cutoff_time:
                recent_times.append(list(self.response_times[api_name])[i])
        
        if not recent_times:
            return {
                'avg_response_time': 0.0,
                'p95_response_time': 0.0,
                'p99_response_time': 0.0,
                'success_rate': 0.0,
                'error_rate': 0.0,
                'throughput': 0.0,
                'total_requests': 0
            }
        
        # Calculate metrics
        avg_response_time = statistics.mean(recent_times)
        p95_response_time = statistics.quantiles(recent_times, n=20)[18] if len(recent_times) > 5 else avg_response_time
        p99_response_time = statistics.quantiles(recent_times, n=100)[98] if len(recent_times) > 10 else avg_response_time
        
        total_requests = self.request_counts[api_name]
        success_count = self.success_counts[api_name]
        error_count = self.error_counts[api_name]
        
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        throughput = total_requests / time_window_minutes  # requests per minute
        
        return {
            'avg_response_time': round(avg_response_time, 3),
            'p95_response_time': round(p95_response_time, 3),
            'p99_response_time': round(p99_response_time, 3),
            'success_rate': round(success_rate, 2),
            'error_rate': round(error_rate, 2),
            'throughput': round(throughput, 2),
            'total_requests': total_requests
        }
    
    def get_error_summary(self, api_name: str) -> Dict[str, Any]:
        """Get error summary for API"""        errors = self.error_details.get(api_name, [])
        if not errors:
            return {'total_errors': 0, 'error_types': {}, 'recent_errors': []}
        
        # Group errors by status code
        error_types = defaultdict(int)
        for error in errors:
            status_code = error.get('status_code', 'unknown')
            error_types[str(status_code)] += 1
        
        # Get recent errors (last 10)
        recent_errors = errors[-10:]
        
        return {
            'total_errors': len(errors),
            'error_types': dict(error_types),
            'recent_errors': [
                {
                    'timestamp': error['timestamp'].isoformat(),
                    'status_code': error.get('status_code'),
                    'message': error.get('error_message', '')[:200]  # Truncate long messages
                }
                for error in recent_errors
            ]
        }

class HealthChecker:
    """Performs health checks on APIs"""    
    def __init__(self):
        self.health_configs: Dict[str, HealthCheckConfig] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.last_check_times: Dict[str, datetime] = {}
    
    def register_health_check(self, config: HealthCheckConfig):
        """Register health check configuration"""        self.health_configs[config.api_name] = config
        self.health_status[config.api_name] = {
            'status': 'unknown',
            'last_check': None,
            'last_success': None,
            'last_failure': None,
            'consecutive_failures': 0,
            'consecutive_successes': 0
        }
        logger.info(f"Registered health check for {config.api_name}")
    
    async def perform_health_check(self, api_name: str) -> Dict[str, Any]:
        """Perform health check for specific API"""        if api_name not in self.health_configs:
            return {'status': 'no_config', 'message': 'No health check configured'}
        
        config = self.health_configs[api_name]
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout_seconds)
            headers = config.custom_headers.copy()
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    config.method,
                    config.endpoint,
                    headers=headers
                ) as response:
                    response_time = time.time() - start_time
                    
                    # Check status code
                    if response.status in config.expected_status_codes:
                        # Custom validation if provided
                        if config.validate_response:
                            try:
                                is_valid = config.validate_response(response)
                                if not is_valid:
                                    return await self._record_failure(
                                        api_name, response_time, 
                                        'Custom validation failed'
                                    )
                            except Exception as e:
                                return await self._record_failure(
                                    api_name, response_time, 
                                    f'Validation error: {str(e)}'
                                )
                        
                        return await self._record_success(api_name, response_time, response.status)
                    else:
                        return await self._record_failure(
                            api_name, response_time,
                            f'Unexpected status code: {response.status}'
                        )
                        
        except asyncio.TimeoutError:
            response_time = config.timeout_seconds
            return await self._record_failure(api_name, response_time, 'Request timeout')
        except Exception as e:
            response_time = time.time() - start_time
            return await self._record_failure(api_name, response_time, str(e))
    
    async def _record_success(self, api_name: str, response_time: float, status_code: int) -> Dict[str, Any]:
        """Record successful health check"""        now = datetime.utcnow()
        self.success_counts[api_name] += 1
        self.failure_counts[api_name] = 0  # Reset failure count
        self.last_check_times[api_name] = now
        
        status = self.health_status[api_name]
        status['status'] = 'healthy'
        status['last_check'] = now
        status['last_success'] = now
        status['consecutive_failures'] = 0
        status['consecutive_successes'] += 1
        
        return {
            'status': 'healthy',
            'response_time': round(response_time * 1000, 2),  # Convert to ms
            'status_code': status_code,
            'timestamp': now.isoformat()
        }
    
    async def _record_failure(self, api_name: str, response_time: float, error_message: str) -> Dict[str, Any]:
        """Record failed health check"""        now = datetime.utcnow()
        self.failure_counts[api_name] += 1
        self.success_counts[api_name] = 0  # Reset success count
        self.last_check_times[api_name] = now
        
        status = self.health_status[api_name]
        status['last_check'] = now
        status['last_failure'] = now
        status['consecutive_failures'] += 1
        status['consecutive_successes'] = 0
        
        # Determine if API should be marked as unhealthy
        config = self.health_configs[api_name]
        if self.failure_counts[api_name] >= config.failure_threshold:
            status['status'] = 'unhealthy'
        else:
            status['status'] = 'degraded'
        
        return {
            'status': status['status'],
            'response_time': round(response_time * 1000, 2),
            'error': error_message,
            'consecutive_failures': status['consecutive_failures'],
            'timestamp': now.isoformat()
        }
    
    async def check_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all registered APIs"""        tasks = []
        api_names = []
        
        for api_name in self.health_configs.keys():
            tasks.append(self.perform_health_check(api_name))
            api_names.append(api_name)
        
        if not tasks:
            return {}
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            api_name = api_names[i]
            if isinstance(result, Exception):
                health_results[api_name] = {
                    'status': 'error',
                    'error': str(result),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                health_results[api_name] = result
        
        return health_results
    
    def get_health_status(self, api_name: str) -> Dict[str, Any]:
        """Get current health status for API"""        return self.health_status.get(api_name, {'status': 'unknown'})
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all APIs"""        return self.health_status.copy()

class AlertManager:
    """Manages monitoring alerts"""    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
    
    def register_alert_rule(self, rule: AlertRule):
        """Register alert rule"""        self.alert_rules[rule.rule_name] = rule
        logger.info(f"Registered alert rule: {rule.rule_name}")
    
    def evaluate_alerts(self, metrics: Dict[str, Dict[str, float]]):
        """Evaluate all alert rules against current metrics"""        current_time = datetime.utcnow()
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            api_metrics = metrics.get(rule.api_name, {})
            if not api_metrics:
                continue
            
            metric_value = api_metrics.get(rule.metric_type.value)
            if metric_value is None:
                continue
            
            # Store metric history
            history_key = f"{rule.api_name}:{rule.metric_type.value}"
            self.metric_history[history_key].append((current_time, metric_value))
            
            # Check if alert condition is met
            if self._check_alert_condition(rule, metric_value):
                # Check if condition has persisted for required duration
                if self._check_alert_duration(rule, history_key):
                    # Check cooldown period
                    if self._check_alert_cooldown(rule_name, current_time):
                        self._trigger_alert(rule, metric_value, current_time)
            else:
                # Check if alert should be resolved
                if rule_name in self.active_alerts:
                    self._resolve_alert(rule_name, current_time)
    
    def _check_alert_condition(self, rule: AlertRule, value: float) -> bool:
        """Check if alert condition is met"""        if rule.operator == "gt":
            return value > rule.threshold
        elif rule.operator == "gte":
            return value >= rule.threshold
        elif rule.operator == "lt":
            return value < rule.threshold
        elif rule.operator == "lte":
            return value <= rule.threshold
        elif rule.operator == "eq":
            return value == rule.threshold
        return False
    
    def _check_alert_duration(self, rule: AlertRule, history_key: str) -> bool:
        """Check if alert condition has persisted for required duration"""        if rule.duration_minutes <= 0:
            return True
        
        history = self.metric_history[history_key]
        if len(history) < 2:
            return False
        
        duration_threshold = datetime.utcnow() - timedelta(minutes=rule.duration_minutes)
        
        # Check if all values in the time window meet the condition
        for timestamp, value in reversed(history):
            if timestamp < duration_threshold:
                break
            if not self._check_alert_condition(rule, value):
                return False
        
        return True
    
    def _check_alert_cooldown(self, rule_name: str, current_time: datetime) -> bool:
        """Check if alert is not in cooldown period"""        if rule_name not in self.last_alert_times:
            return True
        
        rule = self.alert_rules[rule_name]
        last_alert = self.last_alert_times[rule_name]
        cooldown_end = last_alert + timedelta(minutes=rule.cooldown_minutes)
        
        return current_time >= cooldown_end
    
    def _trigger_alert(self, rule: AlertRule, value: float, timestamp: datetime):
        """Trigger new alert"""        alert_id = f"{rule.rule_name}_{int(timestamp.timestamp())}"
        
        message = (
            f"Alert: {rule.rule_name} - "
            f"{rule.api_name} {rule.metric_type.value} is {value} "
            f"({rule.operator} {rule.threshold})"
        )
        
        alert = Alert(
            alert_id=alert_id,
            rule_name=rule.rule_name,
            api_name=rule.api_name,
            severity=rule.severity,
            message=message,
            triggered_at=timestamp,
            metadata={
                'metric_type': rule.metric_type.value,
                'current_value': value,
                'threshold': rule.threshold,
                'operator': rule.operator
            }
        )
        
        self.active_alerts[rule.rule_name] = alert
        self.alert_history.append(alert)
        self.last_alert_times[rule.rule_name] = timestamp
        
        logger.warning(f"Alert triggered: {message}")
    
    def _resolve_alert(self, rule_name: str, timestamp: datetime):
        """Resolve active alert"""        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved_at = timestamp
            del self.active_alerts[rule_name]
            
            logger.info(f"Alert resolved: {alert.message}")
    
    def acknowledge_alert(self, rule_name: str, acknowledged_by: str):
        """Acknowledge active alert"""        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            
            logger.info(f"Alert acknowledged by {acknowledged_by}: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""        return self.alert_history[-limit:]

class APIMonitoringManager:
    """Main API monitoring manager"""    
    def __init__(self, monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED):
        self.monitoring_level = monitoring_level
        self.performance_tracker = PerformanceTracker()
        self.health_checker = HealthChecker()
        self.alert_manager = AlertManager()
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    def register_api_monitoring(self, api_name: str, config: Dict[str, Any]):
        """Register API for monitoring"""        # Register health check if endpoint provided
        if 'health_endpoint' in config:
            health_config = HealthCheckConfig(
                api_name=api_name,
                endpoint=config['health_endpoint'],
                method=config.get('health_method', 'HEAD'),
                timeout_seconds=config.get('health_timeout', 10),
                interval_seconds=config.get('health_interval', 60)
            )
            self.health_checker.register_health_check(health_config)
        
        # Register default alert rules
        self._register_default_alert_rules(api_name)
        
        logger.info(f"Registered monitoring for {api_name}")
    
    def _register_default_alert_rules(self, api_name: str):
        """Register default alert rules for API"""        default_rules = [
            AlertRule(
                rule_name=f"{api_name}_high_error_rate",
                api_name=api_name,
                metric_type=MetricType.ERROR_RATE,
                threshold=10.0,  # 10% error rate
                operator="gt",
                severity=AlertSeverity.HIGH,
                duration_minutes=5
            ),
            AlertRule(
                rule_name=f"{api_name}_slow_response",
                api_name=api_name,
                metric_type=MetricType.RESPONSE_TIME,
                threshold=2000.0,  # 2 seconds
                operator="gt",
                severity=AlertSeverity.MEDIUM,
                duration_minutes=5
            ),
            AlertRule(
                rule_name=f"{api_name}_low_success_rate",
                api_name=api_name,
                metric_type=MetricType.SUCCESS_RATE,
                threshold=95.0,  # 95% success rate
                operator="lt",
                severity=AlertSeverity.HIGH,
                duration_minutes=5
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.register_alert_rule(rule)
    
    def record_api_request(self, api_name: str, response_time: float, success: bool,
                          status_code: Optional[int] = None, error_message: Optional[str] = None):
        """Record API request for monitoring"""        self.performance_tracker.record_request(
            api_name, response_time, success, status_code, error_message
        )
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""        # Get performance metrics for all APIs
        performance_metrics = {}
        for api_name in self.performance_tracker.request_counts.keys():
            performance_metrics[api_name] = self.performance_tracker.get_metrics(api_name)
        
        # Get health status for all APIs
        health_status = self.health_checker.get_all_health_status()
        
        # Evaluate alerts
        self.alert_manager.evaluate_alerts(performance_metrics)
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Calculate overall system health
        overall_health = self._calculate_overall_health(health_status, performance_metrics)
        
        return {
            'overall_health': overall_health,
            'performance_metrics': performance_metrics,
            'health_status': health_status,
            'active_alerts': [
                {
                    'rule_name': alert.rule_name,
                    'api_name': alert.api_name,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'triggered_at': alert.triggered_at.isoformat(),
                    'acknowledged': alert.acknowledged
                }
                for alert in active_alerts
            ],
            'summary': {
                'total_apis': len(performance_metrics),
                'healthy_apis': sum(1 for status in health_status.values() if status.get('status') == 'healthy'),
                'active_alerts': len(active_alerts),
                'critical_alerts': sum(1 for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL)
            }
        }
    
    def _calculate_overall_health(self, health_status: Dict[str, Any], 
                                performance_metrics: Dict[str, Any]) -> str:
        """Calculate overall system health score"""        if not health_status:
            return 'unknown'
        
        health_scores = []
        for api_name, status in health_status.items():
            if status.get('status') == 'healthy':
                health_scores.append(100)
            elif status.get('status') == 'degraded':
                health_scores.append(70)
            elif status.get('status') == 'unhealthy':
                health_scores.append(20)
            else:
                health_scores.append(50)  # unknown
        
        if not health_scores:
            return 'unknown'
        
        avg_score = sum(health_scores) / len(health_scores)
        
        if avg_score >= 95:
            return 'excellent'
        elif avg_score >= 80:
            return 'good'
        elif avg_score >= 60:
            return 'degraded'
        elif avg_score >= 30:
            return 'poor'
        else:
            return 'critical'
    
    async def start_continuous_monitoring(self):
        """Start continuous monitoring tasks"""        # Start health check monitoring
        async def health_check_loop():
            while True:
                try:
                    await self.health_checker.check_all_apis()
                    await asyncio.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health check loop error: {e}")
                    await asyncio.sleep(60)
        
        # Start alert evaluation
        async def alert_evaluation_loop():
            while True:
                try:
                    # Get current metrics
                    metrics = {}
                    for api_name in self.performance_tracker.request_counts.keys():
                        metrics[api_name] = self.performance_tracker.get_metrics(api_name)
                    
                    # Evaluate alerts
                    self.alert_manager.evaluate_alerts(metrics)
                    
                    await asyncio.sleep(30)  # Evaluate every 30 seconds
                except Exception as e:
                    logger.error(f"Alert evaluation loop error: {e}")
                    await asyncio.sleep(30)
        
        # Start monitoring tasks
        self.monitoring_tasks['health_check'] = asyncio.create_task(health_check_loop())
        self.monitoring_tasks['alert_evaluation'] = asyncio.create_task(alert_evaluation_loop())
        
        logger.info("Started continuous API monitoring")
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring tasks"""        for task_name, task in self.monitoring_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Stopped monitoring task: {task_name}")
        
        self.monitoring_tasks.clear()
    
    def export_metrics(self, api_name: Optional[str] = None, 
                      time_window_minutes: int = 60) -> Dict[str, Any]:
        """Export metrics in Prometheus format or JSON"""        if api_name:
            apis = [api_name]
        else:
            apis = list(self.performance_tracker.request_counts.keys())
        
        exported_metrics = {}
        for api in apis:
            metrics = self.performance_tracker.get_metrics(api, time_window_minutes)
            error_summary = self.performance_tracker.get_error_summary(api)
            health_status = self.health_checker.get_health_status(api)
            
            exported_metrics[api] = {
                'performance': metrics,
                'errors': error_summary,
                'health': health_status,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return exported_metrics
