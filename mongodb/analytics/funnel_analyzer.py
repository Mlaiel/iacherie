"""MongoDB Funnel Analyzer
========================

Conversion funnel analysis for user journey optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class FunnelAnalyzer:
    """Conversion funnel analyzer for user journey optimization."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize funnel analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def analyze_creator_onboarding_funnel(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze creator onboarding conversion funnel."""
        try:
            # Step 1: User Registration
            total_registrations = self.database.users.count_documents({
                'createdAt': {'$gte': start_date, '$lte': end_date}
            })
            
            # Step 2: Profile Completion
            completed_profiles = self.database.users.count_documents({
                'createdAt': {'$gte': start_date, '$lte': end_date},
                'profileCompleted': True
            })
            
            # Step 3: First Content Upload
            users_with_content = len(self.database.content.distinct('userId', {
                'createdAt': {'$gte': start_date, '$lte': end_date}
            }))
            
            # Step 4: First Collaboration
            users_with_collaboration = len(self.database.collaborations.distinct('userId', {
                'createdAt': {'$gte': start_date, '$lte': end_date}
            }))
            
            # Step 5: First Revenue
            users_with_revenue = len(self.database.revenue_events.distinct('userId', {
                'timestamp': {'$gte': start_date, '$lte': end_date},
                'status': 'completed'
            }))
            
            # Calculate conversion rates
            funnel_steps = [
                {'step': 'Registration', 'count': total_registrations, 'rate': 100.0},
                {'step': 'Profile Completion', 'count': completed_profiles, 
                 'rate': completed_profiles / total_registrations * 100 if total_registrations > 0 else 0},
                {'step': 'First Content Upload', 'count': users_with_content,
                 'rate': users_with_content / total_registrations * 100 if total_registrations > 0 else 0},
                {'step': 'First Collaboration', 'count': users_with_collaboration,
                 'rate': users_with_collaboration / total_registrations * 100 if total_registrations > 0 else 0},
                {'step': 'First Revenue', 'count': users_with_revenue,
                 'rate': users_with_revenue / total_registrations * 100 if total_registrations > 0 else 0}
            ]
            
            return {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'funnel_steps': funnel_steps,
                'overall_conversion_rate': users_with_revenue / total_registrations * 100 if total_registrations > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze creator onboarding funnel: {e}")
            return {}

__all__ = ['FunnelAnalyzer']