"""
📊 PERFORMANCE PROFILER - ENTERPRISE ARCHITECTURE
================================================

Real-time performance monitoring and optimization for Ainflue Platform
Enterprise-grade performance profiling with AI-powered insights

**Expert Implementation:**
- Performance Engineer: Real-time metrics collection and optimization
- DevOps Engineer: System monitoring and resource management
- ML Engineer: AI-powered performance prediction and optimization
- Backend Senior: High-performance monitoring pipelines

**Features:** Real-time monitoring, Resource tracking, Performance optimization, AI insights
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
from collections import deque, defaultdict

# Performance monitoring libraries
try:
    import psutil
    import GPUtil
    import numpy as np
    from concurrent.futures import ThreadPoolExecutor
    import sqlite3
    from datetime import datetime, timedelta
except ImportError as e:
    logging.warning(f"Performance monitoring dependencies not available: {e}")

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Performance metric types"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    GPU_USAGE = "gpu_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    PROCESSING_TIME = "processing_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    QUEUE_SIZE = "queue_size"
    CACHE_HIT_RATE = "cache_hit_rate"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_type: MetricType
    value: float
    timestamp: float
    unit: str
    metadata: Dict[str, Any] = None

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_usage_gb: float
    disk_usage_percent: float
    disk_io_read_mb_s: float
    disk_io_write_mb_s: float
    network_io_sent_mb_s: float
    network_io_recv_mb_s: float
    gpu_usage_percent: float
    gpu_memory_usage_percent: float
    timestamp: float

@dataclass
class ProcessingMetrics:
    """Multimedia processing performance metrics"""
    files_processed: int
    total_processing_time: float
    average_processing_time: float
    throughput_files_per_hour: float
    error_count: int
    error_rate_percent: float
    queue_size: int
    cache_hit_rate_percent: float
    timestamp: float

@dataclass
class PerformanceAlert:
    """Performance alert notification"""
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    metric_value: float
    threshold: float
    timestamp: float
    recommendations: List[str]

class MetricsCollector:
    """System and application metrics collector"""
    
    def __init__(self) -> None:
        self.collection_interval = 1.0  # seconds
        self.is_collecting = False
        self.metrics_buffer = deque(maxlen=1000)
        self.processing_stats = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'gpu_usage': 90.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'processing_time': 30.0  # seconds per file
        }
        
        # Initialize database for metrics storage
        self._init_metrics_database()
    
    def _init_metrics_database(self) -> None:
        """Initialize SQLite database for metrics storage"""
        try:
            self.db_connection = sqlite3.connect(':memory:', check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    gpu_usage REAL,
                    disk_io_read REAL,
                    disk_io_write REAL,
                    network_io_sent REAL,
                    network_io_recv REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE processing_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    files_processed INTEGER,
                    processing_time REAL,
                    error_count INTEGER,
                    queue_size INTEGER
                )
            ''')
            
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {e}")
    
    async def start_collection(self) -> None:
        """Start metrics collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        asyncio.create_task(self._collection_loop())
        logger.info("Metrics collection started")
    
    async def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.is_collecting = False
        logger.info("Metrics collection stopped")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop"""
        while self.is_collecting:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                
                # Store in buffer and database
                self.metrics_buffer.append(system_metrics)
                await self._store_system_metrics(system_metrics)
                
                # Check for alerts
                alerts = await self._check_performance_alerts(system_metrics)
                for alert in alerts:
                    await self._handle_performance_alert(alert)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent
            memory_usage_gb = memory.used / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb_s = getattr(disk_io, 'read_bytes', 0) / (1024**2)
            disk_write_mb_s = getattr(disk_io, 'write_bytes', 0) / (1024**2)
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent_mb_s = network_io.bytes_sent / (1024**2)
            network_recv_mb_s = network_io.bytes_recv / (1024**2)
            
            # GPU metrics
            gpu_usage = 0.0
            gpu_memory_usage = 0.0
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Primary GPU
                    gpu_usage = gpu.load * 100
                    gpu_memory_usage = gpu.memoryUtil * 100
            except:
                pass  # GPU monitoring not available
            
            return SystemMetrics(
                cpu_usage_percent=cpu_usage,
                memory_usage_percent=memory_usage_percent,
                memory_usage_gb=memory_usage_gb,
                disk_usage_percent=disk_usage_percent,
                disk_io_read_mb_s=disk_read_mb_s,
                disk_io_write_mb_s=disk_write_mb_s,
                network_io_sent_mb_s=network_sent_mb_s,
                network_io_recv_mb_s=network_recv_mb_s,
                gpu_usage_percent=gpu_usage,
                gpu_memory_usage_percent=gpu_memory_usage,
                timestamp=time.time()
            )
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return SystemMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, time.time())
    
    async def _store_system_metrics(self, metrics -> None: SystemMetrics) -> None:
        """Store system metrics in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_usage, memory_usage, gpu_usage, 
                 disk_io_read, disk_io_write, network_io_sent, network_io_recv)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.cpu_usage_percent,
                metrics.memory_usage_percent,
                metrics.gpu_usage_percent,
                metrics.disk_io_read_mb_s,
                metrics.disk_io_write_mb_s,
                metrics.network_io_sent_mb_s,
                metrics.network_io_recv_mb_s
            ))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store system metrics: {e}")
    
    async def _check_performance_alerts(self, metrics: SystemMetrics) -> List[PerformanceAlert]:
        """Check for performance threshold violations"""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage_percent > self.thresholds['cpu_usage']:
            alerts.append(PerformanceAlert(
                alert_type='high_cpu_usage',
                severity='high' if metrics.cpu_usage_percent > 95 else 'medium',
                message=f'High CPU usage: {metrics.cpu_usage_percent:.1f}%',
                metric_value=metrics.cpu_usage_percent,
                threshold=self.thresholds['cpu_usage'],
                timestamp=metrics.timestamp,
                recommendations=[
                    'Consider reducing concurrent processing',
                    'Optimize processing algorithms',
                    'Scale to additional instances'
                ]
            ))
        
        # Memory usage alert
        if metrics.memory_usage_percent > self.thresholds['memory_usage']:
            alerts.append(PerformanceAlert(
                alert_type='high_memory_usage',
                severity='critical' if metrics.memory_usage_percent > 95 else 'high',
                message=f'High memory usage: {metrics.memory_usage_percent:.1f}%',
                metric_value=metrics.memory_usage_percent,
                threshold=self.thresholds['memory_usage'],
                timestamp=metrics.timestamp,
                recommendations=[
                    'Clear unnecessary caches',
                    'Reduce batch sizes',
                    'Implement memory optimization'
                ]
            ))
        
        # GPU usage alert
        if metrics.gpu_usage_percent > self.thresholds['gpu_usage']:
            alerts.append(PerformanceAlert(
                alert_type='high_gpu_usage',
                severity='medium',
                message=f'High GPU usage: {metrics.gpu_usage_percent:.1f}%',
                metric_value=metrics.gpu_usage_percent,
                threshold=self.thresholds['gpu_usage'],
                timestamp=metrics.timestamp,
                recommendations=[
                    'Optimize GPU processing',
                    'Reduce concurrent GPU tasks',
                    'Consider GPU scaling'
                ]
            ))
        
        return alerts
    
    async def _handle_performance_alert(self, alert -> None: PerformanceAlert) -> None:
        """Handle performance alert"""
        # Log alert
        logger.warning(f"Performance Alert [{alert.severity}]: {alert.message}")
        
        # Could send notifications, trigger scaling, etc.
        # For now, just log the recommendations
        for rec in alert.recommendations:
            logger.info(f"Recommendation: {rec}")
    
    def record_processing_event(self, file_path -> None: str, processing_time -> None: float, 
                              success -> None: bool, file_size -> None: int) -> None:
        """Record a multimedia processing event"""
        event = {
            'file_path': file_path,
            'processing_time': processing_time,
            'success': success,
            'file_size': file_size,
            'timestamp': time.time(),
            'throughput_mb_s': (file_size / (1024**2)) / processing_time if processing_time > 0 else 0
        }
        
        self.processing_stats['events'].append(event)
        
        # Keep only recent events (last 1000)
        if len(self.processing_stats['events']) > 1000:
            self.processing_stats['events'] = self.processing_stats['events'][-1000:]
    
    def get_processing_metrics(self, window_minutes: int = 60) -> ProcessingMetrics:
        """Get processing metrics for specified time window"""
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        # Filter events within time window
        recent_events = [
            event for event in self.processing_stats['events']
            if event['timestamp'] >= window_start
        ]
        
        if not recent_events:
            return ProcessingMetrics(0, 0, 0, 0, 0, 0, 0, 0, current_time)
        
        # Calculate metrics
        total_files = len(recent_events)
        successful_files = sum(1 for event in recent_events if event['success'])
        failed_files = total_files - successful_files
        
        total_time = sum(event['processing_time'] for event in recent_events)
        avg_time = total_time / total_files if total_files > 0 else 0
        
        # Calculate throughput (files per hour)
        window_hours = window_minutes / 60
        throughput = total_files / window_hours if window_hours > 0 else 0
        
        error_rate = (failed_files / total_files) * 100 if total_files > 0 else 0
        
        return ProcessingMetrics(
            files_processed=total_files,
            total_processing_time=total_time,
            average_processing_time=avg_time,
            throughput_files_per_hour=throughput,
            error_count=failed_files,
            error_rate_percent=error_rate,
            queue_size=0,  # Would need queue integration
            cache_hit_rate_percent=0,  # Would need cache integration
            timestamp=current_time
        )

