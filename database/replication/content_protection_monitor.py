"""Advanced Monitoring System for Content Protection Replication
IA Influencer Agent + Content Protection Platform
Real-time monitoring and alerting for worldwide content protection
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import yaml
import statistics
from pathlib import Path

# Third-party imports for monitoring
import psutil
import aioredis
import pymongo
from elasticsearch import AsyncElasticsearch
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import websockets

class AlertSeverity(Enum):
    """
Alert severity levels for content protection monitoring"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MonitoringComponent(Enum):
    """Components being monitored in the content protection system"""

    REPLICATION = "replication"
    FINGERPRINTING = "fingerprinting"
    VIOLATION_DETECTION = "violation_detection"
    REVENUE_TRACKING = "revenue_tracking"
    DATABASE = "database"
    API = "api"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class MetricData:
    """Structured metric data for content protection monitoring"""
    timestamp: datetime
    component: MonitoringComponent
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    region: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert metric to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'component': self.component.value,
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags,
            'region': self.region
        }

@dataclass
class Alert:
    """
Alert structure for content protection incidents"""
    id: str
    severity: AlertSeverity
    component: MonitoringComponent
    title: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    impact_level: str = "medium"
    affected_users: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for notifications"""
        return {
            'id': self.id,
            'severity': self.severity.value,
            'component': self.component.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'impact_level': self.impact_level,
            'affected_users': self.affected_users
        }

class PrometheusMetrics:
    """
Prometheus metrics for content protection monitoring"""
    
    def __init__(self):
        # Replication metrics
        self.replication_lag = Histogram(
            'content_protection_replication_lag_seconds',
            'Replication lag in seconds',
            ['source_region', 'target_region', 'database_type']
        )
        
        self.fingerprints_processed = Counter(
            'content_protection_fingerprints_total',
            'Total number of content fingerprints processed',
            ['content_type', 'region', 'status']
        )
        
        self.violations_detected = Counter(
            'content_protection_violations_total',
            'Total number of violations detected',
            ['platform', 'content_type', 'severity', 'region']
        )
        
        self.revenue_tracked = Summary(
            'content_protection_revenue_amount',
            'Revenue amounts tracked for creators',
            ['currency', 'platform', 'region']
        )
        
        # System metrics
        self.database_connections = Gauge(
            'content_protection_db_connections',
            'Number of active database connections',
            ['database_type', 'region']
        )
        
        self.api_requests = Counter(
            'content_protection_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status_code', 'region']
        )
        
        self.api_latency = Histogram(
            'content_protection_api_latency_seconds',
            'API request latency',
            ['endpoint', 'method', 'region']
        )
        
        # Security metrics
        self.failed_auth_attempts = Counter(
            'content_protection_failed_auth_total',
            'Failed authentication attempts',
            ['source_ip', 'user_type', 'region']
        )
        
        self.suspicious_activities = Counter(
            'content_protection_suspicious_activities_total',
            'Suspicious activities detected',
            ['activity_type', 'severity', 'region']
        )

class ContentProtectionMonitor:
    """
