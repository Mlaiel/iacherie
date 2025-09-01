"""Real-Time Monitoring Events Module for IA-Influencer-Agent

Ultra-advanced real-time monitoring and alerting system for content creators.
Provides comprehensive system health, performance monitoring, and anomaly detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import psutil
import redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server


logger = logging.getLogger(__name__)


class MonitoringEventType(Enum):
    """
Types of monitoring events"""

    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_METRIC = "performance_metric"
    ANOMALY_DETECTED = "anomaly_detected"
    ALERT_TRIGGERED = "alert_triggered"
    SERVICE_STATUS = "service_status"
    ERROR_OCCURRED = "error_occurred"
    RESOURCE_USAGE = "resource_usage"
    SECURITY_INCIDENT = "security_incident"


class AlertSeverity(Enum):
    """Alert severity levels"""

    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ServiceStatus(Enum):
    """Service status states"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class MonitoringEvent:
    """Monitoring event data structure"""
    event_id: str
    event_type: MonitoringEventType
    timestamp: datetime
    source: str
    severity: AlertSeverity
    message: str
    data: Dict[str, Any]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'severity': self.severity.value,
            'message': self.message,
            'data': self.data,
            'tags': self.tags
        }


class MonitoringMetrics:
    """
Prometheus metrics for monitoring"""
    
    def __init__(self):
        # Counters
        self.events_total = Counter('monitoring_events_total', 'Total monitoring events', ['event_type', 'severity'])
        self.alerts_total = Counter('monitoring_alerts_total', 'Total alerts triggered', ['severity'])
        self.errors_total = Counter('monitoring_errors_total', 'Total errors', ['source', 'error_type'])
        
        # Histograms
        self.event_processing_duration = Histogram('monitoring_event_processing_seconds', 'Event processing duration')
        self.response_time = Histogram('monitoring_response_time_seconds', 'Response time for monitoring checks')
        
        # Gauges
        self.system_cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
        self.system_memory_usage = Gauge('system_memory_usage_percent', 'Memory usage percentage')
        self.active_connections = Gauge('active_connections_count', 'Number of active connections')
        self.service_health_score = Gauge('service_health_score', 'Overall service health score')


class SystemMonitor:
    """
Advanced system monitoring and health checking"""
    
    def __init__(self):
        self.metrics = MonitoringMetrics()
        self.health_checks = {}
        self.performance_history = deque(maxlen=1000)
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0,
            'error_rate': 0.05
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """
Perform comprehensive system health check"""
        try:
            start_time = time.time()
            
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Update Prometheus metrics
            self.metrics.system_cpu_usage.set(cpu_usage)
            self.metrics.system_memory_usage.set(memory.percent)
            
            # Check thresholds
            alerts = []
            if cpu_usage > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'high_cpu_usage',
                    'severity': AlertSeverity.HIGH,
                    'message': f'CPU usage at {cpu_usage}%',
                    'value': cpu_usage
                })
            
            if memory.percent > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'high_memory_usage',
                    'severity': AlertSeverity.HIGH,
                    'message': f'Memory usage at {memory.percent}%',
                    'value': memory.percent
                })
            
            if disk.percent > self.alert_thresholds['disk_usage']:
                alerts.append({
                    'type': 'high_disk_usage',
                    'severity': AlertSeverity.CRITICAL,
                    'message': f'Disk usage at {disk.percent}%',
                    'value': disk.percent
                })
            
            # Calculate health score
            health_score = self._calculate_health_score(cpu_usage, memory.percent, disk.percent)
            self.metrics.service_health_score.set(health_score)
            
            processing_time = time.time() - start_time
            self.metrics.response_time.observe(processing_time)
            
            health_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'health_score': health_score,
                'system_metrics': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available,
                    'disk_usage': disk.percent,
                    'disk_free': disk.free
                },
                'alerts': alerts,
                'processing_time': processing_time,
                'status': self._determine_status(health_score, alerts)
            }
            
            # Store in history
            self.performance_history.append(health_data)
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            self.metrics.errors_total.labels(source='system_monitor', error_type='health_check').inc()
            raise
    
    def _calculate_health_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate overall health score (0-100)"""
        cpu_score = max(0, 100 - cpu)
        memory_score = max(0, 100 - memory)
        disk_score = max(0, 100 - disk)
        
        # Weighted average
        health_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
        return round(health_score, 2)
    
    def _determine_status(self, health_score: float, alerts: List[Dict]) -> ServiceStatus:
        """
