"""Database Resource Monitor

Advanced system resource monitoring for database operations with intelligent
resource allocation tracking, bottleneck detection, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import statistics
import psutil
import shutil
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_database_session
from ..models.monitoring import ResourceMetrics, ResourceAlert
from ...core.config import Settings
from ...utils.cache import RedisCache


class ResourceType(Enum):
    """
System resource types"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"


class ResourceStatus(Enum):
    """Resource utilization status"""

    OPTIMAL = "optimal"
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class CPUMetrics:
    """CPU utilization metrics"""
    overall_percent: float
    per_core_percent: List[float]
    user_percent: float
    system_percent: float
    idle_percent: float
    iowait_percent: float
    load_average_1m: float
    load_average_5m: float
    load_average_15m: float
    context_switches_per_sec: float
    interrupts_per_sec: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class MemoryMetrics:
    """
Memory utilization metrics"""
    total_mb: float
    available_mb: float
    used_mb: float
    used_percent: float
    free_mb: float
    cached_mb: float
    buffers_mb: float
    shared_mb: float
    swap_total_mb: float
    swap_used_mb: float
    swap_percent: float
    database_memory_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class DiskMetrics:
    """
Disk I/O and storage metrics"""
    total_space_gb: float
    used_space_gb: float
    free_space_gb: float
    used_percent: float
    read_iops: float
    write_iops: float
    read_throughput_mbps: float
    write_throughput_mbps: float
    avg_read_latency_ms: float
    avg_write_latency_ms: float
    queue_depth: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class NetworkMetrics:
    """
Network utilization metrics"""
    bytes_sent_per_sec: float
    bytes_recv_per_sec: float
    packets_sent_per_sec: float
    packets_recv_per_sec: float
    connections_established: int
    connections_time_wait: int
    connection_errors: int
    bandwidth_utilization_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class DatabaseResourceMetrics:
    """
Database-specific resource metrics"""
    shared_buffers_mb: float
    effective_cache_size_mb: float
    work_mem_mb: float
    maintenance_work_mem_mb: float
    buffer_cache_hit_ratio: float
    checkpoint_write_time_ms: float
    wal_write_latency_ms: float
    temp_files_count: int
    temp_files_size_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return asdict(self)


@dataclass
class ResourceSnapshot:
    """
Complete resource utilization snapshot"""
    timestamp: datetime
    cpu_metrics: CPUMetrics
    memory_metrics: MemoryMetrics
    disk_metrics: DiskMetrics
    network_metrics: NetworkMetrics
    database_metrics: DatabaseResourceMetrics
    overall_status: ResourceStatus
    bottlenecks: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['cpu_metrics'] = self.cpu_metrics.to_dict()
        data['memory_metrics'] = self.memory_metrics.to_dict()
        data['disk_metrics'] = self.disk_metrics.to_dict()
        data['network_metrics'] = self.network_metrics.to_dict()
        data['database_metrics'] = self.database_metrics.to_dict()
        data['overall_status'] = self.overall_status.value
        return data


