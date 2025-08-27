"""
Protection Metrics & Analytics Engine

This module provides comprehensive analytics and monitoring for content protection:
- Real-time performance metrics and KPIs
- Protection effectiveness analytics
- Revenue impact analysis
- Platform-specific protection statistics
- Advanced reporting and dashboards
- Predictive analytics using ML

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging
import uuid
import statistics
from concurrent.futures import ThreadPoolExecutor

# Data processing and analytics
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ViolationCase
from ...database.models.analytics import ProtectionMetrics, RevenueLoss, PlatformStats
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class MetricType(Enum):
    """Types of protection metrics"""
    DETECTION_RATE = "detection_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    TAKEDOWN_SUCCESS_RATE = "takedown_success_rate"
    REVENUE_RECOVERED = "revenue_recovered"
    PROTECTION_COVERAGE = "protection_coverage"
    RESPONSE_TIME = "response_time"
    VIOLATION_FREQUENCY = "violation_frequency"
    PLATFORM_EFFECTIVENESS = "platform_effectiveness"


class TimeWindow(Enum):
    """Time windows for metrics aggregation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class ProtectionKPI:
    """Key Performance Indicator for protection system"""
    name: str
    value: float
    unit: str
    target: Optional[float] = None
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    change_percentage: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformAnalytics:
    """Analytics data for specific platform"""
    platform: str
    violations_detected: int
    violations_resolved: int
    revenue_impact: Decimal
    detection_accuracy: float
    average_response_time: float
    top_violation_types: List[str] = field(default_factory=list)
    trend_data: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class ProtectionReport:
    """Comprehensive protection analytics report"""
    report_id: str
    user_id: str
    period_start: datetime
    period_end: datetime
    
    # Overall metrics
    total_violations_detected: int
    total_violations_resolved: int
    total_revenue_recovered: Decimal
    protection_effectiveness: float
    
    # KPIs
    key_metrics: List[ProtectionKPI] = field(default_factory=list)
    
    # Platform breakdown
    platform_analytics: Dict[str, PlatformAnalytics] = field(default_factory=dict)
    
    # Trends and predictions
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    predictions: Dict[str, Any] = field(default_factory=dict)
    
    # Generated at
    generated_at: datetime = field(default_factory=datetime.utcnow)


