"""Edge Performance Monitor
========================

Advanced performance monitoring system for edge computing infrastructure,
providing real-time performance tracking, alerting, and trend analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Performance alert levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class TrendDirection(str, Enum):
    """Performance trend directions."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    VOLATILE = "volatile"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    operator: str = ">"  # >, <, >=, <=, ==, !=
    duration: int = 60  # seconds to exceed threshold
    enabled: bool = True


@dataclass
class PerformanceAlert:
    """Performance alert data."""
    alert_id: str
    alert_level: AlertLevel
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    source: str
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    metric_name: str
    direction: TrendDirection
    slope: float
    confidence: float
    period: timedelta
    start_time: datetime
    end_time: datetime
    sample_count: int


class EdgePerformanceMonitor:
    """Advanced edge performance monitoring system."""
    
    def __init__(self,
                 monitoring_interval: float = 5.0,
                 trend_analysis_window: int = 300,  # 5 minutes
                 alert_cooldown: int = 300):  # 5 minutes
        
        self.monitoring_interval = monitoring_interval
        self.trend_analysis_window = trend_analysis_window
        self.alert_cooldown = alert_cooldown
        
        # Performance data storage
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_metrics: Dict[str, float] = {}
        
        # Threshold and alert management
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Trend analysis
        self.trend_cache: Dict[str, PerformanceTrend] = {}
        
        # Event handlers
        self.alert_handlers: List[Callable] = []
        self.trend_handlers: List[Callable] = []
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.analysis_task: Optional[asyncio.Task] = None
        
        # Control flags
        self.running = False
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        logger.info("EdgePerformanceMonitor initialized")
    
    async def start(self):
        """Start the performance monitoring system."""
        if self.running:
            logger.warning("Performance monitor already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.analysis_task = asyncio.create_task(self._analysis_loop())
        
        logger.info("Edge performance monitoring started")
    
    async def stop(self):
        """Stop the performance monitoring system."""
        self.running = False
        
        # Cancel background tasks
        tasks = [self.monitoring_task, self.analysis_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Edge performance monitoring stopped")
    
    async def update_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Update a performance metric."""
        timestamp = timestamp or datetime.now()
        
        # Store metric value
        self.performance_data[metric_name].append((timestamp, value))
        self.current_metrics[metric_name] = value
        
        # Check thresholds
        await self._check_thresholds(metric_name, value, timestamp)
        
        logger.debug(f"Updated metric {metric_name}: {value}")
    
    async def add_threshold(self, threshold: PerformanceThreshold):
        """Add a performance threshold."""
        self.thresholds[threshold.metric_name] = threshold
        logger.info(f"Added threshold for {threshold.metric_name}: {threshold.warning_threshold}/{threshold.critical_threshold}")
    
    async def remove_threshold(self, metric_name: str):
        """Remove a performance threshold."""
        if metric_name in self.thresholds:
            del self.thresholds[metric_name]
            logger.info(f"Removed threshold for {metric_name}")
    
    async def get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values."""
        return self.current_metrics.copy()
    
    async def get_metric_history(self, 
                                metric_name: str,
                                time_window: Optional[timedelta] = None,
                                limit: Optional[int] = None) -> List[tuple]:
        """Get metric history for analysis."""
        
        if metric_name not in self.performance_data:
            return []
        
        data = list(self.performance_data[metric_name])
        
        # Apply time window filter
        if time_window:
            cutoff_time = datetime.now() - time_window
            data = [(ts, val) for ts, val in data if ts > cutoff_time]
        
        # Apply limit
        if limit:
            data = data[-limit:]
        
        return data
    
    async def get_performance_summary(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Dict[str, float]]:
        """Get performance summary statistics."""
        summary = {}
        
        for metric_name in self.current_metrics.keys():
            history = await self.get_metric_history(metric_name, time_window)
            
            if not history:
                continue
            
            values = [val for _, val in history]
            
            metric_summary = {
                'current': values[-1] if values else 0,
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'count': len(values)
            }
            
            if len(values) > 1:
                metric_summary['stdev'] = statistics.stdev(values)
                metric_summary['median'] = statistics.median(values)
            
            summary[metric_name] = metric_summary
        
        return summary
    
    async def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get currently active alerts."""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    async def get_alert_history(self, 
                               limit: Optional[int] = None,
                               level: Optional[AlertLevel] = None) -> List[PerformanceAlert]:
        """Get alert history."""
        alerts = self.alert_history.copy()
        
        # Filter by level
        if level:
            alerts = [alert for alert in alerts if alert.alert_level == level]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            alerts = alerts[:limit]
        
        return alerts
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            
            logger.info(f"Resolved alert {alert_id}")
            return True
        
        return False
    
    async def get_trend_analysis(self, 
                               metric_name: str,
                               time_window: timedelta = timedelta(minutes=15)) -> Optional[PerformanceTrend]:
        """Get trend analysis for a metric."""
        
        history = await self.get_metric_history(metric_name, time_window)
        
        if len(history) < 3:
            return None
        
        # Calculate trend
        trend = await self._calculate_trend(metric_name, history)
        
        # Cache the trend
        self.trend_cache[metric_name] = trend
        
        return trend
    
    async def get_all_trends(self) -> Dict[str, PerformanceTrend]:
        """Get trend analysis for all metrics."""
        trends = {}
        
        for metric_name in self.current_metrics.keys():
            trend = await self.get_trend_analysis(metric_name)
            if trend:
                trends[metric_name] = trend
        
        return trends
    
    async def export_performance_report(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Export comprehensive performance report."""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'time_window': str(time_window),
            'summary': await self.get_performance_summary(time_window),
            'trends': {},
            'alerts': {
                'active': len([a for a in self.active_alerts.values() if not a.resolved]),
                'total_in_period': 0,
                'by_level': defaultdict(int)
            },
            'thresholds': {}
        }
        
        # Add trend analysis
        trends = await self.get_all_trends()
        for metric_name, trend in trends.items():
            report['trends'][metric_name] = {
                'direction': trend.direction.value,
                'slope': trend.slope,
                'confidence': trend.confidence
            }
        
        # Add alert statistics
        cutoff_time = datetime.now() - time_window
        period_alerts = [a for a in self.alert_history if a.timestamp > cutoff_time]
        
        report['alerts']['total_in_period'] = len(period_alerts)
        for alert in period_alerts:
            report['alerts']['by_level'][alert.alert_level.value] += 1
        
        # Add threshold information
        for metric_name, threshold in self.thresholds.items():
            report['thresholds'][metric_name] = {
                'warning': threshold.warning_threshold,
                'critical': threshold.critical_threshold,
                'enabled': threshold.enabled
            }
        
        return report
    
    def add_alert_handler(self, handler: Callable):
        """Add alert event handler."""
        self.alert_handlers.append(handler)
    
    def add_trend_handler(self, handler: Callable):
        """Add trend event handler."""
        self.trend_handlers.append(handler)
    
    # Private methods
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        default_thresholds = [
            PerformanceThreshold("cpu_usage", 80.0, 95.0, ">"),
            PerformanceThreshold("memory_usage", 85.0, 95.0, ">"),
            PerformanceThreshold("disk_usage", 90.0, 98.0, ">"),
            PerformanceThreshold("latency", 10.0, 50.0, ">"),
            PerformanceThreshold("error_rate", 5.0, 20.0, ">"),
            PerformanceThreshold("service_availability", 95.0, 90.0, "<")
        ]
        
        for threshold in default_thresholds:
            self.thresholds[threshold.metric_name] = threshold
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Update system metrics (integrate with metrics collector)
                await self._update_system_metrics()
                
                # Check for trend changes
                await self._check_trend_changes()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _analysis_loop(self):
        """Background analysis loop."""
        while self.running:
            try:
                # Perform trend analysis
                await self._analyze_trends()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(60)  # Analyze every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _update_system_metrics(self):
        """Update system performance metrics."""
        # This would integrate with the EdgeMetricsCollector
        # For now, we'll use placeholder values
        
        import psutil
        timestamp = datetime.now()
        
        # Update basic system metrics
        await self.update_metric("cpu_usage", psutil.cpu_percent(), timestamp)
        await self.update_metric("memory_usage", psutil.virtual_memory().percent, timestamp)
        await self.update_metric("disk_usage", psutil.disk_usage('/').percent, timestamp)
    
    async def _check_thresholds(self, metric_name: str, value: float, timestamp: datetime):
        """Check if metric value exceeds thresholds."""
        
        if metric_name not in self.thresholds:
            return
        
        threshold = self.thresholds[metric_name]
        
        if not threshold.enabled:
            return
        
        # Check cooldown period
        if metric_name in self.last_alert_time:
            time_since_last = (timestamp - self.last_alert_time[metric_name]).seconds
            if time_since_last < self.alert_cooldown:
                return
        
        # Evaluate threshold conditions
        alert_level = None
        threshold_value = None
        
        if self._evaluate_condition(value, threshold.critical_threshold, threshold.operator):
            alert_level = AlertLevel.CRITICAL
            threshold_value = threshold.critical_threshold
        elif self._evaluate_condition(value, threshold.warning_threshold, threshold.operator):
            alert_level = AlertLevel.WARNING
            threshold_value = threshold.warning_threshold
        
        if alert_level:
            await self._create_alert(metric_name, value, threshold_value, alert_level, timestamp)
    
    def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate threshold condition."""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False
    
    async def _create_alert(self, 
                           metric_name: str, 
                           current_value: float,
                           threshold_value: float,
                           level: AlertLevel,
                           timestamp: datetime):
        """Create a performance alert."""
        
        alert_id = str(uuid.uuid4())
        
        message = f"{metric_name} {level.value}: {current_value:.2f} (threshold: {threshold_value:.2f})"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            alert_level=level,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            message=message,
            timestamp=timestamp,
            source="performance_monitor"
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_time[metric_name] = timestamp
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
        
        logger.warning(f"Performance alert: {message}")
    
    async def _check_trend_changes(self):
        """Check for significant trend changes."""
        for metric_name in self.current_metrics.keys():
            try:
                # Get current trend
                current_trend = await self.get_trend_analysis(metric_name)
                
                if not current_trend:
                    continue
                
                # Check if trend changed significantly
                if metric_name in self.trend_cache:
                    previous_trend = self.trend_cache[metric_name]
                    
                    if (current_trend.direction != previous_trend.direction or
                        abs(current_trend.slope - previous_trend.slope) > 0.5):
                        
                        # Trigger trend handlers
                        for handler in self.trend_handlers:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(current_trend)
                                else:
                                    handler(current_trend)
                            except Exception as e:
                                logger.error(f"Error in trend handler: {e}")
                
            except Exception as e:
                logger.error(f"Error checking trend for {metric_name}: {e}")
    
    async def _analyze_trends(self):
        """Analyze performance trends."""
        for metric_name in self.current_metrics.keys():
            try:
                trend = await self.get_trend_analysis(metric_name)
                
                if trend and trend.direction == TrendDirection.DEGRADING and trend.confidence > 0.7:
                    # Consider creating a trend-based alert
                    logger.info(f"Degrading trend detected for {metric_name}: slope={trend.slope:.3f}")
                
            except Exception as e:
                logger.error(f"Error analyzing trend for {metric_name}: {e}")
    
    async def _calculate_trend(self, metric_name: str, history: List[tuple]) -> PerformanceTrend:
        """Calculate trend analysis for metric history."""
        
        if len(history) < 3:
            return PerformanceTrend(
                metric_name=metric_name,
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                period=timedelta(0),
                start_time=datetime.now(),
                end_time=datetime.now(),
                sample_count=0
            )
        
        # Extract timestamps and values
        timestamps = [ts for ts, _ in history]
        values = [val for _, val in history]
        
        # Calculate linear regression
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
            confidence = 0
        else:
            slope = numerator / denominator
            
            # Calculate R-squared as confidence measure
            y_pred = [slope * x[i] + (y_mean - slope * x_mean) for i in range(n)]
            ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
            ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
            
            confidence = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            confidence = max(0, min(1, confidence))  # Clamp to [0, 1]
        
        # Determine trend direction
        if abs(slope) < 0.1:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING
        else:
            direction = TrendDirection.DEGRADING
        
        # Check for volatility
        if len(values) > 5:
            recent_stdev = statistics.stdev(values[-5:])
            overall_stdev = statistics.stdev(values)
            
            if recent_stdev > overall_stdev * 1.5:
                direction = TrendDirection.VOLATILE
        
        return PerformanceTrend(
            metric_name=metric_name,
            direction=direction,
            slope=slope,
            confidence=confidence,
            period=timestamps[-1] - timestamps[0],
            start_time=timestamps[0],
            end_time=timestamps[-1],
            sample_count=len(values)
        )
    
    async def _cleanup_old_data(self):
        """Clean up old performance data."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Clean up performance data
        for metric_name in list(self.performance_data.keys()):
            data = self.performance_data[metric_name]
            
            # Remove old data points
            while data and data[0][0] < cutoff_time:
                data.popleft()
            
            # Remove empty deques
            if not data:
                del self.performance_data[metric_name]
        
        # Clean up resolved alerts older than 24 hours
        self.alert_history = [
            alert for alert in self.alert_history
            if not alert.resolved or (
                alert.resolution_time and 
                alert.resolution_time > cutoff_time
            )
        ]
        
        # Clean up active alerts that are old
        old_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.timestamp < cutoff_time
        ]
        
        for alert_id in old_alerts:
            del self.active_alerts[alert_id]


