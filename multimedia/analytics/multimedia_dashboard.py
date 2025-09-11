"""Multimedia Dashboard System
Real-time analytics dashboard for multimedia processing and performance monitoring.

This module provides comprehensive dashboard functionality including real-time monitoring,
interactive visualizations, performance tracking, and system health indicators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import numpy as np
from enum import Enum

# Import analytics modules
from .audio_analytics import AudioAnalyzer
from .video_analytics import VideoAnalyzer
from .image_analytics import ImageAnalyzer
from .performance_metrics import PerformanceTracker
from .quality_metrics import MultimediaQuality
from .engagement_analytics import EngagementTracker
from .streaming_analytics import StreamingMonitor

logger = logging.getLogger(__name__)

class DashboardTheme(Enum):
    """Dashboard visual themes"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class UpdateFrequency(Enum):
    """Dashboard update frequencies"""
    REAL_TIME = 1      # 1 second
    FAST = 5           # 5 seconds
    NORMAL = 15        # 15 seconds
    SLOW = 60          # 1 minute

@dataclass
class DashboardConfig:
    """Dashboard configuration settings"""
    theme: DashboardTheme = DashboardTheme.DARK
    update_frequency: UpdateFrequency = UpdateFrequency.NORMAL
    auto_refresh: bool = True
    
    # Layout settings
    show_system_metrics: bool = True
    show_performance_charts: bool = True
    show_quality_indicators: bool = True
    show_engagement_stats: bool = True
    show_alerts: bool = True
    
    # Data retention
    max_data_points: int = 1000
    history_duration_hours: int = 24
    
    # Alert thresholds
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'cpu_usage': 90.0,
        'memory_usage': 85.0,
        'error_rate': 5.0,
        'quality_score': 0.7,
        'processing_time': 300.0
    })

