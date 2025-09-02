"""User Context Profiler - IA Influencer Agent

Advanced user context profiling for multi-format content creators with
behavioral analysis, preference learning, and personalization optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, Counter

from ...core.exceptions import ProfilerError
from ...core.monitoring import MetricsCollector
from ...utils.cache import CacheManager
from ...utils.nlp import TextProcessor


class CreatorType(Enum):
    """
Content creator types"""

    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    PODCASTER = "podcaster"
    VIDEOGRAPHER = "videographer"
    MULTI_FORMAT = "multi_format"


class ExpertiseLevel(Enum):
    """User expertise levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    PROFESSIONAL = "professional"


class ContentPreference(Enum):
    """Content format preferences"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    PODCAST = "podcast"
    BLOG = "blog"
    SOCIAL_MEDIA = "social_media"


@dataclass
class UserBehaviorPattern:
    """User behavior pattern analysis"""
    pattern_id: str
    pattern_type: str
    frequency: float
    confidence: float
    last_observed: datetime
    trend: str  # "increasing", "stable", "decreasing"
    seasonal_indicators: Dict[str, float] = field(default_factory=dict)
    context_triggers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "last_observed": self.last_observed.isoformat(),
            "trend": self.trend,
            "seasonal_indicators": self.seasonal_indicators,
            "context_triggers": self.context_triggers
        }


@dataclass
class PersonalizationInsights:
    """Personalization insights for user experience optimization"""
    user_id: str
    generated_at: datetime
    
    # Content recommendations
    recommended_content_types: List[ContentPreference]
    optimal_engagement_times: List[int]  # Hours of day
    preferred_interaction_style: str
    
    # Business insights
    collaboration_opportunities: List[str]
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    monetization_potential: float
    protection_priorities: List[str]
    
    # Platform insights
    primary_platforms: List[str]
    cross_platform_strategy: Dict[str, str]
    
    # Growth insights
    skill_development_areas: List[str]
    recommended_features: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "generated_at": self.generated_at.isoformat(),
            "recommended_content_types": [pref.value for pref in self.recommended_content_types],
            "optimal_engagement_times": self.optimal_engagement_times,
            "preferred_interaction_style": self.preferred_interaction_style,
            "collaboration_opportunities": self.collaboration_opportunities,
            "monetization_potential": self.monetization_potential,
            "protection_priorities": self.protection_priorities,
            "primary_platforms": self.primary_platforms,
            "cross_platform_strategy": self.cross_platform_strategy,
            "skill_development_areas": self.skill_development_areas,
            "recommended_features": self.recommended_features
        }


@dataclass
class UserContextProfile:
    """Comprehensive user context profile"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    
    # Basic demographics and creator info
    creator_type: CreatorType
    expertise_level: ExpertiseLevel
    primary_language: str
    location: Optional[Dict[str, str]] = None
    
    # Content preferences
    content_preferences: Dict[ContentPreference, float] = field(default_factory=dict)
    platform_usage: Dict[str, float] = field(default_factory=dict)
    genre_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Behavioral patterns
    behavior_patterns: List[UserBehaviorPattern] = field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Business context
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    monetization_goals: List[str] = field(default_factory=list)
    protection_awareness: float = 0.5
    
    # Learning and adaptation
    learning_velocity: float = 0.5
    adaptation_rate: float = 0.3
    feedback_sensitivity: float = 0.7
    
    # Personalization data
    preferences_confidence: float = 0.5
    profile_completeness: float = 0.0
    last_insights: Optional[PersonalizationInsights] = None
    
    def calculate_completeness(self) -> float:
        """
Calculate profile completeness score"""
        total_fields = 10
        completed_fields = 0
        
        if self.creator_type != CreatorType.MULTI_FORMAT:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
        if self.creator_type != CreatorType.MULTI_FORMAT:
            completed_fields += 1
        if self.expertise_level != ExpertiseLevel.BEGINNER:
            completed_fields += 1
        if self.content_preferences:
            completed_fields += 1
        if self.platform_usage:
            completed_fields += 1
        if self.genre_preferences:
            completed_fields += 1
        if self.behavior_patterns:
            completed_fields += 1
        if len(self.interaction_history) > 10:
            completed_fields += 1
        if self.collaboration_preferences:
            completed_fields += 1
        if self.monetization_goals:
            completed_fields += 1
        if self.location:
            completed_fields += 1
        
        self.profile_completeness = completed_fields / total_fields
        return self.profile_completeness
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "creator_type": self.creator_type.value,
            "expertise_level": self.expertise_level.value,
            "primary_language": self.primary_language,
            "location": self.location,
            "content_preferences": {pref.value: score for pref, score in self.content_preferences.items()},
            "platform_usage": self.platform_usage,
            "genre_preferences": self.genre_preferences,
            "behavior_patterns": [pattern.to_dict() for pattern in self.behavior_patterns],
            "interaction_history_count": len(self.interaction_history),
            "engagement_metrics": self.engagement_metrics,
            "collaboration_preferences": self.collaboration_preferences,
            "monetization_goals": self.monetization_goals,
            "protection_awareness": self.protection_awareness,
            "learning_velocity": self.learning_velocity,
            "adaptation_rate": self.adaptation_rate,
            "feedback_sensitivity": self.feedback_sensitivity,
            "preferences_confidence": self.preferences_confidence,
            "profile_completeness": self.profile_completeness,
            "last_insights": self.last_insights.to_dict() if self.last_insights else None
        }


