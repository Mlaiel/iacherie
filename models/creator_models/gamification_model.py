"""🎮 Gamification Model - Creator Engagement System
================================================
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid

class BadgeType(Enum):
    FIRST_UPLOAD = "first_upload"
    CONTENT_CREATOR = "content_creator"
    COLLABORATOR = "collaborator"
    VERIFIED = "verified"

@dataclass
class Badge:
    id: str
    name: str
    description: str
    badge_type: BadgeType
    icon_url: Optional[str] = None

@dataclass
class Achievement:
    id: str
    user_id: str
    badge: Badge
    earned_at: datetime
    points_earned: int = 0

@dataclass
class Level:
    level_number: int
    name: str
    points_required: int
    benefits: List[str] = field(default_factory=list)

class GamificationModel:
    @staticmethod
    def initialize_creator(creator_id: str) -> Dict[str, Any]:
        """Initialize gamification for new creator"""
        return {
            "creator_id": creator_id,
            "level": 1,
            "points": 0,
            "badges": [],
            "achievements": []
        }
    
    @staticmethod
    def update_progress(creator_id: str, action: str) -> Dict[str, Any]:
        """Update gamification progress"""
        points_map = {
            "content_upload": 10,
            "first_upload": 50,
            "collaboration": 25,
            "verification": 100
        }
        
        points = points_map.get(action, 5)
        
        return {
            "creator_id": creator_id,
            "action": action,
            "points_earned": points,
            "new_total": points,  # Mock total
            "level_up": False
        }

__all__ = ['GamificationModel', 'Achievement', 'Badge', 'Level', 'BadgeType']