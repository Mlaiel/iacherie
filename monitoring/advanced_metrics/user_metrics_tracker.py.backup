"""📊 User Metrics Tracker - MAU, DAU, and Retention Analytics
==========================================================

Advanced user metrics tracking system for monitoring Monthly Active Users (MAU),
Daily Active Users (DAU), retention rates, and comprehensive user engagement analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
CRITICAL WARNING: Unauthorized use, copying, or distribution strictly prohibited.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
from collections import defaultdict
import pandas as pd
import numpy as np
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class UserActivityType(Enum):
    """Types of user activities for tracking"""
    LOGIN = "login"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_VIEW = "content_view"
    COLLABORATION = "collaboration"
    REMIX_CREATION = "remix_creation"
    PLATFORM_PUBLISH = "platform_publish"
    COMMENT = "comment"
    LIKE = "like"
    SHARE = "share"
    PROFILE_UPDATE = "profile_update"


class RetentionPeriod(Enum):
    """Retention analysis periods"""
    DAY_1 = "1_day"
    DAY_7 = "7_days"
    DAY_30 = "30_days"
    DAY_90 = "90_days"
    DAY_180 = "180_days"
    DAY_365 = "365_days"


@dataclass
class UserActivity:
    """Individual user activity record"""
    user_id: str
    activity_type: UserActivityType
    timestamp: datetime
    platform: Optional[str] = None
    content_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MAUMetrics:
    """Monthly Active Users metrics"""
    total_mau: int
    new_users_this_month: int
    returning_users: int
    mau_by_platform: Dict[str, int]
    mau_by_activity_type: Dict[str, int]
    mau_growth_rate: float
    timestamp: datetime
    month_year: str


@dataclass
class DAUMetrics:
    """Daily Active Users metrics"""
    total_dau: int
    new_users_today: int
    returning_users_today: int
    dau_by_platform: Dict[str, int]
    dau_by_activity_type: Dict[str, int]
    dau_growth_rate: float
    peak_concurrent_users: int
    timestamp: datetime
    date_str: str


@dataclass
class RetentionMetrics:
    """User retention analysis metrics"""
    retention_rates: Dict[RetentionPeriod, float]
    cohort_analysis: Dict[str, Dict[str, float]]
    churn_rate: float
    user_lifecycle_stage_distribution: Dict[str, int]
    retention_by_platform: Dict[str, Dict[str, float]]
    retention_by_user_type: Dict[str, Dict[str, float]]
    timestamp: datetime


@dataclass
class UserEngagementMetrics:
    """Comprehensive user engagement metrics"""
    avg_session_duration: float
    avg_daily_sessions_per_user: float
    content_engagement_rate: float
    collaboration_participation_rate: float
    platform_distribution: Dict[str, float]
    feature_adoption_rates: Dict[str, float]
    user_satisfaction_score: float
    timestamp: datetime


class UserMetricsTracker:
    """
    Advanced user metrics tracking system.
    Monitors MAU, DAU, retention rates, and comprehensive user engagement analytics.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.activity_cache = {}
        self.user_cache = {}
        self.metrics_cache = {}
        
        # Prometheus metrics
        self.prometheus_metrics = {
            "user_mau_total": Gauge(
                "ainflue_user_mau_total",
                "Monthly Active Users total"
            ),
            "user_dau_total": Gauge(
                "ainflue_user_dau_total", 
                "Daily Active Users total"
            ),
            "user_retention_rate": Gauge(
                "ainflue_user_retention_rate",
                "User retention rate",
                ["period"]
            ),
            "user_activity_total": Counter(
                "ainflue_user_activity_total",
                "Total user activities",
                ["activity_type", "platform"]
            ),
            "user_session_duration": Histogram(
                "ainflue_user_session_duration_seconds",
                "User session duration in seconds"
            )
        }
    
    async def initialize(self) -> None:
        """Initialize the user metrics tracker"""
        try:
            self.logger.info("Initializing User Metrics Tracker...")
            
            # Initialize data connections
            await self._initialize_data_connections()
            
            # Setup activity tracking
            await self._setup_activity_tracking()
            
            self.logger.info("User Metrics Tracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize User Metrics Tracker: {e}")
            raise
    
    async def track_user_activity(self, activity: UserActivity) -> None:
        """Track a user activity for metrics calculation"""
        try:
            # Store activity
            await self._store_activity(activity)
            
            # Update real-time caches
            await self._update_activity_cache(activity)
            
            # Update Prometheus metrics
            self.prometheus_metrics["user_activity_total"].labels(
                activity_type=activity.activity_type.value,
                platform=activity.platform or "unknown"
            ).inc()
            
            self.logger.debug(f"Tracked activity: {activity.activity_type.value} for user {activity.user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to track user activity: {e}")
    
    async def calculate_mau_metrics(self, target_month: Optional[datetime] = None) -> MAUMetrics:
        """Calculate comprehensive Monthly Active Users metrics"""
        target_month = target_month or datetime.now()
        month_start = target_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        try:
            self.logger.info(f"Calculating MAU metrics for {month_start.strftime('%Y-%m')}")
            
            # Get active users for the month
            active_users = await self._get_active_users_in_period(month_start, month_end)
            
            # Calculate MAU by platform
            mau_by_platform = await self._calculate_mau_by_platform(month_start, month_end)
            
            # Calculate MAU by activity type
            mau_by_activity_type = await self._calculate_mau_by_activity_type(month_start, month_end)
            
            # Calculate new vs returning users
            new_users_this_month = await self._count_new_users_in_period(month_start, month_end)
            returning_users = len(active_users) - new_users_this_month
            
            # Calculate growth rate
            previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
            previous_month_end = month_start - timedelta(seconds=1)
            previous_mau = await self._get_mau_for_period(previous_month_start, previous_month_end)
            
            mau_growth_rate = ((len(active_users) - previous_mau) / previous_mau * 100) if previous_mau > 0 else 0
            
            mau_metrics = MAUMetrics(
                total_mau=len(active_users),
                new_users_this_month=new_users_this_month,
                returning_users=returning_users,
                mau_by_platform=mau_by_platform,
                mau_by_activity_type=mau_by_activity_type,
                mau_growth_rate=mau_growth_rate,
                timestamp=datetime.now(),
                month_year=month_start.strftime('%Y-%m')
            )
            
            # Update Prometheus metrics
            self.prometheus_metrics["user_mau_total"].set(len(active_users))
            
            # Cache results
            cache_key = f"mau_{month_start.strftime('%Y-%m')}"
            self.metrics_cache[cache_key] = mau_metrics
            
            return mau_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate MAU metrics: {e}")
            raise
    
    async def calculate_dau_metrics(self, target_date: Optional[datetime] = None) -> DAUMetrics:
        """Calculate comprehensive Daily Active Users metrics"""
        target_date = target_date or datetime.now()
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
        
        try:
            self.logger.info(f"Calculating DAU metrics for {target_date.strftime('%Y-%m-%d')}")
            
            # Get active users for the day
            active_users = await self._get_active_users_in_period(day_start, day_end)
            
            # Calculate DAU by platform
            dau_by_platform = await self._calculate_dau_by_platform(day_start, day_end)
            
            # Calculate DAU by activity type
            dau_by_activity_type = await self._calculate_dau_by_activity_type(day_start, day_end)
            
            # Calculate new vs returning users
            new_users_today = await self._count_new_users_in_period(day_start, day_end)
            returning_users_today = len(active_users) - new_users_today
            
            # Calculate growth rate
            previous_day_start = day_start - timedelta(days=1)
            previous_day_end = day_start - timedelta(seconds=1)
            previous_dau = await self._get_dau_for_period(previous_day_start, previous_day_end)
            
            dau_growth_rate = ((len(active_users) - previous_dau) / previous_dau * 100) if previous_dau > 0 else 0
            
            # Get peak concurrent users (simulated)
            peak_concurrent_users = await self._get_peak_concurrent_users(day_start, day_end)
            
            dau_metrics = DAUMetrics(
                total_dau=len(active_users),
                new_users_today=new_users_today,
                returning_users_today=returning_users_today,
                dau_by_platform=dau_by_platform,
                dau_by_activity_type=dau_by_activity_type,
                dau_growth_rate=dau_growth_rate,
                peak_concurrent_users=peak_concurrent_users,
                timestamp=datetime.now(),
                date_str=target_date.strftime('%Y-%m-%d')
            )
            
            # Update Prometheus metrics
            self.prometheus_metrics["user_dau_total"].set(len(active_users))
            
            # Cache results
            cache_key = f"dau_{target_date.strftime('%Y-%m-%d')}"
            self.metrics_cache[cache_key] = dau_metrics
            
            return dau_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate DAU metrics: {e}")
            raise
    
    async def calculate_retention_metrics(self, analysis_date: Optional[datetime] = None) -> RetentionMetrics:
        """Calculate comprehensive user retention metrics"""
        analysis_date = analysis_date or datetime.now()
        
        try:
            self.logger.info(f"Calculating retention metrics for {analysis_date.strftime('%Y-%m-%d')}")
            
            # Calculate retention rates for different periods
            retention_rates = {}
            for period in RetentionPeriod:
                retention_rate = await self._calculate_retention_rate(analysis_date, period)
                retention_rates[period] = retention_rate
                
                # Update Prometheus metrics
                self.prometheus_metrics["user_retention_rate"].labels(period=period.value).set(retention_rate)
            
            # Calculate cohort analysis
            cohort_analysis = await self._calculate_cohort_analysis(analysis_date)
            
            # Calculate churn rate
            churn_rate = await self._calculate_churn_rate(analysis_date)
            
            # Calculate user lifecycle distribution
            lifecycle_distribution = await self._calculate_lifecycle_distribution(analysis_date)
            
            # Calculate retention by platform
            retention_by_platform = await self._calculate_retention_by_platform(analysis_date)
            
            # Calculate retention by user type
            retention_by_user_type = await self._calculate_retention_by_user_type(analysis_date)
            
            retention_metrics = RetentionMetrics(
                retention_rates=retention_rates,
                cohort_analysis=cohort_analysis,
                churn_rate=churn_rate,
                user_lifecycle_stage_distribution=lifecycle_distribution,
                retention_by_platform=retention_by_platform,
                retention_by_user_type=retention_by_user_type,
                timestamp=datetime.now()
            )
            
            # Cache results
            cache_key = f"retention_{analysis_date.strftime('%Y-%m-%d')}"
            self.metrics_cache[cache_key] = retention_metrics
            
            return retention_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate retention metrics: {e}")
            raise
    
    async def calculate_engagement_metrics(self, analysis_date: Optional[datetime] = None) -> UserEngagementMetrics:
        """Calculate comprehensive user engagement metrics"""
        analysis_date = analysis_date or datetime.now()
        day_start = analysis_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
        
        try:
            self.logger.info(f"Calculating engagement metrics for {analysis_date.strftime('%Y-%m-%d')}")
            
            # Calculate average session duration
            avg_session_duration = await self._calculate_avg_session_duration(day_start, day_end)
            
            # Calculate daily sessions per user
            avg_daily_sessions = await self._calculate_avg_daily_sessions_per_user(day_start, day_end)
            
            # Calculate content engagement rate
            content_engagement_rate = await self._calculate_content_engagement_rate(day_start, day_end)
            
            # Calculate collaboration participation rate
            collaboration_rate = await self._calculate_collaboration_participation_rate(day_start, day_end)
            
            # Calculate platform distribution
            platform_distribution = await self._calculate_platform_distribution(day_start, day_end)
            
            # Calculate feature adoption rates
            feature_adoption_rates = await self._calculate_feature_adoption_rates(day_start, day_end)
            
            # Calculate user satisfaction score (simulated)
            user_satisfaction_score = await self._calculate_user_satisfaction_score(day_start, day_end)
            
            engagement_metrics = UserEngagementMetrics(
                avg_session_duration=avg_session_duration,
                avg_daily_sessions_per_user=avg_daily_sessions,
                content_engagement_rate=content_engagement_rate,
                collaboration_participation_rate=collaboration_rate,
                platform_distribution=platform_distribution,
                feature_adoption_rates=feature_adoption_rates,
                user_satisfaction_score=user_satisfaction_score,
                timestamp=datetime.now()
            )
            
            # Update Prometheus metrics
            self.prometheus_metrics["user_session_duration"].observe(avg_session_duration)
            
            return engagement_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate engagement metrics: {e}")
            raise
    
    # Helper methods for data calculation (simplified implementations)
    async def _get_active_users_in_period(self, start_time: datetime, end_time: datetime) -> Set[str]:
        """Get set of active users in a time period"""
        # In production, this would query the database
        # For now, returning simulated data
        base_users = 15000
        variation = int(base_users * 0.1 * np.random.random())
        return set([f"user_{i}" for i in range(base_users + variation)])
    
    async def _calculate_mau_by_platform(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Calculate MAU broken down by platform"""
        return {
            "spotify": 4200,
            "youtube": 5800,
            "instagram": 3900,
            "tiktok": 4100,
            "soundcloud": 1800,
            "linkedin": 1200
        }
    
    async def _calculate_mau_by_activity_type(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Calculate MAU broken down by activity type"""
        return {
            "content_upload": 8500,
            "collaboration": 3200,
            "platform_publish": 6800,
            "remix_creation": 2100,
            "content_view": 14800
        }
    
    async def _count_new_users_in_period(self, start_time: datetime, end_time: datetime) -> int:
        """Count new users registered in period"""
        return int(2500 + 500 * np.random.random())
    
    async def _get_mau_for_period(self, start_time: datetime, end_time: datetime) -> int:
        """Get MAU count for a specific period"""
        return int(14500 + 1000 * np.random.random())
    
    async def _get_dau_for_period(self, start_time: datetime, end_time: datetime) -> int:
        """Get DAU count for a specific period"""
        return int(3500 + 500 * np.random.random())
    
    async def _calculate_dau_by_platform(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Calculate DAU broken down by platform"""
        return {
            "spotify": 1200,
            "youtube": 1800,
            "instagram": 1100,
            "tiktok": 1400,
            "soundcloud": 600,
            "linkedin": 400
        }
    
    async def _calculate_dau_by_activity_type(self, start_time: datetime, end_time: datetime) -> Dict[str, int]:
        """Calculate DAU broken down by activity type"""
        return {
            "content_upload": 2800,
            "collaboration": 1200,
            "platform_publish": 2200,
            "remix_creation": 800,
            "content_view": 5800
        }
    
    async def _get_peak_concurrent_users(self, start_time: datetime, end_time: datetime) -> int:
        """Get peak concurrent users for the day"""
        return int(850 + 150 * np.random.random())
    
    async def _calculate_retention_rate(self, analysis_date: datetime, period: RetentionPeriod) -> float:
        """Calculate retention rate for a specific period"""
        # Simulated retention rates based on industry standards
        retention_rates = {
            RetentionPeriod.DAY_1: 0.85,
            RetentionPeriod.DAY_7: 0.68,
            RetentionPeriod.DAY_30: 0.45,
            RetentionPeriod.DAY_90: 0.28,
            RetentionPeriod.DAY_180: 0.18,
            RetentionPeriod.DAY_365: 0.12
        }
        return retention_rates.get(period, 0.0) + (np.random.random() - 0.5) * 0.1
    
    async def _calculate_cohort_analysis(self, analysis_date: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate cohort retention analysis"""
        return {
            "2024-01": {"day_1": 0.85, "day_7": 0.70, "day_30": 0.48},
            "2024-02": {"day_1": 0.87, "day_7": 0.72, "day_30": 0.51},
            "2024-03": {"day_1": 0.89, "day_7": 0.75, "day_30": 0.54}
        }
    
    async def _calculate_churn_rate(self, analysis_date: datetime) -> float:
        """Calculate monthly churn rate"""
        return 0.032 + (np.random.random() - 0.5) * 0.01  # ~3.2% churn rate
    
    async def _calculate_lifecycle_distribution(self, analysis_date: datetime) -> Dict[str, int]:
        """Calculate user lifecycle stage distribution"""
        return {
            "new": 2500,
            "active": 8500,
            "at_risk": 1800,
            "dormant": 1200,
            "churned": 600
        }
    
    async def _calculate_retention_by_platform(self, analysis_date: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate retention rates by platform"""
        return {
            "spotify": {"day_7": 0.72, "day_30": 0.48},
            "youtube": {"day_7": 0.75, "day_30": 0.52},
            "instagram": {"day_7": 0.70, "day_30": 0.45},
            "tiktok": {"day_7": 0.78, "day_30": 0.55}
        }
    
    async def _calculate_retention_by_user_type(self, analysis_date: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate retention rates by user type"""
        return {
            "premium": {"day_7": 0.82, "day_30": 0.65},
            "free": {"day_7": 0.65, "day_30": 0.38},
            "enterprise": {"day_7": 0.95, "day_30": 0.87}
        }
    
    async def _calculate_avg_session_duration(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate average session duration in seconds"""
        return 1250.5 + (np.random.random() - 0.5) * 200  # ~20 minutes average
    
    async def _calculate_avg_daily_sessions_per_user(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate average daily sessions per user"""
        return 2.8 + (np.random.random() - 0.5) * 0.5  # ~2.8 sessions per day
    
    async def _calculate_content_engagement_rate(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate content engagement rate"""
        return 0.425 + (np.random.random() - 0.5) * 0.1  # ~42.5% engagement rate
    
    async def _calculate_collaboration_participation_rate(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate collaboration participation rate"""
        return 0.185 + (np.random.random() - 0.5) * 0.05  # ~18.5% collaboration rate
    
    async def _calculate_platform_distribution(self, start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """Calculate user distribution across platforms"""
        return {
            "spotify": 0.28,
            "youtube": 0.32,
            "instagram": 0.22,
            "tiktok": 0.18
        }
    
    async def _calculate_feature_adoption_rates(self, start_time: datetime, end_time: datetime) -> Dict[str, float]:
        """Calculate feature adoption rates"""
        return {
            "ai_protection": 0.87,
            "remix_creation": 0.65,
            "collaboration_tools": 0.58,
            "seo_optimization": 0.72,
            "multi_platform_publish": 0.83
        }
    
    async def _calculate_user_satisfaction_score(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate user satisfaction score (NPS-like)"""
        return 7.8 + (np.random.random() - 0.5) * 1.0  # Score out of 10
    
    async def _store_activity(self, activity: UserActivity) -> None:
        """Store user activity in database"""
        # In production, this would store in database
        pass
    
    async def _update_activity_cache(self, activity: UserActivity) -> None:
        """Update real-time activity cache"""
        if activity.user_id not in self.activity_cache:
            self.activity_cache[activity.user_id] = []
        self.activity_cache[activity.user_id].append(activity)
    
    async def _initialize_data_connections(self) -> None:
        """Initialize database and cache connections"""
        # In production, this would initialize actual connections
        pass
    
    async def _setup_activity_tracking(self) -> None:
        """Setup real-time activity tracking"""
        # In production, this would setup event listeners
        pass