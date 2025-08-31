"""Real-time Load Balancer Monitoring Engine for IA Influencer Agent Platform

Provides comprehensive real-time monitoring, alerting, and adaptive optimization
for content protection, fingerprinting, and monetization load balancing services
with ML-powered performance prediction and anomaly detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import aiohttp
import aiofiles
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import redis
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
import websockets
import ssl
import socket
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

# Prometheus metrics for real-time monitoring
REALTIME_METRICS_PROCESSED = Counter('realtime_metrics_processed_total', 'Total metrics processed')
MONITORING_LATENCY = Histogram('monitoring_latency_seconds', 'Monitoring processing latency')
ALERT_TRIGGERS = Counter('alert_triggers_total', 'Total alerts triggered', ['severity', 'service'])
ANOMALY_DETECTIONS = Counter('anomaly_detections_total', 'Anomalies detected', ['type', 'service'])
PREDICTION_ACCURACY = Gauge('prediction_accuracy_ratio', 'ML prediction accuracy', ['model', 'metric'])
SYSTEM_PERFORMANCE_SCORE = Gauge('system_performance_score', 'Overall system performance score')


class AlertSeverity(Enum):
    """Alert severity levels for monitoring"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MonitoringMetricType(Enum):
    """Types of monitoring metrics"""    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    BANDWIDTH = "bandwidth"
    CONNECTION_COUNT = "connection_count"
    QUEUE_LENGTH = "queue_length"
    CACHE_HIT_RATIO = "cache_hit_ratio"
    SSL_HANDSHAKE_TIME = "ssl_handshake_time"


@dataclass
class MonitoringMetric:
    """Individual monitoring metric data point"""    service_name: str
    metric_type: MonitoringMetricType
    value: float
    timestamp: datetime
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    source: str = "load_balancer"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""        return {
            'service_name': self.service_name,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'unit': self.unit,
            'tags': self.tags,
            'source': self.source
        }


@dataclass
class Alert:
    """Monitoring alert definition"""    id: str
    service_name: str
    metric_type: MonitoringMetricType
    severity: AlertSeverity
    message: str
    threshold_value: float
    current_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    
    def is_resolved(self) -> bool:
        """Check if alert is resolved"""        return self.resolved_at is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""        return {
            'id': self.id,
            'service_name': self.service_name,
            'metric_type': self.metric_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'threshold_value': self.threshold_value,
            'current_value': self.current_value,
            'triggered_at': self.triggered_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'tags': self.tags,
            'actions': self.actions
        }


@dataclass
class ThresholdRule:
    """Threshold-based alerting rule"""    metric_type: MonitoringMetricType
    operator: str  # '>', '<', '>=', '<=', '=='
    threshold: float
    severity: AlertSeverity
    duration_seconds: int = 60  # How long threshold must be breached
    message_template: str = "Threshold breach detected"
    actions: List[str] = field(default_factory=list)
    enabled: bool = True


class AnomalyDetector:
    """ML-based anomaly detection for load balancer metrics"""    
    def __init__(self, window_size: int = 100, sensitivity: float = 2.0):
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.baselines: Dict[str, Dict[str, float]] = {}
        
    def add_metric(self, metric: MonitoringMetric) -> bool:
        """Add metric and detect anomalies"""        metric_key = f"{metric.service_name}_{metric.metric_type.value}"
        self.metric_history[metric_key].append(metric.value)
        
        # Update baseline if we have enough data
        if len(self.metric_history[metric_key]) >= min(30, self.window_size):
            self._update_baseline(metric_key)
        
        # Detect anomaly
        return self._detect_anomaly(metric_key, metric.value)
    
    def _update_baseline(self, metric_key: str) -> None:
        """Update baseline statistics for metric"""        values = list(self.metric_history[metric_key])
        if not values:
            return
        
        self.baselines[metric_key] = {
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'median': statistics.median(values),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }
    
    def _detect_anomaly(self, metric_key: str, value: float) -> bool:
        """Detect if value is anomalous"""        if metric_key not in self.baselines:
            return False
        
        baseline = self.baselines[metric_key]
        mean = baseline['mean']
        std = baseline['std']
        
        if std == 0:
            return False
        
        # Z-score based anomaly detection
        z_score = abs(value - mean) / std
        return z_score > self.sensitivity
    
    def get_anomaly_score(self, metric_key: str, value: float) -> float:
        """Get anomaly score for a value"""        if metric_key not in self.baselines:
            return 0.0
        
        baseline = self.baselines[metric_key]
        mean = baseline['mean']
        std = baseline['std']
        
        if std == 0:
            return 0.0
        
        return abs(value - mean) / std


