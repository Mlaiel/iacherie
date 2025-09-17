#!/usr/bin/env python3
"""
🤖 Enterprise Notification Personalization Engine - Ainflue Platform Core
AI-driven notification personalization with ML content optimization

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import openai
import anthropic
import aiohttp

class PersonalizationStrategy(Enum):
    """Personalization strategies"""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    CONTEXTUAL = "contextual"

class ContentType(Enum):
    """Content types for personalization"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    MIXED_MEDIA = "mixed_media"

class PersonalizationLevel(Enum):
    """Personalization intensity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"

class UserSegment(Enum):
    """User segments for targeting"""
    NEW_USER = "new_user"
    ACTIVE_USER = "active_user"
    POWER_USER = "power_user"
    CHURNING_USER = "churning_user"
    VIP_USER = "vip_user"
    CREATOR = "creator"
    BRAND = "brand"

@dataclass
class UserProfile:
    """Comprehensive user profile for personalization"""
    user_id: str
    demographics: Dict[str, Any]
    preferences: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    engagement_history: List[Dict[str, Any]]
    content_preferences: Dict[str, float]
    channel_preferences: Dict[str, float]
    timezone: str
    language: str
    segment: UserSegment
    created_at: datetime
    updated_at: datetime

@dataclass
class ContentVariant:
    """Content variant for A/B testing"""
    id: str
    content: str
    variant_type: str
    target_segments: List[UserSegment]
    personalization_features: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: datetime

@dataclass
class PersonalizationResult:
    """Result of personalization process"""
    user_id: str
    original_content: str
    personalized_content: str
    strategy_used: PersonalizationStrategy
    confidence_score: float
    personalization_features: Dict[str, Any]
    variant_id: Optional[str]
    processing_time: float
    timestamp: datetime

class NotificationPersonalizationEngine:
    """Enterprise notification personalization engine with AI optimization"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # AI service clients
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        
        # ML models
        self.content_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.user_clustering_model = KMeans(n_clusters=8, random_state=42)
        self.scaler = StandardScaler()
        
        # Model training status
        self.is_content_model_trained = False
        self.is_user_model_trained = False
        
        # User profiles cache
        self.user_profiles: Dict[str, UserProfile] = {}
        self.content_variants: Dict[str, List[ContentVariant]] = {}
        
        # Language support
        self.supported_languages = {
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ar': 'Arabic',
            'zh': 'Chinese'
        }
        
        # Performance metrics
        self.metrics = {
            'personalizations_processed': 0,
            'ai_generations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'model_predictions': 0,
            'content_variants_created': 0,
            'user_profiles_updated': 0
        }

    async def initialize(self):
        """Initialize personalization engine"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ Personalization engine initialized with Redis connection")
            
            # Load existing models
            await self._load_ml_models()
            
            # Load user profiles
            await self._load_user_profiles()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize personalization engine: {e}")
            raise

    async def personalize_notification(
        self,
        user_id: str,
        original_content: str,
        content_type: ContentType = ContentType.TEXT,
        strategy: PersonalizationStrategy = PersonalizationStrategy.HYBRID,
        level: PersonalizationLevel = PersonalizationLevel.STANDARD
    ) -> PersonalizationResult:
        """
        Personalize notification content for specific user
        
        Args:
            user_id: Target user identifier
            original_content: Original notification content
            content_type: Type of content to personalize
            strategy: Personalization strategy to use
            level: Intensity level of personalization
            
        Returns:
            PersonalizationResult with personalized content
        """
        start_time = time.time()
        self.metrics['personalizations_processed'] += 1
        
        try:
            # Get or create user profile
            user_profile = await self._get_user_profile(user_id)
            
            # Determine best personalization strategy
            if strategy == PersonalizationStrategy.HYBRID:
                strategy = await self._determine_optimal_strategy(user_profile, content_type)
            
            # Apply personalization strategy
            personalized_content = await self._apply_personalization_strategy(
                user_profile, original_content, strategy, level, content_type
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                user_profile, original_content, personalized_content, strategy
            )
            
            # Extract personalization features
            features = await self._extract_personalization_features(
                user_profile, original_content, personalized_content
            )
            
            # Create result
            result = PersonalizationResult(
                user_id=user_id,
                original_content=original_content,
                personalized_content=personalized_content,
                strategy_used=strategy,
                confidence_score=confidence_score,
                personalization_features=features,
                variant_id=None,  # Set if using A/B testing
                processing_time=time.time() - start_time,
                timestamp=datetime.utcnow()
            )
            
            # Store result for learning
            await self._store_personalization_result(result)
            
            # Update user profile with interaction
            await self._update_user_profile_interaction(user_id, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Personalization failed for user {user_id}: {e}")
            
            # Return original content on failure
            return PersonalizationResult(
                user_id=user_id,
                original_content=original_content,
                personalized_content=original_content,
                strategy_used=strategy,
                confidence_score=0.0,
                personalization_features={},
                variant_id=None,
                processing_time=time.time() - start_time,
                timestamp=datetime.utcnow()
            )

    async def _determine_optimal_strategy(
        self,
        user_profile: UserProfile,
        content_type: ContentType
    ) -> PersonalizationStrategy:
        """Determine optimal personalization strategy for user"""
        
        # New users: demographic-based
        if user_profile.segment == UserSegment.NEW_USER:
            return PersonalizationStrategy.DEMOGRAPHIC
        
        # Users with rich interaction history: collaborative
        if len(user_profile.engagement_history) > 50:
            return PersonalizationStrategy.COLLABORATIVE
        
        # Content creators: content-based
        if user_profile.segment == UserSegment.CREATOR:
            return PersonalizationStrategy.CONTENT_BASED
        
        # High-value users: behavioral
        if user_profile.segment in [UserSegment.VIP_USER, UserSegment.POWER_USER]:
            return PersonalizationStrategy.BEHAVIORAL
        
        # Default: contextual
        return PersonalizationStrategy.CONTEXTUAL

    async def _apply_personalization_strategy(
        self,
        user_profile: UserProfile,
        content: str,
        strategy: PersonalizationStrategy,
        level: PersonalizationLevel,
        content_type: ContentType
    ) -> str:
        """Apply specific personalization strategy"""
        
        if strategy == PersonalizationStrategy.CONTENT_BASED:
            return await self._personalize_content_based(user_profile, content, level)
            
        elif strategy == PersonalizationStrategy.COLLABORATIVE:
            return await self._personalize_collaborative(user_profile, content, level)
            
        elif strategy == PersonalizationStrategy.BEHAVIORAL:
            return await self._personalize_behavioral(user_profile, content, level)
            
        elif strategy == PersonalizationStrategy.DEMOGRAPHIC:
            return await self._personalize_demographic(user_profile, content, level)
            
        elif strategy == PersonalizationStrategy.CONTEXTUAL:
            return await self._personalize_contextual(user_profile, content, level)
        
        return content

    async def _personalize_content_based(
        self,
        user_profile: UserProfile,
        content: str,
        level: PersonalizationLevel
    ) -> str:
        """Content-based personalization using content similarity"""
        
        if not self.is_content_model_trained:
            return content
        
        try:
            # Get user's content preferences
            user_interests = user_profile.content_preferences
            
            # Find similar content patterns
            similar_content = await self._find_similar_content(content, user_interests)
            
            if level == PersonalizationLevel.BASIC:
                # Simple keyword replacement
                return await self._apply_keyword_personalization(content, user_interests)
                
            elif level == PersonalizationLevel.STANDARD:
                # Content tone adjustment
                return await self._adjust_content_tone(content, user_profile)
                
            elif level in [PersonalizationLevel.ADVANCED, PersonalizationLevel.PREMIUM]:
                # AI-powered content generation
                return await self._generate_ai_personalized_content(content, user_profile)
        
        except Exception as e:
            self.logger.error(f"❌ Content-based personalization failed: {e}")
            return content

    async def _personalize_collaborative(
        self,
        user_profile: UserProfile,
        content: str,
        level: PersonalizationLevel
    ) -> str:
        """Collaborative filtering personalization"""
        
        try:
            # Find similar users
            similar_users = await self._find_similar_users(user_profile)
            
            if not similar_users:
                return content
            
            # Get content preferences from similar users
            collaborative_preferences = await self._aggregate_collaborative_preferences(similar_users)
            
            # Apply collaborative insights
            if level == PersonalizationLevel.BASIC:
                return await self._apply_popularity_bias(content, collaborative_preferences)
                
            elif level == PersonalizationLevel.STANDARD:
                return await self._apply_collaborative_tone(content, collaborative_preferences)
                
            else:  # Advanced/Premium
                return await self._generate_collaborative_content(content, collaborative_preferences, user_profile)
        
        except Exception as e:
            self.logger.error(f"❌ Collaborative personalization failed: {e}")
            return content

    async def _personalize_behavioral(
        self,
        user_profile: UserProfile,
        content: str,
        level: PersonalizationLevel
    ) -> str:
        """Behavioral pattern-based personalization"""
        
        try:
            # Analyze user behavior patterns
            behavior_insights = await self._analyze_behavior_patterns(user_profile)
            
            # Determine optimal timing and format
            optimal_format = behavior_insights.get('preferred_format', 'standard')
            engagement_triggers = behavior_insights.get('engagement_triggers', [])
            
            # Apply behavioral insights
            personalized_content = content
            
            # Add engagement triggers
            if engagement_triggers and level != PersonalizationLevel.BASIC:
                personalized_content = await self._add_engagement_triggers(
                    personalized_content, engagement_triggers
                )
            
            # Adjust format based on behavior
            if level in [PersonalizationLevel.ADVANCED, PersonalizationLevel.PREMIUM]:
                personalized_content = await self._adjust_content_format(
                    personalized_content, optimal_format, user_profile
                )
            
            return personalized_content
        
        except Exception as e:
            self.logger.error(f"❌ Behavioral personalization failed: {e}")
            return content

    async def _personalize_demographic(
        self,
        user_profile: UserProfile,
        content: str,
        level: PersonalizationLevel
    ) -> str:
        """Demographic-based personalization"""
        
        try:
            demographics = user_profile.demographics
            
            # Language localization
            if demographics.get('language') != 'en':
                content = await self._translate_content(content, demographics.get('language', 'en'))
            
            # Age-appropriate content
            age_group = demographics.get('age_group', 'adult')
            content = await self._adjust_content_for_age(content, age_group)
            
            # Cultural adaptation
            if level in [PersonalizationLevel.ADVANCED, PersonalizationLevel.PREMIUM]:
                culture = demographics.get('culture', 'western')
                content = await self._adapt_content_culturally(content, culture)
            
            # Gender-neutral language (if preferred)
            if demographics.get('gender_neutral_preference', False):
                content = await self._apply_gender_neutral_language(content)
            
            return content
        
        except Exception as e:
            self.logger.error(f"❌ Demographic personalization failed: {e}")
            return content

    async def _personalize_contextual(
        self,
        user_profile: UserProfile,
        content: str,
        level: PersonalizationLevel
    ) -> str:
        """Contextual personalization based on current situation"""
        
        try:
            # Get current context
            current_time = datetime.utcnow()
            user_timezone = user_profile.timezone
            
            # Time-based personalization
            local_time = await self._convert_to_user_timezone(current_time, user_timezone)
            content = await self._add_time_context(content, local_time)
            
            # Device/channel context
            preferred_channel = max(user_profile.channel_preferences.items(), key=lambda x: x[1])[0]
            content = await self._optimize_for_channel(content, preferred_channel)
            
            # Recent activity context
            if level != PersonalizationLevel.BASIC:
                recent_activity = user_profile.engagement_history[-5:] if user_profile.engagement_history else []
                content = await self._add_activity_context(content, recent_activity)
            
            return content
        
        except Exception as e:
            self.logger.error(f"❌ Contextual personalization failed: {e}")
            return content

    async def _generate_ai_personalized_content(
        self,
        content: str,
        user_profile: UserProfile
    ) -> str:
        """Generate AI-powered personalized content"""
        
        self.metrics['ai_generations'] += 1
        
        # Try OpenAI first, fallback to Anthropic
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are an expert notification personalization AI. 
                            Personalize the given notification for a user with these characteristics:
                            - Language: {user_profile.language}
                            - Segment: {user_profile.segment.value}
                            - Interests: {', '.join(user_profile.content_preferences.keys())}
                            - Timezone: {user_profile.timezone}
                            
                            Keep the core message intact but adapt tone, style, and examples to match the user's profile.
                            Make it engaging and relevant."""
                        },
                        {
                            "role": "user", 
                            "content": f"Original notification: {content}"
                        }
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                self.logger.error(f"❌ OpenAI personalization failed: {e}")
        
        # Fallback to Anthropic
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=200,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Personalize this notification for a {user_profile.segment.value} user who speaks {user_profile.language}:
                            
                            Original: {content}
                            
                            User interests: {', '.join(user_profile.content_preferences.keys())}
                            
                            Make it engaging and relevant while keeping the core message."""
                        }
                    ]
                )
                
                return response.content[0].text.strip()
                
            except Exception as e:
                self.logger.error(f"❌ Anthropic personalization failed: {e}")
        
        # Final fallback: rule-based personalization
        return await self._apply_rule_based_personalization(content, user_profile)

    async def _apply_rule_based_personalization(
        self,
        content: str,
        user_profile: UserProfile
    ) -> str:
        """Apply rule-based personalization as fallback"""
        
        personalized = content
        
        # Add user's name if available
        if 'name' in user_profile.demographics:
            name = user_profile.demographics['name']
            if not any(greeting in personalized.lower() for greeting in ['hi ', 'hello ', 'hey ']):
                personalized = f"Hi {name}! {personalized}"
        
        # Add segment-specific language
        if user_profile.segment == UserSegment.CREATOR:
            personalized = personalized.replace("your content", "your amazing content")
        elif user_profile.segment == UserSegment.VIP_USER:
            personalized = f"🌟 VIP Alert: {personalized}"
        
        # Add time-sensitive language
        current_hour = datetime.utcnow().hour
        if 5 <= current_hour < 12:
            personalized = personalized.replace("Hello", "Good morning")
        elif 12 <= current_hour < 17:
            personalized = personalized.replace("Hello", "Good afternoon")
        elif 17 <= current_hour < 22:
            personalized = personalized.replace("Hello", "Good evening")
        
        return personalized

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        
        # Check cache first
        if user_id in self.user_profiles:
            self.metrics['cache_hits'] += 1
            return self.user_profiles[user_id]
        
        self.metrics['cache_misses'] += 1
        
        # Try to load from Redis
        profile_data = await self.redis_client.get(f"user_profile:{user_id}")
        
        if profile_data:
            profile_dict = json.loads(profile_data)
            profile = UserProfile(**profile_dict)
            self.user_profiles[user_id] = profile
            return profile
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            demographics={},
            preferences={},
            behavior_patterns={},
            engagement_history=[],
            content_preferences={},
            channel_preferences={'email': 0.5, 'push': 0.3, 'sms': 0.2},
            timezone='UTC',
            language='en',
            segment=UserSegment.NEW_USER,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in cache and Redis
        self.user_profiles[user_id] = profile
        await self._save_user_profile(profile)
        
        return profile

    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to Redis"""
        try:
            profile_dict = asdict(profile)
            # Convert datetime objects to ISO strings
            profile_dict['created_at'] = profile.created_at.isoformat()
            profile_dict['updated_at'] = profile.updated_at.isoformat()
            
            await self.redis_client.setex(
                f"user_profile:{profile.user_id}",
                86400 * 30,  # 30 days
                json.dumps(profile_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to save user profile: {e}")

    async def _find_similar_users(self, user_profile: UserProfile) -> List[str]:
        """Find users with similar preferences"""
        
        if not self.is_user_model_trained:
            return []
        
        try:
            # Create feature vector for current user
            user_features = self._create_user_feature_vector(user_profile)
            
            # Find similar users using clustering
            cluster_id = self.user_clustering_model.predict([user_features])[0]
            
            # Get other users in the same cluster
            similar_users = await self.redis_client.smembers(f"user_cluster:{cluster_id}")
            
            # Remove current user and return sample
            similar_users.discard(user_profile.user_id)
            return list(similar_users)[:10]  # Limit to 10 similar users
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find similar users: {e}")
            return []

    def _create_user_feature_vector(self, profile: UserProfile) -> List[float]:
        """Create numerical feature vector for user"""
        
        features = []
        
        # Demographic features
        age = profile.demographics.get('age', 30) / 100.0  # Normalize
        features.append(age)
        
        # Engagement features
        features.append(len(profile.engagement_history) / 1000.0)  # Normalize
        
        # Preference features
        content_prefs = list(profile.content_preferences.values())[:5]  # Top 5
        while len(content_prefs) < 5:
            content_prefs.append(0.0)
        features.extend(content_prefs)
        
        # Channel preferences
        features.extend(list(profile.channel_preferences.values()))
        
        # Behavioral features
        features.append(profile.behavior_patterns.get('activity_score', 0.5))
        features.append(profile.behavior_patterns.get('engagement_rate', 0.5))
        
        return features

    async def create_content_variants(
        self,
        base_content: str,
        target_segments: List[UserSegment],
        variant_count: int = 3
    ) -> List[ContentVariant]:
        """Create multiple content variants for A/B testing"""
        
        variants = []
        
        for i in range(variant_count):
            variant_id = str(uuid.uuid4())
            
            # Generate variant using AI
            variant_content = await self._generate_content_variant(
                base_content, target_segments, i
            )
            
            variant = ContentVariant(
                id=variant_id,
                content=variant_content,
                variant_type=f"variant_{i+1}",
                target_segments=target_segments,
                personalization_features={
                    'tone': ['professional', 'casual', 'friendly'][i % 3],
                    'length': ['short', 'medium', 'long'][i % 3],
                    'style': ['direct', 'persuasive', 'informative'][i % 3]
                },
                performance_metrics={},
                created_at=datetime.utcnow()
            )
            
            variants.append(variant)
            self.metrics['content_variants_created'] += 1
        
        # Store variants
        content_hash = hashlib.md5(base_content.encode()).hexdigest()
        self.content_variants[content_hash] = variants
        
        await self._save_content_variants(content_hash, variants)
        
        return variants

    async def _generate_content_variant(
        self,
        base_content: str,
        target_segments: List[UserSegment],
        variant_index: int
    ) -> str:
        """Generate a content variant"""
        
        variant_styles = [
            "Make it more professional and formal",
            "Make it casual and friendly", 
            "Make it urgent and action-oriented"
        ]
        
        style = variant_styles[variant_index % len(variant_styles)]
        
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a content optimization AI. {style}. Keep the core message but adapt the tone and style. Target segments: {', '.join([s.value for s in target_segments])}"
                        },
                        {
                            "role": "user",
                            "content": f"Original content: {base_content}"
                        }
                    ],
                    max_tokens=150,
                    temperature=0.8
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception:
                pass
        
        # Fallback: simple rule-based variants
        if variant_index == 0:
            return f"Dear valued user, {base_content}"
        elif variant_index == 1:
            return f"Hey there! {base_content} 😊"
        else:
            return f"⚡ URGENT: {base_content} - Act now!"

    async def get_personalization_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get personalization analytics for user"""
        
        analytics = {
            'user_id': user_id,
            'total_personalizations': 0,
            'strategies_used': {},
            'confidence_scores': [],
            'processing_times': [],
            'recent_results': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get personalization history
        history_key = f"personalization_history:{user_id}"
        history = await self.redis_client.lrange(history_key, 0, 99)  # Last 100
        
        for result_data in history:
            try:
                result = json.loads(result_data)
                analytics['total_personalizations'] += 1
                
                strategy = result['strategy_used']
                analytics['strategies_used'][strategy] = analytics['strategies_used'].get(strategy, 0) + 1
                
                analytics['confidence_scores'].append(result['confidence_score'])
                analytics['processing_times'].append(result['processing_time'])
                
                if len(analytics['recent_results']) < 10:
                    analytics['recent_results'].append(result)
                    
            except Exception:
                continue
        
        # Calculate averages
        if analytics['confidence_scores']:
            analytics['avg_confidence'] = sum(analytics['confidence_scores']) / len(analytics['confidence_scores'])
            analytics['avg_processing_time'] = sum(analytics['processing_times']) / len(analytics['processing_times'])
        else:
            analytics['avg_confidence'] = 0.0
            analytics['avg_processing_time'] = 0.0
        
        return analytics

    async def update_user_engagement(
        self,
        user_id: str,
        notification_id: str,
        engagement_type: str,
        engagement_data: Dict[str, Any]
    ):
        """Update user engagement data for learning"""
        
        try:
            # Get user profile
            profile = await self._get_user_profile(user_id)
            
            # Add engagement record
            engagement_record = {
                'notification_id': notification_id,
                'type': engagement_type,
                'data': engagement_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            profile.engagement_history.append(engagement_record)
            
            # Keep only recent history
            if len(profile.engagement_history) > 1000:
                profile.engagement_history = profile.engagement_history[-1000:]
            
            # Update behavior patterns
            await self._update_behavior_patterns(profile, engagement_record)
            
            # Update content preferences
            await self._update_content_preferences(profile, engagement_record)
            
            # Update user segment if needed
            await self._update_user_segment(profile)
            
            # Save updated profile
            profile.updated_at = datetime.utcnow()
            await self._save_user_profile(profile)
            
            self.metrics['user_profiles_updated'] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update user engagement: {e}")

    async def _update_behavior_patterns(self, profile: UserProfile, engagement: Dict[str, Any]):
        """Update user behavior patterns based on engagement"""
        
        engagement_type = engagement['type']
        
        # Update engagement rate
        recent_engagements = profile.engagement_history[-100:]  # Last 100
        positive_engagements = len([e for e in recent_engagements if e['type'] in ['click', 'view', 'action']])
        profile.behavior_patterns['engagement_rate'] = positive_engagements / len(recent_engagements) if recent_engagements else 0.0
        
        # Update activity patterns
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in recent_engagements]
        if timestamps:
            # Calculate activity score based on recency and frequency
            recent_activity = len([ts for ts in timestamps if ts > datetime.utcnow() - timedelta(days=7)])
            profile.behavior_patterns['activity_score'] = min(1.0, recent_activity / 50.0)  # Normalize to 0-1
        
        # Update time preferences
        if timestamps:
            hours = [ts.hour for ts in timestamps]
            most_active_hour = max(set(hours), key=hours.count) if hours else 12
            profile.behavior_patterns['preferred_hour'] = most_active_hour

    async def _update_content_preferences(self, profile: UserProfile, engagement: Dict[str, Any]):
        """Update content preferences based on engagement"""
        
        engagement_data = engagement.get('data', {})
        content_tags = engagement_data.get('content_tags', [])
        
        if not content_tags:
            return
        
        # Update preferences based on engagement type
        weight = {
            'click': 1.0,
            'view': 0.5,
            'dismiss': -0.5,
            'unsubscribe': -2.0
        }.get(engagement['type'], 0.0)
        
        for tag in content_tags:
            current_score = profile.content_preferences.get(tag, 0.0)
            # Apply exponential moving average
            profile.content_preferences[tag] = 0.9 * current_score + 0.1 * weight

    async def _update_user_segment(self, profile: UserProfile):
        """Update user segment based on behavior"""
        
        engagement_rate = profile.behavior_patterns.get('engagement_rate', 0.0)
        activity_score = profile.behavior_patterns.get('activity_score', 0.0)
        total_engagements = len(profile.engagement_history)
        
        # Determine segment
        if total_engagements < 10:
            profile.segment = UserSegment.NEW_USER
        elif engagement_rate > 0.8 and activity_score > 0.7:
            profile.segment = UserSegment.POWER_USER
        elif engagement_rate > 0.6:
            profile.segment = UserSegment.ACTIVE_USER
        elif engagement_rate < 0.2 and activity_score < 0.3:
            profile.segment = UserSegment.CHURNING_USER
        else:
            profile.segment = UserSegment.ACTIVE_USER

    async def get_metrics(self) -> Dict[str, Any]:
        """Get personalization engine metrics"""
        
        return {
            **self.metrics,
            'user_profiles_cached': len(self.user_profiles),
            'content_variants_stored': len(self.content_variants),
            'models_trained': {
                'content_model': self.is_content_model_trained,
                'user_model': self.is_user_model_trained
            },
            'supported_languages': len(self.supported_languages),
            'ai_services_available': {
                'openai': self.openai_client is not None,
                'anthropic': self.anthropic_client is not None
            }
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("✅ Personalization engine cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_personalization_engine():
        """Test personalization engine functionality"""
        
        # Initialize engine
        engine = NotificationPersonalizationEngine()
        await engine.initialize()
        
        # Test personalization
        result = await engine.personalize_notification(
            user_id="user123",
            original_content="You have a new message waiting for you.",
            strategy=PersonalizationStrategy.HYBRID,
            level=PersonalizationLevel.ADVANCED
        )
        
        print(f"Original: {result.original_content}")
        print(f"Personalized: {result.personalized_content}")
        print(f"Strategy: {result.strategy_used.value}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Processing time: {result.processing_time:.3f}s")
        
        # Test content variants
        variants = await engine.create_content_variants(
            "Check out our new feature!",
            [UserSegment.ACTIVE_USER, UserSegment.CREATOR],
            variant_count=3
        )
        
        print(f"\nContent variants:")
        for i, variant in enumerate(variants):
            print(f"Variant {i+1}: {variant.content}")
        
        # Get analytics
        analytics = await engine.get_personalization_analytics("user123")
        print(f"\nAnalytics: {json.dumps(analytics, indent=2)}")
        
        # Get metrics
        metrics = await engine.get_metrics()
        print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
        
        await engine.cleanup()
    
    # Run test
    asyncio.run(test_personalization_engine())