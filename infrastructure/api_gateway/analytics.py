"""
Gateway Analytics - Advanced API Analytics & Business Intelligence
© 2025 Fahed Mlaiel. All rights reserved.

Gateway analytics providing API usage insights, performance dashboards,
revenue tracking, user behavior analytics, and predictive scaling metrics.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import time
import statistics
from collections import defaultdict, deque
import threading
from decimal import Decimal

logger = logging.getLogger(__name__)


class AnalyticsPeriod(Enum):
    """Analytics time periods"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AnalyticsMetricType(Enum):
    """Analytics metric types"""
    API_USAGE = "api_usage"
    USER_BEHAVIOR = "user_behavior"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    ERROR_RATE = "error_rate"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"


class UserTier(Enum):
    """User subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CREATOR_PRO = "creator_pro"


class RevenueSource(Enum):
    """Revenue sources"""
    SUBSCRIPTION = "subscription"
    API_USAGE = "api_usage"
    PREMIUM_FEATURES = "premium_features"
    ENTERPRISE_SUPPORT = "enterprise_support"
    MARKETPLACE = "marketplace"
    ADVERTISING = "advertising"


@dataclass
class APIUsageMetric:
    """API usage analytics metric"""
    endpoint: str
    method: str
    user_id: Optional[str] = None
    user_tier: Optional[UserTier] = None
    requests_count: int = 0
    bytes_transferred: int = 0
    response_time_ms: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserBehaviorMetric:
    """User behavior analytics metric"""
    user_id: str
    session_id: str
    user_tier: UserTier
    actions_performed: List[str] = field(default_factory=list)
    pages_visited: List[str] = field(default_factory=list)
    time_spent_minutes: float = 0.0
    features_used: Set[str] = field(default_factory=set)
    conversion_events: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueMetric:
    """Revenue analytics metric"""
    user_id: str
    source: RevenueSource
    amount: Decimal
    currency: str = "USD"
    user_tier: Optional[UserTier] = None
    subscription_period: Optional[str] = None
    api_calls_count: Optional[int] = None
    features_used: Set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """Performance analytics metric"""
    service_name: str
    metric_name: str
    value: float
    unit: str
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    avg_value: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictiveInsight:
    """Predictive analytics insight"""
    insight_type: str
    prediction: str
    confidence_score: float
    time_horizon: str
    recommended_actions: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class GatewayAnalytics:
    """
    Gateway Analytics Engine
    
    Provides comprehensive analytics for:
    - API usage patterns and trends
    - User behavior analysis
    - Revenue tracking and optimization
    - Performance insights
    - Predictive scaling recommendations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize analytics engine"""
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Analytics storage
        self.api_usage_metrics: deque = deque(maxlen=10000)
        self.user_behavior_metrics: deque = deque(maxlen=5000)
        self.revenue_metrics: deque = deque(maxlen=2000)
        self.performance_metrics: deque = deque(maxlen=10000)
        self.predictive_insights: List[PredictiveInsight] = []
        
        # Aggregated data
        self.hourly_aggregates: Dict[str, Dict] = defaultdict(dict)
        self.daily_aggregates: Dict[str, Dict] = defaultdict(dict)
        self.monthly_aggregates: Dict[str, Dict] = defaultdict(dict)
        
        # Real-time counters
        self.real_time_counters: Dict[str, int] = defaultdict(int)
        self.active_users: Set[str] = set()
        self.active_sessions: Dict[str, datetime] = {}
        
        # Analytics configuration
        self.retention_days = self.config.get('retention_days', 90)
        self.aggregation_interval = self.config.get('aggregation_interval', 300)  # 5 minutes
        self.prediction_interval = self.config.get('prediction_interval', 3600)  # 1 hour
        
        # Threading for background processing
        self._analytics_lock = threading.RLock()
        self._running = False
        self._analytics_task: Optional[asyncio.Task] = None
        
        self.logger.info("Gateway Analytics initialized")
    
    async def start(self):
        """Start analytics engine"""
        if self._running:
            return
        
        self._running = True
        self._analytics_task = asyncio.create_task(self._analytics_worker())
        self.logger.info("Gateway Analytics engine started")
    
    async def stop(self):
        """Stop analytics engine"""
        if not self._running:
            return
        
        self._running = False
        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Gateway Analytics engine stopped")
    
    async def record_api_usage(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        user_tier: Optional[UserTier] = None,
        response_time_ms: float = 0.0,
        bytes_transferred: int = 0,
        status_code: int = 200,
        **metadata
    ):
        """Record API usage metrics"""
        try:
            with self._analytics_lock:
                metric = APIUsageMetric(
                    endpoint=endpoint,
                    method=method,
                    user_id=user_id,
                    user_tier=user_tier,
                    requests_count=1,
                    bytes_transferred=bytes_transferred,
                    response_time_ms=response_time_ms,
                    error_count=1 if status_code >= 400 else 0,
                    success_rate=0.0 if status_code >= 400 else 100.0,
                    metadata=metadata
                )
                
                self.api_usage_metrics.append(metric)
                
                # Update real-time counters
                endpoint_key = f"{method}:{endpoint}"
                self.real_time_counters[f"api_calls:{endpoint_key}"] += 1
                self.real_time_counters[f"bytes_transferred:{endpoint_key}"] += bytes_transferred
                
                if status_code >= 400:
                    self.real_time_counters[f"errors:{endpoint_key}"] += 1
                
                if user_id:
                    self.active_users.add(user_id)
                    self.real_time_counters[f"unique_users:{user_tier.value if user_tier else 'unknown'}"] = len(self.active_users)
                
                self.logger.debug(f"Recorded API usage: {endpoint_key} by user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to record API usage: {e}")
    
    async def record_user_behavior(
        self,
        user_id: str,
        session_id: str,
        user_tier: UserTier,
        action: str,
        page: Optional[str] = None,
        feature: Optional[str] = None,
        time_spent_minutes: float = 0.0,
        **metadata
    ):
        """Record user behavior metrics"""
        try:
            with self._analytics_lock:
                # Find or create behavior metric for this session
                existing_metric = None
                for metric in reversed(self.user_behavior_metrics):
                    if metric.session_id == session_id and metric.user_id == user_id:
                        existing_metric = metric
                        break
                
                if existing_metric:
                    existing_metric.actions_performed.append(action)
                    if page:
                        existing_metric.pages_visited.append(page)
                    if feature:
                        existing_metric.features_used.add(feature)
                    existing_metric.time_spent_minutes += time_spent_minutes
                    existing_metric.metadata.update(metadata)
                else:
                    metric = UserBehaviorMetric(
                        user_id=user_id,
                        session_id=session_id,
                        user_tier=user_tier,
                        actions_performed=[action],
                        pages_visited=[page] if page else [],
                        time_spent_minutes=time_spent_minutes,
                        features_used={feature} if feature else set(),
                        metadata=metadata
                    )
                    self.user_behavior_metrics.append(metric)
                
                # Update session tracking
                self.active_sessions[session_id] = datetime.utcnow()
                
                # Update real-time counters
                self.real_time_counters[f"user_actions:{action}"] += 1
                if feature:
                    self.real_time_counters[f"feature_usage:{feature}"] += 1
                
                self.logger.debug(f"Recorded user behavior: {action} by user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to record user behavior: {e}")
    
    async def record_revenue(
        self,
        user_id: str,
        source: RevenueSource,
        amount: Union[float, Decimal],
        currency: str = "USD",
        user_tier: Optional[UserTier] = None,
        **metadata
    ):
        """Record revenue metrics"""
        try:
            with self._analytics_lock:
                metric = RevenueMetric(
                    user_id=user_id,
                    source=source,
                    amount=Decimal(str(amount)),
                    currency=currency,
                    user_tier=user_tier,
                    metadata=metadata
                )
                
                self.revenue_metrics.append(metric)
                
                # Update real-time counters
                self.real_time_counters[f"revenue:{source.value}"] += float(amount)
                self.real_time_counters[f"revenue_total"] += float(amount)
                if user_tier:
                    self.real_time_counters[f"revenue_by_tier:{user_tier.value}"] += float(amount)
                
                self.logger.info(f"Recorded revenue: {amount} {currency} from {source.value} by user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to record revenue: {e}")
    
    async def record_performance_metric(
        self,
        service_name: str,
        metric_name: str,
        value: float,
        unit: str = "",
        **metadata
    ):
        """Record performance metrics"""
        try:
            with self._analytics_lock:
                metric = PerformanceMetric(
                    service_name=service_name,
                    metric_name=metric_name,
                    value=value,
                    unit=unit,
                    metadata=metadata
                )
                
                self.performance_metrics.append(metric)
                
                # Update real-time counters
                self.real_time_counters[f"performance:{service_name}:{metric_name}"] = value
                
                self.logger.debug(f"Recorded performance metric: {service_name}.{metric_name} = {value} {unit}")
                
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
    
    async def get_api_usage_analytics(
        self,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get API usage analytics"""
        try:
            with self._analytics_lock:
                end_time = end_time or datetime.utcnow()
                
                if period == AnalyticsPeriod.REAL_TIME:
                    start_time = end_time - timedelta(minutes=5)
                elif period == AnalyticsPeriod.HOURLY:
                    start_time = start_time or (end_time - timedelta(hours=1))
                elif period == AnalyticsPeriod.DAILY:
                    start_time = start_time or (end_time - timedelta(days=1))
                elif period == AnalyticsPeriod.WEEKLY:
                    start_time = start_time or (end_time - timedelta(weeks=1))
                elif period == AnalyticsPeriod.MONTHLY:
                    start_time = start_time or (end_time - timedelta(days=30))
                
                # Filter metrics by time range
                filtered_metrics = [
                    m for m in self.api_usage_metrics
                    if start_time <= m.timestamp <= end_time
                ]
                
                # Aggregate data
                total_requests = sum(m.requests_count for m in filtered_metrics)
                total_errors = sum(m.error_count for m in filtered_metrics)
                total_bytes = sum(m.bytes_transferred for m in filtered_metrics)
                
                response_times = [m.response_time_ms for m in filtered_metrics if m.response_time_ms > 0]
                avg_response_time = statistics.mean(response_times) if response_times else 0
                p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0
                
                # Endpoint breakdown
                endpoint_stats = defaultdict(lambda: {"requests": 0, "errors": 0, "avg_response_time": 0})
                for metric in filtered_metrics:
                    key = f"{metric.method}:{metric.endpoint}"
                    endpoint_stats[key]["requests"] += metric.requests_count
                    endpoint_stats[key]["errors"] += metric.error_count
                    if metric.response_time_ms > 0:
                        endpoint_stats[key]["avg_response_time"] = (
                            endpoint_stats[key]["avg_response_time"] + metric.response_time_ms
                        ) / 2
                
                # User tier breakdown
                tier_stats = defaultdict(lambda: {"requests": 0, "unique_users": set()})
                for metric in filtered_metrics:
                    if metric.user_tier and metric.user_id:
                        tier_stats[metric.user_tier.value]["requests"] += metric.requests_count
                        tier_stats[metric.user_tier.value]["unique_users"].add(metric.user_id)
                
                # Convert sets to counts
                for tier in tier_stats:
                    tier_stats[tier]["unique_users"] = len(tier_stats[tier]["unique_users"])
                
                return {
                    "period": period.value,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "summary": {
                        "total_requests": total_requests,
                        "total_errors": total_errors,
                        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                        "total_bytes_transferred": total_bytes,
                        "average_response_time_ms": avg_response_time,
                        "p95_response_time_ms": p95_response_time,
                        "unique_users": len(set(m.user_id for m in filtered_metrics if m.user_id))
                    },
                    "endpoint_breakdown": dict(endpoint_stats),
                    "user_tier_breakdown": dict(tier_stats),
                    "real_time_counters": dict(self.real_time_counters)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get API usage analytics: {e}")
            return {"error": str(e)}
    
    async def get_user_behavior_analytics(
        self,
        period: AnalyticsPeriod = AnalyticsPeriod.DAILY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get user behavior analytics"""
        try:
            with self._analytics_lock:
                end_time = end_time or datetime.utcnow()
                
                if period == AnalyticsPeriod.DAILY:
                    start_time = start_time or (end_time - timedelta(days=1))
                elif period == AnalyticsPeriod.WEEKLY:
                    start_time = start_time or (end_time - timedelta(weeks=1))
                elif period == AnalyticsPeriod.MONTHLY:
                    start_time = start_time or (end_time - timedelta(days=30))
                
                # Filter metrics by time range
                filtered_metrics = [
                    m for m in self.user_behavior_metrics
                    if start_time <= m.timestamp <= end_time
                ]
                
                # Aggregate data
                total_sessions = len(filtered_metrics)
                unique_users = len(set(m.user_id for m in filtered_metrics))
                total_actions = sum(len(m.actions_performed) for m in filtered_metrics)
                total_time_spent = sum(m.time_spent_minutes for m in filtered_metrics)
                
                # Feature usage
                feature_usage = defaultdict(int)
                action_counts = defaultdict(int)
                
                for metric in filtered_metrics:
                    for feature in metric.features_used:
                        feature_usage[feature] += 1
                    for action in metric.actions_performed:
                        action_counts[action] += 1
                
                # User tier analysis
                tier_behavior = defaultdict(lambda: {
                    "sessions": 0,
                    "total_time": 0,
                    "actions": 0,
                    "features": set()
                })
                
                for metric in filtered_metrics:
                    tier = metric.user_tier.value
                    tier_behavior[tier]["sessions"] += 1
                    tier_behavior[tier]["total_time"] += metric.time_spent_minutes
                    tier_behavior[tier]["actions"] += len(metric.actions_performed)
                    tier_behavior[tier]["features"].update(metric.features_used)
                
                # Convert sets to counts
                for tier in tier_behavior:
                    tier_behavior[tier]["features"] = len(tier_behavior[tier]["features"])
                
                return {
                    "period": period.value,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "summary": {
                        "total_sessions": total_sessions,
                        "unique_users": unique_users,
                        "total_actions": total_actions,
                        "total_time_spent_minutes": total_time_spent,
                        "avg_session_duration": total_time_spent / total_sessions if total_sessions > 0 else 0,
                        "avg_actions_per_session": total_actions / total_sessions if total_sessions > 0 else 0
                    },
                    "feature_usage": dict(feature_usage),
                    "action_breakdown": dict(action_counts),
                    "user_tier_behavior": dict(tier_behavior),
                    "active_sessions": len(self.active_sessions)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get user behavior analytics: {e}")
            return {"error": str(e)}
    
    async def get_revenue_analytics(
        self,
        period: AnalyticsPeriod = AnalyticsPeriod.MONTHLY,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get revenue analytics"""
        try:
            with self._analytics_lock:
                end_time = end_time or datetime.utcnow()
                
                if period == AnalyticsPeriod.DAILY:
                    start_time = start_time or (end_time - timedelta(days=1))
                elif period == AnalyticsPeriod.WEEKLY:
                    start_time = start_time or (end_time - timedelta(weeks=1))
                elif period == AnalyticsPeriod.MONTHLY:
                    start_time = start_time or (end_time - timedelta(days=30))
                elif period == AnalyticsPeriod.QUARTERLY:
                    start_time = start_time or (end_time - timedelta(days=90))
                elif period == AnalyticsPeriod.YEARLY:
                    start_time = start_time or (end_time - timedelta(days=365))
                
                # Filter metrics by time range
                filtered_metrics = [
                    m for m in self.revenue_metrics
                    if start_time <= m.timestamp <= end_time
                ]
                
                # Aggregate data
                total_revenue = sum(float(m.amount) for m in filtered_metrics)
                unique_paying_users = len(set(m.user_id for m in filtered_metrics))
                
                # Revenue by source
                source_revenue = defaultdict(float)
                for metric in filtered_metrics:
                    source_revenue[metric.source.value] += float(metric.amount)
                
                # Revenue by user tier
                tier_revenue = defaultdict(float)
                tier_users = defaultdict(set)
                for metric in filtered_metrics:
                    if metric.user_tier:
                        tier_revenue[metric.user_tier.value] += float(metric.amount)
                        tier_users[metric.user_tier.value].add(metric.user_id)
                
                # Convert sets to counts
                tier_stats = {}
                for tier in tier_revenue:
                    tier_stats[tier] = {
                        "revenue": tier_revenue[tier],
                        "unique_users": len(tier_users[tier]),
                        "avg_revenue_per_user": tier_revenue[tier] / len(tier_users[tier]) if tier_users[tier] else 0
                    }
                
                # Monthly recurring revenue (MRR) estimation
                subscription_revenue = sum(
                    float(m.amount) for m in filtered_metrics
                    if m.source == RevenueSource.SUBSCRIPTION
                )
                
                # Calculate average revenue per user (ARPU)
                arpu = total_revenue / unique_paying_users if unique_paying_users > 0 else 0
                
                return {
                    "period": period.value,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "summary": {
                        "total_revenue": total_revenue,
                        "unique_paying_users": unique_paying_users,
                        "average_revenue_per_user": arpu,
                        "subscription_revenue": subscription_revenue,
                        "estimated_mrr": subscription_revenue * (30 / (end_time - start_time).days) if (end_time - start_time).days > 0 else 0
                    },
                    "revenue_by_source": dict(source_revenue),
                    "revenue_by_tier": tier_stats,
                    "growth_metrics": {
                        "revenue_growth_rate": 0,  # Would need historical data
                        "user_acquisition_cost": 0,  # Would need marketing spend data
                        "customer_lifetime_value": 0  # Would need retention data
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get revenue analytics: {e}")
            return {"error": str(e)}
    
    async def get_predictive_insights(self) -> List[Dict[str, Any]]:
        """Get predictive analytics insights"""
        try:
            insights = []
            
            # Generate scaling predictions based on current trends
            current_usage = self.real_time_counters.get("api_calls_total", 0)
            if current_usage > 0:
                # Simple trend-based prediction
                predicted_growth = current_usage * 1.2  # 20% growth assumption
                
                if predicted_growth > 10000:  # Threshold for scaling
                    insight = PredictiveInsight(
                        insight_type="scaling_recommendation",
                        prediction=f"API traffic expected to reach {predicted_growth:.0f} requests/hour",
                        confidence_score=0.75,
                        time_horizon="next_24_hours",
                        recommended_actions=[
                            "Consider increasing server capacity",
                            "Review rate limiting thresholds",
                            "Enable auto-scaling policies"
                        ],
                        supporting_data={
                            "current_usage": current_usage,
                            "predicted_usage": predicted_growth,
                            "growth_rate": 20
                        }
                    )
                    insights.append(insight)
            
            # Revenue optimization insights
            total_revenue = self.real_time_counters.get("revenue_total", 0)
            if total_revenue > 0:
                insight = PredictiveInsight(
                    insight_type="revenue_optimization",
                    prediction="Premium tier users generate 5x more revenue per API call",
                    confidence_score=0.85,
                    time_horizon="ongoing",
                    recommended_actions=[
                        "Focus marketing on premium tier conversion",
                        "Optimize premium features based on usage patterns",
                        "Implement usage-based pricing models"
                    ],
                    supporting_data={
                        "total_revenue": total_revenue,
                        "revenue_per_tier": dict(self.real_time_counters)
                    }
                )
                insights.append(insight)
            
            # Performance optimization insights
            avg_response_time = self.real_time_counters.get("performance:api_gateway:avg_response_time", 0)
            if avg_response_time > 500:  # 500ms threshold
                insight = PredictiveInsight(
                    insight_type="performance_optimization",
                    prediction=f"Response time trending upward ({avg_response_time:.0f}ms average)",
                    confidence_score=0.90,
                    time_horizon="immediate",
                    recommended_actions=[
                        "Investigate slow endpoints",
                        "Optimize database queries",
                        "Consider implementing caching",
                        "Review resource allocation"
                    ],
                    supporting_data={
                        "avg_response_time": avg_response_time,
                        "threshold": 500
                    }
                )
                insights.append(insight)
            
            # Store insights
            with self._analytics_lock:
                self.predictive_insights.extend(insights)
                # Keep only recent insights
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.predictive_insights = [
                    i for i in self.predictive_insights
                    if i.created_at > cutoff_time
                ]
            
            return [
                {
                    "insight_type": i.insight_type,
                    "prediction": i.prediction,
                    "confidence_score": i.confidence_score,
                    "time_horizon": i.time_horizon,
                    "recommended_actions": i.recommended_actions,
                    "supporting_data": i.supporting_data,
                    "created_at": i.created_at.isoformat()
                }
                for i in insights
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to generate predictive insights: {e}")
            return []
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get analytics for different periods
            daily_api = await self.get_api_usage_analytics(AnalyticsPeriod.DAILY)
            daily_behavior = await self.get_user_behavior_analytics(AnalyticsPeriod.DAILY)
            monthly_revenue = await self.get_revenue_analytics(AnalyticsPeriod.MONTHLY)
            insights = await self.get_predictive_insights()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "real_time_metrics": {
                    "active_users": len(self.active_users),
                    "active_sessions": len(self.active_sessions),
                    "total_api_calls": self.real_time_counters.get("api_calls_total", 0),
                    "total_revenue": self.real_time_counters.get("revenue_total", 0),
                    "current_error_rate": self.real_time_counters.get("error_rate", 0)
                },
                "daily_api_usage": daily_api,
                "daily_user_behavior": daily_behavior,
                "monthly_revenue": monthly_revenue,
                "predictive_insights": insights,
                "system_health": {
                    "analytics_engine_status": "running" if self._running else "stopped",
                    "metrics_collected": {
                        "api_usage": len(self.api_usage_metrics),
                        "user_behavior": len(self.user_behavior_metrics),
                        "revenue": len(self.revenue_metrics),
                        "performance": len(self.performance_metrics)
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    async def _analytics_worker(self):
        """Background analytics processing worker"""
        while self._running:
            try:
                await self._process_aggregations()
                await self._cleanup_old_data()
                await self._update_predictive_models()
                
                await asyncio.sleep(self.aggregation_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Analytics worker error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_aggregations(self):
        """Process data aggregations"""
        try:
            current_time = datetime.utcnow()
            hour_key = current_time.strftime("%Y-%m-%d-%H")
            day_key = current_time.strftime("%Y-%m-%d")
            month_key = current_time.strftime("%Y-%m")
            
            # Hourly aggregations
            if hour_key not in self.hourly_aggregates:
                hourly_metrics = [
                    m for m in self.api_usage_metrics
                    if m.timestamp.strftime("%Y-%m-%d-%H") == hour_key
                ]
                
                self.hourly_aggregates[hour_key] = {
                    "total_requests": sum(m.requests_count for m in hourly_metrics),
                    "total_errors": sum(m.error_count for m in hourly_metrics),
                    "avg_response_time": statistics.mean([m.response_time_ms for m in hourly_metrics if m.response_time_ms > 0]) if hourly_metrics else 0
                }
            
            # Daily aggregations
            if day_key not in self.daily_aggregates:
                daily_metrics = [
                    m for m in self.api_usage_metrics
                    if m.timestamp.strftime("%Y-%m-%d") == day_key
                ]
                
                self.daily_aggregates[day_key] = {
                    "total_requests": sum(m.requests_count for m in daily_metrics),
                    "unique_users": len(set(m.user_id for m in daily_metrics if m.user_id)),
                    "total_revenue": sum(float(m.amount) for m in self.revenue_metrics if m.timestamp.strftime("%Y-%m-%d") == day_key)
                }
            
            self.logger.debug(f"Processed aggregations for {current_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to process aggregations: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old metrics data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
            
            with self._analytics_lock:
                # Clean up old sessions
                expired_sessions = [
                    sid for sid, last_active in self.active_sessions.items()
                    if last_active < datetime.utcnow() - timedelta(hours=1)
                ]
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                
                # Clean up old aggregates
                for agg_dict in [self.hourly_aggregates, self.daily_aggregates, self.monthly_aggregates]:
                    expired_keys = [
                        key for key in agg_dict.keys()
                        if datetime.strptime(key.split('-')[0:3] if len(key.split('-')) >= 3 else key.split('-')[0:2], 
                                          "%Y-%m-%d" if len(key.split('-')) >= 3 else "%Y-%m") < cutoff_time
                    ]
                    
                    for key in expired_keys:
                        del agg_dict[key]
            
            self.logger.debug(f"Cleaned up data older than {cutoff_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    async def _update_predictive_models(self):
        """Update predictive analytics models"""
        try:
            # This would integrate with ML models for more sophisticated predictions
            # For now, we update simple trend-based predictions
            
            # Update total counters
            with self._analytics_lock:
                total_requests = sum(m.requests_count for m in self.api_usage_metrics)
                total_errors = sum(m.error_count for m in self.api_usage_metrics)
                
                self.real_time_counters["api_calls_total"] = total_requests
                self.real_time_counters["errors_total"] = total_errors
                self.real_time_counters["error_rate"] = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            self.logger.debug("Updated predictive models")
            
        except Exception as e:
            self.logger.error(f"Failed to update predictive models: {e}")


# Example usage
if __name__ == "__main__":
    async def main():
        analytics = GatewayAnalytics()
        await analytics.start()
        
        # Simulate some data
        await analytics.record_api_usage(
            endpoint="/api/v1/content/generate",
            method="POST",
            user_id="user123",
            user_tier=UserTier.PREMIUM,
            response_time_ms=250,
            bytes_transferred=1024,
            status_code=200
        )
        
        await analytics.record_revenue(
            user_id="user123",
            source=RevenueSource.SUBSCRIPTION,
            amount=29.99,
            user_tier=UserTier.PREMIUM
        )
        
        # Get analytics
        dashboard_data = await analytics.get_dashboard_data()
        print(json.dumps(dashboard_data, indent=2, default=str))
        
        await analytics.stop()
    
    asyncio.run(main())