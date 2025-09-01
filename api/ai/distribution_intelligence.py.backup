"""IA Influencer Agent - Distribution Intelligence Module
Advanced multi-platform distribution optimization and management system.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result 
in legal action.

© 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    DISCORD = "discord"
    REDDIT = "reddit"
    MEDIUM = "medium"

class ContentFormat(Enum):
    """Content formats for distribution"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"
    BLOG = "blog"

class DistributionStrategy(Enum):
    """Distribution strategies"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PLATFORM_SPECIFIC = "platform_specific"
    VIRAL_CASCADE = "viral_cascade"
    TARGETED_ROLLOUT = "targeted_rollout"

@dataclass
class PlatformRequirements:
    """Platform-specific requirements and constraints"""
    platform: Platform
    supported_formats: List[ContentFormat]
    max_file_size: int  # in bytes
    max_duration: Optional[int]  # in seconds
    aspect_ratios: List[str]
    required_fields: List[str]
    optimal_dimensions: Dict[str, Tuple[int, int]]
    posting_limits: Dict[str, int]
    best_posting_times: List[int]  # hours of day
    hashtag_limits: Dict[str, int]
    character_limits: Dict[str, int]

@dataclass
class ContentVariant:
    """Content variant optimized for specific platform"""
    variant_id: str
    platform: Platform
    format: ContentFormat
    file_path: str
    metadata: Dict[str, Any]
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]
    thumbnail_path: Optional[str]
    duration: Optional[int]
    file_size: int
    dimensions: Optional[Tuple[int, int]]
    optimization_score: float

@dataclass
class DistributionPlan:
    """Complete distribution plan for content"""
    plan_id: str
    content_id: str
    strategy: DistributionStrategy
    target_platforms: List[Platform]
    content_variants: Dict[Platform, ContentVariant]
    posting_schedule: Dict[Platform, datetime]
    expected_reach: Dict[Platform, int]
    budget_allocation: Dict[Platform, float]
    success_metrics: Dict[str, float]
    monitoring_schedule: List[datetime]

@dataclass
class DistributionResult:
    """Results of content distribution"""
    result_id: str
    plan_id: str
    platform: Platform
    status: str
    posted_at: datetime
    content_url: Optional[str]
    initial_metrics: Dict[str, int]
    errors: List[str]
    warnings: List[str]

class PlatformAnalyzer:
    """Analyze platform requirements and optimization opportunities"""
    
    def __init__(self):
        self.platform_requirements = self._initialize_platform_requirements()
        self.content_performance_cache = {}
        
    def _initialize_platform_requirements(self) -> Dict[Platform, PlatformRequirements]:
        """Initialize platform requirements database"""
        return {
            Platform.YOUTUBE: PlatformRequirements(
                platform=Platform.YOUTUBE,
                supported_formats=[ContentFormat.VIDEO, ContentFormat.LIVESTREAM],
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                max_duration=12 * 3600,  # 12 hours
                aspect_ratios=['16:9', '9:16', '1:1'],
                required_fields=['title', 'description'],
                optimal_dimensions={
                    'video': (1920, 1080),
                    'thumbnail': (1280, 720)
                },
                posting_limits={'videos_per_day': 10},
                best_posting_times=[14, 15, 16, 17, 18, 19, 20],
                hashtag_limits={'max_tags': 15},
                character_limits={'title': 100, 'description': 5000}
            ),
            Platform.INSTAGRAM: PlatformRequirements(
                platform=Platform.INSTAGRAM,
                supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.STORY, ContentFormat.REEL],
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=60,  # 60 seconds for reels
                aspect_ratios=['1:1', '9:16', '16:9', '4:5'],
                required_fields=['image_or_video'],
                optimal_dimensions={
                    'feed': (1080, 1080),
                    'story': (1080, 1920),
                    'reel': (1080, 1920)
                },
                posting_limits={'posts_per_day': 5},
                best_posting_times=[11, 12, 14, 17, 18],
                hashtag_limits={'max_hashtags': 30},
                character_limits={'caption': 2200}
            ),
            Platform.TIKTOK: PlatformRequirements(
                platform=Platform.TIKTOK,
                supported_formats=[ContentFormat.VIDEO, ContentFormat.SHORT],
                max_file_size=72 * 1024 * 1024,  # 72MB
                max_duration=180,  # 3 minutes
                aspect_ratios=['9:16'],
                required_fields=['video'],
                optimal_dimensions={
                    'video': (1080, 1920)
                },
                posting_limits={'videos_per_day': 3},
                best_posting_times=[6, 9, 12, 19, 21],
                hashtag_limits={'max_hashtags': 100},
                character_limits={'description': 2200}
            ),
            Platform.SPOTIFY: PlatformRequirements(
                platform=Platform.SPOTIFY,
                supported_formats=[ContentFormat.AUDIO, ContentFormat.PODCAST],
                max_file_size=200 * 1024 * 1024,  # 200MB
                max_duration=None,  # No limit
                aspect_ratios=[],
                required_fields=['audio_file', 'title', 'artist'],
                optimal_dimensions={
                    'cover': (3000, 3000)
                },
                posting_limits={},
                best_posting_times=[9, 12, 15, 18],
                hashtag_limits={},
                character_limits={'title': 100, 'description': 1000}
            ),
            Platform.TWITTER: PlatformRequirements(
                platform=Platform.TWITTER,
                supported_formats=[ContentFormat.TEXT, ContentFormat.IMAGE, ContentFormat.VIDEO],
                max_file_size=512 * 1024 * 1024,  # 512MB
                max_duration=140,  # 140 seconds
                aspect_ratios=['16:9', '1:1'],
                required_fields=['content'],
                optimal_dimensions={
                    'image': (1200, 675),
                    'video': (1280, 720)
                },
                posting_limits={'tweets_per_hour': 300},
                best_posting_times=[8, 9, 12, 13, 17, 18],
                hashtag_limits={},
                character_limits={'tweet': 280}
            )
        }
    
    async def analyze_platform_compatibility(
        self, 
        content_metadata: Dict[str, Any], 
        target_platforms: List[Platform]
    ) -> Dict[Platform, Dict[str, Any]]:
        """Analyze content compatibility with target platforms"""
        compatibility_analysis = {}
        
        for platform in target_platforms:
            analysis = await self._analyze_single_platform_compatibility(
                content_metadata, platform
            )
            compatibility_analysis[platform] = analysis
            
        return compatibility_analysis
    
    async def _analyze_single_platform_compatibility(
        self, 
        content_metadata: Dict[str, Any], 
        platform: Platform
    ) -> Dict[str, Any]:
        """Analyze compatibility with single platform"""
        requirements = self.platform_requirements.get(platform)
        if not requirements:
            return {'compatible': False, 'reason': 'Platform not supported'}
        
        analysis = {
            'compatible': True,
            'optimization_needed': [],
            'warnings': [],
            'recommendations': [],
            'compatibility_score': 1.0
        }
        
        # Check format compatibility
        content_format = ContentFormat(content_metadata.get('format', 'video'))
        if content_format not in requirements.supported_formats:
            analysis['compatible'] = False
            analysis['optimization_needed'].append(f'Convert to supported format: {requirements.supported_formats}')
            analysis['compatibility_score'] *= 0.5
        
        # Check file size
        file_size = content_metadata.get('file_size', 0)
        if file_size > requirements.max_file_size:
            analysis['optimization_needed'].append('Compress file to meet size limits')
            analysis['compatibility_score'] *= 0.8
        
        # Check duration
        duration = content_metadata.get('duration', 0)
        if requirements.max_duration and duration > requirements.max_duration:
            analysis['optimization_needed'].append(f'Trim duration to {requirements.max_duration}s max')
            analysis['compatibility_score'] *= 0.7
        
        # Check dimensions/aspect ratio
        dimensions = content_metadata.get('dimensions', (1920, 1080))
        if dimensions:
            current_ratio = f"{dimensions[0]}:{dimensions[1]}"
            if current_ratio not in requirements.aspect_ratios and requirements.aspect_ratios:
                analysis['optimization_needed'].append(f'Adjust aspect ratio to one of: {requirements.aspect_ratios}')
                analysis['compatibility_score'] *= 0.9
        
        # Check required fields
        for field in requirements.required_fields:
            if field not in content_metadata or not content_metadata[field]:
                analysis['optimization_needed'].append(f'Add required field: {field}')
                analysis['compatibility_score'] *= 0.8
        
        # Check character limits
        for field, limit in requirements.character_limits.items():
            if field in content_metadata:
                content_length = len(str(content_metadata[field]))
                if content_length > limit:
                    analysis['optimization_needed'].append(f'Shorten {field} to {limit} characters max')
                    analysis['compatibility_score'] *= 0.9
        
        # Generate recommendations
        analysis['recommendations'] = await self._generate_platform_recommendations(
            content_metadata, platform, requirements
        )
        
        return analysis
    
    async def _generate_platform_recommendations(
        self, 
        content_metadata: Dict[str, Any], 
        platform: Platform, 
        requirements: PlatformRequirements
    ) -> List[str]:
        """Generate optimization recommendations for platform"""
        recommendations = []
        
        # Optimal posting time
        current_hour = datetime.now().hour
        if current_hour not in requirements.best_posting_times:
            best_time = min(requirements.best_posting_times)
            recommendations.append(f'Consider posting at {best_time}:00 for optimal engagement')
        
        # Hashtag optimization
        hashtags = content_metadata.get('hashtags', [])
        if platform in [Platform.INSTAGRAM, Platform.TIKTOK]:
            max_hashtags = requirements.hashtag_limits.get('max_hashtags', 30)
            if len(hashtags) < max_hashtags // 2:
                recommendations.append(f'Add more hashtags (current: {len(hashtags)}, optimal: {max_hashtags//2}-{max_hashtags})')
        
        # Platform-specific recommendations
        if platform == Platform.YOUTUBE:
            if not content_metadata.get('thumbnail'):
                recommendations.append('Create custom thumbnail for better click-through rate')
            if len(content_metadata.get('description', '')) < 200:
                recommendations.append('Expand description for better SEO')
        
        elif platform == Platform.INSTAGRAM:
            if content_metadata.get('format') == ContentFormat.VIDEO:
                if content_metadata.get('duration', 0) > 15:
                    recommendations.append('Consider creating shorter clips for better engagement')
        
        elif platform == Platform.TIKTOK:
            if 'trending' not in ' '.join(hashtags).lower():
                recommendations.append('Research and use trending hashtags')
        
        return recommendations

class ContentOptimizer:
    """Optimize content for different platforms"""
    
    def __init__(self):
        self.platform_analyzer = PlatformAnalyzer()
        self.optimization_cache = {}
        
    async def create_platform_variants(
        self, 
        original_content: Dict[str, Any], 
        target_platforms: List[Platform]
    ) -> Dict[Platform, ContentVariant]:
        """Create optimized variants for each target platform"""
        variants = {}
        
        for platform in target_platforms:
            variant = await self._create_single_platform_variant(
                original_content, platform
            )
            variants[platform] = variant
            
        return variants
    
    async def _create_single_platform_variant(
        self, 
        original_content: Dict[str, Any], 
        platform: Platform
    ) -> ContentVariant:
        """Create optimized variant for single platform"""
        requirements = self.platform_analyzer.platform_requirements.get(platform)
        
        # Start with original content
        variant_metadata = original_content.copy()
        
        # Optimize for platform
        optimized_metadata = await self._optimize_metadata_for_platform(
            variant_metadata, platform, requirements
        )
        
        # Generate variant
        variant = ContentVariant(
            variant_id=f"{original_content.get('content_id', 'unknown')}_{platform.value}",
            platform=platform,
            format=ContentFormat(optimized_metadata.get('format', 'video')),
            file_path=optimized_metadata.get('file_path', ''),
            metadata=optimized_metadata,
            title=optimized_metadata.get('title', ''),
            description=optimized_metadata.get('description', ''),
            tags=optimized_metadata.get('tags', []),
            hashtags=optimized_metadata.get('hashtags', []),
            thumbnail_path=optimized_metadata.get('thumbnail_path'),
            duration=optimized_metadata.get('duration'),
            file_size=optimized_metadata.get('file_size', 0),
            dimensions=optimized_metadata.get('dimensions'),
            optimization_score=await self._calculate_optimization_score(optimized_metadata, platform)
        )
        
        return variant
    
    async def _optimize_metadata_for_platform(
        self, 
        metadata: Dict[str, Any], 
        platform: Platform, 
        requirements: Optional[PlatformRequirements]
    ) -> Dict[str, Any]:
        """Optimize metadata for specific platform"""
        if not requirements:
            return metadata
        
        optimized = metadata.copy()
        
        # Optimize title
        original_title = metadata.get('title', '')
        optimized_title = await self._optimize_title_for_platform(original_title, platform, requirements)
        optimized['title'] = optimized_title
        
        # Optimize description
        original_description = metadata.get('description', '')
        optimized_description = await self._optimize_description_for_platform(
            original_description, platform, requirements
        )
        optimized['description'] = optimized_description
        
        # Optimize hashtags
        original_hashtags = metadata.get('hashtags', [])
        optimized_hashtags = await self._optimize_hashtags_for_platform(
            original_hashtags, platform, requirements
        )
        optimized['hashtags'] = optimized_hashtags
        
        # Platform-specific optimizations
        if platform == Platform.YOUTUBE:
            optimized.update(await self._optimize_for_youtube(metadata))
        elif platform == Platform.INSTAGRAM:
            optimized.update(await self._optimize_for_instagram(metadata))
        elif platform == Platform.TIKTOK:
            optimized.update(await self._optimize_for_tiktok(metadata))
        elif platform == Platform.TWITTER:
            optimized.update(await self._optimize_for_twitter(metadata))
        elif platform == Platform.SPOTIFY:
            optimized.update(await self._optimize_for_spotify(metadata))
        
        return optimized
    
    async def _optimize_title_for_platform(
        self, 
        original_title: str, 
        platform: Platform, 
        requirements: PlatformRequirements
    ) -> str:
        """Optimize title for platform"""
        if not original_title:
            return "Professional Content"
        
        max_length = requirements.character_limits.get('title', 100)
        
        # Truncate if too long
        if len(original_title) > max_length:
            truncated = original_title[:max_length-3] + "..."
        else:
            truncated = original_title
        
        # Platform-specific title optimization
        if platform == Platform.YOUTUBE:
            # Add engagement words
            if not any(word in truncated.lower() for word in ['amazing', 'incredible', 'must', 'ultimate']):
                if len(truncated) < max_length - 10:
                    truncated = f"Amazing {truncated}"
        
        elif platform == Platform.TIKTOK:
            # Make more casual/trendy
            if not truncated.startswith(('POV:', 'When', 'How to')):
                if len(truncated) < max_length - 6:
                    truncated = f"POV: {truncated}"
        
        return truncated
    
    async def _optimize_description_for_platform(
        self, 
        original_description: str, 
        platform: Platform, 
        requirements: PlatformRequirements
    ) -> str:
        """Optimize description for platform"""
        if not original_description:
            original_description = "Check out this amazing content!"
        
        max_length = requirements.character_limits.get('description', 5000)
        
        # Platform-specific description optimization
        if platform == Platform.YOUTUBE:
            # Add timestamps, links, call-to-action
            optimized = original_description
            if "Subscribe" not in optimized:
                optimized += "\n\n🔔 Subscribe for more amazing content!"
            if "like" not in optimized.lower():
                optimized += "\n👍 Like if you enjoyed this video!"
            
        elif platform == Platform.INSTAGRAM:
            # Add line breaks, emojis
            optimized = original_description
            if not any(emoji in optimized for emoji in ['🎵', '🎥', '📸', '✨']):
                optimized = f"✨ {optimized}"
            
        elif platform == Platform.TWITTER:
            # Keep it short and add relevant hashtags
            optimized = original_description[:200]  # Leave room for hashtags
            
        else:
            optimized = original_description
        
        # Truncate if necessary
        if len(optimized) > max_length:
            optimized = optimized[:max_length-3] + "..."
        
        return optimized
    
    async def _optimize_hashtags_for_platform(
        self, 
        original_hashtags: List[str], 
        platform: Platform, 
        requirements: PlatformRequirements
    ) -> List[str]:
        """Optimize hashtags for platform"""
        optimized_hashtags = original_hashtags.copy()
        
        # Platform-specific hashtag optimization
        platform_specific_hashtags = {
            Platform.YOUTUBE: ['#youtube', '#content', '#creator'],
            Platform.INSTAGRAM: ['#instagram', '#insta', '#photo', '#content'],
            Platform.TIKTOK: ['#fyp', '#foryou', '#viral', '#trending'],
            Platform.TWITTER: ['#twitter', '#content'],
            Platform.LINKEDIN: ['#linkedin', '#professional', '#content']
        }
        
        # Add platform-specific hashtags
        specific_hashtags = platform_specific_hashtags.get(platform, [])
        for hashtag in specific_hashtags:
            if hashtag not in optimized_hashtags:
                optimized_hashtags.append(hashtag)
        
        # Respect platform limits
        max_hashtags = requirements.hashtag_limits.get('max_hashtags')
        if max_hashtags:
            optimized_hashtags = optimized_hashtags[:max_hashtags]
        
        # Remove hashtags for platforms that don't use them much
        if platform in [Platform.YOUTUBE, Platform.SPOTIFY]:
            # YouTube uses tags, Spotify doesn't use hashtags much
            optimized_hashtags = optimized_hashtags[:5]  # Keep minimal
        
        return optimized_hashtags
    
    async def _optimize_for_youtube(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """YouTube-specific optimizations"""
        optimizations = {}
        
        # Ensure video format
        optimizations['format'] = ContentFormat.VIDEO
        
        # Optimize for YouTube algorithm
        optimizations['category'] = metadata.get('category', 'Entertainment')
        
        # Add YouTube-specific fields
        optimizations['youtube_specific'] = {
            'made_for_kids': False,
            'visibility': 'public',
            'allow_comments': True,
            'allow_ratings': True,
            'monetization_enabled': True
        }
        
        return optimizations
    
    async def _optimize_for_instagram(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Instagram-specific optimizations"""
        optimizations = {}
        
        # Determine best format
        if metadata.get('duration', 0) <= 60:
            optimizations['format'] = ContentFormat.REEL
        elif metadata.get('format') == ContentFormat.IMAGE:
            optimizations['format'] = ContentFormat.IMAGE
        else:
            optimizations['format'] = ContentFormat.VIDEO
        
        # Instagram-specific settings
        optimizations['instagram_specific'] = {
            'allow_comments': True,
            'location_tag': metadata.get('location', ''),
            'alt_text': 'Professional content creation'
        }
        
        return optimizations
    
    async def _optimize_for_tiktok(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """TikTok-specific optimizations"""
        optimizations = {}
        
        # TikTok is video-only
        optimizations['format'] = ContentFormat.SHORT
        
        # Optimize for TikTok algorithm
        optimizations['tiktok_specific'] = {
            'duet_enabled': True,
            'stitch_enabled': True,
            'comments_enabled': True,
            'download_enabled': True
        }
        
        return optimizations
    
    async def _optimize_for_twitter(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Twitter-specific optimizations"""
        optimizations = {}
        
        # Twitter supports multiple formats
        if metadata.get('format') == ContentFormat.TEXT:
            optimizations['format'] = ContentFormat.TEXT
        else:
            optimizations['format'] = metadata.get('format', ContentFormat.IMAGE)
        
        # Twitter-specific settings
        optimizations['twitter_specific'] = {
            'reply_enabled': True,
            'retweet_enabled': True,
            'like_enabled': True
        }
        
        return optimizations
    
    async def _optimize_for_spotify(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Spotify-specific optimizations"""
        optimizations = {}
        
        # Spotify is audio-only
        optimizations['format'] = ContentFormat.AUDIO
        
        # Music metadata
        optimizations['spotify_specific'] = {
            'genre': metadata.get('genre', 'Pop'),
            'explicit': False,
            'isrc': metadata.get('isrc', ''),
            'preview_start_time': 30  # 30 seconds into track
        }
        
        return optimizations
    
    async def _calculate_optimization_score(
        self, 
        optimized_metadata: Dict[str, Any], 
        platform: Platform
    ) -> float:
        """Calculate optimization score for platform variant"""
        requirements = self.platform_analyzer.platform_requirements.get(platform)
        if not requirements:
            return 0.5
        
        score_factors = []
        
        # Format compatibility
        content_format = ContentFormat(optimized_metadata.get('format', 'video'))
        if content_format in requirements.supported_formats:
            score_factors.append(1.0)
        else:
            score_factors.append(0.3)
        
        # Required fields completion
        completed_fields = sum(1 for field in requirements.required_fields 
                             if optimized_metadata.get(field))
        if requirements.required_fields:
            field_completion = completed_fields / len(requirements.required_fields)
            score_factors.append(field_completion)
        
        # Character limit compliance
        for field, limit in requirements.character_limits.items():
            if field in optimized_metadata:
                field_length = len(str(optimized_metadata[field]))
                if field_length <= limit:
                    score_factors.append(1.0)
                else:
                    score_factors.append(max(0.5, limit / field_length))
        
        # Hashtag optimization
        hashtags = optimized_metadata.get('hashtags', [])
        if platform in [Platform.INSTAGRAM, Platform.TIKTOK]:
            max_hashtags = requirements.hashtag_limits.get('max_hashtags', 30)
            hashtag_ratio = len(hashtags) / max_hashtags
            if 0.3 <= hashtag_ratio <= 1.0:  # Good hashtag usage
                score_factors.append(1.0)
            else:
                score_factors.append(0.7)
        
        return sum(score_factors) / len(score_factors) if score_factors else 0.5

class DistributionScheduler:
    """Intelligent distribution scheduling system"""
    
    def __init__(self):
        self.platform_analyzer = PlatformAnalyzer()
        self.scheduling_cache = {}
    
    async def create_distribution_plan(
        self, 
        content_variants: Dict[Platform, ContentVariant],
        strategy: DistributionStrategy,
        target_audience: Dict[str, Any] = None,
        budget_constraints: Dict[str, float] = None
    ) -> DistributionPlan:
        """Create comprehensive distribution plan"""
        try:
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            content_id = list(content_variants.values())[0].variant_id.split('_')[0]
            
            # Calculate optimal posting schedule
            posting_schedule = await self._calculate_posting_schedule(
                list(content_variants.keys()), strategy, target_audience
            )
            
            # Predict reach for each platform
            expected_reach = await self._predict_platform_reach(
                content_variants, target_audience
            )
            
            # Allocate budget
            budget_allocation = await self._allocate_budget(
                content_variants, expected_reach, budget_constraints
            )
            
            # Define success metrics
            success_metrics = await self._define_success_metrics(
                content_variants, expected_reach
            )
            
            # Create monitoring schedule
            monitoring_schedule = await self._create_monitoring_schedule(posting_schedule)
            
            plan = DistributionPlan(
                plan_id=plan_id,
                content_id=content_id,
                strategy=strategy,
                target_platforms=list(content_variants.keys()),
                content_variants=content_variants,
                posting_schedule=posting_schedule,
                expected_reach=expected_reach,
                budget_allocation=budget_allocation,
                success_metrics=success_metrics,
                monitoring_schedule=monitoring_schedule
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Distribution plan creation failed: {str(e)}")
            raise
    
    async def _calculate_posting_schedule(
        self, 
        platforms: List[Platform], 
        strategy: DistributionStrategy,
        target_audience: Dict[str, Any] = None
    ) -> Dict[Platform, datetime]:
        """Calculate optimal posting schedule"""
        schedule = {}
        base_time = datetime.now()
        
        if strategy == DistributionStrategy.SIMULTANEOUS:
            # Post to all platforms at the same optimal time
            optimal_hour = await self._find_optimal_cross_platform_time(platforms, target_audience)
            posting_time = base_time.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
            
            # If optimal time is in the past, schedule for next day
            if posting_time <= base_time:
                posting_time += timedelta(days=1)
            
            for platform in platforms:
                schedule[platform] = posting_time
        
        elif strategy == DistributionStrategy.SEQUENTIAL:
            # Post to platforms in order of importance/reach
            platform_priority = await self._rank_platforms_by_priority(platforms, target_audience)
            current_time = base_time
            
            for i, platform in enumerate(platform_priority):
                # Space out posts by 2-4 hours
                posting_time = current_time + timedelta(hours=2 + i)
                schedule[platform] = posting_time
        
        elif strategy == DistributionStrategy.PLATFORM_SPECIFIC:
            # Optimize posting time for each platform individually
            for platform in platforms:
                optimal_time = await self._find_optimal_platform_time(platform, target_audience)
                schedule[platform] = optimal_time
        
        elif strategy == DistributionStrategy.VIRAL_CASCADE:
            # Start with most viral-prone platform, then cascade
            viral_platforms = [Platform.TIKTOK, Platform.INSTAGRAM, Platform.TWITTER, Platform.YOUTUBE]
            ordered_platforms = []
            
            # Add viral platforms first if they're in target list
            for vp in viral_platforms:
                if vp in platforms:
                    ordered_platforms.append(vp)
            
            # Add remaining platforms
            for p in platforms:
                if p not in ordered_platforms:
                    ordered_platforms.append(p)
            
            current_time = base_time
            for i, platform in enumerate(ordered_platforms):
                # Quick succession for viral cascade
                posting_time = current_time + timedelta(hours=i)
                schedule[platform] = posting_time
        
        return schedule
    
    async def _find_optimal_cross_platform_time(
        self, 
        platforms: List[Platform], 
        target_audience: Dict[str, Any] = None
    ) -> int:
        """Find optimal time that works across multiple platforms"""
        platform_times = []
        
        for platform in platforms:
            requirements = self.platform_analyzer.platform_requirements.get(platform)
            if requirements:
                platform_times.extend(requirements.best_posting_times)
        
        if not platform_times:
            return 18  # Default to 6 PM
        
        # Find most common optimal time
        time_counts = defaultdict(int)
        for time in platform_times:
            time_counts[time] += 1
        
        # Return most common time, or median if tie
        max_count = max(time_counts.values())
        best_times = [time for time, count in time_counts.items() if count == max_count]
        
        return sorted(best_times)[len(best_times) // 2]
    
    async def _rank_platforms_by_priority(
        self, 
        platforms: List[Platform], 
        target_audience: Dict[str, Any] = None
    ) -> List[Platform]:
        """Rank platforms by priority/importance"""
        # Base priority scores
        priority_scores = {
            Platform.YOUTUBE: 0.9,  # High reach, monetization
            Platform.INSTAGRAM: 0.8,  # High engagement
            Platform.TIKTOK: 0.8,  # Viral potential
            Platform.SPOTIFY: 0.7,  # Music-specific
            Platform.TWITTER: 0.6,  # News/updates
            Platform.FACEBOOK: 0.5,  # Older demographic
            Platform.LINKEDIN: 0.4   # Professional content
        }
        
        # Adjust based on target audience
        if target_audience:
            age_groups = target_audience.get('age_groups', {})
            
            # Boost TikTok for younger audience
            if age_groups.get('18-24', 0) > 0.4:
                priority_scores[Platform.TIKTOK] = priority_scores.get(Platform.TIKTOK, 0.8) + 0.1
            
            # Boost LinkedIn for professional content
            interests = target_audience.get('interests', [])
            if any(interest in ['business', 'professional', 'career'] for interest in interests):
                priority_scores[Platform.LINKEDIN] = priority_scores.get(Platform.LINKEDIN, 0.4) + 0.3
        
        # Sort platforms by priority
        platform_priorities = [(platform, priority_scores.get(platform, 0.5)) 
                              for platform in platforms]
        platform_priorities.sort(key=lambda x: x[1], reverse=True)
        
        return [platform for platform, score in platform_priorities]
    
    async def _find_optimal_platform_time(
        self, 
        platform: Platform, 
        target_audience: Dict[str, Any] = None
    ) -> datetime:
        """Find optimal posting time for specific platform"""
        requirements = self.platform_analyzer.platform_requirements.get(platform)
        
        if not requirements or not requirements.best_posting_times:
            # Default to 6 PM today or tomorrow if past
            default_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
            if default_time <= datetime.now():
                default_time += timedelta(days=1)
            return default_time
        
        # Choose the first optimal time from the list
        optimal_hour = requirements.best_posting_times[0]
        optimal_time = datetime.now().replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
        
        # If time has passed today, schedule for tomorrow
        if optimal_time <= datetime.now():
            optimal_time += timedelta(days=1)
        
        return optimal_time
    
    async def _predict_platform_reach(
        self, 
        content_variants: Dict[Platform, ContentVariant],
        target_audience: Dict[str, Any] = None
    ) -> Dict[Platform, int]:
        """Predict expected reach for each platform"""
        reach_predictions = {}
        
        # Base reach estimates (these would come from ML models in production)
        base_reach = {
            Platform.YOUTUBE: 5000,
            Platform.INSTAGRAM: 3000,
            Platform.TIKTOK: 8000,  # Higher viral potential
            Platform.TWITTER: 2000,
            Platform.SPOTIFY: 1500,
            Platform.FACEBOOK: 2500,
            Platform.LINKEDIN: 1000
        }
        
        for platform, variant in content_variants.items():
            base = base_reach.get(platform, 1000)
            
            # Adjust based on optimization score
            optimization_multiplier = 0.5 + (variant.optimization_score * 0.5)
            predicted_reach = int(base * optimization_multiplier)
            
            # Adjust based on content quality
            if variant.optimization_score > 0.8:
                predicted_reach = int(predicted_reach * 1.5)
            
            reach_predictions[platform] = predicted_reach
        
        return reach_predictions
    
    async def _allocate_budget(
        self, 
        content_variants: Dict[Platform, ContentVariant],
        expected_reach: Dict[Platform, int],
        budget_constraints: Dict[str, float] = None
    ) -> Dict[Platform, float]:
        """Allocate budget across platforms"""
        if not budget_constraints:
            # No budget allocation needed
            return {platform: 0.0 for platform in content_variants.keys()}
        
        total_budget = budget_constraints.get('total_budget', 1000.0)
        
        # Allocate budget based on expected reach and platform ROI
        platform_roi = {
            Platform.YOUTUBE: 1.2,
            Platform.INSTAGRAM: 1.0,
            Platform.TIKTOK: 1.5,  # High viral ROI
            Platform.TWITTER: 0.8,
            Platform.SPOTIFY: 1.1,
            Platform.FACEBOOK: 0.9,
            Platform.LINKEDIN: 0.7
        }
        
        # Calculate allocation weights
        allocation_weights = {}
        total_weight = 0
        
        for platform in content_variants.keys():
            reach = expected_reach.get(platform, 1000)
            roi = platform_roi.get(platform, 1.0)
            weight = reach * roi
            allocation_weights[platform] = weight
            total_weight += weight
        
        # Allocate budget proportionally
        budget_allocation = {}
        for platform, weight in allocation_weights.items():
            allocation = (weight / total_weight) * total_budget
            budget_allocation[platform] = round(allocation, 2)
        
        return budget_allocation
    
    async def _define_success_metrics(
        self, 
        content_variants: Dict[Platform, ContentVariant],
        expected_reach: Dict[Platform, int]
    ) -> Dict[str, float]:
        """Define success metrics for distribution"""
        total_expected_reach = sum(expected_reach.values())
        
        return {
            'total_reach_target': total_expected_reach,
            'engagement_rate_target': 0.05,  # 5% engagement rate
            'viral_threshold': total_expected_reach * 2,  # 2x expected reach
            'conversion_rate_target': 0.02,  # 2% conversion rate
            'platform_diversity_score': len(content_variants) / 10,  # Max 10 platforms
            'success_threshold': 0.7  # 70% of targets met = success
        }
    
    async def _create_monitoring_schedule(
        self, 
        posting_schedule: Dict[Platform, datetime]
    ) -> List[datetime]:
        """Create monitoring schedule for distribution"""
        monitoring_times = []
        
        # Get earliest and latest posting times
        post_times = list(posting_schedule.values())
        if not post_times:
            return monitoring_times
        
        earliest_post = min(post_times)
        latest_post = max(post_times)
        
        # Monitor at key intervals
        monitoring_intervals = [
            1,    # 1 hour after first post
            6,    # 6 hours after first post
            24,   # 1 day after first post
            72,   # 3 days after first post
            168   # 1 week after first post
        ]
        
        for hours in monitoring_intervals:
            monitor_time = earliest_post + timedelta(hours=hours)
            monitoring_times.append(monitor_time)
        
        return monitoring_times

class DistributionEngine:
    """Main distribution engine coordinating all distribution activities"""
    
    def __init__(self):
        self.platform_analyzer = PlatformAnalyzer()
        self.content_optimizer = ContentOptimizer()
        self.distribution_scheduler = DistributionScheduler()
        self.distribution_results = {}
    
    async def execute_distribution_plan(
        self, 
        plan: DistributionPlan
    ) -> List[DistributionResult]:
        """Execute complete distribution plan"""
        try:
            results = []
            
            for platform in plan.target_platforms:
                result = await self._distribute_to_platform(
                    platform, 
                    plan.content_variants[platform],
                    plan.posting_schedule[platform],
                    plan
                )
                results.append(result)
            
            # Store results
            self.distribution_results[plan.plan_id] = results
            
            return results
            
        except Exception as e:
            logger.error(f"Distribution plan execution failed: {str(e)}")
            raise
    
    async def _distribute_to_platform(
        self, 
        platform: Platform,
        content_variant: ContentVariant,
        scheduled_time: datetime,
        plan: DistributionPlan
    ) -> DistributionResult:
        """Distribute content to single platform"""
        result = DistributionResult(
            result_id=f"result_{plan.plan_id}_{platform.value}",
            plan_id=plan.plan_id,
            platform=platform,
            status="pending",
            posted_at=datetime.now(),
            content_url=None,
            initial_metrics={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Check if it's time to post
            if datetime.now() < scheduled_time:
                result.status = "scheduled"
                result.warnings.append(f"Scheduled for {scheduled_time}")
                return result
            
            # Simulate platform posting (in production, integrate with actual APIs)
            success = await self._simulate_platform_posting(platform, content_variant)
            
            if success:
                result.status = "published"
                result.content_url = f"https://{platform.value}.com/content/{content_variant.variant_id}"
                result.initial_metrics = await self._get_initial_metrics(platform)
            else:
                result.status = "failed"
                result.errors.append("Platform posting failed")
            
        except Exception as e:
            result.status = "error"
            result.errors.append(str(e))
            logger.error(f"Platform distribution failed for {platform}: {str(e)}")
        
        return result
    
    async def _simulate_platform_posting(
        self, 
        platform: Platform, 
        content_variant: ContentVariant
    ) -> bool:
        """Simulate posting to platform (replace with real API calls)"""
        # Simulate API call delay
        await asyncio.sleep(1)
        
        # Simulate 95% success rate
        import random
        return random.random() > 0.05
    
    async def _get_initial_metrics(self, platform: Platform) -> Dict[str, int]:
        """Get initial metrics after posting"""
        # Simulate initial metrics
        import random
        
        base_metrics = {
            'views': random.randint(100, 1000),
            'likes': random.randint(10, 100),
            'comments': random.randint(1, 20),
            'shares': random.randint(0, 10)
        }
        
        return base_metrics
    
    async def monitor_distribution_performance(
        self, 
        plan_id: str
    ) -> Dict[Platform, Dict[str, Any]]:
        """Monitor performance of distributed content"""
        if plan_id not in self.distribution_results:
            return {}
        
        results = self.distribution_results[plan_id]
        performance_data = {}
        
        for result in results:
            if result.status == "published":
                # Simulate performance monitoring
                current_metrics = await self._get_current_metrics(result.platform, result.content_url)
                performance_data[result.platform] = {
                    'initial_metrics': result.initial_metrics,
                    'current_metrics': current_metrics,
                    'growth_rate': await self._calculate_growth_rate(
                        result.initial_metrics, current_metrics
                    ),
                    'engagement_rate': await self._calculate_engagement_rate(current_metrics),
                    'performance_score': await self._calculate_performance_score(
                        result.platform, current_metrics
                    )
                }
        
        return performance_data
    
    async def _get_current_metrics(self, platform: Platform, content_url: str) -> Dict[str, int]:
        """Get current metrics for content"""
        # Simulate metric growth
        import random
        
        growth_factor = random.uniform(1.5, 5.0)  # 50% to 400% growth
        
        return {
            'views': int(random.randint(100, 1000) * growth_factor),
            'likes': int(random.randint(10, 100) * growth_factor),
            'comments': int(random.randint(1, 20) * growth_factor),
            'shares': int(random.randint(0, 10) * growth_factor)
        }
    
    async def _calculate_growth_rate(
        self, 
        initial_metrics: Dict[str, int], 
        current_metrics: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate growth rate for metrics"""
        growth_rates = {}
        
        for metric in initial_metrics:
            initial = initial_metrics[metric]
            current = current_metrics.get(metric, initial)
            
            if initial > 0:
                growth_rate = ((current - initial) / initial) * 100
            else:
                growth_rate = 100.0 if current > 0 else 0.0
            
            growth_rates[metric] = round(growth_rate, 2)
        
        return growth_rates
    
    async def _calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate"""
        views = metrics.get('views', 1)
        engagements = metrics.get('likes', 0) + metrics.get('comments', 0) + metrics.get('shares', 0)
        
        if views > 0:
            engagement_rate = (engagements / views) * 100
        else:
            engagement_rate = 0.0
        
        return round(engagement_rate, 2)
    
    async def _calculate_performance_score(
        self, 
        platform: Platform, 
        metrics: Dict[str, int]
    ) -> float:
        """Calculate overall performance score"""
        # Platform-specific scoring weights
        platform_weights = {
            Platform.YOUTUBE: {'views': 0.4, 'likes': 0.3, 'comments': 0.2, 'shares': 0.1},
            Platform.INSTAGRAM: {'views': 0.3, 'likes': 0.4, 'comments': 0.2, 'shares': 0.1},
            Platform.TIKTOK: {'views': 0.5, 'likes': 0.2, 'comments': 0.1, 'shares': 0.2},
            Platform.TWITTER: {'views': 0.3, 'likes': 0.2, 'comments': 0.2, 'shares': 0.3}
        }
        
        weights = platform_weights.get(platform, {'views': 0.4, 'likes': 0.3, 'comments': 0.2, 'shares': 0.1})
        
        # Normalize metrics (this would use historical data in production)
        normalized_score = 0.0
        
        for metric, weight in weights.items():
            metric_value = metrics.get(metric, 0)
            # Simple normalization (in production, use percentiles)
            normalized_value = min(metric_value / 1000, 1.0)  # Cap at 1000 for normalization
            normalized_score += normalized_value * weight
        
        return round(normalized_score * 100, 1)  # Convert to percentage

# Export main classes
__all__ = [
    'Platform',
    'ContentFormat',
    'DistributionStrategy',
    'PlatformRequirements',
    'ContentVariant',
    'DistributionPlan',
    'DistributionResult',
    'PlatformAnalyzer',
    'ContentOptimizer',
    'DistributionScheduler',
    'DistributionEngine'
]
