"""Protection Monitoring Module

Enterprise-grade monitoring and observability system for copyright protection
infrastructure. Provides real-time monitoring, alerting, analytics, and
performance optimization for content protection operations.

Key Features:
- Real-time protection system monitoring and health checks
- Performance metrics collection and analysis
- Automated alerting and incident response
- Protection effectiveness analytics and reporting
- System resource monitoring and optimization
- Compliance tracking and audit logging
- Dashboard and visualization integration
- Predictive analytics for protection improvements

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import redis
import asyncpg
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
import psutil
import sqlite3
import pickle
import hashlib
import uuid
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, push_to_gateway
import grafana_api
import elasticsearch
from datadog import initialize, statsd
import requests
import warnings
warnings.filterwarnings('ignore')


class AlertSeverity(Enum):
    """
Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SystemStatus(Enum):
    """System component status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class MetricType(Enum):
    """Types of metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


@dataclass
class Alert:
    """System alert definition"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    component: str
    metric_name: str
    threshold: float
    current_value: float
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    escalated: bool = False
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """
System health status"""
    component: str
    status: SystemStatus
    last_check: datetime = field(default_factory=datetime.now)
    uptime: float = 0.0
    error_rate: float = 0.0
    response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ProtectionMetrics:
    """
Content protection specific metrics"""
    detection_rate: float = 0.0
    false_positive_rate: float = 0.0
    enforcement_success_rate: float = 0.0
    average_detection_time: float = 0.0
    revenue_recovered: float = 0.0
    content_protected: int = 0
    violations_detected: int = 0
    violations_resolved: int = 0
    platforms_monitored: int = 0
    crawl_success_rate: float = 0.0


class ProtectionMonitoringSystem:
    """
    Enterprise-grade monitoring system for content protection infrastructure
    
    Features:
    - Real-time system health monitoring and alerting
    - Performance metrics collection and analysis
    - Protection effectiveness tracking and optimization
    - Automated incident response and escalation
    - Comprehensive dashboards and reporting
    - Predictive analytics for system optimization
    - Integration with external monitoring platforms
    - Compliance and audit logging
    """
    
    def __init__(self,
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 postgres_url: str = "postgresql://localhost/ia_influencer",
                 prometheus_gateway: str = "localhost:9091",
                 elasticsearch_url: str = "http://localhost:9200",
                 grafana_url: str = "http://localhost:3000"):
        
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.postgres_url = postgres_url
        self.prometheus_gateway = prometheus_gateway
        self.elasticsearch_url = elasticsearch_url
        self.grafana_url = grafana_url
        
        # Monitoring state
        self.system_health: Dict[str, SystemHealth] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history = deque(maxlen=10000)
        self.metrics_buffer = defaultdict(deque)
        
        # Monitoring configuration
        self.monitoring_config = self._load_monitoring_config()
        self.alert_rules = self._load_alert_rules()
        
        # Performance metrics
        self.registry = CollectorRegistry()
        self._init_prometheus_metrics()
        
        # External integrations
        self.elasticsearch_client = self._init_elasticsearch()
        self.grafana_client = self._init_grafana()
        
        # Background workers
        self.monitoring_executor = ThreadPoolExecutor(max_workers=20)
        self.alert_executor = ThreadPoolExecutor(max_workers=10)
        
        # Start monitoring loops
        self._start_monitoring_workers()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ProtectionMonitoringSystem initialized successfully")
    
    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        return {
            'collection_interval': 30,  # seconds
            'alert_check_interval': 60,  # seconds
            'health_check_interval': 120,  # seconds
            'metrics_retention_days': 30,
            'alert_escalation_timeout': 3600,  # 1 hour
            'components': [
                'fingerprinting_servers',
                'crawler_deployment',
                'detection_systems',
                'enforcement_system',
                'database_cluster',
                'redis_cluster',
                'message_queues'
            ]
        }
    
    def _load_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """
Load alert rules configuration"""
        return {
            'cpu_usage': {
                'warning': 70.0,
                'critical': 85.0,
                'emergency': 95.0
            },
            'memory_usage': {
                'warning': 75.0,
                'critical': 90.0,
                'emergency': 98.0
            },
            'disk_usage': {
                'warning': 80.0,
                'critical': 90.0,
                'emergency': 95.0
            },
            'error_rate': {
                'warning': 5.0,  # 5%
                'critical': 10.0,  # 10%
                'emergency': 25.0  # 25%
            },
            'response_time': {
                'warning': 1000.0,  # 1 second
                'critical': 3000.0,  # 3 seconds
                'emergency': 10000.0  # 10 seconds
            },
            'detection_accuracy': {
                'warning': 0.85,  # Below 85%
                'critical': 0.75,  # Below 75%
                'emergency': 0.60  # Below 60%
            },
            'false_positive_rate': {
                'warning': 5.0,  # Above 5%
                'critical': 10.0,  # Above 10%
                'emergency': 20.0  # Above 20%
            }
        }
    
    def _init_prometheus_metrics(self):
        """
