"""Creator Collaboration Matching Parsers Module
=============================================

Ultra-advanced parsers for creator collaboration matching, partnership analytics,
and collaborative content discovery across platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de

Development Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI systems
- ML Engineer: Content analysis and fingerprinting
- Audio Processing Specialist: Multi-format audio analysis  
- DevOps Engineer: Infrastructure and deployment
- Database Administrator: Performance optimization
- Security Expert: Content protection and compliance
- Microservices Architect: Scalable system design
"""import asyncio
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import networkx as nx

from .exceptions import CollaborationParsingError, MatchingError, AnalysisError
from .parser_config import ParserConfig


class CreatorTier(Enum):
    """Creator tier classification"""    MEGA_INFLUENCER = "mega"      # 1M+ followers
    MACRO_INFLUENCER = "macro"    # 100K-1M followers
    MICRO_INFLUENCER = "micro"    # 10K-100K followers
    NANO_INFLUENCER = "nano"      # 1K-10K followers
    EMERGING = "emerging"         # <1K followers


class ContentCategory(Enum):
    """Content category types"""    MUSIC = "music"
    GAMING = "gaming"
    BEAUTY = "beauty"
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    EDUCATION = "education"
    COMEDY = "comedy"
    ART = "art"
    BUSINESS = "business"
    FASHION = "fashion"
    SPORTS = "sports"
    FAMILY = "family"


class CollaborationType(Enum):
    """Types of collaboration"""    FEATURING = "featuring"       # Music featuring
    GUEST_APPEARANCE = "guest"    # Podcast/video guest
    JOINT_CONTENT = "joint"       # Collaborative content
    CROSS_PROMOTION = "cross_promo"  # Mutual promotion
    SPONSORSHIP = "sponsorship"   # Sponsored content
    CHALLENGE = "challenge"       # Social media challenges
    DUET_COLLAB = "duet"         # TikTok duets, etc.
    REMIX = "remix"              # Content remixes
    SERIES = "series"            # Multi-part collaboration


@dataclass
class CreatorProfile:
    """Comprehensive creator profile"""    creator_id: str
    username: str
    display_name: str
    platforms: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    categories: List[ContentCategory] = field(default_factory=list)
    tier: CreatorTier = CreatorTier.EMERGING
    total_followers: int = 0
    engagement_rate: float = 0.0
    content_quality_score: float = 0.0
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    content_analysis: Dict[str, Any] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    brand_safety_score: float = 0.0
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)
    contact_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class CollaborationMatch:
    """Potential collaboration match"""    primary_creator: CreatorProfile
    matched_creator: CreatorProfile
    compatibility_score: float
    collaboration_types: List[CollaborationType]
    match_reasons: List[str]
    estimated_reach: int
    synergy_score: float
    risk_factors: List[str] = field(default_factory=list)
    recommended_approach: str = ""
    potential_revenue: float = 0.0


@dataclass
class CollaborationAnalytics:
    """Analytics for collaboration opportunities"""    total_matches: int = 0
    high_potential_matches: int = 0
    category_distribution: Dict[ContentCategory, int] = field(default_factory=dict)
    tier_distribution: Dict[CreatorTier, int] = field(default_factory=dict)
    average_compatibility: float = 0.0
    trending_collaboration_types: List[CollaborationType] = field(default_factory=list)
    market_opportunities: List[Dict[str, Any]] = field(default_factory=list)


