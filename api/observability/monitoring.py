"""
Enterprise System Monitoring

Comprehensive system monitoring infrastructure for real-time performance tracking,
resource monitoring, and predictive alerting in the IA Influencer platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import asyncio
import psutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque, defaultdict
import json
import threading
from pathlib import Path


@dataclass
class SystemSnapshot:
    """System performance snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: int
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    load_average: Tuple[float, float, float]
    uptime_seconds: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_available_mb': self.memory_available_mb,
            'disk_usage_percent': self.disk_usage_percent,
            'disk_free_gb': self.disk_free_gb,
            'network_bytes_sent': self.network_bytes_sent,
            'network_bytes_recv': self.network_bytes_recv,
            'process_count': self.process_count,
            'load_average': self.load_average,
            'uptime_seconds': self.uptime_seconds
        }


class SystemMonitor:
    """Real-time system monitoring with predictive alerting."""
    
    def __init__(self, retention_hours: int = 24, collection_interval: int = 30):
        self.retention_hours = retention_hours
        self.collection_interval = collection_interval
        self.snapshots = deque(maxlen=int((retention_hours * 3600) / collection_interval))
        self.is_running = False
        self.monitor_thread = None
        self._lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 80.0, 
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'load_warning': 5.0,
            'load_critical': 10.0
        }
    
    def start_monitoring(self):
        """Start continuous system monitoring."""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logging.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                snapshot = self._collect_system_metrics()
                with self._lock:
                    self.snapshots.append(snapshot)
                
                # Check for anomalies
                self._check_performance_anomalies(snapshot)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> SystemSnapshot:
        """Collect comprehensive system metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Linux/Mac specific)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = (0.0, 0.0, 0.0)  # Windows fallback
        
        # System uptime
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        
        return SystemSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_mb=memory.available // (1024 * 1024),
            disk_usage_percent=(disk.used / disk.total) * 100,
            disk_free_gb=disk.free // (1024 * 1024 * 1024),
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            process_count=process_count,
            load_average=load_avg,
            uptime_seconds=int(uptime)
        )
    
    def _check_performance_anomalies(self, snapshot: SystemSnapshot):
        """Check for performance anomalies and potential issues."""
        anomalies = []
        
        # CPU anomalies
        if snapshot.cpu_percent >= self.thresholds['cpu_critical']:
            anomalies.append({
                'type': 'cpu_critical',
                'message': f"CPU usage critical: {snapshot.cpu_percent:.1f}%",
                'severity': 'critical'
            })
        elif snapshot.cpu_percent >= self.thresholds['cpu_warning']:
            anomalies.append({
                'type': 'cpu_warning',
                'message': f"CPU usage high: {snapshot.cpu_percent:.1f}%",
                'severity': 'warning'
            })
        
        # Memory anomalies
        if snapshot.memory_percent >= self.thresholds['memory_critical']:
            anomalies.append({
                'type': 'memory_critical',
                'message': f"Memory usage critical: {snapshot.memory_percent:.1f}%",
                'severity': 'critical'
            })
        elif snapshot.memory_percent >= self.thresholds['memory_warning']:
            anomalies.append({
                'type': 'memory_warning',
                'message': f"Memory usage high: {snapshot.memory_percent:.1f}%",
                'severity': 'warning'
            })
        
        # Disk anomalies
        if snapshot.disk_usage_percent >= self.thresholds['disk_critical']:
            anomalies.append({
                'type': 'disk_critical',
                'message': f"Disk usage critical: {snapshot.disk_usage_percent:.1f}%",
                'severity': 'critical'
            })
        elif snapshot.disk_usage_percent >= self.thresholds['disk_warning']:
            anomalies.append({
                'type': 'disk_warning',
                'message': f"Disk usage high: {snapshot.disk_usage_percent:.1f}%",
                'severity': 'warning'
            })
        
        # Load average anomalies
        current_load = snapshot.load_average[0]  # 1-minute load average
        if current_load >= self.thresholds['load_critical']:
            anomalies.append({
                'type': 'load_critical',
                'message': f"Load average critical: {current_load:.2f}",
                'severity': 'critical'
            })
        elif current_load >= self.thresholds['load_warning']:
            anomalies.append({
                'type': 'load_warning',
                'message': f"Load average high: {current_load:.2f}",
                'severity': 'warning'
            })
        
        # Log anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'critical':
                logging.error(f"System anomaly: {anomaly['message']}")
            else:
                logging.warning(f"System anomaly: {anomaly['message']}")
    
    def get_current_metrics(self) -> Optional[SystemSnapshot]:
        """Get the most recent system metrics."""
        with self._lock:
            return self.snapshots[-1] if self.snapshots else None
    
    def get_metrics_history(self, hours: int = 1) -> List[SystemSnapshot]:
        """Get system metrics history for specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            return [
                snapshot for snapshot in self.snapshots
                if snapshot.timestamp >= cutoff_time
            ]
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary statistics."""
        if not self.snapshots:
            return {"error": "No metrics available"}
        
        with self._lock:
            recent_snapshots = list(self.snapshots)[-100:]  # Last 100 snapshots
        
        if not recent_snapshots:
            return {"error": "No recent metrics available"}
        
        # Calculate statistics
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        memory_values = [s.memory_percent for s in recent_snapshots]
        disk_values = [s.disk_usage_percent for s in recent_snapshots]
        
        return {
            "monitoring_duration_hours": len(self.snapshots) * self.collection_interval / 3600,
            "total_snapshots": len(self.snapshots),
            "cpu": {
                "current": cpu_values[-1],
                "average": sum(cpu_values) / len(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values)
            },
            "memory": {
                "current": memory_values[-1], 
                "average": sum(memory_values) / len(memory_values),
                "min": min(memory_values),
                "max": max(memory_values)
            },
            "disk": {
                "current": disk_values[-1],
                "average": sum(disk_values) / len(disk_values),
                "min": min(disk_values),
                "max": max(disk_values)
            },
            "uptime_hours": recent_snapshots[-1].uptime_seconds / 3600,
            "timestamp": datetime.utcnow().isoformat()
        }


class PerformanceMonitor:
    """Application performance monitoring with business metrics tracking."""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics = defaultdict(lambda: deque(maxlen=10000))
        self.custom_metrics = {}
        self._lock = threading.Lock()
        
        # Business logic performance tracking
        self.content_processing_times = deque(maxlen=1000)
        self.ai_inference_times = deque(maxlen=1000)
        self.protection_scan_times = deque(maxlen=1000)
        self.collaboration_match_times = deque(maxlen=1000)
    
    def record_content_processing_time(self, processing_type: str, duration_ms: float, success: bool = True):
        """Record content processing performance."""
        timestamp = datetime.utcnow()
        
        metric_data = {
            'timestamp': timestamp,
            'type': processing_type,
            'duration_ms': duration_ms,
            'success': success
        }
        
        with self._lock:
            self.content_processing_times.append(metric_data)
            
            # Record in general metrics
            self.metrics[f"content.processing.{processing_type}"].append(metric_data)
            
            if success:
                self.metrics["content.processing.success_count"].append({
                    'timestamp': timestamp,
                    'value': 1
                })
            else:
                self.metrics["content.processing.error_count"].append({
                    'timestamp': timestamp,
                    'value': 1
                })
    
    def record_ai_inference_time(self, model_name: str, duration_ms: float, input_size: int = 0):
        """Record AI model inference performance."""
        timestamp = datetime.utcnow()
        
        metric_data = {
            'timestamp': timestamp,
            'model': model_name,
            'duration_ms': duration_ms,
            'input_size': input_size
        }
        
        with self._lock:
            self.ai_inference_times.append(metric_data)
            self.metrics[f"ai.inference.{model_name}"].append(metric_data)
    
    def record_protection_scan_time(self, scan_type: str, duration_ms: float, items_scanned: int):
        """Record content protection scan performance."""
        timestamp = datetime.utcnow()
        
        metric_data = {
            'timestamp': timestamp,
            'scan_type': scan_type,
            'duration_ms': duration_ms,
            'items_scanned': items_scanned
        }
        
        with self._lock:
            self.protection_scan_times.append(metric_data)
            self.metrics[f"protection.scan.{scan_type}"].append(metric_data)
    
    def record_collaboration_match_time(self, match_type: str, duration_ms: float, matches_found: int):
        """Record collaboration matching performance."""
        timestamp = datetime.utcnow()
        
        metric_data = {
            'timestamp': timestamp,
            'match_type': match_type,
            'duration_ms': duration_ms,
            'matches_found': matches_found
        }
        
        with self._lock:
            self.collaboration_match_times.append(metric_data)
            self.metrics[f"collaboration.matching.{match_type}"].append(metric_data)
    
    def get_content_performance_metrics(self) -> Dict:
        """Get content processing performance metrics."""
        with self._lock:
            processing_times = list(self.content_processing_times)
        
        if not processing_times:
            return {"error": "No content processing metrics available"}
        
        # Calculate statistics by type
        type_stats = defaultdict(lambda: {"times": [], "success_count": 0, "error_count": 0})
        
        for metric in processing_times:
            type_name = metric['type']
            type_stats[type_name]['times'].append(metric['duration_ms'])
            
            if metric['success']:
                type_stats[type_name]['success_count'] += 1
            else:
                type_stats[type_name]['error_count'] += 1
        
        # Build summary
        summary = {}
        for type_name, stats in type_stats.items():
            times = stats['times']
            total_requests = stats['success_count'] + stats['error_count']
            
            summary[type_name] = {
                "total_requests": total_requests,
                "success_count": stats['success_count'],
                "error_count": stats['error_count'],
                "success_rate": stats['success_count'] / total_requests if total_requests > 0 else 0,
                "avg_duration_ms": sum(times) / len(times) if times else 0,
                "min_duration_ms": min(times) if times else 0,
                "max_duration_ms": max(times) if times else 0,
                "p95_duration_ms": self._calculate_percentile(times, 0.95),
                "p99_duration_ms": self._calculate_percentile(times, 0.99)
            }
        
        return {
            "by_type": summary,
            "total_processing_events": len(processing_times),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_ai_performance_metrics(self) -> Dict:
        """Get AI model performance metrics."""
        with self._lock:
            inference_times = list(self.ai_inference_times)
        
        if not inference_times:
            return {"error": "No AI inference metrics available"}
        
        # Calculate statistics by model
        model_stats = defaultdict(lambda: {"times": [], "input_sizes": []})
        
        for metric in inference_times:
            model_name = metric['model']
            model_stats[model_name]['times'].append(metric['duration_ms'])
            if metric['input_size'] > 0:
                model_stats[model_name]['input_sizes'].append(metric['input_size'])
        
        # Build summary
        summary = {}
        for model_name, stats in model_stats.items():
            times = stats['times']
            input_sizes = stats['input_sizes']
            
            summary[model_name] = {
                "total_inferences": len(times),
                "avg_duration_ms": sum(times) / len(times) if times else 0,
                "min_duration_ms": min(times) if times else 0,
                "max_duration_ms": max(times) if times else 0,
                "p95_duration_ms": self._calculate_percentile(times, 0.95),
                "p99_duration_ms": self._calculate_percentile(times, 0.99),
                "avg_input_size": sum(input_sizes) / len(input_sizes) if input_sizes else 0,
                "throughput_per_second": len(times) / 3600 if times else 0  # Assuming 1-hour window
            }
        
        return {
            "by_model": summary,
            "total_inferences": len(inference_times),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_overall_performance_summary(self) -> Dict:
        """Get overall application performance summary."""
        return {
            "content_processing": self.get_content_performance_metrics(),
            "ai_inference": self.get_ai_performance_metrics(),
            "monitoring_active": True,
            "retention_hours": self.retention_hours,
            "timestamp": datetime.utcnow().isoformat()
        }


class ResourceMonitor:
    """Resource utilization and capacity monitoring."""
    
    def __init__(self):
        self.resource_usage = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
        
        # Resource thresholds for different services
        self.service_thresholds = {
            "content_upload": {"cpu": 70, "memory": 80, "disk": 85},
            "ai_processing": {"cpu": 80, "memory": 90, "disk": 75},
            "protection_scan": {"cpu": 75, "memory": 85, "disk": 90},
            "collaboration": {"cpu": 60, "memory": 70, "disk": 80}
        }
    
    def record_resource_usage(self, service_name: str, resource_type: str, usage_percent: float):
        """Record resource usage for a specific service."""
        timestamp = datetime.utcnow()
        
        usage_data = {
            'timestamp': timestamp,
            'service': service_name,
            'resource': resource_type,
            'usage_percent': usage_percent
        }
        
        with self._lock:
            key = f"{service_name}.{resource_type}"
            self.resource_usage[key].append(usage_data)
    
    def check_resource_thresholds(self) -> Dict:
        """Check if any resources are exceeding thresholds."""
        alerts = []
        
        with self._lock:
            for service_name, thresholds in self.service_thresholds.items():
                for resource_type, threshold in thresholds.items():
                    key = f"{service_name}.{resource_type}"
                    
                    if key in self.resource_usage:
                        recent_usage = list(self.resource_usage[key])[-10:]  # Last 10 measurements
                        
                        if recent_usage:
                            avg_usage = sum(u['usage_percent'] for u in recent_usage) / len(recent_usage)
                            
                            if avg_usage > threshold:
                                alerts.append({
                                    'service': service_name,
                                    'resource': resource_type,
                                    'current_usage': avg_usage,
                                    'threshold': threshold,
                                    'severity': 'critical' if avg_usage > threshold * 1.1 else 'warning'
                                })
        
        return {
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_resource_summary(self) -> Dict:
        """Get summary of resource utilization."""
        summary = {}
        
        with self._lock:
            for service_name in self.service_thresholds:
                service_summary = {}
                
                for resource_type in ['cpu', 'memory', 'disk']:
                    key = f"{service_name}.{resource_type}"
                    
                    if key in self.resource_usage:
                        recent_data = list(self.resource_usage[key])[-50:]  # Last 50 measurements
                        
                        if recent_data:
                            usage_values = [d['usage_percent'] for d in recent_data]
                            service_summary[resource_type] = {
                                'current': usage_values[-1],
                                'average': sum(usage_values) / len(usage_values),
                                'min': min(usage_values),
                                'max': max(usage_values),
                                'threshold': self.service_thresholds[service_name][resource_type]
                            }
                        else:
                            service_summary[resource_type] = {
                                'current': 0,
                                'average': 0,
                                'min': 0,
                                'max': 0,
                                'threshold': self.service_thresholds[service_name][resource_type]
                            }
                    else:
                        service_summary[resource_type] = {
                            'current': 0,
                            'average': 0,
                            'min': 0,
                            'max': 0,
                            'threshold': self.service_thresholds[service_name][resource_type]
                        }
                
                summary[service_name] = service_summary
        
        return {
            "services": summary,
            "threshold_alerts": self.check_resource_thresholds(),
            "timestamp": datetime.utcnow().isoformat()
        }
