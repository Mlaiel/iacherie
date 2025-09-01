"""Content Optimization Module
Copyright (C) 2025 Fahed Mlaiel <mlaiel@live.de>

Advanced content optimization for distribution, SEO, metadata,
and format optimization across multiple platforms.
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..engines.base import BaseEngine
from ..analytics.seo import SEOAnalyzer
from ..services.platforms import PlatformService

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """
Content type enumeration"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    BLOG = "blog"
    SOCIAL_POST = "social_post"


class Platform(Enum):
    """Supported platforms"""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"


@dataclass
class OptimizedContent:
    """Optimized content result"""
    original_title: str
    optimized_title: str
    original_description: str
    optimized_description: str
    tags: List[str]
    hashtags: List[str]
    seo_keywords: List[str]
    platform_specific: Dict[str, Any]
    metadata: Dict[str, Any]
    format_recommendations: List[str]
    performance_prediction: Dict[str, float]


class ContentDistributionOptimizer(BaseEngine):
    """
Optimize content distribution across multiple platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform_service = PlatformService(config.get("platforms", {}))
        self.distribution_rules = self._load_distribution_rules()
        
    async def optimize_distribution_strategy(
        self,
        content_type: ContentType,
        target_audience: Dict[str, Any],
        content_metadata: Dict[str, Any]
    ) -> Dict[Platform, Dict[str, Any]]:
        """Optimize content distribution strategy across platforms"""
        
        # Analyze target audience
        audience_insights = await self._analyze_target_audience(target_audience)
        
        # Get platform recommendations
        platform_scores = await self._score_platforms(content_type, audience_insights)
        
        # Generate platform-specific optimizations
        distribution_plan = {}
        for platform, score in platform_scores.items():
            if score >= 0.6:  # Only include platforms with good fit
                optimization = await self._optimize_for_platform(
                    content_type, platform, content_metadata, audience_insights
                )
                distribution_plan[platform] = {
                    "score": score,
                    "optimization": optimization,
                    "best_times": await self._get_optimal_posting_times(platform, audience_insights),
                    "format_requirements": await self._get_platform_format_requirements(platform)
                }
        
        return distribution_plan
    
    async def _analyze_target_audience(self, target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze target audience for platform optimization"""
        
        insights = {
            "age_groups": target_audience.get("age_groups", []),
            "interests": target_audience.get("interests", []),
            "geographic_regions": target_audience.get("regions", []),
            "platform_preferences": {},
            "engagement_patterns": {},
            "content_preferences": {}
        }
        
        # Calculate platform preferences based on demographics
        age_ranges = insights["age_groups"]
        if "18-24" in age_ranges or "25-34" in age_ranges:
            insights["platform_preferences"]["tiktok"] = 0.9
            insights["platform_preferences"]["instagram"] = 0.8
            insights["platform_preferences"]["youtube"] = 0.7
        
        if "25-34" in age_ranges or "35-44" in age_ranges:
            insights["platform_preferences"]["instagram"] = 0.8
            insights["platform_preferences"]["facebook"] = 0.7
            insights["platform_preferences"]["linkedin"] = 0.6
        
        if "35-44" in age_ranges or "45-54" in age_ranges:
            insights["platform_preferences"]["facebook"] = 0.8
            insights["platform_preferences"]["linkedin"] = 0.7
            insights["platform_preferences"]["youtube"] = 0.6
        
        return insights
    
    async def _score_platforms(
        self,
        content_type: ContentType,
        audience_insights: Dict[str, Any]
    ) -> Dict[Platform, float]:
        """Score platforms based on content type and audience"""
        
        scores = {}
        
        # Content type weights
        type_weights = {
            ContentType.AUDIO: {
                Platform.SPOTIFY: 1.0,
                Platform.YOUTUBE: 0.8,
                Platform.SOUNDCLOUD: 0.9,
                Platform.INSTAGRAM: 0.6,
                Platform.TIKTOK: 0.7
            },
            ContentType.VIDEO: {
                Platform.YOUTUBE: 1.0,
                Platform.TIKTOK: 0.9,
                Platform.INSTAGRAM: 0.8,
                Platform.FACEBOOK: 0.7,
                Platform.TWITTER: 0.5
            },
            ContentType.IMAGE: {
                Platform.INSTAGRAM: 1.0,
                Platform.FACEBOOK: 0.8,
                Platform.TWITTER: 0.7,
                Platform.LINKEDIN: 0.6
            },
            ContentType.TEXT: {
                Platform.TWITTER: 1.0,
                Platform.LINKEDIN: 0.9,
                Platform.FACEBOOK: 0.7
            }
        }
        
        content_weights = type_weights.get(content_type, {})
        platform_preferences = audience_insights.get("platform_preferences", {})
        
        for platform in Platform:
            content_score = content_weights.get(platform, 0.0)
            audience_score = platform_preferences.get(platform.value, 0.5)
            
            # Combined score with weights
            final_score = (content_score * 0.6) + (audience_score * 0.4)
            scores[platform] = round(final_score, 2)
        
        return scores
    
    async def _optimize_for_platform(
        self,
        content_type: ContentType,
        platform: Platform,
        content_metadata: Dict[str, Any],
        audience_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate platform-specific optimization recommendations"""
        
        optimization = {
            "title_length": self._get_optimal_title_length(platform),
            "description_length": self._get_optimal_description_length(platform),
            "hashtag_count": self._get_optimal_hashtag_count(platform),
            "posting_frequency": self._get_optimal_posting_frequency(platform),
            "engagement_tactics": self._get_engagement_tactics(platform),
            "content_format": self._get_content_format_specs(platform, content_type)
        }
        
        return optimization
    
    async def _get_optimal_posting_times(
        self,
        platform: Platform,
        audience_insights: Dict[str, Any]
    ) -> List[str]:
        """Get optimal posting times for platform and audience"""
        
        # Default posting times by platform
        default_times = {
            Platform.INSTAGRAM: ["09:00", "11:00", "13:00", "17:00", "19:00"],
            Platform.TIKTOK: ["06:00", "10:00", "19:00", "20:00", "21:00"],
            Platform.YOUTUBE: ["14:00", "15:00", "20:00", "21:00"],
            Platform.TWITTER: ["08:00", "12:00", "17:00", "18:00"],
            Platform.FACEBOOK: ["09:00", "13:00", "15:00"],
            Platform.LINKEDIN: ["08:00", "10:00", "12:00", "14:00", "17:00"],
            Platform.SPOTIFY: ["08:00", "12:00", "17:00", "22:00"],
            Platform.SOUNDCLOUD: ["10:00", "14:00", "18:00", "21:00"]
        }
        
        return default_times.get(platform, ["12:00", "18:00"])
    
    async def _get_platform_format_requirements(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific format requirements"""
        
        requirements = {
            Platform.INSTAGRAM: {
                "video": {"aspect_ratio": "1:1 or 9:16", "max_duration": 60, "format": "MP4"},
                "image": {"aspect_ratio": "1:1 or 4:5", "min_resolution": "1080x1080"},
                "audio": {"format": "MP4 with video", "max_duration": 60}
            },
            Platform.TIKTOK: {
                "video": {"aspect_ratio": "9:16", "max_duration": 180, "format": "MP4"},
                "audio": {"format": "MP3/AAC", "sync_with_video": True}
            },
            Platform.YOUTUBE: {
                "video": {"aspect_ratio": "16:9", "max_duration": "unlimited", "format": "MP4"},
                "audio": {"format": "MP3/WAV", "min_quality": "128kbps"}
            },
            Platform.SPOTIFY: {
                "audio": {"format": "FLAC/WAV", "min_quality": "320kbps", "max_duration": "unlimited"}
            }
        }
        
        return requirements.get(platform, {})
    
    def _get_optimal_title_length(self, platform: Platform) -> int:
        """Get optimal title length for platform"""
        lengths = {
            Platform.YOUTUBE: 60,
            Platform.INSTAGRAM: 125,
            Platform.TIKTOK: 100,
            Platform.TWITTER: 280,
            Platform.FACEBOOK: 80,
            Platform.LINKEDIN: 150,
            Platform.SPOTIFY: 100,
            Platform.SOUNDCLOUD: 100
        }
        return lengths.get(platform, 100)
    
    def _get_optimal_description_length(self, platform: Platform) -> int:
        """
Get optimal description length for platform"""
        lengths = {
            Platform.YOUTUBE: 5000,
            Platform.INSTAGRAM: 2200,
            Platform.TIKTOK: 300,
            Platform.TWITTER: 280,
            Platform.FACEBOOK: 500,
            Platform.LINKEDIN: 1300,
            Platform.SPOTIFY: 256,
            Platform.SOUNDCLOUD: 1000
        }
        return lengths.get(platform, 500)
    
    def _get_optimal_hashtag_count(self, platform: Platform) -> int:
        """
Get optimal hashtag count for platform"""
        counts = {
            Platform.INSTAGRAM: 11,
            Platform.TIKTOK: 5,
            Platform.TWITTER: 2,
            Platform.FACEBOOK: 1,
            Platform.LINKEDIN: 3,
            Platform.YOUTUBE: 15,
            Platform.SPOTIFY: 0,
            Platform.SOUNDCLOUD: 5
        }
        return counts.get(platform, 3)
    
    def _get_optimal_posting_frequency(self, platform: Platform) -> str:
        """
Get optimal posting frequency for platform"""
        frequencies = {
            Platform.INSTAGRAM: "1-2 times per day",
            Platform.TIKTOK: "1-4 times per day",
            Platform.TWITTER: "3-5 times per day",
            Platform.FACEBOOK: "1 time per day",
            Platform.LINKEDIN: "1 time per day",
            Platform.YOUTUBE: "2-3 times per week",
            Platform.SPOTIFY: "1-2 times per week",
            Platform.SOUNDCLOUD: "2-3 times per week"
        }
        return frequencies.get(platform, "1 time per day")
    
    def _get_engagement_tactics(self, platform: Platform) -> List[str]:
        """Get platform-specific engagement tactics"""
        tactics = {
            Platform.INSTAGRAM: [
                "Use Stories for behind-the-scenes content",
                "Engage with comments within first hour",
                "Use relevant trending hashtags",
                "Post user-generated content",
                "Collaborate with influencers"
            ],
            Platform.TIKTOK: [
                "Jump on trending sounds and challenges",
                "Hook viewers in first 3 seconds",
                "Use trending hashtags and effects",
                "Engage with comments through video responses",
                "Post at trending times"
            ],
            Platform.YOUTUBE: [
                "Optimize thumbnails and titles",
                "Use end screens and cards",
                "Encourage subscriptions and bell notifications",
                "Respond to comments actively",
                "Create playlists for series content"
            ],
            Platform.SPOTIFY: [
                "Submit to playlist curators",
                "Create and promote your own playlists",
                "Use Spotify Canvas for visual appeal",
                "Collaborate with other artists",
                "Promote on social media"
            ]
        }
        return tactics.get(platform, ["Engage with your audience", "Post consistently"])
    
    def _get_content_format_specs(self, platform: Platform, content_type: ContentType) -> Dict[str, Any]:
        """Get content format specifications"""
        specs = {
            "resolution": "1080p minimum",
            "frame_rate": "30fps",
            "audio_quality": "128kbps minimum",
            "file_size": "Under 100MB",
            "duration": "Variable"
        }
        
        # Platform-specific adjustments
        if platform == Platform.TIKTOK:
            specs.update({
                "aspect_ratio": "9:16",
                "duration": "15-60 seconds optimal"
            })
        elif platform == Platform.YOUTUBE:
            specs.update({
                "aspect_ratio": "16:9",
                "duration": "8-15 minutes optimal for discovery"
            })
        elif platform == Platform.INSTAGRAM:
            if content_type == ContentType.VIDEO:
                specs.update({
                    "aspect_ratio": "1:1 or 9:16",
                    "duration": "15-30 seconds for feed, up to 60s for Reels"
                })
        
        return specs
    
    def _load_distribution_rules(self) -> Dict[str, Any]:
        """Load distribution rules and strategies"""
        return {
            "cross_posting_delay": 30,  # minutes between cross-posts
            "platform_priority": [
                Platform.YOUTUBE,
                Platform.INSTAGRAM,
                Platform.TIKTOK,
                Platform.SPOTIFY,
                Platform.TWITTER
            ],
            "content_type_mapping": {
                "music": [Platform.SPOTIFY, Platform.YOUTUBE, Platform.SOUNDCLOUD],
                "video": [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM],
                "image": [Platform.INSTAGRAM, Platform.FACEBOOK, Platform.TWITTER],
                "podcast": [Platform.SPOTIFY, Platform.YOUTUBE, Platform.SOUNDCLOUD]
            }
        }


class SEOOptimizer(BaseEngine):
    """Advanced SEO optimization for content"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.seo_analyzer = SEOAnalyzer(config.get("seo", {}))
        self.keyword_database = {}
        
    async def optimize_seo_content(
        self,
        title: str,
        description: str,
        content_type: ContentType,
        target_keywords: List[str] = None
    ) -> Dict[str, Any]:
        """Optimize content for SEO"""
        
        # Analyze current content
        current_analysis = await self.seo_analyzer.analyze_content(title, description)
        
        # Research keywords
        if not target_keywords:
            target_keywords = await self._research_keywords(title, content_type)
        
        # Optimize title
        optimized_title = await self._optimize_title(title, target_keywords)
        
        # Optimize description
        optimized_description = await self._optimize_description(description, target_keywords)
        
        # Generate additional SEO elements
        seo_elements = await self._generate_seo_elements(
            optimized_title, optimized_description, target_keywords
        )
        
        return {
            "original": {
                "title": title,
                "description": description
            },
            "optimized": {
                "title": optimized_title,
                "description": optimized_description
            },
            "keywords": {
                "primary": target_keywords[:3],
                "secondary": target_keywords[3:8],
                "long_tail": target_keywords[8:]
            },
            "seo_elements": seo_elements,
            "improvement_score": await self._calculate_improvement_score(
                current_analysis, optimized_title, optimized_description
            )
        }
    
    async def _research_keywords(self, title: str, content_type: ContentType) -> List[str]:
        """Research relevant keywords for content"""
        
        # Extract base keywords from title
        base_keywords = self._extract_keywords_from_text(title)
        
        # Add content-type specific keywords
        type_keywords = self._get_content_type_keywords(content_type)
        
        # Combine and rank keywords
        all_keywords = base_keywords + type_keywords
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in all_keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        return unique_keywords[:15]  # Top 15 keywords
    
    async def _optimize_title(self, title: str, keywords: List[str]) -> str:
        """
Optimize title for SEO"""
        
        # Ensure primary keyword is in title
        primary_keyword = keywords[0] if keywords else ""
        
        if primary_keyword and primary_keyword.lower() not in title.lower():
            # Add primary keyword naturally
            if len(title) + len(primary_keyword) + 3 <= 60:  # SEO title length limit
                title = f"{primary_keyword} - {title}"
            else:
                # Replace less important words
                title = f"{primary_keyword} {title[:50-len(primary_keyword)]}..."
        
        # Capitalize properly
        title = self._capitalize_title(title)
        
        # Ensure length is optimal (50-60 characters)
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    async def _optimize_description(self, description: str, keywords: List[str]) -> str:
        """Optimize description for SEO"""
        
        if not description:
            # Generate description from keywords
            description = self._generate_description_from_keywords(keywords)
        
        # Ensure keywords are naturally included
        optimized_desc = description
        
        for i, keyword in enumerate(keywords[:5]):  # Include top 5 keywords
            if keyword.lower() not in optimized_desc.lower():
                # Add keyword naturally
                if i == 0:  # Primary keyword in first sentence
                    optimized_desc = f"{keyword}: {optimized_desc}"
                else:
                    # Add to end if space allows
                    if len(optimized_desc) + len(keyword) + 10 <= 160:
                        optimized_desc += f" #{keyword.replace(' ', '')}"
        
        # Ensure optimal length (150-160 characters)
        if len(optimized_desc) > 160:
            optimized_desc = optimized_desc[:157] + "..."
        
        return optimized_desc
    
    async def _generate_seo_elements(
        self,
        title: str,
        description: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Generate additional SEO elements"""
        
        return {
            "meta_title": title,
            "meta_description": description,
            "schema_markup": self._generate_schema_markup(title, description),
            "og_tags": {
                "og:title": title,
                "og:description": description,
                "og:type": "music.song",  # Adjust based on content type
                "og:url": "",  # To be filled by platform
                "og:image": ""  # To be filled by platform
            },
            "twitter_cards": {
                "twitter:card": "summary_large_image",
                "twitter:title": title,
                "twitter:description": description
            },
            "canonical_url": "",  # To be filled by platform
            "alt_texts": self._generate_alt_texts(keywords),
            "heading_structure": self._generate_heading_structure(title, keywords)
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text"""
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "before", "after", "above", "below", "under", "between", "among"
        }
        
        # Split and clean words
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add phrases (2-3 word combinations)
        phrases = []
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i+1] not in stop_words:
                phrases.append(f"{words[i]} {words[i+1]}")
        
        return keywords + phrases
    
    def _get_content_type_keywords(self, content_type: ContentType) -> List[str]:
        """Get keywords specific to content type"""
        
        type_keywords = {
            ContentType.AUDIO: [
                "music", "song", "audio", "track", "sound", "melody", "rhythm",
                "beat", "instrumental", "vocals", "recording", "studio"
            ],
            ContentType.VIDEO: [
                "video", "visual", "film", "movie", "clip", "footage", "cinematic",
                "production", "entertainment", "media", "content"
            ],
            ContentType.IMAGE: [
                "image", "photo", "picture", "visual", "art", "graphic", "design",
                "photography", "creative", "aesthetic"
            ],
            ContentType.PODCAST: [
                "podcast", "audio", "talk", "discussion", "interview", "show",
                "episode", "series", "conversation", "storytelling"
            ]
        }
        
        return type_keywords.get(content_type, [])
    
    def _capitalize_title(self, title: str) -> str:
        """Properly capitalize title"""
        
        # Words that should not be capitalized (unless first/last word)
        small_words = {"a", "an", "and", "as", "at", "but", "by", "for", "if", 
                      "in", "nor", "of", "on", "or", "so", "the", "to", "up", "yet"}
        
        words = title.split()
        capitalized_words = []
        
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1 or word.lower() not in small_words:
                capitalized_words.append(word.capitalize())
            else:
                capitalized_words.append(word.lower())
        
        return " ".join(capitalized_words)
    
    def _generate_description_from_keywords(self, keywords: List[str]) -> str:
        """Generate description from keywords"""
        
        if not keywords:
            return "Professional content creation and optimization."
        
        primary_keywords = keywords[:3]
        description = f"Discover {primary_keywords[0]}"
        
        if len(primary_keywords) > 1:
            description += f" featuring {', '.join(primary_keywords[1:])}"
        
        description += ". Professional quality content optimized for maximum engagement."
        
        return description
    
    def _generate_schema_markup(self, title: str, description: str) -> Dict[str, Any]:
        """Generate schema.org markup"""
        
        return {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": title,
            "description": description,
            "creator": {
                "@type": "Person",
                "name": "Artist Name"  # To be filled dynamically
            },
            "dateCreated": "",  # To be filled dynamically
            "genre": "",  # To be filled based on content analysis
            "keywords": ""  # To be filled with comma-separated keywords
        }
    
    def _generate_alt_texts(self, keywords: List[str]) -> List[str]:
        """Generate alt text suggestions"""
        
        if not keywords:
            return ["Professional content image", "Creative media content"]
        
        return [
            f"{keywords[0]} - professional content",
            f"High-quality {keywords[0]} content",
            f"{keywords[0]} - creative media",
            f"Professional {keywords[0]} production"
        ]
    
    def _generate_heading_structure(self, title: str, keywords: List[str]) -> Dict[str, str]:
        """Generate SEO-optimized heading structure"""
        
        return {
            "h1": title,
            "h2": f"About This {keywords[0] if keywords else 'Content'}",
            "h3": f"{keywords[1] if len(keywords) > 1 else 'Features'} & Details",
            "h4": "Technical Specifications",
            "h5": "Related Content",
            "h6": "Additional Information"
        }
    
    async def _calculate_improvement_score(
        self,
        current_analysis: Dict[str, Any],
        optimized_title: str,
        optimized_description: str
    ) -> float:
        """Calculate SEO improvement score"""
        
        # Analyze optimized content
        new_analysis = await self.seo_analyzer.analyze_content(optimized_title, optimized_description)
        
        # Compare scores
        current_score = current_analysis.get("overall_score", 0)
        new_score = new_analysis.get("overall_score", 0)
        
        improvement = ((new_score - current_score) / max(current_score, 1)) * 100
        return round(max(0, improvement), 2)


class MetadataOptimizer(BaseEngine):
    """Advanced metadata optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
    async def optimize_metadata(
        self,
        content_type: ContentType,
        original_metadata: Dict[str, Any],
        target_platforms: List[Platform]
    ) -> Dict[str, Any]:
        """
Optimize metadata for multiple platforms"""
        
        optimized_metadata = {}
        
        for platform in target_platforms:
            platform_metadata = await self._optimize_for_platform_metadata(
                content_type, original_metadata, platform
            )
            optimized_metadata[platform.value] = platform_metadata
        
        # Generate universal metadata
        optimized_metadata["universal"] = await self._generate_universal_metadata(
            content_type, original_metadata
        )
        
        return optimized_metadata
    
    async def _optimize_for_platform_metadata(
        self,
        content_type: ContentType,
        metadata: Dict[str, Any],
        platform: Platform
    ) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        
        platform_metadata = metadata.copy()
        
        # Platform-specific optimizations
        if platform == Platform.SPOTIFY:
            platform_metadata.update({
                "explicit": metadata.get("explicit", False),
                "isrc": metadata.get("isrc", ""),
                "copyright": metadata.get("copyright", ""),
                "publishing": metadata.get("publishing", "")
            })
        
        elif platform == Platform.YOUTUBE:
            platform_metadata.update({
                "category": self._map_to_youtube_category(content_type),
                "license": "Standard YouTube License",
                "privacy": metadata.get("privacy", "public"),
                "allow_comments": True,
                "allow_ratings": True
            })
        
        elif platform == Platform.INSTAGRAM:
            platform_metadata.update({
                "location": metadata.get("location", ""),
                "people_tags": metadata.get("people_tags", []),
                "business_tools": metadata.get("business_tools", {})
            })
        
        return platform_metadata
    
    async def _generate_universal_metadata(
        self,
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate universal metadata applicable across platforms"""
        
        return {
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "creator": metadata.get("creator", ""),
            "creation_date": metadata.get("creation_date", ""),
            "duration": metadata.get("duration", 0),
            "file_size": metadata.get("file_size", 0),
            "format": metadata.get("format", ""),
            "quality": metadata.get("quality", ""),
            "tags": metadata.get("tags", []),
            "genre": metadata.get("genre", ""),
            "mood": metadata.get("mood", ""),
            "tempo": metadata.get("tempo", 0) if content_type == ContentType.AUDIO else None,
            "key": metadata.get("key", "") if content_type == ContentType.AUDIO else None,
            "language": metadata.get("language", "en"),
            "content_rating": metadata.get("content_rating", "all_ages"),
            "copyright_info": metadata.get("copyright_info", ""),
            "license_type": metadata.get("license_type", "proprietary")
        }
    
    def _map_to_youtube_category(self, content_type: ContentType) -> str:
        """Map content type to YouTube category"""
        
        mapping = {
            ContentType.AUDIO: "Music",
            ContentType.VIDEO: "Entertainment",
            ContentType.PODCAST: "Education",
            ContentType.BLOG: "People & Blogs"
        }
        
        return mapping.get(content_type, "Entertainment")


class FormatOptimizer(BaseEngine):
    """Content format optimization for different platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
    async def optimize_formats(
        self,
        content_type: ContentType,
        source_file_path: str,
        target_platforms: List[Platform]
    ) -> Dict[Platform, Dict[str, Any]]:
        """
Optimize content formats for target platforms"""
        
        format_recommendations = {}
        
        for platform in target_platforms:
            recommendations = await self._get_format_recommendations(
                content_type, platform, source_file_path
            )
            format_recommendations[platform] = recommendations
        
        return format_recommendations
    
    async def _get_format_recommendations(
        self,
        content_type: ContentType,
        platform: Platform,
        source_file: str
    ) -> Dict[str, Any]:
        """
Get format recommendations for specific platform"""
        
        if content_type == ContentType.AUDIO:
            return await self._get_audio_format_recommendations(platform, source_file)
        elif content_type == ContentType.VIDEO:
            return await self._get_video_format_recommendations(platform, source_file)
        elif content_type == ContentType.IMAGE:
            return await self._get_image_format_recommendations(platform, source_file)
        else:
            return {"format": "original", "optimization": "none"}
    
    async def _get_audio_format_recommendations(
        self,
        platform: Platform,
        source_file: str
    ) -> Dict[str, Any]:
        """Get audio format recommendations"""
        
        recommendations = {
            Platform.SPOTIFY: {
                "format": "FLAC or WAV",
                "bitrate": "1411 kbps (lossless)",
                "sample_rate": "44.1 kHz",
                "bit_depth": "16-bit",
                "channels": "Stereo",
                "loudness": "-14 LUFS"
            },
            Platform.YOUTUBE: {
                "format": "MP3 or AAC",
                "bitrate": "320 kbps",
                "sample_rate": "44.1 kHz",
                "channels": "Stereo",
                "video_wrapper": "MP4 with static image"
            },
            Platform.SOUNDCLOUD: {
                "format": "MP3",
                "bitrate": "320 kbps",
                "sample_rate": "44.1 kHz",
                "channels": "Stereo",
                "max_file_size": "2GB"
            }
        }
        
        return recommendations.get(platform, {
            "format": "MP3",
            "bitrate": "320 kbps",
            "sample_rate": "44.1 kHz"
        })
    
    async def _get_video_format_recommendations(
        self,
        platform: Platform,
        source_file: str
    ) -> Dict[str, Any]:
        """Get video format recommendations"""
        
        recommendations = {
            Platform.YOUTUBE: {
                "format": "MP4",
                "codec": "H.264",
                "resolution": "1920x1080 (1080p)",
                "frame_rate": "30fps or 60fps",
                "bitrate": "8 Mbps (1080p)",
                "audio": "AAC 128kbps"
            },
            Platform.TIKTOK: {
                "format": "MP4",
                "codec": "H.264",
                "resolution": "1080x1920 (9:16)",
                "frame_rate": "30fps",
                "bitrate": "3-5 Mbps",
                "duration": "15-180 seconds"
            },
            Platform.INSTAGRAM: {
                "format": "MP4",
                "codec": "H.264",
                "resolution": "1080x1080 (1:1) or 1080x1920 (9:16)",
                "frame_rate": "30fps",
                "bitrate": "3 Mbps",
                "duration": "3-60 seconds"
            }
        }
        
        return recommendations.get(platform, {
            "format": "MP4",
            "codec": "H.264",
            "resolution": "1920x1080"
        })
    
    async def _get_image_format_recommendations(
        self,
        platform: Platform,
        source_file: str
    ) -> Dict[str, Any]:
        """Get image format recommendations"""
        
        recommendations = {
            Platform.INSTAGRAM: {
                "format": "JPEG",
                "resolution": "1080x1080 (square) or 1080x1350 (portrait)",
                "quality": "85-95%",
                "color_profile": "sRGB",
                "max_file_size": "8MB"
            },
            Platform.FACEBOOK: {
                "format": "JPEG",
                "resolution": "1200x630 (link) or 1080x1080 (post)",
                "quality": "85%",
                "color_profile": "sRGB"
            },
            Platform.TWITTER: {
                "format": "JPEG or PNG",
                "resolution": "1200x675 (16:9) or 1080x1080 (square)",
                "quality": "85%",
                "max_file_size": "5MB"
            }
        }
        
        return recommendations.get(platform, {
            "format": "JPEG",
            "resolution": "1080x1080",
            "quality": "85%"
        })
