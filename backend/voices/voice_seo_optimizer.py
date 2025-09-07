"""Voice Content SEO Optimization Engine

Advanced SEO optimization system for voice content discovery, search ranking,
and viral content prediction for enterprise voice content marketing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class SEOStrategy(Enum):
    """SEO optimization strategies"""
    DISCOVERY_FOCUSED = "discovery_focused"
    RANKING_FOCUSED = "ranking_focused"
    ENGAGEMENT_FOCUSED = "engagement_focused"
    VIRAL_FOCUSED = "viral_focused"
    NICHE_TARGETED = "niche_targeted"
    MAINSTREAM_APPEAL = "mainstream_appeal"


class ContentCategory(Enum):
    """Voice content categories for SEO"""
    MUSIC = "music"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICE_OVER = "voice_over"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    COMMERCIAL = "commercial"


class Platform(Enum):
    """Target platforms for SEO optimization"""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    GOOGLE_PODCASTS = "google_podcasts"
    SOUNDCLOUD = "soundcloud"
    AUDIBLE = "audible"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


@dataclass
class SEOKeywords:
    """SEO keywords analysis result"""
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    trending_keywords: List[str]
    seasonal_keywords: List[str]
    competitor_keywords: List[str]
    search_volumes: Dict[str, int]
    difficulty_scores: Dict[str, float]
    relevance_scores: Dict[str, float]


@dataclass
class SEOOptimization:
    """SEO optimization result"""
    content_id: str
    optimization_strategy: SEOStrategy
    target_platforms: List[Platform]
    optimized_title: str
    optimized_description: str
    optimized_tags: List[str]
    seo_keywords: SEOKeywords
    metadata_optimization: Dict[str, Any]
    predicted_ranking: Dict[str, float]
    viral_potential: float
    optimization_score: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TrendingAnalysis:
    """Trending content analysis"""
    trend_category: str
    trending_topics: List[str]
    trending_keywords: List[str]
    hashtag_trends: List[str]
    seasonal_patterns: Dict[str, Any]
    audience_interests: Dict[str, float]
    platform_trends: Dict[Platform, List[str]]
    growth_predictions: Dict[str, float]


@dataclass
class CompetitorAnalysis:
    """Competitor analysis for SEO"""
    competitor_content: List[Dict[str, Any]]
    market_gaps: List[str]
    opportunity_keywords: List[str]
    competitor_strategies: Dict[str, Any]
    ranking_analysis: Dict[str, Any]
    differentiation_opportunities: List[str]


class VoiceSEOOptimizer:
    """Voice Content SEO Optimization Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # SEO databases and models
        self.keyword_database = self._initialize_keyword_database()
        self.trending_data = self._initialize_trending_data()
        self.platform_algorithms = self._initialize_platform_algorithms()
        
        # SEO optimization history
        self.optimization_history: List[SEOOptimization] = []
        self.performance_tracking: Dict[str, Dict[str, Any]] = {}
        
        # AI models for SEO prediction
        self.ranking_predictor = None
        self.viral_predictor = None
        self.keyword_extractor = None
        
        # Platform-specific optimization rules
        self.platform_rules = self._initialize_platform_rules()
        
        # SEO monitoring
        self.seo_monitoring_enabled = True
        self.ranking_tracking_enabled = True
        
    def _initialize_keyword_database(self) -> Dict[str, Any]:
        """Initialize keyword database with search volumes and trends"""
        return {
            "music_keywords": {
                "original music": {"volume": 50000, "difficulty": 0.7, "trend": "rising"},
                "cover songs": {"volume": 30000, "difficulty": 0.6, "trend": "stable"},
                "instrumental": {"volume": 25000, "difficulty": 0.5, "trend": "rising"},
                "acoustic version": {"volume": 20000, "difficulty": 0.4, "trend": "stable"},
                "live performance": {"volume": 40000, "difficulty": 0.8, "trend": "rising"}
            },
            "podcast_keywords": {
                "true crime podcast": {"volume": 100000, "difficulty": 0.9, "trend": "rising"},
                "business podcast": {"volume": 80000, "difficulty": 0.8, "trend": "stable"},
                "comedy podcast": {"volume": 60000, "difficulty": 0.7, "trend": "stable"},
                "interview podcast": {"volume": 45000, "difficulty": 0.6, "trend": "rising"},
                "education podcast": {"volume": 35000, "difficulty": 0.5, "trend": "rising"}
            },
            "voice_over_keywords": {
                "commercial voice over": {"volume": 15000, "difficulty": 0.7, "trend": "stable"},
                "audiobook narration": {"volume": 25000, "difficulty": 0.6, "trend": "rising"},
                "animated voice": {"volume": 20000, "difficulty": 0.8, "trend": "rising"},
                "documentary narration": {"volume": 12000, "difficulty": 0.5, "trend": "stable"}
            },
            "trending_keywords": {
                "ai generated voice": {"volume": 75000, "difficulty": 0.9, "trend": "exploding"},
                "voice cloning": {"volume": 45000, "difficulty": 0.8, "trend": "rising"},
                "synthetic voice": {"volume": 30000, "difficulty": 0.7, "trend": "rising"},
                "voice assistant": {"volume": 90000, "difficulty": 0.9, "trend": "stable"}
            }
        }
    
    def _initialize_trending_data(self) -> Dict[str, Any]:
        """Initialize trending topics and patterns"""
        return {
            "current_trends": {
                "viral_sounds": ["aesthetic music", "lo-fi beats", "nature sounds", "meditation music"],
                "popular_topics": ["mental health", "productivity", "true crime", "self-improvement"],
                "trending_hashtags": ["#voiceover", "#podcast", "#originalmusic", "#audiobook"],
                "seasonal_trends": {
                    "winter": ["cozy music", "holiday content", "new year motivation"],
                    "spring": ["upbeat music", "workout content", "cleaning motivation"],
                    "summer": ["vacation vibes", "road trip music", "outdoor activities"],
                    "fall": ["study music", "back to school", "productivity content"]
                }
            },
            "platform_specific": {
                Platform.TIKTOK: ["15s clips", "trending sounds", "challenges", "duets"],
                Platform.SPOTIFY: ["playlists", "mood music", "genre fusion", "artist collaborations"],
                Platform.YOUTUBE: ["tutorials", "vlogs", "music videos", "podcasts"],
                Platform.INSTAGRAM: ["reels", "stories", "voice notes", "behind scenes"]
            }
        }
    
    def _initialize_platform_algorithms(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform algorithm understanding"""
        return {
            Platform.SPOTIFY: {
                "ranking_factors": ["listen_time", "skip_rate", "playlist_adds", "shares", "user_engagement"],
                "algorithm_weights": {"discovery": 0.3, "personalization": 0.4, "popularity": 0.3},
                "optimization_focus": ["playlist_placement", "genre_targeting", "mood_matching"],
                "metadata_importance": {"high": ["title", "artist", "genre"], "medium": ["description", "tags"]}
            },
            Platform.YOUTUBE: {
                "ranking_factors": ["watch_time", "click_through_rate", "engagement", "comments", "shares"],
                "algorithm_weights": {"relevance": 0.4, "engagement": 0.3, "authority": 0.3},
                "optimization_focus": ["thumbnail", "title", "description", "tags", "closed_captions"],
                "metadata_importance": {"high": ["title", "description"], "medium": ["tags", "category"]}
            },
            Platform.TIKTOK: {
                "ranking_factors": ["completion_rate", "shares", "comments", "likes", "user_interaction"],
                "algorithm_weights": {"virality": 0.4, "relevance": 0.3, "freshness": 0.3},
                "optimization_focus": ["hooks", "trending_sounds", "hashtags", "timing"],
                "metadata_importance": {"high": ["hashtags", "captions"], "medium": ["sounds", "effects"]}
            },
            Platform.APPLE_MUSIC: {
                "ranking_factors": ["play_count", "completion_rate", "library_adds", "radio_plays"],
                "algorithm_weights": {"editorial": 0.4, "algorithmic": 0.3, "social": 0.3},
                "optimization_focus": ["genre_classification", "mood_tags", "artist_development"],
                "metadata_importance": {"high": ["artist", "album", "genre"], "medium": ["songwriter", "producer"]}
            }
        }
    
    def _initialize_platform_rules(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform-specific optimization rules"""
        return {
            Platform.SPOTIFY: {
                "title_length": {"min": 10, "max": 60, "optimal": 35},
                "description_length": {"min": 50, "max": 300, "optimal": 150},
                "tags_count": {"min": 3, "max": 10, "optimal": 6},
                "content_requirements": ["high_quality_audio", "proper_metadata", "album_art"],
                "prohibited_content": ["explicit_without_tag", "copyright_violation", "low_quality"]
            },
            Platform.YOUTUBE: {
                "title_length": {"min": 10, "max": 100, "optimal": 60},
                "description_length": {"min": 125, "max": 5000, "optimal": 250},
                "tags_count": {"min": 5, "max": 15, "optimal": 10},
                "content_requirements": ["custom_thumbnail", "end_screens", "cards", "closed_captions"],
                "prohibited_content": ["misleading_metadata", "copyright_violation", "spam_tags"]
            },
            Platform.TIKTOK: {
                "title_length": {"min": 5, "max": 100, "optimal": 40},
                "hashtags_count": {"min": 3, "max": 30, "optimal": 8},
                "content_requirements": ["vertical_format", "engaging_hook", "trending_elements"],
                "prohibited_content": ["horizontal_format", "watermarks", "low_engagement_start"]
            }
        }
    
    async def optimize_voice_content_seo(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        target_platforms: List[Platform],
        optimization_strategy: SEOStrategy = SEOStrategy.DISCOVERY_FOCUSED,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> SEOOptimization:
        """Optimize voice content for SEO across multiple platforms"""
        
        try:
            self.logger.info(f"Optimizing SEO for content {content_id}")
            
            # Initialize AI models
            await self._ensure_seo_models()
            
            # Extract content category
            content_category = await self._categorize_content(content_metadata)
            
            # Perform keyword research
            seo_keywords = await self._perform_keyword_research(
                content_metadata, content_category, target_platforms, target_audience
            )
            
            # Analyze trending topics
            trending_analysis = await self._analyze_trending_topics(content_category, target_platforms)
            
            # Perform competitor analysis
            competitor_analysis = await self._analyze_competitors(content_category, seo_keywords)
            
            # Optimize title
            optimized_title = await self._optimize_title(
                content_metadata, seo_keywords, target_platforms, optimization_strategy
            )
            
            # Optimize description
            optimized_description = await self._optimize_description(
                content_metadata, seo_keywords, target_platforms, trending_analysis
            )
            
            # Generate optimized tags
            optimized_tags = await self._generate_optimized_tags(
                seo_keywords, trending_analysis, target_platforms
            )
            
            # Optimize metadata
            metadata_optimization = await self._optimize_metadata(
                content_metadata, seo_keywords, target_platforms
            )
            
            # Predict ranking performance
            predicted_ranking = await self._predict_ranking_performance(
                optimized_title, optimized_description, optimized_tags, target_platforms
            )
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(
                content_metadata, seo_keywords, trending_analysis, target_platforms
            )
            
            # Calculate overall optimization score
            optimization_score = await self._calculate_optimization_score(
                seo_keywords, predicted_ranking, viral_potential, target_platforms
            )
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                content_metadata, seo_keywords, trending_analysis, competitor_analysis, target_platforms
            )
            
            # Create optimization result
            seo_optimization = SEOOptimization(
                content_id=content_id,
                optimization_strategy=optimization_strategy,
                target_platforms=target_platforms,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                optimized_tags=optimized_tags,
                seo_keywords=seo_keywords,
                metadata_optimization=metadata_optimization,
                predicted_ranking=predicted_ranking,
                viral_potential=viral_potential,
                optimization_score=optimization_score,
                recommendations=recommendations
            )
            
            # Store optimization
            self.optimization_history.append(seo_optimization)
            
            # Start performance tracking
            if self.ranking_tracking_enabled:
                asyncio.create_task(self._track_seo_performance(content_id))
            
            self.logger.info(f"SEO optimization completed for content {content_id}")
            return seo_optimization
            
        except Exception as e:
            self.logger.error(f"Error optimizing SEO for content {content_id}: {str(e)}")
            raise
    
    async def _categorize_content(self, content_metadata: Dict[str, Any]) -> ContentCategory:
        """Categorize content for targeted SEO optimization"""
        
        content_type = content_metadata.get("content_type", "").lower()
        title = content_metadata.get("title", "").lower()
        description = content_metadata.get("description", "").lower()
        tags = [tag.lower() for tag in content_metadata.get("tags", [])]
        
        # Content type mapping
        type_mapping = {
            "music": ContentCategory.MUSIC,
            "song": ContentCategory.MUSIC,
            "podcast": ContentCategory.PODCAST,
            "audiobook": ContentCategory.AUDIOBOOK,
            "voice_over": ContentCategory.VOICE_OVER,
            "narration": ContentCategory.AUDIOBOOK,
            "commercial": ContentCategory.COMMERCIAL,
            "education": ContentCategory.EDUCATION,
            "entertainment": ContentCategory.ENTERTAINMENT,
            "news": ContentCategory.NEWS
        }
        
        # Check content type first
        for keyword, category in type_mapping.items():
            if keyword in content_type or keyword in title or keyword in " ".join(tags):
                return category
        
        # Default categorization based on keywords
        music_keywords = ["beats", "melody", "rhythm", "instrumental", "acoustic", "vocal"]
        podcast_keywords = ["episode", "interview", "discussion", "talk", "conversation"]
        education_keywords = ["tutorial", "lesson", "learn", "guide", "course", "training"]
        
        content_text = f"{title} {description} {' '.join(tags)}"
        
        if any(keyword in content_text for keyword in music_keywords):
            return ContentCategory.MUSIC
        elif any(keyword in content_text for keyword in podcast_keywords):
            return ContentCategory.PODCAST
        elif any(keyword in content_text for keyword in education_keywords):
            return ContentCategory.EDUCATION
        else:
            return ContentCategory.ENTERTAINMENT
    
    async def _perform_keyword_research(
        self,
        content_metadata: Dict[str, Any],
        content_category: ContentCategory,
        target_platforms: List[Platform],
        target_audience: Optional[Dict[str, Any]]
    ) -> SEOKeywords:
        """Perform comprehensive keyword research"""
        
        # Get category-specific keywords
        category_keywords = self._get_category_keywords(content_category)
        
        # Extract keywords from content
        content_keywords = await self._extract_content_keywords(content_metadata)
        
        # Get trending keywords
        trending_keywords = await self._get_trending_keywords(content_category, target_platforms)
        
        # Analyze competitor keywords
        competitor_keywords = await self._analyze_competitor_keywords(content_category)
        
        # Get seasonal keywords
        seasonal_keywords = await self._get_seasonal_keywords(content_category)
        
        # Combine and analyze keywords
        all_keywords = list(set(
            category_keywords + content_keywords + trending_keywords + 
            competitor_keywords + seasonal_keywords
        ))
        
        # Calculate search volumes and difficulty scores
        search_volumes = {}
        difficulty_scores = {}
        relevance_scores = {}
        
        for keyword in all_keywords:
            search_volumes[keyword] = await self._get_search_volume(keyword)
            difficulty_scores[keyword] = await self._calculate_keyword_difficulty(keyword)
            relevance_scores[keyword] = await self._calculate_keyword_relevance(
                keyword, content_metadata, content_category
            )
        
        # Categorize keywords by priority
        primary_keywords = await self._select_primary_keywords(
            all_keywords, search_volumes, difficulty_scores, relevance_scores
        )
        secondary_keywords = await self._select_secondary_keywords(
            all_keywords, primary_keywords, search_volumes, relevance_scores
        )
        long_tail_keywords = await self._generate_long_tail_keywords(
            primary_keywords, content_metadata
        )
        
        return SEOKeywords(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            long_tail_keywords=long_tail_keywords,
            trending_keywords=trending_keywords,
            seasonal_keywords=seasonal_keywords,
            competitor_keywords=competitor_keywords,
            search_volumes=search_volumes,
            difficulty_scores=difficulty_scores,
            relevance_scores=relevance_scores
        )
    
    def _get_category_keywords(self, content_category: ContentCategory) -> List[str]:
        """Get keywords specific to content category"""
        
        category_map = {
            ContentCategory.MUSIC: self.keyword_database["music_keywords"],
            ContentCategory.PODCAST: self.keyword_database["podcast_keywords"],
            ContentCategory.VOICE_OVER: self.keyword_database["voice_over_keywords"],
            ContentCategory.AUDIOBOOK: ["audiobook", "narration", "storytelling", "chapter"],
            ContentCategory.EDUCATION: ["tutorial", "learning", "course", "educational"],
            ContentCategory.ENTERTAINMENT: ["entertainment", "fun", "comedy", "drama"],
            ContentCategory.NEWS: ["news", "current events", "updates", "breaking"],
            ContentCategory.COMMERCIAL: ["commercial", "advertisement", "brand", "promotion"]
        }
        
        keywords = category_map.get(content_category, [])
        if isinstance(keywords, dict):
            return list(keywords.keys())
        return keywords
    
    async def _extract_content_keywords(self, content_metadata: Dict[str, Any]) -> List[str]:
        """Extract keywords from content metadata"""
        
        title = content_metadata.get("title", "")
        description = content_metadata.get("description", "")
        tags = content_metadata.get("tags", [])
        
        # Combine all text
        content_text = f"{title} {description} {' '.join(tags)}"
        
        # Extract meaningful keywords (simplified NLP)
        keywords = []
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', content_text.lower())
        
        # Filter out common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        
        # Get meaningful words (length > 3, not stop words)
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Get word frequency and select top keywords
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:20]]  # Top 20 keywords
        
        return keywords
    
    async def _get_trending_keywords(
        self, 
        content_category: ContentCategory, 
        target_platforms: List[Platform]
    ) -> List[str]:
        """Get trending keywords for category and platforms"""
        
        trending = []
        
        # Get general trending keywords
        trending.extend(self.keyword_database.get("trending_keywords", {}).keys())
        
        # Get platform-specific trending topics
        platform_trends = self.trending_data.get("platform_specific", {})
        for platform in target_platforms:
            if platform in platform_trends:
                trending.extend(platform_trends[platform])
        
        # Get seasonal trends
        current_season = self._get_current_season()
        seasonal_trends = self.trending_data.get("current_trends", {}).get("seasonal_trends", {})
        if current_season in seasonal_trends:
            trending.extend(seasonal_trends[current_season])
        
        return list(set(trending))
    
    def _get_current_season(self) -> str:
        """Get current season for seasonal trend analysis"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    async def _analyze_competitor_keywords(self, content_category: ContentCategory) -> List[str]:
        """Analyze competitor keywords (simplified)"""
        
        # In production, this would analyze actual competitor content
        competitor_keywords = {
            ContentCategory.MUSIC: ["remix", "cover", "acoustic", "live version", "remaster"],
            ContentCategory.PODCAST: ["deep dive", "exclusive", "behind scenes", "interview", "recap"],
            ContentCategory.VOICE_OVER: ["professional", "quality", "custom", "commercial grade"],
            ContentCategory.AUDIOBOOK: ["bestseller", "narrator", "full length", "unabridged"]
        }
        
        return competitor_keywords.get(content_category, [])
    
    async def _get_seasonal_keywords(self, content_category: ContentCategory) -> List[str]:
        """Get seasonal keywords relevant to content category"""
        
        season = self._get_current_season()
        seasonal_map = {
            "winter": ["cozy", "warm", "holiday", "new year", "resolution"],
            "spring": ["fresh", "new", "growth", "energy", "motivation"],
            "summer": ["summer", "vacation", "relaxing", "upbeat", "outdoor"],
            "fall": ["autumn", "back to school", "productivity", "focus", "preparation"]
        }
        
        return seasonal_map.get(season, [])
    
    async def _get_search_volume(self, keyword: str) -> int:
        """Get search volume for keyword (simplified)"""
        
        # Check if keyword exists in database
        for category_keywords in self.keyword_database.values():
            if isinstance(category_keywords, dict) and keyword in category_keywords:
                return category_keywords[keyword].get("volume", 1000)
        
        # Estimate based on keyword length and commonality
        base_volume = 5000
        if len(keyword.split()) > 2:  # Long-tail keywords have lower volume
            base_volume = 1000
        elif len(keyword) < 5:  # Short keywords might have higher volume
            base_volume = 10000
        
        return base_volume
    
    async def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty score (0-1)"""
        
        # Check database first
        for category_keywords in self.keyword_database.values():
            if isinstance(category_keywords, dict) and keyword in category_keywords:
                return category_keywords[keyword].get("difficulty", 0.5)
        
        # Estimate difficulty based on keyword characteristics
        difficulty = 0.5  # Base difficulty
        
        # Short, generic keywords are harder
        if len(keyword.split()) == 1 and len(keyword) < 8:
            difficulty += 0.2
        
        # Long-tail keywords are easier
        if len(keyword.split()) > 2:
            difficulty -= 0.2
        
        # Commercial keywords are harder
        commercial_indicators = ["buy", "best", "top", "review", "price"]
        if any(indicator in keyword.lower() for indicator in commercial_indicators):
            difficulty += 0.1
        
        return max(0.0, min(1.0, difficulty))
    
    async def _calculate_keyword_relevance(
        self, 
        keyword: str, 
        content_metadata: Dict[str, Any], 
        content_category: ContentCategory
    ) -> float:
        """Calculate keyword relevance to content"""
        
        title = content_metadata.get("title", "").lower()
        description = content_metadata.get("description", "").lower()
        tags = [tag.lower() for tag in content_metadata.get("tags", [])]
        
        relevance = 0.0
        
        # Direct match in title (highest relevance)
        if keyword.lower() in title:
            relevance += 0.5
        
        # Match in description
        if keyword.lower() in description:
            relevance += 0.3
        
        # Match in tags
        if keyword.lower() in " ".join(tags):
            relevance += 0.2
        
        # Category relevance
        category_keywords = self._get_category_keywords(content_category)
        if keyword.lower() in [ck.lower() for ck in category_keywords]:
            relevance += 0.3
        
        # Partial match bonus
        keyword_words = keyword.lower().split()
        content_text = f"{title} {description} {' '.join(tags)}"
        matching_words = sum(1 for word in keyword_words if word in content_text)
        if matching_words > 0:
            relevance += (matching_words / len(keyword_words)) * 0.2
        
        return min(1.0, relevance)
    
    async def _select_primary_keywords(
        self,
        all_keywords: List[str],
        search_volumes: Dict[str, int],
        difficulty_scores: Dict[str, float],
        relevance_scores: Dict[str, float]
    ) -> List[str]:
        """Select primary keywords based on volume, difficulty, and relevance"""
        
        # Score each keyword
        keyword_scores = {}
        for keyword in all_keywords:
            volume_score = min(1.0, search_volumes.get(keyword, 0) / 50000)  # Normalize to 50k max
            difficulty_score = 1.0 - difficulty_scores.get(keyword, 0.5)  # Lower difficulty is better
            relevance_score = relevance_scores.get(keyword, 0.0)
            
            # Weighted score
            total_score = (volume_score * 0.3) + (difficulty_score * 0.3) + (relevance_score * 0.4)
            keyword_scores[keyword] = total_score
        
        # Sort by score and select top keywords
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        primary_keywords = [keyword for keyword, score in sorted_keywords[:5]]  # Top 5
        
        return primary_keywords
    
    async def _select_secondary_keywords(
        self,
        all_keywords: List[str],
        primary_keywords: List[str],
        search_volumes: Dict[str, int],
        relevance_scores: Dict[str, float]
    ) -> List[str]:
        """Select secondary keywords"""
        
        # Remove primary keywords from consideration
        remaining_keywords = [kw for kw in all_keywords if kw not in primary_keywords]
        
        # Score remaining keywords
        keyword_scores = {}
        for keyword in remaining_keywords:
            volume_score = min(1.0, search_volumes.get(keyword, 0) / 20000)  # Lower threshold for secondary
            relevance_score = relevance_scores.get(keyword, 0.0)
            
            total_score = (volume_score * 0.4) + (relevance_score * 0.6)
            keyword_scores[keyword] = total_score
        
        # Sort and select secondary keywords
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_keywords = [keyword for keyword, score in sorted_keywords[:8]]  # Top 8
        
        return secondary_keywords
    
    async def _generate_long_tail_keywords(
        self,
        primary_keywords: List[str],
        content_metadata: Dict[str, Any]
    ) -> List[str]:
        """Generate long-tail keyword variations"""
        
        long_tail = []
        
        # Combine primary keywords with modifiers
        modifiers = ["best", "free", "new", "latest", "top", "how to", "guide to", "tutorial", "review"]
        qualifiers = ["2024", "online", "quality", "professional", "original", "exclusive"]
        
        for primary in primary_keywords:
            # Add modifiers
            for modifier in modifiers[:3]:  # Limit to avoid too many
                long_tail.append(f"{modifier} {primary}")
            
            # Add qualifiers
            for qualifier in qualifiers[:2]:
                long_tail.append(f"{primary} {qualifier}")
        
        # Generate contextual combinations
        title_words = content_metadata.get("title", "").lower().split()
        for primary in primary_keywords:
            for word in title_words:
                if len(word) > 3 and word != primary:
                    long_tail.append(f"{primary} {word}")
                    long_tail.append(f"{word} {primary}")
        
        # Remove duplicates and return
        return list(set(long_tail))[:15]  # Limit to 15 long-tail keywords
    
    async def _optimize_title(
        self,
        content_metadata: Dict[str, Any],
        seo_keywords: SEOKeywords,
        target_platforms: List[Platform],
        optimization_strategy: SEOStrategy
    ) -> str:
        """Optimize title for SEO"""
        
        original_title = content_metadata.get("title", "")
        
        # Get platform requirements
        title_requirements = {}
        for platform in target_platforms:
            platform_rules = self.platform_rules.get(platform, {})
            title_length = platform_rules.get("title_length", {})
            title_requirements[platform] = title_length
        
        # Find common optimal length
        optimal_length = 60  # Default
        if title_requirements:
            optimal_lengths = [req.get("optimal", 60) for req in title_requirements.values()]
            optimal_length = min(optimal_lengths)  # Use most restrictive
        
        # Select best keywords for title
        primary_keywords = seo_keywords.primary_keywords[:2]  # Top 2 primary keywords
        trending_keywords = [kw for kw in seo_keywords.trending_keywords if len(kw) < 15][:1]  # 1 trending
        
        # Build optimized title
        if optimization_strategy == SEOStrategy.VIRAL_FOCUSED:
            # Focus on trending and engaging elements
            title_elements = trending_keywords + primary_keywords
            engaging_words = ["Amazing", "Incredible", "Must-Hear", "Exclusive", "Viral"]
            optimized_title = f"{engaging_words[0]} {' '.join(title_elements[:2])}"
        elif optimization_strategy == SEOStrategy.DISCOVERY_FOCUSED:
            # Focus on searchable keywords
            optimized_title = f"{' '.join(primary_keywords[:2])}"
            if original_title and len(original_title) < optimal_length // 2:
                optimized_title = f"{original_title} - {optimized_title}"
        else:
            # Balanced approach
            optimized_title = original_title
            if primary_keywords and primary_keywords[0].lower() not in original_title.lower():
                optimized_title = f"{primary_keywords[0]} - {original_title}"
        
        # Ensure title meets length requirements
        if len(optimized_title) > optimal_length:
            optimized_title = optimized_title[:optimal_length-3] + "..."
        
        return optimized_title
    
    async def _optimize_description(
        self,
        content_metadata: Dict[str, Any],
        seo_keywords: SEOKeywords,
        target_platforms: List[Platform],
        trending_analysis: TrendingAnalysis
    ) -> str:
        """Optimize description for SEO"""
        
        original_description = content_metadata.get("description", "")
        
        # Get platform requirements
        description_requirements = {}
        for platform in target_platforms:
            platform_rules = self.platform_rules.get(platform, {})
            desc_length = platform_rules.get("description_length", {})
            description_requirements[platform] = desc_length
        
        # Find optimal length
        optimal_length = 250  # Default
        if description_requirements:
            optimal_lengths = [req.get("optimal", 250) for req in description_requirements.values()]
            optimal_length = min(optimal_lengths)
        
        # Build SEO-optimized description
        description_parts = []
        
        # Start with engaging hook
        if trending_analysis.trending_topics:
            hook = f"Discover the latest in {trending_analysis.trending_topics[0]}!"
            description_parts.append(hook)
        
        # Add original description if good
        if original_description and len(original_description) > 20:
            description_parts.append(original_description)
        
        # Add keyword-rich content
        keyword_text = f"Featuring {', '.join(seo_keywords.primary_keywords[:3])}."
        description_parts.append(keyword_text)
        
        # Add call to action
        cta_options = [
            "Listen now for an amazing experience!",
            "Don't miss this incredible content!",
            "Perfect for fans of quality audio content.",
            "Subscribe for more amazing content like this!"
        ]
        description_parts.append(cta_options[0])
        
        # Combine and optimize length
        optimized_description = " ".join(description_parts)
        
        if len(optimized_description) > optimal_length:
            # Trim while keeping the most important parts
            essential_parts = description_parts[:2]  # Hook and original description
            optimized_description = " ".join(essential_parts)
            
            if len(optimized_description) > optimal_length:
                optimized_description = optimized_description[:optimal_length-3] + "..."
        
        return optimized_description
    
    async def _generate_optimized_tags(
        self,
        seo_keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        target_platforms: List[Platform]
    ) -> List[str]:
        """Generate optimized tags for platforms"""
        
        tags = []
        
        # Add primary keywords
        tags.extend(seo_keywords.primary_keywords)
        
        # Add secondary keywords
        tags.extend(seo_keywords.secondary_keywords[:5])  # Top 5 secondary
        
        # Add trending keywords
        tags.extend(seo_keywords.trending_keywords[:3])  # Top 3 trending
        
        # Add long-tail keywords
        tags.extend(seo_keywords.long_tail_keywords[:3])  # Top 3 long-tail
        
        # Add trending hashtags (for social platforms)
        if any(platform in [Platform.TIKTOK, Platform.INSTAGRAM] for platform in target_platforms):
            hashtags = trending_analysis.hashtag_trends if hasattr(trending_analysis, 'hashtag_trends') else []
            tags.extend(hashtags[:3])
        
        # Remove duplicates and clean tags
        unique_tags = []
        seen = set()
        for tag in tags:
            clean_tag = tag.lower().strip()
            if clean_tag not in seen and len(clean_tag) > 2:
                unique_tags.append(tag)
                seen.add(clean_tag)
        
        # Limit based on platform requirements
        max_tags = 15  # Default
        for platform in target_platforms:
            platform_rules = self.platform_rules.get(platform, {})
            tags_count = platform_rules.get("tags_count", {})
            platform_max = tags_count.get("max", 15)
            max_tags = min(max_tags, platform_max)
        
        return unique_tags[:max_tags]
    
    async def _optimize_metadata(
        self,
        content_metadata: Dict[str, Any],
        seo_keywords: SEOKeywords,
        target_platforms: List[Platform]
    ) -> Dict[str, Any]:
        """Optimize metadata for platforms"""
        
        optimized_metadata = content_metadata.copy()
        
        # Add SEO-optimized metadata
        optimized_metadata.update({
            "seo_keywords": seo_keywords.primary_keywords,
            "search_tags": seo_keywords.secondary_keywords,
            "trending_tags": seo_keywords.trending_keywords,
            "optimization_timestamp": datetime.now().isoformat()
        })
        
        # Platform-specific metadata
        for platform in target_platforms:
            platform_key = f"{platform.value}_metadata"
            optimized_metadata[platform_key] = await self._create_platform_metadata(
                platform, seo_keywords, content_metadata
            )
        
        return optimized_metadata
    
    async def _create_platform_metadata(
        self,
        platform: Platform,
        seo_keywords: SEOKeywords,
        content_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create platform-specific metadata"""
        
        platform_metadata = {}
        
        if platform == Platform.SPOTIFY:
            platform_metadata = {
                "genre": content_metadata.get("genre", "Other"),
                "mood": "energetic",  # Could be determined by AI
                "tempo": "medium",
                "explicit": False,
                "playlist_keywords": seo_keywords.primary_keywords
            }
        elif platform == Platform.YOUTUBE:
            platform_metadata = {
                "category": "Music",  # or other appropriate category
                "language": "en",
                "captions": True,
                "thumbnail_keywords": seo_keywords.primary_keywords,
                "end_screen_elements": ["subscribe", "related_videos"]
            }
        elif platform == Platform.TIKTOK:
            platform_metadata = {
                "hashtags": [f"#{kw.replace(' ', '')}" for kw in seo_keywords.primary_keywords[:5]],
                "trending_sounds": True,
                "duet_enabled": True,
                "stitch_enabled": True
            }
        
        return platform_metadata
    
    async def _predict_ranking_performance(
        self,
        optimized_title: str,
        optimized_description: str,
        optimized_tags: List[str],
        target_platforms: List[Platform]
    ) -> Dict[str, float]:
        """Predict ranking performance on platforms"""
        
        ranking_predictions = {}
        
        for platform in target_platforms:
            algorithm = self.platform_algorithms.get(platform, {})
            ranking_factors = algorithm.get("ranking_factors", [])
            
            # Calculate ranking score based on optimization
            score = 0.5  # Base score
            
            # Title optimization score
            if len(optimized_title) > 10:
                score += 0.1
            if any(tag in optimized_title.lower() for tag in optimized_tags[:3]):
                score += 0.1
            
            # Description optimization score
            if len(optimized_description) > 50:
                score += 0.1
            if len(optimized_description.split()) > 20:
                score += 0.1
            
            # Tags optimization score
            if len(optimized_tags) >= 5:
                score += 0.1
            if len(optimized_tags) <= 10:  # Not too many tags
                score += 0.05
            
            # Platform-specific adjustments
            if platform == Platform.TIKTOK and any("#" in tag for tag in optimized_tags):
                score += 0.1
            elif platform == Platform.YOUTUBE and "tutorial" in optimized_title.lower():
                score += 0.1
            elif platform == Platform.SPOTIFY and "music" in " ".join(optimized_tags).lower():
                score += 0.1
            
            ranking_predictions[platform.value] = min(1.0, score)
        
        return ranking_predictions
    
    async def _calculate_viral_potential(
        self,
        content_metadata: Dict[str, Any],
        seo_keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        target_platforms: List[Platform]
    ) -> float:
        """Calculate viral potential score"""
        
        viral_score = 0.0
        
        # Trending keywords boost
        trending_overlap = len(set(seo_keywords.primary_keywords) & set(seo_keywords.trending_keywords))
        viral_score += trending_overlap * 0.2
        
        # Platform viral factors
        viral_platforms = [Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]
        viral_platform_count = len(set(target_platforms) & set(viral_platforms))
        viral_score += viral_platform_count * 0.15
        
        # Content characteristics
        title = content_metadata.get("title", "").lower()
        viral_words = ["amazing", "incredible", "must", "viral", "trending", "exclusive", "secret"]
        viral_word_count = sum(1 for word in viral_words if word in title)
        viral_score += viral_word_count * 0.1
        
        # Trending topics alignment
        if hasattr(trending_analysis, 'trending_topics'):
            topic_alignment = sum(1 for topic in trending_analysis.trending_topics 
                                if any(keyword in topic.lower() for keyword in seo_keywords.primary_keywords))
            viral_score += topic_alignment * 0.15
        
        # Seasonal alignment
        seasonal_overlap = len(set(seo_keywords.seasonal_keywords) & set(seo_keywords.primary_keywords))
        viral_score += seasonal_overlap * 0.1
        
        return min(1.0, viral_score)
    
    async def _calculate_optimization_score(
        self,
        seo_keywords: SEOKeywords,
        predicted_ranking: Dict[str, float],
        viral_potential: float,
        target_platforms: List[Platform]
    ) -> float:
        """Calculate overall optimization score"""
        
        # Keyword quality score
        keyword_score = 0.0
        if seo_keywords.primary_keywords:
            avg_relevance = sum(seo_keywords.relevance_scores.get(kw, 0) for kw in seo_keywords.primary_keywords) / len(seo_keywords.primary_keywords)
            keyword_score = avg_relevance
        
        # Ranking prediction score
        ranking_score = sum(predicted_ranking.values()) / len(predicted_ranking) if predicted_ranking else 0.0
        
        # Viral potential score
        viral_score = viral_potential
        
        # Platform coverage score
        coverage_score = len(target_platforms) / 4.0  # Normalize to max 4 platforms
        
        # Weighted optimization score
        optimization_score = (
            keyword_score * 0.3 +
            ranking_score * 0.3 +
            viral_score * 0.2 +
            coverage_score * 0.2
        )
        
        return min(1.0, optimization_score)
    
    async def _generate_seo_recommendations(
        self,
        content_metadata: Dict[str, Any],
        seo_keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        competitor_analysis: CompetitorAnalysis,
        target_platforms: List[Platform]
    ) -> List[str]:
        """Generate SEO optimization recommendations"""
        
        recommendations = []
        
        # Keyword recommendations
        if len(seo_keywords.primary_keywords) < 3:
            recommendations.append("Add more primary keywords to improve discoverability")
        
        # Trending recommendations
        if not any(kw in seo_keywords.primary_keywords for kw in seo_keywords.trending_keywords):
            recommendations.append("Include trending keywords to boost viral potential")
        
        # Platform-specific recommendations
        for platform in target_platforms:
            platform_rules = self.platform_rules.get(platform, {})
            
            if platform == Platform.TIKTOK:
                if not any("#" in str(tag) for tag in content_metadata.get("tags", [])):
                    recommendations.append("Add hashtags for TikTok optimization")
            elif platform == Platform.YOUTUBE:
                if len(content_metadata.get("description", "")) < 125:
                    recommendations.append("Expand description for YouTube SEO (minimum 125 characters)")
            elif platform == Platform.SPOTIFY:
                if not content_metadata.get("genre"):
                    recommendations.append("Add genre classification for Spotify discovery")
        
        # Competitor analysis recommendations
        if hasattr(competitor_analysis, 'opportunity_keywords'):
            if competitor_analysis.opportunity_keywords:
                recommendations.append(f"Consider using opportunity keywords: {', '.join(competitor_analysis.opportunity_keywords[:3])}")
        
        # Seasonal recommendations
        current_season = self._get_current_season()
        if seo_keywords.seasonal_keywords:
            recommendations.append(f"Leverage {current_season} seasonal trends: {', '.join(seo_keywords.seasonal_keywords[:2])}")
        
        # Long-tail keyword recommendations
        if len(seo_keywords.long_tail_keywords) < 5:
            recommendations.append("Add more long-tail keywords for niche targeting")
        
        return recommendations
    
    async def _analyze_trending_topics(
        self,
        content_category: ContentCategory,
        target_platforms: List[Platform]
    ) -> TrendingAnalysis:
        """Analyze trending topics for content optimization"""
        
        # Get current trends
        current_trends = self.trending_data.get("current_trends", {})
        
        trending_analysis = TrendingAnalysis(
            trend_category=content_category.value,
            trending_topics=current_trends.get("popular_topics", []),
            trending_keywords=list(self.keyword_database.get("trending_keywords", {}).keys()),
            hashtag_trends=current_trends.get("trending_hashtags", []),
            seasonal_patterns=current_trends.get("seasonal_trends", {}),
            audience_interests={},  # Would be populated with real data
            platform_trends={platform: self.trending_data.get("platform_specific", {}).get(platform, []) for platform in target_platforms},
            growth_predictions={}  # Would be populated with ML predictions
        )
        
        return trending_analysis
    
    async def _analyze_competitors(
        self,
        content_category: ContentCategory,
        seo_keywords: SEOKeywords
    ) -> CompetitorAnalysis:
        """Analyze competitors for SEO opportunities"""
        
        # Simplified competitor analysis
        competitor_analysis = CompetitorAnalysis(
            competitor_content=[],  # Would be populated with actual competitor data
            market_gaps=["underserved_niches", "emerging_trends"],
            opportunity_keywords=seo_keywords.secondary_keywords[:5],
            competitor_strategies={},
            ranking_analysis={},
            differentiation_opportunities=["unique_style", "niche_targeting", "trending_topics"]
        )
        
        return competitor_analysis
    
    async def _ensure_seo_models(self):
        """Ensure all SEO AI models are initialized"""
        if not self.ranking_predictor:
            self.ranking_predictor = await self._initialize_ranking_predictor()
        if not self.viral_predictor:
            self.viral_predictor = await self._initialize_viral_predictor()
        if not self.keyword_extractor:
            self.keyword_extractor = await self._initialize_keyword_extractor()
    
    async def _initialize_ranking_predictor(self):
        """Initialize ranking prediction model"""
        return {"model": "ranking_predictor_v1", "initialized": True}
    
    async def _initialize_viral_predictor(self):
        """Initialize viral prediction model"""
        return {"model": "viral_predictor_v1", "initialized": True}
    
    async def _initialize_keyword_extractor(self):
        """Initialize keyword extraction model"""
        return {"model": "keyword_extractor_v1", "initialized": True}
    
    async def _track_seo_performance(self, content_id: str):
        """Track SEO performance over time"""
        
        while self.ranking_tracking_enabled:
            try:
                # Simulate performance tracking
                await asyncio.sleep(3600)  # Check every hour
                
                if content_id not in self.performance_tracking:
                    self.performance_tracking[content_id] = {
                        "rankings": {},
                        "traffic": {},
                        "engagement": {},
                        "last_updated": datetime.now().isoformat()
                    }
                
                # Update performance metrics (simplified)
                performance = self.performance_tracking[content_id]
                performance["last_updated"] = datetime.now().isoformat()
                
                self.logger.debug(f"Updated SEO performance tracking for content {content_id}")
                
            except Exception as e:
                self.logger.error(f"Error tracking SEO performance for {content_id}: {str(e)}")
                await asyncio.sleep(3600)
    
    async def get_seo_analytics(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """Get SEO analytics for content or overall system"""
        
        if content_id:
            # Get analytics for specific content
            optimization = next((opt for opt in self.optimization_history if opt.content_id == content_id), None)
            if not optimization:
                return {"error": "Content not found"}
            
            performance = self.performance_tracking.get(content_id, {})
            
            return {
                "content_id": content_id,
                "optimization_score": optimization.optimization_score,
                "viral_potential": optimization.viral_potential,
                "predicted_ranking": optimization.predicted_ranking,
                "seo_keywords": {
                    "primary": optimization.seo_keywords.primary_keywords,
                    "trending": optimization.seo_keywords.trending_keywords
                },
                "performance_tracking": performance,
                "recommendations": optimization.recommendations
            }
        else:
            # Get overall SEO analytics
            total_optimizations = len(self.optimization_history)
            avg_optimization_score = sum(opt.optimization_score for opt in self.optimization_history) / max(1, total_optimizations)
            avg_viral_potential = sum(opt.viral_potential for opt in self.optimization_history) / max(1, total_optimizations)
            
            return {
                "overall_metrics": {
                    "total_optimizations": total_optimizations,
                    "average_optimization_score": avg_optimization_score,
                    "average_viral_potential": avg_viral_potential,
                    "content_tracking": len(self.performance_tracking)
                },
                "platform_usage": self._get_platform_usage_stats(),
                "keyword_performance": self._get_keyword_performance_stats(),
                "trending_insights": self._get_trending_insights()
            }
    
    def _get_platform_usage_stats(self) -> Dict[str, Any]:
        """Get platform usage statistics"""
        platform_counts = {}
        for optimization in self.optimization_history:
            for platform in optimization.target_platforms:
                platform_counts[platform.value] = platform_counts.get(platform.value, 0) + 1
        
        return platform_counts
    
    def _get_keyword_performance_stats(self) -> Dict[str, Any]:
        """Get keyword performance statistics"""
        keyword_usage = {}
        for optimization in self.optimization_history:
            for keyword in optimization.seo_keywords.primary_keywords:
                keyword_usage[keyword] = keyword_usage.get(keyword, 0) + 1
        
        # Sort by usage
        top_keywords = sorted(keyword_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "most_used_keywords": dict(top_keywords),
            "total_unique_keywords": len(keyword_usage)
        }
    
    def _get_trending_insights(self) -> Dict[str, Any]:
        """Get trending insights"""
        current_trends = self.trending_data.get("current_trends", {})
        
        return {
            "current_viral_sounds": current_trends.get("viral_sounds", []),
            "popular_topics": current_trends.get("popular_topics", []),
            "trending_hashtags": current_trends.get("trending_hashtags", []),
            "seasonal_focus": self._get_current_season()
        }