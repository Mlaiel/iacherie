"""Advanced User Profiler - Ultra-Advanced Implementation
AI-Powered User Behavior Analysis and Profiling System

This module provides comprehensive user profiling capabilities including
behavioral analysis, interest prediction, demographic inference, and personalization insights.
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
import numpy as np
import re
from collections import defaultdict, Counter

from .base import BaseCrawler
from ..utils.rate_limiter import RateLimiter
from ..utils.cache import CacheManager
from ..utils.encryption import ContentEncryption

logger = logging.getLogger(__name__)


class UserType(str, Enum):
    """Types of user profiles"""    CONSUMER = "consumer"
    CREATOR = "creator"
    INFLUENCER = "influencer"
    BUSINESS = "business"
    BRAND = "brand"
    CELEBRITY = "celebrity"
    JOURNALIST = "journalist"
    ACTIVIST = "activist"
    EXPERT = "expert"
    BOT = "bot"


class EngagementPattern(str, Enum):
    """User engagement patterns"""    PASSIVE = "passive"
    ACTIVE = "active"
    HIGHLY_ACTIVE = "highly_active"
    SPORADIC = "sporadic"
    CONSISTENT = "consistent"
    BURST = "burst"
    LURKER = "lurker"
    CONTRIBUTOR = "contributor"


class PersonalityTrait(str, Enum):
    """Personality traits for analysis"""    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"
    OPTIMISM = "optimism"
    CREATIVITY = "creativity"
    LEADERSHIP = "leadership"


class InterestCategory(str, Enum):
    """Categories of user interests"""    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    HEALTH = "health"
    FINANCE = "finance"
    EDUCATION = "education"
    POLITICS = "politics"
    SCIENCE = "science"
    ART = "art"
    MUSIC = "music"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"


class ContentPreference(BaseModel):
    """User content preferences"""    preferred_content_types: List[str] = Field(default_factory=list)
    preferred_formats: List[str] = Field(default_factory=list)
    preferred_length: str = "medium"  # "short", "medium", "long"
    preferred_tone: str = "neutral"  # "formal", "casual", "humorous", "serious"
    
    # Visual preferences
    preferred_colors: List[str] = Field(default_factory=list)
    preferred_imagery: List[str] = Field(default_factory=list)
    
    # Timing preferences
    active_hours: List[int] = Field(default_factory=list)
    active_days: List[str] = Field(default_factory=list)
    timezone: str = "UTC"
    
    # Engagement preferences
    interaction_style: str = "moderate"  # "minimal", "moderate", "high"
    response_preference: str = "quick"  # "immediate", "quick", "delayed"


class DemographicProfile(BaseModel):
    """Inferred demographic information"""    age_range: Optional[str] = None  # "18-24", "25-34", etc.
    gender: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    location_timezone: Optional[str] = None
    
    # Professional information
    industry: Optional[str] = None
    job_title: Optional[str] = None
    education_level: Optional[str] = None
    income_bracket: Optional[str] = None
    
    # Lifestyle indicators
    relationship_status: Optional[str] = None
    family_status: Optional[str] = None
    lifestyle_category: Optional[str] = None
    
    # Confidence scores for inferences
    age_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    gender_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    location_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    professional_confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class BehaviorMetrics(BaseModel):
    """User behavior analysis metrics"""    # Activity patterns
    total_posts: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_likes_given: int = 0
    total_likes_received: int = 0
    
    # Timing patterns
    avg_posts_per_day: float = 0.0
    avg_session_duration: float = 0.0  # minutes
    peak_activity_hour: Optional[int] = None
    most_active_day: Optional[str] = None
    
    # Engagement quality
    avg_engagement_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    response_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    conversation_initiation_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    
    # Content characteristics
    avg_content_length: float = 0.0
    hashtag_usage_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    mention_usage_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    media_sharing_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    
    # Social patterns
    follower_following_ratio: float = 0.0
    network_diversity_score: float = Field(ge=0.0, le=1.0, default=0.0)
    influence_score: float = Field(ge=0.0, le=1.0, default=0.0)


class InterestProfile(BaseModel):
    """User interest and preference profile"""    primary_interests: List[Tuple[InterestCategory, float]] = Field(default_factory=list)
    secondary_interests: List[Tuple[InterestCategory, float]] = Field(default_factory=list)
    
    # Topic modeling
    discovered_topics: List[Dict[str, Any]] = Field(default_factory=list)
    topic_evolution: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Brand affinity
    preferred_brands: List[Dict[str, Any]] = Field(default_factory=list)
    brand_sentiment: Dict[str, float] = Field(default_factory=dict)
    
    # Content consumption patterns
    content_preferences: ContentPreference
    
    # Seasonal/temporal interests
    seasonal_interests: Dict[str, List[str]] = Field(default_factory=dict)
    trending_interests: List[str] = Field(default_factory=list)


class PersonalityProfile(BaseModel):
    """User personality analysis"""    big_five_scores: Dict[PersonalityTrait, float] = Field(default_factory=dict)
    
    # Communication style
    communication_style: str = "balanced"  # "formal", "casual", "technical", "emotional"
    vocabulary_complexity: float = Field(ge=0.0, le=1.0, default=0.5)
    emotional_expression: float = Field(ge=0.0, le=1.0, default=0.5)
    
    # Social behavior
    social_orientation: str = "ambivert"  # "introvert", "extrovert", "ambivert"
    risk_tolerance: float = Field(ge=0.0, le=1.0, default=0.5)
    innovation_adoption: str = "mainstream"  # "early_adopter", "mainstream", "laggard"
    
    # Decision making
    decision_style: str = "analytical"  # "analytical", "intuitive", "directive", "conceptual"
    information_processing: str = "balanced"  # "visual", "auditory", "kinesthetic", "balanced"
    
    # Confidence scores
    personality_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    analysis_quality: float = Field(ge=0.0, le=1.0, default=0.0)


class SocialNetworkProfile(BaseModel):
    """User's social network analysis"""    # Network metrics
    total_connections: int = 0
    active_connections: int = 0
    network_reach: int = 0
    network_influence: float = Field(ge=0.0, le=1.0, default=0.0)
    
    # Connection analysis
    connection_categories: Dict[str, int] = Field(default_factory=dict)
    mutual_connections: List[str] = Field(default_factory=list)
    influential_connections: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Community involvement
    communities: List[Dict[str, Any]] = Field(default_factory=list)
    community_roles: List[str] = Field(default_factory=list)
    
    # Interaction patterns
    interaction_frequency: Dict[str, float] = Field(default_factory=dict)
    relationship_strength: Dict[str, float] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """Comprehensive user profile"""    profile_id: str
    user_id: str
    username: str
    platform: str
    
    # Profile metadata
    profile_creation_date: datetime
    last_updated: datetime
    profile_version: str = "1.0"
    
    # Classification
    user_type: UserType
    engagement_pattern: EngagementPattern
    verification_status: bool = False
    account_age_days: int = 0
    
    # Core profiles
    demographic_profile: DemographicProfile
    behavior_metrics: BehaviorMetrics
    interest_profile: InterestProfile
    personality_profile: PersonalityProfile
    social_network_profile: SocialNetworkProfile
    
    # Analysis metadata
    data_points_analyzed: int = 0
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_completeness: float = Field(ge=0.0, le=1.0)
    
    # Privacy and compliance
    data_sources: List[str] = Field(default_factory=list)
    privacy_level: str = "standard"  # "minimal", "standard", "comprehensive"
    consent_status: bool = False
    
    # Insights and recommendations
    key_insights: List[str] = Field(default_factory=list)
    personalization_recommendations: List[str] = Field(default_factory=list)
    content_recommendations: List[Dict[str, Any]] = Field(default_factory=list)


