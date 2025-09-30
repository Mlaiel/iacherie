"""🎭 Creator Models Index - Entry Point for Creator Models
========================================================
Module: models/creator_models/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Creator Models Entry Point - Production-Ready

This file serves as the main entry point for all creator models,
providing convenient access to all creator-related functionality.
"""

from typing import Dict, List, Any, Optional, Type

# Import all creator models and their components
from .user_model import (
    UserModel, UserProfile, UserPreferences, SocialLinks,
    UserStatus, SubscriptionTier, PrivacyLevel
)

from .musician_model import (
    MusicianModel, MusicianProfile, Track, Album, AudioContent,
    MusicGenre, AudioQuality, CollaborationRole
)

from .blogger_model import (
    BloggerModel, BloggerProfile, BlogPost, Category, BlogCategory
)

from .photographer_model import (
    PhotographerModel, PhotographerProfile, PhotoGallery, PhotographyStyle
)

from .influencer_model import (
    InfluencerModel, InfluencerProfile, Campaign, Platform
)

from .comedian_model import (
    ComedianModel, ComedianProfile, SketchSeries, ComedyStyle
)

from .podcaster_model import (
    PodcasterModel, PodcasterProfile, PodcastChannel, PodcastCategory
)

from .personality_model import (
    PersonalityModel, PersonalityTrait, BehaviorPattern
)

from .collaboration_model import (
    CollaborationModel, CollaborationRequest, Partnership, CollaborationStatus
)

from .gamification_model import (
    GamificationModel, Achievement, Badge, Level, BadgeType
)

from .creator_analytics_model import (
    CreatorAnalyticsModel, PerformanceMetrics
)

from .achievement_model import (
    AchievementModel, AchievementType, Progress
)

from .reputation_model import (
    ReputationModel, ReputationScore, Review
)

from .goal_tracking_model import (
    GoalTrackingModel, Goal, Milestone, GoalStatus
)

# Import the main module components
from . import (
    CreatorType, CreatorStatus, CREATOR_MODELS_REGISTRY,
    CreatorModelsManager, creator_models_manager,
    register_and_profile_creator, collaboration_and_gamification_workflow,
    determine_creator_type
)

# Creator Models Factory
class CreatorModelsFactory:
    """Factory for creating creator models"""
    
    @staticmethod
    def create_creator_model(creator_type: str, user_data: Dict[str, Any]) -> Any:
        """Create appropriate creator model based on type"""
        creator_type_enum = CreatorType(creator_type.lower())
        return creator_models_manager.create_creator_profile(creator_type_enum, user_data)
    
    @staticmethod
    def get_available_creator_types() -> List[str]:
        """Get list of available creator types"""
        return [creator_type.value for creator_type in CreatorType]
    
    @staticmethod
    def get_model_class(creator_type: str) -> Optional[Type]:
        """Get model class for creator type"""
        model_map = {
            "musician": MusicianModel,
            "blogger": BloggerModel,
            "photographer": PhotographerModel,
            "influencer": InfluencerModel,
            "comedian": ComedianModel,
            "podcaster": PodcasterModel
        }
        return model_map.get(creator_type.lower())

# Workflow Integration Functions
async def execute_creator_workflow(creator_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute complete creator workflow"""
    workflow_results = {}
    
    # Phase 1: Registration & Profiling
    if workflow_data.get("phase") == 1 or workflow_data.get("all_phases"):
        registration_result = await register_and_profile_creator(workflow_data.get("user_data", {}))
        workflow_results["phase_1"] = registration_result
    
    # Phase 5: Collaboration & Gamification
    if workflow_data.get("phase") == 5 or workflow_data.get("all_phases"):
        collaboration_result = await collaboration_and_gamification_workflow(
            creator_id, workflow_data.get("activity_data", {})
        )
        workflow_results["phase_5"] = collaboration_result
    
    return {
        "creator_id": creator_id,
        "workflow_results": workflow_results,
        "status": "completed" if workflow_results else "no_phases_executed"
    }

def get_creator_models_info() -> Dict[str, Any]:
    """Get information about creator models module"""
    return {
        "module": "Creator Models",
        "version": "1.0.0",
        "author": "Fahed Mlaiel (mlaiel@live.de)",
        "total_models": len(CREATOR_MODELS_REGISTRY),
        "creator_types": [t.value for t in CreatorType],
        "workflow_phases": [1, 5],  # Phases handled by this module
        "business_logic": [
            "User Registration & Profiling",
            "Collaboration & Gamification"
        ],
        "enterprise_ready": True,
        "documentation": "Multilingual support (EN, DE, FR, AR)"
    }

# Export all components
__all__ = [
    # Core Models
    'UserModel', 'UserProfile', 'UserPreferences', 'SocialLinks',
    'MusicianModel', 'MusicianProfile', 'Track', 'Album', 'AudioContent',
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
    
    # Enums
    'CreatorType', 'CreatorStatus', 'UserStatus', 'SubscriptionTier', 'PrivacyLevel',
    'MusicGenre', 'AudioQuality', 'CollaborationRole', 'BlogCategory',
    'PhotographyStyle', 'Platform', 'ComedyStyle', 'PodcastCategory',
    'PersonalityTrait', 'BadgeType', 'AchievementType', 'GoalStatus',
    
    # Factory and Utilities
    'CreatorModelsFactory', 'CreatorModelsManager', 'creator_models_manager',
    'CREATOR_MODELS_REGISTRY',
    
    # Workflow Functions
    'register_and_profile_creator', 'collaboration_and_gamification_workflow',
    'execute_creator_workflow', 'determine_creator_type',
    
    # Information Functions
    'get_creator_models_info'
]