"""📊 Database Replication Monitoring - Real-Time Analytics & Performance Tracking
===============================================================================
Module: database/replication/replication_monitoring.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Database Replication & High Availability Architect
Type: Real-Time Monitoring & Analytics - Enterprise Production-Ready
Responsibility: Comprehensive monitoring, metrics collection, and performance analytics
=================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides comprehensive replication monitoring and analytics:
- Real-time performance metrics collection and analysis
- Health monitoring with predictive failure detection
- Alert generation with intelligent escalation
- Performance trend analysis and optimization recommendations
- Dashboard data aggregation and visualization support
"""

import asyncio
import logging
import time
import json
import statistics
from typing import Dict, Any, Optional, List, Set, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
import threading
from collections import defaultdict, deque
import psutil
import os

try:
    from .replication_config import ReplicationConfig, MonitoringConfig
    from .database_replication import ReplicationMetrics, DatabaseHealth, ReplicationStatus
except ImportError:
    # Fallback for development
    pass

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics collected."""
    PERFORMANCE = "performance"
    HEALTH = "health"
    SYSTEM = "system"
    NETWORK = "network"
    SECURITY = "security"

class AlertType(Enum):
    """Types of alerts generated."""
    HIGH_LAG = "high_lag"
    NODE_DOWN = "node_down"
    HIGH_ERROR_RATE = "high_error_rate"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_SPACE = "disk_space"
    NETWORK_ISSUES = "network_issues"
    REPLICATION_FAILURE = "replication_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class Alert:
    """Alert information."""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    database_name: str
    node_name: str
    metric_value: float
    threshold_value: float
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    metric_name: str
    time_window_minutes: int
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0.0 to 1.0
    prediction_next_hour: float
    recommendation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MonitoringDashboard:
    """Monitoring dashboard data."""
    timestamp: datetime
    overall_health: str
    total_databases: int
    healthy_databases: int
    total_alerts: int
    critical_alerts: int
    avg_lag_ms: float
    total_throughput: float
    system_metrics: Dict[str, float]
    recent_alerts: List[Alert]
    performance_trends: List[PerformanceTrend]
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """Collects metrics from various sources."""
    
    def __init__(self):
        self._metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._system_metrics: Dict[str, float] = {}
        self._collection_interval = 60  # seconds
        self._is_running = False
        self._collection_task: Optional[asyncio.Task] = None
        
    async def start_collection(self, interval_seconds: int = 60):
        """Start metrics collection."""
        try:
            self._collection_interval = interval_seconds
            self._is_running = True
            
            self._collection_task = asyncio.create_task(self._collection_loop())
            logger.info(f"✅ Metrics collection started (interval: {interval_seconds}s)")
            
        except Exception as e:
            logger.error(f"❌ Failed to start metrics collection: {e}")
            raise
    
    async def stop_collection(self):
        """Stop metrics collection."""
        try:
            self._is_running = False
            
            if self._collection_task:
                self._collection_task.cancel()
                try:
                    await self._collection_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Metrics collection stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping metrics collection: {e}")
    
    async def _collection_loop(self):
        """Main metrics collection loop."""
        while self._is_running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Sleep until next collection
                await asyncio.sleep(self._collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Process metrics
            process_count = len(psutil.pids())
            
            self._system_metrics = {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_percent': memory_percent,
                'memory_available_gb': memory_available_gb,
                'disk_percent': disk_percent,
                'disk_free_gb': disk_free_gb,
                'network_bytes_sent': network_bytes_sent,
                'network_bytes_recv': network_bytes_recv,
                'process_count': process_count,
                'timestamp': time.time()
            }
            
            # Store in history
            self._metrics_history['system'].append(self._system_metrics.copy())
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system metrics: {e}")
    
    def record_database_metrics(self, database_name: str, metrics: ReplicationMetrics):
        """Record database-specific metrics."""
        try:
            metrics_dict = {
                'database_name': database_name,
                'timestamp': metrics.timestamp.timestamp(),
                'lag_ms': metrics.lag_ms,
                'throughput_ops_per_sec': metrics.throughput_ops_per_sec,
                'error_rate': metrics.error_rate,
                'data_size_gb': metrics.data_size_gb,
                'network_bandwidth_mbps': metrics.network_bandwidth_mbps,
                'cpu_usage_percent': metrics.cpu_usage_percent,
                'memory_usage_percent': metrics.memory_usage_percent,
                'disk_usage_percent': metrics.disk_usage_percent,
                'metadata': metrics.metadata
            }
            
            self._metrics_history[f'db_{database_name}'].append(metrics_dict)
            
        except Exception as e:
            logger.error(f"❌ Failed to record database metrics for {database_name}: {e}")
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        return self._system_metrics.copy()
    
    def get_database_metrics_history(self, database_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get database metrics history."""
        try:
            history_key = f'db_{database_name}'
            if history_key not in self._metrics_history:
                return []
            
            # Filter by time window
            cutoff_time = time.time() - (hours * 3600)
            recent_metrics = [
                m for m in self._metrics_history[history_key]
                if m.get('timestamp', 0) >= cutoff_time
            ]
            
            return recent_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get database metrics history for {database_name}: {e}")
            return []
    
    def get_system_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get system metrics history."""
        try:
            if 'system' not in self._metrics_history:
                return []
            
            # Filter by time window
            cutoff_time = time.time() - (hours * 3600)
            recent_metrics = [
                m for m in self._metrics_history['system']
                if m.get('timestamp', 0) >= cutoff_time
            ]
            
            return recent_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get system metrics history: {e}")
            return []

class PerformanceAnalyzer:
    """Analyzes performance metrics and trends."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self._metrics_collector = metrics_collector
        self._trend_cache: Dict[str, PerformanceTrend] = {}
        self._analysis_interval = 300  # 5 minutes
        self._is_running = False
        self._analysis_task: Optional[asyncio.Task] = None
        
    async def start_analysis(self):
        """Start performance analysis."""
        try:
            self._is_running = True
            self._analysis_task = asyncio.create_task(self._analysis_loop())
            logger.info("✅ Performance analysis started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start performance analysis: {e}")
            raise
    
    async def stop_analysis(self):
        """Stop performance analysis."""
        try:
            self._is_running = False
            
            if self._analysis_task:
                self._analysis_task.cancel()
                try:
                    await self._analysis_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Performance analysis stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping performance analysis: {e}")
    
    async def _analysis_loop(self):
        """Main performance analysis loop."""
        while self._is_running:
            try:
                # Analyze trends for all tracked databases
                await self._analyze_all_trends()
                
                await asyncio.sleep(self._analysis_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Performance analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_all_trends(self):
        """Analyze trends for all databases."""
        try:
            # Get list of databases from metrics history
            database_names = set()
            for key in self._metrics_collector._metrics_history.keys():
                if key.startswith('db_'):
                    database_names.add(key[3:])  # Remove 'db_' prefix
            
            # Analyze trends for each database
            for db_name in database_names:
                await self._analyze_database_trends(db_name)
            
            # Analyze system trends
            await self._analyze_system_trends()
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze all trends: {e}")
    
    async def _analyze_database_trends(self, database_name: str):
        """Analyze trends for a specific database."""
        try:
            # Get recent metrics
            metrics_history = self._metrics_collector.get_database_metrics_history(database_name, hours=2)
            
            if len(metrics_history) < 5:  # Need at least 5 data points
                return
            
            # Analyze lag trend
            lag_trend = self._analyze_metric_trend(
                metrics_history, 'lag_ms', 'Replication Lag'
            )
            if lag_trend:
                self._trend_cache[f'{database_name}_lag'] = lag_trend
            
            # Analyze throughput trend
            throughput_trend = self._analyze_metric_trend(
                metrics_history, 'throughput_ops_per_sec', 'Throughput'
            )
            if throughput_trend:
                self._trend_cache[f'{database_name}_throughput'] = throughput_trend
            
            # Analyze error rate trend
            error_trend = self._analyze_metric_trend(
                metrics_history, 'error_rate', 'Error Rate'
            )
            if error_trend:
                self._trend_cache[f'{database_name}_error_rate'] = error_trend
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze database trends for {database_name}: {e}")
    
    async def _analyze_system_trends(self):
        """Analyze system-level trends."""
        try:
            # Get recent system metrics
            system_history = self._metrics_collector.get_system_metrics_history(hours=2)
            
            if len(system_history) < 5:
                return
            
            # Analyze CPU trend
            cpu_trend = self._analyze_metric_trend(
                system_history, 'cpu_percent', 'CPU Usage'
            )
            if cpu_trend:
                self._trend_cache['system_cpu'] = cpu_trend
            
            # Analyze memory trend
            memory_trend = self._analyze_metric_trend(
                system_history, 'memory_percent', 'Memory Usage'
            )
            if memory_trend:
                self._trend_cache['system_memory'] = memory_trend
            
            # Analyze disk trend
            disk_trend = self._analyze_metric_trend(
                system_history, 'disk_percent', 'Disk Usage'
            )
            if disk_trend:
                self._trend_cache['system_disk'] = disk_trend
                
        except Exception as e:
            logger.error(f"❌ Failed to analyze system trends: {e}")
    
    def _analyze_metric_trend(self, metrics_history: List[Dict], metric_key: str, metric_name: str) -> Optional[PerformanceTrend]:
        """Analyze trend for a specific metric."""
        try:
            # Extract metric values
            values = [m.get(metric_key, 0) for m in metrics_history]
            timestamps = [m.get('timestamp', 0) for m in metrics_history]
            
            if not values or len(values) < 3:
                return None
            
            # Calculate statistics
            current_value = values[-1]
            average_value = statistics.mean(values)
            min_value = min(values)
            max_value = max(values)
            
            # Calculate trend direction and strength
            if len(values) >= 3:
                recent_values = values[-3:]
                trend_direction, trend_strength = self._calculate_trend(recent_values)
            else:
                trend_direction = "stable"
                trend_strength = 0.0
            
            # Simple prediction (linear extrapolation)
            prediction_next_hour = self._predict_next_value(values, timestamps)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                metric_name, current_value, average_value, trend_direction, trend_strength
            )
            
            return PerformanceTrend(
                metric_name=metric_name,
                time_window_minutes=120,  # 2 hours
                current_value=current_value,
                average_value=average_value,
                min_value=min_value,
                max_value=max_value,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                prediction_next_hour=prediction_next_hour,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze metric trend for {metric_name}: {e}")
            return None
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength."""
        try:
            if len(values) < 2:
                return "stable", 0.0
            
            # Calculate differences between consecutive values
            diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
            
            if not diffs:
                return "stable", 0.0
            
            # Determine overall direction
            avg_diff = statistics.mean(diffs)
            
            if abs(avg_diff) < 0.01:  # Very small change
                return "stable", 0.0
            elif avg_diff > 0:
                direction = "increasing"
            else:
                direction = "decreasing"
            
            # Calculate strength (coefficient of variation)
            if statistics.mean(values) != 0:
                strength = min(1.0, abs(avg_diff) / abs(statistics.mean(values)))
            else:
                strength = 0.0
            
            return direction, strength
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate trend: {e}")
            return "stable", 0.0
    
    def _predict_next_value(self, values: List[float], timestamps: List[float]) -> float:
        """Simple linear prediction for next hour."""
        try:
            if len(values) < 2 or len(timestamps) < 2:
                return values[-1] if values else 0.0
            
            # Use last two points for linear extrapolation
            x1, y1 = timestamps[-2], values[-2]
            x2, y2 = timestamps[-1], values[-1]
            
            if x2 == x1:  # Avoid division by zero
                return y2
            
            # Linear slope
            slope = (y2 - y1) / (x2 - x1)
            
            # Predict one hour ahead
            future_time = x2 + 3600  # 1 hour in seconds
            predicted_value = y2 + slope * (future_time - x2)
            
            return max(0, predicted_value)  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"❌ Failed to predict next value: {e}")
            return values[-1] if values else 0.0
    
    def _generate_recommendation(self, metric_name: str, current: float, average: float, 
                                direction: str, strength: float) -> str:
        """Generate performance recommendation."""
        try:
            recommendations = []
            
            # General trend recommendations
            if direction == "increasing" and strength > 0.5:
                if "lag" in metric_name.lower():
                    recommendations.append("Consider optimizing replication configuration")
                elif "error" in metric_name.lower():
                    recommendations.append("Investigate error sources and improve error handling")
                elif "cpu" in metric_name.lower() or "memory" in metric_name.lower():
                    recommendations.append("Monitor resource usage and consider scaling")
            
            elif direction == "decreasing" and strength > 0.5:
                if "throughput" in metric_name.lower():
                    recommendations.append("Investigate performance degradation causes")
            
            # Threshold-based recommendations
            if "lag" in metric_name.lower() and current > 1000:  # > 1 second
                recommendations.append("High replication lag detected - check network and database load")
            
            if "error" in metric_name.lower() and current > 0.05:  # > 5% error rate
                recommendations.append("High error rate - review logs and fix underlying issues")
            
            if "cpu" in metric_name.lower() and current > 80:  # > 80% CPU
                recommendations.append("High CPU usage - consider load balancing or scaling")
            
            if "memory" in metric_name.lower() and current > 85:  # > 85% memory
                recommendations.append("High memory usage - optimize queries or increase memory")
            
            if "disk" in metric_name.lower() and current > 90:  # > 90% disk
                recommendations.append("High disk usage - clean up logs or increase disk space")
            
            return "; ".join(recommendations) if recommendations else "Performance within normal parameters"
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendation: {e}")
            return "Unable to generate recommendation"
    
    def get_trend_analysis(self, metric_key: str) -> Optional[PerformanceTrend]:
        """Get trend analysis for a specific metric."""
        return self._trend_cache.get(metric_key)
    
    def get_all_trends(self) -> List[PerformanceTrend]:
        """Get all current trend analyses."""
        return list(self._trend_cache.values())

class HealthTracker:
    """Tracks health status and generates alerts."""
    
    def __init__(self, config: MonitoringConfig):
        self._config = config
        self._alert_history: deque = deque(maxlen=10000)
        self._alert_handlers: List[Callable] = []
        self._health_status: Dict[str, DatabaseHealth] = {}
        self._alert_counters: Dict[str, int] = defaultdict(int)
        
    def register_alert_handler(self, handler: Callable[[Alert], None]):
        """Register an alert handler."""
        self._alert_handlers.append(handler)
    
    async def check_database_health(self, database_name: str, health: DatabaseHealth):
        """Check database health and generate alerts if needed."""
        try:
            self._health_status[database_name] = health
            
            # Check various health conditions
            await self._check_lag_threshold(database_name, health)
            await self._check_node_availability(database_name, health)
            await self._check_error_rate(database_name, health)
            
        except Exception as e:
            logger.error(f"❌ Failed to check database health for {database_name}: {e}")
    
    async def check_system_health(self, system_metrics: Dict[str, float]):
        """Check system health and generate alerts if needed."""
        try:
            # Check CPU usage
            cpu_percent = system_metrics.get('cpu_percent', 0)
            if cpu_percent > self._config.alert_thresholds.get('cpu_threshold', 80) * 100:
                await self._generate_alert(
                    AlertType.MEMORY_PRESSURE,
                    AlertSeverity.WARNING,
                    f"High CPU usage: {cpu_percent:.1f}%",
                    "system",
                    "system",
                    cpu_percent,
                    self._config.alert_thresholds.get('cpu_threshold', 80) * 100
                )
            
            # Check memory usage
            memory_percent = system_metrics.get('memory_percent', 0)
            if memory_percent > self._config.alert_thresholds.get('memory_threshold', 85) * 100:
                await self._generate_alert(
                    AlertType.MEMORY_PRESSURE,
                    AlertSeverity.WARNING,
                    f"High memory usage: {memory_percent:.1f}%",
                    "system",
                    "system",
                    memory_percent,
                    self._config.alert_thresholds.get('memory_threshold', 85) * 100
                )
            
            # Check disk usage
            disk_percent = system_metrics.get('disk_percent', 0)
            if disk_percent > self._config.alert_thresholds.get('disk_threshold', 90) * 100:
                await self._generate_alert(
                    AlertType.DISK_SPACE,
                    AlertSeverity.ERROR,
                    f"High disk usage: {disk_percent:.1f}%",
                    "system",
                    "system",
                    disk_percent,
                    self._config.alert_thresholds.get('disk_threshold', 90) * 100
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to check system health: {e}")
    
    async def _check_lag_threshold(self, database_name: str, health: DatabaseHealth):
        """Check replication lag threshold."""
        try:
            lag_threshold = self._config.alert_thresholds.get('lag_threshold_ms', 1000)
            
            if health.lag_ms > lag_threshold:
                severity = AlertSeverity.WARNING if health.lag_ms < lag_threshold * 2 else AlertSeverity.ERROR
                
                await self._generate_alert(
                    AlertType.HIGH_LAG,
                    severity,
                    f"High replication lag: {health.lag_ms:.1f}ms",
                    database_name,
                    health.master_node,
                    health.lag_ms,
                    lag_threshold
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to check lag threshold: {e}")
    
    async def _check_node_availability(self, database_name: str, health: DatabaseHealth):
        """Check node availability."""
        try:
            if not health.is_healthy:
                await self._generate_alert(
                    AlertType.NODE_DOWN,
                    AlertSeverity.CRITICAL,
                    f"Database node unhealthy: {health.database_name}",
                    database_name,
                    health.master_node,
                    0,
                    1
                )
            elif health.status == ReplicationStatus.FAILED:
                await self._generate_alert(
                    AlertType.REPLICATION_FAILURE,
                    AlertSeverity.ERROR,
                    f"Replication failure detected: {health.database_name}",
                    database_name,
                    health.master_node,
                    0,
                    1
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to check node availability: {e}")
    
    async def _check_error_rate(self, database_name: str, health: DatabaseHealth):
        """Check error rate threshold."""
        try:
            error_threshold = self._config.alert_thresholds.get('error_rate_threshold', 0.05)
            
            if health.error_count > 0:
                # Calculate error rate (simplified)
                error_rate = min(1.0, health.error_count / 100)  # Assume max 100 operations
                
                if error_rate > error_threshold:
                    await self._generate_alert(
                        AlertType.HIGH_ERROR_RATE,
                        AlertSeverity.WARNING,
                        f"High error rate: {error_rate:.2%}",
                        database_name,
                        health.master_node,
                        error_rate,
                        error_threshold
                    )
                    
        except Exception as e:
            logger.error(f"❌ Failed to check error rate: {e}")
    
    async def _generate_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                            message: str, database_name: str, node_name: str,
                            metric_value: float, threshold_value: float):
        """Generate and process an alert."""
        try:
            # Create alert
            alert_id = f"{alert_type.value}_{database_name}_{int(time.time())}"
            alert = Alert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=datetime.now(timezone.utc),
                database_name=database_name,
                node_name=node_name,
                metric_value=metric_value,
                threshold_value=threshold_value
            )
            
            # Store alert
            self._alert_history.append(alert)
            
            # Update counters
            self._alert_counters[f"{alert_type.value}_{severity.value}"] += 1
            
            # Notify handlers
            for handler in self._alert_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    logger.error(f"❌ Alert handler error: {e}")
            
            logger.warning(f"🚨 Alert generated: {severity.value.upper()} - {message}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate alert: {e}")
    
    def get_recent_alerts(self, hours: int = 24, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get recent alerts."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            filtered_alerts = [
                alert for alert in self._alert_history
                if alert.timestamp >= cutoff_time and (severity is None or alert.severity == severity)
            ]
            
            return sorted(filtered_alerts, key=lambda a: a.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent alerts: {e}")
            return []
    
    def get_alert_statistics(self) -> Dict[str, int]:
        """Get alert statistics."""
        return dict(self._alert_counters)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all tracked databases."""
        try:
            total_databases = len(self._health_status)
            healthy_databases = sum(1 for h in self._health_status.values() if h.is_healthy)
            
            avg_lag = 0.0
            if self._health_status:
                avg_lag = sum(h.lag_ms for h in self._health_status.values()) / len(self._health_status)
            
            recent_critical_alerts = len([
                a for a in self._alert_history
                if a.severity == AlertSeverity.CRITICAL and 
                a.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
            ])
            
            return {
                'total_databases': total_databases,
                'healthy_databases': healthy_databases,
                'health_percentage': (healthy_databases / max(total_databases, 1)) * 100,
                'average_lag_ms': avg_lag,
                'recent_critical_alerts': recent_critical_alerts,
                'overall_status': 'healthy' if healthy_databases == total_databases else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get health summary: {e}")
            return {
                'total_databases': 0,
                'healthy_databases': 0,
                'health_percentage': 0,
                'average_lag_ms': 0,
                'recent_critical_alerts': 0,
                'overall_status': 'unknown'
            }

class ReplicationMonitor:
    """Main replication monitoring coordinator."""
    
    def __init__(self, config: Optional[ReplicationConfig] = None):
        self._config = config
        self._monitoring_config = config.monitoring if config else MonitoringConfig()
        
        # Initialize components
        self._metrics_collector = MetricsCollector()
        self._performance_analyzer = PerformanceAnalyzer(self._metrics_collector)
        self._health_tracker = HealthTracker(self._monitoring_config)
        
        self._is_running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Dashboard cache
        self._dashboard_cache: Optional[MonitoringDashboard] = None
        self._dashboard_cache_time = 0
        
    async def initialize(self, config: ReplicationConfig):
        """Initialize monitoring system."""
        try:
            self._config = config
            self._monitoring_config = config.monitoring
            
            # Setup alert handlers
            self._health_tracker.register_alert_handler(self._default_alert_handler)
            
            logger.info("✅ Replication monitoring system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring system: {e}")
            raise
    
    async def start_monitoring(self):
        """Start all monitoring components."""
        try:
            if self._is_running:
                logger.warning("Monitoring already running")
                return
            
            # Start metrics collection
            await self._metrics_collector.start_collection(
                self._monitoring_config.metrics_interval_seconds
            )
            
            # Start performance analysis
            await self._performance_analyzer.start_analysis()
            
            # Start main monitoring loop
            self._is_running = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("✅ Replication monitoring started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop all monitoring components."""
        try:
            self._is_running = False
            
            # Stop monitoring loop
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Stop components
            await self._performance_analyzer.stop_analysis()
            await self._metrics_collector.stop_collection()
            
            logger.info("✅ Replication monitoring stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring coordination loop."""
        while self._is_running:
            try:
                # Check system health
                system_metrics = self._metrics_collector.get_system_metrics()
                if system_metrics:
                    await self._health_tracker.check_system_health(system_metrics)
                
                # Update dashboard cache
                await self._update_dashboard_cache()
                
                # Sleep until next check
                await asyncio.sleep(self._monitoring_config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def record_database_health(self, database_name: str, health: DatabaseHealth):
        """Record database health status."""
        try:
            # Check health and generate alerts
            await self._health_tracker.check_database_health(database_name, health)
            
        except Exception as e:
            logger.error(f"❌ Failed to record database health for {database_name}: {e}")
    
    async def record_database_metrics(self, database_name: str, metrics: ReplicationMetrics):
        """Record database performance metrics."""
        try:
            # Store metrics
            self._metrics_collector.record_database_metrics(database_name, metrics)
            
        except Exception as e:
            logger.error(f"❌ Failed to record database metrics for {database_name}: {e}")
    
    async def get_monitoring_dashboard(self, force_refresh: bool = False) -> MonitoringDashboard:
        """Get comprehensive monitoring dashboard."""
        try:
            # Check cache
            current_time = time.time()
            if (not force_refresh and 
                self._dashboard_cache and 
                current_time - self._dashboard_cache_time < 30):  # 30 second cache
                return self._dashboard_cache
            
            # Refresh dashboard
            await self._update_dashboard_cache()
            return self._dashboard_cache or self._create_empty_dashboard()
            
        except Exception as e:
            logger.error(f"❌ Failed to get monitoring dashboard: {e}")
            return self._create_empty_dashboard()
    
    async def _update_dashboard_cache(self):
        """Update dashboard cache with latest data."""
        try:
            # Get health summary
            health_summary = self._health_tracker.get_health_summary()
            
            # Get recent alerts
            recent_alerts = self._health_tracker.get_recent_alerts(hours=24)
            critical_alerts = [a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]
            
            # Get system metrics
            system_metrics = self._metrics_collector.get_system_metrics()
            
            # Get performance trends
            performance_trends = self._performance_analyzer.get_all_trends()
            
            # Calculate total throughput (simplified)
            total_throughput = 0.0
            for db_name in self._health_tracker._health_status.keys():
                db_metrics = self._metrics_collector.get_database_metrics_history(db_name, hours=1)
                if db_metrics:
                    latest_metrics = db_metrics[-1]
                    total_throughput += latest_metrics.get('throughput_ops_per_sec', 0)
            
            # Create dashboard
            self._dashboard_cache = MonitoringDashboard(
                timestamp=datetime.now(timezone.utc),
                overall_health=health_summary['overall_status'],
                total_databases=health_summary['total_databases'],
                healthy_databases=health_summary['healthy_databases'],
                total_alerts=len(recent_alerts),
                critical_alerts=len(critical_alerts),
                avg_lag_ms=health_summary['average_lag_ms'],
                total_throughput=total_throughput,
                system_metrics=system_metrics,
                recent_alerts=recent_alerts[:10],  # Last 10 alerts
                performance_trends=performance_trends[:20],  # Top 20 trends
                metadata={
                    'cache_updated_at': time.time(),
                    'monitoring_uptime_seconds': time.time() - self._dashboard_cache_time if self._dashboard_cache_time > 0 else 0
                }
            )
            
            self._dashboard_cache_time = time.time()
            
        except Exception as e:
            logger.error(f"❌ Failed to update dashboard cache: {e}")
    
    def _create_empty_dashboard(self) -> MonitoringDashboard:
        """Create empty dashboard for error cases."""
        return MonitoringDashboard(
            timestamp=datetime.now(timezone.utc),
            overall_health='unknown',
            total_databases=0,
            healthy_databases=0,
            total_alerts=0,
            critical_alerts=0,
            avg_lag_ms=0.0,
            total_throughput=0.0,
            system_metrics={},
            recent_alerts=[],
            performance_trends=[]
        )
    
    async def _default_alert_handler(self, alert: Alert):
        """Default alert handler."""
        try:
            # Log alert
            log_level = {
                AlertSeverity.INFO: logging.INFO,
                AlertSeverity.WARNING: logging.WARNING,
                AlertSeverity.ERROR: logging.ERROR,
                AlertSeverity.CRITICAL: logging.CRITICAL
            }.get(alert.severity, logging.WARNING)
            
            logger.log(log_level, f"🚨 {alert.severity.value.upper()}: {alert.message} (Database: {alert.database_name})")
            
            # TODO: Send notifications via configured channels
            # - Email notifications
            # - Slack/Teams integration
            # - PagerDuty integration
            # - SMS notifications
            
        except Exception as e:
            logger.error(f"❌ Default alert handler error: {e}")
    
    async def close(self):
        """Close monitoring system."""
        try:
            await self.stop_monitoring()
            logger.info("✅ Replication monitoring system closed")
        except Exception as e:
            logger.error(f"❌ Error closing monitoring system: {e}")

# Factory functions
def create_metrics_collector() -> MetricsCollector:
    """Create a metrics collector."""
    return MetricsCollector()

def create_performance_analyzer(metrics_collector: MetricsCollector) -> PerformanceAnalyzer:
    """Create a performance analyzer."""
    return PerformanceAnalyzer(metrics_collector)

def create_health_tracker(config: MonitoringConfig) -> HealthTracker:
    """Create a health tracker."""
    return HealthTracker(config)

def create_replication_monitor(config: ReplicationConfig) -> ReplicationMonitor:
    """Create a replication monitor."""
    return ReplicationMonitor(config)