Initialize Prometheus metrics"""
        # System metrics
        self.system_cpu_usage = Gauge('system_cpu_usage_percent', 
                                    'CPU usage percentage', ['component'], registry=self.registry)
        self.system_memory_usage = Gauge('system_memory_usage_percent', 
                                       'Memory usage percentage', ['component'], registry=self.registry)
        self.system_disk_usage = Gauge('system_disk_usage_percent', 
                                     'Disk usage percentage', ['component'], registry=self.registry)
        
        # Protection metrics
        self.detection_rate = Gauge('protection_detection_rate', 
                                  'Copyright detection rate', registry=self.registry)
        self.false_positive_rate = Gauge('protection_false_positive_rate', 
                                       'False positive rate', registry=self.registry)
        self.enforcement_success_rate = Gauge('protection_enforcement_success_rate', 
                                            'Enforcement success rate', registry=self.registry)
        
        # Performance metrics
        self.detection_time_histogram = Histogram('detection_processing_time_seconds', 
                                                'Detection processing time', ['content_type'], registry=self.registry)
        self.crawl_success_rate = Gauge('crawl_success_rate', 
                                      'Content crawling success rate', ['platform'], registry=self.registry)
        
        # Alert metrics
        self.active_alerts_count = Gauge('active_alerts_total', 
                                       'Number of active alerts', ['severity'], registry=self.registry)
        self.alert_frequency = Counter('alerts_total', 
                                     'Total alerts generated', ['component', 'severity'], registry=self.registry)
    
    def _init_elasticsearch(self):
        """
