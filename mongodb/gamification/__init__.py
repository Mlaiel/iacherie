"""MongoDB Gamification Data Module
=================================

Gamification metrics, achievements, and rewards system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pymongo import MongoClient

logger = logging.getLogger(__name__)

@dataclass
class Achievement:
    """Achievement definition."""
    achievement_id: str
    name: str
    description: str
    points: int
    category: str
    requirements: Dict[str, Any]

@dataclass
class UserAchievement:
    """User achievement record."""
    user_id: str
    achievement_id: str
    earned_at: datetime
    points_earned: int

class GamificationManager:
    """Comprehensive gamification system for the Ainflue platform."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize gamification manager."""
        self.client = client
        self.database = client[database_name]
        
        # Collections
        self._achievements_collection = 'achievements'
        self._user_achievements_collection = 'user_achievements'
        self._leaderboards_collection = 'leaderboards'
        self._user_points_collection = 'user_points'
        
        # Initialize default achievements
        self._initialize_default_achievements()
    
    def award_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Award achievement to user."""
        try:
            # Check if already earned
            existing = self.database[self._user_achievements_collection].find_one({
                'user_id': user_id,
                'achievement_id': achievement_id
            })
            
            if existing:
                return False  # Already earned
            
            # Get achievement details
            achievement = self.database[self._achievements_collection].find_one({
                'achievement_id': achievement_id
            })
            
            if not achievement:
                return False
            
            # Award achievement
            user_achievement = {
                'user_id': user_id,
                'achievement_id': achievement_id,
                'earned_at': datetime.utcnow(),
                'points_earned': achievement['points']
            }
            
            self.database[self._user_achievements_collection].insert_one(user_achievement)
            
            # Update user points
            self.database[self._user_points_collection].update_one(
                {'user_id': user_id},
                {
                    '$inc': {'total_points': achievement['points']},
                    '$set': {'updated_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            logger.info(f"Awarded achievement '{achievement_id}' to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to award achievement: {e}")
            return False
    
    def get_user_leaderboard_position(self, user_id: str, category: str = 'overall') -> Dict[str, Any]:
        """Get user's position in leaderboard."""
        try:
            # Get user's total points
            user_points = self.database[self._user_points_collection].find_one({
                'user_id': user_id
            })
            
            if not user_points:
                return {'position': None, 'total_points': 0}
            
            total_points = user_points.get('total_points', 0)
            
            # Count users with higher points
            higher_count = self.database[self._user_points_collection].count_documents({
                'total_points': {'$gt': total_points}
            })
            
            position = higher_count + 1
            
            return {
                'position': position,
                'total_points': total_points,
                'category': category
            }
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard position: {e}")
            return {'position': None, 'total_points': 0}
    
    def get_top_leaderboard(self, limit: int = 10, category: str = 'overall') -> List[Dict[str, Any]]:
        """Get top users in leaderboard."""
        try:
            pipeline = [
                {'$sort': {'total_points': -1}},
                {'$limit': limit},
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'user_id',
                        'foreignField': '_id',
                        'as': 'user_info'
                    }
                },
                {
                    '$project': {
                        'user_id': 1,
                        'total_points': 1,
                        'username': {'$arrayElemAt': ['$user_info.username', 0]}
                    }
                }
            ]
            
            leaderboard = list(self.database[self._user_points_collection].aggregate(pipeline))
            
            # Add position numbers
            for i, entry in enumerate(leaderboard):
                entry['position'] = i + 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    def _initialize_default_achievements(self) -> None:
        """Initialize default achievements for creator platform."""
        default_achievements = [
            {
                'achievement_id': 'first_upload',
                'name': 'First Creator',
                'description': 'Upload your first content',
                'points': 100,
                'category': 'content',
                'requirements': {'content_uploads': 1}
            },
            {
                'achievement_id': 'prolific_creator',
                'name': 'Prolific Creator',
                'description': 'Upload 100 pieces of content',
                'points': 1000,
                'category': 'content',
                'requirements': {'content_uploads': 100}
            },
            {
                'achievement_id': 'first_collaboration',
                'name': 'Team Player',
                'description': 'Complete your first collaboration',
                'points': 200,
                'category': 'collaboration',
                'requirements': {'collaborations_completed': 1}
            },
            {
                'achievement_id': 'revenue_milestone',
                'name': 'Monetization Master',
                'description': 'Earn your first revenue',
                'points': 500,
                'category': 'revenue',
                'requirements': {'total_revenue': 1}
            }
        ]
        
        for achievement in default_achievements:
            self.database[self._achievements_collection].update_one(
                {'achievement_id': achievement['achievement_id']},
                {'$set': achievement},
                upsert=True
            )

__all__ = ['GamificationManager', 'Achievement', 'UserAchievement']