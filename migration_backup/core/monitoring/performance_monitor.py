"""
📊🔍 PERFORMANCE MONITOR - CORE MONITORING MODULE 🔍📊
Core Performance Monitoring System for IA Chéries Platform
Copyright (C) 2024 IA Chéries Platform. All Rights Reserved.
"""

import asyncio
import logging
import os
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """📊 Performance Metric Types"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    API_RESPONSE_TIME = "api_response_time"
    DATABASE_QUERY_TIME = "database_query_time"
    CACHE_HIT_RATE = "cache_hit_rate"
    REQUEST_COUNT = "request_count"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"

class AlertLevel(Enum):
    """🚨 Alert Levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """📊 Performance Metric Data"""
    name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertThreshold:
    """🚨 Alert Threshold Configuration"""
    metric_name: str = ""
    warning_threshold: float = 0.0
    critical_threshold: float = 0.0
    emergency_threshold: float = 0.0
    operator: str = ">"  # >, <, >=, <=, ==, !=
    enabled: bool = True

@dataclass
class Alert:
    """🚨 Performance Alert"""
    id: str = ""
    metric_name: str = ""
    level: AlertLevel = AlertLevel.INFO
    message: str = ""
    value: float = 0.0
    threshold: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """📊🔍 Core Performance Monitor"""
    
    def __init__(self, monitoring_interval: float = 5.0):
        self.initialized = False
        self.monitoring_interval = monitoring_interval
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds: Dict[str, AlertThreshold] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.logger = logging.getLogger(f"{__name__}.PerformanceMonitor")
        self._initialize_monitor()
        
    def _initialize_monitor(self):
        """🔧 Initialize Performance Monitor"""
        try:
            # Set up default alert thresholds
            self._setup_default_thresholds()
            
            # Start monitoring thread
            self._start_monitoring()
            
            self.initialized = True
            self.logger.info("📊 Performance Monitor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Performance Monitor initialization failed: {e}")
            self.initialized = False
    
    def _setup_default_thresholds(self):
        """🚨 Setup Default Alert Thresholds"""
        try:
            default_thresholds = [
                AlertThreshold("cpu_usage", 70.0, 85.0, 95.0, ">"),
                AlertThreshold("memory_usage", 75.0, 90.0, 98.0, ">"),
                AlertThreshold("disk_usage", 80.0, 90.0, 95.0, ">"),
                AlertThreshold("api_response_time", 1000.0, 3000.0, 5000.0, ">"),
                AlertThreshold("database_query_time", 500.0, 1000.0, 2000.0, ">"),
                AlertThreshold("error_rate", 1.0, 5.0, 10.0, ">"),
                AlertThreshold("cache_hit_rate", 80.0, 70.0, 50.0, "<"),
            ]
            
            for threshold in default_thresholds:
                self.alert_thresholds[threshold.metric_name] = threshold
            
            self.logger.info(f"🚨 Set up {len(default_thresholds)} default alert thresholds")
            
        except Exception as e:
            self.logger.error(f"❌ Default thresholds setup failed: {e}")
    
    def _start_monitoring(self):
        """🔄 Start Background Monitoring"""
        try:
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("🔄 Background monitoring started")
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring start failed: {e}")
    
    def _monitoring_loop(self):
        """🔄 Background Monitoring Loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check alert thresholds
                self._check_alert_thresholds()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """📊 Collect System Performance Metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_usage", cpu_percent, "percent")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric("memory_usage", memory.percent, "percent")
            self.record_metric("memory_available", memory.available / (1024**3), "GB")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("disk_usage", disk_percent, "percent")
            self.record_metric("disk_available", disk.free / (1024**3), "GB")
            
            # Network I/O
            network = psutil.net_io_counters()
            self.record_metric("network_bytes_sent", network.bytes_sent, "bytes")
            self.record_metric("network_bytes_recv", network.bytes_recv, "bytes")
            
            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
                self.record_metric("load_average_1m", load_avg[0], "load")
                self.record_metric("load_average_5m", load_avg[1], "load")
                self.record_metric("load_average_15m", load_avg[2], "load")
            except (AttributeError, OSError):
                pass  # Not available on all systems
            
        except Exception as e:
            self.logger.error(f"❌ System metrics collection failed: {e}")
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     tags: Optional[Dict[str, str]] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """📊 Record Performance Metric"""
        try:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Add to buffer
            self.metrics_buffer[name].append(metric)
            
            # Log significant metrics
            if name in ['cpu_usage', 'memory_usage', 'disk_usage']:
                self.logger.debug(f"📊 {name}: {value:.1f}{unit}")
            
        except Exception as e:
            self.logger.error(f"❌ Metric recording failed: {e}")
    
    def get_metric_history(self, metric_name: str, 
                          duration_minutes: int = 60) -> List[PerformanceMetric]:
        """📊 Get Metric History"""
        try:
            if metric_name not in self.metrics_buffer:
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
            metrics = list(self.metrics_buffer[metric_name])
            
            # Filter by time
            filtered_metrics = [
                m for m in metrics 
                if m.timestamp >= cutoff_time
            ]
            
            return filtered_metrics
            
        except Exception as e:
            self.logger.error(f"❌ Metric history retrieval failed: {e}")
            return []
    
    def get_current_metrics(self) -> Dict[str, PerformanceMetric]:
        """📊 Get Current Metrics"""
        try:
            current_metrics = {}
            
            for metric_name, metric_buffer in self.metrics_buffer.items():
                if metric_buffer:
                    current_metrics[metric_name] = metric_buffer[-1]
            
            return current_metrics
            
        except Exception as e:
            self.logger.error(f"❌ Current metrics retrieval failed: {e}")
            return {}
    
    def set_alert_threshold(self, threshold: AlertThreshold):
        """🚨 Set Alert Threshold"""
        try:
            self.alert_thresholds[threshold.metric_name] = threshold
            self.logger.info(f"🚨 Alert threshold set for {threshold.metric_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Alert threshold setting failed: {e}")
    
    def _check_alert_thresholds(self):
        """🚨 Check Alert Thresholds"""
        try:
            current_metrics = self.get_current_metrics()
            
            for metric_name, metric in current_metrics.items():
                if metric_name in self.alert_thresholds:
                    threshold = self.alert_thresholds[metric_name]
                    
                    if not threshold.enabled:
                        continue
                    
                    alert_level = self._evaluate_threshold(metric.value, threshold)
                    
                    if alert_level:
                        self._trigger_alert(metric, threshold, alert_level)
            
        except Exception as e:
            self.logger.error(f"❌ Alert threshold checking failed: {e}")
    
    def _evaluate_threshold(self, value: float, threshold: AlertThreshold) -> Optional[AlertLevel]:
        """🚨 Evaluate Threshold"""
        try:
            def compare(val, thresh, op):
                if op == ">":
                    return val > thresh
                elif op == "<":
                    return val < thresh
                elif op == ">=":
                    return val >= thresh
                elif op == "<=":
                    return val <= thresh
                elif op == "==":
                    return val == thresh
                elif op == "!=":
                    return val != thresh
                return False
            
            if compare(value, threshold.emergency_threshold, threshold.operator):
                return AlertLevel.EMERGENCY
            elif compare(value, threshold.critical_threshold, threshold.operator):
                return AlertLevel.CRITICAL
            elif compare(value, threshold.warning_threshold, threshold.operator):
                return AlertLevel.WARNING
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Threshold evaluation failed: {e}")
            return None
    
    def _trigger_alert(self, metric: PerformanceMetric, 
                      threshold: AlertThreshold, level: AlertLevel):
        """🚨 Trigger Performance Alert"""
        try:
            alert_id = f"{metric.name}_{level.value}_{int(time.time())}"
            
            # Check if similar alert is already active
            existing_alert_key = f"{metric.name}_{level.value}"
            if existing_alert_key in self.active_alerts:
                # Update existing alert
                existing_alert = self.active_alerts[existing_alert_key]
                existing_alert.value = metric.value
                existing_alert.timestamp = metric.timestamp
                return
            
            # Create new alert
            alert = Alert(
                id=alert_id,
                metric_name=metric.name,
                level=level,
                message=f"{metric.name} is {metric.value:.2f}{metric.unit}, exceeding {level.value} threshold of {self._get_threshold_value(threshold, level):.2f}{metric.unit}",
                value=metric.value,
                threshold=self._get_threshold_value(threshold, level),
                metadata={
                    'metric_tags': metric.tags,
                    'metric_metadata': metric.metadata
                }
            )
            
            # Store alert
            self.active_alerts[existing_alert_key] = alert
            
            # Log alert
            self.logger.warning(f"🚨 {level.value.upper()} ALERT: {alert.message}")
            
            # Trigger callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"❌ Alert callback failed: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Alert triggering failed: {e}")
    
    def _get_threshold_value(self, threshold: AlertThreshold, level: AlertLevel) -> float:
        """🎯 Get Threshold Value for Level"""
        if level == AlertLevel.WARNING:
            return threshold.warning_threshold
        elif level == AlertLevel.CRITICAL:
            return threshold.critical_threshold
        elif level == AlertLevel.EMERGENCY:
            return threshold.emergency_threshold
        return 0.0
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """📞 Add Alert Callback"""
        self.alert_callbacks.append(callback)
        self.logger.info("📞 Alert callback added")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """✅ Acknowledge Alert"""
        try:
            for alert in self.active_alerts.values():
                if alert.id == alert_id:
                    alert.acknowledged = True
                    self.logger.info(f"✅ Alert acknowledged: {alert_id}")
                    return True
            
            self.logger.warning(f"⚠️ Alert not found: {alert_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Alert acknowledgment failed: {e}")
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """🚨 Get Active Alerts"""
        return list(self.active_alerts.values())
    
    def clear_acknowledged_alerts(self):
        """🧹 Clear Acknowledged Alerts"""
        try:
            before_count = len(self.active_alerts)
            self.active_alerts = {
                k: v for k, v in self.active_alerts.items() 
                if not v.acknowledged
            }
            after_count = len(self.active_alerts)
            cleared_count = before_count - after_count
            
            if cleared_count > 0:
                self.logger.info(f"🧹 Cleared {cleared_count} acknowledged alerts")
            
        except Exception as e:
            self.logger.error(f"❌ Alert clearing failed: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """📊 Get Performance Summary"""
        try:
            current_metrics = self.get_current_metrics()
            active_alerts = self.get_active_alerts()
            
            summary = {
                'timestamp': datetime.utcnow().isoformat(),
                'monitoring_active': self.monitoring_active,
                'metrics_count': len(current_metrics),
                'active_alerts_count': len(active_alerts),
                'current_metrics': {}
            }
            
            # Add key metrics to summary
            key_metrics = ['cpu_usage', 'memory_usage', 'disk_usage']
            for metric_name in key_metrics:
                if metric_name in current_metrics:
                    metric = current_metrics[metric_name]
                    summary['current_metrics'][metric_name] = {
                        'value': metric.value,
                        'unit': metric.unit,
                        'timestamp': metric.timestamp.isoformat()
                    }
            
            # Add alert summary
            alert_summary = {}
            for alert in active_alerts:
                level = alert.level.value
                if level not in alert_summary:
                    alert_summary[level] = 0
                alert_summary[level] += 1
            
            summary['alerts_by_level'] = alert_summary
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Performance summary generation failed: {e}")
            return {}
    
    def stop_monitoring(self):
        """🛑 Stop Monitoring"""
        try:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            
            self.logger.info("🛑 Performance monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring stop failed: {e}")
    
    def is_initialized(self) -> bool:
        """✅ Check Initialization Status"""
        return self.initialized

# Instance globale
performance_monitor = PerformanceMonitor()

if performance_monitor.is_initialized():
    logger.info("🚀💯🔥 PERFORMANCE MONITOR MODULE LOADED - MONITORING FOUNDATION! 🔥💯🚀")
    logger.info("✅ Core performance monitoring with alerts and thresholds operational!")
    logger.info("🏆 CRITICAL MONITORING MODULE FOR 100% SUCCESS ACHIEVED!")

__all__ = [
    'PerformanceMonitor',
    'PerformanceMetric',
    'Alert',
    'AlertThreshold',
    'AlertLevel',
    'MetricType',
    'performance_monitor',
]