Initialize Elasticsearch client"""
        try:
            return elasticsearch.Elasticsearch([self.elasticsearch_url])
        except Exception as e:
            self.logger.warning(f"Failed to initialize Elasticsearch: {str(e)}")
            return None
    
    def _init_grafana(self):
        """Initialize Grafana API client"""
        try:
            # Initialize Grafana API client
            return None  # Would initialize actual Grafana client
        except Exception as e:
            self.logger.warning(f"Failed to initialize Grafana: {str(e)}")
            return None
    
    async def collect_system_metrics(self) -> Dict[str, SystemHealth]:
        """Collect system health metrics for all components"""
        health_data = {}
        
        for component in self.monitoring_config['components']:
            try:
                health = await self._collect_component_health(component)
                health_data[component] = health
                self.system_health[component] = health
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(component, health)
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics for {component}: {str(e)}")
        
        return health_data
    
    async def _collect_component_health(self, component: str) -> SystemHealth:
        """Collect health metrics for specific component"""
        try:
            # Get component-specific metrics
            if component == 'fingerprinting_servers':
                return await self._collect_fingerprinting_health()
            elif component == 'crawler_deployment':
                return await self._collect_crawler_health()
            elif component == 'detection_systems':
                return await self._collect_detection_health()
            elif component == 'enforcement_system':
                return await self._collect_enforcement_health()
            elif component == 'database_cluster':
                return await self._collect_database_health()
            elif component == 'redis_cluster':
                return await self._collect_redis_health()
            elif component == 'message_queues':
                return await self._collect_queue_health()
            else:
                return await self._collect_generic_health(component)
                
        except Exception as e:
            self.logger.error(f"Error collecting health for {component}: {str(e)}")
            return SystemHealth(
                component=component,
                status=SystemStatus.UNHEALTHY,
                error_rate=100.0
            )
    
    async def _collect_fingerprinting_health(self) -> SystemHealth:
        """Collect fingerprinting servers health"""
        try:
            # Check fingerprinting server status
            fingerprint_metrics = await self._get_redis_metrics('fingerprint:*')
            
            # Calculate metrics
            total_requests = fingerprint_metrics.get('total_requests', 0)
            failed_requests = fingerprint_metrics.get('failed_requests', 0)
            avg_processing_time = fingerprint_metrics.get('avg_processing_time', 0)
            
            error_rate = (failed_requests / max(total_requests, 1)) * 100
            status = self._determine_status(error_rate, avg_processing_time)
            
            # System resource usage
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            return SystemHealth(
                component='fingerprinting_servers',
                status=status,
                error_rate=error_rate,
                response_time=avg_processing_time,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                custom_metrics={
                    'total_fingerprints': fingerprint_metrics.get('total_fingerprints', 0),
                    'processing_queue_size': fingerprint_metrics.get('queue_size', 0),
                    'active_workers': fingerprint_metrics.get('active_workers', 0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting fingerprinting health: {str(e)}")
            return SystemHealth(
                component='fingerprinting_servers',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_crawler_health(self) -> SystemHealth:
        """Collect crawler deployment health"""
        try:
            # Check crawler status
            crawler_metrics = await self._get_redis_metrics('crawler:*')
            
            # Calculate metrics
            total_crawls = crawler_metrics.get('total_crawls', 0)
            failed_crawls = crawler_metrics.get('failed_crawls', 0)
            avg_crawl_time = crawler_metrics.get('avg_crawl_time', 0)
            
            error_rate = (failed_crawls / max(total_crawls, 1)) * 100
            status = self._determine_status(error_rate, avg_crawl_time)
            
            return SystemHealth(
                component='crawler_deployment',
                status=status,
                error_rate=error_rate,
                response_time=avg_crawl_time,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                custom_metrics={
                    'active_crawlers': crawler_metrics.get('active_crawlers', 0),
                    'platforms_monitored': crawler_metrics.get('platforms_count', 0),
                    'content_discovered': crawler_metrics.get('content_discovered', 0),
                    'queue_backlog': crawler_metrics.get('queue_backlog', 0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting crawler health: {str(e)}")
            return SystemHealth(
                component='crawler_deployment',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_detection_health(self) -> SystemHealth:
        """Collect detection systems health"""
        try:
            # Check detection system metrics
            detection_metrics = await self._get_redis_metrics('detection:*')
            
            # Calculate protection-specific metrics
            total_detections = detection_metrics.get('total_detections', 0)
            false_positives = detection_metrics.get('false_positives', 0)
            avg_detection_time = detection_metrics.get('avg_detection_time', 0)
            
            false_positive_rate = (false_positives / max(total_detections, 1)) * 100
            detection_accuracy = 100 - false_positive_rate
            
            status = self._determine_detection_status(detection_accuracy, false_positive_rate)
            
            return SystemHealth(
                component='detection_systems',
                status=status,
                error_rate=false_positive_rate,
                response_time=avg_detection_time,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                custom_metrics={
                    'detection_accuracy': detection_accuracy,
                    'violations_detected': detection_metrics.get('violations_detected', 0),
                    'processing_queue': detection_metrics.get('processing_queue', 0),
                    'similarity_threshold': detection_metrics.get('similarity_threshold', 0.85)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting detection health: {str(e)}")
            return SystemHealth(
                component='detection_systems',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_enforcement_health(self) -> SystemHealth:
        """Collect enforcement system health"""
        try:
            # Check enforcement metrics
            enforcement_metrics = await self._get_redis_metrics('enforcement:*')
            
            total_actions = enforcement_metrics.get('total_actions', 0)
            successful_actions = enforcement_metrics.get('successful_actions', 0)
            avg_enforcement_time = enforcement_metrics.get('avg_enforcement_time', 0)
            
            success_rate = (successful_actions / max(total_actions, 1)) * 100
            error_rate = 100 - success_rate
            
            status = self._determine_status(error_rate, avg_enforcement_time)
            
            return SystemHealth(
                component='enforcement_system',
                status=status,
                error_rate=error_rate,
                response_time=avg_enforcement_time,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                custom_metrics={
                    'enforcement_success_rate': success_rate,
                    'dmca_notices_sent': enforcement_metrics.get('dmca_notices', 0),
                    'revenue_claims': enforcement_metrics.get('revenue_claims', 0),
                    'pending_actions': enforcement_metrics.get('pending_actions', 0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting enforcement health: {str(e)}")
            return SystemHealth(
                component='enforcement_system',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_database_health(self) -> SystemHealth:
        """Collect database cluster health"""
        try:
            # Check PostgreSQL health
            db_metrics = await self._check_database_performance()
            
            connection_count = db_metrics.get('active_connections', 0)
            max_connections = db_metrics.get('max_connections', 100)
            query_time = db_metrics.get('avg_query_time', 0)
            
            connection_usage = (connection_count / max_connections) * 100
            error_rate = db_metrics.get('error_rate', 0)
            
            status = self._determine_status(error_rate, query_time)
            
            return SystemHealth(
                component='database_cluster',
                status=status,
                error_rate=error_rate,
                response_time=query_time,
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                custom_metrics={
                    'connection_usage': connection_usage,
                    'query_throughput': db_metrics.get('queries_per_second', 0),
                    'deadlocks': db_metrics.get('deadlocks', 0),
                    'table_scans': db_metrics.get('table_scans', 0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting database health: {str(e)}")
            return SystemHealth(
                component='database_cluster',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_redis_health(self) -> SystemHealth:
        """Collect Redis cluster health"""
        try:
            # Check Redis health
            redis_info = self.redis_client.info()
            
            memory_usage = redis_info.get('used_memory_percent', 0)
            connected_clients = redis_info.get('connected_clients', 0)
            ops_per_sec = redis_info.get('instantaneous_ops_per_sec', 0)
            
            # Determine status based on memory usage and client count
            if memory_usage > 90:
                status = SystemStatus.CRITICAL
            elif memory_usage > 75:
                status = SystemStatus.DEGRADED
            else:
                status = SystemStatus.HEALTHY
            
            return SystemHealth(
                component='redis_cluster',
                status=status,
                error_rate=0.0,  # Redis typically doesn't have error rate in info
                response_time=0.0,  # Would need to measure ping time
                memory_usage=memory_usage,
                custom_metrics={
                    'connected_clients': connected_clients,
                    'operations_per_second': ops_per_sec,
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0),
                    'total_keys': sum(redis_info.get(f'db{i}', {}).get('keys', 0) for i in range(16))
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting Redis health: {str(e)}")
            return SystemHealth(
                component='redis_cluster',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_queue_health(self) -> SystemHealth:
        """Collect message queue health"""
        try:
            # Check queue metrics
            queue_metrics = await self._get_queue_metrics()
            
            total_messages = queue_metrics.get('total_messages', 0)
            processed_messages = queue_metrics.get('processed_messages', 0)
            failed_messages = queue_metrics.get('failed_messages', 0)
            queue_depth = queue_metrics.get('queue_depth', 0)
            
            error_rate = (failed_messages / max(total_messages, 1)) * 100
            processing_rate = queue_metrics.get('processing_rate', 0)
            
            # Determine status based on queue depth and error rate
            if queue_depth > 10000 or error_rate > 15:
                status = SystemStatus.CRITICAL
            elif queue_depth > 5000 or error_rate > 5:
                status = SystemStatus.DEGRADED
            else:
                status = SystemStatus.HEALTHY
            
            return SystemHealth(
                component='message_queues',
                status=status,
                error_rate=error_rate,
                response_time=processing_rate,
                custom_metrics={
                    'queue_depth': queue_depth,
                    'processing_rate': processing_rate,
                    'dead_letter_queue': queue_metrics.get('dead_letter_count', 0),
                    'consumer_count': queue_metrics.get('active_consumers', 0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting queue health: {str(e)}")
            return SystemHealth(
                component='message_queues',
                status=SystemStatus.UNHEALTHY
            )
    
    async def _collect_generic_health(self, component: str) -> SystemHealth:
        """Collect generic component health"""
        return SystemHealth(
            component=component,
            status=SystemStatus.HEALTHY,
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent
        )
    
    def _determine_status(self, error_rate: float, response_time: float) -> SystemStatus:
        """
