"""SEO Optimization Engine Module - Advanced Content SEO & Discoverability System

Enterprise-grade SEO optimization system implementing AI-powered content optimization,
multi-platform SEO strategies, and automated discoverability enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import re
from collections import Counter
import nltk
from textblob import TextBlob
import requests

from ...core.database import get_db_session
from ...core.exceptions import BusinessLogicError, ValidationError
from ...utils.cache_manager import CacheManager
from ...utils.event_emitter import EventEmitter
from ...ai.content_generation.text_processor import TextProcessor
from ...ai.content_generation.keyword_extractor import KeywordExtractor
from ...ai.content_generation.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)


class SEOStrategy(Enum):
    """SEO optimization strategies"""
    ORGANIC_GROWTH = "organic_growth"
    VIRAL_OPTIMIZATION = "viral_optimization"
    NICHE_TARGETING = "niche_targeting"
    MASS_APPEAL = "mass_appeal"
    TRENDING_KEYWORDS = "trending_keywords"
    LONG_TAIL_FOCUS = "long_tail_focus"
    BRAND_BUILDING = "brand_building"


class PlatformType(Enum):
    """Platform types for SEO optimization"""
    SEARCH_ENGINE = "search_engine"  # Google, Bing, etc.
    SOCIAL_MEDIA = "social_media"    # Instagram, TikTok, etc.
    VIDEO_PLATFORM = "video_platform"  # YouTube, Vimeo, etc.
    AUDIO_PLATFORM = "audio_platform"  # Spotify, Apple Music, etc.
    PROFESSIONAL = "professional"    # LinkedIn, etc.
    MARKETPLACE = "marketplace"      # Etsy, Amazon, etc.


class OptimizationLevel(Enum):
    """SEO optimization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class KeywordProfile:
    """Keyword optimization profile"""
    profile_id: str
    content_id: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    trending_keywords: List[str]
    keyword_density: Dict[str, float]
    search_volume: Dict[str, int]
    competition_score: Dict[str, float]
    relevance_score: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SEOMetadata:
    """SEO metadata structure"""
    metadata_id: str
    content_id: str
    optimized_title: str
    optimized_description: str
    meta_keywords: List[str]
    hashtags: List[str]
    og_tags: Dict[str, str]  # Open Graph tags
    twitter_tags: Dict[str, str]  # Twitter Card tags
    schema_markup: Dict[str, Any]  # Structured data
    canonical_url: Optional[str]
    alt_text: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformOptimization:
    """Platform-specific optimization"""
    optimization_id: str
    content_id: str
    platform_name: str
    platform_type: PlatformType
    optimized_content: Dict[str, Any]
    platform_keywords: List[str]
    posting_strategy: Dict[str, Any]
    engagement_optimization: Dict[str, Any]
    algorithm_factors: Dict[str, Any]
    performance_predictions: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SEOPerformance:
    """SEO performance metrics"""
    performance_id: str
    content_id: str
    platform: str
    discoverability_score: float
    keyword_rankings: Dict[str, int]
    search_visibility: float
    engagement_metrics: Dict[str, float]
    traffic_sources: Dict[str, int]
    conversion_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    measured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendingTopics:
    """Trending topics data"""
    topic_id: str
    platform: str
    trending_keywords: List[str]
    trending_hashtags: List[str]
    popularity_score: float
    trend_momentum: str  # rising, stable, declining
    related_topics: List[str]
    audience_demographics: Dict[str, Any]
    optimal_timing: Dict[str, Any]
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)


