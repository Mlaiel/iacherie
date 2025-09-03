"""Real-Time Financial Dashboard
Enterprise-grade real-time financial monitoring and analytics dashboard for creators and platform administrators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import json
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class DashboardMetricType(Enum):
    """Dashboard metric types"""
    REVENUE = "revenue"
    EXPENSES = "expenses"
    PROFIT = "profit"
    TRANSACTIONS = "transactions"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    PLATFORM_FEES = "platform_fees"
    ROYALTY_PAYMENTS = "royalty_payments"
    CONVERSION_RATES = "conversion_rates"
    CHURN_RATE = "churn_rate"


class TimeInterval(Enum):
    """Time intervals for metrics"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class FinancialMetric:
    """Financial metric data point"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: DashboardMetricType = DashboardMetricType.REVENUE
    value: Decimal = Decimal('0.00')
    previous_value: Decimal = Decimal('0.00')
    change_percentage: Decimal = Decimal('0.00')
    currency: str = "EUR"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    interval: TimeInterval = TimeInterval.REAL_TIME
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    widget_type: str = "metric"  # metric, chart, table, alert
    metric_types: List[DashboardMetricType] = field(default_factory=list)
    time_interval: TimeInterval = TimeInterval.DAILY
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 1, "height": 1})
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FinancialAlert:
    """Financial alert configuration"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    metric_type: DashboardMetricType = DashboardMetricType.REVENUE
    threshold_value: Decimal = Decimal('0.00')
    threshold_type: str = "above"  # above, below, change_percentage
    is_active: bool = True
    notification_channels: List[str] = field(default_factory=list)
    last_triggered: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class RealTimeFinancialDashboard:
    """Enterprise-grade real-time financial dashboard"""

    def __init__(self):
        self.metrics_history: Dict[str, List[FinancialMetric]] = defaultdict(list)
        self.active_widgets: Dict[str, DashboardWidget] = {}
        self.financial_alerts: Dict[str, FinancialAlert] = {}
        self.real_time_data: Dict[str, Any] = {}
        
        # Performance tracking
        self.update_frequency = timedelta(seconds=5)  # Real-time updates every 5 seconds
        self.data_retention_period = timedelta(days=365)  # Keep 1 year of data
        
        # Initialize default widgets
        self._initialize_default_widgets()
        
        # Performance metrics
        self.dashboard_metrics = {
            "total_updates": 0,
            "average_update_time": 0.0,
            "active_users": 0,
            "alerts_triggered": 0
        }

    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets"""
        default_widgets = [
            {
                "title": "Total Revenue",
                "widget_type": "metric",
                "metric_types": [DashboardMetricType.REVENUE],
                "position": {"x": 0, "y": 0, "width": 2, "height": 1}
            },
            {
                "title": "Revenue Trend",
                "widget_type": "chart",
                "metric_types": [DashboardMetricType.REVENUE],
                "time_interval": TimeInterval.DAILY,
                "position": {"x": 2, "y": 0, "width": 4, "height": 2}
            },
            {
                "title": "Platform Fees",
                "widget_type": "metric",
                "metric_types": [DashboardMetricType.PLATFORM_FEES],
                "position": {"x": 0, "y": 1, "width": 2, "height": 1}
            },
            {
                "title": "Profit Margin",
                "widget_type": "metric",
                "metric_types": [DashboardMetricType.PROFIT],
                "position": {"x": 6, "y": 0, "width": 2, "height": 1}
            },
            {
                "title": "Transaction Volume",
                "widget_type": "chart",
                "metric_types": [DashboardMetricType.TRANSACTIONS],
                "time_interval": TimeInterval.HOURLY,
                "position": {"x": 0, "y": 2, "width": 4, "height": 2}
            },
            {
                "title": "Content Performance",
                "widget_type": "table",
                "metric_types": [DashboardMetricType.CONTENT_PERFORMANCE],
                "position": {"x": 4, "y": 2, "width": 4, "height": 2}
            }
        ]
        
        for widget_config in default_widgets:
            widget = DashboardWidget(
                title=widget_config["title"],
                widget_type=widget_config["widget_type"],
                metric_types=widget_config["metric_types"],
                time_interval=widget_config.get("time_interval", TimeInterval.DAILY),
                position=widget_config["position"]
            )
            self.active_widgets[widget.widget_id] = widget

    async def update_metric(
        self,
        metric_type: DashboardMetricType,
        value: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
        interval: TimeInterval = TimeInterval.REAL_TIME
    ) -> FinancialMetric:
        """Update financial metric with real-time data"""
        try:
            # Get previous value for change calculation
            metric_key = f"{metric_type.value}_{interval.value}"
            previous_metrics = self.metrics_history.get(metric_key, [])
            previous_value = previous_metrics[-1].value if previous_metrics else Decimal('0.00')
            
            # Calculate percentage change
            change_percentage = Decimal('0.00')
            if previous_value > 0:
                change_percentage = ((value - previous_value) / previous_value) * Decimal('100')
            
            # Create new metric
            metric = FinancialMetric(
                metric_type=metric_type,
                value=value,
                previous_value=previous_value,
                change_percentage=change_percentage,
                interval=interval,
                metadata=metadata or {}
            )
            
            # Store metric
            self.metrics_history[metric_key].append(metric)
            
            # Update real-time data
            self.real_time_data[metric_type.value] = {
                "current_value": float(value),
                "previous_value": float(previous_value),
                "change_percentage": float(change_percentage),
                "last_updated": metric.timestamp.isoformat(),
                "trend": "up" if change_percentage > 0 else "down" if change_percentage < 0 else "stable"
            }
            
            # Clean old data
            await self._cleanup_old_metrics(metric_key)
            
            # Check alerts
            await self._check_alerts(metric)
            
            # Update performance metrics
            self.dashboard_metrics["total_updates"] += 1
            
            logger.debug(f"Updated metric {metric_type.value}: {value} (change: {change_percentage}%)")
            return metric
            
        except Exception as e:
            logger.error(f"Failed to update metric {metric_type.value}: {str(e)}")
            raise

    async def get_dashboard_data(
        self,
        user_id: Optional[int] = None,
        content_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            dashboard_data = {
                "overview": {
                    "last_updated": datetime.utcnow().isoformat(),
                    "real_time_metrics": dict(self.real_time_data),
                    "performance": dict(self.dashboard_metrics)
                },
                "widgets": [],
                "alerts": [],
                "time_series_data": {}
            }
            
            # Prepare widget data
            for widget in self.active_widgets.values():
                if not widget.is_active:
                    continue
                
                widget_data = {
                    "widget_id": widget.widget_id,
                    "title": widget.title,
                    "type": widget.widget_type,
                    "position": widget.position,
                    "data": await self._get_widget_data(widget, start_date, end_date)
                }
                dashboard_data["widgets"].append(widget_data)
            
            # Prepare alert data
            for alert in self.financial_alerts.values():
                if not alert.is_active:
                    continue
                
                alert_data = {
                    "alert_id": alert.alert_id,
                    "name": alert.name,
                    "metric_type": alert.metric_type.value,
                    "threshold_value": float(alert.threshold_value),
                    "threshold_type": alert.threshold_type,
                    "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None,
                    "status": await self._get_alert_status(alert)
                }
                dashboard_data["alerts"].append(alert_data)
            
            # Prepare time series data
            for metric_type in DashboardMetricType:
                time_series = await self._get_time_series_data(
                    metric_type, 
                    TimeInterval.HOURLY, 
                    start_date, 
                    end_date
                )
                dashboard_data["time_series_data"][metric_type.value] = time_series
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {str(e)}")
            raise

    async def _get_widget_data(
        self,
        widget: DashboardWidget,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get data for specific widget"""
        try:
            widget_data = {"values": [], "chart_data": [], "table_data": []}
            
            for metric_type in widget.metric_types:
                metric_key = f"{metric_type.value}_{widget.time_interval.value}"
                metrics = self.metrics_history.get(metric_key, [])
                
                # Filter by date range
                if start_date or end_date:
                    filtered_metrics = []
                    for metric in metrics:
                        if start_date and metric.timestamp < start_date:
                            continue
                        if end_date and metric.timestamp > end_date:
                            continue
                        filtered_metrics.append(metric)
                    metrics = filtered_metrics
                
                if widget.widget_type == "metric":
                    # Single value metrics
                    if metrics:
                        latest_metric = metrics[-1]
                        widget_data["values"].append({
                            "metric_type": metric_type.value,
                            "value": float(latest_metric.value),
                            "change_percentage": float(latest_metric.change_percentage),
                            "currency": latest_metric.currency
                        })
                
                elif widget.widget_type == "chart":
                    # Chart data
                    chart_points = []
                    for metric in metrics[-50:]:  # Last 50 points
                        chart_points.append({
                            "timestamp": metric.timestamp.isoformat(),
                            "value": float(metric.value),
                            "metric_type": metric_type.value
                        })
                    widget_data["chart_data"].extend(chart_points)
                
                elif widget.widget_type == "table":
                    # Table data
                    table_rows = []
                    for metric in metrics[-20:]:  # Last 20 entries
                        table_rows.append({
                            "timestamp": metric.timestamp.isoformat(),
                            "metric_type": metric_type.value,
                            "value": float(metric.value),
                            "change": float(metric.change_percentage),
                            "metadata": metric.metadata
                        })
                    widget_data["table_data"].extend(table_rows)
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data: {str(e)}")
            return {"values": [], "chart_data": [], "table_data": []}

    async def _get_time_series_data(
        self,
        metric_type: DashboardMetricType,
        interval: TimeInterval,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get time series data for metric"""
        try:
            metric_key = f"{metric_type.value}_{interval.value}"
            metrics = self.metrics_history.get(metric_key, [])
            
            # Filter by date range
            if start_date or end_date:
                filtered_metrics = []
                for metric in metrics:
                    if start_date and metric.timestamp < start_date:
                        continue
                    if end_date and metric.timestamp > end_date:
                        continue
                    filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            # Convert to time series format
            time_series = []
            for metric in metrics:
                time_series.append({
                    "timestamp": metric.timestamp.isoformat(),
                    "value": float(metric.value),
                    "change_percentage": float(metric.change_percentage)
                })
            
            return time_series
            
        except Exception as e:
            logger.error(f"Failed to get time series data: {str(e)}")
            return []

    async def create_financial_alert(
        self,
        name: str,
        metric_type: DashboardMetricType,
        threshold_value: Decimal,
        threshold_type: str = "above",
        notification_channels: Optional[List[str]] = None
    ) -> FinancialAlert:
        """Create new financial alert"""
        try:
            alert = FinancialAlert(
                name=name,
                metric_type=metric_type,
                threshold_value=threshold_value,
                threshold_type=threshold_type,
                notification_channels=notification_channels or ["email"]
            )
            
            self.financial_alerts[alert.alert_id] = alert
            
            logger.info(f"Created financial alert {alert.alert_id}: {name}")
            return alert
            
        except Exception as e:
            logger.error(f"Failed to create financial alert: {str(e)}")
            raise

    async def _check_alerts(self, metric: FinancialMetric):
        """Check if any alerts should be triggered"""
        try:
            for alert in self.financial_alerts.values():
                if not alert.is_active or alert.metric_type != metric.metric_type:
                    continue
                
                should_trigger = False
                
                if alert.threshold_type == "above" and metric.value > alert.threshold_value:
                    should_trigger = True
                elif alert.threshold_type == "below" and metric.value < alert.threshold_value:
                    should_trigger = True
                elif alert.threshold_type == "change_percentage":
                    if abs(metric.change_percentage) > alert.threshold_value:
                        should_trigger = True
                
                if should_trigger:
                    await self._trigger_alert(alert, metric)
                    
        except Exception as e:
            logger.error(f"Failed to check alerts: {str(e)}")

    async def _trigger_alert(self, alert: FinancialAlert, metric: FinancialMetric):
        """Trigger financial alert"""
        try:
            alert.last_triggered = datetime.utcnow()
            self.dashboard_metrics["alerts_triggered"] += 1
            
            # In real implementation, this would:
            # 1. Send notifications via configured channels
            # 2. Log alert in audit system
            # 3. Update alert status
            # 4. Possibly take automated actions
            
            logger.warning(f"Financial alert triggered: {alert.name} - {metric.metric_type.value}: {metric.value}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {str(e)}")

    async def _get_alert_status(self, alert: FinancialAlert) -> str:
        """Get current status of alert"""
        try:
            # Get latest metric value
            metric_key = f"{alert.metric_type.value}_real_time"
            metrics = self.metrics_history.get(metric_key, [])
            
            if not metrics:
                return "no_data"
            
            latest_metric = metrics[-1]
            
            if alert.threshold_type == "above":
                if latest_metric.value > alert.threshold_value:
                    return "triggered"
            elif alert.threshold_type == "below":
                if latest_metric.value < alert.threshold_value:
                    return "triggered"
            elif alert.threshold_type == "change_percentage":
                if abs(latest_metric.change_percentage) > alert.threshold_value:
                    return "triggered"
            
            return "normal"
            
        except Exception as e:
            logger.error(f"Failed to get alert status: {str(e)}")
            return "error"

    async def _cleanup_old_metrics(self, metric_key: str):
        """Clean up old metric data"""
        try:
            cutoff_date = datetime.utcnow() - self.data_retention_period
            metrics = self.metrics_history.get(metric_key, [])
            
            # Keep only recent metrics
            recent_metrics = [
                metric for metric in metrics
                if metric.timestamp > cutoff_date
            ]
            
            self.metrics_history[metric_key] = recent_metrics
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {str(e)}")

    async def get_financial_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive financial summary for period"""
        try:
            summary = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "revenue": {
                    "total": 0.0,
                    "growth_percentage": 0.0,
                    "trend": "stable"
                },
                "expenses": {
                    "total": 0.0,
                    "platform_fees": 0.0,
                    "processing_fees": 0.0
                },
                "profit": {
                    "total": 0.0,
                    "margin_percentage": 0.0
                },
                "transactions": {
                    "count": 0,
                    "average_value": 0.0,
                    "success_rate": 0.0
                },
                "top_performing_content": [],
                "alerts_summary": {
                    "total_alerts": len(self.financial_alerts),
                    "triggered_alerts": 0,
                    "critical_alerts": 0
                }
            }
            
            # Calculate metrics for period
            for metric_type in DashboardMetricType:
                metric_key = f"{metric_type.value}_daily"
                metrics = self.metrics_history.get(metric_key, [])
                
                period_metrics = [
                    metric for metric in metrics
                    if start_date <= metric.timestamp <= end_date
                ]
                
                if period_metrics:
                    total_value = sum(metric.value for metric in period_metrics)
                    
                    if metric_type == DashboardMetricType.REVENUE:
                        summary["revenue"]["total"] = float(total_value)
                    elif metric_type == DashboardMetricType.EXPENSES:
                        summary["expenses"]["total"] = float(total_value)
                    elif metric_type == DashboardMetricType.PLATFORM_FEES:
                        summary["expenses"]["platform_fees"] = float(total_value)
                    elif metric_type == DashboardMetricType.TRANSACTIONS:
                        summary["transactions"]["count"] = int(total_value)
            
            # Calculate derived metrics
            if summary["revenue"]["total"] > 0 and summary["expenses"]["total"] > 0:
                profit = summary["revenue"]["total"] - summary["expenses"]["total"]
                summary["profit"]["total"] = profit
                summary["profit"]["margin_percentage"] = (profit / summary["revenue"]["total"]) * 100
            
            if summary["transactions"]["count"] > 0:
                summary["transactions"]["average_value"] = summary["revenue"]["total"] / summary["transactions"]["count"]
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get financial summary: {str(e)}")
            raise

    async def export_dashboard_data(
        self,
        export_format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export dashboard data for external analysis"""
        try:
            export_data = {
                "export_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "format": export_format,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "metrics_data": {},
                "widgets_config": [],
                "alerts_config": []
            }
            
            # Export metrics data
            for metric_key, metrics in self.metrics_history.items():
                filtered_metrics = metrics
                if start_date or end_date:
                    filtered_metrics = [
                        metric for metric in metrics
                        if (not start_date or metric.timestamp >= start_date) and
                           (not end_date or metric.timestamp <= end_date)
                    ]
                
                export_data["metrics_data"][metric_key] = [
                    {
                        "timestamp": metric.timestamp.isoformat(),
                        "value": float(metric.value),
                        "change_percentage": float(metric.change_percentage),
                        "metadata": metric.metadata
                    }
                    for metric in filtered_metrics
                ]
            
            # Export widget configurations
            for widget in self.active_widgets.values():
                export_data["widgets_config"].append({
                    "widget_id": widget.widget_id,
                    "title": widget.title,
                    "type": widget.widget_type,
                    "metric_types": [mt.value for mt in widget.metric_types],
                    "position": widget.position,
                    "settings": widget.settings
                })
            
            # Export alert configurations
            for alert in self.financial_alerts.values():
                export_data["alerts_config"].append({
                    "alert_id": alert.alert_id,
                    "name": alert.name,
                    "metric_type": alert.metric_type.value,
                    "threshold_value": float(alert.threshold_value),
                    "threshold_type": alert.threshold_type,
                    "notification_channels": alert.notification_channels
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export dashboard data: {str(e)}")
            raise


# Global dashboard instance
_financial_dashboard = None

def get_financial_dashboard() -> RealTimeFinancialDashboard:
    """Get global financial dashboard instance"""
    global _financial_dashboard
    if _financial_dashboard is None:
        _financial_dashboard = RealTimeFinancialDashboard()
    return _financial_dashboard


async def update_revenue_metric(amount: Decimal, metadata: Optional[Dict[str, Any]] = None):
    """Update revenue metric in real-time dashboard"""
    dashboard = get_financial_dashboard()
    await dashboard.update_metric(DashboardMetricType.REVENUE, amount, metadata)


async def update_expense_metric(amount: Decimal, metadata: Optional[Dict[str, Any]] = None):
    """Update expense metric in real-time dashboard"""
    dashboard = get_financial_dashboard()
    await dashboard.update_metric(DashboardMetricType.EXPENSES, amount, metadata)


async def track_transaction_volume(count: int, metadata: Optional[Dict[str, Any]] = None):
    """Track transaction volume in dashboard"""
    dashboard = get_financial_dashboard()
    await dashboard.update_metric(DashboardMetricType.TRANSACTIONS, Decimal(str(count)), metadata)