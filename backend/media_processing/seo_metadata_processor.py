#!/usr/bin/env python3
"""🔍 SEO Metadata Processor - Advanced SEO Optimization Engine
===============================================================================
Module: backend/media_processing/seo_metadata_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: SEO Specialist + AI Engineer + Content Strategist + Data Analyst
Type: Advanced SEO Processing System - Production-Ready
Responsibility: Comprehensive SEO metadata processing and platform optimization
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🔍 SEO CAPABILITIES:
- AI-powered keyword extraction and optimization
- Platform-specific metadata generation
- Trending analysis and alignment
- Engagement prediction and optimization
- Multi-language SEO support
- Content strategy recommendations
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import uuid

# Import existing SEO systems for integration
try:
    from ...backend.seo_engine.seo_optimization_core import SEOOptimizationCore
    from ...backend.core.seo_optimization_core import SEOOptimizationCore as CoreSEO
    SEO_CORE_AVAILABLE = True
except ImportError:
    SEO_CORE_AVAILABLE = False

# Import AI libraries for content analysis
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for SEO optimization"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    SPOTIFY = "spotify"


class ContentType(Enum):
    """Content types for SEO optimization"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"


class CreatorType(Enum):
    """Creator types for targeted SEO"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    EDUCATOR = "educator"
    GAMER = "gamer"
    BUSINESS = "business"


@dataclass
class SEOKeywords:
    """SEO keywords with relevance scores"""
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    trending_keywords: List[str] = field(default_factory=list)
    keyword_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class PlatformMetadata:
    """Platform-specific metadata"""
    platform: Platform
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SEOAnalysis:
    """SEO analysis result"""
    seo_score: float
    keyword_density: Dict[str, float]
    readability_score: float
    content_length_analysis: Dict[str, Any]
    recommendations: List[str]
    optimization_opportunities: List[str]


@dataclass
class TrendingAnalysis:
    """Trending content analysis"""
    trending_score: float
    trend_alignment: Dict[str, float]
    seasonal_trends: List[str]
    competitive_analysis: Dict[str, Any]
    viral_potential: float


@dataclass
class EngagementPrediction:
    """Engagement prediction result"""
    predicted_engagement_rate: float
    estimated_reach: int
    target_audience_size: int
    engagement_factors: Dict[str, float]
    optimization_suggestions: List[str]


class SEOMetadataProcessor:
    """Advanced SEO Optimization Engine
    
    Comprehensive SEO metadata processing system with AI-powered optimization,
    platform-specific adaptation, and engagement prediction capabilities.
    """

    def __init__(self):
        """Initialize SEO metadata processor"""
        
        # Initialize existing SEO systems if available
        if SEO_CORE_AVAILABLE:
            self.seo_core = SEOOptimizationCore()
        else:
            self.seo_core = None
            logger.warning("SEO core system not available")
        
        # Initialize NLP models if available
        if NLP_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                self.keyword_extractor = pipeline("ner", aggregation_strategy="simple")
                self.nlp_available = True
            except Exception as e:
                logger.warning(f"Failed to load NLP models: {str(e)}")
                self.nlp_available = False
        else:
            self.nlp_available = False
        
        # Platform-specific configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Trending keywords cache
        self.trending_cache = {}
        self.cache_timestamp = None

    def _initialize_platform_configs(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            Platform.YOUTUBE: {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 500,
                "optimal_title_length": 60,
                "optimal_description_length": 125,
                "keyword_importance": {"title": 0.4, "description": 0.3, "tags": 0.3}
            },
            Platform.INSTAGRAM: {
                "caption_max_length": 2200,
                "hashtags_max_count": 30,
                "hashtags_optimal_count": 11,
                "stories_text_limit": 2200,
                "keyword_importance": {"caption": 0.5, "hashtags": 0.5}
            },
            Platform.TIKTOK: {
                "caption_max_length": 300,
                "hashtags_max_count": 100,
                "hashtags_optimal_count": 5,
                "trending_factor": 0.8,
                "keyword_importance": {"caption": 0.3, "hashtags": 0.7}
            },
            Platform.FACEBOOK: {
                "post_optimal_length": 80,
                "description_max_length": 63206,
                "hashtags_max_count": 30,
                "hashtags_optimal_count": 3,
                "keyword_importance": {"title": 0.4, "description": 0.4, "hashtags": 0.2}
            },
            Platform.TWITTER: {
                "tweet_max_length": 280,
                "hashtags_max_count": 2,
                "optimal_hashtags": 1,
                "trending_factor": 0.9,
                "keyword_importance": {"text": 0.7, "hashtags": 0.3}
            },
            Platform.LINKEDIN: {
                "post_max_length": 3000,
                "post_optimal_length": 150,
                "hashtags_max_count": 5,
                "professional_tone": True,
                "keyword_importance": {"title": 0.4, "content": 0.4, "hashtags": 0.2}
            }
        }

    async def process_seo_metadata(
        self,
        content_id: str,
        content_type: ContentType,
        creator_type: CreatorType,
        content_data: Optional[str] = None,
        target_platforms: Optional[List[Platform]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process comprehensive SEO metadata"""
        
        if target_platforms is None:
            target_platforms = [Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK]
        
        if options is None:
            options = {}
        
        start_time = datetime.now()
        
        try:
            # Extract keywords
            keywords = await self._extract_keywords(content_data, content_type, creator_type, options)
            
            # Analyze trending topics
            trending_analysis = await self._analyze_trending_topics(keywords, target_platforms)
            
            # Generate platform-specific metadata
            platform_metadata = {}
            for platform in target_platforms:
                metadata = await self._generate_platform_metadata(
                    platform, content_type, creator_type, keywords, trending_analysis, options
                )
                platform_metadata[platform.value] = metadata
            
            # Perform SEO analysis
            seo_analysis = await self._analyze_seo_performance(
                content_data, keywords, platform_metadata, options
            )
            
            # Predict engagement
            engagement_prediction = await self._predict_engagement(
                content_type, creator_type, keywords, platform_metadata, trending_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                seo_analysis, engagement_prediction, trending_analysis, target_platforms
            )
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "content_id": content_id,
                "keywords": keywords.__dict__,
                "platform_metadata": platform_metadata,
                "seo_analysis": seo_analysis.__dict__,
                "trending_analysis": trending_analysis.__dict__,
                "engagement_prediction": engagement_prediction.__dict__,
                "recommendations": recommendations,
                "processing_time_ms": processing_time,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"SEO metadata processing failed for content {content_id}: {str(e)}")
            return {
                "content_id": content_id,
                "error": str(e),
                "processing_time_ms": 0,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }

    async def _extract_keywords(
        self,
        content_data: Optional[str],
        content_type: ContentType,
        creator_type: CreatorType,
        options: Dict[str, Any]
    ) -> SEOKeywords:
        """Extract and optimize keywords"""
        
        if self.nlp_available and content_data:
            try:
                # Extract entities and keywords using NLP
                doc = self.nlp(content_data)
                
                # Extract named entities
                entities = [ent.text.lower() for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "PRODUCT", "EVENT"]]
                
                # Extract noun phrases as potential keywords
                noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
                
                # Extract important words
                important_words = [token.lemma_.lower() for token in doc 
                                 if not token.is_stop and not token.is_punct and len(token.text) > 2]
                
                # Combine and score keywords
                all_keywords = entities + noun_phrases + important_words
                keyword_scores = {}
                
                for keyword in set(all_keywords):
                    score = all_keywords.count(keyword) / len(all_keywords)
                    keyword_scores[keyword] = score
                
                # Sort by relevance
                sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
                
                primary_keywords = [kw for kw, score in sorted_keywords[:5]]
                secondary_keywords = [kw for kw, score in sorted_keywords[5:15]]
                long_tail_keywords = [kw for kw, score in sorted_keywords if len(kw.split()) > 2][:10]
                
            except Exception as e:
                logger.error(f"NLP keyword extraction failed: {str(e)}")
                primary_keywords = []
                secondary_keywords = []
                long_tail_keywords = []
                keyword_scores = {}
        else:
            primary_keywords = []
            secondary_keywords = []
            long_tail_keywords = []
            keyword_scores = {}
        
        # Add creator and content type specific keywords
        creator_keywords = self._get_creator_type_keywords(creator_type)
        content_keywords = self._get_content_type_keywords(content_type)
        
        primary_keywords.extend(creator_keywords[:3])
        secondary_keywords.extend(content_keywords[:5])
        
        # Add trending keywords
        trending_keywords = await self._get_trending_keywords(creator_type, content_type)
        
        return SEOKeywords(
            primary_keywords=primary_keywords[:10],
            secondary_keywords=secondary_keywords[:20],
            long_tail_keywords=long_tail_keywords[:15],
            trending_keywords=trending_keywords[:10],
            keyword_scores=keyword_scores
        )

    def _get_creator_type_keywords(self, creator_type: CreatorType) -> List[str]:
        """Get keywords specific to creator type"""
        creator_keywords = {
            CreatorType.MUSICIAN: ["music", "song", "artist", "album", "musician", "band", "performance"],
            CreatorType.BLOGGER: ["blog", "article", "writer", "content", "story", "opinion", "review"],
            CreatorType.PHOTOGRAPHER: ["photography", "photo", "image", "camera", "visual", "art", "portrait"],
            CreatorType.INFLUENCER: ["influencer", "lifestyle", "trending", "viral", "social", "content creator"],
            CreatorType.COMEDIAN: ["comedy", "funny", "humor", "joke", "entertainment", "laugh", "comedian"],
            CreatorType.EDUCATOR: ["education", "learning", "tutorial", "teaching", "knowledge", "course"],
            CreatorType.GAMER: ["gaming", "game", "gameplay", "streaming", "esports", "player", "review"],
            CreatorType.BUSINESS: ["business", "professional", "corporate", "industry", "company", "service"]
        }
        return creator_keywords.get(creator_type, [])

    def _get_content_type_keywords(self, content_type: ContentType) -> List[str]:
        """Get keywords specific to content type"""
        content_keywords = {
            ContentType.VIDEO: ["video", "watch", "visual", "film", "movie", "clip", "recording"],
            ContentType.AUDIO: ["audio", "listen", "sound", "voice", "recording", "podcast", "music"],
            ContentType.IMAGE: ["image", "photo", "picture", "visual", "graphic", "art", "design"],
            ContentType.TEXT: ["text", "article", "read", "content", "story", "blog", "writing"],
            ContentType.PODCAST: ["podcast", "audio", "listen", "episode", "show", "talk", "discussion"],
            ContentType.LIVE_STREAM: ["live", "stream", "streaming", "broadcast", "real-time", "watch"]
        }
        return content_keywords.get(content_type, [])

    async def _get_trending_keywords(self, creator_type: CreatorType, content_type: ContentType) -> List[str]:
        """Get trending keywords for creator and content type"""
        
        # Check cache
        cache_key = f"{creator_type.value}_{content_type.value}"
        if (self.cache_timestamp and 
            datetime.now() - self.cache_timestamp < timedelta(hours=1) and
            cache_key in self.trending_cache):
            return self.trending_cache[cache_key]
        
        # Simulate trending keyword retrieval
        # In a real implementation, this would query trending APIs
        trending_keywords = {
            f"{CreatorType.MUSICIAN.value}_{ContentType.AUDIO.value}": [
                "viral music", "trending song", "new release", "spotify trending", "music discovery"
            ],
            f"{CreatorType.INFLUENCER.value}_{ContentType.VIDEO.value}": [
                "viral video", "trending content", "social media", "influencer tips", "lifestyle"
            ],
            f"{CreatorType.PHOTOGRAPHER.value}_{ContentType.IMAGE.value}": [
                "photography tips", "camera gear", "photo editing", "instagram worthy", "visual art"
            ]
        }
        
        result = trending_keywords.get(cache_key, ["trending", "viral", "popular", "new", "latest"])
        
        # Update cache
        self.trending_cache[cache_key] = result
        self.cache_timestamp = datetime.now()
        
        return result

    async def _analyze_trending_topics(
        self,
        keywords: SEOKeywords,
        target_platforms: List[Platform]
    ) -> TrendingAnalysis:
        """Analyze trending topics and alignment"""
        
        # Simulate trending analysis
        # In a real implementation, this would use trending APIs from platforms
        
        trending_score = 0.7  # Base trending score
        
        # Calculate trend alignment for each keyword
        trend_alignment = {}
        for keyword in keywords.primary_keywords + keywords.secondary_keywords:
            # Simulate trend strength
            if keyword in keywords.trending_keywords:
                alignment = 0.9
            elif any(trend_word in keyword for trend_word in ["viral", "trending", "popular"]):
                alignment = 0.8
            else:
                alignment = 0.5
            
            trend_alignment[keyword] = alignment
        
        # Seasonal trends simulation
        current_month = datetime.now().month
        seasonal_trends = []
        if current_month in [12, 1, 2]:  # Winter
            seasonal_trends = ["winter", "holiday", "new year", "resolution"]
        elif current_month in [3, 4, 5]:  # Spring
            seasonal_trends = ["spring", "renewal", "fresh start", "growth"]
        elif current_month in [6, 7, 8]:  # Summer
            seasonal_trends = ["summer", "vacation", "outdoor", "festival"]
        else:  # Fall
            seasonal_trends = ["fall", "autumn", "back to school", "halloween"]
        
        # Competitive analysis simulation
        competitive_analysis = {
            "competitor_keyword_overlap": 0.4,
            "content_saturation": 0.6,
            "opportunity_score": 0.7,
            "differentiation_potential": 0.8
        }
        
        # Viral potential calculation
        viral_factors = [
            len(keywords.trending_keywords) / 10,  # Trending keyword usage
            sum(trend_alignment.values()) / len(trend_alignment) if trend_alignment else 0,  # Trend alignment
            0.7  # Base viral potential
        ]
        viral_potential = min(sum(viral_factors) / len(viral_factors), 1.0)
        
        return TrendingAnalysis(
            trending_score=trending_score,
            trend_alignment=trend_alignment,
            seasonal_trends=seasonal_trends,
            competitive_analysis=competitive_analysis,
            viral_potential=viral_potential
        )

    async def _generate_platform_metadata(
        self,
        platform: Platform,
        content_type: ContentType,
        creator_type: CreatorType,
        keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        options: Dict[str, Any]
    ) -> PlatformMetadata:
        """Generate platform-specific metadata"""
        
        config = self.platform_configs.get(platform, {})
        
        # Generate title
        title = await self._generate_title(platform, keywords, config, options)
        
        # Generate description
        description = await self._generate_description(platform, keywords, trending_analysis, config, options)
        
        # Generate tags
        tags = await self._generate_tags(platform, keywords, content_type, creator_type, config)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(platform, keywords, trending_analysis, config)
        
        # Platform-specific custom fields
        custom_fields = await self._generate_custom_fields(platform, content_type, keywords, options)
        
        return PlatformMetadata(
            platform=platform,
            title=title,
            description=description,
            tags=tags,
            hashtags=hashtags,
            custom_fields=custom_fields
        )

    async def _generate_title(
        self,
        platform: Platform,
        keywords: SEOKeywords,
        config: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Generate optimized title for platform"""
        
        max_length = config.get("title_max_length", 100)
        optimal_length = config.get("optimal_title_length", 60)
        
        # Use primary keywords in title
        primary_keywords = keywords.primary_keywords[:3]
        
        if platform == Platform.YOUTUBE:
            title_templates = [
                "{keyword1} | {keyword2} Tutorial",
                "Amazing {keyword1} - {keyword2} Guide",
                "{keyword1}: Everything You Need to Know About {keyword2}",
                "Ultimate {keyword1} {keyword2} Experience"
            ]
        elif platform == Platform.INSTAGRAM:
            title_templates = [
                "{keyword1} vibes ✨",
                "Living that {keyword1} life",
                "{keyword1} moments that matter",
                "Pure {keyword1} energy"
            ]
        elif platform == Platform.TIKTOK:
            title_templates = [
                "{keyword1} hack you need to try!",
                "POV: You discover {keyword1}",
                "{keyword1} but make it {keyword2}",
                "This {keyword1} trend is everything"
            ]
        else:
            title_templates = [
                "{keyword1} - {keyword2}",
                "Discover {keyword1}",
                "{keyword1} Insights"
            ]
        
        # Generate title
        if len(primary_keywords) >= 2:
            template = title_templates[0]
            title = template.format(
                keyword1=primary_keywords[0].title(),
                keyword2=primary_keywords[1].title()
            )
        elif len(primary_keywords) >= 1:
            title = f"Amazing {primary_keywords[0].title()} Content"
        else:
            title = "Engaging Content"
        
        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title

    async def _generate_description(
        self,
        platform: Platform,
        keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        config: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """Generate optimized description for platform"""
        
        max_length = config.get("description_max_length", 2000)
        
        # Build description sections
        sections = []
        
        # Introduction
        if keywords.primary_keywords:
            intro = f"Discover amazing {keywords.primary_keywords[0]} content that will inspire you."
            sections.append(intro)
        
        # Keywords integration
        if keywords.secondary_keywords:
            keyword_text = f"Featuring: {', '.join(keywords.secondary_keywords[:5])}"
            sections.append(keyword_text)
        
        # Trending elements
        if trending_analysis.seasonal_trends:
            trending_text = f"Perfect for the {trending_analysis.seasonal_trends[0]} season!"
            sections.append(trending_text)
        
        # Call to action
        cta_map = {
            Platform.YOUTUBE: "Don't forget to like, subscribe, and hit the notification bell!",
            Platform.INSTAGRAM: "Double tap if you love this! Share with friends who need to see this! ✨",
            Platform.TIKTOK: "Follow for more content like this! 🔥",
            Platform.FACEBOOK: "Like and share if this resonates with you!",
            Platform.TWITTER: "Retweet if you agree!",
            Platform.LINKEDIN: "What are your thoughts? Share in the comments below."
        }
        
        if platform in cta_map:
            sections.append(cta_map[platform])
        
        # Join sections
        description = "\n\n".join(sections)
        
        # Truncate if too long
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
        
        return description

    async def _generate_tags(
        self,
        platform: Platform,
        keywords: SEOKeywords,
        content_type: ContentType,
        creator_type: CreatorType,
        config: Dict[str, Any]
    ) -> List[str]:
        """Generate tags for platform"""
        
        max_tags = config.get("tags_max_count", 50)
        
        tags = []
        
        # Add primary and secondary keywords as tags
        tags.extend(keywords.primary_keywords)
        tags.extend(keywords.secondary_keywords[:10])
        
        # Add content type specific tags
        content_tags = self._get_content_type_keywords(content_type)
        tags.extend(content_tags[:5])
        
        # Add creator type specific tags
        creator_tags = self._get_creator_type_keywords(creator_type)
        tags.extend(creator_tags[:5])
        
        # Add trending keywords
        tags.extend(keywords.trending_keywords[:5])
        
        # Remove duplicates and clean
        tags = list(set([tag.strip().lower() for tag in tags if tag.strip()]))
        
        # Limit to max tags
        return tags[:max_tags]

    async def _generate_hashtags(
        self,
        platform: Platform,
        keywords: SEOKeywords,
        trending_analysis: TrendingAnalysis,
        config: Dict[str, Any]
    ) -> List[str]:
        """Generate hashtags for platform"""
        
        max_hashtags = config.get("hashtags_max_count", 30)
        optimal_hashtags = config.get("hashtags_optimal_count", 10)
        
        hashtags = []
        
        # Convert keywords to hashtags
        for keyword in keywords.primary_keywords[:5]:
            hashtag = "#" + re.sub(r'\s+', '', keyword.lower())
            hashtags.append(hashtag)
        
        for keyword in keywords.secondary_keywords[:10]:
            hashtag = "#" + re.sub(r'\s+', '', keyword.lower())
            hashtags.append(hashtag)
        
        # Add trending hashtags
        for trend in keywords.trending_keywords[:5]:
            hashtag = "#" + re.sub(r'\s+', '', trend.lower())
            hashtags.append(hashtag)
        
        # Platform-specific popular hashtags
        platform_hashtags = {
            Platform.INSTAGRAM: ["#instagood", "#photooftheday", "#love", "#beautiful", "#happy"],
            Platform.TIKTOK: ["#fyp", "#foryou", "#viral", "#trending", "#tiktokmademebuyit"],
            Platform.TWITTER: ["#trending", "#viral", "#news", "#update"],
            Platform.LINKEDIN: ["#professional", "#career", "#business", "#networking", "#leadership"]
        }
        
        if platform in platform_hashtags:
            hashtags.extend(platform_hashtags[platform][:3])
        
        # Remove duplicates and clean
        hashtags = list(set([tag for tag in hashtags if tag.startswith('#')]))
        
        # Prioritize based on platform preferences
        if platform == Platform.TIKTOK:
            # Limit to optimal count for TikTok
            return hashtags[:optimal_hashtags]
        elif platform == Platform.INSTAGRAM:
            # Use optimal count for Instagram
            return hashtags[:optimal_hashtags]
        else:
            return hashtags[:max_hashtags]

    async def _generate_custom_fields(
        self,
        platform: Platform,
        content_type: ContentType,
        keywords: SEOKeywords,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate platform-specific custom fields"""
        
        custom_fields = {}
        
        if platform == Platform.YOUTUBE:
            custom_fields.update({
                "category": self._get_youtube_category(content_type),
                "thumbnail_suggestions": [
                    "High contrast with bright colors",
                    "Include text overlay with main keyword",
                    "Use emotional expressions or dramatic angles"
                ],
                "end_screen_elements": ["Subscribe button", "Related videos", "Playlist"],
                "chapters": self._generate_video_chapters(keywords)
            })
        
        elif platform == Platform.INSTAGRAM:
            custom_fields.update({
                "story_highlights": keywords.primary_keywords[:5],
                "bio_optimization": f"✨ {keywords.primary_keywords[0] if keywords.primary_keywords else 'Creator'} ✨",
                "posting_time": "6:00 PM - 9:00 PM",
                "carousel_suggestions": keywords.secondary_keywords[:10]
            })
        
        elif platform == Platform.TIKTOK:
            custom_fields.update({
                "sound_suggestions": ["trending audio", "original sound", "viral music"],
                "effects_recommendations": ["trending effects", "beauty filters", "AR filters"],
                "duet_opportunities": True,
                "posting_schedule": "7:00 PM - 10:00 PM"
            })
        
        elif platform == Platform.LINKEDIN:
            custom_fields.update({
                "article_format": True,
                "professional_tone": True,
                "industry_tags": keywords.primary_keywords[:3],
                "networking_opportunities": ["industry groups", "professional discussions"]
            })
        
        return custom_fields

    def _get_youtube_category(self, content_type: ContentType) -> str:
        """Get YouTube category for content type"""
        category_map = {
            ContentType.VIDEO: "Entertainment",
            ContentType.AUDIO: "Music",
            ContentType.TEXT: "Education",
            ContentType.PODCAST: "News & Politics",
            ContentType.LIVE_STREAM: "Gaming"
        }
        return category_map.get(content_type, "Entertainment")

    def _generate_video_chapters(self, keywords: SEOKeywords) -> List[Dict[str, str]]:
        """Generate video chapters based on keywords"""
        chapters = []
        if len(keywords.primary_keywords) >= 2:
            chapters = [
                {"time": "0:00", "title": "Introduction"},
                {"time": "1:00", "title": f"About {keywords.primary_keywords[0]}"},
                {"time": "3:00", "title": f"Deep Dive into {keywords.primary_keywords[1]}"},
                {"time": "7:00", "title": "Key Takeaways"},
                {"time": "9:00", "title": "Conclusion"}
            ]
        return chapters

    async def _analyze_seo_performance(
        self,
        content_data: Optional[str],
        keywords: SEOKeywords,
        platform_metadata: Dict[str, PlatformMetadata],
        options: Dict[str, Any]
    ) -> SEOAnalysis:
        """Analyze SEO performance"""
        
        seo_score = 0.0
        keyword_density = {}
        readability_score = 0.0
        recommendations = []
        optimization_opportunities = []
        
        # Calculate keyword density
        if content_data:
            content_lower = content_data.lower()
            total_words = len(content_data.split())
            
            for keyword in keywords.primary_keywords + keywords.secondary_keywords:
                keyword_count = content_lower.count(keyword.lower())
                density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                keyword_density[keyword] = density
        
        # Calculate readability score
        if content_data and self.nlp_available:
            try:
                readability_score = flesch_reading_ease(content_data)
            except:
                readability_score = 70.0  # Average readability
        else:
            readability_score = 70.0
        
        # Calculate overall SEO score
        factors = []
        
        # Keyword usage factor
        if keyword_density:
            avg_density = sum(keyword_density.values()) / len(keyword_density)
            keyword_factor = min(avg_density / 2.0, 1.0)  # Target 2% density
            factors.append(keyword_factor)
        else:
            factors.append(0.5)
        
        # Readability factor
        readability_factor = min(readability_score / 100, 1.0)
        factors.append(readability_factor)
        
        # Platform optimization factor
        platform_factor = len(platform_metadata) / 5  # Target 5 platforms
        factors.append(min(platform_factor, 1.0))
        
        # Trending factor
        trending_factor = len(keywords.trending_keywords) / 10  # Target 10 trending keywords
        factors.append(min(trending_factor, 1.0))
        
        seo_score = sum(factors) / len(factors)
        
        # Generate recommendations
        if seo_score < 0.7:
            recommendations.append("Increase keyword density in content")
        if readability_score < 60:
            recommendations.append("Improve content readability")
        if len(keywords.trending_keywords) < 5:
            recommendations.append("Include more trending keywords")
        if len(platform_metadata) < 3:
            recommendations.append("Optimize for more platforms")
        
        # Generate optimization opportunities
        if max(keyword_density.values()) if keyword_density else 0 < 1:
            optimization_opportunities.append("Primary keyword appears less than 1% of the time")
        if not any("?" in str(metadata.title) for metadata in platform_metadata.values()):
            optimization_opportunities.append("Consider adding questions in titles for engagement")
        
        # Content length analysis
        content_length_analysis = {
            "word_count": len(content_data.split()) if content_data else 0,
            "character_count": len(content_data) if content_data else 0,
            "optimal_length": True if content_data and 300 <= len(content_data.split()) <= 2000 else False,
            "length_recommendation": "Increase content length" if content_data and len(content_data.split()) < 300 else "Content length is optimal"
        }
        
        return SEOAnalysis(
            seo_score=seo_score,
            keyword_density=keyword_density,
            readability_score=readability_score,
            content_length_analysis=content_length_analysis,
            recommendations=recommendations,
            optimization_opportunities=optimization_opportunities
        )

    async def _predict_engagement(
        self,
        content_type: ContentType,
        creator_type: CreatorType,
        keywords: SEOKeywords,
        platform_metadata: Dict[str, PlatformMetadata],
        trending_analysis: TrendingAnalysis
    ) -> EngagementPrediction:
        """Predict content engagement"""
        
        # Base engagement rates by platform and content type
        base_rates = {
            Platform.TIKTOK: 0.055,
            Platform.INSTAGRAM: 0.018,
            Platform.YOUTUBE: 0.026,
            Platform.FACEBOOK: 0.014,
            Platform.TWITTER: 0.021,
            Platform.LINKEDIN: 0.033
        }
        
        # Calculate weighted engagement rate
        engagement_factors = {}
        total_weight = 0
        weighted_engagement = 0
        
        for platform_name, metadata in platform_metadata.items():
            platform = Platform(platform_name)
            base_rate = base_rates.get(platform, 0.02)
            
            # Adjust based on optimization factors
            optimization_multiplier = 1.0
            
            # Title optimization
            if len(metadata.hashtags) > 0:
                optimization_multiplier += 0.1
            
            # Trending alignment
            trending_alignment = trending_analysis.trend_alignment
            avg_trending = sum(trending_alignment.values()) / len(trending_alignment) if trending_alignment else 0.5
            optimization_multiplier += avg_trending * 0.2
            
            # Keyword optimization
            if len(metadata.tags) > 5:
                optimization_multiplier += 0.1
            
            adjusted_rate = base_rate * optimization_multiplier
            engagement_factors[platform.value] = {
                "base_rate": base_rate,
                "optimization_multiplier": optimization_multiplier,
                "adjusted_rate": adjusted_rate
            }
            
            weight = 1.0  # Equal weight for all platforms
            weighted_engagement += adjusted_rate * weight
            total_weight += weight
        
        predicted_engagement_rate = weighted_engagement / total_weight if total_weight > 0 else 0.02
        
        # Estimate reach and audience size
        creator_reach_multipliers = {
            CreatorType.INFLUENCER: 1.5,
            CreatorType.MUSICIAN: 1.3,
            CreatorType.COMEDIAN: 1.2,
            CreatorType.PHOTOGRAPHER: 1.1,
            CreatorType.BLOGGER: 1.0,
            CreatorType.EDUCATOR: 0.9,
            CreatorType.GAMER: 1.4,
            CreatorType.BUSINESS: 0.8
        }
        
        base_reach = 10000  # Base estimated reach
        reach_multiplier = creator_reach_multipliers.get(creator_type, 1.0)
        estimated_reach = int(base_reach * reach_multiplier * (1 + trending_analysis.viral_potential))
        
        target_audience_size = int(estimated_reach * 0.3)  # 30% of reach is target audience
        
        # Generate optimization suggestions
        optimization_suggestions = []
        
        if predicted_engagement_rate < 0.03:
            optimization_suggestions.append("Increase use of trending hashtags")
        if trending_analysis.viral_potential < 0.7:
            optimization_suggestions.append("Align content with current trends")
        if len(keywords.trending_keywords) < 5:
            optimization_suggestions.append("Include more trending keywords")
        
        optimization_suggestions.extend([
            "Post during peak engagement hours",
            "Use high-quality visuals",
            "Include clear call-to-action",
            "Engage with comments promptly"
        ])
        
        return EngagementPrediction(
            predicted_engagement_rate=predicted_engagement_rate,
            estimated_reach=estimated_reach,
            target_audience_size=target_audience_size,
            engagement_factors=engagement_factors,
            optimization_suggestions=optimization_suggestions[:5]
        )

    async def _generate_seo_recommendations(
        self,
        seo_analysis: SEOAnalysis,
        engagement_prediction: EngagementPrediction,
        trending_analysis: TrendingAnalysis,
        target_platforms: List[Platform]
    ) -> List[str]:
        """Generate comprehensive SEO recommendations"""
        
        recommendations = []
        
        # SEO Score based recommendations
        if seo_analysis.seo_score < 0.8:
            recommendations.append("Overall SEO score needs improvement - focus on keyword optimization")
        
        # Keyword density recommendations
        low_density_keywords = [kw for kw, density in seo_analysis.keyword_density.items() if density < 0.5]
        if low_density_keywords:
            recommendations.append(f"Increase usage of keywords: {', '.join(low_density_keywords[:3])}")
        
        # Readability recommendations
        if seo_analysis.readability_score < 60:
            recommendations.append("Improve content readability - use shorter sentences and simpler words")
        elif seo_analysis.readability_score > 90:
            recommendations.append("Content might be too simple - consider adding more depth")
        
        # Engagement recommendations
        if engagement_prediction.predicted_engagement_rate < 0.025:
            recommendations.append("Low predicted engagement - consider adding more visual elements and trending content")
        
        # Trending recommendations
        if trending_analysis.viral_potential < 0.6:
            recommendations.append("Increase viral potential by aligning with current trends and seasonal topics")
        
        # Platform-specific recommendations
        platform_recommendations = {
            Platform.YOUTUBE: "Optimize video title and thumbnail for higher click-through rates",
            Platform.INSTAGRAM: "Use optimal number of hashtags (11) and post during peak hours",
            Platform.TIKTOK: "Leverage trending sounds and effects for better reach",
            Platform.LINKEDIN: "Maintain professional tone and engage with industry discussions"
        }
        
        for platform in target_platforms:
            if platform in platform_recommendations:
                recommendations.append(platform_recommendations[platform])
        
        # Content length recommendations
        if not seo_analysis.content_length_analysis.get("optimal_length", True):
            recommendations.append(seo_analysis.content_length_analysis.get("length_recommendation", "Optimize content length"))
        
        # Competitive recommendations
        if trending_analysis.competitive_analysis.get("content_saturation", 0) > 0.7:
            recommendations.append("High content saturation - focus on unique angle or niche keywords")
        
        return recommendations[:10]  # Limit to top 10 recommendations

    async def get_platform_best_practices(self, platform: Platform) -> Dict[str, Any]:
        """Get best practices for specific platform"""
        
        best_practices = {
            Platform.YOUTUBE: {
                "title": "Include primary keyword at the beginning",
                "description": "Use first 125 characters effectively",
                "tags": "Use mix of broad and specific tags",
                "thumbnail": "High contrast, bright colors, text overlay",
                "posting_time": "2 PM - 4 PM EST weekdays",
                "engagement": "Respond to comments within first hour"
            },
            Platform.INSTAGRAM: {
                "caption": "Front-load important information",
                "hashtags": "Use 11 hashtags for optimal reach",
                "posting_time": "11 AM - 1 PM and 7 PM - 9 PM",
                "stories": "Use interactive elements like polls",
                "engagement": "Use location tags and tag relevant accounts"
            },
            Platform.TIKTOK: {
                "caption": "Keep under 100 characters for mobile view",
                "hashtags": "Use 3-5 hashtags including trending ones",
                "posting_time": "6 AM - 10 AM and 7 PM - 9 PM",
                "content": "Hook viewers in first 3 seconds",
                "engagement": "Participate in trending challenges"
            }
        }
        
        return best_practices.get(platform, {})


# Global SEO processor instance
_seo_processor_instance = None


def get_seo_processor() -> SEOMetadataProcessor:
    """Get the global SEO processor instance"""
    global _seo_processor_instance
    if _seo_processor_instance is None:
        _seo_processor_instance = SEOMetadataProcessor()
    return _seo_processor_instance