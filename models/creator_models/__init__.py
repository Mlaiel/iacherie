"""🎭 Creator Models Module - Enterprise Architecture
=================================================
Module: models/creator_models/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Multi-Format Creator Models - Production-Ready
Responsibility: Creator management and specialization models

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides enterprise-grade creator models supporting:
- Musicians: Audio content, albums, collaborations, streaming
- Bloggers: Articles, categories, SEO optimization, CMS
- Photographers: Images, galleries, licensing, portfolios
- Influencers: Social campaigns, engagement, cross-platform
- Comedians: Video content, sketches, series, audience
- Podcasters: Episodes, channels, subscribers, distribution

Business Logic Integration:
- Phase 1: User Registration & Profiling
- Phase 5: Collaboration & Gamification
"""

from typing import Dict, List, Any, Optional, Type, Union
import logging
from datetime import datetime
from enum import Enum

# Import all creator models
from .user_model import UserModel, UserProfile, UserPreferences
from .musician_model import MusicianModel, MusicianProfile, AudioContent
from .blogger_model import BloggerModel, BloggerProfile, BlogPost, Category
from .photographer_model import PhotographerModel, PhotographerProfile, PhotoGallery
from .influencer_model import InfluencerModel, InfluencerProfile, Campaign
from .comedian_model import ComedianModel, ComedianProfile, SketchSeries
from .podcaster_model import PodcasterModel, PodcasterProfile, PodcastChannel
from .personality_model import PersonalityModel, PersonalityTrait, BehaviorPattern
from .collaboration_model import CollaborationModel, CollaborationRequest, Partnership
from .gamification_model import GamificationModel, Achievement, Badge, Level
from .creator_analytics_model import CreatorAnalyticsModel, PerformanceMetrics
from .achievement_model import AchievementModel, AchievementType, Progress
from .reputation_model import ReputationModel, ReputationScore, Review
from .goal_tracking_model import GoalTrackingModel, Goal, Milestone

class CreatorType(Enum):
    """Creator type enumeration"""
    MUSICIAN = "musician"
    BLOGGER = "blogger" 
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"

class CreatorStatus(Enum):
    """Creator status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    VERIFIED = "verified"
    PREMIUM = "premium"
    SUSPENDED = "suspended"

class CollaborationStatus(Enum):
    """Collaboration status enumeration"""
    OPEN = "open"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Creator Models Registry
CREATOR_MODELS_REGISTRY: Dict[str, Type] = {
    "user": UserModel,
    "musician": MusicianModel,
    "blogger": BloggerModel,
    "photographer": PhotographerModel,
    "influencer": InfluencerModel,
    "comedian": ComedianModel,
    "podcaster": PodcasterModel,
    "personality": PersonalityModel,
    "collaboration": CollaborationModel,
    "gamification": GamificationModel,
    "analytics": CreatorAnalyticsModel,
    "achievement": AchievementModel,
    "reputation": ReputationModel,
    "goal_tracking": GoalTrackingModel
}

class CreatorModelsManager:
    """Creator Models Manager for Enterprise Architecture"""
    
    def __init__(self):
        self.registry = CREATOR_MODELS_REGISTRY
        self.logger = logging.getLogger(__name__)
        
    def create_creator_profile(self, creator_type: CreatorType, user_data: Dict[str, Any]) -> Any:
        """Create specialized creator profile based on type"""
        try:
            if creator_type == CreatorType.MUSICIAN:
                return MusicianModel.create_profile(user_data)
            elif creator_type == CreatorType.BLOGGER:
                return BloggerModel.create_profile(user_data)
            elif creator_type == CreatorType.PHOTOGRAPHER:
                return PhotographerModel.create_profile(user_data)
            elif creator_type == CreatorType.INFLUENCER:
                return InfluencerModel.create_profile(user_data)
            elif creator_type == CreatorType.COMEDIAN:
                return ComedianModel.create_profile(user_data)
            elif creator_type == CreatorType.PODCASTER:
                return PodcasterModel.create_profile(user_data)
            else:
                return UserModel.create_profile(user_data)
        except Exception as e:
            self.logger.error(f"Failed to create creator profile: {e}")
            return None
    
    def get_specialized_models(self, creator_type: CreatorType) -> List[str]:
        """Get specialized models for creator type"""
        specialization_map = {
            CreatorType.MUSICIAN: ["musician", "analytics", "collaboration", "gamification"],
            CreatorType.BLOGGER: ["blogger", "analytics", "reputation", "goal_tracking"],
            CreatorType.PHOTOGRAPHER: ["photographer", "analytics", "achievement", "collaboration"],
            CreatorType.INFLUENCER: ["influencer", "analytics", "reputation", "collaboration"],
            CreatorType.COMEDIAN: ["comedian", "analytics", "gamification", "achievement"],
            CreatorType.PODCASTER: ["podcaster", "analytics", "collaboration", "goal_tracking"]
        }
        return specialization_map.get(creator_type, ["user", "analytics"])
    
    def find_collaboration_matches(self, creator_id: str, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential collaboration matches"""
        try:
            return CollaborationModel.find_matches(creator_id, criteria)
        except Exception as e:
            self.logger.error(f"Failed to find collaboration matches: {e}")
            return []
    
    def update_gamification_progress(self, creator_id: str, action: str) -> Dict[str, Any]:
        """Update gamification progress for creator"""
        try:
            return GamificationModel.update_progress(creator_id, action)
        except Exception as e:
            self.logger.error(f"Failed to update gamification progress: {e}")
            return {}
    
    def get_creator_analytics(self, creator_id: str, period: str = "month") -> Dict[str, Any]:
        """Get analytics for creator"""
        try:
            return CreatorAnalyticsModel.get_analytics(creator_id, period)
        except Exception as e:
            self.logger.error(f"Failed to get creator analytics: {e}")
            return {}

