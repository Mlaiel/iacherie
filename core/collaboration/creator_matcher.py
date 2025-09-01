"""🎯 CREATOR MATCHER - AI-Powered Creator Matching System
=====================================================

Developed by: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved - Unauthorized use is strictly prohibited

⚠️  LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any attempt to steal, copy, or reproduce this concept, idea, or code
without explicit written authorization from Fahed Mlaiel is strictly forbidden
and will result in immediate legal action under German and international law.

Advanced AI system for matching creators across multiple formats:
- Musicians seeking visual artists
- Bloggers needing photographers  
- Influencers requiring content creators
- Comedians looking for video editors

Features:
- Multi-dimensional compatibility scoring
- Genre and style matching
- Audience overlap analysis
- Geographic proximity matching
- Schedule compatibility assessment
- Budget range compatibility
- Past collaboration success rates
- Real-time market trend analysis
- Advanced ML recommendation algorithms
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import json
import math
import uuid
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import haversine
import openai
import requests

logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """
Creator type enumeration"""

    MUSICIAN = "musician"
    BLOGGER = "blogger" 
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    VIDEO_EDITOR = "video_editor"
    GRAPHIC_DESIGNER = "graphic_designer"
    VOICE_ACTOR = "voice_actor"
    ANIMATOR = "animator"
    PODCAST_HOST = "podcast_host"
    MUSIC_PRODUCER = "music_producer"
    SOUND_ENGINEER = "sound_engineer"
    SCRIPTWRITER = "scriptwriter"
    CINEMATOGRAPHER = "cinematographer"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    CONTENT_WRITER = "content_writer"
    DANCER = "dancer"
    MAKEUP_ARTIST = "makeup_artist"
    STYLIST = "stylist"

class GenreType(Enum):
    """Genre and style enumeration"""
    # Music genres
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    REGGAE = "reggae"
    BLUES = "blues"
    FOLK = "folk"
    METAL = "metal"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    FUNK = "funk"
    SOUL = "soul"
    LATIN = "latin"
    WORLD = "world"
    AMBIENT = "ambient"
    
    # Content styles
    COMEDY = "comedy"
    EDUCATIONAL = "educational"
    LIFESTYLE = "lifestyle"
    TRAVEL = "travel"
    FOOD = "food"
    TECH = "tech"
    FITNESS = "fitness"
    FASHION = "fashion"
    GAMING = "gaming"
    BEAUTY = "beauty"
    DIY = "diy"
    NEWS = "news"
    DOCUMENTARY = "documentary"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    HEALTH = "health"
    SPORTS = "sports"
    SCIENCE = "science"
    ART = "art"
    CULTURE = "culture"

class CollaborationType(Enum):
    """Collaboration type enumeration"""

    CREATIVE_PROJECT = "creative_project"
    CONTENT_CREATION = "content_creation"
    MUSIC_COLLABORATION = "music_collaboration"
    VIDEO_PRODUCTION = "video_production"
    PHOTO_SHOOT = "photo_shoot"
    PODCAST_EPISODE = "podcast_episode"
    LIVE_PERFORMANCE = "live_performance"
    BRAND_CAMPAIGN = "brand_campaign"
    EDUCATIONAL_CONTENT = "educational_content"
    SOCIAL_MEDIA_SERIES = "social_media_series"
    MUSIC_VIDEO = "music_video"
    REMIX_PROJECT = "remix_project"
    COVER_COLLABORATION = "cover_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    MERCHANDISE_DESIGN = "merchandise_design"
    EVENT_COLLABORATION = "event_collaboration"
    TUTORIAL_SERIES = "tutorial_series"
    LIVE_STREAM = "live_stream"
    INTERVIEW = "interview"
    CHALLENGE_COLLABORATION = "challenge_collaboration"

class PlatformType(Enum):
    """Platform enumeration"""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DISCORD = "discord"
    REDDIT = "reddit"
    CLUBHOUSE = "clubhouse"
    SNAPCHAT = "snapchat"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"

class MatchingPriority(Enum):
    """Matching priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class MatchingDimension(Enum):
    """Matching dimension types"""

    GENRE_STYLE = "genre_style"
    AUDIENCE_OVERLAP = "audience_overlap"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    BUDGET_COMPATIBILITY = "budget_compatibility"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    COLLABORATION_HISTORY = "collaboration_history"
    PLATFORM_ALIGNMENT = "platform_alignment"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT_RATES = "engagement_rates"
    GROWTH_TRAJECTORY = "growth_trajectory"
    BRAND_ALIGNMENT = "brand_alignment"

@dataclass
class MatchingCriteria:
    """Advanced criteria for creator matching"""
    creator_type: CreatorType
    target_types: List[CreatorType]
    min_compatibility_score: float = 0.6
    max_distance_km: Optional[float] = None
    budget_range: Optional[Tuple[float, float]] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    preferred_genres: List[str] = field(default_factory=list)
    collaboration_duration: Optional[int] = None  # days
    platform_preferences: List[str] = field(default_factory=list)
    exclude_previous_collaborators: bool = False
    min_follower_count: Optional[int] = None
    max_follower_count: Optional[int] = None
    min_engagement_rate: Optional[float] = None
    language_preferences: List[str] = field(default_factory=list)
    availability_window: Optional[Tuple[datetime, datetime]] = None
    collaboration_types: List[CollaborationType] = field(default_factory=list)
    quality_threshold: float = 0.7
    brand_safety_required: bool = True
    verified_only: bool = False
    
@dataclass
class CreatorProfile:
    """
Comprehensive creator profile"""
    creator_id: str
    creator_type: CreatorType
    username: str
    display_name: str
    bio: str
    skills: List[str]
    genres: List[str]
    languages: List[str]
    location: Dict[str, Any]
    audience_demographics: Dict[str, Any]
    social_metrics: Dict[str, Any]
    collaboration_history: List[Dict[str, Any]]
    content_portfolio: List[Dict[str, Any]]
    availability_schedule: Dict[str, Any]
    budget_preferences: Dict[str, Any]
    platform_presence: Dict[str, Any]
    quality_scores: Dict[str, float]
    verification_status: Dict[str, bool]
    reputation_score: float
    last_active: datetime
    created_at: datetime
    
class MatchingResult:
    """
Advanced result of creator matching process"""
    
    def __init__(
        self,
        creator_id: str,
        matched_creator: CreatorProfile,
        compatibility_score: float,
        dimension_scores: Dict[MatchingDimension, float],
        matching_reasons: List[str],
        potential_synergies: List[str],
        estimated_success_probability: float,
        recommended_collaboration_types: List[CollaborationType],
        estimated_roi: Dict[str, float],
        risk_factors: List[str],
        confidence_score: float
    ):
        self.creator_id = creator_id
        self.matched_creator = matched_creator
        self.compatibility_score = compatibility_score
        self.dimension_scores = dimension_scores
        self.matching_reasons = matching_reasons
        self.potential_synergies = potential_synergies
        self.estimated_success_probability = estimated_success_probability
        self.recommended_collaboration_types = recommended_collaboration_types
        self.estimated_roi = estimated_roi
        self.risk_factors = risk_factors
        self.confidence_score = confidence_score
        self.timestamp = datetime.utcnow()
        self.match_id = str(uuid.uuid4())
        
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'match_id': self.match_id,
            'creator_id': self.creator_id,
            'matched_creator': self.matched_creator.__dict__,
            'compatibility_score': self.compatibility_score,
            'dimension_scores': {dim.value: score for dim, score in self.dimension_scores.items()},
            'matching_reasons': self.matching_reasons,
            'potential_synergies': self.potential_synergies,
            'estimated_success_probability': self.estimated_success_probability,
            'recommended_collaboration_types': [ct.value for ct in self.recommended_collaboration_types],
            'estimated_roi': self.estimated_roi,
            'risk_factors': self.risk_factors,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat()
        }

