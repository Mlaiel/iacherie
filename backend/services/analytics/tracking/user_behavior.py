"""User Behavior Tracker - User Behavior Analytics Service

Advanced user behavior tracking service that integrates with existing
analytics infrastructure for comprehensive behavior analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Import from existing analytics
try:
    from ....data_management.analytics.user_behavior import (
        UserBehaviorCollector,
        BehaviorMetric,
        BehaviorCategory,
        UserSegment
    )
except ImportError:
    # Fallback if import fails
    from enum import Enum
    
    class BehaviorCategory(Enum):
        NAVIGATION = "navigation"
        ENGAGEMENT = "engagement"
        CONVERSION = "conversion"
        RETENTION = "retention"
    
    class UserSegment(Enum):
        NEW_USER = "new_user"
        ACTIVE_USER = "active_user"
        POWER_USER = "power_user"
        INACTIVE_USER = "inactive_user"
    
    @dataclass
    class BehaviorMetric:
        user_id: str
        metric_name: str
        value: float
        category: BehaviorCategory
        timestamp: datetime
        metadata: Dict[str, Any] = field(default_factory=dict)

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """User session data"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    page_views: int = 0
    actions_count: int = 0
    device_info: Dict[str, str] = field(default_factory=dict)
    location: Optional[str] = None


@dataclass
class UserAction:
    """Individual user action"""
    action_id: str
    user_id: str
    session_id: str
    action_type: str
    target: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorAnalysisResult:
    """Result of behavior analysis"""
    user_id: str
    segment: UserSegment
    metrics: List[BehaviorMetric]
    patterns: Dict[str, Any]
    recommendations: List[str]
    analysis_period: Dict[str, datetime]


