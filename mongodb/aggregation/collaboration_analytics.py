"""Collaboration Analytics Module
==============================

Project collaboration metrics, team performance analysis,
and collaboration success tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .pipeline_builder import PipelineBuilder, get_pipeline_builder

logger = logging.getLogger(__name__)

class CollaborationAnalytics:
    """Collaboration analytics engine for team projects."""
    
    def __init__(self, pipeline_builder: Optional[PipelineBuilder] = None):
        """Initialize collaboration analytics."""
        self.pipeline_builder = pipeline_builder or get_pipeline_builder()
    
    def get_project_success_metrics(self, date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Get project success and completion metrics."""
        start_date = datetime.utcnow() - timedelta(days=date_range_days)
        
        pipeline = (self.pipeline_builder.clear()
                   .match({
                       "created_at": {"$gte": start_date},
                       "project_type": "collaboration"
                   })
                   .group(
                       "$project_status",
                       {
                           "project_count": {"$sum": 1},
                           "avg_completion_time": {"$avg": "$completion_time_days"},
                           "total_collaborators": {"$sum": "$collaborator_count"},
                           "avg_rating": {"$avg": "$final_rating"}
                       }
                   )
                   .build())
        
        return pipeline
    
    def get_collaboration_efficiency(self) -> List[Dict[str, Any]]:
        """Analyze collaboration efficiency metrics."""
        pipeline = (self.pipeline_builder.clear()
                   .match({"collaboration_data": {"$exists": True}})
                   .project({
                       "project_id": 1,
                       "efficiency_score": {
                           "$divide": [
                               "$expected_completion_time",
                               "$actual_completion_time"
                           ]
                       },
                       "communication_score": "$collaboration_data.communication_rating",
                       "deliverable_quality": "$collaboration_data.quality_score"
                   })
                   .sort({"efficiency_score": -1})
                   .build())
        
        return pipeline

_default_analytics: Optional[CollaborationAnalytics] = None

def get_collaboration_analytics() -> CollaborationAnalytics:
    global _default_analytics
    if _default_analytics is None:
        _default_analytics = CollaborationAnalytics()
    return _default_analytics

__all__ = ['CollaborationAnalytics', 'get_collaboration_analytics']