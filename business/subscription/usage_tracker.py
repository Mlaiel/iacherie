"""Usage Tracker

Real-time usage tracking and quota management system for subscription features.
Monitors feature usage, enforces limits, and provides usage analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
import logging
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .models import (
    UserSubscription, SubscriptionPlan, UsageMetrics, 
    SubscriptionStatus, UsageQuota
)
from ..core.database import get_db_session
from ..core.exceptions import (
    UsageError, ValidationError, QuotaExceededError,
    SubscriptionNotFoundError
)
from ..core.logging import get_logger
from ..core.cache import CacheManager
from ..core.events import EventPublisher

logger = get_logger(__name__)


class UsageTracker:
    """
    Comprehensive usage tracking and quota management system.
    
    Features:
    - Real-time usage tracking for all subscription features
    - Quota enforcement with soft and hard limits
    - Usage analytics and trend analysis
    - Automated usage reset for billing cycles
    - Usage-based billing preparation
    - Feature usage optimization recommendations
    - Quota warning systems and notifications
    - Historical usage reporting and insights
    """
    
    def __init__(self):
        """
Initialize usage tracker."""
        self.logger = get_logger(__name__)
        self.cache = CacheManager()
        self.events = EventPublisher()
        
        # Usage tracking configuration
        self.soft_limit_warning_threshold = 0.8  # 80% usage warning
        self.cache_ttl = 300  # 5 minutes cache for usage data
        self.batch_update_interval = 60  # Batch updates every 60 seconds
        
        # Initialize batch processing
        self._batch_updates = []
        self._last_batch_process = datetime.utcnow()
    
    async def track_usage(
        self,
        user_id: int,
        feature_name: str,
        usage_amount: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Track feature usage for user.
        
        Args:
            user_id: User ID
            feature_name: Feature name being used
            usage_amount: Amount of usage to track
            metadata: Additional usage metadata
            db: Database session
            
        Returns:
            Usage tracking result with current status
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get user subscription
            subscription = await self._get_active_subscription(user_id, db)
            
            # Get or create current usage metric
            usage_metric = await self._get_or_create_usage_metric(
                user_id, subscription.id if subscription else None, 
                feature_name, db
            )
            
            # Update usage
            old_usage = usage_metric.usage_count
            usage_metric.usage_count += usage_amount
            usage_metric.last_usage_date = datetime.utcnow()
            usage_metric.updated_at = datetime.utcnow()
            
            # Update metadata if provided
            if metadata:
                if not usage_metric.usage_data:
                    usage_metric.usage_data = {}
                usage_metric.usage_data.update(metadata)
            
            # Check quotas and limits
            quota_status = await self._check_quota_status(usage_metric)
            
            # Commit changes
            db.commit()
            
            # Update cache
            cache_key = f"usage:{user_id}:{feature_name}"
            await self.cache.set(cache_key, {
                "usage_count": usage_metric.usage_count,
                "quota_limit": usage_metric.quota_limit,
                "last_updated": usage_metric.updated_at.isoformat()
            }, ttl=self.cache_ttl)
            
            # Publish usage event
            await self._publish_usage_event(user_id, feature_name, usage_amount, quota_status)
            
            # Check for quota warnings
            if quota_status["approaching_limit"] and not quota_status["warning_sent"]:
                await self._send_quota_warning(user_id, feature_name, quota_status)
            
            return {
                "success": True,
                "feature_name": feature_name,
                "usage_tracked": usage_amount,
                "total_usage": usage_metric.usage_count,
                "previous_usage": old_usage,
                "quota_status": quota_status,
                "tracking_period": {
                    "start": usage_metric.period_start.isoformat(),
                    "end": usage_metric.period_end.isoformat()
                }
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Usage tracking failed for user {user_id}, feature {feature_name}: {str(e)}")
            raise UsageError(f"Failed to track usage: {str(e)}")
    
    async def check_usage_limit(
        self,
        user_id: int,
        feature_name: str,
        requested_usage: int = 1,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Check if requested usage is within limits.
        
        Args:
            user_id: User ID
            feature_name: Feature name to check
            requested_usage: Amount of usage to check
            db: Database session
            
        Returns:
            Usage limit check result
        """
        if not db:
            db = get_db_session()
        
        try:
            # Check cache first
            cache_key = f"usage_check:{user_id}:{feature_name}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                # Validate cached data is still current
                if datetime.fromisoformat(cached_result["last_updated"]) > datetime.utcnow() - timedelta(minutes=5):
                    current_usage = cached_result["usage_count"]
                    quota_limit = cached_result["quota_limit"]
                else:
                    # Cache expired, get fresh data
                    usage_metric = await self._get_current_usage_metric(user_id, feature_name, db)
                    current_usage = usage_metric.usage_count if usage_metric else 0
                    quota_limit = usage_metric.quota_limit if usage_metric else None
            else:
                # No cache, get from database
                usage_metric = await self._get_current_usage_metric(user_id, feature_name, db)
                current_usage = usage_metric.usage_count if usage_metric else 0
                quota_limit = usage_metric.quota_limit if usage_metric else None
            
            # Calculate usage after requested amount
            projected_usage = current_usage + requested_usage
            
            # Check limits
            within_limit = True
            quota_exceeded = False
            usage_percentage = 0.0
            
            if quota_limit is not None and quota_limit > 0:
                usage_percentage = (projected_usage / quota_limit) * 100
                within_limit = projected_usage <= quota_limit
                quota_exceeded = projected_usage > quota_limit
            
            # Calculate reset date
            reset_date = None
            if usage_metric:
                reset_date = usage_metric.period_end
            
            return {
                "within_limit": within_limit,
                "quota_exceeded": quota_exceeded,
                "current_usage": current_usage,
                "projected_usage": projected_usage,
                "quota_limit": quota_limit,
                "usage_percentage": round(usage_percentage, 2),
                "approaching_limit": usage_percentage >= (self.soft_limit_warning_threshold * 100),
                "reset_date": reset_date.isoformat() if reset_date else None
            }
            
        except Exception as e:
            self.logger.error(f"Usage limit check failed: {str(e)}")
            raise UsageError(f"Failed to check usage limit: {str(e)}")
    
    async def get_current_usage(
        self,
        user_id: int,
        feature_name: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get current usage for user.
        
        Args:
            user_id: User ID
            feature_name: Optional specific feature name
            db: Database session
            
        Returns:
            Current usage information
        """
        if not db:
            db = get_db_session()
        
        try:
            query = db.query(UsageMetrics).filter(
                UsageMetrics.user_id == user_id,
                UsageMetrics.period_end > datetime.utcnow()
            )
            
            if feature_name:
                query = query.filter(UsageMetrics.feature_name == feature_name)
            
            usage_metrics = query.all()
            
            if feature_name:
                # Return single feature usage
                metric = usage_metrics[0] if usage_metrics else None
                if not metric:
                    return {"feature_name": feature_name, "usage_count": 0, "quota_limit": None}
                
                return {
                    "feature_name": metric.feature_name,
                    "usage_count": metric.usage_count,
                    "quota_limit": metric.quota_limit,
                    "usage_percentage": (metric.usage_count / metric.quota_limit * 100) if metric.quota_limit else 0,
                    "period_start": metric.period_start.isoformat(),
                    "period_end": metric.period_end.isoformat(),
                    "last_usage": metric.last_usage_date.isoformat() if metric.last_usage_date else None
                }
            
            else:
                # Return all feature usage
                usage_data = {}
                for metric in usage_metrics:
                    usage_data[metric.feature_name] = {
                        "usage_count": metric.usage_count,
                        "quota_limit": metric.quota_limit,
                        "usage_percentage": (metric.usage_count / metric.quota_limit * 100) if metric.quota_limit else 0,
                        "last_usage": metric.last_usage_date.isoformat() if metric.last_usage_date else None
                    }
                
                return {
                    "user_id": user_id,
                    "features": usage_data,
                    "total_features_tracked": len(usage_data)
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get current usage: {str(e)}")
            raise UsageError(f"Failed to get current usage: {str(e)}")
    
    async def get_comprehensive_usage(
        self,
        user_id: int,
        include_history: bool = False,
        days_back: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive usage analytics for user.
        
        Args:
            user_id: User ID
            include_history: Include historical usage data
            days_back: Days of history to include
            db: Database session
            
        Returns:
            Comprehensive usage analytics
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get current usage
            current_usage = await self.get_current_usage(user_id, db=db)
            
            # Get subscription info
            subscription = await self._get_active_subscription(user_id, db)
            
            usage_analytics = {
                "user_id": user_id,
                "subscription_plan": subscription.plan.name if subscription else "free",
                "current_usage": current_usage,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            if include_history:
                # Get historical usage
                start_date = datetime.utcnow() - timedelta(days=days_back)
                historical_usage = await self._get_historical_usage(user_id, start_date, db)
                usage_analytics["historical_usage"] = historical_usage
                
                # Calculate usage trends
                usage_trends = await self._calculate_usage_trends(user_id, start_date, db)
                usage_analytics["usage_trends"] = usage_trends
            
            # Add usage recommendations
            recommendations = await self._generate_usage_recommendations(user_id, current_usage, db)
            usage_analytics["recommendations"] = recommendations
            
            return usage_analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive usage: {str(e)}")
            raise UsageError(f"Failed to get comprehensive usage: {str(e)}")
    
    async def reset_usage_metrics(
        self,
        user_id: int,
        feature_names: Optional[List[str]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Reset usage metrics for new billing period.
        
        Args:
            user_id: User ID
            feature_names: Optional list of features to reset
            db: Database session
            
        Returns:
            Reset operation result
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get user subscription for new period calculation
            subscription = await self._get_active_subscription(user_id, db)
            if not subscription:
                raise SubscriptionNotFoundError("No active subscription found for usage reset")
            
            # Calculate new period dates
            current_time = datetime.utcnow()
            new_period_end = current_time + timedelta(days=30)  # Default monthly
            
            # Get current usage metrics
            query = db.query(UsageMetrics).filter(
                UsageMetrics.user_id == user_id,
                UsageMetrics.subscription_id == subscription.id
            )
            
            if feature_names:
                query = query.filter(UsageMetrics.feature_name.in_(feature_names))
            
            current_metrics = query.all()
            
            # Reset or create new metrics
            reset_count = 0
            for metric in current_metrics:
                # Archive old metric data
                metric.period_end = current_time
                
                # Create new metric for new period
                new_metric = UsageMetrics(
                    subscription_id=subscription.id,
                    user_id=user_id,
                    feature_name=metric.feature_name,
                    usage_count=0,
                    quota_limit=metric.quota_limit,
                    period_start=current_time,
                    period_end=new_period_end
                )
                
                db.add(new_metric)
                reset_count += 1
            
            db.commit()
            
            # Clear relevant caches
            for feature_name in (feature_names or [m.feature_name for m in current_metrics]):
                cache_key = f"usage:{user_id}:{feature_name}"
                await self.cache.delete(cache_key)
            
            self.logger.info(f"Reset {reset_count} usage metrics for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "metrics_reset": reset_count,
                "new_period_start": current_time.isoformat(),
                "new_period_end": new_period_end.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Usage metrics reset failed: {str(e)}")
            raise UsageError(f"Failed to reset usage metrics: {str(e)}")
    
    # Private helper methods
    
    async def _get_active_subscription(
        self,
        user_id: int,
        db: Session
    ) -> Optional[UserSubscription]:
        """Get active subscription for user."""
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ]),
            UserSubscription.end_date > datetime.utcnow()
        ).first()
    
    async def _get_or_create_usage_metric(
        self,
        user_id: int,
        subscription_id: Optional[int],
        feature_name: str,
        db: Session
    ) -> UsageMetrics:
        """
Get or create usage metric for current period."""
        current_time = datetime.utcnow()
        
        # Try to get existing metric for current period
        existing_metric = db.query(UsageMetrics).filter(
            UsageMetrics.user_id == user_id,
            UsageMetrics.feature_name == feature_name,
            UsageMetrics.period_end > current_time
        ).first()
        
        if existing_metric:
            return existing_metric
        
        # Create new metric for current period
        period_end = current_time + timedelta(days=30)  # Default monthly period
        
        # Get quota limit from subscription plan
        quota_limit = None
        if subscription_id:
            subscription = db.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if subscription and subscription.plan.limits:
                quota_limit = subscription.plan.limits.get(feature_name)
        
        new_metric = UsageMetrics(
            subscription_id=subscription_id,
            user_id=user_id,
            feature_name=feature_name,
            usage_count=0,
            quota_limit=quota_limit,
            period_start=current_time,
            period_end=period_end
        )
        
        db.add(new_metric)
        db.flush()  # Get ID without committing
        
        return new_metric
    
    async def _get_current_usage_metric(
        self,
        user_id: int,
        feature_name: str,
        db: Session
    ) -> Optional[UsageMetrics]:
        """
Get current usage metric for feature."""
        return db.query(UsageMetrics).filter(
            UsageMetrics.user_id == user_id,
            UsageMetrics.feature_name == feature_name,
            UsageMetrics.period_end > datetime.utcnow()
        ).first()
    
    async def _check_quota_status(self, usage_metric: UsageMetrics) -> Dict[str, Any]:
        """
Check quota status for usage metric."""
        quota_status = {
            "has_limit": usage_metric.quota_limit is not None,
            "within_limit": True,
            "quota_exceeded": False,
            "approaching_limit": False,
            "usage_percentage": 0.0,
            "warning_sent": False
        }
        
        if usage_metric.quota_limit and usage_metric.quota_limit > 0:
            usage_percentage = (usage_metric.usage_count / usage_metric.quota_limit) * 100
            quota_status.update({
                "within_limit": usage_metric.usage_count <= usage_metric.quota_limit,
                "quota_exceeded": usage_metric.usage_count > usage_metric.quota_limit,
                "approaching_limit": usage_percentage >= (self.soft_limit_warning_threshold * 100),
                "usage_percentage": round(usage_percentage, 2)
            })
        
        return quota_status
    
    async def _publish_usage_event(
        self,
        user_id: int,
        feature_name: str,
        usage_amount: int,
        quota_status: Dict[str, Any]
    ) -> None:
        """Publish usage tracking event."""
        await self.events.publish("usage.tracked", {
            "user_id": user_id,
            "feature_name": feature_name,
            "usage_amount": usage_amount,
            "quota_status": quota_status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _send_quota_warning(
        self,
        user_id: int,
        feature_name: str,
        quota_status: Dict[str, Any]
    ) -> None:
        """Send quota warning notification."""
        # Implementation would send notification
        await self.events.publish("usage.quota_warning", {
            "user_id": user_id,
            "feature_name": feature_name,
            "usage_percentage": quota_status["usage_percentage"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _get_historical_usage(
        self,
        user_id: int,
        start_date: datetime,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get historical usage data."""
        historical_metrics = db.query(UsageMetrics).filter(
            UsageMetrics.user_id == user_id,
            UsageMetrics.period_start >= start_date
        ).order_by(UsageMetrics.period_start.desc()).all()
        
        return [{
            "feature_name": metric.feature_name,
            "usage_count": metric.usage_count,
            "quota_limit": metric.quota_limit,
            "period_start": metric.period_start.isoformat(),
            "period_end": metric.period_end.isoformat()
        } for metric in historical_metrics]
    
    async def _calculate_usage_trends(
        self,
        user_id: int,
        start_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate usage trends and patterns."""
        # Implementation would analyze usage trends
        return {"trends": "Usage trend analysis would be implemented here"}
    
    async def _generate_usage_recommendations(
        self,
        user_id: int,
        current_usage: Dict[str, Any],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate usage optimization recommendations."""
        recommendations = []
        
        features = current_usage.get("features", {})
        for feature_name, usage_data in features.items():
            usage_percentage = usage_data.get("usage_percentage", 0)
            
            if usage_percentage > 90:
                recommendations.append({
                    "type": "quota_exceeded",
                    "feature": feature_name,
                    "message": f"{feature_name} usage is at {usage_percentage}%. Consider upgrading your plan.",
                    "action": "upgrade_plan"
                })
            elif usage_percentage > 75:
                recommendations.append({
                    "type": "approaching_limit",
                    "feature": feature_name,
                    "message": f"{feature_name} usage is at {usage_percentage}%. Monitor your usage carefully.",
                    "action": "monitor_usage"
                })
        
        return recommendations


__all__ = ['UsageTracker']