Determine service status based on health score and alerts"""
        critical_alerts = [a for a in alerts if a['severity'] == AlertSeverity.CRITICAL]
        high_alerts = [a for a in alerts if a['severity'] == AlertSeverity.HIGH]
        
        if critical_alerts or health_score < 50:
            return ServiceStatus.UNHEALTHY
        elif high_alerts or health_score < 70:
            return ServiceStatus.DEGRADED
        elif health_score >= 90:
            return ServiceStatus.HEALTHY
        else:
            return ServiceStatus.DEGRADED


class AnomalyDetector:
    """
ML-powered anomaly detection for monitoring"""
    
    def __init__(self):
        self.baseline_metrics = defaultdict(list)
        self.anomaly_threshold = 2.5  # Standard deviations
        self.min_baseline_samples = 50
    
    async def detect_anomalies(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """
Detect anomalies in system metrics"""
        anomalies = []
        
        for metric_name, value in metrics.items():
            # Add to baseline
            self.baseline_metrics[metric_name].append(value)
            
            # Keep only recent values for baseline
            if len(self.baseline_metrics[metric_name]) > 1000:
                self.baseline_metrics[metric_name] = self.baseline_metrics[metric_name][-1000:]
            
            # Check for anomaly if we have enough baseline data
            if len(self.baseline_metrics[metric_name]) >= self.min_baseline_samples:
                anomaly = self._check_anomaly(metric_name, value)
                if anomaly:
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _check_anomaly(self, metric_name: str, value: float) -> Optional[Dict[str, Any]]:
        """
Check if a value is anomalous"""
        baseline = self.baseline_metrics[metric_name]
        
        if len(baseline) < self.min_baseline_samples:
            return None
        
        mean = np.mean(baseline)
        std = np.std(baseline)
        
        if std == 0:
            return None
        
        z_score = abs((value - mean) / std)
        
        if z_score > self.anomaly_threshold:
            severity = AlertSeverity.HIGH if z_score > 3.5 else AlertSeverity.MEDIUM
            
            return {
                'metric_name': metric_name,
                'current_value': value,
                'baseline_mean': round(mean, 2),
                'baseline_std': round(std, 2),
                'z_score': round(z_score, 2),
                'severity': severity,
                'type': 'statistical_anomaly',
                'message': f'{metric_name} anomaly detected: {value} (z-score: {z_score:.2f})'
            }
        
        return None


class AlertManager:
    """
