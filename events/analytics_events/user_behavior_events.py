"""User Behavior Events Module

Advanced user behavior analysis and journey tracking for multi-format content creators.
Provides comprehensive user interaction analysis, personalization, and retention optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn as nn
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import networkx as nx
from collections import defaultdict, deque

from ...core.events.base_event import BaseEvent, BaseEventHandler
from ...core.cache import CacheManager
from ...core.database import DatabaseManager
from ...core.logging import get_logger
from ...ml.models.behavior_predictor import BehaviorPredictor
from ...ai.personalization.user_personalizer import UserPersonalizer
from ...utils.metrics import MetricsCalculator
from ...config import settings

logger = get_logger(__name__)


class BehaviorType(Enum):
    """Types of user behaviors to track"""    CONTENT_VIEW = "content_view"
    CONTENT_INTERACTION = "content_interaction"
    PROFILE_VISIT = "profile_visit"
    SEARCH = "search"
    NAVIGATION = "navigation"
    SCROLL_PATTERN = "scroll_pattern"
    TIME_SPENT = "time_spent"
    SHARING = "sharing"
    COMMENTING = "commenting"
    FOLLOWING = "following"
    UNFOLLOWING = "unfollowing"
    PLAYLIST_CREATION = "playlist_creation"
    CONTENT_COMPLETION = "content_completion"
    REPEAT_CONSUMPTION = "repeat_consumption"
    CROSS_PLATFORM = "cross_platform"


class UserSegment(Enum):
    """User behavior segments"""    POWER_USER = "power_user"
    CASUAL_CONSUMER = "casual_consumer"
    DISCOVERY_FOCUSED = "discovery_focused"
    LOYALTY_FOCUSED = "loyalty_focused"
    ENGAGEMENT_HEAVY = "engagement_heavy"
    PASSIVE_CONSUMER = "passive_consumer"
    TREND_FOLLOWER = "trend_follower"
    NICHE_ENTHUSIAST = "niche_enthusiast"
    SOCIAL_SHARER = "social_sharer"
    CONTENT_CREATOR = "content_creator"


class JourneyStage(Enum):
    """Stages in user journey"""    DISCOVERY = "discovery"
    FIRST_INTERACTION = "first_interaction"
    EXPLORATION = "exploration"
    ENGAGEMENT = "engagement"
    COMMITMENT = "commitment"
    ADVOCACY = "advocacy"
    RETENTION = "retention"
    REACTIVATION = "reactivation"
    CHURN = "churn"


class PersonalizationDimension(Enum):
    """Dimensions for user personalization"""    CONTENT_PREFERENCE = "content_preference"
    TIMING_PREFERENCE = "timing_preference"
    FORMAT_PREFERENCE = "format_preference"
    PLATFORM_PREFERENCE = "platform_preference"
    INTERACTION_STYLE = "interaction_style"
    CONSUMPTION_PATTERN = "consumption_pattern"
    SOCIAL_BEHAVIOR = "social_behavior"
    DISCOVERY_METHOD = "discovery_method"


@dataclass
class UserBehaviorEvent(BaseEvent):
    """Represents a user behavior event"""    user_id: str
    creator_id: str
    behavior_type: BehaviorType
    session_id: str
    platform: str
    content_id: Optional[str]
    behavior_data: Dict[str, Any]
    timestamp: datetime
    duration_seconds: Optional[int] = None
    sequence_position: Optional[int] = None
    referrer_source: Optional[str] = None
    device_info: Optional[Dict[str, str]] = None
    location_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    ab_test_variant: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user behavior event to dictionary"""        return {
            **asdict(self),
            'behavior_type': self.behavior_type.value,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class UserJourney:
    """Represents a user's complete journey"""    user_id: str
    creator_id: str
    journey_id: str
    start_timestamp: datetime
    last_activity: datetime
    current_stage: JourneyStage
    touchpoints: List[Dict[str, Any]]
    conversion_events: List[Dict[str, Any]]
    engagement_score: float
    lifetime_value: float
    churn_probability: float
    next_likely_actions: List[str]
    personalization_profile: Dict[str, Any]


@dataclass
class UserPersonalizationProfile:
    """User personalization profile"""    user_id: str
    creator_id: str
    segment: UserSegment
    preferences: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    engagement_triggers: List[str]
    optimal_touchpoints: List[str]
    content_affinity: Dict[str, float]
    platform_preferences: Dict[str, float]
    timing_preferences: Dict[str, List[str]]
    last_updated: datetime


class UserBehaviorEventHandler(BaseEventHandler):
    """Handles user behavior events with advanced analytics"""    
    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()
        self.db_manager = DatabaseManager()
        self.behavior_tracker = UserBehaviorTracker()
        self.journey_analyzer = UserJourneyAnalyzer()
        self.personalization_engine = UserPersonalizationEngine()
        self.retention_analyzer = UserRetentionAnalyzer()
        
    async def handle(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Process user behavior event with comprehensive analysis"""        try:
            # Validate event data
            await self._validate_event(event)
            
            # Store behavior data
            await self._store_behavior_data(event)
            
            # Track user behavior patterns
            behavior_analysis = await self.behavior_tracker.track_behavior(event)
            
            # Analyze user journey
            journey_analysis = await self.journey_analyzer.analyze_journey(event)
            
            # Update personalization profile
            personalization_update = await self.personalization_engine.update_profile(event)
            
            # Analyze retention factors
            retention_analysis = await self.retention_analyzer.analyze_retention(event)
            
            # Calculate behavior insights
            behavior_insights = await self._calculate_behavior_insights(event)
            
            # Generate next action predictions
            next_actions = await self._predict_next_actions(event)
            
            # Update user segment if needed
            await self._update_user_segment(event, behavior_analysis)
            
            return {
                'status': 'success',
                'event_id': event.event_id,
                'behavior_analysis': behavior_analysis,
                'journey_analysis': journey_analysis,
                'personalization_update': personalization_update,
                'retention_analysis': retention_analysis,
                'behavior_insights': behavior_insights,
                'next_actions': next_actions,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing user behavior event: {str(e)}")
            await self._handle_error(event, e)
            raise
    
    async def _validate_event(self, event: UserBehaviorEvent) -> None:
        """Validate user behavior event data"""        required_fields = ['user_id', 'creator_id', 'behavior_type', 'session_id', 'platform']
        for field in required_fields:
            if not getattr(event, field):
                raise ValueError(f"Missing required field: {field}")
        
        if event.behavior_type not in BehaviorType:
            raise ValueError(f"Invalid behavior type: {event.behavior_type}")
        
        if event.duration_seconds is not None and event.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")
    
    async def _store_behavior_data(self, event: UserBehaviorEvent) -> None:
        """Store user behavior data in database"""        async with self.db_manager.get_session() as session:
            await session.execute(
                """                INSERT INTO user_behavior_events 
                (event_id, user_id, creator_id, behavior_type, session_id, platform,
                 content_id, behavior_data, timestamp, duration_seconds, sequence_position,
                 referrer_source, device_info, location_data, context_data, ab_test_variant)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.event_id, event.user_id, event.creator_id, event.behavior_type.value,
                    event.session_id, event.platform, event.content_id,
                    json.dumps(event.behavior_data), event.timestamp, event.duration_seconds,
                    event.sequence_position, event.referrer_source,
                    json.dumps(event.device_info), json.dumps(event.location_data),
                    json.dumps(event.context_data), event.ab_test_variant
                )
            )
    
    async def _calculate_behavior_insights(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Calculate insights from user behavior"""        # Get user's historical behavior
        user_history = await self._get_user_behavior_history(event.user_id, event.creator_id)
        
        # Calculate behavior patterns
        patterns = await self._identify_behavior_patterns(user_history)
        
        # Calculate engagement quality
        engagement_quality = await self._calculate_engagement_quality(event, user_history)
        
        # Identify anomalies
        anomalies = await self._detect_behavior_anomalies(event, user_history)
        
        # Calculate session quality
        session_quality = await self._calculate_session_quality(event)
        
        return {
            'behavior_patterns': patterns,
            'engagement_quality': engagement_quality,
            'anomalies': anomalies,
            'session_quality': session_quality,
            'behavior_score': await self._calculate_behavior_score(event, user_history)
        }


class UserBehaviorTracker:
    """Tracks and analyzes user behavior patterns"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        self.metrics_calculator = MetricsCalculator()
        
    async def track_behavior(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Track comprehensive user behavior metrics"""        # Session-level analysis
        session_analysis = await self._analyze_session_behavior(event)
        
        # Interaction patterns
        interaction_patterns = await self._analyze_interaction_patterns(event)
        
        # Content consumption patterns
        consumption_patterns = await self._analyze_consumption_patterns(event)
        
        # Temporal behavior analysis
        temporal_analysis = await self._analyze_temporal_behavior(event)
        
        # Platform behavior analysis
        platform_analysis = await self._analyze_platform_behavior(event)
        
        # Social behavior analysis
        social_analysis = await self._analyze_social_behavior(event)
        
        return {
            'session_analysis': session_analysis,
            'interaction_patterns': interaction_patterns,
            'consumption_patterns': consumption_patterns,
            'temporal_analysis': temporal_analysis,
            'platform_analysis': platform_analysis,
            'social_analysis': social_analysis,
            'behavior_summary': await self._generate_behavior_summary(event)
        }
    
    async def _analyze_session_behavior(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Analyze user behavior within the current session"""        # Get all events in current session
        session_events = await self._get_session_events(event.session_id)
        
        # Calculate session metrics
        session_duration = await self._calculate_session_duration(session_events)
        page_views = len([e for e in session_events if e['behavior_type'] == 'content_view'])
        interactions = len([e for e in session_events if e['behavior_type'] in ['content_interaction', 'commenting', 'sharing']])
        
        # Analyze navigation patterns
        navigation_path = [e['content_id'] for e in session_events if e.get('content_id')]
        unique_content = len(set(navigation_path))
        
        # Calculate engagement depth
        engagement_depth = interactions / max(page_views, 1)
        
        # Analyze scroll and time patterns
        scroll_patterns = await self._analyze_scroll_patterns(session_events)
        time_patterns = await self._analyze_time_patterns(session_events)
        
        return {
            'session_duration': session_duration,
            'page_views': page_views,
            'interactions': interactions,
            'unique_content_viewed': unique_content,
            'engagement_depth': engagement_depth,
            'navigation_path': navigation_path,
            'scroll_patterns': scroll_patterns,
            'time_patterns': time_patterns,
            'session_quality_score': await self._calculate_session_quality_score(session_events)
        }
    
    async def _analyze_interaction_patterns(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Analyze how user interacts with content"""        # Get user's interaction history
        user_interactions = await self._get_user_interactions(event.user_id, event.creator_id)
        
        # Analyze interaction types
        interaction_breakdown = defaultdict(int)
        for interaction in user_interactions:
            interaction_breakdown[interaction['behavior_type']] += 1
        
        # Calculate interaction velocity
        interaction_velocity = await self._calculate_interaction_velocity(user_interactions)
        
        # Analyze content preferences
        content_preferences = await self._analyze_content_preferences(user_interactions)
        
        # Analyze timing preferences
        timing_preferences = await self._analyze_timing_preferences(user_interactions)
        
        return {
            'interaction_breakdown': dict(interaction_breakdown),
            'interaction_velocity': interaction_velocity,
            'content_preferences': content_preferences,
            'timing_preferences': timing_preferences,
            'preferred_interaction_types': sorted(interaction_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
        }


class UserJourneyAnalyzer:
    """Analyzes user journey and touchpoint optimization"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    async def analyze_journey(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Analyze user's complete journey"""        # Get user's complete journey
        journey_data = await self._get_user_journey(event.user_id, event.creator_id)
        
        # Identify journey stage
        current_stage = await self._identify_journey_stage(event, journey_data)
        
        # Analyze touchpoint effectiveness
        touchpoint_analysis = await self._analyze_touchpoints(journey_data)
        
        # Calculate journey progression
        journey_progression = await self._calculate_journey_progression(journey_data)
        
        # Identify conversion paths
        conversion_paths = await self._identify_conversion_paths(journey_data)
        
        # Analyze journey health
        journey_health = await self._analyze_journey_health(journey_data)
        
        return {
            'current_stage': current_stage,
            'touchpoint_analysis': touchpoint_analysis,
            'journey_progression': journey_progression,
            'conversion_paths': conversion_paths,
            'journey_health': journey_health,
            'journey_optimization_opportunities': await self._identify_journey_optimizations(journey_data)
        }
    
    async def _get_user_journey(self, user_id: str, creator_id: str) -> List[Dict[str, Any]]:
        """Get complete user journey data"""        async with self.db_manager.get_session() as session:
            result = await session.execute(
                """                SELECT behavior_type, behavior_data, timestamp, platform, content_id,
                       duration_seconds, referrer_source, session_id
                FROM user_behavior_events 
                WHERE user_id = %s AND creator_id = %s
                ORDER BY timestamp ASC
                """,
                (user_id, creator_id)
            )
            
            journey = []
            for row in result.fetchall():
                journey.append({
                    'behavior_type': row[0],
                    'behavior_data': json.loads(row[1]) if row[1] else {},
                    'timestamp': row[2],
                    'platform': row[3],
                    'content_id': row[4],
                    'duration_seconds': row[5],
                    'referrer_source': row[6],
                    'session_id': row[7]
                })
            
            return journey
    
    async def _identify_journey_stage(self, event: UserBehaviorEvent, journey_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify current stage in user journey"""        if not journey_data:
            return {
                'stage': JourneyStage.DISCOVERY.value,
                'confidence': 0.9,
                'reasoning': 'First interaction'
            }
        
        # Analyze interaction patterns to determine stage
        total_interactions = len(journey_data)
        content_views = len([j for j in journey_data if j['behavior_type'] == 'content_view'])
        engagements = len([j for j in journey_data if j['behavior_type'] in ['content_interaction', 'commenting', 'sharing']])
        follows = len([j for j in journey_data if j['behavior_type'] == 'following'])
        
        # Calculate engagement ratio
        engagement_ratio = engagements / max(content_views, 1)
        
        # Determine stage based on patterns
        if total_interactions <= 3:
            stage = JourneyStage.DISCOVERY
            confidence = 0.8
        elif total_interactions <= 10 and engagement_ratio < 0.2:
            stage = JourneyStage.EXPLORATION
            confidence = 0.75
        elif engagement_ratio >= 0.2 and follows == 0:
            stage = JourneyStage.ENGAGEMENT
            confidence = 0.8
        elif follows > 0 and engagement_ratio >= 0.3:
            stage = JourneyStage.COMMITMENT
            confidence = 0.85
        elif total_interactions >= 50 and engagement_ratio >= 0.4:
            stage = JourneyStage.ADVOCACY
            confidence = 0.9
        else:
            stage = JourneyStage.RETENTION
            confidence = 0.7
        
        return {
            'stage': stage.value,
            'confidence': confidence,
            'total_interactions': total_interactions,
            'engagement_ratio': engagement_ratio,
            'stage_indicators': {
                'content_views': content_views,
                'engagements': engagements,
                'follows': follows
            }
        }


class UserPersonalizationEngine:
    """Manages user personalization profiles and recommendations"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.personalizer = UserPersonalizer()
        self.kmeans = KMeans(n_clusters=8, random_state=42)
        self.scaler = StandardScaler()
        
    async def update_profile(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Update user personalization profile"""        # Get current profile
        current_profile = await self._get_current_profile(event.user_id, event.creator_id)
        
        # Update behavioral patterns
        behavior_update = await self._update_behavioral_patterns(event, current_profile)
        
        # Update content preferences
        content_update = await self._update_content_preferences(event, current_profile)
        
        # Update timing preferences
        timing_update = await self._update_timing_preferences(event, current_profile)
        
        # Recalculate user segment
        segment_update = await self._recalculate_user_segment(event, current_profile)
        
        # Generate personalization recommendations
        recommendations = await self._generate_personalization_recommendations(event, current_profile)
        
        # Store updated profile
        await self._store_updated_profile(event, current_profile, behavior_update, content_update, timing_update, segment_update)
        
        return {
            'profile_updated': True,
            'behavior_update': behavior_update,
            'content_update': content_update,
            'timing_update': timing_update,
            'segment_update': segment_update,
            'recommendations': recommendations,
            'personalization_score': await self._calculate_personalization_score(current_profile)
        }


class UserRetentionAnalyzer:
    """Analyzes user retention patterns and predicts churn"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.churn_predictor = BehaviorPredictor()
        
    async def analyze_retention(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Analyze user retention factors"""        # Calculate retention metrics
        retention_metrics = await self._calculate_retention_metrics(event)
        
        # Predict churn probability
        churn_prediction = await self._predict_churn_probability(event)
        
        # Identify retention drivers
        retention_drivers = await self._identify_retention_drivers(event)
        
        # Analyze engagement trends
        engagement_trends = await self._analyze_engagement_trends(event)
        
        # Generate retention strategies
        retention_strategies = await self._generate_retention_strategies(event, churn_prediction)
        
        return {
            'retention_metrics': retention_metrics,
            'churn_prediction': churn_prediction,
            'retention_drivers': retention_drivers,
            'engagement_trends': engagement_trends,
            'retention_strategies': retention_strategies,
            'retention_health_score': await self._calculate_retention_health_score(event)
        }
    
    async def _predict_churn_probability(self, event: UserBehaviorEvent) -> Dict[str, Any]:
        """Predict probability of user churn"""        # Get user behavior features
        behavior_features = await self._extract_churn_features(event)
        
        # Use ML model to predict churn
        try:
            churn_probability = await self.churn_predictor.predict_churn(behavior_features)
            
            # Calculate time to churn
            time_to_churn = await self._estimate_time_to_churn(behavior_features, churn_probability)
            
            # Identify churn risk factors
            risk_factors = await self._identify_churn_risk_factors(behavior_features)
            
            return {
                'churn_probability': float(churn_probability),
                'risk_level': self._get_churn_risk_level(churn_probability),
                'time_to_churn_days': time_to_churn,
                'risk_factors': risk_factors,
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Error predicting churn: {str(e)}")
            return {
                'churn_probability': 0.5,
                'risk_level': 'medium',
                'error': str(e)
            }
    
    def _get_churn_risk_level(self, probability: float) -> str:
        """Convert churn probability to risk level"""        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'very_low'
