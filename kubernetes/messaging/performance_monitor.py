"""IA Influencer Agent - Performance Monitoring & Optimization
from datetime import datetime

Enterprise performance monitoring for messaging infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import aioredis
import psutil
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class PerformanceMetrics:
    """
Performance metrics data structure"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    queue_metrics: Dict[str, Any] = field(default_factory=dict)
    latency_metrics: Dict[str, float] = field(default_factory=dict)
    throughput_metrics: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)


class AlertRule(BaseModel):
    """
Alert rule configuration"""
    name: str = Field(..., description="Alert rule name")
    metric: str = Field(..., description="Metric to monitor")
    threshold: float = Field(..., description="Alert threshold")
    operator: str = Field(default="greater", description="Comparison operator")
    duration: int = Field(default=300, description="Duration in seconds before alert")
    severity: str = Field(default="warning", description="Alert severity")
    enabled: bool = Field(default=True, description="Rule enabled status")


class PerformanceOptimizer(BaseModel):
    """Performance optimization configuration"""
    auto_scaling_enabled: bool = Field(default=True, description="Enable auto-scaling")
    cpu_threshold_scale_up: float = Field(default=80.0, description="CPU threshold for scaling up")
    cpu_threshold_scale_down: float = Field(default=30.0, description="CPU threshold for scaling down")
    memory_threshold: float = Field(default=85.0, description="Memory threshold for alerts")
    queue_length_threshold: int = Field(default=1000, description="Queue length threshold")
    latency_threshold: float = Field(default=5000.0, description="Latency threshold in ms")
    optimization_interval: int = Field(default=60, description="Optimization check interval")


