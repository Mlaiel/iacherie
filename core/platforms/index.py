"""
Platform Integration Index Module

Central index for all platform integrations and utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from typing import Dict, List, Type, Optional
import logging

from .base import PlatformBase, PlatformType, PlatformConfig
from .distributor import PlatformDistributor, DistributionStrategy
from .aggregator import PlatformAggregator, AggregationType
from .monitor import PlatformMonitor, MonitorSeverity
from .connector import PlatformConnector, get_connector

# Platform implementations
from .spotify import SpotifyPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .tiktok import TikTokPlatform
from .twitter import TwitterPlatform
from .facebook import FacebookPlatform
from .twitch import TwitchPlatform
from .soundcloud import SoundCloudPlatform
from .apple_music import AppleMusicPlatform
from .bandcamp import BandcampPlatform
from .reddit import RedditPlatform
from .linkedin import LinkedInPlatform
from .pinterest import PinterestPlatform
from .snapchat import SnapchatPlatform
from .discord import DiscordPlatform
from .telegram import TelegramPlatform
from .whatsapp import WhatsAppPlatform
from .vimeo import VimeoPlatform
from .clubhouse import ClubhousePlatform
from .medium import MediumPlatform
from .mastodon import MastodonPlatform
from .bereal import BeRealPlatform
from .onlyfans import OnlyFansPlatform
from .patreon import PatreonPlatform
from .substack import SubstackPlatform
from .threads import ThreadsPlatform
from .kick import KickPlatform
from .rumble import RumblePlatform

logger = logging.getLogger(__name__)


# Platform registry mapping
PLATFORM_REGISTRY: Dict[PlatformType, Type[PlatformBase]] = {
    # Core original platforms (16)
    PlatformType.SPOTIFY: SpotifyPlatform,
    PlatformType.YOUTUBE: YouTubePlatform,
    PlatformType.INSTAGRAM: InstagramPlatform,
    PlatformType.TIKTOK: TikTokPlatform,
    PlatformType.TWITTER: TwitterPlatform,
    PlatformType.FACEBOOK: FacebookPlatform,
    PlatformType.TWITCH: TwitchPlatform,
    PlatformType.SOUNDCLOUD: SoundCloudPlatform,
    PlatformType.APPLE_MUSIC: AppleMusicPlatform,
    PlatformType.BANDCAMP: BandcampPlatform,
    PlatformType.REDDIT: RedditPlatform,
    PlatformType.LINKEDIN: LinkedInPlatform,
    PlatformType.PINTEREST: PinterestPlatform,
    PlatformType.SNAPCHAT: SnapchatPlatform,
    PlatformType.DISCORD: DiscordPlatform,
    PlatformType.TELEGRAM: TelegramPlatform,
    
    # Extended platforms (12)
    PlatformType.WHATSAPP: WhatsAppPlatform,
    PlatformType.VIMEO: VimeoPlatform,
    PlatformType.CLUBHOUSE: ClubhousePlatform,
    PlatformType.MEDIUM: MediumPlatform,
    PlatformType.MASTODON: MastodonPlatform,
    PlatformType.BEREAL: BeRealPlatform,
    PlatformType.ONLYFANS: OnlyFansPlatform,
    PlatformType.PATREON: PatreonPlatform,
    PlatformType.SUBSTACK: SubstackPlatform,
    PlatformType.THREADS: ThreadsPlatform,
    PlatformType.KICK: KickPlatform,
    PlatformType.RUMBLE: RumblePlatform,
}


class PlatformFactory:
    """Factory for creating platform instances"""
    
    @staticmethod
    def create_platform(platform_type: PlatformType, config: PlatformConfig) -> PlatformBase:
        """Create platform instance by type"""
        platform_class = PLATFORM_REGISTRY.get(platform_type)
        
        if not platform_class:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        return platform_class(config)
    
    @staticmethod
    def get_available_platforms() -> List[PlatformType]:
        """Get list of available platform types"""



        return list(PLATFORM_REGISTRY.keys())
    
    @staticmethod
    def get_platform_class(platform_type: PlatformType) -> Type[PlatformBase]:
        """Get platform class by type"""
        platform_class = PLATFORM_REGISTRY.get(platform_type)
        
        if not platform_class:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        return platform_class
    
    @staticmethod
    def is_platform_supported(platform_type: PlatformType) -> bool:
        """Check if platform type is supported"""



        return platform_type in PLATFORM_REGISTRY


class PlatformEcosystem:
    """Complete platform ecosystem manager"""
    
    def __init__(self):
        """Initialize platform ecosystem"""
        self.factory = PlatformFactory()
        self.connector: Optional[PlatformConnector] = None
        self.distributor: Optional[PlatformDistributor] = None
        self.aggregator: Optional[PlatformAggregator] = None
        self.monitor: Optional[PlatformMonitor] = None
        
    async def initialize(self):
        """Initialize all ecosystem components"""



        try:
            # Initialize connector
            self.connector = await get_connector()
            
            # Initialize other components (they would need platform manager)
            # This is a simplified initialization
            logger.info("Platform ecosystem initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize platform ecosystem: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown ecosystem components"""



        try:
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            if self.connector:
                await self.connector.stop()
            
            logger.info("Platform ecosystem shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during ecosystem shutdown: {e}")
    
    def get_platform_info(self, platform_type: PlatformType) -> Dict[str, str]:
        """Get platform information"""
        platform_info = {
            # Core platforms
            PlatformType.SPOTIFY: {
                "name": "Spotify",
                "category": "Music Streaming",
                "description": "Global music streaming and podcast platform",
                "api_documentation": "https://developer.spotify.com/documentation/web-api/",
                "content_types": "audio, playlist, album"
            },
            PlatformType.YOUTUBE: {
                "name": "YouTube",
                "category": "Video Platform",
                "description": "Global video sharing and streaming platform",
                "api_documentation": "https://developers.google.com/youtube/v3",
                "content_types": "video, playlist, live_stream"
            },
            PlatformType.INSTAGRAM: {
                "name": "Instagram",
                "category": "Social Media",
                "description": "Photo and video sharing social network",
                "api_documentation": "https://developers.facebook.com/docs/instagram-api/",
                "content_types": "image, video, story, reel"
            },
            PlatformType.TIKTOK: {
                "name": "TikTok",
                "category": "Social Media",
                "description": "Short-form video social platform",
                "api_documentation": "https://developers.tiktok.com/",
                "content_types": "video, live_stream"
            },
            PlatformType.TWITTER: {
                "name": "Twitter/X",
                "category": "Social Media",
                "description": "Microblogging and social networking",
                "api_documentation": "https://developer.twitter.com/en/docs",
                "content_types": "text, image, video, thread"
            },
            PlatformType.FACEBOOK: {
                "name": "Facebook",
                "category": "Social Media",
                "description": "Social networking platform",
                "api_documentation": "https://developers.facebook.com/docs/",
                "content_types": "text, image, video, live_stream"
            },
            PlatformType.TWITCH: {
                "name": "Twitch",
                "category": "Live Streaming",
                "description": "Live streaming platform for gaming and entertainment",
                "api_documentation": "https://dev.twitch.tv/docs/api/",
                "content_types": "live_stream, video, clip"
            },
            PlatformType.SOUNDCLOUD: {
                "name": "SoundCloud",
                "category": "Audio Platform",
                "description": "Audio distribution and sharing platform",
                "api_documentation": "https://developers.soundcloud.com/docs/api",
                "content_types": "audio, playlist, podcast"
            },
            PlatformType.APPLE_MUSIC: {
                "name": "Apple Music",
                "category": "Music Streaming",
                "description": "Apple's music streaming service",
                "api_documentation": "https://developer.apple.com/documentation/applemusicapi/",
                "content_types": "audio, playlist, album"
            },
            PlatformType.BANDCAMP: {
                "name": "Bandcamp",
                "category": "Music Platform",
                "description": "Independent music platform and marketplace",
                "api_documentation": "https://bandcamp.com/developer",
                "content_types": "audio, album, merchandise"
            },
            PlatformType.REDDIT: {
                "name": "Reddit",
                "category": "Social News",
                "description": "Social news aggregation and discussion",
                "api_documentation": "https://www.reddit.com/dev/api/",
                "content_types": "text, image, video, link"
            },
            PlatformType.LINKEDIN: {
                "name": "LinkedIn",
                "category": "Professional Network",
                "description": "Professional networking platform",
                "api_documentation": "https://docs.microsoft.com/en-us/linkedin/",
                "content_types": "text, image, video, article"
            },
            PlatformType.PINTEREST: {
                "name": "Pinterest",
                "category": "Visual Discovery",
                "description": "Visual discovery and idea platform",
                "api_documentation": "https://developers.pinterest.com/docs/api/",
                "content_types": "image, video, pin"
            },
            PlatformType.SNAPCHAT: {
                "name": "Snapchat",
                "category": "Social Media",
                "description": "Multimedia messaging and content platform",
                "api_documentation": "https://kit.snapchat.com/docs/",
                "content_types": "image, video, story, ar_lens"
            },
            PlatformType.DISCORD: {
                "name": "Discord",
                "category": "Communication",
                "description": "Communication platform for communities",
                "api_documentation": "https://discord.com/developers/docs/",
                "content_types": "text, image, video, voice"
            },
            PlatformType.TELEGRAM: {
                "name": "Telegram",
                "category": "Messaging",
                "description": "Cloud-based instant messaging",
                "api_documentation": "https://core.telegram.org/api",
                "content_types": "text, image, video, document"
            },
            
            # Extended platforms
            PlatformType.WHATSAPP: {
                "name": "WhatsApp Business",
                "category": "Business Messaging",
                "description": "Business messaging and communication",
                "api_documentation": "https://developers.facebook.com/docs/whatsapp/",
                "content_types": "text, image, video, document"
            },
            PlatformType.VIMEO: {
                "name": "Vimeo",
                "category": "Video Platform",
                "description": "Professional video hosting and streaming",
                "api_documentation": "https://developer.vimeo.com/api",
                "content_types": "video, live_stream"
            },
            PlatformType.CLUBHOUSE: {
                "name": "Clubhouse",
                "category": "Audio Social",
                "description": "Audio-based social networking",
                "api_documentation": "https://www.clubhouseapi.com/",
                "content_types": "audio, live_audio"
            },
            PlatformType.MEDIUM: {
                "name": "Medium",
                "category": "Publishing",
                "description": "Article publishing and blogging platform",
                "api_documentation": "https://github.com/Medium/medium-api-docs",
                "content_types": "text, image"
            },
            PlatformType.MASTODON: {
                "name": "Mastodon",
                "category": "Decentralized Social",
                "description": "Decentralized social networking",
                "api_documentation": "https://docs.joinmastodon.org/api/",
                "content_types": "text, image, video"
            },
            PlatformType.BEREAL: {
                "name": "BeReal",
                "category": "Social Media",
                "description": "Authentic social sharing platform",
                "api_documentation": "https://developers.bereal.com/",
                "content_types": "image, video"
            },
            PlatformType.ONLYFANS: {
                "name": "OnlyFans",
                "category": "Content Creator",
                "description": "Content creator subscription platform",
                "api_documentation": "https://onlyfans.com/api-docs",
                "content_types": "image, video, live_stream"
            },
            PlatformType.PATREON: {
                "name": "Patreon",
                "category": "Creator Economy",
                "description": "Creator membership and subscription platform",
                "api_documentation": "https://docs.patreon.com/",
                "content_types": "text, image, video, audio"
            },
            PlatformType.SUBSTACK: {
                "name": "Substack",
                "category": "Newsletter Publishing",
                "description": "Newsletter publishing platform",
                "api_documentation": "https://substack.com/api",
                "content_types": "text, image, newsletter"
            },
            PlatformType.THREADS: {
                "name": "Threads",
                "category": "Social Media",
                "description": "Meta's text-based conversation platform",
                "api_documentation": "https://developers.facebook.com/docs/threads/",
                "content_types": "text, image, video"
            },
            PlatformType.KICK: {
                "name": "Kick",
                "category": "Live Streaming",
                "description": "Live streaming platform",
                "api_documentation": "https://kick.com/developer-api",
                "content_types": "live_stream, video, clip"
            },
            PlatformType.RUMBLE: {
                "name": "Rumble",
                "category": "Video Platform",
                "description": "Video sharing platform",
                "api_documentation": "https://rumble.com/developer",
                "content_types": "video, live_stream"
            }
        }
        
        return platform_info.get(platform_type, {
            "name": platform_type.value.title(),
            "category": "Unknown",
            "description": f"{platform_type.value} platform integration",
            "api_documentation": "Not available",
            "content_types": "Unknown"
        })
    
    def get_ecosystem_stats(self) -> Dict[str, int]:
        """Get ecosystem statistics"""



        return {
            "total_platforms": len(PLATFORM_REGISTRY),
            "core_platforms": 16,
            "extended_platforms": 12,
            "social_media_platforms": 12,
            "video_platforms": 6,
            "audio_platforms": 4,
            "messaging_platforms": 4,
            "creator_economy_platforms": 3,
            "professional_platforms": 2,
            "decentralized_platforms": 1
        }