class UserContextProfiler:
    """
    Advanced user context profiler providing comprehensive behavioral analysis,
    preference learning, and personalization optimization for content creators.
    
    Features:
    - Multi-dimensional user profiling
    - Behavioral pattern recognition
    - Dynamic preference learning
    - Personalization insights generation
    - Creator journey optimization
    - Cross-platform analytics
    """
    
    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        text_processor: TextProcessor,
        min_interactions_for_analysis: int = 20,
        pattern_confidence_threshold: float = 0.6,
        profile_update_interval: int = 3600  # 1 hour
    ):
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.text_processor = text_processor
        self.min_interactions_for_analysis = min_interactions_for_analysis
        self.pattern_confidence_threshold = pattern_confidence_threshold
        self.profile_update_interval = profile_update_interval
        
        # Profile storage
        self.user_profiles: Dict[str, UserContextProfile] = {}
        
        # Pattern analysis models
        self.pattern_analyzers: Dict[str, Any] = {}
        
        # Background processing
        self.update_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("UserContextProfiler initialized")
    
    async def start(self):
        """Start the user context profiler"""
        try:
            # Load existing profiles
            await self._load_profiles()
            
            # Initialize pattern analyzers
            await self._initialize_analyzers()
            
            # Start background updates
            self.update_task = asyncio.create_task(self._background_updates())
            
            self.logger.info("UserContextProfiler started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start UserContextProfiler: {e}")
            raise ProfilerError(f"Startup failed: {e}")
    
    async def stop(self):
        """Stop the user context profiler"""
        try:
            # Cancel background tasks
            if self.update_task:
                self.update_task.cancel()
                try:
                    await self.update_task
                except asyncio.CancelledError:
                    pass
            
            # Save profiles
            await self._save_profiles()
            
            self.logger.info("UserContextProfiler stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping UserContextProfiler: {e}")
    
    async def create_profile(
        self,
        user_id: str,
        creator_type: CreatorType,
        expertise_level: ExpertiseLevel = ExpertiseLevel.BEGINNER,
        primary_language: str = "en",
        initial_preferences: Optional[Dict[str, Any]] = None
    ) -> UserContextProfile:
        """
        Create new user profile
        
        Args:
            user_id: User identifier
            creator_type: Type of content creator
            expertise_level: User expertise level
            primary_language: User's primary language
            initial_preferences: Initial preference data
            
        Returns:
            UserContextProfile: Created profile
        """
        try:
            # Create profile
            profile = UserContextProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                creator_type=creator_type,
                expertise_level=expertise_level,
                primary_language=primary_language
            )
            
            # Set initial preferences if provided
            if initial_preferences:
                await self._apply_initial_preferences(profile, initial_preferences)
            
            # Store profile
            self.user_profiles[user_id] = profile
            
            # Save to cache
            await self._save_profile(user_id)
            
            # Collect metrics
            await self.metrics_collector.increment(
                "profiles.created",
                tags={"creator_type": creator_type.value}
            )
            
            self.logger.info(f"Profile created for user {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating profile for {user_id}: {e}")
            raise ProfilerError(f"Failed to create profile: {e}")
    
    async def get_profile(
        self,
        user_id: str,
        create_if_missing: bool = False,
        creator_type: Optional[CreatorType] = None
    ) -> Optional[UserContextProfile]:
        """
        Get user profile
        
        Args:
            user_id: User identifier
            create_if_missing: Create profile if not found
            creator_type: Creator type for new profile
            
        Returns:
            UserContextProfile or None
        """
        try:
            # Check in-memory storage
            if user_id in self.user_profiles:
                return self.user_profiles[user_id]
            
            # Try to load from cache
            profile = await self._load_profile(user_id)
            if profile:
                self.user_profiles[user_id] = profile
                return profile
            
            # Create if requested
            if create_if_missing and creator_type:
                return await self.create_profile(user_id, creator_type)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting profile for {user_id}: {e}")
            return None
    
    async def update_interaction(
        self,
        user_id: str,
        interaction_data: Dict[str, Any]
    ) -> bool:
        """
        Update profile with new interaction data
        
        Args:
            user_id: User identifier
            interaction_data: Interaction details
            
        Returns:
            bool: Success status
        """
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                return False
            
            # Add to interaction history
            interaction_record = {
                "timestamp": datetime.utcnow().isoformat(),
                **interaction_data
            }
            profile.interaction_history.append(interaction_record)
            
            # Limit history size
            if len(profile.interaction_history) > 1000:
                profile.interaction_history = profile.interaction_history[-1000:]
            
            # Update profile
            profile.last_updated = datetime.utcnow()
            
            # Analyze patterns if enough data
            if len(profile.interaction_history) >= self.min_interactions_for_analysis:
                await self._analyze_behavior_patterns(profile)
            
            # Update preferences
            await self._update_preferences(profile, interaction_data)
            
            # Update engagement metrics
            await self._update_engagement_metrics(profile, interaction_data)
            
            # Save profile
            await self._save_profile(user_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating interaction for {user_id}: {e}")
            return False
    
    async def analyze_user_behavior(
        self,
        user_id: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze user behavior patterns
        
        Args:
            user_id: User identifier
            analysis_type: Type of analysis to perform
            
        Returns:
            Dict containing behavior analysis
        """
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                return {"error": "Profile not found"}
            
            analysis = {
                "user_id": user_id,
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "profile_completeness": profile.calculate_completeness()
            }
            
            if analysis_type in ["comprehensive", "patterns"]:
                # Behavior pattern analysis
                patterns_analysis = await self._analyze_patterns_comprehensive(profile)
                analysis["behavior_patterns"] = patterns_analysis
            
            if analysis_type in ["comprehensive", "engagement"]:
                # Engagement analysis
                engagement_analysis = await self._analyze_engagement(profile)
                analysis["engagement_analysis"] = engagement_analysis
            
            if analysis_type in ["comprehensive", "preferences"]:
                # Preference analysis
                preference_analysis = await self._analyze_preferences(profile)
                analysis["preference_analysis"] = preference_analysis
            
            if analysis_type in ["comprehensive", "collaboration"]:
                # Collaboration potential analysis
                collaboration_analysis = await self._analyze_collaboration_potential(profile)
                analysis["collaboration_analysis"] = collaboration_analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing behavior for {user_id}: {e}")
            return {"error": str(e)}
    
    async def generate_personalization_insights(
        self,
        user_id: str,
        force_refresh: bool = False
    ) -> Optional[PersonalizationInsights]:
        """
        Generate personalization insights for user
        
        Args:
            user_id: User identifier
            force_refresh: Force regeneration of insights
            
        Returns:
            PersonalizationInsights or None
        """
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                return None
            
            # Check if recent insights exist
            if (not force_refresh and 
                profile.last_insights and
                (datetime.utcnow() - profile.last_insights.generated_at).total_seconds() < 3600):
                return profile.last_insights
            
            # Generate new insights
            insights = PersonalizationInsights(
                user_id=user_id,
                generated_at=datetime.utcnow(),
                recommended_content_types=[],
                optimal_engagement_times=[],
                preferred_interaction_style="",
                collaboration_opportunities=[],
                monetization_potential=0.0,
                protection_priorities=[],
                primary_platforms=[],
                cross_platform_strategy={},
                skill_development_areas=[],
                recommended_features=[]
            )
            
            # Content type recommendations
            insights.recommended_content_types = await self._recommend_content_types(profile)
            
            # Optimal engagement times
            insights.optimal_engagement_times = await self._find_optimal_times(profile)
            
            # Interaction style
            insights.preferred_interaction_style = await self._determine_interaction_style(profile)
            
            # Collaboration opportunities
            insights.collaboration_opportunities = await self._identify_collaboration_opportunities(profile)
            
            # Monetization potential
            insights.monetization_potential = await self._calculate_monetization_potential(profile)
            
            # Protection priorities
            insights.protection_priorities = await self._determine_protection_priorities(profile)
            
            # Platform insights
            insights.primary_platforms = await self._identify_primary_platforms(profile)
            insights.cross_platform_strategy = await self._suggest_platform_strategy(profile)
            
            # Growth recommendations
            insights.skill_development_areas = await self._identify_skill_gaps(profile)
            insights.recommended_features = await self._recommend_features(profile)
            
            # Update profile
            profile.last_insights = insights
            await self._save_profile(user_id)
            
            # Collect metrics
            await self.metrics_collector.increment("insights.generated")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights for {user_id}: {e}")
            return None
    
    async def update_profile_attributes(
        self,
        user_id: str,
        **updates
    ) -> bool:
        """
        Update profile attributes
        
        Args:
            user_id: User identifier
            **updates: Attributes to update
            
        Returns:
            bool: Success status
        """
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                return False
            
            # Update attributes
            for key, value in updates.items():
                if hasattr(profile, key):
                    if key in ["creator_type", "expertise_level"]:
                        # Handle enum types
                        if isinstance(value, str):
                            if key == "creator_type":
                                value = CreatorType(value)
                            elif key == "expertise_level":
                                value = ExpertiseLevel(value)
                    setattr(profile, key, value)
            
            profile.last_updated = datetime.utcnow()
            
            # Recalculate completeness
            profile.calculate_completeness()
            
            # Save profile
            await self._save_profile(user_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating profile for {user_id}: {e}")
            return False
    
    async def get_profile_analytics(
        self,
        user_ids: Optional[List[str]] = None,
        creator_type: Optional[CreatorType] = None
    ) -> Dict[str, Any]:
        """
        Get analytics across profiles
        
        Args:
            user_ids: Specific users to analyze
            creator_type: Filter by creator type
            
        Returns:
            Dict containing analytics
        """
        try:
            profiles_to_analyze = []
            
            if user_ids:
                for user_id in user_ids:
                    profile = await self.get_profile(user_id)
                    if profile:
                        profiles_to_analyze.append(profile)
            else:
                profiles_to_analyze = list(self.user_profiles.values())
            
            # Filter by creator type
            if creator_type:
                profiles_to_analyze = [p for p in profiles_to_analyze if p.creator_type == creator_type]
            
            if not profiles_to_analyze:
                return {"total_profiles": 0}
            
            # Calculate analytics
            total_profiles = len(profiles_to_analyze)
            
            # Creator type distribution
            creator_dist = Counter(p.creator_type.value for p in profiles_to_analyze)
            
            # Expertise distribution
            expertise_dist = Counter(p.expertise_level.value for p in profiles_to_analyze)
            
            # Completeness statistics
            completeness_scores = [p.calculate_completeness() for p in profiles_to_analyze]
            avg_completeness = sum(completeness_scores) / len(completeness_scores)
            
            # Engagement statistics
            engagement_scores = [
                p.engagement_metrics.get("overall_engagement", 0.0) 
                for p in profiles_to_analyze
            ]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
            
            # Platform usage
            platform_usage = defaultdict(int)
            for profile in profiles_to_analyze:
                for platform in profile.platform_usage.keys():
                    platform_usage[platform] += 1
            
            # Content preferences
            content_prefs = defaultdict(float)
            for profile in profiles_to_analyze:
                for pref, score in profile.content_preferences.items():
                    content_prefs[pref.value] += score
            
            return {
                "total_profiles": total_profiles,
                "creator_type_distribution": dict(creator_dist),
                "expertise_distribution": dict(expertise_dist),
                "completeness_statistics": {
                    "average_completeness": avg_completeness,
                    "high_completeness_count": sum(1 for score in completeness_scores if score > 0.8),
                    "low_completeness_count": sum(1 for score in completeness_scores if score < 0.3)
                },
                "engagement_statistics": {
                    "average_engagement": avg_engagement,
                    "high_engagement_count": sum(1 for score in engagement_scores if score > 0.7)
                },
                "platform_usage": dict(platform_usage),
                "content_preferences": dict(content_prefs),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating profile analytics: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _apply_initial_preferences(
        self,
        profile: UserContextProfile,
        preferences: Dict[str, Any]
    ):
        """Apply initial preferences to profile"""
        for key, value in preferences.items():
            if key == "content_preferences" and isinstance(value, dict):
                for pref_str, score in value.items():
                    try:
                        pref = ContentPreference(pref_str)
                        profile.content_preferences[pref] = float(score)
                    except ValueError:
                        continue
            elif key == "platform_usage" and isinstance(value, dict):
                profile.platform_usage.update(value)
            elif key == "genre_preferences" and isinstance(value, dict):
                profile.genre_preferences.update(value)
            elif hasattr(profile, key):
                setattr(profile, key, value)
    
    async def _analyze_behavior_patterns(self, profile: UserContextProfile):
        """Analyze and update behavior patterns"""
        interactions = profile.interaction_history[-100:]  # Recent interactions
        
        # Time-based patterns
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction["timestamp"])
            hour_activity[timestamp.hour] += 1
            day_activity[timestamp.strftime("%A")] += 1
        
        # Find peak activity patterns
        if hour_activity:
            peak_hour = max(hour_activity.items(), key=lambda x: x[1])
            if peak_hour[1] >= 3:  # Minimum frequency for pattern
                pattern = UserBehaviorPattern(
                    pattern_id=f"peak_hour_{peak_hour[0]}",
                    pattern_type="temporal",
                    frequency=peak_hour[1] / len(interactions),
                    confidence=min(peak_hour[1] / 10.0, 1.0),
                    last_observed=datetime.utcnow(),
                    trend="stable"
                )
                
                # Update or add pattern
                existing_patterns = [p for p in profile.behavior_patterns if p.pattern_id == pattern.pattern_id]
                if existing_patterns:
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _update_preferences completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _update_preferences failed: {e}")
                    raise
                    last_observed=datetime.utcnow(),
                    trend="stable"
                )
                
                # Update or add pattern
                existing_patterns = [p for p in profile.behavior_patterns if p.pattern_id == pattern.pattern_id]
                if existing_patterns:
                    existing_patterns[0].frequency = pattern.frequency
                    existing_patterns[0].confidence = pattern.confidence
                    existing_patterns[0].last_observed = pattern.last_observed
                else:
                    profile.behavior_patterns.append(pattern)
        
        # Clean old patterns
        profile.behavior_patterns = [
            p for p in profile.behavior_patterns
            if (datetime.utcnow() - p.last_observed).days <= 30
        ]
    
    async def _update_preferences(
        self,
        profile: UserContextProfile,
        interaction_data: Dict[str, Any]
    ):
        """Update user preferences based on interaction"""
        # Update content preferences
        content_type = interaction_data.get("content_type")
        if content_type:
            try:
                pref = ContentPreference(content_type)
                current_score = profile.content_preferences.get(pref, 0.5)
                
                # Positive interaction increases preference
                interaction_value = interaction_data.get("satisfaction", 0.5)
                new_score = current_score * 0.9 + interaction_value * 0.1
                profile.content_preferences[pref] = min(new_score, 1.0)
            except ValueError:
                pass
        
        # Update platform usage
        platform = interaction_data.get("platform")
        if platform:
            current_usage = profile.platform_usage.get(platform, 0.0)
            profile.platform_usage[platform] = min(current_usage + 0.1, 1.0)
    
    async def _update_engagement_metrics(
        self,
        profile: UserContextProfile,
        interaction_data: Dict[str, Any]
    ):
        """Update engagement metrics"""
        engagement_score = interaction_data.get("engagement_score", 0.5)
        duration = interaction_data.get("duration", 0)
        
        # Update overall engagement
        current_engagement = profile.engagement_metrics.get("overall_engagement", 0.5)
        profile.engagement_metrics["overall_engagement"] = current_engagement * 0.95 + engagement_score * 0.05
        
        # Update average session duration
        current_duration = profile.engagement_metrics.get("avg_session_duration", 0)
        if duration > 0:
            profile.engagement_metrics["avg_session_duration"] = current_duration * 0.9 + duration * 0.1
    
    async def _analyze_patterns_comprehensive(
        self,
        profile: UserContextProfile
    ) -> Dict[str, Any]:
        """Comprehensive pattern analysis"""
        patterns = {}
        
        # Temporal patterns
        temporal_patterns = [p for p in profile.behavior_patterns if p.pattern_type == "temporal"]
        patterns["temporal"] = {
            "count": len(temporal_patterns),
            "patterns": [p.to_dict() for p in temporal_patterns[:5]]
        }
        
        # Content patterns
        content_patterns = [p for p in profile.behavior_patterns if p.pattern_type == "content"]
        patterns["content"] = {
            "count": len(content_patterns),
            "patterns": [p.to_dict() for p in content_patterns[:5]]
        }
        
        # Pattern strength analysis
        strong_patterns = [p for p in profile.behavior_patterns if p.confidence > 0.7]
        patterns["strength_analysis"] = {
            "strong_patterns_count": len(strong_patterns),
            "average_confidence": sum(p.confidence for p in profile.behavior_patterns) / len(profile.behavior_patterns) if profile.behavior_patterns else 0
        }
        
        return patterns
    
    async def _analyze_engagement(
        self,
        profile: UserContextProfile
    ) -> Dict[str, Any]:
        """Analyze user engagement"""
        return {
            "overall_engagement": profile.engagement_metrics.get("overall_engagement", 0.5),
            "avg_session_duration": profile.engagement_metrics.get("avg_session_duration", 0),
            "interaction_frequency": len(profile.interaction_history) / max((datetime.utcnow() - profile.created_at).days, 1),
            "engagement_trend": "stable"  # Would be calculated from historical data
        }
    
    async def _analyze_preferences(
        self,
        profile: UserContextProfile
    ) -> Dict[str, Any]:
        """Analyze user preferences"""
        return {
            "content_preferences": {pref.value: score for pref, score in profile.content_preferences.items()},
            "platform_preferences": profile.platform_usage,
            "genre_preferences": profile.genre_preferences,
            "preferences_confidence": profile.preferences_confidence
        }
    
    async def _analyze_collaboration_potential(
        self,
        profile: UserContextProfile
    ) -> Dict[str, Any]:
        """Analyze collaboration potential"""
        collaboration_score = 0.5
        
        # Factor in creator type
        if profile.creator_type in [CreatorType.MULTI_FORMAT, CreatorType.INFLUENCER]:
            collaboration_score += 0.2
        
        # Factor in platform usage diversity
        platform_diversity = len(profile.platform_usage) / 5.0  # Assuming 5 major platforms
        collaboration_score += platform_diversity * 0.1
        
        # Factor in engagement
        engagement = profile.engagement_metrics.get("overall_engagement", 0.5)
        collaboration_score += engagement * 0.2
        
        return {
            "collaboration_score": min(collaboration_score, 1.0),
            "recommended_collaboration_types": ["cross_platform", "content_exchange"],
            "networking_potential": "high" if collaboration_score > 0.7 else "medium" if collaboration_score > 0.4 else "low"
        }
    
    async def _recommend_content_types(
        self,
        profile: UserContextProfile
    ) -> List[ContentPreference]:
        """Recommend content types for user"""
        # Sort by preference scores
        sorted_prefs = sorted(
            profile.content_preferences.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        recommendations = [pref for pref, score in sorted_prefs[:3] if score > 0.5]
        
        # Add creator type defaults if no strong preferences
        if len(recommendations) < 2:
            if profile.creator_type == CreatorType.MUSICIAN:
                recommendations.extend([ContentPreference.AUDIO, ContentPreference.VIDEO])
            elif profile.creator_type == CreatorType.PHOTOGRAPHER:
                recommendations.extend([ContentPreference.IMAGE, ContentPreference.SOCIAL_MEDIA])
            elif profile.creator_type == CreatorType.BLOGGER:
                recommendations.extend([ContentPreference.TEXT, ContentPreference.BLOG])
        
        return recommendations[:3]
    
    async def _find_optimal_times(self, profile: UserContextProfile) -> List[int]:
        """
Find optimal engagement times"""
        temporal_patterns = [p for p in profile.behavior_patterns if p.pattern_type == "temporal"]
        
        optimal_hours = []
        for pattern in temporal_patterns:
            if pattern.confidence > 0.6:
                try:
                    hour = int(pattern.pattern_id.split("_")[-1])
                    optimal_hours.append(hour)
                except ValueError:
                    continue
        
        # Default to common engagement hours if no patterns found
        if not optimal_hours:
            optimal_hours = [9, 12, 18, 20]  # Common peak hours
        
        return sorted(optimal_hours)
    
    async def _determine_interaction_style(self, profile: UserContextProfile) -> str:
        """Determine preferred interaction style"""
        engagement = profile.engagement_metrics.get("overall_engagement", 0.5)
        
        if engagement > 0.7:
            return "interactive"
        elif engagement > 0.4:
            return "guided"
        else:
            return "simplified"
    
    async def _identify_collaboration_opportunities(
        self,
        profile: UserContextProfile
    ) -> List[str]:
        """Identify collaboration opportunities"""
        opportunities = []
        
        if profile.creator_type in [CreatorType.MUSICIAN, CreatorType.ARTIST]:
            opportunities.extend(["music_collaboration", "creative_partnership"])
        
        if len(profile.platform_usage) > 2:
            opportunities.append("cross_platform_promotion")
        
        if profile.expertise_level in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]:
            opportunities.append("mentorship_opportunity")
        
        return opportunities
    
    async def _calculate_monetization_potential(self, profile: UserContextProfile) -> float:
        """Calculate monetization potential"""
        score = 0.0
        
        # Platform diversity factor
        score += len(profile.platform_usage) * 0.1
        
        # Engagement factor
        score += profile.engagement_metrics.get("overall_engagement", 0) * 0.3
        
        # Content preference diversity
        score += len(profile.content_preferences) * 0.05
        
        # Expertise level factor
        expertise_multiplier = {
            ExpertiseLevel.BEGINNER: 0.1,
            ExpertiseLevel.INTERMEDIATE: 0.3,
            ExpertiseLevel.ADVANCED: 0.5,
            ExpertiseLevel.EXPERT: 0.8,
            ExpertiseLevel.PROFESSIONAL: 1.0
        }
        score += expertise_multiplier.get(profile.expertise_level, 0.1)
        
        return min(score, 1.0)
    
    async def _determine_protection_priorities(self, profile: UserContextProfile) -> List[str]:
        """Determine content protection priorities"""
        priorities = []
        
        # High-value content types
        for pref, score in profile.content_preferences.items():
            if score > 0.7:
                if pref in [ContentPreference.AUDIO, ContentPreference.VIDEO]:
                    priorities.append("media_fingerprinting")
                elif pref == ContentPreference.IMAGE:
                    priorities.append("image_protection")
                elif pref == ContentPreference.TEXT:
                    priorities.append("plagiarism_detection")
        
        # Platform-specific protections
        if "youtube" in profile.platform_usage:
            priorities.append("video_copyright")
        if "spotify" in profile.platform_usage:
            priorities.append("audio_copyright")
        
        return list(set(priorities))
    
    async def _identify_primary_platforms(self, profile: UserContextProfile) -> List[str]:
        """Identify primary platforms"""
        sorted_platforms = sorted(
            profile.platform_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [platform for platform, usage in sorted_platforms[:3] if usage > 0.3]
    
    async def _suggest_platform_strategy(self, profile: UserContextProfile) -> Dict[str, str]:
        """
Suggest cross-platform strategy"""
        strategy = {}
        
        primary_platforms = await self._identify_primary_platforms(profile)
        
        for platform in primary_platforms:
            if platform in ["instagram", "tiktok"]:
                strategy[platform] = "visual_content_focus"
            elif platform in ["youtube", "spotify"]:
                strategy[platform] = "long_form_content"
            elif platform in ["twitter", "linkedin"]:
                strategy[platform] = "engagement_focus"
        
        return strategy
    
    async def _identify_skill_gaps(self, profile: UserContextProfile) -> List[str]:
        """Identify areas for skill development"""
        gaps = []
        
        # Low platform usage suggests growth opportunity
        if len(profile.platform_usage) < 3:
            gaps.append("platform_diversification")
        
        # Low content type diversity
        if len(profile.content_preferences) < 2:
            gaps.append("content_format_expansion")
        
        # Low engagement suggests improvement needed
        if profile.engagement_metrics.get("overall_engagement", 0) < 0.5:
            gaps.append("audience_engagement")
        
        return gaps
    
    async def _recommend_features(self, profile: UserContextProfile) -> List[str]:
        """Recommend platform features"""
        features = []
        
        # Based on creator type
        if profile.creator_type == CreatorType.MUSICIAN:
            features.extend(["audio_analytics", "collaboration_matching"])
        elif profile.creator_type == CreatorType.PHOTOGRAPHER:
            features.extend(["image_protection", "portfolio_optimization"])
        
        # Based on expertise level
        if profile.expertise_level in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]:
            features.append("advanced_analytics")
        
        # Based on engagement
        if profile.engagement_metrics.get("overall_engagement", 0) > 0.7:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__initialize_analyzers_input(data)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__initialize_analyzers_result(result)
            
                    logger.info(f"AI processing _initialize_analyzers completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _initialize_analyzers failed: {e}")
                    raise
        return features
    
    async def _background_updates(self):
        """Background task for profile updates"""
        while True:
            try:
                await asyncio.sleep(self.profile_update_interval)
                
                # Update all profiles
                for user_id, profile in self.user_profiles.items():
                    # Refresh behavior patterns
                    if len(profile.interaction_history) >= self.min_interactions_for_analysis:
                        await self._analyze_behavior_patterns(profile)
                    
                    # Update completeness score
                    profile.calculate_completeness()
                
                # Save updated profiles
                await self._save_profiles()
                
                await self.metrics_collector.increment("profiles.background_updates")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background update error: {e}")
                await asyncio.sleep(300)  # Wait before retrying
    
    async def _initialize_analyzers(self):
        """Initialize pattern analyzers"""
        # Placeholder for ML model initialization
        pass
    
    async def _load_profiles(self):
        """
Load profiles from persistent storage"""
        try:
            profiles_data = await self.cache_manager.get("user_context_profiles")
            if profiles_data:
                for user_id, profile_data in profiles_data.items():
                    profile = self._profile_from_dict(profile_data)
                    self.user_profiles[user_id] = profile
                    
        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")
    
    async def _save_profiles(self):
        """Save profiles to persistent storage"""
        try:
            profiles_data = {}
            for user_id, profile in self.user_profiles.items():
                profiles_data[user_id] = profile.to_dict()
            
            await self.cache_manager.set(
                "user_context_profiles",
                profiles_data,
                ttl=86400 * 7  # 7 days
            )
            
        except Exception as e:
            self.logger.error(f"Error saving profiles: {e}")
    
    async def _load_profile(self, user_id: str) -> Optional[UserContextProfile]:
        """Load specific profile"""
        try:
            profile_data = await self.cache_manager.get(f"user_context_profile:{user_id}")
            if profile_data:
                return self._profile_from_dict(profile_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading profile {user_id}: {e}")
            return None
    
    async def _save_profile(self, user_id: str):
        """Save specific profile"""
        try:
            if user_id in self.user_profiles:
                profile_data = self.user_profiles[user_id].to_dict()
                await self.cache_manager.set(
                    f"user_context_profile:{user_id}",
                    profile_data,
                    ttl=86400 * 7
                )
                
        except Exception as e:
            self.logger.error(f"Error saving profile {user_id}: {e}")
    
    def _profile_from_dict(self, data: Dict[str, Any]) -> UserContextProfile:
        """Reconstruct profile from dictionary"""
        # Reconstruct enums and complex types
        creator_type = CreatorType(data["creator_type"])
        expertise_level = ExpertiseLevel(data["expertise_level"])
        
        content_preferences = {}
        for pref_str, score in data.get("content_preferences", {}).items():
            try:
                pref = ContentPreference(pref_str)
                content_preferences[pref] = score
            except ValueError:
                continue
        
        behavior_patterns = []
        for pattern_data in data.get("behavior_patterns", []):
            pattern = UserBehaviorPattern(
                pattern_id=pattern_data["pattern_id"],
                pattern_type=pattern_data["pattern_type"],
                frequency=pattern_data["frequency"],
                confidence=pattern_data["confidence"],
                last_observed=datetime.fromisoformat(pattern_data["last_observed"]),
                trend=pattern_data["trend"],
                seasonal_indicators=pattern_data.get("seasonal_indicators", {}),
                context_triggers=pattern_data.get("context_triggers", [])
            )
            behavior_patterns.append(pattern)
        
        # Reconstruct insights if present
        last_insights = None
        insights_data = data.get("last_insights")
        if insights_data:
            last_insights = PersonalizationInsights(
                user_id=insights_data["user_id"],
                generated_at=datetime.fromisoformat(insights_data["generated_at"]),
                recommended_content_types=[ContentPreference(pref) for pref in insights_data["recommended_content_types"]],
                optimal_engagement_times=insights_data["optimal_engagement_times"],
                preferred_interaction_style=insights_data["preferred_interaction_style"],
                collaboration_opportunities=insights_data["collaboration_opportunities"],
                monetization_potential=insights_data["monetization_potential"],
                protection_priorities=insights_data["protection_priorities"],
                primary_platforms=insights_data["primary_platforms"],
                cross_platform_strategy=insights_data["cross_platform_strategy"],
                skill_development_areas=insights_data["skill_development_areas"],
                recommended_features=insights_data["recommended_features"]
            )
        
        profile = UserContextProfile(
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            creator_type=creator_type,
            expertise_level=expertise_level,
            primary_language=data["primary_language"],
            location=data.get("location"),
            content_preferences=content_preferences,
            platform_usage=data.get("platform_usage", {}),
            genre_preferences=data.get("genre_preferences", {}),
            behavior_patterns=behavior_patterns,
            engagement_metrics=data.get("engagement_metrics", {}),
            collaboration_preferences=data.get("collaboration_preferences", {}),
            monetization_goals=data.get("monetization_goals", []),
            protection_awareness=data.get("protection_awareness", 0.5),
            learning_velocity=data.get("learning_velocity", 0.5),
            adaptation_rate=data.get("adaptation_rate", 0.3),
            feedback_sensitivity=data.get("feedback_sensitivity", 0.7),
            preferences_confidence=data.get("preferences_confidence", 0.5),
            profile_completeness=data.get("profile_completeness", 0.0),
            last_insights=last_insights
        )
        
        # Note: interaction_history is not fully restored to save space
        # Only count is preserved
        
        return profile
