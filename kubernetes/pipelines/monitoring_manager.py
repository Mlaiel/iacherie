"""IA Influencer Agent - Pipeline Metrics and Monitoring System
Enterprise-Grade Metrics Collection and Performance Monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive metrics collection and monitoring capabilities for pipeline
execution, performance tracking, and system observability.

Features:
- Real-time pipeline metrics collection
- Performance monitoring and analysis
- Integration with Prometheus and Grafana
- Custom metrics definition and tracking
- Alerting based on metrics thresholds

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from pathlib import Path

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .pipeline_manager import PipelineExecution, PipelineStatus

class MetricType(Enum):
    """
Metric type definitions"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricDefinition:
    """Metric definition structure"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = None
    buckets: List[float] = None  # For histograms
    
@dataclass
class MetricData:
    """
Metric data point"""
    name: str
    value: float
    labels: Dict[str, str] = None
    timestamp: datetime = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.labels is None:
            self.labels = {}

class PipelineMetrics:
    """
Pipeline-specific metrics collection"""
    
    def __init__(self) -> None:
        self.execution_start_times: Dict[str, datetime] = {}
        self.step_start_times: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        self.metrics_data: List[MetricData] = []
        self.logger = logging.getLogger(__name__)
        
    def record_pipeline_start(self, execution_id -> None: str, config -> None: Any) -> None:
        """
Record pipeline start event"""
        self.execution_start_times[execution_id] = datetime.utcnow()
        
        # Record start metric
        metric = MetricData(
            name="pipeline_started_total",
            value=1,
            labels={
                "pipeline_name": config.name,
                "environment": config.environment.value,
                "pipeline_type": config.pipeline_type.value
            }
        )
        self.metrics_data.append(metric)
        
    def record_pipeline_end(self, execution -> None: PipelineExecution) -> None:
        """Record pipeline completion/failure event"""
        execution_id = execution.execution_id
        
        if execution_id in self.execution_start_times:
            start_time = self.execution_start_times[execution_id]
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record duration metric
            metric = MetricData(
                name="pipeline_duration_seconds",
                value=duration,
                labels={
                    "pipeline_name": execution.config.name,
                    "environment": execution.config.environment.value,
                    "pipeline_type": execution.config.pipeline_type.value,
                    "status": execution.status.value
                }
            )
            self.metrics_data.append(metric)
            
            # Record completion metric
            if execution.status == PipelineStatus.SUCCESS:
                metric_name = "pipeline_success_total"
            elif execution.status == PipelineStatus.FAILED:
                metric_name = "pipeline_failed_total"
            else:
                metric_name = "pipeline_cancelled_total"
                
            metric = MetricData(
                name=metric_name,
                value=1,
                labels={
                    "pipeline_name": execution.config.name,
                    "environment": execution.config.environment.value,
                    "pipeline_type": execution.config.pipeline_type.value
                }
            )
            self.metrics_data.append(metric)
            
            # Clean up tracking data
            del self.execution_start_times[execution_id]
            if execution_id in self.step_start_times:
                del self.step_start_times[execution_id]
                
    def record_step_start(self, execution_id -> None: str, step_name -> None: str) -> None:
        """Record pipeline step start"""
        self.step_start_times[execution_id][step_name] = datetime.utcnow()
        
    def record_step_end(self, execution_id -> None: str, step_name -> None: str, 
                       success -> None: bool, config -> None: Any) -> None:
        """
