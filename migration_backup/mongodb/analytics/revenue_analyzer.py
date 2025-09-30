"""MongoDB Revenue Analyzer
=========================

Revenue analytics and monetization optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class RevenueAnalyzer:
    """Revenue analyzer for monetization optimization."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize revenue analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def analyze_revenue_streams(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze different revenue streams and their performance."""
        try:
            revenue_collection = self.database.revenue_events
            
            # Analyze by revenue type
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lte': end_date},
                        'status': 'completed'
                    }
                },
                {
                    '$group': {
                        '_id': '$type',
                        'total_revenue': {'$sum': '$amount'},
                        'transaction_count': {'$sum': 1},
                        'avg_transaction_value': {'$avg': '$amount'}
                    }
                },
                {
                    '$sort': {'total_revenue': -1}
                }
            ]
            
            revenue_by_type = list(revenue_collection.aggregate(pipeline))
            
            # Calculate total revenue
            total_revenue = sum(stream['total_revenue'] for stream in revenue_by_type)
            
            # Add percentage to each stream
            for stream in revenue_by_type:
                stream['percentage'] = (stream['total_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            
            # Analyze top earning creators
            top_creators_pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_date, '$lte': end_date},
                        'status': 'completed'
                    }
                },
                {
                    '$group': {
                        '_id': '$userId',
                        'total_earnings': {'$sum': '$amount'},
                        'transaction_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'total_earnings': -1}
                },
                {
                    '$limit': 10
                }
            ]
            
            top_creators = list(revenue_collection.aggregate(top_creators_pipeline))
            
            return {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_revenue': total_revenue,
                'revenue_streams': revenue_by_type,
                'top_creators': top_creators
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze revenue streams: {e}")
            return {}

__all__ = ['RevenueAnalyzer']