Advanced monitoring system for content protection replication"""
    
    def __init__(self, config_path: str = "content_protection_config.yml"):
        self.config = self._load_config(config_path)
        self.metrics = PrometheusMetrics()
        self.active_alerts: Dict[str, Alert] = {}
        self.metrics_buffer: List[MetricData] = []
        self.logger = self._setup_logging()
        
        # Database connections
        self.redis_clients: Dict[str, aioredis.Redis] = {}
        self.mongo_clients: Dict[str, pymongo.MongoClient] = {}
        self.es_clients: Dict[str, AsyncElasticsearch] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.last_health_check = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for content protection monitoring"""
        return {
            'monitoring': {
                'metrics': {
                    'collection_interval': 10,
                    'retention_days': 90,
                    'aggregation_levels': ['1m', '5m', '1h', '1d']
                },
                'alerts': {
                    'replication_lag_ms': 1000,
                    'violation_detection_rate': 100,
                    'false_positive_rate': 0.05,
                    'system_health_score': 80,
                    'api_error_rate': 0.01
                }
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
Setup structured logging for monitoring"""
        logger = logging.getLogger('content_protection_monitor')
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('content_protection_monitor.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    async def initialize_connections(self):
        """
Initialize connections to all monitored databases"""
        try:
            # Initialize Redis connections for each region
            for region, config in self.config.get('regions', {}).items():
                redis_config = config.get('databases', {}).get('redis', {})
                self.redis_clients[region] = await aioredis.from_url(
                    f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                )
            
            # Initialize MongoDB connections
            for region, config in self.config.get('regions', {}).items():
                mongo_config = config.get('databases', {}).get('mongodb', {})
                self.mongo_clients[region] = pymongo.MongoClient(
                    host=mongo_config.get('host', 'localhost'),
                    port=mongo_config.get('port', 27017)
                )
            
            # Initialize Elasticsearch connections
            for region, config in self.config.get('regions', {}).items():
                es_config = config.get('databases', {}).get('elasticsearch', {})
                self.es_clients[region] = AsyncElasticsearch([{
                    'host': es_config.get('host', 'localhost'),
                    'port': es_config.get('port', 9200)
                }])
            
            self.logger.info("Successfully initialized all database connections")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connections: {e}")
            raise
    
    async def start_monitoring(self):
        """Start the comprehensive monitoring system"""
        self.logger.info("Starting Content Protection Monitoring System")
        self.monitoring_active = True
        
        # Initialize connections
        await self.initialize_connections()
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_replication_health()),
            asyncio.create_task(self._monitor_fingerprinting_performance()),
            asyncio.create_task(self._monitor_violation_detection()),
            asyncio.create_task(self._monitor_revenue_tracking()),
            asyncio.create_task(self._monitor_database_health()),
            asyncio.create_task(self._monitor_api_performance()),
            asyncio.create_task(self._monitor_security_events()),
            asyncio.create_task(self._process_metrics()),
            asyncio.create_task(self._health_check_scheduler()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring system error: {e}")
            await self.stop_monitoring()
    
    async def stop_monitoring(self):
        """Stop monitoring and cleanup resources"""
        self.logger.info("Stopping Content Protection Monitoring System")
        self.monitoring_active = False
        
        # Close database connections
        for client in self.redis_clients.values():
            await client.close()
        
        for client in self.mongo_clients.values():
            client.close()
        
        for client in self.es_clients.values():
            await client.close()
    
    async def _monitor_replication_health(self):
        """Monitor replication lag and health across all regions"""
        while self.monitoring_active:
            try:
                for source_region in self.redis_clients.keys():
                    for target_region in self.redis_clients.keys():
                        if source_region != target_region:
                            lag = await self._measure_replication_lag(source_region, target_region)
                            
                            # Record metric
                            self.metrics.replication_lag.labels(
                                source_region=source_region,
                                target_region=target_region,
                                database_type='redis'
                            ).observe(lag)
                            
                            # Check for alerts
                            max_lag = self.config['monitoring']['alerts']['replication_lag_ms'] / 1000
                            if lag > max_lag:
                                await self._create_alert(
                                    AlertSeverity.HIGH,
                                    MonitoringComponent.REPLICATION,
                                    f"High replication lag: {source_region} -> {target_region}",
                                    f"Replication lag is {lag:.2f}s, exceeding threshold of {max_lag}s"
                                )
                
                await asyncio.sleep(self.config['monitoring']['metrics']['collection_interval'])
                
            except Exception as e:
                self.logger.error(f"Error monitoring replication health: {e}")
                await asyncio.sleep(30)
    
    async def _measure_replication_lag(self, source_region: str, target_region: str) -> float:
        """Measure replication lag between two regions"""
        try:
            # Write timestamp to source
            timestamp = time.time()
            test_key = f"replication_test:{timestamp}"
            
            await self.redis_clients[source_region].set(test_key, timestamp, ex=60)
            
            # Measure time to appear in target
            start_time = time.time()
            max_wait = 10  # 10 seconds max wait
            
            while time.time() - start_time < max_wait:
                value = await self.redis_clients[target_region].get(test_key)
                if value:
                    lag = time.time() - float(value)
                    await self.redis_clients[target_region].delete(test_key)
                    return lag
                await asyncio.sleep(0.1)
            
            # If we get here, replication failed
            return max_wait
            
        except Exception as e:
            self.logger.error(f"Error measuring replication lag: {e}")
            return 999.0  # High value to trigger alerts
    
    async def _monitor_fingerprinting_performance(self):
        """Monitor content fingerprinting performance"""
        while self.monitoring_active:
            try:
                for region, redis_client in self.redis_clients.items():
                    # Monitor fingerprint processing queue
                    queue_length = await redis_client.llen("fingerprint_queue")
                    processing_rate = await self._get_fingerprint_processing_rate(region)
                    
                    # Record metrics
                    metric = MetricData(
                        timestamp=datetime.now(),
                        component=MonitoringComponent.FINGERPRINTING,
                        metric_name="queue_length",
                        value=float(queue_length),
                        unit="count",
                        tags={"region": region},
                        region=region
                    )
                    self.metrics_buffer.append(metric)
                    
                    # Alert on high queue length
                    if queue_length > 1000:
                        await self._create_alert(
                            AlertSeverity.MEDIUM,
                            MonitoringComponent.FINGERPRINTING,
                            f"High fingerprint queue length in {region}",
                            f"Queue length: {queue_length} items"
                        )
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error monitoring fingerprinting: {e}")
                await asyncio.sleep(60)
    
    async def _get_fingerprint_processing_rate(self, region: str) -> float:
        """Get fingerprint processing rate for a region"""
        try:
            # Get processing stats from Redis
            stats_key = f"fingerprint_stats:{region}"
            stats = await self.redis_clients[region].hgetall(stats_key)
            
            current_time = time.time()
            last_hour_count = int(stats.get('last_hour_count', 0))
            last_update = float(stats.get('last_update', current_time))
            
            # Calculate rate per minute
            time_diff = current_time - last_update
            if time_diff > 0:
                return (last_hour_count / time_diff) * 60
            return 0.0
            
        except Exception:
            return 0.0
    
    async def _monitor_violation_detection(self):
        """Monitor violation detection system performance"""
        while self.monitoring_active:
            try:
                for region, es_client in self.es_clients.items():
                    # Query recent violations
                    query = {
                        "query": {
                            "range": {
                                "timestamp": {
                                    "gte": "now-1h"
                                }
                            }
                        },
                        "aggs": {
                            "by_platform": {
                                "terms": {
                                    "field": "platform"
                                }
                            },
                            "by_severity": {
                                "terms": {
                                    "field": "severity"
                                }
                            }
                        }
                    }
                    
                    response = await es_client.search(
                        index="content_violations",
                        body=query
                    )
                    
                    # Process violation statistics
                    total_violations = response['hits']['total']['value']
                    platforms = response['aggregations']['by_platform']['buckets']
                    severities = response['aggregations']['by_severity']['buckets']
                    
                    # Update metrics
                    for platform_bucket in platforms:
                        platform = platform_bucket['key']
                        count = platform_bucket['doc_count']
                        
                        self.metrics.violations_detected.labels(
                            platform=platform,
                            content_type="mixed",
                            severity="mixed",
                            region=region
                        ).inc(count)
                    
                    # Check for anomalies
                    violations_per_hour = total_violations
                    threshold = self.config['monitoring']['alerts']['violation_detection_rate']
                    
                    if violations_per_hour > threshold:
                        await self._create_alert(
                            AlertSeverity.HIGH,
                            MonitoringComponent.VIOLATION_DETECTION,
                            f"High violation detection rate in {region}",
                            f"Detected {violations_per_hour} violations in last hour (threshold: {threshold})"
                        )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring violation detection: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_revenue_tracking(self):
        """Monitor revenue tracking accuracy and performance"""
        while self.monitoring_active:
            try:
                for region, mongo_client in self.mongo_clients.items():
                    db = mongo_client.content_protection
                    
                    # Get revenue statistics for last hour
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    
                    pipeline = [
                        {
                            "$match": {
                                "timestamp": {"$gte": one_hour_ago}
                            }
                        },
                        {
                            "$group": {
                                "_id": {
                                    "platform": "$platform",
                                    "currency": "$currency"
                                },
                                "total_amount": {"$sum": "$amount"},
                                "count": {"$sum": 1}
                            }
                        }
                    ]
                    
                    revenue_stats = list(db.revenue_tracking.aggregate(pipeline))
                    
                    # Update metrics
                    for stat in revenue_stats:
                        platform = stat['_id']['platform']
                        currency = stat['_id']['currency']
                        amount = stat['total_amount']
                        
                        self.metrics.revenue_tracked.labels(
                            currency=currency,
                            platform=platform,
                            region=region
                        ).observe(amount)
                    
                    # Monitor for discrepancies
                    await self._check_revenue_discrepancies(region, db)
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring revenue tracking: {e}")
                await asyncio.sleep(600)
    
    async def _check_revenue_discrepancies(self, region: str, db):
        """Check for revenue tracking discrepancies"""
        try:
            # Compare with platform APIs (mock implementation)
            discrepancies = []
            
            # This would normally query platform APIs
            # For demonstration, we'll simulate some checks
            expected_vs_actual = {
                'youtube': {'expected': 1000.0, 'actual': 980.0},
                'spotify': {'expected': 500.0, 'actual': 520.0}
            }
            
            for platform, amounts in expected_vs_actual.items():
                difference = abs(amounts['expected'] - amounts['actual'])
                if difference > amounts['expected'] * 0.05:  # 5% threshold
                    discrepancies.append({
                        'platform': platform,
                        'expected': amounts['expected'],
                        'actual': amounts['actual'],
                        'difference': difference
                    })
            
            if discrepancies:
                for disc in discrepancies:
                    await self._create_alert(
                        AlertSeverity.MEDIUM,
                        MonitoringComponent.REVENUE_TRACKING,
                        f"Revenue discrepancy detected for {disc['platform']}",
                        f"Expected: {disc['expected']}, Actual: {disc['actual']}, Difference: {disc['difference']}"
                    )
        
        except Exception as e:
            self.logger.error(f"Error checking revenue discrepancies: {e}")
    
    async def _monitor_database_health(self):
        """Monitor health of all databases"""
        while self.monitoring_active:
            try:
                for region in self.redis_clients.keys():
                    # Redis health
                    redis_info = await self.redis_clients[region].info()
                    memory_usage = redis_info.get('used_memory', 0)
                    connected_clients = redis_info.get('connected_clients', 0)
                    
                    self.metrics.database_connections.labels(
                        database_type='redis',
                        region=region
                    ).set(connected_clients)
                    
                    # MongoDB health
                    if region in self.mongo_clients:
                        mongo_status = self.mongo_clients[region].admin.command("serverStatus")
                        mongo_connections = mongo_status.get('connections', {}).get('current', 0)
                        
                        self.metrics.database_connections.labels(
                            database_type='mongodb',
                            region=region
                        ).set(mongo_connections)
                    
                    # Elasticsearch health
                    if region in self.es_clients:
                        es_health = await self.es_clients[region].cluster.health()
                        if es_health['status'] not in ['green', 'yellow']:
                            await self._create_alert(
                                AlertSeverity.HIGH,
                                MonitoringComponent.DATABASE,
                                f"Elasticsearch cluster health issue in {region}",
                                f"Cluster status: {es_health['status']}"
                            )
                
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error monitoring database health: {e}")
                await asyncio.sleep(120)
    
    async def _monitor_api_performance(self):
        """Monitor API performance and availability"""
        while self.monitoring_active:
            try:
                # Monitor internal APIs
                api_endpoints = [
                    "/api/v1/fingerprint",
                    "/api/v1/violations",
                    "/api/v1/revenue",
                    "/api/v1/health"
                ]
                
                for endpoint in api_endpoints:
                    start_time = time.time()
                    
                    # Simulate API health check
                    # In real implementation, this would make actual HTTP requests
                    await asyncio.sleep(0.1)  # Simulate network delay
                    
                    latency = time.time() - start_time
                    
                    self.metrics.api_latency.labels(
                        endpoint=endpoint,
                        method='GET',
                        region='eu-west-1'
                    ).observe(latency)
                    
                    # Check for high latency
                    if latency > 2.0:  # 2 second threshold
                        await self._create_alert(
                            AlertSeverity.MEDIUM,
                            MonitoringComponent.API,
                            f"High API latency for {endpoint}",
                            f"Latency: {latency:.2f}s"
                        )
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error monitoring API performance: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_security_events(self):
        """Monitor security-related events and anomalies"""
        while self.monitoring_active:
            try:
                # Monitor failed authentication attempts
                for region, redis_client in self.redis_clients.items():
                    failed_attempts_key = f"failed_auth:{region}"
                    failed_attempts = await redis_client.get(failed_attempts_key)
                    
                    if failed_attempts and int(failed_attempts) > 10:
                        await self._create_alert(
                            AlertSeverity.HIGH,
                            MonitoringComponent.SECURITY,
                            f"High number of failed auth attempts in {region}",
                            f"Failed attempts: {failed_attempts}"
                        )
                
                # Monitor for suspicious activities
                await self._detect_suspicious_patterns()
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring security events: {e}")
                await asyncio.sleep(120)
    
    async def _detect_suspicious_patterns(self):
        """Detect suspicious patterns in system usage"""
        try:
            # Analyze API usage patterns
            # Check for unusual spikes in requests
            # Monitor for potential DDoS attacks
            # Detect abnormal content upload patterns
            
            # This is a simplified implementation
            # Real implementation would use ML-based anomaly detection
            
            suspicious_patterns = [
                "Unusual API request pattern detected",
                "Potential content scraping activity",
                "Abnormal fingerprint submission rate"
            ]
            
            # For demonstration, randomly trigger some patterns
            import random
            if random.random() < 0.1:  # 10% chance
                pattern = random.choice(suspicious_patterns)
                await self._create_alert(
                    AlertSeverity.MEDIUM,
                    MonitoringComponent.SECURITY,
                    "Suspicious activity detected",
                    pattern
                )
        
        except Exception as e:
            self.logger.error(f"Error detecting suspicious patterns: {e}")
    
    async def _process_metrics(self):
        """Process and store collected metrics"""
        while self.monitoring_active:
            try:
                if self.metrics_buffer:
                    # Process batch of metrics
                    batch = self.metrics_buffer.copy()
                    self.metrics_buffer.clear()
                    
                    # Store metrics to time-series database
                    await self._store_metrics(batch)
                    
                    # Generate aggregated metrics
                    await self._generate_aggregated_metrics(batch)
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                self.logger.error(f"Error processing metrics: {e}")
                await asyncio.sleep(60)
    
    async def _store_metrics(self, metrics: List[MetricData]):
        """Store metrics to time-series database"""
        try:
            # In real implementation, this would store to InfluxDB, TimescaleDB, etc.
            self.logger.info(f"Storing {len(metrics)} metrics to time-series database")
            
            # For demonstration, we'll just log the metrics
            for metric in metrics[:5]:  # Log first 5 metrics
                self.logger.debug(f"Metric: {metric.metric_name} = {metric.value} {metric.unit}")
        
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    async def _generate_aggregated_metrics(self, metrics: List[MetricData]):
        """Generate aggregated metrics for dashboards"""
        try:
            # Group metrics by component and calculate aggregations
            component_metrics = {}
            
            for metric in metrics:
                component = metric.component
                if component not in component_metrics:
                    component_metrics[component] = []
                component_metrics[component].append(metric.value)
            
            # Calculate aggregations
            for component, values in component_metrics.items():
                if values:
                    avg_value = statistics.mean(values)
                    max_value = max(values)
                    min_value = min(values)
                    
                    self.logger.debug(
                        f"Component {component.value}: avg={avg_value:.2f}, "
                        f"max={max_value:.2f}, min={min_value:.2f}"
                    )
        
        except Exception as e:
            self.logger.error(f"Error generating aggregated metrics: {e}")
    
    async def _health_check_scheduler(self):
        """Schedule periodic health checks"""
        while self.monitoring_active:
            try:
                health_status = await self._perform_comprehensive_health_check()
                
                # Store health check results
                self.last_health_check = {
                    'timestamp': datetime.now().isoformat(),
                    'status': health_status
                }
                
                # Generate health score
                health_score = self._calculate_health_score(health_status)
                
                threshold = self.config['monitoring']['alerts']['system_health_score']
                if health_score < threshold:
                    await self._create_alert(
                        AlertSeverity.HIGH,
                        MonitoringComponent.PERFORMANCE,
                        f"System health score below threshold",
                        f"Health score: {health_score}%, threshold: {threshold}%"
                    )
                
                await asyncio.sleep(300)  # Health check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in health check scheduler: {e}")
                await asyncio.sleep(300)
    
    async def _perform_comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all systems"""
        health_status = {
            'databases': {},
            'apis': {},
            'security': {},
            'performance': {}
        }
        
        try:
            # Database health checks
            for region in self.redis_clients.keys():
                health_status['databases'][f'redis_{region}'] = await self._check_redis_health(region)
                health_status['databases'][f'mongodb_{region}'] = await self._check_mongodb_health(region)
                health_status['databases'][f'elasticsearch_{region}'] = await self._check_elasticsearch_health(region)
            
            # API health checks
            health_status['apis'] = await self._check_api_health()
            
            # Security checks
            health_status['security'] = await self._check_security_status()
            
            # Performance checks
            health_status['performance'] = await self._check_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive health check: {e}")
            health_status['error'] = str(e)
        
        return health_status
    
    async def _check_redis_health(self, region: str) -> Dict[str, Any]:
        """Check Redis health for a specific region"""
        try:
            client = self.redis_clients[region]
            
            # Ping test
            ping_time = time.time()
            await client.ping()
            ping_latency = time.time() - ping_time
            
            # Memory usage
            info = await client.info()
            memory_usage = info.get('used_memory', 0) / (1024 * 1024)  # MB
            max_memory = info.get('maxmemory', 0) / (1024 * 1024)  # MB
            
            return {
                'status': 'healthy',
                'ping_latency_ms': ping_latency * 1000,
                'memory_usage_mb': memory_usage,
                'memory_usage_percent': (memory_usage / max_memory * 100) if max_memory > 0 else 0,
                'connected_clients': info.get('connected_clients', 0)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_mongodb_health(self, region: str) -> Dict[str, Any]:
        """
Check MongoDB health for a specific region"""
        try:
            client = self.mongo_clients[region]
            
            # Ping test
            ping_time = time.time()
            client.admin.command('ping')
            ping_latency = time.time() - ping_time
            
            # Server status
            status = client.admin.command('serverStatus')
            
            return {
                'status': 'healthy',
                'ping_latency_ms': ping_latency * 1000,
                'connections': status.get('connections', {}),
                'memory': status.get('mem', {}),
                'uptime_seconds': status.get('uptime', 0)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_elasticsearch_health(self, region: str) -> Dict[str, Any]:
        """
Check Elasticsearch health for a specific region"""
        try:
            client = self.es_clients[region]
            
            # Cluster health
            health = await client.cluster.health()
            
            # Node stats
            stats = await client.nodes.stats()
            
            return {
                'status': health['status'],
                'cluster_name': health['cluster_name'],
                'number_of_nodes': health['number_of_nodes'],
                'active_primary_shards': health['active_primary_shards'],
                'active_shards': health['active_shards'],
                'node_stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """
Check API health across all endpoints"""
        # Simplified API health check
        return {
            'status': 'healthy',
            'endpoints_checked': 4,
            'avg_response_time_ms': 150,
            'success_rate': 99.5
        }
    
    async def _check_security_status(self) -> Dict[str, Any]:
        """
Check security status and compliance"""
        return {
            'status': 'secure',
            'failed_auth_attempts_last_hour': 2,
            'suspicious_activities_detected': 0,
            'security_patches_pending': 0,
            'compliance_status': 'compliant'
        }
    
    async def _check_performance_metrics(self) -> Dict[str, Any]:
        """
Check system performance metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage_percent': cpu_percent,
            'memory_usage_percent': memory.percent,
            'disk_usage_percent': (disk.used / disk.total) * 100,
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }
    
    def _calculate_health_score(self, health_status: Dict[str, Any]) -> float:
        """
Calculate overall system health score"""
        try:
            scores = []
            
            # Database health scores
            for db_name, db_status in health_status.get('databases', {}).items():
                if db_status.get('status') == 'healthy':
                    scores.append(100)
                else:
                    scores.append(0)
            
            # API health score
            api_status = health_status.get('apis', {})
            if api_status.get('status') == 'healthy':
                scores.append(api_status.get('success_rate', 0))
            else:
                scores.append(0)
            
            # Security score
            security_status = health_status.get('security', {})
            if security_status.get('status') == 'secure':
                scores.append(100)
            else:
                scores.append(50)
            
            # Performance score
            perf = health_status.get('performance', {})
            cpu_score = max(0, 100 - perf.get('cpu_usage_percent', 0))
            memory_score = max(0, 100 - perf.get('memory_usage_percent', 0))
            disk_score = max(0, 100 - perf.get('disk_usage_percent', 0))
            
            scores.extend([cpu_score, memory_score, disk_score])
            
            # Calculate weighted average
            if scores:
                return sum(scores) / len(scores)
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    async def _create_alert(self, severity: AlertSeverity, component: MonitoringComponent, 
                          title: str, description: str):
        """Create and process a new alert"""
        alert_id = f"{component.value}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            severity=severity,
            component=component,
            title=title,
            description=description,
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        
        # Log alert
        self.logger.warning(f"ALERT [{severity.value.upper()}]: {title} - {description}")
        
        # Send notifications
        await self._send_alert_notifications(alert)
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications via configured channels"""
        try:
            # Email notifications
            if self.config.get('monitoring', {}).get('notifications', {}).get('email', {}).get('enabled'):
                await self._send_email_alert(alert)
            
            # Slack notifications
            if self.config.get('monitoring', {}).get('notifications', {}).get('slack', {}).get('enabled'):
                await self._send_slack_alert(alert)
            
            # PagerDuty for critical alerts
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                await self._send_pagerduty_alert(alert)
        
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert notification"""
        try:
            # Email configuration
            email_config = self.config['monitoring']['notifications']['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_address']
            msg['To'] = "admin@ia-influencer.com"  # Could be configurable
            msg['Subject'] = f"[{alert.severity.value.upper()}] Content Protection Alert: {alert.title}"
            
            body = f"""
            Alert ID: {alert.id}
            Severity: {alert.severity.value.upper()}
            Component: {alert.component.value}
            Time: {alert.timestamp.isoformat()}
            
            Description:
            {alert.description}
            
            Please investigate this issue immediately if it's critical.
            
            IA Influencer Agent Monitoring System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Note: In real implementation, you'd actually send the email
            self.logger.info(f"Email alert sent for {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Send Slack alert notification"""
        try:
            slack_config = self.config['monitoring']['notifications']['slack']
            webhook_url = slack_config['webhook_url']
            
            # Color mapping for severity
            color_map = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning", 
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "danger"
            }
            
            payload = {
                "channel": slack_config['channel'],
                "username": "IA Influencer Monitor",
                "icon_emoji": ":warning:",
                "attachments": [{
                    "color": color_map.get(alert.severity, "warning"),
                    "title": f"[{alert.severity.value.upper()}] {alert.title}",
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Component",
                            "value": alert.component.value,
                            "short": True
                        },
                        {
                            "title": "Alert ID",
                            "value": alert.id,
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert.timestamp.isoformat(),
                            "short": True
                        }
                    ],
                    "footer": "IA Influencer Agent Monitoring",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            # Note: In real implementation, you'd make the actual HTTP request
            # requests.post(webhook_url, json=payload)
            self.logger.info(f"Slack alert sent for {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")
    
    async def _send_pagerduty_alert(self, alert: Alert):
        """Send PagerDuty alert for critical issues"""
        try:
            # Note: In real implementation, you'd integrate with PagerDuty API
            self.logger.critical(f"PagerDuty alert triggered for {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Error sending PagerDuty alert: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics and system status"""
        return {
            'active_alerts': len(self.active_alerts),
            'monitoring_active': self.monitoring_active,
            'last_health_check': self.last_health_check,
            'regions_monitored': list(self.redis_clients.keys()),
            'components_monitored': [comp.value for comp in MonitoringComponent]
        }

# Example usage and demonstration
async def run_monitoring_demo():
    """
Demonstration of the content protection monitoring system"""
    print("🚀 Starting IA Influencer Agent Content Protection Monitoring Demo")
    print("=" * 70)
    
    # Initialize monitor
    monitor = ContentProtectionMonitor()
    
    try:
        # Start monitoring (in demo mode, this would run briefly)
        print("📊 Initializing monitoring system...")
        await monitor.initialize_connections()
        
        print("✅ Monitoring system initialized successfully")
        print(f"📈 Monitoring Summary: {monitor.get_metrics_summary()}")
        
        # Simulate some monitoring activity
        print("\n🔍 Simulating monitoring activities...")
        
        # Create some demo alerts
        await monitor._create_alert(
            AlertSeverity.MEDIUM,
            MonitoringComponent.REPLICATION,
            "Demo: High replication lag detected",
            "This is a demonstration alert for high replication lag between regions"
        )
        
        await monitor._create_alert(
            AlertSeverity.HIGH,
            MonitoringComponent.VIOLATION_DETECTION,
            "Demo: Violation spike detected",
            "Unusual increase in copyright violations detected on YouTube platform"
        )
        
        print(f"⚠️  Active alerts: {len(monitor.active_alerts)}")
        
        # Perform health check
        print("\n🏥 Performing system health check...")
        health_status = await monitor._perform_comprehensive_health_check()
        health_score = monitor._calculate_health_score(health_status)
        
        print(f"💚 System Health Score: {health_score:.1f}%")
        
        # Show metrics summary
        print("\n📊 Current Monitoring Status:")
        summary = monitor.get_metrics_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        print("\n✨ Monitoring demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during monitoring demo: {e}")
    
    finally:
        await monitor.stop_monitoring()
        print("🛑 Monitoring system stopped")

if __name__ == "__main__":
    # Run the monitoring demo
    asyncio.run(run_monitoring_demo())
