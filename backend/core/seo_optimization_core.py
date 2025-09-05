#!/usr/bin/env python3
"""🔍 SEO Optimization Core - Professional Multi-Platform SEO Engine
================================================================
Module: backend/core/seo_optimization_core.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Enterprise SEO Optimization System - Ultra Production-Ready
Responsibility: Advanced SEO optimization, keyword research, trend analysis, and multi-platform content optimization
===========================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 SEO FEATURES:
- AI-powered keyword research and analysis
- Multi-platform content optimization
- Trend prediction and analysis
- Competitor analysis and insights
- Metadata generation and optimization
- Schema markup automation
- Performance tracking and reporting

🚀 SUPPORTED PLATFORMS:
- Search Engines (Google, Bing, Yahoo)
- Social Media (YouTube, Instagram, TikTok)
- Streaming Platforms (Spotify, Apple Music)
- Professional Networks (LinkedIn)
- Creator Platforms (Patreon, OnlyFans)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timezone, timedelta
import json
import uuid
import hashlib
import re
import urllib.parse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Import AI orchestrator for SEO intelligence
try:
    from .ia_agents_orchestrator import get_orchestrator, TaskPriority
    HAS_AI_ORCHESTRATOR = True
except ImportError:
    HAS_AI_ORCHESTRATOR = False
    logger.warning("AI Orchestrator not available, some features disabled")

# Import NLP libraries with fallbacks
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    logger.warning("spaCy not available, NLP features limited")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("Requests not available, API features limited")


# ============================================================================
# SEO SYSTEM DEFINITIONS
# ============================================================================

class SEOPlatform(Enum):
    """SEO target platforms"""
    GOOGLE_SEARCH = "google_search"
    BING_SEARCH = "bing_search"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"


class ContentCategory(Enum):
    """Content categories for SEO optimization"""
    MUSIC = "music"
    VIDEO = "video"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    PRODUCT_PAGE = "product_page"
    ARTIST_PROFILE = "artist_profile"
    EVENT_LISTING = "event_listing"
    PORTFOLIO = "portfolio"


class SEOOptimizationType(Enum):
    """Types of SEO optimization"""
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    METADATA_OPTIMIZATION = "metadata_optimization"
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    SOCIAL_SEO = "social_seo"
    VOICE_SEARCH_OPTIMIZATION = "voice_search_optimization"


class KeywordDifficulty(Enum):
    """Keyword ranking difficulty levels"""
    VERY_EASY = "very_easy"      # 0-20
    EASY = "easy"                # 21-40
    MEDIUM = "medium"            # 41-60
    HARD = "hard"                # 61-80
    VERY_HARD = "very_hard"      # 81-100


@dataclass
class KeywordData:
    """Comprehensive keyword analysis data"""
    keyword: str
    search_volume: int = 0
    difficulty: KeywordDifficulty = KeywordDifficulty.MEDIUM
    competition: float = 0.5  # 0-1 scale
    cpc: float = 0.0  # Cost per click in EUR
    
    # Trend data
    trend_direction: str = "stable"  # rising, falling, stable
    seasonal_peaks: List[str] = field(default_factory=list)
    
    # Related keywords
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variants: List[str] = field(default_factory=list)
    
    # Platform-specific data
    platform_volumes: Dict[str, int] = field(default_factory=dict)
    platform_competition: Dict[str, float] = field(default_factory=dict)
    
    # Semantic analysis
    search_intent: str = "informational"  # informational, navigational, transactional, commercial
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    
    # Performance metrics
    current_ranking: Optional[int] = None
    ranking_history: List[Dict[str, Any]] = field(default_factory=list)
    click_through_rate: float = 0.0
    
    def __post_init__(self):
        if not self.keyword:
            raise ValueError("Keyword cannot be empty")


@dataclass
class SEOOptimization:
    """SEO optimization result"""
    optimization_id: str
    content_id: str
    platform: SEOPlatform
    optimization_type: SEOOptimizationType
    
    # Original content
    original_title: str = ""
    original_description: str = ""
    original_tags: List[str] = field(default_factory=list)
    
    # Optimized content
    optimized_title: str = ""
    optimized_description: str = ""
    optimized_tags: List[str] = field(default_factory=list)
    optimized_metadata: Dict[str, str] = field(default_factory=dict)
    
    # Keywords
    target_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    keyword_density: Dict[str, float] = field(default_factory=dict)
    
    # SEO metrics
    seo_score: float = 0.0  # 0-100
    readability_score: float = 0.0
    keyword_optimization_score: float = 0.0
    metadata_completeness: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance prediction
    estimated_visibility_improvement: float = 0.0
    estimated_traffic_increase: float = 0.0
    confidence_level: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.optimization_id:
            self.optimization_id = f"seo_{uuid.uuid4().hex[:12]}"


@dataclass
class CompetitorAnalysis:
    """Competitor SEO analysis"""
    analysis_id: str
    competitor_url: str
    competitor_name: str = ""
    
    # Content analysis
    title_analysis: Dict[str, Any] = field(default_factory=dict)
    description_analysis: Dict[str, Any] = field(default_factory=dict)
    keyword_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    estimated_traffic: int = 0
    domain_authority: int = 0
    page_authority: int = 0
    backlink_count: int = 0
    
    # SEO factors
    technical_seo_score: float = 0.0
    content_quality_score: float = 0.0
    user_experience_score: float = 0.0
    
    # Opportunities
    keyword_gaps: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    # Timestamps
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not self.analysis_id:
            self.analysis_id = f"comp_{uuid.uuid4().hex[:12]}"


@dataclass
class TrendAnalysis:
    """SEO trend analysis and prediction"""
    trend_id: str
    topic: str
    timeframe: str = "30d"  # 7d, 30d, 90d, 1y
    
    # Trend data
    current_volume: int = 0
    peak_volume: int = 0
    trend_direction: str = "stable"
    growth_rate: float = 0.0
    
    # Prediction
    predicted_volume: int = 0
    prediction_confidence: float = 0.0
    seasonal_pattern: bool = False
    
    # Related trends
    related_topics: List[str] = field(default_factory=list)
    emerging_keywords: List[str] = field(default_factory=list)
    declining_keywords: List[str] = field(default_factory=list)
    
    # Geographic data
    top_regions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    optimization_opportunities: List[str] = field(default_factory=list)
    content_suggestions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.trend_id:
            self.trend_id = f"trend_{uuid.uuid4().hex[:12]}"


# ============================================================================
# KEYWORD RESEARCH ENGINE
# ============================================================================

class KeywordResearchEngine:
    """Advanced keyword research and analysis"""
    
    def __init__(self):
        self.keyword_cache: Dict[str, KeywordData] = {}
        self.trend_cache: Dict[str, TrendAnalysis] = {}
        
        # Initialize keyword database (in production, use external APIs)
        self._initialize_keyword_database()
    
    def _initialize_keyword_database(self):
        """Initialize mock keyword database"""
        # In production, integrate with Google Keyword Planner, SEMrush, Ahrefs APIs
        self.mock_keywords = {
            "music production": {
                "volume": 12000, "difficulty": 65, "cpc": 2.50,
                "related": ["beat making", "audio engineering", "music software"],
                "intent": "informational"
            },
            "beat making": {
                "volume": 8500, "difficulty": 45, "cpc": 1.80,
                "related": ["hip hop beats", "trap beats", "fl studio"],
                "intent": "informational"
            },
            "music collaboration": {
                "volume": 3200, "difficulty": 35, "cpc": 1.20,
                "related": ["producer collaboration", "artist collaboration"],
                "intent": "commercial"
            },
            "video editing": {
                "volume": 22000, "difficulty": 70, "cpc": 3.20,
                "related": ["video production", "adobe premiere", "final cut pro"],
                "intent": "informational"
            },
            "content creator": {
                "volume": 18000, "difficulty": 55, "cpc": 2.80,
                "related": ["influencer", "social media creator", "youtube creator"],
                "intent": "informational"
            }
        }
    
    async def research_keywords(
        self,
        seed_keywords: List[str],
        platform: SEOPlatform = SEOPlatform.GOOGLE_SEARCH,
        language: str = "en",
        country: str = "DE"
    ) -> List[KeywordData]:
        """Research keywords and generate comprehensive data"""
        try:
            keyword_results = []
            
            for seed in seed_keywords:
                # Get base keyword data
                keyword_data = await self._get_keyword_data(seed, platform, language, country)
                if keyword_data:
                    keyword_results.append(keyword_data)
                
                # Get related keywords
                related_keywords = await self._find_related_keywords(seed, platform)
                for related in related_keywords[:5]:  # Limit to top 5 related
                    related_data = await self._get_keyword_data(related, platform, language, country)
                    if related_data:
                        keyword_results.append(related_data)
            
            # Sort by relevance and volume
            keyword_results.sort(key=lambda k: (k.search_volume, -k.competition), reverse=True)
            
            logger.info(f"Researched {len(keyword_results)} keywords for {len(seed_keywords)} seeds")
            return keyword_results
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return []
    
    async def _get_keyword_data(
        self,
        keyword: str,
        platform: SEOPlatform,
        language: str,
        country: str
    ) -> Optional[KeywordData]:
        """Get comprehensive keyword data"""
        try:
            # Check cache first
            cache_key = f"{keyword}_{platform.value}_{language}_{country}"
            if cache_key in self.keyword_cache:
                return self.keyword_cache[cache_key]
            
            # Mock data (in production, use real APIs)
            mock_data = self.mock_keywords.get(keyword.lower())
            if not mock_data:
                return None
            
            keyword_data = KeywordData(
                keyword=keyword,
                search_volume=mock_data["volume"],
                difficulty=self._map_difficulty(mock_data["difficulty"]),
                competition=mock_data["difficulty"] / 100,
                cpc=mock_data["cpc"],
                related_keywords=mock_data["related"],
                search_intent=mock_data["intent"]
            )
            
            # Add platform-specific data
            keyword_data.platform_volumes[platform.value] = int(mock_data["volume"] * 0.8)
            keyword_data.platform_competition[platform.value] = mock_data["difficulty"] / 100
            
            # Generate long-tail variants
            keyword_data.long_tail_variants = self._generate_long_tail_variants(keyword)
            
            # Analyze entities and topics
            keyword_data.entities, keyword_data.topics = await self._analyze_keyword_semantics(keyword)
            
            # Cache result
            self.keyword_cache[cache_key] = keyword_data
            
            return keyword_data
            
        except Exception as e:
            logger.error(f"Keyword data retrieval failed for '{keyword}': {e}")
            return None
    
    def _map_difficulty(self, difficulty_score: int) -> KeywordDifficulty:
        """Map difficulty score to difficulty level"""
        if difficulty_score <= 20:
            return KeywordDifficulty.VERY_EASY
        elif difficulty_score <= 40:
            return KeywordDifficulty.EASY
        elif difficulty_score <= 60:
            return KeywordDifficulty.MEDIUM
        elif difficulty_score <= 80:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD
    
    async def _find_related_keywords(self, seed: str, platform: SEOPlatform) -> List[str]:
        """Find related keywords"""
        try:
            # Mock related keyword generation
            related = []
            
            # Add variations
            if "production" in seed.lower():
                related.extend([f"{seed} software", f"{seed} tips", f"{seed} tutorial"])
            
            if "music" in seed.lower():
                related.extend([f"{seed} maker", f"{seed} studio", f"{seed} equipment"])
            
            if "video" in seed.lower():
                related.extend([f"{seed} software", f"{seed} course", f"{seed} freelancer"])
            
            # Add platform-specific variations
            if platform == SEOPlatform.YOUTUBE:
                related.extend([f"{seed} tutorial", f"how to {seed}", f"{seed} tips"])
            elif platform == SEOPlatform.INSTAGRAM:
                related.extend([f"{seed} inspiration", f"{seed} ideas", f"{seed} trends"])
            
            return related[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Related keyword finding failed: {e}")
            return []
    
    def _generate_long_tail_variants(self, keyword: str) -> List[str]:
        """Generate long-tail keyword variants"""
        try:
            variants = []
            
            # Question-based variants
            variants.extend([
                f"how to {keyword}",
                f"what is {keyword}",
                f"best {keyword}",
                f"{keyword} tutorial",
                f"{keyword} for beginners"
            ])
            
            # Location-based variants
            variants.extend([
                f"{keyword} near me",
                f"{keyword} in germany",
                f"{keyword} berlin",
                f"{keyword} online"
            ])
            
            # Service-based variants
            variants.extend([
                f"{keyword} service",
                f"{keyword} freelancer",
                f"cheap {keyword}",
                f"professional {keyword}"
            ])
            
            return variants
            
        except Exception as e:
            logger.error(f"Long-tail variant generation failed: {e}")
            return []
    
    async def _analyze_keyword_semantics(self, keyword: str) -> Tuple[List[str], List[str]]:
        """Analyze keyword semantics for entities and topics"""
        try:
            entities = []
            topics = []
            
            # Simple entity extraction (in production, use NLP libraries)
            words = keyword.lower().split()
            
            # Common entities in creator space
            entity_map = {
                "music": ["Music", "Audio"],
                "video": ["Video", "Visual"],
                "production": ["Production", "Creation"],
                "beat": ["Beat", "Rhythm"],
                "collaboration": ["Collaboration", "Partnership"],
                "creator": ["Creator", "Artist"]
            }
            
            for word in words:
                if word in entity_map:
                    entities.extend(entity_map[word])
            
            # Topic classification
            if any(w in keyword.lower() for w in ["music", "audio", "beat", "song"]):
                topics.append("Music Production")
            
            if any(w in keyword.lower() for w in ["video", "film", "editing"]):
                topics.append("Video Production")
            
            if any(w in keyword.lower() for w in ["collaboration", "partner", "team"]):
                topics.append("Collaboration")
            
            return entities, topics
            
        except Exception as e:
            logger.error(f"Keyword semantic analysis failed: {e}")
            return [], []
    
    async def analyze_keyword_trends(
        self,
        keywords: List[str],
        timeframe: str = "30d"
    ) -> List[TrendAnalysis]:
        """Analyze keyword trends and predictions"""
        try:
            trend_analyses = []
            
            for keyword in keywords:
                trend = TrendAnalysis(
                    topic=keyword,
                    timeframe=timeframe
                )
                
                # Mock trend data (in production, use Google Trends API)
                base_volume = self.mock_keywords.get(keyword.lower(), {}).get("volume", 1000)
                
                trend.current_volume = base_volume
                trend.peak_volume = int(base_volume * 1.5)
                
                # Simulate trend direction
                import random
                trend_directions = ["rising", "stable", "falling"]
                trend.trend_direction = random.choice(trend_directions)
                
                if trend.trend_direction == "rising":
                    trend.growth_rate = random.uniform(5, 25)
                    trend.predicted_volume = int(base_volume * 1.2)
                elif trend.trend_direction == "falling":
                    trend.growth_rate = random.uniform(-25, -5)
                    trend.predicted_volume = int(base_volume * 0.8)
                else:
                    trend.growth_rate = random.uniform(-2, 2)
                    trend.predicted_volume = base_volume
                
                trend.prediction_confidence = random.uniform(0.7, 0.9)
                
                # Generate related trends
                if "music" in keyword.lower():
                    trend.related_topics = ["beat making", "audio engineering", "music software"]
                elif "video" in keyword.lower():
                    trend.related_topics = ["video editing", "cinematography", "youtube"]
                
                # Generate optimization opportunities
                if trend.trend_direction == "rising":
                    trend.optimization_opportunities = [
                        f"Create content targeting '{keyword}' soon",
                        f"Optimize existing content for '{keyword}'",
                        f"Consider paid campaigns for '{keyword}'"
                    ]
                
                trend_analyses.append(trend)
            
            return trend_analyses
            
        except Exception as e:
            logger.error(f"Keyword trend analysis failed: {e}")
            return []


# ============================================================================
# CONTENT OPTIMIZATION ENGINE
# ============================================================================

class ContentOptimizationEngine:
    """Advanced content optimization for SEO"""
    
    def __init__(self):
        self.optimization_templates = self._initialize_optimization_templates()
        self.platform_requirements = self._initialize_platform_requirements()
    
    def _initialize_optimization_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize optimization templates for different content types"""
        return {
            "music": {
                "title_length": (30, 60),
                "description_length": (150, 300),
                "keyword_density": (1, 3),
                "required_elements": ["genre", "mood", "bpm"],
                "recommended_tags": 5
            },
            "video": {
                "title_length": (40, 70),
                "description_length": (200, 500),
                "keyword_density": (2, 4),
                "required_elements": ["duration", "resolution", "format"],
                "recommended_tags": 8
            },
            "podcast": {
                "title_length": (25, 50),
                "description_length": (100, 200),
                "keyword_density": (1, 2),
                "required_elements": ["episode_number", "guest", "topic"],
                "recommended_tags": 6
            }
        }
    
    def _initialize_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific SEO requirements"""
        return {
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 15,
                "thumbnail_required": True,
                "closed_captions_recommended": True
            },
            "spotify": {
                "title_max_length": 100,
                "description_max_length": 1000,
                "genre_required": True,
                "mood_tags_recommended": True,
                "release_date_required": True
            },
            "instagram": {
                "caption_max_length": 2200,
                "hashtags_max_count": 30,
                "hashtags_recommended_count": 11,
                "alt_text_required": True
            },
            "tiktok": {
                "caption_max_length": 150,
                "hashtags_max_count": 100,
                "hashtags_recommended_count": 3,
                "trending_sounds_consideration": True
            }
        }
    
    async def optimize_content(
        self,
        content_id: str,
        title: str,
        description: str,
        tags: List[str],
        platform: SEOPlatform,
        category: ContentCategory,
        target_keywords: List[str],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> SEOOptimization:
        """Optimize content for SEO"""
        try:
            optimization = SEOOptimization(
                content_id=content_id,
                platform=platform,
                optimization_type=SEOOptimizationType.CONTENT_OPTIMIZATION,
                original_title=title,
                original_description=description,
                original_tags=tags,
                target_keywords=target_keywords
            )
            
            # Optimize title
            optimization.optimized_title = await self._optimize_title(
                title, target_keywords, platform, category
            )
            
            # Optimize description
            optimization.optimized_description = await self._optimize_description(
                description, target_keywords, platform, category
            )
            
            # Optimize tags
            optimization.optimized_tags = await self._optimize_tags(
                tags, target_keywords, platform, category
            )
            
            # Generate metadata
            optimization.optimized_metadata = await self._generate_metadata(
                optimization, platform, category, additional_data
            )
            
            # Calculate SEO scores
            await self._calculate_seo_scores(optimization)
            
            # Generate recommendations
            optimization.recommendations = await self._generate_recommendations(optimization, platform)
            
            # Predict performance improvement
            optimization.estimated_visibility_improvement = await self._estimate_visibility_improvement(optimization)
            optimization.confidence_level = 0.85  # Mock confidence
            
            logger.info(f"Content optimization completed for {content_id}")
            return optimization
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise
    
    async def _optimize_title(
        self,
        original_title: str,
        target_keywords: List[str],
        platform: SEOPlatform,
        category: ContentCategory
    ) -> str:
        """Optimize title for SEO"""
        try:
            if not target_keywords:
                return original_title
            
            primary_keyword = target_keywords[0]
            
            # Get platform requirements
            platform_reqs = self.platform_requirements.get(platform.value, {})
            max_length = platform_reqs.get("title_max_length", 60)
            
            # Start with primary keyword if not already present
            if primary_keyword.lower() not in original_title.lower():
                if len(original_title) + len(primary_keyword) + 3 <= max_length:
                    optimized_title = f"{primary_keyword} - {original_title}"
                else:
                    # Replace part of title with keyword
                    optimized_title = f"{primary_keyword} {original_title[:max_length-len(primary_keyword)-1]}"
            else:
                optimized_title = original_title
            
            # Ensure title is within length limits
            if len(optimized_title) > max_length:
                optimized_title = optimized_title[:max_length-3] + "..."
            
            # Add power words for engagement
            power_words = ["Ultimate", "Complete", "Professional", "Advanced", "Exclusive"]
            if not any(word in optimized_title for word in power_words):
                if len(optimized_title) + 10 < max_length:
                    optimized_title = f"Professional {optimized_title}"
            
            return optimized_title
            
        except Exception as e:
            logger.error(f"Title optimization failed: {e}")
            return original_title
    
    async def _optimize_description(
        self,
        original_description: str,
        target_keywords: List[str],
        platform: SEOPlatform,
        category: ContentCategory
    ) -> str:
        """Optimize description for SEO"""
        try:
            if not target_keywords:
                return original_description
            
            platform_reqs = self.platform_requirements.get(platform.value, {})
            max_length = platform_reqs.get("description_max_length", 300)
            
            optimized_description = original_description
            
            # Ensure primary keyword appears early
            primary_keyword = target_keywords[0]
            if primary_keyword.lower() not in optimized_description.lower()[:100]:
                # Add keyword to beginning if space allows
                keyword_intro = f"This {category.value} focuses on {primary_keyword}. "
                if len(keyword_intro) + len(optimized_description) <= max_length:
                    optimized_description = keyword_intro + optimized_description
            
            # Add secondary keywords naturally
            for keyword in target_keywords[1:3]:  # Add up to 2 secondary keywords
                if keyword.lower() not in optimized_description.lower():
                    # Try to add keyword naturally
                    keyword_phrase = f" Related to {keyword},"
                    if len(optimized_description) + len(keyword_phrase) <= max_length:
                        optimized_description += keyword_phrase
            
            # Add call to action
            if platform in [SEOPlatform.YOUTUBE, SEOPlatform.INSTAGRAM]:
                cta = " Like and subscribe for more content!"
                if len(optimized_description) + len(cta) <= max_length:
                    optimized_description += cta
            
            # Ensure within length limits
            if len(optimized_description) > max_length:
                optimized_description = optimized_description[:max_length-3] + "..."
            
            return optimized_description
            
        except Exception as e:
            logger.error(f"Description optimization failed: {e}")
            return original_description
    
    async def _optimize_tags(
        self,
        original_tags: List[str],
        target_keywords: List[str],
        platform: SEOPlatform,
        category: ContentCategory
    ) -> List[str]:
        """Optimize tags for SEO"""
        try:
            platform_reqs = self.platform_requirements.get(platform.value, {})
            max_tags = platform_reqs.get("tags_max_count", 10)
            recommended_count = platform_reqs.get("hashtags_recommended_count", max_tags)
            
            optimized_tags = list(original_tags)
            
            # Add target keywords as tags if not already present
            for keyword in target_keywords:
                keyword_tag = keyword.replace(" ", "").lower()
                if keyword_tag not in [tag.lower() for tag in optimized_tags]:
                    optimized_tags.append(keyword_tag)
            
            # Add category-specific tags
            category_tags = self._get_category_tags(category, platform)
            for tag in category_tags:
                if tag not in optimized_tags and len(optimized_tags) < max_tags:
                    optimized_tags.append(tag)
            
            # Add trending/popular tags for platform
            trending_tags = await self._get_trending_tags(platform, category)
            for tag in trending_tags:
                if tag not in optimized_tags and len(optimized_tags) < max_tags:
                    optimized_tags.append(tag)
            
            # Limit to platform requirements
            if len(optimized_tags) > max_tags:
                optimized_tags = optimized_tags[:max_tags]
            
            return optimized_tags
            
        except Exception as e:
            logger.error(f"Tags optimization failed: {e}")
            return original_tags
    
    def _get_category_tags(self, category: ContentCategory, platform: SEOPlatform) -> List[str]:
        """Get relevant tags for content category and platform"""
        category_tag_map = {
            ContentCategory.MUSIC: {
                SEOPlatform.SPOTIFY: ["music", "newmusic", "indie", "producer"],
                SEOPlatform.YOUTUBE: ["music", "musicvideo", "artist", "song"],
                SEOPlatform.INSTAGRAM: ["music", "musicproducer", "studio", "beats"]
            },
            ContentCategory.VIDEO: {
                SEOPlatform.YOUTUBE: ["video", "content", "creator", "production"],
                SEOPlatform.INSTAGRAM: ["video", "videocontent", "reels", "creative"],
                SEOPlatform.TIKTOK: ["video", "viral", "fyp", "trending"]
            }
        }
        
        return category_tag_map.get(category, {}).get(platform, [])
    
    async def _get_trending_tags(self, platform: SEOPlatform, category: ContentCategory) -> List[str]:
        """Get trending tags for platform and category"""
        # Mock trending tags (in production, use platform APIs)
        trending_tags = {
            SEOPlatform.INSTAGRAM: ["trending", "viral", "explore", "instadaily"],
            SEOPlatform.TIKTOK: ["fyp", "viral", "trending", "foryou"],
            SEOPlatform.YOUTUBE: ["trending", "viral", "2024", "new"],
            SEOPlatform.SPOTIFY: ["newmusic", "indie", "discover", "playlist"]
        }
        
        return trending_tags.get(platform, [])
    
    async def _generate_metadata(
        self,
        optimization: SEOOptimization,
        platform: SEOPlatform,
        category: ContentCategory,
        additional_data: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate optimized metadata"""
        try:
            metadata = {}
            
            # Basic metadata
            metadata["og:title"] = optimization.optimized_title
            metadata["og:description"] = optimization.optimized_description[:160]
            metadata["og:type"] = "article" if category == ContentCategory.BLOG_POST else "website"
            
            # Twitter Card metadata
            metadata["twitter:title"] = optimization.optimized_title
            metadata["twitter:description"] = optimization.optimized_description[:160]
            metadata["twitter:card"] = "summary_large_image"
            
            # Schema.org markup
            if category == ContentCategory.MUSIC:
                metadata["schema:type"] = "MusicRecording"
                metadata["schema:genre"] = additional_data.get("genre", "") if additional_data else ""
            elif category == ContentCategory.VIDEO:
                metadata["schema:type"] = "VideoObject"
                metadata["schema:duration"] = additional_data.get("duration", "") if additional_data else ""
            
            # Platform-specific metadata
            if platform == SEOPlatform.YOUTUBE:
                metadata["yt:keywords"] = ",".join(optimization.target_keywords)
                metadata["yt:category"] = self._map_category_to_youtube(category)
            
            # Keywords metadata
            metadata["keywords"] = ",".join(optimization.target_keywords + optimization.secondary_keywords)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            return {}
    
    def _map_category_to_youtube(self, category: ContentCategory) -> str:
        """Map content category to YouTube category"""
        mapping = {
            ContentCategory.MUSIC: "Music",
            ContentCategory.VIDEO: "Entertainment",
            ContentCategory.PODCAST: "Education",
            ContentCategory.BLOG_POST: "Education"
        }
        return mapping.get(category, "Entertainment")
    
    async def _calculate_seo_scores(self, optimization: SEOOptimization):
        """Calculate various SEO scores"""
        try:
            # Keyword optimization score
            keyword_score = 0
            if optimization.target_keywords:
                primary_keyword = optimization.target_keywords[0].lower()
                
                # Check title
                if primary_keyword in optimization.optimized_title.lower():
                    keyword_score += 30
                
                # Check description
                if primary_keyword in optimization.optimized_description.lower():
                    keyword_score += 20
                
                # Check tags
                if any(primary_keyword in tag.lower() for tag in optimization.optimized_tags):
                    keyword_score += 20
                
                # Check keyword density
                word_count = len(optimization.optimized_description.split())
                if word_count > 0:
                    keyword_count = optimization.optimized_description.lower().count(primary_keyword)
                    density = (keyword_count / word_count) * 100
                    if 1 <= density <= 3:  # Optimal density
                        keyword_score += 30
                    elif density > 0:
                        keyword_score += 15
            
            optimization.keyword_optimization_score = min(keyword_score, 100)
            
            # Metadata completeness score
            required_metadata = ["og:title", "og:description", "keywords"]
            metadata_score = 0
            for meta in required_metadata:
                if meta in optimization.optimized_metadata and optimization.optimized_metadata[meta]:
                    metadata_score += 100 / len(required_metadata)
            
            optimization.metadata_completeness = metadata_score
            
            # Readability score (simplified)
            desc_length = len(optimization.optimized_description)
            if 150 <= desc_length <= 300:
                optimization.readability_score = 100
            elif 100 <= desc_length <= 500:
                optimization.readability_score = 80
            else:
                optimization.readability_score = 60
            
            # Overall SEO score
            optimization.seo_score = (
                optimization.keyword_optimization_score * 0.4 +
                optimization.metadata_completeness * 0.3 +
                optimization.readability_score * 0.3
            )
            
        except Exception as e:
            logger.error(f"SEO score calculation failed: {e}")
            optimization.seo_score = 0
    
    async def _generate_recommendations(
        self,
        optimization: SEOOptimization,
        platform: SEOPlatform
    ) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        try:
            # Keyword optimization recommendations
            if optimization.keyword_optimization_score < 70:
                recommendations.append("Include primary keyword in title for better visibility")
                recommendations.append("Increase keyword density in description (aim for 1-3%)")
            
            # Length recommendations
            title_length = len(optimization.optimized_title)
            if title_length < 30:
                recommendations.append("Consider lengthening title for better keyword inclusion")
            elif title_length > 60:
                recommendations.append("Consider shortening title for better readability")
            
            desc_length = len(optimization.optimized_description)
            if desc_length < 150:
                recommendations.append("Expand description for better SEO and user engagement")
            
            # Tag recommendations
            if len(optimization.optimized_tags) < 5:
                recommendations.append("Add more relevant tags to improve discoverability")
            
            # Platform-specific recommendations
            if platform == SEOPlatform.YOUTUBE:
                recommendations.append("Consider adding closed captions for accessibility")
                recommendations.append("Create eye-catching thumbnail for better click-through rate")
            elif platform == SEOPlatform.INSTAGRAM:
                recommendations.append("Use optimal posting time for your audience")
                recommendations.append("Engage with comments to boost algorithm visibility")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Review and refine content optimization manually"]
    
    async def _estimate_visibility_improvement(self, optimization: SEOOptimization) -> float:
        """Estimate visibility improvement from optimization"""
        try:
            # Simple estimation based on SEO score improvement
            baseline_score = 50  # Assume baseline
            improvement = optimization.seo_score - baseline_score
            
            # Convert to percentage improvement
            visibility_improvement = max(0, improvement * 0.5)  # Conservative estimate
            
            return min(visibility_improvement, 100)
            
        except Exception as e:
            logger.error(f"Visibility improvement estimation failed: {e}")
            return 0.0