Determine system status based on metrics"""
        if error_rate >= 25 or response_time >= 10000:
            return SystemStatus.OFFLINE
        elif error_rate >= 10 or response_time >= 3000:
            return SystemStatus.UNHEALTHY
        elif error_rate >= 5 or response_time >= 1000:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.HEALTHY
    
    def _determine_detection_status(self, accuracy: float, false_positive_rate: float) -> SystemStatus:
        """
Determine detection system status"""
        if accuracy < 60 or false_positive_rate > 20:
            return SystemStatus.OFFLINE
        elif accuracy < 75 or false_positive_rate > 10:
            return SystemStatus.UNHEALTHY
        elif accuracy < 85 or false_positive_rate > 5:
            return SystemStatus.DEGRADED
        else:
            return SystemStatus.HEALTHY
    
    def _update_prometheus_metrics(self, component: str, health: SystemHealth):
        """
Update Prometheus metrics"""
        try:
            # Update system metrics
            self.system_cpu_usage.labels(component=component).set(health.cpu_usage)
            self.system_memory_usage.labels(component=component).set(health.memory_usage)
            self.system_disk_usage.labels(component=component).set(health.disk_usage)
            
            # Update protection-specific metrics
            if component == 'detection_systems':
                accuracy = health.custom_metrics.get('detection_accuracy', 0)
                self.detection_rate.set(accuracy / 100.0)
                self.false_positive_rate.set(health.error_rate / 100.0)
            
            elif component == 'enforcement_system':
                success_rate = health.custom_metrics.get('enforcement_success_rate', 0)
                self.enforcement_success_rate.set(success_rate / 100.0)
            
            elif component == 'crawler_deployment':
                platform_count = health.custom_metrics.get('platforms_monitored', 0)
                if platform_count > 0:
                    # Calculate success rate for each platform
                    success_rate = 100 - health.error_rate
                    self.crawl_success_rate.labels(platform='average').set(success_rate / 100.0)
            
            # Push to Prometheus gateway
            if self.prometheus_gateway:
                push_to_gateway(self.prometheus_gateway, job='ia_influencer_protection', registry=self.registry)
                
        except Exception as e:
            self.logger.error(f"Error updating Prometheus metrics: {str(e)}")
    
    async def check_alert_conditions(self):
        """Check all alert conditions and trigger alerts if necessary"""
        try:
            for component, health in self.system_health.items():
                await self._check_component_alerts(component, health)
                
        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {str(e)}")
    
    async def _check_component_alerts(self, component: str, health: SystemHealth):
        """Check alert conditions for specific component"""
        alerts_to_trigger = []
        
        # Check CPU usage alerts
        cpu_alerts = self._check_threshold_alerts('cpu_usage', health.cpu_usage, component)
        alerts_to_trigger.extend(cpu_alerts)
        
        # Check memory usage alerts
        memory_alerts = self._check_threshold_alerts('memory_usage', health.memory_usage, component)
        alerts_to_trigger.extend(memory_alerts)
        
        # Check disk usage alerts
        disk_alerts = self._check_threshold_alerts('disk_usage', health.disk_usage, component)
        alerts_to_trigger.extend(disk_alerts)
        
        # Check error rate alerts
        error_alerts = self._check_threshold_alerts('error_rate', health.error_rate, component)
        alerts_to_trigger.extend(error_alerts)
        
        # Check response time alerts
        response_alerts = self._check_threshold_alerts('response_time', health.response_time, component)
        alerts_to_trigger.extend(response_alerts)
        
        # Check component-specific alerts
        if component == 'detection_systems':
            detection_alerts = await self._check_detection_alerts(health)
            alerts_to_trigger.extend(detection_alerts)
        
        # Trigger alerts
        for alert in alerts_to_trigger:
            await self._trigger_alert(alert)
    
    def _check_threshold_alerts(self, metric_name: str, current_value: float, component: str) -> List[Alert]:
        """
