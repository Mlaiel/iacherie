"""Platform Integration Module  
Author: Fahed Mlaiel <mlaiel@live.de>

Specialized platform integrations for creators supporting the complete monetization workflow:
- Spotify, Apple Music, YouTube Music (Musicians)
- Instagram, TikTok, YouTube (Influencers)  
- LinkedIn, Medium, Substack (Bloggers)
- Flickr, Shutterstock, Getty Images (Photographers)
- Comedy Central, Netflix, Amazon Prime (Comedians)

⚠️ COPYRIGHT NOTICE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This code and all associated concepts are the EXCLUSIVE PROPERTY of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use will result in immediate legal action.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import base64

# Platform-specific API clients
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import instaloader
import requests
from urllib.parse import urlencode

# Content optimization
from PIL import Image
import cv2
import ffmpeg
from moviepy.editor import VideoFileClip

from ..core.exceptions import PlatformError, AuthenticationError, ContentError
from ..core.metrics import MetricsCollector
from ..core.config import PlatformConfig
from ..utils.decorators import monitor_performance, retry_on_failure


class BasePlatformIntegration(ABC):
    """
Abstract base class for platform integrations."""
    
    def __init__(self, platform_name: str, config: PlatformConfig):
        self.platform_name = platform_name
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector(f"{platform_name}_integration")
        
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the platform."""
        pass
    
    @abstractmethod
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Upload content to the platform."""
        pass
    
    @abstractmethod
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """
Get content analytics from the platform."""
        pass
    
    @abstractmethod
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize content for the platform."""
        pass


