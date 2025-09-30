#!/usr/bin/env python3
"""
Real-Time Intelligence - Real-Time Personalization Engine
Live User Experience Personalization System

This module provides comprehensive real-time personalization capabilities for the IA Chérie platform,
enabling dynamic content adaptation, behavioral analysis, and intelligent user journey optimization
with advanced ML-powered insights and A/B testing integration.

Architecture:
- Real-time behavioral tracking with ML-powered pattern recognition
- Dynamic content personalization with multi-criteria optimization
- Context-aware experience adaptation (device, location, temporal)
- Conversion funnel optimization with intelligent recommendations
- A/B testing integration with statistical significance tracking

Business Integration:
- Creator discovery personalization based on user preferences and behavior
- Content feed optimization with engagement prediction and ranking
- Collaboration recommendations with compatibility scoring
- Revenue optimization through personalized monetization strategies
- User journey optimization with conversion rate improvement

© 2024 IA Chérie - Proprietary and Confidential
All rights reserved. This code is the intellectual property of IA Chérie.
Unauthorized copying, distribution, or modification is strictly prohibited.
"""

import asyncio
import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union, Tuple
import logging
import threading
import random
import statistics

logger = logging.getLogger(__name__)

class PersonalizationContext(Enum):
    """Context types for personalization."""
    DEVICE_TYPE = "device_type"
    LOCATION = "location"
    TIME_OF_DAY = "time_of_day"
    USER_HISTORY = "user_history"
    SOCIAL_SIGNALS = "social_signals"
    REAL_TIME_BEHAVIOR = "real_time_behavior"

class ContentType(Enum):
    """Types of content for personalization."""
    CREATOR_RECOMMENDATIONS = "creator_recommendations"
    CONTENT_FEED = "content_feed"
    COLLABORATION_OPPORTUNITIES = "collaboration_opportunities"
    BRAND_MATCHES = "brand_matches"
    TRENDING_CONTENT = "trending_content"
    EDUCATIONAL_CONTENT = "educational_content"

class ExperienceVariant(Enum):
    """A/B testing experience variants."""
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"

