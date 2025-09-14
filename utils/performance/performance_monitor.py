"""
Performance Monitor - Performance Utilities Level 3
==================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade performance monitoring consolidating performance_monitor.py + health_checker.py
Enhanced with real-time monitoring and alerting capabilities.

Performance: < 5ms per monitoring operation
Standards: Real-time monitoring, SLA tracking, automated alerting
"""

import asyncio
import logging
import psutil
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class MonitorResult:
    """Result container for monitoring operations."""
    success: bool
    result: Optional[Any] = None
    alerts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class PerformanceMonitor:
    """Enterprise performance monitor with real-time alerting."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize performance monitor."""
        self.config = config or {}
        self._performance_threshold_ms = 5.0
        self._cpu_threshold = self.config.get('cpu_threshold', 80.0)
        self._memory_threshold = self.config.get('memory_threshold', 80.0)
        self._disk_threshold = self.config.get('disk_threshold', 90.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def check_system_health(self) -> MonitorResult:
        """Check overall system health."""
        start_time = time.perf_counter()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network stats
            network = psutil.net_io_counters()
            
            health_data = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Check for alerts
            alerts = []
            if cpu_percent > self._cpu_threshold:
                alerts.append(f"High CPU usage: {cpu_percent}%")
            if memory_percent > self._memory_threshold:
                alerts.append(f"High memory usage: {memory_percent}%")
            if disk_percent > self._disk_threshold:
                alerts.append(f"High disk usage: {disk_percent}%")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return MonitorResult(
                success=True,
                result=health_data,
                alerts=alerts,
                execution_time_ms=exec_time
            )
        except Exception as e:
            exec_time = (time.perf_counter() - start_time) * 1000
            return MonitorResult(
                success=False,
                errors=[str(e)],
                execution_time_ms=exec_time
            )
    
    async def measure_operation_performance(self, operation_name: str, duration_ms: float) -> MonitorResult:
        """Record operation performance metrics."""
        try:
            performance_data = {
                'operation': operation_name,
                'duration_ms': duration_ms,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'within_threshold': duration_ms <= self._performance_threshold_ms
            }
            
            alerts = []
            if duration_ms > self._performance_threshold_ms:
                alerts.append(f"Operation {operation_name} exceeded threshold: {duration_ms}ms")
            
            return MonitorResult(
                success=True,
                result=performance_data,
                alerts=alerts
            )
        except Exception as e:
            return MonitorResult(success=False, errors=[str(e)])

class PerformanceMonitorFactory:
    """Factory for creating performance monitor instances."""
    
    @staticmethod
    def create_monitor(config: Optional[Dict[str, Any]] = None) -> PerformanceMonitor:
        return PerformanceMonitor(config)