"""Backup Monitor for IA Influencer Agent Platform.

Provides real-time monitoring and alerting for backup operations
with comprehensive metrics and health checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import psutil
import json

from ...monitoring.metrics.metrics_collector import MetricsCollector
from ...monitoring.alerting.alert_manager import AlertManager
from ...core.exceptions import MonitoringError


class MonitoringLevel(Enum):
    """Monitoring level enumeration."""    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


class AlertSeverity(Enum):
    """Alert severity enumeration."""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class BackupMetrics:
    """Backup operation metrics."""    backup_id: str
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    bytes_processed: int
    files_processed: int
    throughput_mbps: float
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_usage_mb: float
    network_usage_mb: float
    compression_ratio: float
    error_count: int
    warnings: List[str] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System-wide backup metrics."""    timestamp: datetime
    active_backups: int
    total_backup_size: int
    daily_backup_count: int
    success_rate: float
    average_duration: float
    system_cpu_usage: float
    system_memory_usage: float
    system_disk_usage: float
    backup_queue_size: int


@dataclass
class HealthStatus:
    """Backup system health status."""    overall_status: str
    backup_service_status: str
    storage_status: str
    database_status: str
    network_status: str
    last_successful_backup: Optional[datetime]
    pending_backups: int
    failed_backups_24h: int
    storage_utilization: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class BackupMonitor:
    """    Enterprise backup monitoring system with real-time metrics and alerting.
    
    Monitors backup operations, system resources, and provides comprehensive
    health checking and alerting capabilities.
    """
    def __init__(
        self,
        monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED,
        alert_thresholds: Optional[Dict[str, Any]] = None
    ):
        """        Initialize backup monitor.
        
        Args:
            monitoring_level: Level of monitoring detail
            alert_thresholds: Custom alert thresholds
        """        self.logger = logging.getLogger(__name__)
        self.monitoring_level = monitoring_level
        self.alert_thresholds = alert_thresholds or self._get_default_thresholds()
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        
        # Monitoring data
        self.backup_metrics: Dict[str, BackupMetrics] = {}
        self.system_metrics_history: List[SystemMetrics] = []
        self.active_monitors: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring tasks
        self._monitoring_tasks: List[asyncio.Task] = []
        self._is_monitoring = False

    async def start_monitoring(self) -> None:
        """Start backup monitoring services."""        if self._is_monitoring:
            self.logger.warning("Monitoring is already running")
            return
        
        self.logger.info("Starting backup monitoring...")
        self._is_monitoring = True
        
        # Start monitoring tasks
        self._monitoring_tasks = [
            asyncio.create_task(self._system_metrics_loop()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._alert_evaluation_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        self.logger.info("Backup monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop backup monitoring services."""        if not self._is_monitoring:
            self.logger.warning("Monitoring is not running")
            return
        
        self.logger.info("Stopping backup monitoring...")
        self._is_monitoring = False
        
        # Cancel monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
        self._monitoring_tasks.clear()
        
        self.logger.info("Backup monitoring stopped")

    async def start_backup_monitoring(
        self,
        backup_id: str,
        operation_type: str = "backup"
    ) -> None:
        """        Start monitoring specific backup operation.
        
        Args:
            backup_id: Backup operation identifier
            operation_type: Type of backup operation
        """        self.logger.info(f"Starting monitoring for backup: {backup_id}")
        
        metrics = BackupMetrics(
            backup_id=backup_id,
            operation_type=operation_type,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            bytes_processed=0,
            files_processed=0,
            throughput_mbps=0.0,
            cpu_usage_percent=0.0,
            memory_usage_mb=0.0,
            disk_usage_mb=0.0,
            network_usage_mb=0.0,
            compression_ratio=0.0,
            error_count=0
        )
        
        self.backup_metrics[backup_id] = metrics
        
        # Start detailed monitoring if enabled
        if self.monitoring_level in [MonitoringLevel.DETAILED, MonitoringLevel.COMPREHENSIVE]:
            self.active_monitors[backup_id] = {
                "start_time": time.time(),
                "last_update": time.time(),
                "process_info": await self._get_process_info(),
                "initial_disk_usage": await self._get_disk_usage()
            }

    async def update_backup_progress(
        self,
        backup_id: str,
        bytes_processed: int,
        files_processed: int,
        progress_percent: float = 0.0
    ) -> None:
        """        Update backup operation progress.
        
        Args:
            backup_id: Backup operation identifier
            bytes_processed: Number of bytes processed
            files_processed: Number of files processed
            progress_percent: Progress percentage
        """        if backup_id not in self.backup_metrics:
            self.logger.warning(f"Backup metrics not found: {backup_id}")
            return
        
        metrics = self.backup_metrics[backup_id]
        current_time = time.time()
        
        # Update basic metrics
        metrics.bytes_processed = bytes_processed
        metrics.files_processed = files_processed
        
        # Calculate throughput
        if backup_id in self.active_monitors:
            monitor_data = self.active_monitors[backup_id]
            elapsed_time = current_time - monitor_data["start_time"]
            
            if elapsed_time > 0:
                throughput_bps = bytes_processed / elapsed_time
                metrics.throughput_mbps = throughput_bps / (1024 * 1024)
        
        # Update resource usage
        if self.monitoring_level in [MonitoringLevel.DETAILED, MonitoringLevel.COMPREHENSIVE]:
            await self._update_resource_metrics(backup_id)
        
        # Collect metrics for storage
        await self.metrics_collector.record_backup_progress(
            backup_id, bytes_processed, files_processed, progress_percent
        )

    async def finish_backup_monitoring(
        self,
        backup_id: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> BackupMetrics:
        """        Finish monitoring backup operation.
        
        Args:
            backup_id: Backup operation identifier
            success: Whether backup succeeded
            error_message: Error message if failed
            
        Returns:
            Final backup metrics
        """        if backup_id not in self.backup_metrics:
            raise MonitoringError(f"Backup metrics not found: {backup_id}")
        
        metrics = self.backup_metrics[backup_id]
        end_time = datetime.now()
        
        # Update final metrics
        metrics.end_time = end_time
        metrics.duration_seconds = (end_time - metrics.start_time).total_seconds()
        
        if not success:
            metrics.error_count += 1
            if error_message:
                metrics.warnings.append(error_message)
        
        # Final resource usage update
        if self.monitoring_level in [MonitoringLevel.DETAILED, MonitoringLevel.COMPREHENSIVE]:
            await self._update_resource_metrics(backup_id)
        
        # Clean up active monitoring
        if backup_id in self.active_monitors:
            del self.active_monitors[backup_id]
        
        # Store final metrics
        await self.metrics_collector.record_backup_completion(backup_id, metrics)
        
        # Check for alerts
        await self._evaluate_backup_alerts(backup_id, metrics, success)
        
        self.logger.info(f"Finished monitoring backup: {backup_id} (success: {success})")
        return metrics

    async def get_backup_progress(self, backup_id: str) -> Dict[str, Any]:
        """        Get current backup progress.
        
        Args:
            backup_id: Backup operation identifier
            
        Returns:
            Progress information
        """        if backup_id not in self.backup_metrics:
            return {
                "status": "not_found",
                "message": f"Backup not found: {backup_id}"
            }
        
        metrics = self.backup_metrics[backup_id]
        monitor_data = self.active_monitors.get(backup_id, {})
        
        # Calculate progress percentage
        progress_percent = 0.0
        if monitor_data and "estimated_total_size" in monitor_data:
            estimated_size = monitor_data["estimated_total_size"]
            if estimated_size > 0:
                progress_percent = (metrics.bytes_processed / estimated_size) * 100
        
        # Calculate ETA
        eta_seconds = None
        if metrics.throughput_mbps > 0 and monitor_data and "estimated_total_size" in monitor_data:
            remaining_bytes = monitor_data["estimated_total_size"] - metrics.bytes_processed
            eta_seconds = remaining_bytes / (metrics.throughput_mbps * 1024 * 1024)
        
        return {
            "status": "running",
            "backup_id": backup_id,
            "operation_type": metrics.operation_type,
            "start_time": metrics.start_time.isoformat(),
            "duration_seconds": (datetime.now() - metrics.start_time).total_seconds(),
            "bytes_processed": metrics.bytes_processed,
            "files_processed": metrics.files_processed,
            "progress_percent": min(progress_percent, 100.0),
            "throughput_mbps": metrics.throughput_mbps,
            "cpu_usage_percent": metrics.cpu_usage_percent,
            "memory_usage_mb": metrics.memory_usage_mb,
            "disk_usage_mb": metrics.disk_usage_mb,
            "eta_seconds": eta_seconds,
            "warnings": len(metrics.warnings),
            "compression_ratio": metrics.compression_ratio
        }

    async def get_system_health(self) -> HealthStatus:
        """        Get comprehensive system health status.
        
        Returns:
            System health information
        """        current_time = datetime.now()
        
        # Get active backup count
        active_backups = len(self.active_monitors)
        
        # Calculate metrics from history
        recent_metrics = [
            m for m in self.system_metrics_history 
            if m.timestamp > current_time - timedelta(hours=24)
        ]
        
        success_rate = 100.0
        failed_backups_24h = 0
        last_successful_backup = None
        
        if recent_metrics:
            success_rates = [m.success_rate for m in recent_metrics]
            success_rate = sum(success_rates) / len(success_rates)
            
            # Find last successful backup
            for metrics in reversed(recent_metrics):
                if metrics.success_rate > 0:
                    last_successful_backup = metrics.timestamp
                    break
        
        # Get storage utilization
        storage_utilization = await self._get_storage_utilization()
        
        # Get service status
        backup_service_status = "healthy"
        storage_status = "healthy"
        database_status = "healthy"
        network_status = "healthy"
        
        # Determine overall status
        overall_status = "healthy"
        issues = []
        recommendations = []
        
        # Check for issues
        if success_rate < 90:
            overall_status = "warning"
            issues.append(f"Low success rate: {success_rate:.1f}%")
            recommendations.append("Check backup logs for recurring errors")
        
        if storage_utilization > 85:
            overall_status = "warning"
            issues.append(f"High storage utilization: {storage_utilization:.1f}%")
            recommendations.append("Consider adding more storage or cleanup old backups")
        
        if active_backups > 5:
            issues.append(f"High number of concurrent backups: {active_backups}")
            recommendations.append("Consider adjusting backup scheduling")
        
        if not last_successful_backup or last_successful_backup < current_time - timedelta(hours=48):
            overall_status = "critical"
            issues.append("No successful backups in the last 48 hours")
            recommendations.append("Investigate backup system immediately")
        
        return HealthStatus(
            overall_status=overall_status,
            backup_service_status=backup_service_status,
            storage_status=storage_status,
            database_status=database_status,
            network_status=network_status,
            last_successful_backup=last_successful_backup,
            pending_backups=active_backups,
            failed_backups_24h=failed_backups_24h,
            storage_utilization=storage_utilization,
            issues=issues,
            recommendations=recommendations
        )

    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """        Get comprehensive monitoring statistics.
        
        Returns:
            Monitoring statistics
        """        current_time = datetime.now()
        
        # Calculate statistics from recent metrics
        recent_metrics = [
            m for m in self.system_metrics_history 
            if m.timestamp > current_time - timedelta(hours=24)
        ]
        
        total_backups_24h = sum(m.daily_backup_count for m in recent_metrics) if recent_metrics else 0
        average_duration = sum(m.average_duration for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        # Current system metrics
        current_metrics = await self._collect_current_system_metrics()
        
        return {
            "monitoring_level": self.monitoring_level.value,
            "active_backups": len(self.active_monitors),
            "total_monitored_backups": len(self.backup_metrics),
            "backups_24h": total_backups_24h,
            "average_duration_seconds": average_duration,
            "success_rate_24h": success_rate,
            "current_system_cpu": current_metrics["cpu_usage"],
            "current_system_memory": current_metrics["memory_usage"],
            "current_system_disk": current_metrics["disk_usage"],
            "storage_utilization": await self._get_storage_utilization(),
            "alerts_sent_24h": await self._get_alerts_count_24h(),
            "monitoring_uptime": self._is_monitoring
        }

    async def add_custom_alert(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message: str
    ) -> None:
        """        Add custom alert condition.
        
        Args:
            name: Alert name
            condition: Function to evaluate alert condition
            severity: Alert severity
            message: Alert message
        """        await self.alert_manager.add_custom_alert(
            name, condition, severity.value, message
        )

    async def _system_metrics_loop(self) -> None:
        """Collect system metrics periodically."""        while self._is_monitoring:
            try:
                # Collect current system metrics
                metrics = await self._collect_current_system_metrics()
                
                system_metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    active_backups=len(self.active_monitors),
                    total_backup_size=await self._calculate_total_backup_size(),
                    daily_backup_count=await self._get_daily_backup_count(),
                    success_rate=await self._calculate_success_rate(),
                    average_duration=await self._calculate_average_duration(),
                    system_cpu_usage=metrics["cpu_usage"],
                    system_memory_usage=metrics["memory_usage"],
                    system_disk_usage=metrics["disk_usage"],
                    backup_queue_size=await self._get_backup_queue_size()
                )
                
                self.system_metrics_history.append(system_metrics)
                
                # Keep only recent history (last 7 days)
                cutoff_time = datetime.now() - timedelta(days=7)
                self.system_metrics_history = [
                    m for m in self.system_metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Record metrics
                await self.metrics_collector.record_system_metrics(system_metrics)
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in system metrics loop: {e}")
                await asyncio.sleep(300)

    async def _health_check_loop(self) -> None:
        """Perform health checks periodically."""        while self._is_monitoring:
            try:
                health_status = await self.get_system_health()
                
                # Record health status
                await self.metrics_collector.record_health_status(health_status)
                
                # Send health alerts if necessary
                if health_status.overall_status in ["warning", "critical"]:
                    await self.alert_manager.send_health_alert(health_status)
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(600)

    async def _alert_evaluation_loop(self) -> None:
        """Evaluate alert conditions periodically."""        while self._is_monitoring:
            try:
                # Evaluate system-level alerts
                await self._evaluate_system_alerts()
                
                # Evaluate backup-specific alerts
                for backup_id in list(self.active_monitors.keys()):
                    if backup_id in self.backup_metrics:
                        await self._evaluate_backup_runtime_alerts(backup_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(60)

    async def _cleanup_loop(self) -> None:
        """Clean up old monitoring data periodically."""        while self._is_monitoring:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(days=30)
                
                # Clean up old backup metrics
                old_backup_ids = [
                    backup_id for backup_id, metrics in self.backup_metrics.items()
                    if metrics.end_time and metrics.end_time < cutoff_time
                ]
                
                for backup_id in old_backup_ids:
                    del self.backup_metrics[backup_id]
                
                self.logger.info(f"Cleaned up {len(old_backup_ids)} old backup metrics")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(86400)

    async def _update_resource_metrics(self, backup_id: str) -> None:
        """Update resource usage metrics for backup operation."""        if backup_id not in self.backup_metrics:
            return
        
        metrics = self.backup_metrics[backup_id]
        
        # Get current resource usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = await self._get_disk_usage()
        
        # Update metrics
        metrics.cpu_usage_percent = cpu_percent
        metrics.memory_usage_mb = memory_info.used / (1024 * 1024)
        metrics.disk_usage_mb = disk_info
        
        # Calculate compression ratio if available
        if backup_id in self.active_monitors:
            monitor_data = self.active_monitors[backup_id]
            if "original_size" in monitor_data and "compressed_size" in monitor_data:
                original = monitor_data["original_size"]
                compressed = monitor_data["compressed_size"]
                if original > 0:
                    metrics.compression_ratio = compressed / original

    async def _collect_current_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory_info.percent,
            "disk_usage": disk_info.percent,
            "memory_available_mb": memory_info.available / (1024 * 1024),
            "disk_free_gb": disk_info.free / (1024 * 1024 * 1024)
        }

    async def _get_process_info(self) -> Dict[str, Any]:
        """Get current process information."""        process = psutil.Process()
        return {
            "pid": process.pid,
            "memory_mb": process.memory_info().rss / (1024 * 1024),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads()
        }

    async def _get_disk_usage(self) -> float:
        """Get current disk usage in MB."""        disk_info = psutil.disk_usage('/')
        return disk_info.used / (1024 * 1024)

    async def _get_storage_utilization(self) -> float:
        """Get backup storage utilization percentage."""        disk_info = psutil.disk_usage('/')
        return disk_info.percent

    async def _calculate_total_backup_size(self) -> int:
        """Calculate total size of all backups."""        # This would be implemented based on actual storage backend
        return 0

    async def _get_daily_backup_count(self) -> int:
        """Get number of backups completed today."""        today = datetime.now().date()
        count = 0
        
        for metrics in self.backup_metrics.values():
            if metrics.end_time and metrics.end_time.date() == today:
                count += 1
        
        return count

    async def _calculate_success_rate(self) -> float:
        """Calculate backup success rate."""        if not self.backup_metrics:
            return 100.0
        
        completed_backups = [
            m for m in self.backup_metrics.values() 
            if m.end_time is not None
        ]
        
        if not completed_backups:
            return 100.0
        
        successful_backups = [
            m for m in completed_backups 
            if m.error_count == 0
        ]
        
        return (len(successful_backups) / len(completed_backups)) * 100

    async def _calculate_average_duration(self) -> float:
        """Calculate average backup duration."""        completed_backups = [
            m for m in self.backup_metrics.values() 
            if m.duration_seconds is not None
        ]
        
        if not completed_backups:
            return 0.0
        
        durations = [m.duration_seconds for m in completed_backups]
        return sum(durations) / len(durations)

    async def _get_backup_queue_size(self) -> int:
        """Get number of backups in queue."""        # This would be implemented based on actual queue system
        return 0

    async def _get_alerts_count_24h(self) -> int:
        """Get number of alerts sent in last 24 hours."""        return await self.alert_manager.get_alerts_count_24h()

    async def _evaluate_system_alerts(self) -> None:
        """Evaluate system-level alert conditions."""        current_metrics = await self._collect_current_system_metrics()
        
        # High CPU usage alert
        if current_metrics["cpu_usage"] > self.alert_thresholds["cpu_critical"]:
            await self.alert_manager.send_alert(
                "high_cpu_usage",
                AlertSeverity.CRITICAL.value,
                f"Critical CPU usage: {current_metrics['cpu_usage']:.1f}%"
            )
        elif current_metrics["cpu_usage"] > self.alert_thresholds["cpu_warning"]:
            await self.alert_manager.send_alert(
                "high_cpu_usage",
                AlertSeverity.WARNING.value,
                f"High CPU usage: {current_metrics['cpu_usage']:.1f}%"
            )
        
        # High memory usage alert
        if current_metrics["memory_usage"] > self.alert_thresholds["memory_critical"]:
            await self.alert_manager.send_alert(
                "high_memory_usage",
                AlertSeverity.CRITICAL.value,
                f"Critical memory usage: {current_metrics['memory_usage']:.1f}%"
            )
        elif current_metrics["memory_usage"] > self.alert_thresholds["memory_warning"]:
            await self.alert_manager.send_alert(
                "high_memory_usage",
                AlertSeverity.WARNING.value,
                f"High memory usage: {current_metrics['memory_usage']:.1f}%"
            )
        
        # High disk usage alert
        if current_metrics["disk_usage"] > self.alert_thresholds["disk_critical"]:
            await self.alert_manager.send_alert(
                "high_disk_usage",
                AlertSeverity.CRITICAL.value,
                f"Critical disk usage: {current_metrics['disk_usage']:.1f}%"
            )
        elif current_metrics["disk_usage"] > self.alert_thresholds["disk_warning"]:
            await self.alert_manager.send_alert(
                "high_disk_usage",
                AlertSeverity.WARNING.value,
                f"High disk usage: {current_metrics['disk_usage']:.1f}%"
            )

    async def _evaluate_backup_alerts(
        self, 
        backup_id: str, 
        metrics: BackupMetrics, 
        success: bool
    ) -> None:
        """Evaluate alerts for completed backup."""        if not success:
            await self.alert_manager.send_alert(
                "backup_failed",
                AlertSeverity.ERROR.value,
                f"Backup failed: {backup_id}"
            )
        
        # Long duration alert
        if metrics.duration_seconds and metrics.duration_seconds > self.alert_thresholds["backup_duration_warning"]:
            severity = AlertSeverity.WARNING.value
            if metrics.duration_seconds > self.alert_thresholds["backup_duration_critical"]:
                severity = AlertSeverity.CRITICAL.value
            
            await self.alert_manager.send_alert(
                "backup_long_duration",
                severity,
                f"Backup took {metrics.duration_seconds:.1f} seconds: {backup_id}"
            )
        
        # Low throughput alert
        if metrics.throughput_mbps < self.alert_thresholds["throughput_warning"]:
            await self.alert_manager.send_alert(
                "backup_low_throughput",
                AlertSeverity.WARNING.value,
                f"Low backup throughput: {metrics.throughput_mbps:.1f} MB/s for {backup_id}"
            )

    async def _evaluate_backup_runtime_alerts(self, backup_id: str) -> None:
        """Evaluate alerts for running backup."""        if backup_id not in self.backup_metrics:
            return
        
        metrics = self.backup_metrics[backup_id]
        current_time = datetime.now()
        runtime = (current_time - metrics.start_time).total_seconds()
        
        # Stuck backup alert
        if runtime > self.alert_thresholds["backup_stuck_timeout"]:
            await self.alert_manager.send_alert(
                "backup_stuck",
                AlertSeverity.CRITICAL.value,
                f"Backup appears stuck: {backup_id} (running for {runtime:.1f} seconds)"
            )

    def _get_default_thresholds(self) -> Dict[str, Any]:
        """Get default alert thresholds."""        return {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 85.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "backup_duration_warning": 3600,  # 1 hour
            "backup_duration_critical": 7200,  # 2 hours
            "backup_stuck_timeout": 14400,  # 4 hours
            "throughput_warning": 1.0,  # 1 MB/s
            "storage_utilization_warning": 85.0,
            "storage_utilization_critical": 95.0
        }
