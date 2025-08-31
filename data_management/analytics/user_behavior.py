"""
User Behavior Analytics Collector - Advanced User Intelligence
=============================================================

Comprehensive user behavior tracking and analysis system for
deep insights into user patterns, preferences, and platform optimization.

Features:
- User journey mapping and funnel analysis
- Behavioral pattern recognition using ML
- Segmentation and cohort analysis
- Engagement scoring and prediction
- Churn prediction and retention strategies

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from ...core.database import get_database_session
from ...models.users import User, UserActivity, UserSession
from ...models.content import Content, ContentView, ContentInteraction
from ...models.analytics import UserEvent, UserSegment


class BehaviorCategory(Enum):
    """User behavior analysis categories."""
    NAVIGATION = "navigation"
    CONTENT_CONSUMPTION = "content_consumption"
    CREATION_PATTERNS = "creation_patterns"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    SOCIAL_INTERACTION = "social_interaction"


class UserSegment(Enum):
    """User segmentation categories."""
    POWER_CREATOR = "power_creator"
    CASUAL_CREATOR = "casual_creator"
    CONTENT_CONSUMER = "content_consumer"
    INACTIVE_USER = "inactive_user"
    CHURNED_USER = "churned_user"
    NEW_USER = "new_user"


@dataclass
class BehaviorMetric:
    """Structured behavior metric data."""
    user_id: str
    metric_name: str
    value: float
    category: BehaviorCategory
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """Comprehensive user behavioral profile."""
    user_id: str
    segment: UserSegment
    engagement_score: float
    churn_probability: float
    ltv_prediction: float
    behavior_patterns: Dict[str, Any]
    last_updated: datetime


class UserBehaviorCollector:
    """
    Advanced user behavior analytics system.
    
    Provides deep insights into user patterns, preferences,
    and optimization opportunities using machine learning.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._user_profiles_cache = {}
        self._ml_models = {}
        
    async def collect_user_behavior_metrics(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BehaviorMetric]:
        """
        Collect comprehensive user behavior metrics.
        
        Args:
            user_id: Specific user to analyze (None for all users)
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            List of behavior metrics
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        try:
            metrics = []
            
            # Collect navigation patterns
            navigation_metrics = await self._collect_navigation_patterns(
                user_id, start_date, end_date
            )
            metrics.extend(navigation_metrics)
            
            # Collect content consumption behavior
            consumption_metrics = await self._collect_content_consumption(
                user_id, start_date, end_date
            )
            metrics.extend(consumption_metrics)
            
            # Collect creation patterns
            creation_metrics = await self._collect_creation_patterns(
                user_id, start_date, end_date
            )
            metrics.extend(creation_metrics)
            
            # Collect engagement metrics
            engagement_metrics = await self._collect_engagement_patterns(
                user_id, start_date, end_date
            )
            metrics.extend(engagement_metrics)
            
            # Collect monetization behavior
            monetization_metrics = await self._collect_monetization_behavior(
                user_id, start_date, end_date
            )
            metrics.extend(monetization_metrics)
            
            self.logger.info(f"Collected {len(metrics)} behavior metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting behavior metrics: {e}")
            raise
            
    async def _collect_navigation_patterns(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[BehaviorMetric]:
        """Collect user navigation and journey patterns."""
        
        async with get_database_session() as session:
            # Build base query
            base_query = select(UserEvent).where(
                and_(
                    UserEvent.created_at >= start_date,
                    UserEvent.created_at <= end_date,
                    UserEvent.event_type.in_(['page_view', 'navigation', 'click'])
                )
            )
            
            if user_id:
                base_query = base_query.where(UserEvent.user_id == user_id)
                
            events_result = await session.execute(base_query)
            events = events_result.fetchall()
            
            metrics = []
            user_sessions = defaultdict(list)
            
            # Group events by user and session
            for event in events:
                user_sessions[event.user_id].append(event)
                
            for uid, user_events in user_sessions.items():
                # Calculate session metrics
                session_duration = self._calculate_session_duration(user_events)
                page_views = len([e for e in user_events if e.event_type == 'page_view'])
                bounce_rate = self._calculate_bounce_rate(user_events)
                
                metrics.extend([
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="avg_session_duration",
                        value=session_duration,
                        category=BehaviorCategory.NAVIGATION,
                        timestamp=datetime.now(),
                        metadata={
                            "sessions_analyzed": len(set(e.session_id for e in user_events)),
                            "total_events": len(user_events)
                        }
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="page_views_per_session",
                        value=page_views,
                        category=BehaviorCategory.NAVIGATION,
                        timestamp=datetime.now()
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="bounce_rate",
                        value=bounce_rate,
                        category=BehaviorCategory.NAVIGATION,
                        timestamp=datetime.now()
                    )
                ])
                
            return metrics
            
    def _calculate_session_duration(self, events: List[UserEvent]) -> float:
        """Calculate average session duration from events."""
        if len(events) < 2:
            return 0.0
            
        sessions = defaultdict(list)
        for event in events:
            sessions[event.session_id].append(event.created_at)
            
        durations = []
        for session_events in sessions.values():
            if len(session_events) >= 2:
                session_events.sort()
                duration = (session_events[-1] - session_events[0]).total_seconds()
                durations.append(duration)
                
        return sum(durations) / len(durations) if durations else 0.0
        
    def _calculate_bounce_rate(self, events: List[UserEvent]) -> float:
        """Calculate bounce rate from navigation events."""
        sessions = defaultdict(int)
        for event in events:
            sessions[event.session_id] += 1
            
        single_page_sessions = sum(1 for count in sessions.values() if count == 1)
        total_sessions = len(sessions)
        
        return (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        
    async def _collect_content_consumption(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[BehaviorMetric]:
        """Collect content consumption behavior patterns."""
        
        async with get_database_session() as session:
            # Content views query
            views_query = select(
                ContentView.user_id,
                func.count(ContentView.id).label('total_views'),
                func.avg(ContentView.duration).label('avg_duration'),
                func.count(ContentView.id.distinct()).label('unique_content')
            ).where(
                and_(
                    ContentView.created_at >= start_date,
                    ContentView.created_at <= end_date
                )
            ).group_by(ContentView.user_id)
            
            if user_id:
                views_query = views_query.where(ContentView.user_id == user_id)
                
            views_result = await session.execute(views_query)
            views_data = views_result.fetchall()
            
            metrics = []
            
            for row in views_data:
                uid = row.user_id
                
                # Content diversity score
                diversity_score = await self._calculate_content_diversity(uid, session)
                
                # Engagement depth
                engagement_depth = row.avg_duration or 0
                
                metrics.extend([
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="content_views_total",
                        value=row.total_views or 0,
                        category=BehaviorCategory.CONTENT_CONSUMPTION,
                        timestamp=datetime.now()
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="avg_content_duration",
                        value=engagement_depth,
                        category=BehaviorCategory.CONTENT_CONSUMPTION,
                        timestamp=datetime.now()
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="content_diversity_score",
                        value=diversity_score,
                        category=BehaviorCategory.CONTENT_CONSUMPTION,
                        timestamp=datetime.now()
                    )
                ])
                
            return metrics
            
    async def _calculate_content_diversity(
        self,
        user_id: str,
        session: AsyncSession
    ) -> float:
        """Calculate content diversity score for user."""
        
        # Get content types viewed by user
        content_types_query = select(
            Content.content_type,
            func.count(ContentView.id)
        ).join(ContentView).where(
            ContentView.user_id == user_id
        ).group_by(Content.content_type)
        
        result = await session.execute(content_types_query)
        type_counts = dict(result.fetchall())
        
        if not type_counts:
            return 0.0
            
        # Calculate Shannon diversity index
        total_views = sum(type_counts.values())
        diversity = 0.0
        
        for count in type_counts.values():
            if count > 0:
                proportion = count / total_views
                diversity -= proportion * np.log2(proportion)
                
        return diversity
        
    async def _collect_creation_patterns(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[BehaviorMetric]:
        """Collect content creation behavior patterns."""
        
        async with get_database_session() as session:
            # Content creation query
            creation_query = select(
                Content.user_id,
                func.count(Content.id).label('total_uploads'),
                func.avg(Content.file_size).label('avg_file_size'),
                Content.content_type,
                func.count(Content.id).label('type_count')
            ).where(
                and_(
                    Content.created_at >= start_date,
                    Content.created_at <= end_date
                )
            ).group_by(Content.user_id, Content.content_type)
            
            if user_id:
                creation_query = creation_query.where(Content.user_id == user_id)
                
            creation_result = await session.execute(creation_query)
            creation_data = creation_result.fetchall()
            
            metrics = []
            user_creation_stats = defaultdict(lambda: {
                'total_uploads': 0,
                'avg_file_size': 0,
                'content_types': {}
            })
            
            # Aggregate by user
            for row in creation_data:
                uid = row.user_id
                user_creation_stats[uid]['total_uploads'] += row.total_uploads or 0
                user_creation_stats[uid]['avg_file_size'] = row.avg_file_size or 0
                user_creation_stats[uid]['content_types'][row.content_type] = row.type_count or 0
                
            for uid, stats in user_creation_stats.items():
                # Creation frequency
                days_in_period = (end_date - start_date).days
                creation_frequency = stats['total_uploads'] / max(days_in_period, 1)
                
                # Content type preference
                preferred_type = max(
                    stats['content_types'].items(),
                    key=lambda x: x[1],
                    default=('unknown', 0)
                )[0]
                
                metrics.extend([
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="creation_frequency_daily",
                        value=creation_frequency,
                        category=BehaviorCategory.CREATION_PATTERNS,
                        timestamp=datetime.now(),
                        metadata={
                            "total_uploads": stats['total_uploads'],
                            "period_days": days_in_period
                        }
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="avg_content_size",
                        value=stats['avg_file_size'],
                        category=BehaviorCategory.CREATION_PATTERNS,
                        timestamp=datetime.now()
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="content_type_diversity",
                        value=len(stats['content_types']),
                        category=BehaviorCategory.CREATION_PATTERNS,
                        timestamp=datetime.now(),
                        metadata={
                            "preferred_type": preferred_type,
                            "type_distribution": stats['content_types']
                        }
                    )
                ])
                
            return metrics
            
    async def _collect_engagement_patterns(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[BehaviorMetric]:
        """Collect user engagement behavior patterns."""
        
        async with get_database_session() as session:
            # Engagement interactions query
            interactions_query = select(
                ContentInteraction.user_id,
                ContentInteraction.interaction_type,
                func.count(ContentInteraction.id).label('interaction_count')
            ).where(
                and_(
                    ContentInteraction.created_at >= start_date,
                    ContentInteraction.created_at <= end_date
                )
            ).group_by(ContentInteraction.user_id, ContentInteraction.interaction_type)
            
            if user_id:
                interactions_query = interactions_query.where(
                    ContentInteraction.user_id == user_id
                )
                
            interactions_result = await session.execute(interactions_query)
            interactions_data = interactions_result.fetchall()
            
            metrics = []
            user_engagement = defaultdict(lambda: defaultdict(int))
            
            # Aggregate interactions by user
            for row in interactions_data:
                user_engagement[row.user_id][row.interaction_type] = row.interaction_count
                
            for uid, interactions in user_engagement.items():
                # Calculate engagement score
                engagement_score = self._calculate_engagement_score(interactions)
                
                # Social engagement ratio
                social_interactions = interactions.get('like', 0) + interactions.get('share', 0)
                total_interactions = sum(interactions.values())
                social_ratio = (social_interactions / max(total_interactions, 1)) * 100
                
                metrics.extend([
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="engagement_score",
                        value=engagement_score,
                        category=BehaviorCategory.ENGAGEMENT,
                        timestamp=datetime.now(),
                        metadata={
                            "total_interactions": total_interactions,
                            "interaction_breakdown": dict(interactions)
                        }
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="social_engagement_ratio",
                        value=social_ratio,
                        category=BehaviorCategory.ENGAGEMENT,
                        timestamp=datetime.now()
                    )
                ])
                
            return metrics
            
    def _calculate_engagement_score(self, interactions: Dict[str, int]) -> float:
        """Calculate weighted engagement score."""
        weights = {
            'view': 1.0,
            'like': 2.0,
            'comment': 3.0,
            'share': 4.0,
            'download': 2.5,
            'follow': 5.0
        }
        
        score = 0.0
        for interaction_type, count in interactions.items():
            weight = weights.get(interaction_type, 1.0)
            score += count * weight
            
        return score
        
    async def _collect_monetization_behavior(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[BehaviorMetric]:
        """Collect monetization and revenue behavior patterns."""
        
        async with get_database_session() as session:
            # Revenue generation query
            revenue_query = select(
                Revenue.user_id,
                func.sum(Revenue.amount).label('total_revenue'),
                func.count(Revenue.id).label('revenue_events'),
                func.avg(Revenue.amount).label('avg_revenue_per_event')
            ).where(
                and_(
                    Revenue.created_at >= start_date,
                    Revenue.created_at <= end_date,
                    Revenue.status == 'confirmed'
                )
            ).group_by(Revenue.user_id)
            
            if user_id:
                revenue_query = revenue_query.where(Revenue.user_id == user_id)
                
            revenue_result = await session.execute(revenue_query)
            revenue_data = revenue_result.fetchall()
            
            metrics = []
            
            for row in revenue_data:
                uid = row.user_id
                
                # Revenue efficiency
                revenue_per_day = (row.total_revenue or 0) / max((end_date - start_date).days, 1)
                
                metrics.extend([
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="total_revenue_generated",
                        value=row.total_revenue or 0,
                        category=BehaviorCategory.MONETIZATION,
                        timestamp=datetime.now(),
                        metadata={
                            "currency": "EUR",
                            "revenue_events": row.revenue_events or 0
                        }
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="daily_revenue_rate",
                        value=revenue_per_day,
                        category=BehaviorCategory.MONETIZATION,
                        timestamp=datetime.now()
                    ),
                    BehaviorMetric(
                        user_id=uid,
                        metric_name="avg_revenue_per_event",
                        value=row.avg_revenue_per_event or 0,
                        category=BehaviorCategory.MONETIZATION,
                        timestamp=datetime.now()
                    )
                ])
                
            return metrics
            
    async def generate_user_profiles(
        self,
        user_ids: Optional[List[str]] = None
    ) -> List[UserProfile]:
        """Generate comprehensive user behavioral profiles."""



        
        try:
            # Collect behavior metrics for users
            behavior_metrics = await self.collect_user_behavior_metrics()
            
            # Group metrics by user
            user_metrics = defaultdict(list)
            for metric in behavior_metrics:
                user_metrics[metric.user_id].append(metric)
                
            profiles = []
            
            for uid, metrics in user_metrics.items():
                if user_ids and uid not in user_ids:
                    continue
                    
                # Calculate profile components
                segment = await self._determine_user_segment(uid, metrics)
                engagement_score = self._calculate_user_engagement_score(metrics)
                churn_probability = await self._predict_churn_probability(uid, metrics)
                ltv_prediction = await self._predict_lifetime_value(uid, metrics)
                behavior_patterns = self._extract_behavior_patterns(metrics)
                
                profile = UserProfile(
                    user_id=uid,
                    segment=segment,
                    engagement_score=engagement_score,
                    churn_probability=churn_probability,
                    ltv_prediction=ltv_prediction,
                    behavior_patterns=behavior_patterns,
                    last_updated=datetime.now()
                )
                
                profiles.append(profile)
                
            self.logger.info(f"Generated {len(profiles)} user profiles")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error generating user profiles: {e}")
            raise
            
    async def _determine_user_segment(
        self,
        user_id: str,
        metrics: List[BehaviorMetric]
    ) -> UserSegment:
        """Determine user segment based on behavior patterns."""
        
        # Extract key metrics
        creation_frequency = 0
        engagement_score = 0
        revenue_generated = 0
        
        for metric in metrics:
            if metric.metric_name == "creation_frequency_daily":
                creation_frequency = metric.value
            elif metric.metric_name == "engagement_score":
                engagement_score = metric.value
            elif metric.metric_name == "total_revenue_generated":
                revenue_generated = metric.value
                
        # Segmentation logic
        if creation_frequency > 1.0 and revenue_generated > 1000:
            return UserSegment.POWER_CREATOR
        elif creation_frequency > 0.1 and creation_frequency <= 1.0:
            return UserSegment.CASUAL_CREATOR
        elif engagement_score > 100 and creation_frequency < 0.1:
            return UserSegment.CONTENT_CONSUMER
        elif engagement_score < 10:
            return UserSegment.INACTIVE_USER
        else:
            return UserSegment.NEW_USER
            
    def _calculate_user_engagement_score(self, metrics: List[BehaviorMetric]) -> float:
        """Calculate comprehensive user engagement score."""
        
        score_components = {
            'engagement_score': 0.4,
            'creation_frequency_daily': 0.3,
            'content_views_total': 0.2,
            'social_engagement_ratio': 0.1
        }
        
        total_score = 0.0
        max_possible_score = 100.0
        
        for metric in metrics:
            if metric.metric_name in score_components:
                weight = score_components[metric.metric_name]
                normalized_value = min(metric.value / max_possible_score, 1.0)
                total_score += normalized_value * weight * 100
                
        return min(total_score, 100.0)
        
    async def _predict_churn_probability(
        self,
        user_id: str,
        metrics: List[BehaviorMetric]
    ) -> float:
        """Predict user churn probability using behavioral patterns."""
        
        # Simple churn prediction based on engagement trends
        # In production, this would use ML models
        
        engagement_score = 0
        activity_level = 0
        
        for metric in metrics:
            if metric.metric_name == "engagement_score":
                engagement_score = metric.value
            elif metric.metric_name == "creation_frequency_daily":
                activity_level = metric.value
                
        # Churn probability calculation
        if engagement_score < 10 and activity_level < 0.01:
            return 0.8  # High churn risk
        elif engagement_score < 30 and activity_level < 0.1:
            return 0.5  # Medium churn risk
        elif engagement_score > 70 and activity_level > 0.5:
            return 0.1  # Low churn risk
        else:
            return 0.3  # Default risk level
            
    async def _predict_lifetime_value(
        self,
        user_id: str,
        metrics: List[BehaviorMetric]
    ) -> float:
        """Predict user lifetime value."""
        
        # Extract revenue and engagement metrics
        revenue_generated = 0
        engagement_score = 0
        
        for metric in metrics:
            if metric.metric_name == "total_revenue_generated":
                revenue_generated = metric.value
            elif metric.metric_name == "engagement_score":
                engagement_score = metric.value
                
        # Simple LTV prediction (revenue * engagement factor)
        engagement_multiplier = max(engagement_score / 50.0, 0.5)
        predicted_ltv = revenue_generated * engagement_multiplier * 12  # Annualized
        
        return predicted_ltv
        
    def _extract_behavior_patterns(self, metrics: List[BehaviorMetric]) -> Dict[str, Any]:
        """Extract behavioral patterns from metrics."""
        
        patterns = {
            "primary_activities": [],
            "engagement_trends": {},
            "content_preferences": {},
            "usage_patterns": {}
        }
        
        for metric in metrics:
            category = metric.category.value
            
            if category not in patterns["engagement_trends"]:
                patterns["engagement_trends"][category] = []
                
            patterns["engagement_trends"][category].append({
                "metric": metric.metric_name,
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat()
            })
            
            # Identify primary activities
            if metric.value > 0:
                patterns["primary_activities"].append(metric.metric_name)
                
        return patterns
