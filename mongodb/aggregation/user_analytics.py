"""User Analytics Module
=====================

User behavior analytics with activity tracking, retention analysis,
and engagement pattern detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .pipeline_builder import PipelineBuilder, get_pipeline_builder

logger = logging.getLogger(__name__)

class UserAnalytics:
    """User behavior analytics engine."""
    
    def __init__(self, pipeline_builder -> None: Optional[PipelineBuilder] = None) -> None:
        """Initialize user analytics."""
        self.pipeline_builder = pipeline_builder or get_pipeline_builder()
    
    def get_user_activity_summary(self, user_id: str = None,
                                 date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Get user activity summary."""
        start_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        match_conditions = {"last_activity": {"$gte": start_date}}
        if user_id:
            match_conditions["user_id"] = user_id
        
        pipeline = (self.pipeline_builder.clear()
                   .match(match_conditions)
                   .group(
                       "$user_id",
                       {
                           "total_sessions": {"$sum": 1},
                           "total_time_minutes": {"$sum": {"$divide": ["$session_duration", 60]}},
                           "avg_session_minutes": {"$avg": {"$divide": ["$session_duration", 60]}},
                           "last_activity": {"$max": "$last_activity"},
                           "content_created": {"$sum": {"$cond": [{"$eq": ["$activity_type", "content_create"]}, 1, 0]}},
                           "content_viewed": {"$sum": {"$cond": [{"$eq": ["$activity_type", "content_view"]}, 1, 0]}}
                       }
                   )
                   .project({
                       "_id": 1,
                       "total_sessions": 1,
                       "total_time_minutes": {"$round": ["$total_time_minutes", 2]},
                       "avg_session_minutes": {"$round": ["$avg_session_minutes", 2]},
                       "last_activity": 1,
                       "content_created": 1,
                       "content_viewed": 1,
                       "engagement_score": {
                           "$multiply": [
                               {"$add": ["$content_created", {"$divide": ["$content_viewed", 10]}]},
                               {"$divide": ["$total_sessions", 30]}
                           ]
                       }
                   })
                   .sort({"engagement_score": -1})
                   .build())
        
        return pipeline
    
    def get_retention_cohorts(self, cohort_period: str = "weekly") -> List[Dict[str, Any]]:
        """Get user retention cohort analysis."""
        # Determine cohort grouping based on period
        if cohort_period == "daily":
            date_format = "%Y-%m-%d"
            period_days = 1
        elif cohort_period == "weekly":
            date_format = "%Y-%U"  # Year-Week
            period_days = 7
        else:  # monthly
            date_format = "%Y-%m"
            period_days = 30
        
        pipeline = (self.pipeline_builder.clear()
                   .match({"first_activity": {"$exists": True}})
                   .group(
                       {
                           "cohort": {"$dateToString": {"format": date_format, "date": "$first_activity"}},
                           "user_id": "$user_id"
                       },
                       {
                           "last_activity": {"$max": "$last_activity"},
                           "total_sessions": {"$sum": 1}
                       }
                   )
                   .group(
                       "$_id.cohort",
                       {
                           "cohort_size": {"$sum": 1},
                           "active_users": {
                               "$sum": {
                                   "$cond": [
                                       {"$gte": ["$last_activity", datetime.utcnow() - timedelta(days=period_days)]},
                                       1, 0
                                   ]
                               }
                           }
                       }
                   )
                   .project({
                       "_id": 1,
                       "cohort_size": 1,
                       "active_users": 1,
                       "retention_rate": {
                           "$multiply": [
                               {"$divide": ["$active_users", "$cohort_size"]},
                               100
                           ]
                       }
                   })
                   .sort({"_id": -1})
                   .build())
        
        return pipeline

# Global user analytics instance
_default_analytics: Optional[UserAnalytics] = None

def get_user_analytics() -> UserAnalytics:
    """Get or create default user analytics."""
    global _default_analytics
    if _default_analytics is None:
        _default_analytics = UserAnalytics()
    return _default_analytics

__all__ = ['UserAnalytics', 'get_user_analytics']