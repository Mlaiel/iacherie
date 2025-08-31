"""Content Optimizer - AI-Powered Content Optimization Engine

Advanced AI-driven content optimization system for cross-platform distribution.
Provides platform-specific content adaptation, SEO optimization, and engagement prediction.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.
"""from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
import re
import json
from datetime import datetime, timedelta
import hashlib
import numpy as np
from decimal import Decimal

logger = logging.getLogger(__name__)

class OptimizationType(str, Enum):
    """Content optimization types"""    SEO_KEYWORDS = "seo_keywords"
    HASHTAGS = "hashtags"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_OPTIMIZATION = "description_optimization"
    THUMBNAIL_OPTIMIZATION = "thumbnail_optimization"
    TIMING_OPTIMIZATION = "timing_optimization"
    AUDIENCE_TARGETING = "audience_targeting"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    PLATFORM_ADAPTATION = "platform_adaptation"

class ContentType(str, Enum):
    """Content types for optimization"""    MUSIC_TRACK = "music_track"
    MUSIC_ALBUM = "music_album"
    VIDEO_CONTENT = "video_content"
    PODCAST_EPISODE = "podcast_episode"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    LIVE_STREAM = "live_stream"
    SHORT_FORM_VIDEO = "short_form_video"

class PlatformTarget(str, Enum):
    """Target platforms for optimization"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    INSTAGRAM = "instagram"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"

@dataclass
class OptimizationRequest:
    """Request for content optimization"""    content_id: str
    content_type: ContentType
    target_platforms: List[PlatformTarget]
    original_title: str
    original_description: Optional[str] = None
    original_tags: Optional[List[str]] = field(default_factory=list)
    genre: Optional[str] = None
    target_audience: Optional[str] = None
    content_language: str = "en"
    optimization_goals: List[OptimizationType] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

@dataclass
class OptimizationResult:
    """Result of content optimization"""    content_id: str
    success: bool
    platform_optimizations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    seo_score: Optional[float] = None
    engagement_prediction: Optional[Dict[str, float]] = field(default_factory=dict)
    optimization_applied: List[OptimizationType] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: Optional[float] = None

@dataclass
class PlatformConstraints:
    """Platform-specific constraints and requirements"""    max_title_length: int
    max_description_length: int
    max_tags_count: int
    max_tag_length: int
    supported_hashtags: bool = True
    recommended_aspect_ratio: Optional[str] = None
    max_video_duration: Optional[int] = None  # seconds
    min_video_duration: Optional[int] = None  # seconds
    character_limits: Optional[Dict[str, int]] = field(default_factory=dict)
    forbidden_words: List[str] = field(default_factory=list)
    required_elements: List[str] = field(default_factory=list)

class ContentOptimizer:
    """    Enterprise-grade AI-powered content optimization engine
    
    Provides comprehensive content optimization for cross-platform distribution
    including SEO, engagement prediction, and platform-specific adaptations.
    """    
    # Platform constraints database
    PLATFORM_CONSTRAINTS = {
        PlatformTarget.YOUTUBE: PlatformConstraints(
            max_title_length=100,
            max_description_length=5000,
            max_tags_count=500,
            max_tag_length=30,
            supported_hashtags=True,
            recommended_aspect_ratio="16:9",
            max_video_duration=43200,  # 12 hours
            character_limits={"title": 100, "description": 5000}
        ),
        PlatformTarget.INSTAGRAM: PlatformConstraints(
            max_title_length=150,
            max_description_length=2200,
            max_tags_count=30,
            max_tag_length=100,
            supported_hashtags=True,
            recommended_aspect_ratio="1:1",
            max_video_duration=60,
            character_limits={"caption": 2200}
        ),
        PlatformTarget.TIKTOK: PlatformConstraints(
            max_title_length=150,
            max_description_length=2200,
            max_tags_count=100,
            max_tag_length=100,
            supported_hashtags=True,
            recommended_aspect_ratio="9:16",
            max_video_duration=300,  # 5 minutes
            min_video_duration=15,
            character_limits={"description": 2200}
        ),
        PlatformTarget.SPOTIFY: PlatformConstraints(
            max_title_length=200,
            max_description_length=1000,
            max_tags_count=50,
            max_tag_length=50,
            supported_hashtags=False,
            character_limits={"title": 200, "description": 1000}
        ),
        PlatformTarget.TWITTER: PlatformConstraints(
            max_title_length=280,
            max_description_length=280,
            max_tags_count=10,
            max_tag_length=100,
            supported_hashtags=True,
            character_limits={"tweet": 280}
        )
    }
    
    # SEO keywords database (simplified)
    SEO_KEYWORDS = {
        "music": ["music", "song", "track", "artist", "musician", "band", "album", "single", "release"],
        "video": ["video", "watch", "latest", "new", "trending", "viral", "entertainment"],
        "podcast": ["podcast", "episode", "listen", "audio", "discussion", "interview"],
        "entertainment": ["entertainment", "fun", "exciting", "amazing", "incredible", "awesome"]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def optimize_content(self, request: OptimizationRequest) -> OptimizationResult:
        """        Optimize content for cross-platform distribution
        
        Args:
            request: Optimization request with content details
            
        Returns:
            OptimizationResult: Comprehensive optimization results
        """        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting content optimization for {request.content_id}")
            
            result = OptimizationResult(
                content_id=request.content_id,
                success=True
            )
            
            # Apply optimizations for each target platform
            for platform in request.target_platforms:
                platform_optimization = await self._optimize_for_platform(
                    request, platform
                )
                result.platform_optimizations[platform.value] = platform_optimization
            
            # Apply general optimizations
            if OptimizationType.SEO_KEYWORDS in request.optimization_goals:
                await self._apply_seo_optimization(request, result)
            
            if OptimizationType.ENGAGEMENT_PREDICTION in request.optimization_goals:
                await self._predict_engagement(request, result)
            
            if OptimizationType.TIMING_OPTIMIZATION in request.optimization_goals:
                await self._optimize_timing(request, result)
            
            # Calculate processing time
            end_time = datetime.utcnow()
            result.processing_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Content optimization completed for {request.content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return OptimizationResult(
                content_id=request.content_id,
                success=False,
                warnings=[f"Optimization failed: {str(e)}"]
            )
    
    async def _optimize_for_platform(
        self, 
        request: OptimizationRequest, 
        platform: PlatformTarget
    ) -> Dict[str, Any]:
        """Optimize content for specific platform"""        
        constraints = self.PLATFORM_CONSTRAINTS.get(platform)
        if not constraints:
            return {"error": f"Platform {platform.value} not supported"}
        
        optimization = {
            "platform": platform.value,
            "original_title": request.original_title,
            "original_description": request.original_description,
            "optimized_title": "",
            "optimized_description": "",
            "optimized_tags": [],
            "hashtags": [],
            "seo_keywords": [],
            "recommendations": [],
            "warnings": []
        }
        
        # Optimize title
        optimized_title = await self._optimize_title(
            request.original_title, 
            constraints, 
            platform,
            request.content_type
        )
        optimization["optimized_title"] = optimized_title
        
        # Optimize description
        if request.original_description:
            optimized_description = await self._optimize_description(
                request.original_description,
                constraints,
                platform,
                request.content_type
            )
            optimization["optimized_description"] = optimized_description
        
        # Generate hashtags if supported
        if constraints.supported_hashtags:
            hashtags = await self._generate_hashtags(
                request, 
                constraints, 
                platform
            )
            optimization["hashtags"] = hashtags
        
        # Generate SEO keywords
        seo_keywords = await self._generate_seo_keywords(
            request, 
            platform
        )
        optimization["seo_keywords"] = seo_keywords
        
        # Add platform-specific recommendations
        recommendations = await self._get_platform_recommendations(
            request, 
            platform
        )
        optimization["recommendations"] = recommendations
        
        return optimization
    
    async def _optimize_title(
        self, 
        original_title: str, 
        constraints: PlatformConstraints,
        platform: PlatformTarget,
        content_type: ContentType
    ) -> str:
        """Optimize title for platform constraints"""        
        title = original_title
        
        # Truncate if too long
        if len(title) > constraints.max_title_length:
            title = title[:constraints.max_title_length - 3] + "..."
        
        # Add platform-specific elements
        if platform == PlatformTarget.YOUTUBE:
            if content_type == ContentType.MUSIC_TRACK:
                if "Official" not in title and "Music Video" not in title:
                    if len(title) + 18 <= constraints.max_title_length:
                        title += " (Official Music Video)"
        
        elif platform == PlatformTarget.TIKTOK:
            # TikTok prefers shorter, catchier titles
            if len(title) > 50:
                # Extract key words
                words = title.split()
                if len(words) > 5:
                    title = " ".join(words[:5]) + "..."
        
        return title
    
    async def _optimize_description(
        self,
        original_description: str,
        constraints: PlatformConstraints,
        platform: PlatformTarget,
        content_type: ContentType
    ) -> str:
        """Optimize description for platform constraints"""        
        description = original_description
        
        # Truncate if too long
        if len(description) > constraints.max_description_length:
            description = description[:constraints.max_description_length - 3] + "..."
        
        # Add platform-specific elements
        if platform == PlatformTarget.YOUTUBE:
            # Add standard YouTube elements
            if content_type == ContentType.MUSIC_TRACK:
                footer = "\n\n🎵 Follow for more music!\n#Music #NewRelease"
                if len(description) + len(footer) <= constraints.max_description_length:
                    description += footer
        
        elif platform == PlatformTarget.INSTAGRAM:
            # Add call-to-action for Instagram
            if "follow" not in description.lower():
                cta = "\n\nFollow for more! 💫"
                if len(description) + len(cta) <= constraints.max_description_length:
                    description += cta
        
        return description
    
    async def _generate_hashtags(
        self,
        request: OptimizationRequest,
        constraints: PlatformConstraints,
        platform: PlatformTarget
    ) -> List[str]:
        """Generate platform-specific hashtags"""        
        hashtags = []
        
        # Base hashtags based on content type
        if request.content_type == ContentType.MUSIC_TRACK:
            base_hashtags = ["#music", "#newmusic", "#song", "#artist"]
        elif request.content_type == ContentType.VIDEO_CONTENT:
            base_hashtags = ["#video", "#content", "#creator"]
        elif request.content_type == ContentType.PODCAST_EPISODE:
            base_hashtags = ["#podcast", "#audio", "#listen"]
        else:
            base_hashtags = ["#content", "#creative"]
        
        hashtags.extend(base_hashtags)
        
        # Add genre-specific hashtags
        if request.genre:
            genre_tag = f"#{request.genre.lower().replace(' ', '')}"
            if genre_tag not in hashtags:
                hashtags.append(genre_tag)
        
        # Add platform-specific hashtags
        if platform == PlatformTarget.TIKTOK:
            hashtags.extend(["#fyp", "#foryoupage", "#viral"])
        elif platform == PlatformTarget.INSTAGRAM:
            hashtags.extend(["#instagood", "#follow", "#like4like"])
        elif platform == PlatformTarget.YOUTUBE:
            hashtags.extend(["#youtube", "#subscribe", "#newvideo"])
        
        # Respect platform constraints
        if len(hashtags) > constraints.max_tags_count:
            hashtags = hashtags[:constraints.max_tags_count]
        
        # Filter by length
        hashtags = [
            tag for tag in hashtags 
            if len(tag) <= constraints.max_tag_length
        ]
        
        return hashtags
    
    async def _generate_seo_keywords(
        self,
        request: OptimizationRequest,
        platform: PlatformTarget
    ) -> List[str]:
        """Generate SEO keywords for content"""        
        keywords = []
        
        # Extract keywords from title
        title_words = re.findall(r'\b\w+\b', request.original_title.lower())
        keywords.extend(title_words)
        
        # Add content-type specific keywords
        content_keywords = self.SEO_KEYWORDS.get(
            request.content_type.value.split('_')[0], []
        )
        keywords.extend(content_keywords)
        
        # Add genre-specific keywords
        if request.genre:
            keywords.append(request.genre.lower())
        
        # Platform-specific SEO keywords
        if platform == PlatformTarget.YOUTUBE:
            keywords.extend(["watch", "video", "channel", "subscribe"])
        elif platform == PlatformTarget.SPOTIFY:
            keywords.extend(["stream", "listen", "playlist", "artist"])
        
        # Remove duplicates and limit
        keywords = list(set(keywords))[:20]
        
        return keywords
    
    async def _get_platform_recommendations(
        self,
        request: OptimizationRequest,
        platform: PlatformTarget
    ) -> List[str]:
        """Get platform-specific recommendations"""        
        recommendations = []
        
        if platform == PlatformTarget.YOUTUBE:
            recommendations.extend([
                "Consider creating an eye-catching custom thumbnail",
                "Add timestamps in description for better engagement",
                "Include relevant links in description",
                "Use YouTube Shorts for additional exposure"
            ])
        
        elif platform == PlatformTarget.TIKTOK:
            recommendations.extend([
                "Keep videos under 30 seconds for better engagement",
                "Use trending sounds if applicable",
                "Post during peak hours (6-10 PM)",
                "Engage with comments quickly after posting"
            ])
        
        elif platform == PlatformTarget.INSTAGRAM:
            recommendations.extend([
                "Use Stories to promote your post",
                "Consider Reels for higher reach",
                "Post consistently at optimal times",
                "Use Instagram Shopping if applicable"
            ])
        
        elif platform == PlatformTarget.SPOTIFY:
            recommendations.extend([
                "Submit to Spotify playlists",
                "Create artist playlist featuring your music",
                "Use Spotify for Artists analytics",
                "Consider podcast integration"
            ])
        
        return recommendations
    
    async def _apply_seo_optimization(
        self,
        request: OptimizationRequest,
        result: OptimizationResult
    ):
        """Apply SEO optimization and calculate score"""        
        # Calculate SEO score based on various factors
        seo_factors = {
            "title_length": 0,
            "description_quality": 0,
            "keyword_density": 0,
            "hashtag_relevance": 0
        }
        
        # Title length optimization (sweet spot: 50-60 characters)
        title_length = len(request.original_title)
        if 50 <= title_length <= 60:
            seo_factors["title_length"] = 100
        elif 40 <= title_length < 50 or 60 < title_length <= 70:
            seo_factors["title_length"] = 80
        else:
            seo_factors["title_length"] = 60
        
        # Description quality
        if request.original_description:
            desc_length = len(request.original_description)
            if desc_length >= 125:
                seo_factors["description_quality"] = 100
            elif desc_length >= 50:
                seo_factors["description_quality"] = 70
            else:
                seo_factors["description_quality"] = 40
        
        # Calculate overall SEO score
        result.seo_score = sum(seo_factors.values()) / len(seo_factors)
        result.optimization_applied.append(OptimizationType.SEO_KEYWORDS)
    
    async def _predict_engagement(
        self,
        request: OptimizationRequest,
        result: OptimizationResult
    ):
        """Predict engagement for different platforms"""        
        # Simplified engagement prediction based on content factors
        base_engagement = {
            PlatformTarget.YOUTUBE: 5.2,  # Average 5.2% engagement rate
            PlatformTarget.INSTAGRAM: 1.8,  # Average 1.8% engagement rate
            PlatformTarget.TIKTOK: 8.5,  # Average 8.5% engagement rate
            PlatformTarget.TWITTER: 0.9,  # Average 0.9% engagement rate
            PlatformTarget.SPOTIFY: 12.0  # Average 12% save rate
        }
        
        # Factors that influence engagement
        engagement_multipliers = {
            "title_quality": 1.0,
            "content_type": 1.0,
            "optimization": 1.0
        }
        
        # Title quality factor
        title_words = len(request.original_title.split())
        if 4 <= title_words <= 8:
            engagement_multipliers["title_quality"] = 1.2
        elif title_words < 4 or title_words > 12:
            engagement_multipliers["title_quality"] = 0.8
        
        # Content type factor
        if request.content_type in [ContentType.SHORT_FORM_VIDEO, ContentType.MUSIC_TRACK]:
            engagement_multipliers["content_type"] = 1.3
        
        # Optimization factor (if optimizations are applied)
        if len(request.optimization_goals) >= 3:
            engagement_multipliers["optimization"] = 1.15
        
        # Calculate predicted engagement for each platform
        for platform in request.target_platforms:
            if platform in base_engagement:
                base_rate = base_engagement[platform]
                multiplier = np.prod(list(engagement_multipliers.values()))
                predicted_rate = base_rate * multiplier
                
                # Add some randomness to simulate real-world variance
                variance = np.random.normal(1.0, 0.1)
                final_rate = max(0.1, predicted_rate * variance)
                
                result.engagement_prediction[platform.value] = round(final_rate, 2)
        
        result.optimization_applied.append(OptimizationType.ENGAGEMENT_PREDICTION)
    
    async def _optimize_timing(
        self,
        request: OptimizationRequest,
        result: OptimizationResult
    ):
        """Optimize posting timing for each platform"""        
        # Optimal posting times by platform (in UTC)
        optimal_times = {
            PlatformTarget.YOUTUBE: ["14:00", "18:00", "20:00"],
            PlatformTarget.INSTAGRAM: ["06:00", "12:00", "18:00"],
            PlatformTarget.TIKTOK: ["18:00", "21:00", "09:00"],
            PlatformTarget.TWITTER: ["09:00", "12:00", "15:00"],
            PlatformTarget.SPOTIFY: ["07:00", "12:00", "17:00"]
        }
        
        timing_recommendations = []
        
        for platform in request.target_platforms:
            if platform in optimal_times:
                times = optimal_times[platform]
                timing_recommendations.append(
                    f"{platform.value}: Best posting times are {', '.join(times)} UTC"
                )
        
        result.recommendations.extend(timing_recommendations)
        result.optimization_applied.append(OptimizationType.TIMING_OPTIMIZATION)
    
    async def get_platform_constraints(
        self, 
        platform: PlatformTarget
    ) -> Optional[PlatformConstraints]:
        """Get constraints for a specific platform"""        return self.PLATFORM_CONSTRAINTS.get(platform)
    
    async def validate_content_for_platform(
        self,
        content: Dict[str, Any],
        platform: PlatformTarget
    ) -> Tuple[bool, List[str]]:
        """Validate content against platform constraints"""        
        constraints = self.PLATFORM_CONSTRAINTS.get(platform)
        if not constraints:
            return False, [f"Platform {platform.value} not supported"]
        
        errors = []
        
        # Check title length
        title = content.get("title", "")
        if len(title) > constraints.max_title_length:
            errors.append(
                f"Title too long: {len(title)} > {constraints.max_title_length}"
            )
        
        # Check description length
        description = content.get("description", "")
        if description and len(description) > constraints.max_description_length:
            errors.append(
                f"Description too long: {len(description)} > {constraints.max_description_length}"
            )
        
        # Check tags count
        tags = content.get("tags", [])
        if len(tags) > constraints.max_tags_count:
            errors.append(
                f"Too many tags: {len(tags)} > {constraints.max_tags_count}"
            )
        
        # Check individual tag lengths
        for tag in tags:
            if len(tag) > constraints.max_tag_length:
                errors.append(
                    f"Tag too long: '{tag}' ({len(tag)} > {constraints.max_tag_length})"
                )
        
        return len(errors) == 0, errors

# Export all classes for external use
__all__ = [
    "ContentOptimizer",
    "OptimizationRequest",
    "OptimizationResult",
    "PlatformConstraints",
    "OptimizationType",
    "ContentType",
    "PlatformTarget"
]
