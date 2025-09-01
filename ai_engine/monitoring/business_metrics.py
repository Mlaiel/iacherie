"""Advanced Business Metrics Collection Module

Enterprise-grade business intelligence and KPI tracking for IA Influencer Agent platform.
Tracks revenue, user engagement, creator success, and platform growth metrics.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
import statistics
import json
import numpy as np
from decimal import Decimal
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.metrics import MetricsCollector, MetricEntry, MetricType, MetricPriority
from ..core.exceptions import MonitoringError, BusinessMetricsError
from .content_monitoring import ContentType, ContentStatus

logger = logging.getLogger(__name__)


class RevenueSource(Enum):
    """
Revenue generation sources"""

    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_MATCHING = "collaboration_matching"
    PREMIUM_FEATURES = "premium_features"
    DISTRIBUTION_FEES = "distribution_fees"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    TRANSACTION_FEES = "transaction_fees"
    LICENSING = "licensing"
    PARTNERSHIPS = "partnerships"
    AFFILIATE_COMMISSIONS = "affiliate_commissions"


class UserTier(Enum):
    """User subscription tiers"""

    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class EngagementType(Enum):
    """Types of user engagement"""

    CONTENT_UPLOAD = "content_upload"
    CONTENT_SHARE = "content_share"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_ACCEPT = "collaboration_accept"
    REVENUE_WITHDRAWAL = "revenue_withdrawal"
    FEATURE_USAGE = "feature_usage"
    PROFILE_UPDATE = "profile_update"
    PLATFORM_REFERRAL = "platform_referral"


@dataclass
class RevenueMetrics:
    """Comprehensive revenue tracking metrics"""
    user_id: str
    revenue_source: RevenueSource
    amount: Decimal
    currency: str
    content_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    transaction_id: Optional[str] = None
    commission_rate: float = 0.0
    platform_fee: Decimal = Decimal('0.00')
    net_revenue: Optional[Decimal] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserEngagementMetrics:
    """
User engagement and activity metrics"""
    user_id: str
    engagement_type: EngagementType
    session_id: str
    engagement_value: float
    duration: Optional[float] = None
    feature_used: Optional[str] = None
    content_type: Optional[ContentType] = None
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorSuccessMetrics:
    """
Creator success and growth metrics"""
    user_id: str
    content_uploads: int
    successful_protections: int
    collaborations_initiated: int
    collaborations_completed: int
    total_revenue: Decimal
    follower_growth: int
    engagement_rate: float
    content_quality_score: float
    platform_ranking: int
    success_score: float
    time_period: timedelta
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformGrowthMetrics:
    """