@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics"""
    timestamp: datetime
    
    # System metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    disk_usage: float = 0.0
    
    # Processing metrics
    active_operations: int = 0
    completed_operations_1h: int = 0
    failed_operations_1h: int = 0
    average_processing_time: float = 0.0
    
    # Quality metrics
    average_quality_score: float = 0.0
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Engagement metrics
    active_users: int = 0
    total_views_1h: int = 0
    engagement_rate: float = 0.0
    
    # Streaming metrics
    active_streams: int = 0
    total_bandwidth: float = 0.0
    average_bitrate: float = 0.0
    
    # Health indicators
    system_health_score: float = 0.0
    service_status: Dict[str, str] = field(default_factory=dict)
    
    # Alerts
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ChartData:
    """Chart data structure"""
    chart_id: str
    chart_type: str  # 'line', 'bar', 'pie', 'gauge'
    title: str
    data: List[Dict[str, Any]]
    labels: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)


class RealtimeMonitor:
    """Real-time monitoring coordinator"""
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize analytics components
        self.performance_tracker = PerformanceTracker()
        self.quality_assessor = MultimediaQuality()
        self.engagement_tracker = EngagementTracker()
        self.streaming_monitor = StreamingMonitor()
        
        # Data storage
        self.metrics_history: deque = deque(maxlen=self.config.max_data_points)
        self.alerts_history: deque = deque(maxlen=1000)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Subscribers for real-time updates
        self.subscribers: List[Callable[[DashboardMetrics], None]] = []
        
    async def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Real-time monitoring started")
    
    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Real-time monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect current metrics
                metrics = await self._collect_current_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Notify subscribers
                await self._notify_subscribers(metrics)
                
                # Wait for next update
                await asyncio.sleep(self.config.update_frequency.value)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _collect_current_metrics(self) -> DashboardMetrics:
        """Collect current system and application metrics"""
        try:
            timestamp = datetime.now()
            
            # Get system health
            system_health = self.performance_tracker.get_system_health()
            
            # Initialize metrics
            metrics = DashboardMetrics(timestamp=timestamp)
            
            # System metrics
            if system_health.get('system_metrics'):
                sys_metrics = system_health['system_metrics']
                metrics.cpu_usage = sys_metrics.cpu_usage_overall
                metrics.memory_usage = sys_metrics.memory_percentage
                
                if sys_metrics.gpu_metrics:
                    metrics.gpu_usage = np.mean([gpu['utilization_gpu'] for gpu in sys_metrics.gpu_metrics])
                
                if sys_metrics.disk_usage:
                    metrics.disk_usage = np.mean(list(sys_metrics.disk_usage.values()))
            
            # Performance metrics
            perf_summary = self.performance_tracker.get_performance_summary(hours=1)
            if perf_summary:
                metrics.completed_operations_1h = perf_summary.get('successful_operations', 0)
                metrics.failed_operations_1h = perf_summary.get('failed_operations', 0)
                metrics.average_processing_time = perf_summary.get('average_duration', 0)
            
            # Active operations
            metrics.active_operations = len(self.performance_tracker.operation_metrics)
            
            # System health score
            metrics.system_health_score = system_health.get('health_score', 0) / 100.0
            
            # Service status (simplified)
            metrics.service_status = {
                'performance_tracker': 'healthy',
                'quality_assessor': 'healthy',
                'engagement_tracker': 'healthy',
                'streaming_monitor': 'healthy'
            }
            
            # Quality metrics (would need recent quality assessments)
            metrics.average_quality_score = 0.85  # Placeholder
            
            # Engagement metrics (would need recent engagement data)
            metrics.active_users = len(self.engagement_tracker.user_sessions)
            
            # Streaming metrics
            metrics.active_streams = len(self.streaming_monitor.active_sessions)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return DashboardMetrics(timestamp=datetime.now())
    
    async def _check_alerts(self, metrics: DashboardMetrics):
        """Check for alert conditions"""
        try:
            alerts = []
            
            # CPU usage alert
            if metrics.cpu_usage > self.config.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'system',
                    'severity': 'warning',
                    'message': f"High CPU usage: {metrics.cpu_usage:.1f}%",
                    'timestamp': metrics.timestamp,
                    'value': metrics.cpu_usage,
                    'threshold': self.config.alert_thresholds['cpu_usage']
                })
            
            # Memory usage alert
            if metrics.memory_usage > self.config.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'system',
                    'severity': 'warning',
                    'message': f"High memory usage: {metrics.memory_usage:.1f}%",
                    'timestamp': metrics.timestamp,
                    'value': metrics.memory_usage,
                    'threshold': self.config.alert_thresholds['memory_usage']
                })
            
            # Error rate alert
            total_ops = metrics.completed_operations_1h + metrics.failed_operations_1h
            if total_ops > 0:
                error_rate = (metrics.failed_operations_1h / total_ops) * 100
                if error_rate > self.config.alert_thresholds['error_rate']:
                    alerts.append({
                        'type': 'operations',
                        'severity': 'error',
                        'message': f"High error rate: {error_rate:.1f}%",
                        'timestamp': metrics.timestamp,
                        'value': error_rate,
                        'threshold': self.config.alert_thresholds['error_rate']
                    })
            
            # Quality score alert
            if metrics.average_quality_score < self.config.alert_thresholds['quality_score']:
                alerts.append({
                    'type': 'quality',
                    'severity': 'warning',
                    'message': f"Low quality score: {metrics.average_quality_score:.2f}",
                    'timestamp': metrics.timestamp,
                    'value': metrics.average_quality_score,
                    'threshold': self.config.alert_thresholds['quality_score']
                })
            
            # Processing time alert
            if metrics.average_processing_time > self.config.alert_thresholds['processing_time']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f"Slow processing: {metrics.average_processing_time:.1f}s",
                    'timestamp': metrics.timestamp,
                    'value': metrics.average_processing_time,
                    'threshold': self.config.alert_thresholds['processing_time']
                })
            
            # Store alerts
            metrics.active_alerts = alerts
            self.alerts_history.extend(alerts)
            
        except Exception as e:
            self.logger.error(f"Alert checking failed: {e}")
    
    async def _notify_subscribers(self, metrics: DashboardMetrics):
        """Notify all subscribers of new metrics"""
        try:
            for subscriber in self.subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(metrics)
                    else:
                        subscriber(metrics)
                except Exception as e:
                    self.logger.error(f"Subscriber notification failed: {e}")
        except Exception as e:
            self.logger.error(f"Subscriber notification process failed: {e}")
    
    def subscribe(self, callback: Callable[[DashboardMetrics], None]):
        """Subscribe to real-time metrics updates"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[DashboardMetrics], None]):
        """Unsubscribe from real-time metrics updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_current_metrics(self) -> Optional[DashboardMetrics]:
        """Get the most recent metrics"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, duration_minutes: int = 60) -> List[DashboardMetrics]:
        """Get metrics history for specified duration"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]


class AnalyticsDashboard:
    """Analytics dashboard with visualization support"""
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize real-time monitor
        self.monitor = RealtimeMonitor(config)
        
        # Chart configurations
        self.chart_configs = self._initialize_chart_configs()
        
    def _initialize_chart_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize chart configurations"""
        return {
            'cpu_usage': {
                'type': 'line',
                'title': 'CPU Usage',
                'color': '#ff6b6b',
                'unit': '%',
                'max_value': 100
            },
            'memory_usage': {
                'type': 'line',
                'title': 'Memory Usage',
                'color': '#4ecdc4',
                'unit': '%',
                'max_value': 100
            },
            'processing_time': {
                'type': 'line',
                'title': 'Average Processing Time',
                'color': '#45b7d1',
                'unit': 's',
                'max_value': None
            },
            'quality_score': {
                'type': 'gauge',
                'title': 'Average Quality Score',
                'color': '#96ceb4',
                'unit': '',
                'max_value': 1.0
            },
            'operations_status': {
                'type': 'pie',
                'title': 'Operations Status',
                'colors': ['#96ceb4', '#ff6b6b'],
                'unit': '',
                'max_value': None
            },
            'engagement_trends': {
                'type': 'bar',
                'title': 'Engagement Trends',
                'color': '#feca57',
                'unit': '',
                'max_value': None
            }
        }
    
    async def start(self):
        """Start the dashboard"""
        await self.monitor.start_monitoring()
        self.logger.info("Analytics dashboard started")
    
    async def stop(self):
        """Stop the dashboard"""
        await self.monitor.stop_monitoring()
        self.logger.info("Analytics dashboard stopped")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            current_metrics = self.monitor.get_current_metrics()
            metrics_history = self.monitor.get_metrics_history(60)  # Last hour
            
            if not current_metrics:
                return {'error': 'No metrics available'}
            
            # Generate charts
            charts = await self._generate_charts(current_metrics, metrics_history)
            
            # System overview
            system_overview = {
                'cpu_usage': current_metrics.cpu_usage,
                'memory_usage': current_metrics.memory_usage,
                'gpu_usage': current_metrics.gpu_usage,
                'disk_usage': current_metrics.disk_usage,
                'health_score': current_metrics.system_health_score
            }
            
            # Performance summary
            performance_summary = {
                'active_operations': current_metrics.active_operations,
                'completed_operations_1h': current_metrics.completed_operations_1h,
                'failed_operations_1h': current_metrics.failed_operations_1h,
                'average_processing_time': current_metrics.average_processing_time,
                'success_rate': self._calculate_success_rate(current_metrics)
            }
            
            # Quality overview
            quality_overview = {
                'average_quality_score': current_metrics.average_quality_score,
                'quality_distribution': current_metrics.quality_distribution
            }
            
            # Engagement overview
            engagement_overview = {
                'active_users': current_metrics.active_users,
                'total_views_1h': current_metrics.total_views_1h,
                'engagement_rate': current_metrics.engagement_rate
            }
            
            # Streaming overview
            streaming_overview = {
                'active_streams': current_metrics.active_streams,
                'total_bandwidth': current_metrics.total_bandwidth,
                'average_bitrate': current_metrics.average_bitrate
            }
            
            # Alerts
            recent_alerts = [
                alert for alert in self.monitor.alerts_history
                if alert['timestamp'] >= datetime.now() - timedelta(hours=1)
            ]
            
            return {
                'timestamp': current_metrics.timestamp.isoformat(),
                'system_overview': system_overview,
                'performance_summary': performance_summary,
                'quality_overview': quality_overview,
                'engagement_overview': engagement_overview,
                'streaming_overview': streaming_overview,
                'charts': charts,
                'active_alerts': current_metrics.active_alerts,
                'recent_alerts': recent_alerts,
                'service_status': current_metrics.service_status
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard data generation failed: {e}")
            return {'error': str(e)}
    
    async def _generate_charts(self, current_metrics: DashboardMetrics,
                             history: List[DashboardMetrics]) -> List[ChartData]:
        """Generate chart data for visualization"""
        try:
            charts = []
            
            # CPU Usage Chart
            cpu_chart = ChartData(
                chart_id='cpu_usage',
                chart_type='line',
                title='CPU Usage Over Time',
                data=[
                    {'x': m.timestamp.isoformat(), 'y': m.cpu_usage}
                    for m in history
                ],
                options={'color': '#ff6b6b', 'unit': '%', 'max': 100}
            )
            charts.append(cpu_chart)
            
            # Memory Usage Chart
            memory_chart = ChartData(
                chart_id='memory_usage',
                chart_type='line',
                title='Memory Usage Over Time',
                data=[
                    {'x': m.timestamp.isoformat(), 'y': m.memory_usage}
                    for m in history
                ],
                options={'color': '#4ecdc4', 'unit': '%', 'max': 100}
            )
            charts.append(memory_chart)
            
            # Processing Time Chart
            processing_chart = ChartData(
                chart_id='processing_time',
                chart_type='line',
                title='Average Processing Time',
                data=[
                    {'x': m.timestamp.isoformat(), 'y': m.average_processing_time}
                    for m in history
                ],
                options={'color': '#45b7d1', 'unit': 's'}
            )
            charts.append(processing_chart)
            
            # Operations Status Pie Chart
            total_ops = current_metrics.completed_operations_1h + current_metrics.failed_operations_1h
            if total_ops > 0:
                ops_chart = ChartData(
                    chart_id='operations_status',
                    chart_type='pie',
                    title='Operations Status (Last Hour)',
                    data=[
                        {'label': 'Successful', 'value': current_metrics.completed_operations_1h},
                        {'label': 'Failed', 'value': current_metrics.failed_operations_1h}
                    ],
                    colors=['#96ceb4', '#ff6b6b']
                )
                charts.append(ops_chart)
            
            # Quality Score Gauge
            quality_gauge = ChartData(
                chart_id='quality_score',
                chart_type='gauge',
                title='Average Quality Score',
                data=[{'value': current_metrics.average_quality_score}],
                options={'min': 0, 'max': 1, 'color': '#96ceb4'}
            )
            charts.append(quality_gauge)
            
            # System Health Gauge
            health_gauge = ChartData(
                chart_id='system_health',
                chart_type='gauge',
                title='System Health Score',
                data=[{'value': current_metrics.system_health_score}],
                options={'min': 0, 'max': 1, 'color': '#feca57'}
            )
            charts.append(health_gauge)
            
            return charts
            
        except Exception as e:
            self.logger.error(f"Chart generation failed: {e}")
            return []
    
    def _calculate_success_rate(self, metrics: DashboardMetrics) -> float:
        """Calculate operation success rate"""
        total_ops = metrics.completed_operations_1h + metrics.failed_operations_1h
        if total_ops > 0:
            return (metrics.completed_operations_1h / total_ops) * 100
        return 0.0
    
    async def get_chart_data(self, chart_id: str, duration_minutes: int = 60) -> Optional[ChartData]:
        """Get specific chart data"""
        try:
            history = self.monitor.get_metrics_history(duration_minutes)
            current_metrics = self.monitor.get_current_metrics()
            
            if not current_metrics or not history:
                return None
            
            charts = await self._generate_charts(current_metrics, history)
            
            for chart in charts:
                if chart.chart_id == chart_id:
                    return chart
            
            return None
            
        except Exception as e:
            self.logger.error(f"Chart data retrieval failed for {chart_id}: {e}")
            return None
    
    async def export_metrics(self, format_type: str = 'json', 
                           duration_hours: int = 24) -> Optional[str]:
        """Export metrics data"""
        try:
            metrics_history = self.monitor.get_metrics_history(duration_hours * 60)
            
            if format_type.lower() == 'json':
                return json.dumps([asdict(m) for m in metrics_history], 
                                default=str, indent=2)
            elif format_type.lower() == 'csv':
                # Simple CSV export (would need proper CSV formatting)
                lines = ['timestamp,cpu_usage,memory_usage,gpu_usage,active_operations']
                for m in metrics_history:
                    line = f"{m.timestamp},{m.cpu_usage},{m.memory_usage},{m.gpu_usage},{m.active_operations}"
                    lines.append(line)
                return '\n'.join(lines)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Metrics export failed: {e}")
            return None


class MultimediaDashboard:
    """Main multimedia dashboard coordinator"""
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize dashboard components
        self.analytics_dashboard = AnalyticsDashboard(config)
        self.realtime_monitor = self.analytics_dashboard.monitor
        
        # Dashboard state
        self.is_running = False
        
    async def start(self):
        """Start the multimedia dashboard"""
        if self.is_running:
            return
        
        await self.analytics_dashboard.start()
        self.is_running = True
        self.logger.info("Multimedia dashboard started")
    
    async def stop(self):
        """Stop the multimedia dashboard"""
        if not self.is_running:
            return
        
        await self.analytics_dashboard.stop()
        self.is_running = False
        self.logger.info("Multimedia dashboard stopped")
    
    async def get_full_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return await self.analytics_dashboard.get_dashboard_data()
    
    def add_analyzer(self, name: str, analyzer: Any):
        """Add custom analyzer to dashboard"""
        # This would integrate custom analyzers
        # For now, it's a placeholder
        pass
    
    def add_tracker(self, name: str, tracker: Any):
        """Add custom tracker to dashboard"""
        # This would integrate custom trackers
        # For now, it's a placeholder
        pass