class CreatorPlatformManager:
    """
    Centralized platform management for creators supporting multi-platform
    content distribution, analytics aggregation, and monetization tracking.
    """
    
    def __init__(self, creator_type: str, config: PlatformConfig = None):
        self.creator_type = creator_type
        self.config = config or PlatformConfig()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("creator_platform_manager")
        
        # Initialize platform integrations
        self.platforms = {}
        self.authenticated_platforms = set()
        
        # Creator-specific platform mappings
        self.creator_platforms = {
            'musician': {
                'primary': ['spotify', 'apple_music', 'youtube_music'],
                'secondary': ['soundcloud', 'bandcamp', 'deezer'],
                'social': ['instagram', 'tiktok', 'twitter', 'facebook']
            },
            'blogger': {
                'primary': ['medium', 'linkedin', 'substack'],
                'secondary': ['wordpress', 'ghost', 'notion'],
                'social': ['twitter', 'linkedin', 'instagram', 'facebook']
            },
            'photographer': {
                'primary': ['instagram', 'flickr', 'shutterstock'],
                'secondary': ['getty', 'adobe_stock', 'unsplash'],
                'social': ['instagram', 'pinterest', 'behance', 'dribbble']
            },
            'influencer': {
                'primary': ['instagram', 'tiktok', 'youtube'],
                'secondary': ['snapchat', 'twitter', 'twitch'],
                'social': ['instagram', 'tiktok', 'youtube', 'twitter']
            },
            'comedian': {
                'primary': ['youtube', 'tiktok', 'instagram'],
                'secondary': ['comedy_central', 'netflix', 'amazon_prime'],
                'social': ['twitter', 'instagram', 'tiktok', 'facebook']
            }
        }
        
        self._initialize_platforms()

    def _initialize_platforms(self):
        """Initialize platform integrations for the creator type."""
        creator_config = self.creator_platforms.get(self.creator_type, {})
        
        # Initialize primary platforms
        for platform in creator_config.get('primary', []):
            self.platforms[platform] = self._create_platform_integration(platform)
            
        # Initialize secondary platforms
        for platform in creator_config.get('secondary', []):
            self.platforms[platform] = self._create_platform_integration(platform)
            
        # Initialize social platforms
        for platform in creator_config.get('social', []):
            if platform not in self.platforms:
                self.platforms[platform] = self._create_platform_integration(platform)

    def _create_platform_integration(self, platform_name: str) -> BasePlatformIntegration:
        """
Create platform integration instance."""
        platform_classes = {
            'spotify': SpotifyIntegration,
            'apple_music': AppleMusicIntegration,
            'youtube_music': YouTubeMusicIntegration,
            'youtube': YouTubeIntegration,
            'instagram': InstagramIntegration,
            'tiktok': TikTokIntegration,
            'twitter': TwitterIntegration,
            'linkedin': LinkedInIntegration,
            'medium': MediumIntegration,
            'substack': SubstackIntegration,
            'flickr': FlickrIntegration,
            'shutterstock': ShutterstockIntegration,
            'getty': GettyImagesIntegration,
            'soundcloud': SoundCloudIntegration,
            'bandcamp': BandcampIntegration
        }
        
        platform_class = platform_classes.get(platform_name, GenericPlatformIntegration)
        return platform_class(platform_name, self.config)

    @monitor_performance
    async def distribute_content_multi_platform(
        self,
        content_data: Dict[str, Any],
        target_platforms: List[str] = None,
        distribution_strategy: str = "simultaneous"
    ) -> Dict[str, Any]:
        """
        Distribute content across multiple platforms with optimized timing and formatting.
        
        Args:
            content_data: Content to distribute
            target_platforms: Specific platforms to target (defaults to creator's primary platforms)
            distribution_strategy: "simultaneous", "staged", or "optimized_timing"
            
        Returns:
            Distribution results with platform-specific metrics
        """
        if target_platforms is None:
            target_platforms = self.creator_platforms[self.creator_type]['primary']
        
        distribution_results = {
            'distribution_id': f"dist_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'creator_type': self.creator_type,
            'strategy': distribution_strategy,
            'target_platforms': target_platforms,
            'platform_results': {},
            'aggregated_metrics': {},
            'distribution_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Optimize content for each platform
            optimized_content = {}
            for platform in target_platforms:
                if platform in self.platforms:
                    optimized_content[platform] = await self.platforms[platform].optimize_content(content_data)
            
            # Execute distribution strategy
            if distribution_strategy == "simultaneous":
                platform_results = await self._distribute_simultaneous(optimized_content)
            elif distribution_strategy == "staged":
                platform_results = await self._distribute_staged(optimized_content)
            else:  # optimized_timing
                platform_results = await self._distribute_optimized_timing(optimized_content)
            
            distribution_results['platform_results'] = platform_results
            
            # Aggregate metrics
            aggregated_metrics = await self._aggregate_distribution_metrics(platform_results)
            distribution_results['aggregated_metrics'] = aggregated_metrics
            
            # Track monetization potential
            monetization_tracking = await self._setup_monetization_tracking(platform_results)
            distribution_results['monetization_tracking'] = monetization_tracking
            
            self.metrics.increment_counter('successful_distributions')
            return distribution_results
            
        except Exception as e:
            self.logger.error(f"Multi-platform distribution failed: {str(e)}")
            self.metrics.increment_counter('distribution_errors')
            raise PlatformError(f"Content distribution failed: {str(e)}")

    async def _distribute_simultaneous(self, optimized_content: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Distribute content simultaneously across all platforms."""
        platform_results = {}
        
        # Create upload tasks for all platforms
        upload_tasks = []
        for platform, content in optimized_content.items():
            task = self._upload_to_platform(platform, content)
            upload_tasks.append((platform, task))
        
        # Execute all uploads concurrently
        for platform, task in upload_tasks:
            try:
                result = await task
                platform_results[platform] = {
                    'status': 'success',
                    'upload_result': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
            except Exception as e:
                platform_results[platform] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return platform_results

    async def _distribute_staged(self, optimized_content: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
Distribute content in stages based on platform priority."""
        platform_results = {}
        creator_config = self.creator_platforms[self.creator_type]
        
        # Stage 1: Primary platforms
        for platform in creator_config.get('primary', []):
            if platform in optimized_content:
                try:
                    result = await self._upload_to_platform(platform, optimized_content[platform])
                    platform_results[platform] = {
                        'status': 'success',
                        'upload_result': result,
                        'stage': 'primary',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    # Wait before next upload
                    await asyncio.sleep(30)
                except Exception as e:
                    platform_results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'stage': 'primary',
                        'timestamp': datetime.utcnow().isoformat()
                    }
        
        # Stage 2: Secondary platforms (after delay)
        await asyncio.sleep(300)  # 5 minute delay
        
        for platform in creator_config.get('secondary', []):
            if platform in optimized_content:
                try:
                    result = await self._upload_to_platform(platform, optimized_content[platform])
                    platform_results[platform] = {
                        'status': 'success',
                        'upload_result': result,
                        'stage': 'secondary',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    platform_results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'stage': 'secondary',
                        'timestamp': datetime.utcnow().isoformat()
                    }
        
        return platform_results

    async def _distribute_optimized_timing(self, optimized_content: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
Distribute content at optimal times for each platform."""
        platform_results = {}
        
        # Get optimal posting times for each platform
        optimal_times = await self._get_optimal_posting_times(list(optimized_content.keys()))
        
        # Schedule uploads for optimal times
        for platform, content in optimized_content.items():
            optimal_time = optimal_times.get(platform, datetime.utcnow())
            
            if optimal_time <= datetime.utcnow():
                # Post immediately if optimal time has passed
                try:
                    result = await self._upload_to_platform(platform, content)
                    platform_results[platform] = {
                        'status': 'success',
                        'upload_result': result,
                        'posted_at': 'immediate',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    platform_results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'posted_at': 'immediate',
                        'timestamp': datetime.utcnow().isoformat()
                    }
            else:
                # Schedule for later
                platform_results[platform] = {
                    'status': 'scheduled',
                    'scheduled_time': optimal_time.isoformat(),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return platform_results

    async def _upload_to_platform(self, platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
Upload content to a specific platform."""
        if platform not in self.platforms:
            raise PlatformError(f"Platform {platform} not configured")
        
        return await self.platforms[platform].upload_content(content)

    async def _get_optimal_posting_times(self, platforms: List[str]) -> Dict[str, datetime]:
        """Get optimal posting times for each platform based on audience analytics."""
        # Default optimal times (would be replaced with real analytics)
        default_times = {
            'instagram': datetime.now().replace(hour=11, minute=0),  # 11 AM
            'tiktok': datetime.now().replace(hour=18, minute=0),     # 6 PM
            'youtube': datetime.now().replace(hour=14, minute=0),    # 2 PM
            'twitter': datetime.now().replace(hour=9, minute=0),     # 9 AM
            'linkedin': datetime.now().replace(hour=8, minute=0),    # 8 AM
            'spotify': datetime.now().replace(hour=12, minute=0),    # 12 PM
            'medium': datetime.now().replace(hour=10, minute=0)      # 10 AM
        }
        
        return {platform: default_times.get(platform, datetime.utcnow()) for platform in platforms}

    async def _aggregate_distribution_metrics(self, platform_results: Dict[str, Any]) -> Dict[str, Any]:
        """
Aggregate metrics from all platform distributions."""
        total_platforms = len(platform_results)
        successful_uploads = sum(1 for result in platform_results.values() if result.get('status') == 'success')
        failed_uploads = sum(1 for result in platform_results.values() if result.get('status') == 'failed')
        scheduled_uploads = sum(1 for result in platform_results.values() if result.get('status') == 'scheduled')
        
        return {
            'total_platforms': total_platforms,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'scheduled_uploads': scheduled_uploads,
            'success_rate': successful_uploads / total_platforms if total_platforms > 0 else 0,
            'distribution_score': (successful_uploads + scheduled_uploads) / total_platforms if total_platforms > 0 else 0
        }

    async def _setup_monetization_tracking(self, platform_results: Dict[str, Any]) -> Dict[str, Any]:
        """
Setup monetization tracking for successful uploads."""
        tracking_config = {
            'tracking_enabled': True,
            'tracked_platforms': [],
            'revenue_streams': {},
            'analytics_endpoints': {}
        }
        
        for platform, result in platform_results.items():
            if result.get('status') == 'success':
                tracking_config['tracked_platforms'].append(platform)
                
                # Platform-specific revenue tracking
                if platform in ['spotify', 'apple_music', 'youtube_music']:
                    tracking_config['revenue_streams'][platform] = ['streaming', 'royalties']
                elif platform in ['instagram', 'tiktok', 'youtube']:
                    tracking_config['revenue_streams'][platform] = ['ads', 'sponsorships', 'merchandise']
                elif platform in ['medium', 'substack']:
                    tracking_config['revenue_streams'][platform] = ['subscriptions', 'tips', 'affiliate']
                elif platform in ['shutterstock', 'getty', 'adobe_stock']:
                    tracking_config['revenue_streams'][platform] = ['licensing', 'downloads']
        
        return tracking_config

    async def get_aggregated_analytics(self, time_period: str = "30d") -> Dict[str, Any]:
        """Get aggregated analytics across all platforms."""
        aggregated_analytics = {
            'time_period': time_period,
            'platform_analytics': {},
            'total_metrics': {
                'total_views': 0,
                'total_engagement': 0,
                'total_revenue': 0,
                'average_engagement_rate': 0
            },
            'top_performing_content': [],
            'monetization_summary': {}
        }
        
        # Collect analytics from each platform
        for platform_name, platform in self.platforms.items():
            if platform_name in self.authenticated_platforms:
                try:
                    platform_analytics = await platform.get_analytics(time_period)
                    aggregated_analytics['platform_analytics'][platform_name] = platform_analytics
                    
                    # Add to totals
                    aggregated_analytics['total_metrics']['total_views'] += platform_analytics.get('views', 0)
                    aggregated_analytics['total_metrics']['total_engagement'] += platform_analytics.get('engagement', 0)
                    aggregated_analytics['total_metrics']['total_revenue'] += platform_analytics.get('revenue', 0)
                    
                except Exception as e:
                    self.logger.error(f"Failed to get analytics from {platform_name}: {str(e)}")
        
        # Calculate averages
        num_platforms = len(aggregated_analytics['platform_analytics'])
        if num_platforms > 0:
            total_engagement_rate = sum(
                analytics.get('engagement_rate', 0) 
                for analytics in aggregated_analytics['platform_analytics'].values()
            )
            aggregated_analytics['total_metrics']['average_engagement_rate'] = total_engagement_rate / num_platforms
        
        return aggregated_analytics


# Platform-specific implementations

class SpotifyIntegration(BasePlatformIntegration):
    """Spotify integration for musicians."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
Authenticate with Spotify."""
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=credentials['client_id'],
                client_secret=credentials['client_secret'],
                redirect_uri=credentials['redirect_uri'],
                scope="user-library-read playlist-modify-public"
            ))
            # Test authentication
            user_info = sp.current_user()
            return user_info is not None
        except Exception as e:
            self.logger.error(f"Spotify authentication failed: {str(e)}")
            return False
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload music content to Spotify (via distributors)."""
        # Note: Direct upload to Spotify requires distribution partners
        return {
            'platform': 'spotify',
            'status': 'submitted_to_distributor',
            'estimated_live_date': (datetime.utcnow() + timedelta(days=2)).isoformat(),
            'content_id': f"spotify_{content_data.get('title', 'untitled')}_{datetime.utcnow().strftime('%Y%m%d')}"
        }
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get Spotify analytics."""
        # Mock analytics data (would integrate with Spotify for Artists API)
        return {
            'platform': 'spotify',
            'content_id': content_id,
            'streams': 1250,
            'listeners': 987,
            'saves': 156,
            'revenue': 4.75,
            'countries': ['US', 'UK', 'DE', 'FR'],
            'engagement_rate': 0.125
        }
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize content for Spotify."""
        optimized = content_data.copy()
        
        # Spotify-specific optimizations
        optimized.update({
            'audio_format': 'mp3',
            'bitrate': 320,
            'sample_rate': 44100,
            'metadata': {
                'title': content_data.get('title', ''),
                'artist': content_data.get('artist', ''),
                'album': content_data.get('album', 'Single'),
                'genre': content_data.get('genre', 'Pop'),
                'release_date': content_data.get('release_date', datetime.utcnow().isoformat()),
                'isrc': content_data.get('isrc', ''),
                'explicit': content_data.get('explicit', False)
            },
            'cover_art': {
                'size': (3000, 3000),
                'format': 'JPEG',
                'quality': 95
            }
        })
        
        return optimized


class InstagramIntegration(BasePlatformIntegration):
    """
Instagram integration for visual content creators."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
Authenticate with Instagram."""
        try:
            # Initialize Instagram session
            self.session = instaloader.Instaloader()
            self.session.login(credentials['username'], credentials['password'])
            return True
        except Exception as e:
            self.logger.error(f"Instagram authentication failed: {str(e)}")
            return False
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to Instagram."""
        content_type = content_data.get('content_type', 'image')
        
        if content_type == 'image':
            return await self._upload_image_post(content_data)
        elif content_type == 'video':
            return await self._upload_video_post(content_data)
        else:
            raise ContentError(f"Unsupported content type for Instagram: {content_type}")
    
    async def _upload_image_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload image post to Instagram."""
        # Mock upload (actual implementation would use Instagram Graph API)
        return {
            'platform': 'instagram',
            'post_type': 'image',
            'post_id': f"ig_img_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'status': 'published',
            'url': f"https://instagram.com/p/mock_post_id/",
            'optimizations_applied': ['aspect_ratio_corrected', 'hashtags_optimized', 'caption_enhanced']
        }
    
    async def _upload_video_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video post to Instagram."""
        # Mock upload
        return {
            'platform': 'instagram',
            'post_type': 'video',
            'post_id': f"ig_vid_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'status': 'published',
            'url': f"https://instagram.com/p/mock_video_id/",
            'optimizations_applied': ['duration_optimized', 'quality_enhanced', 'captions_added']
        }
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get Instagram analytics."""
        return {
            'platform': 'instagram',
            'content_id': content_id,
            'views': 5420,
            'likes': 324,
            'comments': 42,
            'shares': 18,
            'saves': 67,
            'reach': 4890,
            'impressions': 6780,
            'engagement_rate': 0.089,
            'revenue': 15.75  # From sponsored content
        }
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize content for Instagram."""
        optimized = content_data.copy()
        
        content_type = content_data.get('content_type', 'image')
        
        if content_type == 'image':
            optimized.update({
                'aspect_ratios': [(1, 1), (4, 5), (16, 9)],  # Square, Portrait, Landscape
                'max_resolution': (1080, 1350),
                'format': 'JPEG',
                'quality': 85,
                'hashtag_limit': 30,
                'caption_limit': 2200
            })
        elif content_type == 'video':
            optimized.update({
                'aspect_ratio': (9, 16),  # Vertical for Reels
                'max_duration': 90,  # seconds
                'resolution': (1080, 1920),
                'format': 'MP4',
                'bitrate': '3500k',
                'fps': 30
            })
        
        # Add Instagram-specific metadata
        optimized['instagram_metadata'] = {
            'caption': await self._optimize_caption(content_data.get('description', '')),
            'hashtags': await self._generate_hashtags(content_data),
            'location': content_data.get('location'),
            'alt_text': content_data.get('alt_text', '')
        }
        
        return optimized
    
    async def _optimize_caption(self, description: str) -> str:
        """
Optimize caption for Instagram engagement."""
        # Add engagement hooks and calls-to-action
        hooks = ["💫 ", "🔥 ", "✨ ", "🚀 "]
        hook = hooks[hash(description) % len(hooks)]
        
        optimized_caption = f"{hook}{description}\n\n"
        optimized_caption += "What do you think? Let me know in the comments! 👇\n"
        optimized_caption += "Follow for more content like this! 🙏"
        
        return optimized_caption[:2200]  # Instagram caption limit
    
    async def _generate_hashtags(self, content_data: Dict[str, Any]) -> List[str]:
        """Generate optimized hashtags for Instagram."""
        base_hashtags = [
            '#content', '#creative', '#inspiration', '#motivation',
            '#follow', '#like', '#share', '#comment'
        ]
        
        # Add content-specific hashtags based on type and metadata
        content_type = content_data.get('content_type', 'image')
        if content_type == 'image':
            base_hashtags.extend(['#photography', '#photooftheday', '#instagood'])
        elif content_type == 'video':
            base_hashtags.extend(['#reels', '#viral', '#trending'])
        
        # Add creator type specific hashtags
        creator_hashtags = {
            'musician': ['#music', '#artist', '#song', '#musician'],
            'photographer': ['#photography', '#photographer', '#photoart'],
            'blogger': ['#blog', '#blogger', '#writing', '#content'],
            'influencer': ['#influencer', '#lifestyle', '#brand'],
            'comedian': ['#comedy', '#funny', '#humor', '#comedian']
        }
        
        creator_type = content_data.get('creator_type', 'influencer')
        base_hashtags.extend(creator_hashtags.get(creator_type, []))
        
        return base_hashtags[:30]  # Instagram hashtag limit


class YouTubeIntegration(BasePlatformIntegration):
    """
YouTube integration for video creators."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
Authenticate with YouTube."""
        # Mock authentication (would use YouTube Data API)
        return True
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Upload video content to YouTube."""
        return {
            'platform': 'youtube',
            'video_id': f"yt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'status': 'uploaded',
            'visibility': 'public',
            'url': f"https://youtube.com/watch?v=mock_video_id",
            'monetization_enabled': True,
            'optimizations_applied': ['title_optimized', 'description_enhanced', 'tags_added', 'thumbnail_optimized']
        }
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get YouTube analytics."""
        return {
            'platform': 'youtube',
            'content_id': content_id,
            'views': 12500,
            'likes': 892,
            'dislikes': 23,
            'comments': 156,
            'shares': 78,
            'subscribers_gained': 45,
            'watch_time_minutes': 8750,
            'revenue': 87.50,
            'cpm': 2.45,
            'engagement_rate': 0.085
        }
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize content for YouTube."""
        optimized = content_data.copy()
        
        optimized.update({
            'video_specs': {
                'resolution': (1920, 1080),
                'aspect_ratio': (16, 9),
                'format': 'MP4',
                'codec': 'H.264',
                'bitrate': '8000k',
                'fps': 30
            },
            'thumbnail': {
                'size': (1280, 720),
                'format': 'JPEG',
                'quality': 90
            },
            'youtube_metadata': {
                'title': await self._optimize_title(content_data.get('title', '')),
                'description': await self._optimize_description(content_data.get('description', '')),
                'tags': await self._generate_tags(content_data),
                'category': content_data.get('category', 'Entertainment'),
                'language': content_data.get('language', 'en'),
                'captions': True,
                'end_screen': True,
                'cards': True
            }
        })
        
        return optimized
    
    async def _optimize_title(self, title: str) -> str:
        """
Optimize YouTube title for search and engagement."""
        # Add engaging elements while keeping under 100 characters
        optimized_title = title
        if len(title) < 60:
            optimized_title += " | Must Watch!"
        
        return optimized_title[:100]
    
    async def _optimize_description(self, description: str) -> str:
        """Optimize YouTube description for SEO and engagement."""
        optimized_desc = f"{description}\n\n"
        optimized_desc += "🔔 Subscribe for more content like this!\n"
        optimized_desc += "👍 Like this video if you enjoyed it!\n"
        optimized_desc += "💬 Leave a comment with your thoughts!\n"
        optimized_desc += "🔗 Share this video with your friends!\n\n"
        optimized_desc += "Follow me on social media:\n"
        optimized_desc += "📷 Instagram: @username\n"
        optimized_desc += "🐦 Twitter: @username\n"
        optimized_desc += "📧 Business inquiries: email@example.com\n\n"
        optimized_desc += "#hashtag #related #content"
        
        return optimized_desc
    
    async def _generate_tags(self, content_data: Dict[str, Any]) -> List[str]:
        """Generate optimized tags for YouTube."""
        base_tags = ['content', 'video', 'creator', 'original', 'quality']
        
        # Add content-specific tags
        creator_tags = {
            'musician': ['music', 'song', 'artist', 'audio', 'musician'],
            'comedian': ['comedy', 'funny', 'humor', 'laugh', 'entertainment'],
            'blogger': ['blog', 'vlog', 'lifestyle', 'tips', 'advice'],
            'photographer': ['photography', 'visual', 'art', 'creative', 'tutorial'],
            'influencer': ['lifestyle', 'influencer', 'brand', 'review', 'recommendation']
        }
        
        creator_type = content_data.get('creator_type', 'influencer')
        base_tags.extend(creator_tags.get(creator_type, []))
        
        return base_tags


# Additional platform integrations would follow similar patterns...

class TikTokIntegration(BasePlatformIntegration):
    """TikTok integration for short-form video creators."""
    
    def __init__(self, platform_name: str, config: PlatformConfig):
        super().__init__(platform_name, config)
        self.api_url = "https://open-api.tiktok.com"
        self.access_token = None
        self.user_id = None
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with TikTok Open API."""
        try:
            # TikTok uses OAuth 2.0 for authentication
            client_key = credentials.get('client_key')
            client_secret = credentials.get('client_secret')
            access_token = credentials.get('access_token')
            
            if not all([client_key, client_secret, access_token]):
                raise AuthenticationError("Missing required TikTok credentials")
            
            # Verify token with TikTok API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test authentication by getting user info
            response = requests.get(
                f"{self.api_url}/v2/user/info/",
                headers=headers,
                params={'fields': 'open_id,union_id,avatar_url,display_name'}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('data'):
                    self.access_token = access_token
                    self.user_id = user_data['data'].get('open_id')
                    self.logger.info(f"TikTok authentication successful for user {self.user_id}")
                    return True
            
            self.logger.error(f"TikTok authentication failed: {response.text}")
            return False
            
        except Exception as e:
            self.logger.error(f"TikTok authentication error: {str(e)}")
            raise AuthenticationError(f"TikTok authentication failed: {str(e)}")
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload video content to TikTok."""
        try:
            if not self.access_token:
                raise ContentError("Not authenticated with TikTok")
            
            video_file = content_data.get('video_file')
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            hashtags = content_data.get('hashtags', [])
            
            if not video_file:
                raise ContentError("Video file is required for TikTok upload")
            
            # Optimize video for TikTok (vertical, max 60 seconds, MP4 format)
            optimized_video = await self._optimize_tiktok_video(video_file, content_data)
            
            # Step 1: Initialize upload
            init_response = await self._initialize_upload()
            
            if not init_response.get('upload_url'):
                raise ContentError("Failed to initialize TikTok upload")
            
            # Step 2: Upload video file
            upload_response = await self._upload_video_file(
                optimized_video, 
                init_response['upload_url']
            )
            
            # Step 3: Create post
            post_data = {
                'post_info': {
                    'title': title[:150],  # TikTok title limit
                    'description': f"{description} {' '.join([f'#{tag}' for tag in hashtags])}"[:2200],
                    'privacy_level': content_data.get('privacy', 'EVERYONE'),
                    'disable_duet': content_data.get('disable_duet', False),
                    'disable_stitch': content_data.get('disable_stitch', False)
                },
                'source_info': {
                    'source': 'PULL_FROM_URL',
                    'video_url': upload_response.get('video_url')
                }
            }
            
            # Create the post
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/v2/post/publish/",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 200:
                result = response.json()
                publish_id = result.get('data', {}).get('publish_id')
                
                # Track metrics
                await self.metrics.track_upload({
                    'platform': 'tiktok',
                    'content_type': 'video',
                    'title_length': len(title),
                    'hashtags_count': len(hashtags),
                    'success': True
                })
                
                return {
                    'platform': 'tiktok',
                    'publish_id': publish_id,
                    'status': 'uploaded',
                    'video_optimized': True,
                    'estimated_processing_time': '5-10 minutes'
                }
            else:
                raise ContentError(f"TikTok upload failed: {response.text}")
                
        except Exception as e:
            self.logger.error(f"TikTok upload error: {str(e)}")
            await self.metrics.track_upload({
                'platform': 'tiktok',
                'success': False,
                'error': str(e)
            })
            raise ContentError(f"TikTok upload failed: {str(e)}")
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get TikTok video analytics."""
        try:
            if not self.access_token:
                raise PlatformError("Not authenticated with TikTok")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get video details and metrics
            response = requests.get(
                f"{self.api_url}/v2/video/query/",
                headers=headers,
                params={
                    'fields': 'id,title,video_description,duration,cover_image_url,create_time,view_count,like_count,comment_count,share_count',
                    'video_ids': content_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get('data', {}).get('videos', [])
                
                if videos:
                    video = videos[0]
                    
                    # Calculate engagement metrics
                    views = video.get('view_count', 0)
                    likes = video.get('like_count', 0)
                    comments = video.get('comment_count', 0)
                    shares = video.get('share_count', 0)
                    
                    engagement_rate = ((likes + comments + shares) / max(views, 1)) * 100
                    
                    return {
                        'platform': 'tiktok',
                        'content_id': content_id,
                        'metrics': {
                            'views': views,
                            'likes': likes,
                            'comments': comments,
                            'shares': shares,
                            'engagement_rate': round(engagement_rate, 2),
                            'watch_time_ratio': self._calculate_watch_time_ratio(video),
                            'trending_score': self._calculate_trending_score(video)
                        },
                        'metadata': {
                            'title': video.get('title'),
                            'description': video.get('video_description'),
                            'duration': video.get('duration'),
                            'created_at': video.get('create_time'),
                            'cover_image': video.get('cover_image_url')
                        },
                        'recommendations': self._generate_tiktok_recommendations(video, engagement_rate)
                    }
                else:
                    return {'platform': 'tiktok', 'error': 'Video not found'}
            
            return {'platform': 'tiktok', 'error': 'Failed to fetch analytics'}
            
        except Exception as e:
            self.logger.error(f"TikTok analytics error: {str(e)}")
            return {'platform': 'tiktok', 'error': str(e)}
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content specifically for TikTok."""
        try:
            optimizations = {
                'platform': 'tiktok',
                'original_content': content_data,
                'optimized_content': {},
                'recommendations': []
            }
            
            # Video optimization
            if content_data.get('video_file'):
                video_opts = await self._optimize_tiktok_video(
                    content_data['video_file'], 
                    content_data
                )
                optimizations['optimized_content']['video'] = video_opts
                optimizations['recommendations'].append("Video optimized for vertical format (9:16 aspect ratio)")
            
            # Title optimization
            title = content_data.get('title', '')
            if title:
                optimized_title = self._optimize_tiktok_title(title)
                optimizations['optimized_content']['title'] = optimized_title
                if len(title) > 100:
                    optimizations['recommendations'].append("Title shortened for better TikTok display")
            
            # Hashtag optimization
            hashtags = content_data.get('hashtags', [])
            optimized_hashtags = self._optimize_tiktok_hashtags(hashtags, content_data)
            optimizations['optimized_content']['hashtags'] = optimized_hashtags
            optimizations['recommendations'].append(f"Optimized hashtags for TikTok algorithm ({len(optimized_hashtags)} hashtags)")
            
            # Timing optimization
            posting_time = self._optimize_posting_time(content_data)
            optimizations['optimized_content']['suggested_posting_time'] = posting_time
            optimizations['recommendations'].append(f"Optimal posting time: {posting_time}")
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"TikTok optimization error: {str(e)}")
            return {'platform': 'tiktok', 'error': str(e)}
    
    async def _optimize_tiktok_video(self, video_file: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video for TikTok platform requirements."""
        try:
            # TikTok video requirements:
            # - Aspect ratio: 9:16 (vertical)
            # - Duration: 15 seconds to 3 minutes (optimal: 15-30 seconds)
            # - Format: MP4
            # - Resolution: 1080x1920 recommended
            # - File size: max 287MB
            
            # For now, return optimized metadata (actual video processing would require ffmpeg)
            return {
                'optimized_file': video_file.replace('.mp4', '_tiktok_optimized.mp4'),
                'optimizations_applied': [
                    'Converted to 9:16 aspect ratio',
                    'Trimmed to optimal 30-second duration',
                    'Enhanced for mobile viewing',
                    'Optimized file size for fast upload'
                ],
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'format': 'MP4',
                'estimated_duration': '30 seconds'
            }
                
        except Exception as e:
            self.logger.error(f"Video optimization error: {str(e)}")
            return {'error': str(e)}
    
    def _optimize_tiktok_title(self, title: str) -> str:
        """Optimize title for TikTok."""
        # TikTok titles should be catchy and under 100 characters
        if len(title) <= 100:
            return title
        
        # Truncate while preserving meaning
        words = title.split()
        optimized = ""
        for word in words:
            if len(optimized + " " + word) <= 97:  # Leave space for "..."
                optimized += " " + word if optimized else word
            else:
                break
        
        return optimized + "..." if len(optimized) < len(title) else optimized
    
    def _optimize_tiktok_hashtags(self, hashtags: List[str], content_data: Dict[str, Any]) -> List[str]:
        """Optimize hashtags for TikTok algorithm."""
        # TikTok hashtag best practices:
        # - Mix trending, niche, and branded hashtags
        # - 3-5 hashtags for optimal reach
        # - Include trending challenges
        
        trending_hashtags = [
            'fyp', 'foryou', 'viral', 'trending', 'tiktok', 
            'music', 'dance', 'comedy', 'tutorial', 'tips'
        ]
        
        optimized = []
        
        # Add original hashtags (cleaned)
        for tag in hashtags[:3]:  # Limit to first 3
            clean_tag = tag.replace('#', '').lower()
            if clean_tag not in optimized:
                optimized.append(clean_tag)
        
        # Add trending hashtags if space available
        for trending in trending_hashtags:
            if len(optimized) < 5 and trending not in optimized:
                optimized.append(trending)
        
        return optimized
    
    def _optimize_posting_time(self, content_data: Dict[str, Any]) -> str:
        """Suggest optimal posting time for TikTok."""
        # TikTok peak hours: 6-10 AM and 7-9 PM EST
        # Best days: Tuesday through Thursday
        
        current_time = datetime.now()
        
        # Find next optimal time slot
        if current_time.hour < 6:
            suggested_time = current_time.replace(hour=8, minute=0)
        elif current_time.hour > 21:
            suggested_time = (current_time + timedelta(days=1)).replace(hour=8, minute=0)
        elif 10 <= current_time.hour < 19:
            suggested_time = current_time.replace(hour=20, minute=0)
        else:
            suggested_time = current_time + timedelta(hours=1)
        
        return suggested_time.strftime("%Y-%m-%d %H:%M EST")
    
    def _calculate_watch_time_ratio(self, video_data: Dict[str, Any]) -> float:
        """Calculate estimated watch time ratio."""
        # Simplified calculation based on engagement
        views = video_data.get('view_count', 0)
        likes = video_data.get('like_count', 0)
        
        if views == 0:
            return 0.0
        
        # Higher like ratio typically indicates better watch time
        like_ratio = likes / views
        estimated_watch_ratio = min(like_ratio * 20, 1.0)  # Scale and cap at 100%
        
        return round(estimated_watch_ratio, 2)
    
    def _calculate_trending_score(self, video_data: Dict[str, Any]) -> float:
        """Calculate trending potential score."""
        views = video_data.get('view_count', 0)
        likes = video_data.get('like_count', 0)
        comments = video_data.get('comment_count', 0)
        shares = video_data.get('share_count', 0)
        
        # Weighted scoring for trending potential
        score = (views * 0.4) + (likes * 1.5) + (comments * 2.0) + (shares * 3.0)
        
        # Normalize to 0-100 scale
        normalized_score = min(score / 10000, 100)
        
        return round(normalized_score, 1)
    
    def _generate_tiktok_recommendations(self, video_data: Dict[str, Any], engagement_rate: float) -> List[str]:
        """Generate optimization recommendations based on performance."""
        recommendations = []
        
        views = video_data.get('view_count', 0)
        
        if engagement_rate < 3:
            recommendations.append("Low engagement - try adding trending sounds or challenges")
        
        if views < 1000:
            recommendations.append("Low reach - consider posting at peak hours (6-10 AM or 7-9 PM EST)")
        
        if video_data.get('comment_count', 0) < views * 0.01:
            recommendations.append("Low comments - ask questions or include call-to-action in description")
        
        if video_data.get('share_count', 0) < views * 0.005:
            recommendations.append("Low shares - create more shareable content with relatable moments")
        
        duration = video_data.get('duration', 0)
        if duration > 30:
            recommendations.append("Consider shorter videos (15-30 seconds) for better completion rates")
        
        return recommendations
    
    async def _initialize_upload(self) -> Dict[str, Any]:
        """Initialize TikTok upload session."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Simulate API response for testing
        return {
            'upload_url': f"{self.api_url}/upload/session",
            'session_id': f"tiktok_session_{datetime.now().timestamp()}"
        }
    
    async def _upload_video_file(self, video_file: str, upload_url: str) -> Dict[str, Any]:
        """Upload video file to TikTok."""
        try:
            # Simulate successful upload response
            return {
                'video_url': f"{self.api_url}/video/{datetime.now().timestamp()}",
                'upload_id': f"upload_{datetime.now().timestamp()}",
                'status': 'uploaded'
            }
            
        except Exception as e:
            self.logger.error(f"Video file upload error: {str(e)}")
            return {}

class LinkedInIntegration(BasePlatformIntegration):
    """LinkedIn integration for professional content creators."""
    
    def __init__(self, platform_name: str, config: PlatformConfig):
        super().__init__(platform_name, config)
        self.api_url = "https://api.linkedin.com/v2"
        self.access_token = None
        self.person_id = None
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with LinkedIn API."""
        try:
            access_token = credentials.get('access_token')
            client_id = credentials.get('client_id')
            client_secret = credentials.get('client_secret')
            
            if not access_token:
                raise AuthenticationError("LinkedIn access token is required")
            
            # Verify token by getting user profile
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/people/~:(id,firstName,lastName,emailAddress)",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.access_token = access_token
                self.person_id = user_data.get('id')
                self.logger.info(f"LinkedIn authentication successful for user {self.person_id}")
                return True
            else:
                self.logger.error(f"LinkedIn authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"LinkedIn authentication error: {str(e)}")
            raise AuthenticationError(f"LinkedIn authentication failed: {str(e)}")
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to LinkedIn."""
        try:
            if not self.access_token:
                raise ContentError("Not authenticated with LinkedIn")
            
            content_type = content_data.get('content_type', 'text')
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare post data based on content type
            if content_type == 'article':
                post_data = await self._create_linkedin_article(content_data)
            elif content_type == 'image':
                post_data = await self._create_linkedin_image_post(content_data)
            elif content_type == 'video':
                post_data = await self._create_linkedin_video_post(content_data)
            else:
                post_data = await self._create_linkedin_text_post(content_data)
            
            # Post to LinkedIn
            response = requests.post(
                f"{self.api_url}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get('id')
                
                # Track metrics
                await self.metrics.track_upload({
                    'platform': 'linkedin',
                    'content_type': content_type,
                    'title_length': len(title),
                    'success': True
                })
                
                return {
                    'platform': 'linkedin',
                    'post_id': post_id,
                    'status': 'published',
                    'content_type': content_type,
                    'visibility': 'professional_network'
                }
            else:
                raise ContentError(f"LinkedIn upload failed: {response.text}")
                
        except Exception as e:
            self.logger.error(f"LinkedIn upload error: {str(e)}")
            await self.metrics.track_upload({
                'platform': 'linkedin',
                'success': False,
                'error': str(e)
            })
            raise ContentError(f"LinkedIn upload failed: {str(e)}")
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get LinkedIn post analytics."""
        try:
            if not self.access_token:
                raise PlatformError("Not authenticated with LinkedIn")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get post statistics
            response = requests.get(
                f"{self.api_url}/socialActions/{content_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                
                # Get additional metrics
                impressions_response = requests.get(
                    f"{self.api_url}/organizationalEntityShareStatistics",
                    headers=headers,
                    params={
                        'q': 'organizationalEntity',
                        'organizationalEntity': f"urn:li:person:{self.person_id}",
                        'ugcPosts': content_id
                    }
                )
                
                impressions_data = impressions_response.json() if impressions_response.status_code == 200 else {}
                
                # Calculate engagement metrics
                likes = stats.get('likesSummary', {}).get('totalFirstLevelLikes', 0)
                comments = stats.get('commentsSummary', {}).get('totalFirstLevelComments', 0)
                shares = stats.get('sharesSummary', {}).get('totalShares', 0)
                impressions = impressions_data.get('elements', [{}])[0].get('totalShareStatistics', {}).get('impressionCount', 0)
                
                engagement_rate = ((likes + comments + shares) / max(impressions, 1)) * 100
                
                return {
                    'platform': 'linkedin',
                    'content_id': content_id,
                    'metrics': {
                        'impressions': impressions,
                        'likes': likes,
                        'comments': comments,
                        'shares': shares,
                        'engagement_rate': round(engagement_rate, 2),
                        'click_through_rate': self._calculate_ctr(impressions_data),
                        'professional_engagement_score': self._calculate_professional_score(stats)
                    },
                    'audience_insights': {
                        'industry_breakdown': self._get_industry_breakdown(impressions_data),
                        'seniority_levels': self._get_seniority_breakdown(impressions_data),
                        'geographic_distribution': self._get_geographic_breakdown(impressions_data)
                    },
                    'recommendations': self._generate_linkedin_recommendations(stats, engagement_rate)
                }
            
            return {'platform': 'linkedin', 'error': 'Failed to fetch analytics'}
            
        except Exception as e:
            self.logger.error(f"LinkedIn analytics error: {str(e)}")
            return {'platform': 'linkedin', 'error': str(e)}
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content specifically for LinkedIn."""
        try:
            optimizations = {
                'platform': 'linkedin',
                'original_content': content_data,
                'optimized_content': {},
                'recommendations': []
            }
            
            # Content type optimization
            content_type = content_data.get('content_type', 'text')
            optimized_type = self._optimize_linkedin_content_type(content_data)
            optimizations['optimized_content']['content_type'] = optimized_type
            
            # Title optimization for professional audience
            title = content_data.get('title', '')
            if title:
                optimized_title = self._optimize_linkedin_title(title)
                optimizations['optimized_content']['title'] = optimized_title
                optimizations['recommendations'].append("Title optimized for professional engagement")
            
            # Description optimization
            description = content_data.get('description', '')
            if description:
                optimized_description = self._optimize_linkedin_description(description)
                optimizations['optimized_content']['description'] = optimized_description
                optimizations['recommendations'].append("Description enhanced with professional insights and call-to-action")
            
            # Hashtag optimization for professional network
            hashtags = content_data.get('hashtags', [])
            optimized_hashtags = self._optimize_linkedin_hashtags(hashtags, content_data)
            optimizations['optimized_content']['hashtags'] = optimized_hashtags
            optimizations['recommendations'].append(f"Professional hashtags optimized ({len(optimized_hashtags)} hashtags)")
            
            # Timing optimization for business audience
            posting_time = self._optimize_linkedin_posting_time(content_data)
            optimizations['optimized_content']['suggested_posting_time'] = posting_time
            optimizations['recommendations'].append(f"Optimal posting time for professional audience: {posting_time}")
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"LinkedIn optimization error: {str(e)}")
            return {'platform': 'linkedin', 'error': str(e)}
    
    async def _create_linkedin_text_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create LinkedIn text post data."""
        description = content_data.get('description', '')
        hashtags = content_data.get('hashtags', [])
        
        # Add hashtags to description
        if hashtags:
            description += '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])
        
        return {
            'author': f'urn:li:person:{self.person_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': description
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
    
    async def _create_linkedin_article(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create LinkedIn article post data."""
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        article_url = content_data.get('article_url', '')
        
        return {
            'author': f'urn:li:person:{self.person_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': description
                    },
                    'shareMediaCategory': 'ARTICLE',
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': description
                            },
                            'media': article_url,
                            'title': {
                                'text': title
                            }
                        }
                    ]
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
    
    async def _create_linkedin_image_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create LinkedIn image post data."""
        description = content_data.get('description', '')
        image_url = content_data.get('image_url', '')
        
        return {
            'author': f'urn:li:person:{self.person_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': description
                    },
                    'shareMediaCategory': 'IMAGE',
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': description
                            },
                            'media': image_url
                        }
                    ]
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
    
    async def _create_linkedin_video_post(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create LinkedIn video post data."""
        description = content_data.get('description', '')
        video_url = content_data.get('video_url', '')
        
        return {
            'author': f'urn:li:person:{self.person_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': description
                    },
                    'shareMediaCategory': 'VIDEO',
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': description
                            },
                            'media': video_url
                        }
                    ]
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
    
    def _optimize_linkedin_content_type(self, content_data: Dict[str, Any]) -> str:
        """Determine optimal content type for LinkedIn."""
        # LinkedIn engagement preferences: Articles > Images > Videos > Text
        if content_data.get('article_url') or len(content_data.get('description', '')) > 1000:
            return 'article'
        elif content_data.get('image_url') or content_data.get('image_file'):
            return 'image'
        elif content_data.get('video_url') or content_data.get('video_file'):
            return 'video'
        else:
            return 'text'
    
    def _optimize_linkedin_title(self, title: str) -> str:
        """Optimize title for LinkedIn professional audience."""
        # LinkedIn best practices: Professional, value-driven titles
        professional_keywords = [
            'insights', 'strategy', 'leadership', 'innovation', 'growth',
            'trends', 'best practices', 'lessons learned', 'industry update'
        ]
        
        # If title is too casual, make it more professional
        if not any(keyword in title.lower() for keyword in professional_keywords):
            if '?' in title:
                # Question format - good for LinkedIn
                return title
            else:
                # Add professional context
                return f"Key Insights: {title}"
        
        return title
    
    def _optimize_linkedin_description(self, description: str) -> str:
        """Optimize description for LinkedIn engagement."""
        # LinkedIn description best practices:
        # - Start with hook
        # - Provide value/insights
        # - Include call-to-action
        # - Use professional tone
        
        optimized = description
        
        # Add professional call-to-action if not present
        cta_keywords = ['what do you think', 'share your thoughts', 'let me know', 'connect with me']
        if not any(cta in optimized.lower() for cta in cta_keywords):
            optimized += "\n\nWhat are your thoughts on this? I'd love to hear your perspective in the comments."
        
        # Add industry context if relevant
        if len(optimized) < 200:
            optimized += "\n\n#LinkedInLearning #ProfessionalDevelopment"
        
        return optimized
    
    def _optimize_linkedin_hashtags(self, hashtags: List[str], content_data: Dict[str, Any]) -> List[str]:
        """Optimize hashtags for LinkedIn professional network."""
        # LinkedIn hashtag best practices:
        # - 3-5 relevant hashtags
        # - Mix of industry-specific and general professional tags
        # - Avoid overly casual hashtags
        
        professional_hashtags = [
            'linkedin', 'professional', 'career', 'business', 'networking',
            'leadership', 'innovation', 'strategy', 'growth', 'insights'
        ]
        
        optimized = []
        
        # Add original hashtags (filtered for professionalism)
        for tag in hashtags[:3]:
            clean_tag = tag.replace('#', '').lower()
            # Skip overly casual tags
            if clean_tag not in ['fun', 'lol', 'yolo', 'mood', 'vibes']:
                optimized.append(clean_tag)
        
        # Add professional hashtags if space available
        for prof_tag in professional_hashtags:
            if len(optimized) < 5 and prof_tag not in optimized:
                optimized.append(prof_tag)
        
        return optimized
    
    def _optimize_linkedin_posting_time(self, content_data: Dict[str, Any]) -> str:
        """Suggest optimal posting time for LinkedIn."""
        # LinkedIn peak hours: 7-9 AM and 5-7 PM on weekdays
        # Best days: Tuesday through Thursday
        
        current_time = datetime.now()
        
        # If it's weekend, suggest Monday
        if current_time.weekday() >= 5:  # Saturday or Sunday
            days_to_monday = 7 - current_time.weekday()
            suggested_time = (current_time + timedelta(days=days_to_monday)).replace(hour=8, minute=0)
        # If it's business hours
        elif 9 <= current_time.hour < 17:
            suggested_time = current_time.replace(hour=17, minute=30)  # End of business day
        # If it's evening
        elif current_time.hour >= 18:
            suggested_time = (current_time + timedelta(days=1)).replace(hour=8, minute=0)  # Next morning
        else:
            suggested_time = current_time.replace(hour=8, minute=0)  # Morning
        
        return suggested_time.strftime("%Y-%m-%d %H:%M (Business Hours)")
    
    def _calculate_ctr(self, impressions_data: Dict[str, Any]) -> float:
        """Calculate click-through rate."""
        # Simplified CTR calculation
        clicks = impressions_data.get('elements', [{}])[0].get('totalShareStatistics', {}).get('clickCount', 0)
        impressions = impressions_data.get('elements', [{}])[0].get('totalShareStatistics', {}).get('impressionCount', 0)
        
        if impressions > 0:
            return round((clicks / impressions) * 100, 2)
        return 0.0
    
    def _calculate_professional_score(self, stats: Dict[str, Any]) -> float:
        """Calculate professional engagement score."""
        # LinkedIn-specific scoring based on professional interactions
        likes = stats.get('likesSummary', {}).get('totalFirstLevelLikes', 0)
        comments = stats.get('commentsSummary', {}).get('totalFirstLevelComments', 0)
        shares = stats.get('sharesSummary', {}).get('totalShares', 0)
        
        # Weight comments and shares higher for professional context
        professional_score = (likes * 1) + (comments * 3) + (shares * 5)
        
        # Normalize to 0-100 scale
        normalized_score = min(professional_score / 100, 100)
        
        return round(normalized_score, 1)
    
    def _get_industry_breakdown(self, impressions_data: Dict[str, Any]) -> Dict[str, int]:
        """Get industry breakdown from impressions data."""
        # Simulated industry breakdown (would come from actual API)
        return {
            'Technology': 35,
            'Finance': 20,
            'Healthcare': 15,
            'Education': 10,
            'Consulting': 10,
            'Other': 10
        }
    
    def _get_seniority_breakdown(self, impressions_data: Dict[str, Any]) -> Dict[str, int]:
        """Get seniority level breakdown."""
        return {
            'Senior': 40,
            'Mid-level': 35,
            'Entry-level': 15,
            'Executive': 10
        }
    
    def _get_geographic_breakdown(self, impressions_data: Dict[str, Any]) -> Dict[str, int]:
        """Get geographic distribution."""
        return {
            'United States': 45,
            'Canada': 15,
            'United Kingdom': 12,
            'Germany': 8,
            'Other': 20
        }
    
    def _generate_linkedin_recommendations(self, stats: Dict[str, Any], engagement_rate: float) -> List[str]:
        """Generate LinkedIn-specific optimization recommendations."""
        recommendations = []
        
        likes = stats.get('likesSummary', {}).get('totalFirstLevelLikes', 0)
        comments = stats.get('commentsSummary', {}).get('totalFirstLevelComments', 0)
        shares = stats.get('sharesSummary', {}).get('totalShares', 0)
        
        if engagement_rate < 2:
            recommendations.append("Low engagement - try asking thought-provoking questions to encourage discussion")
        
        if comments < likes * 0.1:
            recommendations.append("Low comment ratio - include calls-to-action that invite professional dialogue")
        
        if shares < likes * 0.05:
            recommendations.append("Low share rate - create more valuable, shareable insights for professional networks")
        
        if engagement_rate > 5:
            recommendations.append("High engagement - consider posting similar content to maintain momentum")
        
        recommendations.append("Post during business hours (7-9 AM or 5-7 PM) for maximum professional visibility")
        
        return recommendations

class MediumIntegration(BasePlatformIntegration):
    """Medium integration for bloggers and writers."""
    
    def __init__(self, platform_name: str, config: PlatformConfig):
        super().__init__(platform_name, config)
        self.api_url = "https://api.medium.com/v1"
        self.access_token = None
        self.user_id = None
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with Medium API."""
        try:
            access_token = credentials.get('access_token')
            
            if not access_token:
                raise AuthenticationError("Medium access token is required")
            
            # Verify token by getting user info
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.get(f"{self.api_url}/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.access_token = access_token
                self.user_id = user_data.get('data', {}).get('id')
                self.logger.info(f"Medium authentication successful for user {self.user_id}")
                return True
            else:
                self.logger.error(f"Medium authentication failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Medium authentication error: {str(e)}")
            raise AuthenticationError(f"Medium authentication failed: {str(e)}")
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload article to Medium."""
        try:
            if not self.access_token:
                raise ContentError("Not authenticated with Medium")
            
            title = content_data.get('title', '')
            content = content_data.get('content', '')
            description = content_data.get('description', '')
            tags = content_data.get('tags', [])
            
            if not title or not content:
                raise ContentError("Title and content are required for Medium article")
            
            # Optimize content for Medium
            optimized_content = await self._optimize_medium_content(content, content_data)
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Prepare article data
            article_data = {
                'title': title,
                'contentFormat': 'markdown',  # Medium supports HTML and Markdown
                'content': optimized_content,
                'tags': tags[:5],  # Medium allows up to 5 tags
                'publishStatus': content_data.get('publish_status', 'draft'),  # draft or public
                'license': content_data.get('license', 'all-rights-reserved'),
                'notifyFollowers': content_data.get('notify_followers', False)
            }
            
            # Add canonical URL if provided
            if content_data.get('canonical_url'):
                article_data['canonicalUrl'] = content_data['canonical_url']
            
            # Post to Medium
            response = requests.post(
                f"{self.api_url}/users/{self.user_id}/posts",
                headers=headers,
                json=article_data
            )
            
            if response.status_code == 201:
                result = response.json()
                article_data = result.get('data', {})
                
                # Track metrics
                await self.metrics.track_upload({
                    'platform': 'medium',
                    'content_type': 'article',
                    'title_length': len(title),
                    'content_length': len(content),
                    'tags_count': len(tags),
                    'success': True
                })
                
                return {
                    'platform': 'medium',
                    'article_id': article_data.get('id'),
                    'article_url': article_data.get('url'),
                    'status': article_data.get('publishStatus'),
                    'published_at': article_data.get('publishedAt'),
                    'license': article_data.get('license'),
                    'tags': article_data.get('tags', [])
                }
            else:
                raise ContentError(f"Medium upload failed: {response.text}")
                
        except Exception as e:
            self.logger.error(f"Medium upload error: {str(e)}")
            await self.metrics.track_upload({
                'platform': 'medium',
                'success': False,
                'error': str(e)
            })
            raise ContentError(f"Medium upload failed: {str(e)}")
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        """Get Medium article analytics."""
        try:
            if not self.access_token:
                raise PlatformError("Not authenticated with Medium")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Get article details
            response = requests.get(
                f"{self.api_url}/posts/{content_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                article_data = response.json().get('data', {})
                
                # Medium doesn't provide detailed analytics via API
                # This would typically require web scraping or Premium partnership
                # For now, we'll return basic article information
                
                return {
                    'platform': 'medium',
                    'content_id': content_id,
                    'metrics': {
                        'views': 'Not available via API',
                        'reads': 'Not available via API',
                        'claps': 'Not available via API',
                        'responses': 'Not available via API',
                        'reading_time': self._calculate_reading_time(article_data.get('content', '')),
                        'estimated_reach': self._estimate_medium_reach(article_data)
                    },
                    'metadata': {
                        'title': article_data.get('title'),
                        'url': article_data.get('url'),
                        'published_at': article_data.get('publishedAt'),
                        'license': article_data.get('license'),
                        'tags': article_data.get('tags', []),
                        'author_id': article_data.get('authorId')
                    },
                    'recommendations': self._generate_medium_recommendations(article_data),
                    'note': 'Medium API has limited analytics. Full metrics available through Medium Partner Program.'
                }
            
            return {'platform': 'medium', 'error': 'Article not found or access denied'}
            
        except Exception as e:
            self.logger.error(f"Medium analytics error: {str(e)}")
            return {'platform': 'medium', 'error': str(e)}
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content specifically for Medium."""
        try:
            optimizations = {
                'platform': 'medium',
                'original_content': content_data,
                'optimized_content': {},
                'recommendations': []
            }
            
            # Title optimization for Medium's algorithm
            title = content_data.get('title', '')
            if title:
                optimized_title = self._optimize_medium_title(title)
                optimizations['optimized_content']['title'] = optimized_title
                if optimized_title != title:
                    optimizations['recommendations'].append("Title optimized for Medium's recommendation algorithm")
            
            # Content optimization for readability
            content = content_data.get('content', '')
            if content:
                optimized_content = await self._optimize_medium_content(content, content_data)
                optimizations['optimized_content']['content'] = optimized_content
                optimizations['recommendations'].append("Content formatted for optimal Medium reading experience")
            
            # Tags optimization
            tags = content_data.get('tags', [])
            optimized_tags = self._optimize_medium_tags(tags, content_data)
            optimizations['optimized_content']['tags'] = optimized_tags
            optimizations['recommendations'].append(f"Tags optimized for discoverability ({len(optimized_tags)} tags)")
            
            # SEO optimization
            seo_recommendations = self._optimize_medium_seo(content_data)
            optimizations['seo_recommendations'] = seo_recommendations
            optimizations['recommendations'].extend(seo_recommendations)
            
            # Publishing timing
            posting_time = self._optimize_medium_posting_time(content_data)
            optimizations['optimized_content']['suggested_posting_time'] = posting_time
            optimizations['recommendations'].append(f"Optimal publishing time: {posting_time}")
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Medium optimization error: {str(e)}")
            return {'platform': 'medium', 'error': str(e)}
    
    async def _optimize_medium_content(self, content: str, content_data: Dict[str, Any]) -> str:
        """Optimize content for Medium's format and readability."""
        # Medium content optimization:
        # - Use headers for structure
        # - Add compelling intro
        # - Include call-to-action
        # - Optimize for 7-minute read time
        
        optimized = content
        
        # Add engaging intro if not present
        if not optimized.startswith('#') and len(optimized.split('\n')[0]) < 100:
            intro = "In this article, we'll explore insights that could transform your perspective on this topic.\n\n"
            optimized = intro + optimized
        
        # Ensure proper heading structure
        if '##' not in optimized and len(optimized) > 1000:
            # Break long content into sections
            paragraphs = optimized.split('\n\n')
            if len(paragraphs) > 3:
                # Add section headers
                mid_point = len(paragraphs) // 2
                paragraphs.insert(mid_point, "## Key Insights")
                optimized = '\n\n'.join(paragraphs)
        
        # Add call-to-action at the end
        if not any(cta in optimized.lower() for cta in ['clap', 'follow', 'subscribe', 'share your thoughts']):
            cta = "\n\n---\n\n👏 **If this resonated with you, please clap and follow for more insights!** Share your thoughts in the comments below — I'd love to hear your perspective."
            optimized += cta
        
        return optimized
    
    def _optimize_medium_title(self, title: str) -> str:
        """Optimize title for Medium's recommendation algorithm."""
        # Medium title best practices:
        # - 60-100 characters optimal
        # - Include emotional hooks
        # - Use numbers when relevant
        # - Avoid clickbait
        
        # If title is too short, enhance it
        if len(title) < 40:
            enhancers = [
                "The Ultimate Guide to",
                "Everything You Need to Know About",
                "A Deep Dive Into",
                "The Complete Story of",
                "Why Everyone's Talking About"
            ]
            
            # Add enhancer if title doesn't already have one
            if not any(enhancer.lower() in title.lower() for enhancer in enhancers):
                return f"A Deep Dive Into {title}"
        
        # If title is too long, optimize it
        if len(title) > 100:
            # Keep first part, add intrigue
            words = title.split()
            optimized = ' '.join(words[:10])
            if len(optimized) < len(title):
                optimized += "..."
            return optimized
        
        return title
    
    def _optimize_medium_tags(self, tags: List[str], content_data: Dict[str, Any]) -> List[str]:
        """Optimize tags for Medium discoverability."""
        # Medium tag best practices:
        # - Use up to 5 tags
        # - Mix popular and niche tags
        # - Include relevant topic tags
        
        popular_medium_tags = [
            'programming', 'javascript', 'python', 'technology', 'web-development',
            'data-science', 'machine-learning', 'artificial-intelligence', 'startup',
            'entrepreneurship', 'productivity', 'self-improvement', 'writing',
            'design', 'ux', 'leadership', 'business', 'marketing', 'innovation'
        ]
        
        optimized = []
        
        # Add original tags (up to 3)
        for tag in tags[:3]:
            clean_tag = tag.replace('#', '').lower().replace(' ', '-')
            if clean_tag not in optimized:
                optimized.append(clean_tag)
        
        # Add relevant popular tags if space available
        content_text = (content_data.get('content', '') + ' ' + content_data.get('title', '')).lower()
        
        for popular_tag in popular_medium_tags:
            if len(optimized) < 5:
                # Check if tag is relevant to content
                if any(keyword in content_text for keyword in popular_tag.split('-')):
                    if popular_tag not in optimized:
                        optimized.append(popular_tag)
        
        return optimized[:5]  # Maximum 5 tags for Medium
    
    def _optimize_medium_seo(self, content_data: Dict[str, Any]) -> List[str]:
        """Generate SEO optimization recommendations for Medium."""
        recommendations = []
        
        title = content_data.get('title', '')
        content = content_data.get('content', '')
        
        # Title SEO
        if len(title) < 50:
            recommendations.append("Consider extending title to 50-60 characters for better SEO")
        
        # Content length
        word_count = len(content.split())
        if word_count < 1000:
            recommendations.append("Consider expanding content to 1000+ words for better Medium algorithm performance")
        elif word_count > 3000:
            recommendations.append("Consider breaking long content into a series for better engagement")
        
        # Heading structure
        if '##' not in content:
            recommendations.append("Add section headers (##) to improve readability and SEO")
        
        # Links
        if 'http' not in content:
            recommendations.append("Consider adding relevant external links to increase article authority")
        
        return recommendations
    
    def _optimize_medium_posting_time(self, content_data: Dict[str, Any]) -> str:
        """Suggest optimal posting time for Medium."""
        # Medium peak times: Tuesday-Thursday, 1-3 PM EST
        # Best engagement: Weekday mornings and early afternoons
        
        current_time = datetime.now()
        
        # If it's weekend, suggest Tuesday
        if current_time.weekday() >= 5:  # Saturday or Sunday
            days_to_tuesday = (1 - current_time.weekday()) % 7
            if days_to_tuesday == 0:  # It's already Tuesday
                days_to_tuesday = 7
            suggested_time = (current_time + timedelta(days=days_to_tuesday)).replace(hour=14, minute=0)
        # If it's optimal time already
        elif 1 <= current_time.weekday() <= 3 and 13 <= current_time.hour <= 15:
            suggested_time = current_time + timedelta(hours=1)
        # Otherwise suggest next optimal time
        else:
            if current_time.hour < 13:
                suggested_time = current_time.replace(hour=14, minute=0)
            else:
                # Next day at 2 PM
                suggested_time = (current_time + timedelta(days=1)).replace(hour=14, minute=0)
        
        return suggested_time.strftime("%Y-%m-%d %H:%M EST")
    
    def _calculate_reading_time(self, content: str) -> str:
        """Calculate estimated reading time for the article."""
        # Average reading speed: 200-250 words per minute
        word_count = len(content.split())
        reading_time_minutes = word_count / 225  # Use 225 WPM average
        
        if reading_time_minutes < 1:
            return "< 1 minute"
        elif reading_time_minutes < 60:
            return f"{int(reading_time_minutes)} minute{'s' if reading_time_minutes > 1 else ''}"
        else:
            hours = int(reading_time_minutes // 60)
            minutes = int(reading_time_minutes % 60)
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
    
    def _estimate_medium_reach(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate article reach based on various factors."""
        # Simplified reach estimation
        tags = article_data.get('tags', [])
        title_length = len(article_data.get('title', ''))
        
        # Base reach estimation
        base_reach = 100
        
        # Tag popularity bonus
        popular_tags = ['programming', 'javascript', 'python', 'startup', 'productivity']
        tag_bonus = len([tag for tag in tags if tag in popular_tags]) * 50
        
        # Title optimization bonus
        title_bonus = 25 if 50 <= title_length <= 100 else 0
        
        estimated_reach = base_reach + tag_bonus + title_bonus
        
        return {
            'estimated_views': f"{estimated_reach}-{estimated_reach * 3}",
            'factors': {
                'tag_popularity': tag_bonus,
                'title_optimization': title_bonus,
                'base_reach': base_reach
            }
        }
    
    def _generate_medium_recommendations(self, article_data: Dict[str, Any]) -> List[str]:
        """Generate Medium-specific optimization recommendations."""
        recommendations = []
        
        tags = article_data.get('tags', [])
        title = article_data.get('title', '')
        
        if len(tags) < 3:
            recommendations.append("Add more relevant tags (up to 5) to increase discoverability")
        
        if len(title) < 50:
            recommendations.append("Consider a longer, more descriptive title for better engagement")
        
        if article_data.get('license') == 'all-rights-reserved':
            recommendations.append("Consider using Creative Commons license to increase sharing potential")
        
        recommendations.append("Engage with other writers' articles to build your Medium network")
        recommendations.append("Publish consistently (2-3 times per week) to grow your following")
        recommendations.append("Join Medium publications in your niche for wider reach")
        
        return recommendations

class GenericPlatformIntegration(BasePlatformIntegration):
    """
Generic platform integration for unsupported platforms."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return True
    
    async def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        return {'platform': self.platform_name, 'status': 'not_implemented'}
    
    async def get_analytics(self, content_id: str) -> Dict[str, Any]:
        return {'platform': self.platform_name, 'analytics': 'not_available'}
    
    async def optimize_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        return content_data
