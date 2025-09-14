"""🎯 Goal Tracking Model - Creator Goal Management
================================================
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import uuid

class GoalStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class Milestone:
    id: str
    description: str
    target_value: int
    current_value: int = 0
    completed: bool = False

@dataclass
class Goal:
    id: str
    creator_id: str
    title: str
    description: str
    target_date: datetime
    status: GoalStatus = GoalStatus.ACTIVE
    milestones: List[Milestone] = None

class GoalTrackingModel:
    @staticmethod
    def create_goal(creator_id: str, goal_data: Dict[str, Any]) -> Goal:
        """Create a new goal"""
        return Goal(
            id=str(uuid.uuid4()),
            creator_id=creator_id,
            title=goal_data["title"],
            description=goal_data["description"],
            target_date=datetime.fromisoformat(goal_data["target_date"]),
            milestones=[]
        )

__all__ = ['GoalTrackingModel', 'Goal', 'Milestone', 'GoalStatus']
