"""
Gateway Analytics System - Comprehensive API Gateway Analytics
© 2025 Fahed Mlaiel. All rights reserved.

Enterprise analytics providing API usage analytics, platform performance dashboards,
revenue tracking, user behavior analytics, and predictive scaling metrics.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import statistics
from collections import defaultdict, deque
import time
import asyncio

logger = logging.getLogger(__name__)


class AnalyticsMetricType(Enum):
    """Analytics metric types"""
    API_USAGE = "api_usage"
    PERFORMANCE = "performance"
    REVENUE = "revenue"
    USER_BEHAVIOR = "user_behavior"
    SCALING = "scaling"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    THROUGHPUT = "throughput"


class TimeGranularity(Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class UserTier(Enum):
    """User tier for analytics"""
    FREE = "free"
    CREATOR = "creator"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    PLATFORM = "platform"


class APICategory(Enum):
    """API category for analytics"""
    CONTENT_UPLOAD = "content_upload"
    AI_PROCESSING = "ai_processing"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    PROTECTION = "protection"


@dataclass
class APIUsageMetric:
    """API usage metric"""
    endpoint: str
    method: str
    user_id: str
    user_tier: UserTier
    category: APICategory
    response_time_ms: float
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueMetric:
    """Revenue tracking metric"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str = "USD"
    transaction_type: str = ""
    platform_fee: float = 0.0
    creator_earning: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserBehaviorMetric:
    """User behavior metric"""
    user_id: str
    user_tier: UserTier
    session_id: str
    action: str
    page: str
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingMetric:
    """Predictive scaling metric"""
    metric_name: str
    current_value: float
    predicted_value: float
    threshold: float
    confidence: float
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnalyticsDashboard:
    """Analytics dashboard data"""
    dashboard_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    refresh_interval_seconds: int = 60
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class GatewayAnalytics:
    """
    Gateway Analytics System
    
    Provides comprehensive analytics for API gateway including:
    - API usage tracking and insights
    - Platform performance monitoring
    - Revenue tracking and analysis
    - User behavior analytics
    - Predictive scaling recommendations
    """
    
    def __init__(
        self,
        retention_days: int = 90,
        enable_predictive_scaling: bool = True,
        enable_revenue_tracking: bool = True,
        enable_user_behavior: bool = True
    ):
        """
        Initialize Gateway Analytics System
        
        Args:
            retention_days: Number of days to retain analytics data
            enable_predictive_scaling: Enable predictive scaling analytics
            enable_revenue_tracking: Enable revenue tracking
            enable_user_behavior: Enable user behavior analytics
        """
        self.retention_days = retention_days
        self.enable_predictive_scaling = enable_predictive_scaling
        self.enable_revenue_tracking = enable_revenue_tracking
        self.enable_user_behavior = enable_user_behavior
        
        # Analytics data storage
        self.api_usage_metrics: deque = deque(maxlen=1000000)
        self.revenue_metrics: deque = deque(maxlen=100000)
        self.user_behavior_metrics: deque = deque(maxlen=500000)
        self.scaling_metrics: deque = deque(maxlen=10000)
        
        # Aggregated data
        self.hourly_stats: Dict[str, Dict] = defaultdict(dict)
        self.daily_stats: Dict[str, Dict] = defaultdict(dict)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'total_request_size': 0,
            'total_response_size': 0
        })
        
        # User analytics
        self.user_stats: Dict[str, Dict] = defaultdict(lambda: {
            'request_count': 0,
            'total_revenue': 0.0,
            'avg_response_time': 0.0,
            'error_count': 0,
            'last_activity': None
        })
        
        # Platform performance
        self.platform_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Dashboards
        self.dashboards: Dict[str, AnalyticsDashboard] = {}
        
        # Predictive models
        self.scaling_predictions: Dict[str, List[float]] = defaultdict(list)
        
        logger.info("Gateway Analytics System initialized")
    
    def track_api_usage(self, metric: APIUsageMetric) -> None:
        """
        Track API usage metric
        
        Args:
            metric: API usage metric to track
        """
        try:
            self.api_usage_metrics.append(metric)
            
            # Update endpoint statistics
            endpoint_key = f"{metric.method}:{metric.endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_time'] += metric.response_time_ms
            stats['total_request_size'] += metric.request_size_bytes
            stats['total_response_size'] += metric.response_size_bytes
            if metric.status_code >= 400:
                stats['errors'] += 1
            
            # Update user statistics
            user_stats = self.user_stats[metric.user_id]
            user_stats['request_count'] += 1
            user_stats['last_activity'] = metric.timestamp
            if metric.status_code >= 400:
                user_stats['error_count'] += 1
            
            # Update hourly aggregation
            hour_key = metric.timestamp.strftime("%Y-%m-%d-%H")
            if hour_key not in self.hourly_stats:
                self.hourly_stats[hour_key] = {
                    'total_requests': 0,
                    'total_errors': 0,
                    'avg_response_time': 0.0,
                    'by_tier': defaultdict(int),
                    'by_category': defaultdict(int)
                }
            
            hour_stats = self.hourly_stats[hour_key]
            hour_stats['total_requests'] += 1
            if metric.status_code >= 400:
                hour_stats['total_errors'] += 1
            hour_stats['by_tier'][metric.user_tier.value] += 1
            hour_stats['by_category'][metric.category.value] += 1
            
            logger.debug(f"Tracked API usage: {endpoint_key}")
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {e}")
    
    def track_revenue(self, metric: RevenueMetric) -> None:
        """
        Track revenue metric
        
        Args:
            metric: Revenue metric to track
        """
        if not self.enable_revenue_tracking:
            return
        
        try:
            self.revenue_metrics.append(metric)
            
            # Update user revenue statistics
            user_stats = self.user_stats[metric.user_id]
            user_stats['total_revenue'] += metric.amount
            
            # Update daily revenue aggregation
            day_key = metric.timestamp.strftime("%Y-%m-%d")
            if day_key not in self.daily_stats:
                self.daily_stats[day_key] = {
                    'total_revenue': 0.0,
                    'transaction_count': 0,
                    'platform_fees': 0.0,
                    'creator_earnings': 0.0
                }
            
            day_stats = self.daily_stats[day_key]
            day_stats['total_revenue'] += metric.amount
            day_stats['transaction_count'] += 1
            day_stats['platform_fees'] += metric.platform_fee
            day_stats['creator_earnings'] += metric.creator_earning
            
            logger.debug(f"Tracked revenue: ${metric.amount:.2f}")
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
    
    def track_user_behavior(self, metric: UserBehaviorMetric) -> None:
        """
        Track user behavior metric
        
        Args:
            metric: User behavior metric to track
        """
        if not self.enable_user_behavior:
            return
        
        try:
            self.user_behavior_metrics.append(metric)
            logger.debug(f"Tracked user behavior: {metric.action}")
            
        except Exception as e:
            logger.error(f"Error tracking user behavior: {e}")
    
    def record_scaling_prediction(self, metric: ScalingMetric) -> None:
        """
        Record scaling prediction metric
        
        Args:
            metric: Scaling metric with prediction
        """
        if not self.enable_predictive_scaling:
            return
        
        try:
            self.scaling_metrics.append(metric)
            self.scaling_predictions[metric.metric_name].append(metric.predicted_value)
            
            logger.info(
                f"Scaling prediction: {metric.metric_name} - "
                f"Current: {metric.current_value:.2f}, "
                f"Predicted: {metric.predicted_value:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error recording scaling prediction: {e}")
    
    def get_api_usage_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        endpoint: Optional[str] = None,
        user_tier: Optional[UserTier] = None
    ) -> Dict[str, Any]:
        """
        Get API usage summary
        
        Args:
            start_time: Start time for summary
            end_time: End time for summary
            endpoint: Filter by endpoint
            user_tier: Filter by user tier
            
        Returns:
            API usage summary
        """
        try:
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=1)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Filter metrics
            filtered_metrics = [
                m for m in self.api_usage_metrics
                if start_time <= m.timestamp <= end_time
                and (not endpoint or m.endpoint == endpoint)
                and (not user_tier or m.user_tier == user_tier)
            ]
            
            if not filtered_metrics:
                return {
                    'total_requests': 0,
                    'error_count': 0,
                    'error_rate': 0.0,
                    'avg_response_time_ms': 0.0,
                    'requests_by_status': {},
                    'top_endpoints': []
                }
            
            # Calculate statistics
            total_requests = len(filtered_metrics)
            error_count = sum(1 for m in filtered_metrics if m.status_code >= 400)
            response_times = [m.response_time_ms for m in filtered_metrics]
            
            # Status code distribution
            status_distribution = defaultdict(int)
            for m in filtered_metrics:
                status_distribution[str(m.status_code)] += 1
            
            # Top endpoints
            endpoint_counts = defaultdict(int)
            for m in filtered_metrics:
                endpoint_counts[m.endpoint] += 1
            top_endpoints = sorted(
                endpoint_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                'total_requests': total_requests,
                'error_count': error_count,
                'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0.0,
                'avg_response_time_ms': statistics.mean(response_times) if response_times else 0.0,
                'median_response_time_ms': statistics.median(response_times) if response_times else 0.0,
                'p95_response_time_ms': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0.0,
                'p99_response_time_ms': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0.0,
                'requests_by_status': dict(status_distribution),
                'top_endpoints': [{'endpoint': e, 'count': c} for e, c in top_endpoints],
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting API usage summary: {e}")
            return {}
    
    def get_platform_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get platform performance dashboard data
        
        Returns:
            Platform performance dashboard data
        """
        try:
            now = datetime.utcnow()
            last_hour = now - timedelta(hours=1)
            
            recent_metrics = [
                m for m in self.api_usage_metrics
                if m.timestamp >= last_hour
            ]
            
            if not recent_metrics:
                return {
                    'status': 'no_data',
                    'message': 'No recent data available'
                }
            
            # Calculate performance metrics
            response_times = [m.response_time_ms for m in recent_metrics]
            total_requests = len(recent_metrics)
            error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
            
            # Throughput calculation
            time_span_minutes = (now - last_hour).total_seconds() / 60
            throughput = total_requests / time_span_minutes if time_span_minutes > 0 else 0
            
            # Category distribution
            category_dist = defaultdict(int)
            for m in recent_metrics:
                category_dist[m.category.value] += 1
            
            return {
                'status': 'healthy',
                'timestamp': now.isoformat(),
                'metrics': {
                    'total_requests': total_requests,
                    'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0.0,
                    'avg_response_time_ms': statistics.mean(response_times) if response_times else 0.0,
                    'throughput_rpm': round(throughput, 2),
                    'p95_latency_ms': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0.0
                },
                'category_distribution': dict(category_dist),
                'time_range': 'Last 1 Hour'
            }
            
        except Exception as e:
            logger.error(f"Error getting platform performance dashboard: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_revenue_tracking_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get revenue tracking summary
        
        Args:
            start_date: Start date for summary
            end_date: End date for summary
            
        Returns:
            Revenue tracking summary
        """
        if not self.enable_revenue_tracking:
            return {'status': 'disabled'}
        
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter metrics
            filtered_metrics = [
                m for m in self.revenue_metrics
                if start_date <= m.timestamp <= end_date
            ]
            
            if not filtered_metrics:
                return {
                    'total_revenue': 0.0,
                    'transaction_count': 0,
                    'avg_transaction_value': 0.0
                }
            
            total_revenue = sum(m.amount for m in filtered_metrics)
            total_platform_fees = sum(m.platform_fee for m in filtered_metrics)
            total_creator_earnings = sum(m.creator_earning for m in filtered_metrics)
            transaction_count = len(filtered_metrics)
            
            # Daily breakdown
            daily_revenue = defaultdict(float)
            for m in filtered_metrics:
                day_key = m.timestamp.strftime("%Y-%m-%d")
                daily_revenue[day_key] += m.amount
            
            return {
                'total_revenue': round(total_revenue, 2),
                'total_platform_fees': round(total_platform_fees, 2),
                'total_creator_earnings': round(total_creator_earnings, 2),
                'transaction_count': transaction_count,
                'avg_transaction_value': round(total_revenue / transaction_count, 2) if transaction_count > 0 else 0.0,
                'daily_revenue': {k: round(v, 2) for k, v in sorted(daily_revenue.items())},
                'time_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue tracking summary: {e}")
            return {}
    
    def get_user_behavior_insights(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get user behavior insights
        
        Args:
            user_id: Filter by user ID
            limit: Maximum number of insights to return
            
        Returns:
            User behavior insights
        """
        if not self.enable_user_behavior:
            return {'status': 'disabled'}
        
        try:
            # Filter metrics
            filtered_metrics = [
                m for m in list(self.user_behavior_metrics)[-10000:]
                if not user_id or m.user_id == user_id
            ][:limit]
            
            if not filtered_metrics:
                return {
                    'unique_users': 0,
                    'total_actions': 0,
                    'top_actions': []
                }
            
            unique_users = len(set(m.user_id for m in filtered_metrics))
            
            # Action distribution
            action_dist = defaultdict(int)
            for m in filtered_metrics:
                action_dist[m.action] += 1
            
            top_actions = sorted(
                action_dist.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Page distribution
            page_dist = defaultdict(int)
            for m in filtered_metrics:
                page_dist[m.page] += 1
            
            return {
                'unique_users': unique_users,
                'total_actions': len(filtered_metrics),
                'top_actions': [{'action': a, 'count': c} for a, c in top_actions],
                'page_distribution': dict(page_dist),
                'avg_session_duration': statistics.mean([m.duration_seconds for m in filtered_metrics]) if filtered_metrics else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior insights: {e}")
            return {}
    
    def get_predictive_scaling_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get predictive scaling recommendations
        
        Returns:
            List of scaling recommendations
        """
        if not self.enable_predictive_scaling:
            return []
        
        try:
            recommendations = []
            
            # Analyze recent API usage trends
            recent_hours = []
            now = datetime.utcnow()
            for i in range(24):
                hour_key = (now - timedelta(hours=i)).strftime("%Y-%m-%d-%H")
                if hour_key in self.hourly_stats:
                    recent_hours.append(self.hourly_stats[hour_key]['total_requests'])
            
            if len(recent_hours) >= 3:
                # Simple trend analysis
                avg_requests = statistics.mean(recent_hours)
                recent_avg = statistics.mean(recent_hours[:3])
                
                if recent_avg > avg_requests * 1.5:
                    recommendations.append({
                        'type': 'scale_up',
                        'metric': 'request_rate',
                        'current_value': recent_avg,
                        'threshold': avg_requests * 1.5,
                        'confidence': 0.85,
                        'recommendation': 'Increase capacity by 50%',
                        'reason': 'Request rate significantly above average'
                    })
                elif recent_avg < avg_requests * 0.5:
                    recommendations.append({
                        'type': 'scale_down',
                        'metric': 'request_rate',
                        'current_value': recent_avg,
                        'threshold': avg_requests * 0.5,
                        'confidence': 0.75,
                        'recommendation': 'Decrease capacity by 25%',
                        'reason': 'Request rate significantly below average'
                    })
            
            # Add recent scaling metrics
            for metric in list(self.scaling_metrics)[-10:]:
                recommendations.append({
                    'type': 'prediction',
                    'metric': metric.metric_name,
                    'current_value': metric.current_value,
                    'predicted_value': metric.predicted_value,
                    'threshold': metric.threshold,
                    'confidence': metric.confidence,
                    'recommendation': metric.recommendation
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting predictive scaling recommendations: {e}")
            return []
    
    def create_dashboard(
        self,
        name: str,
        description: str,
        widgets: List[Dict[str, Any]]
    ) -> str:
        """
        Create a custom analytics dashboard
        
        Args:
            name: Dashboard name
            description: Dashboard description
            widgets: List of dashboard widgets
            
        Returns:
            Dashboard ID
        """
        try:
            dashboard = AnalyticsDashboard(
                name=name,
                description=description,
                widgets=widgets
            )
            
            self.dashboards[dashboard.dashboard_id] = dashboard
            logger.info(f"Created dashboard: {name}")
            
            return dashboard.dashboard_id
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dashboard data
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard data or None if not found
        """
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        return {
            'dashboard_id': dashboard.dashboard_id,
            'name': dashboard.name,
            'description': dashboard.description,
            'widgets': dashboard.widgets,
            'refresh_interval_seconds': dashboard.refresh_interval_seconds,
            'created_at': dashboard.created_at.isoformat(),
            'updated_at': dashboard.updated_at.isoformat()
        }
    
    def get_creator_insights(self, creator_id: str) -> Dict[str, Any]:
        """
        Get comprehensive insights for a creator
        
        Args:
            creator_id: Creator user ID
            
        Returns:
            Creator insights including usage, revenue, and behavior
        """
        try:
            # Get user stats
            user_stats = self.user_stats.get(creator_id, {})
            
            # Get revenue data
            creator_revenue = [
                m for m in self.revenue_metrics
                if m.user_id == creator_id
            ]
            total_revenue = sum(m.amount for m in creator_revenue)
            
            # Get API usage
            creator_api_usage = [
                m for m in self.api_usage_metrics
                if m.user_id == creator_id
            ]
            
            return {
                'creator_id': creator_id,
                'api_usage': {
                    'total_requests': user_stats.get('request_count', 0),
                    'error_count': user_stats.get('error_count', 0),
                    'last_activity': user_stats.get('last_activity').isoformat() if user_stats.get('last_activity') else None
                },
                'revenue': {
                    'total_earnings': round(total_revenue, 2),
                    'transaction_count': len(creator_revenue)
                },
                'performance': {
                    'avg_response_time': user_stats.get('avg_response_time', 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting creator insights: {e}")
            return {}
    
    def cleanup_old_data(self) -> None:
        """Clean up old analytics data based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Clean up hourly stats
            old_hours = [
                k for k in self.hourly_stats.keys()
                if datetime.strptime(k, "%Y-%m-%d-%H") < cutoff_date
            ]
            for hour in old_hours:
                del self.hourly_stats[hour]
            
            # Clean up daily stats
            old_days = [
                k for k in self.daily_stats.keys()
                if datetime.strptime(k, "%Y-%m-%d") < cutoff_date
            ]
            for day in old_days:
                del self.daily_stats[day]
            
            logger.info(f"Cleaned up analytics data older than {self.retention_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")


# Creator platform analytics configuration
IACHERIE_ANALYTICS_CONFIG = {
    'enabled_features': {
        'api_usage_tracking': True,
        'revenue_tracking': True,
        'user_behavior_analytics': True,
        'predictive_scaling': True,
        'creator_insights': True
    },
    'retention_policy': {
        'raw_metrics_days': 90,
        'aggregated_stats_days': 365,
        'dashboard_data_days': 180
    },
    'dashboards': {
        'creator_dashboard': {
            'widgets': ['revenue', 'api_usage', 'content_performance'],
            'refresh_interval': 60
        },
        'platform_dashboard': {
            'widgets': ['global_performance', 'scaling_metrics', 'error_rates'],
            'refresh_interval': 30
        },
        'admin_dashboard': {
            'widgets': ['all_creators', 'revenue_summary', 'system_health'],
            'refresh_interval': 120
        }
    },
    'alerts': {
        'revenue_drop_threshold': 0.3,  # 30% drop triggers alert
        'error_rate_threshold': 0.05,   # 5% error rate triggers alert
        'scaling_threshold': 0.8         # 80% capacity triggers scaling alert
    }
}