Platform growth and health metrics"""
    new_users: int
    active_users: int
    retained_users: int
    churned_users: int
    total_content_uploaded: int
    total_revenue: Decimal
    average_revenue_per_user: Decimal
    user_acquisition_cost: Decimal
    lifetime_value: Decimal
    platform_health_score: float
    growth_rate: float
    time_period: timedelta
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BusinessMetricsCollector:
    """
    Advanced Business Metrics Collector
    
    Collects, analyzes, and reports business intelligence metrics for the
    IA Influencer Agent platform focusing on revenue, growth, and user success.
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        redis_client: Optional[aioredis.Redis] = None,
        database_session: Optional[AsyncSession] = None
    ):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.redis_client = redis_client
        self.database_session = database_session
        
        # Revenue tracking
        self.revenue_metrics: deque = deque(maxlen=10000)
        self.revenue_by_source: Dict[RevenueSource, Decimal] = defaultdict(lambda: Decimal('0.00'))
        self.revenue_by_user: Dict[str, Decimal] = defaultdict(lambda: Decimal('0.00'))
        self.revenue_trends: Dict[str, List[float]] = defaultdict(list)
        
        # User engagement tracking
        self.engagement_metrics: deque = deque(maxlen=10000)
        self.user_engagement_scores: Dict[str, float] = defaultdict(float)
        self.engagement_trends: Dict[EngagementType, List[float]] = defaultdict(list)
        
        # Creator success tracking
        self.creator_metrics: Dict[str, CreatorSuccessMetrics] = {}
        self.creator_rankings: List[Tuple[str, float]] = []
        
        # Platform growth tracking
        self.platform_metrics: List[PlatformGrowthMetrics] = []
        self.growth_kpis: Dict[str, float] = {}
        
        # Business intelligence
        self.conversion_funnels: Dict[str, List[float]] = defaultdict(list)
        self.cohort_analysis: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.churn_predictions: Dict[str, float] = {}
        
        # Real-time analytics
        self.real_time_stats = {
            "active_users_now": 0,
            "revenue_today": Decimal('0.00'),
            "uploads_today": 0,
            "collaborations_today": 0
        }
        
        # Monitoring state
        self.is_collecting = False
        self._collection_task: Optional[asyncio.Task] = None
        
    async def start_collection(self) -> None:
        """Start business metrics collection"""
        if self.is_collecting:
            logger.warning("Business metrics collection is already running")
            return
            
        self.is_collecting = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        
        logger.info("Business metrics collection started successfully")
        
    async def stop_collection(self) -> None:
        """Stop business metrics collection"""
        if not self.is_collecting:
            return
            
        self.is_collecting = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Business metrics collection stopped")
        
    async def record_revenue(
        self,
        user_id: str,
        revenue_source: RevenueSource,
        amount: Decimal,
        currency: str = "USD",
        content_id: Optional[str] = None,
        collaboration_id: Optional[str] = None,
        commission_rate: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record revenue generation event
        
        Returns:
            transaction_id: Unique identifier for this revenue event
        """
        transaction_id = f"txn_{int(time.time() * 1000)}_{hash(user_id) % 10000}"
        
        # Calculate platform fee and net revenue
        platform_fee = amount * Decimal(str(commission_rate))
        net_revenue = amount - platform_fee
        
        # Create revenue metrics
        revenue_metrics = RevenueMetrics(
            user_id=user_id,
            revenue_source=revenue_source,
            amount=amount,
            currency=currency,
            content_id=content_id,
            collaboration_id=collaboration_id,
            transaction_id=transaction_id,
            commission_rate=commission_rate,
            platform_fee=platform_fee,
            net_revenue=net_revenue,
            metadata=metadata or {}
        )
        
        # Store metrics
        self.revenue_metrics.append(revenue_metrics)
        self.revenue_by_source[revenue_source] += amount
        self.revenue_by_user[user_id] += net_revenue
        
        # Update real-time stats
        self.real_time_stats["revenue_today"] += amount
        
        # Update revenue trends
        hour_key = datetime.utcnow().strftime("%Y%m%d%H")
        self.revenue_trends[hour_key].append(float(amount))
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="revenue_generated",
                value=float(amount),
                metric_type=MetricType.COUNTER,
                tags={
                    "revenue_source": revenue_source.value,
                    "currency": currency,
                    "has_collaboration": str(collaboration_id is not None)
                },
                user_id=user_id,
                priority=MetricPriority.HIGH,
                metadata={
                    "transaction_id": transaction_id,
                    "content_id": content_id,
                    "collaboration_id": collaboration_id,
                    "commission_rate": commission_rate
                }
            )
        )
        
        # Store in Redis for real-time access
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"revenue:{transaction_id}",
                    86400,  # 24 hours TTL
                    json.dumps({
                        "user_id": user_id,
                        "amount": str(amount),
                        "source": revenue_source.value,
                        "timestamp": revenue_metrics.timestamp.isoformat()
                    })
                )
            except Exception as e:
                logger.warning(f"Failed to store revenue in Redis: {e}")
                
        logger.info(f"Recorded revenue: {amount} {currency} from {revenue_source.value} for user {user_id}")
        return transaction_id
        
    async def record_user_engagement(
        self,
        user_id: str,
        engagement_type: EngagementType,
        session_id: str,
        engagement_value: float = 1.0,
        duration: Optional[float] = None,
        feature_used: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record user engagement event"""
        engagement_metrics = UserEngagementMetrics(
            user_id=user_id,
            engagement_type=engagement_type,
            session_id=session_id,
            engagement_value=engagement_value,
            duration=duration,
            feature_used=feature_used,
            content_type=content_type,
            success=success,
            metadata=metadata or {}
        )
        
        # Store metrics
        self.engagement_metrics.append(engagement_metrics)
        
        # Update user engagement score
        self.user_engagement_scores[user_id] += engagement_value
        
        # Update engagement trends
        self.engagement_trends[engagement_type].append(engagement_value)
        
        # Update real-time stats
        if engagement_type == EngagementType.CONTENT_UPLOAD:
            self.real_time_stats["uploads_today"] += 1
        elif engagement_type in [EngagementType.COLLABORATION_REQUEST, EngagementType.COLLABORATION_ACCEPT]:
            self.real_time_stats["collaborations_today"] += 1
            
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="user_engagement",
                value=engagement_value,
                metric_type=MetricType.COUNTER,
                tags={
                    "engagement_type": engagement_type.value,
                    "feature_used": feature_used or "none",
                    "content_type": content_type.value if content_type else "none",
                    "success": str(success)
                },
                user_id=user_id,
                metadata={
                    "session_id": session_id,
                    "duration": duration
                }
            )
        )
        
    async def update_creator_metrics(
        self,
        user_id: str,
        content_uploads: Optional[int] = None,
        successful_protections: Optional[int] = None,
        collaborations_initiated: Optional[int] = None,
        collaborations_completed: Optional[int] = None,
        follower_growth: Optional[int] = None,
        engagement_rate: Optional[float] = None,
        content_quality_score: Optional[float] = None
    ) -> CreatorSuccessMetrics:
        """Update creator success metrics"""
        current_time = datetime.utcnow()
        
        # Get or create creator metrics
        if user_id not in self.creator_metrics:
            self.creator_metrics[user_id] = CreatorSuccessMetrics(
                user_id=user_id,
                content_uploads=0,
                successful_protections=0,
                collaborations_initiated=0,
                collaborations_completed=0,
                total_revenue=Decimal('0.00'),
                follower_growth=0,
                engagement_rate=0.0,
                content_quality_score=0.0,
                platform_ranking=0,
                success_score=0.0,
                time_period=timedelta(days=30)
            )
            
        metrics = self.creator_metrics[user_id]
        
        # Update metrics
        if content_uploads is not None:
            metrics.content_uploads += content_uploads
        if successful_protections is not None:
            metrics.successful_protections += successful_protections
        if collaborations_initiated is not None:
            metrics.collaborations_initiated += collaborations_initiated
        if collaborations_completed is not None:
            metrics.collaborations_completed += collaborations_completed
        if follower_growth is not None:
            metrics.follower_growth += follower_growth
        if engagement_rate is not None:
            metrics.engagement_rate = engagement_rate
        if content_quality_score is not None:
            metrics.content_quality_score = content_quality_score
            
        # Update total revenue
        metrics.total_revenue = self.revenue_by_user[user_id]
        
        # Calculate success score
        metrics.success_score = await self._calculate_creator_success_score(metrics)
        
        # Update timestamp
        metrics.timestamp = current_time
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="creator_success_score",
                value=metrics.success_score,
                metric_type=MetricType.GAUGE,
                tags={
                    "creator_tier": self._determine_creator_tier(metrics).value
                },
                user_id=user_id,
                metadata={
                    "content_uploads": metrics.content_uploads,
                    "total_revenue": str(metrics.total_revenue),
                    "collaboration_rate": (
                        metrics.collaborations_completed / max(metrics.collaborations_initiated, 1)
                    )
                }
            )
        )
        
        # Update creator rankings
        await self._update_creator_rankings()
        
        return metrics
        
    async def track_conversion_funnel(
        self,
        user_id: str,
        funnel_name: str,
        stage: str,
        converted: bool = True
    ) -> None:
        """Track conversion funnel metrics"""
        funnel_key = f"{funnel_name}:{stage}"
        conversion_value = 1.0 if converted else 0.0
        
        self.conversion_funnels[funnel_key].append(conversion_value)
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="conversion_funnel",
                value=conversion_value,
                metric_type=MetricType.COUNTER,
                tags={
                    "funnel_name": funnel_name,
                    "stage": stage,
                    "converted": str(converted)
                },
                user_id=user_id
            )
        )
        
    async def calculate_platform_growth(
        self,
        time_period: timedelta = timedelta(days=7)
    ) -> PlatformGrowthMetrics:
        """Calculate platform growth metrics"""
        cutoff_time = datetime.utcnow() - time_period
        
        # Count users by activity
        active_users = len([
            user_id for user_id, score in self.user_engagement_scores.items()
            if score > 0
        ])
        
        # Calculate revenue metrics
        total_revenue = sum(self.revenue_by_source.values())
        average_revenue_per_user = total_revenue / max(active_users, 1)
        
        # Calculate growth rate (simplified)
        growth_rate = 0.05  # Would calculate from historical data
        
        # Calculate platform health score
        platform_health_score = await self._calculate_platform_health_score()
        
        growth_metrics = PlatformGrowthMetrics(
            new_users=0,  # Would query database for new users
            active_users=active_users,
            retained_users=0,  # Would calculate from cohort analysis
            churned_users=0,  # Would calculate from activity data
            total_content_uploaded=self.real_time_stats["uploads_today"],
            total_revenue=total_revenue,
            average_revenue_per_user=average_revenue_per_user,
            user_acquisition_cost=Decimal('25.00'),  # Would calculate from marketing data
            lifetime_value=Decimal('150.00'),  # Would calculate from user behavior
            platform_health_score=platform_health_score,
            growth_rate=growth_rate,
            time_period=time_period
        )
        
        self.platform_metrics.append(growth_metrics)
        
        # Collect metrics
        await self.metrics_collector.collect_metric(
            MetricEntry(
                name="platform_growth_rate",
                value=growth_rate,
                metric_type=MetricType.GAUGE,
                tags={
                    "time_period": str(time_period.days)
                },
                priority=MetricPriority.HIGH,
                metadata={
                    "active_users": active_users,
                    "total_revenue": str(total_revenue),
                    "health_score": platform_health_score
                }
            )
        )
        
        return growth_metrics
        
    async def get_business_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive business dashboard data"""
        current_time = datetime.utcnow()
        
        # Revenue analytics
        revenue_analytics = await self._calculate_revenue_analytics()
        
        # User analytics
        user_analytics = await self._calculate_user_analytics()
        
        # Creator analytics
        creator_analytics = await self._calculate_creator_analytics()
        
        # Platform analytics
        platform_analytics = await self._calculate_platform_analytics()
        
        # Growth predictions
        growth_predictions = await self._generate_growth_predictions()
        
        return {
            "timestamp": current_time.isoformat(),
            "real_time_stats": {
                "active_users_now": self.real_time_stats["active_users_now"],
                "revenue_today": str(self.real_time_stats["revenue_today"]),
                "uploads_today": self.real_time_stats["uploads_today"],
                "collaborations_today": self.real_time_stats["collaborations_today"]
            },
            "revenue_analytics": revenue_analytics,
            "user_analytics": user_analytics,
            "creator_analytics": creator_analytics,
            "platform_analytics": platform_analytics,
            "growth_predictions": growth_predictions,
            "kpis": await self._calculate_key_performance_indicators()
        }
        
    async def get_revenue_analytics(
        self,
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get detailed revenue analytics"""
        cutoff_time = datetime.utcnow() - time_window
        
        # Filter recent revenue
        recent_revenue = [
            rev for rev in self.revenue_metrics
            if rev.timestamp >= cutoff_time
        ]
        
        if not recent_revenue:
            return {"error": "No revenue data available for the specified time window"}
            
        # Revenue by source
        revenue_by_source = {}
        for source in RevenueSource:
            source_revenue = sum(
                rev.amount for rev in recent_revenue
                if rev.revenue_source == source
            )
            revenue_by_source[source.value] = str(source_revenue)
            
        # Revenue trends
        daily_revenue = defaultdict(lambda: Decimal('0.00'))
        for rev in recent_revenue:
            day_key = rev.timestamp.strftime("%Y-%m-%d")
            daily_revenue[day_key] += rev.amount
            
        # Top earning users
        user_revenues = defaultdict(lambda: Decimal('0.00'))
        for rev in recent_revenue:
            user_revenues[rev.user_id] += rev.net_revenue or rev.amount
            
        top_earners = sorted(
            user_revenues.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        total_revenue = sum(rev.amount for rev in recent_revenue)
        total_transactions = len(recent_revenue)
        average_transaction = total_revenue / max(total_transactions, 1)
        
        return {
            "time_window": str(time_window),
            "total_revenue": str(total_revenue),
            "total_transactions": total_transactions,
            "average_transaction_value": str(average_transaction),
            "revenue_by_source": revenue_by_source,
            "daily_revenue_trend": {
                k: str(v) for k, v in daily_revenue.items()
            },
            "top_earners": [
                {"user_id": user_id, "revenue": str(revenue)}
                for user_id, revenue in top_earners
            ],
            "commission_earned": str(
                sum(rev.platform_fee for rev in recent_revenue)
            )
        }
        
    async def predict_churn_risk(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Predict churn risk for a specific user"""
        # Simple churn prediction based on engagement
        engagement_score = self.user_engagement_scores.get(user_id, 0.0)
        revenue = self.revenue_by_user.get(user_id, Decimal('0.00'))
        
        # Calculate risk factors
        risk_factors = []
        churn_score = 0.0
        
        if engagement_score < 10.0:  # Low engagement
            risk_factors.append("low_engagement")
            churn_score += 0.3
            
        if revenue < Decimal('10.00'):  # Low revenue
            risk_factors.append("low_revenue")
            churn_score += 0.2
            
        # Check recent activity
        recent_engagement = [
            eng for eng in self.engagement_metrics
            if eng.user_id == user_id and 
            eng.timestamp >= datetime.utcnow() - timedelta(days=7)
        ]
        
        if len(recent_engagement) < 3:  # Less than 3 engagements in a week
            risk_factors.append("inactive")
            churn_score += 0.4
            
        # Determine risk level
        if churn_score >= 0.7:
            risk_level = "high"
        elif churn_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
            
        self.churn_predictions[user_id] = churn_score
        
        return {
            "user_id": user_id,
            "churn_score": churn_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_actions": await self._generate_retention_actions(risk_factors)
        }
        
    async def _calculate_creator_success_score(
        self,
        metrics: CreatorSuccessMetrics
    ) -> float:
        """Calculate creator success score based on multiple factors"""
        score = 0.0
        
        # Content success rate (30% weight)
        if metrics.content_uploads > 0:
            success_rate = metrics.successful_protections / metrics.content_uploads
            score += success_rate * 30
            
        # Collaboration success rate (25% weight)
        if metrics.collaborations_initiated > 0:
            collab_rate = metrics.collaborations_completed / metrics.collaborations_initiated
            score += collab_rate * 25
            
        # Revenue performance (25% weight)
        revenue_score = min(float(metrics.total_revenue) / 1000, 1.0)  # Normalize to $1000
        score += revenue_score * 25
        
        # Engagement rate (20% weight)
        score += metrics.engagement_rate * 20
        
        return min(score, 100.0)  # Cap at 100
        
    def _determine_creator_tier(self, metrics: CreatorSuccessMetrics) -> UserTier:
        """
Determine creator tier based on success metrics"""
        if metrics.success_score >= 80 and metrics.total_revenue >= 1000:
            return UserTier.ENTERPRISE
        elif metrics.success_score >= 60 and metrics.total_revenue >= 500:
            return UserTier.PROFESSIONAL
        elif metrics.success_score >= 40 and metrics.total_revenue >= 100:
            return UserTier.PREMIUM
        elif metrics.success_score >= 20:
            return UserTier.BASIC
        else:
            return UserTier.FREE
            
    async def _update_creator_rankings(self) -> None:
        """
Update creator rankings based on success scores"""
        rankings = [
            (user_id, metrics.success_score)
            for user_id, metrics in self.creator_metrics.items()
        ]
        
        # Sort by success score descending
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Update rankings with position
        for i, (user_id, score) in enumerate(rankings):
            self.creator_metrics[user_id].platform_ranking = i + 1
            
        self.creator_rankings = rankings[:100]  # Keep top 100
        
    async def _calculate_platform_health_score(self) -> float:
        """
Calculate overall platform health score"""
        health_factors = []
        
        # Revenue growth (25% weight)
        if len(self.revenue_trends) > 1:
            recent_revenue = sum(
                sum(values) for values in list(self.revenue_trends.values())[-7:]  # Last 7 days
            )
            revenue_health = min(recent_revenue / 10000, 1.0)  # Normalize to $10k
            health_factors.append(revenue_health * 25)
            
        # User engagement (25% weight)
        avg_engagement = statistics.mean(self.user_engagement_scores.values()) if self.user_engagement_scores else 0
        engagement_health = min(avg_engagement / 100, 1.0)
        health_factors.append(engagement_health * 25)
        
        # Creator success (25% weight)
        if self.creator_metrics:
            avg_creator_score = statistics.mean(
                metrics.success_score for metrics in self.creator_metrics.values()
            )
            creator_health = avg_creator_score / 100
            health_factors.append(creator_health * 25)
            
        # Platform growth (25% weight)
        growth_health = 0.8  # Would calculate from user acquisition trends
        health_factors.append(growth_health * 25)
        
        return sum(health_factors) if health_factors else 0.0
        
    async def _calculate_revenue_analytics(self) -> Dict[str, Any]:
        """
Calculate comprehensive revenue analytics"""
        total_revenue = sum(self.revenue_by_source.values())
        
        return {
            "total_revenue": str(total_revenue),
            "revenue_by_source": {
                source.value: str(amount)
                for source, amount in self.revenue_by_source.items()
            },
            "top_revenue_source": max(
                self.revenue_by_source.items(),
                key=lambda x: x[1],
                default=(RevenueSource.CONTENT_PROTECTION, Decimal('0.00'))
            )[0].value,
            "average_revenue_per_user": str(
                total_revenue / max(len(self.revenue_by_user), 1)
            )
        }
        
    async def _calculate_user_analytics(self) -> Dict[str, Any]:
        """Calculate user analytics"""
        total_users = len(self.user_engagement_scores)
        active_users = len([
            score for score in self.user_engagement_scores.values()
            if score > 0
        ])
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "activation_rate": active_users / max(total_users, 1),
            "average_engagement_score": statistics.mean(
                self.user_engagement_scores.values()
            ) if self.user_engagement_scores else 0.0
        }
        
    async def _calculate_creator_analytics(self) -> Dict[str, Any]:
        """Calculate creator analytics"""
        if not self.creator_metrics:
            return {"total_creators": 0}
            
        total_creators = len(self.creator_metrics)
        avg_success_score = statistics.mean(
            metrics.success_score for metrics in self.creator_metrics.values()
        )
        
        # Creator tier distribution
        tier_distribution = defaultdict(int)
        for metrics in self.creator_metrics.values():
            tier = self._determine_creator_tier(metrics)
            tier_distribution[tier.value] += 1
            
        return {
            "total_creators": total_creators,
            "average_success_score": avg_success_score,
            "tier_distribution": dict(tier_distribution),
            "top_creators": [
                {"user_id": user_id, "score": score}
                for user_id, score in self.creator_rankings[:10]
            ]
        }
        
    async def _calculate_platform_analytics(self) -> Dict[str, Any]:
        """Calculate platform analytics"""
        platform_health = await self._calculate_platform_health_score()
        
        return {
            "platform_health_score": platform_health,
            "total_content_uploaded": self.real_time_stats["uploads_today"],
            "total_collaborations": self.real_time_stats["collaborations_today"],
            "active_sessions": self.real_time_stats["active_users_now"]
        }
        
    async def _generate_growth_predictions(self) -> Dict[str, Any]:
        """Generate growth predictions"""
        # Simple growth predictions (would use ML models in production)
        return {
            "predicted_revenue_next_month": "15000.00",
            "predicted_new_users_next_month": 150,
            "predicted_churn_rate": 0.05,
            "confidence_score": 0.75
        }
        
    async def _calculate_key_performance_indicators(self) -> Dict[str, float]:
        """Calculate key performance indicators"""
        total_revenue = float(sum(self.revenue_by_source.values()))
        total_users = len(self.user_engagement_scores)
        
        return {
            "monthly_recurring_revenue": total_revenue * 0.3,  # Estimate
            "customer_acquisition_cost": 25.0,
            "lifetime_value": 150.0,
            "churn_rate": 0.05,
            "net_promoter_score": 8.5,
            "revenue_per_user": total_revenue / max(total_users, 1),
            "creator_retention_rate": 0.85
        }
        
    async def _generate_retention_actions(
        self,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate retention actions based on risk factors"""
        actions = []
        
        if "low_engagement" in risk_factors:
            actions.extend([
                "Send personalized content recommendations",
                "Offer free premium features trial",
                "Schedule onboarding call"
            ])
            
        if "low_revenue" in risk_factors:
            actions.extend([
                "Provide monetization strategy guidance",
                "Connect with high-earning creators",
                "Offer collaboration opportunities"
            ])
            
        if "inactive" in risk_factors:
            actions.extend([
                "Send re-engagement email campaign",
                "Offer special incentives",
                "Request feedback survey"
            ])
            
        return actions
        
    async def _collection_loop(self) -> None:
        """Main collection loop for continuous metrics gathering"""
        while self.is_collecting:
            try:
                # Update real-time statistics
                await self._update_real_time_stats()
                
                # Update growth KPIs
                self.growth_kpis = await self._calculate_key_performance_indicators()
                
                # Cleanup old data
                await self._cleanup_old_metrics()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error in business metrics collection loop: {e}")
                await asyncio.sleep(120)  # Wait longer on error
                
    async def _update_real_time_stats(self) -> None:
        """Update real-time statistics"""
        current_time = datetime.utcnow()
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count today's metrics
        todays_revenue = sum(
            rev.amount for rev in self.revenue_metrics
            if rev.timestamp >= today_start
        )
        
        todays_uploads = len([
            eng for eng in self.engagement_metrics
            if eng.engagement_type == EngagementType.CONTENT_UPLOAD and
            eng.timestamp >= today_start
        ])
        
        todays_collaborations = len([
            eng for eng in self.engagement_metrics
            if eng.engagement_type in [EngagementType.COLLABORATION_REQUEST, EngagementType.COLLABORATION_ACCEPT] and
            eng.timestamp >= today_start
        ])
        
        # Update stats
        self.real_time_stats.update({
            "revenue_today": todays_revenue,
            "uploads_today": todays_uploads,
            "collaborations_today": todays_collaborations,
            "active_users_now": len([
                user_id for user_id, score in self.user_engagement_scores.items()
                if score > 0
            ])
        })
        
    async def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory buildup"""
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        
        # Clean revenue metrics
        while self.revenue_metrics and self.revenue_metrics[0].timestamp < cutoff_time:
            self.revenue_metrics.popleft()
            
        # Clean engagement metrics
        while self.engagement_metrics and self.engagement_metrics[0].timestamp < cutoff_time:
            self.engagement_metrics.popleft()
            
        # Clean platform metrics
        self.platform_metrics = [
            metrics for metrics in self.platform_metrics
            if metrics.timestamp >= cutoff_time
        ]


# Global business metrics collector instance
business_metrics_collector = BusinessMetricsCollector()
