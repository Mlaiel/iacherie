"""Performance Metrics and Monitoring System
Real-time performance tracking for multimedia processing operations.

This module provides comprehensive performance monitoring including resource usage,
processing time tracking, throughput analysis, and bottleneck identification.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import psutil
import time
import asyncio
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np
from contextlib import asynccontextmanager
import gc

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Metrics for a single processing operation"""
    operation_id: str
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Resource usage
    cpu_usage_start: float = 0.0
    cpu_usage_end: float = 0.0
    cpu_usage_avg: float = 0.0
    memory_usage_start: float = 0.0
    memory_usage_end: float = 0.0
    memory_usage_peak: float = 0.0
    gpu_usage_avg: Optional[float] = None
    
    # Processing details
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Performance indicators
    throughput: Optional[float] = None  # MB/s or operations/s
    efficiency_score: float = 0.0
    
    def finalize(self) -> None:
        """Finalize metrics calculation"""
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
            
            # Calculate throughput
            if self.input_size and self.duration > 0:
                self.throughput = (self.input_size / (1024 * 1024)) / self.duration  # MB/s
            
            # Calculate efficiency score
            self._calculate_efficiency_score()
    
    def _calculate_efficiency_score(self) -> None:
        """Calculate overall efficiency score"""
        factors = []
        
        # Time efficiency (faster is better)
        if self.duration:
            time_factor = max(0.0, 1.0 - min(self.duration / 300.0, 1.0))  # Normalize to 5 minutes
            factors.append(time_factor)
        
        # Resource efficiency (lower usage is better for same output)
        if self.cpu_usage_avg:
            cpu_factor = max(0.0, 1.0 - self.cpu_usage_avg / 100.0)
            factors.append(cpu_factor)
        
        # Quality factor
        if self.quality_score:
            factors.append(self.quality_score)
        
        # Success factor
        factors.append(1.0 if self.success else 0.0)
        
        self.efficiency_score = np.mean(factors) if factors else 0.0


@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: datetime
    
    # CPU metrics
    cpu_usage_overall: float = 0.0
    cpu_usage_per_core: List[float] = field(default_factory=list)
    cpu_frequency: float = 0.0
    cpu_temperature: Optional[float] = None
    
    # Memory metrics
    memory_total: float = 0.0
    memory_used: float = 0.0
    memory_available: float = 0.0
    memory_percentage: float = 0.0
    
    # Disk metrics
    disk_usage: Dict[str, float] = field(default_factory=dict)
    disk_io: Dict[str, float] = field(default_factory=dict)
    
    # Network metrics
    network_io: Dict[str, float] = field(default_factory=dict)
    
    # GPU metrics (if available)
    gpu_metrics: List[Dict[str, Any]] = field(default_factory=list)
    
    # Process metrics
    active_processes: int = 0
    multimedia_processes: int = 0


