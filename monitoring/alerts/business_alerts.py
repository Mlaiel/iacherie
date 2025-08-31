"""🚨 Business Alerts Module - Revenue & User Experience Monitoring
===============================================================

Advanced business intelligence alerts for revenue monitoring and user experience tracking.
Integrates with existing revenue tracking and extends monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

from .intelligent_alert_manager import (
    IntelligentAlertManager, AlertCategory, AlertSeverity, 
    AlertType, AlertRule, IntelligentAlert
)

logger = logging.getLogger(__name__)


class BusinessMetric(Enum):
    """Business metrics for monitoring"""    REVENUE = "revenue"
    USER_ENGAGEMENT = "user_engagement"
    CONVERSION_RATE = "conversion_rate"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    PAYMENT_SUCCESS_RATE = "payment_success_rate"
    USER_RETENTION = "user_retention"
    CONTENT_UPLOAD_RATE = "content_upload_rate"


@dataclass
class BusinessMetrics:
    """Business metrics data structure"""    timestamp: datetime
    current_revenue: float
    previous_revenue: float
    daily_revenue: List[float]
    weekly_revenue: List[float]
    active_users: int
    new_users: int
    user_retention_rate: float
    avg_session_duration: float
    bounce_rate: float
    conversion_rate: float
    payment_success_rate: float
    content_uploads: int
    user_satisfaction_score: float
    support_tickets: int
    churn_rate: float


class BusinessAlertManager:
    """    Advanced business alert management for revenue and user experience monitoring
    
    Features:
    - Revenue anomaly detection with trend analysis
    - User experience degradation monitoring
    - Customer satisfaction alerts
    - Payment processing alerts
    - User engagement tracking
    - Business KPI thresholds
    """    
    def __init__(self, alert_manager: IntelligentAlertManager):
        """Initialize business alert manager"""        self.alert_manager = alert_manager
        self.business_metrics_history: List[BusinessMetrics] = []
        self.revenue_baselines: Dict[str, float] = {}
        self.engagement_baselines: Dict[str, float] = {}
        
        # Business alert thresholds
        self.thresholds = {
            "revenue_drop_critical": 0.25,  # 25% drop
            "revenue_drop_warning": 0.15,   # 15% drop
            "user_experience_critical": 0.30,  # 30% degradation
            "user_experience_warning": 0.20,   # 20% degradation
            "engagement_drop_critical": 0.40,  # 40% drop
            "engagement_drop_warning": 0.25,   # 25% drop
            "payment_failure_critical": 0.10,  # 10% failure rate
            "payment_failure_warning": 0.05,   # 5% failure rate
            "satisfaction_critical": 3.0,      # Score below 3.0
            "satisfaction_warning": 3.5,       # Score below 3.5
        }
        
        self._initialize_business_rules()
        logger.info("BusinessAlertManager initialized")
    
    def _initialize_business_rules(self):
        """Initialize business-specific alert rules"""        
        # Revenue Drop Alert - Critical
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="business_revenue_drop_critical",
            name="Critical Revenue Drop",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.REVENUE_DROP,
            severity=AlertSeverity.CRITICAL,
            expression="revenue_drop_percentage > 25",
            threshold={
                "percentage_drop": 25,
                "minimum_amount": 1000,
                "time_period": "1h"
            },
            duration="15m",
            escalation_levels=[
                {"level": 1, "delay": "10m", "channels": ["email", "slack", "phone"]},
                {"level": 2, "delay": "30m", "channels": ["email", "slack", "phone", "pagerduty"]}
            ],
            correlation_rules=["business_payment_failure", "technical_service_down"]
        ))
        
        # Revenue Anomaly Detection
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="business_revenue_anomaly",
            name="Revenue Anomaly Detected",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.REVENUE_ANOMALY,
            severity=AlertSeverity.WARNING,
            expression="revenue_anomaly_score > 0.7",
            threshold={
                "anomaly_score": 0.7,
                "confidence_level": 0.95,
                "historical_window": "7d"
            },
            duration="30m",
            escalation_levels=[
                {"level": 1, "delay": "1h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "4h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # User Experience Degradation
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="business_user_experience_critical",
            name="Critical User Experience Degradation",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.USER_EXPERIENCE_DEGRADATION,
            severity=AlertSeverity.CRITICAL,
            expression="ux_degradation_score > 0.30",
            threshold={
                "degradation_threshold": 0.30,
                "metrics": ["bounce_rate", "session_duration", "satisfaction_score"],
                "time_window": "1h"
            },
            duration="20m",
            escalation_levels=[
                {"level": 1, "delay": "15m", "channels": ["email", "slack"]},
                {"level": 2, "delay": "45m", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        # Payment Processing Failures
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="business_payment_failure_critical",
            name="Critical Payment Processing Failures",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.PAYMENT_FAILURE,
            severity=AlertSeverity.CRITICAL,
            expression="payment_failure_rate > 0.10",
            threshold={
                "failure_rate": 0.10,
                "minimum_transactions": 10,
                "time_window": "15m"
            },
            duration="5m",
            escalation_levels=[
                {"level": 1, "delay": "5m", "channels": ["email", "slack", "phone"]},
                {"level": 2, "delay": "15m", "channels": ["email", "slack", "phone", "pagerduty"]}
            ]
        ))
        
        # User Engagement Drop
        self.alert_manager.add_alert_rule(AlertRule(
            rule_id="business_engagement_drop",
            name="Significant User Engagement Drop",
            category=AlertCategory.BUSINESS,
            alert_type=AlertType.ENGAGEMENT_DROP,
            severity=AlertSeverity.WARNING,
            expression="engagement_drop_percentage > 25",
            threshold={
                "drop_percentage": 25,
                "metrics": ["active_users", "session_duration", "content_uploads"],
                "comparison_period": "24h"
            },
            duration="1h",
            escalation_levels=[
                {"level": 1, "delay": "2h", "channels": ["email", "slack"]},
                {"level": 2, "delay": "6h", "channels": ["email", "slack", "phone"]}
            ]
        ))
        
        logger.info("Business alert rules initialized")
    
    async def evaluate_business_metrics(self, metrics: BusinessMetrics) -> List[IntelligentAlert]:
        """Evaluate business metrics and trigger alerts"""        triggered_alerts = []
        
        # Store metrics for trend analysis
        self.business_metrics_history.append(metrics)
        
        # Keep only last 30 days of history
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        self.business_metrics_history = [
            m for m in self.business_metrics_history 
            if m.timestamp >= cutoff_date
        ]
        
        try:
            # Evaluate revenue alerts
            revenue_alerts = await self._evaluate_revenue_alerts(metrics)
            triggered_alerts.extend(revenue_alerts)
            
            # Evaluate user experience alerts
            ux_alerts = await self._evaluate_user_experience_alerts(metrics)
            triggered_alerts.extend(ux_alerts)
            
            # Evaluate payment processing alerts
            payment_alerts = await self._evaluate_payment_alerts(metrics)
            triggered_alerts.extend(payment_alerts)
            
            # Evaluate engagement alerts
            engagement_alerts = await self._evaluate_engagement_alerts(metrics)
            triggered_alerts.extend(engagement_alerts)
            
            logger.debug(f"Evaluated business metrics, triggered {len(triggered_alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error evaluating business metrics: {e}")
        
        return triggered_alerts
    
    async def _evaluate_revenue_alerts(self, metrics: BusinessMetrics) -> List[IntelligentAlert]:
        """Evaluate revenue-related alerts"""        alerts = []
        
        try:
            # Calculate revenue drop percentage
            if metrics.previous_revenue > 0:
                revenue_drop = (metrics.previous_revenue - metrics.current_revenue) / metrics.previous_revenue
                revenue_drop_percentage = revenue_drop * 100
                
                # Critical revenue drop
                if revenue_drop_percentage >= self.thresholds["revenue_drop_critical"]:
                    alert_metrics = {
                        "current_revenue": metrics.current_revenue,
                        "previous_revenue": metrics.previous_revenue,
                        "revenue_drop_percentage": revenue_drop_percentage,
                        "drop_amount": metrics.previous_revenue - metrics.current_revenue
                    }
                    
                    alert = await self.alert_manager._create_alert(
                        self.alert_manager.alert_rules["business_revenue_drop_critical"],
                        alert_metrics
                    )
                    alerts.append(alert)
                
                # Revenue anomaly detection
                anomaly_score = await self._calculate_revenue_anomaly_score(metrics)
                if anomaly_score > 0.7:
                    alert_metrics = {
                        "revenue_anomaly_score": anomaly_score,
                        "current_revenue": metrics.current_revenue,
                        "expected_revenue": await self._get_expected_revenue(metrics.timestamp),
                        "historical_data": metrics.daily_revenue[-7:] if len(metrics.daily_revenue) >= 7 else metrics.daily_revenue
                    }
                    
                    alert = await self.alert_manager._create_alert(
                        self.alert_manager.alert_rules["business_revenue_anomaly"],
                        alert_metrics
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating revenue alerts: {e}")
        
        return alerts
    
    async def _evaluate_user_experience_alerts(self, metrics: BusinessMetrics) -> List[IntelligentAlert]:
        """Evaluate user experience alerts"""        alerts = []
        
        try:
            # Calculate UX degradation score
            ux_score = await self._calculate_ux_degradation_score(metrics)
            
            if ux_score >= self.thresholds["user_experience_critical"]:
                alert_metrics = {
                    "ux_degradation_score": ux_score,
                    "bounce_rate": metrics.bounce_rate,
                    "avg_session_duration": metrics.avg_session_duration,
                    "user_satisfaction_score": metrics.user_satisfaction_score,
                    "support_tickets": metrics.support_tickets
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["business_user_experience_critical"],
                    alert_metrics
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating user experience alerts: {e}")
        
        return alerts
    
    async def _evaluate_payment_alerts(self, metrics: BusinessMetrics) -> List[IntelligentAlert]:
        """Evaluate payment processing alerts"""        alerts = []
        
        try:
            # Check payment failure rate
            payment_failure_rate = 1.0 - metrics.payment_success_rate
            
            if payment_failure_rate >= self.thresholds["payment_failure_critical"]:
                alert_metrics = {
                    "payment_failure_rate": payment_failure_rate,
                    "payment_success_rate": metrics.payment_success_rate,
                    "timestamp": metrics.timestamp
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["business_payment_failure_critical"],
                    alert_metrics
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating payment alerts: {e}")
        
        return alerts
    
    async def _evaluate_engagement_alerts(self, metrics: BusinessMetrics) -> List[IntelligentAlert]:
        """Evaluate user engagement alerts"""        alerts = []
        
        try:
            # Calculate engagement drop
            engagement_drop = await self._calculate_engagement_drop(metrics)
            
            if engagement_drop >= self.thresholds["engagement_drop_warning"]:
                alert_metrics = {
                    "engagement_drop_percentage": engagement_drop,
                    "active_users": metrics.active_users,
                    "avg_session_duration": metrics.avg_session_duration,
                    "content_uploads": metrics.content_uploads,
                    "user_retention_rate": metrics.user_retention_rate
                }
                
                alert = await self.alert_manager._create_alert(
                    self.alert_manager.alert_rules["business_engagement_drop"],
                    alert_metrics
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error evaluating engagement alerts: {e}")
        
        return alerts
    
    async def _calculate_revenue_anomaly_score(self, metrics: BusinessMetrics) -> float:
        """Calculate revenue anomaly score using statistical analysis"""        try:
            if len(self.business_metrics_history) < 7:
                return 0.0  # Not enough data for anomaly detection
            
            # Get historical revenue data
            historical_revenues = [m.current_revenue for m in self.business_metrics_history[-30:]]
            
            if len(historical_revenues) < 3:
                return 0.0
            
            # Calculate statistical measures
            mean_revenue = statistics.mean(historical_revenues)
            std_revenue = statistics.stdev(historical_revenues) if len(historical_revenues) > 1 else 0
            
            if std_revenue == 0:
                return 0.0
            
            # Calculate Z-score
            z_score = abs((metrics.current_revenue - mean_revenue) / std_revenue)
            
            # Convert Z-score to anomaly score (0-1)
            anomaly_score = min(z_score / 3.0, 1.0)  # Normalize to 0-1 range
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Error calculating revenue anomaly score: {e}")
            return 0.0
    
    async def _calculate_ux_degradation_score(self, metrics: BusinessMetrics) -> float:
        """Calculate user experience degradation score"""        try:
            if len(self.business_metrics_history) < 3:
                return 0.0  # Not enough data
            
            # Get baseline UX metrics (average of last 7 days)
            recent_metrics = self.business_metrics_history[-7:]
            
            if len(recent_metrics) < 3:
                return 0.0
            
            # Calculate baselines
            baseline_bounce_rate = statistics.mean([m.bounce_rate for m in recent_metrics])
            baseline_session_duration = statistics.mean([m.avg_session_duration for m in recent_metrics])
            baseline_satisfaction = statistics.mean([m.user_satisfaction_score for m in recent_metrics])
            
            # Calculate degradation factors
            bounce_rate_increase = (metrics.bounce_rate - baseline_bounce_rate) / baseline_bounce_rate if baseline_bounce_rate > 0 else 0
            session_duration_decrease = (baseline_session_duration - metrics.avg_session_duration) / baseline_session_duration if baseline_session_duration > 0 else 0
            satisfaction_decrease = (baseline_satisfaction - metrics.user_satisfaction_score) / baseline_satisfaction if baseline_satisfaction > 0 else 0
            
            # Weighted degradation score
            degradation_score = (
                bounce_rate_increase * 0.3 +
                session_duration_decrease * 0.4 +
                satisfaction_decrease * 0.3
            )
            
            return max(0.0, min(1.0, degradation_score))
            
        except Exception as e:
            logger.error(f"Error calculating UX degradation score: {e}")
            return 0.0
    
    async def _calculate_engagement_drop(self, metrics: BusinessMetrics) -> float:
        """Calculate user engagement drop percentage"""        try:
            if len(self.business_metrics_history) < 2:
                return 0.0
            
            # Compare with previous day
            previous_metrics = self.business_metrics_history[-2]
            
            # Calculate engagement metrics change
            user_change = (previous_metrics.active_users - metrics.active_users) / previous_metrics.active_users if previous_metrics.active_users > 0 else 0
            session_change = (previous_metrics.avg_session_duration - metrics.avg_session_duration) / previous_metrics.avg_session_duration if previous_metrics.avg_session_duration > 0 else 0
            upload_change = (previous_metrics.content_uploads - metrics.content_uploads) / previous_metrics.content_uploads if previous_metrics.content_uploads > 0 else 0
            
            # Weighted engagement drop
            engagement_drop = (user_change * 0.4 + session_change * 0.3 + upload_change * 0.3) * 100
            
            return max(0.0, engagement_drop)
            
        except Exception as e:
            logger.error(f"Error calculating engagement drop: {e}")
            return 0.0
    
    async def _get_expected_revenue(self, timestamp: datetime) -> float:
        """Get expected revenue based on historical trends"""        try:
            if len(self.business_metrics_history) < 7:
                return 0.0
            
            # Simple trend analysis - could be enhanced with ML models
            recent_revenues = [m.current_revenue for m in self.business_metrics_history[-7:]]
            return statistics.mean(recent_revenues)
            
        except Exception as e:
            logger.error(f"Error calculating expected revenue: {e}")
            return 0.0
    
    async def get_business_alert_summary(self) -> Dict[str, Any]:
        """Get business alert summary and insights"""        try:
            if not self.business_metrics_history:
                return {"error": "No business metrics available"}
            
            latest_metrics = self.business_metrics_history[-1]
            
            # Calculate trends
            revenue_trend = await self._calculate_revenue_trend()
            engagement_trend = await self._calculate_engagement_trend()
            
            return {
                "timestamp": latest_metrics.timestamp.isoformat(),
                "current_revenue": latest_metrics.current_revenue,
                "revenue_trend": revenue_trend,
                "user_engagement": {
                    "active_users": latest_metrics.active_users,
                    "trend": engagement_trend,
                    "satisfaction_score": latest_metrics.user_satisfaction_score
                },
                "payment_health": {
                    "success_rate": latest_metrics.payment_success_rate,
                    "status": "healthy" if latest_metrics.payment_success_rate > 0.95 else "degraded"
                },
                "alert_thresholds": self.thresholds,
                "metrics_history_days": len(self.business_metrics_history)
            }
            
        except Exception as e:
            logger.error(f"Error generating business alert summary: {e}")
            return {"error": str(e)}
    
    async def _calculate_revenue_trend(self) -> str:
        """Calculate revenue trend direction"""        try:
            if len(self.business_metrics_history) < 3:
                return "insufficient_data"
            
            recent_revenues = [m.current_revenue for m in self.business_metrics_history[-3:]]
            
            if recent_revenues[2] > recent_revenues[1] > recent_revenues[0]:
                return "increasing"
            elif recent_revenues[2] < recent_revenues[1] < recent_revenues[0]:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating revenue trend: {e}")
            return "unknown"
    
    async def _calculate_engagement_trend(self) -> str:
        """Calculate engagement trend direction"""        try:
            if len(self.business_metrics_history) < 3:
                return "insufficient_data"
            
            recent_users = [m.active_users for m in self.business_metrics_history[-3:]]
            
            if recent_users[2] > recent_users[1] > recent_users[0]:
                return "increasing"
            elif recent_users[2] < recent_users[1] < recent_users[0]:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating engagement trend: {e}")
            return "unknown"


# Export the main class
__all__ = ["BusinessAlertManager", "BusinessMetrics", "BusinessMetric"]