Record pipeline step completion"""
        if (execution_id in self.step_start_times and 
            step_name in self.step_start_times[execution_id]):
            
            start_time = self.step_start_times[execution_id][step_name]
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record step duration
            metric = MetricData(
                name="pipeline_step_duration_seconds",
                value=duration,
                labels={
                    "pipeline_name": config.name,
                    "environment": config.environment.value,
                    "step_name": step_name,
                    "status": "success" if success else "failed"
                }
            )
            self.metrics_data.append(metric)
            
            # Record step result
            metric_name = "pipeline_step_success_total" if success else "pipeline_step_failed_total"
            metric = MetricData(
                name=metric_name,
                value=1,
                labels={
                    "pipeline_name": config.name,
                    "environment": config.environment.value,
                    "step_name": step_name
                }
            )
            self.metrics_data.append(metric)

class PrometheusExporter:
    """Prometheus metrics exporter"""
    
    def __init__(self, port -> None: int = 8000) -> None:
        self.port = port
        self.metrics: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        if not PROMETHEUS_AVAILABLE:
            self.logger.warning("Prometheus client not available, metrics export disabled")
            return
            
        # Initialize standard metrics
        self._initialize_metrics()
        
        # Start HTTP server for metrics
        start_http_server(self.port)
        self.logger.info(f"Prometheus metrics server started on port {self.port}")
        
    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE:
            return
            
        # Pipeline metrics
        self.metrics['pipeline_started_total'] = Counter(
            'pipeline_started_total',
            'Total number of pipelines started',
            ['pipeline_name', 'environment', 'pipeline_type']
        )
        
        self.metrics['pipeline_success_total'] = Counter(
            'pipeline_success_total', 
            'Total number of successful pipelines',
            ['pipeline_name', 'environment', 'pipeline_type']
        )
        
        self.metrics['pipeline_failed_total'] = Counter(
            'pipeline_failed_total',
            'Total number of failed pipelines', 
            ['pipeline_name', 'environment', 'pipeline_type']
        )
        
        self.metrics['pipeline_duration_seconds'] = Histogram(
            'pipeline_duration_seconds',
            'Pipeline execution duration in seconds',
            ['pipeline_name', 'environment', 'pipeline_type', 'status'],
            buckets=[30, 60, 120, 300, 600, 1200, 1800, 3600, 7200]
        )
        
        # Step metrics
        self.metrics['pipeline_step_duration_seconds'] = Histogram(
            'pipeline_step_duration_seconds',
            'Pipeline step execution duration in seconds',
            ['pipeline_name', 'environment', 'step_name', 'status'],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1200]
        )
        
        self.metrics['pipeline_step_success_total'] = Counter(
            'pipeline_step_success_total',
            'Total number of successful pipeline steps',
            ['pipeline_name', 'environment', 'step_name']
        )
        
        self.metrics['pipeline_step_failed_total'] = Counter(
            'pipeline_step_failed_total',
            'Total number of failed pipeline steps',
            ['pipeline_name', 'environment', 'step_name']
        )
        
        # System metrics
        self.metrics['active_pipelines'] = Gauge(
            'active_pipelines',
            'Number of currently active pipelines',
            ['environment']
        )
        
        self.metrics['pipeline_queue_size'] = Gauge(
            'pipeline_queue_size',
            'Number of pipelines waiting in queue'
        )
        
    def record_metric(self, metric_data -> None: MetricData) -> None:
        """