# Global instance
creator_models_manager = CreatorModelsManager()

# Workflow integration functions
async def register_and_profile_creator(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1: User Registration & Profiling
    Complete creator registration with type determination and profile creation
    """
    workflow_result = {
        "phase": 1,
        "description": "User Registration & Profiling",
        "creator_id": user_data.get("id"),
        "status": "processing"
    }
    
    try:
        # Determine creator type
        creator_type = determine_creator_type(user_data)
        workflow_result["creator_type"] = creator_type.value
        
        # Create base user profile
        user_profile = UserModel.create_profile(user_data)
        workflow_result["user_profile"] = user_profile
        
        # Create specialized creator profile
        creator_profile = creator_models_manager.create_creator_profile(creator_type, user_data)
        workflow_result["creator_profile"] = creator_profile
        
        # Initialize personality model
        personality = PersonalityModel.analyze_personality(user_data)
        workflow_result["personality"] = personality
        
        # Setup gamification
        gamification = GamificationModel.initialize_creator(user_data.get("id"))
        workflow_result["gamification"] = gamification
        
        workflow_result["status"] = "completed"
        workflow_result["models_created"] = ["user", "creator_specialized", "personality", "gamification"]
        
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

async def collaboration_and_gamification_workflow(creator_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 5: Collaboration & Gamification
    Handle collaboration matching and gamification updates
    """
    workflow_result = {
        "phase": 5,
        "description": "Collaboration & Gamification",
        "creator_id": creator_id,
        "status": "processing"
    }
    
    try:
        # Find collaboration opportunities
        collaboration_matches = creator_models_manager.find_collaboration_matches(
            creator_id, activity_data.get("collaboration_criteria", {})
        )
        workflow_result["collaboration_matches"] = collaboration_matches
        
        # Update gamification progress
        gamification_update = creator_models_manager.update_gamification_progress(
            creator_id, activity_data.get("action", "content_upload")
        )
        workflow_result["gamification_update"] = gamification_update
        
        # Check achievements
        achievements = AchievementModel.check_progress(creator_id)
        workflow_result["achievements"] = achievements
        
        # Update reputation
        reputation_update = ReputationModel.update_score(creator_id, activity_data)
        workflow_result["reputation_update"] = reputation_update
        
        workflow_result["status"] = "completed"
        workflow_result["models_used"] = ["collaboration", "gamification", "achievement", "reputation"]
        
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

def determine_creator_type(user_data: Dict[str, Any]) -> CreatorType:
    """Determine creator type based on user data and preferences"""
    content_preferences = user_data.get("content_preferences", [])
    skills = user_data.get("skills", [])
    interests = user_data.get("interests", [])
    
    # Simple heuristic-based type determination
    if any(skill in ["music", "audio", "singing", "instruments"] for skill in skills):
        return CreatorType.MUSICIAN
    elif any(skill in ["writing", "blogging", "content writing"] for skill in skills):
        return CreatorType.BLOGGER
    elif any(skill in ["photography", "photo editing", "visual arts"] for skill in skills):
        return CreatorType.PHOTOGRAPHER
    elif any(skill in ["social media", "marketing", "influence"] for skill in skills):
        return CreatorType.INFLUENCER
    elif any(skill in ["comedy", "entertainment", "video"] for skill in skills):
        return CreatorType.COMEDIAN
    elif any(skill in ["podcasting", "audio content", "interviewing"] for skill in skills):
        return CreatorType.PODCASTER
    else:
        # Default to influencer for broad content creation
        return CreatorType.INFLUENCER

# Export all creator models and components
__all__ = [
    # Enums
    'CreatorType', 'CreatorStatus', 'CollaborationStatus',
    
    # Core Models
    'UserModel', 'UserProfile', 'UserPreferences',
    'MusicianModel', 'MusicianProfile', 'AudioContent',
    'BloggerModel', 'BloggerProfile', 'BlogPost', 'Category',
    'PhotographerModel', 'PhotographerProfile', 'PhotoGallery',
    'InfluencerModel', 'InfluencerProfile', 'Campaign',
    'ComedianModel', 'ComedianProfile', 'SketchSeries',
    'PodcasterModel', 'PodcasterProfile', 'PodcastChannel',
    
    # Supporting Models
    'PersonalityModel', 'PersonalityTrait', 'BehaviorPattern',
    'CollaborationModel', 'CollaborationRequest', 'Partnership',
    'GamificationModel', 'Achievement', 'Badge', 'Level',
    'CreatorAnalyticsModel', 'PerformanceMetrics',
    'AchievementModel', 'AchievementType', 'Progress',
    'ReputationModel', 'ReputationScore', 'Review',
    'GoalTrackingModel', 'Goal', 'Milestone',
    
    # Manager and Registry
    'CreatorModelsManager', 'creator_models_manager',
    'CREATOR_MODELS_REGISTRY',
    
    # Workflow Functions
    'register_and_profile_creator',
    'collaboration_and_gamification_workflow',
    'determine_creator_type'
]