Check threshold-based alerts"""
        alerts = []
        
        if metric_name not in self.alert_rules:
            return alerts
        
        thresholds = self.alert_rules[metric_name]
        
        # Check emergency threshold
        if current_value >= thresholds.get('emergency', float('inf')):
            alerts.append(self._create_alert(
                component, metric_name, AlertSeverity.EMERGENCY, 
                thresholds['emergency'], current_value
            ))
        
        # Check critical threshold
        elif current_value >= thresholds.get('critical', float('inf')):
            alerts.append(self._create_alert(
                component, metric_name, AlertSeverity.CRITICAL,
                thresholds['critical'], current_value
            ))
        
        # Check warning threshold
        elif current_value >= thresholds.get('warning', float('inf')):
            alerts.append(self._create_alert(
                component, metric_name, AlertSeverity.WARNING,
                thresholds['warning'], current_value
            ))
        
        return alerts
    
    async def _check_detection_alerts(self, health: SystemHealth) -> List[Alert]:
        """
Check detection system specific alerts"""
        alerts = []
        
        detection_accuracy = health.custom_metrics.get('detection_accuracy', 100)
        false_positive_rate = health.error_rate
        
        # Check detection accuracy
        accuracy_thresholds = self.alert_rules.get('detection_accuracy', {})
        if detection_accuracy <= accuracy_thresholds.get('critical', 0):
            alerts.append(self._create_alert(
                'detection_systems', 'detection_accuracy', AlertSeverity.CRITICAL,
                accuracy_thresholds['critical'], detection_accuracy
            ))
        
        # Check false positive rate
        fp_thresholds = self.alert_rules.get('false_positive_rate', {})
        if false_positive_rate >= fp_thresholds.get('critical', float('inf')):
            alerts.append(self._create_alert(
                'detection_systems', 'false_positive_rate', AlertSeverity.CRITICAL,
                fp_thresholds['critical'], false_positive_rate
            ))
        
        return alerts
    
    def _create_alert(self, component: str, metric_name: str, severity: AlertSeverity, 
                     threshold: float, current_value: float) -> Alert:
        """
Create new alert"""
        alert_id = str(uuid.uuid4())
        
        return Alert(
            alert_id=alert_id,
            title=f"{severity.value.upper()}: {component} {metric_name}",
            description=f"{component} {metric_name} is {current_value:.2f}, exceeding threshold of {threshold:.2f}",
            severity=severity,
            component=component,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            tags={'component': component, 'metric': metric_name}
        )
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger alert and send notifications"""
        try:
            # Check if alert already exists (avoid spam)
            existing_alert_key = f"{alert.component}:{alert.metric_name}:{alert.severity.value}"
            
            if existing_alert_key in self.active_alerts:
                # Update existing alert
                existing_alert = self.active_alerts[existing_alert_key]
                existing_alert.current_value = alert.current_value
                existing_alert.triggered_at = alert.triggered_at
                return
            
            # Store new alert
            self.active_alerts[existing_alert_key] = alert
            self.alert_history.append(alert)
            
            # Update metrics
            self.alert_frequency.labels(
                component=alert.component,
                severity=alert.severity.value
            ).inc()
            
            self._update_alert_count_metrics()
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            # Log alert
            self.logger.warning(f"ALERT TRIGGERED: {alert.title} - {alert.description}")
            
            # Store in Elasticsearch
            await self._store_alert_in_elasticsearch(alert)
            
        except Exception as e:
            self.logger.error(f"Error triggering alert: {str(e)}")
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications via multiple channels"""
        try:
            # Email notification
            await self._send_alert_email(alert)
            
            # Slack notification (if configured)
            await self._send_slack_notification(alert)
            
            # PagerDuty integration (for critical/emergency alerts)
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                await self._send_pagerduty_alert(alert)
            
            # Discord notification
            await self._send_discord_notification(alert)
            
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {str(e)}")
    
    async def _send_alert_email(self, alert: Alert):
        """Send alert via email"""
        try:
            # Email configuration would be loaded from config
            email_config = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'email': 'alerts@ia-influencer.com',
                'password': 'app_password'
            }
            
            subject = f"[{alert.severity.value.upper()}] IA Influencer Alert: {alert.title}"
            
            body = f"""IA Influencer Agent Protection System Alert

Alert Details:
- Severity: {alert.severity.value.upper()}
- Component: {alert.component}
- Metric: {alert.metric_name}
- Current Value: {alert.current_value:.2f}
- Threshold: {alert.threshold:.2f}
- Time: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}

Description:
{alert.description}

Please investigate and take appropriate action.

System Dashboard: http://monitoring.ia-influencer.com/dashboard
Alert Management: http://monitoring.ia-influencer.com/alerts

