"""Events Monitoring Hub for IA Influencer Agent Platform
=====================================================

Consolidated events and monitoring system combining event streaming,
monitoring, and alerting functionality for enterprise streaming operations.

CONSOLIDATED ARCHITECTURE:
- EventsMonitoringHub: Main orchestrator for events and monitoring
- EventStreamer: Legacy compatibility for event streaming
- StreamMonitor: Legacy compatibility for monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import threading
from queue import Queue, Empty
import statistics

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for stream processing"""
    STREAM_CREATED = "stream_created"
    STREAM_STARTED = "stream_started"
    STREAM_STOPPED = "stream_stopped"
    STREAM_ERROR = "stream_error"
    CONTENT_PROCESSED = "content_processed"
    CONTENT_FAILED = "content_failed"
    PROTECTION_TRIGGERED = "protection_triggered"
    REVENUE_GENERATED = "revenue_generated"
    PLATFORM_SYNC = "platform_sync"
    SYSTEM_ALERT = "system_alert"
    PERFORMANCE_WARNING = "performance_warning"
    SECURITY_EVENT = "security_event"
    USER_ACTION = "user_action"
    CUSTOM = "custom"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringMetric(str, Enum):
    """Monitoring metric types"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    ACTIVE_STREAMS = "active_streams"
    QUEUE_SIZE = "queue_size"
    WORKER_UTILIZATION = "worker_utilization"


class HealthStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class Event:
    """Event data structure"""
    event_id: str
    event_type: EventType
    source: str
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class EventHandler:
    """Event handler configuration"""
    handler_id: str
    event_types: Set[EventType]
    callback: Callable
    filter_conditions: Dict[str, Any] = field(default_factory=dict)
    is_async: bool = True
    max_concurrent: int = 10
    timeout_seconds: float = 30.0
    retry_on_failure: bool = True


@dataclass
class MetricSample:
    """Metric sample data point"""
    metric_type: MonitoringMetric
    value: float
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    source: str
    metric_type: Optional[MonitoringMetric] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


@dataclass
class HealthCheck:
    """Health check result"""
    check_id: str
    check_name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventsMonitoringHub:
    """
    Consolidated events and monitoring hub combining event streaming,
    monitoring, alerting, and health checking functionality.
    
    Features:
    - High-performance event processing and routing
    - Real-time system monitoring and metrics collection
    - Intelligent alerting and notification system
    - Comprehensive health checking and status reporting
    - Event filtering, correlation, and pattern detection
    """
    
    def __init__(
        self,
        max_event_handlers: int = 100,
        max_event_queue_size: int = 10000,
        metrics_retention_hours: int = 24,
        enable_correlation: bool = True
    ):
        # Configuration
        self.max_event_handlers = max_event_handlers
        self.max_event_queue_size = max_event_queue_size
        self.metrics_retention_hours = metrics_retention_hours
        self.enable_correlation = enable_correlation
        
        # Event management
        self.event_handlers: Dict[str, EventHandler] = {}
        self.event_queue = Queue(maxsize=max_event_queue_size)
        self.event_history: deque = deque(maxlen=10000)
        self.event_stats: Dict[str, int] = defaultdict(int)
        
        # Monitoring infrastructure
        self.metrics_buffer: Dict[MonitoringMetric, deque] = {
            metric: deque(maxlen=1440)  # 24 hours at 1-minute intervals
            for metric in MonitoringMetric
        }
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.health_checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, HealthCheck] = {}
        
        # Performance tracking
        self.processing_stats = {
            "events_processed": 0,
            "events_failed": 0,
            "average_processing_time": 0.0,
            "peak_processing_time": 0.0
        }
        
        # Background tasks
        self.event_processor_thread: Optional[threading.Thread] = None
        self.metrics_collector_task: Optional[asyncio.Task] = None
        self.health_checker_task: Optional[asyncio.Task] = None
        self.alert_manager_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = threading.Event()
        self._lock = threading.RLock()
        
        logger.info("EventsMonitoringHub initialized")
        
    async def initialize(self) -> None:
        """Initialize the events monitoring hub"""
        try:
            with self._lock:
                if self._running:
                    return
                    
                # Start event processor
                self._start_event_processor()
                
                # Start background tasks
                self.metrics_collector_task = asyncio.create_task(self._metrics_collector())
                self.health_checker_task = asyncio.create_task(self._health_checker())
                self.alert_manager_task = asyncio.create_task(self._alert_manager())
                
                self._running = True
                logger.info("EventsMonitoringHub initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize EventsMonitoringHub: {e}")
            raise
            
    async def register_event_handler(
        self,
        handler_id: str,
        event_types: Union[EventType, List[EventType]],
        callback: Callable,
        filter_conditions: Optional[Dict[str, Any]] = None,
        is_async: bool = True,
        max_concurrent: int = 10,
        timeout_seconds: float = 30.0
    ) -> bool:
        """
        Register an event handler
        
        Args:
            handler_id: Unique handler identifier
            event_types: Event types to handle
            callback: Handler callback function
            filter_conditions: Optional event filtering conditions
            is_async: Whether the callback is async
            max_concurrent: Maximum concurrent handler executions
            timeout_seconds: Handler timeout
            
        Returns:
            Success status
        """
        try:
            if len(self.event_handlers) >= self.max_event_handlers:
                logger.error("Maximum event handlers limit reached")
                return False
                
            if isinstance(event_types, EventType):
                event_types = [event_types]
                
            handler = EventHandler(
                handler_id=handler_id,
                event_types=set(event_types),
                callback=callback,
                filter_conditions=filter_conditions or {},
                is_async=is_async,
                max_concurrent=max_concurrent,
                timeout_seconds=timeout_seconds
            )
            
            with self._lock:
                self.event_handlers[handler_id] = handler
                
            logger.info(f"Event handler {handler_id} registered for {len(event_types)} event types")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register event handler {handler_id}: {e}")
            return False
            
    async def emit_event(
        self,
        event_type: EventType,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        target: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        tags: Optional[Set[str]] = None
    ) -> str:
        """
        Emit an event to the system
        
        Args:
            event_type: Type of event
            source: Event source identifier
            data: Optional event data
            target: Optional target identifier
            priority: Event priority
            correlation_id: Optional correlation ID for event tracking
            tags: Optional event tags
            
        Returns:
            Event ID
        """
        try:
            event_id = str(uuid.uuid4())
            
            event = Event(
                event_id=event_id,
                event_type=event_type,
                source=source,
                target=target,
                data=data or {},
                priority=priority,
                correlation_id=correlation_id,
                trace_id=str(uuid.uuid4()) if not correlation_id else correlation_id,
                tags=tags or set()
            )
            
            # Add to queue for processing
            try:
                self.event_queue.put(event, block=False)
                logger.debug(f"Event {event_id} queued for processing")
                return event_id
            except:
                logger.error(f"Event queue full, dropping event {event_id}")
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
            return ""
            
    async def record_metric(
        self,
        metric_type: MonitoringMetric,
        value: float,
        source: str,
        tags: Optional[Dict[str, str]] = None,
        unit: str = ""
    ) -> None:
        """
        Record a metric sample
        
        Args:
            metric_type: Type of metric
            value: Metric value
            source: Source of the metric
            tags: Optional metric tags
            unit: Optional unit of measurement
        """
        try:
            sample = MetricSample(
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(timezone.utc),
                source=source,
                tags=tags or {},
                unit=unit
            )
            
            # Add to metrics buffer
            if metric_type in self.metrics_buffer:
                self.metrics_buffer[metric_type].append(sample)
                
            # Check for alert conditions
            await self._check_metric_alerts(sample)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            
    async def register_health_check(
        self,
        check_id: str,
        check_name: str,
        check_function: Callable
    ) -> bool:
        """
        Register a health check function
        
        Args:
            check_id: Unique check identifier
            check_name: Human-readable check name
            check_function: Function to execute for health check
            
        Returns:
            Success status
        """
        try:
            with self._lock:
                self.health_checks[check_id] = check_function
                
            logger.info(f"Health check {check_name} registered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register health check {check_name}: {e}")
            return False
            
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Calculate overall health
            health_scores = []
            for check in self.health_status.values():
                if check.status == HealthStatus.HEALTHY:
                    health_scores.append(100)
                elif check.status == HealthStatus.DEGRADED:
                    health_scores.append(70)
                elif check.status == HealthStatus.UNHEALTHY:
                    health_scores.append(30)
                else:  # CRITICAL
                    health_scores.append(0)
                    
            overall_score = statistics.mean(health_scores) if health_scores else 100
            
            if overall_score >= 90:
                overall_status = HealthStatus.HEALTHY
            elif overall_score >= 70:
                overall_status = HealthStatus.DEGRADED
            elif overall_score >= 30:
                overall_status = HealthStatus.UNHEALTHY
            else:
                overall_status = HealthStatus.CRITICAL
                
            return {
                "overall_status": overall_status.value,
                "overall_score": overall_score,
                "checks": {
                    check_id: {
                        "name": check.check_name,
                        "status": check.status.value,
                        "message": check.message,
                        "timestamp": check.timestamp.isoformat(),
                        "execution_time_ms": check.execution_time_ms
                    }
                    for check_id, check in self.health_status.items()
                },
                "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
                "total_events_processed": self.processing_stats["events_processed"],
                "event_processing_rate": self._calculate_event_rate()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {}
            
    async def get_metrics_summary(
        self,
        metric_type: MonitoringMetric,
        time_range_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get metrics summary for specified time range"""
        try:
            if metric_type not in self.metrics_buffer:
                return {}
                
            # Filter metrics by time range
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_range_minutes)
            recent_metrics = [
                sample for sample in self.metrics_buffer[metric_type]
                if sample.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
                
            values = [sample.value for sample in recent_metrics]
            
            return {
                "metric_type": metric_type.value,
                "time_range_minutes": time_range_minutes,
                "sample_count": len(values),
                "current_value": values[-1] if values else 0,
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "trend": self._calculate_trend(values)
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}
            
    async def create_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        title: str,
        description: str,
        source: str,
        metric_type: Optional[MonitoringMetric] = None,
        threshold_value: Optional[float] = None,
        current_value: Optional[float] = None
    ) -> str:
        """Create a new alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = Alert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                source=source,
                metric_type=metric_type,
                threshold_value=threshold_value,
                current_value=current_value
            )
            
            with self._lock:
                self.alerts[alert_id] = alert
                
            # Notify alert handlers
            await self._notify_alert_handlers(alert)
            
            logger.warning(f"Alert created: {title} ({severity.value})")
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return ""
            
    def _start_event_processor(self) -> None:
        """Start event processor thread"""
        self.event_processor_thread = threading.Thread(
            target=self._event_processor_worker,
            daemon=True
        )
        self.event_processor_thread.start()
        logger.info("Event processor started")
        
    def _event_processor_worker(self) -> None:
        """Event processor main loop"""
        logger.info("Event processor worker started")
        
        while not self._shutdown_event.is_set():
            try:
                # Get event from queue
                try:
                    event = self.event_queue.get(timeout=1.0)
                except Empty:
                    continue
                    
                # Process the event
                start_time = time.time()
                success = self._process_event(event)
                processing_time = time.time() - start_time
                
                # Update statistics
                if success:
                    self.processing_stats["events_processed"] += 1
                else:
                    self.processing_stats["events_failed"] += 1
                    
                # Update processing time stats
                total_events = self.processing_stats["events_processed"] + self.processing_stats["events_failed"]
                if total_events > 1:
                    avg_time = self.processing_stats["average_processing_time"]
                    self.processing_stats["average_processing_time"] = (avg_time * (total_events - 1) + processing_time) / total_events
                else:
                    self.processing_stats["average_processing_time"] = processing_time
                    
                self.processing_stats["peak_processing_time"] = max(
                    self.processing_stats["peak_processing_time"],
                    processing_time
                )
                
                # Add to history
                event.status = EventStatus.PROCESSED if success else EventStatus.FAILED
                self.event_history.append(event)
                
                # Update event stats
                self.event_stats[event.event_type.value] += 1
                
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Event processor error: {e}")
                
        logger.info("Event processor worker stopped")
        
    def _process_event(self, event: Event) -> bool:
        """Process a single event"""
        try:
            event.status = EventStatus.PROCESSING
            
            # Find matching handlers
            matching_handlers = []
            for handler in self.event_handlers.values():
                if event.event_type in handler.event_types:
                    if self._matches_filter(event, handler.filter_conditions):
                        matching_handlers.append(handler)
                        
            # Execute handlers
            success = True
            for handler in matching_handlers:
                try:
                    if handler.is_async:
                        # Run async handler in thread
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(
                                asyncio.wait_for(
                                    handler.callback(event),
                                    timeout=handler.timeout_seconds
                                )
                            )
                        finally:
                            loop.close()
                    else:
                        # Run sync handler
                        handler.callback(event)
                        
                except Exception as e:
                    logger.error(f"Handler {handler.handler_id} failed: {e}")
                    success = False
                    
                    if handler.retry_on_failure and event.retry_count < event.max_retries:
                        event.retry_count += 1
                        event.status = EventStatus.PENDING
                        self.event_queue.put(event)
                        
            return success
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            return False
            
    def _matches_filter(self, event: Event, filter_conditions: Dict[str, Any]) -> bool:
        """Check if event matches filter conditions"""
        try:
            for key, expected_value in filter_conditions.items():
                if key == "source" and event.source != expected_value:
                    return False
                elif key == "target" and event.target != expected_value:
                    return False
                elif key == "priority" and event.priority != expected_value:
                    return False
                elif key in event.data and event.data[key] != expected_value:
                    return False
                elif key in event.metadata and event.metadata[key] != expected_value:
                    return False
                elif key == "tags" and not set(expected_value).issubset(event.tags):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Filter matching error: {e}")
            return False
            
    async def _metrics_collector(self) -> None:
        """Background metrics collection task"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Clean old metrics
                await self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        try:
            # Event processing metrics
            await self.record_metric(
                MonitoringMetric.THROUGHPUT,
                self._calculate_event_rate(),
                "events_monitoring_hub"
            )
            
            # Queue size metric
            await self.record_metric(
                MonitoringMetric.QUEUE_SIZE,
                self.event_queue.qsize(),
                "events_monitoring_hub"
            )
            
            # Active handlers metric
            await self.record_metric(
                MonitoringMetric.ACTIVE_STREAMS,
                len(self.event_handlers),
                "events_monitoring_hub"
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            
    def _calculate_event_rate(self) -> float:
        """Calculate current event processing rate"""
        try:
            recent_events = [
                event for event in self.event_history
                if event.timestamp >= datetime.now(timezone.utc) - timedelta(minutes=5)
            ]
            return len(recent_events) / 5.0  # Events per minute over last 5 minutes
        except:
            return 0.0
            
    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics based on retention policy"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.metrics_retention_hours)
            
            for metric_type, samples in self.metrics_buffer.items():
                while samples and samples[0].timestamp < cutoff_time:
                    samples.popleft()
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            
    async def _health_checker(self) -> None:
        """Background health checking task"""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Execute all health checks
                for check_id, check_function in self.health_checks.items():
                    await self._execute_health_check(check_id, check_function)
                    
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                
    async def _execute_health_check(self, check_id: str, check_function: Callable) -> None:
        """Execute a single health check"""
        try:
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
                
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Parse result
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "healthy"))
                message = result.get("message", "OK")
                metadata = result.get("metadata", {})
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "OK" if result else "Check failed"
                metadata = {}
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                metadata = {}
                
            health_check = HealthCheck(
                check_id=check_id,
                check_name=check_id.replace("_", " ").title(),
                status=status,
                message=message,
                execution_time_ms=execution_time,
                metadata=metadata
            )
            
            with self._lock:
                self.health_status[check_id] = health_check
                
        except Exception as e:
            health_check = HealthCheck(
                check_id=check_id,
                check_name=check_id.replace("_", " ").title(),
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {e}",
                execution_time_ms=0.0
            )
            
            with self._lock:
                self.health_status[check_id] = health_check
                
            logger.error(f"Health check {check_id} failed: {e}")
            
    async def _alert_manager(self) -> None:
        """Background alert management task"""
        while self._running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                # Auto-resolve alerts based on conditions
                await self._auto_resolve_alerts()
                
                # Escalate critical unacknowledged alerts
                await self._escalate_alerts()
                
            except Exception as e:
                logger.error(f"Alert manager error: {e}")
                
    async def _check_metric_alerts(self, sample: MetricSample) -> None:
        """Check if metric sample triggers any alerts"""
        try:
            # Define alert thresholds
            thresholds = {
                MonitoringMetric.CPU_USAGE: {"warning": 80, "critical": 95},
                MonitoringMetric.MEMORY_USAGE: {"warning": 80, "critical": 95},
                MonitoringMetric.ERROR_RATE: {"warning": 5, "critical": 10},
                MonitoringMetric.LATENCY: {"warning": 1000, "critical": 5000},
                MonitoringMetric.QUEUE_SIZE: {"warning": 5000, "critical": 8000}
            }
            
            if sample.metric_type in thresholds:
                threshold = thresholds[sample.metric_type]
                
                if sample.value >= threshold["critical"]:
                    await self.create_alert(
                        "metric_threshold",
                        AlertSeverity.CRITICAL,
                        f"Critical {sample.metric_type.value}",
                        f"{sample.metric_type.value} is {sample.value} (threshold: {threshold['critical']})",
                        sample.source,
                        sample.metric_type,
                        threshold["critical"],
                        sample.value
                    )
                elif sample.value >= threshold["warning"]:
                    await self.create_alert(
                        "metric_threshold",
                        AlertSeverity.WARNING,
                        f"High {sample.metric_type.value}",
                        f"{sample.metric_type.value} is {sample.value} (threshold: {threshold['warning']})",
                        sample.source,
                        sample.metric_type,
                        threshold["warning"],
                        sample.value
                    )
                    
        except Exception as e:
            logger.error(f"Failed to check metric alerts: {e}")
            
    async def _auto_resolve_alerts(self) -> None:
        """Auto-resolve alerts based on current conditions"""
        try:
            for alert in self.alerts.values():
                if alert.resolved or not alert.metric_type:
                    continue
                    
                # Check if metric is back to normal
                recent_samples = [
                    sample for sample in self.metrics_buffer.get(alert.metric_type, [])
                    if sample.timestamp >= datetime.now(timezone.utc) - timedelta(minutes=5)
                ]
                
                if recent_samples:
                    avg_value = statistics.mean([sample.value for sample in recent_samples])
                    
                    # If value is below threshold for 5 minutes, resolve alert
                    if alert.threshold_value and avg_value < alert.threshold_value * 0.8:
                        alert.resolved = True
                        alert.resolved_at = datetime.now(timezone.utc)
                        
                        logger.info(f"Alert {alert.alert_id} auto-resolved")
                        
        except Exception as e:
            logger.error(f"Failed to auto-resolve alerts: {e}")
            
    async def _escalate_alerts(self) -> None:
        """Escalate critical unacknowledged alerts"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            
            for alert in self.alerts.values():
                if (alert.severity == AlertSeverity.CRITICAL and 
                    not alert.acknowledged and 
                    not alert.resolved and
                    alert.timestamp < cutoff_time):
                    
                    # Escalate alert
                    await self._notify_alert_handlers(alert, escalated=True)
                    
        except Exception as e:
            logger.error(f"Failed to escalate alerts: {e}")
            
    async def _notify_alert_handlers(self, alert: Alert, escalated: bool = False) -> None:
        """Notify registered alert handlers"""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert, escalated)
                else:
                    handler(alert, escalated)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
                
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
            
        # Simple linear regression slope
        n = len(values)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, values))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        
        if denominator == 0:
            return "stable"
            
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the events monitoring hub"""
        try:
            logger.info("Shutting down EventsMonitoringHub...")
            
            with self._lock:
                self._running = False
                self._shutdown_event.set()
                
            # Cancel background tasks
            if self.metrics_collector_task:
                self.metrics_collector_task.cancel()
            if self.health_checker_task:
                self.health_checker_task.cancel()
            if self.alert_manager_task:
                self.alert_manager_task.cancel()
                
            # Wait for event queue to empty
            self.event_queue.join()
            
            logger.info("EventsMonitoringHub shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Legacy compatibility classes
class EventStreamer:
    """Legacy compatibility wrapper for EventsMonitoringHub event functionality"""
    
    def __init__(self, hub: Optional[EventsMonitoringHub] = None):
        self.hub = hub or EventsMonitoringHub()
        
    async def initialize(self) -> None:
        """Initialize the event streamer"""
        await self.hub.initialize()
        
    async def emit_event(self, event_type: EventType, source: str, data: Dict[str, Any] = None) -> str:
        """Emit an event"""
        return await self.hub.emit_event(event_type, source, data)
        
    async def register_handler(self, handler_id: str, event_types: List[EventType], callback: Callable) -> bool:
        """Register an event handler"""
        return await self.hub.register_event_handler(handler_id, event_types, callback)


class StreamMonitor:
    """Legacy compatibility wrapper for EventsMonitoringHub monitoring functionality"""
    
    def __init__(self, hub: Optional[EventsMonitoringHub] = None):
        self.hub = hub or EventsMonitoringHub()
        
    async def initialize(self) -> None:
        """Initialize the monitor"""
        await self.hub.initialize()
        
    async def record_metric(self, metric_type: MonitoringMetric, value: float, source: str) -> None:
        """Record a metric"""
        await self.hub.record_metric(metric_type, value, source)
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health"""
        return await self.hub.get_system_health()
        
    async def register_health_check(self, check_id: str, check_name: str, check_function: Callable) -> bool:
        """Register a health check"""
        return await self.hub.register_health_check(check_id, check_name, check_function)