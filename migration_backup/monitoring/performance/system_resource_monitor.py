"""
⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️

System Resource Monitor - Enterprise Performance Monitoring
Advanced system resource monitoring for Creator Economy infrastructure

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import psutil
import docker
import subprocess
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import threading
from prometheus_client import Gauge, Counter, Histogram
import kubernetes
from kubernetes import client, config
import aiohttp
import os
import platform

logger = logging.getLogger(__name__)

@dataclass
class SystemResourceMetrics:
    """System resource metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    cpu_cores: int
    cpu_frequency: Dict[str, float]
    memory_total: int
    memory_used: int
    memory_percent: float
    memory_available: int
    disk_total: int
    disk_used: int
    disk_percent: float
    disk_io_read: int
    disk_io_write: int
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    load_average: List[float]
    processes_running: int
    processes_total: int
    open_file_descriptors: int
    temperature: Optional[float] = None

@dataclass
class ContainerMetrics:
    """Container resource metrics"""
    container_id: str
    container_name: str
    image: str
    cpu_percent: float
    memory_usage: int
    memory_limit: int
    memory_percent: float
    network_rx_bytes: int
    network_tx_bytes: int
    block_read_bytes: int
    block_write_bytes: int
    pids: int
    status: str
    created: datetime

@dataclass
class KubernetesNodeMetrics:
    """Kubernetes node metrics"""
    node_name: str
    cpu_capacity: str
    cpu_allocatable: str
    cpu_usage: float
    memory_capacity: str
    memory_allocatable: str
    memory_usage: float
    pods_capacity: int
    pods_running: int
    node_status: str
    conditions: List[Dict[str, Any]]