def create_performance_monitor(
    monitoring_interval: float = 5.0,
    trend_analysis_window: int = 300,
    alert_cooldown: int = 300
) -> EdgePerformanceMonitor:
    """Create and configure a performance monitor instance."""
    return EdgePerformanceMonitor(
        monitoring_interval=monitoring_interval,
        trend_analysis_window=trend_analysis_window,
        alert_cooldown=alert_cooldown
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_performance_monitor():
        """Test the performance monitor."""
        monitor = create_performance_monitor(monitoring_interval=2.0)
        
        # Add alert handler
        async def alert_handler(alert: PerformanceAlert):
            print(f"ALERT: {alert.message}")
        
        monitor.add_alert_handler(alert_handler)
        
        # Start monitor
        await monitor.start()
        
        # Let it run and collect data
        await asyncio.sleep(10)
        
        # Get performance summary
        summary = await monitor.get_performance_summary()
        print(f"Performance summary: {summary}")
        
        # Get active alerts
        alerts = await monitor.get_active_alerts()
        print(f"Active alerts: {len(alerts)}")
        
        # Export report
        report = await monitor.export_performance_report()
        print(f"Report generated with {len(report['summary'])} metrics")
        
        # Stop monitor
        await monitor.stop()
    
    # Run test
    asyncio.run(test_performance_monitor())