class CreatorMatcher:
    """
Advanced AI-powered creator matching system"""
    
    def __init__(self, db_session, vector_store, ml_models, cache_service, analytics_tracker):
        self.db_session = db_session
        self.vector_store = vector_store
        self.ml_models = ml_models
        self.cache_service = cache_service
        self.analytics_tracker = analytics_tracker
        self.scaler = StandardScaler()
        
        # Enhanced ML model weights for advanced multi-dimensional matching
        self.dimension_weights = {
            MatchingDimension.GENRE_STYLE: 0.20,
            MatchingDimension.AUDIENCE_OVERLAP: 0.18,
            MatchingDimension.SKILL_COMPLEMENTARITY: 0.16,
            MatchingDimension.PLATFORM_ALIGNMENT: 0.14,
            MatchingDimension.CONTENT_QUALITY: 0.12,
            MatchingDimension.GEOGRAPHIC_PROXIMITY: 0.08,
            MatchingDimension.SCHEDULE_COMPATIBILITY: 0.06,
            MatchingDimension.BUDGET_COMPATIBILITY: 0.04,
            MatchingDimension.COLLABORATION_HISTORY: 0.02
        }
        
        # Advanced AI matching components
        self.behavioral_analyzer = None
        self.trend_predictor = None
        self.success_predictor = None
        
    async def find_matches(
        self,
        creator_id: str,
        criteria: MatchingCriteria,
        limit: int = 20,
        use_cache: bool = True
    ) -> List[MatchingResult]:
        """
Find compatible creators based on advanced criteria"""
        try:
            logger.info(f"Finding matches for creator {creator_id} with criteria: {criteria}")
            
            # Check cache first
            if use_cache:
                cache_key = f"creator_matches:{creator_id}:{hash(str(criteria))}"
                cached_matches = await self.cache_service.get(cache_key)
                if cached_matches:
                    logger.info("Returning cached matches")
                    return [MatchingResult(**match) for match in cached_matches]
            
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                raise ValueError(f"Creator profile not found: {creator_id}")
                
            # Get candidate creators
            candidates = await self._get_candidate_creators(criteria, limit * 5)
            
            # Calculate compatibility scores using AI
            matches = []
            for candidate in candidates:
                if candidate.creator_id == creator_id:
                    continue
                    
                compatibility_result = await self._calculate_advanced_compatibility(
                    creator_profile, candidate, criteria
                )
                
                if compatibility_result['score'] >= criteria.min_compatibility_score:
                    match_result = MatchingResult(
                        creator_id=creator_id,
                        matched_creator=candidate,
                        compatibility_score=compatibility_result['score'],
                        dimension_scores=compatibility_result['dimension_scores'],
                        matching_reasons=compatibility_result['reasons'],
                        potential_synergies=compatibility_result['synergies'],
                        estimated_success_probability=compatibility_result['success_probability'],
                        recommended_collaboration_types=compatibility_result['collaboration_types'],
                        estimated_roi=compatibility_result['estimated_roi'],
                        risk_factors=compatibility_result['risk_factors'],
                        confidence_score=compatibility_result['confidence_score']
                    )
                    matches.append(match_result)
            
            # Sort by compatibility score and apply ML ranking
            matches = await self._apply_ml_ranking(creator_profile, matches, criteria)
            
            # Cache results
            if use_cache:
                await self.cache_service.set(
                    cache_key, 
                    [match.to_dict() for match in matches[:limit]], 
                    ttl=3600  # 1 hour
                )
            
            # Track analytics
            await self.analytics_tracker.track_matching_request(
                creator_id, criteria, len(matches)
            )
            
            logger.info(f"Found {len(matches)} compatible creators")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            raise
            
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get comprehensive creator profile"""
        try:
            # Query database for creator profile
            query = """
            SELECT c.*, p.*, s.skills, g.genres, a.audience_demographics,
                   geo.latitude, geo.longitude, geo.city, geo.country,
                   sm.platform_metrics, ch.collaboration_history,
                   cp.content_portfolio, qs.quality_scores, vs.verification_status
            FROM creators c
            LEFT JOIN creator_profiles p ON c.id = p.creator_id
            LEFT JOIN creator_skills s ON c.id = s.creator_id
            LEFT JOIN creator_genres g ON c.id = g.creator_id
            LEFT JOIN audience_analytics a ON c.id = a.creator_id
            LEFT JOIN creator_geography geo ON c.id = geo.creator_id
            LEFT JOIN social_media_metrics sm ON c.id = sm.creator_id
            LEFT JOIN collaboration_history ch ON c.id = ch.creator_id
            LEFT JOIN content_portfolios cp ON c.id = cp.creator_id
            LEFT JOIN quality_scores qs ON c.id = qs.creator_id
            LEFT JOIN verification_status vs ON c.id = vs.creator_id
            WHERE c.id = %s AND c.is_active = true
            """
            
            result = await self.db_session.execute(query, (creator_id,))
            profile_data = result.fetchone()
            
            if not profile_data:
                return None
                
            # Create comprehensive profile
            profile = CreatorProfile(
                creator_id=profile_data['id'],
                creator_type=CreatorType(profile_data['creator_type']),
                username=profile_data['username'],
                display_name=profile_data['display_name'],
                bio=profile_data['bio'] or '',
                skills=json.loads(profile_data['skills']) if profile_data['skills'] else [],
                genres=json.loads(profile_data['genres']) if profile_data['genres'] else [],
                languages=json.loads(profile_data['languages']) if profile_data['languages'] else ['en'],
                location={
                    'latitude': profile_data['latitude'],
                    'longitude': profile_data['longitude'],
                    'city': profile_data['city'],
                    'country': profile_data['country']
                },
                audience_demographics=json.loads(profile_data['audience_demographics']) if profile_data['audience_demographics'] else {},
                social_metrics=json.loads(profile_data['platform_metrics']) if profile_data['platform_metrics'] else {},
                collaboration_history=json.loads(profile_data['collaboration_history']) if profile_data['collaboration_history'] else [],
                content_portfolio=json.loads(profile_data['content_portfolio']) if profile_data['content_portfolio'] else [],
                availability_schedule=await self._get_availability_schedule(creator_id),
                budget_preferences=await self._get_budget_preferences(creator_id),
                platform_presence=await self._get_platform_presence(creator_id),
                quality_scores=json.loads(profile_data['quality_scores']) if profile_data['quality_scores'] else {},
                verification_status=json.loads(profile_data['verification_status']) if profile_data['verification_status'] else {},
                reputation_score=profile_data['reputation_score'] or 0.0,
                last_active=profile_data['last_active'],
                created_at=profile_data['created_at']
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting creator profile: {str(e)}")
            return None
            
    async def _get_candidate_creators(
        self, 
        criteria: MatchingCriteria, 
        limit: int
    ) -> List[CreatorProfile]:
        """Get candidate creators based on initial filtering"""
        try:
            # Build query with initial filters
            where_conditions = ["c.is_active = true"]
            params = []
            
            # Filter by creator types
            if criteria.target_types:
                type_placeholders = ','.join(['%s'] * len(criteria.target_types))
                where_conditions.append(f"c.creator_type IN ({type_placeholders})")
                params.extend([ct.value for ct in criteria.target_types])
                
            # Filter by follower count
            if criteria.min_follower_count:
                where_conditions.append("sm.total_followers >= %s")
                params.append(criteria.min_follower_count)
                
            if criteria.max_follower_count:
                where_conditions.append("sm.total_followers <= %s")
                params.append(criteria.max_follower_count)
                
            # Filter by engagement rate
            if criteria.min_engagement_rate:
                where_conditions.append("sm.engagement_rate >= %s")
                params.append(criteria.min_engagement_rate)
                
            # Filter by verification if required
            if criteria.verified_only:
                where_conditions.append("vs.is_verified = true")
                
            # Filter by quality threshold
            where_conditions.append("qs.overall_score >= %s")
            params.append(criteria.quality_threshold)
            
            query = f"""
            SELECT c.*, p.*, s.skills, g.genres, a.audience_demographics,
                   geo.latitude, geo.longitude, geo.city, geo.country,
                   sm.platform_metrics, ch.collaboration_history,
                   cp.content_portfolio, qs.quality_scores, vs.verification_status
            FROM creators c
            LEFT JOIN creator_profiles p ON c.id = p.creator_id
            LEFT JOIN creator_skills s ON c.id = s.creator_id
            LEFT JOIN creator_genres g ON c.id = g.creator_id
            LEFT JOIN audience_analytics a ON c.id = a.creator_id
            LEFT JOIN creator_geography geo ON c.id = geo.creator_id
            LEFT JOIN social_media_metrics sm ON c.id = sm.creator_id
            LEFT JOIN collaboration_history ch ON c.id = ch.creator_id
            LEFT JOIN content_portfolios cp ON c.id = cp.creator_id
            LEFT JOIN quality_scores qs ON c.id = qs.creator_id
            LEFT JOIN verification_status vs ON c.id = vs.creator_id
            WHERE {' AND '.join(where_conditions)}
            ORDER BY qs.overall_score DESC, sm.total_followers DESC
            LIMIT %s
            """
            
            params.append(limit)
            result = await self.db_session.execute(query, params)
            
            candidates = []
            for row in result.fetchall():
                profile = await self._row_to_creator_profile(row)
                if profile:
                    candidates.append(profile)
                    
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting candidate creators: {str(e)}")
            return []
            
    async def _calculate_advanced_compatibility(
        self,
        creator_profile: CreatorProfile,
        candidate_profile: CreatorProfile,
        criteria: MatchingCriteria
    ) -> Dict[str, Any]:
        """Calculate advanced compatibility using AI algorithms"""
        try:
            dimension_scores = {}
            
            # Calculate each dimension score
            dimension_scores[MatchingDimension.GENRE_STYLE] = await self._calculate_genre_compatibility(
                creator_profile, candidate_profile
            )
            
            dimension_scores[MatchingDimension.AUDIENCE_OVERLAP] = await self._calculate_audience_overlap(
                creator_profile, candidate_profile
            )
            
            dimension_scores[MatchingDimension.SKILL_COMPLEMENTARITY] = await self._calculate_skill_complementarity(
                creator_profile, candidate_profile
            )
            
            dimension_scores[MatchingDimension.PLATFORM_ALIGNMENT] = await self._calculate_platform_alignment(
                creator_profile, candidate_profile
            )
            
            dimension_scores[MatchingDimension.CONTENT_QUALITY] = await self._calculate_content_quality_match(
                creator_profile, candidate_profile
            )
            
            dimension_scores[MatchingDimension.GEOGRAPHIC_PROXIMITY] = await self._calculate_geographic_proximity(
                creator_profile, candidate_profile, criteria.max_distance_km
            )
            
            dimension_scores[MatchingDimension.SCHEDULE_COMPATIBILITY] = await self._calculate_schedule_compatibility(
                creator_profile, candidate_profile, criteria.availability_window
            )
            
            dimension_scores[MatchingDimension.BUDGET_COMPATIBILITY] = await self._calculate_budget_compatibility(
                creator_profile, candidate_profile, criteria.budget_range
            )
            
            dimension_scores[MatchingDimension.COLLABORATION_HISTORY] = await self._calculate_collaboration_compatibility(
                creator_profile, candidate_profile
            )
            
            # Calculate weighted compatibility score
            total_score = sum(
                score * self.dimension_weights[dimension]
                for dimension, score in dimension_scores.items()
            )
            
            # Generate AI-powered insights
            insights = await self._generate_ai_insights(
                creator_profile, candidate_profile, dimension_scores
            )
            
            # Calculate success probability using ML model
            success_probability = await self._predict_collaboration_success(
                creator_profile, candidate_profile, dimension_scores
            )
            
            # Estimate ROI
            estimated_roi = await self._estimate_collaboration_roi(
                creator_profile, candidate_profile, criteria.collaboration_types
            )
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(
                creator_profile, candidate_profile, dimension_scores
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                dimension_scores, creator_profile, candidate_profile
            )
            
            return {
                'score': total_score,
                'dimension_scores': dimension_scores,
                'reasons': insights['matching_reasons'],
                'synergies': insights['potential_synergies'],
                'success_probability': success_probability,
                'collaboration_types': insights['recommended_collaboration_types'],
                'estimated_roi': estimated_roi,
                'risk_factors': risk_factors,
                'confidence_score': confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {str(e)}")
            return {
                'score': 0.0,
                'dimension_scores': {},
                'reasons': [],
                'synergies': [],
                'success_probability': 0.0,
                'collaboration_types': [],
                'estimated_roi': {},
                'risk_factors': ['Calculation error'],
                'confidence_score': 0.0
            }
            
    async def _calculate_genre_compatibility(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """Calculate genre/style compatibility"""
        if not creator1.genres or not creator2.genres:
            return 0.5  # Neutral score if no genre data
            
        # Direct genre overlap
        common_genres = set(creator1.genres) & set(creator2.genres)
        total_genres = set(creator1.genres) | set(creator2.genres)
        direct_overlap = len(common_genres) / len(total_genres) if total_genres else 0
        
        # Semantic similarity using embeddings
        semantic_similarity = await self._calculate_genre_semantic_similarity(
            creator1.genres, creator2.genres
        )
        
        # Complementary genres bonus
        complementary_bonus = await self._calculate_complementary_genre_bonus(
            creator1.genres, creator2.genres
        )
        
        # Weighted combination
        score = (direct_overlap * 0.4 + semantic_similarity * 0.4 + complementary_bonus * 0.2)
        return min(1.0, score)
        
    async def _calculate_audience_overlap(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """
