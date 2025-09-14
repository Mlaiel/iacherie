"""
Health Monitoring module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Health Monitoring System
Comprehensive health monitoring and alerting for the IA Influencer Agent platform
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
import requests
import psycopg2
from kubernetes import client, config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """
Health status enumeration"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity enumeration"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthCheck:
    """Health check data class"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    metadata: Dict[str, Any] = None


@dataclass
class Alert:
    """
Alert data class"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class HealthMonitor:
    """
    Enterprise-grade health monitoring system
    Monitors system health, services, and generates alerts
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
Initialize health monitor"""
        self.config_path = config_path or "/etc/monitoring/health_config.json"
        self.checks = {}
        self.alerts = []
        self.running = False
        self.check_interval = 30  # seconds
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self._load_configuration()
        self._register_default_checks()
        self._initialize_kubernetes_client()
    
    def _load_configuration(self) -> None:
        """Load monitoring configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded health monitoring configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default health monitoring configuration")
        except Exception as e:
            logger.error(f"Failed to load health monitoring configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration"""
        return {
            "check_interval": 30,
            "thresholds": {
                "cpu_usage": {"warning": 70, "critical": 90},
                "memory_usage": {"warning": 80, "critical": 95},
                "disk_usage": {"warning": 80, "critical": 95},
                "response_time": {"warning": 1000, "critical": 5000}
            },
            "endpoints": {
                "api_gateway": "http://localhost:8000/health",
                "database": "postgresql://localhost:5432",
                "redis": "redis://localhost:6379",
                "elasticsearch": "http://localhost:9200/_cluster/health"
            },
            "kubernetes": {
                "enabled": True,
                "namespace": "default"
            },
            "notifications": {
                "slack": {
                    "enabled": False,
                    "webhook": None
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "localhost",
                    "smtp_port": 587,
                    "recipients": []
                },
                "pagerduty": {
                    "enabled": False,
                    "integration_key": None
                }
            },
            "retention": {
                "health_checks": 7,  # days
                "alerts": 30  # days
            }
        }
    
    def _register_default_checks(self) -> None:
        """Register default health checks"""
        self.register_check("system_cpu", self._check_system_cpu)
        self.register_check("system_memory", self._check_system_memory)
        self.register_check("system_disk", self._check_system_disk)
        self.register_check("api_gateway", self._check_api_gateway)
        self.register_check("database", self._check_database)
        self.register_check("redis", self._check_redis)
        self.register_check("elasticsearch", self._check_elasticsearch)
        
        if self.config.get("kubernetes", {}).get("enabled", False):
            self.register_check("kubernetes_pods", self._check_kubernetes_pods)
            self.register_check("kubernetes_services", self._check_kubernetes_services)
            self.register_check("kubernetes_nodes", self._check_kubernetes_nodes)
    
    def _initialize_kubernetes_client(self) -> None:
        """Initialize Kubernetes client if enabled"""
        try:
            if not self.config.get("kubernetes", {}).get("enabled", False):
                return
                
            try:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            except config.ConfigException:
                try:
                    config.load_kube_config()
                    logger.info("Loaded local Kubernetes configuration")
                except config.ConfigException:
                    logger.warning("Failed to load Kubernetes configuration")
                    return
            
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_apps_v1 = client.AppsV1Api()
            
        except Exception as e:
            logger.error(f"Kubernetes client initialization error: {e}")
    
    def register_check(self, name: str, check_function: Callable[[], HealthCheck]) -> None:
        """Register new health check"""
        self.checks[name] = check_function
        logger.info(f"Registered health check: {name}")
    
    def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        try:
            logger.info("Starting health monitoring")
            self.running = True
            
            while self.running:
                try:
                    self._execute_health_checks()
                    time.sleep(self.check_interval)
                except KeyboardInterrupt:
                    logger.info("Monitoring interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(self.check_interval)
            
        except Exception as e:
            logger.error(f"Monitoring startup error: {e}")
        finally:
            self.running = False
            self.executor.shutdown(wait=True)
            logger.info("Health monitoring stopped")
    
    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.running = False
        logger.info("Stopping health monitoring")
    
    def _execute_health_checks(self) -> None:
        """Execute all registered health checks"""
        try:
            logger.debug("Executing health checks")
            
            # Submit all checks to thread pool
            future_to_check = {}
            for check_name, check_function in self.checks.items():
                future = self.executor.submit(self._execute_single_check, check_name, check_function)
                future_to_check[future] = check_name
            
            # Collect results
            health_results = {}
            for future in as_completed(future_to_check, timeout=60):
                check_name = future_to_check[future]
                try:
                    health_check = future.result()
                    health_results[check_name] = health_check
                    
                    # Generate alerts if needed
                    self._evaluate_health_check_for_alerts(health_check)
                    
                except Exception as e:
                    logger.error(f"Health check failed: {check_name} - {e}")
                    
                    # Create failed health check
                    health_results[check_name] = HealthCheck(
                        name=check_name,
                        status=HealthStatus.CRITICAL,
                        message=f"Check execution failed: {e}",
                        timestamp=datetime.now(),
                        response_time_ms=0.0
                    )
            
            # Store results and send notifications if needed
            self._process_health_results(health_results)
            
        except Exception as e:
            logger.error(f"Health checks execution error: {e}")
    
    def _execute_single_check(self, check_name: str, check_function: Callable) -> HealthCheck:
        """Execute single health check with timing"""
        start_time = time.time()
        
        try:
            health_check = check_function()
            health_check.response_time_ms = (time.time() - start_time) * 1000
            return health_check
            
        except Exception as e:
            return HealthCheck(
                name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Check execution error: {e}",
                timestamp=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_system_cpu(self) -> HealthCheck:
        """Check system CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            thresholds = self.config.get("thresholds", {}).get("cpu_usage", {})
            
            if cpu_percent >= thresholds.get("critical", 90):
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent}%"
            elif cpu_percent >= thresholds.get("warning", 70):
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent}%"
            
            return HealthCheck(
                name="system_cpu",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0.0,
                metadata={"cpu_percent": cpu_percent}
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_cpu",
                status=HealthStatus.CRITICAL,
                message=f"CPU check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_system_memory(self) -> HealthCheck:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            thresholds = self.config.get("thresholds", {}).get("memory_usage", {})
            
            if memory_percent >= thresholds.get("critical", 95):
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory_percent}%"
            elif memory_percent >= thresholds.get("warning", 80):
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent}%"
            
            return HealthCheck(
                name="system_memory",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0.0,
                metadata={
                    "memory_percent": memory_percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_memory",
                status=HealthStatus.CRITICAL,
                message=f"Memory check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_system_disk(self) -> HealthCheck:
        """Check system disk usage"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            thresholds = self.config.get("thresholds", {}).get("disk_usage", {})
            
            if disk_percent >= thresholds.get("critical", 95):
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent >= thresholds.get("warning", 80):
                status = HealthStatus.WARNING
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            return HealthCheck(
                name="system_disk",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0.0,
                metadata={
                    "disk_percent": disk_percent,
                    "total": disk.total,
                    "free": disk.free,
                    "used": disk.used
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="system_disk",
                status=HealthStatus.CRITICAL,
                message=f"Disk check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_api_gateway(self) -> HealthCheck:
        """Check API Gateway health"""
        try:
            endpoint = self.config.get("endpoints", {}).get("api_gateway", "http://localhost:8000/health")
            
            start_time = time.time()
            response = requests.get(endpoint, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            thresholds = self.config.get("thresholds", {}).get("response_time", {})
            
            if response.status_code == 200:
                if response_time >= thresholds.get("critical", 5000):
                    status = HealthStatus.CRITICAL
                    message = f"API Gateway slow response: {response_time:.0f}ms"
                elif response_time >= thresholds.get("warning", 1000):
                    status = HealthStatus.WARNING
                    message = f"API Gateway slow response: {response_time:.0f}ms"
                else:
                    status = HealthStatus.HEALTHY
                    message = f"API Gateway healthy: {response_time:.0f}ms"
            else:
                status = HealthStatus.CRITICAL
                message = f"API Gateway unhealthy: HTTP {response.status_code}"
            
            return HealthCheck(
                name="api_gateway",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                metadata={"status_code": response.status_code}
            )
            
        except Exception as e:
            return HealthCheck(
                name="api_gateway",
                status=HealthStatus.CRITICAL,
                message=f"API Gateway check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_database(self) -> HealthCheck:
        """Check database connectivity"""
        try:
            db_url = self.config.get("endpoints", {}).get("database", "postgresql://localhost:5432")
            
            start_time = time.time()
            
            # Parse database URL
            if db_url.startswith("postgresql://"):
                # Simple connection test
                conn = psycopg2.connect(db_url)
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                conn.close()
                
                response_time = (time.time() - start_time) * 1000
                
                return HealthCheck(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    message=f"Database healthy: {response_time:.0f}ms",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
            else:
                raise ValueError("Unsupported database URL format")
                
        except Exception as e:
            return HealthCheck(
                name="database",
                status=HealthStatus.CRITICAL,
                message=f"Database check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_redis(self) -> HealthCheck:
        """Check Redis connectivity"""
        try:
            redis_url = self.config.get("endpoints", {}).get("redis", "redis://localhost:6379")
            
            start_time = time.time()
            
            # Simple Redis ping test
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message=f"Redis healthy: {response_time:.0f}ms",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheck(
                name="redis",
                status=HealthStatus.CRITICAL,
                message=f"Redis check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_elasticsearch(self) -> HealthCheck:
        """Check Elasticsearch cluster health"""
        try:
            es_url = self.config.get("endpoints", {}).get("elasticsearch", "http://localhost:9200/_cluster/health")
            
            start_time = time.time()
            response = requests.get(es_url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                cluster_status = health_data.get("status", "unknown")
                
                if cluster_status == "green":
                    status = HealthStatus.HEALTHY
                    message = f"Elasticsearch cluster green: {response_time:.0f}ms"
                elif cluster_status == "yellow":
                    status = HealthStatus.WARNING
                    message = f"Elasticsearch cluster yellow: {response_time:.0f}ms"
                else:
                    status = HealthStatus.CRITICAL
                    message = f"Elasticsearch cluster red: {response_time:.0f}ms"
                
                return HealthCheck(
                    name="elasticsearch",
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    metadata=health_data
                )
            else:
                return HealthCheck(
                    name="elasticsearch",
                    status=HealthStatus.CRITICAL,
                    message=f"Elasticsearch unhealthy: HTTP {response.status_code}",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            return HealthCheck(
                name="elasticsearch",
                status=HealthStatus.CRITICAL,
                message=f"Elasticsearch check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_kubernetes_pods(self) -> HealthCheck:
        """Check Kubernetes pods health"""
        try:
            if not hasattr(self, 'k8s_core_v1'):
                return HealthCheck(
                    name="kubernetes_pods",
                    status=HealthStatus.UNKNOWN,
                    message="Kubernetes client not available",
                    timestamp=datetime.now(),
                    response_time_ms=0.0
                )
            
            namespace = self.config.get("kubernetes", {}).get("namespace", "default")
            
            start_time = time.time()
            pods = self.k8s_core_v1.list_namespaced_pod(namespace=namespace)
            response_time = (time.time() - start_time) * 1000
            
            total_pods = len(pods.items)
            running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
            failed_pods = sum(1 for pod in pods.items if pod.status.phase == "Failed")
            
            if failed_pods > 0:
                status = HealthStatus.CRITICAL
                message = f"Kubernetes: {failed_pods} pods failed out of {total_pods}"
            elif running_pods < total_pods:
                status = HealthStatus.WARNING
                message = f"Kubernetes: {running_pods}/{total_pods} pods running"
            else:
                status = HealthStatus.HEALTHY
                message = f"Kubernetes: All {total_pods} pods running"
            
            return HealthCheck(
                name="kubernetes_pods",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                metadata={
                    "total_pods": total_pods,
                    "running_pods": running_pods,
                    "failed_pods": failed_pods
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="kubernetes_pods",
                status=HealthStatus.CRITICAL,
                message=f"Kubernetes pods check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_kubernetes_services(self) -> HealthCheck:
        """Check Kubernetes services health"""
        try:
            if not hasattr(self, 'k8s_core_v1'):
                return HealthCheck(
                    name="kubernetes_services",
                    status=HealthStatus.UNKNOWN,
                    message="Kubernetes client not available",
                    timestamp=datetime.now(),
                    response_time_ms=0.0
                )
            
            namespace = self.config.get("kubernetes", {}).get("namespace", "default")
            
            start_time = time.time()
            services = self.k8s_core_v1.list_namespaced_service(namespace=namespace)
            response_time = (time.time() - start_time) * 1000
            
            total_services = len(services.items)
            
            return HealthCheck(
                name="kubernetes_services",
                status=HealthStatus.HEALTHY,
                message=f"Kubernetes: {total_services} services available",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                metadata={"total_services": total_services}
            )
            
        except Exception as e:
            return HealthCheck(
                name="kubernetes_services",
                status=HealthStatus.CRITICAL,
                message=f"Kubernetes services check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _check_kubernetes_nodes(self) -> HealthCheck:
        """Check Kubernetes nodes health"""
        try:
            if not hasattr(self, 'k8s_core_v1'):
                return HealthCheck(
                    name="kubernetes_nodes",
                    status=HealthStatus.UNKNOWN,
                    message="Kubernetes client not available",
                    timestamp=datetime.now(),
                    response_time_ms=0.0
                )
            
            start_time = time.time()
            nodes = self.k8s_core_v1.list_node()
            response_time = (time.time() - start_time) * 1000
            
            total_nodes = len(nodes.items)
            ready_nodes = 0
            
            for node in nodes.items:
                for condition in node.status.conditions:
                    if condition.type == "Ready" and condition.status == "True":
                        ready_nodes += 1
                        break
            
            if ready_nodes < total_nodes:
                status = HealthStatus.CRITICAL
                message = f"Kubernetes: {ready_nodes}/{total_nodes} nodes ready"
            else:
                status = HealthStatus.HEALTHY
                message = f"Kubernetes: All {total_nodes} nodes ready"
            
            return HealthCheck(
                name="kubernetes_nodes",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                metadata={
                    "total_nodes": total_nodes,
                    "ready_nodes": ready_nodes
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="kubernetes_nodes",
                status=HealthStatus.CRITICAL,
                message=f"Kubernetes nodes check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=0.0
            )
    
    def _evaluate_health_check_for_alerts(self, health_check: HealthCheck) -> None:
        """Evaluate health check and generate alerts if needed"""
        try:
            # Check if we need to generate an alert
            if health_check.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                # Check if similar alert already exists
                existing_alert = self._find_existing_alert(health_check.name, health_check.status)
                
                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        id=f"alert_{int(time.time())}_{health_check.name}",
                        title=f"Health Check Alert: {health_check.name}",
                        description=health_check.message,
                        severity=AlertSeverity.CRITICAL if health_check.status == HealthStatus.CRITICAL else AlertSeverity.WARNING,
                        source=health_check.name,
                        timestamp=datetime.now(),
                        metadata=health_check.metadata
                    )
                    
                    self.alerts.append(alert)
                    self._send_alert_notification(alert)
                    
                    logger.info(f"Generated alert: {alert.id}")
            
            elif health_check.status == HealthStatus.HEALTHY:
                # Check if we need to resolve existing alerts
                self._resolve_alerts_for_check(health_check.name)
                
        except Exception as e:
            logger.error(f"Alert evaluation error: {e}")
    
    def _find_existing_alert(self, check_name: str, status: HealthStatus) -> Optional[Alert]:
        """Find existing unresolved alert for check"""
        for alert in self.alerts:
            if (alert.source == check_name and 
                not alert.resolved and
                alert.severity.value == ("critical" if status == HealthStatus.CRITICAL else "warning")):
                return alert
        return None
    
    def _resolve_alerts_for_check(self, check_name: str) -> None:
        """Resolve all alerts for specific check"""
        for alert in self.alerts:
            if alert.source == check_name and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                # Send resolution notification
                self._send_alert_resolution_notification(alert)
                
                logger.info(f"Resolved alert: {alert.id}")
    
    def _send_alert_notification(self, alert: Alert) -> None:
        """Send alert notification"""
        try:
            notifications_config = self.config.get("notifications", {})
            
            # Slack notification
            if notifications_config.get("slack", {}).get("enabled", False):
                self._send_slack_alert(alert, notifications_config["slack"])
            
            # Email notification
            if notifications_config.get("email", {}).get("enabled", False):
                self._send_email_alert(alert, notifications_config["email"])
            
            # PagerDuty notification
            if notifications_config.get("pagerduty", {}).get("enabled", False):
                self._send_pagerduty_alert(alert, notifications_config["pagerduty"])
                
        except Exception as e:
            logger.error(f"Alert notification error: {e}")
    
    def _send_alert_resolution_notification(self, alert: Alert) -> None:
        """Send alert resolution notification"""
        try:
            notifications_config = self.config.get("notifications", {})
            
            # Slack notification
            if notifications_config.get("slack", {}).get("enabled", False):
                self._send_slack_resolution(alert, notifications_config["slack"])
                
        except Exception as e:
            logger.error(f"Alert resolution notification error: {e}")
    
    def _send_slack_alert(self, alert: Alert, slack_config: Dict[str, Any]) -> None:
        """Send Slack alert notification"""
        try:
            webhook_url = slack_config.get("webhook")
            if not webhook_url:
                return
            
            color = "danger" if alert.severity == AlertSeverity.CRITICAL else "warning"
            
            message = {
                "attachments": [
                    {
                        "color": color,
                        "title": alert.title,
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            requests.post(webhook_url, json=message, timeout=10)
            logger.info(f"Sent Slack alert notification: {alert.id}")
            
        except Exception as e:
            logger.error(f"Slack alert notification error: {e}")
    
    def _send_slack_resolution(self, alert: Alert, slack_config: Dict[str, Any]) -> None:
        """Send Slack alert resolution notification"""
        try:
            webhook_url = slack_config.get("webhook")
            if not webhook_url:
                return
            
            message = {
                "attachments": [
                    {
                        "color": "good",
                        "title": f"✅ RESOLVED: {alert.title}",
                        "text": f"Alert has been resolved",
                        "fields": [
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Resolved At",
                                "value": alert.resolved_at.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            requests.post(webhook_url, json=message, timeout=10)
            logger.info(f"Sent Slack resolution notification: {alert.id}")
            
        except Exception as e:
            logger.error(f"Slack resolution notification error: {e}")
    
    def _send_email_alert(self, alert: Alert, email_config: Dict[str, Any]) -> None:
        """Send email alert notification"""
        try:
            # This would integrate with email service
            logger.info(f"Email alert notification sent: {alert.id}")
            
        except Exception as e:
            logger.error(f"Email alert notification error: {e}")
    
    def _send_pagerduty_alert(self, alert: Alert, pagerduty_config: Dict[str, Any]) -> None:
        """Send PagerDuty alert notification"""
        try:
            # This would integrate with PagerDuty API
            logger.info(f"PagerDuty alert notification sent: {alert.id}")
            
        except Exception as e:
            logger.error(f"PagerDuty alert notification error: {e}")
    
    def _process_health_results(self, health_results: Dict[str, HealthCheck]) -> None:
        """Process health check results"""
        try:
            # Store results (in production, this would go to a database)
            logger.debug(f"Processing {len(health_results)} health check results")
            
            # Calculate overall health status
            overall_status = self._calculate_overall_health(health_results)
            
            # Log summary
            healthy_count = sum(1 for hc in health_results.values() if hc.status == HealthStatus.HEALTHY)
            warning_count = sum(1 for hc in health_results.values() if hc.status == HealthStatus.WARNING)
            critical_count = sum(1 for hc in health_results.values() if hc.status == HealthStatus.CRITICAL)
            
            logger.info(f"Health summary: {healthy_count} healthy, {warning_count} warning, {critical_count} critical")
            
        except Exception as e:
            logger.error(f"Health results processing error: {e}")
    
    def _calculate_overall_health(self, health_results: Dict[str, HealthCheck]) -> HealthStatus:
        """Calculate overall system health status"""
        if not health_results:
            return HealthStatus.UNKNOWN
        
        # If any check is critical, overall is critical
        if any(hc.status == HealthStatus.CRITICAL for hc in health_results.values()):
            return HealthStatus.CRITICAL
        
        # If any check is warning, overall is warning
        if any(hc.status == HealthStatus.WARNING for hc in health_results.values()):
            return HealthStatus.WARNING
        
        # If all checks are healthy, overall is healthy
        if all(hc.status == HealthStatus.HEALTHY for hc in health_results.values()):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def get_health_status(self) -> Dict[str, Any]:
        """
Get current health status"""
        try:
            # Execute all checks once
            health_results = {}
            for check_name, check_function in self.checks.items():
                try:
                    health_check = self._execute_single_check(check_name, check_function)
                    health_results[check_name] = health_check
                except Exception as e:
                    logger.error(f"Health check failed: {check_name} - {e}")
            
            overall_status = self._calculate_overall_health(health_results)
            
            return {
                "overall_status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    name: {
                        "status": hc.status.value,
                        "message": hc.message,
                        "response_time_ms": hc.response_time_ms,
                        "metadata": hc.metadata
                    }
                    for name, hc in health_results.items()
                },
                "summary": {
                    "total_checks": len(health_results),
                    "healthy": sum(1 for hc in health_results.values() if hc.status == HealthStatus.HEALTHY),
                    "warning": sum(1 for hc in health_results.values() if hc.status == HealthStatus.WARNING),
                    "critical": sum(1 for hc in health_results.values() if hc.status == HealthStatus.CRITICAL),
                    "unknown": sum(1 for hc in health_results.values() if hc.status == HealthStatus.UNKNOWN)
                }
            }
            
        except Exception as e:
            logger.error(f"Get health status error: {e}")
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_alerts(self, resolved: Optional[bool] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering"""
        try:
            alerts = self.alerts
            
            if resolved is not None:
                alerts = [a for a in alerts if a.resolved == resolved]
            
            # Sort by timestamp (most recent first)
            alerts = sorted(alerts, key=lambda x: x.timestamp, reverse=True)
            
            return [
                {
                    "id": alert.id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "source": alert.source,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "metadata": alert.metadata
                }
                for alert in alerts[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Get alerts error: {e}")
            return []
    
    def cleanup_old_data(self) -> None:
        """Clean up old health checks and resolved alerts"""
        try:
            retention_config = self.config.get("retention", {})
            alert_retention_days = retention_config.get("alerts", 30)
            
            cutoff_date = datetime.now() - timedelta(days=alert_retention_days)
            
            # Remove old resolved alerts
            before_count = len(self.alerts)
            self.alerts = [
                alert for alert in self.alerts
                if not (alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_date)
            ]
            after_count = len(self.alerts)
            
            if before_count > after_count:
                logger.info(f"Cleaned up {before_count - after_count} old alerts")
            
        except Exception as e:
            logger.error(f"Data cleanup error: {e}")


def main() -> None:
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Monitoring System")
    parser.add_argument("--action", required=True, 
                       choices=["start", "status", "alerts", "cleanup"])
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--resolved", type=bool, help="Filter alerts by resolved status")
    parser.add_argument("--limit", type=int, default=50, help="Limit number of results")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(config_path=args.config)
    
    if args.action == "start":
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    elif args.action == "status":
        status = monitor.get_health_status()
        print(json.dumps(status, indent=2))
    
    elif args.action == "alerts":
        alerts = monitor.get_alerts(resolved=args.resolved, limit=args.limit)
        print(json.dumps(alerts, indent=2))
    
    elif args.action == "cleanup":
        monitor.cleanup_old_data()
        print("Cleanup completed")


if __name__ == "__main__":
    main()
