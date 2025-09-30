"""MongoDB Behavior Analyzer
==========================

User behavior analysis and pattern detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class BehaviorAnalyzer:
    """User behavior analyzer for pattern detection and optimization."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize behavior analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def analyze_user_behavior_patterns(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze behavior patterns for specific user."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Content upload patterns
            content_activity = list(self.database.content.aggregate([
                {
                    '$match': {
                        'userId': user_id,
                        'createdAt': {'$gte': start_date, '$lte': end_date}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'hour': {'$hour': '$createdAt'},
                            'dayOfWeek': {'$dayOfWeek': '$createdAt'}
                        },
                        'count': {'$sum': 1}
                    }
                }
            ]))
            
            # Interaction patterns
            interaction_activity = list(self.database.interactions.aggregate([
                {
                    '$match': {
                        'userId': user_id,
                        'timestamp': {'$gte': start_date, '$lte': end_date}
                    }
                },
                {
                    '$group': {
                        '_id': '$type',
                        'count': {'$sum': 1}
                    }
                }
            ]))
            
            # Session duration analysis
            session_data = self._analyze_session_patterns(user_id, start_date, end_date)
            
            return {
                'user_id': user_id,
                'analysis_period_days': days_back,
                'content_upload_patterns': content_activity,
                'interaction_patterns': interaction_activity,
                'session_analysis': session_data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user behavior patterns: {e}")
            return {}
    
    def _analyze_session_patterns(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze user session patterns."""
        try:
            # This is a simplified analysis - in production you'd have session tracking
            activities = list(self.database.analytics_events.find({
                'userId': user_id,
                'timestamp': {'$gte': start_date, '$lte': end_date}
            }).sort('timestamp', 1))
            
            if not activities:
                return {'sessions': 0, 'avg_session_duration': 0}
            
            # Group activities into sessions (gap > 30 minutes = new session)
            sessions = []
            current_session = [activities[0]]
            
            for activity in activities[1:]:
                time_gap = (activity['timestamp'] - current_session[-1]['timestamp']).total_seconds()
                
                if time_gap > 1800:  # 30 minutes
                    sessions.append(current_session)
                    current_session = [activity]
                else:
                    current_session.append(activity)
            
            if current_session:
                sessions.append(current_session)
            
            # Calculate session metrics
            session_durations = []
            for session in sessions:
                if len(session) > 1:
                    duration = (session[-1]['timestamp'] - session[0]['timestamp']).total_seconds()
                    session_durations.append(duration)
            
            avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            
            return {
                'sessions': len(sessions),
                'avg_session_duration': avg_duration,
                'total_activities': len(activities)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze session patterns: {e}")
            return {}

__all__ = ['BehaviorAnalyzer']