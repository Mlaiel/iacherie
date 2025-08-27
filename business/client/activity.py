"""
Activity Manager - Client activity tracking and analytics.

Tracks comprehensive client activities, engagement metrics, and behavioral analytics
for creators on the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
from enum import Enum
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_, or_
from pydantic import BaseModel, validator

from ...core.database import get_db
from ...core.exceptions import ActivityServiceError
from ...models.activity import (
    ClientActivity, ActivityType, ActivityStatus, SessionLog,
    EngagementMetric, ContentInteraction, CollaborationActivity
)
from ...services.analytics.engagement import EngagementAnalytics
from ...services.analytics.behavioral import BehaviorAnalytics
from ...services.cache.redis_cache import RedisCache
from ...utils.time_utils import TimeUtils
from ...utils.geo_utils import GeoUtils


logger = logging.getLogger(__name__)


class ActivityCategory(str, Enum):
    """Activity categories for classification."""
    AUTHENTICATION = "authentication"
    CONTENT_MANAGEMENT = "content_management"
    PROFILE_MANAGEMENT = "profile_management"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    COMMUNICATION = "communication"
    SETTINGS = "settings"
    ANALYTICS = "analytics"


class InteractionType(str, Enum):
    """Content interaction types."""
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    DOWNLOAD = "download"
    BOOKMARK = "bookmark"
    REPORT = "report"


class SessionData(BaseModel):
    """Session data for activity tracking."""
    ip_address: str
    user_agent: str
    device_type: Optional[str] = None
    browser: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    referrer: Optional[str] = None


class ActivityFilter(BaseModel):
    """Activity filtering options."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    activity_types: Optional[List[ActivityType]] = None
    categories: Optional[List[ActivityCategory]] = None
    status_filter: Optional[ActivityStatus] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class ActivityManager:
    """
    Comprehensive activity tracking and analytics system.
    
    Features:
    - Real-time activity logging
    - Session management and tracking
    - Content interaction analytics
    - Behavioral pattern analysis
    - Security event monitoring
    - Engagement metrics calculation
    - Activity reporting and insights
    - Performance optimization with caching
    """
    
    def __init__(
        self,
        db: Session,
        engagement_analytics: EngagementAnalytics,
        behavior_analytics: BehaviorAnalytics,
        redis_cache: RedisCache
    ):
        self.db = db
        self.engagement_analytics = engagement_analytics
        self.behavior_analytics = behavior_analytics
        self.redis_cache = redis_cache
        self.time_utils = TimeUtils()
        self.geo_utils = GeoUtils()
        
        # Activity importance levels
        self.activity_importance = {
            ActivityType.LOGIN: 5,
            ActivityType.CONTENT_UPLOAD: 10,
            ActivityType.PROFILE_UPDATE: 3,
            ActivityType.SUBSCRIPTION_CHANGE: 8,
            ActivityType.PAYMENT_PROCESSED: 9,
            ActivityType.SECURITY_EVENT: 10,
            ActivityType.COLLABORATION_REQUEST: 7,
            ActivityType.CONTENT_SHARED: 6
        }
        
    async def log_activity(
        self,
        client_id: UUID,
        activity_type: ActivityType,
        description: str,
        session_data: Optional[SessionData] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[UUID] = None,
        target_user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Log client activity with comprehensive tracking.
        
        Args:
            client_id: Client performing the activity
            activity_type: Type of activity
            description: Activity description
            session_data: Session information
            metadata: Additional activity metadata
            content_id: Related content ID (if applicable)
            target_user_id: Target user for collaborative activities
            
        Returns:
            Logged activity information
        """
        try:
            # Determine activity category
            category = self._categorize_activity(activity_type)
            
            # Process location data if available
            location_data = None
            if session_data and session_data.ip_address:
                location_data = await self.geo_utils.get_location_from_ip(
                    session_data.ip_address
                )
                
            # Create activity record
            activity = ClientActivity(
                client_id=client_id,
                activity_type=activity_type,
                category=category,
                description=description,
                status=ActivityStatus.COMPLETED,
                metadata=metadata or {},
                content_id=content_id,
                target_user_id=target_user_id,
                ip_address=session_data.ip_address if session_data else None,
                user_agent=session_data.user_agent if session_data else None,
                device_type=session_data.device_type if session_data else None,
                browser=session_data.browser if session_data else None,
                location_data=location_data,
                referrer=session_data.referrer if session_data else None,
                importance_score=self.activity_importance.get(activity_type, 5)
            )
            
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            # Update real-time activity cache
            await self._update_activity_cache(client_id, activity)
            
            # Process security-relevant activities
            if activity_type in [ActivityType.LOGIN, ActivityType.SECURITY_EVENT]:
                await self._process_security_activity(activity)
                
            # Update engagement metrics asynchronously
            if activity_type in [ActivityType.CONTENT_VIEW, ActivityType.CONTENT_SHARED]:
                await self._update_engagement_metrics(activity)
                
            logger.debug(f"Activity logged for client {client_id}: {activity_type.value}")
            
            return {
                "activity_id": str(activity.id),
                "timestamp": activity.created_at.isoformat(),
                "type": activity_type.value,
                "category": category.value,
                "importance": activity.importance_score
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error logging activity: {e}")
            raise ActivityServiceError("Failed to log activity") from e
            
    async def start_session(
        self,
        client_id: UUID,
        session_data: SessionData
    ) -> Dict[str, Any]:
        """
        Start new client session with tracking.
        
        Args:
            client_id: Client identifier
            session_data: Session initialization data
            
        Returns:
            Session information
        """
        try:
            # Check for existing active session
            existing_session = self.db.query(SessionLog).filter(
                SessionLog.client_id == client_id,
                SessionLog.ended_at.is_(None)
            ).first()
            
            if existing_session:
                # End previous session
                await self.end_session(existing_session.session_id)
                
            # Process device and browser info
            device_info = await self._parse_user_agent(session_data.user_agent)
            location_data = await self.geo_utils.get_location_from_ip(session_data.ip_address)
            
            # Create new session
            session = SessionLog(
                client_id=client_id,
                session_id=UUID(),
                ip_address=session_data.ip_address,
                user_agent=session_data.user_agent,
                device_type=device_info.get('device_type', 'unknown'),
                browser=device_info.get('browser', 'unknown'),
                browser_version=device_info.get('browser_version'),
                os=device_info.get('os'),
                location_data=location_data,
                referrer=session_data.referrer,
                started_at=datetime.utcnow()
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            # Log session start activity
            await self.log_activity(
                client_id=client_id,
                activity_type=ActivityType.LOGIN,
                description="User session started",
                session_data=session_data,
                metadata={
                    "session_id": str(session.session_id),
                    "device_info": device_info,
                    "location": location_data
                }
            )
            
            # Cache session data for quick access
            await self.redis_cache.set(
                f"session:{session.session_id}",
                {
                    "client_id": str(client_id),
                    "started_at": session.started_at.isoformat(),
                    "device_type": session.device_type,
                    "location": location_data
                },
                expire_seconds=86400  # 24 hours
            )
            
            logger.info(f"Session started for client {client_id}: {session.session_id}")
            
            return {
                "session_id": str(session.session_id),
                "started_at": session.started_at.isoformat(),
                "device_info": device_info,
                "location": location_data
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error starting session: {e}")
            raise ActivityServiceError("Failed to start session") from e
            
    async def end_session(self, session_id: UUID) -> Dict[str, Any]:
        """
        End client session with duration tracking.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        try:
            session = self.db.query(SessionLog).filter(
                SessionLog.session_id == session_id
            ).first()
            
            if not session:
                return {"success": False, "error": "Session not found"}
                
            if session.ended_at:
                return {"success": False, "error": "Session already ended"}
                
            # Calculate session duration
            session.ended_at = datetime.utcnow()
            session.duration_seconds = (session.ended_at - session.started_at).total_seconds()
            
            # Count activities during session
            activity_count = self.db.query(ClientActivity).filter(
                ClientActivity.client_id == session.client_id,
                ClientActivity.created_at >= session.started_at,
                ClientActivity.created_at <= session.ended_at
            ).count()
            
            session.activity_count = activity_count
            self.db.commit()
            
            # Remove from cache
            await self.redis_cache.delete(f"session:{session_id}")
            
            # Log session end
            await self.log_activity(
                client_id=session.client_id,
                activity_type=ActivityType.LOGOUT,
                description="User session ended",
                metadata={
                    "session_id": str(session_id),
                    "duration_minutes": round(session.duration_seconds / 60, 2),
                    "activity_count": activity_count
                }
            )
            
            logger.info(f"Session ended: {session_id}, duration: {session.duration_seconds}s")
            
            return {
                "success": True,
                "session_id": str(session_id),
                "duration_seconds": session.duration_seconds,
                "activity_count": activity_count,
                "ended_at": session.ended_at.isoformat()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error ending session: {e}")
            raise ActivityServiceError("Failed to end session") from e
            
    async def track_content_interaction(
        self,
        client_id: UUID,
        content_id: UUID,
        interaction_type: InteractionType,
        session_data: Optional[SessionData] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track content interaction with detailed analytics.
        
        Args:
            client_id: Client performing interaction
            content_id: Content being interacted with
            interaction_type: Type of interaction
            session_data: Session information
            metadata: Additional interaction data
            
        Returns:
            Interaction tracking result
        """
        try:
            # Create interaction record
            interaction = ContentInteraction(
                client_id=client_id,
                content_id=content_id,
                interaction_type=interaction_type,
                session_data=session_data.dict() if session_data else {},
                metadata=metadata or {},
                ip_address=session_data.ip_address if session_data else None,
                user_agent=session_data.user_agent if session_data else None
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            # Log as activity
            activity_types_map = {
                InteractionType.VIEW: ActivityType.CONTENT_VIEW,
                InteractionType.LIKE: ActivityType.CONTENT_LIKED,
                InteractionType.SHARE: ActivityType.CONTENT_SHARED,
                InteractionType.DOWNLOAD: ActivityType.CONTENT_DOWNLOAD
            }
            
            if interaction_type in activity_types_map:
                await self.log_activity(
                    client_id=client_id,
                    activity_type=activity_types_map[interaction_type],
                    description=f"Content {interaction_type.value}",
                    session_data=session_data,
                    metadata=metadata,
                    content_id=content_id
                )
                
            # Update engagement metrics
            await self.engagement_analytics.record_interaction(
                content_id=content_id,
                client_id=client_id,
                interaction_type=interaction_type.value
            )
            
            # Update real-time engagement cache
            await self._update_real_time_engagement(content_id, interaction_type)
            
            return {
                "interaction_id": str(interaction.id),
                "timestamp": interaction.created_at.isoformat(),
                "type": interaction_type.value
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error tracking interaction: {e}")
            raise ActivityServiceError("Failed to track interaction") from e
            
    async def get_activity_timeline(
        self,
        client_id: UUID,
        activity_filter: Optional[ActivityFilter] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get paginated activity timeline for client.
        
        Args:
            client_id: Client identifier
            activity_filter: Activity filtering options
            page: Page number
            limit: Items per page
            
        Returns:
            Paginated activity timeline
        """
        try:
            query = self.db.query(ClientActivity).filter(
                ClientActivity.client_id == client_id
            )
            
            # Apply filters
            if activity_filter:
                if activity_filter.start_date:
                    query = query.filter(ClientActivity.created_at >= activity_filter.start_date)
                if activity_filter.end_date:
                    query = query.filter(ClientActivity.created_at <= activity_filter.end_date)
                if activity_filter.activity_types:
                    query = query.filter(ClientActivity.activity_type.in_(activity_filter.activity_types))
                if activity_filter.categories:
                    query = query.filter(ClientActivity.category.in_(activity_filter.categories))
                if activity_filter.status_filter:
                    query = query.filter(ClientActivity.status == activity_filter.status_filter)
                if activity_filter.ip_address:
                    query = query.filter(ClientActivity.ip_address == activity_filter.ip_address)
                if activity_filter.device_type:
                    query = query.filter(ClientActivity.device_type == activity_filter.device_type)
                    
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            offset = (page - 1) * limit
            activities = query.order_by(
                ClientActivity.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Format activities
            formatted_activities = []
            for activity in activities:
                formatted_activity = {
                    "id": str(activity.id),
                    "type": activity.activity_type.value,
                    "category": activity.category.value,
                    "description": activity.description,
                    "status": activity.status.value,
                    "importance": activity.importance_score,
                    "timestamp": activity.created_at.isoformat(),
                    "device_type": activity.device_type,
                    "browser": activity.browser,
                    "location": activity.location_data,
                    "metadata": activity.metadata
                }
                
                # Add content information if available
                if activity.content_id:
                    formatted_activity["content_id"] = str(activity.content_id)
                    
                # Add target user information if available
                if activity.target_user_id:
                    formatted_activity["target_user_id"] = str(activity.target_user_id)
                    
                formatted_activities.append(formatted_activity)
                
            return {
                "activities": formatted_activities,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error retrieving activity timeline: {e}")
            raise ActivityServiceError("Failed to retrieve activity timeline") from e
            
    async def get_activity_statistics(
        self,
        client_id: UUID,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity statistics and insights for client.
        
        Args:
            client_id: Client identifier
            period_days: Analysis period in days
            
        Returns:
            Activity statistics and insights
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Activity counts by type
            activity_counts = self.db.query(
                ClientActivity.activity_type,
                func.count(ClientActivity.id)
            ).filter(
                ClientActivity.client_id == client_id,
                ClientActivity.created_at >= start_date
            ).group_by(ClientActivity.activity_type).all()
            
            # Activity counts by day
            daily_activities = self.db.query(
                func.date(ClientActivity.created_at).label('date'),
                func.count(ClientActivity.id).label('count')
            ).filter(
                ClientActivity.client_id == client_id,
                ClientActivity.created_at >= start_date
            ).group_by(func.date(ClientActivity.created_at)).all()
            
            # Session statistics
            session_stats = self.db.query(
                func.count(SessionLog.id).label('session_count'),
                func.avg(SessionLog.duration_seconds).label('avg_duration'),
                func.sum(SessionLog.duration_seconds).label('total_duration')
            ).filter(
                SessionLog.client_id == client_id,
                SessionLog.started_at >= start_date
            ).first()
            
            # Device type distribution
            device_distribution = self.db.query(
                ClientActivity.device_type,
                func.count(ClientActivity.id)
            ).filter(
                ClientActivity.client_id == client_id,
                ClientActivity.created_at >= start_date,
                ClientActivity.device_type.isnot(None)
            ).group_by(ClientActivity.device_type).all()
            
            # Most active hours
            hourly_distribution = self.db.query(
                func.extract('hour', ClientActivity.created_at).label('hour'),
                func.count(ClientActivity.id).label('count')
            ).filter(
                ClientActivity.client_id == client_id,
                ClientActivity.created_at >= start_date
            ).group_by(func.extract('hour', ClientActivity.created_at)).all()
            
            # Engagement metrics
            engagement_metrics = await self.engagement_analytics.get_client_engagement_summary(
                client_id, period_days
            )
            
            # Behavioral insights
            behavioral_insights = await self.behavior_analytics.analyze_client_behavior(
                client_id, period_days
            )
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "activity_summary": {
                    "total_activities": sum(count for _, count in activity_counts),
                    "activity_types": {
                        activity_type.value: count 
                        for activity_type, count in activity_counts
                    },
                    "daily_activities": {
                        date.isoformat(): count 
                        for date, count in daily_activities
                    }
                },
                "session_summary": {
                    "session_count": session_stats.session_count or 0,
                    "avg_duration_minutes": round((session_stats.avg_duration or 0) / 60, 2),
                    "total_duration_hours": round((session_stats.total_duration or 0) / 3600, 2)
                },
                "device_distribution": {
                    device_type: count 
                    for device_type, count in device_distribution
                },
                "hourly_distribution": {
                    str(int(hour)): count 
                    for hour, count in hourly_distribution
                },
                "engagement_metrics": engagement_metrics,
                "behavioral_insights": behavioral_insights
            }
            
        except Exception as e:
            logger.error(f"Error generating activity statistics: {e}")
            raise ActivityServiceError("Failed to generate activity statistics") from e
            
    def _categorize_activity(self, activity_type: ActivityType) -> ActivityCategory:
        """Categorize activity type."""
        category_mapping = {
            ActivityType.LOGIN: ActivityCategory.AUTHENTICATION,
            ActivityType.LOGOUT: ActivityCategory.AUTHENTICATION,
            ActivityType.CONTENT_UPLOAD: ActivityCategory.CONTENT_MANAGEMENT,
            ActivityType.CONTENT_VIEW: ActivityCategory.CONTENT_MANAGEMENT,
            ActivityType.CONTENT_SHARED: ActivityCategory.CONTENT_MANAGEMENT,
            ActivityType.PROFILE_UPDATE: ActivityCategory.PROFILE_MANAGEMENT,
            ActivityType.COLLABORATION_REQUEST: ActivityCategory.COLLABORATION,
            ActivityType.PAYMENT_PROCESSED: ActivityCategory.MONETIZATION,
            ActivityType.SUBSCRIPTION_CHANGE: ActivityCategory.MONETIZATION,
            ActivityType.SETTINGS_CHANGE: ActivityCategory.SETTINGS,
            ActivityType.ANALYTICS_VIEW: ActivityCategory.ANALYTICS
        }
        
        return category_mapping.get(activity_type, ActivityCategory.CONTENT_MANAGEMENT)
        
    async def _update_activity_cache(self, client_id: UUID, activity: ClientActivity) -> None:
        """Update real-time activity cache."""
        cache_key = f"recent_activity:{client_id}"
        recent_activities = await self.redis_cache.get(cache_key) or []
        
        # Add new activity to front of list
        activity_data = {
            "id": str(activity.id),
            "type": activity.activity_type.value,
            "timestamp": activity.created_at.isoformat(),
            "description": activity.description
        }
        
        recent_activities.insert(0, activity_data)
        
        # Keep only last 20 activities
        recent_activities = recent_activities[:20]
        
        await self.redis_cache.set(
            cache_key, recent_activities, expire_seconds=3600
        )
        
    async def _process_security_activity(self, activity: ClientActivity) -> None:
        """Process security-relevant activities."""
        # Implementation would check for suspicious patterns
        pass
        
    async def _update_engagement_metrics(self, activity: ClientActivity) -> None:
        """Update engagement metrics for activity."""
        if activity.content_id:
            await self.engagement_analytics.record_activity(
                content_id=activity.content_id,
                activity_type=activity.activity_type.value
            )
            
    async def _update_real_time_engagement(
        self,
        content_id: UUID,
        interaction_type: InteractionType
    ) -> None:
        """Update real-time engagement metrics."""
        cache_key = f"engagement:{content_id}"
        engagement_data = await self.redis_cache.get(cache_key) or {}
        
        # Increment interaction counter
        counter_key = f"{interaction_type.value}_count"
        engagement_data[counter_key] = engagement_data.get(counter_key, 0) + 1
        engagement_data["last_interaction"] = datetime.utcnow().isoformat()
        
        await self.redis_cache.set(
            cache_key, engagement_data, expire_seconds=3600
        )
        
    async def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Parse user agent string for device and browser info."""
        # Implementation would parse user agent
        return {
            "device_type": "desktop",
            "browser": "unknown",
            "browser_version": "unknown",
            "os": "unknown"
        }
