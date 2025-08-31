"""User Profiler
=============

Industrial-grade user profiling engine for IA Influencer Agent.
Creates comprehensive user profiles, tracks user preferences, analyzes behavioral patterns,
and maintains dynamic user personas for advanced personalization.

Business Logic:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → AI rights protection → Professional SEO → Collaboration matching → Multi-platform distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

WARNING: Any attempt to steal, copy, or use the concept, idea, or code without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import json
from uuid import uuid4

from ..core.base_service import BaseService
from ..core.exceptions import UserProfilingError, ValidationError
from ..database.mongodb import MongoDBHandler
from ..cache.redis_cache import RedisCache
from ..ml.feature_engineering import FeatureEngineer
from ..ml.clustering_models import UserClusteringModel
from ..analytics.demographic_analyzer import DemographicAnalyzer

logger = logging.getLogger(__name__)


class ProfileDimension(str, Enum):
    """User profile dimensions"""    CREATIVE_STYLE = "creative_style"
    CONTENT_PREFERENCES = "content_preferences"
    ENGAGEMENT_PATTERNS = "engagement_patterns"
    COLLABORATION_STYLE = "collaboration_style"
    SKILL_LEVEL = "skill_level"
    CAREER_STAGE = "career_stage"
    PLATFORM_BEHAVIOR = "platform_behavior"
    LEARNING_STYLE = "learning_style"


class UserPersona(str, Enum):
    """User persona types"""    CREATIVE_EXPLORER = "creative_explorer"
    BUSINESS_FOCUSED_CREATOR = "business_focused_creator"
    COMMUNITY_BUILDER = "community_builder"
    TECHNICAL_INNOVATOR = "technical_innovator"
    TRENDY_INFLUENCER = "trendy_influencer"
    EDUCATIONAL_CONTENT_CREATOR = "educational_content_creator"
    COLLABORATIVE_ARTIST = "collaborative_artist"
    INDEPENDENT_PRODUCER = "independent_producer"


class PreferenceCategory(str, Enum):
    """Categories of user preferences"""    CONTENT_TYPE = "content_type"
    GENRE_MUSIC = "genre_music"
    VISUAL_STYLE = "visual_style"
    INTERACTION_TYPE = "interaction_type"
    PLATFORM_PREFERENCE = "platform_preference"
    COLLABORATION_TYPE = "collaboration_type"
    LEARNING_FORMAT = "learning_format"
    MONETIZATION_STRATEGY = "monetization_strategy"


@dataclass
class UserPreference:
    """Individual user preference"""    category: PreferenceCategory
    preference_key: str
    preference_value: str
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    last_updated: datetime
    source: str  # explicit, implicit, inferred
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """Comprehensive user profile"""    user_id: str
    persona: UserPersona
    profile_dimensions: Dict[ProfileDimension, Dict[str, Any]]
    preferences: List[UserPreference]
    demographic_info: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    skill_assessments: Dict[str, float]
    career_stage_info: Dict[str, Any]
    interaction_history_summary: Dict[str, Any]
    collaboration_history: List[Dict[str, Any]]
    content_creation_patterns: Dict[str, Any]
    platform_activity: Dict[str, Dict[str, Any]]
    learning_progress: Dict[str, Any]
    monetization_profile: Dict[str, Any]
    profile_confidence: float
    last_updated: datetime
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileUpdateRequest:
    """Request to update user profile"""    user_id: str
    update_type: str  # explicit, implicit, batch
    updates: Dict[str, Any]
    interaction_data: Optional[List[Dict[str, Any]]] = None
    feedback_data: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = field(default_factory=dict)


class UserProfiler(BaseService):
    """    Advanced user profiling engine for personalization
    """    
    def __init__(
        self,
        mongodb_handler: MongoDBHandler,
        redis_cache: RedisCache,
        feature_engineer: FeatureEngineer,
        clustering_model: UserClusteringModel,
        demographic_analyzer: DemographicAnalyzer
    ):
        super().__init__()
        self.mongodb = mongodb_handler
        self.redis_cache = redis_cache
        self.feature_engineer = feature_engineer
        self.clustering_model = clustering_model
        self.demographic_analyzer = demographic_analyzer
        
        # Configuration
        self.profile_cache_ttl = 3600  # 1 hour
        self.min_interactions_for_profiling = 5
        self.preference_decay_rate = 0.05  # Daily decay rate
        self.confidence_threshold = 0.6
        self.profile_update_frequency = timedelta(hours=12)
        
        # Internal state
        self._profile_cache = {}
        self._preference_models = {}
        self._persona_classifiers = {}
        
        logger.info("UserProfiler initialized successfully")

    async def initialize(self) -> None:
        """Initialize user profiler"""        try:
            # Initialize ML models
            await self.feature_engineer.initialize()
            await self.clustering_model.initialize()
            await self.demographic_analyzer.initialize()
            
            # Load preference models
            await self._load_preference_models()
            
            # Load persona classifiers
            await self._load_persona_classifiers()
            
            logger.info("UserProfiler initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize UserProfiler: {e}")
            raise UserProfilingError(f"Initialization failed: {e}")

    async def get_user_profile(
        self,
        user_id: str,
        include_details: bool = True
    ) -> Optional[UserProfile]:
        """        Get comprehensive user profile
        
        Args:
            user_id: User identifier
            include_details: Whether to include detailed profile information
            
        Returns:
            Complete user profile or None if not found
        """        try:
            # Check cache
            cache_key = f"user_profile:{user_id}:{include_details}"
            cached_profile = await self.redis_cache.get(cache_key)
            if cached_profile:
                profile_data = json.loads(cached_profile)
                return self._deserialize_user_profile(profile_data)
            
            # Load from database
            profile_data = await self.mongodb.find_one(
                "user_profiles", {"user_id": user_id}
            )
            
            if not profile_data:
                # Create new profile
                profile = await self._create_new_user_profile(user_id)
            else:
                # Deserialize existing profile
                profile = self._deserialize_user_profile(profile_data)
                
                # Check if profile needs updating
                if await self._should_update_profile(profile):
                    profile = await self._update_user_profile(profile)
            
            # Cache profile
            if profile:
                serialized_profile = self._serialize_user_profile(profile)
                await self.redis_cache.setex(
                    cache_key, self.profile_cache_ttl, 
                    json.dumps(serialized_profile, default=str)
                )
            
            logger.info(f"User profile retrieved for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile for {user_id}: {e}")
            return None

    async def update_user_profile(
        self,
        request: ProfileUpdateRequest
    ) -> bool:
        """        Update user profile based on new data
        
        Args:
            request: Profile update request with new data
            
        Returns:
            Success status
        """        try:
            # Validate request
            await self._validate_profile_update_request(request)
            
            # Get current profile
            current_profile = await self.get_user_profile(request.user_id)
            if not current_profile:
                current_profile = await self._create_new_user_profile(request.user_id)
            
            # Process updates based on type
            if request.update_type == "explicit":
                updated_profile = await self._apply_explicit_updates(
                    current_profile, request.updates
                )
            elif request.update_type == "implicit":
                updated_profile = await self._apply_implicit_updates(
                    current_profile, request.interaction_data or []
                )
            elif request.update_type == "batch":
                updated_profile = await self._apply_batch_updates(
                    current_profile, request.updates, request.interaction_data or []
                )
            else:
                raise ValidationError(f"Invalid update type: {request.update_type}")
            
            # Update demographic analysis
            if request.interaction_data:
                demographic_updates = await self.demographic_analyzer.analyze_interactions(
                    request.interaction_data
                )
                updated_profile.demographic_info.update(demographic_updates)
            
            # Re-classify persona if needed
            updated_profile.persona = await self._classify_user_persona(updated_profile)
            
            # Update profile confidence
            updated_profile.profile_confidence = await self._calculate_profile_confidence(
                updated_profile
            )
            
            # Update timestamp
            updated_profile.last_updated = datetime.now()
            
            # Save to database
            serialized_profile = self._serialize_user_profile(updated_profile)
            await self.mongodb.update_one(
                "user_profiles",
                {"user_id": request.user_id},
                {"$set": serialized_profile},
                upsert=True
            )
            
            # Invalidate cache
            await self._invalidate_user_profile_cache(request.user_id)
            
            # Track profile update
            await self._track_profile_update(request, updated_profile)
            
            logger.info(f"User profile updated for user {request.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False

    async def analyze_user_preferences(
        self,
        user_id: str,
        analysis_period: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """        Analyze user preferences from interaction data
        
        Args:
            user_id: User identifier
            analysis_period: Time period for analysis
            
        Returns:
            Comprehensive preference analysis
        """        try:
            # Set default analysis period
            if not analysis_period:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                analysis_period = (start_date, end_date)
            
            # Get interaction data
            interactions = await self._get_user_interactions(user_id, analysis_period)
            
            if len(interactions) < self.min_interactions_for_profiling:
                return {"error": "Insufficient interaction data for analysis"}
            
            # Analyze different preference categories
            preference_analysis = {}
            
            for category in PreferenceCategory:
                category_preferences = await self._analyze_preference_category(
                    interactions, category
                )
                preference_analysis[category.value] = category_preferences
            
            # Calculate preference strengths
            preference_strengths = await self._calculate_preference_strengths(
                interactions, preference_analysis
            )
            
            # Identify preference trends
            preference_trends = await self._identify_preference_trends(
                user_id, interactions, analysis_period
            )
            
            # Generate preference insights
            preference_insights = await self._generate_preference_insights(
                preference_analysis, preference_strengths, preference_trends
            )
            
            analysis_result = {
                "user_id": user_id,
                "analysis_period": {
                    "start": analysis_period[0].isoformat(),
                    "end": analysis_period[1].isoformat()
                },
                "interactions_analyzed": len(interactions),
                "preference_analysis": preference_analysis,
                "preference_strengths": preference_strengths,
                "preference_trends": preference_trends,
                "insights": preference_insights,
                "confidence_score": await self._calculate_preference_confidence(
                    interactions, preference_analysis
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Preference analysis completed for user {user_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze user preferences: {e}")
            return {"error": f"Preference analysis failed: {e}"}

    async def get_user_personas(
        self,
        user_ids: Optional[List[str]] = None,
        include_confidence: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """        Get user personas for multiple users
        
        Args:
            user_ids: List of user IDs (if None, get all)
            include_confidence: Whether to include confidence scores
            
        Returns:
            Dictionary mapping user IDs to persona information
        """        try:
            # Get user profiles
            if user_ids:
                profiles = {}
                for user_id in user_ids:
                    profile = await self.get_user_profile(user_id)
                    if profile:
                        profiles[user_id] = profile
            else:
                # Get all profiles (with pagination for large datasets)
                profiles = await self._get_all_user_profiles()
            
            # Extract persona information
            user_personas = {}
            for user_id, profile in profiles.items():
                persona_info = {
                    "persona": profile.persona.value,
                    "persona_description": await self._get_persona_description(profile.persona),
                    "key_characteristics": await self._get_persona_characteristics(profile)
                }
                
                if include_confidence:
                    persona_info["confidence"] = profile.profile_confidence
                    persona_info["last_updated"] = profile.last_updated.isoformat()
                
                user_personas[user_id] = persona_info
            
            logger.info(f"Retrieved personas for {len(user_personas)} users")
            return user_personas
            
        except Exception as e:
            logger.error(f"Failed to get user personas: {e}")
            return {}

    async def cluster_users(
        self,
        clustering_features: Optional[List[str]] = None,
        num_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """        Cluster users based on profile features
        
        Args:
            clustering_features: Features to use for clustering
            num_clusters: Number of clusters (auto-determined if None)
            
        Returns:
            Clustering results with user assignments
        """        try:
            # Get all user profiles
            all_profiles = await self._get_all_user_profiles()
            
            if len(all_profiles) < 10:  # Minimum users for meaningful clustering
                return {"error": "Insufficient users for clustering analysis"}
            
            # Extract features for clustering
            feature_matrix, user_ids = await self._extract_clustering_features(
                all_profiles, clustering_features
            )
            
            # Perform clustering
            clustering_result = await self.clustering_model.cluster_users(
                feature_matrix, num_clusters
            )
            
            # Assign users to clusters
            user_clusters = {}
            for i, user_id in enumerate(user_ids):
                cluster_id = clustering_result["labels"][i]
                user_clusters[user_id] = {
                    "cluster_id": int(cluster_id),
                    "cluster_confidence": float(clustering_result["confidences"][i]) if "confidences" in clustering_result else 1.0
                }
            
            # Analyze cluster characteristics
            cluster_characteristics = await self._analyze_cluster_characteristics(
                all_profiles, user_clusters
            )
            
            clustering_analysis = {
                "num_clusters": clustering_result["num_clusters"],
                "num_users": len(user_ids),
                "clustering_features": clustering_features or ["all"],
                "user_clusters": user_clusters,
                "cluster_characteristics": cluster_characteristics,
                "clustering_quality": clustering_result.get("quality_metrics", {}),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"User clustering completed: {clustering_result['num_clusters']} clusters")
            return clustering_analysis
            
        except Exception as e:
            logger.error(f"Failed to cluster users: {e}")
            return {"error": f"User clustering failed: {e}"}

    # Private helper methods
    
    async def _create_new_user_profile(self, user_id: str) -> UserProfile:
        """Create a new user profile with default values"""        try:
            # Get basic user information
            user_info = await self.mongodb.find_one("users", {"user_id": user_id})
            
            # Initialize profile dimensions
            profile_dimensions = {
                ProfileDimension.CREATIVE_STYLE: {},
                ProfileDimension.CONTENT_PREFERENCES: {},
                ProfileDimension.ENGAGEMENT_PATTERNS: {},
                ProfileDimension.COLLABORATION_STYLE: {},
                ProfileDimension.SKILL_LEVEL: {},
                ProfileDimension.CAREER_STAGE: {},
                ProfileDimension.PLATFORM_BEHAVIOR: {},
                ProfileDimension.LEARNING_STYLE: {}
            }
            
            # Create basic profile
            profile = UserProfile(
                user_id=user_id,
                persona=UserPersona.CREATIVE_EXPLORER,  # Default persona
                profile_dimensions=profile_dimensions,
                preferences=[],
                demographic_info=user_info.get("demographics", {}) if user_info else {},
                behavioral_patterns={},
                skill_assessments={},
                career_stage_info={},
                interaction_history_summary={},
                collaboration_history=[],
                content_creation_patterns={},
                platform_activity={},
                learning_progress={},
                monetization_profile={},
                profile_confidence=0.1,  # Low confidence for new profile
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
            
            # Save to database
            serialized_profile = self._serialize_user_profile(profile)
            await self.mongodb.insert_one("user_profiles", serialized_profile)
            
            logger.info(f"New user profile created for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create new user profile: {e}")
            raise UserProfilingError(f"Failed to create profile: {e}")

    async def _apply_explicit_updates(
        self,
        profile: UserProfile,
        updates: Dict[str, Any]
    ) -> UserProfile:
        """Apply explicit user updates to profile"""        try:
            # Update demographic information
            if "demographics" in updates:
                profile.demographic_info.update(updates["demographics"])
            
            # Update preferences
            if "preferences" in updates:
                for pref_data in updates["preferences"]:
                    preference = UserPreference(
                        category=PreferenceCategory(pref_data["category"]),
                        preference_key=pref_data["key"],
                        preference_value=pref_data["value"],
                        strength=pref_data.get("strength", 1.0),
                        confidence=1.0,  # High confidence for explicit preferences
                        last_updated=datetime.now(),
                        source="explicit"
                    )
                    
                    # Update or add preference
                    await self._update_preference_in_profile(profile, preference)
            
            # Update skill assessments
            if "skills" in updates:
                profile.skill_assessments.update(updates["skills"])
            
            # Update creative goals
            if "creative_goals" in updates:
                profile.career_stage_info["creative_goals"] = updates["creative_goals"]
            
            # Update monetization preferences
            if "monetization" in updates:
                profile.monetization_profile.update(updates["monetization"])
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to apply explicit updates: {e}")
            return profile

    async def _apply_implicit_updates(
        self,
        profile: UserProfile,
        interactions: List[Dict[str, Any]]
    ) -> UserProfile:
        """Apply implicit updates from user interactions"""        try:
            # Analyze interaction patterns
            interaction_patterns = await self._analyze_interaction_patterns(interactions)
            
            # Update behavioral patterns
            profile.behavioral_patterns.update(interaction_patterns)
            
            # Infer preferences from interactions
            inferred_preferences = await self._infer_preferences_from_interactions(interactions)
            
            # Update preferences with lower confidence
            for pref_data in inferred_preferences:
                preference = UserPreference(
                    category=PreferenceCategory(pref_data["category"]),
                    preference_key=pref_data["key"],
                    preference_value=pref_data["value"],
                    strength=pref_data["strength"],
                    confidence=pref_data.get("confidence", 0.7),
                    last_updated=datetime.now(),
                    source="implicit"
                )
                
                await self._update_preference_in_profile(profile, preference)
            
            # Update content creation patterns
            creation_patterns = await self._analyze_content_creation_patterns(interactions)
            profile.content_creation_patterns.update(creation_patterns)
            
            # Update platform activity
            platform_activity = await self._analyze_platform_activity(interactions)
            profile.platform_activity.update(platform_activity)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to apply implicit updates: {e}")
            return profile

    async def _classify_user_persona(self, profile: UserProfile) -> UserPersona:
        """Classify user persona based on profile data"""        try:
            # Extract features for persona classification
            features = await self._extract_persona_features(profile)
            
            # Use persona classifier
            if "persona_classifier" in self._persona_classifiers:
                persona_probabilities = await self._persona_classifiers["persona_classifier"].predict(features)
                predicted_persona = max(persona_probabilities, key=persona_probabilities.get)
                return UserPersona(predicted_persona)
            
            # Fallback: rule-based classification
            return await self._rule_based_persona_classification(profile)
            
        except Exception as e:
            logger.error(f"Failed to classify user persona: {e}")
            return UserPersona.CREATIVE_EXPLORER  # Default persona

    async def _calculate_profile_confidence(self, profile: UserProfile) -> float:
        """Calculate confidence score for user profile"""        try:
            confidence_factors = []
            
            # Number of preferences
            num_preferences = len(profile.preferences)
            preference_confidence = min(num_preferences / 20.0, 1.0)  # Max at 20 preferences
            confidence_factors.append(preference_confidence)
            
            # Interaction history
            interaction_count = profile.interaction_history_summary.get("total_interactions", 0)
            interaction_confidence = min(interaction_count / 100.0, 1.0)  # Max at 100 interactions
            confidence_factors.append(interaction_confidence)
            
            # Time since creation
            days_since_creation = (datetime.now() - profile.created_at).days
            time_confidence = min(days_since_creation / 30.0, 1.0)  # Max at 30 days
            confidence_factors.append(time_confidence)
            
            # Explicit vs implicit data ratio
            explicit_prefs = len([p for p in profile.preferences if p.source == "explicit"])
            explicit_ratio = explicit_prefs / max(len(profile.preferences), 1)
            confidence_factors.append(explicit_ratio)
            
            # Calculate weighted average
            weights = [0.3, 0.3, 0.2, 0.2]
            weighted_confidence = sum(
                factor * weight 
                for factor, weight in zip(confidence_factors, weights)
            )
            
            return min(weighted_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate profile confidence: {e}")
            return 0.5  # Default medium confidence


# Factory functions and utilities

def create_user_profiler(
    mongodb_handler: MongoDBHandler,
    redis_cache: RedisCache,
    feature_engineer: FeatureEngineer,
    clustering_model: UserClusteringModel,
    demographic_analyzer: DemographicAnalyzer
) -> UserProfiler:
    """Create user profiler instance"""    return UserProfiler(
        mongodb_handler=mongodb_handler,
        redis_cache=redis_cache,
        feature_engineer=feature_engineer,
        clustering_model=clustering_model,
        demographic_analyzer=demographic_analyzer
    )


def validate_profile_update_request(request: ProfileUpdateRequest) -> bool:
    """Validate profile update request"""    if not request.user_id or not isinstance(request.user_id, str):
        return False
    
    if request.update_type not in ["explicit", "implicit", "batch"]:
        return False
    
    if not request.updates and not request.interaction_data:
        return False
    
    return True
