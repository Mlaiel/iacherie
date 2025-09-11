"""
📋 Achievement Service - Achievement System & Badge Management
============================================================

**Module**: Achievement Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: Backend Senior + Gamification Expert + Microservices Architect

Advanced achievement system with AI-powered badge management, progress tracking,
and intelligent milestone recognition for creator engagement.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AchievementService")

class AchievementType(str, Enum):
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    REVENUE = "revenue"
    GROWTH = "growth"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"

class BadgeRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class AchievementStatus(str, Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"

class ProgressType(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    THRESHOLD = "threshold"
    STREAK = "streak"
    CUMULATIVE = "cumulative"

@dataclass
class AchievementMetrics:
    """Achievement system metrics"""
    total_achievements: int
    active_achievers: int
    completion_rate: float
    badge_distribution: Dict[str, int]
    average_progress: float
    engagement_boost: float
    retention_impact: float

class AchievementModel(BaseModel):
    """Achievement definition model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    achievement_type: AchievementType = AchievementType.MILESTONE
    badge_rarity: BadgeRarity = BadgeRarity.COMMON
    icon_url: Optional[str] = None
    criteria: Dict[str, Any] = Field(default_factory=dict)
    reward_points: int = 100
    reward_items: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_repeatable: bool = False
    expiration_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserAchievementModel(BaseModel):
    """User achievement progress model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    achievement_id: str
    status: AchievementStatus = AchievementStatus.LOCKED
    progress: float = 0.0
    current_value: float = 0.0
    target_value: float = 0.0
    progress_type: ProgressType = ProgressType.COUNT
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    streak_count: int = 0
    last_update: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BadgeModel(BaseModel):
    """Badge model for visual representation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    image_url: str
    rarity: BadgeRarity = BadgeRarity.COMMON
    category: str
    earned_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AchievementService:
    """Advanced achievement system with AI-powered badge management"""
    
    def __init__(self):
        self.achievements: Dict[str, AchievementModel] = {}
        self.user_achievements: Dict[str, List[UserAchievementModel]] = {}
        self.badges: Dict[str, BadgeModel] = {}
        self.achievement_progress: Dict[str, UserAchievementModel] = {}
        self.metrics = AchievementMetrics(
            total_achievements=0,
            active_achievers=0,
            completion_rate=0.0,
            badge_distribution={},
            average_progress=0.0,
            engagement_boost=0.0,
            retention_impact=0.0
        )
        self.init_default_achievements()
        logger.info("Achievement Service initialized successfully")

    def init_default_achievements(self):
        """Initialize default achievements and badges"""
        # Content Creation Achievements
        first_post = AchievementModel(
            id="achievement_first_post",
            name="First Steps",
            description="Create your first piece of content",
            achievement_type=AchievementType.CONTENT_CREATION,
            badge_rarity=BadgeRarity.COMMON,
            criteria={"content_count": 1},
            reward_points=50
        )
        
        prolific_creator = AchievementModel(
            id="achievement_prolific_creator",
            name="Prolific Creator",
            description="Create 100 pieces of content",
            achievement_type=AchievementType.CONTENT_CREATION,
            badge_rarity=BadgeRarity.RARE,
            criteria={"content_count": 100},
            reward_points=500
        )
        
        # Engagement Achievements
        viral_sensation = AchievementModel(
            id="achievement_viral_sensation",
            name="Viral Sensation",
            description="Achieve 1 million views on a single piece of content",
            achievement_type=AchievementType.ENGAGEMENT,
            badge_rarity=BadgeRarity.EPIC,
            criteria={"single_content_views": 1000000},
            reward_points=2000
        )
        
        # Collaboration Achievements
        team_player = AchievementModel(
            id="achievement_team_player",
            name="Team Player",
            description="Complete 10 successful collaborations",
            achievement_type=AchievementType.COLLABORATION,
            badge_rarity=BadgeRarity.RARE,
            criteria={"collaborations_completed": 10},
            reward_points=750
        )
        
        # Revenue Achievements
        first_dollar = AchievementModel(
            id="achievement_first_dollar",
            name="First Dollar",
            description="Earn your first dollar from content",
            achievement_type=AchievementType.REVENUE,
            badge_rarity=BadgeRarity.COMMON,
            criteria={"total_earnings": 1.0},
            reward_points=100
        )
        
        entrepreneur = AchievementModel(
            id="achievement_entrepreneur",
            name="Entrepreneur",
            description="Earn $10,000 from content creation",
            achievement_type=AchievementType.REVENUE,
            badge_rarity=BadgeRarity.LEGENDARY,
            criteria={"total_earnings": 10000.0},
            reward_points=5000
        )
        
        # Consistency Achievements
        consistency_king = AchievementModel(
            id="achievement_consistency_king",
            name="Consistency King",
            description="Post content for 30 consecutive days",
            achievement_type=AchievementType.CONSISTENCY,
            badge_rarity=BadgeRarity.RARE,
            criteria={"consecutive_days": 30},
            reward_points=1000
        )
        
        self.achievements = {
            first_post.id: first_post,
            prolific_creator.id: prolific_creator,
            viral_sensation.id: viral_sensation,
            team_player.id: team_player,
            first_dollar.id: first_dollar,
            entrepreneur.id: entrepreneur,
            consistency_king.id: consistency_king
        }
        
        self.metrics.total_achievements = len(self.achievements)

    async def create_achievement(self, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new achievement"""
        try:
            achievement = AchievementModel(**achievement_data)
            self.achievements[achievement.id] = achievement
            self.metrics.total_achievements += 1
            
            logger.info(f"Created achievement: {achievement.id}")
            return {
                "success": True,
                "achievement_id": achievement.id,
                "message": "Achievement created successfully",
                "achievement": achievement.dict()
            }
        except Exception as e:
            logger.error(f"Error creating achievement: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create achievement: {str(e)}")

    async def update_user_progress(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progress for all applicable achievements"""
        try:
            updated_achievements = []
            newly_completed = []
            
            # Initialize user achievements if not exists
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []
                # Create progress tracking for all achievements
                for achievement_id, achievement in self.achievements.items():
                    if self._check_prerequisites(user_id, achievement):
                        user_achievement = UserAchievementModel(
                            user_id=user_id,
                            achievement_id=achievement_id,
                            status=AchievementStatus.IN_PROGRESS,
                            target_value=self._get_target_value(achievement),
                            progress_type=self._get_progress_type(achievement)
                        )
                        self.user_achievements[user_id].append(user_achievement)
                        self.achievement_progress[f"{user_id}_{achievement_id}"] = user_achievement
            
            # Update progress for each achievement
            for user_achievement in self.user_achievements[user_id]:
                if user_achievement.status in [AchievementStatus.COMPLETED, AchievementStatus.CLAIMED]:
                    continue
                
                achievement = self.achievements[user_achievement.achievement_id]
                if not achievement.is_active:
                    continue
                
                # Calculate new progress
                old_progress = user_achievement.progress
                new_value = self._calculate_progress(achievement, activity_data, user_achievement)
                
                if new_value > user_achievement.current_value:
                    user_achievement.current_value = new_value
                    user_achievement.progress = min(100.0, (new_value / user_achievement.target_value) * 100)
                    user_achievement.last_update = datetime.utcnow()
                    
                    if user_achievement.status == AchievementStatus.LOCKED:
                        user_achievement.status = AchievementStatus.IN_PROGRESS
                        user_achievement.started_at = datetime.utcnow()
                    
                    # Check if achievement is completed
                    if user_achievement.progress >= 100.0 and user_achievement.status != AchievementStatus.COMPLETED:
                        user_achievement.status = AchievementStatus.COMPLETED
                        user_achievement.completed_at = datetime.utcnow()
                        newly_completed.append(achievement)
                        
                        # Trigger completion rewards
                        await self._grant_achievement_rewards(user_id, achievement)
                    
                    updated_achievements.append({
                        "achievement_id": achievement.id,
                        "achievement_name": achievement.name,
                        "old_progress": old_progress,
                        "new_progress": user_achievement.progress,
                        "status": user_achievement.status
                    })
            
            logger.info(f"Updated progress for user {user_id}: {len(updated_achievements)} achievements")
            return {
                "success": True,
                "user_id": user_id,
                "updated_achievements": updated_achievements,
                "newly_completed": [a.dict() for a in newly_completed],
                "message": f"Progress updated for {len(updated_achievements)} achievements"
            }
        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to update progress: {str(e)}")

    def _check_prerequisites(self, user_id: str, achievement: AchievementModel) -> bool:
        """Check if user meets achievement prerequisites"""
        if not achievement.prerequisites:
            return True
        
        user_achievements = self.user_achievements.get(user_id, [])
        completed_achievements = [
            ua.achievement_id for ua in user_achievements 
            if ua.status == AchievementStatus.COMPLETED
        ]
        
        return all(prereq in completed_achievements for prereq in achievement.prerequisites)

    def _get_target_value(self, achievement: AchievementModel) -> float:
        """Get target value for achievement completion"""
        criteria = achievement.criteria
        if "content_count" in criteria:
            return float(criteria["content_count"])
        elif "total_earnings" in criteria:
            return float(criteria["total_earnings"])
        elif "single_content_views" in criteria:
            return float(criteria["single_content_views"])
        elif "collaborations_completed" in criteria:
            return float(criteria["collaborations_completed"])
        elif "consecutive_days" in criteria:
            return float(criteria["consecutive_days"])
        return 1.0

    def _get_progress_type(self, achievement: AchievementModel) -> ProgressType:
        """Determine progress type based on achievement criteria"""
        criteria = achievement.criteria
        if "consecutive_days" in criteria:
            return ProgressType.STREAK
        elif "content_count" in criteria or "collaborations_completed" in criteria:
            return ProgressType.CUMULATIVE
        elif "single_content_views" in criteria:
            return ProgressType.THRESHOLD
        return ProgressType.COUNT

    def _calculate_progress(self, achievement: AchievementModel, activity_data: Dict[str, Any], 
                          user_achievement: UserAchievementModel) -> float:
        """Calculate new progress value based on activity"""
        criteria = achievement.criteria
        current_value = user_achievement.current_value
        
        # Content creation progress
        if "content_count" in criteria and "content_created" in activity_data:
            return current_value + activity_data["content_created"]
        
        # Revenue progress
        elif "total_earnings" in criteria and "earnings" in activity_data:
            return current_value + activity_data["earnings"]
        
        # Views progress
        elif "single_content_views" in criteria and "content_views" in activity_data:
            return max(current_value, activity_data["content_views"])
        
        # Collaboration progress
        elif "collaborations_completed" in criteria and "collaborations" in activity_data:
            return current_value + activity_data["collaborations"]
        
        # Streak progress
        elif "consecutive_days" in criteria and "daily_activity" in activity_data:
            if activity_data["daily_activity"]:
                return current_value + 1
            else:
                return 0  # Reset streak
        
        return current_value

    async def _grant_achievement_rewards(self, user_id: str, achievement: AchievementModel):
        """Grant rewards for completed achievement"""
        try:
            # Award points
            await self._award_points(user_id, achievement.reward_points)
            
            # Grant reward items
            for item in achievement.reward_items:
                await self._grant_item(user_id, item)
            
            # Send notification
            await self._send_achievement_notification(user_id, achievement)
            
            logger.info(f"Granted rewards for achievement {achievement.id} to user {user_id}")
        except Exception as e:
            logger.error(f"Error granting achievement rewards: {str(e)}")

    async def _award_points(self, user_id: str, points: int):
        """Award points to user"""
        # In real implementation, this would update user's point balance
        logger.info(f"Awarded {points} points to user {user_id}")

    async def _grant_item(self, user_id: str, item: str):
        """Grant item to user"""
        # In real implementation, this would add item to user's inventory
        logger.info(f"Granted item '{item}' to user {user_id}")

    async def _send_achievement_notification(self, user_id: str, achievement: AchievementModel):
        """Send achievement completion notification"""
        logger.info(f"Sending achievement notification to user {user_id} for '{achievement.name}'")

    async def claim_achievement(self, user_id: str, achievement_id: str) -> Dict[str, Any]:
        """Claim a completed achievement"""
        try:
            user_achievement = next(
                (ua for ua in self.user_achievements.get(user_id, []) 
                 if ua.achievement_id == achievement_id),
                None
            )
            
            if not user_achievement:
                raise HTTPException(status_code=404, detail="User achievement not found")
            
            if user_achievement.status != AchievementStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="Achievement not completed yet")
            
            if user_achievement.status == AchievementStatus.CLAIMED:
                raise HTTPException(status_code=400, detail="Achievement already claimed")
            
            user_achievement.status = AchievementStatus.CLAIMED
            user_achievement.claimed_at = datetime.utcnow()
            
            achievement = self.achievements[achievement_id]
            
            logger.info(f"User {user_id} claimed achievement {achievement_id}")
            return {
                "success": True,
                "achievement": achievement.dict(),
                "rewards": {
                    "points": achievement.reward_points,
                    "items": achievement.reward_items
                },
                "message": "Achievement claimed successfully"
            }
        except Exception as e:
            logger.error(f"Error claiming achievement: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to claim achievement: {str(e)}")

    async def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get all achievements for a user"""
        try:
            user_achievements = self.user_achievements.get(user_id, [])
            
            achievements_data = []
            for user_achievement in user_achievements:
                achievement = self.achievements[user_achievement.achievement_id]
                achievements_data.append({
                    "achievement": achievement.dict(),
                    "progress": user_achievement.dict()
                })
            
            # Calculate statistics
            completed_count = sum(1 for ua in user_achievements if ua.status == AchievementStatus.COMPLETED)
            claimed_count = sum(1 for ua in user_achievements if ua.status == AchievementStatus.CLAIMED)
            total_points = sum(
                self.achievements[ua.achievement_id].reward_points 
                for ua in user_achievements 
                if ua.status == AchievementStatus.CLAIMED
            )
            
            return {
                "user_id": user_id,
                "achievements": achievements_data,
                "statistics": {
                    "total_achievements": len(user_achievements),
                    "completed": completed_count,
                    "claimed": claimed_count,
                    "in_progress": len([ua for ua in user_achievements if ua.status == AchievementStatus.IN_PROGRESS]),
                    "total_points_earned": total_points
                }
            }
        except Exception as e:
            logger.error(f"Error getting user achievements: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get user achievements: {str(e)}")

    async def get_achievement_leaderboard(self, achievement_type: Optional[AchievementType] = None,
                                        limit: int = 50) -> Dict[str, Any]:
        """Get leaderboard for achievements"""
        try:
            # Calculate user scores
            user_scores = {}
            for user_id, user_achievements in self.user_achievements.items():
                score = 0
                completed_count = 0
                
                for user_achievement in user_achievements:
                    if user_achievement.status == AchievementStatus.CLAIMED:
                        achievement = self.achievements[user_achievement.achievement_id]
                        if not achievement_type or achievement.achievement_type == achievement_type:
                            score += achievement.reward_points
                            completed_count += 1
                
                if score > 0:
                    user_scores[user_id] = {
                        "user_id": user_id,
                        "total_points": score,
                        "achievements_completed": completed_count
                    }
            
            # Sort by total points
            leaderboard = sorted(user_scores.values(), key=lambda x: x["total_points"], reverse=True)
            leaderboard = leaderboard[:limit]
            
            # Add rankings
            for i, entry in enumerate(leaderboard):
                entry["rank"] = i + 1
            
            return {
                "achievement_type": achievement_type,
                "leaderboard": leaderboard,
                "total_participants": len(user_scores)
            }
        except Exception as e:
            logger.error(f"Error getting achievement leaderboard: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to get leaderboard: {str(e)}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get achievement system metrics"""
        # Update metrics
        total_users = len(self.user_achievements)
        if total_users > 0:
            completed_achievements = sum(
                sum(1 for ua in user_achievements if ua.status == AchievementStatus.COMPLETED)
                for user_achievements in self.user_achievements.values()
            )
            total_possible = total_users * len(self.achievements)
            self.metrics.completion_rate = (completed_achievements / total_possible) * 100 if total_possible > 0 else 0
            self.metrics.active_achievers = total_users
        
        return {
            "total_achievements": self.metrics.total_achievements,
            "active_achievers": self.metrics.active_achievers,
            "completion_rate": self.metrics.completion_rate,
            "average_progress": self.metrics.average_progress,
            "engagement_boost": self.metrics.engagement_boost
        }

# FastAPI application setup
app = FastAPI(title="Achievement Service")
service = AchievementService()

@app.post("/achievements/")
async def create_achievement(achievement_data: Dict[str, Any]):
    """Create a new achievement"""
    return await service.create_achievement(achievement_data)

@app.post("/users/{user_id}/progress")
async def update_user_progress(user_id: str, activity_data: Dict[str, Any]):
    """Update user progress"""
    return await service.update_user_progress(user_id, activity_data)

@app.post("/users/{user_id}/achievements/{achievement_id}/claim")
async def claim_achievement(user_id: str, achievement_id: str):
    """Claim a completed achievement"""
    return await service.claim_achievement(user_id, achievement_id)

@app.get("/users/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """Get user achievements"""
    return await service.get_user_achievements(user_id)

@app.get("/leaderboard")
async def get_achievement_leaderboard(achievement_type: Optional[AchievementType] = None, limit: int = 50):
    """Get achievement leaderboard"""
    return await service.get_achievement_leaderboard(achievement_type, limit)

@app.get("/metrics")
async def get_metrics():
    """Get achievement metrics"""
    return await service.get_metrics()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AchievementService"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)