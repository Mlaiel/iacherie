"""Monitoring System Engine - Main Interface

Enterprise-grade monitoring system providing unified interface
for all monitoring, alerting, and observability capabilities across the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Monitoring metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemHealth(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """Monitoring metric value"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: MetricType


@dataclass
class AlertRule:
    """Monitoring alert rule"""
    name: str
    metric: str
    condition: str
    threshold: float
    severity: AlertSeverity
    enabled: bool = True


@dataclass
class Alert:
    """Monitoring alert"""
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    triggered_at: datetime
    resolved_at: Optional[datetime] = None


class MonitoringEngine:
    """Main Monitoring System Engine
    
    Provides comprehensive monitoring, alerting, and observability
    for the entire Ainflue distribution platform.
    """
    
    def __init__(self) -> None:
        """Initialize Monitoring Engine"""
        self.metrics_store = {}
        self.alert_rules = {}
        self.active_alerts = {}
        self.subscribers = []
        self.collection_interval = 60  # seconds
        self._running = False
    
    async def record_metric(self, name: str, value: float, 
                          tags: Dict[str, str] = None,
                          metric_type: MetricType = MetricType.GAUGE) -> bool:
        """Record a metric value
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags
            metric_type: Type of metric
            
        Returns:
            Success status
        """
        try:
            metric = MetricValue(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                metric_type=metric_type
            )
            
            if name not in self.metrics_store:
                self.metrics_store[name] = []
            
            self.metrics_store[name].append(metric)
            
            # Keep only last 1000 values per metric
            if len(self.metrics_store[name]) > 1000:
                self.metrics_store[name] = self.metrics_store[name][-1000:]
            
            # Check alert rules
            await self._check_alert_rules(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {e}")
            return False
    
    async def get_metric_stats(self, name: str, 
                             duration: timedelta = timedelta(hours=1)) -> Dict[str, float]:
        """Get metric statistics for a time period
        
        Args:
            name: Metric name
            duration: Time period to analyze
            
        Returns:
            Metric statistics
        """
        try:
            if name not in self.metrics_store:
                return {}
            
            cutoff_time = datetime.now() - duration
            recent_values = [
                m.value for m in self.metrics_store[name]
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_values:
                return {}
            
            return {
                "count": len(recent_values),
                "min": min(recent_values),
                "max": max(recent_values),
                "avg": statistics.mean(recent_values),
                "median": statistics.median(recent_values),
                "std_dev": statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating metric stats for {name}: {e}")
            return {}
    
    async def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add monitoring alert rule
        
        Args:
            rule: Alert rule to add
            
        Returns:
            Success status
        """
        try:
            self.alert_rules[rule.name] = rule
            logger.info(f"Added alert rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding alert rule {rule.name}: {e}")
            return False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status
        
        Returns:
            System health information
        """
        try:
            health_data = {
                "status": SystemHealth.HEALTHY,
                "timestamp": datetime.now(),
                "active_alerts": len(self.active_alerts),
                "metrics_collected": len(self.metrics_store),
                "uptime_seconds": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
            # Determine overall health based on active alerts
            critical_alerts = sum(1 for alert in self.active_alerts.values() 
                                if alert.severity == AlertSeverity.CRITICAL)
            error_alerts = sum(1 for alert in self.active_alerts.values() 
                             if alert.severity == AlertSeverity.ERROR)
            
            if critical_alerts > 0:
                health_data["status"] = SystemHealth.CRITICAL
            elif error_alerts > 3:
                health_data["status"] = SystemHealth.UNHEALTHY
            elif len(self.active_alerts) > 10:
                health_data["status"] = SystemHealth.DEGRADED
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": SystemHealth.UNHEALTHY,
                "timestamp": datetime.now(),
                "error": str(e)
            }
    
    async def start_monitoring(self) -> None:
        """Start the monitoring engine"""
        try:
            self.start_time = time.time()
            self._running = True
            logger.info("Monitoring engine started")
            
            # Start background monitoring tasks
            asyncio.create_task(self._metrics_collection_loop())
            asyncio.create_task(self._alert_check_loop())
            
        except Exception as e:
            logger.error(f"Error starting monitoring engine: {e}")
    
    async def stop_monitoring(self) -> None:
        """Stop the monitoring engine"""
        self._running = False
        logger.info("Monitoring engine stopped")
    
    async def _check_alert_rules(self, metric -> None: MetricValue) -> None:
        """Check if metric triggers any alert rules"""
        try:
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled or rule.metric != metric.name:
                    continue
                
                triggered = False
                if rule.condition == "greater_than" and metric.value > rule.threshold:
                    triggered = True
                elif rule.condition == "less_than" and metric.value < rule.threshold:
                    triggered = True
                elif rule.condition == "equals" and metric.value == rule.threshold:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(rule, metric)
                elif rule_name in self.active_alerts:
                    await self._resolve_alert(rule_name)
                    
        except Exception as e:
            logger.error(f"Error checking alert rules: {e}")
    
    async def _trigger_alert(self, rule -> None: AlertRule, metric -> None: MetricValue) -> None:
        """Trigger an alert"""
        try:
            alert = Alert(
                rule_name=rule.name,
                metric_name=metric.name,
                current_value=metric.value,
                threshold=rule.threshold,
                severity=rule.severity,
                triggered_at=datetime.now()
            )
            
            self.active_alerts[rule.name] = alert
            
            # Notify subscribers
            for subscriber in self.subscribers:
                await subscriber(alert)
            
            logger.warning(f"Alert triggered: {rule.name} - {metric.name}={metric.value}")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _resolve_alert(self, rule_name -> None: str) -> None:
        """Resolve an active alert"""
        try:
            if rule_name in self.active_alerts:
                alert = self.active_alerts[rule_name]
                alert.resolved_at = datetime.now()
                del self.active_alerts[rule_name]
                logger.info(f"Alert resolved: {rule_name}")
        except Exception as e:
            logger.error(f"Error resolving alert {rule_name}: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self._running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(5)
    
    async def _alert_check_loop(self) -> None:
        """Background alert checking loop"""
        while self._running:
            try:
                # Check for stale alerts and system health
                await self._cleanup_stale_alerts()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self) -> None:
        """Collect basic system metrics"""
        try:
            import psutil
            
            # CPU usage
            await self.record_metric("system.cpu_percent", psutil.cpu_percent())
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric("system.memory_percent", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.record_metric("system.disk_percent", 
                                   (disk.used / disk.total) * 100)
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _cleanup_stale_alerts(self) -> None:
        """Clean up stale alerts"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            stale_alerts = [
                name for name, alert in self.active_alerts.items()
                if alert.triggered_at < cutoff_time
            ]
            
            for alert_name in stale_alerts:
                await self._resolve_alert(alert_name)
                
        except Exception as e:
            logger.error(f"Error cleaning up stale alerts: {e}")


# Import all monitoring modules
from .alerting_system import *
from .anomaly_detector import *
from .capacity_planner import *
from .cost_tracker import *
from .dashboard_generator import *
from .distribution_metrics_collector import *
from .performance_tracker import *
from .platform_health_monitor import *
from .report_engine import *
from .roi_calculator import *
from .sla_monitor import *

# Public API exports
__all__ = [
    'MonitoringEngine',
    'MetricType',
    'AlertSeverity',
    'SystemHealth',
    'MetricValue',
    'AlertRule',
    'Alert',
]

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."