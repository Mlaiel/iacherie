"""🚨 Revenue Anomaly Alert System
=============================

Intelligent revenue anomaly detection and alerting for the Ainflue platform.
Detects unusual revenue patterns, drops, spikes, and fraud indicators.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import statistics
import json

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of revenue anomalies"""
    SUDDEN_DROP = "sudden_drop"
    SUDDEN_SPIKE = "sudden_spike"
    GRADUAL_DECLINE = "gradual_decline"
    UNUSUAL_PATTERN = "unusual_pattern"
    FRAUD_INDICATOR = "fraud_indicator"
    ZERO_REVENUE = "zero_revenue"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class RevenueAlert:
    """Revenue alert data"""
    alert_id: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    current_value: float
    expected_value: float
    deviation_percentage: float
    timestamp: datetime
    details: Dict[str, Any]
    recommended_actions: List[str]


class RevenueAnomalyDetector:
    """
    Advanced revenue anomaly detection system
    
    Features:
    - Statistical anomaly detection
    - Machine learning pattern recognition
    - Real-time monitoring
    - Escalation management
    - Automated response suggestions
    """
    
    def __init__(self, revenue_tracker):
        """Initialize anomaly detector"""
        self.revenue_tracker = revenue_tracker
        self.historical_data = []
        self.alert_history = []
        
        # Detection thresholds
        self.thresholds = {
            "drop_threshold": 30.0,  # 30% drop
            "spike_threshold": 200.0,  # 200% spike
            "zero_revenue_hours": 4,  # 4 hours without revenue
            "fraud_velocity": 10,  # 10 transactions per minute
            "minimum_samples": 7  # Minimum data points for analysis
        }
        
        logger.info("RevenueAnomalyDetector initialized")
    
    async def check_anomalies(self) -> List[RevenueAlert]:
        """Check for revenue anomalies"""
        alerts = []
        
        try:
            # Get recent revenue data
            analytics = await self.revenue_tracker.get_revenue_analytics(period_days=7)
            
            if "error" in analytics:
                return alerts
            
            # Check for different types of anomalies
            alerts.extend(await self._check_sudden_changes(analytics))
            alerts.extend(await self._check_zero_revenue())
            alerts.extend(await self._check_fraud_indicators())
            alerts.extend(await self._check_gradual_decline(analytics))
            
            # Store alerts
            self.alert_history.extend(alerts)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking anomalies: {e}")
            return []
    
    async def _check_sudden_changes(self, analytics: Dict[str, Any]) -> List[RevenueAlert]:
        """Check for sudden revenue changes"""
        alerts = []
        
        try:
            trends = analytics.get("trends", {})
            growth_rate = trends.get("growth_rate_percentage", 0)
            
            current_revenue = analytics.get("total_revenue", {}).get("amount", 0)
            previous_revenue = trends.get("previous_period_revenue", 0)
            
            if previous_revenue > 0:
                change_percentage = abs(growth_rate)
                
                # Sudden drop
                if growth_rate < -self.thresholds["drop_threshold"]:
                    alerts.append(RevenueAlert(
                        alert_id=f"drop_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        anomaly_type=AnomalyType.SUDDEN_DROP,
                        severity=AlertSeverity.CRITICAL if change_percentage > 50 else AlertSeverity.WARNING,
                        current_value=current_revenue,
                        expected_value=previous_revenue,
                        deviation_percentage=change_percentage,
                        timestamp=datetime.utcnow(),
                        details={
                            "growth_rate": growth_rate,
                            "previous_period": previous_revenue,
                            "current_period": current_revenue
                        },
                        recommended_actions=[
                            "Investigate payment processing issues",
                            "Check for technical problems affecting revenue collection",
                            "Review recent platform changes or outages",
                            "Contact major clients to ensure no issues"
                        ]
                    ))
                
                # Sudden spike (could indicate fraud or data error)
                elif growth_rate > self.thresholds["spike_threshold"]:
                    alerts.append(RevenueAlert(
                        alert_id=f"spike_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        anomaly_type=AnomalyType.SUDDEN_SPIKE,
                        severity=AlertSeverity.WARNING,
                        current_value=current_revenue,
                        expected_value=previous_revenue,
                        deviation_percentage=change_percentage,
                        timestamp=datetime.utcnow(),
                        details={
                            "growth_rate": growth_rate,
                            "previous_period": previous_revenue,
                            "current_period": current_revenue
                        },
                        recommended_actions=[
                            "Verify revenue data accuracy",
                            "Check for duplicate transactions",
                            "Investigate potential fraud",
                            "Review unusual transaction patterns"
                        ]
                    ))
            
        except Exception as e:
            logger.error(f"Error checking sudden changes: {e}")
        
        return alerts
    
    async def _check_zero_revenue(self) -> List[RevenueAlert]:
        """Check for periods of zero revenue"""
        alerts = []
        
        try:
            # Get recent events
            recent_events = [
                event for event in self.revenue_tracker.revenue_events
                if event.timestamp >= datetime.utcnow() - timedelta(hours=self.thresholds["zero_revenue_hours"])
            ]
            
            if not recent_events:
                alerts.append(RevenueAlert(
                    alert_id=f"zero_rev_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    anomaly_type=AnomalyType.ZERO_REVENUE,
                    severity=AlertSeverity.CRITICAL,
                    current_value=0,
                    expected_value=100,  # Expected minimum hourly revenue
                    deviation_percentage=100,
                    timestamp=datetime.utcnow(),
                    details={
                        "hours_without_revenue": self.thresholds["zero_revenue_hours"],
                        "last_revenue_event": self.revenue_tracker.revenue_events[-1].timestamp.isoformat() if self.revenue_tracker.revenue_events else "never"
                    },
                    recommended_actions=[
                        "Check payment gateway status",
                        "Verify platform availability",
                        "Review API endpoint health",
                        "Check for system maintenance or outages"
                    ]
                ))
            
        except Exception as e:
            logger.error(f"Error checking zero revenue: {e}")
        
        return alerts
    
    async def _check_fraud_indicators(self) -> List[RevenueAlert]:
        """Check for potential fraud indicators"""
        alerts = []
        
        try:
            # Check transaction velocity
            recent_events = [
                event for event in self.revenue_tracker.revenue_events
                if event.timestamp >= datetime.utcnow() - timedelta(minutes=1)
            ]
            
            if len(recent_events) > self.thresholds["fraud_velocity"]:
                alerts.append(RevenueAlert(
                    alert_id=f"fraud_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    anomaly_type=AnomalyType.FRAUD_INDICATOR,
                    severity=AlertSeverity.EMERGENCY,
                    current_value=len(recent_events),
                    expected_value=self.thresholds["fraud_velocity"],
                    deviation_percentage=((len(recent_events) - self.thresholds["fraud_velocity"]) / self.thresholds["fraud_velocity"]) * 100,
                    timestamp=datetime.utcnow(),
                    details={
                        "transactions_per_minute": len(recent_events),
                        "threshold": self.thresholds["fraud_velocity"],
                        "user_ids": list(set(event.user_id for event in recent_events if event.user_id))
                    },
                    recommended_actions=[
                        "Immediately review transaction patterns",
                        "Implement temporary rate limiting",
                        "Investigate suspicious user accounts",
                        "Contact fraud prevention team"
                    ]
                ))
            
        except Exception as e:
            logger.error(f"Error checking fraud indicators: {e}")
        
        return alerts
    
    async def _check_gradual_decline(self, analytics: Dict[str, Any]) -> List[RevenueAlert]:
        """Check for gradual revenue decline trends"""
        alerts = []
        
        try:
            # Get daily revenue data
            daily_revenue = analytics.get("daily_revenue", [])
            
            if len(daily_revenue) >= self.thresholds["minimum_samples"]:
                # Calculate trend
                values = [day["amount"] for day in daily_revenue[-7:]]  # Last 7 days
                
                if len(values) >= 3:
                    # Simple linear regression to detect trend
                    x_values = list(range(len(values)))
                    mean_x = statistics.mean(x_values)
                    mean_y = statistics.mean(values)
                    
                    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
                    denominator = sum((x - mean_x) ** 2 for x in x_values)
                    
                    if denominator > 0:
                        slope = numerator / denominator
                        
                        # If slope is negative and significant
                        if slope < -50:  # Losing more than 50 EUR per day on average
                            alerts.append(RevenueAlert(
                                alert_id=f"decline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                                anomaly_type=AnomalyType.GRADUAL_DECLINE,
                                severity=AlertSeverity.WARNING,
                                current_value=values[-1],
                                expected_value=values[0],
                                deviation_percentage=abs(((values[-1] - values[0]) / values[0]) * 100) if values[0] > 0 else 0,
                                timestamp=datetime.utcnow(),
                                details={
                                    "daily_decline_rate": slope,
                                    "trend_period_days": len(values),
                                    "first_value": values[0],
                                    "last_value": values[-1]
                                },
                                recommended_actions=[
                                    "Analyze customer churn patterns",
                                    "Review competitive landscape",
                                    "Investigate product/service issues",
                                    "Consider marketing campaign adjustments"
                                ]
                            ))
            
        except Exception as e:
            logger.error(f"Error checking gradual decline: {e}")
        
        return alerts


# Export classes
__all__ = [
    "RevenueAnomalyDetector",
    "RevenueAlert",
    "AnomalyType", 
    "AlertSeverity"
]