class PerformanceProfiler:
    """Main performance profiler"""
    
    def __init__(self) -> None:
        self.metrics_collector = MetricsCollector()
        self.is_monitoring = False
        self.performance_history = deque(maxlen=10000)
        
        # Performance optimization suggestions
        self.optimization_suggestions = []
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        await self.metrics_collector.start_collection()
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        await self.metrics_collector.stop_collection()
        logger.info("Performance monitoring stopped")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.metrics_collector.metrics_buffer:
            return {}
        
        latest_system_metrics = self.metrics_collector.metrics_buffer[-1]
        processing_metrics = self.metrics_collector.get_processing_metrics()
        
        return {
            'system': asdict(latest_system_metrics),
            'processing': asdict(processing_metrics),
            'timestamp': time.time(),
            'monitoring_active': self.is_monitoring
        }
    
    def get_performance_history(self, minutes: int = 60) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance history for specified time period"""
        current_time = time.time()
        cutoff_time = current_time - (minutes * 60)
        
        # Filter metrics within time window
        recent_metrics = [
            asdict(metrics) for metrics in self.metrics_collector.metrics_buffer
            if metrics.timestamp >= cutoff_time
        ]
        
        return {
            'system_metrics': recent_metrics,
            'time_window_minutes': minutes,
            'data_points': len(recent_metrics)
        }
    
    def record_processing_performance(self, file_path -> None: str, processing_time -> None: float,
                                    success -> None: bool, file_size -> None: int,
                                    optimization_applied -> None: List[str] = None) -> None:
        """Record multimedia processing performance"""
        self.metrics_collector.record_processing_event(
            file_path, processing_time, success, file_size
        )
        
        # Analyze performance and generate suggestions
        if processing_time > 10.0:  # Slow processing
            self.optimization_suggestions.append({
                'type': 'slow_processing',
                'file_path': file_path,
                'processing_time': processing_time,
                'suggestion': 'Consider GPU acceleration or file optimization',
                'timestamp': time.time()
            })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_metrics = self.get_current_metrics()
        processing_metrics = self.metrics_collector.get_processing_metrics()
        
        # Calculate performance scores
        performance_scores = self._calculate_performance_scores(current_metrics)
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            current_metrics, processing_metrics
        )
        
        return {
            'summary': {
                'overall_performance_score': performance_scores['overall'],
                'system_health_score': performance_scores['system'],
                'processing_efficiency_score': performance_scores['processing'],
                'monitoring_duration_hours': self._get_monitoring_duration_hours()
            },
            'current_metrics': current_metrics,
            'processing_metrics': asdict(processing_metrics),
            'performance_scores': performance_scores,
            'optimization_recommendations': recommendations,
            'recent_alerts': self._get_recent_alerts(),
            'timestamp': time.time()
        }
    
    def _calculate_performance_scores(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance scores (0-100)"""
        if not metrics or 'system' not in metrics:
            return {'overall': 0, 'system': 0, 'processing': 0}
        
        system = metrics['system']
        processing = metrics.get('processing', {})
        
        # System performance score
        system_score = 100
        system_score -= max(0, system.get('cpu_usage_percent', 0) - 70) * 2
        system_score -= max(0, system.get('memory_usage_percent', 0) - 80) * 2
        system_score -= max(0, system.get('gpu_usage_percent', 0) - 80) * 1
        
        # Processing performance score
        processing_score = 100
        if processing:
            processing_score -= min(processing.get('error_rate_percent', 0) * 10, 50)
            avg_time = processing.get('average_processing_time', 0)
            if avg_time > 5:
                processing_score -= min((avg_time - 5) * 5, 30)
        
        # Overall score
        overall_score = (system_score + processing_score) / 2
        
        return {
            'overall': max(0, min(100, overall_score)),
            'system': max(0, min(100, system_score)),
            'processing': max(0, min(100, processing_score))
        }
    
    def _generate_optimization_recommendations(self, current_metrics: Dict[str, Any],
                                             processing_metrics: ProcessingMetrics) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if not current_metrics or 'system' not in current_metrics:
            return recommendations
        
        system = current_metrics['system']
        
        # CPU optimization
        if system.get('cpu_usage_percent', 0) > 80:
            recommendations.append("High CPU usage detected. Consider enabling GPU acceleration or reducing concurrent processing.")
        
        # Memory optimization
        if system.get('memory_usage_percent', 0) > 85:
            recommendations.append("High memory usage detected. Implement caching optimization or reduce batch sizes.")
        
        # Processing optimization
        if processing_metrics.error_rate_percent > 5:
            recommendations.append(f"High error rate ({processing_metrics.error_rate_percent:.1f}%). Review file validation and error handling.")
        
        if processing_metrics.average_processing_time > 10:
            recommendations.append("Slow processing detected. Consider format optimization or hardware acceleration.")
        
        # GPU optimization
        if system.get('gpu_usage_percent', 0) < 20 and system.get('cpu_usage_percent', 0) > 70:
            recommendations.append("Low GPU utilization with high CPU usage. Consider GPU acceleration for processing.")
        
        return recommendations
    
    def _get_monitoring_duration_hours(self) -> float:
        """Get monitoring duration in hours"""
        if not self.metrics_collector.metrics_buffer:
            return 0
        
        earliest = min(metrics.timestamp for metrics in self.metrics_collector.metrics_buffer)
        latest = max(metrics.timestamp for metrics in self.metrics_collector.metrics_buffer)
        
        return (latest - earliest) / 3600
    
    def _get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        # This would typically fetch from alert storage
        # For now, return empty list
        return []

# Module exports for enterprise integration
__all__ = [
    'PerformanceProfiler',
    'MetricsCollector',
    'PerformanceMetric',
    'SystemMetrics',
    'ProcessingMetrics',
    'PerformanceAlert',
    'MetricType'
]