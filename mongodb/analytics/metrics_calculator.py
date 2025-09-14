"""MongoDB Metrics Calculator
===========================

Advanced business metrics calculation and KPI tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Business metric definition."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class KPISummary:
    """KPI summary report."""
    period_start: datetime
    period_end: datetime
    total_users: int
    active_users: int
    content_uploads: int
    engagement_rate: float
    revenue_total: float
    conversion_rate: float

class MetricsCalculator:
    """Advanced business metrics calculator for creator platform analytics."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize metrics calculator.
        
        Args:
            client: MongoDB client instance
            database_name: Target database name
        """
        self.client = client
        self.database = client[database_name]
        
        # Collection mappings for Ainflue platform
        self._collections = {
            'users': 'users',
            'content': 'content',
            'interactions': 'interactions',
            'collaborations': 'collaborations',
            'revenue': 'revenue_events',
            'analytics_events': 'analytics_events'
        }
        
        # Metric cache
        self._metric_cache: Dict[str, Metric] = {}
        self._cache_ttl = 300  # 5 minutes
    
    def calculate_kpi_summary(self, start_date: datetime, end_date: datetime) -> KPISummary:
        """Calculate comprehensive KPI summary for date range.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            KPI summary report
        """
        try:
            # Calculate individual metrics
            total_users = self.calculate_total_users(start_date, end_date)
            active_users = self.calculate_active_users(start_date, end_date)
            content_uploads = self.calculate_content_uploads(start_date, end_date)
            engagement_rate = self.calculate_engagement_rate(start_date, end_date)
            revenue_total = self.calculate_total_revenue(start_date, end_date)
            conversion_rate = self.calculate_conversion_rate(start_date, end_date)
            
            summary = KPISummary(
                period_start=start_date,
                period_end=end_date,
                total_users=total_users,
                active_users=active_users,
                content_uploads=content_uploads,
                engagement_rate=engagement_rate,
                revenue_total=revenue_total,
                conversion_rate=conversion_rate
            )
            
            logger.info(f"Generated KPI summary for period {start_date} to {end_date}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to calculate KPI summary: {e}")
            raise
    
    def calculate_total_users(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate total users registered in period."""
        try:
            users_collection = self.database[self._collections['users']]
            
            query = {
                'createdAt': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            count = users_collection.count_documents(query)
            
            # Cache result
            metric = Metric(
                name='total_users',
                value=float(count),
                unit='count',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['total_users'] = metric
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to calculate total users: {e}")
            return 0
    
    def calculate_active_users(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate active users in period (users with content uploads or interactions)."""
        try:
            # Get users who uploaded content
            content_collection = self.database[self._collections['content']]
            content_users = content_collection.distinct(
                'userId',
                {
                    'createdAt': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            )
            
            # Get users who had interactions
            interactions_collection = self.database[self._collections['interactions']]
            interaction_users = interactions_collection.distinct(
                'userId',
                {
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            )
            
            # Combine and deduplicate
            active_users = set(content_users) | set(interaction_users)
            count = len(active_users)
            
            # Cache result
            metric = Metric(
                name='active_users',
                value=float(count),
                unit='count',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['active_users'] = metric
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to calculate active users: {e}")
            return 0
    
    def calculate_content_uploads(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate total content uploads in period."""
        try:
            content_collection = self.database[self._collections['content']]
            
            query = {
                'createdAt': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            count = content_collection.count_documents(query)
            
            # Cache result
            metric = Metric(
                name='content_uploads',
                value=float(count),
                unit='count',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['content_uploads'] = metric
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to calculate content uploads: {e}")
            return 0
    
    def calculate_engagement_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate engagement rate (interactions per content piece)."""
        try:
            # Get total content in period
            content_count = self.calculate_content_uploads(start_date, end_date)
            
            if content_count == 0:
                return 0.0
            
            # Get total interactions
            interactions_collection = self.database[self._collections['interactions']]
            interaction_count = interactions_collection.count_documents({
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            })
            
            engagement_rate = (interaction_count / content_count) * 100
            
            # Cache result
            metric = Metric(
                name='engagement_rate',
                value=engagement_rate,
                unit='percentage',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['engagement_rate'] = metric
            
            return engagement_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement rate: {e}")
            return 0.0
    
    def calculate_total_revenue(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate total revenue in period."""
        try:
            revenue_collection = self.database[self._collections['revenue']]
            
            pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_date,
                            '$lte': end_date
                        },
                        'status': 'completed'
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_revenue': {'$sum': '$amount'}
                    }
                }
            ]
            
            result = list(revenue_collection.aggregate(pipeline))
            total_revenue = result[0]['total_revenue'] if result else 0.0
            
            # Cache result
            metric = Metric(
                name='total_revenue',
                value=total_revenue,
                unit='currency',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['total_revenue'] = metric
            
            return total_revenue
            
        except Exception as e:
            logger.error(f"Failed to calculate total revenue: {e}")
            return 0.0
    
    def calculate_conversion_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate conversion rate (paying users / total users)."""
        try:
            # Get total users in period
            total_users = self.calculate_total_users(start_date, end_date)
            
            if total_users == 0:
                return 0.0
            
            # Get paying users
            revenue_collection = self.database[self._collections['revenue']]
            paying_users = revenue_collection.distinct(
                'userId',
                {
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    },
                    'status': 'completed'
                }
            )
            
            conversion_rate = (len(paying_users) / total_users) * 100
            
            # Cache result
            metric = Metric(
                name='conversion_rate',
                value=conversion_rate,
                unit='percentage',
                timestamp=datetime.utcnow()
            )
            self._metric_cache['conversion_rate'] = metric
            
            return conversion_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate conversion rate: {e}")
            return 0.0
    
    def calculate_creator_performance_metrics(self, user_id: str,
                                            start_date: datetime,
                                            end_date: datetime) -> Dict[str, Any]:
        """Calculate performance metrics for specific creator.
        
        Args:
            user_id: Creator user ID
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Creator performance metrics
        """
        try:
            content_collection = self.database[self._collections['content']]
            interactions_collection = self.database[self._collections['interactions']]
            revenue_collection = self.database[self._collections['revenue']]
            
            # Content metrics
            content_query = {
                'userId': user_id,
                'createdAt': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            total_content = content_collection.count_documents(content_query)
            
            # Get content IDs for interaction calculation
            content_ids = list(content_collection.find(content_query, {'_id': 1}))
            content_id_list = [doc['_id'] for doc in content_ids]
            
            # Interaction metrics
            total_interactions = 0
            if content_id_list:
                total_interactions = interactions_collection.count_documents({
                    'contentId': {'$in': content_id_list},
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                })
            
            # Revenue metrics
            revenue_pipeline = [
                {
                    '$match': {
                        'userId': user_id,
                        'timestamp': {
                            '$gte': start_date,
                            '$lte': end_date
                        },
                        'status': 'completed'
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_revenue': {'$sum': '$amount'},
                        'transaction_count': {'$sum': 1}
                    }
                }
            ]
            
            revenue_result = list(revenue_collection.aggregate(revenue_pipeline))
            total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0.0
            transaction_count = revenue_result[0]['transaction_count'] if revenue_result else 0
            
            # Calculate derived metrics
            avg_interactions_per_content = total_interactions / total_content if total_content > 0 else 0
            avg_revenue_per_content = total_revenue / total_content if total_content > 0 else 0
            avg_revenue_per_transaction = total_revenue / transaction_count if transaction_count > 0 else 0
            
            metrics = {
                'user_id': user_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_content_uploaded': total_content,
                'total_interactions': total_interactions,
                'total_revenue': total_revenue,
                'transaction_count': transaction_count,
                'avg_interactions_per_content': avg_interactions_per_content,
                'avg_revenue_per_content': avg_revenue_per_content,
                'avg_revenue_per_transaction': avg_revenue_per_transaction
            }
            
            logger.info(f"Calculated performance metrics for creator {user_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate creator performance metrics: {e}")
            return {}
    
    def calculate_platform_growth_metrics(self, months_back: int = 12) -> Dict[str, Any]:
        """Calculate platform growth metrics over time.
        
        Args:
            months_back: Number of months to analyze
            
        Returns:
            Growth metrics
        """
        try:
            growth_data = []
            
            # Calculate monthly metrics for the past N months
            for i in range(months_back, 0, -1):
                month_start = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
                month_end = month_start + timedelta(days=30)
                
                monthly_metrics = {
                    'month': month_start.strftime('%Y-%m'),
                    'total_users': self.calculate_total_users(month_start, month_end),
                    'active_users': self.calculate_active_users(month_start, month_end),
                    'content_uploads': self.calculate_content_uploads(month_start, month_end),
                    'total_revenue': self.calculate_total_revenue(month_start, month_end)
                }
                
                growth_data.append(monthly_metrics)
            
            # Calculate growth rates
            for i in range(1, len(growth_data)):
                prev_month = growth_data[i-1]
                curr_month = growth_data[i]
                
                for metric in ['total_users', 'active_users', 'content_uploads', 'total_revenue']:
                    prev_value = prev_month[metric]
                    curr_value = curr_month[metric]
                    
                    if prev_value > 0:
                        growth_rate = ((curr_value - prev_value) / prev_value) * 100
                        curr_month[f'{metric}_growth_rate'] = growth_rate
                    else:
                        curr_month[f'{metric}_growth_rate'] = 0.0
            
            return {
                'months_analyzed': months_back,
                'monthly_data': growth_data,
                'latest_month': growth_data[-1] if growth_data else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate platform growth metrics: {e}")
            return {}
    
    def get_cached_metrics(self) -> Dict[str, Metric]:
        """Get cached metrics.
        
        Returns:
            Dictionary of cached metrics
        """
        # Filter out expired metrics
        current_time = datetime.utcnow()
        valid_metrics = {}
        
        for name, metric in self._metric_cache.items():
            age_seconds = (current_time - metric.timestamp).total_seconds()
            if age_seconds < self._cache_ttl:
                valid_metrics[name] = metric
        
        return valid_metrics
    
    def clear_metric_cache(self) -> None:
        """Clear all cached metrics."""
        self._metric_cache.clear()
        logger.info("Metrics cache cleared")

# Global metrics calculator instance
_default_metrics_calculator: Optional[MetricsCalculator] = None

def get_metrics_calculator(client: MongoClient, database_name: str) -> MetricsCalculator:
    """Get or create default metrics calculator."""
    global _default_metrics_calculator
    if _default_metrics_calculator is None:
        _default_metrics_calculator = MetricsCalculator(client, database_name)
    return _default_metrics_calculator

__all__ = ['MetricsCalculator', 'Metric', 'KPISummary', 'get_metrics_calculator']