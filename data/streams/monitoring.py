"""Stream Monitoring System for IA Influencer Agent Platform
========================================================

Advanced monitoring and alerting system for real-time stream health,
performance tracking, and automated incident response.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from statistics import mean, stdev

from pydantic import BaseModel, Field
from redis.asyncio import Redis

from ...core.config import get_settings
from ...utils.logging import get_logger
from ...utils.notifications import NotificationManager
from .manager import StreamEvent

logger = get_logger(__name__)
settings = get_settings()


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringMetric(str, Enum):
    """Monitoring metric types"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    QUEUE_SIZE = "queue_size"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    name: str
    metric: MonitoringMetric
    threshold: float
    operator: str  # >, <, >=, <=, ==, !=
    severity: AlertSeverity
    enabled: bool = True
    cooldown_seconds: int = 300
    description: Optional[str] = None
    last_triggered: Optional[datetime] = None


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamHealth(BaseModel):
    """Stream health status"""
    stream_id: str = Field(description="Stream identifier")
    status: str = Field(description="Health status")
    last_activity: datetime = Field(description="Last activity timestamp")
    event_count: int = Field(default=0, description="Total events processed")
    error_count: int = Field(default=0, description="Error count")
    average_latency: float = Field(default=0.0, description="Average processing latency")
    throughput: float = Field(default=0.0, description="Events per second")
    health_score: float = Field(default=100.0, description="Overall health score")


class MonitoringStats(BaseModel):
    """Comprehensive monitoring statistics"""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active_streams: int = Field(default=0, description="Number of active streams")
    total_events: int = Field(default=0, description="Total events processed")
    events_per_second: float = Field(default=0.0, description="Current throughput")
    average_latency: float = Field(default=0.0, description="Average processing latency")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    success_rate: float = Field(default=100.0, description="Success rate percentage")
    active_alerts: int = Field(default=0, description="Number of active alerts")
    system_health: str = Field(default="healthy", description="Overall system health")