Calculate audience overlap and compatibility"""
        demo1 = creator1.audience_demographics
        demo2 = creator2.audience_demographics
        
        if not demo1 or not demo2:
            return 0.5
            
        age_overlap = await self._calculate_age_overlap(
            demo1.get('age_distribution', {}),
            demo2.get('age_distribution', {})
        )
        
        gender_overlap = await self._calculate_gender_overlap(
            demo1.get('gender_distribution', {}),
            demo2.get('gender_distribution', {})
        )
        
        location_overlap = await self._calculate_location_overlap(
            demo1.get('location_distribution', {}),
            demo2.get('location_distribution', {})
        )
        
        interest_overlap = await self._calculate_interest_overlap(
            demo1.get('interests', []),
            demo2.get('interests', [])
        )
        
        # Weighted average
        score = (age_overlap * 0.3 + gender_overlap * 0.2 + 
                location_overlap * 0.2 + interest_overlap * 0.3)
        return score
        
    async def _calculate_skill_complementarity(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile
    ) -> float:
        """
Calculate skill complementarity"""
        skills1 = set(creator1.skills)
        skills2 = set(creator2.skills)
        
        if not skills1 or not skills2:
            return 0.3
            
        # Skills overlap (some overlap is good, too much is redundant)
        overlap = len(skills1 & skills2)
        total_skills = len(skills1 | skills2)
        overlap_ratio = overlap / total_skills if total_skills > 0 else 0
        
        # Optimal overlap is around 20-40%
        overlap_score = 1.0 - abs(overlap_ratio - 0.3) / 0.7
        
        # Complementary skills bonus
        complementary_pairs = await self._find_complementary_skills(skills1, skills2)
        complementary_score = min(1.0, len(complementary_pairs) * 0.2)
        
        # Combined score
        return (overlap_score * 0.6 + complementary_score * 0.4)
        
    # Additional helper methods for compatibility calculations
    async def _apply_ml_ranking(
        self,
        creator_profile: CreatorProfile,
        matches: List[MatchingResult],
        criteria: MatchingCriteria
    ) -> List[MatchingResult]:
        """
