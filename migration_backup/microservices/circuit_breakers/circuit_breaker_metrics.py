"""
Circuit Breaker Metrics & Observability - IA Chéries Platform
=========================================================

Système metrics et observability pour circuit breakers.
Prometheus + Grafana + custom dashboards + alerting.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import math

# Monitoring imports with graceful degradation
try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    from prometheus_client.core import REGISTRY
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    Counter = Histogram = Gauge = CollectorRegistry = generate_latest = REGISTRY = None

# Grafana integration
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# Alert manager integration
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    aiohttp = None

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    SUMMARY = "SUMMARY"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

class DashboardType(Enum):
    """Dashboard types"""
    CIRCUIT_OVERVIEW = "CIRCUIT_OVERVIEW"
    SERVICE_HEALTH = "SERVICE_HEALTH"
    PERFORMANCE_METRICS = "PERFORMANCE_METRICS"
    ALERT_STATUS = "ALERT_STATUS"
    CUSTOM = "CUSTOM"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    duration: int = 60  # seconds
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'condition': self.condition,
            'threshold': self.threshold,
            'severity': self.severity.value,
            'duration': self.duration,
            'labels': self.labels,
            'annotations': self.annotations,
            'enabled': self.enabled
        }

@dataclass
class MetricsConfig:
    """Configuration for metrics collection"""
    prometheus_enabled: bool = True
    prometheus_port: int = 8000
    grafana_enabled: bool = False
    grafana_url: str = "http://localhost:3000"
    grafana_api_key: str = ""
    alert_manager_enabled: bool = False
    alert_manager_url: str = "http://localhost:9093"
    
    # Collection settings
    collection_interval: int = 15  # seconds
    retention_period_hours: int = 24
    max_metrics_in_memory: int = 10000
    
    # Export settings
    export_to_file: bool = False
    export_file_path: str = "/tmp/circuit_breaker_metrics.json"

class PrometheusClient:
    """Prometheus metrics client"""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.registry = CollectorRegistry() if HAS_PROMETHEUS else None
        self.metrics = {}
        
        if HAS_PROMETHEUS:
            self._initialize_metrics()
            logger.info("Prometheus client initialized")
        else:
            logger.warning("Prometheus client not available")
    
    def _initialize_metrics(self):
        """Initialize Prometheus metrics"""
        if not HAS_PROMETHEUS:
            return
        
        # Circuit breaker state metrics
        self.metrics['circuit_state'] = Gauge(
            'circuit_breaker_state',
            'Current state of circuit breaker (0=CLOSED, 1=OPEN, 2=HALF_OPEN)',
            ['service_name', 'circuit_id'],
            registry=self.registry
        )
        
        # Request metrics
        self.metrics['requests_total'] = Counter(
            'circuit_breaker_requests_total',
            'Total number of requests through circuit breaker',
            ['service_name', 'circuit_id', 'status'],
            registry=self.registry
        )
        
        self.metrics['request_duration'] = Histogram(
            'circuit_breaker_request_duration_seconds',
            'Request duration in seconds',
            ['service_name', 'circuit_id'],
            registry=self.registry
        )
        
        # Failure metrics
        self.metrics['failures_total'] = Counter(
            'circuit_breaker_failures_total',
            'Total number of failures',
            ['service_name', 'circuit_id', 'failure_type'],
            registry=self.registry
        )
        
        self.metrics['failure_rate'] = Gauge(
            'circuit_breaker_failure_rate',
            'Current failure rate (0-1)',
            ['service_name', 'circuit_id'],
            registry=self.registry
        )
        
        # Threshold metrics
        self.metrics['failure_threshold'] = Gauge(
            'circuit_breaker_failure_threshold',
            'Current failure threshold',
            ['service_name', 'circuit_id'],
            registry=self.registry
        )
        
        # State transition metrics
        self.metrics['state_transitions'] = Counter(
            'circuit_breaker_state_transitions_total',
            'Total number of state transitions',
            ['service_name', 'circuit_id', 'from_state', 'to_state'],
            registry=self.registry
        )
        
        # Fallback metrics
        self.metrics['fallbacks_total'] = Counter(
            'circuit_breaker_fallbacks_total',
            'Total number of fallback executions',
            ['service_name', 'circuit_id', 'fallback_type'],
            registry=self.registry
        )
        
        # Performance metrics
        self.metrics['concurrent_requests'] = Gauge(
            'circuit_breaker_concurrent_requests',
            'Current number of concurrent requests',
            ['service_name', 'circuit_id'],
            registry=self.registry
        )
        
        self.metrics['response_time_percentile'] = Histogram(
            'circuit_breaker_response_time_percentile',
            'Response time percentiles',
            ['service_name', 'circuit_id', 'percentile'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0],
            registry=self.registry
        )
    
    def record_circuit_state(self, service_name: str, circuit_id: str, state: str):
        """Record circuit breaker state"""
        if not HAS_PROMETHEUS or 'circuit_state' not in self.metrics:
            return
        
        state_mapping = {'CLOSED': 0, 'OPEN': 1, 'HALF_OPEN': 2, 'FORCED_OPEN': 3, 'FORCED_CLOSED': 4}
        state_value = state_mapping.get(state, -1)
        
        self.metrics['circuit_state'].labels(
            service_name=service_name,
            circuit_id=circuit_id
        ).set(state_value)
    
    def record_request(self, service_name: str, circuit_id: str, status: str, duration: float):
        """Record request metrics"""
        if not HAS_PROMETHEUS:
            return
        
        if 'requests_total' in self.metrics:
            self.metrics['requests_total'].labels(
                service_name=service_name,
                circuit_id=circuit_id,
                status=status
            ).inc()
        
        if 'request_duration' in self.metrics:
            self.metrics['request_duration'].labels(
                service_name=service_name,
                circuit_id=circuit_id
            ).observe(duration)
    
    def record_failure(self, service_name: str, circuit_id: str, failure_type: str):
        """Record failure metrics"""
        if not HAS_PROMETHEUS or 'failures_total' not in self.metrics:
            return
        
        self.metrics['failures_total'].labels(
            service_name=service_name,
            circuit_id=circuit_id,
            failure_type=failure_type
        ).inc()
    
    def record_failure_rate(self, service_name: str, circuit_id: str, rate: float):
        """Record current failure rate"""
        if not HAS_PROMETHEUS or 'failure_rate' not in self.metrics:
            return
        
        self.metrics['failure_rate'].labels(
            service_name=service_name,
            circuit_id=circuit_id
        ).set(rate)
    
    def record_state_transition(self, service_name: str, circuit_id: str, from_state: str, to_state: str):
        """Record state transition"""
        if not HAS_PROMETHEUS or 'state_transitions' not in self.metrics:
            return
        
        self.metrics['state_transitions'].labels(
            service_name=service_name,
            circuit_id=circuit_id,
            from_state=from_state,
            to_state=to_state
        ).inc()
    
    def record_fallback(self, service_name: str, circuit_id: str, fallback_type: str):
        """Record fallback execution"""
        if not HAS_PROMETHEUS or 'fallbacks_total' not in self.metrics:
            return
        
        self.metrics['fallbacks_total'].labels(
            service_name=service_name,
            circuit_id=circuit_id,
            fallback_type=fallback_type
        ).inc()
    
    def get_metrics(self) -> Optional[str]:
        """Get Prometheus formatted metrics"""
        if not HAS_PROMETHEUS or not self.registry:
            return None
        
        return generate_latest(self.registry).decode('utf-8')

class GrafanaClient:
    """Grafana dashboard client"""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.base_url = config.grafana_url
        self.api_key = config.grafana_api_key
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        if config.grafana_enabled and HAS_REQUESTS:
            logger.info("Grafana client initialized")
        else:
            logger.warning("Grafana client disabled or requests not available")
    
    async def create_dashboard(self, dashboard_spec: Dict[str, Any]) -> Optional[str]:
        """Create Grafana dashboard"""
        if not self.config.grafana_enabled or not HAS_REQUESTS:
            return None
        
        try:
            url = f"{self.base_url}/api/dashboards/db"
            
            response = requests.post(url, headers=self.headers, json=dashboard_spec, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                dashboard_url = f"{self.base_url}/d/{result.get('uid', '')}"
                logger.info(f"Dashboard created: {dashboard_url}")
                return dashboard_url
            else:
                logger.error(f"Dashboard creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Dashboard creation error: {str(e)}")
            return None
    
    def create_circuit_overview_dashboard(self) -> Dict[str, Any]:
        """Create circuit breaker overview dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": "Circuit Breaker Overview",
                "tags": ["circuit-breaker", "monitoring"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Circuit Breaker States",
                        "type": "stat",
                        "targets": [{
                            "expr": "circuit_breaker_state",
                            "legendFormat": "{{service_name}} - {{circuit_id}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(circuit_breaker_requests_total[5m])",
                            "legendFormat": "{{service_name}} - {{status}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Failure Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "circuit_breaker_failure_rate",
                            "legendFormat": "{{service_name}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Response Time Percentiles",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, circuit_breaker_request_duration_seconds)",
                            "legendFormat": "95th percentile"
                        }, {
                            "expr": "histogram_quantile(0.50, circuit_breaker_request_duration_seconds)",
                            "legendFormat": "50th percentile"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            }
        }
    
    def create_service_health_dashboard(self, service_name: str) -> Dict[str, Any]:
        """Create service-specific health dashboard"""
        return {
            "dashboard": {
                "id": None,
                "title": f"Service Health - {service_name}",
                "tags": ["circuit-breaker", "service-health", service_name],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Service Status",
                        "type": "singlestat",
                        "targets": [{
                            "expr": f'circuit_breaker_state{{service_name="{service_name}"}}',
                            "legendFormat": "Circuit State"
                        }],
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Success Rate",
                        "type": "singlestat",
                        "targets": [{
                            "expr": f'rate(circuit_breaker_requests_total{{service_name="{service_name}",status="success"}}[5m])',
                            "legendFormat": "Success Rate"
                        }],
                        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "15s"
            }
        }