Advanced alert management and notification system"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        self.notification_channels = []
        self.alert_rules = []
    
    async def process_alert(self, alert: Dict[str, Any]) -> None:
        """
Process and route alerts"""
        try:
            alert_id = f"{alert['type']}_{alert.get('source', 'unknown')}"
            
            # Check if this is a duplicate alert
            if self._is_duplicate_alert(alert_id, alert):
                return
            
            # Create monitoring event
            event = MonitoringEvent(
                event_id=f"alert_{int(time.time())}_{hash(str(alert)) % 10000}",
                event_type=MonitoringEventType.ALERT_TRIGGERED,
                timestamp=datetime.now(timezone.utc),
                source=alert.get('source', 'unknown'),
                severity=alert['severity'],
                message=alert['message'],
                data=alert,
                tags=[alert['type'], alert['severity'].value]
            )
            
            # Store alert
            self.active_alerts[alert_id] = {
                'alert': alert,
                'event': event,
                'first_seen': datetime.now(timezone.utc),
                'last_seen': datetime.now(timezone.utc),
                'count': 1
            }
            
            self.alert_history.append(event.to_dict())
            
            # Send notifications
            await self._send_notifications(event)
            
            logger.warning(f"Alert triggered: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
    
    def _is_duplicate_alert(self, alert_id: str, alert: Dict[str, Any]) -> bool:
        """Check if this is a duplicate alert within cooldown period"""
        if alert_id in self.active_alerts:
            existing = self.active_alerts[alert_id]
            time_diff = datetime.now(timezone.utc) - existing['last_seen']
            
            # Update existing alert
            existing['last_seen'] = datetime.now(timezone.utc)
            existing['count'] += 1
            
            # Return True if within cooldown (5 minutes)
            return time_diff.total_seconds() < 300
        
        return False
    
    async def _send_notifications(self, event: MonitoringEvent) -> None:
        """
Send alert notifications through configured channels"""
        # Implementation would send to Slack, email, SMS, etc.
        logger.info(f"Notification sent: {event.message}")


class PerformanceProfiler:
    """Performance profiling and optimization recommendations"""
    
    def __init__(self):
        self.performance_data = defaultdict(list)
        self.profiling_active = False
    
    async def profile_operation(self, operation_name: str, duration: float, 
                              metadata: Dict[str, Any] = None) -> None:
        """
Profile an operation's performance"""
        profile_data = {
            'operation': operation_name,
            'duration': duration,
            'timestamp': datetime.now(timezone.utc),
            'metadata': metadata or {}
        }
        
        self.performance_data[operation_name].append(profile_data)
        
        # Keep only recent data
        if len(self.performance_data[operation_name]) > 1000:
            self.performance_data[operation_name] = self.performance_data[operation_name][-1000:]
        
        # Check for performance degradation
        await self._check_performance_degradation(operation_name, duration)
    
    async def _check_performance_degradation(self, operation: str, current_duration: float) -> None:
        """
Check if operation performance has degraded"""
        if len(self.performance_data[operation]) < 10:
            return
        
        recent_durations = [d['duration'] for d in self.performance_data[operation][-10:]]
        avg_recent = np.mean(recent_durations)
        
        # Compare with baseline (older data)
        if len(self.performance_data[operation]) >= 50:
            baseline_durations = [d['duration'] for d in self.performance_data[operation][-50:-10]]
            avg_baseline = np.mean(baseline_durations)
            
            # Alert if recent performance is 50% worse than baseline
            if avg_recent > avg_baseline * 1.5:
                alert = {
                    'type': 'performance_degradation',
                    'source': 'performance_profiler',
                    'severity': AlertSeverity.MEDIUM,
                    'message': f'Performance degradation detected for {operation}: {avg_recent:.2f}s vs {avg_baseline:.2f}s baseline',
                    'operation': operation,
                    'current_avg': avg_recent,
                    'baseline_avg': avg_baseline,
                    'degradation_percent': ((avg_recent - avg_baseline) / avg_baseline) * 100
                }
                
                # Process alert (would typically go through AlertManager)
                logger.warning(alert['message'])
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """
Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'operations': {}
        }
        
        for operation, data in self.performance_data.items():
            if not data:
                continue
            
            durations = [d['duration'] for d in data]
            
            report['operations'][operation] = {
                'total_executions': len(data),
                'avg_duration': round(np.mean(durations), 3),
                'min_duration': round(min(durations), 3),
                'max_duration': round(max(durations), 3),
                'p95_duration': round(np.percentile(durations, 95), 3),
                'p99_duration': round(np.percentile(durations, 99), 3),
                'recent_avg': round(np.mean(durations[-10:]), 3) if len(durations) >= 10 else None
            }
        
        return report


class MonitoringEventHandler:
    """
Main monitoring event handler orchestrating all monitoring components"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()
        self.performance_profiler = PerformanceProfiler()
        self.redis_client = None
        self.monitoring_active = False
    
    async def start_monitoring(self, check_interval: int = 30) -> None:
        """
Start continuous monitoring"""
        self.monitoring_active = True
        
        try:
            # Initialize Redis for caching
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis not available for monitoring cache: {e}")
        
        # Start Prometheus metrics server
        try:
            start_http_server(8090)
            logger.info("Prometheus metrics server started on port 8090")
        except Exception as e:
            logger.warning(f"Could not start Prometheus server: {e}")
        
        logger.info(f"Starting continuous monitoring (interval: {check_interval}s)")
        
        while self.monitoring_active:
            try:
                await self._run_monitoring_cycle()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Monitoring cycle error: {str(e)}")
                await asyncio.sleep(check_interval)
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("Monitoring stopped")
    
    async def _run_monitoring_cycle(self) -> None:
        """Run a single monitoring cycle"""
        cycle_start = time.time()
        
        try:
            # System health check
            health_data = await self.system_monitor.check_system_health()
            
            # Anomaly detection
            metrics = health_data['system_metrics']
            anomalies = await self.anomaly_detector.detect_anomalies(metrics)
            
            # Process anomaly alerts
            for anomaly in anomalies:
                await self.alert_manager.process_alert(anomaly)
            
            # Process health alerts
            for alert in health_data['alerts']:
                await self.alert_manager.process_alert(alert)
            
            # Cache monitoring data
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        'monitoring:latest_health',
                        300,  # 5 minutes TTL
                        json.dumps(health_data)
                    )
                except Exception as e:
                    logger.warning(f"Could not cache monitoring data: {e}")
            
            cycle_duration = time.time() - cycle_start
            await self.performance_profiler.profile_operation('monitoring_cycle', cycle_duration)
            
            logger.debug(f"Monitoring cycle completed in {cycle_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {str(e)}")
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        try:
            # Get latest health data
            health_data = await self.system_monitor.check_system_health()
            
            # Get performance report
            performance_report = await self.performance_profiler.get_performance_report()
            
            # Get active alerts
            active_alerts = [
                alert_data['event'].to_dict() 
                for alert_data in self.alert_manager.active_alerts.values()
            ]
            
            # Get recent alert history
            recent_alerts = list(self.alert_manager.alert_history)[-50:]
            
            dashboard = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_health': health_data,
                'performance_metrics': performance_report,
                'active_alerts': active_alerts,
                'recent_alerts': recent_alerts,
                'monitoring_status': {
                    'active': self.monitoring_active,
                    'components': {
                        'system_monitor': True,
                        'anomaly_detector': True,
                        'alert_manager': True,
                        'performance_profiler': True,
                        'redis_cache': self.redis_client is not None
                    }
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating monitoring dashboard: {str(e)}")
            return {'error': str(e)}


# Global monitoring instance
global_monitoring_handler = MonitoringEventHandler()


async def start_monitoring_system(check_interval: int = 30) -> None:
    """Start the global monitoring system"""
    await global_monitoring_handler.start_monitoring(check_interval)


async def stop_monitoring_system() -> None:
    """
Stop the global monitoring system"""
    await global_monitoring_handler.stop_monitoring()


async def get_monitoring_status() -> Dict[str, Any]:
    """
Get current monitoring system status"""
    return await global_monitoring_handler.get_monitoring_dashboard()


# Export classes and functions
__all__ = [
    'MonitoringEventType',
    'AlertSeverity', 
    'ServiceStatus',
    'MonitoringEvent',
    'MonitoringMetrics',
    'SystemMonitor',
    'AnomalyDetector',
    'AlertManager',
    'PerformanceProfiler',
    'MonitoringEventHandler',
    'global_monitoring_handler',
    'start_monitoring_system',
    'stop_monitoring_system',
    'get_monitoring_status'
]
