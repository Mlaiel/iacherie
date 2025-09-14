"""MongoDB Retention Analyzer
===========================

User retention analysis and churn prediction.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class RetentionAnalyzer:
    """User retention analyzer with churn prediction."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize retention analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def calculate_retention_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate user retention rates for different time periods."""
        try:
            # Get all users who were active in the period
            active_users = list(self.database.users.find({
                'lastActive': {'$gte': start_date, '$lte': end_date}
            }, {'_id': 1, 'createdAt': 1, 'lastActive': 1}))
            
            total_users = len(active_users)
            
            # Calculate 1-day retention
            one_day_retained = 0
            seven_day_retained = 0
            thirty_day_retained = 0
            
            for user in active_users:
                user_start = user.get('lastActive', user['createdAt'])
                
                # Check 1-day retention
                if self._was_active_after_days(user['_id'], user_start, 1):
                    one_day_retained += 1
                
                # Check 7-day retention
                if self._was_active_after_days(user['_id'], user_start, 7):
                    seven_day_retained += 1
                
                # Check 30-day retention
                if self._was_active_after_days(user['_id'], user_start, 30):
                    thirty_day_retained += 1
            
            return {
                'total_users': total_users,
                'retention_1_day': {
                    'count': one_day_retained,
                    'rate': one_day_retained / total_users * 100 if total_users > 0 else 0
                },
                'retention_7_day': {
                    'count': seven_day_retained,
                    'rate': seven_day_retained / total_users * 100 if total_users > 0 else 0
                },
                'retention_30_day': {
                    'count': thirty_day_retained,
                    'rate': thirty_day_retained / total_users * 100 if total_users > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate retention rates: {e}")
            return {}
    
    def _was_active_after_days(self, user_id: str, start_date: datetime, days: int) -> bool:
        """Check if user was active after specified days."""
        target_date = start_date + timedelta(days=days)
        end_date = target_date + timedelta(days=1)
        
        # Check for any activity (content upload, interaction, etc.)
        activity = self.database.content.count_documents({
            'userId': user_id,
            'createdAt': {'$gte': target_date, '$lt': end_date}
        })
        
        return activity > 0

__all__ = ['RetentionAnalyzer']