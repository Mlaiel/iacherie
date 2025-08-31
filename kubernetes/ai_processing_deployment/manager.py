"""AI Processing Deployment Manager
===============================

Enterprise deployment management system for AI processing infrastructure
with comprehensive monitoring, scaling, and lifecycle management.

Features:
- Comprehensive deployment lifecycle management
- Auto-scaling and resource optimization
- Health monitoring and alerting
- Performance analytics and reporting
- Enterprise security and compliance

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
import os
import time
import yaml
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import json

import psutil
import docker
from kubernetes import client as k8s_client, config as k8s_config
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis.asyncio as aioredis
import aiofiles
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Float, Integer, JSON
from sqlalchemy.orm import sessionmaker

from .core import AIProcessingDeployment, ProcessingConfig, AIModelType
from .orchestrator import ProcessingOrchestrator, OrchestratorMode
from .pipeline import ProcessingPipeline, PipelineConfig
from .scheduler import AIProcessingScheduler, SchedulingConfig, SchedulingStrategy

# Metrics
deployment_health_score = Gauge('deployment_health_score', 'Overall deployment health score')
deployment_uptime_seconds = Gauge('deployment_uptime_seconds', 'Deployment uptime in seconds')
deployment_resource_usage = Gauge('deployment_resource_usage_percent', 'Resource usage percentage', ['resource'])
deployment_operations_total = Counter('deployment_operations_total', 'Total deployment operations', ['operation'])

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status states."""    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    SCALING = "scaling"
    UPDATING = "updating"
    FAILED = "failed"
    SHUTDOWN = "shutdown"


class ScalingPolicy(Enum):
    """Auto-scaling policies."""    DISABLED = "disabled"
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


@dataclass
class DeploymentMetrics:
    """Deployment metrics and statistics."""    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_mbps: float
    active_connections: int
    request_rate_per_minute: float
    error_rate_percent: float
    response_time_p95_ms: float
    health_score: float
    uptime_seconds: float
    last_updated: datetime


@dataclass
class ScalingConfiguration:
    """Auto-scaling configuration."""    enabled: bool = True
    policy: ScalingPolicy = ScalingPolicy.MODERATE
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_percent: float = 70.0
    target_memory_percent: float = 80.0
    scale_up_threshold: float = 85.0
    scale_down_threshold: float = 30.0
    scale_up_cooldown_minutes: int = 5
    scale_down_cooldown_minutes: int = 10
    custom_metrics: Dict[str, float] = None


@dataclass
class AlertConfiguration:
    """Alert configuration for monitoring."""    enabled: bool = True
    error_rate_threshold: float = 5.0
    response_time_threshold_ms: float = 5000.0
    cpu_threshold_percent: float = 90.0
    memory_threshold_percent: float = 95.0
    disk_threshold_percent: float = 85.0
    health_score_threshold: float = 0.7
    notification_channels: List[str] = None


