"""Context Adapter
===============

Industrial-grade context adaptation engine for IA Influencer Agent.
Adapts user experience based on contextual factors like device, location, time,
platform, mood, and environmental conditions for optimal personalization.

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
import json
from geopy.distance import geodesic
import pytz

from ..core.base_service import BaseService
from ..core.exceptions import ContextAdaptationError, ValidationError
from ..cache.redis_cache import RedisCache
from ..database.mongodb import MongoDBHandler
from ..ml.context_models import ContextualMLModel
from ..analytics.environment_analyzer import EnvironmentAnalyzer

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context factors"""    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    DEVICE = "device"
    PLATFORM = "platform"
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    BEHAVIORAL = "behavioral"
    EMOTIONAL = "emotional"


class DeviceType(str, Enum):
    """Device types for context adaptation"""    MOBILE_PHONE = "mobile_phone"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    SMART_TV = "smart_tv"
    SMART_SPEAKER = "smart_speaker"
    WEARABLE = "wearable"
    UNKNOWN = "unknown"


class PlatformContext(str, Enum):
    """Platform contexts"""    WEB_BROWSER = "web_browser"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    API_INTEGRATION = "api_integration"
    SOCIAL_MEDIA_EMBED = "social_media_embed"
    THIRD_PARTY_WIDGET = "third_party_widget"


class TimeOfDay(str, Enum):
    """Time periods for temporal context"""    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"  # 8-12 PM
    AFTERNOON = "afternoon"  # 12-5 PM
    EVENING = "evening"  # 5-8 PM
    NIGHT = "night"  # 8-11 PM
    LATE_NIGHT = "late_night"  # 11 PM-5 AM


class MoodState(str, Enum):
    """User mood states for emotional context"""    CREATIVE_INSPIRED = "creative_inspired"
    FOCUSED_PRODUCTIVE = "focused_productive"
    RELAXED_BROWSING = "relaxed_browsing"
    SOCIAL_ENGAGED = "social_engaged"
    LEARNING_CURIOUS = "learning_curious"
    STRESSED_BUSY = "stressed_busy"
    ENTERTAINMENT_SEEKING = "entertainment_seeking"
    PROFESSIONAL_WORKING = "professional_working"


@dataclass
class ContextualFactor:
    """Individual contextual factor"""    factor_type: ContextType
    factor_name: str
    factor_value: Any
    confidence: float
    impact_weight: float
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserContext:
    """Complete user context information"""    user_id: str
    session_id: str
    timestamp: datetime
    
    # Temporal context
    time_of_day: TimeOfDay
    day_of_week: str
    timezone: str
    
    # Spatial context
    location: Optional[Dict[str, Any]] = None
    location_type: Optional[str] = None  # home, work, travel, etc.
    
    # Device context
    device_type: DeviceType
    device_capabilities: Dict[str, Any] = field(default_factory=dict)
    screen_size: Optional[Tuple[int, int]] = None
    connection_type: Optional[str] = None
    
    # Platform context
    platform: PlatformContext
    platform_version: Optional[str] = None
    feature_availability: Dict[str, bool] = field(default_factory=dict)
    
    # Environmental context
    noise_level: Optional[str] = None
    lighting_conditions: Optional[str] = None
    activity_level: Optional[str] = None
    
    # Social context
    social_setting: Optional[str] = None  # alone, with_friends, at_work, etc.
    collaboration_mode: bool = False
    
    # Behavioral context
    session_duration: Optional[int] = None
    recent_actions: List[str] = field(default_factory=list)
    interaction_frequency: Optional[float] = None
    
    # Emotional context
    mood_state: Optional[MoodState] = None
    energy_level: Optional[str] = None
    
    # Additional factors
    contextual_factors: List[ContextualFactor] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationRule:
    """Context adaptation rule"""    rule_id: str
    rule_name: str
    conditions: Dict[str, Any]
    adaptations: Dict[str, Any]
    priority: int
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AdaptationResult:
    """Result of context adaptation"""    user_id: str
    original_context: UserContext
    applied_rules: List[str]
    adaptations: Dict[str, Any]
    adaptation_confidence: float
    processing_time_ms: float
    generated_at: datetime = field(default_factory=datetime.now)