Record metric data point to Prometheus"""
        if not PROMETHEUS_AVAILABLE:
            return
            
        metric = self.metrics.get(metric_data.name)
        if not metric:
            self.logger.warning(f"Unknown metric: {metric_data.name}")
            return
            
        try:
            labels = metric_data.labels or {}
            
            if hasattr(metric, 'inc'):  # Counter
                metric.labels(**labels).inc(metric_data.value)
            elif hasattr(metric, 'observe'):  # Histogram/Summary
                metric.labels(**labels).observe(metric_data.value)
            elif hasattr(metric, 'set'):  # Gauge
                metric.labels(**labels).set(metric_data.value)
                
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_data.name}: {str(e)}")

class MetricsStorage:
    """Local metrics storage for historical data"""
    
    def __init__(self, db_path -> None: Optional[Path] = None) -> None:
        self.db_path = db_path or Path(__file__).parent / "metrics.db"
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._initialize_database()
        
    def _initialize_database(self) -> None:
        """Initialize SQLite database for metrics storage"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        value REAL NOT NULL,
                        labels TEXT,
                        timestamp DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                    ON metrics(name, timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                    ON metrics(timestamp)
                ''')
                
            self.logger.info("Metrics database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics database: {str(e)}")
            
    def store_metric(self, metric_data -> None: MetricData) -> None:
        """Store metric data point"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    'INSERT INTO metrics (name, value, labels, timestamp) VALUES (?, ?, ?, ?)',
                    (
                        metric_data.name,
                        metric_data.value,
                        json.dumps(metric_data.labels) if metric_data.labels else None,
                        metric_data.timestamp.isoformat()
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Failed to store metric: {str(e)}")
            
    def get_metrics(self, metric_name: str, start_time: datetime, 
                   end_time: Optional[datetime] = None,
                   labels: Optional[Dict[str, str]] = None) -> List[MetricData]:
        """Retrieve metrics from storage"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                query = 'SELECT name, value, labels, timestamp FROM metrics WHERE name = ? AND timestamp >= ?'
                params = [metric_name, start_time.isoformat()]
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time.isoformat())
                    
                query += ' ORDER BY timestamp'
                
                cursor = conn.execute(query, params)
                results = []
                
                for row in cursor.fetchall():
                    metric_labels = json.loads(row[2]) if row[2] else {}
                    
                    # Filter by labels if specified
                    if labels:
                        if not all(metric_labels.get(k) == v for k, v in labels.items()):
                            continue
                            
                    results.append(MetricData(
                        name=row[0],
                        value=row[1], 
                        labels=metric_labels,
                        timestamp=datetime.fromisoformat(row[3])
                    ))
                    
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve metrics: {str(e)}")
            return []
            
    def cleanup_old_metrics(self, retention_days -> None: int = 30) -> None:
        """Clean up old metrics data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                result = conn.execute(
                    'DELETE FROM metrics WHERE timestamp < ?',
                    (cutoff_date.isoformat(),)
                )
                
                self.logger.info(f"Cleaned up {result.rowcount} old metric records")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {str(e)}")

class MetricsAnalyzer:
    """Metrics analysis and alerting"""
    
    def __init__(self, storage -> None: MetricsStorage) -> None:
        self.storage = storage
        self.alert_thresholds: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default alert thresholds
        self._set_default_thresholds()
        
    def _set_default_thresholds(self) -> None:
        """
Set default alert thresholds"""
        self.alert_thresholds = {
            'pipeline_failure_rate': {
                'threshold': 0.1,  # 10% failure rate
                'window_minutes': 60,
                'severity': 'warning'
            },
            'pipeline_duration_p95': {
                'threshold': 3600,  # 1 hour
                'window_minutes': 60,
                'severity': 'warning'
            },
            'step_failure_rate': {
                'threshold': 0.05,  # 5% step failure rate
                'window_minutes': 30,
                'severity': 'warning'
            }
        }
        
    def set_alert_threshold(self, metric_name -> None: str, threshold -> None: float,
                          window_minutes -> None: int = 60, severity -> None: str = 'warning') -> None:
        """
Set custom alert threshold"""
        self.alert_thresholds[metric_name] = {
            'threshold': threshold,
            'window_minutes': window_minutes,
            'severity': severity
        }
        
    def analyze_pipeline_performance(self, pipeline_name: str, 
                                   environment: str,
                                   hours: int = 24) -> Dict[str, Any]:
        """
Analyze pipeline performance over specified time period"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get pipeline metrics
        success_metrics = self.storage.get_metrics(
            'pipeline_success_total',
            start_time,
            end_time,
            {'pipeline_name': pipeline_name, 'environment': environment}
        )
        
        failed_metrics = self.storage.get_metrics(
            'pipeline_failed_total',
            start_time, 
            end_time,
            {'pipeline_name': pipeline_name, 'environment': environment}
        )
        
        duration_metrics = self.storage.get_metrics(
            'pipeline_duration_seconds',
            start_time,
            end_time,
            {'pipeline_name': pipeline_name, 'environment': environment}
        )
        
        # Calculate statistics
        total_executions = len(success_metrics) + len(failed_metrics)
        success_rate = len(success_metrics) / total_executions if total_executions > 0 else 0
        failure_rate = len(failed_metrics) / total_executions if total_executions > 0 else 0
        
        durations = [m.value for m in duration_metrics]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Calculate percentiles
        if durations:
            sorted_durations = sorted(durations)
            p50 = sorted_durations[int(len(sorted_durations) * 0.5)]
            p95 = sorted_durations[int(len(sorted_durations) * 0.95)]
            p99 = sorted_durations[int(len(sorted_durations) * 0.99)]
        else:
            p50 = p95 = p99 = 0
            
        return {
            'pipeline_name': pipeline_name,
            'environment': environment,
            'analysis_period_hours': hours,
            'total_executions': total_executions,
            'success_count': len(success_metrics),
            'failure_count': len(failed_metrics),
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'duration_stats': {
                'average': avg_duration,
                'min': min_duration,
                'max': max_duration,
                'p50': p50,
                'p95': p95,
                'p99': p99
            }
        }
        
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
Check for alert conditions"""
        alerts = []
        current_time = datetime.utcnow()
        
        for metric_name, config in self.alert_thresholds.items():
            window_start = current_time - timedelta(minutes=config['window_minutes'])
            
            if metric_name == 'pipeline_failure_rate':
                alerts.extend(self._check_failure_rate_alert(window_start, current_time, config))
            elif metric_name == 'pipeline_duration_p95':
                alerts.extend(self._check_duration_alert(window_start, current_time, config))
                
        return alerts
        
    def _check_failure_rate_alert(self, start_time: datetime, end_time: datetime,
                                config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Check for pipeline failure rate alerts"""
        alerts = []
        
        # Get all pipeline executions in window
        success_metrics = self.storage.get_metrics('pipeline_success_total', start_time, end_time)
        failed_metrics = self.storage.get_metrics('pipeline_failed_total', start_time, end_time)
        
        # Group by pipeline and environment
        pipeline_stats = defaultdict(lambda: {'success': 0, 'failed': 0})
        
        for metric in success_metrics:
            key = (metric.labels.get('pipeline_name'), metric.labels.get('environment'))
            pipeline_stats[key]['success'] += metric.value
            
        for metric in failed_metrics:
            key = (metric.labels.get('pipeline_name'), metric.labels.get('environment'))
            pipeline_stats[key]['failed'] += metric.value
            
        # Check thresholds
        for (pipeline_name, environment), stats in pipeline_stats.items():
            total = stats['success'] + stats['failed']
            if total > 0:
                failure_rate = stats['failed'] / total
                if failure_rate > config['threshold']:
                    alerts.append({
                        'metric': 'pipeline_failure_rate',
                        'pipeline_name': pipeline_name,
                        'environment': environment,
                        'current_value': failure_rate,
                        'threshold': config['threshold'],
                        'severity': config['severity'],
                        'message': f"High failure rate: {failure_rate:.2%} (threshold: {config['threshold']:.2%})"
                    })
                    
        return alerts

class PipelineMonitoringManager:
    """
    Comprehensive Pipeline Monitoring and Metrics Management System
    
    Provides enterprise-grade monitoring capabilities with:
    - Real-time metrics collection and export
    - Performance analysis and reporting
    - Alert detection and notification
    - Integration with Prometheus and Grafana
    - Historical data storage and retrieval
    """
    
    def __init__(self, prometheus_port -> None: int = 8000, 
                 storage_path -> None: Optional[Path] = None) -> None:
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pipeline_metrics = PipelineMetrics()
        self.storage = MetricsStorage(storage_path)
        self.analyzer = MetricsAnalyzer(self.storage)
        
        # Initialize Prometheus exporter if available
        self.prometheus_exporter = None
        if PROMETHEUS_AVAILABLE:
            try:
                self.prometheus_exporter = PrometheusExporter(prometheus_port)
            except Exception as e:
                self.logger.error(f"Failed to initialize Prometheus exporter: {str(e)}")
        
        # Metrics processing queue
        self.metrics_queue = deque()
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
        # Start metrics processing
        self._start_metrics_processing()
        
    def _start_metrics_processing(self) -> None:
        """Start background metrics processing"""
        self.processing_thread = threading.Thread(target=self._process_metrics_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        self.logger.info("Started metrics processing thread")
        
    def _process_metrics_loop(self) -> None:
        """Background metrics processing loop"""
        while not self.stop_processing.is_set():
            try:
                if self.metrics_queue:
                    metric_data = self.metrics_queue.popleft()
                    
                    # Store to local storage
                    self.storage.store_metric(metric_data)
                    
                    # Export to Prometheus
                    if self.prometheus_exporter:
                        self.prometheus_exporter.record_metric(metric_data)
                        
                else:
                    time.sleep(0.1)  # Short sleep when queue is empty
                    
            except Exception as e:
                self.logger.error(f"Error in metrics processing: {str(e)}")
                time.sleep(1)
                
    def record_metric(self, metric_data -> None: MetricData) -> None:
        """Record metric data point"""
        self.metrics_queue.append(metric_data)
        
    def record_pipeline_event(self, event_type -> None: str, execution -> None: PipelineExecution) -> None:
        """
Record pipeline event with automatic metric generation"""
        if event_type == 'start':
            self.pipeline_metrics.record_pipeline_start(
                execution.execution_id, 
                execution.config
            )
        elif event_type == 'end':
            self.pipeline_metrics.record_pipeline_end(execution)
            
        # Add generated metrics to queue
        for metric in self.pipeline_metrics.metrics_data:
            self.record_metric(metric)
            
        # Clear processed metrics
        self.pipeline_metrics.metrics_data.clear()
        
    def get_pipeline_analytics(self, pipeline_name: str, environment: str,
                             hours: int = 24) -> Dict[str, Any]:
        """
Get comprehensive pipeline analytics"""
        return self.analyzer.analyze_pipeline_performance(
            pipeline_name, environment, hours
        )
        
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
Check for active alerts"""
        return self.analyzer.check_alerts()
        
    def set_alert_threshold(self, metric_name -> None: str, threshold -> None: float,
                          window_minutes -> None: int = 60, severity -> None: str = 'warning') -> None:
        """
Configure alert threshold"""
        self.analyzer.set_alert_threshold(
            metric_name, threshold, window_minutes, severity
        )
        
    def cleanup_old_data(self, retention_days -> None: int = 30) -> None:
        """
Clean up old metrics data"""
        self.storage.cleanup_old_metrics(retention_days)
        
    def shutdown(self) -> None:
        """
Shutdown monitoring manager"""
        self.stop_processing.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        self.logger.info("Pipeline monitoring manager shutdown complete")

# Global monitoring manager instance
monitoring_manager = PipelineMonitoringManager()