class ProfileAnalysisResult(BaseModel):
    """Result of profile analysis operation"""    analysis_id: str
    user_profile: UserProfile
    analysis_timestamp: datetime
    processing_time_ms: int
    
    # Analysis quality metrics
    data_quality_score: float = Field(ge=0.0, le=1.0)
    inference_accuracy: float = Field(ge=0.0, le=1.0)
    completeness_score: float = Field(ge=0.0, le=1.0)
    
    # Changes detected
    profile_changes: List[Dict[str, Any]] = Field(default_factory=list)
    new_insights: List[str] = Field(default_factory=list)
    
    # Recommendations
    improvement_suggestions: List[str] = Field(default_factory=list)
    data_collection_recommendations: List[str] = Field(default_factory=list)


class AdvancedUserProfiler(BaseCrawler):
    """    Ultra-Advanced User Profiler
    
    Provides comprehensive user behavior analysis and profiling with AI-powered
    insights, demographic inference, and personalization recommendations.
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Analysis configuration
        self.ai_analysis_enabled = config.get('ai_analysis_enabled', True)
        self.demographic_inference_enabled = config.get('demographic_inference_enabled', True)
        self.personality_analysis_enabled = config.get('personality_analysis_enabled', True)
        self.behavioral_analysis_enabled = config.get('behavioral_analysis_enabled', True)
        
        # AI service endpoints
        self.personality_api_endpoint = config.get('personality_api_endpoint')
        self.demographic_api_endpoint = config.get('demographic_api_endpoint')
        self.interest_api_endpoint = config.get('interest_api_endpoint')
        self.sentiment_api_endpoint = config.get('sentiment_api_endpoint')
        
        # Rate limiting for AI services
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get('ai_requests_per_minute', 200),
            requests_per_hour=config.get('ai_requests_per_hour', 5000),
            burst_limit=config.get('ai_burst_limit', 50)
        )
        
        # Cache for profile data
        self.cache_manager = CacheManager(
            cache_ttl=config.get('cache_ttl', 7200),  # 2 hours
            max_cache_size=config.get('max_cache_size', 10000)
        )
        
        # Content encryption
        self.content_encryption = ContentEncryption()
        
        # Profile storage
        self.user_profiles = {}
        self.profile_history = defaultdict(list)
        
        # Analysis thresholds
        self.min_data_points = config.get('min_data_points', 50)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.update_threshold = config.get('update_threshold', 0.1)
        
        # Privacy and compliance
        self.privacy_mode = config.get('privacy_mode', 'standard')
        self.anonymization_enabled = config.get('anonymization_enabled', True)
        self.data_retention_days = config.get('data_retention_days', 365)
        
        # Machine learning models (would be loaded from files)
        self.personality_model = None
        self.demographic_model = None
        self.interest_model = None
        self.behavior_model = None
        
        logger.info("Advanced User Profiler initialized with AI-powered analysis")

    async def create_user_profile(
        self,
        user_id: str,
        username: str,
        platform: str,
        initial_data: Dict[str, Any] = None
    ) -> str:
        """        Create new user profile
        
        Args:
            user_id: Unique user identifier
            username: Username on platform
            platform: Platform name
            initial_data: Initial user data
            
        Returns:
            str: Profile ID
        """        try:
            profile_id = hashlib.md5(f"{user_id}_{platform}_{datetime.utcnow()}".encode()).hexdigest()
            
            # Initialize profile components
            demographic_profile = DemographicProfile()
            behavior_metrics = BehaviorMetrics()
            interest_profile = InterestProfile(
                content_preferences=ContentPreference()
            )
            personality_profile = PersonalityProfile()
            social_network_profile = SocialNetworkProfile()
            
            # Create user profile
            user_profile = UserProfile(
                profile_id=profile_id,
                user_id=user_id,
                username=username,
                platform=platform,
                profile_creation_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                user_type=UserType.CONSUMER,  # Default, will be updated
                engagement_pattern=EngagementPattern.PASSIVE,  # Default
                demographic_profile=demographic_profile,
                behavior_metrics=behavior_metrics,
                interest_profile=interest_profile,
                personality_profile=personality_profile,
                social_network_profile=social_network_profile,
                confidence_score=0.0,
                analysis_completeness=0.0
            )
            
            # Apply initial data if provided
            if initial_data:
                await self._apply_initial_data(user_profile, initial_data)
            
            # Store profile
            self.user_profiles[profile_id] = user_profile
            
            logger.info(f"User profile created: {profile_id} for {username}")
            return profile_id
            
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise

    async def analyze_user_behavior(
        self,
        profile_id: str,
        activity_data: List[Dict[str, Any]],
        analysis_depth: str = "comprehensive"
    ) -> ProfileAnalysisResult:
        """        Analyze user behavior and update profile
        
        Args:
            profile_id: Profile identifier
            activity_data: User activity data
            analysis_depth: Depth of analysis ("basic", "standard", "comprehensive")
            
        Returns:
            ProfileAnalysisResult: Analysis results
        """        start_time = datetime.utcnow()
        
        try:
            if profile_id not in self.user_profiles:
                raise ValueError(f"Profile {profile_id} not found")
            
            await self.rate_limiter.acquire()
            
            user_profile = self.user_profiles[profile_id]
            previous_profile = user_profile.copy(deep=True)
            
            # Update behavior metrics
            if self.behavioral_analysis_enabled:
                await self._analyze_behavioral_patterns(user_profile, activity_data)
            
            # Analyze interests
            await self._analyze_user_interests(user_profile, activity_data)
            
            # Demographic inference
            if self.demographic_inference_enabled:
                await self._infer_demographics(user_profile, activity_data)
            
            # Personality analysis
            if self.personality_analysis_enabled and analysis_depth in ["standard", "comprehensive"]:
                await self._analyze_personality(user_profile, activity_data)
            
            # Social network analysis
            if analysis_depth == "comprehensive":
                await self._analyze_social_network(user_profile, activity_data)
            
            # Update profile classifications
            await self._update_profile_classifications(user_profile)
            
            # Generate insights and recommendations
            await self._generate_profile_insights(user_profile)
            
            # Calculate profile quality metrics
            quality_metrics = await self._calculate_profile_quality(user_profile, activity_data)
            
            # Detect changes
            profile_changes = await self._detect_profile_changes(previous_profile, user_profile)
            
            # Update profile metadata
            user_profile.last_updated = datetime.utcnow()
            user_profile.data_points_analyzed += len(activity_data)
            user_profile.confidence_score = quality_metrics['confidence_score']
            user_profile.analysis_completeness = quality_metrics['completeness_score']
            
            # Store profile history
            self.profile_history[profile_id].append({
                'timestamp': datetime.utcnow(),
                'profile_snapshot': user_profile.dict(),
                'analysis_trigger': 'behavior_analysis'
            })
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            analysis_result = ProfileAnalysisResult(
                analysis_id=hashlib.md5(f"{profile_id}_{datetime.utcnow()}".encode()).hexdigest(),
                user_profile=user_profile,
                analysis_timestamp=datetime.utcnow(),
                processing_time_ms=processing_time,
                data_quality_score=quality_metrics['data_quality_score'],
                inference_accuracy=quality_metrics['inference_accuracy'],
                completeness_score=quality_metrics['completeness_score'],
                profile_changes=profile_changes,
                new_insights=user_profile.key_insights[-5:] if user_profile.key_insights else []
            )
            
            logger.info(f"User behavior analysis completed for {profile_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            raise

    async def get_user_recommendations(
        self,
        profile_id: str,
        recommendation_type: str = "content"
    ) -> List[Dict[str, Any]]:
        """        Get personalized recommendations for user
        
        Args:
            profile_id: Profile identifier
            recommendation_type: Type of recommendations ("content", "connections", "products")
            
        Returns:
            List[Dict[str, Any]]: Personalized recommendations
        """        try:
            if profile_id not in self.user_profiles:
                return []
            
            user_profile = self.user_profiles[profile_id]
            
            if recommendation_type == "content":
                recommendations = await self._generate_content_recommendations(user_profile)
            elif recommendation_type == "connections":
                recommendations = await self._generate_connection_recommendations(user_profile)
            elif recommendation_type == "products":
                recommendations = await self._generate_product_recommendations(user_profile)
            else:
                recommendations = []
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    async def compare_user_profiles(
        self,
        profile_id_1: str,
        profile_id_2: str
    ) -> Dict[str, Any]:
        """        Compare two user profiles for similarity
        
        Args:
            profile_id_1: First profile ID
            profile_id_2: Second profile ID
            
        Returns:
            Dict[str, Any]: Comparison analysis
        """        try:
            if profile_id_1 not in self.user_profiles or profile_id_2 not in self.user_profiles:
                return {}
            
            profile_1 = self.user_profiles[profile_id_1]
            profile_2 = self.user_profiles[profile_id_2]
            
            # Calculate similarity scores
            demographic_similarity = await self._calculate_demographic_similarity(
                profile_1.demographic_profile, profile_2.demographic_profile
            )
            
            interest_similarity = await self._calculate_interest_similarity(
                profile_1.interest_profile, profile_2.interest_profile
            )
            
            personality_similarity = await self._calculate_personality_similarity(
                profile_1.personality_profile, profile_2.personality_profile
            )
            
            behavior_similarity = await self._calculate_behavior_similarity(
                profile_1.behavior_metrics, profile_2.behavior_metrics
            )
            
            # Overall similarity
            overall_similarity = np.mean([
                demographic_similarity,
                interest_similarity,
                personality_similarity,
                behavior_similarity
            ])
            
            comparison = {
                'overall_similarity': overall_similarity,
                'demographic_similarity': demographic_similarity,
                'interest_similarity': interest_similarity,
                'personality_similarity': personality_similarity,
                'behavior_similarity': behavior_similarity,
                'shared_interests': await self._find_shared_interests(profile_1, profile_2),
                'key_differences': await self._identify_key_differences(profile_1, profile_2),
                'compatibility_score': overall_similarity,
                'recommendation_overlap': await self._calculate_recommendation_overlap(profile_1, profile_2)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing user profiles: {str(e)}")
            return {}

    async def get_profile_insights(self, profile_id: str) -> Dict[str, Any]:
        """        Get comprehensive insights for user profile
        
        Args:
            profile_id: Profile identifier
            
        Returns:
            Dict[str, Any]: Profile insights
        """        try:
            if profile_id not in self.user_profiles:
                return {}
            
            user_profile = self.user_profiles[profile_id]
            
            insights = {
                'profile_summary': {
                    'user_type': user_profile.user_type.value,
                    'engagement_pattern': user_profile.engagement_pattern.value,
                    'confidence_score': user_profile.confidence_score,
                    'completeness': user_profile.analysis_completeness
                },
                'demographic_insights': await self._get_demographic_insights(user_profile.demographic_profile),
                'interest_insights': await self._get_interest_insights(user_profile.interest_profile),
                'personality_insights': await self._get_personality_insights(user_profile.personality_profile),
                'behavior_insights': await self._get_behavior_insights(user_profile.behavior_metrics),
                'social_insights': await self._get_social_insights(user_profile.social_network_profile),
                'trends_and_patterns': await self._analyze_profile_trends(profile_id),
                'optimization_opportunities': await self._identify_optimization_opportunities(user_profile),
                'risk_factors': await self._identify_risk_factors(user_profile)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting profile insights: {str(e)}")
            return {}

    # Helper methods
    
    async def _apply_initial_data(self, profile: UserProfile, data: Dict[str, Any]):
        """Apply initial data to profile"""        # Apply basic profile information
        if 'account_age_days' in data:
            profile.account_age_days = data['account_age_days']
        
        if 'verification_status' in data:
            profile.verification_status = data['verification_status']
        
        # Apply demographic data
        if 'location' in data:
            profile.demographic_profile.location_country = data['location'].get('country')
            profile.demographic_profile.location_city = data['location'].get('city')
        
        if 'age_range' in data:
            profile.demographic_profile.age_range = data['age_range']

    async def _analyze_behavioral_patterns(self, profile: UserProfile, activity_data: List[Dict[str, Any]]):
        """Analyze user behavioral patterns"""        if not activity_data:
            return
        
        # Calculate activity metrics
        total_posts = len([a for a in activity_data if a.get('type') == 'post'])
        total_comments = len([a for a in activity_data if a.get('type') == 'comment'])
        total_shares = len([a for a in activity_data if a.get('type') == 'share'])
        total_likes = len([a for a in activity_data if a.get('type') == 'like'])
        
        # Update behavior metrics
        profile.behavior_metrics.total_posts += total_posts
        profile.behavior_metrics.total_comments += total_comments
        profile.behavior_metrics.total_shares += total_shares
        profile.behavior_metrics.total_likes_given += total_likes
        
        # Calculate timing patterns
        if activity_data:
            timestamps = [
                datetime.fromisoformat(a['timestamp']) if isinstance(a['timestamp'], str) 
                else a['timestamp'] 
                for a in activity_data if 'timestamp' in a
            ]
            
            if timestamps:
                hours = [t.hour for t in timestamps]
                days = [t.strftime('%A') for t in timestamps]
                
                if hours:
                    profile.behavior_metrics.peak_activity_hour = Counter(hours).most_common(1)[0][0]
                if days:
                    profile.behavior_metrics.most_active_day = Counter(days).most_common(1)[0][0]
        
        # Calculate engagement patterns
        if total_posts > 0:
            avg_engagement = (total_comments + total_shares + total_likes) / max(total_posts, 1)
            profile.behavior_metrics.avg_engagement_rate = min(avg_engagement / 100.0, 1.0)

    async def _analyze_user_interests(self, profile: UserProfile, activity_data: List[Dict[str, Any]]):
        """Analyze user interests from activity data"""        # Extract keywords and topics from content
        content_texts = []
        for activity in activity_data:
            if 'content' in activity:
                content_texts.append(activity['content'])
        
        if not content_texts:
            return
        
        # Simplified interest analysis (would use advanced NLP)
        all_text = ' '.join(content_texts).lower()
        
        # Category mapping
        category_keywords = {
            InterestCategory.TECHNOLOGY: ['tech', 'ai', 'software', 'digital', 'innovation'],
            InterestCategory.SPORTS: ['sport', 'game', 'team', 'player', 'match'],
            InterestCategory.ENTERTAINMENT: ['movie', 'music', 'tv', 'celebrity', 'show'],
            InterestCategory.FOOD: ['food', 'restaurant', 'recipe', 'cooking', 'meal'],
            InterestCategory.TRAVEL: ['travel', 'trip', 'vacation', 'destination', 'flight']
        }
        
        # Calculate interest scores
        interest_scores = []
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                normalized_score = min(score / len(content_texts), 1.0)
                interest_scores.append((category, normalized_score))
        
        # Sort by score and update profile
        interest_scores.sort(key=lambda x: x[1], reverse=True)
        profile.interest_profile.primary_interests = interest_scores[:3]
        profile.interest_profile.secondary_interests = interest_scores[3:8]

    async def _infer_demographics(self, profile: UserProfile, activity_data: List[Dict[str, Any]]):
        """Infer demographic information from user data"""        # Simplified demographic inference (would use ML models)
        
        # Analyze language patterns for age inference
        content_texts = [a.get('content', '') for a in activity_data if 'content' in a]
        if content_texts:
            all_text = ' '.join(content_texts).lower()
            
            # Simple age inference based on language patterns
            young_indicators = ['lol', 'omg', 'tbh', 'fr', 'no cap']
            mature_indicators = ['furthermore', 'however', 'consequently', 'nevertheless']
            
            young_score = sum(1 for indicator in young_indicators if indicator in all_text)
            mature_score = sum(1 for indicator in mature_indicators if indicator in all_text)
            
            if young_score > mature_score:
                profile.demographic_profile.age_range = "18-24"
                profile.demographic_profile.age_confidence = 0.6
            elif mature_score > young_score:
                profile.demographic_profile.age_range = "35-44"
                profile.demographic_profile.age_confidence = 0.6
            else:
                profile.demographic_profile.age_range = "25-34"
                profile.demographic_profile.age_confidence = 0.4

    async def _analyze_personality(self, profile: UserProfile, activity_data: List[Dict[str, Any]]):
        """Analyze personality traits from user behavior"""        # Simplified personality analysis (would use advanced models)
        content_texts = [a.get('content', '') for a in activity_data if 'content' in a]
        
        if not content_texts:
            return
        
        all_text = ' '.join(content_texts).lower()
        
        # Simple trait indicators
        trait_indicators = {
            PersonalityTrait.EXTRAVERSION: ['excited', 'party', 'social', 'friends', 'meet'],
            PersonalityTrait.OPENNESS: ['creative', 'art', 'new', 'innovative', 'explore'],
            PersonalityTrait.CONSCIENTIOUSNESS: ['plan', 'organize', 'schedule', 'goal', 'achieve'],
            PersonalityTrait.AGREEABLENESS: ['help', 'kind', 'support', 'care', 'thank'],
            PersonalityTrait.NEUROTICISM: ['stress', 'worry', 'anxious', 'difficult', 'problem']
        }
        
        # Calculate trait scores
        for trait, indicators in trait_indicators.items():
            score = sum(1 for indicator in indicators if indicator in all_text)
            normalized_score = min(score / len(content_texts), 1.0)
            profile.personality_profile.big_five_scores[trait] = normalized_score
        
        profile.personality_profile.personality_confidence = 0.7

    async def _analyze_social_network(self, profile: UserProfile, activity_data: List[Dict[str, Any]]):
        """Analyze social network patterns"""        # Extract interaction data
        mentions = []
        replies = []
        
        for activity in activity_data:
            if activity.get('type') == 'mention' and 'target_user' in activity:
                mentions.append(activity['target_user'])
            elif activity.get('type') == 'reply' and 'target_user' in activity:
                replies.append(activity['target_user'])
        
        # Calculate network metrics
        all_interactions = mentions + replies
        unique_interactions = list(set(all_interactions))
        
        profile.social_network_profile.total_connections = len(unique_interactions)
        profile.social_network_profile.active_connections = len([
            user for user in unique_interactions 
            if all_interactions.count(user) > 1
        ])
        
        # Analyze interaction patterns
        if all_interactions:
            interaction_counts = Counter(all_interactions)
            top_interactions = interaction_counts.most_common(5)
            
            profile.social_network_profile.interaction_frequency = {
                user: count / len(all_interactions)
                for user, count in top_interactions
            }

    async def _update_profile_classifications(self, profile: UserProfile):
        """Update profile type and engagement pattern classifications"""        # Determine user type based on behavior metrics
        if profile.behavior_metrics.total_posts > 100:
            if profile.behavior_metrics.avg_engagement_rate > 0.1:
                profile.user_type = UserType.INFLUENCER
            else:
                profile.user_type = UserType.CREATOR
        elif profile.behavior_metrics.total_posts > 20:
            profile.user_type = UserType.CREATOR
        else:
            profile.user_type = UserType.CONSUMER
        
        # Determine engagement pattern
        if profile.behavior_metrics.avg_posts_per_day > 5:
            profile.engagement_pattern = EngagementPattern.HIGHLY_ACTIVE
        elif profile.behavior_metrics.avg_posts_per_day > 1:
            profile.engagement_pattern = EngagementPattern.ACTIVE
        elif profile.behavior_metrics.total_comments > profile.behavior_metrics.total_posts:
            profile.engagement_pattern = EngagementPattern.CONTRIBUTOR
        else:
            profile.engagement_pattern = EngagementPattern.PASSIVE

    async def _generate_profile_insights(self, profile: UserProfile):
        """Generate insights and recommendations for profile"""        insights = []
        recommendations = []
        
        # Interest-based insights
        if profile.interest_profile.primary_interests:
            top_interest = profile.interest_profile.primary_interests[0][0]
            insights.append(f"Primary interest area: {top_interest.value}")
        
        # Behavior insights
        if profile.behavior_metrics.avg_engagement_rate > 0.1:
            insights.append("High engagement rate indicates strong audience connection")
        
        if profile.behavior_metrics.peak_activity_hour:
            insights.append(f"Most active during hour {profile.behavior_metrics.peak_activity_hour}")
        
        # Personality insights
        if profile.personality_profile.big_five_scores:
            highest_trait = max(
                profile.personality_profile.big_five_scores.items(),
                key=lambda x: x[1]
            )
            if highest_trait[1] > 0.7:
                insights.append(f"Strong {highest_trait[0].value} personality trait")
        
        # Generate recommendations
        if profile.user_type == UserType.CREATOR:
            recommendations.append("Consider posting consistently to build audience")
            recommendations.append("Engage with followers through comments and replies")
        
        if profile.behavior_metrics.avg_engagement_rate < 0.05:
            recommendations.append("Focus on creating more engaging content")
            recommendations.append("Use trending hashtags relevant to your interests")
        
        profile.key_insights = insights
        profile.personalization_recommendations = recommendations

    async def _calculate_profile_quality(self, profile: UserProfile, activity_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate profile quality metrics"""        # Data quality score
        data_points = len(activity_data)
        data_quality = min(data_points / self.min_data_points, 1.0)
        
        # Completeness score
        completeness_factors = [
            1.0 if profile.demographic_profile.age_range else 0.0,
            1.0 if profile.interest_profile.primary_interests else 0.0,
            1.0 if profile.personality_profile.big_five_scores else 0.0,
            1.0 if profile.behavior_metrics.total_posts > 0 else 0.0,
            1.0 if profile.social_network_profile.total_connections > 0 else 0.0
        ]
        completeness = np.mean(completeness_factors)
        
        # Confidence score
        confidence_scores = [
            profile.demographic_profile.age_confidence,
            profile.personality_profile.personality_confidence,
            data_quality
        ]
        confidence = np.mean([s for s in confidence_scores if s > 0])
        
        return {
            'data_quality_score': data_quality,
            'completeness_score': completeness,
            'confidence_score': confidence,
            'inference_accuracy': 0.8  # Would calculate from validation data
        }

    async def _detect_profile_changes(self, old_profile: UserProfile, new_profile: UserProfile) -> List[Dict[str, Any]]:
        """Detect significant changes in profile"""        changes = []
        
        # Check user type change
        if old_profile.user_type != new_profile.user_type:
            changes.append({
                'field': 'user_type',
                'old_value': old_profile.user_type.value,
                'new_value': new_profile.user_type.value,
                'change_type': 'classification_update'
            })
        
        # Check engagement pattern change
        if old_profile.engagement_pattern != new_profile.engagement_pattern:
            changes.append({
                'field': 'engagement_pattern',
                'old_value': old_profile.engagement_pattern.value,
                'new_value': new_profile.engagement_pattern.value,
                'change_type': 'behavior_shift'
            })
        
        # Check significant interest changes
        old_interests = {interest[0] for interest in old_profile.interest_profile.primary_interests}
        new_interests = {interest[0] for interest in new_profile.interest_profile.primary_interests}
        
        if old_interests != new_interests:
            changes.append({
                'field': 'primary_interests',
                'old_value': list(old_interests),
                'new_value': list(new_interests),
                'change_type': 'interest_evolution'
            })
        
        return changes

    # Additional helper methods for recommendations and comparisons...
    
    async def _generate_content_recommendations(self, profile: UserProfile) -> List[Dict[str, Any]]:
        """Generate content recommendations based on profile"""        recommendations = []
        
        # Based on interests
        for interest, score in profile.interest_profile.primary_interests:
            recommendations.append({
                'type': 'content_topic',
                'topic': interest.value,
                'relevance_score': score,
                'reason': f"High interest in {interest.value}"
            })
        
        # Based on timing preferences
        if profile.behavior_metrics.peak_activity_hour:
            recommendations.append({
                'type': 'posting_time',
                'hour': profile.behavior_metrics.peak_activity_hour,
                'relevance_score': 0.8,
                'reason': "Optimal engagement time"
            })
        
        return recommendations

    async def _generate_connection_recommendations(self, profile: UserProfile) -> List[Dict[str, Any]]:
        """Generate connection recommendations"""        # Simplified connection recommendations
        return []

    async def _generate_product_recommendations(self, profile: UserProfile) -> List[Dict[str, Any]]:
        """Generate product recommendations"""        # Simplified product recommendations
        return []

    async def _calculate_demographic_similarity(self, demo1: DemographicProfile, demo2: DemographicProfile) -> float:
        """Calculate demographic similarity"""        similarities = []
        
        if demo1.age_range and demo2.age_range:
            similarities.append(1.0 if demo1.age_range == demo2.age_range else 0.0)
        
        if demo1.location_country and demo2.location_country:
            similarities.append(1.0 if demo1.location_country == demo2.location_country else 0.0)
        
        return np.mean(similarities) if similarities else 0.0

    async def _calculate_interest_similarity(self, interest1: InterestProfile, interest2: InterestProfile) -> float:
        """Calculate interest similarity"""        interests1 = {interest[0] for interest in interest1.primary_interests}
        interests2 = {interest[0] for interest in interest2.primary_interests}
        
        if not interests1 or not interests2:
            return 0.0
        
        intersection = interests1.intersection(interests2)
        union = interests1.union(interests2)
        
        return len(intersection) / len(union) if union else 0.0

    async def _calculate_personality_similarity(self, pers1: PersonalityProfile, pers2: PersonalityProfile) -> float:
        """Calculate personality similarity"""        if not pers1.big_five_scores or not pers2.big_five_scores:
            return 0.0
        
        common_traits = set(pers1.big_five_scores.keys()).intersection(pers2.big_five_scores.keys())
        
        if not common_traits:
            return 0.0
        
        similarities = []
        for trait in common_traits:
            score1 = pers1.big_five_scores[trait]
            score2 = pers2.big_five_scores[trait]
            similarity = 1.0 - abs(score1 - score2)
            similarities.append(similarity)
        
        return np.mean(similarities)

    async def _calculate_behavior_similarity(self, behavior1: BehaviorMetrics, behavior2: BehaviorMetrics) -> float:
        """Calculate behavior similarity"""        # Simplified behavior similarity calculation
        similarities = []
        
        # Compare engagement rates
        eng_diff = abs(behavior1.avg_engagement_rate - behavior2.avg_engagement_rate)
        similarities.append(1.0 - eng_diff)
        
        # Compare activity patterns
        if behavior1.peak_activity_hour and behavior2.peak_activity_hour:
            hour_diff = abs(behavior1.peak_activity_hour - behavior2.peak_activity_hour)
            hour_similarity = 1.0 - (hour_diff / 24.0)
            similarities.append(hour_similarity)
        
        return np.mean(similarities) if similarities else 0.0

    async def _find_shared_interests(self, profile1: UserProfile, profile2: UserProfile) -> List[str]:
        """Find shared interests between profiles"""        interests1 = {interest[0].value for interest in profile1.interest_profile.primary_interests}
        interests2 = {interest[0].value for interest in profile2.interest_profile.primary_interests}
        
        return list(interests1.intersection(interests2))

    async def _identify_key_differences(self, profile1: UserProfile, profile2: UserProfile) -> List[str]:
        """Identify key differences between profiles"""        differences = []
        
        if profile1.user_type != profile2.user_type:
            differences.append(f"User type: {profile1.user_type.value} vs {profile2.user_type.value}")
        
        if profile1.engagement_pattern != profile2.engagement_pattern:
            differences.append(f"Engagement: {profile1.engagement_pattern.value} vs {profile2.engagement_pattern.value}")
        
        return differences

    async def _calculate_recommendation_overlap(self, profile1: UserProfile, profile2: UserProfile) -> float:
        """Calculate recommendation overlap between profiles"""        # Simplified overlap calculation
        return 0.5

    # Insight generation methods...
    
    async def _get_demographic_insights(self, demographic: DemographicProfile) -> List[str]:
        """Get demographic insights"""        insights = []
        
        if demographic.age_range:
            insights.append(f"Age range: {demographic.age_range}")
        
        if demographic.location_country:
            insights.append(f"Location: {demographic.location_country}")
        
        return insights

    async def _get_interest_insights(self, interests: InterestProfile) -> List[str]:
        """Get interest insights"""        insights = []
        
        if interests.primary_interests:
            top_interest = interests.primary_interests[0]
            insights.append(f"Top interest: {top_interest[0].value} (score: {top_interest[1]:.2f})")
        
        return insights

    async def _get_personality_insights(self, personality: PersonalityProfile) -> List[str]:
        """Get personality insights"""        insights = []
        
        if personality.big_five_scores:
            highest_trait = max(personality.big_five_scores.items(), key=lambda x: x[1])
            insights.append(f"Dominant trait: {highest_trait[0].value} ({highest_trait[1]:.2f})")
        
        return insights

    async def _get_behavior_insights(self, behavior: BehaviorMetrics) -> List[str]:
        """Get behavior insights"""        insights = []
        
        if behavior.peak_activity_hour:
            insights.append(f"Most active at hour {behavior.peak_activity_hour}")
        
        if behavior.avg_engagement_rate > 0.1:
            insights.append("High engagement rate")
        
        return insights

    async def _get_social_insights(self, social: SocialNetworkProfile) -> List[str]:
        """Get social network insights"""        insights = []
        
        if social.total_connections > 100:
            insights.append("Large social network")
        
        return insights

    async def _analyze_profile_trends(self, profile_id: str) -> List[str]:
        """Analyze profile trends over time"""        # Simplified trend analysis
        return ["Increasing engagement over time"]

    async def _identify_optimization_opportunities(self, profile: UserProfile) -> List[str]:
        """Identify optimization opportunities"""        opportunities = []
        
        if profile.behavior_metrics.avg_engagement_rate < 0.05:
            opportunities.append("Improve content engagement")
        
        if len(profile.interest_profile.primary_interests) < 3:
            opportunities.append("Diversify content topics")
        
        return opportunities

    async def _identify_risk_factors(self, profile: UserProfile) -> List[str]:
        """Identify potential risk factors"""        risks = []
        
        if profile.confidence_score < 0.5:
            risks.append("Low profile confidence - need more data")
        
        return risks

    async def close(self):
        """Close profiler and cleanup resources"""        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Advanced User Profiler closed successfully")
        except Exception as e:
            logger.error(f"Error closing user profiler: {str(e)}")
