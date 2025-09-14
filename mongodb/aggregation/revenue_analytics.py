"""Revenue Analytics Module
=========================

Financial analytics, monetization tracking, and revenue optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .pipeline_builder import PipelineBuilder, get_pipeline_builder

logger = logging.getLogger(__name__)

class RevenueAnalytics:
    """Revenue and monetization analytics engine."""
    
    def __init__(self, pipeline_builder -> None: Optional[PipelineBuilder] = None) -> None:
        """Initialize revenue analytics."""
        self.pipeline_builder = pipeline_builder or get_pipeline_builder()
    
    def get_daily_revenue(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily revenue breakdown."""
        pipeline = (self.pipeline_builder.clear()
                   .match({
                       "transaction_date": {"$gte": start_date, "$lte": end_date},
                       "status": "completed"
                   })
                   .group(
                       {"$dateToString": {"format": "%Y-%m-%d", "date": "$transaction_date"}},
                       {
                           "daily_revenue": {"$sum": "$amount"},
                           "transaction_count": {"$sum": 1},
                           "avg_transaction": {"$avg": "$amount"},
                           "unique_users": {"$addToSet": "$user_id"}
                       }
                   )
                   .project({
                       "_id": 1,
                       "daily_revenue": {"$round": ["$daily_revenue", 2]},
                       "transaction_count": 1,
                       "avg_transaction": {"$round": ["$avg_transaction", 2]},
                       "unique_users_count": {"$size": "$unique_users"}
                   })
                   .sort({"_id": 1})
                   .build())
        
        return pipeline
    
    def get_user_lifetime_value(self, min_transactions: int = 2) -> List[Dict[str, Any]]:
        """Calculate user lifetime value metrics."""
        pipeline = (self.pipeline_builder.clear()
                   .match({"status": "completed"})
                   .group(
                       "$user_id",
                       {
                           "total_revenue": {"$sum": "$amount"},
                           "transaction_count": {"$sum": 1},
                           "first_transaction": {"$min": "$transaction_date"},
                           "last_transaction": {"$max": "$transaction_date"},
                           "avg_transaction": {"$avg": "$amount"}
                       }
                   )
                   .match({"transaction_count": {"$gte": min_transactions}})
                   .project({
                       "_id": 1,
                       "total_revenue": {"$round": ["$total_revenue", 2]},
                       "transaction_count": 1,
                       "avg_transaction": {"$round": ["$avg_transaction", 2]},
                       "customer_lifespan_days": {
                           "$divide": [
                               {"$subtract": ["$last_transaction", "$first_transaction"]},
                               86400000  # Convert to days
                           ]
                       }
                   })
                   .sort({"total_revenue": -1})
                   .build())
        
        return pipeline

_default_analytics: Optional[RevenueAnalytics] = None

def get_revenue_analytics() -> RevenueAnalytics:
    global _default_analytics
    if _default_analytics is None:
        _default_analytics = RevenueAnalytics()
    return _default_analytics

__all__ = ['RevenueAnalytics', 'get_revenue_analytics']