Apply machine learning ranking to improve match quality"""
        try:
            if not matches:
                return matches
                
            # Prepare features for ML model
            features = []
            for match in matches:
                feature_vector = await self._extract_match_features(
                    creator_profile, match, criteria
                )
                features.append(feature_vector)
                
            # Use ML model to predict match quality
            if hasattr(self.ml_models, 'match_ranking_model'):
                ml_scores = self.ml_models.match_ranking_model.predict_proba(features)[:, 1]
                
                # Combine compatibility score with ML score
                for i, match in enumerate(matches):
                    combined_score = (match.compatibility_score * 0.7 + ml_scores[i] * 0.3)
                    match.compatibility_score = combined_score
                    match.confidence_score = ml_scores[i]
                    
            # Sort by combined score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Error applying ML ranking: {str(e)}")
            return matches
            
    # Placeholder methods for complex calculations
    async def _calculate_genre_semantic_similarity(self, genres1: List[str], genres2: List[str]) -> float:
        """Calculate semantic similarity between genres using embeddings"""
        # Implementation would use genre embeddings
        return 0.5
        
    async def _calculate_complementary_genre_bonus(self, genres1: List[str], genres2: List[str]) -> float:
        """
Calculate bonus for complementary genres"""
        # Implementation would check for complementary genre pairs
        return 0.2
        
    async def _calculate_age_overlap(self, age_dist1: Dict, age_dist2: Dict) -> float:
        """
Calculate age distribution overlap"""
        # Implementation would calculate distribution similarity
        return 0.7
        
    async def _calculate_gender_overlap(self, gender_dist1: Dict, gender_dist2: Dict) -> float:
        """
Calculate gender distribution overlap"""
        return 0.6
        
    async def _calculate_location_overlap(self, loc_dist1: Dict, loc_dist2: Dict) -> float:
        """
Calculate location distribution overlap"""
        return 0.5
        
    async def _calculate_interest_overlap(self, interests1: List[str], interests2: List[str]) -> float:
        """
Calculate interest overlap"""
        if not interests1 or not interests2:
            return 0.5
        common = set(interests1) & set(interests2)
        total = set(interests1) | set(interests2)
        return len(common) / len(total) if total else 0
        
    async def _find_complementary_skills(self, skills1: set, skills2: set) -> List[Tuple[str, str]]:
        """
Find complementary skill pairs"""
        # Implementation would identify complementary skills
        return []
        
    async def _calculate_platform_alignment(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """
Calculate platform presence alignment"""
        return 0.6
        
    async def _calculate_content_quality_match(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """
Calculate content quality compatibility"""
        quality1 = creator1.quality_scores.get('overall_score', 0.5)
        quality2 = creator2.quality_scores.get('overall_score', 0.5)
        # Similar quality levels are better for collaboration
        quality_diff = abs(quality1 - quality2)
        return 1.0 - quality_diff
        
    async def _calculate_geographic_proximity(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        max_distance: Optional[float]
    ) -> float:
        """
Calculate geographic proximity score"""
        if not creator1.location or not creator2.location:
            return 0.5
            
        try:
            lat1, lon1 = creator1.location.get('latitude'), creator1.location.get('longitude')
            lat2, lon2 = creator2.location.get('latitude'), creator2.location.get('longitude')
            
            if not all([lat1, lon1, lat2, lon2]):
                return 0.5
                
            # Calculate distance using haversine formula
            distance = haversine((lat1, lon1), (lat2, lon2))
            
            if max_distance:
                if distance > max_distance:
                    return 0.0
                return 1.0 - (distance / max_distance)
            else:
                # Score based on distance ranges
                if distance < 50:
                    return 1.0
                elif distance < 200:
                    return 0.8
                elif distance < 500:
                    return 0.6
                elif distance < 1000:
                    return 0.4
                else:
                    return 0.2
                    
        except Exception:
            return 0.5
            
    # More placeholder methods for comprehensive functionality
    async def _calculate_schedule_compatibility(self, creator1, creator2, availability_window) -> float:
        return 0.7
        
    async def _calculate_budget_compatibility(self, creator1, creator2, budget_range) -> float:
        return 0.8
        
    async def _calculate_collaboration_compatibility(self, creator1, creator2) -> float:
        return 0.6
        
    async def _generate_ai_insights(self, creator1, creator2, dimension_scores) -> Dict[str, Any]:
        return {
            'matching_reasons': ['Strong genre compatibility', 'Complementary skills'],
            'potential_synergies': ['Cross-audience growth', 'Content diversification'],
            'recommended_collaboration_types': [CollaborationType.CREATIVE_PROJECT]
        }
        
    async def _predict_collaboration_success(self, creator1, creator2, dimension_scores) -> float:
        return 0.75
        
    async def _estimate_collaboration_roi(self, creator1, creator2, collaboration_types) -> Dict[str, float]:
        return {'revenue_increase': 0.25, 'audience_growth': 0.30, 'engagement_boost': 0.20}
        
    async def _identify_risk_factors(self, creator1, creator2, dimension_scores) -> List[str]:
        return []
        
    async def _calculate_confidence_score(self, dimension_scores, creator1, creator2) -> float:
        return 0.85
        
    async def _extract_match_features(self, creator_profile, match, criteria) -> List[float]:
        return [0.5] * 20  # Feature vector placeholder
        
    async def _get_availability_schedule(self, creator_id: str) -> Dict[str, Any]:
        return {}
        
    async def _get_budget_preferences(self, creator_id: str) -> Dict[str, Any]:
        return {}
        
    async def _get_platform_presence(self, creator_id: str) -> Dict[str, Any]:
        return {}
        
    async def _row_to_creator_profile(self, row: Dict[str, Any]) -> Optional[CreatorProfile]:
        """