class CreatorProfileParser:
    """Advanced creator profile analysis and parsing"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def analyze_creator_profile(
        self, 
        creator_data: Dict[str, Any],
        platforms: List[str] = None
    ) -> CreatorProfile:
        """Analyze and create comprehensive creator profile"""        try:
            profile = CreatorProfile(
                creator_id=creator_data.get('id', ''),
                username=creator_data.get('username', ''),
                display_name=creator_data.get('display_name', '')
            )
            
            # Analyze each platform
            if platforms is None:
                platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'spotify']
            
            total_followers = 0
            platform_data = {}
            
            for platform in platforms:
                if platform in creator_data:
                    platform_analysis = await self._analyze_platform_presence(
                        creator_data[platform], platform
                    )
                    platform_data[platform] = platform_analysis
                    total_followers += platform_analysis.get('followers', 0)
            
            profile.platforms = platform_data
            profile.total_followers = total_followers
            
            # Determine tier
            profile.tier = self._determine_creator_tier(total_followers)
            
            # Analyze content categories
            profile.categories = await self._analyze_content_categories(creator_data)
            
            # Calculate engagement rate
            profile.engagement_rate = await self._calculate_overall_engagement(platform_data)
            
            # Analyze content quality
            profile.content_quality_score = await self._assess_content_quality(creator_data)
            
            # Extract collaboration history
            profile.collaboration_history = await self._extract_collaboration_history(creator_data)
            
            # Analyze audience demographics
            profile.audience_demographics = await self._analyze_audience_demographics(creator_data)
            
            # Calculate brand safety score
            profile.brand_safety_score = await self._calculate_brand_safety_score(creator_data)
            
            # Extract collaboration preferences
            profile.collaboration_preferences = await self._extract_collaboration_preferences(creator_data)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Creator profile analysis failed: {e}")
            raise CollaborationParsingError(f"Failed to analyze creator profile: {e}")
    
    async def _analyze_platform_presence(self, platform_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Analyze creator's presence on specific platform"""        analysis = {
            'platform': platform,
            'followers': platform_data.get('followers', 0),
            'following': platform_data.get('following', 0),
            'posts_count': platform_data.get('posts_count', 0),
            'verified': platform_data.get('verified', False),
            'engagement_metrics': {},
            'content_types': [],
            'posting_frequency': 0.0,
            'growth_rate': 0.0
        }
        
        # Platform-specific analysis
        if platform == 'youtube':
            analysis.update({
                'subscribers': platform_data.get('subscribers', 0),
                'total_views': platform_data.get('total_views', 0),
                'video_count': platform_data.get('video_count', 0),
                'average_views': platform_data.get('average_views', 0),
                'channel_age_days': platform_data.get('channel_age_days', 0)
            })
            
            # Calculate engagement rate for YouTube
            if analysis['total_views'] > 0 and analysis['subscribers'] > 0:
                # Simplified engagement calculation
                analysis['engagement_rate'] = min(
                    (analysis['average_views'] / max(analysis['subscribers'], 1)) * 100, 100
                )
        
        elif platform == 'instagram':
            analysis.update({
                'posts': platform_data.get('posts', 0),
                'stories_count': platform_data.get('stories_count', 0),
                'reels_count': platform_data.get('reels_count', 0),
                'igtv_count': platform_data.get('igtv_count', 0)
            })
            
            # Instagram engagement calculation
            total_engagement = platform_data.get('total_likes', 0) + platform_data.get('total_comments', 0)
            if analysis['followers'] > 0 and analysis['posts'] > 0:
                analysis['engagement_rate'] = (total_engagement / (analysis['followers'] * analysis['posts'])) * 100
        
        elif platform == 'tiktok':
            analysis.update({
                'videos_count': platform_data.get('videos_count', 0),
                'total_likes': platform_data.get('total_likes', 0),
                'total_shares': platform_data.get('total_shares', 0)
            })
        
        elif platform == 'spotify':
            analysis.update({
                'monthly_listeners': platform_data.get('monthly_listeners', 0),
                'tracks_count': platform_data.get('tracks_count', 0),
                'playlists_count': platform_data.get('playlists_count', 0),
                'total_streams': platform_data.get('total_streams', 0)
            })
        
        # Calculate posting frequency (posts per week)
        if analysis['posts_count'] > 0 and 'account_age_days' in platform_data:
            weeks_active = max(platform_data['account_age_days'] / 7, 1)
            analysis['posting_frequency'] = analysis['posts_count'] / weeks_active
        
        return analysis
    
    def _determine_creator_tier(self, total_followers: int) -> CreatorTier:
        """Determine creator tier based on follower count"""        if total_followers >= 1_000_000:
            return CreatorTier.MEGA_INFLUENCER
        elif total_followers >= 100_000:
            return CreatorTier.MACRO_INFLUENCER
        elif total_followers >= 10_000:
            return CreatorTier.MICRO_INFLUENCER
        elif total_followers >= 1_000:
            return CreatorTier.NANO_INFLUENCER
        else:
            return CreatorTier.EMERGING
    
    async def _analyze_content_categories(self, creator_data: Dict[str, Any]) -> List[ContentCategory]:
        """Analyze and categorize creator's content"""        categories = []
        
        # Analyze bio/description text
        bio_text = ""
        for field in ['bio', 'description', 'about', 'channel_description']:
            if field in creator_data:
                bio_text += f" {creator_data[field]}"
        
        bio_text = bio_text.lower()
        
        # Category keywords mapping
        category_keywords = {
            ContentCategory.MUSIC: ['music', 'singer', 'artist', 'song', 'album', 'musician', 'producer'],
            ContentCategory.GAMING: ['gaming', 'gamer', 'games', 'esports', 'twitch', 'stream'],
            ContentCategory.BEAUTY: ['beauty', 'makeup', 'skincare', 'cosmetics', 'fashion'],
            ContentCategory.TECH: ['tech', 'technology', 'software', 'coding', 'programming', 'ai'],
            ContentCategory.LIFESTYLE: ['lifestyle', 'vlog', 'daily', 'life', 'personal'],
            ContentCategory.FITNESS: ['fitness', 'workout', 'gym', 'health', 'training', 'exercise'],
            ContentCategory.FOOD: ['food', 'cooking', 'recipe', 'chef', 'restaurant', 'cuisine'],
            ContentCategory.TRAVEL: ['travel', 'adventure', 'explore', 'journey', 'vacation'],
            ContentCategory.EDUCATION: ['education', 'tutorial', 'teach', 'learn', 'course', 'study'],
            ContentCategory.COMEDY: ['comedy', 'funny', 'humor', 'jokes', 'entertainment'],
            ContentCategory.ART: ['art', 'artist', 'creative', 'design', 'drawing', 'painting'],
            ContentCategory.BUSINESS: ['business', 'entrepreneur', 'startup', 'marketing', 'finance'],
            ContentCategory.FASHION: ['fashion', 'style', 'outfit', 'trends', 'clothing'],
            ContentCategory.SPORTS: ['sports', 'athlete', 'football', 'basketball', 'soccer'],
            ContentCategory.FAMILY: ['family', 'parenting', 'kids', 'children', 'mom', 'dad']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in bio_text)
            if score > 0:
                category_scores[category] = score
        
        # Add categories with highest scores
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        categories = [cat for cat, score in sorted_categories[:3]]  # Top 3 categories
        
        # If no categories found, try to infer from platform data
        if not categories:
            if 'spotify' in creator_data:
                categories.append(ContentCategory.MUSIC)
            elif 'twitch' in creator_data:
                categories.append(ContentCategory.GAMING)
            else:
                categories.append(ContentCategory.LIFESTYLE)  # Default
        
        return categories
    
    async def _calculate_overall_engagement(self, platform_data: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall engagement rate across platforms"""        total_engagement = 0
        total_weight = 0
        
        for platform, data in platform_data.items():
            engagement_rate = data.get('engagement_rate', 0)
            followers = data.get('followers', 0)
            
            if engagement_rate > 0 and followers > 0:
                # Weight by follower count
                weight = math.log10(max(followers, 1))
                total_engagement += engagement_rate * weight
                total_weight += weight
        
        return total_engagement / max(total_weight, 1)
    
    async def _assess_content_quality(self, creator_data: Dict[str, Any]) -> float:
        """Assess overall content quality score"""        quality_score = 0.5  # Base score
        
        # Check for verified status
        verified_count = sum(1 for platform_data in creator_data.values() 
                           if isinstance(platform_data, dict) and platform_data.get('verified'))
        quality_score += verified_count * 0.1
        
        # Check for consistent posting
        posting_frequencies = []
        for platform_data in creator_data.values():
            if isinstance(platform_data, dict) and 'posting_frequency' in platform_data:
                posting_frequencies.append(platform_data['posting_frequency'])
        
        if posting_frequencies:
            avg_posting_freq = sum(posting_frequencies) / len(posting_frequencies)
            # Optimal posting frequency bonus (1-3 posts per week)
            if 1 <= avg_posting_freq <= 3:
                quality_score += 0.2
            elif 0.5 <= avg_posting_freq < 1 or 3 < avg_posting_freq <= 5:
                quality_score += 0.1
        
        # Check for multi-platform presence
        platform_count = sum(1 for key in creator_data.keys() 
                           if key in ['youtube', 'instagram', 'tiktok', 'twitter', 'spotify'])
        quality_score += min(platform_count * 0.05, 0.15)
        
        return min(quality_score, 1.0)
    
    async def _extract_collaboration_history(self, creator_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract collaboration history from creator data"""        collaborations = []
        
        # This would typically involve analyzing:
        # - Video titles/descriptions for "feat.", "with", "collab"
        # - Guest appearances
        # - Shared content
        # - Cross-mentions
        
        # Placeholder implementation
        return collaborations
    
    async def _analyze_audience_demographics(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience demographics"""        demographics = {
            'age_groups': {},
            'gender_distribution': {},
            'geographic_distribution': {},
            'interests': [],
            'engagement_patterns': {}
        }
        
        # This would integrate with platform analytics APIs
        # Placeholder data
        return demographics
    
    async def _calculate_brand_safety_score(self, creator_data: Dict[str, Any]) -> float:
        """Calculate brand safety score"""        safety_score = 0.8  # Base safe score
        
        # Check for controversial content indicators
        content_text = ""
        for field in ['bio', 'description', 'recent_posts']:
            if field in creator_data:
                if isinstance(creator_data[field], list):
                    content_text += " ".join(str(item) for item in creator_data[field])
                else:
                    content_text += str(creator_data[field])
        
        content_text = content_text.lower()
        
        # Risk keywords (would be more comprehensive in production)
        risk_keywords = ['hate', 'violence', 'drugs', 'illegal', 'scam', 'fraud']
        risk_count = sum(1 for keyword in risk_keywords if keyword in content_text)
        
        # Reduce score based on risk factors
        safety_score -= risk_count * 0.1
        
        # Increase score for positive indicators
        positive_keywords = ['education', 'family', 'positive', 'inspire', 'help']
        positive_count = sum(1 for keyword in positive_keywords if keyword in content_text)
        safety_score += positive_count * 0.05
        
        return max(0.0, min(safety_score, 1.0))
    
    async def _extract_collaboration_preferences(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract collaboration preferences from creator data"""        preferences = {
            'collaboration_types': [],
            'preferred_brands': [],
            'budget_range': {'min': 0, 'max': 0},
            'availability': {},
            'requirements': [],
            'contact_preferences': []
        }
        
        # This would analyze:
        # - Past collaboration patterns
        # - Bio mentions of collaboration interests
        # - Media kit information
        # - Rate cards
        
        return preferences


class CollaborationMatchingEngine:
    """Advanced AI-powered collaboration matching engine"""    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.profile_parser = CreatorProfileParser(config)
    
    async def find_collaboration_matches(
        self,
        target_creator: CreatorProfile,
        candidate_creators: List[CreatorProfile],
        collaboration_types: List[CollaborationType] = None,
        min_compatibility_score: float = 0.6
    ) -> List[CollaborationMatch]:
        """Find potential collaboration matches using AI algorithms"""        try:
            matches = []
            
            for candidate in candidate_creators:
                # Skip self-matching
                if candidate.creator_id == target_creator.creator_id:
                    continue
                
                # Calculate compatibility score
                compatibility = await self._calculate_compatibility_score(target_creator, candidate)
                
                if compatibility >= min_compatibility_score:
                    # Determine suitable collaboration types
                    suitable_types = await self._determine_collaboration_types(
                        target_creator, candidate, collaboration_types
                    )
                    
                    if suitable_types:
                        match = await self._create_collaboration_match(
                            target_creator, candidate, compatibility, suitable_types
                        )
                        matches.append(match)
            
            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Collaboration matching failed: {e}")
            raise MatchingError(f"Failed to find collaboration matches: {e}")
    
    async def _calculate_compatibility_score(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile
    ) -> float:
        """Calculate compatibility score between two creators"""        try:
            scores = []
            
            # 1. Category overlap score
            category_score = self._calculate_category_compatibility(creator1, creator2)
            scores.append(('category', category_score, 0.25))
            
            # 2. Tier compatibility score
            tier_score = self._calculate_tier_compatibility(creator1, creator2)
            scores.append(('tier', tier_score, 0.15))
            
            # 3. Audience size compatibility
            audience_score = self._calculate_audience_compatibility(creator1, creator2)
            scores.append(('audience', audience_score, 0.20))
            
            # 4. Engagement compatibility
            engagement_score = self._calculate_engagement_compatibility(creator1, creator2)
            scores.append(('engagement', engagement_score, 0.15))
            
            # 5. Content quality compatibility
            quality_score = self._calculate_quality_compatibility(creator1, creator2)
            scores.append(('quality', quality_score, 0.10))
            
            # 6. Brand safety compatibility
            safety_score = self._calculate_safety_compatibility(creator1, creator2)
            scores.append(('safety', safety_score, 0.10))
            
            # 7. Platform overlap score
            platform_score = self._calculate_platform_overlap(creator1, creator2)
            scores.append(('platform', platform_score, 0.05))
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in scores)
            
            return min(max(total_score, 0.0), 1.0)
            
        except Exception as e:
            self.logger.warning(f"Compatibility calculation failed: {e}")
            return 0.0
    
    def _calculate_category_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate category compatibility score"""        categories1 = set(creator1.categories)
        categories2 = set(creator2.categories)
        
        if not categories1 or not categories2:
            return 0.5  # Neutral score if no categories
        
        # Calculate Jaccard similarity
        intersection = len(categories1.intersection(categories2))
        union = len(categories1.union(categories2))
        
        if union == 0:
            return 0.0
        
        jaccard_score = intersection / union
        
        # Bonus for complementary categories
        complementary_pairs = [
            (ContentCategory.MUSIC, ContentCategory.ART),
            (ContentCategory.FITNESS, ContentCategory.LIFESTYLE),
            (ContentCategory.TECH, ContentCategory.EDUCATION),
            (ContentCategory.FOOD, ContentCategory.TRAVEL),
            (ContentCategory.BEAUTY, ContentCategory.FASHION)
        ]
        
        for cat1, cat2 in complementary_pairs:
            if (cat1 in categories1 and cat2 in categories2) or (cat2 in categories1 and cat1 in categories2):
                jaccard_score += 0.2  # Bonus for complementary categories
                break
        
        return min(jaccard_score, 1.0)
    
    def _calculate_tier_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate tier compatibility score"""        tier_values = {
            CreatorTier.EMERGING: 1,
            CreatorTier.NANO_INFLUENCER: 2,
            CreatorTier.MICRO_INFLUENCER: 3,
            CreatorTier.MACRO_INFLUENCER: 4,
            CreatorTier.MEGA_INFLUENCER: 5
        }
        
        tier1_value = tier_values.get(creator1.tier, 1)
        tier2_value = tier_values.get(creator2.tier, 1)
        
        # Calculate compatibility based on tier difference
        tier_diff = abs(tier1_value - tier2_value)
        
        if tier_diff == 0:
            return 1.0  # Same tier
        elif tier_diff == 1:
            return 0.8  # Adjacent tiers
        elif tier_diff == 2:
            return 0.6  # Two tiers apart
        else:
            return 0.3  # Very different tiers
    
    def _calculate_audience_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate audience size compatibility"""        followers1 = creator1.total_followers
        followers2 = creator2.total_followers
        
        if followers1 == 0 or followers2 == 0:
            return 0.5
        
        # Calculate ratio
        ratio = min(followers1, followers2) / max(followers1, followers2)
        
        # Score based on ratio (closer ratios = better compatibility)
        if ratio >= 0.5:
            return 1.0
        elif ratio >= 0.2:
            return 0.8
        elif ratio >= 0.1:
            return 0.6
        elif ratio >= 0.05:
            return 0.4
        else:
            return 0.2
    
    def _calculate_engagement_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate engagement rate compatibility"""        engagement1 = creator1.engagement_rate
        engagement2 = creator2.engagement_rate
        
        if engagement1 == 0 or engagement2 == 0:
            return 0.5
        
        # Calculate similarity in engagement rates
        ratio = min(engagement1, engagement2) / max(engagement1, engagement2)
        return ratio
    
    def _calculate_quality_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate content quality compatibility"""        quality1 = creator1.content_quality_score
        quality2 = creator2.content_quality_score
        
        # Both should have reasonably high quality scores
        min_quality = min(quality1, quality2)
        avg_quality = (quality1 + quality2) / 2
        
        # Score based on minimum quality (both need to be good)
        return min_quality * 0.7 + avg_quality * 0.3
    
    def _calculate_safety_compatibility(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate brand safety compatibility"""        safety1 = creator1.brand_safety_score
        safety2 = creator2.brand_safety_score
        
        # Both should have high safety scores
        return min(safety1, safety2)
    
    def _calculate_platform_overlap(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate platform overlap score"""        platforms1 = set(creator1.platforms.keys())
        platforms2 = set(creator2.platforms.keys())
        
        if not platforms1 or not platforms2:
            return 0.0
        
        intersection = len(platforms1.intersection(platforms2))
        union = len(platforms1.union(platforms2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _determine_collaboration_types(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        requested_types: List[CollaborationType] = None
    ) -> List[CollaborationType]:
        """Determine suitable collaboration types for creators"""        suitable_types = []
        
        # Music collaborations
        if ContentCategory.MUSIC in creator1.categories and ContentCategory.MUSIC in creator2.categories:
            suitable_types.extend([CollaborationType.FEATURING, CollaborationType.REMIX])
        
        # Video collaborations
        if ('youtube' in creator1.platforms and 'youtube' in creator2.platforms):
            suitable_types.extend([
                CollaborationType.GUEST_APPEARANCE, 
                CollaborationType.JOINT_CONTENT,
                CollaborationType.SERIES
            ])
        
        # Social media collaborations
        if ('instagram' in creator1.platforms and 'instagram' in creator2.platforms) or \
           ('tiktok' in creator1.platforms and 'tiktok' in creator2.platforms):
            suitable_types.extend([
                CollaborationType.CHALLENGE,
                CollaborationType.DUET_COLLAB,
                CollaborationType.CROSS_PROMOTION
            ])
        
        # General collaborations based on tiers
        if creator1.tier in [CreatorTier.MACRO_INFLUENCER, CreatorTier.MEGA_INFLUENCER] or \
           creator2.tier in [CreatorTier.MACRO_INFLUENCER, CreatorTier.MEGA_INFLUENCER]:
            suitable_types.append(CollaborationType.SPONSORSHIP)
        
        # Filter by requested types if specified
        if requested_types:
            suitable_types = [t for t in suitable_types if t in requested_types]
        
        return list(set(suitable_types))  # Remove duplicates
    
    async def _create_collaboration_match(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        compatibility_score: float,
        collaboration_types: List[CollaborationType]
    ) -> CollaborationMatch:
        """Create a complete collaboration match object"""        
        # Calculate estimated reach
        estimated_reach = int((creator1.total_followers + creator2.total_followers) * 0.7)  # 70% overlap assumption
        
        # Calculate synergy score
        synergy_score = await self._calculate_synergy_score(creator1, creator2)
        
        # Identify risk factors
        risk_factors = await self._identify_risk_factors(creator1, creator2)
        
        # Generate match reasons
        match_reasons = await self._generate_match_reasons(creator1, creator2, compatibility_score)
        
        # Recommend approach
        recommended_approach = await self._recommend_collaboration_approach(
            creator1, creator2, collaboration_types
        )
        
        # Estimate potential revenue
        potential_revenue = await self._estimate_collaboration_revenue(
            creator1, creator2, collaboration_types, estimated_reach
        )
        
        return CollaborationMatch(
            primary_creator=creator1,
            matched_creator=creator2,
            compatibility_score=compatibility_score,
            collaboration_types=collaboration_types,
            match_reasons=match_reasons,
            estimated_reach=estimated_reach,
            synergy_score=synergy_score,
            risk_factors=risk_factors,
            recommended_approach=recommended_approach,
            potential_revenue=potential_revenue
        )
    
    async def _calculate_synergy_score(self, creator1: CreatorProfile, creator2: CreatorProfile) -> float:
        """Calculate synergy score between creators"""        # Synergy factors
        synergy_factors = []
        
        # Complementary strengths
        if creator1.engagement_rate > 5.0 and creator2.total_followers > 100000:
            synergy_factors.append(0.2)  # High engagement + large audience
        
        if creator2.engagement_rate > 5.0 and creator1.total_followers > 100000:
            synergy_factors.append(0.2)
        
        # Cross-platform strength
        creator1_platforms = set(creator1.platforms.keys())
        creator2_platforms = set(creator2.platforms.keys())
        
        if 'youtube' in creator1_platforms and 'tiktok' in creator2_platforms:
            synergy_factors.append(0.15)  # YouTube + TikTok synergy
        
        if 'spotify' in creator1_platforms and 'youtube' in creator2_platforms:
            synergy_factors.append(0.15)  # Music + Video synergy
        
        # Quality complementarity
        quality_avg = (creator1.content_quality_score + creator2.content_quality_score) / 2
        if quality_avg > 0.8:
            synergy_factors.append(0.1)
        
        return min(sum(synergy_factors), 1.0)
    
    async def _identify_risk_factors(self, creator1: CreatorProfile, creator2: CreatorProfile) -> List[str]:
        """Identify potential risk factors in collaboration"""        risks = []
        
        # Brand safety risks
        if creator1.brand_safety_score < 0.7 or creator2.brand_safety_score < 0.7:
            risks.append("Low brand safety score detected")
        
        # Tier mismatch risk
        tier_values = {
            CreatorTier.EMERGING: 1,
            CreatorTier.NANO_INFLUENCER: 2,
            CreatorTier.MICRO_INFLUENCER: 3,
            CreatorTier.MACRO_INFLUENCER: 4,
            CreatorTier.MEGA_INFLUENCER: 5
        }
        
        tier_diff = abs(tier_values.get(creator1.tier, 1) - tier_values.get(creator2.tier, 1))
        if tier_diff > 2:
            risks.append("Significant tier mismatch may affect collaboration balance")
        
        # Engagement disparity
        if creator1.engagement_rate > 0 and creator2.engagement_rate > 0:
            engagement_ratio = max(creator1.engagement_rate, creator2.engagement_rate) / \
                             min(creator1.engagement_rate, creator2.engagement_rate)
            if engagement_ratio > 3:
                risks.append("Large engagement rate disparity")
        
        # Limited platform overlap
        platforms1 = set(creator1.platforms.keys())
        platforms2 = set(creator2.platforms.keys())
        overlap = len(platforms1.intersection(platforms2))
        
        if overlap == 0:
            risks.append("No platform overlap - limited collaboration opportunities")
        
        return risks
    
    async def _generate_match_reasons(
        self, 
        creator1: CreatorProfile, 
        creator2: CreatorProfile, 
        compatibility_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the match"""        reasons = []
        
        # Category overlap
        shared_categories = set(creator1.categories).intersection(set(creator2.categories))
        if shared_categories:
            category_names = [cat.value for cat in shared_categories]
            reasons.append(f"Shared content categories: {', '.join(category_names)}")
        
        # Tier compatibility
        if creator1.tier == creator2.tier:
            reasons.append(f"Same influencer tier ({creator1.tier.value})")
        
        # High engagement
        if creator1.engagement_rate > 5.0 and creator2.engagement_rate > 5.0:
            reasons.append("Both creators have high engagement rates")
        
        # Platform presence
        shared_platforms = set(creator1.platforms.keys()).intersection(set(creator2.platforms.keys()))
        if shared_platforms:
            platform_names = list(shared_platforms)
            reasons.append(f"Active on same platforms: {', '.join(platform_names)}")
        
        # Quality scores
        if creator1.content_quality_score > 0.8 and creator2.content_quality_score > 0.8:
            reasons.append("Both creators maintain high content quality")
        
        # Compatibility score
        if compatibility_score > 0.8:
            reasons.append("Exceptional compatibility match")
        elif compatibility_score > 0.7:
            reasons.append("Strong compatibility match")
        
        return reasons
    
    async def _recommend_collaboration_approach(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_types: List[CollaborationType]
    ) -> str:
        """Recommend approach for collaboration"""        
        if CollaborationType.FEATURING in collaboration_types:
            return "Start with a music featuring to test audience reception, then explore video content collaboration"
        
        elif CollaborationType.GUEST_APPEARANCE in collaboration_types:
            return "Begin with guest appearances on each other's channels to introduce audiences"
        
        elif CollaborationType.CHALLENGE in collaboration_types:
            return "Launch a joint social media challenge to maximize viral potential"
        
        elif CollaborationType.CROSS_PROMOTION in collaboration_types:
            return "Start with mutual promotion posts, then develop joint content series"
        
        else:
            return "Begin with small-scale collaboration to test audience engagement before major projects"
    
    async def _estimate_collaboration_revenue(
        self,
        creator1: CreatorProfile,
        creator2: CreatorProfile,
        collaboration_types: List[CollaborationType],
        estimated_reach: int
    ) -> float:
        """Estimate potential revenue from collaboration"""        
        # Base revenue calculation (simplified)
        base_cpm = 2.0  # $2 per 1000 views/impressions
        base_revenue = (estimated_reach / 1000) * base_cpm
        
        # Collaboration type multipliers
        type_multipliers = {
            CollaborationType.FEATURING: 1.5,
            CollaborationType.SPONSORSHIP: 2.0,
            CollaborationType.JOINT_CONTENT: 1.3,
            CollaborationType.SERIES: 1.8,
            CollaborationType.CHALLENGE: 1.2,
            CollaborationType.CROSS_PROMOTION: 0.8
        }
        
        # Calculate weighted multiplier
        if collaboration_types:
            avg_multiplier = sum(type_multipliers.get(ct, 1.0) for ct in collaboration_types) / len(collaboration_types)
        else:
            avg_multiplier = 1.0
        
        # Quality bonus
        quality_bonus = (creator1.content_quality_score + creator2.content_quality_score) / 2
        
        # Engagement bonus
        engagement_bonus = min((creator1.engagement_rate + creator2.engagement_rate) / 20, 0.5)
        
        estimated_revenue = base_revenue * avg_multiplier * (1 + quality_bonus) * (1 + engagement_bonus)
        
        return round(estimated_revenue, 2)


__all__ = [
    'CreatorProfileParser',
    'CollaborationMatchingEngine',
    'CreatorProfile',
    'CollaborationMatch',
    'CollaborationAnalytics',
    'CreatorTier',
    'ContentCategory',
    'CollaborationType'
]