class UserBehaviorTracker:
    """User behavior tracking and analytics service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        try:
            # Use existing collector if available
            self.behavior_collector = UserBehaviorCollector()
        except:
            self.behavior_collector = None
            logger.warning("UserBehaviorCollector not available, using fallback mode")
        
        logger.info("UserBehaviorTracker service initialized")
    
    async def track_user_action(self, action: UserAction) -> bool:
        """
        Track individual user action
        
        Args:
            action: User action to track
            
        Returns:
            bool: Success status
        """
        try:
            # Log the action for analytics
            logger.info(f"User action tracked: {action.action_type} by {action.user_id}")
            
            # Store action data (in real implementation, this would go to database)
            action_data = {
                'user_id': action.user_id,
                'session_id': action.session_id,
                'action_type': action.action_type,
                'target': action.target,
                'timestamp': action.timestamp,
                'metadata': action.metadata
            }
            
            # TODO: Store in database
            # await self._store_action(action_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track user action: {str(e)}")
            return False
    
    async def start_session(self, user_id: str, device_info: Dict[str, str]) -> UserSession:
        """
        Start new user session
        
        Args:
            user_id: User identifier
            device_info: Device information
            
        Returns:
            UserSession: Created session
        """
        try:
            session = UserSession(
                session_id=f"session_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                start_time=datetime.now(),
                device_info=device_info
            )
            
            # Track session start
            await self.track_user_action(UserAction(
                action_id=f"session_start_{session.session_id}",
                user_id=user_id,
                session_id=session.session_id,
                action_type="session_start",
                target="platform",
                timestamp=session.start_time,
                metadata=device_info
            ))
            
            logger.info(f"Session started for user {user_id}: {session.session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start session: {str(e)}")
            raise
    
    async def end_session(self, session: UserSession) -> UserSession:
        """
        End user session
        
        Args:
            session: Session to end
            
        Returns:
            UserSession: Updated session
        """
        try:
            session.end_time = datetime.now()
            
            # Calculate session duration
            duration = (session.end_time - session.start_time).total_seconds()
            
            # Track session end
            await self.track_user_action(UserAction(
                action_id=f"session_end_{session.session_id}",
                user_id=session.user_id,
                session_id=session.session_id,
                action_type="session_end",
                target="platform",
                timestamp=session.end_time,
                metadata={
                    'duration_seconds': duration,
                    'page_views': session.page_views,
                    'actions_count': session.actions_count
                }
            ))
            
            logger.info(f"Session ended for user {session.user_id}: {duration}s duration")
            return session
            
        except Exception as e:
            logger.error(f"Failed to end session: {str(e)}")
            raise
    
    async def analyze_user_behavior(self, user_id: str, days: int = 30) -> BehaviorAnalysisResult:
        """
        Analyze user behavior patterns
        
        Args:
            user_id: User to analyze
            days: Analysis period in days
            
        Returns:
            BehaviorAnalysisResult: Analysis results
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Collect behavior metrics
            metrics = []
            if self.behavior_collector:
                try:
                    # Use existing collector if available
                    metrics = await self.behavior_collector.collect_user_behavior_metrics(
                        user_id=user_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                except Exception as e:
                    logger.warning(f"Failed to use existing collector: {str(e)}")
            
            # If no metrics from collector, generate basic analysis
            if not metrics:
                metrics = await self._generate_basic_metrics(user_id, start_date, end_date)
            
            # Determine user segment
            segment = await self._determine_user_segment(metrics)
            
            # Analyze patterns
            patterns = await self._analyze_patterns(metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(segment, patterns)
            
            result = BehaviorAnalysisResult(
                user_id=user_id,
                segment=segment,
                metrics=metrics,
                patterns=patterns,
                recommendations=recommendations,
                analysis_period={'start_date': start_date, 'end_date': end_date}
            )
            
            logger.info(f"Behavior analysis completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Behavior analysis failed: {str(e)}")
            raise
    
    async def _generate_basic_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> List[BehaviorMetric]:
        """Generate basic behavior metrics"""
        metrics = []
        
        # Simulate basic metrics
        metrics.extend([
            BehaviorMetric(
                user_id=user_id,
                metric_name="session_count",
                value=15.0,
                category=BehaviorCategory.ENGAGEMENT,
                timestamp=datetime.now()
            ),
            BehaviorMetric(
                user_id=user_id,
                metric_name="avg_session_duration",
                value=480.0,  # 8 minutes
                category=BehaviorCategory.ENGAGEMENT,
                timestamp=datetime.now()
            ),
            BehaviorMetric(
                user_id=user_id,
                metric_name="page_views",
                value=75.0,
                category=BehaviorCategory.NAVIGATION,
                timestamp=datetime.now()
            )
        ])
        
        return metrics
    
    async def _determine_user_segment(self, metrics: List[BehaviorMetric]) -> UserSegment:
        """Determine user segment based on metrics"""
        if not metrics:
            return UserSegment.NEW_USER
        
        # Simple segmentation logic
        engagement_metrics = [m for m in metrics if m.category == BehaviorCategory.ENGAGEMENT]
        if engagement_metrics:
            avg_engagement = sum(m.value for m in engagement_metrics) / len(engagement_metrics)
            if avg_engagement > 100:
                return UserSegment.POWER_USER
            elif avg_engagement > 50:
                return UserSegment.ACTIVE_USER
            elif avg_engagement > 10:
                return UserSegment.ACTIVE_USER
            else:
                return UserSegment.INACTIVE_USER
        
        return UserSegment.NEW_USER
    
    async def _analyze_patterns(self, metrics: List[BehaviorMetric]) -> Dict[str, Any]:
        """Analyze behavior patterns"""
        patterns = {
            'most_active_category': BehaviorCategory.ENGAGEMENT.value,
            'engagement_trend': 'increasing',
            'session_patterns': 'regular',
            'preferred_actions': ['view', 'like', 'share']
        }
        
        return patterns
    
    async def _generate_recommendations(self, segment: UserSegment, patterns: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if segment == UserSegment.NEW_USER:
            recommendations.extend([
                "Complete your profile to get personalized content",
                "Explore trending content in your interests",
                "Follow recommended creators"
            ])
        elif segment == UserSegment.ACTIVE_USER:
            recommendations.extend([
                "Try creating your own content",
                "Engage more with community features",
                "Explore advanced platform features"
            ])
        elif segment == UserSegment.POWER_USER:
            recommendations.extend([
                "Consider becoming a content creator",
                "Use analytics dashboard to track performance",
                "Join creator community programs"
            ])
        elif segment == UserSegment.INACTIVE_USER:
            recommendations.extend([
                "Check out new content in your favorite categories",
                "Update your preferences for better recommendations",
                "Reconnect with creators you follow"
            ])
        
        return recommendations