Convert database row to CreatorProfile"""
        try:
            return CreatorProfile(
                creator_id=row['id'],
                creator_type=CreatorType(row['creator_type']),
                username=row['username'],
                display_name=row['display_name'],
                bio=row['bio'] or '',
                skills=json.loads(row['skills']) if row['skills'] else [],
                genres=json.loads(row['genres']) if row['genres'] else [],
                languages=json.loads(row.get('languages', '["en"]')),
                location={
                    'latitude': row.get('latitude'),
                    'longitude': row.get('longitude'),
                    'city': row.get('city'),
                    'country': row.get('country')
                },
                audience_demographics=json.loads(row['audience_demographics']) if row['audience_demographics'] else {},
                social_metrics=json.loads(row['platform_metrics']) if row['platform_metrics'] else {},
                collaboration_history=json.loads(row['collaboration_history']) if row['collaboration_history'] else [],
                content_portfolio=json.loads(row['content_portfolio']) if row['content_portfolio'] else [],
                availability_schedule={},
                budget_preferences={},
                platform_presence={},
                quality_scores=json.loads(row['quality_scores']) if row['quality_scores'] else {},
                verification_status=json.loads(row['verification_status']) if row['verification_status'] else {},
                reputation_score=row.get('reputation_score', 0.0),
                last_active=row.get('last_active', datetime.utcnow()),
                created_at=row.get('created_at', datetime.utcnow())
            )
        except Exception as e:
            logger.error(f"Error converting row to creator profile: {str(e)}")
            return None
    CONTENT_WRITER = "content_writer"

class MatchingDimension(Enum):
    """Matching dimension types"""

    GENRE_STYLE = "genre_style"
    AUDIENCE_OVERLAP = "audience_overlap"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    BUDGET_COMPATIBILITY = "budget_compatibility"
    SKILL_COMPLEMENTARITY = "skill_complementarity"
    COLLABORATION_HISTORY = "collaboration_history"
    PLATFORM_ALIGNMENT = "platform_alignment"

@dataclass
class MatchingCriteria:
    """Criteria for creator matching"""
    creator_type: CreatorType
    target_types: List[CreatorType]
    min_compatibility_score: float = 0.6
    max_distance_km: Optional[float] = None
    budget_range: Optional[Tuple[float, float]] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_genres: List[str] = field(default_factory=list)
    collaboration_duration: Optional[int] = None  # days
    platform_preferences: List[str] = field(default_factory=list)
    exclude_previous_collaborators: bool = False
    
class MatchingResult:
    """
Result of creator matching process"""
    
    def __init__(
        self,
        creator_id: str,
        matched_creator_id: str,
        compatibility_score: float,
        dimension_scores: Dict[MatchingDimension, float],
        matching_reasons: List[str],
        potential_synergies: List[str],
        estimated_success_probability: float,
        recommended_collaboration_types: List[str]
    ):
        self.creator_id = creator_id
        self.matched_creator_id = matched_creator_id
        self.compatibility_score = compatibility_score
        self.dimension_scores = dimension_scores
        self.matching_reasons = matching_reasons
        self.potential_synergies = potential_synergies
        self.estimated_success_probability = estimated_success_probability
        self.recommended_collaboration_types = recommended_collaboration_types
        self.timestamp = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'creator_id': self.creator_id,
            'matched_creator_id': self.matched_creator_id,
            'compatibility_score': self.compatibility_score,
            'dimension_scores': {dim.value: score for dim, score in self.dimension_scores.items()},
            'matching_reasons': self.matching_reasons,
            'potential_synergies': self.potential_synergies,
            'estimated_success_probability': self.estimated_success_probability,
            'recommended_collaboration_types': self.recommended_collaboration_types,
            'timestamp': self.timestamp.isoformat()
        }

class CreatorMatcher:
    """
AI-powered creator matching system"""
    
    def __init__(self, db_session, vector_store, ml_models):
        self.db_session = db_session
        self.vector_store = vector_store
        self.ml_models = ml_models
        self.scaler = StandardScaler()
        
    async def find_matches(
        self,
        creator_id: str,
        criteria: MatchingCriteria,
        limit: int = 20
    ) -> List[MatchingResult]:
        """