class ResourceMonitor:
    """Real-time system resource monitoring"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Monitoring parameters
        self.monitoring_interval = self.config.get('monitoring_interval', 1.0)  # seconds
        self.history_size = self.config.get('history_size', 1000)
        
        # Data storage
        self.metrics_history: deque = deque(maxlen=self.history_size)
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # GPU monitoring
        self.gpu_available = self._check_gpu_availability()
        
    def _check_gpu_availability(self) -> bool:
        """Check if GPU monitoring is available"""
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except:
            return False
    
    def start_monitoring(self) -> None:
        """Start continuous system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Continuous monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=None)
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk_usage = {}
            disk_io_counters = psutil.disk_io_counters()
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = usage.percent
                except:
                    pass
            
            # Network metrics
            network_io = {}
            net_io = psutil.net_io_counters()
            if net_io:
                network_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            
            # Process metrics
            processes = list(psutil.process_iter(['pid', 'name']))
            multimedia_keywords = ['ffmpeg', 'opencv', 'python']
            multimedia_processes = sum(1 for p in processes 
                                     if any(keyword in p.info['name'].lower() 
                                           for keyword in multimedia_keywords))
            
            # GPU metrics
            gpu_metrics = []
            if self.gpu_available:
                gpu_metrics = self._collect_gpu_metrics()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage_overall=cpu_usage,
                cpu_usage_per_core=cpu_per_core,
                cpu_frequency=cpu_freq.current if cpu_freq else 0.0,
                memory_total=memory.total / (1024**3),  # GB
                memory_used=memory.used / (1024**3),    # GB
                memory_available=memory.available / (1024**3),  # GB
                memory_percentage=memory.percent,
                disk_usage=disk_usage,
                network_io=network_io,
                gpu_metrics=gpu_metrics,
                active_processes=len(processes),
                multimedia_processes=multimedia_processes
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(timestamp=datetime.now())
    
    def _collect_gpu_metrics(self) -> List[Dict[str, Any]]:
        """Collect GPU metrics using nvidia-ml-py"""
        try:
            import pynvml
            
            gpu_metrics = []
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # GPU utilization
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Memory info
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Temperature
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temperature = None
                
                # Power
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    power = None
                
                gpu_metrics.append({
                    'gpu_id': i,
                    'utilization_gpu': utilization.gpu,
                    'utilization_memory': utilization.memory,
                    'memory_total': memory_info.total / (1024**3),  # GB
                    'memory_used': memory_info.used / (1024**3),    # GB
                    'memory_free': memory_info.free / (1024**3),    # GB
                    'temperature': temperature,
                    'power_usage': power
                })
            
            return gpu_metrics
            
        except Exception as e:
            self.logger.error(f"GPU metrics collection failed: {e}")
            return []
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_system_metrics()
    
    def get_metrics_history(self, duration_minutes: int = 10) -> List[SystemMetrics]:
        """Get metrics history for specified duration"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]


class PerformanceTracker:
    """Main performance tracking and analysis system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize resource monitor
        self.resource_monitor = ResourceMonitor(config)
        
        # Performance data storage
        self.operation_metrics: Dict[str, ProcessingMetrics] = {}
        self.completed_operations: deque = deque(maxlen=self.config.get('history_size', 10000))
        
        # Statistics
        self.operation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'success_count': 0,
            'average_duration': 0.0,
            'success_rate': 0.0,
            'average_throughput': 0.0
        })
        
        # Alerts and thresholds
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'cpu_usage': 90.0,
            'memory_usage': 85.0,
            'processing_time': 300.0,  # 5 minutes
            'error_rate': 10.0
        })
        
        self.alerts: List[Dict[str, Any]] = []
        
        # Start monitoring
        if self.config.get('auto_start_monitoring', True):
            self.resource_monitor.start_monitoring()
    
    @asynccontextmanager
    async def track_operation(self, operation_type -> None: str, operation_id -> None: Optional[str] = None) -> None:
        """Context manager for tracking operation performance"""
        if operation_id is None:
            operation_id = f"{operation_type}_{int(time.time() * 1000)}"
        
        # Initialize metrics
        start_metrics = self.resource_monitor.get_current_metrics()
        
        metrics = ProcessingMetrics(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=datetime.now(),
            cpu_usage_start=start_metrics.cpu_usage_overall if start_metrics else 0.0,
            memory_usage_start=start_metrics.memory_percentage if start_metrics else 0.0
        )
        
        self.operation_metrics[operation_id] = metrics
        
        try:
            yield metrics
            metrics.success = True
        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            self.logger.error(f"Operation {operation_id} failed: {e}")
            raise
        finally:
            # Finalize metrics
            metrics.end_time = datetime.now()
            end_metrics = self.resource_monitor.get_current_metrics()
            
            if end_metrics:
                metrics.cpu_usage_end = end_metrics.cpu_usage_overall
                metrics.memory_usage_end = end_metrics.memory_percentage
                
                # Calculate peak memory usage during operation
                history = self.resource_monitor.get_metrics_history(duration_minutes=1)
                if history:
                    operation_history = [m for m in history if m.timestamp >= metrics.start_time]
                    if operation_history:
                        metrics.memory_usage_peak = max(m.memory_percentage for m in operation_history)
                        metrics.cpu_usage_avg = np.mean([m.cpu_usage_overall for m in operation_history])
            
            metrics.finalize()
            
            # Store completed operation
            self.completed_operations.append(metrics)
            del self.operation_metrics[operation_id]
            
            # Update statistics
            self._update_operation_stats(metrics)
            
            # Check for alerts
            self._check_alerts(metrics)
    
    def _update_operation_stats(self, metrics -> None: ProcessingMetrics) -> None:
        """Update operation statistics"""
        op_type = metrics.operation_type
        stats = self.operation_stats[op_type]
        
        stats['count'] += 1
        if metrics.duration:
            stats['total_duration'] += metrics.duration
            stats['average_duration'] = stats['total_duration'] / stats['count']
        
        if metrics.success:
            stats['success_count'] += 1
        
        stats['success_rate'] = (stats['success_count'] / stats['count']) * 100
        
        if metrics.throughput:
            # Update rolling average throughput
            if 'throughput_values' not in stats:
                stats['throughput_values'] = deque(maxlen=100)
            stats['throughput_values'].append(metrics.throughput)
            stats['average_throughput'] = np.mean(stats['throughput_values'])
    
    def _check_alerts(self, metrics -> None: ProcessingMetrics) -> None:
        """Check for performance alerts"""
        alerts = []
        
        # High processing time
        if metrics.duration and metrics.duration > self.alert_thresholds['processing_time']:
            alerts.append({
                'type': 'high_processing_time',
                'severity': 'warning',
                'message': f"Operation {metrics.operation_id} took {metrics.duration:.2f}s",
                'timestamp': datetime.now()
            })
        
        # High resource usage
        if metrics.cpu_usage_avg > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"High CPU usage: {metrics.cpu_usage_avg:.1f}%",
                'timestamp': datetime.now()
            })
        
        if metrics.memory_usage_peak > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"High memory usage: {metrics.memory_usage_peak:.1f}%",
                'timestamp': datetime.now()
            })
        
        # Operation failure
        if not metrics.success:
            alerts.append({
                'type': 'operation_failure',
                'severity': 'error',
                'message': f"Operation {metrics.operation_id} failed: {metrics.error_message}",
                'timestamp': datetime.now()
            })
        
        self.alerts.extend(alerts)
        
        # Keep only recent alerts
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert['timestamp'] >= cutoff_time]
    
    def get_operation_stats(self, operation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get operation statistics"""
        if operation_type:
            return dict(self.operation_stats.get(operation_type, {}))
        return {op_type: dict(stats) for op_type, stats in self.operation_stats.items()}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        current_metrics = self.resource_monitor.get_current_metrics()
        
        health_score = 100.0
        issues = []
        
        if current_metrics:
            # CPU health
            if current_metrics.cpu_usage_overall > 90:
                health_score -= 20
                issues.append("High CPU usage")
            elif current_metrics.cpu_usage_overall > 75:
                health_score -= 10
                issues.append("Elevated CPU usage")
            
            # Memory health
            if current_metrics.memory_percentage > 90:
                health_score -= 25
                issues.append("High memory usage")
            elif current_metrics.memory_percentage > 80:
                health_score -= 15
                issues.append("Elevated memory usage")
            
            # GPU health
            for gpu in current_metrics.gpu_metrics:
                if gpu.get('utilization_gpu', 0) > 95:
                    health_score -= 15
                    issues.append(f"GPU {gpu['gpu_id']} high utilization")
        
        # Check recent operation success rate
        recent_ops = list(self.completed_operations)[-100:]  # Last 100 operations
        if recent_ops:
            success_rate = sum(1 for op in recent_ops if op.success) / len(recent_ops) * 100
            if success_rate < 90:
                health_score -= 20
                issues.append(f"Low success rate: {success_rate:.1f}%")
        
        health_status = "excellent" if health_score >= 90 else \
                       "good" if health_score >= 75 else \
                       "fair" if health_score >= 60 else \
                       "poor"
        
        return {
            'health_score': max(0.0, health_score),
            'status': health_status,
            'issues': issues,
            'timestamp': datetime.now(),
            'system_metrics': current_metrics
        }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent operations
        recent_ops = [op for op in self.completed_operations if op.start_time >= cutoff_time]
        
        if not recent_ops:
            return {'message': 'No operations in specified time period'}
        
        # Calculate summary statistics
        total_operations = len(recent_ops)
        successful_operations = sum(1 for op in recent_ops if op.success)
        failed_operations = total_operations - successful_operations
        
        durations = [op.duration for op in recent_ops if op.duration]
        throughputs = [op.throughput for op in recent_ops if op.throughput]
        
        # Group by operation type
        by_type = defaultdict(list)
        for op in recent_ops:
            by_type[op.operation_type].append(op)
        
        type_summaries = {}
        for op_type, ops in by_type.items():
            type_summaries[op_type] = {
                'count': len(ops),
                'success_rate': sum(1 for op in ops if op.success) / len(ops) * 100,
                'avg_duration': np.mean([op.duration for op in ops if op.duration]) if ops else 0,
                'avg_throughput': np.mean([op.throughput for op in ops if op.throughput]) if ops else 0
            }
        
        return {
            'time_period': f"Last {hours} hours",
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'overall_success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            'average_duration': np.mean(durations) if durations else 0,
            'median_duration': np.median(durations) if durations else 0,
            'average_throughput': np.mean(throughputs) if throughputs else 0,
            'by_operation_type': type_summaries,
            'recent_alerts_count': len([a for a in self.alerts if a['timestamp'] >= cutoff_time])
        }
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.resource_monitor.stop_monitoring()
        gc.collect()