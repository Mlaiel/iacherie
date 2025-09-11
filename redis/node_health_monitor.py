#!/usr/bin/env python3
"""
Redis Node Health Monitor - Ainflue Platform
===========================================

Real-time Redis cluster node health monitoring with predictive analytics,
automated alerting, and intelligent diagnostics.

Author: Fahed Mlaiel (mlaiel@live.de)
Roles: Lead Dev IA + Backend Senior + DBA + DevOps + ML Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
import psutil
import aiohttp
from datetime import datetime, timedelta
import numpy as np
from collections import deque, defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Node health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class NodeMetrics:
    """Redis node metrics structure"""
    node_id: str
    host: str
    port: int
    timestamp: float
    
    # Connection metrics
    connected_clients: int
    blocked_clients: int
    total_connections_received: int
    
    # Memory metrics
    used_memory: int
    used_memory_peak: int
    used_memory_rss: int
    memory_fragmentation_ratio: float
    maxmemory: int
    
    # Performance metrics
    total_commands_processed: int
    instantaneous_ops_per_sec: int
    avg_ttl: float
    
    # Network metrics
    total_net_input_bytes: int
    total_net_output_bytes: int
    instantaneous_input_kbps: float
    instantaneous_output_kbps: float
    
    # Persistence metrics
    rdb_last_save_time: int
    rdb_changes_since_last_save: int
    aof_last_rewrite_time_sec: float
    aof_current_size: int
    
    # System metrics
    cpu_usage: float
    uptime_in_seconds: int
    used_cpu_sys: float
    used_cpu_user: float
    
    # Cluster specific
    cluster_state: str
    cluster_slots_assigned: int
    cluster_known_nodes: int


@dataclass
class HealthAlert:
    """Health alert structure"""
    alert_id: str
    node_id: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: float
    resolved: bool = False
    resolution_time: Optional[float] = None
    resolution_action: Optional[str] = None


@dataclass
class NodeHealthScore:
    """Node health scoring"""
    node_id: str
    overall_score: float  # 0-100
    memory_score: float
    performance_score: float
    network_score: float
    availability_score: float
    trend_score: float
    predicted_issues: List[str]


class RedisNodeHealthMonitor:
    """
    Advanced Redis Node Health Monitor
    
    Features:
    - Real-time health monitoring
    - Predictive analytics
    - Automated alerting
    - Performance trend analysis
    - Capacity planning
    - Intelligent diagnostics
    - Recovery recommendations
    """

    def __init__(self, cluster_client: RedisCluster, config: Dict[str, Any] = None):
        """Initialize health monitor"""
        self.cluster_client = cluster_client
        self.config = config or self._get_default_config()
        
        # Monitoring state
        self.node_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_metrics: Dict[str, NodeMetrics] = {}
        self.health_scores: Dict[str, NodeHealthScore] = {}
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.alerting_enabled = self.config.get('alerting_enabled', True)
        
        # Thresholds
        self.thresholds = self.config.get('thresholds', self._get_default_thresholds())
        
        # Predictive analytics
        self.prediction_window = self.config.get('prediction_window', 3600)  # 1 hour
        self.prediction_models: Dict[str, Dict] = {}

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'monitoring_interval': 30,
            'alerting_enabled': True,
            'alert_cooldown': 300,  # 5 minutes
            'metrics_retention': 86400,  # 24 hours
            'prediction_enabled': True,
            'notification_webhook': None,
            'email_alerts': [],
            'slack_webhook': None
        }

    def _get_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get default health thresholds"""
        return {
            'memory': {
                'warning': 0.80,  # 80% memory usage
                'critical': 0.90,  # 90% memory usage
                'fragmentation_warning': 1.5,
                'fragmentation_critical': 2.0
            },
            'performance': {
                'ops_warning': 10000,  # ops/sec
                'ops_critical': 50000,
                'latency_warning': 10.0,  # ms
                'latency_critical': 50.0
            },
            'connections': {
                'warning': 8000,
                'critical': 9000,
                'blocked_warning': 100,
                'blocked_critical': 500
            },
            'network': {
                'input_warning': 10240,  # KB/s
                'input_critical': 51200,
                'output_warning': 10240,
                'output_critical': 51200
            },
            'system': {
                'cpu_warning': 0.80,
                'cpu_critical': 0.95,
                'disk_warning': 0.85,
                'disk_critical': 0.95
            }
        }

    async def initialize(self) -> None:
        """Initialize health monitor"""
        try:
            # Discover nodes
            await self._discover_nodes()
            
            # Initialize prediction models
            if self.config.get('prediction_enabled', True):
                await self._initialize_prediction_models()
            
            # Start monitoring tasks
            await self._start_monitoring()
            
            logger.info("Node health monitor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize health monitor: {e}")
            raise

    async def _discover_nodes(self) -> None:
        """Discover cluster nodes"""
        try:
            nodes_info = await self.cluster_client.cluster_nodes()
            
            for line in nodes_info.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 8:
                        node_id = parts[0]
                        endpoint = parts[1].split('@')[0]
                        host, port = endpoint.split(':')
                        
                        # Initialize metrics deque for node
                        if node_id not in self.node_metrics:
                            self.node_metrics[node_id] = deque(maxlen=1000)
                        
                        # Initialize prediction model for node
                        if node_id not in self.prediction_models:
                            self.prediction_models[node_id] = {
                                'memory_trend': [],
                                'performance_trend': [],
                                'error_patterns': [],
                                'seasonal_patterns': {}
                            }
            
            logger.info(f"Discovered {len(self.node_metrics)} nodes for monitoring")
            
        except Exception as e:
            logger.error(f"Failed to discover nodes: {e}")

    async def _initialize_prediction_models(self) -> None:
        """Initialize predictive analytics models"""
        try:
            # Simple moving average and trend analysis models
            # In production, this could use more sophisticated ML models
            for node_id in self.node_metrics.keys():
                self.prediction_models[node_id] = {
                    'memory_trend': deque(maxlen=100),
                    'performance_trend': deque(maxlen=100),
                    'anomaly_baseline': {},
                    'seasonal_patterns': defaultdict(list),
                    'failure_indicators': []
                }
            
            logger.info("Prediction models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction models: {e}")

    async def _start_monitoring(self) -> None:
        """Start monitoring tasks"""
        try:
            # Health monitoring task
            health_task = asyncio.create_task(self._health_monitoring_loop())
            self.monitoring_tasks.append(health_task)
            
            # Alert processing task
            if self.alerting_enabled:
                alert_task = asyncio.create_task(self._alert_processing_loop())
                self.monitoring_tasks.append(alert_task)
            
            # Prediction task
            if self.config.get('prediction_enabled', True):
                prediction_task = asyncio.create_task(self._prediction_loop())
                self.monitoring_tasks.append(prediction_task)
            
            # Cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.monitoring_tasks.append(cleanup_task)
            
            logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")

    async def _health_monitoring_loop(self) -> None:
        """Main health monitoring loop"""
        while True:
            try:
                # Collect metrics from all nodes
                await self._collect_all_metrics()
                
                # Calculate health scores
                await self._calculate_health_scores()
                
                # Check for alerts
                await self._check_alerts()
                
                # Sleep until next cycle
                interval = self.config.get('monitoring_interval', 30)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(10)

    async def _collect_all_metrics(self) -> None:
        """Collect metrics from all nodes"""
        tasks = []
        
        for node_id in self.node_metrics.keys():
            task = asyncio.create_task(self._collect_node_metrics(node_id))
            tasks.append(task)
        
        # Wait for all metrics collection to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                node_id = list(self.node_metrics.keys())[i]
                logger.warning(f"Failed to collect metrics for node {node_id}: {result}")

    async def _collect_node_metrics(self, node_id: str) -> None:
        """Collect metrics from a specific node"""
        try:
            # Get node connection info
            node_info = await self._get_node_connection_info(node_id)
            if not node_info:
                return
            
            # Connect to node
            node_client = redis.Redis(
                host=node_info['host'],
                port=node_info['port'],
                decode_responses=True,
                socket_timeout=5.0
            )
            
            # Collect Redis info
            memory_info = await node_client.info('memory')
            stats_info = await node_client.info('stats')
            clients_info = await node_client.info('clients')
            server_info = await node_client.info('server')
            persistence_info = await node_client.info('persistence')
            cluster_info = await node_client.info('cluster')
            
            # System metrics (if available)
            cpu_usage = 0.0
            try:
                cpu_usage = psutil.cpu_percent()
            except:
                pass
            
            # Create metrics object
            metrics = NodeMetrics(
                node_id=node_id,
                host=node_info['host'],
                port=node_info['port'],
                timestamp=time.time(),
                
                # Connection metrics
                connected_clients=clients_info.get('connected_clients', 0),
                blocked_clients=clients_info.get('blocked_clients', 0),
                total_connections_received=stats_info.get('total_connections_received', 0),
                
                # Memory metrics
                used_memory=memory_info.get('used_memory', 0),
                used_memory_peak=memory_info.get('used_memory_peak', 0),
                used_memory_rss=memory_info.get('used_memory_rss', 0),
                memory_fragmentation_ratio=memory_info.get('mem_fragmentation_ratio', 1.0),
                maxmemory=memory_info.get('maxmemory', 0),
                
                # Performance metrics
                total_commands_processed=stats_info.get('total_commands_processed', 0),
                instantaneous_ops_per_sec=stats_info.get('instantaneous_ops_per_sec', 0),
                avg_ttl=stats_info.get('avg_ttl', 0.0),
                
                # Network metrics
                total_net_input_bytes=stats_info.get('total_net_input_bytes', 0),
                total_net_output_bytes=stats_info.get('total_net_output_bytes', 0),
                instantaneous_input_kbps=stats_info.get('instantaneous_input_kbps', 0.0),
                instantaneous_output_kbps=stats_info.get('instantaneous_output_kbps', 0.0),
                
                # Persistence metrics
                rdb_last_save_time=persistence_info.get('rdb_last_save_time', 0),
                rdb_changes_since_last_save=persistence_info.get('rdb_changes_since_last_save', 0),
                aof_last_rewrite_time_sec=persistence_info.get('aof_last_rewrite_time_sec', 0.0),
                aof_current_size=persistence_info.get('aof_current_size', 0),
                
                # System metrics
                cpu_usage=cpu_usage,
                uptime_in_seconds=server_info.get('uptime_in_seconds', 0),
                used_cpu_sys=server_info.get('used_cpu_sys', 0.0),
                used_cpu_user=server_info.get('used_cpu_user', 0.0),
                
                # Cluster metrics
                cluster_state=cluster_info.get('cluster_state', 'unknown'),
                cluster_slots_assigned=cluster_info.get('cluster_slots_assigned', 0),
                cluster_known_nodes=cluster_info.get('cluster_known_nodes', 0)
            )
            
            # Store metrics
            self.node_metrics[node_id].append(metrics)
            self.current_metrics[node_id] = metrics
            
            # Update prediction models
            if self.config.get('prediction_enabled', True):
                await self._update_prediction_models(node_id, metrics)
            
            await node_client.close()
            
        except Exception as e:
            logger.warning(f"Failed to collect metrics for node {node_id}: {e}")
            
            # Create unavailable metrics entry
            if node_id in self.current_metrics:
                unavailable_metrics = self.current_metrics[node_id]
                unavailable_metrics.timestamp = time.time()
                self.node_metrics[node_id].append(unavailable_metrics)

    async def _get_node_connection_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node connection information"""
        try:
            nodes_info = await self.cluster_client.cluster_nodes()
            
            for line in nodes_info.split('\n'):
                if line.strip() and line.startswith(node_id):
                    parts = line.split()
                    endpoint = parts[1].split('@')[0]
                    host, port = endpoint.split(':')
                    return {'host': host, 'port': int(port)}
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get connection info for node {node_id}: {e}")
            return None

    async def _calculate_health_scores(self) -> None:
        """Calculate health scores for all nodes"""
        for node_id, metrics in self.current_metrics.items():
            try:
                health_score = await self._calculate_node_health_score(node_id, metrics)
                self.health_scores[node_id] = health_score
                
            except Exception as e:
                logger.warning(f"Failed to calculate health score for node {node_id}: {e}")

    async def _calculate_node_health_score(self, node_id: str, 
                                         metrics: NodeMetrics) -> NodeHealthScore:
        """Calculate comprehensive health score for a node"""
        try:
            # Memory score (0-100)
            memory_score = 100.0
            if metrics.maxmemory > 0:
                memory_usage_ratio = metrics.used_memory / metrics.maxmemory
                memory_score = max(0, 100 - (memory_usage_ratio * 100))
                
                # Penalize fragmentation
                if metrics.memory_fragmentation_ratio > 1.5:
                    fragmentation_penalty = (metrics.memory_fragmentation_ratio - 1.0) * 20
                    memory_score = max(0, memory_score - fragmentation_penalty)
            
            # Performance score (0-100)
            performance_score = 100.0
            if metrics.instantaneous_ops_per_sec > self.thresholds['performance']['ops_warning']:
                ops_ratio = metrics.instantaneous_ops_per_sec / self.thresholds['performance']['ops_critical']
                performance_score = max(0, 100 - (ops_ratio * 50))
            
            # Network score (0-100)
            network_score = 100.0
            network_load = max(
                metrics.instantaneous_input_kbps / self.thresholds['network']['input_critical'],
                metrics.instantaneous_output_kbps / self.thresholds['network']['output_critical']
            )
            if network_load > 0.5:
                network_score = max(0, 100 - (network_load * 50))
            
            # Availability score (0-100)
            availability_score = 100.0
            if metrics.cluster_state != 'ok':
                availability_score = 50.0
            
            # Check recent metrics for availability
            if node_id in self.node_metrics and len(self.node_metrics[node_id]) > 10:
                recent_metrics = list(self.node_metrics[node_id])[-10:]
                failed_checks = sum(1 for m in recent_metrics 
                                  if time.time() - m.timestamp > 120)  # Failed if older than 2 min
                availability_score = max(0, 100 - (failed_checks * 10))
            
            # Trend score (0-100) - based on historical data
            trend_score = await self._calculate_trend_score(node_id)
            
            # Overall score (weighted average)
            overall_score = (
                memory_score * 0.25 +
                performance_score * 0.25 +
                network_score * 0.20 +
                availability_score * 0.20 +
                trend_score * 0.10
            )
            
            # Predict potential issues
            predicted_issues = await self._predict_issues(node_id, metrics)
            
            return NodeHealthScore(
                node_id=node_id,
                overall_score=overall_score,
                memory_score=memory_score,
                performance_score=performance_score,
                network_score=network_score,
                availability_score=availability_score,
                trend_score=trend_score,
                predicted_issues=predicted_issues
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate health score for {node_id}: {e}")
            return NodeHealthScore(
                node_id=node_id,
                overall_score=0.0,
                memory_score=0.0,
                performance_score=0.0,
                network_score=0.0,
                availability_score=0.0,
                trend_score=0.0,
                predicted_issues=["health_calculation_failed"]
            )

    async def _calculate_trend_score(self, node_id: str) -> float:
        """Calculate trend score based on historical data"""
        try:
            if node_id not in self.node_metrics or len(self.node_metrics[node_id]) < 10:
                return 100.0  # No data, assume good
            
            recent_metrics = list(self.node_metrics[node_id])[-20:]  # Last 20 measurements
            
            # Memory trend
            memory_values = [m.used_memory for m in recent_metrics if m.maxmemory > 0]
            memory_trend = 0.0
            if len(memory_values) > 5:
                # Simple linear trend calculation
                x = list(range(len(memory_values)))
                memory_trend = np.polyfit(x, memory_values, 1)[0]  # Slope
            
            # Performance trend
            ops_values = [m.instantaneous_ops_per_sec for m in recent_metrics]
            ops_trend = 0.0
            if len(ops_values) > 5:
                x = list(range(len(ops_values)))
                ops_trend = np.polyfit(x, ops_values, 1)[0]
            
            # Calculate trend score
            trend_score = 100.0
            
            # Penalize negative trends
            if memory_trend > 0:  # Memory increasing
                trend_score -= min(50, abs(memory_trend) * 1000000)  # Scale factor
            
            if ops_trend > self.thresholds['performance']['ops_warning'] / 100:
                trend_score -= min(30, abs(ops_trend) * 100)
            
            return max(0, trend_score)
            
        except Exception as e:
            logger.warning(f"Failed to calculate trend score for {node_id}: {e}")
            return 50.0  # Default moderate score

    async def _predict_issues(self, node_id: str, metrics: NodeMetrics) -> List[str]:
        """Predict potential issues using simple heuristics"""
        issues = []
        
        try:
            # Memory issues
            if metrics.maxmemory > 0:
                memory_ratio = metrics.used_memory / metrics.maxmemory
                if memory_ratio > 0.85:
                    issues.append("memory_pressure_increasing")
                
                if metrics.memory_fragmentation_ratio > 2.0:
                    issues.append("high_memory_fragmentation")
            
            # Performance issues
            if metrics.instantaneous_ops_per_sec > self.thresholds['performance']['ops_warning']:
                issues.append("high_operation_load")
            
            # Connection issues
            if metrics.connected_clients > self.thresholds['connections']['warning']:
                issues.append("connection_pool_exhaustion")
            
            if metrics.blocked_clients > self.thresholds['connections']['blocked_warning']:
                issues.append("client_blocking_issues")
            
            # Persistence issues
            if metrics.rdb_changes_since_last_save > 10000:
                issues.append("rdb_backup_delay")
            
            # Cluster issues
            if metrics.cluster_state != 'ok':
                issues.append("cluster_instability")
            
            # Trend-based predictions
            if node_id in self.node_metrics and len(self.node_metrics[node_id]) > 10:
                recent_metrics = list(self.node_metrics[node_id])[-10:]
                
                # Check for increasing memory trend
                memory_values = [m.used_memory for m in recent_metrics if m.maxmemory > 0]
                if len(memory_values) > 5:
                    memory_increase_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)
                    if memory_increase_rate > 1024 * 1024:  # 1MB per measurement
                        issues.append("memory_leak_suspected")
            
            return issues
            
        except Exception as e:
            logger.error(f"Failed to predict issues for {node_id}: {e}")
            return ["prediction_failed"]

    async def _check_alerts(self) -> None:
        """Check for alert conditions"""
        for node_id, metrics in self.current_metrics.items():
            try:
                await self._check_node_alerts(node_id, metrics)
            except Exception as e:
                logger.error(f"Failed to check alerts for node {node_id}: {e}")

    async def _check_node_alerts(self, node_id: str, metrics: NodeMetrics) -> None:
        """Check alert conditions for a specific node"""
        alerts_to_create = []
        
        # Memory alerts
        if metrics.maxmemory > 0:
            memory_ratio = metrics.used_memory / metrics.maxmemory
            
            if memory_ratio > self.thresholds['memory']['critical']:
                alerts_to_create.append({
                    'severity': AlertSeverity.CRITICAL,
                    'title': f"Critical Memory Usage - Node {node_id}",
                    'description': f"Memory usage at {memory_ratio:.1%} exceeds critical threshold"
                })
            elif memory_ratio > self.thresholds['memory']['warning']:
                alerts_to_create.append({
                    'severity': AlertSeverity.WARNING,
                    'title': f"High Memory Usage - Node {node_id}",
                    'description': f"Memory usage at {memory_ratio:.1%} exceeds warning threshold"
                })
        
        # Performance alerts
        if metrics.instantaneous_ops_per_sec > self.thresholds['performance']['ops_critical']:
            alerts_to_create.append({
                'severity': AlertSeverity.CRITICAL,
                'title': f"Critical Operation Load - Node {node_id}",
                'description': f"Operations per second ({metrics.instantaneous_ops_per_sec}) exceeds critical threshold"
            })
        
        # Connection alerts
        if metrics.connected_clients > self.thresholds['connections']['critical']:
            alerts_to_create.append({
                'severity': AlertSeverity.CRITICAL,
                'title': f"Connection Pool Exhaustion - Node {node_id}",
                'description': f"Connected clients ({metrics.connected_clients}) exceeds critical threshold"
            })
        
        # Cluster alerts
        if metrics.cluster_state != 'ok':
            alerts_to_create.append({
                'severity': AlertSeverity.WARNING,
                'title': f"Cluster State Issue - Node {node_id}",
                'description': f"Cluster state is '{metrics.cluster_state}' instead of 'ok'"
            })
        
        # Create alerts
        for alert_data in alerts_to_create:
            await self._create_alert(node_id, **alert_data)

    async def _create_alert(self, node_id: str, severity: AlertSeverity, 
                          title: str, description: str) -> None:
        """Create new alert"""
        try:
            alert_id = f"{node_id}_{int(time.time())}_{severity.value}"
            
            # Check for duplicate alerts (cooldown period)
            cooldown = self.config.get('alert_cooldown', 300)
            similar_alerts = [
                alert for alert in self.active_alerts.values()
                if (alert.node_id == node_id and 
                    alert.title == title and
                    time.time() - alert.timestamp < cooldown)
            ]
            
            if similar_alerts:
                return  # Skip duplicate alert
            
            alert = HealthAlert(
                alert_id=alert_id,
                node_id=node_id,
                severity=severity,
                title=title,
                description=description,
                timestamp=time.time()
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Send notifications
            if self.alerting_enabled:
                await self._send_alert_notification(alert)
            
            logger.warning(f"Alert created: {title} ({severity.value})")
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")

    async def _send_alert_notification(self, alert: HealthAlert) -> None:
        """Send alert notification"""
        try:
            # Webhook notification
            webhook_url = self.config.get('notification_webhook')
            if webhook_url:
                await self._send_webhook_notification(webhook_url, alert)
            
            # Slack notification
            slack_webhook = self.config.get('slack_webhook')
            if slack_webhook:
                await self._send_slack_notification(slack_webhook, alert)
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")

    async def _send_webhook_notification(self, webhook_url: str, alert: HealthAlert) -> None:
        """Send webhook notification"""
        try:
            payload = {
                'alert_id': alert.alert_id,
                'node_id': alert.node_id,
                'severity': alert.severity.value,
                'title': alert.title,
                'description': alert.description,
                'timestamp': alert.timestamp
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert {alert.alert_id}")
                    else:
                        logger.warning(f"Webhook notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Webhook notification error: {e}")

    async def _send_slack_notification(self, slack_webhook: str, alert: HealthAlert) -> None:
        """Send Slack notification"""
        try:
            color = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9800",
                AlertSeverity.CRITICAL: "#f44336",
                AlertSeverity.EMERGENCY: "#9c27b0"
            }.get(alert.severity, "#607d8b")
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {"title": "Node ID", "value": alert.node_id, "short": True},
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Time", "value": datetime.fromtimestamp(alert.timestamp).strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(slack_webhook, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert {alert.alert_id}")
                    else:
                        logger.warning(f"Slack notification failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Slack notification error: {e}")

    async def _update_prediction_models(self, node_id: str, metrics: NodeMetrics) -> None:
        """Update prediction models with new metrics"""
        try:
            if node_id not in self.prediction_models:
                return
            
            model = self.prediction_models[node_id]
            
            # Update memory trend
            if metrics.maxmemory > 0:
                memory_ratio = metrics.used_memory / metrics.maxmemory
                model['memory_trend'].append({
                    'timestamp': metrics.timestamp,
                    'value': memory_ratio
                })
            
            # Update performance trend
            model['performance_trend'].append({
                'timestamp': metrics.timestamp,
                'ops_per_sec': metrics.instantaneous_ops_per_sec,
                'connected_clients': metrics.connected_clients
            })
            
            # Update seasonal patterns (hourly)
            hour = datetime.fromtimestamp(metrics.timestamp).hour
            model['seasonal_patterns'][hour].append({
                'memory_usage': metrics.used_memory,
                'ops_per_sec': metrics.instantaneous_ops_per_sec
            })
            
            # Keep only recent data
            if len(model['seasonal_patterns'][hour]) > 30:  # Last 30 days for this hour
                model['seasonal_patterns'][hour] = model['seasonal_patterns'][hour][-30:]
                
        except Exception as e:
            logger.error(f"Failed to update prediction models for {node_id}: {e}")

    async def _alert_processing_loop(self) -> None:
        """Process and manage alerts"""
        while True:
            try:
                # Auto-resolve alerts
                await self._auto_resolve_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Alert processing loop error: {e}")
                await asyncio.sleep(30)

    async def _auto_resolve_alerts(self) -> None:
        """Automatically resolve alerts when conditions improve"""
        for alert_id, alert in list(self.active_alerts.items()):
            try:
                if alert.resolved:
                    continue
                
                node_id = alert.node_id
                if node_id not in self.current_metrics:
                    continue
                
                metrics = self.current_metrics[node_id]
                should_resolve = False
                
                # Check if alert condition has improved
                if "Memory Usage" in alert.title and metrics.maxmemory > 0:
                    memory_ratio = metrics.used_memory / metrics.maxmemory
                    if memory_ratio < self.thresholds['memory']['warning']:
                        should_resolve = True
                
                elif "Operation Load" in alert.title:
                    if metrics.instantaneous_ops_per_sec < self.thresholds['performance']['ops_warning']:
                        should_resolve = True
                
                elif "Connection Pool" in alert.title:
                    if metrics.connected_clients < self.thresholds['connections']['warning']:
                        should_resolve = True
                
                elif "Cluster State" in alert.title:
                    if metrics.cluster_state == 'ok':
                        should_resolve = True
                
                if should_resolve:
                    alert.resolved = True
                    alert.resolution_time = time.time()
                    alert.resolution_action = "auto_resolved_condition_improved"
                    
                    del self.active_alerts[alert_id]
                    logger.info(f"Auto-resolved alert: {alert.title}")
                    
            except Exception as e:
                logger.error(f"Failed to process alert {alert_id}: {e}")

    async def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts"""
        try:
            current_time = time.time()
            retention_period = self.config.get('alert_retention', 86400)  # 24 hours
            
            # Remove old alerts from active alerts
            old_alerts = [
                alert_id for alert_id, alert in self.active_alerts.items()
                if current_time - alert.timestamp > retention_period
            ]
            
            for alert_id in old_alerts:
                del self.active_alerts[alert_id]
            
            if old_alerts:
                logger.info(f"Cleaned up {len(old_alerts)} old alerts")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")

    async def _prediction_loop(self) -> None:
        """Prediction and analytics loop"""
        while True:
            try:
                # Run predictive analytics
                await self._run_predictive_analytics()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Prediction loop error: {e}")
                await asyncio.sleep(60)

    async def _run_predictive_analytics(self) -> None:
        """Run predictive analytics on collected data"""
        try:
            for node_id in self.prediction_models.keys():
                await self._analyze_node_trends(node_id)
                
        except Exception as e:
            logger.error(f"Predictive analytics error: {e}")

    async def _analyze_node_trends(self, node_id: str) -> None:
        """Analyze trends for a specific node"""
        try:
            if node_id not in self.prediction_models or node_id not in self.node_metrics:
                return
            
            model = self.prediction_models[node_id]
            recent_metrics = list(self.node_metrics[node_id])[-100:]  # Last 100 measurements
            
            if len(recent_metrics) < 20:
                return  # Not enough data
            
            # Analyze memory trend
            memory_values = [m.used_memory for m in recent_metrics if m.maxmemory > 0]
            if len(memory_values) > 10:
                # Predict memory exhaustion
                x = list(range(len(memory_values)))
                slope, intercept = np.polyfit(x, memory_values, 1)
                
                # Predict when memory will reach critical level
                current_memory = memory_values[-1]
                current_metrics = recent_metrics[-1]
                
                if current_metrics.maxmemory > 0 and slope > 0:
                    critical_memory = current_metrics.maxmemory * 0.9
                    time_to_critical = (critical_memory - current_memory) / slope
                    
                    # If critical in less than 1 hour (assuming 30s intervals)
                    if 0 < time_to_critical < 120:  # 120 measurements = 1 hour
                        await self._create_alert(
                            node_id,
                            AlertSeverity.WARNING,
                            f"Predicted Memory Exhaustion - Node {node_id}",
                            f"Memory exhaustion predicted in {time_to_critical * 0.5:.1f} minutes"
                        )
            
            # Analyze performance trends
            ops_values = [m.instantaneous_ops_per_sec for m in recent_metrics]
            if len(ops_values) > 10:
                # Check for performance degradation
                recent_avg = statistics.mean(ops_values[-10:])
                baseline_avg = statistics.mean(ops_values[:10])
                
                if baseline_avg > 0 and recent_avg > baseline_avg * 2:
                    await self._create_alert(
                        node_id,
                        AlertSeverity.WARNING,
                        f"Performance Degradation Detected - Node {node_id}",
                        f"Operations increased by {((recent_avg / baseline_avg - 1) * 100):.1f}%"
                    )
                    
        except Exception as e:
            logger.error(f"Failed to analyze trends for node {node_id}: {e}")

    async def _cleanup_loop(self) -> None:
        """Cleanup old data loop"""
        while True:
            try:
                current_time = time.time()
                retention_period = self.config.get('metrics_retention', 86400)
                
                # Cleanup old metrics
                for node_id, metrics_deque in self.node_metrics.items():
                    # Convert to list for iteration
                    metrics_list = list(metrics_deque)
                    
                    # Keep only recent metrics
                    recent_metrics = [
                        m for m in metrics_list
                        if current_time - m.timestamp <= retention_period
                    ]
                    
                    # Update deque
                    metrics_deque.clear()
                    metrics_deque.extend(recent_metrics)
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(1800)  # Retry in 30 minutes

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'nodes': {
                node_id: {
                    'metrics': asdict(metrics),
                    'health_score': asdict(self.health_scores.get(node_id, None)) if node_id in self.health_scores else None
                }
                for node_id, metrics in self.current_metrics.items()
            },
            'active_alerts': {
                alert_id: asdict(alert)
                for alert_id, alert in self.active_alerts.items()
            },
            'summary': {
                'total_nodes': len(self.current_metrics),
                'healthy_nodes': len([
                    score for score in self.health_scores.values()
                    if score.overall_score > 80
                ]),
                'active_alerts': len(self.active_alerts),
                'critical_alerts': len([
                    alert for alert in self.active_alerts.values()
                    if alert.severity == AlertSeverity.CRITICAL
                ])
            }
        }

    async def get_node_history(self, node_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics for a node"""
        if node_id not in self.node_metrics:
            return []
        
        cutoff_time = time.time() - (hours * 3600)
        
        return [
            asdict(metrics)
            for metrics in self.node_metrics[node_id]
            if metrics.timestamp >= cutoff_time
        ]

    async def shutdown(self) -> None:
        """Shutdown health monitor"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            logger.info("Node health monitor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage
async def main():
    """Example usage of Node Health Monitor"""
    try:
        # This would normally be initialized with actual cluster client
        print("Node Health Monitor Demo")
        print("Note: This would require actual Redis cluster connection")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())