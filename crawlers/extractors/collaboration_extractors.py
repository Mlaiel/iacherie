"""Collaboration Extractors - Industrial IA Collaboration and Matching System
==========================================================================

Ultra-advanced professional collaboration extraction and creator matching system.
Implements enterprise-grade collaboration detection, matching algorithms, and partnership analytics with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""
import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from pathlib import Path
import json
import hashlib
import uuid

# External libraries conditionally imported
try:
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import networkx as nx
    from transformers import pipeline, AutoModel, AutoTokenizer
    import torch
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False
    
try:
    from bs4 import BeautifulSoup
    import requests
    HAS_WEB_LIBS = True
except ImportError:
    HAS_WEB_LIBS = False

from .base import BaseExtractor, ExtractionRequest
from ...core.enums import PlatformType, ContentType
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaboration"""    DUET = "duet"
    FEATURE = "feature"
    REMIX = "remix"
    JOINT_PROJECT = "joint_project"
    CROSS_PROMOTION = "cross_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    LIVE_STREAM = "live_stream"
    PLAYLIST = "playlist"


class MatchingCriteria(Enum):
    """Creator matching criteria"""    GENRE_SIMILARITY = "genre_similarity"
    AUDIENCE_OVERLAP = "audience_overlap"
    ENGAGEMENT_COMPATIBILITY = "engagement_compatibility"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    FOLLOWER_COUNT_COMPATIBILITY = "follower_count_compatibility"
    CONTENT_STYLE_SIMILARITY = "content_style_similarity"
    COLLABORATION_HISTORY = "collaboration_history"