class PerformancePredictor:
    """ML-based performance prediction for load balancer"""    
    def __init__(self, prediction_window: int = 300):  # 5 minutes
        self.prediction_window = prediction_window
        self.metric_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self.predictions: Dict[str, Dict[str, float]] = {}
        
    def add_metric(self, metric: MonitoringMetric) -> None:
        """Add metric for prediction training"""        metric_key = f"{metric.service_name}_{metric.metric_type.value}"
        
        # Clean old data
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metric_history[metric_key] = [
            (ts, val) for ts, val in self.metric_history[metric_key]
            if ts > cutoff_time
        ]
        
        # Add new data point
        self.metric_history[metric_key].append((metric.timestamp, metric.value))
        
        # Update predictions if we have enough data
        if len(self.metric_history[metric_key]) >= 60:  # At least 1 hour of data
            self._update_predictions(metric_key)
    
    def _update_predictions(self, metric_key: str) -> None:
        """Update predictions using simple time series analysis"""        data = self.metric_history[metric_key]
        if len(data) < 10:
            return
        
        # Simple linear trend analysis
        timestamps = [(dt - data[0][0]).total_seconds() for dt, _ in data]
        values = [val for _, val in data]
        
        if len(timestamps) < 2:
            return
        
        # Calculate trend using linear regression
        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict future values
        current_time = (datetime.now() - data[0][0]).total_seconds()
        future_times = [current_time + i * 60 for i in range(1, 6)]  # Next 5 minutes
        
        predictions = {}
        for i, future_time in enumerate(future_times):
            predicted_value = slope * future_time + intercept
            predictions[f"t+{i+1}min"] = predicted_value
        
        self.predictions[metric_key] = predictions
    
    def get_predictions(self, service_name: str, metric_type: MonitoringMetricType) -> Dict[str, float]:
        """Get predictions for specific metric"""        metric_key = f"{service_name}_{metric_type.value}"
        return self.predictions.get(metric_key, {})


