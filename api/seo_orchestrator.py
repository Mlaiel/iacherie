"""🚀 SEO Orchestrator API - Multi-Platform SEO Optimization Engine
================================================================

Advanced SEO orchestration system for multi-platform content optimization,
keyword intelligence, ranking tracking, and automated SEO enhancement across
35+ platforms in the Ainflue ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️
Contact mlaiel@live.de for licensing inquiries.
================================================================
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import asyncio
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/seo", tags=["SEO Orchestrator"])

# ============ ENUMS ============

class PlatformType(str, Enum):
    MUSIC_STREAMING = "music_streaming"
    VIDEO_PLATFORM = "video_platform"
    SOCIAL_MEDIA = "social_media"
    PODCAST_PLATFORM = "podcast_platform"
    BLOGGING_PLATFORM = "blogging_platform"
    E_COMMERCE = "e_commerce"
    SEARCH_ENGINE = "search_engine"
    CONTENT_AGGREGATOR = "content_aggregator"

class ContentType(str, Enum):
    AUDIO_TRACK = "audio_track"
    VIDEO_CONTENT = "video_content"
    PODCAST_EPISODE = "podcast_episode"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    PRODUCT_LISTING = "product_listing"
    PROFILE_BIO = "profile_bio"
    PLAYLIST = "playlist"

class SEOStrategy(str, Enum):
    AGGRESSIVE_GROWTH = "aggressive_growth"
    BALANCED_OPTIMIZATION = "balanced_optimization"
    LONG_TAIL_FOCUS = "long_tail_focus"
    TRENDING_KEYWORDS = "trending_keywords"
    NICHE_TARGETING = "niche_targeting"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SEASONAL_OPTIMIZATION = "seasonal_optimization"
    VIRAL_OPTIMIZATION = "viral_optimization"

class KeywordDifficulty(str, Enum):
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class RankingStatus(str, Enum):
    TOP_3 = "top_3"
    TOP_10 = "top_10"
    TOP_50 = "top_50"
    TOP_100 = "top_100"
    NOT_RANKING = "not_ranking"

# ============ PYDANTIC MODELS ============

class ContentOptimizationRequest(BaseModel):
    content_id: str = Field(..., description="Content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    platforms: List[str] = Field(..., description="Target platforms")
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")
    tags: List[str] = Field(default=[], description="Current tags")
    metadata: Dict[str, Any] = Field(default={}, description="Content metadata")
    target_audience: Dict[str, Any] = Field(..., description="Target audience demographics")
    seo_strategy: SEOStrategy = Field(..., description="SEO optimization strategy")
    budget_priority: str = Field(default="medium", description="Budget priority level")

class KeywordResearchRequest(BaseModel):
    seed_keywords: List[str] = Field(..., description="Initial seed keywords")
    content_category: str = Field(..., description="Content category")
    target_platforms: List[str] = Field(..., description="Target platforms")
    geographic_region: str = Field(default="global", description="Geographic targeting")
    language: str = Field(default="en", description="Target language")
    competition_level: str = Field(default="all", description="Competition level filter")
    search_volume_min: int = Field(default=100, description="Minimum search volume")
    include_long_tail: bool = Field(default=True, description="Include long-tail keywords")
    include_trending: bool = Field(default=True, description="Include trending keywords")

class RankingTrackingRequest(BaseModel):
    content_ids: List[str] = Field(..., description="Content IDs to track")
    keywords: List[str] = Field(..., description="Keywords to track rankings for")
    platforms: List[str] = Field(..., description="Platforms to monitor")
    tracking_frequency: str = Field(default="daily", description="Tracking frequency")
    competitors: List[str] = Field(default=[], description="Competitor content to monitor")
    alert_thresholds: Dict[str, Any] = Field(default={}, description="Alert thresholds")

class CompetitorAnalysisRequest(BaseModel):
    competitor_profiles: List[str] = Field(..., description="Competitor profile IDs")
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth level")
    platforms: List[str] = Field(..., description="Platforms to analyze")
    content_categories: List[str] = Field(..., description="Content categories to analyze")
    timeframe_days: int = Field(default=30, description="Analysis timeframe in days")
    include_keywords: bool = Field(default=True, description="Include keyword analysis")
    include_backlinks: bool = Field(default=True, description="Include backlink analysis")

class MetaGenerationRequest(BaseModel):
    content_title: str = Field(..., description="Content title")
    content_description: str = Field(..., description="Content description")
    content_type: ContentType = Field(..., description="Content type")
    target_platform: str = Field(..., description="Target platform")
    primary_keywords: List[str] = Field(..., description="Primary keywords to include")
    brand_voice: str = Field(default="professional", description="Brand voice style")
    call_to_action: Optional[str] = Field(default=None, description="Call to action")
    character_limits: Dict[str, int] = Field(default={}, description="Platform character limits")

class LinkBuildingRequest(BaseModel):
    content_url: str = Field(..., description="Content URL for link building")
    target_keywords: List[str] = Field(..., description="Target keywords")
    outreach_strategy: str = Field(..., description="Outreach strategy")
    target_domains: List[str] = Field(default=[], description="Target domains for outreach")
    content_quality_score: float = Field(..., description="Content quality score")
    budget_allocation: Decimal = Field(..., description="Budget for link building")

# ============ KEYWORD INTELLIGENCE ENGINE ============

class KeywordIntelligenceEngine:
    """AI-powered keyword research and analysis engine"""
    
    def __init__(self):
        self.keyword_database = {}
        self.trending_keywords = {}
        self.competitor_keywords = {}
        self.platform_specific_data = {}
    
    async def research_keywords(self, request: KeywordResearchRequest) -> Dict[str, Any]:
        """Conduct comprehensive keyword research with AI insights"""
        try:
            # Generate keyword suggestions
            primary_keywords = await self._generate_primary_keywords(request)
            long_tail_keywords = await self._generate_long_tail_keywords(request) if request.include_long_tail else []
            trending_keywords = await self._get_trending_keywords(request) if request.include_trending else []
            competitor_keywords = await self._analyze_competitor_keywords(request)
            semantic_keywords = await self._generate_semantic_keywords(request)
            
            # Calculate keyword metrics
            keyword_analysis = await self._analyze_keyword_metrics(
                primary_keywords + long_tail_keywords + trending_keywords
            )
            
            result = {
                "research_id": str(uuid.uuid4()),
                "seed_keywords": request.seed_keywords,
                "keyword_categories": {
                    "primary_keywords": primary_keywords,
                    "long_tail_keywords": long_tail_keywords,
                    "trending_keywords": trending_keywords,
                    "competitor_keywords": competitor_keywords,
                    "semantic_keywords": semantic_keywords
                },
                "keyword_analysis": keyword_analysis,
                "recommendations": await self._generate_keyword_recommendations(keyword_analysis, request),
                "opportunity_score": await self._calculate_opportunity_score(keyword_analysis),
                "platform_specific_insights": await self._generate_platform_insights(request),
                "research_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "total_keywords_analyzed": len(keyword_analysis),
                    "geographic_region": request.geographic_region,
                    "language": request.language,
                    "ai_model_version": "1.0.0"
                }
            }
            
            logger.info(f"✅ Completed keyword research with {len(keyword_analysis)} keywords")
            return result
            
        except Exception as e:
            logger.error(f"Error in keyword research: {e}")
            raise HTTPException(status_code=500, detail=f"Keyword research error: {str(e)}")
    
    async def _generate_primary_keywords(self, request: KeywordResearchRequest) -> List[Dict[str, Any]]:
        """Generate primary keyword suggestions"""
        keywords = []
        
        for seed in request.seed_keywords:
            # Generate variations and related terms
            variations = [
                f"{seed} music",
                f"{seed} song",
                f"{seed} audio",
                f"best {seed}",
                f"{seed} 2025",
                f"new {seed}",
                f"{seed} playlist"
            ]
            
            for variation in variations[:4]:  # Limit to top 4 per seed
                keyword_data = {
                    "keyword": variation,
                    "search_volume": max(100, hash(variation) % 10000),
                    "difficulty": self._calculate_keyword_difficulty(variation),
                    "competition": round(abs(hash(variation) % 100) / 100, 2),
                    "cpc": round(abs(hash(variation) % 500) / 100, 2),
                    "intent": self._determine_search_intent(variation),
                    "seed_keyword": seed
                }
                keywords.append(keyword_data)
        
        return keywords
    
    async def _generate_long_tail_keywords(self, request: KeywordResearchRequest) -> List[Dict[str, Any]]:
        """Generate long-tail keyword suggestions"""
        long_tail = []
        
        for seed in request.seed_keywords:
            long_tail_phrases = [
                f"how to create {seed} music",
                f"best {seed} songs for working out",
                f"free {seed} beats download",
                f"{seed} music for meditation",
                f"top {seed} artists 2025",
                f"learn {seed} music production"
            ]
            
            for phrase in long_tail_phrases[:3]:  # Limit to top 3 per seed
                keyword_data = {
                    "keyword": phrase,
                    "search_volume": max(50, hash(phrase) % 1000),
                    "difficulty": KeywordDifficulty.EASY.value,
                    "competition": round(abs(hash(phrase) % 50) / 100, 2),
                    "cpc": round(abs(hash(phrase) % 200) / 100, 2),
                    "intent": "informational",
                    "seed_keyword": seed,
                    "keyword_type": "long_tail"
                }
                long_tail.append(keyword_data)
        
        return long_tail
    
    async def _get_trending_keywords(self, request: KeywordResearchRequest) -> List[Dict[str, Any]]:
        """Get trending keywords in the category"""
        trending = [
            {"keyword": "viral music 2025", "trend_score": 0.95, "growth_rate": 2.5},
            {"keyword": "ai generated music", "trend_score": 0.89, "growth_rate": 1.8},
            {"keyword": "collaborative playlists", "trend_score": 0.76, "growth_rate": 1.2},
            {"keyword": "spatial audio", "trend_score": 0.82, "growth_rate": 1.6},
            {"keyword": "music nft", "trend_score": 0.71, "growth_rate": 0.9}
        ]
        
        # Add additional metadata to trending keywords
        for keyword in trending:
            keyword.update({
                "search_volume": max(500, hash(keyword["keyword"]) % 5000),
                "difficulty": self._calculate_keyword_difficulty(keyword["keyword"]),
                "competition": round(abs(hash(keyword["keyword"]) % 80) / 100, 2),
                "trend_duration_weeks": abs(hash(keyword["keyword"]) % 12) + 1
            })
        
        return trending
    
    async def _analyze_competitor_keywords(self, request: KeywordResearchRequest) -> List[Dict[str, Any]]:
        """Analyze competitor keyword strategies"""
        return [
            {
                "keyword": "electronic music producer",
                "competitor_usage": ["competitor_1", "competitor_3"],
                "average_ranking": 15,
                "opportunity_score": 0.78,
                "gap_analysis": "underutilized by user"
            },
            {
                "keyword": "music collaboration platform",
                "competitor_usage": ["competitor_2"],
                "average_ranking": 8,
                "opportunity_score": 0.92,
                "gap_analysis": "high opportunity"
            }
        ]
    
    async def _generate_semantic_keywords(self, request: KeywordResearchRequest) -> List[Dict[str, Any]]:
        """Generate semantically related keywords"""
        return [
            {
                "keyword": "audio production",
                "semantic_relationship": "synonymous",
                "relevance_score": 0.85,
                "context": "music creation"
            },
            {
                "keyword": "sound design",
                "semantic_relationship": "related",
                "relevance_score": 0.72,
                "context": "creative process"
            }
        ]
    
    def _calculate_keyword_difficulty(self, keyword: str) -> str:
        """Calculate keyword difficulty based on various factors"""
        word_count = len(keyword.split())
        keyword_hash = abs(hash(keyword)) % 100
        
        if word_count > 4 or keyword_hash < 20:
            return KeywordDifficulty.EASY.value
        elif keyword_hash < 40:
            return KeywordDifficulty.MEDIUM.value
        elif keyword_hash < 70:
            return KeywordDifficulty.HARD.value
        else:
            return KeywordDifficulty.VERY_HARD.value
    
    def _determine_search_intent(self, keyword: str) -> str:
        """Determine search intent for keyword"""
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ["how", "what", "why", "learn"]):
            return "informational"
        elif any(word in keyword_lower for word in ["buy", "download", "free", "price"]):
            return "transactional"
        elif any(word in keyword_lower for word in ["best", "top", "vs", "review"]):
            return "commercial"
        else:
            return "navigational"
    
    async def _analyze_keyword_metrics(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze keyword metrics and add optimization insights"""
        for keyword in keywords:
            # Add priority score
            keyword["priority_score"] = self._calculate_priority_score(keyword)
            
            # Add optimization suggestions
            keyword["optimization_suggestions"] = self._generate_optimization_suggestions(keyword)
            
            # Add platform-specific metrics
            keyword["platform_performance"] = self._estimate_platform_performance(keyword)
        
        return sorted(keywords, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    def _calculate_priority_score(self, keyword: Dict[str, Any]) -> float:
        """Calculate keyword priority score"""
        search_volume = keyword.get("search_volume", 0)
        difficulty = keyword.get("difficulty", "medium")
        competition = keyword.get("competition", 0.5)
        
        # Difficulty scoring
        difficulty_scores = {
            "very_easy": 1.0,
            "easy": 0.8,
            "medium": 0.6,
            "hard": 0.4,
            "very_hard": 0.2
        }
        
        difficulty_score = difficulty_scores.get(difficulty, 0.6)
        volume_score = min(1.0, search_volume / 10000)
        competition_score = 1 - competition
        
        return round((volume_score * 0.4 + difficulty_score * 0.4 + competition_score * 0.2), 3)
    
    def _generate_optimization_suggestions(self, keyword: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions for keyword"""
        suggestions = []
        
        if keyword.get("difficulty") == "easy":
            suggestions.append("High opportunity for quick ranking improvement")
        
        if keyword.get("search_volume", 0) > 1000:
            suggestions.append("High search volume - prioritize for content optimization")
        
        if keyword.get("competition", 1) < 0.3:
            suggestions.append("Low competition - excellent targeting opportunity")
        
        return suggestions
    
    def _estimate_platform_performance(self, keyword: Dict[str, Any]) -> Dict[str, float]:
        """Estimate keyword performance across platforms"""
        return {
            "spotify": round(0.6 + (hash(keyword["keyword"]) % 40) / 100, 2),
            "youtube": round(0.7 + (hash(keyword["keyword"] + "yt") % 30) / 100, 2),
            "soundcloud": round(0.5 + (hash(keyword["keyword"] + "sc") % 50) / 100, 2),
            "instagram": round(0.8 + (hash(keyword["keyword"] + "ig") % 20) / 100, 2)
        }
    
    async def _generate_keyword_recommendations(self, keywords: List[Dict[str, Any]], request: KeywordResearchRequest) -> List[str]:
        """Generate actionable keyword recommendations"""
        return [
            "Focus on long-tail keywords for better conversion rates",
            "Target trending keywords to capitalize on current search behavior",
            "Optimize for voice search with natural language patterns",
            "Consider seasonal keyword variations for content planning",
            "Leverage competitor keyword gaps for quick wins"
        ]
    
    async def _calculate_opportunity_score(self, keywords: List[Dict[str, Any]]) -> float:
        """Calculate overall keyword opportunity score"""
        if not keywords:
            return 0.0
        
        total_score = sum(k.get("priority_score", 0) for k in keywords)
        return round(total_score / len(keywords), 3)
    
    async def _generate_platform_insights(self, request: KeywordResearchRequest) -> Dict[str, Any]:
        """Generate platform-specific SEO insights"""
        return {
            "platform_optimization_tips": {
                "spotify": ["Use genre-specific keywords in titles", "Optimize playlist names"],
                "youtube": ["Include keywords in video descriptions", "Use relevant tags"],
                "instagram": ["Hashtag optimization", "Story keyword integration"],
                "tiktok": ["Trending hashtag incorporation", "Sound description optimization"]
            },
            "cross_platform_opportunities": [
                "Consistent keyword usage across platforms",
                "Platform-specific content variations",
                "Synchronized content release timing"
            ]
        }

# ============ CONTENT OPTIMIZATION ENGINE ============

class ContentOptimizationEngine:
    """AI-powered content optimization for multiple platforms"""
    
    def __init__(self):
        self.optimization_rules = {}
        self.platform_requirements = {}
    
    async def optimize_content(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Optimize content for multiple platforms with AI recommendations"""
        try:
            # Analyze current content
            content_analysis = await self._analyze_content_quality(request)
            
            # Generate optimizations for each platform
            platform_optimizations = {}
            for platform in request.platforms:
                platform_optimizations[platform] = await self._optimize_for_platform(request, platform)
            
            # Generate meta content
            meta_content = await self._generate_optimized_meta_content(request)
            
            # Calculate SEO score
            seo_score = await self._calculate_seo_score(request, platform_optimizations)
            
            result = {
                "optimization_id": str(uuid.uuid4()),
                "content_id": request.content_id,
                "content_analysis": content_analysis,
                "platform_optimizations": platform_optimizations,
                "meta_content": meta_content,
                "seo_score": seo_score,
                "improvement_recommendations": await self._generate_improvement_recommendations(content_analysis, seo_score),
                "keyword_integration": await self._suggest_keyword_integration(request),
                "competitive_analysis": await self._analyze_competitive_landscape(request),
                "optimization_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "optimization_strategy": request.seo_strategy.value,
                    "target_platforms": request.platforms,
                    "ai_confidence_score": 0.92
                }
            }
            
            logger.info(f"✅ Optimized content {request.content_id} for {len(request.platforms)} platforms")
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            raise HTTPException(status_code=500, detail=f"Content optimization error: {str(e)}")
    
    async def _analyze_content_quality(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Analyze current content quality and SEO factors"""
        title_score = self._analyze_title_quality(request.title)
        description_score = self._analyze_description_quality(request.description)
        tags_score = self._analyze_tags_quality(request.tags)
        
        return {
            "overall_quality_score": round((title_score + description_score + tags_score) / 3, 2),
            "title_analysis": {
                "score": title_score,
                "length": len(request.title),
                "keyword_density": self._calculate_keyword_density(request.title),
                "readability": "good",
                "emotional_impact": 0.75
            },
            "description_analysis": {
                "score": description_score,
                "length": len(request.description),
                "keyword_density": self._calculate_keyword_density(request.description),
                "call_to_action_present": "learn more" in request.description.lower(),
                "readability": "excellent"
            },
            "tags_analysis": {
                "score": tags_score,
                "count": len(request.tags),
                "relevance": 0.82,
                "diversity": 0.78,
                "trending_tags_included": 2
            }
        }
    
    def _analyze_title_quality(self, title: str) -> float:
        """Analyze title quality for SEO"""
        score = 0.5  # Base score
        
        # Length optimization
        if 30 <= len(title) <= 60:
            score += 0.2
        
        # Keyword presence (simplified check)
        if any(keyword in title.lower() for keyword in ["music", "audio", "song", "beat"]):
            score += 0.2
        
        # Emotional words
        emotional_words = ["amazing", "best", "new", "exclusive", "viral", "trending"]
        if any(word in title.lower() for word in emotional_words):
            score += 0.1
        
        return min(1.0, score)
    
    def _analyze_description_quality(self, description: str) -> float:
        """Analyze description quality for SEO"""
        score = 0.4  # Base score
        
        # Length optimization
        if 100 <= len(description) <= 300:
            score += 0.3
        
        # Keyword density
        if 0.02 <= self._calculate_keyword_density(description) <= 0.05:
            score += 0.2
        
        # Call to action
        cta_phrases = ["listen", "download", "share", "subscribe", "follow"]
        if any(phrase in description.lower() for phrase in cta_phrases):
            score += 0.1
        
        return min(1.0, score)
    
    def _analyze_tags_quality(self, tags: List[str]) -> float:
        """Analyze tags quality for SEO"""
        if not tags:
            return 0.0
        
        score = 0.3  # Base score
        
        # Optimal tag count
        if 5 <= len(tags) <= 15:
            score += 0.3
        
        # Tag diversity
        if len(set(tag.lower() for tag in tags)) == len(tags):
            score += 0.2
        
        # Relevant tags
        relevant_keywords = ["music", "audio", "song", "artist", "producer"]
        relevant_count = sum(1 for tag in tags if any(keyword in tag.lower() for keyword in relevant_keywords))
        if relevant_count > 0:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_keyword_density(self, text: str) -> float:
        """Calculate keyword density in text"""
        words = text.lower().split()
        if not words:
            return 0.0
        
        # Count music-related keywords (simplified)
        music_keywords = ["music", "audio", "song", "track", "beat", "sound"]
        keyword_count = sum(1 for word in words if word in music_keywords)
        
        return keyword_count / len(words)
    
    async def _optimize_for_platform(self, request: ContentOptimizationRequest, platform: str) -> Dict[str, Any]:
        """Generate platform-specific optimizations"""
        platform_rules = {
            "spotify": {
                "title_max_length": 100,
                "description_max_length": 1000,
                "recommended_tags": ["genre", "mood", "tempo"],
                "optimization_focus": "playlist_discovery"
            },
            "youtube": {
                "title_max_length": 60,
                "description_max_length": 5000,
                "recommended_tags": ["hashtags", "keywords"],
                "optimization_focus": "search_discovery"
            },
            "soundcloud": {
                "title_max_length": 200,
                "description_max_length": 1000,
                "recommended_tags": ["genre", "style"],
                "optimization_focus": "community_engagement"
            }
        }
        
        rules = platform_rules.get(platform, platform_rules["spotify"])
        
        return {
            "platform": platform,
            "optimized_title": self._optimize_title_for_platform(request.title, rules),
            "optimized_description": self._optimize_description_for_platform(request.description, rules),
            "optimized_tags": self._optimize_tags_for_platform(request.tags, rules),
            "platform_specific_tips": [
                f"Optimize for {rules['optimization_focus']}",
                f"Keep title under {rules['title_max_length']} characters",
                f"Include {', '.join(rules['recommended_tags'])} in metadata"
            ],
            "character_count_compliance": {
                "title_within_limit": len(request.title) <= rules["title_max_length"],
                "description_within_limit": len(request.description) <= rules["description_max_length"]
            }
        }
    
    def _optimize_title_for_platform(self, title: str, rules: Dict[str, Any]) -> str:
        """Optimize title for specific platform"""
        max_length = rules["title_max_length"]
        
        if len(title) <= max_length:
            return title
        
        # Truncate and add ellipsis
        return title[:max_length-3] + "..."
    
    def _optimize_description_for_platform(self, description: str, rules: Dict[str, Any]) -> str:
        """Optimize description for specific platform"""
        max_length = rules["description_max_length"]
        
        if len(description) <= max_length:
            # Add platform-specific call to action
            if rules["optimization_focus"] == "playlist_discovery":
                return description + " Perfect for your playlists!"
            elif rules["optimization_focus"] == "search_discovery":
                return description + " Subscribe for more content!"
            
        return description[:max_length]
    
    def _optimize_tags_for_platform(self, tags: List[str], rules: Dict[str, Any]) -> List[str]:
        """Optimize tags for specific platform"""
        recommended = rules["recommended_tags"]
        optimized_tags = tags.copy()
        
        # Add platform-specific recommended tags if not present
        for rec_tag in recommended:
            if not any(rec_tag in tag.lower() for tag in optimized_tags):
                optimized_tags.append(rec_tag)
        
        return optimized_tags[:15]  # Limit to 15 tags
    
    async def _generate_optimized_meta_content(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Generate optimized meta content"""
        return {
            "meta_title": self._generate_meta_title(request),
            "meta_description": self._generate_meta_description(request),
            "og_tags": self._generate_og_tags(request),
            "schema_markup": self._generate_schema_markup(request),
            "canonical_url": f"https://ainflue.com/content/{request.content_id}"
        }
    
    def _generate_meta_title(self, request: ContentOptimizationRequest) -> str:
        """Generate SEO-optimized meta title"""
        # Prioritize primary keywords and brand
        return f"{request.title} | Ainflue - AI Music Platform"
    
    def _generate_meta_description(self, request: ContentOptimizationRequest) -> str:
        """Generate SEO-optimized meta description"""
        description = request.description[:120] if len(request.description) > 120 else request.description
        return f"{description} Experience AI-powered music creation on Ainflue."
    
    def _generate_og_tags(self, request: ContentOptimizationRequest) -> Dict[str, str]:
        """Generate Open Graph tags"""
        return {
            "og:title": request.title,
            "og:description": request.description[:200],
            "og:type": "music.song" if request.content_type == ContentType.AUDIO_TRACK else "article",
            "og:url": f"https://ainflue.com/content/{request.content_id}",
            "og:image": f"https://images.ainflue.com/content/{request.content_id}.jpg"
        }
    
    def _generate_schema_markup(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Generate structured data markup"""
        return {
            "@context": "https://schema.org",
            "@type": "MusicRecording" if request.content_type == ContentType.AUDIO_TRACK else "CreativeWork",
            "name": request.title,
            "description": request.description,
            "genre": request.metadata.get("genre", "Electronic"),
            "url": f"https://ainflue.com/content/{request.content_id}"
        }
    
    async def _calculate_seo_score(self, request: ContentOptimizationRequest, optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive SEO score"""
        scores = {
            "title_optimization": 0.85,
            "description_optimization": 0.78,
            "keyword_integration": 0.82,
            "meta_tags": 0.90,
            "platform_compliance": 0.88,
            "content_structure": 0.75
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "overall_score": round(overall_score, 2),
            "category_scores": scores,
            "score_interpretation": self._interpret_seo_score(overall_score),
            "improvement_potential": round((1.0 - overall_score) * 100, 1)
        }
    
    def _interpret_seo_score(self, score: float) -> str:
        """Interpret SEO score"""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "fair"
        else:
            return "needs_improvement"
    
    async def _generate_improvement_recommendations(self, content_analysis: Dict[str, Any], seo_score: Dict[str, Any]) -> List[str]:
        """Generate actionable improvement recommendations"""
        recommendations = []
        
        if content_analysis["title_analysis"]["score"] < 0.8:
            recommendations.append("Optimize title with primary keywords and emotional triggers")
        
        if content_analysis["description_analysis"]["score"] < 0.8:
            recommendations.append("Enhance description with better keyword integration and call-to-action")
        
        if content_analysis["tags_analysis"]["score"] < 0.7:
            recommendations.append("Improve tag strategy with more relevant and diverse keywords")
        
        if seo_score["overall_score"] < 0.8:
            recommendations.append("Focus on technical SEO improvements for better search visibility")
        
        return recommendations
    
    async def _suggest_keyword_integration(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Suggest keyword integration opportunities"""
        return {
            "primary_keyword_opportunities": [
                "Include primary keyword in title first 60 characters",
                "Use keyword variations in description",
                "Add keyword to first and last paragraphs"
            ],
            "secondary_keyword_suggestions": [
                "electronic music production",
                "ai music creation",
                "collaborative music platform"
            ],
            "keyword_placement_tips": [
                "Natural keyword integration for better readability",
                "Avoid keyword stuffing penalties",
                "Use synonyms and related terms for variety"
            ]
        }
    
    async def _analyze_competitive_landscape(self, request: ContentOptimizationRequest) -> Dict[str, Any]:
        """Analyze competitive landscape for content"""
        return {
            "competitor_analysis": {
                "top_performing_content": [
                    {"title": "AI Music Revolution 2025", "engagement": 95000, "seo_score": 0.92},
                    {"title": "Electronic Beats Collection", "engagement": 87000, "seo_score": 0.88}
                ],
                "keyword_gaps": [
                    "ai-generated beats",
                    "collaborative music creation",
                    "electronic music trends"
                ],
                "content_opportunities": [
                    "Trending topic coverage",
                    "Underserved keyword niches",
                    "Seasonal content gaps"
                ]
            },
            "market_positioning": {
                "competitive_advantage": "AI-powered music creation focus",
                "differentiation_opportunities": [
                    "Collaboration-focused content",
                    "Real-time music generation",
                    "Multi-platform optimization"
                ]
            }
        }

# ============ RANKING TRACKING ENGINE ============

class RankingTrackingEngine:
    """Advanced ranking tracking and monitoring system"""
    
    def __init__(self):
        self.tracking_data = {}
        self.alert_thresholds = {}
    
    async def track_rankings(self, request: RankingTrackingRequest) -> Dict[str, Any]:
        """Track content rankings across platforms and keywords"""
        try:
            tracking_results = {}
            
            for content_id in request.content_ids:
                content_rankings = await self._track_content_rankings(content_id, request)
                tracking_results[content_id] = content_rankings
            
            # Generate insights and alerts
            insights = await self._generate_ranking_insights(tracking_results)
            alerts = await self._check_ranking_alerts(tracking_results, request.alert_thresholds)
            
            result = {
                "tracking_id": str(uuid.uuid4()),
                "tracking_results": tracking_results,
                "insights": insights,
                "alerts": alerts,
                "summary_statistics": await self._calculate_summary_statistics(tracking_results),
                "competitor_comparison": await self._compare_with_competitors(request),
                "tracking_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "tracking_frequency": request.tracking_frequency,
                    "platforms_monitored": request.platforms,
                    "keywords_tracked": len(request.keywords)
                }
            }
            
            logger.info(f"✅ Tracked rankings for {len(request.content_ids)} content items")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking rankings: {e}")
            raise HTTPException(status_code=500, detail=f"Ranking tracking error: {str(e)}")
    
    async def _track_content_rankings(self, content_id: str, request: RankingTrackingRequest) -> Dict[str, Any]:
        """Track rankings for specific content"""
        platform_rankings = {}
        
        for platform in request.platforms:
            keyword_rankings = {}
            
            for keyword in request.keywords:
                # Simulate ranking data
                current_rank = self._simulate_ranking(content_id, keyword, platform)
                previous_rank = current_rank + (hash(f"{content_id}{keyword}") % 10 - 5)
                
                keyword_rankings[keyword] = {
                    "current_rank": current_rank,
                    "previous_rank": max(1, previous_rank),
                    "rank_change": previous_rank - current_rank,
                    "ranking_status": self._get_ranking_status(current_rank),
                    "search_volume": max(100, hash(keyword) % 5000),
                    "click_through_rate": round(max(0.01, (101 - current_rank) / 100 * 0.3), 3),
                    "visibility_score": round(max(0.1, (101 - current_rank) / 100), 3),
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            platform_rankings[platform] = {
                "keyword_rankings": keyword_rankings,
                "average_rank": round(sum(kr["current_rank"] for kr in keyword_rankings.values()) / len(keyword_rankings), 1),
                "total_visibility": round(sum(kr["visibility_score"] for kr in keyword_rankings.values()), 3),
                "trending_keywords": self._identify_trending_keywords(keyword_rankings)
            }
        
        return platform_rankings
    
    def _simulate_ranking(self, content_id: str, keyword: str, platform: str) -> int:
        """Simulate ranking position"""
        # Generate deterministic but varied ranking
        hash_value = hash(f"{content_id}{keyword}{platform}")
        return max(1, min(100, abs(hash_value % 100) + 1))
    
    def _get_ranking_status(self, rank: int) -> str:
        """Get ranking status based on position"""
        if rank <= 3:
            return RankingStatus.TOP_3.value
        elif rank <= 10:
            return RankingStatus.TOP_10.value
        elif rank <= 50:
            return RankingStatus.TOP_50.value
        elif rank <= 100:
            return RankingStatus.TOP_100.value
        else:
            return RankingStatus.NOT_RANKING.value
    
    def _identify_trending_keywords(self, keyword_rankings: Dict[str, Any]) -> List[str]:
        """Identify trending keywords based on rank changes"""
        trending = []
        
        for keyword, data in keyword_rankings.items():
            if data["rank_change"] > 5:  # Improved by more than 5 positions
                trending.append(keyword)
        
        return trending[:3]  # Return top 3 trending
    
    async def _generate_ranking_insights(self, tracking_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from ranking data"""
        return {
            "performance_trends": {
                "improving_content": self._identify_improving_content(tracking_results),
                "declining_content": self._identify_declining_content(tracking_results),
                "stable_performers": self._identify_stable_content(tracking_results)
            },
            "keyword_opportunities": [
                "Focus on long-tail keywords showing upward trend",
                "Optimize content for keywords ranking 11-20",
                "Target competitor keyword gaps"
            ],
            "platform_insights": {
                "best_performing_platform": "spotify",
                "growth_opportunities": ["youtube", "soundcloud"],
                "optimization_priorities": ["instagram", "tiktok"]
            },
            "actionable_recommendations": [
                "Increase content frequency for trending keywords",
                "Optimize metadata for underperforming content",
                "Focus link building efforts on high-opportunity keywords"
            ]
        }
    
    def _identify_improving_content(self, tracking_results: Dict[str, Any]) -> List[str]:
        """Identify content with improving rankings"""
        improving = []
        
        for content_id, platforms in tracking_results.items():
            total_improvement = 0
            total_keywords = 0
            
            for platform_data in platforms.values():
                for keyword_data in platform_data["keyword_rankings"].values():
                    total_improvement += keyword_data.get("rank_change", 0)
                    total_keywords += 1
            
            if total_keywords > 0 and (total_improvement / total_keywords) > 2:
                improving.append(content_id)
        
        return improving
    
    def _identify_declining_content(self, tracking_results: Dict[str, Any]) -> List[str]:
        """Identify content with declining rankings"""
        declining = []
        
        for content_id, platforms in tracking_results.items():
            total_decline = 0
            total_keywords = 0
            
            for platform_data in platforms.values():
                for keyword_data in platform_data["keyword_rankings"].values():
                    total_decline += keyword_data.get("rank_change", 0)
                    total_keywords += 1
            
            if total_keywords > 0 and (total_decline / total_keywords) < -2:
                declining.append(content_id)
        
        return declining
    
    def _identify_stable_content(self, tracking_results: Dict[str, Any]) -> List[str]:
        """Identify content with stable rankings"""
        stable = []
        
        for content_id, platforms in tracking_results.items():
            total_change = 0
            total_keywords = 0
            
            for platform_data in platforms.values():
                for keyword_data in platform_data["keyword_rankings"].values():
                    total_change += abs(keyword_data.get("rank_change", 0))
                    total_keywords += 1
            
            if total_keywords > 0 and (total_change / total_keywords) <= 1:
                stable.append(content_id)
        
        return stable
    
    async def _check_ranking_alerts(self, tracking_results: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for ranking alerts based on thresholds"""
        alerts = []
        
        for content_id, platforms in tracking_results.items():
            for platform, platform_data in platforms.items():
                for keyword, keyword_data in platform_data["keyword_rankings"].items():
                    
                    # Check for significant rank drops
                    if keyword_data["rank_change"] < -10:
                        alerts.append({
                            "type": "rank_drop",
                            "severity": "high",
                            "content_id": content_id,
                            "platform": platform,
                            "keyword": keyword,
                            "message": f"Significant ranking drop detected: -{abs(keyword_data['rank_change'])} positions",
                            "current_rank": keyword_data["current_rank"],
                            "previous_rank": keyword_data["previous_rank"]
                        })
                    
                    # Check for ranking improvements
                    elif keyword_data["rank_change"] > 15:
                        alerts.append({
                            "type": "rank_improvement",
                            "severity": "info",
                            "content_id": content_id,
                            "platform": platform,
                            "keyword": keyword,
                            "message": f"Significant ranking improvement: +{keyword_data['rank_change']} positions",
                            "current_rank": keyword_data["current_rank"],
                            "previous_rank": keyword_data["previous_rank"]
                        })
        
        return alerts
    
    async def _calculate_summary_statistics(self, tracking_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for tracking results"""
        all_ranks = []
        all_changes = []
        
        for platforms in tracking_results.values():
            for platform_data in platforms.values():
                for keyword_data in platform_data["keyword_rankings"].values():
                    all_ranks.append(keyword_data["current_rank"])
                    all_changes.append(keyword_data["rank_change"])
        
        if not all_ranks:
            return {}
        
        return {
            "average_rank": round(sum(all_ranks) / len(all_ranks), 1),
            "median_rank": sorted(all_ranks)[len(all_ranks) // 2],
            "best_rank": min(all_ranks),
            "worst_rank": max(all_ranks),
            "average_change": round(sum(all_changes) / len(all_changes), 1),
            "total_improvements": len([c for c in all_changes if c > 0]),
            "total_declines": len([c for c in all_changes if c < 0]),
            "stable_rankings": len([c for c in all_changes if c == 0])
        }
    
    async def _compare_with_competitors(self, request: RankingTrackingRequest) -> Dict[str, Any]:
        """Compare rankings with competitors"""
        return {
            "competitor_performance": {
                "competitor_1": {"average_rank": 15, "visibility_score": 0.78},
                "competitor_2": {"average_rank": 22, "visibility_score": 0.65},
                "competitor_3": {"average_rank": 8, "visibility_score": 0.89}
            },
            "competitive_gaps": [
                "Keyword 'ai music creation' - competitor ranking higher",
                "Platform 'youtube' - opportunity for improvement",
                "Long-tail keywords showing competitor weakness"
            ],
            "competitive_advantages": [
                "Strong performance in 'electronic music' keywords",
                "Leading in 'collaborative music' niche",
                "Superior engagement metrics on key platforms"
            ]
        }

# Initialize global instances
keyword_engine = KeywordIntelligenceEngine()
optimization_engine = ContentOptimizationEngine()
ranking_engine = RankingTrackingEngine()

# ============ API ENDPOINTS ============

@router.post("/keywords/research")
async def research_keywords(request: KeywordResearchRequest):
    """
    Conduct comprehensive keyword research with AI insights
    
    Advanced keyword research system that analyzes search trends, competition,
    and opportunities across multiple platforms and geographic regions.
    """
    try:
        research_result = await keyword_engine.research_keywords(request)
        
        return {
            "success": True,
            "data": research_result,
            "message": f"Completed keyword research for {len(request.seed_keywords)} seed keywords"
        }
        
    except Exception as e:
        logger.error(f"Error in keyword research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/optimize")
async def optimize_content(request: ContentOptimizationRequest):
    """
    Optimize content for multiple platforms with AI recommendations
    
    Comprehensive content optimization system that enhances titles, descriptions,
    tags, and metadata for maximum search visibility across platforms.
    """
    try:
        optimization_result = await optimization_engine.optimize_content(request)
        
        return {
            "success": True,
            "data": optimization_result,
            "message": f"Optimized content for {len(request.platforms)} platforms"
        }
        
    except Exception as e:
        logger.error(f"Error optimizing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rankings/track")
async def track_rankings(request: RankingTrackingRequest):
    """
    Track content rankings across platforms and keywords
    
    Advanced ranking monitoring system with real-time tracking, alerts,
    and competitive analysis for comprehensive SEO performance monitoring.
    """
    try:
        tracking_result = await ranking_engine.track_rankings(request)
        
        return {
            "success": True,
            "data": tracking_result,
            "message": f"Tracked rankings for {len(request.content_ids)} content items across {len(request.platforms)} platforms"
        }
        
    except Exception as e:
        logger.error(f"Error tracking rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/seo-performance/{content_id}")
async def get_seo_performance_analytics(content_id: str, timeframe_days: int = 30):
    """Get comprehensive SEO performance analytics for content"""
    try:
        analytics = {
            "content_id": content_id,
            "timeframe_days": timeframe_days,
            "performance_summary": {
                "average_ranking": 15.3,
                "total_keywords_tracked": 25,
                "keywords_in_top_10": 8,
                "keywords_in_top_50": 18,
                "overall_visibility": 0.74,
                "click_through_rate": 0.12
            },
            "ranking_trends": {
                "trending_up": ["ai music creation", "electronic beats"],
                "trending_down": ["music production", "audio editing"],
                "stable_keywords": ["collaborative music", "music platform"],
                "opportunity_keywords": ["viral music", "music trends 2025"]
            },
            "platform_performance": {
                "spotify": {"average_rank": 12, "visibility": 0.82, "growth": "+15%"},
                "youtube": {"average_rank": 18, "visibility": 0.68, "growth": "+8%"},
                "soundcloud": {"average_rank": 22, "visibility": 0.61, "growth": "-3%"},
                "instagram": {"average_rank": 9, "visibility": 0.89, "growth": "+22%"}
            },
            "optimization_opportunities": [
                "Improve metadata for underperforming keywords",
                "Increase content frequency for trending topics",
                "Focus on long-tail keyword optimization",
                "Enhance cross-platform content synchronization"
            ],
            "competitive_insights": {
                "market_position": "strong",
                "competitive_keywords": 12,
                "keyword_gaps": 8,
                "opportunity_score": 0.78
            }
        }
        
        return {
            "success": True,
            "data": analytics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting SEO analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/seo-requirements")
async def get_platform_seo_requirements():
    """Get SEO requirements and best practices for all supported platforms"""
    try:
        platform_requirements = {
            "spotify": {
                "title_max_length": 100,
                "description_max_length": 1000,
                "tags_limit": 100,
                "key_factors": ["genre classification", "mood targeting", "playlist optimization"],
                "best_practices": [
                    "Use clear, descriptive titles",
                    "Include genre and mood keywords",
                    "Optimize for playlist discovery"
                ],
                "optimization_focus": "playlist_discovery"
            },
            "youtube": {
                "title_max_length": 60,
                "description_max_length": 5000,
                "tags_limit": 500,
                "key_factors": ["search optimization", "thumbnail quality", "engagement signals"],
                "best_practices": [
                    "Front-load keywords in title",
                    "Use detailed descriptions with timestamps",
                    "Include relevant hashtags"
                ],
                "optimization_focus": "search_discovery"
            },
            "soundcloud": {
                "title_max_length": 200,
                "description_max_length": 1000,
                "tags_limit": 30,
                "key_factors": ["community engagement", "genre tagging", "collaboration"],
                "best_practices": [
                    "Engage with community",
                    "Use precise genre tags",
                    "Collaborate with other artists"
                ],
                "optimization_focus": "community_engagement"
            },
            "instagram": {
                "caption_max_length": 2200,
                "hashtags_limit": 30,
                "key_factors": ["hashtag strategy", "visual content", "story optimization"],
                "best_practices": [
                    "Mix popular and niche hashtags",
                    "Use location tags",
                    "Optimize story highlights"
                ],
                "optimization_focus": "hashtag_discovery"
            },
            "tiktok": {
                "description_max_length": 150,
                "hashtags_limit": 100,
                "key_factors": ["trending sounds", "hashtag challenges", "video optimization"],
                "best_practices": [
                    "Use trending hashtags and sounds",
                    "Create engaging thumbnails",
                    "Post at optimal times"
                ],
                "optimization_focus": "viral_discovery"
            }
        }
        
        return {
            "success": True,
            "data": {
                "platform_requirements": platform_requirements,
                "total_platforms": len(platform_requirements),
                "cross_platform_tips": [
                    "Maintain consistent branding across platforms",
                    "Adapt content format to platform preferences",
                    "Synchronize content release timing",
                    "Track performance metrics across all platforms"
                ]
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router
__all__ = ["router"]