class CollaborationStatus(Enum):
    """Collaboration request status"""    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching"""    
    creator_id: str
    username: str
    display_name: str
    platforms: List[str]
    genres: List[str]
    follower_count: Dict[str, int]
    engagement_rates: Dict[str, float]
    content_types: List[str]
    geographic_location: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    availability: Dict[str, Any] = field(default_factory=dict)
    pricing: Dict[str, Any] = field(default_factory=dict)
    portfolio_urls: List[str] = field(default_factory=list)
    contact_info: Dict[str, str] = field(default_factory=dict)
    verified_status: bool = False
    reputation_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationMatch:
    """Collaboration match result"""    
    match_id: str
    primary_creator: str
    matched_creator: str
    compatibility_score: float
    matching_criteria: Dict[MatchingCriteria, float]
    suggested_collaboration_types: List[CollaborationType]
    mutual_benefits: List[str]
    potential_challenges: List[str]
    estimated_reach: Dict[str, int]
    confidence_level: float
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class CollaborationProposal:
    """Collaboration proposal"""    
    proposal_id: str
    initiator_id: str
    target_creator_id: str
    collaboration_type: CollaborationType
    proposal_details: Dict[str, Any]
    status: CollaborationStatus
    created_at: datetime
    response_deadline: Optional[datetime] = None
    terms: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CollaborationMetrics:
    """Collaboration performance metrics"""    
    collaboration_id: str
    participants: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    content_produced: List[str] = field(default_factory=list)
    combined_reach: Dict[str, int] = field(default_factory=dict)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    revenue_generated: Dict[str, float] = field(default_factory=dict)
    audience_growth: Dict[str, int] = field(default_factory=dict)
    success_score: float = 0.0


class BaseCollaborationExtractor(BaseExtractor):
    """Base class for collaboration extractors"""    
    def __init__(self, name: str):
        super().__init__(name)
        self.matching_weights = {
            MatchingCriteria.GENRE_SIMILARITY: 0.25,
            MatchingCriteria.AUDIENCE_OVERLAP: 0.20,
            MatchingCriteria.ENGAGEMENT_COMPATIBILITY: 0.15,
            MatchingCriteria.FOLLOWER_COUNT_COMPATIBILITY: 0.15,
            MatchingCriteria.CONTENT_STYLE_SIMILARITY: 0.15,
            MatchingCriteria.GEOGRAPHIC_PROXIMITY: 0.05,
            MatchingCriteria.COLLABORATION_HISTORY: 0.05
        }
    
    @abstractmethod
    async def extract_creator_profile(self, creator_id: str, platform: str) -> CreatorProfile:
        """Extract creator profile for collaboration matching"""        pass
    
    @abstractmethod
    async def find_collaboration_matches(self, creator_profile: CreatorProfile, 
                                       criteria: List[MatchingCriteria]) -> List[CollaborationMatch]:
        """Find potential collaboration matches"""        pass


class CreatorProfileExtractor(BaseCollaborationExtractor):
    """Extract and analyze creator profiles"""    
    def __init__(self):
        super().__init__("CreatorProfileExtractor")
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for creator profile extraction"""        return request.metadata and request.metadata.get('extract_type') == 'creator_profile'
    
    async def extract_creator_profile(self, creator_id: str, platform: str) -> CreatorProfile:
        """Extract comprehensive creator profile"""        try:
            # This would integrate with platform-specific extractors
            # For now, we'll create a comprehensive profile structure
            
            profile_data = await self._fetch_creator_data(creator_id, platform)
            
            # Extract follower counts across platforms
            follower_counts = await self._analyze_follower_metrics(profile_data)
            
            # Calculate engagement rates
            engagement_rates = await self._calculate_engagement_rates(profile_data)
            
            # Analyze content genres and styles
            genres = await self._analyze_content_genres(profile_data)
            content_types = await self._analyze_content_types(profile_data)
            
            # Extract collaboration preferences
            collaboration_prefs = await self._extract_collaboration_preferences(profile_data)
            
            # Calculate reputation score
            reputation_score = await self._calculate_reputation_score(profile_data)
            
            profile = CreatorProfile(
                creator_id=creator_id,
                username=profile_data.get('username', ''),
                display_name=profile_data.get('display_name', ''),
                platforms=[platform],  # Start with primary platform
                genres=genres,
                follower_count=follower_counts,
                engagement_rates=engagement_rates,
                content_types=content_types,
                geographic_location=profile_data.get('location'),
                languages=profile_data.get('languages', ['en']),
                collaboration_preferences=collaboration_prefs,
                verified_status=profile_data.get('verified', False),
                reputation_score=reputation_score
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Creator profile extraction failed: {e}")
            # Return minimal profile
            return CreatorProfile(
                creator_id=creator_id,
                username=creator_id,
                display_name=creator_id,
                platforms=[platform],
                genres=[],
                follower_count={platform: 0},
                engagement_rates={platform: 0.0},
                content_types=[]
            )
    
    async def _fetch_creator_data(self, creator_id: str, platform: str) -> Dict[str, Any]:
        """Fetch creator data from platform"""        # This would use platform-specific APIs
        # Returning mock data for demonstration
        return {
            'username': f'creator_{creator_id}',
            'display_name': f'Creator {creator_id}',
            'follower_count': 10000,
            'following_count': 500,
            'post_count': 200,
            'verified': False,
            'location': 'Global',
            'bio': 'Content creator passionate about music and entertainment',
            'languages': ['en'],
            'recent_posts': []
        }
    
    async def _analyze_follower_metrics(self, profile_data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze follower metrics across platforms"""        return {
            'total': profile_data.get('follower_count', 0),
            'active': int(profile_data.get('follower_count', 0) * 0.8),  # Estimated active followers
            'growth_rate': profile_data.get('growth_rate', 0)
        }
    
    async def _calculate_engagement_rates(self, profile_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate engagement rates"""        # Mock calculation based on available data
        follower_count = profile_data.get('follower_count', 1)
        post_count = profile_data.get('post_count', 1)
        
        # Estimated engagement rate
        base_engagement = 0.05  # 5% base rate
        activity_boost = min(post_count / 100, 0.02)  # Boost for activity
        
        return {
            'overall': base_engagement + activity_boost,
            'likes': base_engagement + activity_boost,
            'comments': (base_engagement + activity_boost) * 0.3,
            'shares': (base_engagement + activity_boost) * 0.1
        }
    
    async def _analyze_content_genres(self, profile_data: Dict[str, Any]) -> List[str]:
        """Analyze content genres from creator's content"""        bio = profile_data.get('bio', '').lower()
        
        # Simple keyword-based genre detection
        genre_keywords = {
            'music': ['music', 'song', 'artist', 'musician', 'band'],
            'comedy': ['comedy', 'funny', 'humor', 'jokes'],
            'gaming': ['gaming', 'gamer', 'games', 'esports'],
            'lifestyle': ['lifestyle', 'vlog', 'daily', 'life'],
            'fashion': ['fashion', 'style', 'outfit', 'beauty'],
            'tech': ['tech', 'technology', 'gadgets', 'reviews'],
            'fitness': ['fitness', 'workout', 'health', 'gym'],
            'food': ['food', 'cooking', 'recipe', 'chef'],
            'travel': ['travel', 'adventure', 'explore', 'vacation'],
            'education': ['education', 'tutorial', 'learn', 'teach']
        }
        
        detected_genres = []
        for genre, keywords in genre_keywords.items():
            if any(keyword in bio for keyword in keywords):
                detected_genres.append(genre)
        
        return detected_genres if detected_genres else ['general']
    
    async def _analyze_content_types(self, profile_data: Dict[str, Any]) -> List[str]:
        """Analyze content types creator produces"""        # This would analyze actual content
        # For now, return common types
        return ['video', 'image', 'audio', 'text']
    
    async def _extract_collaboration_preferences(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract collaboration preferences from profile"""        return {
            'open_to_collaborations': True,
            'preferred_collaboration_types': ['duet', 'feature', 'cross_promotion'],
            'collaboration_rate': 'negotiable',
            'response_time': '24-48 hours',
            'minimum_follower_requirement': 1000
        }
    
    async def _calculate_reputation_score(self, profile_data: Dict[str, Any]) -> float:
        """Calculate creator reputation score"""        factors = {
            'verified_status': 0.2 if profile_data.get('verified') else 0.0,
            'follower_count': min(profile_data.get('follower_count', 0) / 100000, 0.3),
            'post_consistency': min(profile_data.get('post_count', 0) / 1000, 0.2),
            'account_age': 0.1,  # Would calculate based on creation date
            'engagement_quality': 0.2  # Would analyze comment sentiment
        }
        
        return min(sum(factors.values()), 1.0)


class CollaborationMatcher(BaseCollaborationExtractor):
    """Advanced creator matching algorithm"""    
    def __init__(self):
        super().__init__("CollaborationMatcher")
        
        if HAS_ML_LIBS:
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.content_similarity_cache = {}
    
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for collaboration matching"""        return request.metadata and request.metadata.get('extract_type') == 'collaboration_matching'
    
    async def find_collaboration_matches(self, creator_profile: CreatorProfile, 
                                       criteria: List[MatchingCriteria],
                                       candidate_pool: List[CreatorProfile] = None) -> List[CollaborationMatch]:
        """Find potential collaboration matches"""        if not HAS_ML_LIBS:
            return []
        
        try:
            # Use provided candidate pool or fetch from database
            candidates = candidate_pool or await self._get_candidate_creators(creator_profile)
            
            matches = []
            
            for candidate in candidates:
                if candidate.creator_id == creator_profile.creator_id:
                    continue
                
                # Calculate compatibility score
                compatibility_scores = {}
                
                for criterion in criteria:
                    score = await self._calculate_criterion_score(
                        creator_profile, candidate, criterion
                    )
                    compatibility_scores[criterion] = score
                
                # Calculate overall compatibility
                overall_score = sum(
                    compatibility_scores.get(criterion, 0) * self.matching_weights.get(criterion, 0)
                    for criterion in criteria
                )
                
                # Only include high-quality matches
                if overall_score >= 0.6:  # 60% threshold
                    match = await self._create_collaboration_match(
                        creator_profile, candidate, overall_score, compatibility_scores
                    )
                    matches.append(match)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            return matches[:20]  # Return top 20 matches
            
        except Exception as e:
            self.logger.error(f"Collaboration matching failed: {e}")
            return []
    
    async def _get_candidate_creators(self, creator_profile: CreatorProfile) -> List[CreatorProfile]:
        """Get candidate creators for matching"""        # This would query the database for potential matches
        # For now, return empty list - would be implemented with actual database
        return []
    
    async def _calculate_criterion_score(self, creator1: CreatorProfile, 
                                       creator2: CreatorProfile,
                                       criterion: MatchingCriteria) -> float:
        """Calculate score for specific matching criterion"""        
        if criterion == MatchingCriteria.GENRE_SIMILARITY:
            return self._calculate_genre_similarity(creator1, creator2)
        
        elif criterion == MatchingCriteria.AUDIENCE_OVERLAP:
            return self._calculate_audience_overlap(creator1, creator2)
        
        elif criterion == MatchingCriteria.ENGAGEMENT_COMPATIBILITY:
            return self._calculate_engagement_compatibility(creator1, creator2)
        
        elif criterion == MatchingCriteria.FOLLOWER_COUNT_COMPATIBILITY:
            return self._calculate_follower_compatibility(creator1, creator2)
        
        elif criterion == MatchingCriteria.CONTENT_STYLE_SIMILARITY:
            return await self._calculate_content_similarity(creator1, creator2)
        
        elif criterion == MatchingCriteria.GEOGRAPHIC_PROXIMITY:
            return self._calculate_geographic_proximity(creator1, creator2)
        
        elif criterion == MatchingCriteria.COLLABORATION_HISTORY:
            return await self._calculate_collaboration_history_score(creator1, creator2)
        
        return 0.0
    
    def _calculate_genre_similarity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate genre similarity between creators"""        genres1 = set(creator1.genres)
        genres2 = set(creator2.genres)
        
        if not genres1 or not genres2:
            return 0.0
        
        intersection = len(genres1.intersection(genres2))
        union = len(genres1.union(genres2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_audience_overlap(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate potential audience overlap"""        # This would require actual audience data analysis
        # For now, use geographic and language similarity as proxy
        
        geo_similarity = 1.0 if creator1.geographic_location == creator2.geographic_location else 0.5
        
        lang_intersection = len(set(creator1.languages).intersection(set(creator2.languages)))
        lang_union = len(set(creator1.languages).union(set(creator2.languages)))
        lang_similarity = lang_intersection / lang_union if lang_union > 0 else 0.0
        
        return (geo_similarity + lang_similarity) / 2
    
    def _calculate_engagement_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate engagement rate compatibility"""        rate1 = creator1.engagement_rates.get('overall', 0)
        rate2 = creator2.engagement_rates.get('overall', 0)
        
        if rate1 == 0 or rate2 == 0:
            return 0.0
        
        # Higher similarity for closer engagement rates
        max_rate = max(rate1, rate2)
        min_rate = min(rate1, rate2)
        
        return min_rate / max_rate
    
    def _calculate_follower_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate follower count compatibility"""        count1 = creator1.follower_count.get('total', 0)
        count2 = creator2.follower_count.get('total', 0)
        
        if count1 == 0 or count2 == 0:
            return 0.0
        
        # Optimal ratio is within 1:10 range
        ratio = max(count1, count2) / min(count1, count2)
        
        if ratio <= 2:
            return 1.0
        elif ratio <= 5:
            return 0.8
        elif ratio <= 10:
            return 0.6
        else:
            return 0.2
    
    async def _calculate_content_similarity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate content style similarity"""        # This would analyze actual content using NLP/ML
        # For now, use content types as proxy
        
        types1 = set(creator1.content_types)
        types2 = set(creator2.content_types)
        
        if not types1 or not types2:
            return 0.0
        
        intersection = len(types1.intersection(types2))
        union = len(types1.union(types2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_geographic_proximity(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate geographic proximity score"""        if not creator1.geographic_location or not creator2.geographic_location:
            return 0.5  # Neutral score for unknown locations
        
        if creator1.geographic_location == creator2.geographic_location:
            return 1.0
        
        # This would use actual geographic distance calculation
        # For now, simple string matching
        return 0.7 if creator1.geographic_location.split(',')[0] == creator2.geographic_location.split(',')[0] else 0.3
    
    async def _calculate_collaboration_history_score(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate collaboration history compatibility"""        # This would analyze past collaboration success rates
        # For now, use reputation scores as proxy
        
        rep1 = creator1.reputation_score
        rep2 = creator2.reputation_score
        
        # Higher scores for both creators having good reputation
        return (rep1 + rep2) / 2
    
    async def _create_collaboration_match(self, creator1: CreatorProfile, creator2: CreatorProfile,
                                        overall_score: float, criterion_scores: Dict[MatchingCriteria, float]) -> CollaborationMatch:
        """Create collaboration match object"""        
        match_id = hashlib.md5(f"{creator1.creator_id}_{creator2.creator_id}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Suggest collaboration types based on compatibility
        suggested_types = self._suggest_collaboration_types(creator1, creator2, criterion_scores)
        
        # Calculate mutual benefits
        mutual_benefits = self._identify_mutual_benefits(creator1, creator2)
        
        # Identify potential challenges
        challenges = self._identify_potential_challenges(creator1, creator2)
        
        # Estimate combined reach
        estimated_reach = self._estimate_combined_reach(creator1, creator2)
        
        # Calculate confidence level
        confidence = self._calculate_confidence_level(overall_score, criterion_scores)
        
        return CollaborationMatch(
            match_id=match_id,
            primary_creator=creator1.creator_id,
            matched_creator=creator2.creator_id,
            compatibility_score=overall_score,
            matching_criteria=criterion_scores,
            suggested_collaboration_types=suggested_types,
            mutual_benefits=mutual_benefits,
            potential_challenges=challenges,
            estimated_reach=estimated_reach,
            confidence_level=confidence,
            expires_at=datetime.now() + timedelta(days=30)
        )
    
    def _suggest_collaboration_types(self, creator1: CreatorProfile, creator2: CreatorProfile,
                                   scores: Dict[MatchingCriteria, float]) -> List[CollaborationType]:
        """Suggest collaboration types based on compatibility"""        suggestions = []
        
        # High genre similarity -> musical collaborations
        if scores.get(MatchingCriteria.GENRE_SIMILARITY, 0) > 0.8:
            if 'music' in creator1.genres and 'music' in creator2.genres:
                suggestions.extend([CollaborationType.DUET, CollaborationType.FEATURE, CollaborationType.REMIX])
        
        # High follower compatibility -> cross promotion
        if scores.get(MatchingCriteria.FOLLOWER_COUNT_COMPATIBILITY, 0) > 0.7:
            suggestions.append(CollaborationType.CROSS_PROMOTION)
        
        # High content similarity -> joint projects
        if scores.get(MatchingCriteria.CONTENT_STYLE_SIMILARITY, 0) > 0.7:
            suggestions.append(CollaborationType.JOINT_PROJECT)
        
        # Geographic proximity -> live streams
        if scores.get(MatchingCriteria.GEOGRAPHIC_PROXIMITY, 0) > 0.8:
            suggestions.append(CollaborationType.LIVE_STREAM)
        
        # Default suggestions
        if not suggestions:
            suggestions = [CollaborationType.CROSS_PROMOTION, CollaborationType.PLAYLIST]
        
        return list(set(suggestions))  # Remove duplicates
    
    def _identify_mutual_benefits(self, creator1: CreatorProfile, creator2: CreatorProfile) -> List[str]:
        """Identify mutual benefits of collaboration"""        benefits = []
        
        # Audience expansion
        if creator1.follower_count.get('total', 0) != creator2.follower_count.get('total', 0):
            benefits.append("Audience expansion through cross-promotion")
        
        # Genre diversification
        if not set(creator1.genres).intersection(set(creator2.genres)):
            benefits.append("Genre diversification and new audience segments")
        
        # Content variety
        if set(creator1.content_types) != set(creator2.content_types):
            benefits.append("Content format variety and creative synergy")
        
        # Geographic reach
        if creator1.geographic_location != creator2.geographic_location:
            benefits.append("Geographic reach expansion")
        
        # Skill complement
        benefits.append("Complementary skills and creative perspectives")
        
        # Engagement boost
        benefits.append("Potential engagement rate improvement")
        
        return benefits
    
    def _identify_potential_challenges(self, creator1: CreatorProfile, creator2: CreatorProfile) -> List[str]:
        """Identify potential collaboration challenges"""        challenges = []
        
        # Large follower gap
        count1 = creator1.follower_count.get('total', 0)
        count2 = creator2.follower_count.get('total', 0)
        ratio = max(count1, count2) / max(min(count1, count2), 1)
        
        if ratio > 10:
            challenges.append("Significant follower count disparity")
        
        # Different engagement rates
        rate1 = creator1.engagement_rates.get('overall', 0)
        rate2 = creator2.engagement_rates.get('overall', 0)
        
        if abs(rate1 - rate2) > 0.03:  # 3% difference
            challenges.append("Different engagement rate patterns")
        
        # Geographic distance
        if creator1.geographic_location != creator2.geographic_location:
            challenges.append("Geographic distance for live collaborations")
        
        # No genre overlap
        if not set(creator1.genres).intersection(set(creator2.genres)):
            challenges.append("No common content genres")
        
        # Language barriers
        if not set(creator1.languages).intersection(set(creator2.languages)):
            challenges.append("Potential language communication barriers")
        
        return challenges
    
    def _estimate_combined_reach(self, creator1: CreatorProfile, creator2: CreatorProfile) -> Dict[str, int]:
        """Estimate combined reach of collaboration"""        count1 = creator1.follower_count.get('total', 0)
        count2 = creator2.follower_count.get('total', 0)
        
        # Estimate audience overlap (typically 10-30% for similar creators)
        estimated_overlap = min(count1, count2) * 0.2
        
        # Combined unique reach
        combined_reach = count1 + count2 - estimated_overlap
        
        # Engagement boost from collaboration (typically 20-50% increase)
        engagement_boost = 1.3
        
        return {
            'total_followers': int(combined_reach),
            'estimated_views': int(combined_reach * 0.1 * engagement_boost),  # 10% view rate
            'estimated_engagement': int(combined_reach * 0.05 * engagement_boost),  # 5% engagement rate
            'potential_new_followers': int((count1 + count2) * 0.02)  # 2% conversion rate
        }
    
    def _calculate_confidence_level(self, overall_score: float, 
                                  criterion_scores: Dict[MatchingCriteria, float]) -> float:
        """Calculate confidence level in match"""        # High confidence requires high overall score and balanced criteria
        score_variance = np.var(list(criterion_scores.values())) if criterion_scores else 1.0
        
        # Lower variance = higher confidence
        variance_penalty = min(score_variance * 2, 0.3)
        
        confidence = overall_score - variance_penalty
        
        return max(0.0, min(1.0, confidence))


class CollaborationAnalyzer:
    """Analyze collaboration performance and ROI"""    
    def __init__(self):
        self.performance_cache = {}
    
    async def analyze_collaboration_performance(self, collaboration_metrics: CollaborationMetrics) -> Dict[str, Any]:
        """Analyze collaboration performance"""        try:
            analysis = {
                'collaboration_id': collaboration_metrics.collaboration_id,
                'performance_summary': {},
                'reach_analysis': {},
                'engagement_analysis': {},
                'roi_analysis': {},
                'recommendations': []
            }
            
            # Performance summary
            duration = (collaboration_metrics.end_date - collaboration_metrics.start_date).days if collaboration_metrics.end_date else 0
            content_count = len(collaboration_metrics.content_produced)
            
            analysis['performance_summary'] = {
                'duration_days': duration,
                'content_pieces_created': content_count,
                'participants_count': len(collaboration_metrics.participants),
                'success_score': collaboration_metrics.success_score,
                'status': 'completed' if collaboration_metrics.end_date else 'ongoing'
            }
            
            # Reach analysis
            total_reach = sum(collaboration_metrics.combined_reach.values())
            avg_reach_per_content = total_reach / content_count if content_count > 0 else 0
            
            analysis['reach_analysis'] = {
                'total_combined_reach': total_reach,
                'average_reach_per_content': avg_reach_per_content,
                'platform_breakdown': collaboration_metrics.combined_reach,
                'reach_efficiency': total_reach / max(duration, 1)
            }
            
            # Engagement analysis
            avg_engagement = np.mean(list(collaboration_metrics.engagement_metrics.values())) if collaboration_metrics.engagement_metrics else 0
            
            analysis['engagement_analysis'] = {
                'average_engagement_rate': avg_engagement,
                'platform_engagement': collaboration_metrics.engagement_metrics,
                'engagement_trend': 'positive' if avg_engagement > 0.05 else 'needs_improvement'
            }
            
            # ROI analysis
            total_revenue = sum(collaboration_metrics.revenue_generated.values())
            revenue_per_day = total_revenue / max(duration, 1)
            
            analysis['roi_analysis'] = {
                'total_revenue_generated': total_revenue,
                'revenue_per_day': revenue_per_day,
                'revenue_per_content': total_revenue / content_count if content_count > 0 else 0,
                'platform_revenue_breakdown': collaboration_metrics.revenue_generated
            }
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(collaboration_metrics, analysis)
            analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"Collaboration analysis failed: {e}")
            return {}
    
    def _generate_performance_recommendations(self, metrics: CollaborationMetrics, 
                                            analysis: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""        recommendations = []
        
        # Engagement recommendations
        avg_engagement = analysis['engagement_analysis']['average_engagement_rate']
        if avg_engagement < 0.03:
            recommendations.append("Consider improving content quality and audience targeting")
        
        # Content frequency recommendations
        duration = analysis['performance_summary']['duration_days']
        content_count = analysis['performance_summary']['content_pieces_created']
        content_frequency = content_count / max(duration, 1)
        
        if content_frequency < 0.2:  # Less than 1 post per 5 days
            recommendations.append("Increase content creation frequency for better audience retention")
        
        # Platform diversification
        platform_count = len(metrics.combined_reach)
        if platform_count < 3:
            recommendations.append("Consider expanding to additional platforms for broader reach")
        
        # Revenue optimization
        total_revenue = analysis['roi_analysis']['total_revenue_generated']
        if total_revenue < 100:  # Low revenue threshold
            recommendations.append("Explore monetization strategies and brand partnership opportunities")
        
        # Collaboration duration
        if duration > 90:  # Long collaboration
            recommendations.append("Consider breaking long collaborations into phases for sustained engagement")
        elif duration < 7:  # Very short collaboration
            recommendations.append("Extend collaboration duration for better relationship building")
        
        return recommendations


class CollaborationExtractorFactory:
    """Factory for creating collaboration extractors"""    
    @staticmethod
    def create_extractor(extractor_type: str) -> BaseCollaborationExtractor:
        """Create appropriate collaboration extractor"""        extractors = {
            'profile': CreatorProfileExtractor,
            'matcher': CollaborationMatcher
        }
        
        extractor_class = extractors.get(extractor_type.lower())
        if not extractor_class:
            raise ValueError(f"No collaboration extractor available for type: {extractor_type}")
        
        return extractor_class()
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported extractor types"""        return ['profile', 'matcher']


__all__ = [
    'CollaborationType',
    'MatchingCriteria',
    'CollaborationStatus',
    'CreatorProfile',
    'CollaborationMatch',
    'CollaborationProposal',
    'CollaborationMetrics',
    'BaseCollaborationExtractor',
    'CreatorProfileExtractor',
    'CollaborationMatcher',
    'CollaborationAnalyzer',
    'CollaborationExtractorFactory'
]