class RealtimeMonitor:
    """    Enterprise Real-time Load Balancer Monitor
    
    Provides comprehensive real-time monitoring with:
    - Real-time metric collection and analysis
    - ML-based anomaly detection
    - Performance prediction
    - Intelligent alerting system
    - WebSocket real-time dashboard feeds
    - Automated performance optimization
    """    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/etc/ia-influencer/monitoring.yaml"
        self.config = {}
        
        # Core components
        self.anomaly_detector = AnomalyDetector()
        self.performance_predictor = PerformancePredictor()
        
        # Data storage
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.active_alerts: Dict[str, Alert] = {}
        self.threshold_rules: List[ThresholdRule] = []
        self.alert_callbacks: List[Callable] = []
        
        # State management
        self.is_monitoring = False
        self.monitor_thread = None
        self.websocket_server = None
        self.websocket_clients = set()
        
        # Redis for distributed monitoring
        self.redis_client = None
        
        # Performance tracking
        self.last_performance_score = 0.0
        self.performance_history = deque(maxlen=1000)
        
        logger.info("Real-time Load Balancer Monitor initialized")
    
    async def initialize(self) -> bool:
        """Initialize monitoring system"""        try:
            # Load configuration
            await self._load_configuration()
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Setup default threshold rules
            self._setup_default_thresholds()
            
            # Initialize WebSocket server for real-time feeds
            await self._initialize_websocket_server()
            
            logger.info("Real-time monitoring system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring system: {e}")
            return False
    
    async def _load_configuration(self) -> None:
        """Load monitoring configuration"""        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                async with aiofiles.open(config_file, 'r') as f:
                    content = await f.read()
                    self.config = yaml.safe_load(content)
            else:
                self.config = self._get_default_configuration()
            
            logger.info("Monitoring configuration loaded")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")
            self.config = self._get_default_configuration()
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default monitoring configuration"""        return {
            'monitoring': {
                'interval_seconds': 10,
                'anomaly_sensitivity': 2.0,
                'prediction_enabled': True,
                'websocket_port': 9001
            },
            'alerts': {
                'enabled': True,
                'webhook_url': None,
                'email_notifications': False
            },
            'services': {
                'fingerprinting': {
                    'response_time_threshold': 5.0,
                    'error_rate_threshold': 0.05,
                    'throughput_min': 10.0
                },
                'protection': {
                    'response_time_threshold': 2.0,
                    'error_rate_threshold': 0.01,
                    'throughput_min': 50.0
                },
                'monetization': {
                    'response_time_threshold': 1.0,
                    'error_rate_threshold': 0.001,
                    'throughput_min': 100.0
                }
            }
        }
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection for distributed monitoring"""        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established for monitoring")
            
        except Exception as e:
            logger.warning(f"Redis not available for monitoring: {e}")
            self.redis_client = None
    
    def _setup_default_thresholds(self) -> None:
        """Setup default threshold rules for platform services"""        services_config = self.config.get('services', {})
        
        for service_name, service_config in services_config.items():
            # Response time threshold
            if 'response_time_threshold' in service_config:
                self.threshold_rules.append(ThresholdRule(
                    metric_type=MonitoringMetricType.RESPONSE_TIME,
                    operator='>',
                    threshold=service_config['response_time_threshold'],
                    severity=AlertSeverity.HIGH,
                    message_template=f"High response time for {service_name}: {{value}}s > {{threshold}}s",
                    actions=['scale_up', 'check_health']
                ))
            
            # Error rate threshold
            if 'error_rate_threshold' in service_config:
                self.threshold_rules.append(ThresholdRule(
                    metric_type=MonitoringMetricType.ERROR_RATE,
                    operator='>',
                    threshold=service_config['error_rate_threshold'],
                    severity=AlertSeverity.CRITICAL,
                    message_template=f"High error rate for {service_name}: {{value}} > {{threshold}}",
                    actions=['investigate_errors', 'failover']
                ))
            
            # Throughput minimum threshold
            if 'throughput_min' in service_config:
                self.threshold_rules.append(ThresholdRule(
                    metric_type=MonitoringMetricType.THROUGHPUT,
                    operator='<',
                    threshold=service_config['throughput_min'],
                    severity=AlertSeverity.MEDIUM,
                    message_template=f"Low throughput for {service_name}: {{value}} < {{threshold}}",
                    actions=['check_capacity', 'scale_up']
                ))
        
        logger.info(f"Setup {len(self.threshold_rules)} default threshold rules")
    
    async def _initialize_websocket_server(self) -> None:
        """Initialize WebSocket server for real-time dashboard feeds"""        try:
            websocket_port = self.config.get('monitoring', {}).get('websocket_port', 9001)
            
            async def websocket_handler(websocket, path):
                """Handle WebSocket connections for real-time data"""                self.websocket_clients.add(websocket)
                try:
                    await websocket.wait_closed()
                finally:
                    self.websocket_clients.discard(websocket)
            
            # Start WebSocket server in background
            self.websocket_server = await websockets.serve(
                websocket_handler,
                "localhost",
                websocket_port
            )
            
            logger.info(f"WebSocket server started on port {websocket_port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
    
    async def start_monitoring(self) -> None:
        """Start real-time monitoring"""        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        
        # Start monitoring loop
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Real-time monitoring started")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        interval = self.config.get('monitoring', {}).get('interval_seconds', 10)
        
        while self.is_monitoring:
            try:
                # Collect metrics from all sources
                asyncio.run(self._collect_metrics())
                
                # Process metrics
                asyncio.run(self._process_metrics())
                
                # Update performance score
                self._update_performance_score()
                
                # Send real-time updates to WebSocket clients
                asyncio.run(self._broadcast_updates())
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval * 2)  # Wait longer on error
    
    async def _collect_metrics(self) -> None:
        """Collect metrics from various sources"""        current_time = datetime.now()
        
        # Collect system metrics
        await self._collect_system_metrics(current_time)
        
        # Collect load balancer specific metrics
        await self._collect_load_balancer_metrics(current_time)
        
        # Collect service-specific metrics
        await self._collect_service_metrics(current_time)
    
    async def _collect_system_metrics(self, timestamp: datetime) -> None:
        """Collect system-level metrics"""        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric(MonitoringMetric(
                service_name="system",
                metric_type=MonitoringMetricType.CPU_USAGE,
                value=cpu_percent,
                timestamp=timestamp,
                unit="percent"
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.add_metric(MonitoringMetric(
                service_name="system",
                metric_type=MonitoringMetricType.MEMORY_USAGE,
                value=memory.percent,
                timestamp=timestamp,
                unit="percent"
            ))
            
            # Network bandwidth
            net_io = psutil.net_io_counters()
            self.add_metric(MonitoringMetric(
                service_name="system",
                metric_type=MonitoringMetricType.BANDWIDTH,
                value=net_io.bytes_sent + net_io.bytes_recv,
                timestamp=timestamp,
                unit="bytes",
                tags={"direction": "total"}
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_load_balancer_metrics(self, timestamp: datetime) -> None:
        """Collect load balancer specific metrics"""        try:
            # Connection count (simulated)
            active_connections = len(self.websocket_clients)
            self.add_metric(MonitoringMetric(
                service_name="load_balancer",
                metric_type=MonitoringMetricType.CONNECTION_COUNT,
                value=active_connections,
                timestamp=timestamp,
                unit="count"
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect load balancer metrics: {e}")
    
    async def _collect_service_metrics(self, timestamp: datetime) -> None:
        """Collect service-specific metrics"""        services = ['fingerprinting', 'protection', 'monetization', 'ai_agent', 'crawlers']
        
        for service in services:
            try:
                # Simulate metric collection (in real implementation, these would come from actual services)
                await self._collect_service_health_metrics(service, timestamp)
                
            except Exception as e:
                logger.error(f"Failed to collect metrics for {service}: {e}")
    
    async def _collect_service_health_metrics(self, service_name: str, timestamp: datetime) -> None:
        """Collect health metrics for a specific service"""        try:
            # This would typically make HTTP requests to service health endpoints
            # For demo purposes, we'll generate realistic metrics
            
            base_port = {'fingerprinting': 8001, 'protection': 8002, 'monetization': 8003, 
                        'ai_agent': 8004, 'crawlers': 8005}.get(service_name, 8000)
            
            # Simulate response time
            response_time = np.random.normal(0.5, 0.2)  # Average 500ms with variation
            if response_time < 0:
                response_time = 0.1
            
            self.add_metric(MonitoringMetric(
                service_name=service_name,
                metric_type=MonitoringMetricType.RESPONSE_TIME,
                value=response_time,
                timestamp=timestamp,
                unit="seconds",
                tags={"port": str(base_port)}
            ))
            
            # Simulate error rate
            error_rate = max(0, np.random.normal(0.01, 0.005))  # Low error rate
            self.add_metric(MonitoringMetric(
                service_name=service_name,
                metric_type=MonitoringMetricType.ERROR_RATE,
                value=error_rate,
                timestamp=timestamp,
                unit="ratio"
            ))
            
            # Simulate throughput
            throughput = max(0, np.random.normal(100, 20))  # Requests per second
            self.add_metric(MonitoringMetric(
                service_name=service_name,
                metric_type=MonitoringMetricType.THROUGHPUT,
                value=throughput,
                timestamp=timestamp,
                unit="requests/second"
            ))
            
        except Exception as e:
            logger.error(f"Failed to collect health metrics for {service_name}: {e}")
    
    def add_metric(self, metric: MonitoringMetric) -> None:
        """Add a metric to the monitoring system"""        # Add to buffer
        self.metrics_buffer.append(metric)
        
        # Update anomaly detector
        is_anomaly = self.anomaly_detector.add_metric(metric)
        if is_anomaly:
            ANOMALY_DETECTIONS.labels(
                type="statistical",
                service=metric.service_name
            ).inc()
            
            logger.warning(f"Anomaly detected: {metric.service_name} {metric.metric_type.value} = {metric.value}")
        
        # Update performance predictor
        self.performance_predictor.add_metric(metric)
        
        # Check threshold rules
        self._check_threshold_rules(metric)
        
        # Store in Redis if available
        if self.redis_client:
            try:
                key = f"metrics:{metric.service_name}:{metric.metric_type.value}"
                self.redis_client.zadd(key, {json.dumps(metric.to_dict()): time.time()})
                # Keep only last 1000 metrics per type
                self.redis_client.zremrangebyrank(key, 0, -1001)
            except Exception as e:
                logger.error(f"Failed to store metric in Redis: {e}")
        
        # Update Prometheus metrics
        REALTIME_METRICS_PROCESSED.inc()
    
    def _check_threshold_rules(self, metric: MonitoringMetric) -> None:
        """Check if metric violates any threshold rules"""        for rule in self.threshold_rules:
            if not rule.enabled:
                continue
            
            if rule.metric_type != metric.metric_type:
                continue
            
            # Evaluate threshold condition
            violated = False
            if rule.operator == '>':
                violated = metric.value > rule.threshold
            elif rule.operator == '<':
                violated = metric.value < rule.threshold
            elif rule.operator == '>=':
                violated = metric.value >= rule.threshold
            elif rule.operator == '<=':
                violated = metric.value <= rule.threshold
            elif rule.operator == '==':
                violated = metric.value == rule.threshold
            
            if violated:
                alert_id = f"{metric.service_name}_{rule.metric_type.value}_{rule.operator}_{rule.threshold}"
                
                # Check if alert already exists
                if alert_id not in self.active_alerts:
                    alert = Alert(
                        id=alert_id,
                        service_name=metric.service_name,
                        metric_type=rule.metric_type,
                        severity=rule.severity,
                        message=rule.message_template.format(
                            value=metric.value,
                            threshold=rule.threshold
                        ),
                        threshold_value=rule.threshold,
                        current_value=metric.value,
                        triggered_at=metric.timestamp,
                        tags=metric.tags,
                        actions=rule.actions
                    )
                    
                    self.active_alerts[alert_id] = alert
                    
                    # Trigger alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Alert callback failed: {e}")
                    
                    # Update Prometheus metrics
                    ALERT_TRIGGERS.labels(
                        severity=rule.severity.value,
                        service=metric.service_name
                    ).inc()
                    
                    logger.warning(f"Alert triggered: {alert.message}")
    
    async def _process_metrics(self) -> None:
        """Process collected metrics for analysis"""        try:
            # Calculate performance score
            current_score = self._calculate_performance_score()
            self.performance_history.append(current_score)
            self.last_performance_score = current_score
            
            # Update Prometheus gauge
            SYSTEM_PERFORMANCE_SCORE.set(current_score)
            
        except Exception as e:
            logger.error(f"Failed to process metrics: {e}")
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall system performance score (0-100)"""        if not self.metrics_buffer:
            return 0.0
        
        scores = []
        
        # Recent metrics (last 5 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_metrics = [m for m in self.metrics_buffer if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return self.last_performance_score
        
        # Response time score (inverse relationship)
        response_times = [m.value for m in recent_metrics if m.metric_type == MonitoringMetricType.RESPONSE_TIME]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            response_score = max(0, 100 - (avg_response_time * 50))  # 2s = 0 score
            scores.append(response_score)
        
        # Error rate score (inverse relationship)
        error_rates = [m.value for m in recent_metrics if m.metric_type == MonitoringMetricType.ERROR_RATE]
        if error_rates:
            avg_error_rate = statistics.mean(error_rates)
            error_score = max(0, 100 - (avg_error_rate * 10000))  # 1% error = 0 score
            scores.append(error_score)
        
        # System resource scores
        cpu_usage = [m.value for m in recent_metrics if m.metric_type == MonitoringMetricType.CPU_USAGE and m.service_name == "system"]
        if cpu_usage:
            avg_cpu = statistics.mean(cpu_usage)
            cpu_score = max(0, 100 - avg_cpu)  # 100% CPU = 0 score
            scores.append(cpu_score)
        
        memory_usage = [m.value for m in recent_metrics if m.metric_type == MonitoringMetricType.MEMORY_USAGE and m.service_name == "system"]
        if memory_usage:
            avg_memory = statistics.mean(memory_usage)
            memory_score = max(0, 100 - avg_memory)  # 100% memory = 0 score
            scores.append(memory_score)
        
        # Calculate weighted average
        if scores:
            return statistics.mean(scores)
        else:
            return self.last_performance_score
    
    def _update_performance_score(self) -> None:
        """Update performance score tracking"""        current_score = self._calculate_performance_score()
        self.performance_history.append(current_score)
        self.last_performance_score = current_score
    
    async def _broadcast_updates(self) -> None:
        """Broadcast real-time updates to WebSocket clients"""        if not self.websocket_clients:
            return
        
        try:
            # Prepare update data
            update_data = {
                'timestamp': datetime.now().isoformat(),
                'performance_score': self.last_performance_score,
                'active_alerts': len(self.active_alerts),
                'metrics_processed': len(self.metrics_buffer),
                'recent_metrics': [
                    m.to_dict() for m in list(self.metrics_buffer)[-10:]  # Last 10 metrics
                ],
                'active_alerts_list': [
                    alert.to_dict() for alert in list(self.active_alerts.values())[-5:]  # Last 5 alerts
                ]
            }
            
            message = json.dumps(update_data)
            
            # Send to all connected clients
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"Failed to send WebSocket update: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients
            
        except Exception as e:
            logger.error(f"Failed to broadcast updates: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add callback function for alert notifications"""        self.alert_callbacks.append(callback)
    
    def get_metrics(self, service_name: Optional[str] = None, 
                   metric_type: Optional[MonitoringMetricType] = None,
                   since: Optional[datetime] = None) -> List[MonitoringMetric]:
        """Get metrics with optional filtering"""        filtered_metrics = list(self.metrics_buffer)
        
        if service_name:
            filtered_metrics = [m for m in filtered_metrics if m.service_name == service_name]
        
        if metric_type:
            filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
        
        if since:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
        
        return filtered_metrics
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""        return list(self.active_alerts.values())
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert"""        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            logger.info(f"Alert {alert_id} resolved manually")
            return True
        return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary and statistics"""        return {
            'current_score': self.last_performance_score,
            'average_score_1h': statistics.mean(list(self.performance_history)[-360:]) if self.performance_history else 0,
            'active_alerts': len(self.active_alerts),
            'metrics_processed': len(self.metrics_buffer),
            'anomaly_detection_enabled': True,
            'prediction_enabled': self.config.get('monitoring', {}).get('prediction_enabled', True),
            'monitoring_interval': self.config.get('monitoring', {}).get('interval_seconds', 10),
            'websocket_clients': len(self.websocket_clients),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_predictions(self, service_name: str, metric_type: MonitoringMetricType) -> Dict[str, float]:
        """Get performance predictions for service"""        return self.performance_predictor.get_predictions(service_name, metric_type)
    
    async def stop_monitoring(self) -> None:
        """Stop real-time monitoring"""        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        logger.info("Real-time monitoring stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of monitoring system"""        return {
            'is_monitoring': self.is_monitoring,
            'config_loaded': bool(self.config),
            'redis_available': self.redis_client is not None,
            'websocket_clients': len(self.websocket_clients),
            'active_alerts': len(self.active_alerts),
            'metrics_buffer_size': len(self.metrics_buffer),
            'threshold_rules': len(self.threshold_rules),
            'performance_score': self.last_performance_score,
            'anomaly_detector_initialized': self.anomaly_detector is not None,
            'performance_predictor_initialized': self.performance_predictor is not None,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Demo function for real-time monitoring"""    monitor = RealtimeMonitor()
    
    try:
        # Initialize monitoring
        await monitor.initialize()
        
        # Add alert callback for demo
        def alert_handler(alert: Alert):
            print(f"🚨 ALERT: {alert.severity.value.upper()} - {alert.message}")
        
        monitor.add_alert_callback(alert_handler)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        print("Real-time monitoring started. Press Ctrl+C to stop...")
        
        # Run for demo
        while True:
            await asyncio.sleep(30)
            
            # Print status
            status = await monitor.get_status()
            print(f"Performance Score: {status['performance_score']:.1f}")
            print(f"Active Alerts: {status['active_alerts']}")
            print(f"Metrics Processed: {status['metrics_buffer_size']}")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("Stopping monitoring...")
    finally:
        await monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
