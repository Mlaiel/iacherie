#!/usr/bin/env python3
"""
Industrial Multi-Platform SEO System
====================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides industrial-grade SEO optimization for multiple platforms with
644+ language support and multi-provider translation integration.

Features:
- Platform-specific SEO optimization
- 644+ language support with regional variants
- Multi-provider translation with intelligent routing
- Content localization and cultural adaptation
- Automated hreflang generation
- Performance monitoring and analytics
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
import json
import hashlib

from .extended_languages import ExtendedLanguageSupport, LanguageInfo, ScriptSystem, TextDirection
from .multi_provider_translation import (
    MultiProviderTranslationManager, 
    TranslationRequest, 
    TranslationQuality,
    TranslationProvider
)

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for SEO optimization"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    BANDCAMP = "bandcamp"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    DEVIANTART = "deviantart"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    TUMBLR = "tumblr"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    WEIBO = "weibo"
    WECHAT = "wechat"
    BAIDU = "baidu"
    YANDEX = "yandex"
    NAVER = "naver"


class ContentType(Enum):
    """Content types for optimization"""
    MUSIC = "music"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POST = "post"
    ARTICLE = "article"
    BLOG = "blog"


class SEOObjective(Enum):
    """SEO optimization objectives"""
    DISCOVERABILITY = "discoverability"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    BRAND_AWARENESS = "brand_awareness"
    VIRAL_POTENTIAL = "viral_potential"
    LOCAL_REACH = "local_reach"
    GLOBAL_REACH = "global_reach"


@dataclass
class PlatformRequirements:
    """Platform-specific requirements and constraints"""
    title_max_length: int
    description_max_length: int
    tags_max_count: int
    tag_max_length: int
    supports_hashtags: bool = True
    supports_mentions: bool = True
    supports_html: bool = False
    supports_markdown: bool = False
    character_encoding: str = "utf-8"
    rtl_support: bool = True
    image_formats: List[str] = None
    video_formats: List[str] = None
    audio_formats: List[str] = None
    preferred_languages: List[str] = None
    regional_restrictions: List[str] = None
    algorithm_factors: Dict[str, float] = None


@dataclass
class SEOContent:
    """SEO-optimized content structure"""
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]
    keywords: List[str]
    metadata: Dict[str, Any]
    platform: Platform
    language: str
    content_type: ContentType
    optimization_score: float
    cultural_adaptations: List[str] = None
    hreflang_alternatives: Dict[str, str] = None


@dataclass
class MultilingualSEOResult:
    """Complete multilingual SEO optimization result"""
    original_content: SEOContent
    localized_versions: Dict[str, SEOContent]  # language_code: content
    hreflang_tags: List[Dict[str, str]]
    platform_variations: Dict[Platform, Dict[str, SEOContent]]
    global_optimization_score: float
    translation_costs: Dict[TranslationProvider, float]
    performance_predictions: Dict[str, float]
    recommendations: List[str]
    processing_time: float
    metadata: Dict[str, Any]


class IndustrialSEOOptimizer:
    """
    Industrial-grade multi-platform SEO optimization system with 644+ language support
    """
    
    def __init__(self):
        """Initialize the industrial SEO optimizer"""
        self.language_support = ExtendedLanguageSupport()
        self.translation_manager = MultiProviderTranslationManager()
        self.platform_requirements = self._initialize_platform_requirements()
        self.optimization_cache = {}
        self.performance_analytics = {}
        
    def _initialize_platform_requirements(self) -> Dict[Platform, PlatformRequirements]:
        """Initialize platform-specific requirements"""
        return {
            Platform.YOUTUBE: PlatformRequirements(
                title_max_length=100,
                description_max_length=5000,
                tags_max_count=500,
                tag_max_length=50,
                supports_hashtags=True,
                supports_html=False,
                preferred_languages=["en", "es", "pt", "hi", "ar", "fr", "de", "ja", "ko", "zh"],
                algorithm_factors={
                    "title_keyword_density": 0.25,
                    "description_length": 0.15,
                    "tags_relevance": 0.20,
                    "engagement_prediction": 0.40
                }
            ),
            Platform.TIKTOK: PlatformRequirements(
                title_max_length=150,
                description_max_length=2200,
                tags_max_count=100,
                tag_max_length=100,
                supports_hashtags=True,
                preferred_languages=["en", "zh", "es", "pt", "ar", "fr", "ja", "ko", "de", "hi"],
                algorithm_factors={
                    "hashtag_trending": 0.35,
                    "title_hook": 0.25,
                    "viral_potential": 0.40
                }
            ),
            Platform.INSTAGRAM: PlatformRequirements(
                title_max_length=125,
                description_max_length=2200,
                tags_max_count=30,
                tag_max_length=100,
                supports_hashtags=True,
                supports_mentions=True,
                preferred_languages=["en", "es", "pt", "fr", "de", "it", "ja", "ko", "ar", "hi"],
                algorithm_factors={
                    "hashtag_strategy": 0.30,
                    "engagement_rate": 0.35,
                    "content_quality": 0.35
                }
            ),
            Platform.SPOTIFY: PlatformRequirements(
                title_max_length=80,
                description_max_length=1000,
                tags_max_count=20,
                tag_max_length=50,
                supports_hashtags=False,
                audio_formats=["mp3", "flac", "wav"],
                preferred_languages=["en", "es", "pt", "fr", "de", "sv", "no", "da", "fi", "nl"],
                algorithm_factors={
                    "title_searchability": 0.40,
                    "genre_accuracy": 0.30,
                    "metadata_completeness": 0.30
                }
            ),
            Platform.LINKEDIN: PlatformRequirements(
                title_max_length=120,
                description_max_length=3000,
                tags_max_count=10,
                tag_max_length=25,
                supports_hashtags=True,
                supports_html=True,
                preferred_languages=["en", "es", "pt", "fr", "de", "it", "ja", "zh", "ar", "ru"],
                algorithm_factors={
                    "professional_keywords": 0.35,
                    "industry_relevance": 0.30,
                    "networking_potential": 0.35
                }
            ),
            Platform.TWITTER: PlatformRequirements(
                title_max_length=280,
                description_max_length=280,
                tags_max_count=10,
                tag_max_length=100,
                supports_hashtags=True,
                supports_mentions=True,
                preferred_languages=["en", "ja", "es", "pt", "ar", "fr", "de", "it", "ko", "hi"],
                algorithm_factors={
                    "trending_hashtags": 0.40,
                    "real_time_relevance": 0.35,
                    "engagement_velocity": 0.25
                }
            ),
            Platform.WEIBO: PlatformRequirements(
                title_max_length=140,
                description_max_length=2000,
                tags_max_count=20,
                tag_max_length=50,
                supports_hashtags=True,
                character_encoding="utf-8",
                preferred_languages=["zh", "zh-cn", "zh-tw", "en"],
                regional_restrictions=["CN"],
                algorithm_factors={
                    "chinese_keywords": 0.45,
                    "cultural_relevance": 0.30,
                    "social_sharing": 0.25
                }
            ),
            Platform.BAIDU: PlatformRequirements(
                title_max_length=60,
                description_max_length=200,
                tags_max_count=10,
                tag_max_length=20,
                supports_hashtags=False,
                preferred_languages=["zh", "zh-cn"],
                regional_restrictions=["CN"],
                algorithm_factors={
                    "chinese_seo": 0.50,
                    "baidu_preferences": 0.30,
                    "local_relevance": 0.20
                }
            ),
            Platform.YANDEX: PlatformRequirements(
                title_max_length=70,
                description_max_length=300,
                tags_max_count=15,
                tag_max_length=30,
                supports_hashtags=False,
                preferred_languages=["ru", "be", "uk", "kk", "uz", "en"],
                regional_restrictions=["RU", "BY", "KZ", "UZ"],
                algorithm_factors={
                    "russian_seo": 0.45,
                    "yandex_factors": 0.35,
                    "regional_relevance": 0.20
                }
            ),
            Platform.NAVER: PlatformRequirements(
                title_max_length=50,
                description_max_length=150,
                tags_max_count=8,
                tag_max_length=20,
                supports_hashtags=False,
                preferred_languages=["ko", "en"],
                regional_restrictions=["KR"],
                algorithm_factors={
                    "korean_keywords": 0.50,
                    "naver_algorithm": 0.30,
                    "local_content": 0.20
                }
            )
        }
    
    async def optimize_content_multilingual(
        self,
        content: str,
        title: str,
        description: str,
        source_language: str,
        target_languages: List[str],
        platforms: List[Platform],
        content_type: ContentType,
        objectives: List[SEOObjective],
        translation_quality: TranslationQuality = TranslationQuality.STANDARD
    ) -> MultilingualSEOResult:
        """
        Optimize content for multiple languages and platforms simultaneously
        """
        start_time = datetime.now()
        
        try:
            # Validate inputs
            self._validate_optimization_inputs(
                source_language, target_languages, platforms, content_type
            )
            
            # Create original SEO content
            original_content = await self._create_base_seo_content(
                content, title, description, source_language, 
                platforms[0], content_type, objectives
            )
            
            # Generate multilingual versions
            localized_versions = await self._generate_multilingual_versions(
                original_content, target_languages, translation_quality
            )
            
            # Optimize for each platform
            platform_variations = await self._optimize_for_platforms(
                localized_versions, platforms, objectives
            )
            
            # Generate hreflang tags
            hreflang_tags = self._generate_hreflang_tags(localized_versions, platforms)
            
            # Calculate global optimization score
            global_score = self._calculate_global_optimization_score(
                localized_versions, platform_variations
            )
            
            # Generate performance predictions
            performance_predictions = await self._predict_performance(
                platform_variations, objectives
            )
            
            # Calculate translation costs
            translation_costs = self._calculate_translation_costs(localized_versions)
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(
                localized_versions, platform_variations, objectives
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = MultilingualSEOResult(
                original_content=original_content,
                localized_versions=localized_versions,
                hreflang_tags=hreflang_tags,
                platform_variations=platform_variations,
                global_optimization_score=global_score,
                translation_costs=translation_costs,
                performance_predictions=performance_predictions,
                recommendations=recommendations,
                processing_time=processing_time,
                metadata={
                    "total_languages": len(target_languages) + 1,
                    "total_platforms": len(platforms),
                    "optimization_objectives": [obj.value for obj in objectives],
                    "translation_quality": translation_quality.value,
                    "processing_timestamp": datetime.now().isoformat()
                }
            )
            
            # Cache result for performance
            cache_key = self._generate_cache_key(
                content, title, source_language, target_languages, platforms
            )
            self.optimization_cache[cache_key] = result
            
            logger.info(f"Multilingual SEO optimization completed: {len(target_languages)+1} languages, "
                       f"{len(platforms)} platforms, {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Multilingual SEO optimization failed: {str(e)}")
            raise
    
    def _validate_optimization_inputs(
        self, 
        source_language: str, 
        target_languages: List[str], 
        platforms: List[Platform], 
        content_type: ContentType
    ):
        """Validate optimization inputs"""
        
        # Validate source language
        if not self.language_support.validate_language_code(source_language):
            raise ValueError(f"Unsupported source language: {source_language}")
        
        # Validate target languages
        for lang in target_languages:
            if not self.language_support.validate_language_code(lang):
                raise ValueError(f"Unsupported target language: {lang}")
        
        # Check for duplicates
        if source_language in target_languages:
            raise ValueError("Source language cannot be in target languages list")
        
        # Validate platforms
        if not platforms:
            raise ValueError("At least one platform must be specified")
        
        # Validate content type compatibility
        for platform in platforms:
            if not self._is_content_type_supported(platform, content_type):
                logger.warning(f"Content type {content_type.value} may not be optimal for {platform.value}")
    
    def _is_content_type_supported(self, platform: Platform, content_type: ContentType) -> bool:
        """Check if content type is supported by platform"""
        platform_content_support = {
            Platform.YOUTUBE: [ContentType.VIDEO, ContentType.LIVE_STREAM, ContentType.MUSIC],
            Platform.SPOTIFY: [ContentType.MUSIC, ContentType.PODCAST],
            Platform.INSTAGRAM: [ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY],
            Platform.TWITTER: [ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
            Platform.LINKEDIN: [ContentType.TEXT, ContentType.ARTICLE, ContentType.IMAGE],
            Platform.TIKTOK: [ContentType.VIDEO, ContentType.LIVE_STREAM],
            Platform.MEDIUM: [ContentType.ARTICLE, ContentType.BLOG, ContentType.TEXT],
        }
        
        supported_types = platform_content_support.get(platform, list(ContentType))
        return content_type in supported_types
    
    async def _create_base_seo_content(
        self,
        content: str,
        title: str,
        description: str,
        language: str,
        platform: Platform,
        content_type: ContentType,
        objectives: List[SEOObjective]
    ) -> SEOContent:
        """Create base SEO content for the source language"""
        
        # Generate keywords based on content
        keywords = await self._extract_keywords(content, language, objectives)
        
        # Generate tags
        tags = await self._generate_tags(content, title, language, platform, objectives)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(keywords, language, platform)
        
        # Generate metadata
        metadata = await self._generate_metadata(
            content, title, description, language, content_type, platform
        )
        
        # Calculate base optimization score
        optimization_score = self._calculate_seo_score(
            title, description, keywords, tags, hashtags, platform, objectives
        )
        
        return SEOContent(
            title=title,
            description=description,
            tags=tags,
            hashtags=hashtags,
            keywords=keywords,
            metadata=metadata,
            platform=platform,
            language=language,
            content_type=content_type,
            optimization_score=optimization_score
        )
    
    async def _generate_multilingual_versions(
        self,
        original_content: SEOContent,
        target_languages: List[str],
        translation_quality: TranslationQuality
    ) -> Dict[str, SEOContent]:
        """Generate localized versions for all target languages"""
        
        localized_versions = {original_content.language: original_content}
        
        # Prepare translation requests
        translation_tasks = []
        
        for target_lang in target_languages:
            # Translate title
            title_request = TranslationRequest(
                text=original_content.title,
                source_language=original_content.language,
                target_language=target_lang,
                quality=translation_quality,
                context="SEO title",
                domain="marketing"
            )
            
            # Translate description
            desc_request = TranslationRequest(
                text=original_content.description,
                source_language=original_content.language,
                target_language=target_lang,
                quality=translation_quality,
                context="SEO description",
                domain="marketing"
            )
            
            # Translate keywords
            keywords_text = ", ".join(original_content.keywords)
            keywords_request = TranslationRequest(
                text=keywords_text,
                source_language=original_content.language,
                target_language=target_lang,
                quality=translation_quality,
                context="SEO keywords",
                domain="marketing"
            )
            
            translation_tasks.append((target_lang, title_request, desc_request, keywords_request))
        
        # Execute translations in parallel
        for target_lang, title_req, desc_req, keywords_req in translation_tasks:
            try:
                # Translate content elements
                title_response = await self.translation_manager.translate(title_req)
                desc_response = await self.translation_manager.translate(desc_req)
                keywords_response = await self.translation_manager.translate(keywords_req)
                
                # Extract translated text
                translated_title = title_response.translated_text
                translated_description = desc_response.translated_text
                translated_keywords = keywords_response.translated_text.split(", ")
                
                # Generate localized tags and hashtags
                localized_tags = await self._generate_tags(
                    translated_description, translated_title, target_lang, 
                    original_content.platform, []
                )
                
                localized_hashtags = await self._generate_hashtags(
                    translated_keywords, target_lang, original_content.platform
                )
                
                # Apply cultural adaptations
                cultural_adaptations = await self._apply_cultural_adaptations(
                    translated_title, translated_description, translated_keywords,
                    target_lang, original_content.platform
                )
                
                # Generate localized metadata
                localized_metadata = await self._generate_metadata(
                    translated_description, translated_title, translated_description,
                    target_lang, original_content.content_type, original_content.platform
                )
                
                # Calculate localized optimization score
                localized_score = self._calculate_seo_score(
                    translated_title, translated_description, translated_keywords,
                    localized_tags, localized_hashtags, original_content.platform, []
                )
                
                # Create localized content
                localized_content = SEOContent(
                    title=translated_title,
                    description=translated_description,
                    tags=localized_tags,
                    hashtags=localized_hashtags,
                    keywords=translated_keywords,
                    metadata=localized_metadata,
                    platform=original_content.platform,
                    language=target_lang,
                    content_type=original_content.content_type,
                    optimization_score=localized_score,
                    cultural_adaptations=cultural_adaptations
                )
                
                localized_versions[target_lang] = localized_content
                
                logger.info(f"Generated localized content for {target_lang}")
                
            except Exception as e:
                logger.error(f"Failed to localize content for {target_lang}: {str(e)}")
                # Create fallback version with original content
                fallback_content = SEOContent(
                    title=f"[{target_lang.upper()}] {original_content.title}",
                    description=f"[{target_lang.upper()}] {original_content.description}",
                    tags=original_content.tags,
                    hashtags=original_content.hashtags,
                    keywords=original_content.keywords,
                    metadata=original_content.metadata,
                    platform=original_content.platform,
                    language=target_lang,
                    content_type=original_content.content_type,
                    optimization_score=original_content.optimization_score * 0.5,
                    cultural_adaptations=[f"Translation failed: {str(e)}"]
                )
                localized_versions[target_lang] = fallback_content
        
        return localized_versions
    
    async def _optimize_for_platforms(
        self,
        localized_versions: Dict[str, SEOContent],
        platforms: List[Platform],
        objectives: List[SEOObjective]
    ) -> Dict[Platform, Dict[str, SEOContent]]:
        """Optimize localized content for each platform"""
        
        platform_variations = {}
        
        for platform in platforms:
            platform_variations[platform] = {}
            requirements = self.platform_requirements.get(platform)
            
            if not requirements:
                logger.warning(f"No requirements found for platform {platform.value}")
                continue
            
            for lang_code, content in localized_versions.items():
                try:
                    # Adapt content to platform requirements
                    adapted_content = await self._adapt_content_to_platform(
                        content, platform, requirements, objectives
                    )
                    
                    platform_variations[platform][lang_code] = adapted_content
                    
                except Exception as e:
                    logger.error(f"Failed to adapt content for {platform.value} in {lang_code}: {str(e)}")
                    # Use original content as fallback
                    platform_variations[platform][lang_code] = content
        
        return platform_variations
    
    async def _adapt_content_to_platform(
        self,
        content: SEOContent,
        platform: Platform,
        requirements: PlatformRequirements,
        objectives: List[SEOObjective]
    ) -> SEOContent:
        """Adapt content to specific platform requirements"""
        
        # Truncate title if necessary
        adapted_title = content.title
        if len(adapted_title) > requirements.title_max_length:
            adapted_title = adapted_title[:requirements.title_max_length-3] + "..."
        
        # Truncate description if necessary
        adapted_description = content.description
        if len(adapted_description) > requirements.description_max_length:
            adapted_description = adapted_description[:requirements.description_max_length-3] + "..."
        
        # Limit tags
        adapted_tags = content.tags[:requirements.tags_max_count]
        adapted_tags = [tag[:requirements.tag_max_length] for tag in adapted_tags]
        
        # Adapt hashtags based on platform support
        adapted_hashtags = content.hashtags if requirements.supports_hashtags else []
        
        # Platform-specific optimizations
        if platform == Platform.YOUTUBE:
            adapted_title = await self._optimize_youtube_title(adapted_title, content.keywords)
            adapted_description = await self._optimize_youtube_description(adapted_description, content.keywords)
        
        elif platform == Platform.TIKTOK:
            adapted_hashtags = await self._optimize_tiktok_hashtags(content.keywords, content.language)
            adapted_title = await self._optimize_tiktok_title(adapted_title)
        
        elif platform == Platform.INSTAGRAM:
            adapted_hashtags = await self._optimize_instagram_hashtags(content.keywords, content.language)
        
        elif platform == Platform.LINKEDIN:
            adapted_title = await self._optimize_linkedin_title(adapted_title, objectives)
            adapted_description = await self._optimize_linkedin_description(adapted_description)
        
        elif platform == Platform.SPOTIFY:
            adapted_title = await self._optimize_spotify_title(adapted_title, content.keywords)
            adapted_tags = await self._optimize_spotify_genres(content.keywords)
        
        # Calculate platform-specific optimization score
        platform_score = self._calculate_platform_seo_score(
            adapted_title, adapted_description, content.keywords,
            adapted_tags, adapted_hashtags, platform, objectives, requirements
        )
        
        # Create adapted content
        adapted_content = SEOContent(
            title=adapted_title,
            description=adapted_description,
            tags=adapted_tags,
            hashtags=adapted_hashtags,
            keywords=content.keywords,
            metadata=content.metadata,
            platform=platform,
            language=content.language,
            content_type=content.content_type,
            optimization_score=platform_score,
            cultural_adaptations=content.cultural_adaptations
        )
        
        return adapted_content
    
    async def _extract_keywords(
        self, 
        content: str, 
        language: str, 
        objectives: List[SEOObjective]
    ) -> List[str]:
        """Extract relevant keywords from content"""
        
        # Simple keyword extraction (in real implementation would use NLP)
        words = content.lower().split()
        
        # Filter out common stop words (simplified)
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Get unique keywords and limit to reasonable number
        keywords = list(set(keywords))[:20]
        
        # Add objective-based keywords
        objective_keywords = {
            SEOObjective.DISCOVERABILITY: ["discover", "find", "search", "explore"],
            SEOObjective.ENGAGEMENT: ["like", "share", "comment", "engage"],
            SEOObjective.MONETIZATION: ["buy", "purchase", "premium", "subscribe"],
            SEOObjective.VIRAL_POTENTIAL: ["viral", "trending", "popular", "amazing"],
            SEOObjective.BRAND_AWARENESS: ["brand", "official", "authentic", "original"]
        }
        
        for objective in objectives:
            if objective in objective_keywords:
                keywords.extend(objective_keywords[objective])
        
        return keywords[:15]  # Limit to top 15 keywords
    
    async def _generate_tags(
        self,
        content: str,
        title: str,
        language: str,
        platform: Platform,
        objectives: List[SEOObjective]
    ) -> List[str]:
        """Generate relevant tags for the content"""
        
        # Extract tags from content and title
        text_for_tags = f"{title} {content}".lower()
        
        # Simple tag extraction
        potential_tags = []
        
        # Extract noun phrases (simplified)
        words = text_for_tags.split()
        for i in range(len(words)-1):
            if len(words[i]) > 3 and len(words[i+1]) > 3:
                potential_tags.append(f"{words[i]} {words[i+1]}")
        
        # Add single word tags
        potential_tags.extend([word for word in words if len(word) > 4])
        
        # Platform-specific tag optimization
        if platform == Platform.YOUTUBE:
            potential_tags.extend(["tutorial", "review", "entertainment", "music", "vlog"])
        elif platform == Platform.TIKTOK:
            potential_tags.extend(["dance", "comedy", "challenge", "trend", "viral"])
        elif platform == Platform.SPOTIFY:
            potential_tags.extend(["music", "song", "album", "artist", "playlist"])
        
        # Remove duplicates and limit
        tags = list(set(potential_tags))[:20]
        
        return tags
    
    async def _generate_hashtags(
        self,
        keywords: List[str],
        language: str,
        platform: Platform
    ) -> List[str]:
        """Generate relevant hashtags"""
        
        hashtags = []
        
        # Convert keywords to hashtags
        for keyword in keywords[:10]:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            hashtags.append(hashtag)
        
        # Add platform-specific hashtags
        platform_hashtags = {
            Platform.INSTAGRAM: ["#instagram", "#instagood", "#photooftheday"],
            Platform.TIKTOK: ["#tiktok", "#fyp", "#viral", "#trending"],
            Platform.TWITTER: ["#twitter", "#trending", "#viral"],
            Platform.LINKEDIN: ["#linkedin", "#professional", "#business"],
        }
        
        if platform in platform_hashtags:
            hashtags.extend(platform_hashtags[platform])
        
        # Add language-specific hashtags
        if language != "en":
            lang_info = self.language_support.get_language(language)
            if lang_info:
                hashtags.append(f"#{language}")
                hashtags.append(f"#{lang_info.name.lower().replace(' ', '')}")
        
        return hashtags[:20]  # Limit hashtags
    
    async def _generate_metadata(
        self,
        content: str,
        title: str,
        description: str,
        language: str,
        content_type: ContentType,
        platform: Platform
    ) -> Dict[str, Any]:
        """Generate comprehensive metadata"""
        
        lang_info = self.language_support.get_language(language)
        
        metadata = {
            "language": language,
            "content_type": content_type.value,
            "platform": platform.value,
            "character_count": len(content),
            "word_count": len(content.split()),
            "title_length": len(title),
            "description_length": len(description),
            "generated_at": datetime.now().isoformat(),
        }
        
        if lang_info:
            metadata.update({
                "language_name": lang_info.name,
                "native_name": lang_info.native_name,
                "script": lang_info.script.value,
                "text_direction": lang_info.direction.value,
                "language_family": lang_info.family.value
            })
        
        return metadata
    
    async def _apply_cultural_adaptations(
        self,
        title: str,
        description: str,
        keywords: List[str],
        language: str,
        platform: Platform
    ) -> List[str]:
        """Apply cultural adaptations for specific language/region"""
        
        adaptations = []
        lang_info = self.language_support.get_language(language)
        
        if not lang_info:
            return adaptations
        
        # RTL language adaptations
        if lang_info.direction == TextDirection.RTL:
            adaptations.append("Applied RTL text direction")
        
        # Cultural color preferences
        if language in ["zh", "zh-cn"]:
            # Chinese cultural preferences
            if "red" in title.lower() or "red" in description.lower():
                adaptations.append("Red color considered lucky in Chinese culture")
            adaptations.append("Applied Chinese cultural preferences")
        
        elif language in ["ja", "ja-jp"]:
            # Japanese cultural preferences
            adaptations.append("Applied Japanese cultural nuances")
        
        elif language in ["ar", "ar-sa", "ar-eg"]:
            # Arabic cultural preferences
            adaptations.append("Applied Arabic cultural considerations")
        
        # Regional platform preferences
        if platform == Platform.WEIBO and language.startswith("zh"):
            adaptations.append("Optimized for Weibo algorithm preferences")
        
        elif platform == Platform.YANDEX and language == "ru":
            adaptations.append("Optimized for Yandex search preferences")
        
        return adaptations
    
    def _calculate_seo_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        tags: List[str],
        hashtags: List[str],
        platform: Platform,
        objectives: List[SEOObjective]
    ) -> float:
        """Calculate SEO optimization score"""
        
        score = 0.0
        
        # Title optimization (30 points)
        title_score = 0
        if title and len(title) > 10:
            title_score += 10
        if any(keyword.lower() in title.lower() for keyword in keywords[:3]):
            title_score += 15
        if len(title) <= 60:  # Good length for most platforms
            title_score += 5
        score += title_score
        
        # Description optimization (25 points)
        desc_score = 0
        if description and len(description) > 50:
            desc_score += 10
        if len(description) <= 155:  # Good length for meta descriptions
            desc_score += 5
        keyword_in_desc = sum(1 for keyword in keywords[:5] if keyword.lower() in description.lower())
        desc_score += min(keyword_in_desc * 2, 10)
        score += desc_score
        
        # Keywords optimization (20 points)
        keywords_score = min(len(keywords) * 2, 20)
        score += keywords_score
        
        # Tags optimization (15 points)
        tags_score = min(len(tags) * 1.5, 15)
        score += tags_score
        
        # Hashtags optimization (10 points)
        hashtags_score = min(len(hashtags) * 1, 10)
        score += hashtags_score
        
        return min(score, 100.0)
    
    def _calculate_platform_seo_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        tags: List[str],
        hashtags: List[str],
        platform: Platform,
        objectives: List[SEOObjective],
        requirements: PlatformRequirements
    ) -> float:
        """Calculate platform-specific SEO score"""
        
        base_score = self._calculate_seo_score(
            title, description, keywords, tags, hashtags, platform, objectives
        )
        
        # Platform-specific adjustments
        platform_bonus = 0.0
        
        # Check adherence to platform requirements
        if len(title) <= requirements.title_max_length:
            platform_bonus += 5
        if len(description) <= requirements.description_max_length:
            platform_bonus += 5
        if len(tags) <= requirements.tags_max_count:
            platform_bonus += 3
        
        # Platform algorithm factors
        if requirements.algorithm_factors:
            for factor, weight in requirements.algorithm_factors.items():
                if factor == "hashtag_trending" and hashtags:
                    platform_bonus += weight * 10
                elif factor == "title_keyword_density" and keywords:
                    keyword_density = sum(1 for kw in keywords if kw.lower() in title.lower()) / len(keywords)
                    platform_bonus += weight * keyword_density * 10
        
        return min(base_score + platform_bonus, 100.0)
    
    def _calculate_global_optimization_score(
        self,
        localized_versions: Dict[str, SEOContent],
        platform_variations: Dict[Platform, Dict[str, SEOContent]]
    ) -> float:
        """Calculate overall global optimization score"""
        
        total_scores = []
        
        # Base localized scores
        for content in localized_versions.values():
            total_scores.append(content.optimization_score)
        
        # Platform-specific scores
        for platform_dict in platform_variations.values():
            for content in platform_dict.values():
                total_scores.append(content.optimization_score)
        
        if not total_scores:
            return 0.0
        
        # Calculate weighted average
        global_score = sum(total_scores) / len(total_scores)
        
        # Bonus for language diversity
        language_count = len(localized_versions)
        diversity_bonus = min(language_count * 2, 15)
        
        # Bonus for platform coverage
        platform_count = len(platform_variations)
        platform_bonus = min(platform_count * 3, 20)
        
        return min(global_score + diversity_bonus + platform_bonus, 100.0)
    
    def _generate_hreflang_tags(
        self,
        localized_versions: Dict[str, SEOContent],
        platforms: List[Platform]
    ) -> List[Dict[str, str]]:
        """Generate hreflang tags for international SEO"""
        
        hreflang_tags = []
        
        for lang_code, content in localized_versions.items():
            lang_info = self.language_support.get_language(lang_code)
            
            if lang_info and lang_info.regions:
                # Add hreflang for each region where this language is spoken
                for region in lang_info.regions[:3]:  # Limit to 3 main regions
                    hreflang_code = f"{lang_code}-{region.lower()}"
                    
                    tag = {
                        "hreflang": hreflang_code,
                        "href": f"https://example.com/{lang_code}/{region.lower()}/",
                        "language": lang_code,
                        "region": region,
                        "title": content.title
                    }
                    hreflang_tags.append(tag)
            else:
                # Generic language tag
                tag = {
                    "hreflang": lang_code,
                    "href": f"https://example.com/{lang_code}/",
                    "language": lang_code,
                    "title": content.title
                }
                hreflang_tags.append(tag)
        
        # Add x-default tag
        if localized_versions:
            default_lang = list(localized_versions.keys())[0]
            default_content = localized_versions[default_lang]
            
            default_tag = {
                "hreflang": "x-default",
                "href": "https://example.com/",
                "language": "default",
                "title": default_content.title
            }
            hreflang_tags.append(default_tag)
        
        return hreflang_tags
    
    async def _predict_performance(
        self,
        platform_variations: Dict[Platform, Dict[str, SEOContent]],
        objectives: List[SEOObjective]
    ) -> Dict[str, float]:
        """Predict performance metrics for optimized content"""
        
        predictions = {}
        
        # Calculate average optimization scores
        all_scores = []
        for platform_dict in platform_variations.values():
            for content in platform_dict.values():
                all_scores.append(content.optimization_score)
        
        if all_scores:
            avg_score = sum(all_scores) / len(all_scores)
            
            # Predict based on optimization score
            predictions["discoverability_score"] = min(avg_score * 0.8, 95.0)
            predictions["engagement_potential"] = min(avg_score * 0.7, 90.0)
            predictions["viral_probability"] = min(avg_score * 0.6, 85.0)
            predictions["monetization_potential"] = min(avg_score * 0.75, 88.0)
            
            # Platform-specific predictions
            for platform in platform_variations.keys():
                platform_scores = [content.optimization_score for content in platform_variations[platform].values()]
                if platform_scores:
                    platform_avg = sum(platform_scores) / len(platform_scores)
                    predictions[f"{platform.value}_performance"] = platform_avg
        
        return predictions
    
    def _calculate_translation_costs(
        self,
        localized_versions: Dict[str, SEOContent]
    ) -> Dict[TranslationProvider, float]:
        """Calculate estimated translation costs by provider"""
        
        costs = {provider: 0.0 for provider in TranslationProvider}
        
        # Estimate character count for translations
        total_chars = 0
        for content in localized_versions.values():
            total_chars += len(content.title) + len(content.description)
        
        # Provider cost estimates (simplified)
        provider_rates = {
            TranslationProvider.GOOGLE: 0.00002,
            TranslationProvider.DEEPL: 0.00003,
            TranslationProvider.MICROSOFT: 0.000015,
            TranslationProvider.AMAZON: 0.000012
        }
        
        for provider, rate in provider_rates.items():
            costs[provider] = total_chars * rate
        
        return costs
    
    def _generate_optimization_recommendations(
        self,
        localized_versions: Dict[str, SEOContent],
        platform_variations: Dict[Platform, Dict[str, SEOContent]],
        objectives: List[SEOObjective]
    ) -> List[str]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Language coverage recommendations
        language_count = len(localized_versions)
        if language_count < 5:
            recommendations.append(f"Consider adding more languages (currently {language_count}). Popular additions: Spanish, French, German, Portuguese, Arabic")
        
        # Platform coverage recommendations
        platform_count = len(platform_variations)
        if platform_count < 3:
            recommendations.append(f"Expand to more platforms (currently {platform_count}). Consider YouTube, Instagram, TikTok for maximum reach")
        
        # Score-based recommendations
        avg_scores = []
        for content_dict in platform_variations.values():
            for content in content_dict.values():
                avg_scores.append(content.optimization_score)
        
        if avg_scores:
            avg_score = sum(avg_scores) / len(avg_scores)
            
            if avg_score < 70:
                recommendations.append("Overall optimization score is below 70%. Consider improving titles and descriptions with more relevant keywords")
            
            if avg_score < 50:
                recommendations.append("Low optimization detected. Review keyword strategy and ensure content aligns with platform requirements")
        
        # Objective-specific recommendations
        if SEOObjective.VIRAL_POTENTIAL in objectives:
            recommendations.append("For viral potential: Focus on trending hashtags and emotionally engaging titles")
        
        if SEOObjective.MONETIZATION in objectives:
            recommendations.append("For monetization: Include call-to-action keywords and premium content indicators")
        
        if SEOObjective.GLOBAL_REACH in objectives:
            recommendations.append("For global reach: Ensure cultural adaptations and regional platform optimization")
        
        return recommendations
    
    def _generate_cache_key(
        self,
        content: str,
        title: str,
        source_language: str,
        target_languages: List[str],
        platforms: List[Platform]
    ) -> str:
        """Generate cache key for optimization results"""
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        title_hash = hashlib.md5(title.encode()).hexdigest()
        languages_str = ",".join(sorted([source_language] + target_languages))
        platforms_str = ",".join(sorted([p.value for p in platforms]))
        
        cache_string = f"{content_hash}_{title_hash}_{languages_str}_{platforms_str}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    # Platform-specific optimization methods
    
    async def _optimize_youtube_title(self, title: str, keywords: List[str]) -> str:
        """Optimize title for YouTube algorithm"""
        # Add most relevant keyword to beginning if not present
        if keywords and not any(kw.lower() in title.lower() for kw in keywords[:3]):
            title = f"{keywords[0]} | {title}"
        return title[:100]  # YouTube limit
    
    async def _optimize_youtube_description(self, description: str, keywords: List[str]) -> str:
        """Optimize description for YouTube"""
        # Add keyword-rich intro
        if keywords:
            keyword_intro = f"This content focuses on {', '.join(keywords[:3])}. "
            if not any(kw.lower() in description[:100].lower() for kw in keywords[:3]):
                description = keyword_intro + description
        return description[:5000]  # YouTube limit
    
    async def _optimize_tiktok_title(self, title: str) -> str:
        """Optimize title for TikTok engagement"""
        # Add engaging elements
        if not any(char in title for char in "!?"):
            title += "!"
        return title[:150]  # TikTok limit
    
    async def _optimize_tiktok_hashtags(self, keywords: List[str], language: str) -> List[str]:
        """Optimize hashtags for TikTok"""
        hashtags = [f"#{kw.replace(' ', '').lower()}" for kw in keywords[:5]]
        hashtags.extend(["#fyp", "#viral", "#trending"])
        return hashtags[:20]
    
    async def _optimize_instagram_hashtags(self, keywords: List[str], language: str) -> List[str]:
        """Optimize hashtags for Instagram"""
        hashtags = [f"#{kw.replace(' ', '').lower()}" for kw in keywords[:10]]
        hashtags.extend(["#instagram", "#instagood", "#photooftheday"])
        return hashtags[:30]  # Instagram limit
    
    async def _optimize_linkedin_title(self, title: str, objectives: List[SEOObjective]) -> str:
        """Optimize title for LinkedIn professional audience"""
        professional_keywords = ["professional", "business", "industry", "career", "leadership"]
        if SEOObjective.BRAND_AWARENESS in objectives:
            if not any(kw in title.lower() for kw in professional_keywords):
                title = f"Professional {title}"
        return title[:120]  # LinkedIn limit
    
    async def _optimize_linkedin_description(self, description: str) -> str:
        """Optimize description for LinkedIn"""
        # Add professional call-to-action
        if "connect" not in description.lower():
            description += " Connect with me to learn more!"
        return description[:3000]  # LinkedIn limit
    
    async def _optimize_spotify_title(self, title: str, keywords: List[str]) -> str:
        """Optimize title for Spotify discoverability"""
        # Ensure genre or style is mentioned
        music_keywords = ["song", "music", "track", "album", "single"]
        if not any(kw in title.lower() for kw in music_keywords):
            title = f"{title} (Song)"
        return title[:80]  # Spotify limit
    
    async def _optimize_spotify_genres(self, keywords: List[str]) -> List[str]:
        """Generate genre tags for Spotify"""
        # Map keywords to music genres
        genre_mapping = {
            "electronic": "Electronic",
            "dance": "Dance",
            "rock": "Rock",
            "pop": "Pop",
            "hip": "Hip-Hop",
            "jazz": "Jazz",
            "classical": "Classical",
            "indie": "Indie",
            "folk": "Folk",
            "country": "Country"
        }
        
        genres = []
        for keyword in keywords:
            for key, genre in genre_mapping.items():
                if key in keyword.lower():
                    genres.append(genre)
        
        # Add default genres if none found
        if not genres:
            genres = ["Music", "Entertainment"]
        
        return genres[:10]
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization performance statistics"""
        return {
            "total_optimizations": len(self.optimization_cache),
            "supported_languages": len(self.language_support.languages),
            "supported_platforms": len(self.platform_requirements),
            "cache_size": len(self.optimization_cache),
            "performance_analytics": self.performance_analytics
        }
    
    def export_optimization_report(self, result: MultilingualSEOResult, format: str = "json") -> str:
        """Export optimization report in specified format"""
        
        if format == "json":
            export_data = {
                "summary": {
                    "total_languages": len(result.localized_versions),
                    "total_platforms": len(result.platform_variations),
                    "global_score": result.global_optimization_score,
                    "processing_time": result.processing_time
                },
                "localized_versions": {
                    lang: {
                        "title": content.title,
                        "description": content.description,
                        "keywords": content.keywords,
                        "tags": content.tags,
                        "hashtags": content.hashtags,
                        "optimization_score": content.optimization_score,
                        "cultural_adaptations": content.cultural_adaptations
                    }
                    for lang, content in result.localized_versions.items()
                },
                "platform_variations": {
                    platform.value: {
                        lang: {
                            "title": content.title,
                            "optimization_score": content.optimization_score
                        }
                        for lang, content in content_dict.items()
                    }
                    for platform, content_dict in result.platform_variations.items()
                },
                "hreflang_tags": result.hreflang_tags,
                "performance_predictions": result.performance_predictions,
                "translation_costs": {k.value: v for k, v in result.translation_costs.items()},
                "recommendations": result.recommendations
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Module exports
__all__ = [
    "IndustrialSEOOptimizer",
    "Platform",
    "ContentType", 
    "SEOObjective",
    "SEOContent",
    "MultilingualSEOResult",
    "PlatformRequirements"
]

logger.info("Industrial Multi-Platform SEO System loaded successfully")