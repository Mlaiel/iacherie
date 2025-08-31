"""Content Optimizer for multi-platform distribution.
Optimizes content for each platform's specific requirements and audience.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

from .models.distribution_models import ContentMetadata, ContentType
from .utils.content_processors import (
    VideoProcessor, AudioProcessor, ImageProcessor, TextProcessor
)
from .utils.platform_rules import PLATFORM_OPTIMIZATION_RULES

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """    Advanced content optimizer that adapts content for each platform's 
    specific requirements, algorithms, and audience preferences.
    """    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        
        # Platform-specific optimization rules
        self.platform_rules = PLATFORM_OPTIMIZATION_RULES
        
        logger.info("Content Optimizer initialized with all platform rules")
    
    async def optimize_for_platform(
        self,
        content_metadata: ContentMetadata,
        platform_name: str
    ) -> ContentMetadata:
        """Optimize content for a specific platform."""        try:
            platform_rules = self.platform_rules.get(platform_name.lower(), {})
            if not platform_rules:
                logger.warning(f"No optimization rules found for {platform_name}")
                return content_metadata
            
            # Create optimized copy
            optimized = ContentMetadata(**content_metadata.to_dict())
            
            # Apply text optimizations
            optimized = await self._optimize_text_content(optimized, platform_rules)
            
            # Apply media optimizations
            optimized = await self._optimize_media_content(optimized, platform_rules)
            
            # Apply SEO optimizations
            optimized = await self._optimize_seo_elements(optimized, platform_rules)
            
            # Apply scheduling optimizations
            optimized = await self._optimize_timing_elements(optimized, platform_rules)
            
            # Apply monetization optimizations
            optimized = await self._optimize_monetization_elements(optimized, platform_rules)
            
            logger.info(f"Content optimized for {platform_name}")
            return optimized
            
        except Exception as e:
            logger.error(f"Content optimization failed for {platform_name}: {e}")
            return content_metadata  # Return original on error
    
    async def _optimize_text_content(
        self,
        content_metadata: ContentMetadata,
        platform_rules: Dict[str, Any]
    ) -> ContentMetadata:
        """Optimize text content based on platform rules."""        try:
            # Title optimization
            if "title" in platform_rules:
                title_rules = platform_rules["title"]
                content_metadata.title = await self.text_processor.optimize_title(
                    content_metadata.title,
                    max_length=title_rules.get("max_length", 100),
                    style=title_rules.get("style", "neutral"),
                    keywords=content_metadata.seo_keywords
                )
            
            # Description optimization
            if "description" in platform_rules:
                desc_rules = platform_rules["description"]
                content_metadata.description = await self.text_processor.optimize_description(
                    content_metadata.description,
                    max_length=desc_rules.get("max_length", 2000),
                    style=desc_rules.get("style", "informative"),
                    include_cta=desc_rules.get("include_cta", True)
                )
            
            # Hashtag optimization
            if "hashtags" in platform_rules:
                hashtag_rules = platform_rules["hashtags"]
                content_metadata.hashtags = await self.text_processor.optimize_hashtags(
                    content_metadata.hashtags,
                    max_count=hashtag_rules.get("max_count", 30),
                    trending_boost=hashtag_rules.get("trending_boost", True),
                    platform_specific=hashtag_rules.get("platform_specific", [])
                )
            
            # Tags optimization
            if "tags" in platform_rules:
                tag_rules = platform_rules["tags"]
                content_metadata.tags = await self.text_processor.optimize_tags(
                    content_metadata.tags,
                    max_count=tag_rules.get("max_count", 10),
                    category_specific=tag_rules.get("category_specific", [])
                )
            
            return content_metadata
            
        except Exception as e:
            logger.error(f"Text optimization failed: {e}")
            return content_metadata
    
    async def _optimize_media_content(
        self,
        content_metadata: ContentMetadata,
        platform_rules: Dict[str, Any]
    ) -> ContentMetadata:
        """Optimize media content based on platform rules."""        try:
            if not content_metadata.file_path:
                return content_metadata
            
            content_type = content_metadata.content_type
            
            # Video optimization
            if content_type == ContentType.VIDEO:
                if "video" in platform_rules:
                    video_rules = platform_rules["video"]
                    optimization_result = await self.video_processor.optimize_video(
                        content_metadata.file_path,
                        max_duration=video_rules.get("max_duration", 600),
                        target_resolution=video_rules.get("target_resolution", "1080p"),
                        target_format=video_rules.get("target_format", "mp4"),
                        bitrate=video_rules.get("bitrate", 2000),
                        aspect_ratio=video_rules.get("aspect_ratio", "16:9")
                    )
                    
                    if optimization_result:
                        content_metadata.file_path = optimization_result["file_path"]
                        content_metadata.resolution = optimization_result["resolution"]
                        content_metadata.format = optimization_result["format"]
                        content_metadata.duration = optimization_result["duration"]
                        content_metadata.size = optimization_result["file_size"]
            
            # Audio optimization
            elif content_type == ContentType.AUDIO:
                if "audio" in platform_rules:
                    audio_rules = platform_rules["audio"]
                    optimization_result = await self.audio_processor.optimize_audio(
                        content_metadata.file_path,
                        max_duration=audio_rules.get("max_duration", 3600),
                        target_format=audio_rules.get("target_format", "mp3"),
                        bitrate=audio_rules.get("bitrate", 320),
                        sample_rate=audio_rules.get("sample_rate", 44100)
                    )
                    
                    if optimization_result:
                        content_metadata.file_path = optimization_result["file_path"]
                        content_metadata.format = optimization_result["format"]
                        content_metadata.duration = optimization_result["duration"]
                        content_metadata.size = optimization_result["file_size"]
                        content_metadata.bitrate = optimization_result["bitrate"]
            
            # Image optimization
            elif content_type == ContentType.IMAGE:
                if "image" in platform_rules:
                    image_rules = platform_rules["image"]
                    optimization_result = await self.image_processor.optimize_image(
                        content_metadata.file_path,
                        max_width=image_rules.get("max_width", 1920),
                        max_height=image_rules.get("max_height", 1080),
                        target_format=image_rules.get("target_format", "jpg"),
                        quality=image_rules.get("quality", 85),
                        aspect_ratio=image_rules.get("aspect_ratio", None)
                    )
                    
                    if optimization_result:
                        content_metadata.file_path = optimization_result["file_path"]
                        content_metadata.resolution = optimization_result["resolution"]
                        content_metadata.format = optimization_result["format"]
                        content_metadata.size = optimization_result["file_size"]
            
            return content_metadata
            
        except Exception as e:
            logger.error(f"Media optimization failed: {e}")
            return content_metadata
    
    async def _optimize_seo_elements(
        self,
        content_metadata: ContentMetadata,
        platform_rules: Dict[str, Any]
    ) -> ContentMetadata:
        """Optimize SEO elements for platform discovery."""        try:
            if "seo" in platform_rules:
                seo_rules = platform_rules["seo"]
                
                # Optimize SEO keywords
                if content_metadata.seo_keywords:
                    optimized_keywords = await self.text_processor.optimize_seo_keywords(
                        content_metadata.seo_keywords,
                        max_count=seo_rules.get("max_keywords", 20),
                        platform_boost=seo_rules.get("platform_boost", [])
                    )
                    content_metadata.seo_keywords = optimized_keywords
                
                # Add platform-specific keywords
                if "recommended_keywords" in seo_rules:
                    content_metadata.seo_keywords.extend(
                        seo_rules["recommended_keywords"][:5]
                    )
                    content_metadata.seo_keywords = list(set(content_metadata.seo_keywords))  # Remove duplicates
                
                # Optimize category selection
                if "categories" in seo_rules and not content_metadata.category:
                    content_metadata.category = await self._auto_select_category(
                        content_metadata,
                        seo_rules["categories"]
                    )
            
            return content_metadata
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            return content_metadata
    
    async def _optimize_timing_elements(
        self,
        content_metadata: ContentMetadata,
        platform_rules: Dict[str, Any]
    ) -> ContentMetadata:
        """Optimize timing-related elements."""        try:
            if "timing" in platform_rules:
                timing_rules = platform_rules["timing"]
                
                # Set expected performance based on optimal timing
                if "peak_hours" in timing_rules:
                    current_hour = datetime.now().hour
                    peak_hours = timing_rules["peak_hours"]
                    
                    if current_hour in peak_hours:
                        # Boost expected performance during peak hours
                        if content_metadata.expected_reach:
                            content_metadata.expected_reach = int(content_metadata.expected_reach * 1.3)
                        if content_metadata.expected_engagement_rate:
                            content_metadata.expected_engagement_rate *= 1.2
                
                # Add optimal posting recommendations to metadata
                if "optimal_days" in timing_rules:
                    if not hasattr(content_metadata, 'timing_recommendations'):
                        content_metadata.timing_recommendations = {}
                    content_metadata.timing_recommendations["optimal_days"] = timing_rules["optimal_days"]
            
            return content_metadata
            
        except Exception as e:
            logger.error(f"Timing optimization failed: {e}")
            return content_metadata
    
    async def _optimize_monetization_elements(
        self,
        content_metadata: ContentMetadata,
        platform_rules: Dict[str, Any]
    ) -> ContentMetadata:
        """Optimize monetization settings for platform."""        try:
            if "monetization" in platform_rules and content_metadata.monetization_enabled:
                monetization_rules = platform_rules["monetization"]
                
                # Set platform-specific revenue sharing
                if "revenue_share" in monetization_rules:
                    platform_share = monetization_rules["revenue_share"]
                    content_metadata.revenue_sharing["platform"] = platform_share
                    content_metadata.revenue_sharing["creator"] = 100 - platform_share
                
                # Add platform-specific monetization features
                if "features" in monetization_rules:
                    features = monetization_rules["features"]
                    if not content_metadata.sponsorship_info:
                        content_metadata.sponsorship_info = {}
                    content_metadata.sponsorship_info["available_features"] = features
                
                # Set minimum requirements for monetization
                if "requirements" in monetization_rules:
                    requirements = monetization_rules["requirements"]
                    content_metadata.sponsorship_info["requirements"] = requirements
            
            return content_metadata
            
        except Exception as e:
            logger.error(f"Monetization optimization failed: {e}")
            return content_metadata
    
    async def _auto_select_category(
        self,
        content_metadata: ContentMetadata,
        available_categories: List[str]
    ) -> Optional[str]:
        """Automatically select the best category for content."""        try:
            # Simple keyword-based category selection
            content_text = f"{content_metadata.title} {content_metadata.description}".lower()
            
            category_keywords = {
                "entertainment": ["fun", "funny", "entertainment", "comedy", "humor"],
                "education": ["learn", "tutorial", "educational", "how-to", "guide"],
                "technology": ["tech", "technology", "software", "AI", "digital"],
                "lifestyle": ["lifestyle", "life", "personal", "daily", "routine"],
                "music": ["music", "song", "audio", "sound", "beats"],
                "gaming": ["game", "gaming", "play", "player", "stream"],
                "sports": ["sport", "fitness", "workout", "exercise", "health"],
                "business": ["business", "entrepreneur", "startup", "professional"]
            }
            
            best_category = None
            max_matches = 0
            
            for category, keywords in category_keywords.items():
                if category.lower() in [cat.lower() for cat in available_categories]:
                    matches = sum(1 for keyword in keywords if keyword in content_text)
                    if matches > max_matches:
                        max_matches = matches
                        best_category = category
            
            return best_category if best_category else available_categories[0]
            
        except Exception as e:
            logger.error(f"Auto category selection failed: {e}")
            return available_categories[0] if available_categories else None
    
    async def get_optimization_suggestions(
        self,
        content_metadata: ContentMetadata,
        platform_name: str
    ) -> Dict[str, Any]:
        """Get optimization suggestions without applying them."""        try:
            platform_rules = self.platform_rules.get(platform_name.lower(), {})
            suggestions = {
                "text_optimizations": [],
                "media_optimizations": [],
                "seo_improvements": [],
                "timing_recommendations": [],
                "monetization_tips": []
            }
            
            # Text suggestions
            if "title" in platform_rules:
                title_rules = platform_rules["title"]
                if len(content_metadata.title) > title_rules.get("max_length", 100):
                    suggestions["text_optimizations"].append({
                        "type": "title_length",
                        "current": len(content_metadata.title),
                        "recommended": title_rules.get("max_length", 100),
                        "suggestion": "Title is too long for optimal performance"
                    })
            
            # SEO suggestions
            if len(content_metadata.hashtags) == 0:
                suggestions["seo_improvements"].append({
                    "type": "missing_hashtags",
                    "suggestion": "Add relevant hashtags to improve discoverability"
                })
            
            # Timing suggestions
            if "timing" in platform_rules:
                timing_rules = platform_rules["timing"]
                if "peak_hours" in timing_rules:
                    suggestions["timing_recommendations"].append({
                        "type": "optimal_hours",
                        "peak_hours": timing_rules["peak_hours"],
                        "suggestion": f"Best posting hours: {timing_rules['peak_hours']}"
                    })
            
            # Monetization suggestions
            if content_metadata.monetization_enabled and "monetization" in platform_rules:
                monetization_rules = platform_rules["monetization"]
                if "requirements" in monetization_rules:
                    suggestions["monetization_tips"].append({
                        "type": "requirements",
                        "requirements": monetization_rules["requirements"],
                        "suggestion": "Ensure you meet monetization requirements"
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {e}")
            return {"error": str(e)}
    
    async def batch_optimize(
        self,
        content_list: List[ContentMetadata],
        target_platforms: List[str]
    ) -> Dict[str, List[ContentMetadata]]:
        """Optimize multiple content pieces for multiple platforms."""        try:
            results = {}
            
            for platform in target_platforms:
                platform_results = []
                
                for content in content_list:
                    try:
                        optimized = await self.optimize_for_platform(content, platform)
                        platform_results.append(optimized)
                    except Exception as e:
                        logger.error(f"Batch optimization failed for {platform}: {e}")
                        platform_results.append(content)  # Use original on error
                
                results[platform] = platform_results
            
            logger.info(f"Batch optimization completed for {len(content_list)} content pieces across {len(target_platforms)} platforms")
            return results
            
        except Exception as e:
            logger.error(f"Batch optimization failed: {e}")
            return {}

# Platform-specific optimization rules
PLATFORM_OPTIMIZATION_RULES = {
    "youtube": {
        "title": {"max_length": 100, "style": "engaging"},
        "description": {"max_length": 5000, "include_cta": True},
        "hashtags": {"max_count": 15, "trending_boost": True},
        "video": {
            "max_duration": 43200,  # 12 hours
            "target_resolution": "1080p",
            "aspect_ratio": "16:9",
            "target_format": "mp4"
        },
        "seo": {
            "max_keywords": 20,
            "categories": ["Entertainment", "Education", "Technology", "Gaming", "Music"]
        },
        "timing": {"peak_hours": [14, 17, 20]},
        "monetization": {"revenue_share": 45, "features": ["ads", "memberships", "super_chat"]}
    },
    
    "instagram": {
        "title": {"max_length": 2200, "style": "casual"},
        "description": {"max_length": 2200, "include_cta": True},
        "hashtags": {"max_count": 30, "trending_boost": True},
        "image": {
            "max_width": 1080,
            "max_height": 1350,
            "aspect_ratio": "4:5",
            "target_format": "jpg"
        },
        "video": {
            "max_duration": 60,
            "target_resolution": "1080p",
            "aspect_ratio": "9:16",
            "target_format": "mp4"
        },
        "timing": {"peak_hours": [11, 13, 17]},
        "monetization": {"revenue_share": 45, "features": ["reels_bonus", "branded_content"]}
    },
    
    "tiktok": {
        "title": {"max_length": 150, "style": "trendy"},
        "description": {"max_length": 300, "include_cta": True},
        "hashtags": {"max_count": 100, "trending_boost": True},
        "video": {
            "max_duration": 180,
            "target_resolution": "1080p",
            "aspect_ratio": "9:16",
            "target_format": "mp4"
        },
        "timing": {"peak_hours": [18, 19, 20]},
        "monetization": {"revenue_share": 50, "features": ["creator_fund", "live_gifts"]}
    },
    
    "twitter": {
        "title": {"max_length": 280, "style": "conversational"},
        "description": {"max_length": 280, "include_cta": False},
        "hashtags": {"max_count": 2, "trending_boost": True},
        "image": {
            "max_width": 1200,
            "max_height": 675,
            "aspect_ratio": "16:9",
            "target_format": "jpg"
        },
        "video": {
            "max_duration": 140,
            "target_resolution": "720p",
            "aspect_ratio": "16:9"
        },
        "timing": {"peak_hours": [9, 12, 17]}
    },
    
    "facebook": {
        "title": {"max_length": 255, "style": "engaging"},
        "description": {"max_length": 63206, "include_cta": True},
        "hashtags": {"max_count": 20, "trending_boost": False},
        "video": {
            "max_duration": 14400,  # 4 hours
            "target_resolution": "1080p",
            "aspect_ratio": "16:9"
        },
        "timing": {"peak_hours": [9, 13, 15]},
        "monetization": {"revenue_share": 55, "features": ["ad_breaks", "fan_subscriptions"]}
    },
    
    "linkedin": {
        "title": {"max_length": 150, "style": "professional"},
        "description": {"max_length": 3000, "include_cta": True},
        "hashtags": {"max_count": 3, "trending_boost": False},
        "image": {
            "max_width": 1200,
            "max_height": 627,
            "aspect_ratio": "1.91:1"
        },
        "timing": {"peak_hours": [9, 12, 17]},
        "monetization": {"revenue_share": 0, "features": ["sponsored_content"]}
    },
    
    "pinterest": {
        "title": {"max_length": 100, "style": "descriptive"},
        "description": {"max_length": 500, "include_cta": True},
        "hashtags": {"max_count": 20, "trending_boost": False},
        "image": {
            "max_width": 1000,
            "max_height": 1500,
            "aspect_ratio": "2:3",
            "target_format": "jpg"
        },
        "timing": {"peak_hours": [20, 21, 22]},
        "monetization": {"revenue_share": 0, "features": ["shopping_ads", "affiliate"]}
    },
    
    "spotify": {
        "title": {"max_length": 100, "style": "descriptive"},
        "description": {"max_length": 256, "include_cta": False},
        "tags": {"max_count": 10, "category_specific": ["genre", "mood", "energy"]},
        "audio": {
            "max_duration": 7200,  # 2 hours
            "target_format": "mp3",
            "bitrate": 320,
            "sample_rate": 44100
        },
        "timing": {"peak_hours": [17, 19, 21]},
        "monetization": {"revenue_share": 70, "features": ["streaming_royalties"]}
    },
    
    "twitch": {
        "title": {"max_length": 140, "style": "engaging"},
        "description": {"max_length": 300, "include_cta": True},
        "hashtags": {"max_count": 5, "trending_boost": True},
        "video": {
            "target_resolution": "1080p",
            "aspect_ratio": "16:9",
            "bitrate": 6000
        },
        "timing": {"peak_hours": [19, 20, 21]},
        "monetization": {"revenue_share": 50, "features": ["bits", "subscriptions", "ads"]}
    },
    
    "discord": {
        "title": {"max_length": 256, "style": "community"},
        "description": {"max_length": 2000, "include_cta": False},
        "image": {
            "max_width": 4096,
            "max_height": 4096,
            "target_format": "png"
        },
        "timing": {"peak_hours": [18, 19, 20]},
        "monetization": {"revenue_share": 10, "features": ["server_boosting", "nitro"]}
    }
}