class StreamMonitor:
    """
    Enterprise-grade stream monitoring system for real-time health tracking,
    performance analysis, and automated incident response.
    """
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.stream_health: Dict[str, StreamHealth] = {}
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self.monitoring_callbacks: List[Callable[[MonitoringStats], None]] = []
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize stream monitor with dependencies"""
        try:
            from ...core.cache import get_redis_client
            self.redis = await get_redis_client()
            
            self.notification_manager = NotificationManager()
            await self.notification_manager.initialize()
            
            # Setup default alert rules
            await self._setup_default_alert_rules()
            
            # Start monitoring tasks
            asyncio.create_task(self._health_checker())
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._alert_processor())
            
            logger.info("StreamMonitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamMonitor: {e}")
            raise
            
    async def _setup_default_alert_rules(self) -> None:
        """Setup default monitoring alert rules"""
        default_rules = [
            AlertRule(
                id="high_error_rate",
                name="High Error Rate",
                metric=MonitoringMetric.ERROR_RATE,
                threshold=5.0,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="Error rate exceeds 5%"
            ),
            AlertRule(
                id="critical_error_rate",
                name="Critical Error Rate",
                metric=MonitoringMetric.ERROR_RATE,
                threshold=15.0,
                operator=">",
                severity=AlertSeverity.CRITICAL,
                description="Error rate exceeds 15%"
            ),
            AlertRule(
                id="high_latency",
                name="High Processing Latency",
                metric=MonitoringMetric.LATENCY,
                threshold=5.0,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="Processing latency exceeds 5 seconds"
            ),
            AlertRule(
                id="low_throughput",
                name="Low Throughput",
                metric=MonitoringMetric.THROUGHPUT,
                threshold=1.0,
                operator="<",
                severity=AlertSeverity.WARNING,
                description="Throughput below 1 event/second"
            ),
            AlertRule(
                id="queue_overflow",
                name="Queue Overflow",
                metric=MonitoringMetric.QUEUE_SIZE,
                threshold=10000,
                operator=">",
                severity=AlertSeverity.ERROR,
                description="Queue size exceeds 10,000 items"
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.id] = rule
            
    async def track_stream_event(
        self,
        stream_id: str,
        event: StreamEvent,
        processing_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Track stream event for monitoring
        
        Args:
            stream_id: Stream identifier
            event: Stream event
            processing_time: Processing time in seconds
            error: Error message if failed
        """
        try:
            # Update stream health
            if stream_id not in self.stream_health:
                self.stream_health[stream_id] = StreamHealth(
                    stream_id=stream_id,
                    status="active",
                    last_activity=datetime.now(timezone.utc)
                )
                
            health = self.stream_health[stream_id]
            health.last_activity = datetime.now(timezone.utc)
            health.event_count += 1
            
            if error:
                health.error_count += 1
                health.status = "degraded" if health.error_count > 5 else "active"
            else:
                health.status = "active"
                
            if processing_time is not None:
                # Update average latency
                current_avg = health.average_latency
                count = health.event_count
                health.average_latency = ((current_avg * (count - 1)) + processing_time) / count
                
            # Calculate health score
            error_rate = (health.error_count / health.event_count) * 100 if health.event_count > 0 else 0
            health.health_score = max(0, 100 - (error_rate * 2))
            
            # Store metrics for historical analysis
            await self._store_metrics(stream_id, health, processing_time, error)
            
        except Exception as e:
            logger.error(f"Failed to track stream event: {e}")
            
    async def get_stream_health(self, stream_id: str) -> Optional[StreamHealth]:
        """Get health status for specific stream"""
        return self.stream_health.get(stream_id)
        
    async def get_all_stream_health(self) -> List[StreamHealth]:
        """Get health status for all monitored streams"""
        return list(self.stream_health.values())
        
    async def get_monitoring_stats(self) -> MonitoringStats:
        """Get comprehensive monitoring statistics"""
        try:
            total_events = sum(health.event_count for health in self.stream_health.values())
            total_errors = sum(health.error_count for health in self.stream_health.values())
            
            error_rate = (total_errors / total_events * 100) if total_events > 0 else 0
            success_rate = 100 - error_rate
            
            avg_latency = mean([
                health.average_latency for health in self.stream_health.values()
                if health.average_latency > 0
            ]) if self.stream_health else 0
            
            # Calculate current throughput
            recent_events = await self._get_recent_event_count()
            events_per_second = recent_events / 60.0  # Events in last minute
            
            # Determine system health
            system_health = "healthy"
            if error_rate > 15 or len(self.active_alerts) > 5:
                system_health = "critical"
            elif error_rate > 5 or avg_latency > 5 or len(self.active_alerts) > 0:
                system_health = "degraded"
                
            return MonitoringStats(
                active_streams=len(self.stream_health),
                total_events=total_events,
                events_per_second=events_per_second,
                average_latency=avg_latency,
                error_rate=error_rate,
                success_rate=success_rate,
                active_alerts=len(self.active_alerts),
                system_health=system_health
            )
            
        except Exception as e:
            logger.error(f"Failed to get monitoring stats: {e}")
            return MonitoringStats()
            
    async def create_alert_rule(self, rule: AlertRule) -> None:
        """Create new alert rule"""
        self.alert_rules[rule.id] = rule
        logger.info(f"Created alert rule: {rule.name}")
        
    async def update_alert_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing alert rule"""
        if rule_id not in self.alert_rules:
            return False
            
        rule = self.alert_rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
                
        logger.info(f"Updated alert rule: {rule.name}")
        return True
        
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Deleted alert rule: {rule_id}")
            return True
        return False
        
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.active_alerts.values() if not alert.resolved_at]
        
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Acknowledged alert: {alert_id}")
            return True
        return False
        
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved_at = datetime.now(timezone.utc)
            logger.info(f"Resolved alert: {alert_id}")
            return True
        return False
        
    async def register_monitoring_callback(self, callback: Callable[[MonitoringStats], None]) -> None:
        """Register callback for monitoring stats updates"""
        self.monitoring_callbacks.append(callback)
        
    async def get_metrics_history(
        self,
        stream_id: Optional[str] = None,
        metric: Optional[MonitoringMetric] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get historical metrics data"""
        try:
            # Filter metrics based on parameters
            if stream_id:
                history = self.metrics_history.get(stream_id, [])
            else:
                history = []
                for stream_metrics in self.metrics_history.values():
                    history.extend(stream_metrics)
                    
            # Apply time filters
            if start_time or end_time:
                filtered_history = []
                for metric_data in history:
                    timestamp = datetime.fromisoformat(metric_data["timestamp"])
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    filtered_history.append(metric_data)
                history = filtered_history
                
            # Apply metric type filter
            if metric:
                history = [
                    metric_data for metric_data in history
                    if metric_data.get("metric_type") == metric.value
                ]
                
            return sorted(history, key=lambda x: x["timestamp"])
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return []
            
    async def _health_checker(self) -> None:
        """Periodic health checker task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                current_time = datetime.now(timezone.utc)
                
                # Check for inactive streams
                for stream_id, health in self.stream_health.items():
                    time_since_activity = current_time - health.last_activity
                    
                    if time_since_activity > timedelta(minutes=5):
                        health.status = "inactive"
                        health.health_score = 0
                    elif time_since_activity > timedelta(minutes=2):
                        health.status = "stale"
                        health.health_score = max(health.health_score * 0.8, 50)
                        
                # Clean up old inactive streams
                inactive_streams = [
                    sid for sid, health in self.stream_health.items()
                    if health.status == "inactive" and 
                    (current_time - health.last_activity) > timedelta(hours=1)
                ]
                
                for stream_id in inactive_streams:
                    del self.stream_health[stream_id]
                    logger.info(f"Cleaned up inactive stream: {stream_id}")
                    
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                
    async def _metrics_collector(self) -> None:
        """Periodic metrics collection task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Collect and publish monitoring stats
                stats = await self.get_monitoring_stats()
                
                # Notify callbacks
                for callback in self.monitoring_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(stats)
                        else:
                            callback(stats)
                    except Exception as e:
                        logger.error(f"Monitoring callback error: {e}")
                        
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def _alert_processor(self) -> None:
        """Periodic alert evaluation task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(15)  # Check every 15 seconds
                
                stats = await self.get_monitoring_stats()
                
                # Evaluate alert rules
                for rule in self.alert_rules.values():
                    if not rule.enabled:
                        continue
                        
                    # Check cooldown
                    if rule.last_triggered:
                        time_since_trigger = datetime.now(timezone.utc) - rule.last_triggered
                        if time_since_trigger.total_seconds() < rule.cooldown_seconds:
                            continue
                            
                    # Get metric value
                    metric_value = self._get_metric_value(stats, rule.metric)
                    
                    # Evaluate condition
                    if self._evaluate_condition(metric_value, rule.threshold, rule.operator):
                        await self._trigger_alert(rule, metric_value)
                        
            except Exception as e:
                logger.error(f"Alert processor error: {e}")
                
    def _get_metric_value(self, stats: MonitoringStats, metric: MonitoringMetric) -> float:
        """Get metric value from monitoring stats"""
        metric_map = {
            MonitoringMetric.THROUGHPUT: stats.events_per_second,
            MonitoringMetric.LATENCY: stats.average_latency,
            MonitoringMetric.ERROR_RATE: stats.error_rate,
            MonitoringMetric.SUCCESS_RATE: stats.success_rate,
            MonitoringMetric.QUEUE_SIZE: 0,  # Would need queue size from processor
        }
        return metric_map.get(metric, 0.0)
        
    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate alert condition"""
        operators = {
            ">": lambda v, t: v > t,
            "<": lambda v, t: v < t,
            ">=": lambda v, t: v >= t,
            "<=": lambda v, t: v <= t,
            "==": lambda v, t: v == t,
            "!=": lambda v, t: v != t,
        }
        return operators.get(operator, lambda v, t: False)(value, threshold)
        
    async def _trigger_alert(self, rule: AlertRule, metric_value: float) -> None:
        """Trigger alert for rule violation"""
        try:
            alert = Alert(
                id=f"alert_{rule.id}_{int(datetime.now(timezone.utc).timestamp())}",
                rule_id=rule.id,
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric.value}={metric_value:.2f} {rule.operator} {rule.threshold}",
                metric_value=metric_value,
                threshold=rule.threshold,
                triggered_at=datetime.now(timezone.utc),
                metadata={"rule_description": rule.description}
            )
            
            self.active_alerts[alert.id] = alert
            rule.last_triggered = alert.triggered_at
            
            # Send notification
            if self.notification_manager:
                await self.notification_manager.send_alert_notification(alert)
                
            logger.warning(f"Triggered alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            
    async def _store_metrics(
        self,
        stream_id: str,
        health: StreamHealth,
        processing_time: Optional[float],
        error: Optional[str]
    ) -> None:
        """Store metrics for historical analysis"""
        try:
            if stream_id not in self.metrics_history:
                self.metrics_history[stream_id] = []
                
            metric_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stream_id": stream_id,
                "event_count": health.event_count,
                "error_count": health.error_count,
                "average_latency": health.average_latency,
                "health_score": health.health_score,
                "processing_time": processing_time,
                "error": error
            }
            
            self.metrics_history[stream_id].append(metric_data)
            
            # Keep only last 1000 metrics per stream
            if len(self.metrics_history[stream_id]) > 1000:
                self.metrics_history[stream_id] = self.metrics_history[stream_id][-1000:]
                
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            
    async def _get_recent_event_count(self) -> int:
        """Get event count in the last minute"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=1)
            recent_count = 0
            
            for stream_metrics in self.metrics_history.values():
                for metric in stream_metrics:
                    timestamp = datetime.fromisoformat(metric["timestamp"])
                    if timestamp >= cutoff_time:
                        recent_count += 1
                        
            return recent_count
            
        except Exception as e:
            logger.error(f"Failed to get recent event count: {e}")
            return 0
            
    async def shutdown(self) -> None:
        """Gracefully shutdown stream monitor"""
        try:
            self._shutdown_event.set()
            
            if self.notification_manager:
                await self.notification_manager.shutdown()
                
            if self.redis:
                await self.redis.close()
                
            logger.info("StreamMonitor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during monitor shutdown: {e}")
