"""
Enterprise Rate Limits Manager

Advanced rate limiting and quota management for API crawling operations
with platform-specific limits and intelligent throttling.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    RateLimit,
    RateLimitScope,
    RateLimitType
)
from ..core.exceptions import (
    RateLimitExceededError,
    DatabaseError,
    ValidationError
)


class RateLimitPeriod(Enum):
    """Rate limit time periods."""
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


class PlatformLimits:
    """Default rate limits for different platforms."""
    
    YOUTUBE = {
        'requests_per_hour': 10000,
        'requests_per_day': 100000,
        'concurrent_sessions': 5
    }
    
    TIKTOK = {
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'concurrent_sessions': 3
    }
    
    INSTAGRAM = {
        'requests_per_hour': 5000,
        'requests_per_day': 50000,
        'concurrent_sessions': 4
    }
    
    TWITTER = {
        'requests_per_hour': 15000,
        'requests_per_day': 150000,
        'concurrent_sessions': 6
    }
    
    GENERIC = {
        'requests_per_hour': 3600,
        'requests_per_day': 36000,
        'concurrent_sessions': 2
    }


class RateLimitManager(DatabaseManager):
    """
    Enterprise-grade rate limit manager for crawling operations.
    
    Handles:
    - Platform-specific rate limits
    - User-level quota management
    - Real-time usage tracking
    - Intelligent throttling
    - Quota recovery and resets
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize rate limit manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(db_session)
        self.table = RateLimit
        self.platform_limits = {
            'youtube': PlatformLimits.YOUTUBE,
            'tiktok': PlatformLimits.TIKTOK,
            'instagram': PlatformLimits.INSTAGRAM,
            'twitter': PlatformLimits.TWITTER,
            'generic': PlatformLimits.GENERIC
        }
    
    async def check_platform_quota(
        self,
        platform: str,
        user_id: str,
        requested_quota: int = 1
    ) -> bool:
        """
        Check if user has sufficient quota for platform operations.
        
        Args:
            platform: Target platform
            user_id: User identifier
            requested_quota: Number of requests being requested
            
        Returns:
            bool indicating if quota is available
        """



        try:
            # Get platform limits
            limits = self.platform_limits.get(platform, PlatformLimits.GENERIC)
            
            # Check hourly limits
            hourly_available = await self._check_quota_period(
                platform, user_id, RateLimitPeriod.HOUR.value,
                limits['requests_per_hour'], requested_quota
            )
            
            # Check daily limits
            daily_available = await self._check_quota_period(
                platform, user_id, RateLimitPeriod.DAY.value,
                limits['requests_per_day'], requested_quota
            )
            
            # Check concurrent sessions
            concurrent_available = await self._check_concurrent_sessions(
                platform, user_id, limits['concurrent_sessions']
            )
            
            return hourly_available and daily_available and concurrent_available
            
        except Exception as e:
            raise DatabaseError(f"Failed to check platform quota: {str(e)}")
    
    async def _check_quota_period(
        self,
        platform: str,
        user_id: str,
        period: str,
        limit: int,
        requested: int
    ) -> bool:
        """
        Check quota for specific time period.
        
        Args:
            platform: Target platform
            user_id: User identifier
            period: Time period (hour, day, etc.)
            limit: Maximum allowed requests
            requested: Number of requests being requested
            
        Returns:
            bool indicating if quota is available
        """



        try:
            # Calculate period start time
            now = datetime.utcnow()
            if period == RateLimitPeriod.HOUR.value:
                period_start = now.replace(minute=0, second=0, microsecond=0)
            elif period == RateLimitPeriod.DAY.value:
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == RateLimitPeriod.WEEK.value:
                days_since_monday = now.weekday()
                period_start = (now - timedelta(days=days_since_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            elif period == RateLimitPeriod.MONTH.value:
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                period_start = now - timedelta(minutes=1)
            
            # Get current usage for period
            current_usage = await self.db.execute(
                text("""
                SELECT COALESCE(SUM(usage_count), 0) as total_usage
                FROM rate_limits
                WHERE platform = :platform
                  AND user_id = :user_id
                  AND period_type = :period
                  AND period_start = :period_start
                """),
                {
                    'platform': platform,
                    'user_id': user_id,
                    'period': period,
                    'period_start': period_start
                }
            )
            
            usage_result = current_usage.first()
            current_count = usage_result.total_usage or 0
            
            # Check if adding requested quota would exceed limit
            return (current_count + requested) <= limit
            
        except Exception as e:
            raise DatabaseError(f"Failed to check quota period: {str(e)}")
    
    async def _check_concurrent_sessions(
        self,
        platform: str,
        user_id: str,
        max_concurrent: int
    ) -> bool:
        """
        Check concurrent sessions limit.
        
        Args:
            platform: Target platform
            user_id: User identifier
            max_concurrent: Maximum concurrent sessions allowed
            
        Returns:
            bool indicating if concurrent limit allows new session
        """



        try:
            # Count active sessions for user on platform
            active_sessions = await self.db.execute(
                text("""
                SELECT COUNT(*) as session_count
                FROM crawling_sessions
                WHERE platform = :platform
                  AND user_id = :user_id
                  AND status IN ('active', 'running')
                """),
                {
                    'platform': platform,
                    'user_id': user_id
                }
            )
            
            session_result = active_sessions.first()
            current_sessions = session_result.session_count or 0
            
            return current_sessions < max_concurrent
            
        except Exception as e:
            raise DatabaseError(f"Failed to check concurrent sessions: {str(e)}")
    
    async def increment_usage(
        self,
        platform: str,
        user_id: str,
        usage_count: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Increment usage count for platform and user.
        
        Args:
            platform: Target platform
            user_id: User identifier
            usage_count: Number of requests to add
            metadata: Optional usage metadata
            
        Returns:
            bool indicating success
        """



        try:
            now = datetime.utcnow()
            
            # Update usage for different time periods
            periods = [
                (RateLimitPeriod.HOUR.value, now.replace(minute=0, second=0, microsecond=0)),
                (RateLimitPeriod.DAY.value, now.replace(hour=0, minute=0, second=0, microsecond=0)),
                (RateLimitPeriod.WEEK.value, 
                 (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)),
                (RateLimitPeriod.MONTH.value, 
                 now.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
            ]
            
            for period_type, period_start in periods:
                await self._upsert_rate_limit_record(
                    platform, user_id, period_type, period_start, usage_count, metadata
                )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to increment usage: {str(e)}")
    
    async def _upsert_rate_limit_record(
        self,
        platform: str,
        user_id: str,
        period_type: str,
        period_start: datetime,
        usage_count: int,
        metadata: Optional[Dict[str, Any]]
    ) -> None:
        """
        Insert or update rate limit record for specific period.
        
        Args:
            platform: Target platform
            user_id: User identifier
            period_type: Type of time period
            period_start: Start of the time period
            usage_count: Usage count to add
            metadata: Optional metadata
        """



        try:
            # Try to update existing record
            result = await self.db.execute(
                text("""
                UPDATE rate_limits 
                SET usage_count = usage_count + :usage_count,
                    last_request_at = :now,
                    updated_at = :now,
                    metadata = COALESCE(metadata, :metadata)
                WHERE platform = :platform
                  AND user_id = :user_id
                  AND period_type = :period_type
                  AND period_start = :period_start
                """),
                {
                    'platform': platform,
                    'user_id': user_id,
                    'period_type': period_type,
                    'period_start': period_start,
                    'usage_count': usage_count,
                    'metadata': json.dumps(metadata) if metadata else None,
                    'now': datetime.utcnow()
                }
            )
            
            # If no record was updated, insert new one
            if result.rowcount == 0:
                limit_data = {
                    'limit_id': str(uuid4()),
                    'platform': platform,
                    'user_id': user_id,
                    'period_type': period_type,
                    'period_start': period_start,
                    'usage_count': usage_count,
                    'limit_value': self._get_limit_for_period(platform, period_type),
                    'scope': RateLimitScope.USER.value,
                    'limit_type': RateLimitType.REQUESTS.value,
                    'metadata': json.dumps(metadata) if metadata else None,
                    'first_request_at': datetime.utcnow(),
                    'last_request_at': datetime.utcnow(),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                
                rate_limit = RateLimit(**limit_data)
                self.db.add(rate_limit)
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to upsert rate limit record: {str(e)}")
    
    def _get_limit_for_period(self, platform: str, period_type: str) -> int:
        """
        Get the rate limit value for platform and period.
        
        Args:
            platform: Target platform
            period_type: Time period type
            
        Returns:
            Rate limit value
        """
        limits = self.platform_limits.get(platform, PlatformLimits.GENERIC)
        
        if period_type == RateLimitPeriod.HOUR.value:
            return limits['requests_per_hour']
        elif period_type == RateLimitPeriod.DAY.value:
            return limits['requests_per_day']
        elif period_type == RateLimitPeriod.WEEK.value:
            return limits['requests_per_day'] * 7
        elif period_type == RateLimitPeriod.MONTH.value:
            return limits['requests_per_day'] * 30
        else:
            return limits['requests_per_hour']  # Default to hourly
    
    async def get_remaining_quota(
        self,
        platform: str,
        user_id: str,
        period_type: str = RateLimitPeriod.HOUR.value
    ) -> Dict[str, Any]:
        """
        Get remaining quota for user on platform.
        
        Args:
            platform: Target platform
            user_id: User identifier
            period_type: Time period to check
            
        Returns:
            Dict containing quota information
        """



        try:
            # Calculate period start
            now = datetime.utcnow()
            if period_type == RateLimitPeriod.HOUR.value:
                period_start = now.replace(minute=0, second=0, microsecond=0)
            elif period_type == RateLimitPeriod.DAY.value:
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                period_start = now.replace(minute=0, second=0, microsecond=0)
            
            # Get current usage
            usage_result = await self.db.execute(
                text("""
                SELECT usage_count, limit_value, last_request_at
                FROM rate_limits
                WHERE platform = :platform
                  AND user_id = :user_id
                  AND period_type = :period_type
                  AND period_start = :period_start
                """),
                {
                    'platform': platform,
                    'user_id': user_id,
                    'period_type': period_type,
                    'period_start': period_start
                }
            )
            
            usage_data = usage_result.first()
            
            if usage_data:
                used = usage_data.usage_count
                limit = usage_data.limit_value
                last_request = usage_data.last_request_at
            else:
                used = 0
                limit = self._get_limit_for_period(platform, period_type)
                last_request = None
            
            remaining = max(0, limit - used)
            percentage_used = (used / limit * 100) if limit > 0 else 0
            
            # Calculate reset time
            if period_type == RateLimitPeriod.HOUR.value:
                reset_time = period_start + timedelta(hours=1)
            elif period_type == RateLimitPeriod.DAY.value:
                reset_time = period_start + timedelta(days=1)
            else:
                reset_time = period_start + timedelta(hours=1)
            
            return {
                'platform': platform,
                'period_type': period_type,
                'limit': limit,
                'used': used,
                'remaining': remaining,
                'percentage_used': percentage_used,
                'reset_time': reset_time.isoformat(),
                'last_request_at': last_request.isoformat() if last_request else None,
                'is_exhausted': remaining == 0
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get remaining quota: {str(e)}")
    
    async def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive rate limit status for user across all platforms.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user's rate limit status
        """



        try:
            platform_status = {}
            
            for platform in self.platform_limits.keys():
                # Get hourly and daily quotas
                hourly_quota = await self.get_remaining_quota(
                    platform, user_id, RateLimitPeriod.HOUR.value
                )
                daily_quota = await self.get_remaining_quota(
                    platform, user_id, RateLimitPeriod.DAY.value
                )
                
                # Check concurrent sessions
                concurrent_result = await self.db.execute(
                    text("""
                    SELECT COUNT(*) as active_sessions
                    FROM crawling_sessions
                    WHERE platform = :platform
                      AND user_id = :user_id
                      AND status IN ('active', 'running')
                    """),
                    {'platform': platform, 'user_id': user_id}
                )
                
                active_sessions = concurrent_result.first().active_sessions or 0
                max_concurrent = self.platform_limits[platform]['concurrent_sessions']
                
                platform_status[platform] = {
                    'hourly_quota': hourly_quota,
                    'daily_quota': daily_quota,
                    'concurrent_sessions': {
                        'active': active_sessions,
                        'max_allowed': max_concurrent,
                        'available': max(0, max_concurrent - active_sessions)
                    },
                    'is_throttled': (
                        hourly_quota['remaining'] == 0 or 
                        daily_quota['remaining'] == 0 or
                        active_sessions >= max_concurrent
                    )
                }
            
            return {
                'user_id': user_id,
                'platforms': platform_status,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user status: {str(e)}")
    
    async def reset_user_quota(
        self,
        platform: str,
        user_id: str,
        period_type: str = RateLimitPeriod.DAY.value
    ) -> bool:
        """
        Reset quota for user on platform (admin function).
        
        Args:
            platform: Target platform
            user_id: User identifier
            period_type: Period type to reset
            
        Returns:
            bool indicating success
        """



        try:
            result = await self.db.execute(
                text("""
                DELETE FROM rate_limits
                WHERE platform = :platform
                  AND user_id = :user_id
                  AND period_type = :period_type
                """),
                {
                    'platform': platform,
                    'user_id': user_id,
                    'period_type': period_type
                }
            )
            
            await self.db.commit()
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to reset user quota: {str(e)}")
    
    async def get_global_rate_statistics(
        self,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        Get global rate limiting statistics.
        
        Args:
            time_range: Time range for statistics
            
        Returns:
            Dict containing global statistics
        """



        try:
            since = datetime.utcnow() - time_range
            
            # Get platform usage statistics
            platform_stats = await self.db.execute(
                text("""
                SELECT 
                    platform,
                    COUNT(DISTINCT user_id) as unique_users,
                    SUM(usage_count) as total_requests,
                    AVG(usage_count) as avg_requests_per_user,
                    MAX(usage_count) as max_requests_single_user
                FROM rate_limits
                WHERE updated_at >= :since
                GROUP BY platform
                """),
                {'since': since}
            )
            
            # Get period type breakdown
            period_stats = await self.db.execute(
                text("""
                SELECT 
                    period_type,
                    COUNT(*) as record_count,
                    SUM(usage_count) as total_usage,
                    AVG(usage_count) as avg_usage
                FROM rate_limits
                WHERE updated_at >= :since
                GROUP BY period_type
                """),
                {'since': since}
            )
            
            # Get top users by usage
            top_users = await self.db.execute(
                text("""
                SELECT 
                    user_id,
                    platform,
                    SUM(usage_count) as total_usage
                FROM rate_limits
                WHERE updated_at >= :since
                GROUP BY user_id, platform
                ORDER BY total_usage DESC
                LIMIT 10
                """),
                {'since': since}
            )
            
            platform_data = {
                row.platform: {
                    'unique_users': row.unique_users,
                    'total_requests': row.total_requests,
                    'avg_requests_per_user': float(row.avg_requests_per_user or 0),
                    'max_requests_single_user': row.max_requests_single_user
                }
                for row in platform_stats
            }
            
            period_data = {
                row.period_type: {
                    'record_count': row.record_count,
                    'total_usage': row.total_usage,
                    'avg_usage': float(row.avg_usage or 0)
                }
                for row in period_stats
            }
            
            top_users_data = [
                {
                    'user_id': row.user_id,
                    'platform': row.platform,
                    'total_usage': row.total_usage
                }
                for row in top_users
            ]
            
            return {
                'time_range_days': time_range.days,
                'platform_statistics': platform_data,
                'period_statistics': period_data,
                'top_users': top_users_data,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get global rate statistics: {str(e)}")
    
    async def cleanup_expired_limits(
        self,
        retention_days: int = 30
    ) -> Dict[str, int]:
        """
        Clean up expired rate limit records.
        
        Args:
            retention_days: Number of days to retain rate limit records
            
        Returns:
            Dict containing cleanup statistics
        """



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            result = await self.db.execute(
                text("DELETE FROM rate_limits WHERE updated_at < :cutoff_date"),
                {'cutoff_date': cutoff_date}
            )
            
            await self.db.commit()
            
            return {
                'deleted_records': result.rowcount,
                'cutoff_date': cutoff_date.isoformat(),
                'retention_days': retention_days
            }
            
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to cleanup expired limits: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of rate limiting system.
        
        Returns:
            Dict containing health status
        """



        try:
            # Check recent rate limit activity
            recent_activity = await self.db.query(func.count(RateLimit.limit_id)).filter(
                RateLimit.updated_at >= datetime.utcnow() - timedelta(hours=1)
            ).scalar()
            
            # Check for users hitting limits
            users_at_limit = await self.db.execute(
                text("""
                SELECT COUNT(DISTINCT user_id) as count
                FROM rate_limits
                WHERE usage_count >= limit_value
                  AND updated_at >= :since
                """),
                {'since': datetime.utcnow() - timedelta(hours=1)}
            )
            
            users_limited = users_at_limit.first().count or 0
            
            # Determine health status
            status = 'healthy'
            if users_limited > recent_activity * 0.1:  # More than 10% users limited
                status = 'degraded'
            if users_limited > recent_activity * 0.3:  # More than 30% users limited
                status = 'unhealthy'
            
            return {
                'status': status,
                'recent_activity_1h': recent_activity,
                'users_at_limit_1h': users_limited,
                'throttling_percentage': (users_limited / max(recent_activity, 1)) * 100,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['RateLimitManager', 'RateLimitPeriod', 'PlatformLimits']
