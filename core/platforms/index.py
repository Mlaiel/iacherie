"""Platform Integration Index Module

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
    """
Factory for creating platform instances"""
    
    @staticmethod
    def create_platform(platform_type: PlatformType, config: PlatformConfig) -> PlatformBase:
        """
Create platform instance by type"""
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
        """
Get platform class by type"""
        platform_class = PLATFORM_REGISTRY.get(platform_type)
        
        if not platform_class:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        return platform_class
    
    @staticmethod
    def is_platform_supported(platform_type: PlatformType) -> bool:
        """Check if platform type is supported"""
        return platform_type in PLATFORM_REGISTRY


class PlatformEcosystem:
    """
Complete platform ecosystem manager"""
    
    def __init__(self):
        """
Initialize platform ecosystem"""
        self.factory = PlatformFactory()
        self.connector: Optional[PlatformConnector] = None
        self.distributor: Optional[PlatformDistributor] = None
        self.aggregator: Optional[PlatformAggregator] = None
        self.monitor: Optional[PlatformMonitor] = None
        
    async def initialize(self):
        """
Initialize all ecosystem components"""
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
        try:
                    # Request validation
                    if not platform_type:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_platform_info_request(platform_type)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_platform_info failed: {e}")
                    return {"status": "error", "message": str(e)}
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
    """
Shutdown global ecosystem"""
    global _global_ecosystem
    
    if _global_ecosystem:
        await _global_ecosystem.shutdown()
        _global_ecosystem = None


# Convenience functions
def create_platform(platform_type: PlatformType, config: PlatformConfig) -> PlatformBase:
    """
Create platform instance"""
    return PlatformFactory.create_platform(platform_type, config)


def get_available_platforms() -> List[PlatformType]:
    """
Get available platforms"""
    return PlatformFactory.get_available_platforms()


def is_platform_supported(platform_type: PlatformType) -> bool:
    """
Check if platform is supported"""
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
