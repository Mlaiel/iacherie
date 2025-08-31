"""Blockchain Analytics and Intelligence Module

Advanced blockchain analytics, monitoring, and intelligence system for the
IA Influencer Agent platform providing comprehensive insights into content
protection performance, revenue analytics, and market intelligence.

Features:
- Real-time blockchain transaction monitoring and analysis
- Content protection performance metrics and KPIs
- Revenue analytics and financial intelligence
- Market trends analysis and predictive modeling
- Fraud detection and risk assessment
- Compliance monitoring and regulatory reporting
- Advanced data visualization and dashboards
- AI-powered insights and recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead AI Developer + Blockchain Specialist + Backend Senior + ML Engineer + 
      DBA + Security Expert + Microservices Architect + Audio Processing + 
      DevOps Engineer + IA Prompt Engineer

Copyright: All rights reserved. Unauthorized use prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import statistics
from collections import defaultdict

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class AnalyticsMetric(Enum):
    """Types of analytics metrics tracked."""    TRANSACTION_VOLUME = "transaction_volume"
    REVENUE_PERFORMANCE = "revenue_performance"
    PROTECTION_EFFECTIVENESS = "protection_effectiveness"
    USER_ENGAGEMENT = "user_engagement"
    NETWORK_HEALTH = "network_health"
    FRAUD_DETECTION = "fraud_detection"
    COMPLIANCE_STATUS = "compliance_status"
    MARKET_TRENDS = "market_trends"

class TimeFrame(Enum):
    """Time frames for analytics reporting."""    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AlertSeverity(Enum):
    """Severity levels for analytics alerts."""    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    URGENT = "urgent"

@dataclass
class AnalyticsConfig:
    """Configuration for blockchain analytics system."""    enabled_metrics: List[AnalyticsMetric]
    update_intervals: Dict[AnalyticsMetric, int]  # seconds
    data_retention_days: int = 365
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    ml_models_enabled: bool = True
    fraud_detection_enabled: bool = True
    compliance_monitoring_enabled: bool = True

@dataclass
class MetricDataPoint:
    """Individual metric data point."""    metric_type: AnalyticsMetric
    timestamp: datetime
    value: Union[float, int, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AnalyticsAlert:
    """Analytics alert notification."""    alert_id: str
    metric_type: AnalyticsMetric
    severity: AlertSeverity
    title: str
    description: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    affected_entities: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""    report_id: str
    report_type: str
    time_period: Tuple[datetime, datetime]
    metrics_summary: Dict[AnalyticsMetric, Dict[str, Any]]
    key_insights: List[str]
    recommendations: List[str]
    alerts_generated: List[AnalyticsAlert]
    generation_timestamp: datetime
    data_sources: List[str]

class BlockchainAnalytics:
    """    Advanced blockchain analytics engine providing comprehensive insights
    into platform performance, security, and business intelligence.
    """    
    def __init__(self, config: AnalyticsConfig):
        """        Initialize blockchain analytics system.
        
        Args:
            config: Analytics configuration
        """        self.config = config
        self.metric_data: Dict[AnalyticsMetric, List[MetricDataPoint]] = defaultdict(list)
        self.alerts: List[AnalyticsAlert] = []
        self.ml_models: Dict[str, Any] = {}
        self.running_tasks: List[asyncio.Task] = []
        self._initialize_ml_models()
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for analytics."""        if not self.config.ml_models_enabled:
            return
        
        try:
            # Fraud detection model
            self.ml_models['fraud_detector'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Anomaly detection for transactions
            self.ml_models['transaction_anomaly'] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            # Performance prediction model
            self.ml_models['performance_predictor'] = StandardScaler()
            
            logger.info("Initialized ML models for blockchain analytics")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def start_monitoring(self) -> None:
        """Start continuous analytics monitoring."""        try:
            for metric in self.config.enabled_metrics:
                interval = self.config.update_intervals.get(metric, 60)
                task = asyncio.create_task(
                    self._monitor_metric(metric, interval)
                )
                self.running_tasks.append(task)
            
            # Start alert processing
            alert_task = asyncio.create_task(self._process_alerts())
            self.running_tasks.append(alert_task)
            
            logger.info("Started blockchain analytics monitoring")
            
        except Exception as e:
            logger.error(f"Failed to start analytics monitoring: {e}")
    
    async def _monitor_metric(
        self, 
        metric: AnalyticsMetric, 
        interval: int
    ) -> None:
        """Monitor a specific metric continuously."""        while True:
            try:
                data_point = await self._collect_metric_data(metric)
                if data_point:
                    self.metric_data[metric].append(data_point)
                    await self._check_alert_conditions(metric, data_point)
                
                # Clean old data
                await self._cleanup_old_data(metric)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error monitoring {metric.value}: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metric_data(
        self, 
        metric: AnalyticsMetric
    ) -> Optional[MetricDataPoint]:
        """Collect data for a specific metric."""        try:
            if metric == AnalyticsMetric.TRANSACTION_VOLUME:
                return await self._collect_transaction_volume()
            elif metric == AnalyticsMetric.REVENUE_PERFORMANCE:
                return await self._collect_revenue_performance()
            elif metric == AnalyticsMetric.PROTECTION_EFFECTIVENESS:
                return await self._collect_protection_effectiveness()
            elif metric == AnalyticsMetric.USER_ENGAGEMENT:
                return await self._collect_user_engagement()
            elif metric == AnalyticsMetric.NETWORK_HEALTH:
                return await self._collect_network_health()
            elif metric == AnalyticsMetric.FRAUD_DETECTION:
                return await self._collect_fraud_metrics()
            elif metric == AnalyticsMetric.COMPLIANCE_STATUS:
                return await self._collect_compliance_status()
            elif metric == AnalyticsMetric.MARKET_TRENDS:
                return await self._collect_market_trends()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to collect data for {metric.value}: {e}")
            return None
    
    async def _collect_transaction_volume(self) -> MetricDataPoint:
        """Collect blockchain transaction volume metrics."""        # Mock implementation - in production, would query blockchain nodes
        current_time = datetime.utcnow()
        
        # Simulate transaction volume calculation
        volume_data = {
            "total_transactions": np.random.randint(1000, 5000),
            "successful_transactions": np.random.randint(950, 4900),
            "failed_transactions": np.random.randint(0, 100),
            "average_gas_price": np.random.uniform(10, 50),
            "network_congestion": np.random.uniform(0, 1)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.TRANSACTION_VOLUME,
            timestamp=current_time,
            value=volume_data["total_transactions"],
            metadata=volume_data
        )
    
    async def _collect_revenue_performance(self) -> MetricDataPoint:
        """Collect revenue performance metrics."""        current_time = datetime.utcnow()
        
        revenue_data = {
            "total_revenue_24h": np.random.uniform(1000, 10000),
            "royalty_payments_24h": np.random.uniform(500, 5000),
            "platform_fees_24h": np.random.uniform(100, 1000),
            "average_revenue_per_user": np.random.uniform(10, 100),
            "revenue_growth_rate": np.random.uniform(-5, 15)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.REVENUE_PERFORMANCE,
            timestamp=current_time,
            value=revenue_data["total_revenue_24h"],
            metadata=revenue_data
        )
    
    async def _collect_protection_effectiveness(self) -> MetricDataPoint:
        """Collect content protection effectiveness metrics."""        current_time = datetime.utcnow()
        
        protection_data = {
            "content_items_protected": np.random.randint(1000, 5000),
            "infringement_detected": np.random.randint(10, 100),
            "takedown_success_rate": np.random.uniform(0.8, 0.98),
            "false_positive_rate": np.random.uniform(0.01, 0.05),
            "average_detection_time_hours": np.random.uniform(0.5, 24)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.PROTECTION_EFFECTIVENESS,
            timestamp=current_time,
            value=protection_data["takedown_success_rate"],
            metadata=protection_data
        )
    
    async def _collect_user_engagement(self) -> MetricDataPoint:
        """Collect user engagement metrics."""        current_time = datetime.utcnow()
        
        engagement_data = {
            "active_users_24h": np.random.randint(500, 2000),
            "new_registrations_24h": np.random.randint(10, 100),
            "content_uploads_24h": np.random.randint(100, 1000),
            "average_session_duration_minutes": np.random.uniform(15, 60),
            "user_retention_rate": np.random.uniform(0.7, 0.95)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.USER_ENGAGEMENT,
            timestamp=current_time,
            value=engagement_data["active_users_24h"],
            metadata=engagement_data
        )
    
    async def _collect_network_health(self) -> MetricDataPoint:
        """Collect blockchain network health metrics."""        current_time = datetime.utcnow()
        
        health_data = {
            "node_connectivity": np.random.uniform(0.95, 1.0),
            "average_block_time": np.random.uniform(2, 15),
            "network_hashrate": np.random.uniform(100000, 500000),
            "mempool_size": np.random.randint(1000, 10000),
            "sync_status": np.random.uniform(0.98, 1.0)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.NETWORK_HEALTH,
            timestamp=current_time,
            value=health_data["node_connectivity"],
            metadata=health_data
        )
    
    async def _collect_fraud_metrics(self) -> MetricDataPoint:
        """Collect fraud detection metrics."""        current_time = datetime.utcnow()
        
        fraud_data = {
            "suspicious_transactions": np.random.randint(0, 50),
            "confirmed_fraud_cases": np.random.randint(0, 10),
            "false_positive_rate": np.random.uniform(0.01, 0.05),
            "fraud_prevention_rate": np.random.uniform(0.95, 0.99),
            "average_investigation_time_hours": np.random.uniform(1, 48)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.FRAUD_DETECTION,
            timestamp=current_time,
            value=fraud_data["fraud_prevention_rate"],
            metadata=fraud_data
        )
    
    async def _collect_compliance_status(self) -> MetricDataPoint:
        """Collect compliance monitoring metrics."""        current_time = datetime.utcnow()
        
        compliance_data = {
            "kyc_completion_rate": np.random.uniform(0.8, 0.95),
            "aml_checks_passed": np.random.randint(950, 1000),
            "regulatory_violations": np.random.randint(0, 5),
            "audit_trail_completeness": np.random.uniform(0.95, 1.0),
            "data_privacy_compliance": np.random.uniform(0.9, 1.0)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.COMPLIANCE_STATUS,
            timestamp=current_time,
            value=compliance_data["kyc_completion_rate"],
            metadata=compliance_data
        )
    
    async def _collect_market_trends(self) -> MetricDataPoint:
        """Collect market trends and intelligence."""        current_time = datetime.utcnow()
        
        market_data = {
            "nft_market_volume": np.random.uniform(10000, 100000),
            "average_nft_price": np.random.uniform(0.1, 10),
            "creator_economy_growth": np.random.uniform(-5, 20),
            "platform_market_share": np.random.uniform(0.05, 0.3),
            "competitor_activity_score": np.random.uniform(0.3, 0.8)
        }
        
        return MetricDataPoint(
            metric_type=AnalyticsMetric.MARKET_TRENDS,
            timestamp=current_time,
            value=market_data["nft_market_volume"],
            metadata=market_data
        )
    
    async def _check_alert_conditions(
        self, 
        metric: AnalyticsMetric, 
        data_point: MetricDataPoint
    ) -> None:
        """Check if metric data point triggers any alerts."""        try:
            threshold_key = f"{metric.value}_threshold"
            threshold = self.config.alert_thresholds.get(threshold_key)
            
            if threshold is None:
                return
            
            # Check if value exceeds threshold
            should_alert = False
            severity = AlertSeverity.INFO
            
            if isinstance(data_point.value, (int, float)):
                if metric in [
                    AnalyticsMetric.FRAUD_DETECTION,
                    AnalyticsMetric.NETWORK_HEALTH
                ]:
                    # For these metrics, lower values are bad
                    if data_point.value < threshold:
                        should_alert = True
                        severity = AlertSeverity.WARNING if data_point.value > threshold * 0.8 else AlertSeverity.CRITICAL
                else:
                    # For most metrics, higher values trigger alerts
                    if data_point.value > threshold:
                        should_alert = True
                        severity = AlertSeverity.WARNING if data_point.value < threshold * 1.5 else AlertSeverity.CRITICAL
            
            if should_alert:
                alert = AnalyticsAlert(
                    alert_id=str(uuid.uuid4()),
                    metric_type=metric,
                    severity=severity,
                    title=f"{metric.value.replace('_', ' ').title()} Alert",
                    description=f"Metric {metric.value} value {data_point.value} exceeds threshold {threshold}",
                    threshold_value=threshold,
                    actual_value=float(data_point.value),
                    timestamp=datetime.utcnow(),
                    recommended_actions=self._get_recommended_actions(metric, severity)
                )
                
                self.alerts.append(alert)
                logger.warning(f"Generated alert: {alert.title}")
                
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
    
    def _get_recommended_actions(
        self, 
        metric: AnalyticsMetric, 
        severity: AlertSeverity
    ) -> List[str]:
        """Get recommended actions for metric alerts."""        actions = []
        
        if metric == AnalyticsMetric.FRAUD_DETECTION:
            actions.extend([
                "Review recent transactions for suspicious patterns",
                "Increase fraud detection sensitivity",
                "Contact security team for investigation"
            ])
        elif metric == AnalyticsMetric.NETWORK_HEALTH:
            actions.extend([
                "Check blockchain node connectivity",
                "Monitor network congestion",
                "Consider scaling infrastructure"
            ])
        elif metric == AnalyticsMetric.REVENUE_PERFORMANCE:
            actions.extend([
                "Analyze revenue trends and patterns",
                "Review pricing strategy",
                "Check for technical issues affecting payments"
            ])
        
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.URGENT]:
            actions.insert(0, "Immediate attention required")
        
        return actions
    
    async def _process_alerts(self) -> None:
        """Process and manage analytics alerts."""        while True:
            try:
                # Clean up old alerts
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.alerts = [
                    alert for alert in self.alerts 
                    if alert.timestamp > cutoff_time
                ]
                
                # Send notifications for critical alerts
                critical_alerts = [
                    alert for alert in self.alerts 
                    if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.URGENT]
                    and alert.timestamp > datetime.utcnow() - timedelta(minutes=5)
                ]
                
                for alert in critical_alerts:
                    await self._send_alert_notification(alert)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(60)
    
    async def _send_alert_notification(self, alert: AnalyticsAlert) -> None:
        """Send notification for critical alerts."""        # Mock implementation - in production, would send to notification service
        logger.critical(
            f"CRITICAL ALERT: {alert.title} - {alert.description}"
        )
    
    async def _cleanup_old_data(self, metric: AnalyticsMetric) -> None:
        """Clean up old metric data based on retention policy."""        cutoff_time = datetime.utcnow() - timedelta(days=self.config.data_retention_days)
        
        self.metric_data[metric] = [
            dp for dp in self.metric_data[metric]
            if dp.timestamp > cutoff_time
        ]
    
    def get_metric_summary(
        self, 
        metric: AnalyticsMetric, 
        time_frame: TimeFrame = TimeFrame.DAILY
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric over a time frame."""        try:
            # Calculate time range
            now = datetime.utcnow()
            if time_frame == TimeFrame.HOURLY:
                start_time = now - timedelta(hours=1)
            elif time_frame == TimeFrame.DAILY:
                start_time = now - timedelta(days=1)
            elif time_frame == TimeFrame.WEEKLY:
                start_time = now - timedelta(weeks=1)
            elif time_frame == TimeFrame.MONTHLY:
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)
            
            # Filter data points
            data_points = [
                dp for dp in self.metric_data[metric]
                if dp.timestamp >= start_time
            ]
            
            if not data_points:
                return {"error": "No data available for the specified time frame"}
            
            # Extract values
            values = [
                float(dp.value) for dp in data_points 
                if isinstance(dp.value, (int, float))
            ]
            
            if not values:
                return {"error": "No numeric values available"}
            
            # Calculate statistics
            summary = {
                "metric": metric.value,
                "time_frame": time_frame.value,
                "data_points": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "latest_value": values[-1],
                "trend": self._calculate_trend(values)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate metric summary: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metric values."""        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation based on first and last quartile
        q1_end = len(values) // 4
        q4_start = 3 * len(values) // 4
        
        if q1_end == q4_start:
            return "stable"
        
        q1_avg = statistics.mean(values[:q1_end]) if q1_end > 0 else values[0]
        q4_avg = statistics.mean(values[q4_start:])
        
        change_percent = ((q4_avg - q1_avg) / q1_avg) * 100 if q1_avg != 0 else 0
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    async def generate_analytics_report(
        self, 
        report_type: str = "comprehensive",
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report."""        try:
            if time_period is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
                time_period = (start_time, end_time)
            
            # Collect metrics summaries
            metrics_summary = {}
            for metric in self.config.enabled_metrics:
                summary = self.get_metric_summary(metric, TimeFrame.WEEKLY)
                metrics_summary[metric] = summary
            
            # Generate insights and recommendations
            insights = self._generate_insights(metrics_summary)
            recommendations = self._generate_recommendations(metrics_summary)
            
            # Get recent alerts
            recent_alerts = [
                alert for alert in self.alerts
                if time_period[0] <= alert.timestamp <= time_period[1]
            ]
            
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                report_type=report_type,
                time_period=time_period,
                metrics_summary=metrics_summary,
                key_insights=insights,
                recommendations=recommendations,
                alerts_generated=recent_alerts,
                generation_timestamp=datetime.utcnow(),
                data_sources=["blockchain_nodes", "application_metrics", "ml_models"]
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            raise
    
    def _generate_insights(self, metrics_summary: Dict[AnalyticsMetric, Dict[str, Any]]) -> List[str]:
        """Generate key insights from metrics data."""        insights = []
        
        for metric, summary in metrics_summary.items():
            if "error" in summary:
                continue
                
            trend = summary.get("trend", "unknown")
            metric_name = metric.value.replace("_", " ").title()
            
            if trend == "increasing":
                insights.append(f"{metric_name} shows positive growth trend")
            elif trend == "decreasing":
                insights.append(f"{metric_name} shows declining trend - investigation recommended")
            
            # Specific insights based on metric type
            if metric == AnalyticsMetric.FRAUD_DETECTION:
                fraud_rate = summary.get("mean", 0)
                if fraud_rate > 0.95:
                    insights.append("Fraud detection performance is excellent")
                elif fraud_rate < 0.9:
                    insights.append("Fraud detection performance needs attention")
        
        return insights
    
    def _generate_recommendations(self, metrics_summary: Dict[AnalyticsMetric, Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations from metrics data."""        recommendations = []
        
        for metric, summary in metrics_summary.items():
            if "error" in summary:
                continue
            
            trend = summary.get("trend", "unknown")
            std_dev = summary.get("std_dev", 0)
            
            # High volatility recommendations
            if std_dev > summary.get("mean", 0) * 0.5:
                metric_name = metric.value.replace("_", " ").title()
                recommendations.append(
                    f"Consider implementing stability measures for {metric_name} - high volatility detected"
                )
            
            # Specific recommendations based on metric type
            if metric == AnalyticsMetric.REVENUE_PERFORMANCE and trend == "decreasing":
                recommendations.append("Review pricing strategy and user acquisition efforts")
            
            if metric == AnalyticsMetric.USER_ENGAGEMENT and trend == "decreasing":
                recommendations.append("Implement user retention strategies and improve user experience")
        
        return recommendations
    
    async def stop_monitoring(self) -> None:
        """Stop analytics monitoring and clean up resources."""        try:
            for task in self.running_tasks:
                task.cancel()
            
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
            self.running_tasks.clear()
            
            logger.info("Stopped blockchain analytics monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping analytics monitoring: {e}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[AnalyticsAlert]:
        """Get active alerts, optionally filtered by severity."""        alerts = [
            alert for alert in self.alerts
            if alert.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def get_fraud_analysis(self) -> Dict[str, Any]:
        """Get specialized fraud analysis using ML models."""        if not self.config.fraud_detection_enabled:
            return {"error": "Fraud detection not enabled"}
        
        try:
            # Mock fraud analysis - in production, would use real transaction data
            fraud_analysis = {
                "risk_score": np.random.uniform(0, 1),
                "anomalous_transactions": np.random.randint(0, 10),
                "patterns_detected": [
                    "Unusual transaction timing",
                    "Suspicious amount patterns"
                ],
                "recommended_actions": [
                    "Increase monitoring for flagged accounts",
                    "Review transaction approval thresholds"
                ]
            }
            
            return fraud_analysis
            
        except Exception as e:
            logger.error(f"Failed to generate fraud analysis: {e}")
            return {"error": str(e)}