class ResourceMonitor:
    """
    Advanced system resource monitoring for database operations.
    
    Features:
    - Multi-dimensional resource tracking
    - Intelligent bottleneck detection
    - Performance trend analysis
    - Automated optimization recommendations
    - Resource allocation planning
    - Capacity planning assistance
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        
        # Monitoring state
        self.monitoring_active = False
        self.resource_history: deque = deque(maxlen=2880)  # 48 hours at 1-minute intervals
        self.baseline_metrics: Optional[ResourceSnapshot] = None
        
        # Previous measurements for delta calculations
        self.previous_cpu_times = None
        self.previous_disk_io = None
        self.previous_network_io = None
        
        # Alert thresholds
        self.thresholds = {
            'cpu_warning': 75.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_usage_warning': 85.0,
            'disk_usage_critical': 95.0,
            'disk_iops_warning': 1000.0,
            'disk_iops_critical': 2000.0,
            'network_warning': 80.0,  # % of estimated bandwidth
            'network_critical': 95.0
        }
        
        self.logger.info("Resource Monitor initialized")
    
    async def start_monitoring(self, interval: int = 60) -> None:
        """Start resource monitoring"""
        if self.monitoring_active:
            self.logger.warning("Resource monitoring already active")
            return
        
        self.monitoring_active = True
        self.logger.info(f"Starting resource monitoring with {interval}s interval")
        
        try:
            # Establish baseline
            await self._establish_baseline()
            
            # Start monitoring loop
            while self.monitoring_active:
                snapshot = await self._collect_resource_snapshot()
                if snapshot:
                    await self._process_snapshot(snapshot)
                
                await asyncio.sleep(interval)
                
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        self.monitoring_active = False
        self.logger.info("Resource monitoring stopped")
    
    async def _establish_baseline(self) -> None:
        """Establish baseline resource metrics"""
        try:
            baseline_snapshots = []
            
            # Collect baseline over 5 minutes
            for _ in range(5):
                snapshot = await self._collect_resource_snapshot()
                if snapshot:
                    baseline_snapshots.append(snapshot)
                await asyncio.sleep(60)
            
            if baseline_snapshots:
                # Calculate average baseline
                self.baseline_metrics = await self._calculate_baseline_average(baseline_snapshots)
                self.logger.info("Baseline metrics established")
            
        except Exception as e:
            self.logger.error(f"Error establishing baseline: {e}")
    
    async def _collect_resource_snapshot(self) -> Optional[ResourceSnapshot]:
        """Collect comprehensive resource snapshot"""
        try:
            timestamp = datetime.utcnow()
            
            # Collect all metric types
            cpu_metrics = await self._collect_cpu_metrics()
            memory_metrics = await self._collect_memory_metrics()
            disk_metrics = await self._collect_disk_metrics()
            network_metrics = await self._collect_network_metrics()
            database_metrics = await self._collect_database_metrics()
            
            # Analyze bottlenecks and status
            bottlenecks = self._identify_bottlenecks(
                cpu_metrics, memory_metrics, disk_metrics, network_metrics, database_metrics
            )
            
            overall_status = self._determine_overall_status(
                cpu_metrics, memory_metrics, disk_metrics, network_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(bottlenecks, overall_status)
            
            snapshot = ResourceSnapshot(
                timestamp=timestamp,
                cpu_metrics=cpu_metrics,
                memory_metrics=memory_metrics,
                disk_metrics=disk_metrics,
                network_metrics=network_metrics,
                database_metrics=database_metrics,
                overall_status=overall_status,
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error collecting resource snapshot: {e}")
            return True
    
    async def _collect_cpu_metrics(self) -> CPUMetrics:
        """Collect CPU utilization metrics"""
        try:
            # Get CPU times
            cpu_times = psutil.cpu_times()
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            
            # Get load averages
            load_avg = psutil.getloadavg()
            
            # Calculate rates if we have previous data
            context_switches_rate = 0.0
            interrupts_rate = 0.0
            
            try:
                cpu_stats = psutil.cpu_stats()
                if self.previous_cpu_times:
                    time_delta = time.time() - self.previous_cpu_times['timestamp']
                    if time_delta > 0:
                        context_switches_rate = (cpu_stats.ctx_switches - self.previous_cpu_times['ctx_switches']) / time_delta
                        interrupts_rate = (cpu_stats.interrupts - self.previous_cpu_times['interrupts']) / time_delta
                
                self.previous_cpu_times = {
                    'timestamp': time.time(),
                    'ctx_switches': cpu_stats.ctx_switches,
                    'interrupts': cpu_stats.interrupts
                }
            except Exception:
                pass
            
            return CPUMetrics(
                overall_percent=cpu_percent,
                per_core_percent=cpu_per_core,
                user_percent=cpu_times.user / sum(cpu_times) * 100,
                system_percent=cpu_times.system / sum(cpu_times) * 100,
                idle_percent=cpu_times.idle / sum(cpu_times) * 100,
                iowait_percent=getattr(cpu_times, 'iowait', 0) / sum(cpu_times) * 100,
                load_average_1m=load_avg[0],
                load_average_5m=load_avg[1],
                load_average_15m=load_avg[2],
                context_switches_per_sec=context_switches_rate,
                interrupts_per_sec=interrupts_rate
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
            # Return default metrics on error
            return CPUMetrics(0, [], 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    async def _collect_memory_metrics(self) -> MemoryMetrics:
        """Collect memory utilization metrics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Estimate database memory usage
            database_memory = 0.0
            try:
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    if 'postgres' in proc.info['name'].lower():
                        database_memory += proc.info['memory_info'].rss / (1024 * 1024)  # MB
            except Exception:
                pass
            
            return MemoryMetrics(
                total_mb=memory.total / (1024 * 1024),
                available_mb=memory.available / (1024 * 1024),
                used_mb=memory.used / (1024 * 1024),
                used_percent=memory.percent,
                free_mb=memory.free / (1024 * 1024),
                cached_mb=getattr(memory, 'cached', 0) / (1024 * 1024),
                buffers_mb=getattr(memory, 'buffers', 0) / (1024 * 1024),
                shared_mb=getattr(memory, 'shared', 0) / (1024 * 1024),
                swap_total_mb=swap.total / (1024 * 1024),
                swap_used_mb=swap.used / (1024 * 1024),
                swap_percent=swap.percent,
                database_memory_mb=database_memory
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            return MemoryMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    async def _collect_disk_metrics(self) -> DiskMetrics:
        """Collect disk I/O and storage metrics"""
        try:
            # Get disk usage for database data directory
            data_dir = getattr(self.settings, 'database_data_dir', '/')
            disk_usage = shutil.disk_usage(data_dir)
            
            # Get disk I/O statistics
            disk_io = psutil.disk_io_counters()
            
            # Calculate rates if we have previous data
            read_iops = 0.0
            write_iops = 0.0
            read_throughput = 0.0
            write_throughput = 0.0
            
            if self.previous_disk_io and disk_io:
                time_delta = time.time() - self.previous_disk_io['timestamp']
                if time_delta > 0:
                    read_iops = (disk_io.read_count - self.previous_disk_io['read_count']) / time_delta
                    write_iops = (disk_io.write_count - self.previous_disk_io['write_count']) / time_delta
                    read_throughput = (disk_io.read_bytes - self.previous_disk_io['read_bytes']) / time_delta / (1024 * 1024)
                    write_throughput = (disk_io.write_bytes - self.previous_disk_io['write_bytes']) / time_delta / (1024 * 1024)
            
            if disk_io:
                self.previous_disk_io = {
                    'timestamp': time.time(),
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                }
            
            return DiskMetrics(
                total_space_gb=disk_usage.total / (1024 * 1024 * 1024),
                used_space_gb=disk_usage.used / (1024 * 1024 * 1024),
                free_space_gb=disk_usage.free / (1024 * 1024 * 1024),
                used_percent=(disk_usage.used / disk_usage.total) * 100,
                read_iops=read_iops,
                write_iops=write_iops,
                read_throughput_mbps=read_throughput,
                write_throughput_mbps=write_throughput,
                avg_read_latency_ms=disk_io.read_time / max(disk_io.read_count, 1) if disk_io else 0,
                avg_write_latency_ms=disk_io.write_time / max(disk_io.write_count, 1) if disk_io else 0,
                queue_depth=0.0  # Not directly available from psutil
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {e}")
            return DiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    async def _collect_network_metrics(self) -> NetworkMetrics:
        """Collect network utilization metrics"""
        try:
            network_io = psutil.net_io_counters()
            
            # Calculate rates if we have previous data
            bytes_sent_rate = 0.0
            bytes_recv_rate = 0.0
            packets_sent_rate = 0.0
            packets_recv_rate = 0.0
            
            if self.previous_network_io and network_io:
                time_delta = time.time() - self.previous_network_io['timestamp']
                if time_delta > 0:
                    bytes_sent_rate = (network_io.bytes_sent - self.previous_network_io['bytes_sent']) / time_delta
                    bytes_recv_rate = (network_io.bytes_recv - self.previous_network_io['bytes_recv']) / time_delta
                    packets_sent_rate = (network_io.packets_sent - self.previous_network_io['packets_sent']) / time_delta
                    packets_recv_rate = (network_io.packets_recv - self.previous_network_io['packets_recv']) / time_delta
            
            if network_io:
                self.previous_network_io = {
                    'timestamp': time.time(),
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            
            # Get connection statistics
            connections = psutil.net_connections()
            established_count = sum(1 for conn in connections if conn.status == 'ESTABLISHED')
            time_wait_count = sum(1 for conn in connections if conn.status == 'TIME_WAIT')
            
            # Estimate bandwidth utilization (assuming 1Gbps interface)
            estimated_bandwidth_bps = 1000 * 1024 * 1024  # 1 Gbps
            total_throughput = bytes_sent_rate + bytes_recv_rate
            bandwidth_utilization = (total_throughput / estimated_bandwidth_bps) * 100
            
            return NetworkMetrics(
                bytes_sent_per_sec=bytes_sent_rate,
                bytes_recv_per_sec=bytes_recv_rate,
                packets_sent_per_sec=packets_sent_rate,
                packets_recv_per_sec=packets_recv_rate,
                connections_established=established_count,
                connections_time_wait=time_wait_count,
                connection_errors=network_io.errin + network_io.errout if network_io else 0,
                bandwidth_utilization_percent=bandwidth_utilization
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
            return NetworkMetrics(0, 0, 0, 0, 0, 0, 0, 0)
    
    async def _collect_database_metrics(self) -> DatabaseResourceMetrics:
        """Collect database-specific resource metrics"""
        try:
            async with get_database_session() as session:
                # Get database configuration
                result = await session.execute(text("""
                    SELECT name, setting, unit
                    FROM pg_settings 
                    WHERE name IN (
                        'shared_buffers', 'effective_cache_size', 
                        'work_mem', 'maintenance_work_mem'
                    )
                """))
                
                config_values = {row.name: row.setting for row in result}
                
                # Get buffer cache hit ratio
                result = await session.execute(text("""
                    SELECT CASE 
                        WHEN sum(heap_blks_hit + heap_blks_read) = 0 THEN 1.0
                        ELSE sum(heap_blks_hit)::float / sum(heap_blks_hit + heap_blks_read)
                    END as hit_ratio
                    FROM pg_statio_user_tables
                """))
                hit_ratio = result.scalar() or 0
                
                # Get checkpoint and WAL statistics
                result = await session.execute(text("""
                    SELECT 
                        checkpoint_write_time,
                        checkpoint_sync_time
                    FROM pg_stat_bgwriter
                """))
                checkpoint_stats = result.fetchone()
                
                # Get temporary file statistics
                result = await session.execute(text("""
                    SELECT 
                        sum(temp_files) as temp_files_count,
                        sum(temp_bytes) / (1024*1024) as temp_files_size_mb
                    FROM pg_stat_database
                """))
                temp_stats = result.fetchone()
                
                return DatabaseResourceMetrics(
                    shared_buffers_mb=self._parse_pg_size(config_values.get('shared_buffers', '0')),
                    effective_cache_size_mb=self._parse_pg_size(config_values.get('effective_cache_size', '0')),
                    work_mem_mb=self._parse_pg_size(config_values.get('work_mem', '0')),
                    maintenance_work_mem_mb=self._parse_pg_size(config_values.get('maintenance_work_mem', '0')),
                    buffer_cache_hit_ratio=hit_ratio * 100,
                    checkpoint_write_time_ms=checkpoint_stats.checkpoint_write_time if checkpoint_stats else 0,
                    wal_write_latency_ms=0.0,  # Not directly available
                    temp_files_count=temp_stats.temp_files_count if temp_stats else 0,
                    temp_files_size_mb=temp_stats.temp_files_size_mb if temp_stats else 0
                )
                
        except Exception as e:
            self.logger.error(f"Error collecting database metrics: {e}")
            return DatabaseResourceMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    def _parse_pg_size(self, size_str: str) -> float:
        """Parse PostgreSQL size string to MB"""
        try:
            if not size_str:
                return 0.0
            
            size_str = size_str.upper()
            
            if 'GB' in size_str:
                return float(size_str.replace('GB', '')) * 1024
            elif 'MB' in size_str:
                return float(size_str.replace('MB', ''))
            elif 'KB' in size_str:
                return float(size_str.replace('KB', '')) / 1024
            else:
                # Assume it's in 8KB blocks (PostgreSQL default)
                return float(size_str) * 8 / 1024
                
        except Exception:
            return 0.0
    
    def _identify_bottlenecks(
        self,
        cpu: CPUMetrics,
        memory: MemoryMetrics,
        disk: DiskMetrics,
        network: NetworkMetrics,
        database: DatabaseResourceMetrics
    ) -> List[str]:
        """
Identify system bottlenecks"""
        bottlenecks = []
        
        # CPU bottlenecks
        if cpu.overall_percent > self.thresholds['cpu_critical']:
            bottlenecks.append("Critical CPU utilization")
        elif cpu.overall_percent > self.thresholds['cpu_warning']:
            bottlenecks.append("High CPU utilization")
        
        if cpu.iowait_percent > 20:
            bottlenecks.append("High I/O wait time")
        
        # Memory bottlenecks
        if memory.used_percent > self.thresholds['memory_critical']:
            bottlenecks.append("Critical memory utilization")
        elif memory.used_percent > self.thresholds['memory_warning']:
            bottlenecks.append("High memory utilization")
        
        if memory.swap_percent > 10:
            bottlenecks.append("Excessive swap usage")
        
        # Disk bottlenecks
        if disk.used_percent > self.thresholds['disk_usage_critical']:
            bottlenecks.append("Critical disk space")
        elif disk.used_percent > self.thresholds['disk_usage_warning']:
            bottlenecks.append("Low disk space")
        
        total_iops = disk.read_iops + disk.write_iops
        if total_iops > self.thresholds['disk_iops_critical']:
            bottlenecks.append("Critical disk I/O load")
        elif total_iops > self.thresholds['disk_iops_warning']:
            bottlenecks.append("High disk I/O load")
        
        # Network bottlenecks
        if network.bandwidth_utilization_percent > self.thresholds['network_critical']:
            bottlenecks.append("Critical network utilization")
        elif network.bandwidth_utilization_percent > self.thresholds['network_warning']:
            bottlenecks.append("High network utilization")
        
        # Database-specific bottlenecks
        if database.buffer_cache_hit_ratio < 80:
            bottlenecks.append("Low database cache hit ratio")
        
        if database.temp_files_size_mb > 1000:  # > 1GB
            bottlenecks.append("Excessive temporary file usage")
        
        return bottlenecks
    
    def _determine_overall_status(
        self,
        cpu: CPUMetrics,
        memory: MemoryMetrics,
        disk: DiskMetrics,
        network: NetworkMetrics
    ) -> ResourceStatus:
        """Determine overall resource status"""
        
        critical_count = 0
        warning_count = 0
        
        # CPU status
        if cpu.overall_percent > self.thresholds['cpu_critical']:
            critical_count += 1
        elif cpu.overall_percent > self.thresholds['cpu_warning']:
            warning_count += 1
        
        # Memory status
        if memory.used_percent > self.thresholds['memory_critical']:
            critical_count += 1
        elif memory.used_percent > self.thresholds['memory_warning']:
            warning_count += 1
        
        # Disk status
        if disk.used_percent > self.thresholds['disk_usage_critical']:
            critical_count += 1
        elif disk.used_percent > self.thresholds['disk_usage_warning']:
            warning_count += 1
        
        # Network status
        if network.bandwidth_utilization_percent > self.thresholds['network_critical']:
            critical_count += 1
        elif network.bandwidth_utilization_percent > self.thresholds['network_warning']:
            warning_count += 1
        
        # Determine overall status
        if critical_count >= 3:
            return ResourceStatus.EMERGENCY
        elif critical_count >= 1:
            return ResourceStatus.CRITICAL
        elif warning_count >= 2:
            return ResourceStatus.WARNING
        elif warning_count >= 1:
            return ResourceStatus.NORMAL
        else:
            return ResourceStatus.OPTIMAL
    
    def _generate_recommendations(
        self, 
        bottlenecks: List[str], 
        status: ResourceStatus
    ) -> List[str]:
        """
Generate optimization recommendations based on bottlenecks"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if "CPU utilization" in bottleneck:
                recommendations.extend([
                    "Review and optimize slow queries",
                    "Consider adding CPU cores or upgrading processor",
                    "Implement query result caching"
                ])
            
            elif "memory utilization" in bottleneck:
                recommendations.extend([
                    "Increase available system memory",
                    "Optimize database shared_buffers configuration",
                    "Review memory-intensive queries"
                ])
            
            elif "disk space" in bottleneck:
                recommendations.extend([
                    "Clean up old log files and temporary data",
                    "Implement data archival strategy",
                    "Add additional storage capacity"
                ])
            
            elif "disk I/O" in bottleneck:
                recommendations.extend([
                    "Optimize database indexes",
                    "Consider SSD storage upgrade",
                    "Review and tune query performance"
                ])
            
            elif "network utilization" in bottleneck:
                recommendations.extend([
                    "Optimize data transfer patterns",
                    "Implement connection pooling",
                    "Consider network bandwidth upgrade"
                ])
            
            elif "cache hit ratio" in bottleneck:
                recommendations.extend([
                    "Increase shared_buffers setting",
                    "Review query patterns and add indexes",
                    "Consider database tuning"
                ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Limit to top 5 recommendations
    
    async def _process_snapshot(self, snapshot: ResourceSnapshot) -> None:
        """Process resource snapshot"""
        try:
            # Store in history
            self.resource_history.append(snapshot)
            
            # Cache latest snapshot
            await self.cache.set(
                "resource_monitor:latest",
                json.dumps(snapshot.to_dict()),
                expire=300
            )
            
            # Check for alerts
            if snapshot.overall_status in [ResourceStatus.CRITICAL, ResourceStatus.EMERGENCY]:
                await self._send_resource_alert(snapshot)
            
        except Exception as e:
            self.logger.error(f"Error processing resource snapshot: {e}")
    
    async def _send_resource_alert(self, snapshot: ResourceSnapshot) -> None:
        """Send resource alert"""
        try:
            alert = {
                "type": "resource_alert",
                "severity": "critical" if snapshot.overall_status == ResourceStatus.CRITICAL else "emergency",
                "message": f"Resource status: {snapshot.overall_status.value}",
                "bottlenecks": snapshot.bottlenecks,
                "recommendations": snapshot.recommendations,
                "timestamp": snapshot.timestamp.isoformat(),
                "metrics_summary": {
                    "cpu_percent": snapshot.cpu_metrics.overall_percent,
                    "memory_percent": snapshot.memory_metrics.used_percent,
                    "disk_percent": snapshot.disk_metrics.used_percent,
                    "network_percent": snapshot.network_metrics.bandwidth_utilization_percent
                }
            }
            
            # Store alert
            await self.cache.lpush(
                "resource_monitor:alerts",
                json.dumps(alert)
            )
            
            self.logger.warning(f"Resource alert: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Error sending resource alert: {e}")
    
    async def _calculate_baseline_average(
        self, 
        snapshots: List[ResourceSnapshot]
    ) -> ResourceSnapshot:
        """Calculate average baseline from multiple snapshots"""
        if not snapshots:
            return True
        
        # Calculate averages for each metric type
        cpu_values = {
            'overall_percent': statistics.mean(s.cpu_metrics.overall_percent for s in snapshots),
            'user_percent': statistics.mean(s.cpu_metrics.user_percent for s in snapshots),
            'system_percent': statistics.mean(s.cpu_metrics.system_percent for s in snapshots),
            'idle_percent': statistics.mean(s.cpu_metrics.idle_percent for s in snapshots),
            'iowait_percent': statistics.mean(s.cpu_metrics.iowait_percent for s in snapshots),
            'load_average_1m': statistics.mean(s.cpu_metrics.load_average_1m for s in snapshots),
            'load_average_5m': statistics.mean(s.cpu_metrics.load_average_5m for s in snapshots),
            'load_average_15m': statistics.mean(s.cpu_metrics.load_average_15m for s in snapshots)
        }
        
        # Create baseline snapshot (simplified)
        baseline_cpu = CPUMetrics(
            overall_percent=cpu_values['overall_percent'],
            per_core_percent=[],
            user_percent=cpu_values['user_percent'],
            system_percent=cpu_values['system_percent'],
            idle_percent=cpu_values['idle_percent'],
            iowait_percent=cpu_values['iowait_percent'],
            load_average_1m=cpu_values['load_average_1m'],
            load_average_5m=cpu_values['load_average_5m'],
            load_average_15m=cpu_values['load_average_15m'],
            context_switches_per_sec=0,
            interrupts_per_sec=0
        )
        
        # Use the last snapshot as template and update with averages
        baseline = snapshots[-1]
        baseline.cpu_metrics = baseline_cpu
        baseline.timestamp = datetime.utcnow()
        
        return baseline
    
    async def get_resource_summary(self) -> Dict[str, Any]:
        """
Get current resource summary"""
        try:
            if not self.resource_history:
                return {"error": "No resource data available", "monitoring_active": self.monitoring_active}
            
            latest = self.resource_history[-1]
            
            summary = {
                "monitoring_active": self.monitoring_active,
                "last_update": latest.timestamp.isoformat(),
                "overall_status": latest.overall_status.value,
                "current_metrics": {
                    "cpu_percent": latest.cpu_metrics.overall_percent,
                    "memory_percent": latest.memory_metrics.used_percent,
                    "disk_percent": latest.disk_metrics.used_percent,
                    "network_percent": latest.network_metrics.bandwidth_utilization_percent
                },
                "bottlenecks": latest.bottlenecks,
                "recommendations": latest.recommendations,
                "history_points": len(self.resource_history),
                "baseline_established": self.baseline_metrics is not None
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting resource summary: {e}")
            return {"error": str(e)}
    
    async def get_resource_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get resource history"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_snapshots = [
                snapshot.to_dict() for snapshot in self.resource_history
                if snapshot.timestamp >= cutoff_time
            ]
            
            return recent_snapshots
            
        except Exception as e:
            self.logger.error(f"Error getting resource history: {e}")
            return []
    
    async def get_capacity_planning_report(self) -> Dict[str, Any]:
        """Generate capacity planning report"""
        try:
            if len(self.resource_history) < 100:  # Need sufficient data
                return {"error": "Insufficient data for capacity planning"}
            
            # Analyze trends over different periods
            recent_24h = [s for s in self.resource_history if s.timestamp >= datetime.utcnow() - timedelta(hours=24)]
            recent_7d = [s for s in self.resource_history if s.timestamp >= datetime.utcnow() - timedelta(days=7)]
            
            # Calculate growth rates
            cpu_trend = self._calculate_trend([s.cpu_metrics.overall_percent for s in recent_7d])
            memory_trend = self._calculate_trend([s.memory_metrics.used_percent for s in recent_7d])
            disk_trend = self._calculate_trend([s.disk_metrics.used_percent for s in recent_7d])
            
            # Project future capacity needs
            projections = {
                "cpu": self._project_capacity(cpu_trend, 90.0),  # 90% threshold
                "memory": self._project_capacity(memory_trend, 90.0),
                "disk": self._project_capacity(disk_trend, 90.0)
            }
            
            report = {
                "analysis_period_days": 7,
                "data_points": len(recent_7d),
                "current_utilization": {
                    "cpu_percent": recent_24h[-1].cpu_metrics.overall_percent if recent_24h else 0,
                    "memory_percent": recent_24h[-1].memory_metrics.used_percent if recent_24h else 0,
                    "disk_percent": recent_24h[-1].disk_metrics.used_percent if recent_24h else 0
                },
                "growth_trends": {
                    "cpu_percent_per_day": cpu_trend,
                    "memory_percent_per_day": memory_trend,
                    "disk_percent_per_day": disk_trend
                },
                "capacity_projections": projections,
                "recommendations": self._generate_capacity_recommendations(projections),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating capacity planning report: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) from values"""
        if len(values) < 2:
            return 0.0
        
        try:
            # Simple linear regression
            n = len(values)
            x_values = list(range(n))
            
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(values)
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator == 0:
                return 0.0
            
            slope = numerator / denominator
            return slope
            
        except Exception:
            return 0.0
    
    def _project_capacity(self, trend: float, threshold: float) -> Dict[str, Any]:
        """
Project when capacity threshold will be reached"""
        try:
            if trend <= 0:
                return {"days_to_threshold": None, "action_needed": False}
            
            # Assume current utilization and project forward
            current_utilization = 50.0  # Default assumption
            if self.resource_history:
                # Use actual current utilization based on context
                pass
            
            days_to_threshold = (threshold - current_utilization) / trend
            
            return {
                "days_to_threshold": max(0, days_to_threshold),
                "action_needed": days_to_threshold < 30,  # Action needed if < 30 days
                "urgency": "high" if days_to_threshold < 7 else "medium" if days_to_threshold < 30 else "low"
            }
            
        except Exception:
            return {"days_to_threshold": None, "action_needed": False}
    
    def _generate_capacity_recommendations(self, projections: Dict[str, Any]) -> List[str]:
        """Generate capacity planning recommendations"""
        recommendations = []
        
        for resource, projection in projections.items():
            if projection.get("action_needed"):
                days = projection.get("days_to_threshold", 0)
                if days < 7:
                    recommendations.append(f"URGENT: {resource.upper()} capacity will be exceeded in {days:.1f} days")
                elif days < 30:
                    recommendations.append(f"Plan {resource.upper()} capacity upgrade within {days:.1f} days")
        
        if not recommendations:
            recommendations.append("Current capacity trends are sustainable")
        
        return recommendations
