"""SEO Configuration Module

Advanced SEO optimization system for multi-format content creators.
Supports musicians, bloggers, photographers, influencers, and comedians.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected intellectual property. Unauthorized use is prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""
import os
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import re
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class SEOLevel(Enum):
    """SEO optimization levels"""    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentCategory(Enum):
    """Content categories for SEO optimization"""    MUSIC = "music"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    SOCIAL_MEDIA = "social_media"
    COMEDY = "comedy"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"


class Platform(Enum):
    """Target platforms for SEO optimization"""    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"


class Language(Enum):
    """Supported languages for SEO"""    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


@dataclass
class KeywordConfig:
    """Keyword optimization configuration"""    enabled: bool = True
    
    # Primary keywords
    primary_keywords: List[str] = field(default_factory=list)
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    
    # Keyword density settings
    primary_density_target: float = 0.02  # 2%
    secondary_density_target: float = 0.01  # 1%
    max_keyword_density: float = 0.05  # 5%
    
    # Keyword research
    auto_keyword_research: bool = True
    competitor_keyword_analysis: bool = True
    trending_keywords_integration: bool = True
    semantic_keyword_expansion: bool = True
    
    # Language-specific settings
    keyword_languages: List[Language] = field(default_factory=lambda: [Language.ENGLISH])
    localized_keywords: Dict[str, List[str]] = field(default_factory=dict)
    
    # Advanced features
    intent_based_keywords: bool = True
    voice_search_optimization: bool = True
    featured_snippet_optimization: bool = True


@dataclass
class MetaTagsConfig:
    """Meta tags configuration"""    enabled: bool = True
    
    # Title optimization
    auto_title_generation: bool = True
    title_template: str = "{primary_keyword} | {content_title} | {creator_name}"
    title_max_length: int = 60
    title_include_keywords: bool = True
    
    # Description optimization
    auto_description_generation: bool = True
    description_template: str = "{content_summary} {call_to_action} {keywords}"
    description_max_length: int = 160
    description_include_keywords: bool = True
    
    # Keywords meta tag
    keywords_meta_enabled: bool = True
    max_keywords_count: int = 10
    
    # Open Graph tags
    og_enabled: bool = True
    og_type: str = "article"
    og_site_name: str = "IA Influencer Agent Platform"
    og_locale: str = "en_US"
    
    # Twitter Card tags
    twitter_card_enabled: bool = True
    twitter_card_type: str = "summary_large_image"
    twitter_creator: str = "@fahed_mlaiel"
    
    # Schema.org markup
    schema_enabled: bool = True
    schema_types: List[str] = field(default_factory=lambda: [
        "Article", "CreativeWork", "MusicRecording", "Photograph", "VideoObject"
    ])
    
    # Custom meta tags
    custom_meta_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContentStructureConfig:
    """Content structure optimization configuration"""    enabled: bool = True
    
    # Heading optimization
    h1_optimization: bool = True
    h1_include_primary_keyword: bool = True
    h2_h6_optimization: bool = True
    heading_hierarchy_check: bool = True
    
    # Paragraph optimization
    paragraph_length_optimization: bool = True
    ideal_paragraph_length: int = 150  # characters
    max_paragraph_length: int = 300
    
    # List optimization
    bullet_points_optimization: bool = True
    numbered_lists_optimization: bool = True
    
    # Internal linking
    internal_linking_enabled: bool = True
    internal_links_per_article: int = 3
    anchor_text_optimization: bool = True
    
    # External linking
    external_linking_enabled: bool = True
    authoritative_sources_only: bool = True
    nofollow_external_links: bool = True
    
    # Image optimization
    image_alt_text_optimization: bool = True
    image_title_optimization: bool = True
    image_filename_optimization: bool = True
    lazy_loading_enabled: bool = True
    
    # Content formatting
    bold_text_keywords: bool = True
    italic_text_emphasis: bool = True
    quote_highlighting: bool = True


@dataclass
class TechnicalSEOConfig:
    """Technical SEO configuration"""    enabled: bool = True
    
    # URL optimization
    url_optimization: bool = True
    clean_urls: bool = True
    keyword_in_url: bool = True
    url_max_length: int = 100
    
    # Site speed optimization
    page_speed_optimization: bool = True
    image_compression: bool = True
    css_minification: bool = True
    javascript_minification: bool = True
    
    # Mobile optimization
    mobile_friendly: bool = True
    responsive_design: bool = True
    amp_enabled: bool = True
    
    # Core Web Vitals
    largest_contentful_paint_target: float = 2.5  # seconds
    first_input_delay_target: float = 0.1  # seconds
    cumulative_layout_shift_target: float = 0.1
    
    # Indexing
    sitemap_generation: bool = True
    robots_txt_optimization: bool = True
    canonical_urls: bool = True
    
    # Security
    https_enforcement: bool = True
    security_headers: bool = True
    
    # Structured data
    json_ld_enabled: bool = True
    microdata_enabled: bool = True
    rdfa_enabled: bool = False


@dataclass
class LocalSEOConfig:
    """Local SEO configuration"""    enabled: bool = True
    
    # Business information
    business_name: str = "IA Influencer Agent Platform"
    business_address: str = ""
    business_phone: str = ""
    business_email: str = "mlaiel@live.de"
    business_website: str = "https://ia-influencer.com"
    
    # Geographic targeting
    target_countries: List[str] = field(default_factory=lambda: ["DE", "EU", "US"])
    target_cities: List[str] = field(default_factory=list)
    target_languages: List[Language] = field(default_factory=lambda: [Language.GERMAN, Language.ENGLISH])
    
    # Local keywords
    location_based_keywords: bool = True
    near_me_optimization: bool = True
    local_intent_keywords: bool = True
    
    # Google My Business
    gmb_optimization: bool = True
    gmb_posts_automation: bool = True
    review_management: bool = True
    
    # Local directories
    directory_submissions: bool = True
    citation_building: bool = True
    nap_consistency: bool = True  # Name, Address, Phone


@dataclass
class AnalyticsConfig:
    """SEO analytics configuration"""    enabled: bool = True
    
    # Tracking codes
    google_analytics_id: str = ""
    google_search_console_id: str = ""
    bing_webmaster_tools_id: str = ""
    
    # Ranking tracking
    keyword_rank_tracking: bool = True
    competitor_rank_tracking: bool = True
    serp_feature_tracking: bool = True
    
    # Performance metrics
    organic_traffic_tracking: bool = True
    click_through_rate_tracking: bool = True
    bounce_rate_tracking: bool = True
    conversion_tracking: bool = True
    
    # Advanced analytics
    user_behavior_tracking: bool = True
    content_performance_analysis: bool = True
    seo_roi_tracking: bool = True
    
    # Reporting
    automated_reports: bool = True
    report_frequency: str = "weekly"  # daily, weekly, monthly
    report_recipients: List[str] = field(default_factory=lambda: ["mlaiel@live.de"])


@dataclass
class PlatformSpecificConfig:
    """Platform-specific SEO settings"""    enabled: bool = True
    
    # YouTube SEO
    youtube_title_optimization: bool = True
    youtube_description_optimization: bool = True
    youtube_tags_optimization: bool = True
    youtube_thumbnail_optimization: bool = True
    youtube_cards_and_screens: bool = True
    
    # Instagram SEO
    instagram_hashtag_optimization: bool = True
    instagram_alt_text: bool = True
    instagram_story_optimization: bool = True
    
    # TikTok SEO
    tiktok_hashtag_strategy: bool = True
    tiktok_trending_sounds: bool = True
    tiktok_caption_optimization: bool = True
    
    # Spotify SEO
    spotify_playlist_optimization: bool = True
    spotify_artist_description: bool = True
    spotify_track_metadata: bool = True
    
    # Platform-specific keywords
    platform_keywords: Dict[str, List[str]] = field(default_factory=dict)
    platform_hashtags: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SEOConfig:
    """Main SEO configuration"""    
    # Core settings
    enabled: bool = True
    seo_level: SEOLevel = SEOLevel.ENTERPRISE
    target_platforms: List[Platform] = field(default_factory=lambda: [
        Platform.GOOGLE, Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK
    ])
    
    # Creator information
    creator_name: str = "Fahed Mlaiel"
    creator_brand: str = "IA Influencer Agent"
    creator_website: str = "https://ia-influencer.com"
    creator_social_profiles: Dict[str, str] = field(default_factory=dict)
    
    # Sub-configurations
    keywords: KeywordConfig = field(default_factory=KeywordConfig)
    meta_tags: MetaTagsConfig = field(default_factory=MetaTagsConfig)
    content_structure: ContentStructureConfig = field(default_factory=ContentStructureConfig)
    technical_seo: TechnicalSEOConfig = field(default_factory=TechnicalSEOConfig)
    local_seo: LocalSEOConfig = field(default_factory=LocalSEOConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    platform_specific: PlatformSpecificConfig = field(default_factory=PlatformSpecificConfig)
    
    # Content-specific settings
    content_category_settings: Dict[ContentCategory, Dict[str, Any]] = field(default_factory=dict)
    
    # AI-powered features
    ai_content_optimization: bool = True
    ai_keyword_research: bool = True
    ai_competitor_analysis: bool = True
    ai_trend_prediction: bool = True
    
    # Automation settings
    auto_optimization: bool = True
    bulk_optimization: bool = True
    scheduled_optimization: bool = True
    
    # Quality control
    seo_score_threshold: float = 0.8
    content_quality_check: bool = True
    plagiarism_check: bool = True
    brand_safety_check: bool = True

    def __post_init__(self):
        """Initialize default configurations"""        if not self.creator_social_profiles:
            self._setup_default_social_profiles()
        if not self.content_category_settings:
            self._setup_content_category_settings()

    def _setup_default_social_profiles(self):
        """Setup default social media profiles"""        self.creator_social_profiles = {
            "instagram": "@fahed_mlaiel",
            "twitter": "@fahed_mlaiel",
            "youtube": "@fahed_mlaiel",
            "linkedin": "fahed-mlaiel",
            "tiktok": "@fahed_mlaiel"
        }

    def _setup_content_category_settings(self):
        """Setup content category specific settings"""        self.content_category_settings = {
            ContentCategory.MUSIC: {
                "primary_keywords": ["music", "artist", "song", "album"],
                "platforms": ["youtube", "spotify", "soundcloud"],
                "schema_type": "MusicRecording",
                "meta_focus": "artist_and_track"
            },
            ContentCategory.BLOG: {
                "primary_keywords": ["blog", "article", "guide", "tips"],
                "platforms": ["google", "linkedin", "facebook"],
                "schema_type": "Article",
                "meta_focus": "topic_and_value"
            },
            ContentCategory.PHOTOGRAPHY: {
                "primary_keywords": ["photography", "photo", "image", "portrait"],
                "platforms": ["instagram", "pinterest", "flickr"],
                "schema_type": "Photograph",
                "meta_focus": "visual_and_style"
            },
            ContentCategory.VIDEO: {
                "primary_keywords": ["video", "tutorial", "vlog", "entertainment"],
                "platforms": ["youtube", "tiktok", "instagram"],
                "schema_type": "VideoObject",
                "meta_focus": "content_and_engagement"
            },
            ContentCategory.COMEDY: {
                "primary_keywords": ["comedy", "funny", "humor", "entertainment"],
                "platforms": ["tiktok", "youtube", "instagram"],
                "schema_type": "VideoObject",
                "meta_focus": "entertainment_and_viral"
            }
        }

    def optimize_for_content_type(self, content_type: ContentCategory, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for specific content type"""        if content_type not in self.content_category_settings:
            logger.warning(f"No specific settings for content type: {content_type}")
            content_type = ContentCategory.BLOG  # Default fallback
        
        settings = self.content_category_settings[content_type]
        
        optimization_result = {
            "content_type": content_type.value,
            "optimized_content": content,
            "meta_tags": {},
            "keywords": {},
            "structure_recommendations": [],
            "platform_adaptations": {},
            "seo_score": 0.0
        }
        
        # Generate optimized title
        if self.meta_tags.auto_title_generation:
            title = self._generate_optimized_title(content, settings, metadata)
            optimization_result["meta_tags"]["title"] = title
        
        # Generate optimized description
        if self.meta_tags.auto_description_generation:
            description = self._generate_optimized_description(content, settings, metadata)
            optimization_result["meta_tags"]["description"] = description
        
        # Extract and optimize keywords
        if self.keywords.enabled:
            keywords_data = self._extract_and_optimize_keywords(content, settings)
            optimization_result["keywords"] = keywords_data
        
        # Generate platform-specific adaptations
        for platform in settings.get("platforms", []):
            if platform in [p.value for p in self.target_platforms]:
                adaptation = self._adapt_for_platform(content, platform, settings)
                optimization_result["platform_adaptations"][platform] = adaptation
        
        # Calculate SEO score
        optimization_result["seo_score"] = self._calculate_seo_score(optimization_result)
        
        return optimization_result

    def _generate_optimized_title(self, content: str, settings: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate SEO-optimized title"""        # Extract primary keyword
        primary_keyword = settings["primary_keywords"][0] if settings["primary_keywords"] else "content"
        
        # Get content title from metadata or extract from content
        content_title = metadata.get("title", "")
        if not content_title:
            # Extract first heading or first sentence
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    content_title = line.strip()[:30] + "..."
                    break
        
        # Generate title using template
        title = self.meta_tags.title_template.format(
            primary_keyword=primary_keyword.title(),
            content_title=content_title,
            creator_name=self.creator_name
        )
        
        # Ensure title length is within limits
        if len(title) > self.meta_tags.title_max_length:
            title = title[:self.meta_tags.title_max_length-3] + "..."
        
        return title

    def _generate_optimized_description(self, content: str, settings: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate SEO-optimized description"""        # Extract content summary (first 100 characters of meaningful content)
        content_lines = [line.strip() for line in content.split('\n') if line.strip()]
        content_summary = ""
        
        for line in content_lines:
            if len(line) > 20:  # Skip short lines like headers
                content_summary = line[:100]
                break
        
        if not content_summary:
            content_summary = content[:100]
        
        # Add call to action based on content type
        cta_map = {
            "music": "🎵 Listen now and discover amazing music!",
            "blog": "📖 Read the full article for expert insights!",
            "photography": "📸 See more stunning photography!",
            "video": "🎬 Watch the full video now!",
            "comedy": "😂 Get ready to laugh!"
        }
        
        call_to_action = cta_map.get(settings.get("meta_focus", "").split("_")[0], "✨ Discover more!")
        
        # Include primary keywords
        keywords_text = ", ".join(settings["primary_keywords"][:3])
        
        description = self.meta_tags.description_template.format(
            content_summary=content_summary,
            call_to_action=call_to_action,
            keywords=f"#{keywords_text.replace(', ', ' #')}"
        )
        
        # Ensure description length is within limits
        if len(description) > self.meta_tags.description_max_length:
            description = description[:self.meta_tags.description_max_length-3] + "..."
        
        return description

    def _extract_and_optimize_keywords(self, content: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and optimize keywords from content"""        # This is a simplified implementation
        # In a real system, this would use NLP and keyword research APIs
        
        content_lower = content.lower()
        word_frequency = {}
        
        # Count word frequency
        words = re.findall(r'\b\w+\b', content_lower)
        for word in words:
            if len(word) > 3:  # Skip short words
                word_frequency[word] = word_frequency.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Extract top keywords
        extracted_keywords = [word for word, freq in sorted_words[:20]]
        
        # Combine with predefined keywords
        primary_keywords = settings.get("primary_keywords", [])
        secondary_keywords = list(set(extracted_keywords) & set(primary_keywords))
        
        return {
            "primary_keywords": primary_keywords,
            "secondary_keywords": secondary_keywords,
            "extracted_keywords": extracted_keywords[:10],
            "keyword_density": self._calculate_keyword_density(content, primary_keywords)
        }

    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""        content_lower = content.lower()
        total_words = len(re.findall(r'\b\w+\b', content_lower))
        
        density = {}
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density[keyword] = (count / total_words) if total_words > 0 else 0.0
        
        return density

    def _adapt_for_platform(self, content: str, platform: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt content for specific platform"""        platform_adaptations = {
            "youtube": {
                "title_length": 100,
                "description_length": 5000,
                "tags_count": 15,
                "focus": "engagement_and_retention"
            },
            "instagram": {
                "caption_length": 2200,
                "hashtags_count": 30,
                "story_optimization": True,
                "focus": "visual_and_hashtags"
            },
            "tiktok": {
                "caption_length": 150,
                "hashtags_count": 10,
                "trending_sounds": True,
                "focus": "viral_and_trending"
            },
            "spotify": {
                "title_optimization": True,
                "artist_description": True,
                "playlist_optimization": True,
                "focus": "discoverability"
            }
        }
        
        adaptation = platform_adaptations.get(platform, {})
        
        # Generate platform-specific content
        adapted_content = {
            "platform": platform,
            "optimized_title": content[:adaptation.get("title_length", 60)],
            "optimized_description": content[:adaptation.get("description_length", 160)],
            "hashtags": self._generate_hashtags(settings, adaptation.get("hashtags_count", 10)),
            "focus_area": adaptation.get("focus", "general"),
            "recommendations": []
        }
        
        return adapted_content

    def _generate_hashtags(self, settings: Dict[str, Any], max_count: int) -> List[str]:
        """Generate relevant hashtags"""        # Combine keywords to create hashtags
        keywords = settings.get("primary_keywords", [])
        hashtags = [f"#{keyword.replace(' ', '').lower()}" for keyword in keywords[:max_count]]
        
        # Add creator-specific hashtags
        creator_hashtags = [
            f"#{self.creator_name.replace(' ', '').lower()}",
            f"#{self.creator_brand.replace(' ', '').lower()}",
            "#iainfluencer",
            "#contentcreator"
        ]
        
        hashtags.extend(creator_hashtags[:max_count - len(hashtags)])
        
        return hashtags[:max_count]

    def _calculate_seo_score(self, optimization_result: Dict[str, Any]) -> float:
        """Calculate overall SEO score"""        score = 0.0
        max_score = 100.0
        
        # Title optimization (20 points)
        title = optimization_result.get("meta_tags", {}).get("title", "")
        if title:
            if len(title) <= self.meta_tags.title_max_length:
                score += 10
            if any(keyword.lower() in title.lower() for keyword in optimization_result.get("keywords", {}).get("primary_keywords", [])):
                score += 10
        
        # Description optimization (20 points)
        description = optimization_result.get("meta_tags", {}).get("description", "")
        if description:
            if len(description) <= self.meta_tags.description_max_length:
                score += 10
            if any(keyword.lower() in description.lower() for keyword in optimization_result.get("keywords", {}).get("primary_keywords", [])):
                score += 10
        
        # Keyword optimization (30 points)
        keywords_data = optimization_result.get("keywords", {})
        if keywords_data.get("primary_keywords"):
            score += 15
        if keywords_data.get("keyword_density"):
            avg_density = sum(keywords_data["keyword_density"].values()) / len(keywords_data["keyword_density"])
            if self.keywords.primary_density_target <= avg_density <= self.keywords.max_keyword_density:
                score += 15
        
        # Platform adaptations (20 points)
        adaptations = optimization_result.get("platform_adaptations", {})
        if adaptations:
            score += 10
            if len(adaptations) >= 2:
                score += 10
        
        # Content structure (10 points)
        if optimization_result.get("structure_recommendations"):
            score += 10
        
        return min(score / max_score, 1.0)

    def validate_configuration(self) -> List[str]:
        """Validate SEO configuration"""        issues = []
        
        # Check required fields
        if not self.creator_name:
            issues.append("Creator name is required")
        if not self.creator_website:
            issues.append("Creator website is required")
        
        # Validate thresholds
        if not 0.0 <= self.seo_score_threshold <= 1.0:
            issues.append("SEO score threshold must be between 0.0 and 1.0")
        
        # Check analytics IDs
        if self.analytics.enabled:
            if not self.analytics.google_analytics_id:
                issues.append("Google Analytics ID is recommended for tracking")
        
        return issues

    @classmethod
    def from_env(cls) -> 'SEOConfig':
        """Create configuration from environment variables"""        config = cls()
        
        # Load basic settings
        config.enabled = os.getenv("SEO_ENABLED", "true").lower() == "true"
        config.seo_level = SEOLevel(os.getenv("SEO_LEVEL", "enterprise"))
        config.creator_name = os.getenv("CREATOR_NAME", "Fahed Mlaiel")
        config.creator_website = os.getenv("CREATOR_WEBSITE", "https://ia-influencer.com")
        
        # Load keyword settings
        config.keywords.auto_keyword_research = os.getenv("AUTO_KEYWORD_RESEARCH", "true").lower() == "true"
        config.keywords.primary_density_target = float(os.getenv("PRIMARY_KEYWORD_DENSITY", "0.02"))
        
        # Load meta tags settings
        config.meta_tags.auto_title_generation = os.getenv("AUTO_TITLE_GENERATION", "true").lower() == "true"
        config.meta_tags.auto_description_generation = os.getenv("AUTO_DESCRIPTION_GENERATION", "true").lower() == "true"
        
        # Load analytics settings
        config.analytics.google_analytics_id = os.getenv("GOOGLE_ANALYTICS_ID", "")
        config.analytics.google_search_console_id = os.getenv("GOOGLE_SEARCH_CONSOLE_ID", "")
        
        return config


# Global configuration instance
seo_config = SEOConfig.from_env()