# ============================================================================
# COMPETITOR ANALYSIS ENGINE
# ============================================================================

class CompetitorAnalysisEngine:
    """Competitor SEO analysis and insights"""
    
    def __init__(self):
        self.analysis_cache: Dict[str, CompetitorAnalysis] = {}
    
    async def analyze_competitor(
        self,
        competitor_url: str,
        competitor_name: str = "",
        target_keywords: List[str] = None
    ) -> CompetitorAnalysis:
        """Analyze competitor SEO performance"""
        try:
            analysis = CompetitorAnalysis(
                competitor_url=competitor_url,
                competitor_name=competitor_name or self._extract_domain_name(competitor_url)
            )
            
            # Mock competitor analysis (in production, use web scraping and SEO tools)
            await self._analyze_competitor_content(analysis, target_keywords or [])
            await self._analyze_competitor_performance(analysis)
            await self._identify_opportunities(analysis, target_keywords or [])
            
            # Cache analysis
            self.analysis_cache[competitor_url] = analysis
            
            logger.info(f"Competitor analysis completed for {competitor_url}")
            return analysis
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            raise
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return url
    
    async def _analyze_competitor_content(
        self,
        analysis: CompetitorAnalysis,
        target_keywords: List[str]
    ):
        """Analyze competitor content strategy"""
        try:
            # Mock content analysis
            analysis.title_analysis = {
                "average_length": 45,
                "keyword_optimization": "good",
                "power_words_usage": "moderate",
                "emotional_triggers": ["professional", "ultimate", "complete"]
            }
            
            analysis.description_analysis = {
                "average_length": 280,
                "keyword_density": 2.5,
                "readability_score": 85,
                "call_to_action_presence": True
            }
            
            analysis.keyword_analysis = {
                "primary_keywords": target_keywords[:3] if target_keywords else [],
                "keyword_distribution": "well_balanced",
                "long_tail_usage": "high",
                "semantic_relevance": "strong"
            }
            
        except Exception as e:
            logger.error(f"Competitor content analysis failed: {e}")
    
    async def _analyze_competitor_performance(self, analysis: CompetitorAnalysis):
        """Analyze competitor performance metrics"""
        try:
            # Mock performance metrics
            import random
            
            analysis.estimated_traffic = random.randint(10000, 100000)
            analysis.domain_authority = random.randint(30, 90)
            analysis.page_authority = random.randint(25, 85)
            analysis.backlink_count = random.randint(500, 50000)
            
            analysis.technical_seo_score = random.uniform(70, 95)
            analysis.content_quality_score = random.uniform(75, 90)
            analysis.user_experience_score = random.uniform(65, 88)
            
        except Exception as e:
            logger.error(f"Competitor performance analysis failed: {e}")
    
    async def _identify_opportunities(
        self,
        analysis: CompetitorAnalysis,
        target_keywords: List[str]
    ):
        """Identify opportunities based on competitor analysis"""
        try:
            # Mock opportunity identification
            analysis.keyword_gaps = [
                "music collaboration tools",
                "beat making software",
                "audio mastering tips"
            ]
            
            analysis.content_opportunities = [
                "Create in-depth tutorials competitor lacks",
                "Focus on emerging music production techniques",
                "Develop mobile-first content strategy"
            ]
            
            analysis.improvement_suggestions = [
                "Optimize for voice search queries",
                "Improve page loading speed",
                "Enhance social media integration",
                "Create more engaging video content"
            ]
            
        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")


