"""
Distribution Tracker - Enterprise Content Distribution Tracking and Analytics

This module provides comprehensive tracking of content distribution across
platforms with analytics, performance monitoring, and success metrics.

🎯 Expert Roles Applied:
- Lead Dev IA: AI-driven distribution analytics and optimization insights
- Backend Senior: Robust tracking infrastructure with data integrity
- ML Engineer: Machine learning for distribution performance prediction
- DBA: Optimized tracking data storage and analytics queries
- Sécurité: Secure tracking with privacy-compliant analytics
- Microservices: Distributed tracking service architecture
- Audio: Audio content distribution tracking and metrics
- DevOps: Scalable tracking infrastructure and monitoring
- IA Prompt Engineer: AI-powered distribution insights and recommendations

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
import hashlib

from .platform_manager import PlatformType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistributionStatus(Enum):
    """Distribution status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    FAILED = "failed"
    PARTIALLY_DISTRIBUTED = "partially_distributed"
    CANCELLED = "cancelled"


class TrackingEventType(Enum):
    """Types of tracking events"""
    DISTRIBUTION_STARTED = "distribution_started"
    PLATFORM_UPLOAD = "platform_upload"
    PLATFORM_SUCCESS = "platform_success"
    PLATFORM_FAILURE = "platform_failure"
    ENGAGEMENT_UPDATE = "engagement_update"
    REVENUE_UPDATE = "revenue_update"
    DISTRIBUTION_COMPLETED = "distribution_completed"


@dataclass
class DistributionRecord:
    """Content distribution record"""
    distribution_id: str
    user_id: str
    content_id: str
    content_title: str
    platforms: List[PlatformType]
    status: DistributionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_platforms: int = 0
    successful_platforms: int = 0
    failed_platforms: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.total_platforms == 0:
            self.total_platforms = len(self.platforms)