class SystemResourceMonitor:
    """
    Enterprise-grade system resource monitoring
    Tracks CPU, memory, disk, network, containers, and Kubernetes metrics
    """
    
    def __init__(self, 
                 collection_interval: int = 5,
                 enable_kubernetes: bool = True,
                 enable_docker: bool = True,
                 enable_advanced_metrics: bool = True):
        """
        Initialize system resource monitor
        
        Args:
            collection_interval: Metrics collection interval in seconds
            enable_kubernetes: Enable Kubernetes monitoring
            enable_docker: Enable Docker container monitoring
            enable_advanced_metrics: Enable advanced system metrics
        """
        self.collection_interval = collection_interval
        self.enable_kubernetes = enable_kubernetes
        self.enable_docker = enable_docker
        self.enable_advanced_metrics = enable_advanced_metrics
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=1000)
        self.container_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.node_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_task = None
        
        # Docker client
        self.docker_client = None
        if self.enable_docker:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                logger.warning(f"Docker not available: {e}")
                self.enable_docker = False
        
        # Kubernetes client
        self.k8s_v1 = None
        self.k8s_metrics = None
        if self.enable_kubernetes:
            try:
                config.load_incluster_config()
                self.k8s_v1 = client.CoreV1Api()
                self.k8s_metrics = client.CustomObjectsApi()
            except:
                try:
                    config.load_kube_config()
                    self.k8s_v1 = client.CoreV1Api()
                    self.k8s_metrics = client.CustomObjectsApi()
                except Exception as e:
                    logger.warning(f"Kubernetes not available: {e}")
                    self.enable_kubernetes = False
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.cpu_usage_gauge = Gauge('system_cpu_usage_percent', 
                                   'System CPU usage percentage')
        self.memory_usage_gauge = Gauge('system_memory_usage_percent', 
                                      'System memory usage percentage')
        self.disk_usage_gauge = Gauge('system_disk_usage_percent', 
                                    'System disk usage percentage')
        self.network_bytes_counter = Counter('system_network_bytes_total', 
                                           'System network bytes transferred',
                                           ['direction'])
        self.load_average_gauge = Gauge('system_load_average', 
                                      'System load average',
                                      ['interval'])
        self.container_cpu_gauge = Gauge('container_cpu_usage_percent',
                                       'Container CPU usage percentage',
                                       ['container_name', 'image'])
        self.container_memory_gauge = Gauge('container_memory_usage_bytes',
                                          'Container memory usage in bytes',
                                          ['container_name', 'image'])
        self.node_cpu_gauge = Gauge('kubernetes_node_cpu_usage_percent',
                                  'Kubernetes node CPU usage percentage',
                                  ['node_name'])
        self.node_memory_gauge = Gauge('kubernetes_node_memory_usage_percent',
                                     'Kubernetes node memory usage percentage',
                                     ['node_name'])
    
    def collect_system_metrics(self) -> SystemResourceMetrics:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Load average (Unix only)
            load_avg = []
            if hasattr(os, 'getloadavg'):
                load_avg = list(os.getloadavg())
            
            # Process metrics
            processes = list(psutil.process_iter(['pid', 'status']))
            running_processes = len([p for p in processes if p.info['status'] == 'running'])
            
            # File descriptors (Unix only)
            open_fds = 0
            try:
                open_fds = len(psutil.Process().open_files())
            except:
                pass
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get CPU temperature if available
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            temperature = entries[0].current
                            break
            except:
                pass
            
            metrics = SystemResourceMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                cpu_cores=cpu_count,
                cpu_frequency=cpu_freq,
                memory_total=memory.total,
                memory_used=memory.used,
                memory_percent=memory.percent,
                memory_available=memory.available,
                disk_total=disk.total,
                disk_used=disk.used,
                disk_percent=disk.percent,
                disk_io_read=disk_io.read_bytes if disk_io else 0,
                disk_io_write=disk_io.write_bytes if disk_io else 0,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                network_packets_sent=network.packets_sent,
                network_packets_recv=network.packets_recv,
                load_average=load_avg,
                processes_running=running_processes,
                processes_total=len(processes),
                open_file_descriptors=open_fds,
                temperature=temperature
            )
            
            # Update Prometheus metrics
            self.cpu_usage_gauge.set(cpu_percent)
            self.memory_usage_gauge.set(memory.percent)
            self.disk_usage_gauge.set(disk.percent)
            self.network_bytes_counter.labels('sent').inc(network.bytes_sent)
            self.network_bytes_counter.labels('received').inc(network.bytes_recv)
            
            for i, load in enumerate(load_avg):
                self.load_average_gauge.labels(interval=f'{[1,5,15][i]}min').set(load)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise
    
    def collect_container_metrics(self) -> List[ContainerMetrics]:
        """Collect Docker container metrics"""
        if not self.enable_docker or not self.docker_client:
            return []
        
        container_metrics = []
        
        try:
            for container in self.docker_client.containers.list():
                stats = container.stats(stream=False)
                
                # Calculate CPU percentage
                cpu_percent = 0.0
                if 'cpu_stats' in stats and 'precpu_stats' in stats:
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * \
                                     len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
                
                # Memory metrics
                memory_usage = stats['memory_stats'].get('usage', 0)
                memory_limit = stats['memory_stats'].get('limit', 0)
                memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0
                
                # Network metrics
                network_rx = 0
                network_tx = 0
                if 'networks' in stats:
                    for interface in stats['networks'].values():
                        network_rx += interface.get('rx_bytes', 0)
                        network_tx += interface.get('tx_bytes', 0)
                
                # Block I/O metrics
                block_read = 0
                block_write = 0
                if 'blkio_stats' in stats and 'io_service_bytes_recursive' in stats['blkio_stats']:
                    for io_stat in stats['blkio_stats']['io_service_bytes_recursive']:
                        if io_stat['op'] == 'Read':
                            block_read += io_stat['value']
                        elif io_stat['op'] == 'Write':
                            block_write += io_stat['value']
                
                metrics = ContainerMetrics(
                    container_id=container.id[:12],
                    container_name=container.name,
                    image=container.image.tags[0] if container.image.tags else 'unknown',
                    cpu_percent=cpu_percent,
                    memory_usage=memory_usage,
                    memory_limit=memory_limit,
                    memory_percent=memory_percent,
                    network_rx_bytes=network_rx,
                    network_tx_bytes=network_tx,
                    block_read_bytes=block_read,
                    block_write_bytes=block_write,
                    pids=stats.get('pids_stats', {}).get('current', 0),
                    status=container.status,
                    created=datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
                )
                
                container_metrics.append(metrics)
                
                # Update Prometheus metrics
                self.container_cpu_gauge.labels(
                    container_name=container.name,
                    image=metrics.image
                ).set(cpu_percent)
                
                self.container_memory_gauge.labels(
                    container_name=container.name,
                    image=metrics.image
                ).set(memory_usage)
                
        except Exception as e:
            logger.error(f"Error collecting container metrics: {e}")
        
        return container_metrics
    
    def collect_kubernetes_metrics(self) -> List[KubernetesNodeMetrics]:
        """Collect Kubernetes node metrics"""
        if not self.enable_kubernetes or not self.k8s_v1:
            return []
        
        node_metrics = []
        
        try:
            # Get nodes
            nodes = self.k8s_v1.list_node()
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                # Node capacity and allocatable resources
                capacity = node.status.capacity
                allocatable = node.status.allocatable
                
                # Node conditions
                conditions = []
                if node.status.conditions:
                    conditions = [
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'reason': condition.reason,
                            'message': condition.message
                        }
                        for condition in node.status.conditions
                    ]
                
                # Get node metrics from metrics server
                cpu_usage = 0.0
                memory_usage = 0.0
                
                try:
                    metrics_response = self.k8s_metrics.get_cluster_custom_object(
                        group="metrics.k8s.io",
                        version="v1beta1",
                        plural="nodes",
                        name=node_name
                    )
                    
                    if 'usage' in metrics_response:
                        cpu_usage_str = metrics_response['usage'].get('cpu', '0')
                        memory_usage_str = metrics_response['usage'].get('memory', '0')
                        
                        # Parse CPU usage (e.g., "100m" = 0.1 cores)
                        if cpu_usage_str.endswith('m'):
                            cpu_usage = float(cpu_usage_str[:-1]) / 1000
                        elif cpu_usage_str.endswith('n'):
                            cpu_usage = float(cpu_usage_str[:-1]) / 1000000000
                        else:
                            cpu_usage = float(cpu_usage_str)
                        
                        # Parse memory usage (e.g., "1024Ki" = 1024*1024 bytes)
                        if memory_usage_str.endswith('Ki'):
                            memory_usage = float(memory_usage_str[:-2]) * 1024
                        elif memory_usage_str.endswith('Mi'):
                            memory_usage = float(memory_usage_str[:-2]) * 1024 * 1024
                        elif memory_usage_str.endswith('Gi'):
                            memory_usage = float(memory_usage_str[:-2]) * 1024 * 1024 * 1024
                        else:
                            memory_usage = float(memory_usage_str)
                        
                except Exception as e:
                    logger.debug(f"Could not get metrics for node {node_name}: {e}")
                
                # Count running pods
                pods = self.k8s_v1.list_pod_for_all_namespaces(
                    field_selector=f"spec.nodeName={node_name},status.phase=Running"
                )
                pods_running = len(pods.items)
                
                # Get pod capacity
                pods_capacity = int(allocatable.get('pods', '0'))
                
                metrics = KubernetesNodeMetrics(
                    node_name=node_name,
                    cpu_capacity=capacity.get('cpu', '0'),
                    cpu_allocatable=allocatable.get('cpu', '0'),
                    cpu_usage=cpu_usage,
                    memory_capacity=capacity.get('memory', '0'),
                    memory_allocatable=allocatable.get('memory', '0'),
                    memory_usage=memory_usage,
                    pods_capacity=pods_capacity,
                    pods_running=pods_running,
                    node_status=node.status.phase or 'Unknown',
                    conditions=conditions
                )
                
                node_metrics.append(metrics)
                
                # Update Prometheus metrics
                self.node_cpu_gauge.labels(node_name=node_name).set(cpu_usage)
                self.node_memory_gauge.labels(node_name=node_name).set(memory_usage)
                
        except Exception as e:
            logger.error(f"Error collecting Kubernetes metrics: {e}")
        
        return node_metrics
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("System resource monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("System resource monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self.collect_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # Collect container metrics
                if self.enable_docker:
                    container_metrics = self.collect_container_metrics()
                    for metrics in container_metrics:
                        self.container_metrics[metrics.container_name].append(metrics)
                
                # Collect Kubernetes metrics
                if self.enable_kubernetes:
                    node_metrics = self.collect_kubernetes_metrics()
                    for metrics in node_metrics:
                        self.node_metrics[metrics.node_name].append(metrics)
                
                # Check for resource contention and alerts
                await self._check_resource_alerts(system_metrics)
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _check_resource_alerts(self, metrics: SystemResourceMetrics):
        """Check for resource alerts and contention"""
        alerts = []
        
        # CPU alerts
        if metrics.cpu_percent > 90:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'critical',
                'message': f'CPU usage at {metrics.cpu_percent:.1f}%',
                'threshold': 90,
                'value': metrics.cpu_percent
            })
        elif metrics.cpu_percent > 80:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f'CPU usage at {metrics.cpu_percent:.1f}%',
                'threshold': 80,
                'value': metrics.cpu_percent
            })
        
        # Memory alerts
        if metrics.memory_percent > 95:
            alerts.append({
                'type': 'high_memory',
                'severity': 'critical',
                'message': f'Memory usage at {metrics.memory_percent:.1f}%',
                'threshold': 95,
                'value': metrics.memory_percent
            })
        elif metrics.memory_percent > 85:
            alerts.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f'Memory usage at {metrics.memory_percent:.1f}%',
                'threshold': 85,
                'value': metrics.memory_percent
            })
        
        # Disk alerts
        if metrics.disk_percent > 95:
            alerts.append({
                'type': 'high_disk',
                'severity': 'critical',
                'message': f'Disk usage at {metrics.disk_percent:.1f}%',
                'threshold': 95,
                'value': metrics.disk_percent
            })
        elif metrics.disk_percent > 90:
            alerts.append({
                'type': 'high_disk',
                'severity': 'warning',
                'message': f'Disk usage at {metrics.disk_percent:.1f}%',
                'threshold': 90,
                'value': metrics.disk_percent
            })
        
        # Load average alerts (Unix only)
        if metrics.load_average and len(metrics.load_average) >= 1:
            if metrics.load_average[0] > metrics.cpu_cores * 2:
                alerts.append({
                    'type': 'high_load',
                    'severity': 'critical',
                    'message': f'Load average {metrics.load_average[0]:.2f} exceeds 2x CPU cores',
                    'threshold': metrics.cpu_cores * 2,
                    'value': metrics.load_average[0]
                })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Resource alert: {alert}")
    
    def get_metrics_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        disk_values = [m.disk_percent for m in recent_metrics]
        
        return {
            'time_window_minutes': minutes,
            'sample_count': len(recent_metrics),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values),
                'current': cpu_values[-1] if cpu_values else 0
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values),
                'current': memory_values[-1] if memory_values else 0
            },
            'disk': {
                'average': sum(disk_values) / len(disk_values),
                'min': min(disk_values),
                'max': max(disk_values),
                'current': disk_values[-1] if disk_values else 0
            },
            'latest_metrics': asdict(recent_metrics[-1]) if recent_metrics else None
        }
    
    def get_resource_recommendations(self) -> List[Dict[str, Any]]:
        """Get resource optimization recommendations"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        # Analyze recent metrics (last hour)
        recent_metrics = list(self.metrics_history)[-720:]  # 1 hour at 5s intervals
        
        if len(recent_metrics) < 10:
            return recommendations
        
        # CPU analysis
        cpu_values = [m.cpu_percent for m in recent_metrics]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        
        if avg_cpu < 20 and max_cpu < 50:
            recommendations.append({
                'type': 'cpu_optimization',
                'priority': 'medium',
                'description': 'CPU utilization is consistently low, consider downsizing instances',
                'current_avg': avg_cpu,
                'potential_savings': '20-40%'
            })
        elif avg_cpu > 80:
            recommendations.append({
                'type': 'cpu_scaling',
                'priority': 'high',
                'description': 'CPU utilization is high, consider scaling up or optimizing workloads',
                'current_avg': avg_cpu,
                'recommendation': 'Scale up CPU or optimize code'
            })
        
        # Memory analysis
        memory_values = [m.memory_percent for m in recent_metrics]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        
        if avg_memory < 30 and max_memory < 60:
            recommendations.append({
                'type': 'memory_optimization',
                'priority': 'medium',
                'description': 'Memory utilization is low, consider reducing memory allocation',
                'current_avg': avg_memory,
                'potential_savings': '15-30%'
            })
        elif avg_memory > 85:
            recommendations.append({
                'type': 'memory_scaling',
                'priority': 'high',
                'description': 'Memory utilization is high, risk of OOM errors',
                'current_avg': avg_memory,
                'recommendation': 'Increase memory or optimize memory usage'
            })
        
        return recommendations