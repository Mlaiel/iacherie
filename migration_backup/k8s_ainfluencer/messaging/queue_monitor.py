"""
IA Influencer Agent - Queue Monitoring System
Real-time monitoring and metrics collection for message queues

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Any
import json

from .unified_messaging import UnifiedMessagingSystem, QueueStats
from .messaging_config import MessagingConfig

logger = logging.getLogger(__name__)


@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    queue_name: str
    messages_per_second: float = 0.0
    average_processing_time: float = 0.0
    error_rate: float = 0.0
    consumer_utilization: float = 0.0
    queue_depth: int = 0
    dlq_depth: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class AlertConfig:
    """Alert configuration for queue monitoring"""
    queue_name: str
    max_queue_depth: int = 1000
    max_processing_time: float = 30.0
    max_error_rate: float = 0.1
    min_consumer_utilization: float = 0.1
    alert_cooldown: int = 300  # 5 minutes


class QueueMonitor:
    """Real-time queue monitoring system"""
    
    def __init__(self, messaging_system: UnifiedMessagingSystem, config: Optional[MessagingConfig] = None):
        self.messaging_system = messaging_system
        self.config = config or MessagingConfig.from_env()
        self.metrics_history: Dict[str, List[QueueMetrics]] = {}
        self.alert_configs: Dict[str, AlertConfig] = {}
        self.alert_handlers: List[Callable[[str, str, Dict[str, Any]], None]] = []
        self.last_alerts: Dict[str, datetime] = {}
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Metrics collection interval
        self.collection_interval = config.metrics_export_interval if config else 30
    
    def add_alert_config(self, alert_config: AlertConfig) -> None:
        """Add alert configuration for a queue"""
        self.alert_configs[alert_config.queue_name] = alert_config
        logger.info(f"Added alert config for queue {alert_config.queue_name}")
    
    def add_alert_handler(self, handler: Callable[[str, str, Dict[str, Any]], None]) -> None:
        """Add alert handler function"""
        self.alert_handlers.append(handler)
        logger.info("Added alert handler")
    
    async def start_monitoring(self) -> None:
        """Start queue monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Queue monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop queue monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Queue monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._collect_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self) -> None:
        """Collect metrics for all queues"""
        try:
            all_stats = await self.messaging_system.get_all_stats()
            
            for queue_name, stats in all_stats.items():
                metrics = await self._calculate_metrics(queue_name, stats)
                self._store_metrics(queue_name, metrics)
                
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    async def _calculate_metrics(self, queue_name: str, stats: QueueStats) -> QueueMetrics:
        """Calculate performance metrics for a queue"""
        try:
            # Get historical data for calculations
            history = self.metrics_history.get(queue_name, [])
            
            # Calculate messages per second
            messages_per_second = 0.0
            if len(history) > 0:
                prev_metrics = history[-1]
                time_diff = (datetime.utcnow() - prev_metrics.timestamp).total_seconds()
                if time_diff > 0:
                    # This is a simplified calculation - in production you'd track actual message counts
                    messages_per_second = max(0, stats.completed_messages) / time_diff
            
            # Calculate error rate
            total_messages = stats.completed_messages + stats.failed_messages
            error_rate = stats.failed_messages / total_messages if total_messages > 0 else 0.0
            
            # Calculate consumer utilization (simplified)
            consumer_utilization = min(1.0, stats.processing_messages / max(1, stats.consumer_count))
            
            # Calculate average processing time (mock data for now)
            average_processing_time = 5.0  # This would be tracked from actual message processing
            
            return QueueMetrics(
                queue_name=queue_name,
                messages_per_second=messages_per_second,
                average_processing_time=average_processing_time,
                error_rate=error_rate,
                consumer_utilization=consumer_utilization,
                queue_depth=stats.pending_messages,
                dlq_depth=stats.dead_letter_messages
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics for {queue_name}: {e}")
            return QueueMetrics(queue_name=queue_name)
    
    def _store_metrics(self, queue_name: str, metrics: QueueMetrics) -> None:
        """Store metrics in history"""
        if queue_name not in self.metrics_history:
            self.metrics_history[queue_name] = []
        
        self.metrics_history[queue_name].append(metrics)
        
        # Keep only last hour of data (assuming 30-second intervals)
        max_history = 120
        if len(self.metrics_history[queue_name]) > max_history:
            self.metrics_history[queue_name] = self.metrics_history[queue_name][-max_history:]
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions"""
        try:
            for queue_name, alert_config in self.alert_configs.items():
                if queue_name not in self.metrics_history:
                    continue
                
                latest_metrics = self.metrics_history[queue_name][-1]
                await self._check_queue_alerts(alert_config, latest_metrics)
                
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    async def _check_queue_alerts(self, alert_config: AlertConfig, metrics: QueueMetrics) -> None:
        """Check alert conditions for a specific queue"""
        try:
            alert_key = alert_config.queue_name
            now = datetime.utcnow()
            
            # Check cooldown
            if alert_key in self.last_alerts:
                time_since_last = (now - self.last_alerts[alert_key]).total_seconds()
                if time_since_last < alert_config.alert_cooldown:
                    return
            
            alerts = []
            
            # Check queue depth
            if metrics.queue_depth > alert_config.max_queue_depth:
                alerts.append({
                    "type": "high_queue_depth",
                    "message": f"Queue depth {metrics.queue_depth} exceeds threshold {alert_config.max_queue_depth}",
                    "severity": "warning",
                    "value": metrics.queue_depth,
                    "threshold": alert_config.max_queue_depth
                })
            
            # Check processing time
            if metrics.average_processing_time > alert_config.max_processing_time:
                alerts.append({
                    "type": "high_processing_time",
                    "message": f"Processing time {metrics.average_processing_time:.2f}s exceeds threshold {alert_config.max_processing_time}s",
                    "severity": "warning",
                    "value": metrics.average_processing_time,
                    "threshold": alert_config.max_processing_time
                })
            
            # Check error rate
            if metrics.error_rate > alert_config.max_error_rate:
                alerts.append({
                    "type": "high_error_rate",
                    "message": f"Error rate {metrics.error_rate:.2%} exceeds threshold {alert_config.max_error_rate:.2%}",
                    "severity": "critical",
                    "value": metrics.error_rate,
                    "threshold": alert_config.max_error_rate
                })
            
            # Check consumer utilization
            if metrics.consumer_utilization < alert_config.min_consumer_utilization:
                alerts.append({
                    "type": "low_consumer_utilization",
                    "message": f"Consumer utilization {metrics.consumer_utilization:.2%} below threshold {alert_config.min_consumer_utilization:.2%}",
                    "severity": "info",
                    "value": metrics.consumer_utilization,
                    "threshold": alert_config.min_consumer_utilization
                })
            
            # Send alerts
            for alert in alerts:
                await self._send_alert(alert_config.queue_name, alert["message"], alert)
                self.last_alerts[alert_key] = now
                
        except Exception as e:
            logger.error(f"Failed to check alerts for {alert_config.queue_name}: {e}")
    
    async def _send_alert(self, queue_name: str, message: str, alert_data: Dict[str, Any]) -> None:
        """Send alert to all registered handlers"""
        try:
            for handler in self.alert_handlers:
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, handler, queue_name, message, alert_data
                    )
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def get_queue_metrics(self, queue_name: str, hours: int = 1) -> List[QueueMetrics]:
        """Get historical metrics for a queue"""
        if queue_name not in self.metrics_history:
            return []
        
        # Filter by time range
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history[queue_name]
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_all_current_metrics(self) -> Dict[str, QueueMetrics]:
        """Get current metrics for all queues"""
        current_metrics = {}
        for queue_name, history in self.metrics_history.items():
            if history:
                current_metrics[queue_name] = history[-1]
        return current_metrics
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        if format == "json":
            return json.dumps({
                queue_name: [asdict(metric) for metric in history]
                for queue_name, history in self.metrics_history.items()
            }, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Alert handlers
def log_alert_handler(queue_name: str, message: str, alert_data: Dict[str, Any]) -> None:
    """Log alert to logger"""
    severity = alert_data.get("severity", "info")
    if severity == "critical":
        logger.error(f"CRITICAL ALERT [{queue_name}]: {message}")
    elif severity == "warning":
        logger.warning(f"WARNING [{queue_name}]: {message}")
    else:
        logger.info(f"INFO [{queue_name}]: {message}")


def console_alert_handler(queue_name: str, message: str, alert_data: Dict[str, Any]) -> None:
    """Print alert to console"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    severity = alert_data.get("severity", "info").upper()
    print(f"[{timestamp}] {severity} ALERT - {queue_name}: {message}")


async def webhook_alert_handler(webhook_url: str):
    """Create webhook alert handler"""
    import aiohttp
    
    async def handler(queue_name: str, message: str, alert_data: Dict[str, Any]) -> None:
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "queue_name": queue_name,
                "message": message,
                "alert_data": alert_data
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Webhook alert error: {e}")
    
    return handler