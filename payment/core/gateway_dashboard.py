"""📊 Payment Gateway Dashboard
==============================

Enterprise dashboard for real-time payment gateway monitoring,
transaction visualization, provider performance tracking, and
executive reporting.

Features:
- Real-time transaction monitoring
- Provider performance visualization
- Alert management and notifications
- Executive reporting and KPIs
- Interactive charts and graphs
- Live data streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import aioredis

logger = logging.getLogger(__name__)


class DashboardWidget(Enum):
    """Dashboard widget types"""
    TRANSACTION_VOLUME = "transaction_volume"
    SUCCESS_RATE = "success_rate"
    REVENUE_CHART = "revenue_chart"
    PROVIDER_PERFORMANCE = "provider_performance"
    FRAUD_DETECTION = "fraud_detection"
    GEOGRAPHIC_MAP = "geographic_map"
    PAYMENT_METHODS = "payment_methods"
    ALERTS_PANEL = "alerts_panel"
    KPI_METRICS = "kpi_metrics"
    REAL_TIME_FEED = "real_time_feed"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ChartType(Enum):
    """Chart types for visualization"""
    LINE_CHART = "line"
    BAR_CHART = "bar"
    PIE_CHART = "pie"
    SCATTER_PLOT = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    CANDLESTICK = "candlestick"


@dataclass
class DashboardAlert:
    """Dashboard alert information"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    is_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPIMetric:
    """Key Performance Indicator metric"""
    metric_id: str
    name: str
    value: float
    unit: str
    previous_value: Optional[float] = None
    target_value: Optional[float] = None
    trend: str = "stable"  # up, down, stable
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardData:
    """Dashboard data container"""
    transactions_24h: int
    revenue_24h: Decimal
    success_rate_24h: float
    active_providers: List[str]
    fraud_rate_24h: float
    average_response_time: float
    top_payment_methods: List[Tuple[str, int]]
    geographic_distribution: Dict[str, int]
    hourly_trends: List[Tuple[datetime, int, Decimal]]
    alerts: List[DashboardAlert]
    kpis: List[KPIMetric]