Find compatible creators based on criteria"""
        try:
            logger.info(f"Finding matches for creator {creator_id}")
            
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                raise ValueError(f"Creator profile not found: {creator_id}")
                
            # Get candidate creators
            candidates = await self._get_candidate_creators(criteria, limit * 3)
            
            # Calculate compatibility scores
            matches = []
            for candidate in candidates:
                if candidate['id'] == creator_id:
                    continue
                    
                compatibility_result = await self._calculate_compatibility(
                    creator_profile, candidate, criteria
                )
                
                if compatibility_result['score'] >= criteria.min_compatibility_score:
                    match_result = MatchingResult(
                        creator_id=creator_id,
                        matched_creator_id=candidate['id'],
                        compatibility_score=compatibility_result['score'],
                        dimension_scores=compatibility_result['dimension_scores'],
                        matching_reasons=compatibility_result['reasons'],
                        potential_synergies=compatibility_result['synergies'],
                        estimated_success_probability=compatibility_result['success_probability'],
                        recommended_collaboration_types=compatibility_result['collaboration_types']
                    )
                    matches.append(match_result)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            logger.info(f"Found {len(matches)} compatible creators")
            return matches[:limit]
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            raise
            
    async def _get_creator_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator profile data"""
        try:
            # Query database for creator profile
            query = """
            SELECT c.*, p.*, s.skills, g.genres, a.audience_demographics,
                   geo.latitude, geo.longitude, geo.city, geo.country
            FROM creators c
            LEFT JOIN creator_profiles p ON c.id = p.creator_id
            LEFT JOIN creator_skills s ON c.id = s.creator_id
            LEFT JOIN creator_genres g ON c.id = g.creator_id
            LEFT JOIN audience_analytics a ON c.id = a.creator_id
            LEFT JOIN creator_geography geo ON c.id = geo.creator_id
            WHERE c.id = %s AND c.is_active = true
            """
            
            result = await self.db_session.execute(query, (creator_id,))
            profile_data = result.fetchone()
            
            if not profile_data:
                return None
                
            # Get collaboration history
            collab_history = await self._get_collaboration_history(creator_id)
            
            # Get social media metrics
            social_metrics = await self._get_social_metrics(creator_id)
            
            return {
                'id': profile_data['id'],
                'creator_type': profile_data['creator_type'],
                'skills': profile_data['skills'] or [],
                'genres': profile_data['genres'] or [],
                'audience_demographics': profile_data['audience_demographics'] or {},
                'location': {
                    'latitude': profile_data['latitude'],
                    'longitude': profile_data['longitude'],
                    'city': profile_data['city'],
                    'country': profile_data['country']
                },
                'collaboration_history': collab_history,
                'social_metrics': social_metrics,
                'budget_range': (profile_data['min_budget'], profile_data['max_budget']),
                'availability': profile_data['availability_schedule'],
                'platform_preferences': profile_data['platform_preferences'] or []
            }
            
        except Exception as e:
            logger.error(f"Error getting creator profile: {str(e)}")
            return None
            
    async def _get_candidate_creators(
        self, 
        criteria: MatchingCriteria, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get candidate creators for matching"""
        try:
            # Build query conditions
            conditions = ["c.is_active = true"]
            params = []
            
            # Filter by target creator types
            if criteria.target_types:
                type_placeholders = ','.join(['%s'] * len(criteria.target_types))
                conditions.append(f"c.creator_type IN ({type_placeholders})")
                params.extend([ct.value for ct in criteria.target_types])
                
            # Filter by geographic proximity
            if criteria.max_distance_km:
                conditions.append("""
                    ST_DWithin(
                        geography(ST_MakePoint(geo.longitude, geo.latitude)),
                        geography(ST_MakePoint(%s, %s)),
                        %s * 1000
                    )
                """)
                # These would need to be filled with requester's coordinates
                params.extend([0.0, 0.0, criteria.max_distance_km])
                
            # Filter by budget compatibility
            if criteria.budget_range:
                conditions.append(
                    "(p.min_budget <= %s AND p.max_budget >= %s)"
                )
                params.extend([criteria.budget_range[1], criteria.budget_range[0]])
                
            query = f"""
            SELECT c.*, p.*, s.skills, g.genres, a.audience_demographics,
                   geo.latitude, geo.longitude, geo.city, geo.country
            FROM creators c
            LEFT JOIN creator_profiles p ON c.id = p.creator_id
            LEFT JOIN creator_skills s ON c.id = s.creator_id
            LEFT JOIN creator_genres g ON c.id = g.creator_id
            LEFT JOIN audience_analytics a ON c.id = a.creator_id
            LEFT JOIN creator_geography geo ON c.id = geo.creator_id
            WHERE {' AND '.join(conditions)}
            ORDER BY c.created_at DESC
            LIMIT %s
            """
            
            params.append(limit)
            result = await self.db_session.execute(query, params)
            candidates = result.fetchall()
            
            return [dict(row) for row in candidates]
            
        except Exception as e:
            logger.error(f"Error getting candidate creators: {str(e)}")
            return []
            
    async def _calculate_compatibility(
        self,
        creator_profile: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        criteria: MatchingCriteria
    ) -> Dict[str, Any]:
        """Calculate compatibility between two creators"""
        try:
            dimension_scores = {}
            reasons = []
            synergies = []
            
            # 1. Genre/Style compatibility
            genre_score = await self._calculate_genre_compatibility(
                creator_profile['genres'], candidate_profile['genres']
            )
            dimension_scores[MatchingDimension.GENRE_STYLE] = genre_score
            
            if genre_score > 0.7:
                reasons.append("Strong genre compatibility")
                synergies.append("Complementary artistic styles")
                
            # 2. Audience overlap analysis
            audience_score = await self._calculate_audience_overlap(
                creator_profile['audience_demographics'],
                candidate_profile['audience_demographics']
            )
            dimension_scores[MatchingDimension.AUDIENCE_OVERLAP] = audience_score
            
            if audience_score > 0.6:
                reasons.append("Similar target audience")
                synergies.append("Cross-promotion opportunities")
                
            # 3. Geographic proximity
            geo_score = await self._calculate_geographic_proximity(
                creator_profile['location'], candidate_profile['location']
            )
            dimension_scores[MatchingDimension.GEOGRAPHIC_PROXIMITY] = geo_score
            
            if geo_score > 0.8:
                reasons.append("Close geographic location")
                synergies.append("Potential for in-person collaboration")
                
            # 4. Skill complementarity
            skill_score = await self._calculate_skill_complementarity(
                creator_profile['skills'], candidate_profile['skills']
            )
            dimension_scores[MatchingDimension.SKILL_COMPLEMENTARITY] = skill_score
            
            if skill_score > 0.7:
                reasons.append("Complementary skill sets")
                synergies.append("Comprehensive content creation capabilities")
                
            # 5. Schedule compatibility
            schedule_score = await self._calculate_schedule_compatibility(
                creator_profile['availability'], candidate_profile['availability']
            )
            dimension_scores[MatchingDimension.SCHEDULE_COMPATIBILITY] = schedule_score
            
            # 6. Budget compatibility
            budget_score = await self._calculate_budget_compatibility(
                creator_profile['budget_range'], candidate_profile['budget_range']
            )
            dimension_scores[MatchingDimension.BUDGET_COMPATIBILITY] = budget_score
            
            # 7. Collaboration history analysis
            history_score = await self._analyze_collaboration_history(
                creator_profile['collaboration_history'],
                candidate_profile['collaboration_history']
            )
            dimension_scores[MatchingDimension.COLLABORATION_HISTORY] = history_score
            
            # 8. Platform alignment
            platform_score = await self._calculate_platform_alignment(
                creator_profile['platform_preferences'],
                candidate_profile['platform_preferences']
            )
            dimension_scores[MatchingDimension.PLATFORM_ALIGNMENT] = platform_score
            
            # Calculate overall compatibility score
            weights = {
                MatchingDimension.GENRE_STYLE: 0.2,
                MatchingDimension.AUDIENCE_OVERLAP: 0.15,
                MatchingDimension.SKILL_COMPLEMENTARITY: 0.2,
                MatchingDimension.GEOGRAPHIC_PROXIMITY: 0.1,
                MatchingDimension.SCHEDULE_COMPATIBILITY: 0.1,
                MatchingDimension.BUDGET_COMPATIBILITY: 0.1,
                MatchingDimension.COLLABORATION_HISTORY: 0.1,
                MatchingDimension.PLATFORM_ALIGNMENT: 0.05
            }
            
            overall_score = sum(
                dimension_scores[dim] * weight 
                for dim, weight in weights.items()
            )
            
            # Estimate success probability using ML model
            success_probability = await self._predict_collaboration_success(
                creator_profile, candidate_profile, dimension_scores
            )
            
            # Recommend collaboration types
            collaboration_types = await self._recommend_collaboration_types(
                creator_profile, candidate_profile, dimension_scores
            )
            
            return {
                'score': overall_score,
                'dimension_scores': dimension_scores,
                'reasons': reasons,
                'synergies': synergies,
                'success_probability': success_probability,
                'collaboration_types': collaboration_types
            }
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {str(e)}")
            return {
                'score': 0.0,
                'dimension_scores': {},
                'reasons': [],
                'synergies': [],
                'success_probability': 0.0,
                'collaboration_types': []
            }
            
    async def _calculate_genre_compatibility(
        self, 
        genres1: List[str], 
        genres2: List[str]
    ) -> float:
        """Calculate genre compatibility score"""
        if not genres1 or not genres2:
            return 0.3  # Default neutral score
            
        # Convert to embeddings and calculate similarity
        try:
            genre_vector1 = await self._get_genre_embedding(genres1)
            genre_vector2 = await self._get_genre_embedding(genres2)
            
            if genre_vector1 is not None and genre_vector2 is not None:
                similarity = cosine_similarity([genre_vector1], [genre_vector2])[0][0]
                return max(0.0, min(1.0, similarity))
            else:
                # Fallback to simple overlap calculation
                intersection = set(genres1) & set(genres2)
                union = set(genres1) | set(genres2)
                return len(intersection) / len(union) if union else 0.0
                
        except Exception as e:
            logger.error(f"Error calculating genre compatibility: {str(e)}")
            return 0.0
            
    async def _calculate_audience_overlap(
        self,
        audience1: Dict[str, Any],
        audience2: Dict[str, Any]
    ) -> float:
        """Calculate audience overlap score"""
        try:
            if not audience1 or not audience2:
                return 0.3
                
            overlap_score = 0.0
            factors = 0
            
            # Age group overlap
            if 'age_groups' in audience1 and 'age_groups' in audience2:
                age_overlap = self._calculate_demographic_overlap(
                    audience1['age_groups'], audience2['age_groups']
                )
                overlap_score += age_overlap
                factors += 1
                
            # Geographic overlap
            if 'countries' in audience1 and 'countries' in audience2:
                geo_overlap = self._calculate_demographic_overlap(
                    audience1['countries'], audience2['countries']
                )
                overlap_score += geo_overlap
                factors += 1
                
            # Interest overlap
            if 'interests' in audience1 and 'interests' in audience2:
                interest_overlap = self._calculate_demographic_overlap(
                    audience1['interests'], audience2['interests']
                )
                overlap_score += interest_overlap
                factors += 1
                
            return overlap_score / factors if factors > 0 else 0.3
            
        except Exception as e:
            logger.error(f"Error calculating audience overlap: {str(e)}")
            return 0.0
            
    def _calculate_demographic_overlap(
        self, 
        demo1: Dict[str, float], 
        demo2: Dict[str, float]
    ) -> float:
        """Calculate overlap between demographic distributions"""
        if not demo1 or not demo2:
            return 0.0
            
        total_overlap = 0.0
        all_keys = set(demo1.keys()) | set(demo2.keys())
        
        for key in all_keys:
            percentage1 = demo1.get(key, 0.0)
            percentage2 = demo2.get(key, 0.0)
            total_overlap += min(percentage1, percentage2)
            
        return total_overlap / 100.0  # Convert to 0-1 scale
        
    async def _calculate_geographic_proximity(
        self,
        location1: Dict[str, Any],
        location2: Dict[str, Any]
    ) -> float:
        """
Calculate geographic proximity score"""
        try:
            if not all(k in location1 for k in ['latitude', 'longitude']) or \
               not all(k in location2 for k in ['latitude', 'longitude']):
                return 0.5  # Default neutral score
                
            # Calculate distance using haversine formula
            distance_km = self._calculate_distance_km(
                location1['latitude'], location1['longitude'],
                location2['latitude'], location2['longitude']
            )
            
            # Convert distance to proximity score (closer = higher score)
            if distance_km <= 50:  # Same city
                return 1.0
            elif distance_km <= 200:  # Same region
                return 0.8
            elif distance_km <= 500:  # Same country
                return 0.6
            elif distance_km <= 2000:  # Same continent
                return 0.4
            else:  # Different continents
                return 0.2
                
        except Exception as e:
            logger.error(f"Error calculating geographic proximity: {str(e)}")
            return 0.0
            
    def _calculate_distance_km(
        self, 
        lat1: float, lon1: float, 
        lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
        
    async def _calculate_skill_complementarity(
        self,
        skills1: List[str],
        skills2: List[str]
    ) -> float:
        """
Calculate skill complementarity score"""
        try:
            if not skills1 or not skills2:
                return 0.3
                
            # Look for complementary skills rather than overlapping ones
            complementary_pairs = await self._get_complementary_skills()
            
            complementarity_score = 0.0
            matches = 0
            
            for skill1 in skills1:
                for skill2 in skills2:
                    if self._are_skills_complementary(skill1, skill2, complementary_pairs):
                        complementarity_score += 1.0
                        matches += 1
                        
            # Normalize score
            max_possible_matches = min(len(skills1), len(skills2))
            return min(1.0, complementarity_score / max_possible_matches) if max_possible_matches > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating skill complementarity: {str(e)}")
            return 0.0
            
    async def _get_complementary_skills(self) -> Dict[str, List[str]]:
        """Get complementary skill mappings"""
        return {
            'music_production': ['video_editing', 'graphic_design', 'social_media'],
            'singing': ['music_production', 'video_editing', 'photography'],
            'photography': ['graphic_design', 'social_media', 'content_writing'],
            'video_editing': ['music_production', 'graphic_design', 'storytelling'],
            'content_writing': ['photography', 'graphic_design', 'seo'],
            'graphic_design': ['photography', 'video_editing', 'content_writing'],
            'social_media': ['photography', 'content_writing', 'graphic_design']
        }
        
    def _are_skills_complementary(
        self, 
        skill1: str, 
        skill2: str, 
        complementary_pairs: Dict[str, List[str]]
    ) -> bool:
        """
Check if two skills are complementary"""
        return (
            skill2 in complementary_pairs.get(skill1, []) or
            skill1 in complementary_pairs.get(skill2, [])
        )
        
    async def _calculate_schedule_compatibility(
        self,
        schedule1: Dict[str, Any],
        schedule2: Dict[str, Any]
    ) -> float:
        """
Calculate schedule compatibility score"""
        try:
            if not schedule1 or not schedule2:
                return 0.5
                
            # This would analyze availability windows, time zones, etc.
            # For now, return a placeholder score
            return 0.7
            
        except Exception as e:
            logger.error(f"Error calculating schedule compatibility: {str(e)}")
            return 0.0
            
    async def _calculate_budget_compatibility(
        self,
        budget1: Tuple[float, float],
        budget2: Tuple[float, float]
    ) -> float:
        """Calculate budget compatibility score"""
        try:
            if not budget1 or not budget2:
                return 0.5
                
            min1, max1 = budget1
            min2, max2 = budget2
            
            # Check if ranges overlap
            overlap_start = max(min1, min2)
            overlap_end = min(max1, max2)
            
            if overlap_start <= overlap_end:
                overlap_size = overlap_end - overlap_start
                total_range = max(max1, max2) - min(min1, min2)
                return overlap_size / total_range if total_range > 0 else 1.0
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating budget compatibility: {str(e)}")
            return 0.0
            
    async def _analyze_collaboration_history(
        self,
        history1: List[Dict[str, Any]],
        history2: List[Dict[str, Any]]
    ) -> float:
        """Analyze collaboration history compatibility"""
        try:
            # Analyze success rates, collaboration types, etc.
            # For now, return a placeholder score
            return 0.6
            
        except Exception as e:
            logger.error(f"Error analyzing collaboration history: {str(e)}")
            return 0.0
            
    async def _calculate_platform_alignment(
        self,
        platforms1: List[str],
        platforms2: List[str]
    ) -> float:
        """Calculate platform alignment score"""
        try:
            if not platforms1 or not platforms2:
                return 0.5
                
            intersection = set(platforms1) & set(platforms2)
            union = set(platforms1) | set(platforms2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating platform alignment: {str(e)}")
            return 0.0
            
    async def _predict_collaboration_success(
        self,
        creator_profile: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        dimension_scores: Dict[MatchingDimension, float]
    ) -> float:
        """Predict collaboration success probability using ML"""
        try:
            # Feature vector for ML model
            features = [
                dimension_scores.get(MatchingDimension.GENRE_STYLE, 0.0),
                dimension_scores.get(MatchingDimension.AUDIENCE_OVERLAP, 0.0),
                dimension_scores.get(MatchingDimension.SKILL_COMPLEMENTARITY, 0.0),
                dimension_scores.get(MatchingDimension.GEOGRAPHIC_PROXIMITY, 0.0),
                dimension_scores.get(MatchingDimension.COLLABORATION_HISTORY, 0.0),
                # Add more features as needed
            ]
            
            # Use ML model to predict success (placeholder)
            if hasattr(self.ml_models, 'collaboration_success_model'):
                prediction = self.ml_models.collaboration_success_model.predict([features])
                return float(prediction[0])
            else:
                # Fallback calculation
                return sum(features) / len(features)
                
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {str(e)}")
            return 0.5
            
    async def _recommend_collaboration_types(
        self,
        creator_profile: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        dimension_scores: Dict[MatchingDimension, float]
    ) -> List[str]:
        """Recommend collaboration types based on compatibility"""
        try:
            recommendations = []
            
            creator_type = creator_profile['creator_type']
            candidate_type = candidate_profile['creator_type']
            
            # Define collaboration type mappings
            type_combinations = {
                ('musician', 'video_editor'): ['music_video', 'promotional_content'],
                ('musician', 'photographer'): ['album_artwork', 'promotional_photos'],
                ('blogger', 'photographer'): ['blog_photography', 'content_creation'],
                ('influencer', 'graphic_designer'): ['social_media_graphics', 'brand_assets'],
                ('comedian', 'video_editor'): ['comedy_videos', 'sketch_production'],
            }
            
            key1 = (creator_type, candidate_type)
            key2 = (candidate_type, creator_type)
            
            if key1 in type_combinations:
                recommendations.extend(type_combinations[key1])
            elif key2 in type_combinations:
                recommendations.extend(type_combinations[key2])
            else:
                recommendations = ['content_collaboration', 'cross_promotion']
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending collaboration types: {str(e)}")
            return ['general_collaboration']
            
    async def _get_genre_embedding(self, genres: List[str]) -> Optional[np.ndarray]:
        """Get genre embedding vector"""
        try:
            # This would use a pre-trained model to get genre embeddings
            # For now, return a placeholder
            return np.random.rand(128)  # 128-dimensional embedding
            
        except Exception as e:
            logger.error(f"Error getting genre embedding: {str(e)}")
            return None
            
    async def _get_collaboration_history(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get collaboration history for creator"""
        try:
            query = """
            SELECT ch.*, c.creator_type as partner_type, c.name as partner_name
            FROM collaboration_history ch
            JOIN creators c ON (ch.creator1_id = c.id OR ch.creator2_id = c.id)
            WHERE (ch.creator1_id = %s OR ch.creator2_id = %s) 
            AND c.id != %s
            ORDER BY ch.created_at DESC
            LIMIT 10
            """
            
            result = await self.db_session.execute(query, (creator_id, creator_id, creator_id))
            return [dict(row) for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting collaboration history: {str(e)}")
            return []
            
    async def _get_social_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get social media metrics for creator"""
        try:
            query = """
            SELECT platform, followers_count, engagement_rate, last_updated
            FROM creator_social_metrics
            WHERE creator_id = %s
            """
            
            result = await self.db_session.execute(query, (creator_id,))
            metrics = {}
            for row in result.fetchall():
                metrics[row['platform']] = {
                    'followers': row['followers_count'],
                    'engagement_rate': row['engagement_rate'],
                    'last_updated': row['last_updated']
                }
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting social metrics: {str(e)}")
            return {}

    async def analyze_behavioral_patterns(
        self,
        creator_profile: 'CreatorProfile',
        candidate_profile: 'CreatorProfile'
    ) -> Dict[str, float]:
        """
        Advanced behavioral pattern analysis for enhanced matching
        """
        try:
            patterns = {}
            
            # Content creation frequency pattern matching
            creator_frequency = creator_profile.metadata.get('content_frequency', 1.0)
            candidate_frequency = candidate_profile.metadata.get('content_frequency', 1.0)
            frequency_compatibility = 1.0 - abs(creator_frequency - candidate_frequency) / max(creator_frequency, candidate_frequency)
            patterns['frequency_sync'] = frequency_compatibility
            
            # Audience engagement time patterns
            creator_peak_hours = creator_profile.metadata.get('peak_engagement_hours', [])
            candidate_peak_hours = candidate_profile.metadata.get('peak_engagement_hours', [])
            if creator_peak_hours and candidate_peak_hours:
                overlap_hours = set(creator_peak_hours) & set(candidate_peak_hours)
                time_compatibility = len(overlap_hours) / max(len(creator_peak_hours), len(candidate_peak_hours))
                patterns['engagement_timing'] = time_compatibility
            else:
                patterns['engagement_timing'] = 0.5
                
            # Communication style compatibility
            creator_style = creator_profile.metadata.get('communication_style', 'neutral')
            candidate_style = candidate_profile.metadata.get('communication_style', 'neutral')
            style_matrix = {
                ('formal', 'formal'): 0.9,
                ('casual', 'casual'): 0.9,
                ('creative', 'creative'): 0.95,
                ('formal', 'casual'): 0.6,
                ('formal', 'creative'): 0.5,
                ('casual', 'creative'): 0.8
            }
            patterns['communication_style'] = style_matrix.get((creator_style, candidate_style), 0.7)
            
            # Brand alignment score
            creator_values = set(creator_profile.metadata.get('brand_values', []))
            candidate_values = set(candidate_profile.metadata.get('brand_values', []))
            if creator_values and candidate_values:
                value_overlap = len(creator_values & candidate_values)
                total_values = len(creator_values | candidate_values)
                patterns['brand_alignment'] = value_overlap / total_values if total_values > 0 else 0.5
            else:
                patterns['brand_alignment'] = 0.5
                
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing behavioral patterns: {str(e)}")
            return {'frequency_sync': 0.5, 'engagement_timing': 0.5, 'communication_style': 0.5, 'brand_alignment': 0.5}
    
    async def predict_collaboration_success(
        self,
        creator_profile: 'CreatorProfile',
        candidate_profile: 'CreatorProfile',
        collaboration_type: str
    ) -> float:
        """
        AI-powered collaboration success prediction
        """
        try:
            # Historical success rate based on similar collaborations
            similar_collabs = await self._get_similar_collaborations(creator_profile, candidate_profile, collaboration_type)
            historical_score = self._calculate_historical_success_rate(similar_collabs)
            
            # Audience synergy analysis
            audience_synergy = await self._analyze_audience_synergy(creator_profile, candidate_profile)
            
            # Content compatibility analysis
            content_compatibility = await self._analyze_content_compatibility(creator_profile, candidate_profile)
            
            # Behavioral pattern compatibility
            behavioral_patterns = await self.analyze_behavioral_patterns(creator_profile, candidate_profile)
            behavioral_score = sum(behavioral_patterns.values()) / len(behavioral_patterns)
            
            # Market trend alignment
            market_trend_score = await self._analyze_market_trends(creator_profile, candidate_profile, collaboration_type)
            
            # Weighted success prediction
            success_probability = (
                historical_score * 0.25 +
                audience_synergy * 0.25 +
                content_compatibility * 0.20 +
                behavioral_score * 0.20 +
                market_trend_score * 0.10
            )
            
            return min(max(success_probability, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error predicting collaboration success: {str(e)}")
            return 0.5
    
    async def _get_similar_collaborations(
        self,
        creator_profile: 'CreatorProfile',
        candidate_profile: 'CreatorProfile',
        collaboration_type: str
    ) -> List[Dict[str, Any]]:
        """Get similar historical collaborations for success prediction"""
        try:
            # Query database for similar collaborations
            query = """
            SELECT success_rate, outcome_score, collaboration_duration
            FROM collaboration_history 
            WHERE (creator_type_1 = %s AND creator_type_2 = %s)
               OR (creator_type_1 = %s AND creator_type_2 = %s)
            AND collaboration_type = %s
            AND outcome_score IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 50
            """
            
            result = await self.db_session.execute(query, (
                creator_profile.content_type, candidate_profile.content_type,
                candidate_profile.content_type, creator_profile.content_type,
                collaboration_type
            ))
            
            return [dict(row) for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting similar collaborations: {str(e)}")
            return []
    
    async def _analyze_audience_synergy(
        self,
        creator_profile: 'CreatorProfile',
        candidate_profile: 'CreatorProfile'
    ) -> float:
        """Analyze potential audience synergy between creators"""
        try:
            # Get audience demographics
            creator_audience = creator_profile.metadata.get('audience_demographics', {})
            candidate_audience = candidate_profile.metadata.get('audience_demographics', {})
            
            # Calculate demographic overlap
            age_overlap = self._calculate_age_overlap(
                creator_audience.get('age_distribution', {}),
                candidate_audience.get('age_distribution', {})
            )
            
            # Geographic overlap
            geo_overlap = self._calculate_geographic_overlap(
                creator_audience.get('geographic_distribution', {}),
                candidate_audience.get('geographic_distribution', {})
            )
            
            # Interest overlap
            interest_overlap = self._calculate_interest_overlap(
                creator_audience.get('interests', []),
                candidate_audience.get('interests', [])
            )
            
            # Complementary audience potential (low overlap might be good for expansion)
            complementary_score = 1.0 - ((age_overlap + geo_overlap + interest_overlap) / 3.0)
            
            # Balance between overlap and complementarity
            synergy_score = (age_overlap * 0.3 + geo_overlap * 0.2 + interest_overlap * 0.3 + complementary_score * 0.2)
            
            return synergy_score
            
        except Exception as e:
            logger.error(f"Error analyzing audience synergy: {str(e)}")
            return 0.5