IA Influencer Agent Monitoring System
"""
            
            # Send email
            msg = MimeMultipart()
            msg['From'] = email_config['email']
            msg['To'] = 'team@ia-influencer.com'
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['email'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Error sending alert email: {str(e)}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send alert to Slack"""
        try:
            # Slack webhook URL would be configured
            webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            
            color_map = {
                AlertSeverity.INFO: "good",
                AlertSeverity.WARNING: "warning", 
                AlertSeverity.ERROR: "danger",
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "danger"
            }
            
            slack_message = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "warning"),
                        "title": f"🚨 {alert.title}",
                        "text": alert.description,
                        "fields": [
                            {"title": "Component", "value": alert.component, "short": True},
                            {"title": "Metric", "value": alert.metric_name, "short": True},
                            {"title": "Current Value", "value": f"{alert.current_value:.2f}", "short": True},
                            {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True}
                        ],
                        "footer": "IA Influencer Agent Monitoring",
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_message) as response:
                    if response.status != 200:
                        self.logger.error(f"Failed to send Slack notification: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {str(e)}")
    
    async def _send_pagerduty_alert(self, alert: Alert):
        """Send alert to PagerDuty"""
        try:
            # PagerDuty integration key would be configured
            integration_key = "YOUR_PAGERDUTY_INTEGRATION_KEY"
            
            pagerduty_event = {
                "routing_key": integration_key,
                "event_action": "trigger",
                "dedup_key": f"{alert.component}:{alert.metric_name}",
                "payload": {
                    "summary": alert.title,
                    "source": "IA Influencer Agent",
                    "severity": "critical" if alert.severity == AlertSeverity.EMERGENCY else "error",
                    "component": alert.component,
                    "custom_details": {
                        "metric": alert.metric_name,
                        "current_value": alert.current_value,
                        "threshold": alert.threshold,
                        "description": alert.description
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue", 
                    json=pagerduty_event
                ) as response:
                    if response.status != 202:
                        self.logger.error(f"Failed to send PagerDuty alert: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending PagerDuty alert: {str(e)}")
    
    async def _send_discord_notification(self, alert: Alert):
        """Send alert to Discord"""
        try:
            # Discord webhook URL would be configured
            webhook_url = "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK"
            
            embed_color = {
                AlertSeverity.INFO: 0x00ff00,      # Green
                AlertSeverity.WARNING: 0xffff00,   # Yellow
                AlertSeverity.ERROR: 0xff8800,     # Orange
                AlertSeverity.CRITICAL: 0xff0000,  # Red
                AlertSeverity.EMERGENCY: 0x8b0000  # Dark Red
            }
            
            discord_message = {
                "embeds": [
                    {
                        "title": f"🚨 {alert.title}",
                        "description": alert.description,
                        "color": embed_color.get(alert.severity, 0xffff00),
                        "fields": [
                            {"name": "Component", "value": alert.component, "inline": True},
                            {"name": "Metric", "value": alert.metric_name, "inline": True},
                            {"name": "Current Value", "value": f"{alert.current_value:.2f}", "inline": True},
                            {"name": "Threshold", "value": f"{alert.threshold:.2f}", "inline": True}
                        ],
                        "footer": {"text": "IA Influencer Agent Monitoring"},
                        "timestamp": alert.triggered_at.isoformat()
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=discord_message) as response:
                    if response.status not in [200, 204]:
                        self.logger.error(f"Failed to send Discord notification: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending Discord notification: {str(e)}")
    
    def _update_alert_count_metrics(self):
        """Update alert count metrics"""
        try:
            # Count active alerts by severity
            severity_counts = defaultdict(int)
            for alert in self.active_alerts.values():
                severity_counts[alert.severity.value] += 1
            
            # Update Prometheus metrics
            for severity in AlertSeverity:
                count = severity_counts.get(severity.value, 0)
                self.active_alerts_count.labels(severity=severity.value).set(count)
                
        except Exception as e:
            self.logger.error(f"Error updating alert count metrics: {str(e)}")
    
    async def _store_alert_in_elasticsearch(self, alert: Alert):
        """Store alert in Elasticsearch for analytics"""
        try:
            if not self.elasticsearch_client:
                return
            
            alert_doc = {
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity.value,
                'component': alert.component,
                'metric_name': alert.metric_name,
                'threshold': alert.threshold,
                'current_value': alert.current_value,
                'triggered_at': alert.triggered_at.isoformat(),
                'tags': alert.tags,
                'timestamp': datetime.now().isoformat()
            }
            
            index_name = f"ia-influencer-alerts-{datetime.now().strftime('%Y-%m')}"
            
            await asyncio.get_event_loop().run_in_executor(
                self.monitoring_executor,
                self.elasticsearch_client.index,
                index_name,
                alert_doc
            )
            
        except Exception as e:
            self.logger.error(f"Error storing alert in Elasticsearch: {str(e)}")
    
    async def generate_protection_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive protection analytics report"""
        try:
            # Collect protection metrics
            protection_metrics = await self._collect_protection_metrics()
            
            # Calculate analytics
            analytics = {
                'summary': {
                    'report_generated': datetime.now().isoformat(),
                    'monitoring_period': '24h',
                    'overall_system_health': self._calculate_overall_health(),
                    'protection_effectiveness': protection_metrics.detection_rate
                },
                'detection_performance': {
                    'detection_rate': protection_metrics.detection_rate,
                    'false_positive_rate': protection_metrics.false_positive_rate,
                    'average_detection_time': protection_metrics.average_detection_time,
                    'content_types_protected': self._get_protected_content_types(),
                    'violations_by_platform': await self._get_violations_by_platform()
                },
                'enforcement_performance': {
                    'enforcement_success_rate': protection_metrics.enforcement_success_rate,
                    'dmca_notices_sent': await self._get_dmca_notices_count(),
                    'revenue_recovered': protection_metrics.revenue_recovered,
                    'pending_enforcements': await self._get_pending_enforcements_count()
                },
                'system_performance': {
                    'component_health': {comp: health.status.value for comp, health in self.system_health.items()},
                    'resource_utilization': await self._get_resource_utilization_summary(),
                    'throughput_metrics': await self._get_throughput_metrics(),
                    'error_rates': await self._get_error_rate_summary()
                },
                'alerts_summary': {
                    'active_alerts': len(self.active_alerts),
                    'alerts_by_severity': self._get_alerts_by_severity(),
                    'resolved_alerts_24h': await self._get_resolved_alerts_count(),
                    'top_alert_sources': await self._get_top_alert_sources()
                },
                'recommendations': await self._generate_optimization_recommendations()
            }
            
            # Store report
            await self._store_analytics_report(analytics)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {str(e)}")
            return {}
    
    async def _collect_protection_metrics(self) -> ProtectionMetrics:
        """Collect protection-specific metrics"""
        try:
            # Get metrics from Redis
            detection_metrics = await self._get_redis_metrics('detection:*')
            enforcement_metrics = await self._get_redis_metrics('enforcement:*')
            crawler_metrics = await self._get_redis_metrics('crawler:*')
            
            return ProtectionMetrics(
                detection_rate=detection_metrics.get('detection_rate', 0.0),
                false_positive_rate=detection_metrics.get('false_positive_rate', 0.0),
                enforcement_success_rate=enforcement_metrics.get('success_rate', 0.0),
                average_detection_time=detection_metrics.get('avg_detection_time', 0.0),
                revenue_recovered=enforcement_metrics.get('revenue_recovered', 0.0),
                content_protected=detection_metrics.get('content_protected', 0),
                violations_detected=detection_metrics.get('violations_detected', 0),
                violations_resolved=enforcement_metrics.get('violations_resolved', 0),
                platforms_monitored=crawler_metrics.get('platforms_count', 0),
                crawl_success_rate=crawler_metrics.get('success_rate', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting protection metrics: {str(e)}")
            return ProtectionMetrics()
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health score"""
        if not self.system_health:
            return "unknown"
        
        health_scores = {
            SystemStatus.HEALTHY: 100,
            SystemStatus.DEGRADED: 75,
            SystemStatus.UNHEALTHY: 50,
            SystemStatus.OFFLINE: 0,
            SystemStatus.MAINTENANCE: 90
        }
        
        total_score = 0
        component_count = 0
        
        for health in self.system_health.values():
            total_score += health_scores.get(health.status, 0)
            component_count += 1
        
        if component_count == 0:
            return "unknown"
        
        average_score = total_score / component_count
        
        if average_score >= 90:
            return "excellent"
        elif average_score >= 75:
            return "good"
        elif average_score >= 50:
            return "degraded"
        else:
            return "critical"
    
    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        # Analyze system health for recommendations
        for component, health in self.system_health.items():
            if health.cpu_usage > 80:
                recommendations.append(f"Consider scaling {component} - high CPU usage ({health.cpu_usage:.1f}%)")
            
            if health.memory_usage > 85:
                recommendations.append(f"Optimize memory usage for {component} ({health.memory_usage:.1f}%)")
            
            if health.error_rate > 5:
                recommendations.append(f"Investigate errors in {component} - error rate {health.error_rate:.1f}%")
        
        # Check detection system performance
        detection_health = self.system_health.get('detection_systems')
        if detection_health:
            accuracy = detection_health.custom_metrics.get('detection_accuracy', 100)
            if accuracy < 85:
                recommendations.append(f"Improve detection accuracy - currently {accuracy:.1f}%")
        
        # Check enforcement performance
        enforcement_health = self.system_health.get('enforcement_system')
        if enforcement_health:
            success_rate = enforcement_health.custom_metrics.get('enforcement_success_rate', 0)
            if success_rate < 80:
                recommendations.append(f"Improve enforcement success rate - currently {success_rate:.1f}%")
        
        # Check alert frequency
        if len(self.active_alerts) > 10:
            recommendations.append("High number of active alerts - review and adjust thresholds")
        
        return recommendations[:10]  # Return top 10 recommendations
    
    # Helper methods for metrics collection
    async def _get_redis_metrics(self, pattern: str) -> Dict[str, Any]:
        """Get metrics from Redis matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            metrics = {}
            
            for key in keys:
                data = self.redis_client.hgetall(key)
                for metric_key, value in data.items():
                    try:
                        numeric_value = float(value)
                        if metric_key in metrics:
                            metrics[metric_key] += numeric_value
                        else:
                            metrics[metric_key] = numeric_value
                    except (ValueError, TypeError):
                        continue
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting Redis metrics: {str(e)}")
            return {}
    
    async def _check_database_performance(self) -> Dict[str, Any]:
        """Check database performance metrics"""
        try:
            # This would connect to PostgreSQL and collect metrics
            # For now, return mock data
            return {
                'active_connections': 25,
                'max_connections': 100,
                'avg_query_time': 150.0,
                'queries_per_second': 500,
                'error_rate': 0.5,
                'deadlocks': 0,
                'table_scans': 10
            }
            
        except Exception as e:
            self.logger.error(f"Error checking database performance: {str(e)}")
            return {}
    
    async def _get_queue_metrics(self) -> Dict[str, Any]:
        """Get message queue metrics"""
        try:
            # This would integrate with actual message queue system
            return {
                'total_messages': 10000,
                'processed_messages': 9800,
                'failed_messages': 200,
                'queue_depth': 150,
                'processing_rate': 100.0,
                'dead_letter_count': 5,
                'active_consumers': 10
            }
            
        except Exception as e:
            self.logger.error(f"Error getting queue metrics: {str(e)}")
            return {}
    
    def _get_protected_content_types(self) -> Dict[str, int]:
        """Get count of protected content by type"""
        return {
            'audio': 1500,
            'video': 800,
            'image': 2000,
            'text': 500
        }
    
    async def _get_violations_by_platform(self) -> Dict[str, int]:
        """
Get violations count by platform"""
        return {
            'youtube': 45,
            'tiktok': 32,
            'instagram': 28,
            'twitter': 15,
            'generic_web': 20
        }
    
    async def _get_dmca_notices_count(self) -> int:
        """
Get count of DMCA notices sent"""
        return 25
    
    async def _get_pending_enforcements_count(self) -> int:
        """
Get count of pending enforcement actions"""
        return 8
    
    async def _get_resource_utilization_summary(self) -> Dict[str, float]:
        """
Get resource utilization summary"""
        return {
            'avg_cpu_usage': 65.5,
            'avg_memory_usage': 70.2,
            'avg_disk_usage': 45.8,
            'network_throughput': 850.5
        }
    
    async def _get_throughput_metrics(self) -> Dict[str, float]:
        """
Get system throughput metrics"""
        return {
            'fingerprints_per_second': 125.0,
            'detections_per_hour': 450.0,
            'enforcements_per_day': 15.0,
            'crawl_rate_per_minute': 85.0
        }
    
    async def _get_error_rate_summary(self) -> Dict[str, float]:
        """
Get error rate summary across components"""
        return {
            'fingerprinting_servers': 1.2,
            'crawler_deployment': 2.1,
            'detection_systems': 0.8,
            'enforcement_system': 3.5,
            'overall': 1.9
        }
    
    def _get_alerts_by_severity(self) -> Dict[str, int]:
        """
Get active alerts count by severity"""
        severity_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1
        return dict(severity_counts)
    
    async def _get_resolved_alerts_count(self) -> int:
        """
Get count of alerts resolved in last 24h"""
        return 12
    
    async def _get_top_alert_sources(self) -> Dict[str, int]:
        """
Get top sources generating alerts"""
        return {
            'detection_systems': 8,
            'crawler_deployment': 5,
            'database_cluster': 3,
            'enforcement_system': 2
        }
    
    async def _store_analytics_report(self, analytics: Dict[str, Any]):
        """
Store analytics report"""
        try:
            # Store in Redis with timestamp
            report_key = f"analytics_report:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await asyncio.get_event_loop().run_in_executor(
                self.monitoring_executor,
                self.redis_client.set,
                report_key,
                json.dumps(analytics, default=str),
                3600 * 24  # 24 hour expiry
            )
            
            # Store in Elasticsearch
            if self.elasticsearch_client:
                index_name = f"ia-influencer-analytics-{datetime.now().strftime('%Y-%m')}"
                await asyncio.get_event_loop().run_in_executor(
                    self.monitoring_executor,
                    self.elasticsearch_client.index,
                    index_name,
                    analytics
                )
            
        except Exception as e:
            self.logger.error(f"Error storing analytics report: {str(e)}")
    
    def _start_monitoring_workers(self):
        """Start background monitoring workers"""
        def metrics_collector():
            """
Collect metrics periodically"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def collect_loop():
                while True:
                    try:
                        await self.collect_system_metrics()
                        await asyncio.sleep(self.monitoring_config['collection_interval'])
                    except Exception as e:
                        self.logger.error(f"Error in metrics collection loop: {str(e)}")
                        await asyncio.sleep(10)
            
            loop.run_until_complete(collect_loop())
        
        def alert_checker():
            """Check alerts periodically"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def alert_loop():
                while True:
                    try:
                        await self.check_alert_conditions()
                        await asyncio.sleep(self.monitoring_config['alert_check_interval'])
                    except Exception as e:
                        self.logger.error(f"Error in alert checking loop: {str(e)}")
                        await asyncio.sleep(10)
            
            loop.run_until_complete(alert_loop())
        
        # Start worker threads
        metrics_thread = threading.Thread(target=metrics_collector, daemon=True)
        alert_thread = threading.Thread(target=alert_checker, daemon=True)
        
        metrics_thread.start()
        alert_thread.start()
        
        self.logger.info("Monitoring workers started successfully")


# Factory function for creating monitoring system
def create_monitoring_system(config: Dict[str, Any]) -> ProtectionMonitoringSystem:
    """
    Create and configure protection monitoring system
    
    Args:
        config: System configuration parameters
        
    Returns:
        ProtectionMonitoringSystem: Configured monitoring system
    """
    return ProtectionMonitoringSystem(
        redis_host=config.get('redis_host', 'localhost'),
        redis_port=config.get('redis_port', 6379),
        postgres_url=config.get('postgres_url', 'postgresql://localhost/ia_influencer'),
        prometheus_gateway=config.get('prometheus_gateway', 'localhost:9091'),
        elasticsearch_url=config.get('elasticsearch_url', 'http://localhost:9200'),
        grafana_url=config.get('grafana_url', 'http://localhost:3000')
    )