@dataclass
class PlatformDistribution:
    """Platform-specific distribution data"""
    platform_distribution_id: str
    distribution_id: str
    platform: PlatformType
    status: DistributionStatus
    platform_content_id: Optional[str] = None
    platform_url: Optional[str] = None
    upload_started_at: Optional[datetime] = None
    upload_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EngagementMetrics:
    """Engagement metrics for distributed content"""
    platform_distribution_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    click_through_rate: float = 0.0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class RevenueMetrics:
    """Revenue metrics for distributed content"""
    platform_distribution_id: str
    revenue: float = 0.0
    currency: str = "USD"
    ad_revenue: float = 0.0
    sponsorship_revenue: float = 0.0
    subscription_revenue: float = 0.0
    tip_revenue: float = 0.0
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class TrackingEvent:
    """Tracking event data"""
    event_id: str
    distribution_id: str
    platform_distribution_id: Optional[str]
    event_type: TrackingEventType
    platform: Optional[PlatformType]
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class DistributionTracker:
    """
    Enterprise Content Distribution Tracker
    
    Provides comprehensive tracking of content distribution across platforms
    with real-time analytics, performance monitoring, and AI-driven insights.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize Distribution Tracker
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        
        # Collections
        self.distributions_collection = db.content_distributions
        self.platform_distributions_collection = db.platform_distributions
        self.engagement_metrics_collection = db.engagement_metrics
        self.revenue_metrics_collection = db.revenue_metrics
        self.tracking_events_collection = db.tracking_events
        self.analytics_collection = db.distribution_analytics
        
        # Analytics cache
        self._analytics_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._last_cache_update = datetime.utcnow()
    
    async def initialize(self) -> None:
        """Initialize Distribution Tracker"""
        try:
            # Create indexes
            await self.distributions_collection.create_index([("user_id", 1), ("started_at", -1)])
            await self.distributions_collection.create_index([("content_id", 1)])
            await self.distributions_collection.create_index([("status", 1)])
            
            await self.platform_distributions_collection.create_index([("distribution_id", 1)])
            await self.platform_distributions_collection.create_index([("platform", 1), ("status", 1)])
            await self.platform_distributions_collection.create_index([("platform_content_id", 1)])
            
            await self.engagement_metrics_collection.create_index([("platform_distribution_id", 1)])
            await self.engagement_metrics_collection.create_index([("updated_at", -1)])
            
            await self.revenue_metrics_collection.create_index([("platform_distribution_id", 1)])
            await self.revenue_metrics_collection.create_index([("updated_at", -1)])
            
            await self.tracking_events_collection.create_index([("distribution_id", 1), ("timestamp", -1)])
            await self.tracking_events_collection.create_index([("event_type", 1), ("timestamp", -1)])
            
            await self.analytics_collection.create_index([("user_id", 1), ("date", -1)])
            await self.analytics_collection.create_index([("platform", 1), ("date", -1)])
            
            logger.info("Distribution Tracker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Distribution Tracker: {e}")
            raise
    
    async def start_distribution_tracking(self, user_id: str, content_id: str,
                                        content_title: str, platforms: List[PlatformType]) -> str:
        """
        Start tracking a new content distribution
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            content_title: Content title
            platforms: Target platforms
            
        Returns:
            str: Distribution ID
        """
        try:
            distribution_id = hashlib.md5(f"{user_id}:{content_id}:{datetime.utcnow()}".encode()).hexdigest()
            
            # Create distribution record
            distribution = DistributionRecord(
                distribution_id=distribution_id,
                user_id=user_id,
                content_id=content_id,
                content_title=content_title,
                platforms=platforms,
                status=DistributionStatus.PENDING,
                started_at=datetime.utcnow()
            )
            
            # Store distribution record
            await self.distributions_collection.insert_one(asdict(distribution))
            
            # Create platform distribution records
            for platform in platforms:
                platform_dist = PlatformDistribution(
                    platform_distribution_id=hashlib.md5(f"{distribution_id}:{platform.value}".encode()).hexdigest(),
                    distribution_id=distribution_id,
                    platform=platform,
                    status=DistributionStatus.PENDING
                )
                
                await self.platform_distributions_collection.insert_one(asdict(platform_dist))
            
            # Log tracking event
            await self._log_event(
                distribution_id=distribution_id,
                event_type=TrackingEventType.DISTRIBUTION_STARTED,
                data={
                    "content_id": content_id,
                    "content_title": content_title,
                    "platforms": [p.value for p in platforms]
                }
            )
            
            logger.info(f"Started tracking distribution {distribution_id}")
            return distribution_id
            
        except Exception as e:
            logger.error(f"Failed to start distribution tracking: {e}")
            raise
    
    async def update_platform_status(self, distribution_id: str, platform: PlatformType,
                                   status: DistributionStatus,
                                   platform_content_id: Optional[str] = None,
                                   platform_url: Optional[str] = None,
                                   error_message: Optional[str] = None) -> bool:
        """
        Update platform distribution status
        
        Args:
            distribution_id: Distribution identifier
            platform: Platform type
            status: New status
            platform_content_id: Platform-specific content ID
            platform_url: Platform content URL
            error_message: Error message if failed
            
        Returns:
            bool: Success status
        """
        try:
            # Update platform distribution
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if platform_content_id:
                update_data["platform_content_id"] = platform_content_id
            
            if platform_url:
                update_data["platform_url"] = platform_url
            
            if error_message:
                update_data["error_message"] = error_message
            
            if status == DistributionStatus.PROCESSING:
                update_data["upload_started_at"] = datetime.utcnow()
            elif status in [DistributionStatus.DISTRIBUTED, DistributionStatus.FAILED]:
                update_data["upload_completed_at"] = datetime.utcnow()
            
            result = await self.platform_distributions_collection.update_one(
                {"distribution_id": distribution_id, "platform": platform.value},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Log tracking event
                await self._log_event(
                    distribution_id=distribution_id,
                    event_type=TrackingEventType.PLATFORM_SUCCESS if status == DistributionStatus.DISTRIBUTED else TrackingEventType.PLATFORM_FAILURE,
                    platform=platform,
                    data={
                        "status": status.value,
                        "platform_content_id": platform_content_id,
                        "platform_url": platform_url,
                        "error_message": error_message
                    }
                )
                
                # Update overall distribution status
                await self._update_overall_distribution_status(distribution_id)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update platform status: {e}")
            return False
    
    async def update_engagement_metrics(self, platform_distribution_id: str,
                                      metrics: EngagementMetrics) -> bool:
        """
        Update engagement metrics for platform distribution
        
        Args:
            platform_distribution_id: Platform distribution identifier
            metrics: Engagement metrics
            
        Returns:
            bool: Success status
        """
        try:
            # Store/update engagement metrics
            await self.engagement_metrics_collection.replace_one(
                {"platform_distribution_id": platform_distribution_id},
                asdict(metrics),
                upsert=True
            )
            
            # Log tracking event
            await self._log_event_by_platform_id(
                platform_distribution_id=platform_distribution_id,
                event_type=TrackingEventType.ENGAGEMENT_UPDATE,
                data=asdict(metrics)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update engagement metrics: {e}")
            return False
    
    async def update_revenue_metrics(self, platform_distribution_id: str,
                                   metrics: RevenueMetrics) -> bool:
        """
        Update revenue metrics for platform distribution
        
        Args:
            platform_distribution_id: Platform distribution identifier
            metrics: Revenue metrics
            
        Returns:
            bool: Success status
        """
        try:
            # Store/update revenue metrics
            await self.revenue_metrics_collection.replace_one(
                {"platform_distribution_id": platform_distribution_id},
                asdict(metrics),
                upsert=True
            )
            
            # Log tracking event
            await self._log_event_by_platform_id(
                platform_distribution_id=platform_distribution_id,
                event_type=TrackingEventType.REVENUE_UPDATE,
                data=asdict(metrics)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update revenue metrics: {e}")
            return False
    
    async def get_distribution_status(self, distribution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get distribution status and metrics
        
        Args:
            distribution_id: Distribution identifier
            
        Returns:
            Optional[Dict[str, Any]]: Distribution status data
        """
        try:
            # Get distribution record
            distribution = await self.distributions_collection.find_one({"distribution_id": distribution_id})
            if not distribution:
                return None
            
            # Get platform distributions
            platform_cursor = self.platform_distributions_collection.find({"distribution_id": distribution_id})
            platforms = await platform_cursor.to_list(length=None)
            
            # Get metrics for each platform
            for platform in platforms:
                platform_id = platform["platform_distribution_id"]
                
                # Get engagement metrics
                engagement = await self.engagement_metrics_collection.find_one({"platform_distribution_id": platform_id})
                platform["engagement_metrics"] = engagement
                
                # Get revenue metrics
                revenue = await self.revenue_metrics_collection.find_one({"platform_distribution_id": platform_id})
                platform["revenue_metrics"] = revenue
            
            distribution["platforms"] = platforms
            
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to get distribution status: {e}")
            return None
    
    async def get_user_distribution_analytics(self, user_id: str,
                                            start_date: Optional[datetime] = None,
                                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get user distribution analytics
        
        Args:
            user_id: User identifier
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dict[str, Any]: Analytics data
        """
        try:
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Check cache
            cache_key = f"{user_id}:{start_date.date()}:{end_date.date()}"
            if self._is_cache_valid() and cache_key in self._analytics_cache:
                return self._analytics_cache[cache_key]
            
            # Aggregate distribution data
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "started_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_distributions": {"$sum": 1},
                        "successful_distributions": {
                            "$sum": {"$cond": [{"$eq": ["$status", "distributed"]}, 1, 0]}
                        },
                        "failed_distributions": {
                            "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                        },
                        "total_platforms": {"$sum": "$total_platforms"},
                        "successful_platforms": {"$sum": "$successful_platforms"},
                        "failed_platforms": {"$sum": "$failed_platforms"}
                    }
                }
            ]
            
            cursor = self.distributions_collection.aggregate(pipeline)
            distribution_stats = await cursor.to_list(length=1)
            
            # Platform performance analytics
            platform_analytics = await self._get_platform_analytics(user_id, start_date, end_date)
            
            # Engagement analytics
            engagement_analytics = await self._get_engagement_analytics(user_id, start_date, end_date)
            
            # Revenue analytics
            revenue_analytics = await self._get_revenue_analytics(user_id, start_date, end_date)
            
            analytics = {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "distribution_summary": distribution_stats[0] if distribution_stats else {},
                "platform_performance": platform_analytics,
                "engagement_metrics": engagement_analytics,
                "revenue_metrics": revenue_analytics,
                "success_rate": 0.0
            }
            
            # Calculate success rate
            if distribution_stats and distribution_stats[0]["total_distributions"] > 0:
                analytics["success_rate"] = (
                    distribution_stats[0]["successful_distributions"] / 
                    distribution_stats[0]["total_distributions"]
                ) * 100
            
            # Cache results
            self._analytics_cache[cache_key] = analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {}
    
    async def get_platform_performance_comparison(self, user_id: str,
                                                platforms: List[PlatformType],
                                                date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Compare performance across platforms
        
        Args:
            user_id: User identifier
            platforms: Platforms to compare
            date_range: Optional date range
            
        Returns:
            Dict[str, Any]: Platform comparison data
        """
        try:
            if not date_range:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            comparison = {}
            
            for platform in platforms:
                platform_data = await self._get_single_platform_analytics(
                    user_id, platform, date_range[0], date_range[1]
                )
                comparison[platform.value] = platform_data
            
            # Calculate rankings
            rankings = await self._calculate_platform_rankings(comparison)
            
            return {
                "comparison": comparison,
                "rankings": rankings,
                "date_range": {
                    "start": date_range[0],
                    "end": date_range[1]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform comparison: {e}")
            return {}
    
    async def _update_overall_distribution_status(self, distribution_id: str) -> None:
        """Update overall distribution status based on platform statuses"""
        
        try:
            # Get all platform distributions for this distribution
            cursor = self.platform_distributions_collection.find({"distribution_id": distribution_id})
            platforms = await cursor.to_list(length=None)
            
            if not platforms:
                return
            
            # Count statuses
            total_platforms = len(platforms)
            successful_count = sum(1 for p in platforms if p["status"] == "distributed")
            failed_count = sum(1 for p in platforms if p["status"] == "failed")
            pending_count = sum(1 for p in platforms if p["status"] in ["pending", "processing"])
            
            # Determine overall status
            if pending_count > 0:
                overall_status = DistributionStatus.PROCESSING
            elif successful_count == total_platforms:
                overall_status = DistributionStatus.DISTRIBUTED
            elif failed_count == total_platforms:
                overall_status = DistributionStatus.FAILED
            else:
                overall_status = DistributionStatus.PARTIALLY_DISTRIBUTED
            
            # Update distribution record
            update_data = {
                "status": overall_status.value,
                "successful_platforms": successful_count,
                "failed_platforms": failed_count,
                "updated_at": datetime.utcnow()
            }
            
            if overall_status in [DistributionStatus.DISTRIBUTED, DistributionStatus.FAILED, DistributionStatus.PARTIALLY_DISTRIBUTED]:
                update_data["completed_at"] = datetime.utcnow()
            
            await self.distributions_collection.update_one(
                {"distribution_id": distribution_id},
                {"$set": update_data}
            )
            
            # Log completion event if finished
            if overall_status != DistributionStatus.PROCESSING:
                await self._log_event(
                    distribution_id=distribution_id,
                    event_type=TrackingEventType.DISTRIBUTION_COMPLETED,
                    data={
                        "final_status": overall_status.value,
                        "successful_platforms": successful_count,
                        "failed_platforms": failed_count,
                        "total_platforms": total_platforms
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to update overall distribution status: {e}")
    
    async def _get_platform_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform performance analytics"""
        
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "content_distributions",
                        "localField": "distribution_id",
                        "foreignField": "distribution_id",
                        "as": "distribution"
                    }
                },
                {
                    "$unwind": "$distribution"
                },
                {
                    "$match": {
                        "distribution.user_id": user_id,
                        "distribution.started_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$platform",
                        "total_uploads": {"$sum": 1},
                        "successful_uploads": {
                            "$sum": {"$cond": [{"$eq": ["$status", "distributed"]}, 1, 0]}
                        },
                        "failed_uploads": {
                            "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                        },
                        "avg_upload_time": {
                            "$avg": {
                                "$subtract": ["$upload_completed_at", "$upload_started_at"]
                            }
                        }
                    }
                }
            ]
            
            cursor = self.platform_distributions_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            platform_analytics = {}
            for result in results:
                platform = result["_id"]
                platform_analytics[platform] = {
                    "total_uploads": result["total_uploads"],
                    "successful_uploads": result["successful_uploads"],
                    "failed_uploads": result["failed_uploads"],
                    "success_rate": (result["successful_uploads"] / result["total_uploads"]) * 100 if result["total_uploads"] > 0 else 0,
                    "avg_upload_time_ms": result["avg_upload_time"] if result["avg_upload_time"] else 0
                }
            
            return platform_analytics
            
        except Exception as e:
            logger.error(f"Platform analytics failed: {e}")
            return {}
    
    async def _get_engagement_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get engagement analytics"""
        
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "platform_distributions",
                        "localField": "platform_distribution_id",
                        "foreignField": "platform_distribution_id",
                        "as": "platform_dist"
                    }
                },
                {
                    "$unwind": "$platform_dist"
                },
                {
                    "$lookup": {
                        "from": "content_distributions",
                        "localField": "platform_dist.distribution_id",
                        "foreignField": "distribution_id",
                        "as": "distribution"
                    }
                },
                {
                    "$unwind": "$distribution"
                },
                {
                    "$match": {
                        "distribution.user_id": user_id,
                        "updated_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_views": {"$sum": "$views"},
                        "total_likes": {"$sum": "$likes"},
                        "total_shares": {"$sum": "$shares"},
                        "total_comments": {"$sum": "$comments"},
                        "avg_engagement_rate": {"$avg": "$engagement_rate"},
                        "total_reach": {"$sum": "$reach"},
                        "total_impressions": {"$sum": "$impressions"}
                    }
                }
            ]
            
            cursor = self.engagement_metrics_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Engagement analytics failed: {e}")
            return {}
    
    async def _get_revenue_analytics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get revenue analytics"""
        
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "platform_distributions",
                        "localField": "platform_distribution_id",
                        "foreignField": "platform_distribution_id",
                        "as": "platform_dist"
                    }
                },
                {
                    "$unwind": "$platform_dist"
                },
                {
                    "$lookup": {
                        "from": "content_distributions",
                        "localField": "platform_dist.distribution_id",
                        "foreignField": "distribution_id",
                        "as": "distribution"
                    }
                },
                {
                    "$unwind": "$distribution"
                },
                {
                    "$match": {
                        "distribution.user_id": user_id,
                        "updated_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_revenue": {"$sum": "$revenue"},
                        "ad_revenue": {"$sum": "$ad_revenue"},
                        "sponsorship_revenue": {"$sum": "$sponsorship_revenue"},
                        "subscription_revenue": {"$sum": "$subscription_revenue"},
                        "tip_revenue": {"$sum": "$tip_revenue"}
                    }
                }
            ]
            
            cursor = self.revenue_metrics_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Revenue analytics failed: {e}")
            return {}
    
    async def _get_single_platform_analytics(self, user_id: str, platform: PlatformType,
                                           start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics for a single platform"""
        
        try:
            # Platform distribution stats
            dist_pipeline = [
                {
                    "$lookup": {
                        "from": "content_distributions",
                        "localField": "distribution_id",
                        "foreignField": "distribution_id",
                        "as": "distribution"
                    }
                },
                {
                    "$unwind": "$distribution"
                },
                {
                    "$match": {
                        "platform": platform.value,
                        "distribution.user_id": user_id,
                        "distribution.started_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_uploads": {"$sum": 1},
                        "successful_uploads": {
                            "$sum": {"$cond": [{"$eq": ["$status", "distributed"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            cursor = self.platform_distributions_collection.aggregate(dist_pipeline)
            dist_stats = await cursor.to_list(length=1)
            
            # Engagement stats
            eng_pipeline = [
                {
                    "$lookup": {
                        "from": "platform_distributions",
                        "localField": "platform_distribution_id",
                        "foreignField": "platform_distribution_id",
                        "as": "platform_dist"
                    }
                },
                {
                    "$unwind": "$platform_dist"
                },
                {
                    "$match": {
                        "platform_dist.platform": platform.value,
                        "updated_at": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_views": {"$sum": "$views"},
                        "total_engagement": {"$sum": {"$add": ["$likes", "$shares", "$comments"]}},
                        "avg_engagement_rate": {"$avg": "$engagement_rate"}
                    }
                }
            ]
            
            cursor = self.engagement_metrics_collection.aggregate(eng_pipeline)
            eng_stats = await cursor.to_list(length=1)
            
            analytics = {
                "platform": platform.value,
                "uploads": dist_stats[0] if dist_stats else {"total_uploads": 0, "successful_uploads": 0},
                "engagement": eng_stats[0] if eng_stats else {"total_views": 0, "total_engagement": 0, "avg_engagement_rate": 0}
            }
            
            # Calculate success rate
            if analytics["uploads"]["total_uploads"] > 0:
                analytics["success_rate"] = (analytics["uploads"]["successful_uploads"] / analytics["uploads"]["total_uploads"]) * 100
            else:
                analytics["success_rate"] = 0
            
            return analytics
            
        except Exception as e:
            logger.error(f"Single platform analytics failed: {e}")
            return {}
    
    async def _calculate_platform_rankings(self, comparison: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate platform rankings by various metrics"""
        
        try:
            rankings = {}
            
            # Success rate ranking
            success_rates = [(platform, data.get("success_rate", 0)) for platform, data in comparison.items()]
            success_rates.sort(key=lambda x: x[1], reverse=True)
            rankings["success_rate"] = [platform for platform, _ in success_rates]
            
            # Total views ranking
            total_views = [(platform, data.get("engagement", {}).get("total_views", 0)) for platform, data in comparison.items()]
            total_views.sort(key=lambda x: x[1], reverse=True)
            rankings["total_views"] = [platform for platform, _ in total_views]
            
            # Engagement rate ranking
            engagement_rates = [(platform, data.get("engagement", {}).get("avg_engagement_rate", 0)) for platform, data in comparison.items()]
            engagement_rates.sort(key=lambda x: x[1], reverse=True)
            rankings["engagement_rate"] = [platform for platform, _ in engagement_rates]
            
            return rankings
            
        except Exception as e:
            logger.error(f"Platform ranking calculation failed: {e}")
            return {}
    
    async def _log_event(self, distribution_id: str, event_type: TrackingEventType,
                        platform: Optional[PlatformType] = None,
                        data: Optional[Dict[str, Any]] = None,
                        platform_distribution_id: Optional[str] = None) -> None:
        """Log a tracking event"""
        
        try:
            event = TrackingEvent(
                event_id=hashlib.md5(f"{distribution_id}:{event_type.value}:{datetime.utcnow()}".encode()).hexdigest(),
                distribution_id=distribution_id,
                platform_distribution_id=platform_distribution_id,
                event_type=event_type,
                platform=platform,
                data=data or {}
            )
            
            await self.tracking_events_collection.insert_one(asdict(event))
            
        except Exception as e:
            logger.error(f"Event logging failed: {e}")
    
    async def _log_event_by_platform_id(self, platform_distribution_id: str,
                                      event_type: TrackingEventType,
                                      data: Optional[Dict[str, Any]] = None) -> None:
        """Log event by platform distribution ID"""
        
        try:
            # Get platform distribution to find distribution ID
            platform_dist = await self.platform_distributions_collection.find_one(
                {"platform_distribution_id": platform_distribution_id}
            )
            
            if platform_dist:
                await self._log_event(
                    distribution_id=platform_dist["distribution_id"],
                    event_type=event_type,
                    platform=PlatformType(platform_dist["platform"]),
                    data=data,
                    platform_distribution_id=platform_distribution_id
                )
                
        except Exception as e:
            logger.error(f"Platform event logging failed: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Check if analytics cache is valid"""
        return (datetime.utcnow() - self._last_cache_update) < self._cache_ttl


async def create_distribution_tracker(db: AsyncIOMotorDatabase) -> DistributionTracker:
    """
    Factory function to create and initialize Distribution Tracker
    
    Args:
        db: MongoDB database connection
        
    Returns:
        DistributionTracker: Initialized distribution tracker
    """
    tracker = DistributionTracker(db)
    await tracker.initialize()
    return tracker