class MessagingPerformanceMonitor:
    """
    Enterprise performance monitoring system for messaging infrastructure
    Monitors system metrics, queue performance, and provides optimization
    """
    def __init__(self) -> None:
        self.redis_client: Optional[aioredis.Redis] = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.alert_rules: List[AlertRule] = []
        self.optimizer_config = PerformanceOptimizer()
        
        # Performance tracking
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.optimization_recommendations: List[Dict[str, Any]] = []
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.is_running = False

    async def initialize(self) -> None:
        """
Initialize performance monitor"""
        try:
            # Setup Redis connection
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Setup default alert rules
            self._setup_default_alert_rules()
            
            # Start monitoring
            await self._start_monitoring()
            
            self.is_running = True
            logger.info("Performance monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise

    def _setup_default_alert_rules(self) -> None:
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                metric="cpu_usage",
                threshold=85.0,
                operator="greater",
                duration=300,
                severity="warning"
            ),
            AlertRule(
                name="critical_cpu_usage",
                metric="cpu_usage",
                threshold=95.0,
                operator="greater",
                duration=60,
                severity="critical"
            ),
            AlertRule(
                name="high_memory_usage",
                metric="memory_usage",
                threshold=90.0,
                operator="greater",
                duration=300,
                severity="warning"
            ),
            AlertRule(
                name="critical_memory_usage",
                metric="memory_usage",
                threshold=98.0,
                operator="greater",
                duration=60,
                severity="critical"
            ),
            AlertRule(
                name="high_queue_length",
                metric="queue_length",
                threshold=1000.0,
                operator="greater",
                duration=180,
                severity="warning"
            ),
            AlertRule(
                name="high_message_latency",
                metric="message_latency",
                threshold=5000.0,
                operator="greater",
                duration=120,
                severity="warning"
            ),
            AlertRule(
                name="low_throughput",
                metric="message_throughput",
                threshold=100.0,
                operator="less",
                duration=600,
                severity="warning"
            ),
            AlertRule(
                name="high_error_rate",
                metric="error_rate",
                threshold=5.0,
                operator="greater",
                duration=300,
                severity="critical"
            )
        ]
        
        self.alert_rules = default_rules

    async def _start_monitoring(self) -> None:
        """Start all monitoring tasks"""
        try:
            # System metrics monitoring
            system_task = asyncio.create_task(self._monitor_system_metrics())
            self.monitoring_tasks.append(system_task)
            
            # Queue performance monitoring
            queue_task = asyncio.create_task(self._monitor_queue_performance())
            self.monitoring_tasks.append(queue_task)
            
            # Alert processing
            alert_task = asyncio.create_task(self._process_alerts())
            self.monitoring_tasks.append(alert_task)
            
            # Performance optimization
            optimization_task = asyncio.create_task(self._performance_optimization())
            self.monitoring_tasks.append(optimization_task)
            
            # Metrics cleanup
            cleanup_task = asyncio.create_task(self._cleanup_old_metrics())
            self.monitoring_tasks.append(cleanup_task)
            
            logger.info("Started performance monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    async def _monitor_system_metrics(self) -> None:
        """Monitor system-level metrics"""
        while self.is_running:
            try:
                # Collect system metrics
                metrics = await self._collect_system_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Store in Redis for external access
                await self._store_metrics_in_redis(metrics)
                
                # Check alerts
                await self._check_alert_conditions(metrics)
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system metrics monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": float(network.bytes_sent),
                "bytes_recv": float(network.bytes_recv),
                "packets_sent": float(network.packets_sent),
                "packets_recv": float(network.packets_recv)
            }
            
            # Create metrics object
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise

    async def _monitor_queue_performance(self) -> None:
        """Monitor queue-specific performance metrics"""
        while self.is_running:
            try:
                # Collect queue metrics from Redis
                queue_metrics = await self._collect_queue_metrics()
                
                # Calculate performance indicators
                performance_metrics = await self._calculate_queue_performance(queue_metrics)
                
                # Store in latest metrics
                if self.metrics_history:
                    latest_metrics = self.metrics_history[-1]
                    latest_metrics.queue_metrics = queue_metrics
                    latest_metrics.latency_metrics = performance_metrics.get("latency", {})
                    latest_metrics.throughput_metrics = performance_metrics.get("throughput", {})
                    latest_metrics.error_rates = performance_metrics.get("errors", {})
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in queue performance monitoring: {e}")
                await asyncio.sleep(120)

    async def _collect_queue_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all queues"""
        try:
            queue_metrics = {}
            
            # Get all queue keys
            queue_keys = await self.redis_client.keys("queue:*:stats")
            
            for key in queue_keys:
                queue_name = key.split(":")[1]
                
                # Get queue lengths
                pending_count = 0
                for priority in ["critical", "high", "medium", "low"]:
                    count = await self.redis_client.llen(f"queue:{queue_name}:{priority}")
                    pending_count += count
                
                # Get active tasks
                active_count = await self.redis_client.scard(f"queue:{queue_name}:active")
                
                # Get dead letter queue count
                dlq_count = await self.redis_client.llen(f"queue:{queue_name}:dlq")
                
                queue_metrics[queue_name] = {
                    "pending_tasks": pending_count,
                    "active_tasks": active_count,
                    "dlq_tasks": dlq_count,
                    "total_length": pending_count + active_count
                }
            
            return queue_metrics
            
        except Exception as e:
            logger.error(f"Error collecting queue metrics: {e}")
            return {}

    async def _calculate_queue_performance(self, queue_metrics: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Calculate queue performance indicators"""
        try:
            performance = {
                "latency": {},
                "throughput": {},
                "errors": {}
            }
            
            # Calculate metrics for each queue
            for queue_name, metrics in queue_metrics.items():
                # Average latency (placeholder - would need actual timing data)
                performance["latency"][queue_name] = self._estimate_queue_latency(metrics)
                
                # Throughput calculation (messages per minute)
                performance["throughput"][queue_name] = await self._calculate_throughput(queue_name)
                
                # Error rate calculation
                performance["errors"][queue_name] = await self._calculate_error_rate(queue_name)
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating queue performance: {e}")
            return {"latency": {}, "throughput": {}, "errors": {}}

    def _estimate_queue_latency(self, metrics: Dict[str, Any]) -> float:
        """Estimate queue latency based on queue length and processing rate"""
        try:
            # Simple estimation: pending_tasks / estimated_processing_rate
            pending = metrics.get("pending_tasks", 0)
            active = metrics.get("active_tasks", 1)
            
            # Assume 1 task per second per active worker
            estimated_latency = (pending / max(active, 1)) * 1000  # Convert to milliseconds
            
            return min(estimated_latency, 60000)  # Cap at 1 minute
            
        except Exception as e:
            logger.error(f"Error estimating queue latency: {e}")
            return 0.0

    async def _calculate_throughput(self, queue_name: str) -> float:
        """Calculate throughput for a queue"""
        try:
            # Get completed tasks count from Redis
            completed_key = f"queue:{queue_name}:completed_count"
            current_completed = await self.redis_client.get(completed_key) or 0
            current_completed = int(current_completed)
            
            # Get last completed count
            last_completed_key = f"queue:{queue_name}:last_completed"
            last_completed = await self.redis_client.get(last_completed_key) or current_completed
            last_completed = int(last_completed)
            
            # Calculate throughput (tasks per minute)
            time_diff = 60  # 1 minute interval
            throughput = (current_completed - last_completed) / (time_diff / 60)
            
            # Update last completed count
            await self.redis_client.set(last_completed_key, current_completed)
            
            return throughput
            
        except Exception as e:
            logger.error(f"Error calculating throughput for {queue_name}: {e}")
            return 0.0

    async def _calculate_error_rate(self, queue_name: str) -> float:
        """Calculate error rate for a queue"""
        try:
            # Get DLQ count and total processed
            dlq_count = await self.redis_client.llen(f"queue:{queue_name}:dlq")
            completed_count = await self.redis_client.get(f"queue:{queue_name}:completed_count") or 0
            completed_count = int(completed_count)
            
            total_processed = dlq_count + completed_count
            
            if total_processed == 0:
                return 0.0
            
            error_rate = (dlq_count / total_processed) * 100
            return error_rate
            
        except Exception as e:
            logger.error(f"Error calculating error rate for {queue_name}: {e}")
            return 0.0

    async def _store_metrics_in_redis(self, metrics: PerformanceMetrics) -> None:
        """Store metrics in Redis for external access"""
        try:
            metrics_data = {
                "timestamp": metrics.timestamp,
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "disk_usage": metrics.disk_usage,
                "network_bytes_sent": metrics.network_io.get("bytes_sent", 0),
                "network_bytes_recv": metrics.network_io.get("bytes_recv", 0)
            }
            
            # Store latest metrics
            await self.redis_client.hset("performance:latest", mapping=metrics_data)
            
            # Store in time series (last 24 hours)
            timestamp_key = int(metrics.timestamp)
            await self.redis_client.zadd(
                "performance:timeseries",
                {f"{timestamp_key}:{metrics.cpu_usage}:{metrics.memory_usage}": timestamp_key}
            )
            
            # Cleanup old entries (keep last 24 hours)
            cutoff_time = time.time() - 86400  # 24 hours
            await self.redis_client.zremrangebyscore("performance:timeseries", 0, cutoff_time)
            
        except Exception as e:
            logger.error(f"Error storing metrics in Redis: {e}")

    async def _check_alert_conditions(self, metrics: PerformanceMetrics) -> None:
        """Check alert conditions against current metrics"""
        try:
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue
                
                # Get metric value
                metric_value = self._get_metric_value(metrics, rule.metric)
                if metric_value is None:
                    continue
                
                # Check threshold
                alert_triggered = self._evaluate_threshold(metric_value, rule.threshold, rule.operator)
                
                if alert_triggered:
                    await self._handle_alert(rule, metric_value, metrics.timestamp)
                else:
                    # Clear alert if it was active
                    if rule.name in self.active_alerts:
                        await self._clear_alert(rule.name)
                        
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")

    def _get_metric_value(self, metrics: PerformanceMetrics, metric_name: str) -> Optional[float]:
        """Extract metric value from metrics object"""
        try:
            if metric_name == "cpu_usage":
                return metrics.cpu_usage
            elif metric_name == "memory_usage":
                return metrics.memory_usage
            elif metric_name == "disk_usage":
                return metrics.disk_usage
            elif metric_name == "queue_length":
                # Sum all queue lengths
                total_length = 0
                for queue_metrics in metrics.queue_metrics.values():
                    total_length += queue_metrics.get("total_length", 0)
                return float(total_length)
            elif metric_name == "message_latency":
                # Average latency across all queues
                latencies = list(metrics.latency_metrics.values())
                return statistics.mean(latencies) if latencies else 0.0
            elif metric_name == "message_throughput":
                # Total throughput across all queues
                return sum(metrics.throughput_metrics.values())
            elif metric_name == "error_rate":
                # Average error rate across all queues
                error_rates = list(metrics.error_rates.values())
                return statistics.mean(error_rates) if error_rates else 0.0
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting metric value for {metric_name}: {e}")
            return None

    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate threshold condition"""
        try:
            if operator == "greater":
                return value > threshold
            elif operator == "less":
                return value < threshold
            elif operator == "equal":
                return abs(value - threshold) < 0.01
            elif operator == "greater_equal":
                return value >= threshold
            elif operator == "less_equal":
                return value <= threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating threshold: {e}")
            return False

    async def _handle_alert(self, rule: AlertRule, metric_value: float, timestamp: float) -> None:
        """Handle triggered alert"""
        try:
            alert_key = rule.name
            
            if alert_key in self.active_alerts:
                # Update existing alert
                alert = self.active_alerts[alert_key]
                alert["last_triggered"] = timestamp
                alert["current_value"] = metric_value
                
                # Check if duration threshold is met
                if timestamp - alert["first_triggered"] >= rule.duration:
                    await self._fire_alert(rule, metric_value, alert)
            else:
                # New alert
                self.active_alerts[alert_key] = {
                    "rule": rule,
                    "first_triggered": timestamp,
                    "last_triggered": timestamp,
                    "current_value": metric_value,
                    "fired": False
                }
                
        except Exception as e:
            logger.error(f"Error handling alert: {e}")

    async def _fire_alert(self, rule: AlertRule, metric_value: float, alert: Dict[str, Any]) -> None:
        """Fire an alert"""
        try:
            if alert["fired"]:
                return  # Already fired
            
            alert["fired"] = True
            alert["fired_at"] = time.time()
            
            # Log alert
            logger.warning(
                f"ALERT: {rule.name} - {rule.metric} is {metric_value:.2f} "
                f"(threshold: {rule.threshold}, severity: {rule.severity})"
            )
            
            # Store alert in Redis
            alert_data = {
                "rule_name": rule.name,
                "metric": rule.metric,
                "current_value": metric_value,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "fired_at": alert["fired_at"]
            }
            
            await self.redis_client.lpush("alerts:active", str(alert_data))
            await self.redis_client.ltrim("alerts:active", 0, 100)  # Keep last 100 alerts
            
            # Send notifications (email, SMS, Slack, webhook)
            await self._send_performance_alert_notifications(rule, metric_value, alert_data)
            
        except Exception as e:
            logger.error(f"Error firing alert: {e}")

    async def _clear_alert(self, alert_name: str) -> None:
        """Clear an active alert"""
        try:
            if alert_name in self.active_alerts:
                logger.info(f"CLEARED: Alert {alert_name} resolved")
                del self.active_alerts[alert_name]
                
        except Exception as e:
            logger.error(f"Error clearing alert: {e}")

    async def _process_alerts(self) -> None:
        """Process active alerts"""
        while self.is_running:
            try:
                # Check for stale alerts
                current_time = time.time()
                stale_alerts = []
                
                for alert_name, alert in self.active_alerts.items():
                    # Clear alerts that haven't been triggered in 5 minutes
                    if current_time - alert["last_triggered"] > 300:
                        stale_alerts.append(alert_name)
                
                for alert_name in stale_alerts:
                    await self._clear_alert(alert_name)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(120)

    async def _performance_optimization(self) -> None:
        """Perform automated performance optimization"""
        while self.is_running:
            try:
                if self.optimizer_config.auto_scaling_enabled:
                    await self._auto_optimize_performance()
                
                await asyncio.sleep(self.optimizer_config.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in performance optimization: {e}")
                await asyncio.sleep(300)

    async def _auto_optimize_performance(self) -> None:
        """Auto-optimize performance based on current metrics"""
        try:
            if not self.metrics_history:
                return
            
            latest_metrics = self.metrics_history[-1]
            recommendations = []
            
            # CPU optimization
            if latest_metrics.cpu_usage > self.optimizer_config.cpu_threshold_scale_up:
                recommendations.append({
                    "type": "scale_up",
                    "component": "workers",
                    "reason": f"High CPU usage: {latest_metrics.cpu_usage:.1f}%",
                    "priority": "high"
                })
            elif latest_metrics.cpu_usage < self.optimizer_config.cpu_threshold_scale_down:
                recommendations.append({
                    "type": "scale_down",
                    "component": "workers",
                    "reason": f"Low CPU usage: {latest_metrics.cpu_usage:.1f}%",
                    "priority": "low"
                })
            
            # Memory optimization
            if latest_metrics.memory_usage > self.optimizer_config.memory_threshold:
                recommendations.append({
                    "type": "memory_cleanup",
                    "component": "cache",
                    "reason": f"High memory usage: {latest_metrics.memory_usage:.1f}%",
                    "priority": "medium"
                })
            
            # Queue optimization
            for queue_name, metrics in latest_metrics.queue_metrics.items():
                if metrics.get("total_length", 0) > self.optimizer_config.queue_length_threshold:
                    recommendations.append({
                        "type": "scale_queue_workers",
                        "component": queue_name,
                        "reason": f"High queue length: {metrics['total_length']}",
                        "priority": "high"
                    })
            
            # Store recommendations
            self.optimization_recommendations = recommendations
            
            # Log recommendations
            for rec in recommendations:
                logger.info(f"Optimization recommendation: {rec['type']} for {rec['component']} - {rec['reason']}")
                
        except Exception as e:
            logger.error(f"Error in auto-optimization: {e}")

    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory issues"""
        while self.is_running:
            try:
                # Keep only last 1000 metrics (about 8 hours at 30s intervals)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(3600)

    async def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        try:
            if self.metrics_history:
                return self.metrics_history[-1]
            return None
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return None

    async def get_metrics_history(self, duration_minutes: int = 60) -> List[PerformanceMetrics]:
        """Get metrics history for specified duration"""
        try:
            cutoff_time = time.time() - (duration_minutes * 60)
            
            filtered_metrics = [
                m for m in self.metrics_history
                if m.timestamp >= cutoff_time
            ]
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics history: {e}")
            return []

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            if not self.metrics_history:
                return {"status": "no_data"}
            
            # Get recent metrics (last hour)
            recent_metrics = await self.get_metrics_history(60)
            
            if not recent_metrics:
                return {"status": "no_recent_data"}
            
            # Calculate averages
            avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
            avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_disk = statistics.mean([m.disk_usage for m in recent_metrics])
            
            # Get current status
            current = recent_metrics[-1]
            
            return {
                "status": "healthy" if avg_cpu < 80 and avg_memory < 85 else "warning",
                "current_metrics": {
                    "cpu_usage": current.cpu_usage,
                    "memory_usage": current.memory_usage,
                    "disk_usage": current.disk_usage,
                    "timestamp": current.timestamp
                },
                "averages_1h": {
                    "cpu_usage": avg_cpu,
                    "memory_usage": avg_memory,
                    "disk_usage": avg_disk
                },
                "active_alerts": len(self.active_alerts),
                "optimization_recommendations": len(self.optimization_recommendations),
                "queue_metrics": current.queue_metrics,
                "latency_metrics": current.latency_metrics,
                "throughput_metrics": current.throughput_metrics,
                "error_rates": current.error_rates
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"status": "error", "error": str(e)}

    async def _send_performance_alert_notifications(
        self, 
        rule, 
        metric_value: float, 
        alert_data: Dict[str, Any]
    ) -> None:
        """
        Send notifications for performance alerts
        
        Args:
            rule: Alert rule that triggered
            metric_value: Current metric value
            alert_data: Alert data dictionary
        """
        try:
            notification_payload = {
                "alert_type": "performance_threshold_exceeded",
                "severity": rule.severity,
                "metric_name": rule.metric,
                "current_value": metric_value,
                "threshold": rule.threshold,
                "rule_name": rule.name,
                "timestamp": alert_data["fired_at"],
                "system": "ainflue_performance_monitor",
                "message": f"Performance alert: {rule.name} - {rule.metric} is {metric_value:.2f} (threshold: {rule.threshold})",
                "metadata": {
                    "rule_description": getattr(rule, 'description', ''),
                    "comparison": rule.comparison,
                    "alert_data": alert_data
                }
            }
            
            # Send notifications based on severity
            if rule.severity in ["critical", "high"]:
                # Send all notification types for critical/high severity
                await self._send_email_alert(notification_payload)
                await self._send_slack_alert(notification_payload)
                await self._send_webhook_alert(notification_payload)
                
                if rule.severity == "critical":
                    await self._send_sms_alert(notification_payload)
            
            elif rule.severity == "medium":
                # Send email and Slack for medium severity
                await self._send_email_alert(notification_payload)
                await self._send_slack_alert(notification_payload)
            
            else:  # low severity
                # Send only Slack for low severity
                await self._send_slack_alert(notification_payload)
            
            logger.info(f"Performance alert notifications sent for rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Failed to send performance alert notifications: {e}")
    
    async def _send_email_alert(self, notification_payload: Dict[str, Any]) -> None:
        """Send email alert notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os
            
            # Email configuration
            smtp_server = os.environ.get('PERF_SMTP_SERVER', 'localhost')
            smtp_port = int(os.environ.get('PERF_SMTP_PORT', '587'))
            smtp_user = os.environ.get('PERF_SMTP_USER')
            smtp_password = os.environ.get('PERF_SMTP_PASSWORD')
            recipients = os.environ.get('PERF_EMAIL_RECIPIENTS', '').split(',')
            
            if not smtp_user or not recipients[0]:
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"[AINFLUE PERF] {notification_payload['severity'].upper()}: {notification_payload['rule_name']}"
            
            # Email body
            body = f"""
            AINFLUE PERFORMANCE ALERT
            ========================
            
            Rule: {notification_payload['rule_name']}
            Metric: {notification_payload['metric_name']}
            Current Value: {notification_payload['current_value']:.2f}
            Threshold: {notification_payload['threshold']}
            Severity: {notification_payload['severity']}
            Timestamp: {notification_payload['timestamp']}
            
            Message: {notification_payload['message']}
            
            Please investigate and take appropriate action.
            
            System: {notification_payload['system']}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info("Performance alert email sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send performance alert email: {e}")
    
    async def _send_slack_alert(self, notification_payload: Dict[str, Any]) -> None:
        """Send Slack alert notification"""
        try:
            import aiohttp
            import os
            
            webhook_url = os.environ.get('PERF_SLACK_WEBHOOK_URL')
            if not webhook_url:
                return
            
            # Create Slack payload
            severity_colors = {
                "critical": "#FF0000",
                "high": "#FF6600",
                "medium": "#FFAA00",
                "low": "#00FF00"
            }
            
            severity_emojis = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "💛",
                "low": "ℹ️"
            }
            
            emoji = severity_emojis.get(notification_payload['severity'], "📊")
            color = severity_colors.get(notification_payload['severity'], "#808080")
            
            slack_payload = {
                "text": f"{emoji} Ainflue Performance Alert: {notification_payload['rule_name']}",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Metric",
                                "value": notification_payload['metric_name'],
                                "short": True
                            },
                            {
                                "title": "Current Value",
                                "value": f"{notification_payload['current_value']:.2f}",
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": str(notification_payload['threshold']),
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": notification_payload['severity'].upper(),
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": notification_payload['message'],
                                "short": False
                            }
                        ],
                        "footer": "Ainflue Performance Monitor",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_payload) as response:
                    if response.status == 200:
                        logger.info("Performance alert Slack notification sent successfully")
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Failed to send performance alert Slack notification: {e}")
    
    async def _send_webhook_alert(self, notification_payload: Dict[str, Any]) -> None:
        """Send webhook alert notification"""
        try:
            import aiohttp
            import os
            
            webhook_url = os.environ.get('PERF_WEBHOOK_URL')
            if not webhook_url:
                return
            
            # Send full payload via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=notification_payload) as response:
                    if response.status in [200, 201, 202]:
                        logger.info("Performance alert webhook notification sent successfully")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Failed to send performance alert webhook notification: {e}")
    
    async def _send_sms_alert(self, notification_payload: Dict[str, Any]) -> None:
        """Send SMS alert notification for critical alerts"""
        try:
            import os
            
            # SMS configuration
            account_sid = os.environ.get('PERF_TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('PERF_TWILIO_AUTH_TOKEN')
            from_number = os.environ.get('PERF_TWILIO_FROM_NUMBER')
            to_numbers = os.environ.get('PERF_SMS_RECIPIENTS', '').split(',')
            
            if not all([account_sid, auth_token, from_number]) or not to_numbers[0]:
                return
            
            # Create short SMS message
            sms_message = f"CRITICAL: Ainflue {notification_payload['metric_name']} alert: {notification_payload['current_value']:.1f} exceeds {notification_payload['threshold']}. Check system immediately."
            
            # Log SMS (in production, use real SMS API)
            logger.info(f"SMS alert would be sent to {len(to_numbers)} recipients")
            logger.info(f"SMS message: {sms_message}")
            
            # In production environment:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # for to_number in to_numbers:
            #     message = client.messages.create(
            #         body=sms_message,
            #         from_=from_number,
            #         to=to_number.strip()
            #     )
            
        except Exception as e:
            logger.error(f"Failed to send performance alert SMS: {e}")

    async def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add a new alert rule"""
        try:
            # Check if rule already exists
            for existing_rule in self.alert_rules:
                if existing_rule.name == rule.name:
                    return False
            
            self.alert_rules.append(rule)
            logger.info(f"Added alert rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding alert rule: {e}")
            return False

    async def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule"""
        try:
            self.alert_rules = [r for r in self.alert_rules if r.name != rule_name]
            
            # Clear active alert if exists
            if rule_name in self.active_alerts:
                del self.active_alerts[rule_name]
            
            logger.info(f"Removed alert rule: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing alert rule: {e}")
            return False

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        try:
            active_alerts = []
            
            for alert_name, alert in self.active_alerts.items():
                active_alerts.append({
                    "name": alert_name,
                    "rule": alert["rule"].dict(),
                    "first_triggered": alert["first_triggered"],
                    "last_triggered": alert["last_triggered"],
                    "current_value": alert["current_value"],
                    "fired": alert["fired"]
                })
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []

    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get current optimization recommendations"""
        return self.optimization_recommendations.copy()

    async def shutdown(self) -> None:
        """
Shutdown performance monitor"""
        try:
            logger.info("Shutting down performance monitor")
            
            self.is_running = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Performance monitor shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
