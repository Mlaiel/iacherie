#!/usr/bin/env python3
"""
📈 Resource Monitoring Service - Enterprise Infrastructure Service
=================================================================

Comprehensive resource monitoring service for enterprise infrastructure.
Provides real-time monitoring of CPU, memory, disk, network, and application resources.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CONTAINER = "container"
    CUSTOM = "custom"


class AlertLevel(Enum):
    """Alert level enumeration."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ResourceMetric:
    """Resource metric data structure."""
    resource_type: ResourceType
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class ResourceAlert:
    """Resource alert data structure."""
    id: str
    resource_type: ResourceType
    metric_name: str
    level: AlertLevel
    current_value: float
    threshold: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class ResourceMonitoringService:
    """
    📈 Enterprise Resource Monitoring Service
    
    Provides comprehensive monitoring of system resources including CPU, memory,
    disk, network, and custom application metrics with alerting capabilities.
    """
    
    def __init__(self, monitoring_interval: int = 30):
        """Initialize the resource monitoring service."""
        self.monitoring_interval = monitoring_interval
        self.metrics_history: Dict[str, List[ResourceMetric]] = {}
        self.current_metrics: Dict[str, ResourceMetric] = {}
        self.alerts: Dict[str, ResourceAlert] = {}
        self.alert_callbacks: List[Callable] = []
        self.custom_collectors: Dict[str, Callable] = {}
        
        # Configure default thresholds
        self.thresholds = {
            'cpu_usage': {'warning': 80.0, 'critical': 95.0},
            'memory_usage': {'warning': 85.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'disk_io_wait': {'warning': 20.0, 'critical': 50.0},
            'network_errors': {'warning': 1.0, 'critical': 5.0}
        }
        
        # Monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("📈 Resource Monitoring Service initialized")
    
    async def start(self):
        """Start the resource monitoring service."""
        logger.info("🚀 Starting Resource Monitoring Service")
        
        # Start monitoring loops
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("✅ Resource Monitoring Service started")
    
    async def stop(self):
        """Stop the resource monitoring service."""
        logger.info("🛑 Stopping Resource Monitoring Service")
        
        # Cancel tasks
        tasks = [self.monitoring_task, self.cleanup_task]
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("✅ Resource Monitoring Service stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await self._collect_all_metrics()
                await self._check_thresholds()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Monitoring loop error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_all_metrics(self):
        """Collect all resource metrics."""
        await asyncio.gather(
            self._collect_cpu_metrics(),
            self._collect_memory_metrics(),
            self._collect_disk_metrics(),
            self._collect_network_metrics(),
            self._collect_process_metrics(),
            self._collect_custom_metrics(),
            return_exceptions=True
        )
    
    async def _collect_cpu_metrics(self):
        """Collect CPU metrics."""
        try:
            # Overall CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.CPU,
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                threshold_warning=self.thresholds['cpu_usage']['warning'],
                threshold_critical=self.thresholds['cpu_usage']['critical']
            ))
            
            # Per-core CPU usage
            cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
            for i, cpu_core_percent in enumerate(cpu_percents):
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.CPU,
                    name=f"cpu_core_{i}_usage",
                    value=cpu_core_percent,
                    unit="percent",
                    labels={"core": str(i)}
                ))
            
            # CPU load average
            load_avg = psutil.getloadavg()
            for i, (period, avg) in enumerate(zip(['1min', '5min', '15min'], load_avg)):
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.CPU,
                    name=f"load_average_{period}",
                    value=avg,
                    unit="load",
                    labels={"period": period}
                ))
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.CPU,
                    name="cpu_frequency",
                    value=cpu_freq.current,
                    unit="mhz"
                ))
            
        except Exception as e:
            logger.error(f"❌ Error collecting CPU metrics: {e}")
    
    async def _collect_memory_metrics(self):
        """Collect memory metrics."""
        try:
            # Virtual memory
            memory = psutil.virtual_memory()
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                threshold_warning=self.thresholds['memory_usage']['warning'],
                threshold_critical=self.thresholds['memory_usage']['critical']
            ))
            
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="memory_total",
                value=memory.total,
                unit="bytes"
            ))
            
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="memory_available",
                value=memory.available,
                unit="bytes"
            ))
            
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="memory_used",
                value=memory.used,
                unit="bytes"
            ))
            
            # Swap memory
            swap = psutil.swap_memory()
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="swap_usage",
                value=swap.percent,
                unit="percent"
            ))
            
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.MEMORY,
                name="swap_total",
                value=swap.total,
                unit="bytes"
            ))
            
        except Exception as e:
            logger.error(f"❌ Error collecting memory metrics: {e}")
    
    async def _collect_disk_metrics(self):
        """Collect disk metrics."""
        try:
            # Disk usage for all partitions
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    await self._record_metric(ResourceMetric(
                        resource_type=ResourceType.DISK,
                        name="disk_usage",
                        value=(usage.used / usage.total) * 100,
                        unit="percent",
                        labels={"device": partition.device, "mountpoint": partition.mountpoint},
                        threshold_warning=self.thresholds['disk_usage']['warning'],
                        threshold_critical=self.thresholds['disk_usage']['critical']
                    ))
                    
                    await self._record_metric(ResourceMetric(
                        resource_type=ResourceType.DISK,
                        name="disk_total",
                        value=usage.total,
                        unit="bytes",
                        labels={"device": partition.device, "mountpoint": partition.mountpoint}
                    ))
                    
                    await self._record_metric(ResourceMetric(
                        resource_type=ResourceType.DISK,
                        name="disk_free",
                        value=usage.free,
                        unit="bytes",
                        labels={"device": partition.device, "mountpoint": partition.mountpoint}
                    ))
                    
                except PermissionError:
                    continue
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.DISK,
                    name="disk_read_bytes",
                    value=disk_io.read_bytes,
                    unit="bytes"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.DISK,
                    name="disk_write_bytes",
                    value=disk_io.write_bytes,
                    unit="bytes"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.DISK,
                    name="disk_read_count",
                    value=disk_io.read_count,
                    unit="operations"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.DISK,
                    name="disk_write_count",
                    value=disk_io.write_count,
                    unit="operations"
                ))
            
        except Exception as e:
            logger.error(f"❌ Error collecting disk metrics: {e}")
    
    async def _collect_network_metrics(self):
        """Collect network metrics."""
        try:
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            if net_io:
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_bytes_sent",
                    value=net_io.bytes_sent,
                    unit="bytes"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_bytes_recv",
                    value=net_io.bytes_recv,
                    unit="bytes"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_packets_sent",
                    value=net_io.packets_sent,
                    unit="packets"
                ))
                
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_packets_recv",
                    value=net_io.packets_recv,
                    unit="packets"
                ))
                
                # Network errors
                error_rate = (net_io.errin + net_io.errout) / max(net_io.packets_sent + net_io.packets_recv, 1) * 100
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_error_rate",
                    value=error_rate,
                    unit="percent",
                    threshold_warning=self.thresholds['network_errors']['warning'],
                    threshold_critical=self.thresholds['network_errors']['critical']
                ))
            
            # Network connections
            connections = psutil.net_connections()
            connection_states = {}
            for conn in connections:
                state = conn.status
                connection_states[state] = connection_states.get(state, 0) + 1
            
            for state, count in connection_states.items():
                await self._record_metric(ResourceMetric(
                    resource_type=ResourceType.NETWORK,
                    name="network_connections",
                    value=count,
                    unit="connections",
                    labels={"state": state}
                ))
            
        except Exception as e:
            logger.error(f"❌ Error collecting network metrics: {e}")
    
    async def _collect_process_metrics(self):
        """Collect process metrics."""
        try:
            processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
            process_count = 0
            
            for proc in processes:
                try:
                    process_count += 1
                    
                    # Record metrics for high-resource processes
                    if proc.info['cpu_percent'] > 10 or proc.info['memory_percent'] > 5:
                        await self._record_metric(ResourceMetric(
                            resource_type=ResourceType.PROCESS,
                            name="process_cpu_usage",
                            value=proc.info['cpu_percent'],
                            unit="percent",
                            labels={"pid": str(proc.info['pid']), "name": proc.info['name']}
                        ))
                        
                        await self._record_metric(ResourceMetric(
                            resource_type=ResourceType.PROCESS,
                            name="process_memory_usage",
                            value=proc.info['memory_percent'],
                            unit="percent",
                            labels={"pid": str(proc.info['pid']), "name": proc.info['name']}
                        ))
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            await self._record_metric(ResourceMetric(
                resource_type=ResourceType.PROCESS,
                name="process_count",
                value=process_count,
                unit="processes"
            ))
            
        except Exception as e:
            logger.error(f"❌ Error collecting process metrics: {e}")
    
    async def _collect_custom_metrics(self):
        """Collect custom metrics from registered collectors."""
        for collector_name, collector_func in self.custom_collectors.items():
            try:
                metrics = await collector_func()
                if isinstance(metrics, list):
                    for metric in metrics:
                        if isinstance(metric, ResourceMetric):
                            await self._record_metric(metric)
                elif isinstance(metrics, ResourceMetric):
                    await self._record_metric(metrics)
            except Exception as e:
                logger.error(f"❌ Error in custom collector '{collector_name}': {e}")
    
    async def _record_metric(self, metric: ResourceMetric):
        """Record a metric."""
        # Create unique key for metric
        metric_key = f"{metric.resource_type.value}_{metric.name}"
        if metric.labels:
            label_str = "_".join(f"{k}_{v}" for k, v in sorted(metric.labels.items()))
            metric_key += f"_{label_str}"
        
        # Store current metric
        self.current_metrics[metric_key] = metric
        
        # Add to history
        if metric_key not in self.metrics_history:
            self.metrics_history[metric_key] = []
        
        self.metrics_history[metric_key].append(metric)
        
        # Keep only last 1000 metrics per key
        if len(self.metrics_history[metric_key]) > 1000:
            self.metrics_history[metric_key] = self.metrics_history[metric_key][-1000:]
    
    async def _check_thresholds(self):
        """Check metric thresholds and generate alerts."""
        for metric_key, metric in self.current_metrics.items():
            if metric.threshold_warning is None and metric.threshold_critical is None:
                continue
            
            alert_level = None
            threshold = None
            
            if metric.threshold_critical and metric.value >= metric.threshold_critical:
                alert_level = AlertLevel.CRITICAL
                threshold = metric.threshold_critical
            elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                alert_level = AlertLevel.WARNING
                threshold = metric.threshold_warning
            
            if alert_level:
                await self._trigger_alert(metric, alert_level, threshold)
            else:
                await self._resolve_alert(metric_key)
    
    async def _trigger_alert(self, metric: ResourceMetric, level: AlertLevel, threshold: float):
        """Trigger a resource alert."""
        alert_id = f"{metric.resource_type.value}_{metric.name}_{level.value}"
        
        # Check if alert already exists
        if alert_id in self.alerts and not self.alerts[alert_id].resolved:
            return  # Alert already active
        
        alert = ResourceAlert(
            id=alert_id,
            resource_type=metric.resource_type,
            metric_name=metric.name,
            level=level,
            current_value=metric.value,
            threshold=threshold,
            message=f"{metric.resource_type.value.title()} {metric.name} is {level.value}: {metric.value:.2f}{metric.unit} (threshold: {threshold:.2f}{metric.unit})"
        )
        
        self.alerts[alert_id] = alert
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"❌ Error in alert callback: {e}")
        
        logger.warning(f"🚨 {level.value.upper()} Alert: {alert.message}")
    
    async def _resolve_alert(self, metric_key: str):
        """Resolve alerts for a metric."""
        alerts_to_resolve = [alert_id for alert_id, alert in self.alerts.items() 
                           if not alert.resolved and metric_key.startswith(f"{alert.resource_type.value}_{alert.metric_name}")]
        
        for alert_id in alerts_to_resolve:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            logger.info(f"✅ Alert resolved: {alert.message}")
    
    def register_custom_collector(self, name: str, collector_func: Callable):
        """Register a custom metric collector."""
        self.custom_collectors[name] = collector_func
        logger.info(f"📊 Registered custom collector: {name}")
    
    def register_alert_callback(self, callback: Callable):
        """Register an alert callback."""
        self.alert_callbacks.append(callback)
        logger.info("🚨 Registered alert callback")
    
    def get_current_metrics(self) -> Dict[str, ResourceMetric]:
        """Get current metrics snapshot."""
        return self.current_metrics.copy()
    
    def get_metric_history(self, metric_key: str, limit: int = 100) -> List[ResourceMetric]:
        """Get metric history."""
        return self.metrics_history.get(metric_key, [])[-limit:]
    
    def get_active_alerts(self) -> List[ResourceAlert]:
        """Get active alerts."""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system resource summary."""
        cpu_usage = self.current_metrics.get('cpu_cpu_usage')
        memory_usage = self.current_metrics.get('memory_memory_usage')
        
        return {
            'cpu_usage': cpu_usage.value if cpu_usage else 0,
            'memory_usage': memory_usage.value if memory_usage else 0,
            'active_alerts': len(self.get_active_alerts()),
            'total_metrics': len(self.current_metrics),
            'monitoring_interval': self.monitoring_interval,
            'uptime_seconds': time.time() - (datetime.now().timestamp() - 60)  # Approximate
        }
    
    async def _cleanup_loop(self):
        """Cleanup old data periodically."""
        while True:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"⚠️ Cleanup loop error: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Clean old resolved alerts
        alerts_to_remove = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time
        ]
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
        
        logger.info(f"🧹 Cleaned up {len(alerts_to_remove)} old alerts")


async def main():
    """Example usage of the Resource Monitoring Service."""
    print("📈 Resource Monitoring Service Example")
    print("=" * 42)
    
    # Create monitoring service
    monitoring = ResourceMonitoringService(monitoring_interval=5)
    
    # Register alert callback
    async def alert_handler(alert: ResourceAlert):
        print(f"🚨 ALERT [{alert.level.value.upper()}]: {alert.message}")
    
    monitoring.register_alert_callback(alert_handler)
    
    # Register custom collector
    async def custom_app_metrics():
        return [
            ResourceMetric(
                resource_type=ResourceType.CUSTOM,
                name="app_response_time",
                value=150.5,
                unit="ms"
            ),
            ResourceMetric(
                resource_type=ResourceType.CUSTOM,
                name="app_active_users",
                value=245,
                unit="users"
            )
        ]
    
    monitoring.register_custom_collector("app_metrics", custom_app_metrics)
    
    # Start monitoring
    await monitoring.start()
    
    # Let it collect metrics for a bit
    await asyncio.sleep(10)
    
    # Show current metrics
    summary = monitoring.get_system_summary()
    print(f"\n📊 System Summary:")
    print(f"   CPU Usage: {summary['cpu_usage']:.1f}%")
    print(f"   Memory Usage: {summary['memory_usage']:.1f}%")
    print(f"   Active Alerts: {summary['active_alerts']}")
    print(f"   Total Metrics: {summary['total_metrics']}")
    
    # Show recent metrics
    current_metrics = monitoring.get_current_metrics()
    print(f"\n📈 Recent Metrics (showing first 5):")
    for i, (key, metric) in enumerate(list(current_metrics.items())[:5]):
        print(f"   {metric.name}: {metric.value:.2f} {metric.unit}")
    
    await monitoring.stop()
    print("\n🛑 Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())