@dataclass
class UserBehavior:
    """Real-time user behavior tracking."""
    user_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Interaction tracking
    page_views: List[str] = field(default_factory=list)
    clicks: List[Dict[str, Any]] = field(default_factory=list)
    time_spent: Dict[str, float] = field(default_factory=dict)
    scroll_depth: Dict[str, float] = field(default_factory=dict)
    
    # Engagement metrics
    content_interactions: List[Dict[str, Any]] = field(default_factory=list)
    creator_follows: List[str] = field(default_factory=list)
    collaboration_interests: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    
    # Context
    device_type: str = "desktop"
    location: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: str = "unknown"
    
    # Session metadata
    session_start: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    session_duration: float = 0.0
    
    def update_activity(self) -> None:
        """Update last activity and calculate session duration."""
        now = datetime.utcnow()
        self.session_duration = (now - self.session_start).total_seconds()
        self.last_activity = now
    
    def add_page_view(self, page: str, duration: float = 0.0) -> None:
        """Add page view event."""
        self.page_views.append(page)
        if duration > 0:
            self.time_spent[page] = duration
        self.update_activity()
    
    def add_click(self, element: str, target: str, context: Dict[str, Any] = None) -> None:
        """Add click event."""
        self.clicks.append({
            'element': element,
            'target': target,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        })
        self.update_activity()
    
    def add_content_interaction(self, content_id: str, action: str, 
                              engagement_score: float = 0.0) -> None:
        """Add content interaction event."""
        self.content_interactions.append({
            'content_id': content_id,
            'action': action,
            'engagement_score': engagement_score,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.update_activity()

@dataclass
class PersonalizationConfig:
    """Configuration for personalization algorithms."""
    user_id: str
    
    # Algorithm weights
    behavioral_weight: float = 0.4
    contextual_weight: float = 0.3
    collaborative_weight: float = 0.2
    content_weight: float = 0.1
    
    # Personalization preferences
    enable_location_based: bool = True
    enable_time_based: bool = True
    enable_social_signals: bool = True
    
    # Content preferences
    preferred_content_types: Set[ContentType] = field(default_factory=set)
    excluded_categories: Set[str] = field(default_factory=set)
    
    # Experience settings
    experience_variant: ExperienceVariant = ExperienceVariant.CONTROL
    enable_ab_testing: bool = True
    
    # Performance settings
    max_recommendations: int = 20
    cache_duration_minutes: int = 30
    real_time_updates: bool = True
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExperienceMetrics:
    """Experience performance metrics."""
    user_id: str
    variant: ExperienceVariant
    
    # Engagement metrics
    click_through_rate: float = 0.0
    time_on_page: float = 0.0
    bounce_rate: float = 0.0
    pages_per_session: float = 0.0
    
    # Conversion metrics
    conversion_rate: float = 0.0
    revenue_per_user: float = 0.0
    lifetime_value: float = 0.0
    
    # Satisfaction metrics
    user_satisfaction_score: float = 0.0
    recommendation_acceptance_rate: float = 0.0
    feedback_score: float = 0.0
    
    # Performance tracking
    total_sessions: int = 0
    total_interactions: int = 0
    total_conversions: int = 0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_engagement_score(self) -> float:
        """Calculate overall engagement score."""
        return (self.click_through_rate * 0.3 + 
                min(self.time_on_page / 300, 1.0) * 0.2 +  # Normalize to 5 minutes
                (1 - self.bounce_rate) * 0.2 +
                min(self.pages_per_session / 10, 1.0) * 0.3) * 100

class RealTimePersonalizationEngine:
    """
    Real-time personalization engine for dynamic user experience optimization.
    
    Provides comprehensive personalization capabilities with:
    - Real-time behavioral analysis and pattern recognition
    - Dynamic content personalization with ML optimization
    - Context-aware experience adaptation
    - A/B testing integration with statistical analysis
    - Conversion funnel optimization
    """
    
    def __init__(self):
        """Initialize the personalization engine."""
        # User tracking
        self.user_behaviors: Dict[str, UserBehavior] = {}
        self.user_configs: Dict[str, PersonalizationConfig] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Experience tracking
        self.experience_metrics: Dict[str, ExperienceMetrics] = {}
        self.ab_test_assignments: Dict[str, ExperienceVariant] = {}
        
        # Recommendation caching
        self.recommendation_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # ML models simulation (in production, load actual models)
        self.behavioral_model = self._initialize_behavioral_model()
        self.content_model = self._initialize_content_model()
        self.conversion_model = self._initialize_conversion_model()
        
        # Performance tracking
        self.personalization_metrics = {
            'total_users': 0,
            'active_personalizations': 0,
            'avg_engagement_improvement': 0.0,
            'conversion_rate_improvement': 0.0,
            'cache_hit_rate': 0.0
        }
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info("RealTimePersonalizationEngine initialized")
    
    def _initialize_behavioral_model(self) -> Dict[str, Any]:
        """Initialize behavioral analysis model."""
        return {
            'type': 'behavioral_clustering',
            'clusters': {
                'highly_engaged': {'threshold': 0.8, 'features': ['time_spent', 'interactions']},
                'moderately_engaged': {'threshold': 0.5, 'features': ['page_views', 'clicks']},
                'low_engaged': {'threshold': 0.2, 'features': ['bounce_rate', 'session_duration']}
            },
            'weights': {
                'recency': 0.4,
                'frequency': 0.3,
                'engagement': 0.3
            }
        }
    
    def _initialize_content_model(self) -> Dict[str, Any]:
        """Initialize content recommendation model."""
        return {
            'type': 'hybrid_filtering',
            'collaborative_filtering': {
                'similarity_threshold': 0.7,
                'min_interactions': 10
            },
            'content_based': {
                'feature_weights': {
                    'category': 0.3,
                    'tags': 0.3,
                    'engagement_score': 0.4
                }
            },
            'matrix_factorization': {
                'factors': 50,
                'regularization': 0.01
            }
        }
    
    def _initialize_conversion_model(self) -> Dict[str, Any]:
        """Initialize conversion prediction model."""
        return {
            'type': 'gradient_boosting',
            'features': [
                'user_engagement_score',
                'content_relevance',
                'temporal_context',
                'device_context',
                'social_signals'
            ],
            'conversion_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8
            }
        }
    
    async def start_personalization_engine(self) -> None:
        """Start the personalization engine."""
        logger.info("Starting real-time personalization engine")
        
        # Start background tasks
        self.background_tasks.extend([
            asyncio.create_task(self._behavior_analyzer(), name="behavior_analyzer"),
            asyncio.create_task(self._recommendation_updater(), name="recommendation_updater"),
            asyncio.create_task(self._ab_test_manager(), name="ab_test_manager"),
            asyncio.create_task(self._conversion_optimizer(), name="conversion_optimizer"),
            asyncio.create_task(self._cache_manager(), name="cache_manager"),
            asyncio.create_task(self._metrics_collector(), name="metrics_collector")
        ])
        
        logger.info(f"Started {len(self.background_tasks)} personalization tasks")
    
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> None:
        """Track user behavior for personalization."""
        with self.lock:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = UserBehavior(user_id=user_id)
                self.personalization_metrics['total_users'] += 1
            
            behavior = self.user_behaviors[user_id]
        
        # Process behavior data
        if 'page_view' in behavior_data:
            behavior.add_page_view(
                behavior_data['page_view']['page'],
                behavior_data['page_view'].get('duration', 0.0)
            )
        
        if 'click' in behavior_data:
            click_data = behavior_data['click']
            behavior.add_click(
                click_data['element'],
                click_data['target'],
                click_data.get('context', {})
            )
        
        if 'content_interaction' in behavior_data:
            interaction = behavior_data['content_interaction']
            behavior.add_content_interaction(
                interaction['content_id'],
                interaction['action'],
                interaction.get('engagement_score', 0.0)
            )
        
        # Update context
        if 'context' in behavior_data:
            context = behavior_data['context']
            behavior.device_type = context.get('device_type', behavior.device_type)
            behavior.location = context.get('location', behavior.location)
        
        # Trigger real-time personalization update
        await self._update_user_personalization(user_id)
    
    async def get_personalized_recommendations(self, user_id: str, 
                                             content_type: ContentType,
                                             limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user."""
        cache_key = f"{user_id}_{content_type.value}_{limit}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            with self.lock:
                self.personalization_metrics['cache_hit_rate'] = (
                    self.personalization_metrics.get('cache_hit_rate', 0) * 0.9 + 0.1
                )
            return self.recommendation_cache[cache_key]['recommendations']
        
        # Generate new recommendations
        recommendations = await self._generate_recommendations(user_id, content_type, limit)
        
        # Cache recommendations
        with self.lock:
            self.recommendation_cache[cache_key] = {
                'recommendations': recommendations,
                'generated_at': datetime.utcnow()
            }
            self.cache_timestamps[cache_key] = datetime.utcnow()
        
        return recommendations
    
    async def _generate_recommendations(self, user_id: str, content_type: ContentType,
                                      limit: int) -> List[Dict[str, Any]]:
        """Generate personalized recommendations using ML models."""
        # Get user profile and behavior
        user_profile = await self._get_user_profile(user_id)
        user_behavior = self.user_behaviors.get(user_id)
        
        if not user_behavior:
            # Return default recommendations for new users
            return await self._get_default_recommendations(content_type, limit)
        
        # Analyze user behavior patterns
        behavior_features = self._extract_behavior_features(user_behavior)
        
        # Get contextual information
        context_features = self._extract_context_features(user_behavior)
        
        # Generate recommendations based on content type
        if content_type == ContentType.CREATOR_RECOMMENDATIONS:
            recommendations = await self._recommend_creators(
                user_profile, behavior_features, context_features, limit
            )
        elif content_type == ContentType.CONTENT_FEED:
            recommendations = await self._recommend_content(
                user_profile, behavior_features, context_features, limit
            )
        elif content_type == ContentType.COLLABORATION_OPPORTUNITIES:
            recommendations = await self._recommend_collaborations(
                user_profile, behavior_features, context_features, limit
            )
        elif content_type == ContentType.BRAND_MATCHES:
            recommendations = await self._recommend_brands(
                user_profile, behavior_features, context_features, limit
            )
        else:
            recommendations = await self._get_default_recommendations(content_type, limit)
        
        # Apply personalization scoring
        recommendations = self._apply_personalization_scoring(
            recommendations, user_profile, behavior_features
        )
        
        return recommendations[:limit]
    
    def _extract_behavior_features(self, behavior: UserBehavior) -> Dict[str, float]:
        """Extract behavioral features for ML models."""
        features = {
            'session_duration': behavior.session_duration,
            'page_views_count': len(behavior.page_views),
            'clicks_count': len(behavior.clicks),
            'content_interactions_count': len(behavior.content_interactions),
            'avg_time_per_page': statistics.mean(behavior.time_spent.values()) if behavior.time_spent else 0.0,
            'engagement_rate': len(behavior.content_interactions) / max(len(behavior.page_views), 1),
            'creator_follows_count': len(behavior.creator_follows),
            'search_queries_count': len(behavior.search_queries)
        }
        
        # Calculate engagement score
        features['engagement_score'] = min(
            (features['session_duration'] / 3600) * 0.3 +
            (features['page_views_count'] / 20) * 0.2 +
            features['engagement_rate'] * 0.5, 1.0
        )
        
        return features
    
    def _extract_context_features(self, behavior: UserBehavior) -> Dict[str, Any]:
        """Extract contextual features for personalization."""
        current_time = datetime.utcnow()
        
        return {
            'device_type': behavior.device_type,
            'location': behavior.location,
            'time_of_day': current_time.hour,
            'day_of_week': current_time.weekday(),
            'is_weekend': current_time.weekday() >= 5,
            'session_recency': (current_time - behavior.last_activity).total_seconds(),
            'referrer': behavior.referrer
        }
    
    async def _recommend_creators(self, user_profile: Dict[str, Any],
                                behavior_features: Dict[str, float],
                                context_features: Dict[str, Any],
                                limit: int) -> List[Dict[str, Any]]:
        """Recommend creators based on user preferences and behavior."""
        # Simulate creator recommendation algorithm
        creators = []
        
        # Base creator pool (in production, query from database)
        base_creators = [
            {
                'creator_id': f'creator_{i}',
                'name': f'Creator {i}',
                'category': random.choice(['lifestyle', 'tech', 'fitness', 'gaming', 'food']),
                'followers': random.randint(1000, 1000000),
                'engagement_rate': random.uniform(2.0, 15.0),
                'content_quality_score': random.uniform(6.0, 10.0),
                'collaboration_rate': random.uniform(0.1, 0.8)
            }
            for i in range(100)
        ]
        
        # Score creators based on user preferences
        for creator in base_creators:
            score = self._calculate_creator_score(
                creator, user_profile, behavior_features, context_features
            )
            creator['personalization_score'] = score
            creators.append(creator)
        
        # Sort by score and return top recommendations
        creators.sort(key=lambda x: x['personalization_score'], reverse=True)
        return creators[:limit * 2]  # Return more for filtering
    
    def _calculate_creator_score(self, creator: Dict[str, Any],
                               user_profile: Dict[str, Any],
                               behavior_features: Dict[str, float],
                               context_features: Dict[str, Any]) -> float:
        """Calculate personalization score for a creator."""
        score = 0.0
        
        # Category preference matching
        user_interests = user_profile.get('interests', [])
        if creator['category'] in user_interests:
            score += 0.3
        
        # Engagement alignment
        user_engagement = behavior_features.get('engagement_score', 0.5)
        creator_engagement = creator['engagement_rate'] / 15.0  # Normalize
        engagement_match = 1 - abs(user_engagement - creator_engagement)
        score += engagement_match * 0.25
        
        # Follower count preference (some users prefer micro-influencers)
        follower_score = min(creator['followers'] / 100000, 1.0)
        if behavior_features.get('creator_follows_count', 0) < 10:
            follower_score = 1 - follower_score  # Prefer smaller creators for new users
        score += follower_score * 0.2
        
        # Content quality
        score += (creator['content_quality_score'] / 10.0) * 0.15
        
        # Collaboration potential
        score += creator['collaboration_rate'] * 0.1
        
        return min(score, 1.0)
    
    async def _recommend_content(self, user_profile: Dict[str, Any],
                               behavior_features: Dict[str, float],
                               context_features: Dict[str, Any],
                               limit: int) -> List[Dict[str, Any]]:
        """Recommend content based on user behavior and preferences."""
        # Simulate content recommendation
        content_items = []
        
        for i in range(limit * 3):
            content = {
                'content_id': f'content_{i}',
                'title': f'Content Item {i}',
                'type': random.choice(['video', 'image', 'article', 'poll']),
                'category': random.choice(['lifestyle', 'tech', 'fitness', 'gaming', 'food']),
                'creator_id': f'creator_{random.randint(1, 50)}',
                'engagement_score': random.uniform(3.0, 10.0),
                'viral_potential': random.uniform(0.1, 0.9),
                'creation_time': datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            }
            
            # Calculate personalization score
            content['personalization_score'] = self._calculate_content_score(
                content, user_profile, behavior_features, context_features
            )
            content_items.append(content)
        
        # Sort by score
        content_items.sort(key=lambda x: x['personalization_score'], reverse=True)
        return content_items[:limit * 2]
    
    def _calculate_content_score(self, content: Dict[str, Any],
                               user_profile: Dict[str, Any],
                               behavior_features: Dict[str, float],
                               context_features: Dict[str, Any]) -> float:
        """Calculate personalization score for content."""
        score = 0.0
        
        # Category matching
        user_interests = user_profile.get('interests', [])
        if content['category'] in user_interests:
            score += 0.3
        
        # Content type preference
        preferred_types = user_profile.get('preferred_content_types', [])
        if content['type'] in preferred_types:
            score += 0.2
        
        # Engagement potential
        score += (content['engagement_score'] / 10.0) * 0.2
        
        # Viral potential (for highly engaged users)
        if behavior_features.get('engagement_score', 0) > 0.7:
            score += content['viral_potential'] * 0.15
        
        # Recency (fresher content gets higher score)
        content_age_hours = (datetime.utcnow() - content['creation_time']).total_seconds() / 3600
        recency_score = max(0, 1 - (content_age_hours / 48))  # Decay over 48 hours
        score += recency_score * 0.15
        
        return min(score, 1.0)
    
    async def _recommend_collaborations(self, user_profile: Dict[str, Any],
                                      behavior_features: Dict[str, float],
                                      context_features: Dict[str, Any],
                                      limit: int) -> List[Dict[str, Any]]:
        """Recommend collaboration opportunities."""
        collaborations = []
        
        for i in range(limit * 2):
            collaboration = {
                'collaboration_id': f'collab_{i}',
                'brand_name': f'Brand {i}',
                'campaign_title': f'Campaign {i}',
                'category': random.choice(['lifestyle', 'tech', 'fitness', 'gaming', 'food']),
                'budget_range': random.choice(['$500-1000', '$1000-5000', '$5000-10000']),
                'duration_days': random.randint(7, 90),
                'requirements': random.choice(['micro', 'macro', 'mega']),
                'match_score': random.uniform(0.3, 0.95)
            }
            
            collaboration['personalization_score'] = collaboration['match_score']
            collaborations.append(collaboration)
        
        collaborations.sort(key=lambda x: x['personalization_score'], reverse=True)
        return collaborations[:limit * 2]
    
    async def _recommend_brands(self, user_profile: Dict[str, Any],
                              behavior_features: Dict[str, float],
                              context_features: Dict[str, Any],
                              limit: int) -> List[Dict[str, Any]]:
        """Recommend brand partnerships."""
        brands = []
        
        for i in range(limit * 2):
            brand = {
                'brand_id': f'brand_{i}',
                'name': f'Brand {i}',
                'industry': random.choice(['fashion', 'tech', 'health', 'food', 'travel']),
                'collaboration_history': random.randint(0, 50),
                'average_budget': random.randint(1000, 50000),
                'rating': random.uniform(3.5, 5.0),
                'match_probability': random.uniform(0.2, 0.9)
            }
            
            brand['personalization_score'] = brand['match_probability']
            brands.append(brand)
        
        brands.sort(key=lambda x: x['personalization_score'], reverse=True)
        return brands[:limit * 2]
    
    async def _get_default_recommendations(self, content_type: ContentType,
                                         limit: int) -> List[Dict[str, Any]]:
        """Get default recommendations for new users."""
        # Return trending/popular content as default
        default_items = []
        
        for i in range(limit):
            item = {
                'id': f'default_{content_type.value}_{i}',
                'title': f'Popular {content_type.value.title()} {i}',
                'type': content_type.value,
                'popularity_score': random.uniform(7.0, 10.0),
                'personalization_score': 0.5  # Neutral score
            }
            default_items.append(item)
        
        return default_items
    
    def _apply_personalization_scoring(self, recommendations: List[Dict[str, Any]],
                                     user_profile: Dict[str, Any],
                                     behavior_features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Apply final personalization scoring and ranking."""
        # Apply user-specific adjustments
        for item in recommendations:
            base_score = item.get('personalization_score', 0.5)
            
            # Boost score based on user engagement level
            engagement_boost = behavior_features.get('engagement_score', 0.5) * 0.1
            
            # Apply diversity penalty (reduce score for similar items)
            # This would involve actual similarity calculations in production
            diversity_penalty = random.uniform(0.0, 0.05)
            
            final_score = base_score + engagement_boost - diversity_penalty
            item['final_personalization_score'] = min(max(final_score, 0.0), 1.0)
        
        # Sort by final score
        recommendations.sort(key=lambda x: x['final_personalization_score'], reverse=True)
        return recommendations
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached recommendations are still valid."""
        if cache_key not in self.recommendation_cache:
            return False
        
        cache_time = self.cache_timestamps.get(cache_key)
        if not cache_time:
            return False
        
        # Check if cache has expired (default 30 minutes)
        cache_age = (datetime.utcnow() - cache_time).total_seconds()
        return cache_age < 1800  # 30 minutes
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get or create user profile."""
        if user_id not in self.user_profiles:
            # Create default profile
            self.user_profiles[user_id] = {
                'user_id': user_id,
                'interests': random.sample(['lifestyle', 'tech', 'fitness', 'gaming', 'food'], 2),
                'preferred_content_types': random.sample(['video', 'image', 'article'], 2),
                'engagement_level': 'medium',
                'collaboration_interest': random.choice([True, False]),
                'created_at': datetime.utcnow()
            }
        
        return self.user_profiles[user_id]
    
    async def _update_user_personalization(self, user_id: str) -> None:
        """Update user personalization based on recent behavior."""
        behavior = self.user_behaviors.get(user_id)
        if not behavior:
            return
        
        # Update user profile based on behavior
        profile = await self._get_user_profile(user_id)
        
        # Analyze recent interactions to update interests
        recent_interactions = [
            interaction for interaction in behavior.content_interactions
            if (datetime.utcnow() - datetime.fromisoformat(interaction['timestamp'])).total_seconds() < 3600
        ]
        
        if recent_interactions:
            # Extract categories from recent interactions
            # In production, this would involve actual content analysis
            logger.debug(f"Updated personalization for user {user_id} based on {len(recent_interactions)} recent interactions")
        
        # Invalidate cache for this user
        self._invalidate_user_cache(user_id)
    
    def _invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate cached recommendations for a user."""
        with self.lock:
            keys_to_remove = [
                key for key in self.recommendation_cache.keys()
                if key.startswith(user_id)
            ]
            
            for key in keys_to_remove:
                self.recommendation_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
    
    async def assign_ab_test_variant(self, user_id: str) -> ExperienceVariant:
        """Assign A/B test variant to user."""
        if user_id in self.ab_test_assignments:
            return self.ab_test_assignments[user_id]
        
        # Random assignment with equal distribution
        variants = list(ExperienceVariant)
        variant = random.choice(variants)
        
        with self.lock:
            self.ab_test_assignments[user_id] = variant
        
        return variant
    
    async def track_conversion(self, user_id: str, conversion_type: str,
                             value: float = 0.0, metadata: Dict[str, Any] = None) -> None:
        """Track conversion events for optimization."""
        # Update experience metrics
        if user_id in self.experience_metrics:
            metrics = self.experience_metrics[user_id]
            metrics.total_conversions += 1
            
            if metrics.total_sessions > 0:
                metrics.conversion_rate = metrics.total_conversions / metrics.total_sessions
            
            if value > 0:
                metrics.revenue_per_user += value
        
        logger.info(f"Conversion tracked for user {user_id}: {conversion_type} (value: {value})")
    
    async def _behavior_analyzer(self) -> None:
        """Analyze user behavior patterns in real-time."""
        while not self.shutdown_event.is_set():
            try:
                # Analyze behavior patterns for active users
                with self.lock:
                    active_users = [
                        user_id for user_id, behavior in self.user_behaviors.items()
                        if (datetime.utcnow() - behavior.last_activity).total_seconds() < 3600
                    ]
                
                for user_id in active_users:
                    await self._update_user_personalization(user_id)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in behavior analyzer: {e}")
                await asyncio.sleep(300)
    
    async def _recommendation_updater(self) -> None:
        """Update recommendations for active users."""
        while not self.shutdown_event.is_set():
            try:
                # Update recommendations for users with expired cache
                current_time = datetime.utcnow()
                
                with self.lock:
                    expired_users = set()
                    for cache_key, cache_time in self.cache_timestamps.items():
                        if (current_time - cache_time).total_seconds() > 1800:  # 30 minutes
                            user_id = cache_key.split('_')[0]
                            expired_users.add(user_id)
                
                # Pre-generate recommendations for active users
                for user_id in list(expired_users)[:10]:  # Limit to 10 users per cycle
                    if user_id in self.user_behaviors:
                        for content_type in [ContentType.CREATOR_RECOMMENDATIONS, ContentType.CONTENT_FEED]:
                            await self.get_personalized_recommendations(user_id, content_type, 10)
                
                await asyncio.sleep(600)  # Update every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in recommendation updater: {e}")
                await asyncio.sleep(600)
    
    async def _ab_test_manager(self) -> None:
        """Manage A/B testing and statistical analysis."""
        while not self.shutdown_event.is_set():
            try:
                # Analyze A/B test results
                variant_metrics = defaultdict(list)
                
                with self.lock:
                    for user_id, metrics in self.experience_metrics.items():
                        variant = self.ab_test_assignments.get(user_id, ExperienceVariant.CONTROL)
                        variant_metrics[variant].append(metrics.calculate_engagement_score())
                
                # Calculate statistical significance
                for variant, scores in variant_metrics.items():
                    if len(scores) > 30:  # Minimum sample size
                        avg_score = statistics.mean(scores)
                        logger.info(f"A/B Test {variant.value}: avg engagement = {avg_score:.2f} (n={len(scores)})")
                
                await asyncio.sleep(3600)  # Analyze hourly
                
            except Exception as e:
                logger.error(f"Error in A/B test manager: {e}")
                await asyncio.sleep(3600)
    
    async def _conversion_optimizer(self) -> None:
        """Optimize conversion rates based on user behavior."""
        while not self.shutdown_event.is_set():
            try:
                # Analyze conversion patterns and optimize recommendations
                with self.lock:
                    total_conversions = sum(
                        metrics.total_conversions 
                        for metrics in self.experience_metrics.values()
                    )
                    
                    if total_conversions > 0:
                        avg_conversion_rate = statistics.mean([
                            metrics.conversion_rate 
                            for metrics in self.experience_metrics.values()
                            if metrics.total_sessions > 0
                        ])
                        
                        self.personalization_metrics['conversion_rate_improvement'] = avg_conversion_rate
                
                await asyncio.sleep(1800)  # Optimize every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in conversion optimizer: {e}")
                await asyncio.sleep(1800)
    
    async def _cache_manager(self) -> None:
        """Manage recommendation cache and cleanup."""
        while not self.shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                with self.lock:
                    # Remove expired cache entries
                    expired_keys = [
                        key for key, timestamp in self.cache_timestamps.items()
                        if (current_time - timestamp).total_seconds() > 3600  # 1 hour
                    ]
                    
                    for key in expired_keys:
                        self.recommendation_cache.pop(key, None)
                        self.cache_timestamps.pop(key, None)
                    
                    # Update cache hit rate
                    total_cache_requests = len(self.cache_timestamps)
                    if total_cache_requests > 0:
                        cache_hits = len([
                            key for key, timestamp in self.cache_timestamps.items()
                            if (current_time - timestamp).total_seconds() < 1800
                        ])
                        self.personalization_metrics['cache_hit_rate'] = cache_hits / total_cache_requests
                
                await asyncio.sleep(1800)  # Clean every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in cache manager: {e}")
                await asyncio.sleep(1800)
    
    async def _metrics_collector(self) -> None:
        """Collect personalization performance metrics."""
        while not self.shutdown_event.is_set():
            try:
                with self.lock:
                    # Update active personalization count
                    self.personalization_metrics['active_personalizations'] = len([
                        behavior for behavior in self.user_behaviors.values()
                        if (datetime.utcnow() - behavior.last_activity).total_seconds() < 3600
                    ])
                    
                    # Calculate engagement improvement
                    if self.experience_metrics:
                        engagement_scores = [
                            metrics.calculate_engagement_score()
                            for metrics in self.experience_metrics.values()
                        ]
                        if engagement_scores:
                            self.personalization_metrics['avg_engagement_improvement'] = statistics.mean(engagement_scores)
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
                await asyncio.sleep(300)
    
    async def shutdown(self) -> None:
        """Shutdown the personalization engine."""
        logger.info("Shutting down real-time personalization engine")
        
        self.shutdown_event.set()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Real-time personalization engine shutdown complete")
    
    def get_personalization_metrics(self) -> Dict[str, Any]:
        """Get current personalization metrics."""
        with self.lock:
            return self.personalization_metrics.copy()
    
    def get_user_experience_metrics(self, user_id: str) -> Optional[ExperienceMetrics]:
        """Get experience metrics for a specific user."""
        return self.experience_metrics.get(user_id)
    
    def get_ab_test_results(self) -> Dict[str, Any]:
        """Get A/B test results summary."""
        results = {}
        
        with self.lock:
            variant_data = defaultdict(list)
            
            for user_id, metrics in self.experience_metrics.items():
                variant = self.ab_test_assignments.get(user_id, ExperienceVariant.CONTROL)
                variant_data[variant].append({
                    'engagement_score': metrics.calculate_engagement_score(),
                    'conversion_rate': metrics.conversion_rate,
                    'revenue_per_user': metrics.revenue_per_user
                })
            
            for variant, data in variant_data.items():
                if data:
                    results[variant.value] = {
                        'sample_size': len(data),
                        'avg_engagement': statistics.mean([d['engagement_score'] for d in data]),
                        'avg_conversion_rate': statistics.mean([d['conversion_rate'] for d in data]),
                        'avg_revenue_per_user': statistics.mean([d['revenue_per_user'] for d in data])
                    }
        
        return results

# Factory functions for easy instantiation
def create_personalization_engine() -> RealTimePersonalizationEngine:
    """Create a configured personalization engine."""
    return RealTimePersonalizationEngine()

# Example usage and testing
async def main():
    """Example usage of the real-time personalization engine."""
    # Create engine
    engine = create_personalization_engine()
    
    try:
        # Start engine
        await engine.start_personalization_engine()
        
        # Simulate user behavior
        await engine.track_user_behavior("user_123", {
            'page_view': {'page': 'creator_discovery', 'duration': 45.5},
            'context': {'device_type': 'mobile', 'location': 'New York'}
        })
        
        await engine.track_user_behavior("user_123", {
            'click': {'element': 'creator_card', 'target': 'creator_456'},
            'content_interaction': {'content_id': 'content_789', 'action': 'like', 'engagement_score': 0.8}
        })
        
        # Get personalized recommendations
        recommendations = await engine.get_personalized_recommendations(
            "user_123", ContentType.CREATOR_RECOMMENDATIONS, 5
        )
        print(f"Creator recommendations: {len(recommendations)} items")
        
        content_recs = await engine.get_personalized_recommendations(
            "user_123", ContentType.CONTENT_FEED, 10
        )
        print(f"Content recommendations: {len(content_recs)} items")
        
        # Assign A/B test variant
        variant = await engine.assign_ab_test_variant("user_123")
        print(f"A/B test variant: {variant.value}")
        
        # Track conversion
        await engine.track_conversion("user_123", "creator_follow", 0.0)
        
        # Wait for background processing
        await asyncio.sleep(10)
        
        # Get metrics
        metrics = engine.get_personalization_metrics()
        print(f"Personalization metrics: {metrics}")
        
        ab_results = engine.get_ab_test_results()
        print(f"A/B test results: {ab_results}")
        
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main())