class DeploymentManager:
    """    Enterprise AI Processing Deployment Manager
    
    Manages complete lifecycle of AI processing deployments with
    enterprise-grade monitoring, scaling, and operational capabilities.
    """    
    def __init__(
        self,
        deployment_id: str,
        config_path: Optional[str] = None
    ):
        """Initialize deployment manager."""        self.deployment_id = deployment_id
        self.config_path = config_path
        self.start_time = datetime.utcnow()
        
        # Configuration
        self.deployment_config: Optional[Dict[str, Any]] = None
        self.scaling_config: Optional[ScalingConfiguration] = None
        self.alert_config: Optional[AlertConfiguration] = None
        
        # Core components
        self.ai_deployment: Optional[AIProcessingDeployment] = None
        self.orchestrator: Optional[ProcessingOrchestrator] = None
        self.pipeline: Optional[ProcessingPipeline] = None
        self.scheduler: Optional[AIProcessingScheduler] = None
        
        # Infrastructure
        self.redis_client: Optional[aioredis.Redis] = None
        self.db_engine = None
        self.docker_client: Optional[docker.DockerClient] = None
        self.k8s_client: Optional[k8s_client.AppsV1Api] = None
        
        # Monitoring
        self.current_metrics: Optional[DeploymentMetrics] = None
        self.status = DeploymentStatus.INITIALIZING
        self.last_scaling_operation = None
        self.active_alerts = []
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._scaling_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Initialize manager
        asyncio.create_task(self._initialize_manager())
    
    async def _initialize_manager(self):
        """Initialize deployment manager components."""        try:
            logger.info(f"Initializing deployment manager: {self.deployment_id}")
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize infrastructure connections
            await self._initialize_infrastructure()
            
            # Initialize core components
            await self._initialize_components()
            
            # Start monitoring
            await self._start_monitoring()
            
            # Start Prometheus metrics server
            if self.deployment_config.get('monitoring', {}).get('prometheus_enabled', True):
                start_http_server(8000)
            
            self.status = DeploymentStatus.HEALTHY
            deployment_operations_total.labels(operation='initialize').inc()
            
            logger.info(f"Deployment manager {self.deployment_id} initialized successfully")
            
        except Exception as e:
            self.status = DeploymentStatus.FAILED
            logger.error(f"Failed to initialize deployment manager: {e}")
            raise
    
    async def _load_configuration(self):
        """Load deployment configuration from file or defaults."""        try:
            if self.config_path and os.path.exists(self.config_path):
                async with aiofiles.open(self.config_path, 'r') as f:
                    content = await f.read()
                    self.deployment_config = yaml.safe_load(content)
            else:
                # Default configuration
                self.deployment_config = {
                    'deployment': {
                        'name': self.deployment_id,
                        'environment': 'production',
                        'version': '2.0.0'
                    },
                    'processing': {
                        'max_workers': 10,
                        'gpu_enabled': True,
                        'memory_limit': '16Gi',
                        'cpu_limit': '8',
                        'scaling_enabled': True
                    },
                    'orchestrator': {
                        'mode': 'production',
                        'max_concurrent_tasks': 50
                    },
                    'pipeline': {
                        'enable_parallel_processing': True,
                        'enable_gpu_acceleration': True,
                        'quality_threshold': 0.85
                    },
                    'scheduler': {
                        'strategy': 'resource_optimized',
                        'max_queue_size': 1000
                    },
                    'scaling': {
                        'enabled': True,
                        'policy': 'moderate',
                        'min_replicas': 2,
                        'max_replicas': 20,
                        'target_cpu_percent': 70.0
                    },
                    'monitoring': {
                        'enabled': True,
                        'prometheus_enabled': True,
                        'health_check_interval': 30,
                        'metrics_retention_hours': 24
                    },
                    'alerts': {
                        'enabled': True,
                        'error_rate_threshold': 5.0,
                        'response_time_threshold_ms': 5000.0
                    }
                }
            
            # Parse specialized configurations
            self.scaling_config = ScalingConfiguration(**self.deployment_config.get('scaling', {}))
            self.alert_config = AlertConfiguration(**self.deployment_config.get('alerts', {}))
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def _initialize_infrastructure(self):
        """Initialize infrastructure connections."""        try:
            # Redis connection
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
            
            # Database connection
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                self.db_engine = create_engine(db_url, pool_size=20, max_overflow=30)
                await self._initialize_database_schema()
            
            # Docker client
            try:
                self.docker_client = docker.from_env()
            except Exception:
                logger.warning("Docker client not available")
            
            # Kubernetes client
            try:
                k8s_config.load_incluster_config()
                self.k8s_client = k8s_client.AppsV1Api()
            except Exception:
                try:
                    k8s_config.load_kube_config()
                    self.k8s_client = k8s_client.AppsV1Api()
                except Exception:
                    logger.warning("Kubernetes client not available")
            
            logger.info("Infrastructure connections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize infrastructure: {e}")
            raise
    
    async def _initialize_database_schema(self):
        """Initialize database schema for deployment tracking."""        try:
            metadata = MetaData()
            
            # Deployment status table
            deployment_status_table = Table(
                'deployment_status',
                metadata,
                Column('deployment_id', String(100), primary_key=True),
                Column('status', String(50)),
                Column('metrics', JSON),
                Column('configuration', JSON),
                Column('last_updated', DateTime),
                Column('created_at', DateTime)
            )
            
            # Deployment events table
            deployment_events_table = Table(
                'deployment_events',
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('deployment_id', String(100)),
                Column('event_type', String(50)),
                Column('event_data', JSON),
                Column('timestamp', DateTime)
            )
            
            metadata.create_all(self.db_engine)
            logger.info("Database schema initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
    
    async def _initialize_components(self):
        """Initialize core AI processing components."""        try:
            # Initialize AI processing deployment
            processing_config = ProcessingConfig(
                **self.deployment_config.get('processing', {})
            )
            self.ai_deployment = AIProcessingDeployment(processing_config)
            
            # Initialize orchestrator
            orchestrator_mode = self.deployment_config.get('orchestrator', {}).get('mode', 'production')
            self.orchestrator = ProcessingOrchestrator(OrchestratorMode(orchestrator_mode))
            
            # Initialize pipeline
            pipeline_config = PipelineConfig(
                **self.deployment_config.get('pipeline', {})
            )
            self.pipeline = ProcessingPipeline(pipeline_config)
            
            # Initialize scheduler
            scheduler_config = SchedulingConfig(
                strategy=SchedulingStrategy(self.deployment_config.get('scheduler', {}).get('strategy', 'priority')),
                **{k: v for k, v in self.deployment_config.get('scheduler', {}).items() if k != 'strategy'}
            )
            self.scheduler = AIProcessingScheduler(scheduler_config)
            
            # Load AI models
            await self._load_ai_models()
            
            logger.info("Core components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def _load_ai_models(self):
        """Load AI models for processing."""        try:
            models_config = self.deployment_config.get('models', {})
            
            # Default model configurations
            default_models = {
                'audio_fingerprint': {
                    'name': 'audio_fingerprint_model',
                    'path': '/models/audio/',
                    'sample_rate': 22050,
                    'n_mfcc': 13
                },
                'video_fingerprint': {
                    'name': 'video_fingerprint_model',
                    'path': '/models/video/',
                    'frame_rate': 1,
                    'resize_dims': (224, 224)
                },
                'image_fingerprint': {
                    'name': 'image_fingerprint_model',
                    'path': '/models/image/',
                    'hash_size': 16,
                    'similarity_threshold': 0.85
                },
                'text_fingerprint': {
                    'name': 'text_fingerprint_model',
                    'path': '/models/text/',
                    'max_length': 512,
                    'similarity_threshold': 0.8
                }
            }
            
            # Load each model type
            for model_type_str, model_config in default_models.items():
                try:
                    model_type = AIModelType(model_type_str)
                    user_config = models_config.get(model_type_str, {})
                    final_config = {**model_config, **user_config}
                    
                    success = await self.ai_deployment.load_model(model_type, final_config)
                    if success:
                        logger.info(f"Loaded model: {model_type_str}")
                    else:
                        logger.warning(f"Failed to load model: {model_type_str}")
                        
                except Exception as e:
                    logger.error(f"Error loading model {model_type_str}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
    
    async def _start_monitoring(self):
        """Start monitoring background tasks."""        try:
            # Start monitoring tasks
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            if self.scaling_config.enabled:
                self._scaling_task = asyncio.create_task(self._scaling_loop())
            
            logger.info("Monitoring tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Main monitoring loop for metrics collection."""        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_metrics()
                self.current_metrics = metrics
                
                # Update Prometheus metrics
                deployment_health_score.set(metrics.health_score)
                deployment_uptime_seconds.set(metrics.uptime_seconds)
                deployment_resource_usage.labels(resource='cpu').set(metrics.cpu_usage_percent)
                deployment_resource_usage.labels(resource='memory').set(metrics.memory_usage_percent)
                deployment_resource_usage.labels(resource='disk').set(metrics.disk_usage_percent)
                
                # Store metrics in Redis
                if self.redis_client:
                    metrics_data = asdict(metrics)
                    metrics_data['last_updated'] = metrics.last_updated.isoformat()
                    await self.redis_client.hset(
                        f"deployment_metrics:{self.deployment_id}",
                        mapping=metrics_data
                    )
                    await self.redis_client.expire(f"deployment_metrics:{self.deployment_id}", 3600)
                
                # Store in database
                await self._store_metrics_in_database(metrics)
                
                # Check alerts
                await self._check_alerts(metrics)
                
                # Wait for next collection
                interval = self.deployment_config.get('monitoring', {}).get('interval_seconds', 30)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_metrics(self) -> DeploymentMetrics:
        """Collect comprehensive deployment metrics."""        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            # Application metrics
            active_connections = len(self.scheduler.active_tasks) if self.scheduler else 0
            
            # Calculate health score
            health_score = self._calculate_health_score(cpu_percent, memory.percent, disk.percent)
            
            # Uptime
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            
            return DeploymentMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io_mbps=net_io.bytes_sent / 1024 / 1024,  # Simplified calculation
                active_connections=active_connections,
                request_rate_per_minute=0.0,  # Would be calculated from actual request metrics
                error_rate_percent=0.0,  # Would be calculated from error metrics
                response_time_p95_ms=0.0,  # Would be calculated from response time metrics
                health_score=health_score,
                uptime_seconds=uptime_seconds,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            # Return default metrics on error
            return DeploymentMetrics(
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0,
                network_io_mbps=0.0,
                active_connections=0,
                request_rate_per_minute=0.0,
                error_rate_percent=0.0,
                response_time_p95_ms=0.0,
                health_score=0.5,
                uptime_seconds=0.0,
                last_updated=datetime.utcnow()
            )
    
    def _calculate_health_score(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> float:
        """Calculate overall health score based on system metrics."""        try:
            # Weight factors for different metrics
            cpu_weight = 0.3
            memory_weight = 0.4
            disk_weight = 0.3
            
            # Calculate individual scores (inverted - lower usage = higher score)
            cpu_score = max(0, (100 - cpu_percent) / 100)
            memory_score = max(0, (100 - memory_percent) / 100)
            disk_score = max(0, (100 - disk_percent) / 100)
            
            # Weighted average
            health_score = (
                cpu_score * cpu_weight +
                memory_score * memory_weight +
                disk_score * disk_weight
            )
            
            return round(health_score, 3)
            
        except Exception:
            return 0.5  # Default score on error
    
    async def _store_metrics_in_database(self, metrics: DeploymentMetrics):
        """Store metrics in database for historical analysis."""        try:
            if not self.db_engine:
                return
            
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            
            try:
                # Update deployment status
                status_data = {
                    'deployment_id': self.deployment_id,
                    'status': self.status.value,
                    'metrics': asdict(metrics),
                    'configuration': self.deployment_config,
                    'last_updated': datetime.utcnow(),
                    'created_at': self.start_time
                }
                
                # Use raw SQL for upsert
                session.execute("""                    INSERT INTO deployment_status (deployment_id, status, metrics, configuration, last_updated, created_at)
                    VALUES (:deployment_id, :status, :metrics, :configuration, :last_updated, :created_at)
                    ON CONFLICT (deployment_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    metrics = EXCLUDED.metrics,
                    configuration = EXCLUDED.configuration,
                    last_updated = EXCLUDED.last_updated
                """, status_data)
                
                session.commit()
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to store metrics in database: {e}")
    
    async def _check_alerts(self, metrics: DeploymentMetrics):
        """Check alert conditions and trigger notifications."""        try:
            if not self.alert_config.enabled:
                return
            
            alerts = []
            
            # CPU threshold
            if metrics.cpu_usage_percent > self.alert_config.cpu_threshold_percent:
                alerts.append({
                    'type': 'cpu_high',
                    'message': f"CPU usage {metrics.cpu_usage_percent:.1f}% exceeds threshold {self.alert_config.cpu_threshold_percent}%",
                    'severity': 'warning',
                    'value': metrics.cpu_usage_percent,
                    'threshold': self.alert_config.cpu_threshold_percent
                })
            
            # Memory threshold
            if metrics.memory_usage_percent > self.alert_config.memory_threshold_percent:
                alerts.append({
                    'type': 'memory_high',
                    'message': f"Memory usage {metrics.memory_usage_percent:.1f}% exceeds threshold {self.alert_config.memory_threshold_percent}%",
                    'severity': 'critical',
                    'value': metrics.memory_usage_percent,
                    'threshold': self.alert_config.memory_threshold_percent
                })
            
            # Disk threshold
            if metrics.disk_usage_percent > self.alert_config.disk_threshold_percent:
                alerts.append({
                    'type': 'disk_high',
                    'message': f"Disk usage {metrics.disk_usage_percent:.1f}% exceeds threshold {self.alert_config.disk_threshold_percent}%",
                    'severity': 'warning',
                    'value': metrics.disk_usage_percent,
                    'threshold': self.alert_config.disk_threshold_percent
                })
            
            # Health score threshold
            if metrics.health_score < self.alert_config.health_score_threshold:
                alerts.append({
                    'type': 'health_low',
                    'message': f"Health score {metrics.health_score:.3f} below threshold {self.alert_config.health_score_threshold}",
                    'severity': 'critical',
                    'value': metrics.health_score,
                    'threshold': self.alert_config.health_score_threshold
                })
            
            # Process new alerts
            for alert in alerts:
                await self._process_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    async def _process_alert(self, alert: Dict[str, Any]):
        """Process and handle an alert."""        try:
            alert['timestamp'] = datetime.utcnow().isoformat()
            alert['deployment_id'] = self.deployment_id
            
            # Add to active alerts
            self.active_alerts.append(alert)
            
            # Log alert
            logger.warning(f"ALERT [{alert['type']}]: {alert['message']}")
            
            # Store in Redis
            if self.redis_client:
                await self.redis_client.lpush(f"alerts:{self.deployment_id}", json.dumps(alert))
                await self.redis_client.ltrim(f"alerts:{self.deployment_id}", 0, 100)  # Keep last 100 alerts
            
            # Store in database
            await self._store_alert_in_database(alert)
            
            # Send notifications (placeholder)
            await self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"Failed to process alert: {e}")
    
    async def _store_alert_in_database(self, alert: Dict[str, Any]):
        """Store alert in database."""        try:
            if not self.db_engine:
                return
            
            Session = sessionmaker(bind=self.db_engine)
            session = Session()
            
            try:
                session.execute("""                    INSERT INTO deployment_events (deployment_id, event_type, event_data, timestamp)
                    VALUES (:deployment_id, :event_type, :event_data, :timestamp)
                """, {
                    'deployment_id': self.deployment_id,
                    'event_type': 'alert',
                    'event_data': alert,
                    'timestamp': datetime.utcnow()
                })
                session.commit()
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")
    
    async def _send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification to configured channels."""        try:
            # Placeholder for notification system
            # Would integrate with Slack, email, PagerDuty, etc.
            logger.info(f"Alert notification: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    async def _health_check_loop(self):
        """Health check monitoring loop."""        while True:
            try:
                # Perform health checks
                health_status = await self._perform_health_checks()
                
                # Update deployment status based on health
                if health_status['overall_health'] < 0.3:
                    self.status = DeploymentStatus.UNHEALTHY
                elif health_status['overall_health'] < 0.7:
                    self.status = DeploymentStatus.DEGRADED
                else:
                    self.status = DeploymentStatus.HEALTHY
                
                # Health check interval
                interval = self.deployment_config.get('monitoring', {}).get('health_check_interval', 30)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                self.status = DeploymentStatus.UNHEALTHY
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """Perform comprehensive health checks."""        try:
            health_checks = {}
            
            # Component health checks
            health_checks['ai_deployment'] = self.ai_deployment is not None
            health_checks['orchestrator'] = self.orchestrator is not None
            health_checks['pipeline'] = self.pipeline is not None
            health_checks['scheduler'] = self.scheduler is not None
            
            # Infrastructure health checks
            health_checks['redis'] = await self._check_redis_health()
            health_checks['database'] = await self._check_database_health()
            
            # System health checks
            if self.current_metrics:
                health_checks['cpu_ok'] = self.current_metrics.cpu_usage_percent < 95
                health_checks['memory_ok'] = self.current_metrics.memory_usage_percent < 95
                health_checks['disk_ok'] = self.current_metrics.disk_usage_percent < 90
            else:
                health_checks['cpu_ok'] = True
                health_checks['memory_ok'] = True
                health_checks['disk_ok'] = True
            
            # Calculate overall health
            total_checks = len(health_checks)
            passed_checks = sum(1 for check in health_checks.values() if check)
            overall_health = passed_checks / total_checks if total_checks > 0 else 0
            
            return {
                'checks': health_checks,
                'overall_health': overall_health,
                'passed_checks': passed_checks,
                'total_checks': total_checks,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
            return {
                'checks': {},
                'overall_health': 0.0,
                'passed_checks': 0,
                'total_checks': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def _check_redis_health(self) -> bool:
        """Check Redis connection health."""        try:
            if not self.redis_client:
                return False
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def _check_database_health(self) -> bool:
        """Check database connection health."""        try:
            if not self.db_engine:
                return False
            with self.db_engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def _scaling_loop(self):
        """Auto-scaling monitoring and execution loop."""        while True:
            try:
                if self.scaling_config.enabled and self.current_metrics:
                    await self._evaluate_scaling_decisions()
                
                # Scaling check interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _evaluate_scaling_decisions(self):
        """Evaluate and execute scaling decisions."""        try:
            metrics = self.current_metrics
            if not metrics:
                return
            
            # Check cooldown periods
            if self.last_scaling_operation:
                time_since_scaling = (datetime.utcnow() - self.last_scaling_operation).total_seconds() / 60
                cooldown_minutes = (self.scaling_config.scale_up_cooldown_minutes 
                                  if self._should_scale_up(metrics) 
                                  else self.scaling_config.scale_down_cooldown_minutes)
                
                if time_since_scaling < cooldown_minutes:
                    return  # Still in cooldown period
            
            # Evaluate scaling up
            if self._should_scale_up(metrics):
                await self._scale_up()
            
            # Evaluate scaling down
            elif self._should_scale_down(metrics):
                await self._scale_down()
            
        except Exception as e:
            logger.error(f"Failed to evaluate scaling decisions: {e}")
    
    def _should_scale_up(self, metrics: DeploymentMetrics) -> bool:
        """Determine if scaling up is needed."""        cpu_trigger = metrics.cpu_usage_percent > self.scaling_config.scale_up_threshold
        memory_trigger = metrics.memory_usage_percent > self.scaling_config.scale_up_threshold
        
        return cpu_trigger or memory_trigger
    
    def _should_scale_down(self, metrics: DeploymentMetrics) -> bool:
        """Determine if scaling down is possible."""        cpu_ok = metrics.cpu_usage_percent < self.scaling_config.scale_down_threshold
        memory_ok = metrics.memory_usage_percent < self.scaling_config.scale_down_threshold
        
        return cpu_ok and memory_ok
    
    async def _scale_up(self):
        """Execute scale up operation."""        try:
            self.status = DeploymentStatus.SCALING
            current_replicas = await self._get_current_replicas()
            
            if current_replicas < self.scaling_config.max_replicas:
                target_replicas = min(current_replicas + 1, self.scaling_config.max_replicas)
                await self._set_replicas(target_replicas)
                
                self.last_scaling_operation = datetime.utcnow()
                deployment_operations_total.labels(operation='scale_up').inc()
                
                logger.info(f"Scaled up from {current_replicas} to {target_replicas} replicas")
            
            self.status = DeploymentStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Failed to scale up: {e}")
            self.status = DeploymentStatus.FAILED
    
    async def _scale_down(self):
        """Execute scale down operation."""        try:
            self.status = DeploymentStatus.SCALING
            current_replicas = await self._get_current_replicas()
            
            if current_replicas > self.scaling_config.min_replicas:
                target_replicas = max(current_replicas - 1, self.scaling_config.min_replicas)
                await self._set_replicas(target_replicas)
                
                self.last_scaling_operation = datetime.utcnow()
                deployment_operations_total.labels(operation='scale_down').inc()
                
                logger.info(f"Scaled down from {current_replicas} to {target_replicas} replicas")
            
            self.status = DeploymentStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Failed to scale down: {e}")
            self.status = DeploymentStatus.FAILED
    
    async def _get_current_replicas(self) -> int:
        """Get current number of replicas."""        try:
            if self.k8s_client:
                deployment = self.k8s_client.read_namespaced_deployment(
                    name=f"ai-processing-{self.deployment_id}",
                    namespace="default"
                )
                return deployment.spec.replicas
            else:
                # Fallback to configuration
                return self.deployment_config.get('processing', {}).get('replicas', 1)
                
        except Exception as e:
            logger.error(f"Failed to get current replicas: {e}")
            return 1
    
    async def _set_replicas(self, target_replicas: int):
        """Set target number of replicas."""        try:
            if self.k8s_client:
                deployment = self.k8s_client.read_namespaced_deployment(
                    name=f"ai-processing-{self.deployment_id}",
                    namespace="default"
                )
                deployment.spec.replicas = target_replicas
                
                self.k8s_client.patch_namespaced_deployment(
                    name=f"ai-processing-{self.deployment_id}",
                    namespace="default",
                    body=deployment
                )
            else:
                logger.warning("Kubernetes client not available, cannot scale replicas")
                
        except Exception as e:
            logger.error(f"Failed to set replicas to {target_replicas}: {e}")
            raise
    
    async def get_deployment_status(self) -> Dict[str, Any]:
        """Get comprehensive deployment status."""        try:
            status_data = {
                'deployment_id': self.deployment_id,
                'status': self.status.value,
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'configuration': self.deployment_config,
                'metrics': asdict(self.current_metrics) if self.current_metrics else None,
                'scaling_config': asdict(self.scaling_config) if self.scaling_config else None,
                'active_alerts': len(self.active_alerts),
                'components': {
                    'ai_deployment': self.ai_deployment is not None,
                    'orchestrator': self.orchestrator is not None,
                    'pipeline': self.pipeline is not None,
                    'scheduler': self.scheduler is not None
                },
                'last_scaling_operation': self.last_scaling_operation.isoformat() if self.last_scaling_operation else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return status_data
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return {
                'deployment_id': self.deployment_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Gracefully shutdown deployment manager."""        try:
            logger.info(f"Shutting down deployment manager: {self.deployment_id}")
            self.status = DeploymentStatus.SHUTDOWN
            
            # Cancel background tasks
            for task in [self._monitoring_task, self._scaling_task, self._health_check_task]:
                if task:
                    task.cancel()
            
            # Shutdown components
            if self.ai_deployment:
                await self.ai_deployment.shutdown()
            
            if self.orchestrator:
                await self.orchestrator.shutdown()
            
            if self.scheduler:
                await self.scheduler.shutdown()
            
            # Close connections
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_engine:
                self.db_engine.dispose()
            
            deployment_operations_total.labels(operation='shutdown').inc()
            logger.info("Deployment manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Factory functions
def create_deployment_manager(deployment_id: str, config_path: Optional[str] = None) -> DeploymentManager:
    """Create deployment manager with configuration."""    return DeploymentManager(deployment_id, config_path)


def create_production_deployment_manager(deployment_id: str) -> DeploymentManager:
    """Create production-ready deployment manager."""    return DeploymentManager(deployment_id, None)
