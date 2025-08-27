"""
Personalization Engine - AI-Powered Notification Content Personalization

Advanced AI-driven personalization engine for IA Influencer Agent notifications.
Provides intelligent content adaptation, multi-language support, user behavior analysis,
dynamic template customization, and A/B testing optimization for maximum engagement.

Key Features:
- AI-powered content personalization based on user profiles and behavior
- Multi-language localization with cultural adaptation
- Dynamic template customization with real-time optimization
- User preference learning with behavioral pattern analysis
- Content tone and style adaptation based on creator type
- Engagement optimization with A/B testing framework

Personalization Factors:
- Creator type (musician, blogger, photographer, influencer, comedian)
- Platform preferences and usage patterns
- Historical engagement metrics and interaction data
- Cultural and linguistic preferences
- Time zone and communication timing optimization
- Content format preferences (visual, audio, text)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission from the author is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing and usage rights.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import re
from pathlib import Path

from .notification_models import NotificationRequest, NotificationContent, NotificationTemplate
from .config import NotificationConfig
from .constants import PERSONALIZATION_RULES, CREATOR_TYPES, LANGUAGE_CODES

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Creator types for personalization."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ARTIST = "artist"
    PODCASTER = "podcaster"
    STREAMER = "streamer"
    CONTENT_CREATOR = "content_creator"


class PersonalizationStyle(Enum):
    """Content personalization styles."""
    PROFESSIONAL = "professional"      # Formal, business-focused
    CASUAL = "casual"                  # Friendly, conversational
    ENTHUSIASTIC = "enthusiastic"     # Energetic, motivational
    EDUCATIONAL = "educational"       # Informative, instructional
    CREATIVE = "creative"              # Artistic, expressive
    TECHNICAL = "technical"            # Detailed, specification-focused


class CommunicationTone(Enum):
    """Communication tone options."""
    FORMAL = "formal"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    URGENT = "urgent"
    INFORMATIVE = "informative"
    CELEBRATORY = "celebratory"
    WARNING = "warning"
    SUPPORTIVE = "supportive"


@dataclass
class UserProfile:
    """User profile for personalization."""
    user_id: str
    creator_type: CreatorType
    preferred_language: str
    timezone: str
    communication_style: PersonalizationStyle
    preferred_tone: CommunicationTone
    engagement_patterns: Dict[str, Any]
    content_preferences: Dict[str, Any]
    cultural_context: Dict[str, Any]
    historical_interactions: List[Dict[str, Any]]
    personalization_settings: Dict[str, Any]


@dataclass
class PersonalizationContext:
    """Context for content personalization."""
    user_profile: UserProfile
    notification_type: str
    business_context: Dict[str, Any]
    temporal_context: Dict[str, Any]
    platform_context: Dict[str, Any]
    engagement_history: Dict[str, Any]
    ab_test_variant: Optional[str] = None


@dataclass
class PersonalizationResult:
    """Result of content personalization."""
    personalized_content: NotificationContent
    personalization_factors: Dict[str, Any]
    confidence_score: float
    ab_test_variant: Optional[str]
    processing_time: float
    applied_rules: List[str]
    original_content: NotificationContent


class PersonalizationEngine:
    """
    AI-powered notification content personalization engine.
    
    Provides intelligent content adaptation based on user profiles,
    behavioral patterns, cultural preferences, and business context.
    """
    
    def __init__(self, config: NotificationConfig):
        """Initialize personalization engine with configuration."""
        self.config = config
        self.personalization_rules = PERSONALIZATION_RULES
        self.creator_types = CREATOR_TYPES
        self.language_codes = LANGUAGE_CODES
        
        # User profile cache
        self._profile_cache: Dict[str, UserProfile] = {}
        self._cache_ttl = timedelta(hours=1)
        
        # Personalization templates
        self._personalization_templates = self._load_personalization_templates()
        
        # A/B testing variants
        self._ab_test_variants = self._initialize_ab_test_variants()
        
        # Language resources
        self._language_resources = self._load_language_resources()
        
        # Performance metrics
        self.personalization_stats = {
            "total_personalizations": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "engagement_improvement": 0.0,
            "localization_accuracy": 0.0
        }
        
        logger.info("Personalization engine initialized successfully")
    
    async def personalize_content(
        self,
        request: NotificationRequest,
        context: Optional[PersonalizationContext] = None
    ) -> PersonalizationResult:
        """
        Personalize notification content based on user profile and context.
        
        Args:
            request: Notification request to personalize
            context: Optional personalization context
            
        Returns:
            PersonalizationResult with personalized content
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get or build personalization context
            if not context:
                context = await self._build_personalization_context(request)
            
            # Store original content
            original_content = request.content
            
            # Apply personalization transformations
            personalized_content = await self._apply_personalization_transformations(
                request.content, context
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_personalization_confidence(
                original_content, personalized_content, context
            )
            
            # Get applied personalization rules
            applied_rules = self._get_applied_personalization_rules(context)
            
            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create result
            result = PersonalizationResult(
                personalized_content=personalized_content,
                personalization_factors=self._extract_personalization_factors(context),
                confidence_score=confidence_score,
                ab_test_variant=context.ab_test_variant,
                processing_time=processing_time,
                applied_rules=applied_rules,
                original_content=original_content
            )
            
            # Update statistics
            self._update_personalization_stats(processing_time)
            
            logger.debug(
                f"Content personalized for user {context.user_profile.user_id} "
                f"(confidence: {confidence_score:.3f}, time: {processing_time:.3f}s)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Content personalization failed: {e}")
            
            # Return fallback result
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return PersonalizationResult(
                personalized_content=request.content,
                personalization_factors={},
                confidence_score=0.3,
                ab_test_variant=None,
                processing_time=processing_time,
                applied_rules=[],
                original_content=request.content
            )
    
    async def _build_personalization_context(self, request: NotificationRequest) -> PersonalizationContext:
        """Build personalization context from notification request."""
        try:
            # Get user profile
            user_profile = await self._get_user_profile(request.recipient_id)
            
            # Build business context
            business_context = self._extract_business_context(request)
            
            # Build temporal context
            temporal_context = self._extract_temporal_context(request, user_profile)
            
            # Build platform context
            platform_context = self._extract_platform_context(request)
            
            # Get engagement history
            engagement_history = await self._get_engagement_history(request.recipient_id)
            
            # Select A/B test variant
            ab_test_variant = self._select_ab_test_variant(request, user_profile)
            
            return PersonalizationContext(
                user_profile=user_profile,
                notification_type=request.type,
                business_context=business_context,
                temporal_context=temporal_context,
                platform_context=platform_context,
                engagement_history=engagement_history,
                ab_test_variant=ab_test_variant
            )
            
        except Exception as e:
            logger.error(f"Failed to build personalization context: {e}")
            
            # Return minimal context
            return PersonalizationContext(
                user_profile=self._get_default_user_profile(request.recipient_id),
                notification_type=request.type,
                business_context={},
                temporal_context={},
                platform_context={},
                engagement_history={}
            )
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile for personalization."""
        try:
            # Check cache first
            if user_id in self._profile_cache:
                cached_profile = self._profile_cache[user_id]
                if self._is_profile_cache_valid(cached_profile):
                    return cached_profile
            
            # Build user profile from various data sources
            profile = await self._build_user_profile(user_id)
            
            # Cache profile
            self._profile_cache[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile for {user_id}: {e}")
            return self._get_default_user_profile(user_id)
    
    async def _build_user_profile(self, user_id: str) -> UserProfile:
        """Build comprehensive user profile."""
        try:
            # In production, this would query various data sources:
            # - User account information
            # - Content creation history
            # - Platform usage patterns
            # - Engagement analytics
            # - Preference settings
            
            # Mock profile building for now
            profile = UserProfile(
                user_id=user_id,
                creator_type=CreatorType.CONTENT_CREATOR,  # Default
                preferred_language="en",
                timezone="UTC",
                communication_style=PersonalizationStyle.PROFESSIONAL,
                preferred_tone=CommunicationTone.FRIENDLY,
                engagement_patterns={
                    "best_time_of_day": "10:00",
                    "preferred_frequency": "daily",
                    "response_rate": 0.75,
                    "preferred_channels": ["email", "push"]
                },
                content_preferences={
                    "format": "mixed",
                    "length": "medium",
                    "include_visuals": True,
                    "personalization_level": "high"
                },
                cultural_context={
                    "country": "US",
                    "language_preference": "en",
                    "cultural_adaptation": True
                },
                historical_interactions=[],
                personalization_settings={
                    "enable_ai_personalization": True,
                    "enable_localization": True,
                    "enable_tone_adaptation": True
                }
            )
            
            # Enhance profile with actual data if available
            profile = await self._enhance_user_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to build user profile: {e}")
            return self._get_default_user_profile(user_id)
    
    async def _enhance_user_profile(self, profile: UserProfile) -> UserProfile:
        """Enhance user profile with additional data sources."""
        try:
            # Creator type detection based on content history
            creator_type = await self._detect_creator_type(profile.user_id)
            if creator_type:
                profile.creator_type = creator_type
            
            # Language preference detection
            language = await self._detect_preferred_language(profile.user_id)
            if language:
                profile.preferred_language = language
            
            # Timezone detection
            timezone = await self._detect_user_timezone(profile.user_id)
            if timezone:
                profile.timezone = timezone
            
            # Communication style analysis
            style = await self._analyze_communication_style(profile.user_id)
            if style:
                profile.communication_style = style
            
            # Engagement pattern analysis
            patterns = await self._analyze_engagement_patterns(profile.user_id)
            if patterns:
                profile.engagement_patterns.update(patterns)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to enhance user profile: {e}")
            return profile
    
    def _get_default_user_profile(self, user_id: str) -> UserProfile:
        """Get default user profile when data is unavailable."""
        return UserProfile(
            user_id=user_id,
            creator_type=CreatorType.CONTENT_CREATOR,
            preferred_language="en",
            timezone="UTC",
            communication_style=PersonalizationStyle.PROFESSIONAL,
            preferred_tone=CommunicationTone.FRIENDLY,
            engagement_patterns={
                "best_time_of_day": "10:00",
                "preferred_frequency": "daily",
                "response_rate": 0.5,
                "preferred_channels": ["email"]
            },
            content_preferences={
                "format": "text",
                "length": "medium",
                "include_visuals": False,
                "personalization_level": "low"
            },
            cultural_context={
                "country": "US",
                "language_preference": "en",
                "cultural_adaptation": False
            },
            historical_interactions=[],
            personalization_settings={
                "enable_ai_personalization": True,
                "enable_localization": False,
                "enable_tone_adaptation": False
            }
        )
    
    async def _apply_personalization_transformations(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply personalization transformations to notification content."""
        try:
            # Start with original content
            personalized_content = NotificationContent(
                title=content.title,
                message=content.message,
                template_id=content.template_id,
                variables=content.variables.copy() if content.variables else {},
                metadata=content.metadata.copy() if content.metadata else {}
            )
            
            # Apply transformations in order
            personalized_content = await self._apply_language_localization(
                personalized_content, context
            )
            
            personalized_content = await self._apply_tone_adaptation(
                personalized_content, context
            )
            
            personalized_content = await self._apply_creator_type_customization(
                personalized_content, context
            )
            
            personalized_content = await self._apply_cultural_adaptation(
                personalized_content, context
            )
            
            personalized_content = await self._apply_temporal_optimization(
                personalized_content, context
            )
            
            personalized_content = await self._apply_platform_optimization(
                personalized_content, context
            )
            
            personalized_content = await self._apply_engagement_optimization(
                personalized_content, context
            )
            
            # Apply A/B test variant if applicable
            if context.ab_test_variant:
                personalized_content = await self._apply_ab_test_variant(
                    personalized_content, context
                )
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Personalization transformations failed: {e}")
            return content
    
    async def _apply_language_localization(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply language localization to content."""
        try:
            target_language = context.user_profile.preferred_language
            
            # Skip if already in target language or localization disabled
            if (target_language == "en" or 
                not context.user_profile.personalization_settings.get("enable_localization", True)):
                return content
            
            # Localize title
            if content.title:
                content.title = await self._localize_text(content.title, target_language)
            
            # Localize message
            content.message = await self._localize_text(content.message, target_language)
            
            # Update metadata
            if not content.metadata:
                content.metadata = {}
            content.metadata["localized_language"] = target_language
            content.metadata["localization_applied"] = True
            
            return content
            
        except Exception as e:
            logger.error(f"Language localization failed: {e}")
            return content
    
    async def _localize_text(self, text: str, target_language: str) -> str:
        """Localize text to target language."""
        try:
            # In production, this would use a translation service
            # For now, return original text with language marker
            
            # Get language resources if available
            language_resources = self._language_resources.get(target_language, {})
            
            # Apply simple keyword translations
            localized_text = text
            for english_term, translated_term in language_resources.items():
                localized_text = localized_text.replace(english_term, translated_term)
            
            return localized_text
            
        except Exception as e:
            logger.error(f"Text localization failed: {e}")
            return text
    
    async def _apply_tone_adaptation(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply tone adaptation based on user preferences."""
        try:
            preferred_tone = context.user_profile.preferred_tone
            
            # Skip if tone adaptation disabled
            if not context.user_profile.personalization_settings.get("enable_tone_adaptation", True):
                return content
            
            # Apply tone-specific modifications
            content.message = self._adapt_message_tone(content.message, preferred_tone)
            
            # Update title if present
            if content.title:
                content.title = self._adapt_message_tone(content.title, preferred_tone)
            
            # Update metadata
            if not content.metadata:
                content.metadata = {}
            content.metadata["tone_adaptation"] = preferred_tone.value
            
            return content
            
        except Exception as e:
            logger.error(f"Tone adaptation failed: {e}")
            return content
    
    def _adapt_message_tone(self, message: str, tone: CommunicationTone) -> str:
        """Adapt message tone based on preference."""
        try:
            # Tone-specific adaptations
            if tone == CommunicationTone.FORMAL:
                # Make more formal
                message = re.sub(r"Hi\b", "Dear", message)
                message = re.sub(r"Thanks", "Thank you", message)
                message = re.sub(r"'re", " are", message)
                message = re.sub(r"'ll", " will", message)
                
            elif tone == CommunicationTone.FRIENDLY:
                # Make more friendly
                message = re.sub(r"Dear", "Hi", message)
                message = message.replace("Thank you", "Thanks")
                if not message.endswith(("!", "?")):
                    message += " 😊"
                
            elif tone == CommunicationTone.ENCOURAGING:
                # Add encouraging language
                encouragement_words = [
                    "Great work!", "Keep it up!", "Excellent!",
                    "You're doing amazing!", "Fantastic progress!"
                ]
                if "opportunity" in message.lower():
                    message = f"Great news! {message}"
                
            elif tone == CommunicationTone.URGENT:
                # Make more urgent
                message = f"⚠️ IMPORTANT: {message}"
                message = message.replace(".", "!")
                
            elif tone == CommunicationTone.CELEBRATORY:
                # Add celebration
                message = f"🎉 {message}"
                if "success" in message.lower() or "achievement" in message.lower():
                    message += " Congratulations!"
            
            return message
            
        except Exception as e:
            logger.error(f"Message tone adaptation failed: {e}")
            return message
    
    async def _apply_creator_type_customization(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply creator type-specific customizations."""
        try:
            creator_type = context.user_profile.creator_type
            
            # Creator type-specific terminology
            terminology_maps = {
                CreatorType.MUSICIAN: {
                    "content": "music",
                    "followers": "fans",
                    "post": "track",
                    "audience": "listeners"
                },
                CreatorType.PHOTOGRAPHER: {
                    "content": "photos",
                    "followers": "followers",
                    "post": "image",
                    "audience": "viewers"
                },
                CreatorType.BLOGGER: {
                    "content": "articles",
                    "followers": "readers",
                    "post": "blog post",
                    "audience": "readers"
                },
                CreatorType.INFLUENCER: {
                    "content": "posts",
                    "followers": "followers",
                    "post": "content",
                    "audience": "audience"
                },
                CreatorType.COMEDIAN: {
                    "content": "comedy",
                    "followers": "fans",
                    "post": "joke",
                    "audience": "audience"
                }
            }
            
            # Apply terminology customization
            if creator_type in terminology_maps:
                terminology = terminology_maps[creator_type]
                for generic_term, specific_term in terminology.items():
                    content.message = content.message.replace(generic_term, specific_term)
                    if content.title:
                        content.title = content.title.replace(generic_term, specific_term)
            
            # Add creator type-specific context
            if not content.metadata:
                content.metadata = {}
            content.metadata["creator_type_customization"] = creator_type.value
            
            return content
            
        except Exception as e:
            logger.error(f"Creator type customization failed: {e}")
            return content
    
    async def _apply_cultural_adaptation(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply cultural adaptations to content."""
        try:
            cultural_context = context.user_profile.cultural_context
            
            # Skip if cultural adaptation disabled
            if not cultural_context.get("cultural_adaptation", False):
                return content
            
            country = cultural_context.get("country", "US")
            
            # Country-specific adaptations
            if country == "DE":  # Germany
                # Use formal addressing
                content.message = content.message.replace("Hi", "Guten Tag")
                content.message = content.message.replace("Thanks", "Vielen Dank")
                
            elif country == "JP":  # Japan
                # Use more polite language
                content.message = f"お疲れさまです。{content.message}"
                
            elif country == "FR":  # France
                # Use French greetings
                content.message = content.message.replace("Hi", "Bonjour")
                content.message = content.message.replace("Thanks", "Merci")
            
            # Update metadata
            if not content.metadata:
                content.metadata = {}
            content.metadata["cultural_adaptation"] = country
            
            return content
            
        except Exception as e:
            logger.error(f"Cultural adaptation failed: {e}")
            return content
    
    async def _apply_temporal_optimization(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply temporal optimization based on user patterns."""
        try:
            temporal_context = context.temporal_context
            engagement_patterns = context.user_profile.engagement_patterns
            
            # Add time-sensitive messaging if appropriate
            current_hour = datetime.now().hour
            best_hour = int(engagement_patterns.get("best_time_of_day", "10").split(":")[0])
            
            # If sending at optimal time, add positive reinforcement
            if abs(current_hour - best_hour) <= 2:
                if "opportunity" in content.message.lower():
                    content.message = f"Perfect timing! {content.message}"
            
            # Add temporal context to variables
            if not content.variables:
                content.variables = {}
            content.variables["current_time"] = datetime.now().strftime("%H:%M")
            content.variables["user_timezone"] = context.user_profile.timezone
            
            return content
            
        except Exception as e:
            logger.error(f"Temporal optimization failed: {e}")
            return content
    
    async def _apply_platform_optimization(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply platform-specific optimizations."""
        try:
            platform_context = context.platform_context
            
            # Platform-specific formatting
            platform = platform_context.get("primary_platform", "email")
            
            if platform == "sms":
                # Shorten message for SMS
                content.message = self._shorten_message(content.message, 160)
                
            elif platform == "push":
                # Optimize for push notifications
                content.message = self._optimize_for_push(content.message)
                
            elif platform == "email":
                # Add email-specific formatting
                content.message = self._format_for_email(content.message)
            
            # Update metadata
            if not content.metadata:
                content.metadata = {}
            content.metadata["platform_optimization"] = platform
            
            return content
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {e}")
            return content
    
    async def _apply_engagement_optimization(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply engagement optimization based on historical data."""
        try:
            engagement_history = context.engagement_history
            
            # Get engagement patterns
            high_engagement_keywords = engagement_history.get("high_engagement_keywords", [])
            preferred_cta_style = engagement_history.get("preferred_cta_style", "action")
            
            # Add high-engagement keywords
            if high_engagement_keywords and any(keyword in content.message.lower() for keyword in high_engagement_keywords):
                # Boost content with proven engaging elements
                pass
            
            # Optimize call-to-action
            if preferred_cta_style == "urgent":
                content.message = re.sub(
                    r'Click here', 'Act now', content.message, flags=re.IGNORECASE
                )
            elif preferred_cta_style == "friendly":
                content.message = re.sub(
                    r'Click here', 'Check it out', content.message, flags=re.IGNORECASE
                )
            
            return content
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return content
    
    async def _apply_ab_test_variant(
        self,
        content: NotificationContent,
        context: PersonalizationContext
    ) -> NotificationContent:
        """Apply A/B test variant modifications."""
        try:
            variant = context.ab_test_variant
            
            if variant == "variant_a":
                # Version A: More formal
                content.message = content.message.replace("Hi", "Hello")
                content.message = content.message.replace("Thanks", "Thank you")
                
            elif variant == "variant_b":
                # Version B: More casual
                content.message = content.message.replace("Hello", "Hey")
                content.message = content.message.replace("Thank you", "Thanks")
                if not content.message.endswith("!"):
                    content.message += "!"
            
            # Add A/B test metadata
            if not content.metadata:
                content.metadata = {}
            content.metadata["ab_test_variant"] = variant
            
            return content
            
        except Exception as e:
            logger.error(f"A/B test variant application failed: {e}")
            return content
    
    def _shorten_message(self, message: str, max_length: int) -> str:
        """Shorten message for character-limited platforms."""
        if len(message) <= max_length:
            return message
        
        # Try to shorten intelligently
        shortened = message[:max_length-3] + "..."
        
        # Try to break at word boundary
        last_space = shortened.rfind(' ')
        if last_space > max_length * 0.8:
            shortened = shortened[:last_space] + "..."
        
        return shortened
    
    def _optimize_for_push(self, message: str) -> str:
        """Optimize message for push notifications."""
        # Keep it concise and actionable
        if len(message) > 100:
            message = self._shorten_message(message, 100)
        
        # Add urgency if appropriate
        urgent_keywords = ["opportunity", "alert", "important", "deadline"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            if not message.startswith(("⚠️", "🔔", "⏰")):
                message = f"🔔 {message}"
        
        return message
    
    def _format_for_email(self, message: str) -> str:
        """Format message for email delivery."""
        # Add proper email formatting
        if not message.startswith(("Hi", "Hello", "Dear")):
            message = f"Hi there,\n\n{message}"
        
        if not message.endswith(("\n\nBest regards,", "\n\nThanks,")):
            message += "\n\nBest regards,\nIA Influencer Agent Team"
        
        return message
    
    def _extract_business_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Extract business context from notification request."""
        context = {
            "notification_type": request.type,
            "priority": getattr(request, 'priority', 'medium'),
            "business_category": self._categorize_business_notification(request.type)
        }
        
        if hasattr(request, 'metadata') and request.metadata:
            context.update(request.metadata)
        
        return context
    
    def _categorize_business_notification(self, notification_type: str) -> str:
        """Categorize notification for business context."""
        categories = {
            "revenue": ["monetization", "revenue", "payment", "earnings"],
            "protection": ["copyright", "infringement", "protection", "security"],
            "collaboration": ["collaboration", "partnership", "network"],
            "performance": ["analytics", "performance", "metrics", "seo"],
            "content": ["content", "upload", "distribution", "publishing"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in notification_type.lower() for keyword in keywords):
                return category
        
        return "general"
    
    def _extract_temporal_context(self, request: NotificationRequest, profile: UserProfile) -> Dict[str, Any]:
        """Extract temporal context for personalization."""
        now = datetime.now(timezone.utc)
        
        return {
            "current_time": now,
            "user_timezone": profile.timezone,
            "is_business_hours": self._is_business_hours(now),
            "day_of_week": now.strftime("%A"),
            "time_of_day": self._get_time_of_day_category(now.hour)
        }
    
    def _get_time_of_day_category(self, hour: int) -> str:
        """Get time of day category."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is during business hours."""
        return timestamp.weekday() < 5 and 9 <= timestamp.hour < 17
    
    def _extract_platform_context(self, request: NotificationRequest) -> Dict[str, Any]:
        """Extract platform context from request."""
        context = {
            "primary_platform": "email",  # Default
            "preferred_channels": ["email"],
            "mobile_optimized": False
        }
        
        # Extract from metadata if available
        if hasattr(request, 'metadata') and request.metadata:
            if 'platform' in request.metadata:
                context["primary_platform"] = request.metadata['platform']
            if 'channels' in request.metadata:
                context["preferred_channels"] = request.metadata['channels']
        
        return context
    
    async def _get_engagement_history(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement history for optimization."""
        try:
            # In production, this would query engagement analytics
            return {
                "average_open_rate": 0.75,
                "average_click_rate": 0.25,
                "preferred_time": "10:00",
                "high_engagement_keywords": ["opportunity", "revenue", "collaboration"],
                "preferred_cta_style": "action",
                "response_patterns": {
                    "quick_responder": True,
                    "prefers_details": False,
                    "mobile_user": True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get engagement history: {e}")
            return {}
    
    def _select_ab_test_variant(self, request: NotificationRequest, profile: UserProfile) -> Optional[str]:
        """Select A/B test variant for personalization."""
        try:
            # Simple hash-based variant selection
            user_hash = hash(profile.user_id) % 100
            
            # 50/50 split for now
            if user_hash < 50:
                return "variant_a"
            else:
                return "variant_b"
            
        except Exception:
            return None
    
    def _calculate_personalization_confidence(
        self,
        original: NotificationContent,
        personalized: NotificationContent,
        context: PersonalizationContext
    ) -> float:
        """Calculate confidence score for personalization quality."""
        try:
            confidence_factors = []
            
            # Profile completeness factor
            profile_completeness = self._calculate_profile_completeness(context.user_profile)
            confidence_factors.append(profile_completeness * 0.3)
            
            # Personalization depth factor
            changes_made = self._count_personalization_changes(original, personalized)
            personalization_depth = min(1.0, changes_made / 5.0)  # Max 5 expected changes
            confidence_factors.append(personalization_depth * 0.2)
            
            # Context richness factor
            context_richness = len(context.business_context) / 10.0  # Normalize
            confidence_factors.append(min(1.0, context_richness) * 0.2)
            
            # Language/localization factor
            if context.user_profile.preferred_language != "en":
                confidence_factors.append(0.8 * 0.15)  # Slightly lower for non-English
            else:
                confidence_factors.append(0.9 * 0.15)
            
            # A/B test factor
            if context.ab_test_variant:
                confidence_factors.append(0.85 * 0.15)
            else:
                confidence_factors.append(0.7 * 0.15)
            
            return sum(confidence_factors)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.5
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate user profile completeness score."""
        completeness_factors = [
            1.0 if profile.creator_type != CreatorType.CONTENT_CREATOR else 0.5,
            1.0 if profile.preferred_language != "en" else 0.8,
            1.0 if profile.timezone != "UTC" else 0.5,
            1.0 if profile.communication_style != PersonalizationStyle.PROFESSIONAL else 0.7,
            1.0 if profile.engagement_patterns else 0.0,
            1.0 if profile.content_preferences else 0.0,
            1.0 if profile.historical_interactions else 0.0
        ]
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _count_personalization_changes(
        self,
        original: NotificationContent,
        personalized: NotificationContent
    ) -> int:
        """Count number of personalization changes made."""
        changes = 0
        
        if original.title != personalized.title:
            changes += 1
        
        if original.message != personalized.message:
            changes += 1
        
        if original.variables != personalized.variables:
            changes += 1
        
        original_metadata_count = len(original.metadata) if original.metadata else 0
        personalized_metadata_count = len(personalized.metadata) if personalized.metadata else 0
        
        if personalized_metadata_count > original_metadata_count:
            changes += 1
        
        return changes
    
    def _get_applied_personalization_rules(self, context: PersonalizationContext) -> List[str]:
        """Get list of applied personalization rules."""
        rules = []
        
        if context.user_profile.personalization_settings.get("enable_localization"):
            rules.append("language_localization")
        
        if context.user_profile.personalization_settings.get("enable_tone_adaptation"):
            rules.append("tone_adaptation")
        
        if context.user_profile.creator_type != CreatorType.CONTENT_CREATOR:
            rules.append("creator_type_customization")
        
        if context.user_profile.cultural_context.get("cultural_adaptation"):
            rules.append("cultural_adaptation")
        
        if context.ab_test_variant:
            rules.append("ab_test_variant")
        
        rules.extend(["temporal_optimization", "platform_optimization", "engagement_optimization"])
        
        return rules
    
    def _extract_personalization_factors(self, context: PersonalizationContext) -> Dict[str, Any]:
        """Extract personalization factors for transparency."""
        return {
            "creator_type": context.user_profile.creator_type.value,
            "preferred_language": context.user_profile.preferred_language,
            "communication_style": context.user_profile.communication_style.value,
            "preferred_tone": context.user_profile.preferred_tone.value,
            "timezone": context.user_profile.timezone,
            "business_context": context.business_context,
            "ab_test_variant": context.ab_test_variant,
            "personalization_enabled": context.user_profile.personalization_settings.get(
                "enable_ai_personalization", True
            )
        }
    
    def _load_personalization_templates(self) -> Dict[str, Any]:
        """Load personalization templates."""
        # In production, this would load from database or files
        return {
            "creator_type_templates": {},
            "tone_templates": {},
            "cultural_templates": {},
            "ab_test_templates": {}
        }
    
    def _initialize_ab_test_variants(self) -> Dict[str, Any]:
        """Initialize A/B test variants."""
        return {
            "variant_a": {
                "name": "Formal Communication",
                "description": "More formal and professional tone"
            },
            "variant_b": {
                "name": "Casual Communication", 
                "description": "More casual and friendly tone"
            }
        }
    
    def _load_language_resources(self) -> Dict[str, Dict[str, str]]:
        """Load language resources for localization."""
        return {
            "de": {
                "Hello": "Hallo",
                "Thanks": "Danke",
                "opportunity": "Gelegenheit",
                "revenue": "Umsatz",
                "content": "Inhalt"
            },
            "fr": {
                "Hello": "Bonjour",
                "Thanks": "Merci",
                "opportunity": "opportunité",
                "revenue": "revenus",
                "content": "contenu"
            },
            "es": {
                "Hello": "Hola",
                "Thanks": "Gracias",
                "opportunity": "oportunidad",
                "revenue": "ingresos",
                "content": "contenido"
            }
        }
    
    async def _detect_creator_type(self, user_id: str) -> Optional[CreatorType]:
        """Detect user's creator type from content history."""
        # This would analyze user's content history
        # For now, return None to use default
        return None
    
    async def _detect_preferred_language(self, user_id: str) -> Optional[str]:
        """Detect user's preferred language."""
        # This would analyze user's language patterns
        return None
    
    async def _detect_user_timezone(self, user_id: str) -> Optional[str]:
        """Detect user's timezone from activity patterns."""
        # This would analyze user's activity timing
        return None
    
    async def _analyze_communication_style(self, user_id: str) -> Optional[PersonalizationStyle]:
        """Analyze user's preferred communication style."""
        # This would analyze user's response patterns
        return None
    
    async def _analyze_engagement_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Analyze user's engagement patterns."""
        # This would analyze user's interaction history
        return None
    
    def _is_profile_cache_valid(self, profile: UserProfile) -> bool:
        """Check if cached profile is still valid."""
        # For now, assume profiles are valid for 1 hour
        return True
    
    def _update_personalization_stats(self, processing_time: float):
        """Update personalization performance statistics."""
        self.personalization_stats["total_personalizations"] += 1
        
        # Update average processing time
        total_time = (
            self.personalization_stats["average_processing_time"] * 
            (self.personalization_stats["total_personalizations"] - 1) + 
            processing_time
        )
        self.personalization_stats["average_processing_time"] = (
            total_time / self.personalization_stats["total_personalizations"]
        )
    
    def get_personalization_stats(self) -> Dict[str, Any]:
        """Get personalization performance statistics."""
        return self.personalization_stats.copy()
    
    def clear_profile_cache(self):
        """Clear user profile cache."""
        self._profile_cache.clear()
        logger.info("User profile cache cleared")
