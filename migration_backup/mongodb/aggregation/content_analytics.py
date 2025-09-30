"""Content Analytics Module
========================

Advanced content performance analytics with engagement metrics,
trend analysis, and content optimization insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .pipeline_builder import PipelineBuilder, get_pipeline_builder

logger = logging.getLogger(__name__)

class ContentAnalytics:
    """Content performance analytics engine."""
    
    def __init__(self, pipeline_builder: Optional[PipelineBuilder] = None):
        """Initialize content analytics."""
        self.pipeline_builder = pipeline_builder or get_pipeline_builder()
    
    def get_content_performance_summary(self, user_id: str = None, 
                                      content_type: str = None,
                                      date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Get content performance summary."""
        start_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        match_conditions = {"created_at": {"$gte": start_date}}
        if user_id:
            match_conditions["user_id"] = user_id
        if content_type:
            match_conditions["content_type"] = content_type
        
        pipeline = (self.pipeline_builder.clear()
                   .match(match_conditions)
                   .project({
                       "content_id": 1,
                       "user_id": 1,
                       "content_type": 1,
                       "title": 1,
                       "created_at": 1,
                       "views": {"$ifNull": ["$analytics.views", 0]},
                       "likes": {"$ifNull": ["$analytics.likes", 0]},
                       "shares": {"$ifNull": ["$analytics.shares", 0]},
                       "comments": {"$ifNull": ["$analytics.comments", 0]},
                       "engagement_rate": {
                           "$divide": [
                               {"$add": ["$analytics.likes", "$analytics.shares", "$analytics.comments"]},
                               {"$max": ["$analytics.views", 1]}
                           ]
                       }
                   })
                   .sort({"views": -1})
                   .build())
        
        return pipeline
    
    def get_trending_content(self, time_window_hours: int = 24, 
                           min_engagement: int = 10) -> List[Dict[str, Any]]:
        """Get trending content based on recent engagement."""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        pipeline = (self.pipeline_builder.clear()
                   .match({
                       "created_at": {"$gte": cutoff_time},
                       "analytics.total_engagement": {"$gte": min_engagement}
                   })
                   .project({
                       "content_id": 1,
                       "title": 1,
                       "content_type": 1,
                       "user_id": 1,
                       "created_at": 1,
                       "velocity": {
                           "$divide": [
                               "$analytics.total_engagement",
                               {"$divide": [
                                   {"$subtract": [datetime.utcnow(), "$created_at"]},
                                   3600000  # Convert to hours
                               ]}
                           ]
                       }
                   })
                   .sort({"velocity": -1})
                   .limit(50)
                   .build())
        
        return pipeline

# Global content analytics instance
_default_analytics: Optional[ContentAnalytics] = None

def get_content_analytics() -> ContentAnalytics:
    """Get or create default content analytics."""
    global _default_analytics
    if _default_analytics is None:
        _default_analytics = ContentAnalytics()
    return _default_analytics

__all__ = ['ContentAnalytics', 'get_content_analytics']