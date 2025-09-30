# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

import logging
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import statistics
import psutil
import platform
import threading
from kubernetes import client, config
import redis
import sqlite3

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/ainflue/performance_monitoring.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str]
    source: str  # system, application, kubernetes, etc.

@dataclass
class SystemResource:
    """System resource utilization"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes_sent: int
    network_io_bytes_recv: int
    load_average: Tuple[float, float, float]
    open_files: int
    process_count: int

@dataclass
class ApplicationMetrics:
    """Application-specific performance metrics"""
    request_rate: float
    response_time_avg: float
    response_time_p95: float
    error_rate: float
    active_connections: int
    queue_size: int
    cache_hit_rate: float
    database_connections: int

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    resolved: bool
    resolution_time: Optional[datetime]

class SystemMonitor:
    """Monitors system-level performance metrics"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.monitoring = False
        self.metrics_history = deque(maxlen=1000)
    
    async def collect_system_metrics(self) -> SystemResource:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # Load average
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Open files (approximate)
            try:
                open_files = len(self.process.open_files())
            except:
                open_files = 0
            
            return SystemResource(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io_bytes_sent=net_io.bytes_sent,
                network_io_bytes_recv=net_io.bytes_recv,
                load_average=load_avg,
                open_files=open_files,
                process_count=process_count
            )
        
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def get_cpu_breakdown(self) -> Dict[str, float]:
        """Get detailed CPU usage breakdown"""
        try:
            cpu_times = psutil.cpu_times_percent(interval=1)
            return {
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle,
                'iowait': getattr(cpu_times, 'iowait', 0),
                'irq': getattr(cpu_times, 'irq', 0),
                'softirq': getattr(cpu_times, 'softirq', 0)
            }
        except Exception as e:
            logger.error(f"Error getting CPU breakdown: {e}")
            return {}
    
    def get_memory_breakdown(self) -> Dict[str, int]:
        """Get detailed memory usage breakdown"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total_mb': memory.total // (1024 * 1024),
                'available_mb': memory.available // (1024 * 1024),
                'used_mb': memory.used // (1024 * 1024),
                'free_mb': memory.free // (1024 * 1024),
                'cached_mb': getattr(memory, 'cached', 0) // (1024 * 1024),
                'buffers_mb': getattr(memory, 'buffers', 0) // (1024 * 1024),
                'swap_total_mb': swap.total // (1024 * 1024),
                'swap_used_mb': swap.used // (1024 * 1024),
                'swap_free_mb': swap.free // (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting memory breakdown: {e}")
            return {}
    
    def get_disk_breakdown(self) -> List[Dict[str, Any]]:
        """Get disk usage for all mounted filesystems"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': usage.total // (1024**3),
                        'used_gb': usage.used // (1024**3),
                        'free_gb': usage.free // (1024**3),
                        'percent': (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            logger.error(f"Error getting disk breakdown: {e}")
            return []
    
    def get_network_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get network interface statistics"""
        try:
            net_stats = {}
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, stats in net_io.items():
                net_stats[interface] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errin': stats.errin,
                    'errout': stats.errout,
                    'dropin': stats.dropin,
                    'dropout': stats.dropout
                }
            
            return net_stats
        except Exception as e:
            logger.error(f"Error getting network breakdown: {e}")
            return {}

class ApplicationMonitor:
    """Monitors application-specific performance metrics"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_count = 0
        self.request_count = 0
        self.connection_count = 0
        self.last_reset = datetime.utcnow()
    
    def record_request(self, response_time: float, status_code: int):
        """Record HTTP request metrics"""
        self.request_times.append(response_time)
        self.request_count += 1
        
        if status_code >= 400:
            self.error_count += 1
    
    def record_connection(self, is_new: bool = True):
        """Record connection metrics"""
        if is_new:
            self.connection_count += 1
        else:
            self.connection_count = max(0, self.connection_count - 1)
    
    async def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application performance metrics"""
        try:
            current_time = datetime.utcnow()
            time_window = (current_time - self.last_reset).total_seconds()
            
            # Calculate request rate (requests per second)
            request_rate = self.request_count / max(time_window, 1)
            
            # Calculate response time metrics
            if self.request_times:
                response_time_avg = statistics.mean(self.request_times)
                response_time_p95 = np.percentile(list(self.request_times), 95)
            else:
                response_time_avg = 0
                response_time_p95 = 0
            
            # Calculate error rate
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            # Get additional metrics
            queue_size = await self._get_queue_size()
            cache_hit_rate = await self._get_cache_hit_rate()
            db_connections = await self._get_database_connections()
            
            return ApplicationMetrics(
                request_rate=request_rate,
                response_time_avg=response_time_avg,
                response_time_p95=response_time_p95,
                error_rate=error_rate,
                active_connections=self.connection_count,
                queue_size=queue_size,
                cache_hit_rate=cache_hit_rate,
                database_connections=db_connections
            )
        
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    async def _get_queue_size(self) -> int:
        """Get current queue size from Redis or message broker"""
        try:
            # Example Redis connection
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            queue_size = redis_client.llen('task_queue')
            return queue_size
        except:
            return 0
    
    async def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate from Redis"""
        try:
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            info = redis_client.info('stats')
            
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            if total > 0:
                return (hits / total) * 100
            return 0
        except:
            return 0
    
    async def _get_database_connections(self) -> int:
        """Get active database connections"""
        try:
            # This would be implemented based on your database
            # Example for PostgreSQL using psycopg2
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                database="ainflue",
                user="postgres",
                password="password"
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity;")
                count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except:
            return 0
    
    def reset_counters(self):
        """Reset counters for next measurement period"""
        self.request_count = 0
        self.error_count = 0
        self.last_reset = datetime.utcnow()

class KubernetesMonitor:
    """Monitors Kubernetes cluster performance"""
    
    def __init__(self):
        self.v1 = None
        self.metrics_v1beta1 = None
        self._initialize_k8s_client()
    
    def _initialize_k8s_client(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except Exception as e:
                logger.warning(f"Failed to load Kubernetes config: {e}")
                return
        
        self.v1 = client.CoreV1Api()
        
        try:
            self.metrics_v1beta1 = client.CustomObjectsApi()
        except Exception as e:
            logger.warning(f"Metrics API not available: {e}")
    
    async def collect_pod_metrics(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Collect pod performance metrics"""
        if not self.v1:
            return []
        
        try:
            pods = self.v1.list_namespaced_pod(namespace) if namespace else self.v1.list_pod_for_all_namespaces()
            
            pod_metrics = []
            for pod in pods.items:
                # Get basic pod info
                pod_info = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'phase': pod.status.phase,
                    'restart_count': 0,
                    'cpu_requests': 0,
                    'memory_requests': 0,
                    'cpu_limits': 0,
                    'memory_limits': 0
                }
                
                # Calculate restart count
                if pod.status.container_statuses:
                    pod_info['restart_count'] = sum(
                        container.restart_count for container in pod.status.container_statuses
                    )
                
                # Get resource requests and limits
                if pod.spec.containers:
                    for container in pod.spec.containers:
                        if container.resources:
                            if container.resources.requests:
                                cpu_req = container.resources.requests.get('cpu', '0')
                                mem_req = container.resources.requests.get('memory', '0')
                                pod_info['cpu_requests'] += self._parse_cpu(cpu_req)
                                pod_info['memory_requests'] += self._parse_memory(mem_req)
                            
                            if container.resources.limits:
                                cpu_lim = container.resources.limits.get('cpu', '0')
                                mem_lim = container.resources.limits.get('memory', '0')
                                pod_info['cpu_limits'] += self._parse_cpu(cpu_lim)
                                pod_info['memory_limits'] += self._parse_memory(mem_lim)
                
                pod_metrics.append(pod_info)
            
            return pod_metrics
        
        except Exception as e:
            logger.error(f"Error collecting pod metrics: {e}")
            return []
    
    async def collect_node_metrics(self) -> List[Dict[str, Any]]:
        """Collect node performance metrics"""
        if not self.v1:
            return []
        
        try:
            nodes = self.v1.list_node()
            
            node_metrics = []
            for node in nodes.items:
                node_info = {
                    'name': node.metadata.name,
                    'status': 'Unknown',
                    'cpu_capacity': 0,
                    'memory_capacity': 0,
                    'cpu_allocatable': 0,
                    'memory_allocatable': 0,
                    'pod_count': 0
                }
                
                # Get node status
                if node.status.conditions:
                    for condition in node.status.conditions:
                        if condition.type == 'Ready':
                            node_info['status'] = 'Ready' if condition.status == 'True' else 'NotReady'
                
                # Get resource capacity and allocatable
                if node.status.capacity:
                    node_info['cpu_capacity'] = self._parse_cpu(node.status.capacity.get('cpu', '0'))
                    node_info['memory_capacity'] = self._parse_memory(node.status.capacity.get('memory', '0'))
                
                if node.status.allocatable:
                    node_info['cpu_allocatable'] = self._parse_cpu(node.status.allocatable.get('cpu', '0'))
                    node_info['memory_allocatable'] = self._parse_memory(node.status.allocatable.get('memory', '0'))
                
                # Count pods on this node
                pods = self.v1.list_pod_for_all_namespaces(field_selector=f'spec.nodeName={node.metadata.name}')
                node_info['pod_count'] = len(pods.items)
                
                node_metrics.append(node_info)
            
            return node_metrics
        
        except Exception as e:
            logger.error(f"Error collecting node metrics: {e}")
            return []
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU resource string to cores"""
        if not cpu_str or cpu_str == '0':
            return 0.0
        
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        
        return float(cpu_str)
    
    def _parse_memory(self, memory_str: str) -> int:
        """Parse memory resource string to bytes"""
        if not memory_str or memory_str == '0':
            return 0
        
        units = {
            'Ki': 1024,
            'Mi': 1024**2,
            'Gi': 1024**3,
            'Ti': 1024**4,
            'K': 1000,
            'M': 1000**2,
            'G': 1000**3,
            'T': 1000**4,
        }
        
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return int(float(memory_str[:-len(unit)]) * multiplier)
        
        return int(memory_str)

class PerformanceAlertManager:
    """Manages performance alerts and thresholds"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_percent': {'warning': 70, 'critical': 90},
            'memory_percent': {'warning': 80, 'critical': 95},
            'disk_usage_percent': {'warning': 85, 'critical': 95},
            'response_time_avg': {'warning': 1000, 'critical': 5000},  # ms
            'error_rate': {'warning': 5, 'critical': 10},  # percent
            'queue_size': {'warning': 1000, 'critical': 5000}
        }
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
    
    def set_threshold(self, metric_name: str, warning: float, critical: float):
        """Set alert thresholds for a metric"""
        self.thresholds[metric_name] = {
            'warning': warning,
            'critical': critical
        }
    
    async def check_alerts(self, system_metrics: SystemResource, 
                          app_metrics: ApplicationMetrics) -> List[PerformanceAlert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        current_time = datetime.utcnow()
        
        # Check system metrics
        if system_metrics:
            alerts.extend(self._check_metric_thresholds(
                'cpu_percent', system_metrics.cpu_percent, current_time
            ))
            alerts.extend(self._check_metric_thresholds(
                'memory_percent', system_metrics.memory_percent, current_time
            ))
            alerts.extend(self._check_metric_thresholds(
                'disk_usage_percent', system_metrics.disk_usage_percent, current_time
            ))
        
        # Check application metrics
        if app_metrics:
            alerts.extend(self._check_metric_thresholds(
                'response_time_avg', app_metrics.response_time_avg, current_time
            ))
            alerts.extend(self._check_metric_thresholds(
                'error_rate', app_metrics.error_rate, current_time
            ))
            alerts.extend(self._check_metric_thresholds(
                'queue_size', app_metrics.queue_size, current_time
            ))
        
        # Process new alerts
        for alert in alerts:
            if alert.alert_id not in self.active_alerts:
                self.active_alerts[alert.alert_id] = alert
                self.alert_history.append(alert)
                logger.warning(f"New alert: {alert.message}")
        
        # Check for resolved alerts
        await self._check_resolved_alerts(system_metrics, app_metrics, current_time)
        
        return alerts
    
    def _check_metric_thresholds(self, metric_name: str, value: float, 
                               timestamp: datetime) -> List[PerformanceAlert]:
        """Check single metric against thresholds"""
        alerts = []
        
        if metric_name not in self.thresholds:
            return alerts
        
        thresholds = self.thresholds[metric_name]
        
        if value >= thresholds['critical']:
            alert_id = f"{metric_name}_critical_{int(timestamp.timestamp())}"
            alert = PerformanceAlert(
                alert_id=alert_id,
                metric_name=metric_name,
                current_value=value,
                threshold_value=thresholds['critical'],
                severity='critical',
                message=f"Critical: {metric_name} is {value:.2f}, exceeds critical threshold {thresholds['critical']}",
                timestamp=timestamp,
                resolved=False,
                resolution_time=None
            )
            alerts.append(alert)
        
        elif value >= thresholds['warning']:
            alert_id = f"{metric_name}_warning_{int(timestamp.timestamp())}"
            alert = PerformanceAlert(
                alert_id=alert_id,
                metric_name=metric_name,
                current_value=value,
                threshold_value=thresholds['warning'],
                severity='warning',
                message=f"Warning: {metric_name} is {value:.2f}, exceeds warning threshold {thresholds['warning']}",
                timestamp=timestamp,
                resolved=False,
                resolution_time=None
            )
            alerts.append(alert)
        
        return alerts
    
    async def _check_resolved_alerts(self, system_metrics: SystemResource,
                                   app_metrics: ApplicationMetrics, current_time: datetime):
        """Check if any active alerts should be resolved"""
        current_values = {}
        
        if system_metrics:
            current_values.update({
                'cpu_percent': system_metrics.cpu_percent,
                'memory_percent': system_metrics.memory_percent,
                'disk_usage_percent': system_metrics.disk_usage_percent
            })
        
        if app_metrics:
            current_values.update({
                'response_time_avg': app_metrics.response_time_avg,
                'error_rate': app_metrics.error_rate,
                'queue_size': app_metrics.queue_size
            })
        
        for alert_id, alert in self.active_alerts.items():
            if alert.resolved:
                continue
            
            metric_name = alert.metric_name
            if metric_name in current_values:
                current_value = current_values[metric_name]
                threshold = self.thresholds.get(metric_name, {}).get(alert.severity, 0)
                
                # Alert is resolved if current value is below threshold
                if current_value < threshold:
                    alert.resolved = True
                    alert.resolution_time = current_time
                    logger.info(f"Alert resolved: {alert.message}")
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """Get currently active alerts"""
        active = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        if severity:
            active = [alert for alert in active if alert.severity == severity]
        
        return active
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of alerts by severity"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            'critical': 0,
            'warning': 0,
            'total_active': len(active_alerts),
            'total_resolved_today': 0
        }
        
        for alert in active_alerts:
            summary[alert.severity] = summary.get(alert.severity, 0) + 1
        
        # Count resolved alerts from today
        today = datetime.utcnow().date()
        for alert in self.alert_history:
            if (alert.resolved and alert.resolution_time and 
                alert.resolution_time.date() == today):
                summary['total_resolved_today'] += 1
        
        return summary

class PerformanceMonitoringEngine:
    """Main performance monitoring engine"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.app_monitor = ApplicationMonitor()
        self.k8s_monitor = KubernetesMonitor()
        self.alert_manager = PerformanceAlertManager()
        self.monitoring = False
        self.metrics_storage = deque(maxlen=10000)
        self.collection_interval = 30  # seconds
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        logger.info("Starting Ainflue Performance Monitoring Engine")
        
        monitoring_tasks = [
            self._monitoring_loop(),
            self._alert_checking_loop(),
            self._cleanup_loop()
        ]
        
        await asyncio.gather(*monitoring_tasks)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        logger.info("Stopping performance monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect all metrics
                system_metrics = await self.system_monitor.collect_system_metrics()
                app_metrics = await self.app_monitor.collect_application_metrics()
                pod_metrics = await self.k8s_monitor.collect_pod_metrics()
                node_metrics = await self.k8s_monitor.collect_node_metrics()
                
                # Store metrics
                metrics_snapshot = {
                    'timestamp': datetime.utcnow(),
                    'system': asdict(system_metrics) if system_metrics else None,
                    'application': asdict(app_metrics) if app_metrics else None,
                    'pods': pod_metrics,
                    'nodes': node_metrics
                }
                
                self.metrics_storage.append(metrics_snapshot)
                
                # Log summary
                if system_metrics and app_metrics:
                    logger.info(
                        f"Performance snapshot - CPU: {system_metrics.cpu_percent:.1f}%, "
                        f"Memory: {system_metrics.memory_percent:.1f}%, "
                        f"Response time: {app_metrics.response_time_avg:.1f}ms, "
                        f"Error rate: {app_metrics.error_rate:.1f}%"
                    )
                
                await asyncio.sleep(self.collection_interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _alert_checking_loop(self):
        """Alert checking loop"""
        while self.monitoring:
            try:
                # Get latest metrics
                if self.metrics_storage:
                    latest = self.metrics_storage[-1]
                    system_metrics = SystemResource(**latest['system']) if latest['system'] else None
                    app_metrics = ApplicationMetrics(**latest['application']) if latest['application'] else None
                    
                    # Check for alerts
                    alerts = await self.alert_manager.check_alerts(system_metrics, app_metrics)
                    
                    # Handle new alerts (send notifications, etc.)
                    for alert in alerts:
                        await self._handle_new_alert(alert)
                
                await asyncio.sleep(60)  # Check alerts every minute
            
            except Exception as e:
                logger.error(f"Error in alert checking loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Cleanup old data"""
        while self.monitoring:
            try:
                # Reset application counters periodically
                self.app_monitor.reset_counters()
                
                # Clean up resolved alerts older than 24 hours
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)
                
                expired_alerts = [
                    alert_id for alert_id, alert in self.alert_manager.active_alerts.items()
                    if alert.resolved and alert.resolution_time and alert.resolution_time < cutoff_time
                ]
                
                for alert_id in expired_alerts:
                    del self.alert_manager.active_alerts[alert_id]
                
                if expired_alerts:
                    logger.info(f"Cleaned up {len(expired_alerts)} expired alerts")
                
                await asyncio.sleep(3600)  # Cleanup every hour
            
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _handle_new_alert(self, alert: PerformanceAlert):
        """Handle new performance alert"""
        # This would integrate with notification systems
        logger.warning(f"Performance Alert [{alert.severity.upper()}]: {alert.message}")
        
        # Could send to:
        # - Email notifications
        # - Slack/Teams
        # - PagerDuty
        # - Custom webhooks
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        if not self.metrics_storage:
            return {}
        
        latest = self.metrics_storage[-1]
        
        # Get system details
        system_details = {}
        if latest['system']:
            system_details = {
                **latest['system'],
                'cpu_breakdown': self.system_monitor.get_cpu_breakdown(),
                'memory_breakdown': self.system_monitor.get_memory_breakdown(),
                'disk_breakdown': self.system_monitor.get_disk_breakdown(),
                'network_breakdown': self.system_monitor.get_network_breakdown()
            }
        
        # Get alert summary
        alert_summary = self.alert_manager.get_alert_summary()
        
        # Get recent performance trends
        trends = self._calculate_trends()
        
        return {
            'timestamp': latest['timestamp'].isoformat(),
            'system_metrics': system_details,
            'application_metrics': latest['application'],
            'kubernetes_metrics': {
                'pods': latest['pods'],
                'nodes': latest['nodes']
            },
            'alerts': {
                'summary': alert_summary,
                'active_alerts': [asdict(alert) for alert in self.alert_manager.get_active_alerts()]
            },
            'trends': trends,
            'system_info': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total // (1024**3)
            }
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(self.metrics_storage) < 2:
            return {}
        
        # Get metrics from last hour
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        recent_metrics = [
            m for m in self.metrics_storage
            if m['timestamp'] > hour_ago
        ]
        
        if len(recent_metrics) < 2:
            return {}
        
        trends = {}
        
        # Calculate CPU trend
        cpu_values = [m['system']['cpu_percent'] for m in recent_metrics if m['system']]
        if len(cpu_values) >= 2:
            trends['cpu_trend'] = 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing'
            trends['cpu_avg_last_hour'] = statistics.mean(cpu_values)
        
        # Calculate memory trend
        memory_values = [m['system']['memory_percent'] for m in recent_metrics if m['system']]
        if len(memory_values) >= 2:
            trends['memory_trend'] = 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing'
            trends['memory_avg_last_hour'] = statistics.mean(memory_values)
        
        # Calculate response time trend
        response_time_values = [m['application']['response_time_avg'] for m in recent_metrics if m['application']]
        if len(response_time_values) >= 2:
            trends['response_time_trend'] = 'increasing' if response_time_values[-1] > response_time_values[0] else 'decreasing'
            trends['response_time_avg_last_hour'] = statistics.mean(response_time_values)
        
        return trends
    
    async def export_metrics(self, format: str = 'json', hours: int = 24) -> str:
        """Export metrics data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        export_data = [
            m for m in self.metrics_storage
            if m['timestamp'] > cutoff_time
        ]
        
        if format == 'json':
            return json.dumps(export_data, indent=2, default=str)
        elif format == 'csv':
            # Convert to CSV format (simplified)
            import csv
            import io
            
            output = io.StringIO()
            if export_data:
                fieldnames = ['timestamp', 'cpu_percent', 'memory_percent', 'response_time_avg', 'error_rate']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in export_data:
                    row = {
                        'timestamp': record['timestamp'].isoformat(),
                        'cpu_percent': record['system']['cpu_percent'] if record['system'] else '',
                        'memory_percent': record['system']['memory_percent'] if record['system'] else '',
                        'response_time_avg': record['application']['response_time_avg'] if record['application'] else '',
                        'error_rate': record['application']['error_rate'] if record['application'] else ''
                    }
                    writer.writerow(row)
            
            return output.getvalue()
        
        return ""

async def main():
    """Main function for testing"""
    engine = PerformanceMonitoringEngine()
    
    # Set custom thresholds
    engine.alert_manager.set_threshold('cpu_percent', 60, 85)
    engine.alert_manager.set_threshold('memory_percent', 70, 90)
    
    try:
        # Start monitoring (run for a short time for testing)
        monitoring_task = asyncio.create_task(engine.start_monitoring())
        
        # Wait a bit to collect some data
        await asyncio.sleep(30)
        
        # Get dashboard data
        dashboard = await engine.get_performance_dashboard()
        print(json.dumps(dashboard, indent=2, default=str))
        
        # Stop monitoring
        engine.stop_monitoring()
        
    except KeyboardInterrupt:
        engine.stop_monitoring()
        logger.info("Performance monitoring stopped")

if __name__ == "__main__":
    asyncio.run(main())