class AlertManagerClient:
    """Alert Manager client for alerting"""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.base_url = config.alert_manager_url
        self.enabled = config.alert_manager_enabled and HAS_AIOHTTP
        
        if self.enabled:
            logger.info("Alert Manager client initialized")
        else:
            logger.warning("Alert Manager client disabled or aiohttp not available")
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert to Alert Manager"""
        if not self.enabled:
            return False
        
        try:
            url = f"{self.base_url}/api/v1/alerts"
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.post(url, json=[alert_data], timeout=timeout) as response:
                    if response.status == 200:
                        logger.info(f"Alert sent successfully: {alert_data.get('alertname', 'Unknown')}")
                        return True
                    else:
                        logger.error(f"Alert sending failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Alert sending error: {str(e)}")
            return False
    
    def create_circuit_open_alert(self, service_name: str, circuit_id: str) -> Dict[str, Any]:
        """Create circuit open alert"""
        return {
            "alertname": "CircuitBreakerOpen",
            "startsAt": datetime.now().isoformat() + "Z",
            "labels": {
                "severity": "critical",
                "service": service_name,
                "circuit_id": circuit_id,
                "alertname": "CircuitBreakerOpen"
            },
            "annotations": {
                "summary": f"Circuit breaker is open for service {service_name}",
                "description": f"Circuit breaker {circuit_id} for service {service_name} has opened due to failures"
            },
            "generatorURL": f"http://localhost:8080/circuits/{circuit_id}"
        }
    
    def create_high_failure_rate_alert(self, service_name: str, circuit_id: str, failure_rate: float) -> Dict[str, Any]:
        """Create high failure rate alert"""
        return {
            "alertname": "HighFailureRate",
            "startsAt": datetime.now().isoformat() + "Z",
            "labels": {
                "severity": "warning",
                "service": service_name,
                "circuit_id": circuit_id,
                "alertname": "HighFailureRate"
            },
            "annotations": {
                "summary": f"High failure rate detected for service {service_name}",
                "description": f"Service {service_name} has failure rate of {failure_rate:.2%}"
            },
            "generatorURL": f"http://localhost:8080/circuits/{circuit_id}"
        }

class CustomMetricsRegistry:
    """Custom metrics registry for circuit breaker specific metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics = {}
        self.last_aggregation = datetime.now()
        
    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a custom metric"""
        timestamp = datetime.now()
        labels = labels or {}
        
        metric_entry = {
            'timestamp': timestamp,
            'value': value,
            'labels': labels
        }
        
        self.metrics[metric_name].append(metric_entry)
    
    def get_metric_values(self, metric_name: str, time_range_minutes: int = 60) -> List[float]:
        """Get metric values within time range"""
        cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
        
        values = []
        for entry in self.metrics[metric_name]:
            if entry['timestamp'] >= cutoff_time:
                values.append(entry['value'])
        
        return values
    
    def calculate_percentile(self, metric_name: str, percentile: float, time_range_minutes: int = 60) -> float:
        """Calculate percentile for metric"""
        values = self.get_metric_values(metric_name, time_range_minutes)
        
        if not values:
            return 0.0
        
        try:
            import numpy as np
            return float(np.percentile(values, percentile))
        except ImportError:
            # Fallback calculation
            values.sort()
            index = int(percentile / 100 * len(values))
            return float(values[min(index, len(values) - 1)])
    
    def calculate_average(self, metric_name: str, time_range_minutes: int = 60) -> float:
        """Calculate average for metric"""
        values = self.get_metric_values(metric_name, time_range_minutes)
        return statistics.mean(values) if values else 0.0
    
    def calculate_rate(self, metric_name: str, time_range_minutes: int = 5) -> float:
        """Calculate rate per second for metric"""
        values = self.get_metric_values(metric_name, time_range_minutes)
        
        if len(values) < 2:
            return 0.0
        
        time_span_seconds = time_range_minutes * 60
        return len(values) / time_span_seconds
    
    def aggregate_metrics(self):
        """Aggregate metrics for reporting"""
        current_time = datetime.now()
        
        for metric_name in self.metrics:
            values = self.get_metric_values(metric_name)
            
            if values:
                self.aggregated_metrics[metric_name] = {
                    'count': len(values),
                    'average': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'p50': self.calculate_percentile(metric_name, 50),
                    'p95': self.calculate_percentile(metric_name, 95),
                    'p99': self.calculate_percentile(metric_name, 99),
                    'rate_per_second': self.calculate_rate(metric_name),
                    'last_updated': current_time.isoformat()
                }
        
        self.last_aggregation = current_time

class CircuitBreakerMetrics:
    """
    Système metrics et observability pour circuit breakers.
    Prometheus + Grafana + custom dashboards + alerting.
    """
    
    def __init__(self, metrics_config: MetricsConfig):
        self.metrics_config = metrics_config
        self.prometheus_client = PrometheusClient(metrics_config)
        self.grafana_client = GrafanaClient(metrics_config)
        self.custom_metrics = CustomMetricsRegistry()
        self.alert_manager = AlertManagerClient(metrics_config)
        
        # Circuit breaker registrations
        self.registered_circuits = {}
        self.circuit_metrics_cache = {}
        
        # Background tasks
        self.collection_task = None
        self.export_task = None
        
        # Alert rules
        self.alert_rules = []
        
        logger.info("Circuit breaker metrics system initialized")
    
    async def start_collection(self):
        """Start metrics collection"""
        self.collection_task = asyncio.create_task(self._periodic_collection())
        
        if self.metrics_config.export_to_file:
            self.export_task = asyncio.create_task(self._periodic_export())
    
    async def stop_collection(self):
        """Stop metrics collection"""
        if self.collection_task:
            self.collection_task.cancel()
        if self.export_task:
            self.export_task.cancel()
    
    async def collect_circuit_metrics(self, circuit_id: str) -> Dict[str, Any]:
        """
        Collection métriques circuit breaker comprehensive.
        
        Metrics:
        - Circuit state transitions
        - Failure rates et success rates
        - Response times et latency percentiles
        - Throughput et request volume
        - Error categorization et root cause analysis
        - Fallback execution rates
        """
        if circuit_id not in self.registered_circuits:
            logger.warning(f"Circuit {circuit_id} not registered for metrics collection")
            return {}
        
        circuit_info = self.registered_circuits[circuit_id]
        service_name = circuit_info['service_name']
        
        # Collect from custom metrics
        metrics = {
            'circuit_id': circuit_id,
            'service_name': service_name,
            'collection_timestamp': datetime.now().isoformat(),
            
            # State metrics
            'current_state': circuit_info.get('current_state', 'UNKNOWN'),
            'state_transitions': self._get_state_transitions(circuit_id),
            
            # Request metrics
            'total_requests': self.custom_metrics.calculate_average(f'{circuit_id}_requests_total'),
            'request_rate': self.custom_metrics.calculate_rate(f'{circuit_id}_requests'),
            
            # Performance metrics
            'average_response_time': self.custom_metrics.calculate_average(f'{circuit_id}_response_time'),
            'response_time_p50': self.custom_metrics.calculate_percentile(f'{circuit_id}_response_time', 50),
            'response_time_p95': self.custom_metrics.calculate_percentile(f'{circuit_id}_response_time', 95),
            'response_time_p99': self.custom_metrics.calculate_percentile(f'{circuit_id}_response_time', 99),
            
            # Error metrics
            'failure_rate': self.custom_metrics.calculate_average(f'{circuit_id}_failure_rate'),
            'error_categories': self._get_error_categories(circuit_id),
            
            # Fallback metrics
            'fallback_executions': self.custom_metrics.calculate_average(f'{circuit_id}_fallbacks'),
            'fallback_success_rate': self.custom_metrics.calculate_average(f'{circuit_id}_fallback_success'),
            
            # Throughput metrics
            'successful_requests_rate': self.custom_metrics.calculate_rate(f'{circuit_id}_success'),
            'failed_requests_rate': self.custom_metrics.calculate_rate(f'{circuit_id}_failures'),
            'rejected_requests_rate': self.custom_metrics.calculate_rate(f'{circuit_id}_rejections'),
        }
        
        # Cache metrics
        self.circuit_metrics_cache[circuit_id] = metrics
        
        return metrics
    
    def _get_state_transitions(self, circuit_id: str) -> List[Dict[str, Any]]:
        """Get recent state transitions"""
        transition_metrics = self.custom_metrics.get_metric_values(f'{circuit_id}_state_transitions', 60)
        
        transitions = []
        for i, entry in enumerate(self.custom_metrics.metrics[f'{circuit_id}_state_transitions']):
            if i >= len(transition_metrics):
                break
                
            transitions.append({
                'timestamp': entry['timestamp'].isoformat(),
                'from_state': entry['labels'].get('from_state', 'UNKNOWN'),
                'to_state': entry['labels'].get('to_state', 'UNKNOWN'),
                'reason': entry['labels'].get('reason', '')
            })
        
        return transitions[-10:]  # Last 10 transitions
    
    def _get_error_categories(self, circuit_id: str) -> Dict[str, int]:
        """Get error categorization"""
        error_categories = {}
        
        for entry in self.custom_metrics.metrics[f'{circuit_id}_errors']:
            error_type = entry['labels'].get('error_type', 'unknown')
            error_categories[error_type] = error_categories.get(error_type, 0) + 1
        
        return error_categories
    
    async def create_custom_dashboard(self, dashboard_spec: Dict[str, Any]) -> Optional[str]:
        """Création dashboard Grafana personnalisé"""
        dashboard_type = dashboard_spec.get('type', DashboardType.CUSTOM.value)
        
        if dashboard_type == DashboardType.CIRCUIT_OVERVIEW.value:
            dashboard_config = self.grafana_client.create_circuit_overview_dashboard()
        elif dashboard_type == DashboardType.SERVICE_HEALTH.value:
            service_name = dashboard_spec.get('service_name', 'unknown')
            dashboard_config = self.grafana_client.create_service_health_dashboard(service_name)
        else:
            dashboard_config = dashboard_spec
        
        return await self.grafana_client.create_dashboard(dashboard_config)
    
    async def setup_alerting_rules(self, alert_rules: List[AlertRule]) -> bool:
        """Configuration règles alerting enterprise"""
        try:
            self.alert_rules = alert_rules
            
            # Validate alert rules
            for rule in alert_rules:
                if not self._validate_alert_rule(rule):
                    logger.error(f"Invalid alert rule: {rule.name}")
                    return False
            
            logger.info(f"Configured {len(alert_rules)} alert rules")
            return True
            
        except Exception as e:
            logger.error(f"Alert rules setup failed: {str(e)}")
            return False
    
    def _validate_alert_rule(self, rule: AlertRule) -> bool:
        """Validate alert rule configuration"""
        if not rule.name or not rule.condition:
            return False
        
        if rule.threshold < 0:
            return False
        
        if rule.duration < 0:
            return False
        
        return True
    
    async def generate_circuit_health_report(self, timeframe: str = "1h") -> Dict[str, Any]:
        """Génération rapport santé circuits comprehensive"""
        report_time = datetime.now()
        
        # Parse timeframe
        timeframe_minutes = self._parse_timeframe(timeframe)
        
        # Collect metrics for all registered circuits
        circuit_reports = {}
        overall_stats = {
            'total_circuits': len(self.registered_circuits),
            'healthy_circuits': 0,
            'degraded_circuits': 0,
            'failed_circuits': 0,
            'total_requests': 0,
            'total_failures': 0,
            'average_response_time': 0
        }
        
        response_times = []
        
        for circuit_id in self.registered_circuits:
            circuit_metrics = await self.collect_circuit_metrics(circuit_id)
            
            # Classify circuit health
            health_status = self._classify_circuit_health(circuit_metrics)
            circuit_metrics['health_status'] = health_status
            
            if health_status == 'HEALTHY':
                overall_stats['healthy_circuits'] += 1
            elif health_status == 'DEGRADED':
                overall_stats['degraded_circuits'] += 1
            else:
                overall_stats['failed_circuits'] += 1
            
            # Aggregate stats
            overall_stats['total_requests'] += circuit_metrics.get('total_requests', 0)
            overall_stats['total_failures'] += circuit_metrics.get('total_requests', 0) * circuit_metrics.get('failure_rate', 0)
            
            avg_resp_time = circuit_metrics.get('average_response_time', 0)
            if avg_resp_time > 0:
                response_times.append(avg_resp_time)
            
            circuit_reports[circuit_id] = circuit_metrics
        
        # Calculate overall averages
        if response_times:
            overall_stats['average_response_time'] = statistics.mean(response_times)
        
        if overall_stats['total_requests'] > 0:
            overall_stats['overall_failure_rate'] = overall_stats['total_failures'] / overall_stats['total_requests']
        else:
            overall_stats['overall_failure_rate'] = 0
        
        overall_stats['health_percentage'] = (overall_stats['healthy_circuits'] / overall_stats['total_circuits'] * 100) if overall_stats['total_circuits'] > 0 else 0
        
        return {
            'report_timestamp': report_time.isoformat(),
            'timeframe': timeframe,
            'overall_stats': overall_stats,
            'circuit_reports': circuit_reports,
            'recommendations': self._generate_health_recommendations(overall_stats, circuit_reports)
        }
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to minutes"""
        timeframe = timeframe.lower()
        
        if timeframe.endswith('m'):
            return int(timeframe[:-1])
        elif timeframe.endswith('h'):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith('d'):
            return int(timeframe[:-1]) * 24 * 60
        else:
            return 60  # Default to 1 hour
    
    def _classify_circuit_health(self, metrics: Dict[str, Any]) -> str:
        """Classify circuit health status"""
        failure_rate = metrics.get('failure_rate', 0)
        current_state = metrics.get('current_state', 'UNKNOWN')
        response_time_p95 = metrics.get('response_time_p95', 0)
        
        if current_state == 'OPEN' or failure_rate > 0.1:
            return 'FAILED'
        elif failure_rate > 0.05 or response_time_p95 > 5000:  # 5 seconds
            return 'DEGRADED'
        else:
            return 'HEALTHY'
    
    def _generate_health_recommendations(self, overall_stats: Dict[str, Any], 
                                       circuit_reports: Dict[str, Any]) -> List[str]:
        """Generate health recommendations"""
        recommendations = []
        
        # Overall health recommendations
        health_percentage = overall_stats.get('health_percentage', 0)
        if health_percentage < 50:
            recommendations.append("CRITICAL: Less than 50% of circuits are healthy - immediate attention required")
        elif health_percentage < 80:
            recommendations.append("WARNING: Circuit health below 80% - review failing circuits")
        
        # Failure rate recommendations
        overall_failure_rate = overall_stats.get('overall_failure_rate', 0)
        if overall_failure_rate > 0.1:
            recommendations.append("HIGH: Overall failure rate exceeds 10% - investigate root causes")
        elif overall_failure_rate > 0.05:
            recommendations.append("MEDIUM: Overall failure rate above 5% - monitor closely")
        
        # Response time recommendations
        avg_response_time = overall_stats.get('average_response_time', 0)
        if avg_response_time > 2000:  # 2 seconds
            recommendations.append("Performance issue: Average response time exceeds 2 seconds")
        
        # Circuit-specific recommendations
        for circuit_id, metrics in circuit_reports.items():
            if metrics.get('health_status') == 'FAILED':
                recommendations.append(f"Circuit {circuit_id}: Currently failed - requires immediate attention")
            elif metrics.get('health_status') == 'DEGRADED':
                recommendations.append(f"Circuit {circuit_id}: Performance degraded - consider optimization")
        
        if not recommendations:
            recommendations.append("All circuits operating normally - continue monitoring")
        
        return recommendations
    
    async def register_circuit(self, circuit_id: str, service_name: str, circuit_config: Dict[str, Any] = None):
        """Register circuit for metrics collection"""
        self.registered_circuits[circuit_id] = {
            'service_name': service_name,
            'registration_time': datetime.now(),
            'current_state': 'CLOSED',
            'config': circuit_config or {}
        }
        
        logger.info(f"Registered circuit {circuit_id} for service {service_name}")
    
    async def record_circuit_event(self, circuit_id: str, event_type: str, event_data: Dict[str, Any]):
        """Record circuit breaker event"""
        if circuit_id not in self.registered_circuits:
            logger.warning(f"Circuit {circuit_id} not registered - cannot record event")
            return
        
        circuit_info = self.registered_circuits[circuit_id]
        service_name = circuit_info['service_name']
        
        # Record in Prometheus
        if event_type == 'request':
            status = event_data.get('status', 'unknown')
            duration = event_data.get('duration', 0)
            self.prometheus_client.record_request(service_name, circuit_id, status, duration)
        
        elif event_type == 'state_change':
            from_state = event_data.get('from_state', 'UNKNOWN')
            to_state = event_data.get('to_state', 'UNKNOWN')
            circuit_info['current_state'] = to_state
            
            self.prometheus_client.record_circuit_state(service_name, circuit_id, to_state)
            self.prometheus_client.record_state_transition(service_name, circuit_id, from_state, to_state)
            
            # Send alert if circuit opens
            if to_state == 'OPEN':
                alert = self.alert_manager.create_circuit_open_alert(service_name, circuit_id)
                await self.alert_manager.send_alert(alert)
        
        elif event_type == 'failure':
            failure_type = event_data.get('failure_type', 'unknown')
            self.prometheus_client.record_failure(service_name, circuit_id, failure_type)
        
        elif event_type == 'fallback':
            fallback_type = event_data.get('fallback_type', 'unknown')
            self.prometheus_client.record_fallback(service_name, circuit_id, fallback_type)
        
        # Record in custom metrics
        metric_name = f'{circuit_id}_{event_type}'
        value = event_data.get('value', 1)
        labels = {
            'service_name': service_name,
            'circuit_id': circuit_id,
            **event_data.get('labels', {})
        }
        
        self.custom_metrics.record_metric(metric_name, value, labels)
    
    async def _periodic_collection(self):
        """Periodic metrics collection task"""
        while True:
            try:
                await asyncio.sleep(self.metrics_config.collection_interval)
                
                # Aggregate custom metrics
                self.custom_metrics.aggregate_metrics()
                
                # Check alert conditions
                await self._check_alert_conditions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
    
    async def _check_alert_conditions(self):
        """Check alert conditions and send alerts"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            try:
                condition_met = await self._evaluate_alert_condition(rule)
                
                if condition_met:
                    alert_data = {
                        "alertname": rule.name,
                        "startsAt": datetime.now().isoformat() + "Z",
                        "labels": {
                            "severity": rule.severity.value.lower(),
                            "alertname": rule.name,
                            **rule.labels
                        },
                        "annotations": rule.annotations
                    }
                    
                    await self.alert_manager.send_alert(alert_data)
                    
            except Exception as e:
                logger.error(f"Alert condition check failed for {rule.name}: {str(e)}")
    
    async def _evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """Evaluate if alert condition is met"""
        # Simple condition evaluation (in production, this would be more sophisticated)
        condition = rule.condition.lower()
        threshold = rule.threshold
        
        if 'failure_rate' in condition:
            # Check average failure rate across all circuits
            avg_failure_rate = 0
            circuit_count = 0
            
            for circuit_id in self.registered_circuits:
                failure_rate = self.custom_metrics.calculate_average(f'{circuit_id}_failure_rate', 5)
                if failure_rate > 0:
                    avg_failure_rate += failure_rate
                    circuit_count += 1
            
            if circuit_count > 0:
                avg_failure_rate /= circuit_count
                return avg_failure_rate > threshold
        
        elif 'response_time' in condition:
            # Check average response time
            avg_response_times = []
            
            for circuit_id in self.registered_circuits:
                avg_resp_time = self.custom_metrics.calculate_average(f'{circuit_id}_response_time', 5)
                if avg_resp_time > 0:
                    avg_response_times.append(avg_resp_time)
            
            if avg_response_times:
                overall_avg = statistics.mean(avg_response_times)
                return overall_avg > threshold
        
        return False
    
    async def _periodic_export(self):
        """Periodic metrics export task"""
        while True:
            try:
                await asyncio.sleep(300)  # Export every 5 minutes
                
                # Export metrics to file
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'prometheus_metrics': self.prometheus_client.get_metrics(),
                    'custom_metrics': self.custom_metrics.aggregated_metrics,
                    'circuit_status': {
                        circuit_id: info for circuit_id, info in self.registered_circuits.items()
                    }
                }
                
                with open(self.metrics_config.export_file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                logger.debug(f"Metrics exported to {self.metrics_config.export_file_path}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics export error: {str(e)}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            'registered_circuits': len(self.registered_circuits),
            'prometheus_enabled': self.metrics_config.prometheus_enabled and HAS_PROMETHEUS,
            'grafana_enabled': self.metrics_config.grafana_enabled,
            'alert_manager_enabled': self.metrics_config.alert_manager_enabled,
            'active_alert_rules': len([rule for rule in self.alert_rules if rule.enabled]),
            'collection_interval': self.metrics_config.collection_interval,
            'last_collection': self.custom_metrics.last_aggregation.isoformat(),
            'export_enabled': self.metrics_config.export_to_file,
            'metrics_count': len(self.custom_metrics.aggregated_metrics)
        }

# Export main classes
__all__ = [
    'CircuitBreakerMetrics',
    'MetricsConfig',
    'AlertRule',
    'AlertSeverity',
    'DashboardType',
    'PrometheusClient',
    'GrafanaClient',
    'AlertManagerClient',
    'CustomMetricsRegistry'
]