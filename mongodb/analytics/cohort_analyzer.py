"""MongoDB Cohort Analyzer
========================

User cohort analysis for retention and engagement tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class CohortAnalyzer:
    """User cohort analysis for tracking retention and behavior."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize cohort analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def analyze_user_cohorts(self, months_back: int = 6) -> Dict[str, Any]:
        """Analyze user cohorts based on registration month."""
        try:
            cohort_data = {}
            
            for i in range(months_back, 0, -1):
                cohort_month = datetime.utcnow().replace(day=1) - timedelta(days=30 * i)
                cohort_end = cohort_month + timedelta(days=30)
                
                # Get users who registered in this cohort month
                cohort_users = list(self.database.users.find({
                    'createdAt': {
                        '$gte': cohort_month,
                        '$lt': cohort_end
                    }
                }, {'_id': 1, 'createdAt': 1}))
                
                if not cohort_users:
                    continue
                
                cohort_size = len(cohort_users)
                user_ids = [user['_id'] for user in cohort_users]
                
                # Calculate retention for each subsequent month
                retention_data = []
                for month_offset in range(6):  # Track 6 months of retention
                    retention_month = cohort_month + timedelta(days=30 * (month_offset + 1))
                    retention_month_end = retention_month + timedelta(days=30)
                    
                    # Count active users in retention month
                    active_users = self.database.content.distinct('userId', {
                        'userId': {'$in': user_ids},
                        'createdAt': {
                            '$gte': retention_month,
                            '$lt': retention_month_end
                        }
                    })
                    
                    retention_rate = len(active_users) / cohort_size * 100 if cohort_size > 0 else 0
                    
                    retention_data.append({
                        'month_offset': month_offset + 1,
                        'active_users': len(active_users),
                        'retention_rate': retention_rate
                    })
                
                cohort_data[cohort_month.strftime('%Y-%m')] = {
                    'cohort_size': cohort_size,
                    'retention_data': retention_data
                }
            
            return {
                'cohorts': cohort_data,
                'analysis_months': months_back
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user cohorts: {e}")
            return {}

__all__ = ['CohortAnalyzer']