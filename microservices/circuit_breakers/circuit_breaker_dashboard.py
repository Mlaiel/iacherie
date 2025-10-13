"""
Circuit Breaker Dashboard - Enterprise Circuit Breakers
Real-time visualization and monitoring dashboard for circuit breakers

This module provides an enterprise-grade dashboard for monitoring circuit breaker
health, performance metrics, and system-wide resilience patterns.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
import base64
import io
import tempfile
import os

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("⚠️ Matplotlib not available - advanced visualizations disabled")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logging.warning("⚠️ Plotly not available - interactive charts disabled")

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logging.warning("⚠️ Jinja2 not available - template rendering limited")


logger = logging.getLogger(__name__)


class DashboardTheme(Enum):
    """Dashboard visual themes"""
    LIGHT = "light"
    DARK = "dark"
    ENTERPRISE = "enterprise"
    IACHERIE = "iacherie"


class ChartType(Enum):
    """Types of charts available"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    AREA_CHART = "area_chart"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    title: str = "Circuit Breakers Enterprise Dashboard"
    theme: DashboardTheme = DashboardTheme.ENTERPRISE
    refresh_interval_seconds: int = 30
    max_data_points: int = 1000
    enable_real_time: bool = True
    enable_alerts: bool = True
    enable_export: bool = True
    custom_css: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WidgetConfig:
    """Widget configuration"""
    widget_id: str
    title: str
    chart_type: ChartType
    data_source: str
    refresh_interval: int = 30
    height: int = 400
    width: Optional[int] = None
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (6, 4)  # Grid units (cols, rows)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardAlert:
    """Dashboard alert"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    source_service: str
    dismissed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collect metrics from various circuit breaker components"""
    
    def __init__(self):
        self.metric_sources: Dict[str, Callable] = {}
        self.cached_metrics: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_metric_source(self, source_name: str, collector_func: Callable):
        """Register a metric collection function"""
        self.metric_sources[source_name] = collector_func
        self.logger.info(f"📊 Registered metric source: {source_name}")
    
    async def collect_metrics(self, source_name: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Collect metrics from registered source"""
        try:
            # Check cache first
            if not force_refresh and source_name in self.cached_metrics:
                cache_time = self.cache_ttl.get(source_name, datetime.min)
                if datetime.now() - cache_time < timedelta(seconds=30):  # 30 second cache
                    return self.cached_metrics[source_name]
            
            # Collect fresh metrics
            if source_name not in self.metric_sources:
                return {'error': f'Metric source {source_name} not registered'}
            
            collector_func = self.metric_sources[source_name]
            if asyncio.iscoroutinefunction(collector_func):
                metrics = await collector_func()
            else:
                metrics = collector_func()
            
            # Cache results
            self.cached_metrics[source_name] = metrics
            self.cache_ttl[source_name] = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect metrics from {source_name}: {e}")
            return {'error': str(e)}
    
    async def collect_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Collect metrics from all registered sources"""
        all_metrics = {}
        
        for source_name in self.metric_sources.keys():
            try:
                metrics = await self.collect_metrics(source_name)
                all_metrics[source_name] = metrics
            except Exception as e:
                all_metrics[source_name] = {'error': str(e)}
        
        return all_metrics


class ChartGenerator:
    """Generate charts and visualizations"""
    
    def __init__(self, theme: DashboardTheme = DashboardTheme.ENTERPRISE):
        self.theme = theme
        self.color_palette = self._get_color_palette()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _get_color_palette(self) -> Dict[str, str]:
        """Get color palette based on theme"""
        palettes = {
            DashboardTheme.LIGHT: {
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'background': '#ffffff',
                'text': '#333333'
            },
            DashboardTheme.DARK: {
                'primary': '#0d6efd',
                'secondary': '#6c757d',
                'success': '#198754',
                'warning': '#ffc107',
                'error': '#dc3545',
                'background': '#212529',
                'text': '#ffffff'
            },
            DashboardTheme.ENTERPRISE: {
                'primary': '#2c3e50',
                'secondary': '#7f8c8d',
                'success': '#27ae60',
                'warning': '#f39c12',
                'error': '#e74c3c',
                'background': '#ecf0f1',
                'text': '#2c3e50'
            },
            DashboardTheme.IACHERIE: {
                'primary': '#6366f1',
                'secondary': '#8b5cf6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'background': '#f8fafc',
                'text': '#1e293b'
            }
        }
        
        return palettes.get(self.theme, palettes[DashboardTheme.ENTERPRISE])
    
    async def generate_line_chart(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate line chart"""
        if PLOTLY_AVAILABLE:
            return await self._generate_plotly_line_chart(data, config)
        elif MATPLOTLIB_AVAILABLE:
            return await self._generate_matplotlib_line_chart(data, config)
        else:
            return await self._generate_text_chart(data, config)
    
    async def _generate_plotly_line_chart(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate interactive line chart with Plotly"""
        try:
            fig = go.Figure()
            
            x_data = data.get('x_data', [])
            y_series = data.get('y_series', {})
            
            for series_name, y_data in y_series.items():
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name=series_name,
                    line=dict(width=2),
                    marker=dict(size=4)
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title=data.get('x_title', 'Time'),
                yaxis_title=data.get('y_title', 'Value'),
                height=config.height,
                template='plotly_white' if self.theme == DashboardTheme.LIGHT else 'plotly_dark',
                showlegend=True,
                hovermode='x unified'
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id=f"chart_{config.widget_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate Plotly line chart: {e}")
            return f"<div>Error generating chart: {e}</div>"
    
    async def _generate_matplotlib_line_chart(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate static line chart with Matplotlib"""
        try:
            plt.style.use('seaborn-v0_8' if hasattr(plt.style, 'available') and 'seaborn-v0_8' in plt.style.available else 'default')
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x_data = data.get('x_data', [])
            y_series = data.get('y_series', {})
            
            for series_name, y_data in y_series.items():
                ax.plot(x_data, y_data, label=series_name, linewidth=2, marker='o', markersize=4)
            
            ax.set_title(config.title, fontsize=14, fontweight='bold')
            ax.set_xlabel(data.get('x_title', 'Time'))
            ax.set_ylabel(data.get('y_title', 'Value'))
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis if datetime
            if x_data and isinstance(x_data[0], datetime):
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            
            return f'<img src="data:image/png;base64,{image_base64}" alt="{config.title}" style="max-width: 100%; height: auto;">'
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate Matplotlib line chart: {e}")
            return f"<div>Error generating chart: {e}</div>"
    
    async def _generate_text_chart(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate simple text-based chart when visualization libraries unavailable"""
        try:
            html = f"<div class='text-chart'><h4>{config.title}</h4>"
            
            y_series = data.get('y_series', {})
            
            for series_name, y_data in y_series.items():
                if y_data:
                    latest_value = y_data[-1] if isinstance(y_data, list) else y_data
                    avg_value = statistics.mean(y_data) if isinstance(y_data, list) and len(y_data) > 1 else latest_value
                    
                    html += f"""
                    <div class='metric-row'>
                        <strong>{series_name}:</strong>
                        <span>Current: {latest_value:.2f}</span>
                        <span>Average: {avg_value:.2f}</span>
                    </div>
                    """
            
            html += "</div>"
            return html
            
        except Exception as e:
            return f"<div>Error generating text chart: {e}</div>"
    
    async def generate_gauge_chart(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate gauge chart for single metrics"""
        if not PLOTLY_AVAILABLE:
            return await self._generate_text_gauge(data, config)
        
        try:
            value = data.get('value', 0)
            min_value = data.get('min', 0)
            max_value = data.get('max', 100)
            threshold_good = data.get('threshold_good', max_value * 0.7)
            threshold_warning = data.get('threshold_warning', max_value * 0.9)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = value,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': config.title},
                delta = {'reference': data.get('reference', value)},
                gauge = {
                    'axis': {'range': [None, max_value]},
                    'bar': {'color': self.color_palette['primary']},
                    'steps': [
                        {'range': [min_value, threshold_good], 'color': self.color_palette['success']},
                        {'range': [threshold_good, threshold_warning], 'color': self.color_palette['warning']},
                        {'range': [threshold_warning, max_value], 'color': self.color_palette['error']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': threshold_warning
                    }
                }
            ))
            
            fig.update_layout(height=config.height)
            
            return fig.to_html(include_plotlyjs='cdn', div_id=f"gauge_{config.widget_id}")
            
        except Exception as e:
            return f"<div>Error generating gauge: {e}</div>"
    
    async def _generate_text_gauge(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate text-based gauge when Plotly unavailable"""
        value = data.get('value', 0)
        max_value = data.get('max', 100)
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        
        # Create ASCII progress bar
        bar_length = 20
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        return f"""
        <div class='text-gauge'>
            <h4>{config.title}</h4>
            <div class='gauge-value'>{value:.2f} / {max_value}</div>
            <div class='gauge-bar'>{bar} {percentage:.1f}%</div>
        </div>
        """
    
    async def generate_heatmap(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate heatmap visualization"""
        if PLOTLY_AVAILABLE:
            return await self._generate_plotly_heatmap(data, config)
        else:
            return await self._generate_text_heatmap(data, config)
    
    async def _generate_plotly_heatmap(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate interactive heatmap with Plotly"""
        try:
            z_data = data.get('z_data', [])
            x_labels = data.get('x_labels', [])
            y_labels = data.get('y_labels', [])
            
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=x_labels,
                y=y_labels,
                colorscale='RdYlGn_r',  # Red-Yellow-Green reversed
                showscale=True
            ))
            
            fig.update_layout(
                title=config.title,
                height=config.height,
                xaxis_title='Services',
                yaxis_title='Metrics'
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id=f"heatmap_{config.widget_id}")
            
        except Exception as e:
            return f"<div>Error generating heatmap: {e}</div>"
    
    async def _generate_text_heatmap(self, data: Dict[str, Any], config: WidgetConfig) -> str:
        """Generate text-based heatmap"""
        z_data = data.get('z_data', [])
        x_labels = data.get('x_labels', [])
        y_labels = data.get('y_labels', [])
        
        if not z_data or not x_labels or not y_labels:
            return f"<div>No heatmap data available for {config.title}</div>"
        
        html = f"<div class='text-heatmap'><h4>{config.title}</h4><table>"
        
        # Header row
        html += "<tr><th></th>"
        for x_label in x_labels:
            html += f"<th>{x_label}</th>"
        html += "</tr>"
        
        # Data rows
        for i, y_label in enumerate(y_labels):
            html += f"<tr><th>{y_label}</th>"
            for j, x_label in enumerate(x_labels):
                if i < len(z_data) and j < len(z_data[i]):
                    value = z_data[i][j]
                    # Simple color coding based on value
                    if value > 0.8:
                        color_class = "high"
                    elif value > 0.5:
                        color_class = "medium"
                    else:
                        color_class = "low"
                    html += f"<td class='{color_class}'>{value:.2f}</td>"
                else:
                    html += "<td>-</td>"
            html += "</tr>"
        
        html += "</table></div>"
        return html


class AlertManager:
    """Manage dashboard alerts and notifications"""
    
    def __init__(self):
        self.alerts: List[DashboardAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_channels: Dict[str, Callable] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def add_alert_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add alert rule"""
        self.alert_rules[rule_name] = rule_config
        self.logger.info(f"📢 Added alert rule: {rule_name}")
    
    def register_notification_channel(self, channel_name: str, handler: Callable):
        """Register notification channel"""
        self.notification_channels[channel_name] = handler
        self.logger.info(f"📡 Registered notification channel: {channel_name}")
    
    async def check_alert_conditions(self, metrics: Dict[str, Any]) -> List[DashboardAlert]:
        """Check metrics against alert rules"""
        new_alerts = []
        
        for rule_name, rule_config in self.alert_rules.items():
            try:
                alert = await self._evaluate_alert_rule(rule_name, rule_config, metrics)
                if alert:
                    new_alerts.append(alert)
            except Exception as e:
                self.logger.error(f"❌ Error evaluating alert rule {rule_name}: {e}")
        
        # Add new alerts to the list
        self.alerts.extend(new_alerts)
        
        # Send notifications
        for alert in new_alerts:
            await self._send_notifications(alert)
        
        return new_alerts
    
    async def _evaluate_alert_rule(self, rule_name: str, rule_config: Dict[str, Any], 
                                 metrics: Dict[str, Any]) -> Optional[DashboardAlert]:
        """Evaluate single alert rule"""
        metric_path = rule_config.get('metric_path', '')
        threshold = rule_config.get('threshold', 0)
        comparison = rule_config.get('comparison', 'greater_than')  # greater_than, less_than, equals
        level = AlertLevel[rule_config.get('level', 'WARNING')]
        
        # Extract metric value
        metric_value = self._extract_metric_value(metrics, metric_path)
        if metric_value is None:
            return None
        
        # Check condition
        condition_met = False
        if comparison == 'greater_than':
            condition_met = metric_value > threshold
        elif comparison == 'less_than':
            condition_met = metric_value < threshold
        elif comparison == 'equals':
            condition_met = metric_value == threshold
        
        if condition_met:
            return DashboardAlert(
                alert_id=str(uuid.uuid4()),
                level=level,
                title=rule_config.get('title', f'Alert: {rule_name}'),
                message=rule_config.get('message', f'Metric {metric_path} is {metric_value}, threshold: {threshold}'),
                timestamp=datetime.now(),
                source_service=rule_config.get('source_service', 'dashboard'),
                metadata={
                    'rule_name': rule_name,
                    'metric_value': metric_value,
                    'threshold': threshold,
                    'comparison': comparison
                }
            )
        
        return None
    
    def _extract_metric_value(self, metrics: Dict[str, Any], path: str) -> Optional[float]:
        """Extract metric value from nested dictionary using dot notation"""
        try:
            parts = path.split('.')
            value = metrics
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return float(value) if isinstance(value, (int, float)) else None
            
        except (ValueError, TypeError):
            return None
    
    async def _send_notifications(self, alert: DashboardAlert):
        """Send alert notifications to registered channels"""
        for channel_name, handler in self.notification_channels.items():
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f"❌ Failed to send notification via {channel_name}: {e}")
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[DashboardAlert]:
        """Get active (non-dismissed) alerts"""
        active_alerts = [alert for alert in self.alerts if not alert.dismissed]
        
        if level:
            active_alerts = [alert for alert in active_alerts if alert.level == level]
        
        return sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.dismissed = True
                self.logger.info(f"✅ Alert dismissed: {alert_id}")
                return True
        return False


class CircuitBreakerDashboard:
    """
    Enterprise circuit breaker dashboard with real-time monitoring.
    Provides comprehensive visualization and alerting capabilities.
    """
    
    def __init__(self, config: DashboardConfig = None):
        """Initialize circuit breaker dashboard"""
        self.config = config or DashboardConfig()
        self.metrics_collector = MetricsCollector()
        self.chart_generator = ChartGenerator(self.config.theme)
        self.alert_manager = AlertManager()
        
        self.widgets: Dict[str, WidgetConfig] = {}
        self.dashboard_data: Dict[str, Any] = {}
        self.update_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default widgets and alerts
        self._initialize_default_setup()
        
        self.logger.info("📊 Circuit Breaker Dashboard initialized - Enterprise monitoring ready")
    
    def _initialize_default_setup(self):
        """Initialize default widgets and alert rules"""
        # Default widgets
        self.add_widget(WidgetConfig(
            widget_id="circuit_states",
            title="Circuit Breaker States",
            chart_type=ChartType.PIE_CHART,
            data_source="circuit_states",
            position=(0, 0),
            size=(6, 4)
        ))
        
        self.add_widget(WidgetConfig(
            widget_id="response_times",
            title="Response Times",
            chart_type=ChartType.LINE_CHART,
            data_source="response_times",
            position=(6, 0),
            size=(6, 4)
        ))
        
        self.add_widget(WidgetConfig(
            widget_id="error_rates",
            title="Error Rates",
            chart_type=ChartType.AREA_CHART,
            data_source="error_rates",
            position=(0, 4),
            size=(6, 4)
        ))
        
        self.add_widget(WidgetConfig(
            widget_id="throughput_gauge",
            title="System Throughput",
            chart_type=ChartType.GAUGE,
            data_source="throughput",
            position=(6, 4),
            size=(6, 4)
        ))
        
        # Default alert rules
        self.alert_manager.add_alert_rule("high_error_rate", {
            'metric_path': 'circuit_metrics.overall_error_rate',
            'threshold': 0.1,
            'comparison': 'greater_than',
            'level': 'ERROR',
            'title': 'High Error Rate Alert',
            'message': 'Overall error rate exceeded 10%'
        })
        
        self.alert_manager.add_alert_rule("circuit_breaker_open", {
            'metric_path': 'circuit_states.open_count',
            'threshold': 0,
            'comparison': 'greater_than',
            'level': 'WARNING',
            'title': 'Circuit Breaker Open',
            'message': 'One or more circuit breakers are in OPEN state'
        })
    
    async def create_realtime_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create real-time dashboard with custom configuration"""
        try:
            # Update configuration
            if 'title' in dashboard_config:
                self.config.title = dashboard_config['title']
            if 'theme' in dashboard_config:
                self.config.theme = DashboardTheme[dashboard_config['theme']]
                self.chart_generator = ChartGenerator(self.config.theme)
            if 'refresh_interval' in dashboard_config:
                self.config.refresh_interval_seconds = dashboard_config['refresh_interval']
            
            # Add custom widgets
            custom_widgets = dashboard_config.get('widgets', [])
            for widget_config in custom_widgets:
                widget = WidgetConfig(**widget_config)
                self.add_widget(widget)
            
            # Register custom metric sources
            metric_sources = dashboard_config.get('metric_sources', {})
            for source_name, source_config in metric_sources.items():
                # In a real implementation, this would create actual metric collectors
                # For demo, we'll register dummy collectors
                self.metrics_collector.register_metric_source(
                    source_name, 
                    lambda: self._generate_sample_metrics(source_name)
                )
            
            # Generate dashboard HTML
            dashboard_html = await self._generate_dashboard_html()
            
            # Start real-time updates if enabled
            if self.config.enable_real_time:
                await self.start_realtime_updates()
            
            self.logger.info(f"📊 Real-time dashboard created: {self.config.title}")
            return dashboard_html
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create real-time dashboard: {e}")
            raise
    
    def add_widget(self, widget_config: WidgetConfig):
        """Add widget to dashboard"""
        self.widgets[widget_config.widget_id] = widget_config
        self.logger.info(f"📈 Added widget: {widget_config.title} ({widget_config.chart_type.value})")
    
    def remove_widget(self, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            self.logger.info(f"🗑️ Removed widget: {widget_id}")
            return True
        return False
    
    async def setup_alert_notifications(self, notification_config: Dict[str, Any]) -> bool:
        """Setup alert notification channels"""
        try:
            channels = notification_config.get('channels', {})
            
            for channel_name, channel_config in channels.items():
                channel_type = channel_config.get('type', 'email')
                
                if channel_type == 'email':
                    handler = lambda alert: self._send_email_notification(alert, channel_config)
                elif channel_type == 'webhook':
                    handler = lambda alert: self._send_webhook_notification(alert, channel_config)
                elif channel_type == 'slack':
                    handler = lambda alert: self._send_slack_notification(alert, channel_config)
                else:
                    continue
                
                self.alert_manager.register_notification_channel(channel_name, handler)
            
            # Add custom alert rules
            alert_rules = notification_config.get('alert_rules', {})
            for rule_name, rule_config in alert_rules.items():
                self.alert_manager.add_alert_rule(rule_name, rule_config)
            
            self.logger.info(f"📢 Setup {len(channels)} notification channels and {len(alert_rules)} alert rules")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup alert notifications: {e}")
            return False
    
    async def _send_email_notification(self, alert: DashboardAlert, config: Dict[str, Any]):
        """Send email notification (placeholder)"""
        # In a real implementation, this would send actual emails
        self.logger.info(f"📧 Email notification: {alert.title} to {config.get('recipients', [])}")
    
    async def _send_webhook_notification(self, alert: DashboardAlert, config: Dict[str, Any]):
        """Send webhook notification"""
        import aiohttp
        
        try:
            webhook_url = config.get('url')
            if not webhook_url:
                return
            
            payload = {
                'alert_id': alert.alert_id,
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'source_service': alert.source_service
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info(f"🔗 Webhook notification sent: {alert.title}")
                    else:
                        self.logger.warning(f"⚠️ Webhook notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"❌ Webhook notification error: {e}")
    
    async def _send_slack_notification(self, alert: DashboardAlert, config: Dict[str, Any]):
        """Send Slack notification (placeholder)"""
        # In a real implementation, this would send to Slack API
        self.logger.info(f"💬 Slack notification: {alert.title} to {config.get('channel', '#alerts')}")
    
    async def generate_executive_reports(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive reports with KPIs and business metrics"""
        try:
            report_type = report_config.get('type', 'daily')
            time_range = report_config.get('time_range', 24)  # hours
            
            # Collect comprehensive metrics
            all_metrics = await self.metrics_collector.collect_all_metrics()
            
            # Calculate executive KPIs
            kpis = await self._calculate_executive_kpis(all_metrics, time_range)
            
            # Generate insights
            insights = await self._generate_insights(all_metrics, kpis)
            
            # Create recommendations
            recommendations = await self._generate_recommendations(all_metrics, insights)
            
            report = {
                'report_id': str(uuid.uuid4()),
                'report_type': report_type,
                'generation_time': datetime.now().isoformat(),
                'time_range_hours': time_range,
                'executive_summary': {
                    'overall_health_score': kpis.get('health_score', 0),
                    'system_availability': kpis.get('availability', 0),
                    'performance_score': kpis.get('performance_score', 0),
                    'reliability_score': kpis.get('reliability_score', 0)
                },
                'key_metrics': kpis,
                'insights': insights,
                'recommendations': recommendations,
                'alert_summary': {
                    'total_alerts': len(self.alert_manager.alerts),
                    'critical_alerts': len([a for a in self.alert_manager.alerts if a.level == AlertLevel.CRITICAL]),
                    'active_alerts': len(self.alert_manager.get_active_alerts())
                }
            }
            
            # Generate visualizations for report
            if report_config.get('include_charts', True):
                report['charts'] = await self._generate_report_charts(all_metrics)
            
            self.logger.info(f"📋 Generated executive report: {report_type}")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate executive report: {e}")
            raise
    
    async def _calculate_executive_kpis(self, metrics: Dict[str, Any], time_range: int) -> Dict[str, float]:
        """Calculate executive-level KPIs"""
        # Sample KPI calculations
        total_requests = sum(m.get('total_requests', 0) for m in metrics.values() if isinstance(m, dict))
        total_errors = sum(m.get('error_count', 0) for m in metrics.values() if isinstance(m, dict))
        
        error_rate = (total_errors / total_requests) if total_requests > 0 else 0
        availability = 1.0 - error_rate
        
        # Health score (composite metric)
        health_score = min(100, max(0, (availability * 100) - (error_rate * 50)))
        
        # Performance score (based on response times)
        avg_response_times = [m.get('avg_response_time', 0) for m in metrics.values() 
                             if isinstance(m, dict) and 'avg_response_time' in m]
        avg_response_time = statistics.mean(avg_response_times) if avg_response_times else 0
        performance_score = max(0, 100 - (avg_response_time * 20))  # Penalty for slow responses
        
        # Reliability score (based on circuit breaker states)
        open_circuits = sum(m.get('open_circuits', 0) for m in metrics.values() if isinstance(m, dict))
        total_circuits = sum(m.get('total_circuits', 1) for m in metrics.values() if isinstance(m, dict))
        reliability_score = ((total_circuits - open_circuits) / total_circuits * 100) if total_circuits > 0 else 100
        
        return {
            'health_score': health_score,
            'availability': availability * 100,
            'performance_score': performance_score,
            'reliability_score': reliability_score,
            'total_requests': total_requests,
            'error_rate': error_rate * 100,
            'avg_response_time': avg_response_time,
            'open_circuits': open_circuits
        }
    
    async def _generate_insights(self, metrics: Dict[str, Any], kpis: Dict[str, float]) -> List[str]:
        """Generate insights from metrics and KPIs"""
        insights = []
        
        # Availability insights
        if kpis['availability'] < 99.0:
            insights.append(f"System availability is below target (99%) at {kpis['availability']:.2f}%")
        elif kpis['availability'] >= 99.9:
            insights.append("Excellent system availability maintained above 99.9%")
        
        # Performance insights
        if kpis['avg_response_time'] > 1.0:
            insights.append(f"Response times are elevated at {kpis['avg_response_time']:.2f}s average")
        
        # Circuit breaker insights
        if kpis['open_circuits'] > 0:
            insights.append(f"{int(kpis['open_circuits'])} circuit breakers are currently open, indicating service issues")
        
        # Error rate insights
        if kpis['error_rate'] > 5.0:
            insights.append(f"Error rate is concerning at {kpis['error_rate']:.2f}%")
        elif kpis['error_rate'] < 1.0:
            insights.append("Error rate is excellent, below 1%")
        
        return insights
    
    async def _generate_recommendations(self, metrics: Dict[str, Any], insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on insights, generate recommendations
        for insight in insights:
            if "availability" in insight.lower() and "below" in insight.lower():
                recommendations.append("Consider scaling up critical services and reviewing error handling")
            elif "response times" in insight.lower():
                recommendations.append("Investigate performance bottlenecks and consider caching strategies")
            elif "circuit breakers" in insight.lower() and "open" in insight.lower():
                recommendations.append("Review and restart failed services, check dependencies")
            elif "error rate" in insight.lower() and "concerning" in insight.lower():
                recommendations.append("Immediate investigation required - check logs and service health")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring trends")
        
        return recommendations
    
    async def _generate_report_charts(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts for executive report"""
        charts = {}
        
        try:
            # Availability trend chart
            availability_data = {
                'x_data': [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)],
                'y_series': {
                    'Availability %': [99.5 + (i % 3) * 0.1 for i in range(24)]  # Sample data
                },
                'x_title': 'Time',
                'y_title': 'Availability %'
            }
            
            availability_config = WidgetConfig(
                widget_id="availability_trend",
                title="24-Hour Availability Trend",
                chart_type=ChartType.LINE_CHART,
                data_source="availability"
            )
            
            charts['availability_trend'] = await self.chart_generator.generate_line_chart(
                availability_data, availability_config
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate report charts: {e}")
            charts['error'] = f"Chart generation failed: {e}"
        
        return charts
    
    async def _generate_dashboard_html(self) -> str:
        """Generate complete dashboard HTML"""
        try:
            # Collect all current metrics
            all_metrics = await self.metrics_collector.collect_all_metrics()
            
            # Generate widgets
            widget_html = ""
            for widget_id, widget_config in self.widgets.items():
                try:
                    # Get data for widget
                    widget_data = await self._get_widget_data(widget_config, all_metrics)
                    
                    # Generate chart based on type
                    if widget_config.chart_type == ChartType.LINE_CHART:
                        chart_html = await self.chart_generator.generate_line_chart(widget_data, widget_config)
                    elif widget_config.chart_type == ChartType.GAUGE:
                        chart_html = await self.chart_generator.generate_gauge_chart(widget_data, widget_config)
                    elif widget_config.chart_type == ChartType.HEATMAP:
                        chart_html = await self.chart_generator.generate_heatmap(widget_data, widget_config)
                    else:
                        chart_html = await self.chart_generator.generate_line_chart(widget_data, widget_config)
                    
                    widget_html += f"""
                    <div class="widget" id="widget_{widget_id}" 
                         style="grid-column: span {widget_config.size[0]}; grid-row: span {widget_config.size[1]};">
                        {chart_html}
                    </div>
                    """
                    
                except Exception as e:
                    widget_html += f"""
                    <div class="widget error" id="widget_{widget_id}">
                        <h4>{widget_config.title}</h4>
                        <p>Error loading widget: {e}</p>
                    </div>
                    """
            
            # Generate alerts section
            active_alerts = self.alert_manager.get_active_alerts()
            alerts_html = ""
            for alert in active_alerts[:5]:  # Show top 5 alerts
                alert_class = f"alert-{alert.level.value}"
                alerts_html += f"""
                <div class="alert {alert_class}">
                    <strong>{alert.title}</strong>
                    <p>{alert.message}</p>
                    <small>{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small>
                    <button onclick="dismissAlert('{alert.alert_id}')">Dismiss</button>
                </div>
                """
            
            # Complete dashboard HTML
            dashboard_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{self.config.title}</title>
                <style>
                    {self._get_dashboard_css()}
                </style>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <header>
                    <h1>{self.config.title}</h1>
                    <div class="header-info">
                        <span>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                        <span>Theme: {self.config.theme.value}</span>
                    </div>
                </header>
                
                <div class="alerts-panel">
                    <h3>Active Alerts ({len(active_alerts)})</h3>
                    {alerts_html if alerts_html else '<p>No active alerts</p>'}
                </div>
                
                <div class="dashboard-grid">
                    {widget_html}
                </div>
                
                <script>
                    {self._get_dashboard_javascript()}
                </script>
            </body>
            </html>
            """
            
            return dashboard_html
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate dashboard HTML: {e}")
            return f"<html><body><h1>Dashboard Error</h1><p>{e}</p></body></html>"
    
    def _get_dashboard_css(self) -> str:
        """Get dashboard CSS styles"""
        colors = self.chart_generator.color_palette
        
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        
        header {{
            background-color: {colors['primary']};
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .alerts-panel {{
            background-color: {colors['background']};
            border-bottom: 1px solid #ddd;
            padding: 1rem;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .alert {{
            margin: 0.5rem 0;
            padding: 0.75rem;
            border-radius: 4px;
            border-left: 4px solid;
        }}
        
        .alert-info {{
            background-color: #d1ecf1;
            border-left-color: #bee5eb;
        }}
        
        .alert-warning {{
            background-color: #fff3cd;
            border-left-color: {colors['warning']};
        }}
        
        .alert-error {{
            background-color: #f8d7da;
            border-left-color: {colors['error']};
        }}
        
        .alert-critical {{
            background-color: #f8d7da;
            border-left-color: {colors['error']};
            font-weight: bold;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            grid-gap: 1rem;
            padding: 1rem;
        }}
        
        .widget {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 1rem;
            overflow: hidden;
        }}
        
        .widget.error {{
            border-left: 4px solid {colors['error']};
        }}
        
        .text-chart, .text-gauge, .text-heatmap {{
            font-family: monospace;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            margin: 0.5rem 0;
        }}
        
        .gauge-bar {{
            font-family: monospace;
            background-color: #f0f0f0;
            padding: 0.25rem;
            border-radius: 4px;
        }}
        
        .text-heatmap table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .text-heatmap th, .text-heatmap td {{
            padding: 0.5rem;
            text-align: center;
            border: 1px solid #ddd;
        }}
        
        .text-heatmap .high {{
            background-color: {colors['error']};
            color: white;
        }}
        
        .text-heatmap .medium {{
            background-color: {colors['warning']};
        }}
        
        .text-heatmap .low {{
            background-color: {colors['success']};
            color: white;
        }}
        """
    
    def _get_dashboard_javascript(self) -> str:
        """Get dashboard JavaScript"""
        return f"""
        function dismissAlert(alertId) {{
            // In a real implementation, this would call the backend
            console.log('Dismissing alert:', alertId);
            
            // Hide the alert element
            const alertElement = document.querySelector(`[onclick="dismissAlert('${{alertId}}')"]`).parentElement;
            alertElement.style.display = 'none';
        }}
        
        function refreshDashboard() {{
            window.location.reload();
        }}
        
        // Auto-refresh every {self.config.refresh_interval_seconds} seconds
        setInterval(refreshDashboard, {self.config.refresh_interval_seconds * 1000});
        
        console.log('Circuit Breaker Dashboard initialized');
        """
    
    async def _get_widget_data(self, widget_config: WidgetConfig, all_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for specific widget"""
        data_source = widget_config.data_source
        
        # Generate sample data based on data source
        if data_source == "circuit_states":
            return {
                'labels': ['CLOSED', 'OPEN', 'HALF_OPEN'],
                'values': [15, 3, 2],
                'colors': [self.chart_generator.color_palette['success'], 
                          self.chart_generator.color_palette['error'],
                          self.chart_generator.color_palette['warning']]
            }
        elif data_source == "response_times":
            time_points = [datetime.now() - timedelta(minutes=i*5) for i in range(12, 0, -1)]
            return {
                'x_data': time_points,
                'y_series': {
                    'Average': [0.5 + 0.1 * (i % 3) for i in range(12)],
                    'P95': [1.0 + 0.2 * (i % 4) for i in range(12)]
                },
                'x_title': 'Time',
                'y_title': 'Response Time (s)'
            }
        elif data_source == "throughput":
            return {
                'value': 850,
                'min': 0,
                'max': 1000,
                'threshold_good': 700,
                'threshold_warning': 900,
                'reference': 800
            }
        else:
            return {'error': f'Unknown data source: {data_source}'}
    
    def _generate_sample_metrics(self, source_name: str) -> Dict[str, Any]:
        """Generate sample metrics for demonstration"""
        import random
        
        return {
            'total_requests': random.randint(1000, 5000),
            'error_count': random.randint(0, 50),
            'avg_response_time': random.uniform(0.1, 2.0),
            'open_circuits': random.randint(0, 3),
            'total_circuits': 20,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_realtime_updates(self):
        """Start real-time dashboard updates"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start update tasks for each widget
        for widget_id, widget_config in self.widgets.items():
            task = asyncio.create_task(self._widget_update_loop(widget_id))
            self.update_tasks[widget_id] = task
        
        # Start alert checking task
        alert_task = asyncio.create_task(self._alert_monitoring_loop())
        self.update_tasks['alerts'] = alert_task
        
        self.logger.info(f"🔄 Started real-time updates for {len(self.widgets)} widgets")
    
    async def stop_realtime_updates(self):
        """Stop real-time dashboard updates"""
        self.is_running = False
        
        for task_name, task in self.update_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.update_tasks.clear()
        self.logger.info("⏹️ Stopped real-time updates")
    
    async def _widget_update_loop(self, widget_id: str):
        """Update loop for individual widget"""
        widget_config = self.widgets[widget_id]
        
        while self.is_running:
            try:
                # Collect metrics for this widget
                metrics = await self.metrics_collector.collect_metrics(widget_config.data_source)
                
                # Store updated data
                self.dashboard_data[widget_id] = metrics
                
                await asyncio.sleep(widget_config.refresh_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Widget update error {widget_id}: {e}")
                await asyncio.sleep(30)
    
    async def _alert_monitoring_loop(self):
        """Monitor for alert conditions"""
        while self.is_running:
            try:
                # Collect all metrics
                all_metrics = await self.metrics_collector.collect_all_metrics()
                
                # Check alert conditions
                new_alerts = await self.alert_manager.check_alert_conditions(all_metrics)
                
                if new_alerts:
                    self.logger.info(f"🚨 Generated {len(new_alerts)} new alerts")
                
                await asyncio.sleep(60)  # Check alerts every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Alert monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def export_dashboard_data(self, export_format: str = "json") -> str:
        """Export dashboard data in various formats"""
        try:
            export_data = {
                'dashboard_config': {
                    'title': self.config.title,
                    'theme': self.config.theme.value,
                    'refresh_interval': self.config.refresh_interval_seconds
                },
                'widgets': {wid: {
                    'title': w.title,
                    'type': w.chart_type.value,
                    'data_source': w.data_source
                } for wid, w in self.widgets.items()},
                'current_data': self.dashboard_data,
                'active_alerts': [
                    {
                        'id': alert.alert_id,
                        'level': alert.level.value,
                        'title': alert.title,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat()
                    } for alert in self.alert_manager.get_active_alerts()
                ],
                'export_timestamp': datetime.now().isoformat()
            }
            
            if export_format.lower() == 'json':
                return json.dumps(export_data, indent=2)
            else:
                return str(export_data)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to export dashboard data: {e}")
            return f'{{"error": "{e}"}}'
    
    async def cleanup(self):
        """Cleanup dashboard resources"""
        try:
            await self.stop_realtime_updates()
            
            self.widgets.clear()
            self.dashboard_data.clear()
            
            self.logger.info("🧹 Circuit Breaker Dashboard cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global dashboard instance
circuit_breaker_dashboard = None


def create_dashboard(config: DashboardConfig = None) -> CircuitBreakerDashboard:
    """Create circuit breaker dashboard instance"""
    global circuit_breaker_dashboard
    circuit_breaker_dashboard = CircuitBreakerDashboard(config)
    return circuit_breaker_dashboard


# Export main classes and functions
__all__ = [
    'CircuitBreakerDashboard',
    'DashboardConfig',
    'WidgetConfig',
    'DashboardAlert',
    'DashboardTheme',
    'ChartType',
    'AlertLevel',
    'MetricsCollector',
    'ChartGenerator',
    'AlertManager',
    'create_dashboard'
]


if __name__ == "__main__":
    async def demo():
        """Demo circuit breaker dashboard functionality"""
        # Create dashboard configuration
        config = DashboardConfig(
            title="IA Chérie Circuit Breakers Dashboard",
            theme=DashboardTheme.ENTERPRISE,
            refresh_interval_seconds=10,
            enable_real_time=True
        )
        
        # Create dashboard
        dashboard = CircuitBreakerDashboard(config)
        
        # Register sample metric sources
        dashboard.metrics_collector.register_metric_source(
            "circuit_states",
            lambda: {"closed": 15, "open": 2, "half_open": 1}
        )
        
        # Setup notifications
        notification_config = {
            'channels': {
                'webhook': {
                    'type': 'webhook',
                    'url': 'https://hooks.slack.com/services/example'
                }
            },
            'alert_rules': {
                'demo_rule': {
                    'metric_path': 'circuit_states.open',
                    'threshold': 1,
                    'comparison': 'greater_than',
                    'level': 'WARNING',
                    'title': 'Demo Alert',
                    'message': 'This is a demo alert'
                }
            }
        }
        
        await dashboard.setup_alert_notifications(notification_config)
        
        # Create dashboard HTML
        dashboard_html = await dashboard.create_realtime_dashboard({
            'title': 'Demo Circuit Breakers Dashboard',
            'theme': 'ENTERPRISE'
        })
        
        print(f"Dashboard HTML generated: {len(dashboard_html)} characters")
        
        # Generate executive report
        report = await dashboard.generate_executive_reports({
            'type': 'demo',
            'time_range': 24,
            'include_charts': True
        })
        
        print(f"Executive report: {json.dumps(report, indent=2, default=str)}")
        
        # Export data
        export_data = await dashboard.export_dashboard_data('json')
        print(f"Export data: {len(export_data)} characters")
        
        # Cleanup
        await dashboard.cleanup()
    
    # Run demo
    asyncio.run(demo())