class ContextAdapter(BaseService):
    """    Advanced context adaptation engine for personalization
    """    
    def __init__(
        self,
        redis_cache: RedisCache,
        mongodb_handler: MongoDBHandler,
        contextual_model: ContextualMLModel,
        environment_analyzer: EnvironmentAnalyzer
    ):
        super().__init__()
        self.redis_cache = redis_cache
        self.mongodb = mongodb_handler
        self.contextual_model = contextual_model
        self.environment_analyzer = environment_analyzer
        
        # Configuration
        self.cache_ttl = 600  # 10 minutes
        self.context_window_minutes = 30
        self.adaptation_threshold = 0.6
        self.max_adaptation_rules = 100
        
        # Adaptation rules
        self._adaptation_rules = {}
        self._rule_priorities = {}
        
        # Context history
        self._context_history = {}
        
        logger.info("ContextAdapter initialized successfully")

    async def initialize(self) -> None:
        """Initialize context adapter"""        try:
            # Initialize ML models
            await self.contextual_model.initialize()
            await self.environment_analyzer.initialize()
            
            # Load adaptation rules
            await self._load_adaptation_rules()
            
            # Initialize context tracking
            await self._initialize_context_tracking()
            
            logger.info("ContextAdapter initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContextAdapter: {e}")
            raise ContextAdaptationError(f"Initialization failed: {e}")

    async def adapt_experience(
        self,
        user_context: UserContext,
        base_experience: Dict[str, Any],
        adaptation_scope: Optional[List[str]] = None
    ) -> AdaptationResult:
        """        Adapt user experience based on context
        
        Args:
            user_context: Current user context
            base_experience: Base experience to adapt
            adaptation_scope: Specific aspects to adapt
            
        Returns:
            Adaptation result with modified experience
        """        try:
            start_time = datetime.now()
            
            # Validate context
            await self._validate_user_context(user_context)
            
            # Analyze current context
            context_analysis = await self._analyze_context(user_context)
            
            # Find applicable adaptation rules
            applicable_rules = await self._find_applicable_rules(
                user_context, context_analysis
            )
            
            # Apply adaptations
            adapted_experience = base_experience.copy()
            applied_rules = []
            
            for rule in applicable_rules:
                if await self._should_apply_rule(rule, user_context, context_analysis):
                    adapted_experience = await self._apply_adaptation_rule(
                        rule, adapted_experience, user_context
                    )
                    applied_rules.append(rule.rule_id)
            
            # Calculate adaptation confidence
            adaptation_confidence = await self._calculate_adaptation_confidence(
                user_context, applied_rules, context_analysis
            )
            
            # Create adaptation result
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = AdaptationResult(
                user_id=user_context.user_id,
                original_context=user_context,
                applied_rules=applied_rules,
                adaptations={
                    "original": base_experience,
                    "adapted": adapted_experience,
                    "changes": await self._calculate_adaptation_changes(
                        base_experience, adapted_experience
                    )
                },
                adaptation_confidence=adaptation_confidence,
                processing_time_ms=processing_time
            )
            
            # Cache result
            await self._cache_adaptation_result(result)
            
            # Track adaptation
            await self._track_adaptation(result)
            
            # Update context history
            await self._update_context_history(user_context, result)
            
            logger.info(f"Context adaptation completed for user {user_context.user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to adapt experience: {e}")
            raise ContextAdaptationError(f"Experience adaptation failed: {e}")

    async def infer_context(
        self,
        user_id: str,
        session_id: str,
        raw_context_data: Dict[str, Any]
    ) -> UserContext:
        """        Infer comprehensive user context from raw data
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            raw_context_data: Raw context information
            
        Returns:
            Inferred user context
        """        try:
            # Extract basic context information
            timestamp = datetime.now()
            
            # Infer temporal context
            temporal_context = await self._infer_temporal_context(
                timestamp, raw_context_data
            )
            
            # Infer spatial context
            spatial_context = await self._infer_spatial_context(raw_context_data)
            
            # Infer device context
            device_context = await self._infer_device_context(raw_context_data)
            
            # Infer platform context
            platform_context = await self._infer_platform_context(raw_context_data)
            
            # Infer environmental context
            environmental_context = await self._infer_environmental_context(
                raw_context_data
            )
            
            # Infer social context
            social_context = await self._infer_social_context(
                user_id, raw_context_data
            )
            
            # Infer behavioral context
            behavioral_context = await self._infer_behavioral_context(
                user_id, session_id, raw_context_data
            )
            
            # Infer emotional context
            emotional_context = await self._infer_emotional_context(
                user_id, raw_context_data
            )
            
            # Combine all contextual factors
            contextual_factors = []
            contextual_factors.extend(temporal_context.get("factors", []))
            contextual_factors.extend(spatial_context.get("factors", []))
            contextual_factors.extend(device_context.get("factors", []))
            contextual_factors.extend(platform_context.get("factors", []))
            contextual_factors.extend(environmental_context.get("factors", []))
            contextual_factors.extend(social_context.get("factors", []))
            contextual_factors.extend(behavioral_context.get("factors", []))
            contextual_factors.extend(emotional_context.get("factors", []))
            
            # Create user context
            user_context = UserContext(
                user_id=user_id,
                session_id=session_id,
                timestamp=timestamp,
                time_of_day=temporal_context.get("time_of_day", TimeOfDay.MORNING),
                day_of_week=temporal_context.get("day_of_week", "unknown"),
                timezone=temporal_context.get("timezone", "UTC"),
                location=spatial_context.get("location"),
                location_type=spatial_context.get("location_type"),
                device_type=device_context.get("device_type", DeviceType.UNKNOWN),
                device_capabilities=device_context.get("capabilities", {}),
                screen_size=device_context.get("screen_size"),
                connection_type=device_context.get("connection_type"),
                platform=platform_context.get("platform", PlatformContext.WEB_BROWSER),
                platform_version=platform_context.get("version"),
                feature_availability=platform_context.get("features", {}),
                noise_level=environmental_context.get("noise_level"),
                lighting_conditions=environmental_context.get("lighting"),
                activity_level=environmental_context.get("activity_level"),
                social_setting=social_context.get("setting"),
                collaboration_mode=social_context.get("collaboration", False),
                session_duration=behavioral_context.get("session_duration"),
                recent_actions=behavioral_context.get("recent_actions", []),
                interaction_frequency=behavioral_context.get("interaction_frequency"),
                mood_state=emotional_context.get("mood_state"),
                energy_level=emotional_context.get("energy_level"),
                contextual_factors=contextual_factors,
                metadata=raw_context_data.get("metadata", {})
            )
            
            logger.info(f"Context inferred for user {user_id}")
            return user_context
            
        except Exception as e:
            logger.error(f"Failed to infer context: {e}")
            raise ContextAdaptationError(f"Context inference failed: {e}")

    async def get_context_recommendations(
        self,
        user_context: UserContext,
        recommendation_type: str = "experience_optimization"
    ) -> Dict[str, Any]:
        """        Get context-based recommendations for user experience optimization
        
        Args:
            user_context: Current user context
            recommendation_type: Type of recommendations
            
        Returns:
            Context-based recommendations
        """        try:
            # Analyze context patterns
            context_patterns = await self._analyze_context_patterns(user_context)
            
            # Generate recommendations based on type
            if recommendation_type == "experience_optimization":
                recommendations = await self._generate_experience_recommendations(
                    user_context, context_patterns
                )
            elif recommendation_type == "content_timing":
                recommendations = await self._generate_timing_recommendations(
                    user_context, context_patterns
                )
            elif recommendation_type == "interaction_optimization":
                recommendations = await self._generate_interaction_recommendations(
                    user_context, context_patterns
                )
            elif recommendation_type == "platform_adaptation":
                recommendations = await self._generate_platform_recommendations(
                    user_context, context_patterns
                )
            else:
                recommendations = await self._generate_general_recommendations(
                    user_context, context_patterns
                )
            
            # Add context insights
            context_insights = await self._generate_context_insights(
                user_context, context_patterns
            )
            
            result = {
                "user_id": user_context.user_id,
                "recommendation_type": recommendation_type,
                "context_summary": await self._summarize_context(user_context),
                "recommendations": recommendations,
                "context_insights": context_insights,
                "confidence": await self._calculate_recommendation_confidence(
                    user_context, recommendations
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Context recommendations generated for user {user_context.user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate context recommendations: {e}")
            return {"error": f"Recommendation generation failed: {e}"}

    # Private helper methods
    
    async def _validate_user_context(self, user_context: UserContext) -> None:
        """Validate user context data"""        if not user_context.user_id:
            raise ValidationError("User ID is required")
        
        if not user_context.session_id:
            raise ValidationError("Session ID is required")
        
        if not isinstance(user_context.timestamp, datetime):
            raise ValidationError("Timestamp must be a datetime object")

    async def _analyze_context(self, user_context: UserContext) -> Dict[str, Any]:
        """Analyze user context for adaptation"""        try:
            analysis = {
                "temporal_analysis": await self._analyze_temporal_context(user_context),
                "spatial_analysis": await self._analyze_spatial_context(user_context),
                "device_analysis": await self._analyze_device_context(user_context),
                "platform_analysis": await self._analyze_platform_context(user_context),
                "environmental_analysis": await self._analyze_environmental_context(user_context),
                "behavioral_analysis": await self._analyze_behavioral_context(user_context),
                "emotional_analysis": await self._analyze_emotional_context(user_context)
            }
            
            # Calculate overall context score
            analysis["context_score"] = await self._calculate_context_score(user_context)
            
            # Identify context patterns
            analysis["patterns"] = await self._identify_context_patterns(user_context)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze context: {e}")
            return {}

    async def _find_applicable_rules(
        self,
        user_context: UserContext,
        context_analysis: Dict[str, Any]
    ) -> List[AdaptationRule]:
        """Find adaptation rules applicable to current context"""        try:
            applicable_rules = []
            
            for rule_id, rule in self._adaptation_rules.items():
                if not rule.enabled:
                    continue
                
                if await self._rule_matches_context(rule, user_context, context_analysis):
                    applicable_rules.append(rule)
            
            # Sort by priority
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Failed to find applicable rules: {e}")
            return []

    async def _apply_adaptation_rule(
        self,
        rule: AdaptationRule,
        experience: Dict[str, Any],
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Apply adaptation rule to experience"""        try:
            adapted_experience = experience.copy()
            
            for adaptation_key, adaptation_value in rule.adaptations.items():
                if adaptation_key == "ui_layout":
                    adapted_experience = await self._adapt_ui_layout(
                        adapted_experience, adaptation_value, user_context
                    )
                elif adaptation_key == "content_density":
                    adapted_experience = await self._adapt_content_density(
                        adapted_experience, adaptation_value, user_context
                    )
                elif adaptation_key == "interaction_mode":
                    adapted_experience = await self._adapt_interaction_mode(
                        adapted_experience, adaptation_value, user_context
                    )
                elif adaptation_key == "feature_availability":
                    adapted_experience = await self._adapt_feature_availability(
                        adapted_experience, adaptation_value, user_context
                    )
                elif adaptation_key == "notification_settings":
                    adapted_experience = await self._adapt_notification_settings(
                        adapted_experience, adaptation_value, user_context
                    )
                else:
                    # Generic adaptation
                    adapted_experience[adaptation_key] = adaptation_value
            
            return adapted_experience
            
        except Exception as e:
            logger.error(f"Failed to apply adaptation rule: {e}")
            return experience

    async def _infer_temporal_context(
        self,
        timestamp: datetime,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Infer temporal context factors"""        try:
            # Determine timezone
            timezone_str = raw_data.get("timezone", "UTC")
            tz = pytz.timezone(timezone_str)
            local_time = timestamp.astimezone(tz)
            
            # Determine time of day
            hour = local_time.hour
            if 5 <= hour < 8:
                time_of_day = TimeOfDay.EARLY_MORNING
            elif 8 <= hour < 12:
                time_of_day = TimeOfDay.MORNING
            elif 12 <= hour < 17:
                time_of_day = TimeOfDay.AFTERNOON
            elif 17 <= hour < 20:
                time_of_day = TimeOfDay.EVENING
            elif 20 <= hour < 23:
                time_of_day = TimeOfDay.NIGHT
            else:
                time_of_day = TimeOfDay.LATE_NIGHT
            
            # Day of week
            day_of_week = local_time.strftime("%A").lower()
            
            # Create temporal factors
            factors = [
                ContextualFactor(
                    factor_type=ContextType.TEMPORAL,
                    factor_name="time_of_day",
                    factor_value=time_of_day.value,
                    confidence=1.0,
                    impact_weight=0.8,
                    last_updated=timestamp
                ),
                ContextualFactor(
                    factor_type=ContextType.TEMPORAL,
                    factor_name="day_of_week",
                    factor_value=day_of_week,
                    confidence=1.0,
                    impact_weight=0.6,
                    last_updated=timestamp
                )
            ]
            
            return {
                "time_of_day": time_of_day,
                "day_of_week": day_of_week,
                "timezone": timezone_str,
                "local_time": local_time,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Failed to infer temporal context: {e}")
            return {}

    async def _infer_device_context(
        self,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Infer device context factors"""        try:
            # Extract device information
            user_agent = raw_data.get("user_agent", "")
            screen_width = raw_data.get("screen_width")
            screen_height = raw_data.get("screen_height")
            connection_type = raw_data.get("connection_type")
            
            # Determine device type
            device_type = DeviceType.UNKNOWN
            if "Mobile" in user_agent or "Android" in user_agent:
                device_type = DeviceType.MOBILE_PHONE
            elif "Tablet" in user_agent or "iPad" in user_agent:
                device_type = DeviceType.TABLET
            elif "TV" in user_agent:
                device_type = DeviceType.SMART_TV
            else:
                device_type = DeviceType.DESKTOP
            
            # Device capabilities
            capabilities = {
                "touch_enabled": raw_data.get("touch_enabled", False),
                "camera_available": raw_data.get("camera_available", False),
                "microphone_available": raw_data.get("microphone_available", False),
                "geolocation_available": raw_data.get("geolocation_available", False)
            }
            
            # Screen size
            screen_size = None
            if screen_width and screen_height:
                screen_size = (int(screen_width), int(screen_height))
            
            # Create device factors
            factors = [
                ContextualFactor(
                    factor_type=ContextType.DEVICE,
                    factor_name="device_type",
                    factor_value=device_type.value,
                    confidence=0.8,
                    impact_weight=0.9,
                    last_updated=datetime.now()
                )
            ]
            
            if screen_size:
                factors.append(
                    ContextualFactor(
                        factor_type=ContextType.DEVICE,
                        factor_name="screen_size",
                        factor_value=screen_size,
                        confidence=1.0,
                        impact_weight=0.7,
                        last_updated=datetime.now()
                    )
                )
            
            return {
                "device_type": device_type,
                "capabilities": capabilities,
                "screen_size": screen_size,
                "connection_type": connection_type,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Failed to infer device context: {e}")
            return {}


# Factory functions and utilities

def create_context_adapter(
    redis_cache: RedisCache,
    mongodb_handler: MongoDBHandler,
    contextual_model: ContextualMLModel,
    environment_analyzer: EnvironmentAnalyzer
) -> ContextAdapter:
    """Create context adapter instance"""    return ContextAdapter(
        redis_cache=redis_cache,
        mongodb_handler=mongodb_handler,
        contextual_model=contextual_model,
        environment_analyzer=environment_analyzer
    )


def validate_user_context(user_context: UserContext) -> bool:
    """Validate user context data"""    if not user_context.user_id or not isinstance(user_context.user_id, str):
        return False
    
    if not user_context.session_id or not isinstance(user_context.session_id, str):
        return False
    
    if not isinstance(user_context.timestamp, datetime):
        return False
    
    return True
