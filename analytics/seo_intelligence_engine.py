"""SEO Intelligence Engine
======================

Advanced multi-platform SEO analytics and optimization system.
Monitors and optimizes content discoverability across all platforms and search engines.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import re
import redis
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor


class SEOPlatform(Enum):
    """SEO platforms and search engines"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    TWITCH = "twitch"
    REDDIT = "reddit"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"


class ContentType(Enum):
    """Types of content for SEO optimization"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PLAYLIST = "playlist"
    PROFILE = "profile"


class SEOMetricType(Enum):
    """Types of SEO metrics"""
    RANKING_POSITION = "ranking_position"
    CLICK_THROUGH_RATE = "click_through_rate"
    IMPRESSION_COUNT = "impression_count"
    ORGANIC_TRAFFIC = "organic_traffic"
    KEYWORD_DENSITY = "keyword_density"
    BACKLINK_COUNT = "backlink_count"
    SOCIAL_SIGNALS = "social_signals"
    ENGAGEMENT_RATE = "engagement_rate"
    BOUNCE_RATE = "bounce_rate"
    DWELL_TIME = "dwell_time"
    CONVERSION_RATE = "conversion_rate"
    BRAND_MENTION = "brand_mention"


@dataclass
class KeywordData:
    """Keyword performance data"""
    keyword: str
    search_volume: int
    competition_score: float  # 0-1
    cpc: float  # Cost per click
    ranking_position: int
    click_through_rate: float
    trend_direction: str  # "up", "down", "stable"
    related_keywords: List[str] = field(default_factory=list)
    intent_type: str = "informational"  # informational, navigational, transactional
    difficulty_score: float = 0.5  # 0-1


@dataclass
class ContentSEOAnalysis:
    """SEO analysis for individual content"""
    content_id: str
    content_type: ContentType
    platform: SEOPlatform
    title: str
    description: str
    keywords: List[str]
    seo_score: float  # 0-100
    optimization_suggestions: List[str]
    ranking_data: Dict[str, int] = field(default_factory=dict)
    traffic_metrics: Dict[str, float] = field(default_factory=dict)
    social_signals: Dict[str, int] = field(default_factory=dict)
    technical_seo: Dict[str, Any] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class SEOCampaign:
    """SEO optimization campaign"""
    campaign_id: str
    name: str
    target_keywords: List[str]
    target_platforms: List[SEOPlatform]
    content_pieces: List[str]
    start_date: datetime
    end_date: datetime
    objectives: Dict[str, float]  # target metrics
    current_performance: Dict[str, float] = field(default_factory=dict)
    optimization_actions: List[str] = field(default_factory=list)
    roi_score: float = 0.0
    success_rate: float = 0.0


@dataclass
class SEOIntelligenceMetrics:
    """Comprehensive SEO intelligence metrics"""
    time_period: Tuple[datetime, datetime]
    total_content_analyzed: int = 0
    average_seo_score: float = 0.0
    total_organic_traffic: int = 0
    total_impressions: int = 0
    average_ranking_position: float = 0.0
    click_through_rate: float = 0.0
    keyword_performance: Dict[str, Any] = field(default_factory=dict)
    platform_performance: Dict[str, Any] = field(default_factory=dict)
    content_type_performance: Dict[str, Any] = field(default_factory=dict)
    trending_keywords: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    technical_seo_health: Dict[str, float] = field(default_factory=dict)


class SEOIntelligenceEngine:
    """
    Advanced SEO intelligence and optimization analytics engine.
    
    Provides comprehensive SEO analysis, keyword optimization,
    and multi-platform content discoverability enhancement.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.content_seo_analyses = deque(maxlen=50000)
        self.keyword_database: Dict[str, KeywordData] = {}
        self.seo_campaigns: Dict[str, SEOCampaign] = {}
        self.metrics_history = deque(maxlen=1000)
        
        # ML models for SEO optimization
        self.ranking_predictor = None
        self.keyword_difficulty_estimator = None
        self.content_optimizer = None
        
        # Redis for real-time SEO data
        self.redis_client = None
        self._initialize_redis()
        
        # SEO analyzers by platform
        self.platform_analyzers = {
            SEOPlatform.GOOGLE: self._analyze_google_seo,
            SEOPlatform.YOUTUBE: self._analyze_youtube_seo,
            SEOPlatform.INSTAGRAM: self._analyze_instagram_seo,
            SEOPlatform.TIKTOK: self._analyze_tiktok_seo,
            SEOPlatform.TWITTER: self._analyze_twitter_seo,
            SEOPlatform.LINKEDIN: self._analyze_linkedin_seo,
            SEOPlatform.SPOTIFY: self._analyze_spotify_seo
        }
        
        # Text analysis tools
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # SEO best practices database
        self.seo_rules = {
            "title_length": {"min": 30, "max": 60, "optimal": 50},
            "description_length": {"min": 120, "max": 160, "optimal": 140},
            "keyword_density": {"min": 0.01, "max": 0.03, "optimal": 0.02},
            "readability_score": {"min": 60, "optimal": 75},
            "image_alt_text": {"required": True},
            "meta_tags": {"required": ["title", "description", "keywords"]},
            "url_structure": {"max_length": 100, "use_hyphens": True}
        }
        
        # Initialize ML models
        self._ml_models_initialized = False
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_host = self.config.get("redis_host", "localhost")
            redis_port = self.config.get("redis_port", 6379)
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize ML models for SEO optimization"""
        try:
            if self._ml_models_initialized:
                return
            
            # Ranking prediction model
            self.ranking_predictor = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            # Keyword difficulty estimation model
            self.keyword_difficulty_estimator = RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            )
            
            # Content clustering for optimization
            self.content_optimizer = KMeans(
                n_clusters=10, 
                random_state=42
            )
            
            self._ml_models_initialized = True
            self.logger.info("SEO ML models initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
    
    async def analyze_content_seo(
        self,
        content_id: str,
        content_type: ContentType,
        platform: SEOPlatform,
        title: str,
        description: str,
        content_text: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ContentSEOAnalysis:
        """Perform comprehensive SEO analysis on content"""
        try:
            if not self._ml_models_initialized:
                await self._initialize_ml_models()
            
            # Extract keywords from content
            keywords = await self._extract_keywords(title, description, content_text)
            
            # Calculate SEO score
            seo_score = await self._calculate_seo_score(
                title, description, keywords, content_type, platform
            )
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(
                title, description, keywords, seo_score, platform
            )
            
            # Get ranking data
            ranking_data = await self._get_ranking_data(keywords, platform)
            
            # Calculate traffic metrics
            traffic_metrics = await self._calculate_traffic_metrics(content_id, platform)
            
            # Analyze social signals
            social_signals = await self._analyze_social_signals(content_id)
            
            # Technical SEO analysis
            technical_seo = await self._analyze_technical_seo(content_id, platform, metadata)
            
            # Create analysis object
            analysis = ContentSEOAnalysis(
                content_id=content_id,
                content_type=content_type,
                platform=platform,
                title=title,
                description=description,
                keywords=keywords,
                seo_score=seo_score,
                optimization_suggestions=suggestions,
                ranking_data=ranking_data,
                traffic_metrics=traffic_metrics,
                social_signals=social_signals,
                technical_seo=technical_seo
            )
            
            # Store analysis
            self.content_seo_analyses.append(analysis)
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_seo_analysis(analysis)
            
            self.logger.info(f"SEO analysis completed for content {content_id}: score {seo_score:.1f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content SEO: {e}")
            raise
    
    async def _extract_keywords(
        self,
        title: str,
        description: str,
        content_text: Optional[str] = None
    ) -> List[str]:
        """Extract relevant keywords from content"""
        try:
            # Combine all text
            all_text = f"{title} {description}"
            if content_text:
                all_text += f" {content_text}"
            
            # Clean and process text
            text = re.sub(r'[^\w\s]', ' ', all_text.lower())
            words = text.split()
            
            # Remove common stop words and short words
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
            
            # Extract single words
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Extract phrases (2-3 words)
            phrases = []
            for i in range(len(words) - 1):
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    phrase = f"{words[i]} {words[i+1]}"
                    if not any(stop_word in phrase for stop_word in stop_words):
                        phrases.append(phrase)
            
            # Combine and deduplicate
            all_keywords = list(set(keywords + phrases))
            
            # Sort by frequency in text
            keyword_freq = {kw: all_text.lower().count(kw) for kw in all_keywords}
            sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Return top keywords
            return [kw for kw, freq in sorted_keywords[:20] if freq > 1]
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def _calculate_seo_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        content_type: ContentType,
        platform: SEOPlatform
    ) -> float:
        """Calculate comprehensive SEO score (0-100)"""
        try:
            score = 0.0
            
            # Title optimization (25 points)
            title_score = 0
            title_length = len(title)
            
            if self.seo_rules["title_length"]["min"] <= title_length <= self.seo_rules["title_length"]["max"]:
                title_score += 15
            elif title_length > 0:
                title_score += 10
            
            # Check if title contains keywords
            title_lower = title.lower()
            for keyword in keywords[:3]:  # Check top 3 keywords
                if keyword.lower() in title_lower:
                    title_score += 3
                    break
            
            # Check title readability
            if title[0].isupper() and not title.isupper():
                title_score += 7
            
            score += min(25, title_score)
            
            # Description optimization (20 points)
            desc_score = 0
            desc_length = len(description)
            
            if self.seo_rules["description_length"]["min"] <= desc_length <= self.seo_rules["description_length"]["max"]:
                desc_score += 12
            elif desc_length > 0:
                desc_score += 8
            
            # Check if description contains keywords
            desc_lower = description.lower()
            keyword_in_desc = sum(1 for kw in keywords[:5] if kw.lower() in desc_lower)
            desc_score += min(8, keyword_in_desc * 2)
            
            score += min(20, desc_score)
            
            # Keyword optimization (25 points)
            keyword_score = 0
            
            # Number of keywords
            keyword_count = len(keywords)
            if 5 <= keyword_count <= 15:
                keyword_score += 10
            elif keyword_count > 0:
                keyword_score += 7
            
            # Keyword diversity
            if keyword_count > 5:
                keyword_score += 5
            
            # Long-tail keywords (phrases)
            long_tail = [kw for kw in keywords if ' ' in kw]
            if long_tail:
                keyword_score += min(10, len(long_tail) * 2)
            
            score += min(25, keyword_score)
            
            # Platform-specific optimization (15 points)
            platform_score = await self._calculate_platform_specific_score(
                title, description, keywords, content_type, platform
            )
            score += platform_score
            
            # Content type optimization (15 points)
            content_type_score = await self._calculate_content_type_score(
                title, description, keywords, content_type
            )
            score += content_type_score
            
            return min(100.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating SEO score: {e}")
            return 50.0  # Default moderate score
    
    async def _calculate_platform_specific_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        content_type: ContentType,
        platform: SEOPlatform
    ) -> float:
        """Calculate platform-specific SEO score"""
        score = 0.0
        
        if platform == SEOPlatform.YOUTUBE:
            # YouTube-specific factors
            if len(title) > 10:
                score += 3
            if any(word in title.lower() for word in ['how to', 'tutorial', 'review', 'vs', 'best']):
                score += 4
            if len(keywords) >= 8:
                score += 3
            if content_type in [ContentType.VIDEO]:
                score += 5
            
        elif platform == SEOPlatform.INSTAGRAM:
            # Instagram-specific factors
            hashtag_keywords = [kw for kw in keywords if not ' ' in kw]  # Single words for hashtags
            if len(hashtag_keywords) >= 10:
                score += 5
            if len(description) <= 2200:  # Instagram caption limit
                score += 3
            if content_type in [ContentType.IMAGE, ContentType.VIDEO, ContentType.REEL, ContentType.STORY]:
                score += 5
            if any(word in description.lower() for word in ['#', '@']):
                score += 2
        
        elif platform == SEOPlatform.TIKTOK:
            # TikTok-specific factors
            if len(title) <= 100:  # TikTok caption limit
                score += 4
            if any(word in title.lower() for word in ['challenge', 'trend', 'viral', 'fyp']):
                score += 5
            if content_type in [ContentType.SHORT, ContentType.VIDEO]:
                score += 6
        
        elif platform == SEOPlatform.GOOGLE:
            # Google SEO factors
            if 50 <= len(title) <= 60:  # Optimal title length for Google
                score += 5
            if 140 <= len(description) <= 160:  # Optimal meta description
                score += 5
            if any(' ' in kw for kw in keywords):  # Long-tail keywords
                score += 5
        
        elif platform == SEOPlatform.LINKEDIN:
            # LinkedIn-specific factors
            if any(word in title.lower() for word in ['professional', 'business', 'career', 'industry']):
                score += 4
            if len(description) >= 100:  # Detailed descriptions perform better
                score += 4
            if content_type in [ContentType.BLOG_POST, ContentType.SOCIAL_POST]:
                score += 7
        
        return min(15.0, score)
    
    async def _calculate_content_type_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        content_type: ContentType
    ) -> float:
        """Calculate content type-specific SEO score"""
        score = 0.0
        
        if content_type == ContentType.VIDEO:
            # Video-specific optimization
            if any(word in title.lower() for word in ['video', 'watch', 'see', 'show']):
                score += 3
            if len(description) >= 100:  # Detailed video descriptions
                score += 4
            score += 8  # Videos generally perform well in search
        
        elif content_type == ContentType.BLOG_POST:
            # Blog post optimization
            if len(description) >= 150:
                score += 5
            if len(keywords) >= 10:
                score += 5
            if any(' ' in kw for kw in keywords):  # Long-tail keywords important for blogs
                score += 5
        
        elif content_type == ContentType.AUDIO:
            # Audio/podcast optimization
            if any(word in title.lower() for word in ['podcast', 'episode', 'listen', 'audio']):
                score += 4
            if len(description) >= 200:  # Detailed show notes
                score += 6
            score += 5
        
        elif content_type == ContentType.IMAGE:
            # Image optimization
            if any(word in title.lower() for word in ['photo', 'image', 'picture', 'art']):
                score += 3
            if len(keywords) >= 5:  # Important for image discovery
                score += 7
            score += 5
        
        return min(15.0, score)
    
    async def _generate_optimization_suggestions(
        self,
        title: str,
        description: str,
        keywords: List[str],
        seo_score: float,
        platform: SEOPlatform
    ) -> List[str]:
        """Generate actionable SEO optimization suggestions"""
        suggestions = []
        
        # Title optimizations
        title_length = len(title)
        if title_length < self.seo_rules["title_length"]["min"]:
            suggestions.append(f"Expand title to at least {self.seo_rules['title_length']['min']} characters for better SEO")
        elif title_length > self.seo_rules["title_length"]["max"]:
            suggestions.append(f"Shorten title to under {self.seo_rules['title_length']['max']} characters to avoid truncation")
        
        # Check if title contains primary keywords
        if keywords and not any(kw.lower() in title.lower() for kw in keywords[:3]):
            suggestions.append("Include your primary keyword in the title for better ranking")
        
        # Description optimizations
        desc_length = len(description)
        if desc_length < self.seo_rules["description_length"]["min"]:
            suggestions.append(f"Expand description to at least {self.seo_rules['description_length']['min']} characters")
        elif desc_length > self.seo_rules["description_length"]["max"]:
            suggestions.append(f"Shorten description to under {self.seo_rules['description_length']['max']} characters")
        
        # Keyword optimizations
        if len(keywords) < 5:
            suggestions.append("Add more relevant keywords to improve discoverability")
        elif len(keywords) > 20:
            suggestions.append("Focus on 10-15 most relevant keywords to avoid keyword stuffing")
        
        # Long-tail keyword suggestions
        single_word_keywords = [kw for kw in keywords if ' ' not in kw]
        if len(single_word_keywords) > len(keywords) * 0.8:
            suggestions.append("Include more long-tail keywords (2-3 word phrases) for better targeting")
        
        # Platform-specific suggestions
        if platform == SEOPlatform.YOUTUBE:
            if not any(word in title.lower() for word in ['how', 'what', 'why', 'best', 'top']):
                suggestions.append("Consider using question words or superlatives in title (How, What, Best, Top)")
            if len(description) < 100:
                suggestions.append("Expand description with timestamps, links, and detailed information")
        
        elif platform == SEOPlatform.INSTAGRAM:
            hashtag_potential = [kw for kw in keywords if ' ' not in kw]
            if len(hashtag_potential) < 10:
                suggestions.append("Add more single-word keywords that can be used as hashtags")
            if '#' not in description:
                suggestions.append("Include relevant hashtags in your caption for better discoverability")
        
        elif platform == SEOPlatform.GOOGLE:
            if not any(' ' in kw for kw in keywords):
                suggestions.append("Include long-tail keywords that match search intent")
            if seo_score < 70:
                suggestions.append("Optimize for featured snippets by answering common questions")
        
        # General improvements based on score
        if seo_score < 50:
            suggestions.append("Consider a complete SEO overhaul - current optimization is below average")
        elif seo_score < 70:
            suggestions.append("Focus on keyword optimization and content structure improvements")
        elif seo_score < 85:
            suggestions.append("Fine-tune existing optimization with platform-specific best practices")
        
        return suggestions
    
    async def _get_ranking_data(self, keywords: List[str], platform: SEOPlatform) -> Dict[str, int]:
        """Get ranking positions for keywords (simulated)"""
        # In a real implementation, this would query actual search APIs
        ranking_data = {}
        
        for keyword in keywords[:10]:  # Top 10 keywords
            # Simulate ranking position (1-100)
            import random
            position = random.randint(1, 100)
            ranking_data[keyword] = position
        
        return ranking_data
    
    async def _calculate_traffic_metrics(self, content_id: str, platform: SEOPlatform) -> Dict[str, float]:
        """Calculate traffic metrics for content"""
        # Simulated traffic metrics
        # In real implementation, would integrate with analytics APIs
        
        base_traffic = 1000  # Base traffic volume
        
        return {
            "organic_traffic": base_traffic * (0.5 + random.random()),
            "impressions": base_traffic * (2 + random.random() * 3),
            "click_through_rate": 0.02 + random.random() * 0.08,  # 2-10% CTR
            "bounce_rate": 0.3 + random.random() * 0.4,  # 30-70% bounce rate
            "average_session_duration": 60 + random.random() * 240,  # 1-5 minutes
            "pages_per_session": 1 + random.random() * 3
        }
    
    async def _analyze_social_signals(self, content_id: str) -> Dict[str, int]:
        """Analyze social signals for content"""
        # Simulated social signals
        import random
        
        return {
            "likes": random.randint(10, 1000),
            "shares": random.randint(5, 200),
            "comments": random.randint(2, 50),
            "saves": random.randint(5, 100),
            "mentions": random.randint(0, 20)
        }
    
    async def _analyze_technical_seo(
        self,
        content_id: str,
        platform: SEOPlatform,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        metadata = metadata or {}
        
        technical_analysis = {
            "mobile_friendly": True,  # Would check responsive design
            "page_speed_score": 85 + random.random() * 15,  # 85-100 speed score
            "ssl_certificate": True,
            "structured_data": bool(metadata.get("schema_markup")),
            "meta_tags_present": bool(metadata.get("meta_description")),
            "image_alt_text": bool(metadata.get("alt_text")),
            "canonical_url": bool(metadata.get("canonical")),
            "sitemap_included": True,
            "robots_txt": True,
            "url_structure_score": 90 + random.random() * 10
        }
        
        # Platform-specific technical factors
        if platform == SEOPlatform.YOUTUBE:
            technical_analysis.update({
                "video_quality": metadata.get("video_quality", "HD"),
                "closed_captions": bool(metadata.get("captions")),
                "thumbnail_optimized": bool(metadata.get("custom_thumbnail")),
                "end_screens": bool(metadata.get("end_screens"))
            })
        
        elif platform == SEOPlatform.INSTAGRAM:
            technical_analysis.update({
                "image_quality": metadata.get("image_quality", "high"),
                "aspect_ratio_optimized": bool(metadata.get("aspect_ratio")),
                "story_highlights": bool(metadata.get("highlights")),
                "business_profile": bool(metadata.get("business_account"))
            })
        
        return technical_analysis
    
    async def research_keywords(
        self,
        seed_keywords: List[str],
        platform: SEOPlatform,
        content_type: ContentType,
        target_audience: str = "general"
    ) -> List[KeywordData]:
        """Research and analyze keywords for optimization"""
        try:
            keyword_results = []
            
            for seed_keyword in seed_keywords:
                # Generate related keywords
                related_keywords = await self._generate_related_keywords(seed_keyword, platform)
                
                # Analyze each keyword
                for keyword in [seed_keyword] + related_keywords[:5]:
                    keyword_data = await self._analyze_keyword(keyword, platform, content_type)
                    keyword_results.append(keyword_data)
                    
                    # Store in keyword database
                    self.keyword_database[keyword] = keyword_data
            
            # Sort by opportunity score (high volume, low competition)
            keyword_results.sort(
                key=lambda k: k.search_volume * (1 - k.competition_score), 
                reverse=True
            )
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_keyword_research(keyword_results)
            
            return keyword_results[:20]  # Return top 20 keywords
            
        except Exception as e:
            self.logger.error(f"Error researching keywords: {e}")
            return []
    
    async def _generate_related_keywords(self, seed_keyword: str, platform: SEOPlatform) -> List[str]:
        """Generate related keywords for a seed keyword"""
        # Simulated keyword expansion
        # In real implementation, would use keyword research APIs
        
        base_variations = [
            f"best {seed_keyword}",
            f"how to {seed_keyword}",
            f"{seed_keyword} tutorial",
            f"{seed_keyword} tips",
            f"{seed_keyword} guide",
            f"{seed_keyword} review",
            f"{seed_keyword} 2025",
            f"top {seed_keyword}",
            f"{seed_keyword} examples",
            f"{seed_keyword} strategy"
        ]
        
        # Platform-specific variations
        if platform == SEOPlatform.YOUTUBE:
            base_variations.extend([
                f"{seed_keyword} video",
                f"{seed_keyword} channel",
                f"{seed_keyword} explained",
                f"{seed_keyword} vs"
            ])
        elif platform == SEOPlatform.INSTAGRAM:
            base_variations.extend([
                f"{seed_keyword} photo",
                f"{seed_keyword} inspiration",
                f"{seed_keyword} aesthetic",
                f"{seed_keyword} style"
            ])
        
        return base_variations[:10]
    
    async def _analyze_keyword(
        self,
        keyword: str,
        platform: SEOPlatform,
        content_type: ContentType
    ) -> KeywordData:
        """Analyze individual keyword metrics"""
        # Simulated keyword analysis
        # In real implementation, would use keyword research APIs
        
        import random
        
        # Estimate search volume based on keyword characteristics
        word_count = len(keyword.split())
        base_volume = 10000 if word_count == 1 else 5000 if word_count == 2 else 2000
        search_volume = int(base_volume * (0.1 + random.random() * 0.9))
        
        # Competition score (higher for shorter, more generic terms)
        competition_score = max(0.1, 1 - (word_count * 0.2) + random.random() * 0.3)
        
        # Cost per click (simulated)
        cpc = 0.5 + random.random() * 2.0
        
        # Determine intent type
        intent_type = "informational"
        if any(word in keyword.lower() for word in ["buy", "purchase", "price", "cost"]):
            intent_type = "transactional"
        elif any(word in keyword.lower() for word in ["how to", "what is", "why"]):
            intent_type = "informational"
        elif any(word in keyword.lower() for word in ["best", "review", "compare"]):
            intent_type = "commercial"
        
        # Trend direction (simulated)
        trend_direction = random.choice(["up", "stable", "down"])
        
        # Difficulty score
        difficulty_score = competition_score * (1 + random.random() * 0.2)
        
        return KeywordData(
            keyword=keyword,
            search_volume=search_volume,
            competition_score=competition_score,
            cpc=cpc,
            ranking_position=random.randint(1, 100),
            click_through_rate=0.01 + random.random() * 0.09,
            trend_direction=trend_direction,
            related_keywords=[],  # Would be populated separately
            intent_type=intent_type,
            difficulty_score=difficulty_score
        )
    
    async def create_seo_campaign(
        self,
        name: str,
        target_keywords: List[str],
        target_platforms: List[SEOPlatform],
        content_pieces: List[str],
        duration_days: int,
        objectives: Dict[str, float]
    ) -> SEOCampaign:
        """Create SEO optimization campaign"""
        try:
            campaign_id = f"seo_{int(datetime.now().timestamp())}_{hash(name) % 10000}"
            
            campaign = SEOCampaign(
                campaign_id=campaign_id,
                name=name,
                target_keywords=target_keywords,
                target_platforms=target_platforms,
                content_pieces=content_pieces,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=duration_days),
                objectives=objectives
            )
            
            # Generate optimization actions
            campaign.optimization_actions = await self._generate_campaign_actions(campaign)
            
            self.seo_campaigns[campaign_id] = campaign
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_seo_campaign(campaign)
            
            self.logger.info(f"SEO campaign created: {name}")
            return campaign
            
        except Exception as e:
            self.logger.error(f"Error creating SEO campaign: {e}")
            raise
    
    async def _generate_campaign_actions(self, campaign: SEOCampaign) -> List[str]:
        """Generate optimization actions for SEO campaign"""
        actions = []
        
        # Keyword-based actions
        for keyword in campaign.target_keywords[:5]:
            actions.append(f"Optimize content for '{keyword}' keyword")
            actions.append(f"Research long-tail variations of '{keyword}'")
        
        # Platform-specific actions
        for platform in campaign.target_platforms:
            if platform == SEOPlatform.YOUTUBE:
                actions.extend([
                    "Optimize video titles and descriptions",
                    "Add closed captions to videos",
                    "Create custom thumbnails",
                    "Use end screens and cards"
                ])
            elif platform == SEOPlatform.INSTAGRAM:
                actions.extend([
                    "Research and use trending hashtags",
                    "Optimize image alt text",
                    "Create consistent posting schedule",
                    "Engage with community hashtags"
                ])
            elif platform == SEOPlatform.GOOGLE:
                actions.extend([
                    "Optimize meta titles and descriptions",
                    "Improve page loading speed",
                    "Add structured data markup",
                    "Build quality backlinks"
                ])
        
        # Content optimization actions
        actions.extend([
            "Conduct content gap analysis",
            "Optimize existing content for target keywords",
            "Create new content around trending topics",
            "Improve internal linking structure",
            "Monitor and respond to comments"
        ])
        
        return list(set(actions))  # Remove duplicates
    
    async def analyze_seo_performance(
        self,
        time_range: Tuple[datetime, datetime],
        platforms: Optional[List[SEOPlatform]] = None,
        content_types: Optional[List[ContentType]] = None
    ) -> SEOIntelligenceMetrics:
        """Analyze comprehensive SEO performance metrics"""
        try:
            start_time, end_time = time_range
            
            # Filter analyses by time range, platforms, and content types
            filtered_analyses = [
                analysis for analysis in self.content_seo_analyses
                if start_time <= analysis.analyzed_at <= end_time
                and (not platforms or analysis.platform in platforms)
                and (not content_types or analysis.content_type in content_types)
            ]
            
            if not filtered_analyses:
                return SEOIntelligenceMetrics(time_period=time_range)
            
            # Basic metrics
            total_content = len(filtered_analyses)
            avg_seo_score = statistics.mean([a.seo_score for a in filtered_analyses])
            
            # Traffic metrics
            total_traffic = sum(a.traffic_metrics.get("organic_traffic", 0) for a in filtered_analyses)
            total_impressions = sum(a.traffic_metrics.get("impressions", 0) for a in filtered_analyses)
            avg_ctr = statistics.mean([a.traffic_metrics.get("click_through_rate", 0) for a in filtered_analyses])
            
            # Ranking metrics
            all_rankings = []
            for analysis in filtered_analyses:
                all_rankings.extend(analysis.ranking_data.values())
            avg_ranking = statistics.mean(all_rankings) if all_rankings else 0
            
            # Keyword performance
            keyword_performance = await self._analyze_keyword_performance(filtered_analyses)
            
            # Platform performance
            platform_performance = await self._analyze_platform_performance(filtered_analyses)
            
            # Content type performance
            content_type_performance = await self._analyze_content_type_performance(filtered_analyses)
            
            # Trending keywords
            trending_keywords = await self._identify_trending_keywords(filtered_analyses)
            
            # Optimization opportunities
            opportunities = await self._identify_optimization_opportunities(filtered_analyses)
            
            # Competitor analysis (simulated)
            competitor_analysis = await self._analyze_competitors(keyword_performance)
            
            # Technical SEO health
            technical_health = await self._calculate_technical_seo_health(filtered_analyses)
            
            metrics = SEOIntelligenceMetrics(
                time_period=time_range,
                total_content_analyzed=total_content,
                average_seo_score=avg_seo_score,
                total_organic_traffic=int(total_traffic),
                total_impressions=int(total_impressions),
                average_ranking_position=avg_ranking,
                click_through_rate=avg_ctr,
                keyword_performance=keyword_performance,
                platform_performance=platform_performance,
                content_type_performance=content_type_performance,
                trending_keywords=trending_keywords,
                optimization_opportunities=opportunities,
                competitor_analysis=competitor_analysis,
                technical_seo_health=technical_health
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing SEO performance: {e}")
            return SEOIntelligenceMetrics(time_period=time_range)
    
    async def _analyze_keyword_performance(self, analyses: List[ContentSEOAnalysis]) -> Dict[str, Any]:
        """Analyze keyword performance across content"""
        keyword_stats = defaultdict(lambda: {"count": 0, "avg_score": 0, "avg_ranking": 0, "total_traffic": 0})
        
        for analysis in analyses:
            for keyword in analysis.keywords:
                stats = keyword_stats[keyword]
                stats["count"] += 1
                stats["avg_score"] += analysis.seo_score
                
                if keyword in analysis.ranking_data:
                    stats["avg_ranking"] += analysis.ranking_data[keyword]
                
                stats["total_traffic"] += analysis.traffic_metrics.get("organic_traffic", 0)
        
        # Calculate averages and sort by performance
        performance_data = {}
        for keyword, stats in keyword_stats.items():
            if stats["count"] > 0:
                performance_data[keyword] = {
                    "usage_count": stats["count"],
                    "average_seo_score": stats["avg_score"] / stats["count"],
                    "average_ranking": stats["avg_ranking"] / stats["count"] if stats["avg_ranking"] > 0 else 0,
                    "total_traffic": stats["total_traffic"],
                    "traffic_per_usage": stats["total_traffic"] / stats["count"]
                }
        
        # Sort by traffic per usage
        sorted_keywords = sorted(
            performance_data.items(),
            key=lambda x: x[1]["traffic_per_usage"],
            reverse=True
        )
        
        return {
            "top_performing_keywords": dict(sorted_keywords[:10]),
            "total_unique_keywords": len(performance_data),
            "average_keywords_per_content": statistics.mean([len(a.keywords) for a in analyses])
        }
    
    async def _analyze_platform_performance(self, analyses: List[ContentSEOAnalysis]) -> Dict[str, Any]:
        """Analyze SEO performance by platform"""
        platform_stats = defaultdict(lambda: {"count": 0, "total_score": 0, "total_traffic": 0})
        
        for analysis in analyses:
            platform = analysis.platform.value
            stats = platform_stats[platform]
            stats["count"] += 1
            stats["total_score"] += analysis.seo_score
            stats["total_traffic"] += analysis.traffic_metrics.get("organic_traffic", 0)
        
        performance_by_platform = {}
        for platform, stats in platform_stats.items():
            if stats["count"] > 0:
                performance_by_platform[platform] = {
                    "content_count": stats["count"],
                    "average_seo_score": stats["total_score"] / stats["count"],
                    "total_traffic": stats["total_traffic"],
                    "average_traffic_per_content": stats["total_traffic"] / stats["count"]
                }
        
        return performance_by_platform
    
    async def _analyze_content_type_performance(self, analyses: List[ContentSEOAnalysis]) -> Dict[str, Any]:
        """Analyze SEO performance by content type"""
        type_stats = defaultdict(lambda: {"count": 0, "total_score": 0, "total_traffic": 0})
        
        for analysis in analyses:
            content_type = analysis.content_type.value
            stats = type_stats[content_type]
            stats["count"] += 1
            stats["total_score"] += analysis.seo_score
            stats["total_traffic"] += analysis.traffic_metrics.get("organic_traffic", 0)
        
        performance_by_type = {}
        for content_type, stats in type_stats.items():
            if stats["count"] > 0:
                performance_by_type[content_type] = {
                    "content_count": stats["count"],
                    "average_seo_score": stats["total_score"] / stats["count"],
                    "total_traffic": stats["total_traffic"],
                    "average_traffic_per_content": stats["total_traffic"] / stats["count"]
                }
        
        return performance_by_type
    
    async def _identify_trending_keywords(self, analyses: List[ContentSEOAnalysis]) -> List[Dict[str, Any]]:
        """Identify trending keywords from recent content"""
        keyword_frequency = defaultdict(int)
        keyword_scores = defaultdict(list)
        
        # Count keyword usage and collect scores
        for analysis in analyses:
            for keyword in analysis.keywords:
                keyword_frequency[keyword] += 1
                keyword_scores[keyword].append(analysis.seo_score)
        
        # Calculate trending score (frequency * average performance)
        trending_keywords = []
        for keyword, frequency in keyword_frequency.items():
            if frequency >= 2:  # Must appear in at least 2 pieces of content
                avg_score = statistics.mean(keyword_scores[keyword])
                trending_score = frequency * (avg_score / 100)
                
                trending_keywords.append({
                    "keyword": keyword,
                    "frequency": frequency,
                    "average_seo_score": round(avg_score, 2),
                    "trending_score": round(trending_score, 3)
                })
        
        # Sort by trending score
        trending_keywords.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return trending_keywords[:15]
    
    async def _identify_optimization_opportunities(self, analyses: List[ContentSEOAnalysis]) -> List[Dict[str, Any]]:
        """Identify SEO optimization opportunities"""
        opportunities = []
        
        # Low-performing content with high potential
        low_performers = [a for a in analyses if a.seo_score < 60]
        if low_performers:
            opportunities.append({
                "type": "low_performing_content",
                "priority": "high",
                "count": len(low_performers),
                "description": f"{len(low_performers)} pieces of content have SEO scores below 60",
                "action": "Review and optimize title, description, and keywords for these content pieces"
            })
        
        # Missing keywords opportunities
        keyword_counts = [len(a.keywords) for a in analyses]
        avg_keywords = statistics.mean(keyword_counts)
        if avg_keywords < 8:
            opportunities.append({
                "type": "keyword_optimization",
                "priority": "medium",
                "count": len([k for k in keyword_counts if k < 5]),
                "description": f"Average keyword count is {avg_keywords:.1f}, below recommended 8-12",
                "action": "Research and add more relevant keywords to content"
            })
        
        # Platform-specific opportunities
        platform_scores = defaultdict(list)
        for analysis in analyses:
            platform_scores[analysis.platform].append(analysis.seo_score)
        
        for platform, scores in platform_scores.items():
            avg_score = statistics.mean(scores)
            if avg_score < 70:
                opportunities.append({
                    "type": "platform_optimization",
                    "priority": "medium",
                    "platform": platform.value,
                    "average_score": round(avg_score, 2),
                    "description": f"{platform.value} content has below-average SEO performance",
                    "action": f"Implement {platform.value}-specific SEO best practices"
                })
        
        # Technical SEO opportunities
        technical_issues = []
        for analysis in analyses:
            if not analysis.technical_seo.get("mobile_friendly", True):
                technical_issues.append("mobile_optimization")
            if analysis.technical_seo.get("page_speed_score", 100) < 80:
                technical_issues.append("page_speed")
            if not analysis.technical_seo.get("structured_data", True):
                technical_issues.append("structured_data")
        
        if technical_issues:
            common_issues = list(set(technical_issues))
            opportunities.append({
                "type": "technical_seo",
                "priority": "high",
                "issues": common_issues,
                "description": f"Technical SEO issues found: {', '.join(common_issues)}",
                "action": "Address technical SEO issues to improve search performance"
            })
        
        return opportunities
    
    async def _analyze_competitors(self, keyword_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor SEO performance (simulated)"""
        # In real implementation, would analyze actual competitor data
        
        return {
            "competitor_keywords": {
                "shared_keywords": 15,
                "competitor_only": 8,
                "our_advantage": 12
            },
            "ranking_comparison": {
                "better_than_competitors": 0.65,
                "equal_to_competitors": 0.25,
                "worse_than_competitors": 0.10
            },
            "content_gaps": [
                "Tutorial content",
                "Product comparison guides",
                "FAQ content",
                "How-to videos"
            ],
            "competitor_strengths": [
                "Strong backlink profile",
                "Consistent content publishing",
                "Better technical SEO",
                "Higher domain authority"
            ]
        }
    
    async def _calculate_technical_seo_health(self, analyses: List[ContentSEOAnalysis]) -> Dict[str, float]:
        """Calculate overall technical SEO health score"""
        if not analyses:
            return {}
        
        # Aggregate technical SEO factors
        mobile_friendly_count = sum(1 for a in analyses if a.technical_seo.get("mobile_friendly", False))
        ssl_count = sum(1 for a in analyses if a.technical_seo.get("ssl_certificate", False))
        structured_data_count = sum(1 for a in analyses if a.technical_seo.get("structured_data", False))
        meta_tags_count = sum(1 for a in analyses if a.technical_seo.get("meta_tags_present", False))
        
        total_content = len(analyses)
        
        # Calculate speed scores
        speed_scores = [a.technical_seo.get("page_speed_score", 0) for a in analyses if a.technical_seo.get("page_speed_score")]
        avg_speed_score = statistics.mean(speed_scores) if speed_scores else 0
        
        return {
            "mobile_friendly_percentage": (mobile_friendly_count / total_content) * 100,
            "ssl_coverage_percentage": (ssl_count / total_content) * 100,
            "structured_data_percentage": (structured_data_count / total_content) * 100,
            "meta_tags_percentage": (meta_tags_count / total_content) * 100,
            "average_page_speed_score": avg_speed_score,
            "overall_technical_health": (
                (mobile_friendly_count + ssl_count + structured_data_count + meta_tags_count) / 
                (total_content * 4)
            ) * 100
        }
    
    # Platform-specific SEO analyzers
    async def _analyze_google_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze Google-specific SEO factors"""
        return {
            "title_tag_optimization": len(analysis.title) <= 60,
            "meta_description_optimization": len(analysis.description) <= 160,
            "keyword_in_title": any(kw.lower() in analysis.title.lower() for kw in analysis.keywords[:3]),
            "keyword_in_description": any(kw.lower() in analysis.description.lower() for kw in analysis.keywords[:3]),
            "readability_score": 75 + random.random() * 20,  # Simulated
            "internal_links": random.randint(2, 10),
            "external_links": random.randint(1, 5),
            "schema_markup": bool(random.choice([True, False]))
        }
    
    async def _analyze_youtube_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze YouTube-specific SEO factors"""
        return {
            "title_optimization": len(analysis.title) <= 100,
            "description_length": len(analysis.description) >= 125,
            "tags_count": len(analysis.keywords),
            "thumbnail_quality": "high",  # Would analyze actual thumbnail
            "closed_captions": True,  # Would check for captions
            "end_screens": True,
            "cards": random.randint(0, 5),
            "playlist_inclusion": bool(random.choice([True, False]))
        }
    
    async def _analyze_instagram_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze Instagram-specific SEO factors"""
        hashtag_keywords = [kw for kw in analysis.keywords if ' ' not in kw]
        
        return {
            "hashtag_count": len(hashtag_keywords),
            "caption_length": len(analysis.description),
            "alt_text_present": True,  # Would check actual alt text
            "location_tagged": bool(random.choice([True, False])),
            "user_tagged": random.randint(0, 5),
            "story_highlights": bool(random.choice([True, False])),
            "business_account": True,
            "consistent_posting": True
        }
    
    async def _analyze_tiktok_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze TikTok-specific SEO factors"""
        return {
            "caption_optimization": len(analysis.title) <= 100,
            "trending_hashtags": random.randint(3, 8),
            "trending_sounds": bool(random.choice([True, False])),
            "captions_enabled": True,
            "posting_time_optimal": True,
            "engagement_rate": 0.05 + random.random() * 0.15,
            "completion_rate": 0.6 + random.random() * 0.3,
            "shares_to_views_ratio": 0.02 + random.random() * 0.08
        }
    
    async def _analyze_twitter_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze Twitter-specific SEO factors"""
        return {
            "character_count": len(analysis.title),
            "hashtag_usage": len([kw for kw in analysis.keywords if len(kw) < 20]),
            "mention_usage": random.randint(0, 3),
            "media_attachment": bool(random.choice([True, False])),
            "thread_structure": bool(random.choice([True, False])),
            "retweet_potential": 0.1 + random.random() * 0.3,
            "reply_engagement": 0.05 + random.random() * 0.15,
            "trending_topics": random.randint(0, 2)
        }
    
    async def _analyze_linkedin_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze LinkedIn-specific SEO factors"""
        return {
            "professional_keywords": sum(1 for kw in analysis.keywords if any(
                prof_word in kw.lower() for prof_word in ["business", "professional", "career", "industry"]
            )),
            "post_length": len(analysis.description),
            "industry_hashtags": random.randint(3, 8),
            "company_mention": bool(random.choice([True, False])),
            "skill_keywords": random.randint(2, 6),
            "networking_potential": 0.2 + random.random() * 0.4,
            "thought_leadership": bool(random.choice([True, False])),
            "engagement_quality": 0.15 + random.random() * 0.25
        }
    
    async def _analyze_spotify_seo(self, analysis: ContentSEOAnalysis) -> Dict[str, Any]:
        """Analyze Spotify-specific SEO factors"""
        return {
            "track_title_optimization": len(analysis.title) <= 50,
            "artist_name_consistency": True,
            "genre_tags": len(analysis.keywords),
            "playlist_placement": random.randint(5, 50),
            "album_artwork_quality": "high",
            "release_timing": True,
            "collaborative_playlists": random.randint(0, 10),
            "podcast_optimization": bool(analysis.content_type == ContentType.PODCAST)
        }
    
    # Redis caching methods
    async def _cache_seo_analysis(self, analysis: ContentSEOAnalysis):
        """Cache SEO analysis in Redis"""
        if self.redis_client:
            try:
                key = f"seo_analysis:{analysis.content_id}"
                data = {
                    "seo_score": analysis.seo_score,
                    "platform": analysis.platform.value,
                    "content_type": analysis.content_type.value,
                    "keywords_count": len(analysis.keywords),
                    "analyzed_at": analysis.analyzed_at.isoformat()
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 86400)  # 24 hour expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_keyword_research(self, keywords: List[KeywordData]):
        """Cache keyword research results in Redis"""
        if self.redis_client:
            try:
                for keyword_data in keywords:
                    key = f"keyword:{keyword_data.keyword}"
                    data = {
                        "search_volume": keyword_data.search_volume,
                        "competition_score": keyword_data.competition_score,
                        "difficulty_score": keyword_data.difficulty_score,
                        "trend_direction": keyword_data.trend_direction
                    }
                    self.redis_client.hset(key, mapping=data)
                    self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    async def _cache_seo_campaign(self, campaign: SEOCampaign):
        """Cache SEO campaign in Redis"""
        if self.redis_client:
            try:
                key = f"seo_campaign:{campaign.campaign_id}"
                data = {
                    "name": campaign.name,
                    "target_keywords": ",".join(campaign.target_keywords),
                    "target_platforms": ",".join([p.value for p in campaign.target_platforms]),
                    "success_rate": campaign.success_rate,
                    "roi_score": campaign.roi_score
                }
                self.redis_client.hset(key, mapping=data)
                self.redis_client.expire(key, 604800)  # 7 day expiry
            except Exception as e:
                self.logger.error(f"Redis cache error: {e}")
    
    def get_seo_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of SEO intelligence system"""
        try:
            total_analyses = len(self.content_seo_analyses)
            total_keywords = len(self.keyword_database)
            total_campaigns = len(self.seo_campaigns)
            
            # Calculate averages
            if self.content_seo_analyses:
                avg_seo_score = statistics.mean([a.seo_score for a in self.content_seo_analyses])
                platform_distribution = defaultdict(int)
                for analysis in self.content_seo_analyses:
                    platform_distribution[analysis.platform.value] += 1
            else:
                avg_seo_score = 0
                platform_distribution = {}
            
            return {
                "system_stats": {
                    "total_content_analyzed": total_analyses,
                    "total_keywords_tracked": total_keywords,
                    "active_campaigns": total_campaigns,
                    "platform_coverage": len(platform_distribution)
                },
                "performance_metrics": {
                    "average_seo_score": round(avg_seo_score, 2),
                    "ml_models_initialized": self._ml_models_initialized,
                    "redis_connected": self.redis_client is not None
                },
                "platform_distribution": dict(platform_distribution),
                "recent_activity": {
                    "analyses_last_24h": len([
                        a for a in self.content_seo_analyses 
                        if (datetime.now() - a.analyzed_at).days == 0
                    ])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SEO intelligence summary: {e}")
            return {"error": str(e)}

# Add random import for simulations
import random