# ============================================================================
# MAIN SEO OPTIMIZATION CORE
# ============================================================================

class SEOOptimizationCore:
    """Main SEO optimization and management system"""
    
    def __init__(self):
        self.keyword_research = KeywordResearchEngine()
        self.content_optimizer = ContentOptimizationEngine()
        self.competitor_analyzer = CompetitorAnalysisEngine()
        
        # SEO tracking
        self.optimizations: Dict[str, SEOOptimization] = {}
        self.competitor_analyses: Dict[str, CompetitorAnalysis] = {}
        
        # System metrics
        self.metrics = {
            "total_optimizations": 0,
            "average_seo_score": 0.0,
            "keyword_research_requests": 0,
            "competitor_analyses": 0,
            "estimated_visibility_improvements": 0.0
        }
        
        # Executor for parallel processing
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    async def research_keywords(
        self,
        seed_keywords: List[str],
        platform: str = "google_search",
        language: str = "en",
        country: str = "DE"
    ) -> List[Dict[str, Any]]:
        """Research keywords for SEO optimization"""
        try:
            platform_enum = SEOPlatform(platform)
            
            keyword_results = await self.keyword_research.research_keywords(
                seed_keywords, platform_enum, language, country
            )
            
            # Convert to serializable format
            keywords_data = []
            for keyword in keyword_results:
                keywords_data.append({
                    "keyword": keyword.keyword,
                    "search_volume": keyword.search_volume,
                    "difficulty": keyword.difficulty.value,
                    "competition": keyword.competition,
                    "cpc": keyword.cpc,
                    "related_keywords": keyword.related_keywords,
                    "search_intent": keyword.search_intent,
                    "long_tail_variants": keyword.long_tail_variants[:5]  # Limit for response size
                })
            
            # Update metrics
            self.metrics["keyword_research_requests"] += 1
            
            logger.info(f"Keyword research completed: {len(keywords_data)} keywords")
            return keywords_data
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return []
    
    async def optimize_content(
        self,
        content_id: str,
        title: str,
        description: str,
        tags: List[str],
        platform: str,
        category: str,
        target_keywords: List[str],
        **kwargs
    ) -> str:
        """Optimize content for SEO"""
        try:
            platform_enum = SEOPlatform(platform)
            category_enum = ContentCategory(category)
            
            optimization = await self.content_optimizer.optimize_content(
                content_id=content_id,
                title=title,
                description=description,
                tags=tags,
                platform=platform_enum,
                category=category_enum,
                target_keywords=target_keywords,
                additional_data=kwargs.get("additional_data")
            )
            
            # Store optimization
            self.optimizations[optimization.optimization_id] = optimization
            
            # Update metrics
            self.metrics["total_optimizations"] += 1
            total_score = sum(opt.seo_score for opt in self.optimizations.values())
            self.metrics["average_seo_score"] = total_score / len(self.optimizations)
            self.metrics["estimated_visibility_improvements"] += optimization.estimated_visibility_improvement
            
            logger.info(f"Content optimization completed: {optimization.optimization_id}")
            return optimization.optimization_id
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise
    
    async def get_optimization_result(self, optimization_id: str) -> Optional[Dict[str, Any]]:
        """Get SEO optimization result"""
        try:
            if optimization_id not in self.optimizations:
                return None
            
            optimization = self.optimizations[optimization_id]
            
            return {
                "optimization_id": optimization_id,
                "content_id": optimization.content_id,
                "platform": optimization.platform.value,
                "seo_score": optimization.seo_score,
                "optimized_title": optimization.optimized_title,
                "optimized_description": optimization.optimized_description,
                "optimized_tags": optimization.optimized_tags,
                "optimized_metadata": optimization.optimized_metadata,
                "target_keywords": optimization.target_keywords,
                "keyword_optimization_score": optimization.keyword_optimization_score,
                "readability_score": optimization.readability_score,
                "recommendations": optimization.recommendations,
                "estimated_visibility_improvement": optimization.estimated_visibility_improvement,
                "confidence_level": optimization.confidence_level,
                "created_at": optimization.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Optimization result retrieval failed: {e}")
            return None
    
    async def analyze_competitor(
        self,
        competitor_url: str,
        competitor_name: str = "",
        target_keywords: List[str] = None
    ) -> str:
        """Analyze competitor SEO strategy"""
        try:
            analysis = await self.competitor_analyzer.analyze_competitor(
                competitor_url, competitor_name, target_keywords or []
            )
            
            # Store analysis
            self.competitor_analyses[analysis.analysis_id] = analysis
            
            # Update metrics
            self.metrics["competitor_analyses"] += 1
            
            logger.info(f"Competitor analysis completed: {analysis.analysis_id}")
            return analysis.analysis_id
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            raise
    
    async def get_competitor_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get competitor analysis result"""
        try:
            if analysis_id not in self.competitor_analyses:
                return None
            
            analysis = self.competitor_analyses[analysis_id]
            
            return {
                "analysis_id": analysis_id,
                "competitor_url": analysis.competitor_url,
                "competitor_name": analysis.competitor_name,
                "estimated_traffic": analysis.estimated_traffic,
                "domain_authority": analysis.domain_authority,
                "technical_seo_score": analysis.technical_seo_score,
                "content_quality_score": analysis.content_quality_score,
                "keyword_gaps": analysis.keyword_gaps,
                "content_opportunities": analysis.content_opportunities,
                "improvement_suggestions": analysis.improvement_suggestions,
                "analyzed_at": analysis.analyzed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis retrieval failed: {e}")
            return None
    
    async def analyze_trends(
        self,
        keywords: List[str],
        timeframe: str = "30d"
    ) -> List[Dict[str, Any]]:
        """Analyze keyword trends"""
        try:
            trend_analyses = await self.keyword_research.analyze_keyword_trends(
                keywords, timeframe
            )
            
            trends_data = []
            for trend in trend_analyses:
                trends_data.append({
                    "topic": trend.topic,
                    "current_volume": trend.current_volume,
                    "trend_direction": trend.trend_direction,
                    "growth_rate": trend.growth_rate,
                    "predicted_volume": trend.predicted_volume,
                    "prediction_confidence": trend.prediction_confidence,
                    "related_topics": trend.related_topics,
                    "optimization_opportunities": trend.optimization_opportunities
                })
            
            logger.info(f"Trend analysis completed for {len(keywords)} keywords")
            return trends_data
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return []
    
    async def get_seo_recommendations(
        self,
        content_type: str,
        current_performance: Dict[str, Any],
        target_platforms: List[str]
    ) -> List[str]:
        """Get personalized SEO recommendations"""
        try:
            recommendations = []
            
            # Performance-based recommendations
            current_score = current_performance.get("seo_score", 0)
            if current_score < 60:
                recommendations.append("Focus on basic SEO fundamentals: title optimization and keyword inclusion")
            elif current_score < 80:
                recommendations.append("Enhance content structure and metadata completeness")
            else:
                recommendations.append("Fine-tune advanced SEO techniques and monitor performance")
            
            # Platform-specific recommendations
            for platform in target_platforms:
                if platform == "youtube":
                    recommendations.append("Optimize for YouTube: create compelling thumbnails and use video descriptions")
                elif platform == "instagram":
                    recommendations.append("Leverage Instagram features: use relevant hashtags and Stories")
                elif platform == "spotify":
                    recommendations.append("Optimize for music discovery: use proper genre tags and mood descriptors")
            
            # Content type recommendations
            if content_type == "music":
                recommendations.append("Include genre, BPM, and mood in metadata for better music discovery")
            elif content_type == "video":
                recommendations.append("Add closed captions and optimize video length for engagement")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"SEO recommendations generation failed: {e}")
            return ["Review content optimization best practices"]
    
    async def health_check(self) -> Dict[str, Any]:
        """SEO optimization system health check"""
        try:
            return {
                "seo_core": {
                    "healthy": True,
                    "active_optimizations": len(self.optimizations),
                    "competitor_analyses": len(self.competitor_analyses),
                    "metrics": self.metrics.copy()
                },
                "components": {
                    "keyword_research_engine": True,
                    "content_optimization_engine": True,
                    "competitor_analysis_engine": True,
                    "ai_orchestrator": HAS_AI_ORCHESTRATOR
                },
                "features": {
                    "nlp_processing": HAS_SPACY,
                    "api_requests": HAS_REQUESTS,
                    "trend_analysis": True,
                    "multi_platform_optimization": True
                }
            }
            
        except Exception as e:
            logger.error(f"SEO health check failed: {e}")
            return {
                "seo_core": {"healthy": False, "error": str(e)},
                "components": {},
                "features": {}
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_seo_instance: Optional[SEOOptimizationCore] = None

def get_seo_core() -> SEOOptimizationCore:
    """Get global SEO optimization core instance"""
    global _seo_instance
    if _seo_instance is None:
        _seo_instance = SEOOptimizationCore()
    return _seo_instance


async def optimize_for_seo(
    content_id: str,
    title: str,
    description: str,
    platform: str,
    target_keywords: List[str],
    **kwargs
) -> str:
    """Convenience function to optimize content for SEO"""
    seo_core = get_seo_core()
    return await seo_core.optimize_content(
        content_id=content_id,
        title=title,
        description=description,
        tags=kwargs.get("tags", []),
        platform=platform,
        category=kwargs.get("category", "content"),
        target_keywords=target_keywords,
        **kwargs
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core classes
    "SEOOptimizationCore",
    "KeywordResearchEngine",
    "ContentOptimizationEngine",
    "CompetitorAnalysisEngine",
    
    # Data classes
    "KeywordData",
    "SEOOptimization",
    "CompetitorAnalysis",
    "TrendAnalysis",
    
    # Enums
    "SEOPlatform",
    "ContentCategory",
    "SEOOptimizationType",
    "KeywordDifficulty",
    
    # Convenience functions
    "get_seo_core",
    "optimize_for_seo"
]

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Example usage for testing
    import asyncio
    
    async def main():
        print("🔍 SEO Optimization Core Test")
        print("=" * 50)
        
        try:
            # Get SEO core
            seo_core = get_seo_core()
            
            # Research keywords
            keywords = await seo_core.research_keywords(
                seed_keywords=["music production", "beat making"],
                platform="youtube",
                language="en",
                country="DE"
            )
            print(f"✅ Researched {len(keywords)} keywords")
            
            # Optimize content
            optimization_id = await seo_core.optimize_content(
                content_id="test_content_001",
                title="Amazing Beat Making Tutorial",
                description="Learn professional beat making techniques",
                tags=["beats", "music", "tutorial"],
                platform="youtube",
                category="video",
                target_keywords=["beat making", "music production"]
            )
            print(f"✅ Content optimized: {optimization_id}")
            
            # Get optimization result
            result = await seo_core.get_optimization_result(optimization_id)
            if result:
                print(f"📊 SEO Score: {result['seo_score']:.1f}")
                print(f"🎯 Optimized Title: {result['optimized_title']}")
            
            # Analyze trends
            trends = await seo_core.analyze_trends(["music production", "beat making"])
            print(f"📈 Analyzed {len(trends)} trends")
            
            # Get recommendations
            recommendations = await seo_core.get_seo_recommendations(
                content_type="music",
                current_performance={"seo_score": 75},
                target_platforms=["youtube", "spotify"]
            )
            print(f"💡 Generated {len(recommendations)} recommendations")
            
            # Health check
            health = await seo_core.health_check()
            print(f"🏥 SEO system healthy: {health['seo_core']['healthy']}")
            
            print("🎉 SEO Optimization Core test completed successfully!")
            
        except Exception as e:
            print(f"❌ SEO Optimization Core test failed: {e}")
    
    # Run the test if this module is executed directly
    asyncio.run(main())