class ProtectionAnalytics:
    """
    Advanced analytics engine for content protection system
    
    Provides comprehensive metrics, KPIs, and predictive analytics
    for protection effectiveness and revenue impact.
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        logger.info("Protection analytics engine initialized")
    
    async def calculate_protection_kpis(self, user_id: str, start_date: datetime, end_date: datetime) -> List[ProtectionKPI]:
        """Calculate key protection KPIs for the specified period"""
        try:
            kpis = []
            
            # Get violation data
            violations = await self._get_violations_data(user_id, start_date, end_date)
            
            # Calculate detection rate
            detection_rate = await self._calculate_detection_rate(violations)
            kpis.append(ProtectionKPI(
                name="Detection Rate",
                value=detection_rate,
                unit="%",
                target=95.0,
                trend=await self._calculate_trend(user_id, "detection_rate", start_date)
            ))
            
            # Calculate false positive rate
            false_positive_rate = await self._calculate_false_positive_rate(violations)
            kpis.append(ProtectionKPI(
                name="False Positive Rate",
                value=false_positive_rate,
                unit="%",
                target=5.0,
                trend=await self._calculate_trend(user_id, "false_positive_rate", start_date)
            ))
            
            # Calculate takedown success rate
            takedown_success_rate = await self._calculate_takedown_success_rate(violations)
            kpis.append(ProtectionKPI(
                name="Takedown Success Rate",
                value=takedown_success_rate,
                unit="%",
                target=90.0,
                trend=await self._calculate_trend(user_id, "takedown_success_rate", start_date)
            ))
            
            # Calculate revenue recovered
            revenue_recovered = await self._calculate_revenue_recovered(user_id, start_date, end_date)
            kpis.append(ProtectionKPI(
                name="Revenue Recovered",
                value=float(revenue_recovered),
                unit="EUR",
                trend=await self._calculate_trend(user_id, "revenue_recovered", start_date)
            ))
            
            # Calculate average response time
            response_time = await self._calculate_average_response_time(violations)
            kpis.append(ProtectionKPI(
                name="Average Response Time",
                value=response_time,
                unit="hours",
                target=4.0,
                trend=await self._calculate_trend(user_id, "response_time", start_date)
            ))
            
            # Calculate protection coverage
            coverage = await self._calculate_protection_coverage(user_id)
            kpis.append(ProtectionKPI(
                name="Protection Coverage",
                value=coverage,
                unit="%",
                target=100.0
            ))
            
            logger.info(f"Calculated {len(kpis)} KPIs for user {user_id}")
            return kpis
            
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}")
            return []
    
    async def generate_platform_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, PlatformAnalytics]:
        """Generate analytics breakdown by platform"""
        try:
            platform_analytics = {}
            
            # Get violations by platform
            platform_violations = await self._get_violations_by_platform(user_id, start_date, end_date)
            
            for platform, violations in platform_violations.items():
                # Calculate platform-specific metrics
                detected = len([v for v in violations if v.get('status') != 'false_positive'])
                resolved = len([v for v in violations if v.get('status') == 'resolved'])
                
                # Calculate revenue impact
                revenue_impact = sum(
                    Decimal(str(v.get('revenue_impact', 0))) 
                    for v in violations
                )
                
                # Calculate detection accuracy
                accuracy = self._calculate_platform_accuracy(violations)
                
                # Calculate average response time
                response_times = [
                    v.get('response_time_hours', 0) 
                    for v in violations 
                    if v.get('response_time_hours')
                ]
                avg_response_time = statistics.mean(response_times) if response_times else 0.0
                
                # Get top violation types
                violation_types = [v.get('violation_type', 'unknown') for v in violations]
                top_types = self._get_top_violation_types(violation_types)
                
                # Generate trend data
                trend_data = await self._generate_platform_trends(platform, user_id, start_date, end_date)
                
                platform_analytics[platform] = PlatformAnalytics(
                    platform=platform,
                    violations_detected=detected,
                    violations_resolved=resolved,
                    revenue_impact=revenue_impact,
                    detection_accuracy=accuracy,
                    average_response_time=avg_response_time,
                    top_violation_types=top_types,
                    trend_data=trend_data
                )
            
            logger.info(f"Generated analytics for {len(platform_analytics)} platforms")
            return platform_analytics
            
        except Exception as e:
            logger.error(f"Platform analytics generation failed: {e}")
            return {}
    
    async def predict_violation_trends(self, user_id: str, historical_days: int = 90, forecast_days: int = 30) -> Dict[str, Any]:
        """Predict future violation trends using ML"""
        try:
            # Get historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=historical_days)
            
            violations_data = await self._get_daily_violations_data(user_id, start_date, end_date)
            
            if len(violations_data) < 14:  # Need at least 2 weeks of data
                logger.warning("Insufficient data for trend prediction")
                return {}
            
            # Prepare data for ML
            df = pd.DataFrame(violations_data)
            df['date'] = pd.to_datetime(df['date'])
            df['day_number'] = (df['date'] - df['date'].min()).dt.days
            
            # Train models for different metrics
            predictions = {}
            
            # Predict violations count
            X = df[['day_number']].values
            y_violations = df['violations_count'].values
            
            model_violations = LinearRegression()
            model_violations.fit(X, y_violations)
            
            # Generate predictions
            future_days = np.array([[historical_days + i] for i in range(1, forecast_days + 1)])
            predicted_violations = model_violations.predict(future_days)
            
            predictions['violations_forecast'] = {
                'dates': [(end_date + timedelta(days=i)).isoformat() for i in range(1, forecast_days + 1)],
                'predicted_counts': predicted_violations.tolist(),
                'confidence_interval': self._calculate_confidence_interval(predicted_violations, 0.95)
            }
            
            # Predict revenue impact
            if 'revenue_impact' in df.columns:
                y_revenue = df['revenue_impact'].values
                model_revenue = LinearRegression()
                model_revenue.fit(X, y_revenue)
                
                predicted_revenue = model_revenue.predict(future_days)
                predictions['revenue_impact_forecast'] = {
                    'dates': [(end_date + timedelta(days=i)).isoformat() for i in range(1, forecast_days + 1)],
                    'predicted_amounts': predicted_revenue.tolist()
                }
            
            # Calculate trend indicators
            predictions['trend_indicators'] = {
                'violations_trend': 'increasing' if predicted_violations[-1] > predicted_violations[0] else 'decreasing',
                'trend_strength': abs(predicted_violations[-1] - predicted_violations[0]) / len(predicted_violations),
                'seasonality_detected': self._detect_seasonality(df['violations_count'].values)
            }
            
            logger.info(f"Generated {forecast_days}-day predictions for user {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {e}")
            return {}
    
    async def generate_comprehensive_report(self, user_id: str, start_date: datetime, end_date: datetime) -> ProtectionReport:
        """Generate comprehensive protection analytics report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Calculate KPIs
            kpis = await self.calculate_protection_kpis(user_id, start_date, end_date)
            
            # Generate platform analytics
            platform_analytics = await self.generate_platform_analytics(user_id, start_date, end_date)
            
            # Get overall metrics
            violations = await self._get_violations_data(user_id, start_date, end_date)
            total_detected = len([v for v in violations if v.get('status') != 'false_positive'])
            total_resolved = len([v for v in violations if v.get('status') == 'resolved'])
            
            # Calculate revenue recovered
            revenue_recovered = await self._calculate_revenue_recovered(user_id, start_date, end_date)
            
            # Calculate protection effectiveness
            effectiveness = (total_resolved / max(1, total_detected)) * 100
            
            # Generate trend analysis
            trend_analysis = await self._generate_trend_analysis(user_id, start_date, end_date)
            
            # Generate predictions
            predictions = await self.predict_violation_trends(user_id)
            
            # Create report
            report = ProtectionReport(
                report_id=report_id,
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                total_violations_detected=total_detected,
                total_violations_resolved=total_resolved,
                total_revenue_recovered=revenue_recovered,
                protection_effectiveness=effectiveness,
                key_metrics=kpis,
                platform_analytics=platform_analytics,
                trend_analysis=trend_analysis,
                predictions=predictions
            )
            
            logger.info(f"Generated comprehensive protection report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return ProtectionReport(
                report_id="",
                user_id=user_id,
                period_start=start_date,
                period_end=end_date,
                total_violations_detected=0,
                total_violations_resolved=0,
                total_revenue_recovered=Decimal('0.00'),
                protection_effectiveness=0.0
            )
    
    async def generate_real_time_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Generate real-time dashboard data"""
        try:
            # Get data for last 24 hours
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)
            
            dashboard_data = {
                'timestamp': end_date.isoformat(),
                'user_id': user_id,
                'real_time_metrics': {},
                'alerts': [],
                'recent_violations': [],
                'quick_stats': {}
            }
            
            # Get real-time metrics
            violations_last_24h = await self._get_violations_data(user_id, start_date, end_date)
            
            dashboard_data['real_time_metrics'] = {
                'violations_detected_24h': len(violations_last_24h),
                'violations_resolved_24h': len([v for v in violations_last_24h if v.get('status') == 'resolved']),
                'new_content_protected': await self._count_new_protected_content(user_id, start_date),
                'active_monitoring': await self._count_active_monitoring(user_id),
                'pending_takedowns': await self._count_pending_takedowns(user_id)
            }
            
            # Get recent violations (last 10)
            recent_violations = violations_last_24h[-10:] if len(violations_last_24h) > 10 else violations_last_24h
            dashboard_data['recent_violations'] = [
                {
                    'id': v.get('id'),
                    'platform': v.get('platform'),
                    'similarity_score': v.get('similarity_score'),
                    'status': v.get('status'),
                    'detected_at': v.get('detected_at'),
                    'url': v.get('infringing_url')
                }
                for v in recent_violations
            ]
            
            # Generate alerts for concerning trends
            alerts = await self._generate_alerts(user_id, violations_last_24h)
            dashboard_data['alerts'] = alerts
            
            # Quick stats
            dashboard_data['quick_stats'] = {
                'total_content_protected': await self._count_total_protected_content(user_id),
                'total_violations_all_time': await self._count_total_violations(user_id),
                'total_revenue_recovered': float(await self._calculate_total_revenue_recovered(user_id)),
                'protection_score': await self._calculate_protection_score(user_id)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            return {}
    
    # Helper methods
    async def _get_violations_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get violations data from database"""
        # This would query the database for violation records
        # Placeholder implementation
        return []
    
    async def _calculate_detection_rate(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate violation detection rate"""
        if not violations:
            return 0.0
        
        detected = len([v for v in violations if v.get('status') != 'missed'])
        total = len(violations)
        return (detected / total) * 100 if total > 0 else 0.0
    
    async def _calculate_false_positive_rate(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate false positive rate"""
        if not violations:
            return 0.0
        
        false_positives = len([v for v in violations if v.get('status') == 'false_positive'])
        total_detected = len([v for v in violations if v.get('similarity_score', 0) > 0.5])
        return (false_positives / total_detected) * 100 if total_detected > 0 else 0.0
    
    async def _calculate_takedown_success_rate(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate takedown success rate"""
        if not violations:
            return 0.0
        
        takedown_attempts = [v for v in violations if v.get('takedown_requested', False)]
        successful_takedowns = [v for v in takedown_attempts if v.get('status') == 'resolved']
        
        return (len(successful_takedowns) / len(takedown_attempts)) * 100 if takedown_attempts else 0.0
    
    async def _calculate_revenue_recovered(self, user_id: str, start_date: datetime, end_date: datetime) -> Decimal:
        """Calculate total revenue recovered"""
        # This would query revenue records from database
        return Decimal('0.00')
    
    async def _calculate_average_response_time(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate average response time in hours"""
        if not violations:
            return 0.0
        
        response_times = [
            v.get('response_time_hours', 0) 
            for v in violations 
            if v.get('response_time_hours') is not None
        ]
        
        return statistics.mean(response_times) if response_times else 0.0
    
    async def _calculate_protection_coverage(self, user_id: str) -> float:
        """Calculate percentage of content under protection"""
        # This would calculate based on total content vs protected content
        return 100.0
    
    async def _calculate_trend(self, user_id: str, metric: str, current_date: datetime) -> str:
        """Calculate trend direction for a metric"""
        # This would compare current period with previous period
        return "stable"
    
    def _calculate_platform_accuracy(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate detection accuracy for a platform"""
        if not violations:
            return 0.0
        
        accurate_detections = len([v for v in violations if v.get('status') != 'false_positive'])
        total_detections = len(violations)
        
        return (accurate_detections / total_detections) * 100 if total_detections > 0 else 0.0
    
    def _get_top_violation_types(self, violation_types: List[str]) -> List[str]:
        """Get top violation types by frequency"""
        from collections import Counter
        
        counter = Counter(violation_types)
        return [vtype for vtype, count in counter.most_common(5)]
    
    async def _generate_platform_trends(self, platform: str, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List[float]]:
        """Generate trend data for platform"""
        # This would generate daily/weekly trend data
        return {
            'violations_daily': [],
            'resolution_rate_daily': [],
            'response_time_daily': []
        }
    
    def _calculate_confidence_interval(self, predictions: np.ndarray, confidence: float) -> Dict[str, List[float]]:
        """Calculate confidence interval for predictions"""
        # Simplified confidence interval calculation
        margin = np.std(predictions) * confidence
        return {
            'lower_bound': (predictions - margin).tolist(),
            'upper_bound': (predictions + margin).tolist()
        }
    
    def _detect_seasonality(self, data: np.ndarray) -> bool:
        """Detect if there's seasonality in the data"""
        # Simple seasonality detection
        if len(data) < 14:
            return False
        
        # Check for weekly patterns
        weekly_correlation = np.corrcoef(data[:-7], data[7:])[0, 1] if len(data) > 14 else 0
        return abs(weekly_correlation) > 0.3
    
    async def _get_violations_by_platform(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get violations grouped by platform"""
        # This would query and group violations by platform
        return {}
    
    async def _get_daily_violations_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily aggregated violations data"""
        # This would return daily aggregated data for ML
        return []
    
    async def _generate_trend_analysis(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive trend analysis"""
        return {
            'violation_trends': {},
            'platform_trends': {},
            'revenue_trends': {},
            'seasonal_patterns': {}
        }
    
    async def _count_new_protected_content(self, user_id: str, start_date: datetime) -> int:
        """Count new content added to protection"""
        return 0
    
    async def _count_active_monitoring(self, user_id: str) -> int:
        """Count active monitoring tasks"""
        return 0
    
    async def _count_pending_takedowns(self, user_id: str) -> int:
        """Count pending takedown requests"""
        return 0
    
    async def _generate_alerts(self, user_id: str, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate alerts for concerning trends"""
        return []
    
    async def _count_total_protected_content(self, user_id: str) -> int:
        """Count total protected content"""
        return 0
    
    async def _count_total_violations(self, user_id: str) -> int:
        """Count total violations all time"""
        return 0
    
    async def _calculate_total_revenue_recovered(self, user_id: str) -> Decimal:
        """Calculate total revenue recovered all time"""
        return Decimal('0.00')
    
    async def _calculate_protection_score(self, user_id: str) -> float:
        """Calculate overall protection effectiveness score"""
        return 100.0