class SEOOptimizationEngine:
    """
    Enterprise-grade SEO optimization engine for multi-platform content optimization
    and discoverability enhancement in the creator economy workflow.
    """
    
    def __init__(self, cache_manager: CacheManager, event_emitter: EventEmitter):
        self.cache_manager = cache_manager
        self.event_emitter = event_emitter
        self.text_processor = TextProcessor()
        self.keyword_extractor = KeywordExtractor()
        self.trend_analyzer = TrendAnalyzer()
        self.platform_configs = self._initialize_platform_configs()
        self.seo_templates = self._initialize_seo_templates()
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific SEO configurations"""
        return {
            "youtube": {
                "platform_type": PlatformType.VIDEO_PLATFORM,
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 15,
                "optimal_keywords": 5,
                "algorithm_factors": ["watch_time", "engagement", "click_through_rate", "retention"],
                "posting_times": ["14:00-16:00", "19:00-21:00"],
                "hashtag_format": "#tag"
            },
            "instagram": {
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "title_max_length": 125,
                "description_max_length": 2200,
                "tags_max_count": 30,
                "optimal_keywords": 8,
                "algorithm_factors": ["engagement", "saves", "shares", "comments"],
                "posting_times": ["11:00-13:00", "17:00-19:00"],
                "hashtag_format": "#tag"
            },
            "tiktok": {
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "title_max_length": 80,
                "description_max_length": 2200,
                "tags_max_count": 20,
                "optimal_keywords": 6,
                "algorithm_factors": ["completion_rate", "shares", "engagement", "trending_sounds"],
                "posting_times": ["06:00-10:00", "19:00-23:00"],
                "hashtag_format": "#tag"
            },
            "spotify": {
                "platform_type": PlatformType.AUDIO_PLATFORM,
                "title_max_length": 50,
                "description_max_length": 1000,
                "tags_max_count": 10,
                "optimal_keywords": 4,
                "algorithm_factors": ["completion_rate", "saves", "playlist_adds", "skip_rate"],
                "posting_times": ["12:00-15:00", "20:00-22:00"],
                "hashtag_format": "#tag"
            },
            "linkedin": {
                "platform_type": PlatformType.PROFESSIONAL,
                "title_max_length": 70,
                "description_max_length": 1300,
                "tags_max_count": 5,
                "optimal_keywords": 3,
                "algorithm_factors": ["engagement", "shares", "professional_relevance"],
                "posting_times": ["08:00-10:00", "17:00-18:00"],
                "hashtag_format": "#tag"
            },
            "twitter": {
                "platform_type": PlatformType.SOCIAL_MEDIA,
                "title_max_length": 70,
                "description_max_length": 280,
                "tags_max_count": 10,
                "optimal_keywords": 4,
                "algorithm_factors": ["engagement", "retweets", "replies", "trending_topics"],
                "posting_times": ["09:00-10:00", "12:00-15:00"],
                "hashtag_format": "#tag"
            }
        }
    
    def _initialize_seo_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize SEO templates for different content types"""
        return {
            "audio": {
                "title_template": "{artist} - {title} | {genre} Music",
                "description_template": "🎵 {title} by {artist}\n\n{description}\n\n🎼 Genre: {genre}\n🔥 Tags: {tags}\n\n#music #{genre} #artist",
                "keywords_template": "{artist}, {title}, {genre}, music, song, audio"
            },
            "video": {
                "title_template": "{title} | {category} Content by {creator}",
                "description_template": "🎬 {title}\n\n{description}\n\n📹 Category: {category}\n🔥 Tags: {tags}\n\nSubscribe for more {category} content!",
                "keywords_template": "{title}, {category}, {creator}, video, content"
            },
            "image": {
                "title_template": "{title} | {style} by {artist}",
                "description_template": "🎨 {title}\n\n{description}\n\n🖼️ Style: {style}\n🔥 Tags: {tags}\n\n#art #{style} #photography",
                "keywords_template": "{title}, {style}, {artist}, art, image, photography"
            },
            "text": {
                "title_template": "{title} | {category} Content",
                "description_template": "📝 {title}\n\n{description}\n\n📚 Category: {category}\n🔥 Tags: {tags}",
                "keywords_template": "{title}, {category}, content, article, text"
            }
        }
    
    async def optimize_content_seo(
        self,
        content_id: str,
        user_id: str,
        content_data: Dict[str, Any],
        target_platforms: List[str],
        seo_strategy: SEOStrategy = SEOStrategy.ORGANIC_GROWTH,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Comprehensive SEO optimization for content across multiple platforms
        
        Business Logic Integration:
        Content Upload → AI Processing → Protection → SEO OPTIMIZATION → Distribution
        """
        try:
            # Step 1: Analyze content and extract base keywords
            keyword_analysis = await self._analyze_content_keywords(content_data, seo_strategy)
            
            # Step 2: Research trending topics and keywords
            trending_analysis = await self._analyze_trending_topics(target_platforms, content_data)
            
            # Step 3: Generate comprehensive keyword profile
            keyword_profile = await self._generate_keyword_profile(
                content_id, keyword_analysis, trending_analysis
            )
            
            # Step 4: Create optimized metadata
            seo_metadata = await self._create_seo_metadata(
                content_id, content_data, keyword_profile, optimization_level
            )
            
            # Step 5: Platform-specific optimizations
            platform_optimizations = await self._create_platform_optimizations(
                content_id, content_data, keyword_profile, target_platforms
            )
            
            # Step 6: Generate SEO performance predictions
            performance_predictions = await self._predict_seo_performance(
                content_data, keyword_profile, platform_optimizations
            )
            
            # Step 7: Create discoverability enhancement strategies
            discoverability_strategies = await self._create_discoverability_strategies(
                content_data, keyword_profile, trending_analysis
            )
            
            # Store SEO optimization results
            await self._store_seo_optimization_results(
                content_id, seo_metadata, platform_optimizations, keyword_profile
            )
            
            # Emit SEO optimization completed event
            await self.event_emitter.emit("seo_optimization_completed", {
                "content_id": content_id,
                "user_id": user_id,
                "target_platforms": target_platforms,
                "seo_strategy": seo_strategy.value,
                "optimization_results": {
                    "keyword_profile": keyword_profile,
                    "seo_metadata": seo_metadata,
                    "platform_optimizations": platform_optimizations,
                    "performance_predictions": performance_predictions
                }
            })
            
            return {
                "seo_optimized": True,
                "content_id": content_id,
                "optimization_level": optimization_level.value,
                "seo_strategy": seo_strategy.value,
                "optimization_components": {
                    "keyword_analysis": keyword_analysis,
                    "trending_analysis": trending_analysis,
                    "keyword_profile": keyword_profile,
                    "seo_metadata": seo_metadata,
                    "platform_optimizations": platform_optimizations,
                    "performance_predictions": performance_predictions,
                    "discoverability_strategies": discoverability_strategies
                },
                "discoverability_score": self._calculate_discoverability_score(
                    keyword_profile, seo_metadata, platform_optimizations
                ),
                "next_stage": "collaboration_matching"
            }
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {str(e)}")
            await self.event_emitter.emit("seo_optimization_failed", {
                "content_id": content_id,
                "user_id": user_id,
                "error": str(e)
            })
            raise BusinessLogicError(f"SEO optimization failed: {str(e)}")
    
    async def _analyze_content_keywords(
        self,
        content_data: Dict[str, Any],
        seo_strategy: SEOStrategy
    ) -> Dict[str, Any]:
        """Analyze content to extract and optimize keywords"""
        try:
            # Extract text content for analysis
            text_content = await self._extract_text_content(content_data)
            
            # Extract keywords using AI
            keyword_extraction = await self.keyword_extractor.extract_keywords(
                text_content, strategy=seo_strategy.value
            )
            
            # Analyze keyword relevance and competition
            keyword_analysis = await self._analyze_keyword_competition(
                keyword_extraction["keywords"]
            )
            
            # Generate semantic keywords
            semantic_keywords = await self._generate_semantic_keywords(
                keyword_extraction["keywords"], text_content
            )
            
            return {
                "primary_keywords": keyword_extraction["primary_keywords"],
                "secondary_keywords": keyword_extraction["secondary_keywords"],
                "semantic_keywords": semantic_keywords,
                "keyword_density": keyword_extraction["density"],
                "keyword_analysis": keyword_analysis,
                "content_themes": keyword_extraction.get("themes", []),
                "readability_score": keyword_extraction.get("readability", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {str(e)}")
            return {
                "primary_keywords": [],
                "secondary_keywords": [],
                "error": str(e)
            }
    
    async def _analyze_trending_topics(
        self,
        target_platforms: List[str],
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze trending topics across target platforms"""
        try:
            trending_data = {}
            
            for platform in target_platforms:
                platform_trends = await self.trend_analyzer.get_platform_trends(
                    platform, content_data.get("content_format", "general")
                )
                trending_data[platform] = platform_trends
            
            # Consolidate trending topics
            consolidated_trends = await self._consolidate_trending_topics(trending_data)
            
            # Find content-relevant trends
            relevant_trends = await self._find_relevant_trends(
                consolidated_trends, content_data
            )
            
            return {
                "platform_trends": trending_data,
                "consolidated_trends": consolidated_trends,
                "relevant_trends": relevant_trends,
                "trending_keywords": relevant_trends.get("keywords", []),
                "trending_hashtags": relevant_trends.get("hashtags", []),
                "trend_momentum": relevant_trends.get("momentum", "stable")
            }
            
        except Exception as e:
            logger.error(f"Trending analysis failed: {str(e)}")
            return {
                "platform_trends": {},
                "trending_keywords": [],
                "error": str(e)
            }
    
    async def _generate_keyword_profile(
        self,
        content_id: str,
        keyword_analysis: Dict[str, Any],
        trending_analysis: Dict[str, Any]
    ) -> KeywordProfile:
        """Generate comprehensive keyword profile"""
        try:
            # Combine analyzed keywords with trending keywords
            primary_keywords = keyword_analysis.get("primary_keywords", [])
            secondary_keywords = keyword_analysis.get("secondary_keywords", [])
            trending_keywords = trending_analysis.get("trending_keywords", [])
            
            # Generate long-tail keywords
            long_tail_keywords = await self._generate_long_tail_keywords(
                primary_keywords, secondary_keywords
            )
            
            # Calculate keyword metrics
            all_keywords = primary_keywords + secondary_keywords + trending_keywords
            keyword_density = await self._calculate_keyword_density(all_keywords, keyword_analysis)
            search_volume = await self._get_search_volumes(all_keywords)
            competition_score = await self._calculate_competition_scores(all_keywords)
            relevance_score = await self._calculate_relevance_scores(all_keywords, keyword_analysis)
            
            return KeywordProfile(
                profile_id=str(uuid.uuid4()),
                content_id=content_id,
                primary_keywords=primary_keywords[:5],  # Top 5 primary
                secondary_keywords=secondary_keywords[:10],  # Top 10 secondary
                long_tail_keywords=long_tail_keywords[:8],  # Top 8 long-tail
                trending_keywords=trending_keywords[:6],  # Top 6 trending
                keyword_density=keyword_density,
                search_volume=search_volume,
                competition_score=competition_score,
                relevance_score=relevance_score
            )
            
        except Exception as e:
            logger.error(f"Keyword profile generation failed: {str(e)}")
            return KeywordProfile(
                profile_id=str(uuid.uuid4()),
                content_id=content_id,
                primary_keywords=[],
                secondary_keywords=[],
                long_tail_keywords=[],
                trending_keywords=[],
                keyword_density={},
                search_volume={},
                competition_score={},
                relevance_score={}
            )
    
    async def _create_seo_metadata(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        keyword_profile: KeywordProfile,
        optimization_level: OptimizationLevel
    ) -> SEOMetadata:
        """Create comprehensive SEO metadata"""
        try:
            content_format = content_data.get("content_format", "text")
            template = self.seo_templates.get(content_format, self.seo_templates["text"])
            
            # Generate optimized title
            optimized_title = await self._generate_optimized_title(
                content_data, keyword_profile, template
            )
            
            # Generate optimized description
            optimized_description = await self._generate_optimized_description(
                content_data, keyword_profile, template
            )
            
            # Generate meta keywords
            meta_keywords = (
                keyword_profile.primary_keywords + 
                keyword_profile.secondary_keywords[:5] + 
                keyword_profile.trending_keywords[:3]
            )
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(keyword_profile, content_data)
            
            # Generate Open Graph tags
            og_tags = await self._generate_og_tags(
                optimized_title, optimized_description, content_data
            )
            
            # Generate Twitter Card tags
            twitter_tags = await self._generate_twitter_tags(
                optimized_title, optimized_description, content_data
            )
            
            # Generate schema markup
            schema_markup = await self._generate_schema_markup(
                content_data, keyword_profile, optimization_level
            )
            
            return SEOMetadata(
                metadata_id=str(uuid.uuid4()),
                content_id=content_id,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                meta_keywords=meta_keywords,
                hashtags=hashtags,
                og_tags=og_tags,
                twitter_tags=twitter_tags,
                schema_markup=schema_markup,
                canonical_url=content_data.get("canonical_url"),
                alt_text=content_data.get("alt_text")
            )
            
        except Exception as e:
            logger.error(f"SEO metadata creation failed: {str(e)}")
            return SEOMetadata(
                metadata_id=str(uuid.uuid4()),
                content_id=content_id,
                optimized_title=content_data.get("title", "Untitled"),
                optimized_description=content_data.get("description", ""),
                meta_keywords=[],
                hashtags=[],
                og_tags={},
                twitter_tags={},
                schema_markup={}
            )
    
    async def _create_platform_optimizations(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        keyword_profile: KeywordProfile,
        target_platforms: List[str]
    ) -> List[PlatformOptimization]:
        """Create platform-specific optimizations"""
        optimizations = []
        
        for platform in target_platforms:
            try:
                platform_config = self.platform_configs.get(platform)
                if not platform_config:
                    logger.warning(f"Platform config not found for {platform}")
                    continue
                
                # Generate platform-specific content
                optimized_content = await self._optimize_for_platform(
                    content_data, keyword_profile, platform_config
                )
                
                # Generate platform-specific keywords
                platform_keywords = await self._select_platform_keywords(
                    keyword_profile, platform_config
                )
                
                # Generate posting strategy
                posting_strategy = await self._generate_posting_strategy(
                    platform_config, content_data
                )
                
                # Generate engagement optimization
                engagement_optimization = await self._generate_engagement_optimization(
                    platform_config, keyword_profile
                )
                
                # Analyze algorithm factors
                algorithm_factors = await self._analyze_algorithm_factors(
                    platform_config, content_data, keyword_profile
                )
                
                # Predict performance
                performance_predictions = await self._predict_platform_performance(
                    platform, optimized_content, keyword_profile
                )
                
                optimization = PlatformOptimization(
                    optimization_id=str(uuid.uuid4()),
                    content_id=content_id,
                    platform_name=platform,
                    platform_type=platform_config["platform_type"],
                    optimized_content=optimized_content,
                    platform_keywords=platform_keywords,
                    posting_strategy=posting_strategy,
                    engagement_optimization=engagement_optimization,
                    algorithm_factors=algorithm_factors,
                    performance_predictions=performance_predictions
                )
                
                optimizations.append(optimization)
                
            except Exception as e:
                logger.error(f"Platform optimization failed for {platform}: {str(e)}")
                continue
        
        return optimizations
    
    async def _predict_seo_performance(
        self,
        content_data: Dict[str, Any],
        keyword_profile: KeywordProfile,
        platform_optimizations: List[PlatformOptimization]
    ) -> Dict[str, Any]:
        """Predict SEO performance across platforms"""
        try:
            predictions = {}
            
            for optimization in platform_optimizations:
                platform_prediction = await self._predict_single_platform_performance(
                    optimization, keyword_profile, content_data
                )
                predictions[optimization.platform_name] = platform_prediction
            
            # Calculate overall predictions
            overall_prediction = await self._calculate_overall_performance_prediction(
                predictions, keyword_profile
            )
            
            return {
                "platform_predictions": predictions,
                "overall_prediction": overall_prediction,
                "discoverability_factors": {
                    "keyword_strength": self._calculate_keyword_strength(keyword_profile),
                    "trending_alignment": self._calculate_trending_alignment(keyword_profile),
                    "competition_advantage": self._calculate_competition_advantage(keyword_profile),
                    "content_quality": content_data.get("quality_score", 0.5)
                },
                "improvement_recommendations": await self._generate_improvement_recommendations(
                    keyword_profile, platform_optimizations
                )
            }
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {str(e)}")
            return {
                "platform_predictions": {},
                "overall_prediction": {"discoverability_score": 0.5},
                "error": str(e)
            }
    
    async def _create_discoverability_strategies(
        self,
        content_data: Dict[str, Any],
        keyword_profile: KeywordProfile,
        trending_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create strategies to enhance content discoverability"""
        try:
            strategies = {
                "content_timing": await self._optimize_content_timing(trending_analysis),
                "cross_platform_strategy": await self._create_cross_platform_strategy(
                    keyword_profile, trending_analysis
                ),
                "engagement_tactics": await self._generate_engagement_tactics(
                    keyword_profile, content_data
                ),
                "viral_potential": await self._assess_viral_potential(
                    content_data, keyword_profile, trending_analysis
                ),
                "niche_targeting": await self._create_niche_targeting_strategy(
                    keyword_profile, content_data
                ),
                "collaboration_opportunities": await self._identify_collaboration_keywords(
                    keyword_profile, trending_analysis
                )
            }
            
            return strategies
            
        except Exception as e:
            logger.error(f"Discoverability strategy creation failed: {str(e)}")
            return {
                "content_timing": {},
                "cross_platform_strategy": {},
                "error": str(e)
            }
    
    def _calculate_discoverability_score(
        self,
        keyword_profile: KeywordProfile,
        seo_metadata: SEOMetadata,
        platform_optimizations: List[PlatformOptimization]
    ) -> float:
        """Calculate overall discoverability score"""
        try:
            scores = []
            
            # Keyword quality score (30%)
            keyword_score = (
                len(keyword_profile.primary_keywords) * 0.4 +
                len(keyword_profile.secondary_keywords) * 0.3 +
                len(keyword_profile.trending_keywords) * 0.3
            ) / 15  # Normalize to 0-1
            scores.append(keyword_score * 0.3)
            
            # Metadata completeness score (25%)
            metadata_score = (
                (1 if seo_metadata.optimized_title else 0) +
                (1 if seo_metadata.optimized_description else 0) +
                (1 if seo_metadata.meta_keywords else 0) +
                (1 if seo_metadata.hashtags else 0) +
                (1 if seo_metadata.og_tags else 0)
            ) / 5
            scores.append(metadata_score * 0.25)
            
            # Platform optimization score (25%)
            platform_score = len(platform_optimizations) / 6  # Normalize for 6 platforms
            scores.append(min(platform_score, 1.0) * 0.25)
            
            # Trending alignment score (20%)
            trending_score = len(keyword_profile.trending_keywords) / 6
            scores.append(min(trending_score, 1.0) * 0.2)
            
            return min(sum(scores), 1.0)
            
        except Exception as e:
            logger.error(f"Discoverability score calculation failed: {str(e)}")
            return 0.5
    
    async def monitor_seo_performance(
        self,
        content_id: str,
        platforms: List[str]
    ) -> Dict[str, SEOPerformance]:
        """Monitor SEO performance across platforms"""
        try:
            performance_data = {}
            
            for platform in platforms:
                try:
                    # Get platform-specific performance metrics
                    platform_metrics = await self._get_platform_performance_metrics(
                        content_id, platform
                    )
                    
                    # Calculate performance scores
                    performance = SEOPerformance(
                        performance_id=str(uuid.uuid4()),
                        content_id=content_id,
                        platform=platform,
                        discoverability_score=platform_metrics.get("discoverability_score", 0.0),
                        keyword_rankings=platform_metrics.get("keyword_rankings", {}),
                        search_visibility=platform_metrics.get("search_visibility", 0.0),
                        engagement_metrics=platform_metrics.get("engagement_metrics", {}),
                        traffic_sources=platform_metrics.get("traffic_sources", {}),
                        conversion_metrics=platform_metrics.get("conversion_metrics", {}),
                        improvement_suggestions=platform_metrics.get("improvement_suggestions", [])
                    )
                    
                    performance_data[platform] = performance
                    
                except Exception as platform_error:
                    logger.error(f"Performance monitoring failed for {platform}: {platform_error}")
                    continue
            
            return performance_data
            
        except Exception as e:
            logger.error(f"SEO performance monitoring failed: {str(e)}")
            return {}
    
    # Helper methods (implementation details)
    async def _extract_text_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content from various content formats"""
        # Implementation for text extraction
        return content_data.get("description", "") + " " + content_data.get("title", "")
    
    async def _analyze_keyword_competition(self, keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword competition levels"""
        # Implementation for keyword competition analysis
        return {"competition_level": "medium", "difficulty_scores": {}}
    
    async def _generate_semantic_keywords(self, keywords: List[str], text_content: str) -> List[str]:
        """Generate semantic keywords using NLP"""
        # Implementation for semantic keyword generation
        return []
    
    async def _consolidate_trending_topics(self, trending_data: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate trending topics across platforms"""
        # Implementation for trending topics consolidation
        return {"keywords": [], "hashtags": []}
    
    async def _find_relevant_trends(
        self, 
        consolidated_trends: Dict[str, Any], 
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find trends relevant to content"""
        # Implementation for relevant trend identification
        return {"keywords": [], "hashtags": [], "momentum": "stable"}
    
    # Additional helper methods would be implemented here...


# Factory function for creating SEO optimization engine
def create_seo_optimization_engine(
    cache_manager: CacheManager,
    event_emitter: EventEmitter
) -> SEOOptimizationEngine:
    """Factory function to create SEO optimization engine instance"""
    return SEOOptimizationEngine(cache_manager, event_emitter)