class PaymentGatewayDashboard:
    """Enterprise dashboard for payment gateway monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.active_alerts: Dict[str, DashboardAlert] = {}
        self.kpi_metrics: Dict[str, KPIMetric] = {}
        self.real_time_data: deque = deque(maxlen=1000)
        self.widget_cache: Dict[str, Any] = {}
        self.is_initialized = False
        
        # Dashboard configuration
        self.refresh_interval = config.get('refresh_interval', 30)  # seconds
        self.data_retention_hours = config.get('data_retention_hours', 72)
        self.alert_thresholds = config.get('alert_thresholds', {
            'success_rate_min': 95.0,
            'response_time_max': 3000,  # milliseconds
            'fraud_rate_max': 2.0
        })
        
    async def initialize(self):
        """Initialize the dashboard"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = aioredis.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}"
            )
            
            # Load existing alerts and KPIs
            await self._load_dashboard_data()
            
            # Initialize default KPIs
            await self._initialize_default_kpis()
            
            # Start real-time data collection
            asyncio.create_task(self._collect_real_time_data())
            
            self.is_initialized = True
            logger.info("Payment Gateway Dashboard initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Payment Gateway Dashboard: {e}")
            raise
    
    async def _load_dashboard_data(self):
        """Load existing dashboard data from storage"""
        try:
            # Load alerts
            alerts_data = await self.redis_client.get("dashboard:alerts")
            if alerts_data:
                alerts_dict = json.loads(alerts_data.decode())
                for alert_id, alert_info in alerts_dict.items():
                    self.active_alerts[alert_id] = DashboardAlert(
                        alert_id=alert_info['alert_id'],
                        level=AlertLevel(alert_info['level']),
                        title=alert_info['title'],
                        message=alert_info['message'],
                        created_at=datetime.fromisoformat(alert_info['created_at']),
                        resolved_at=datetime.fromisoformat(alert_info['resolved_at']) if alert_info.get('resolved_at') else None,
                        is_resolved=alert_info['is_resolved'],
                        metadata=alert_info.get('metadata', {})
                    )
            
            # Load KPIs
            kpis_data = await self.redis_client.get("dashboard:kpis")
            if kpis_data:
                kpis_dict = json.loads(kpis_data.decode())
                for metric_id, metric_info in kpis_dict.items():
                    self.kpi_metrics[metric_id] = KPIMetric(
                        metric_id=metric_info['metric_id'],
                        name=metric_info['name'],
                        value=metric_info['value'],
                        unit=metric_info['unit'],
                        previous_value=metric_info.get('previous_value'),
                        target_value=metric_info.get('target_value'),
                        trend=metric_info.get('trend', 'stable'),
                        last_updated=datetime.fromisoformat(metric_info['last_updated'])
                    )
                    
            logger.info("Dashboard data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dashboard data: {e}")
    
    async def _initialize_default_kpis(self):
        """Initialize default KPI metrics"""
        try:
            default_kpis = [
                {"id": "transactions_per_hour", "name": "Transactions/Hour", "unit": "txns", "target": 1000},
                {"id": "success_rate", "name": "Success Rate", "unit": "%", "target": 99.5},
                {"id": "average_response_time", "name": "Avg Response Time", "unit": "ms", "target": 500},
                {"id": "revenue_per_hour", "name": "Revenue/Hour", "unit": "$", "target": 10000},
                {"id": "fraud_rate", "name": "Fraud Rate", "unit": "%", "target": 0.5},
                {"id": "active_providers", "name": "Active Providers", "unit": "count", "target": 4},
                {"id": "uptime", "name": "System Uptime", "unit": "%", "target": 99.99},
                {"id": "customer_satisfaction", "name": "Customer Satisfaction", "unit": "/5", "target": 4.5}
            ]
            
            for kpi_config in default_kpis:
                if kpi_config["id"] not in self.kpi_metrics:
                    self.kpi_metrics[kpi_config["id"]] = KPIMetric(
                        metric_id=kpi_config["id"],
                        name=kpi_config["name"],
                        value=0.0,
                        unit=kpi_config["unit"],
                        target_value=kpi_config["target"]
                    )
            
            await self._save_kpis()
            
        except Exception as e:
            logger.error(f"Failed to initialize default KPIs: {e}")
    
    async def _collect_real_time_data(self):
        """Collect real-time data for dashboard"""
        while True:
            try:
                # Simulate data collection - in real implementation, this would
                # connect to actual payment processing systems
                current_time = datetime.now()
                
                # Add real-time data point
                self.real_time_data.append({
                    'timestamp': current_time,
                    'transactions': np.random.poisson(50),
                    'revenue': float(np.random.normal(1000, 200)),
                    'response_time': float(np.random.gamma(2, 100)),
                    'success_rate': float(np.random.normal(98.5, 1.5))
                })
                
                # Update KPIs based on real-time data
                await self._update_kpis_from_real_time_data()
                
                # Check for alerts
                await self._check_alert_conditions()
                
                # Sleep for refresh interval
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                logger.error(f"Error in real-time data collection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _update_kpis_from_real_time_data(self):
        """Update KPI metrics from real-time data"""
        try:
            if not self.real_time_data:
                return
                
            # Calculate metrics from recent data
            recent_data = list(self.real_time_data)[-60:]  # Last 60 data points
            
            # Update transactions per hour
            transactions_per_hour = sum(d['transactions'] for d in recent_data)
            await self._update_kpi('transactions_per_hour', transactions_per_hour)
            
            # Update success rate
            avg_success_rate = np.mean([d['success_rate'] for d in recent_data])
            await self._update_kpi('success_rate', avg_success_rate)
            
            # Update average response time
            avg_response_time = np.mean([d['response_time'] for d in recent_data])
            await self._update_kpi('average_response_time', avg_response_time)
            
            # Update revenue per hour
            revenue_per_hour = sum(d['revenue'] for d in recent_data)
            await self._update_kpi('revenue_per_hour', revenue_per_hour)
            
        except Exception as e:
            logger.error(f"Failed to update KPIs from real-time data: {e}")
    
    async def _update_kpi(self, metric_id: str, new_value: float):
        """Update a specific KPI metric"""
        try:
            if metric_id in self.kpi_metrics:
                kpi = self.kpi_metrics[metric_id]
                
                # Calculate trend
                if kpi.previous_value is not None:
                    if new_value > kpi.previous_value * 1.05:
                        trend = "up"
                    elif new_value < kpi.previous_value * 0.95:
                        trend = "down"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"
                
                # Update values
                kpi.previous_value = kpi.value
                kpi.value = new_value
                kpi.trend = trend
                kpi.last_updated = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to update KPI {metric_id}: {e}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions based on current metrics"""
        try:
            current_time = datetime.now()
            
            # Check success rate threshold
            success_rate_kpi = self.kpi_metrics.get('success_rate')
            if success_rate_kpi and success_rate_kpi.value < self.alert_thresholds['success_rate_min']:
                await self._create_alert(
                    AlertLevel.ERROR,
                    "Low Success Rate",
                    f"Success rate dropped to {success_rate_kpi.value:.2f}%"
                )
            
            # Check response time threshold
            response_time_kpi = self.kpi_metrics.get('average_response_time')
            if response_time_kpi and response_time_kpi.value > self.alert_thresholds['response_time_max']:
                await self._create_alert(
                    AlertLevel.WARNING,
                    "High Response Time",
                    f"Average response time is {response_time_kpi.value:.0f}ms"
                )
            
            # Check fraud rate threshold
            fraud_rate_kpi = self.kpi_metrics.get('fraud_rate')
            if fraud_rate_kpi and fraud_rate_kpi.value > self.alert_thresholds['fraud_rate_max']:
                await self._create_alert(
                    AlertLevel.CRITICAL,
                    "High Fraud Rate",
                    f"Fraud rate increased to {fraud_rate_kpi.value:.2f}%"
                )
            
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
    
    async def _create_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict[str, Any] = None):
        """Create a new dashboard alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = DashboardAlert(
                alert_id=alert_id,
                level=level,
                title=title,
                message=message,
                created_at=datetime.now(),
                metadata=metadata or {}
            )
            
            self.active_alerts[alert_id] = alert
            await self._save_alerts()
            
            logger.warning(f"Dashboard alert created: {level.value} - {title}")
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def generate_transaction_volume_chart(self, hours: int = 24) -> Dict[str, Any]:
        """Generate transaction volume chart"""
        try:
            # Get data for the specified time period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Generate sample data (in real implementation, query from database)
            time_points = []
            current_time = start_time
            while current_time <= end_time:
                time_points.append(current_time)
                current_time += timedelta(hours=1)
            
            transaction_counts = np.random.poisson(100, len(time_points))
            success_counts = [int(count * np.random.uniform(0.95, 0.99)) for count in transaction_counts]
            failed_counts = [total - success for total, success in zip(transaction_counts, success_counts)]
            
            # Create chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=success_counts,
                mode='lines+markers',
                name='Successful Transactions',
                line=dict(color='green')
            ))
            
            fig.add_trace(go.Scatter(
                x=time_points,
                y=failed_counts,
                mode='lines+markers',
                name='Failed Transactions',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title=f'Transaction Volume - Last {hours} Hours',
                xaxis_title='Time',
                yaxis_title='Transaction Count',
                hovermode='x unified'
            )
            
            return {
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'chart_json': fig.to_json(),
                'data_points': len(time_points),
                'total_transactions': sum(transaction_counts),
                'success_rate': (sum(success_counts) / sum(transaction_counts)) * 100
            }
            
        except Exception as e:
            logger.error(f"Failed to generate transaction volume chart: {e}")
            return {'error': str(e)}
    
    async def generate_provider_performance_chart(self) -> Dict[str, Any]:
        """Generate provider performance comparison chart"""
        try:
            # Sample provider data
            providers = ['Stripe', 'PayPal', 'Wise', 'Crypto']
            success_rates = [98.5, 97.8, 99.1, 96.2]
            response_times = [450, 680, 320, 1200]
            transaction_volumes = [45000, 32000, 15000, 8000]
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Success Rate (%)', 'Response Time (ms)', 
                              'Transaction Volume', 'Provider Comparison'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # Success rate chart
            fig.add_trace(
                go.Bar(x=providers, y=success_rates, name='Success Rate', 
                      marker_color='lightblue'),
                row=1, col=1
            )
            
            # Response time chart
            fig.add_trace(
                go.Bar(x=providers, y=response_times, name='Response Time',
                      marker_color='lightcoral'),
                row=1, col=2
            )
            
            # Transaction volume chart
            fig.add_trace(
                go.Bar(x=providers, y=transaction_volumes, name='Transaction Volume',
                      marker_color='lightgreen'),
                row=2, col=1
            )
            
            # Scatter plot comparison
            fig.add_trace(
                go.Scatter(x=response_times, y=success_rates, 
                          mode='markers+text', text=providers,
                          textposition='top center',
                          marker=dict(size=[(v/1000) for v in transaction_volumes],
                                    color=transaction_volumes,
                                    colorscale='Viridis',
                                    showscale=True),
                          name='Performance Matrix'),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Payment Provider Performance Dashboard',
                showlegend=False,
                height=600
            )
            
            return {
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'chart_json': fig.to_json(),
                'providers': providers,
                'best_success_rate': max(success_rates),
                'fastest_response': min(response_times)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate provider performance chart: {e}")
            return {'error': str(e)}
    
    async def generate_revenue_chart(self, period: str = "24h") -> Dict[str, Any]:
        """Generate revenue chart for specified period"""
        try:
            # Determine time period
            if period == "24h":
                hours = 24
                interval = timedelta(hours=1)
            elif period == "7d":
                hours = 168
                interval = timedelta(hours=6)
            elif period == "30d":
                hours = 720
                interval = timedelta(days=1)
            else:
                hours = 24
                interval = timedelta(hours=1)
            
            # Generate time points
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            time_points = []
            current_time = start_time
            while current_time <= end_time:
                time_points.append(current_time)
                current_time += interval
            
            # Generate revenue data
            base_revenue = 1000
            revenue_data = []
            cumulative_revenue = 0
            
            for i, time_point in enumerate(time_points):
                # Add some realistic variation
                daily_variation = np.sin(2 * np.pi * i / 24) * 200  # Daily cycle
                weekly_variation = np.sin(2 * np.pi * i / (24 * 7)) * 500  # Weekly cycle
                random_variation = np.random.normal(0, 100)
                
                revenue = base_revenue + daily_variation + weekly_variation + random_variation
                revenue = max(revenue, 0)  # Ensure non-negative
                
                revenue_data.append(revenue)
                cumulative_revenue += revenue
            
            # Create chart
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Hourly Revenue', 'Cumulative Revenue'),
                vertical_spacing=0.1
            )
            
            # Hourly revenue
            fig.add_trace(
                go.Scatter(x=time_points, y=revenue_data,
                          mode='lines+markers',
                          name='Hourly Revenue',
                          line=dict(color='blue', width=2),
                          fill='tonexty'),
                row=1, col=1
            )
            
            # Cumulative revenue
            cumulative_data = np.cumsum(revenue_data)
            fig.add_trace(
                go.Scatter(x=time_points, y=cumulative_data,
                          mode='lines',
                          name='Cumulative Revenue',
                          line=dict(color='green', width=3)),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f'Revenue Analysis - {period.upper()}',
                showlegend=False,
                height=600
            )
            
            return {
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'chart_json': fig.to_json(),
                'total_revenue': float(cumulative_revenue),
                'average_hourly_revenue': float(np.mean(revenue_data)),
                'peak_revenue': float(max(revenue_data)),
                'period': period
            }
            
        except Exception as e:
            logger.error(f"Failed to generate revenue chart: {e}")
            return {'error': str(e)}
    
    async def generate_geographic_distribution_map(self) -> Dict[str, Any]:
        """Generate geographic distribution map of transactions"""
        try:
            # Sample geographic data
            countries = ['United States', 'United Kingdom', 'Germany', 'France', 
                        'Canada', 'Australia', 'Japan', 'Brazil', 'India', 'China']
            
            # Generate realistic transaction counts
            transaction_counts = np.random.poisson(1000, len(countries))
            
            # Create choropleth map
            fig = go.Figure(data=go.Choropleth(
                locations=countries,
                z=transaction_counts,
                locationmode='country names',
                colorscale='Blues',
                colorbar_title="Transactions"
            ))
            
            fig.update_layout(
                title='Global Transaction Distribution',
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='equirectangular'
                )
            )
            
            return {
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'chart_json': fig.to_json(),
                'top_countries': [(country, count) for country, count in 
                                 sorted(zip(countries, transaction_counts), 
                                       key=lambda x: x[1], reverse=True)[:5]],
                'total_countries': len(countries)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate geographic distribution map: {e}")
            return {'error': str(e)}
    
    async def generate_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate KPI dashboard with gauges and metrics"""
        try:
            # Create subplots for KPI gauges
            fig = make_subplots(
                rows=2, cols=4,
                specs=[[{"type": "indicator"} for _ in range(4)] for _ in range(2)],
                subplot_titles=[kpi.name for kpi in list(self.kpi_metrics.values())[:8]]
            )
            
            # Add gauge charts for each KPI
            positions = [(1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 3), (2, 4)]
            
            for i, (kpi_id, kpi) in enumerate(list(self.kpi_metrics.items())[:8]):
                row, col = positions[i]
                
                # Determine gauge color based on performance vs target
                if kpi.target_value:
                    performance_ratio = kpi.value / kpi.target_value
                    if performance_ratio >= 0.9:
                        color = "green"
                    elif performance_ratio >= 0.7:
                        color = "yellow"
                    else:
                        color = "red"
                else:
                    color = "blue"
                
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number+delta",
                        value=kpi.value,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"{kpi.name} ({kpi.unit})"},
                        delta={'reference': kpi.previous_value or 0},
                        gauge={
                            'axis': {'range': [None, kpi.target_value * 1.2 if kpi.target_value else kpi.value * 1.5]},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, (kpi.target_value or kpi.value) * 0.7], 'color': "lightgray"},
                                {'range': [(kpi.target_value or kpi.value) * 0.7, kpi.target_value or kpi.value], 'color': "gray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': kpi.target_value or kpi.value
                            }
                        }
                    ),
                    row=row, col=col
                )
            
            fig.update_layout(
                title='Payment Gateway KPI Dashboard',
                height=800
            )
            
            return {
                'chart_html': fig.to_html(include_plotlyjs='cdn'),
                'chart_json': fig.to_json(),
                'kpi_summary': {
                    kpi_id: {
                        'name': kpi.name,
                        'current_value': kpi.value,
                        'target_value': kpi.target_value,
                        'trend': kpi.trend,
                        'last_updated': kpi.last_updated.isoformat()
                    }
                    for kpi_id, kpi in self.kpi_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate KPI dashboard: {e}")
            return {'error': str(e)}
    
    async def get_dashboard_data(self) -> DashboardData:
        """Get comprehensive dashboard data"""
        try:
            # Calculate 24-hour metrics
            current_time = datetime.now()
            start_24h = current_time - timedelta(hours=24)
            
            # Sample data calculation (in real implementation, query from database)
            transactions_24h = sum(d['transactions'] for d in self.real_time_data 
                                  if d['timestamp'] > start_24h)
            revenue_24h = Decimal(str(sum(d['revenue'] for d in self.real_time_data 
                                        if d['timestamp'] > start_24h)))
            
            if self.real_time_data:
                recent_data = [d for d in self.real_time_data if d['timestamp'] > start_24h]
                success_rate_24h = np.mean([d['success_rate'] for d in recent_data]) if recent_data else 0
                fraud_rate_24h = np.random.uniform(0.1, 2.0)  # Sample fraud rate
                average_response_time = np.mean([d['response_time'] for d in recent_data]) if recent_data else 0
            else:
                success_rate_24h = 0
                fraud_rate_24h = 0
                average_response_time = 0
            
            # Sample data for other metrics
            active_providers = ['Stripe', 'PayPal', 'Wise', 'Crypto']
            top_payment_methods = [
                ('Credit Card', 45000),
                ('PayPal', 28000),
                ('Bank Transfer', 15000),
                ('Crypto', 8000),
                ('Digital Wallet', 12000)
            ]
            
            geographic_distribution = {
                'US': 35000,
                'UK': 18000,
                'DE': 15000,
                'FR': 12000,
                'CA': 10000,
                'AU': 8000,
                'JP': 7000,
                'BR': 5000
            }
            
            # Generate hourly trends
            hourly_trends = []
            for i in range(24):
                hour_time = current_time - timedelta(hours=23-i)
                hour_transactions = np.random.poisson(100)
                hour_revenue = Decimal(str(np.random.normal(1000, 200)))
                hourly_trends.append((hour_time, hour_transactions, hour_revenue))
            
            return DashboardData(
                transactions_24h=transactions_24h,
                revenue_24h=revenue_24h,
                success_rate_24h=success_rate_24h,
                active_providers=active_providers,
                fraud_rate_24h=fraud_rate_24h,
                average_response_time=average_response_time,
                top_payment_methods=top_payment_methods,
                geographic_distribution=geographic_distribution,
                hourly_trends=hourly_trends,
                alerts=list(self.active_alerts.values()),
                kpis=list(self.kpi_metrics.values())
            )
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a dashboard alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.is_resolved = True
                alert.resolved_at = datetime.now()
                
                await self._save_alerts()
                logger.info(f"Alert resolved: {alert_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def export_dashboard_data(self, format: str = "json") -> str:
        """Export dashboard data in specified format"""
        try:
            dashboard_data = await self.get_dashboard_data()
            
            if format.lower() == "json":
                # Convert to JSON-serializable format
                export_data = {
                    "transactions_24h": dashboard_data.transactions_24h,
                    "revenue_24h": float(dashboard_data.revenue_24h),
                    "success_rate_24h": dashboard_data.success_rate_24h,
                    "active_providers": dashboard_data.active_providers,
                    "fraud_rate_24h": dashboard_data.fraud_rate_24h,
                    "average_response_time": dashboard_data.average_response_time,
                    "top_payment_methods": dashboard_data.top_payment_methods,
                    "geographic_distribution": dashboard_data.geographic_distribution,
                    "exported_at": datetime.now().isoformat()
                }
                return json.dumps(export_data, indent=2)
                
            elif format.lower() == "csv":
                # Convert to CSV format
                df = pd.DataFrame([{
                    "metric": "transactions_24h",
                    "value": dashboard_data.transactions_24h
                }, {
                    "metric": "revenue_24h", 
                    "value": float(dashboard_data.revenue_24h)
                }, {
                    "metric": "success_rate_24h",
                    "value": dashboard_data.success_rate_24h
                }])
                return df.to_csv(index=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export dashboard data: {e}")
            raise
    
    async def _save_alerts(self):
        """Save alerts to storage"""
        try:
            alerts_dict = {}
            for alert_id, alert in self.active_alerts.items():
                alerts_dict[alert_id] = {
                    "alert_id": alert.alert_id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "is_resolved": alert.is_resolved,
                    "metadata": alert.metadata
                }
            
            await self.redis_client.set(
                "dashboard:alerts",
                json.dumps(alerts_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    async def _save_kpis(self):
        """Save KPIs to storage"""
        try:
            kpis_dict = {}
            for metric_id, kpi in self.kpi_metrics.items():
                kpis_dict[metric_id] = {
                    "metric_id": kpi.metric_id,
                    "name": kpi.name,
                    "value": kpi.value,
                    "unit": kpi.unit,
                    "previous_value": kpi.previous_value,
                    "target_value": kpi.target_value,
                    "trend": kpi.trend,
                    "last_updated": kpi.last_updated.isoformat()
                }
            
            await self.redis_client.set(
                "dashboard:kpis",
                json.dumps(kpis_dict),
                ex=86400  # 1 day expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save KPIs: {e}")
    
    async def get_dashboard_status(self) -> Dict[str, Any]:
        """Get dashboard status and health"""
        try:
            unresolved_alerts = [alert for alert in self.active_alerts.values() if not alert.is_resolved]
            critical_alerts = [alert for alert in unresolved_alerts if alert.level == AlertLevel.CRITICAL]
            
            return {
                "is_initialized": self.is_initialized,
                "total_alerts": len(self.active_alerts),
                "unresolved_alerts": len(unresolved_alerts),
                "critical_alerts": len(critical_alerts),
                "total_kpis": len(self.kpi_metrics),
                "real_time_data_points": len(self.real_time_data),
                "last_updated": datetime.now().isoformat(),
                "refresh_interval": self.refresh_interval
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard status: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the dashboard and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Payment Gateway Dashboard closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Payment Gateway Dashboard: {e}")