# Global ecosystem instance
_global_ecosystem: Optional[PlatformEcosystem] = None


async def get_ecosystem() -> PlatformEcosystem:
    """Get global ecosystem instance"""
    global _global_ecosystem
    
    if _global_ecosystem is None:
        _global_ecosystem = PlatformEcosystem()
        await _global_ecosystem.initialize()
    
    return _global_ecosystem


async def shutdown_ecosystem():
    """Shutdown global ecosystem"""
    global _global_ecosystem
    
    if _global_ecosystem:
        await _global_ecosystem.shutdown()
        _global_ecosystem = None


# Convenience functions
def create_platform(platform_type: PlatformType, config: PlatformConfig) -> PlatformBase:
    """Create platform instance"""



    return PlatformFactory.create_platform(platform_type, config)


def get_available_platforms() -> List[PlatformType]:
    """Get available platforms"""



    return PlatformFactory.get_available_platforms()


def is_platform_supported(platform_type: PlatformType) -> bool:
    """Check if platform is supported"""



    return PlatformFactory.is_platform_supported(platform_type)


# Export main components
__all__ = [
    # Core classes
    'PlatformBase',
    'PlatformType', 
    'PlatformConfig',
    'PlatformFactory',
    'PlatformEcosystem',
    
    # Management components
    'PlatformDistributor',
    'PlatformAggregator', 
    'PlatformMonitor',
    'PlatformConnector',
    
    # Platform implementations
    'SpotifyPlatform',
    'YouTubePlatform',
    'InstagramPlatform',
    'TikTokPlatform',
    'TwitterPlatform',
    'FacebookPlatform',
    'TwitchPlatform',
    'SoundCloudPlatform',
    'AppleMusicPlatform',
    'BandcampPlatform',
    'RedditPlatform',
    'LinkedInPlatform',
    'PinterestPlatform',
    'SnapchatPlatform',
    'DiscordPlatform',
    'TelegramPlatform',
    'WhatsAppPlatform',
    'VimeoPlatform',
    'ClubhousePlatform',
    'MediumPlatform',
    'MastodonPlatform',
    'BeRealPlatform',
    'OnlyFansPlatform',
    'PatreonPlatform',
    'SubstackPlatform',
    'ThreadsPlatform',
    'KickPlatform',
    'RumblePlatform',
    
    # Utility functions
    'create_platform',
    'get_available_platforms',
    'is_platform_supported',
    'get_ecosystem',
    'shutdown_ecosystem',
    
    # Registry
    'PLATFORM_REGISTRY'
]
