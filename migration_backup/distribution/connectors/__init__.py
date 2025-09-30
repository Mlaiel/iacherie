"""
Connectors Module - Consolidated Platform Integration Connectors
==============================================================

Enterprise-grade platform connectors supporting 40+ platforms through
consolidated architecture. Designed to respect technical constraints
while satisfying complete business logic requirements.

Architecture: Consolidated connectors by business category
- Social Media: Instagram, TikTok, YouTube, Facebook, Twitter, LinkedIn, etc.
- Music Streaming: Spotify, Apple Music, SoundCloud, Bandcamp, etc.
- Creator Economy: OnlyFans, Patreon, Ko-fi, Gumroad, Substack, etc.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Main platform management
from .platform_manager import PlatformManager, DistributionRequest, DistributionResult, ContentType

# Consolidated connector managers
from .social_media_connectors import (
    SocialMediaConnectors,
    SocialContent,
    SocialPlatform,
    InstagramConnector,
    TikTokConnector,
    YouTubeConnector,
    TwitterConnector,
    LinkedInConnector
)

from .music_streaming_connectors import (
    MusicStreamingConnectors,
    MusicContent,
    MusicPlatform,
    SpotifyConnector,
    SoundCloudConnector,
    AppleMusicConnector,
    BandcampConnector
)

from .creator_economy_connectors import (
    CreatorEconomyConnectors,
    CreatorContent,
    CreatorPlatform,
    PatreonConnector,
    OnlyFansConnector,
    KoFiConnector,
    GumroadConnector,
    SubstackConnector
)

# Legacy individual connectors (backwards compatibility)
from .discord_connector import DiscordConnector
from .reddit_connector import RedditConnector
from .telegram_connector import TelegramConnector
from .whatsapp_business_connector import WhatsAppBusinessConnector
from .dailymotion_connector import DailymotionConnector
from .medium_connector import MediumConnector
from .substack_connector import SubstackConnector
from .vimeo_connector import VimeoConnector
from .apple_music_connector import AppleMusicConnector
from .bandcamp_connector import BandcampConnector
from .clubhouse_connector import ClubhouseConnector
from .onlyfans_connector import OnlyFansConnector
from .patreon_connector import PatreonConnector
from .twitch_connector import TwitchConnector

# Platform management utilities
from .platform_connectors import PlatformConnectors
from .platform_connectors_emerging import EmergingPlatformConnectors

__all__ = [
    # Main Platform Management
    'PlatformManager',
    'DistributionRequest',
    'DistributionResult',
    'ContentType',
    
    # Consolidated Managers
    'SocialMediaConnectors',
    'MusicStreamingConnectors', 
    'CreatorEconomyConnectors',
    
    # Content Types
    'SocialContent',
    'MusicContent',
    'CreatorContent',
    
    # Platform Enums
    'SocialPlatform',
    'MusicPlatform',
    'CreatorPlatform',
    
    # Individual Connectors (New Consolidated)
    'InstagramConnector',
    'TikTokConnector',
    'YouTubeConnector',
    'TwitterConnector',
    'LinkedInConnector',
    'SpotifyConnector',
    'SoundCloudConnector',
    'AppleMusicConnector',
    'BandcampConnector',
    'PatreonConnector',
    'OnlyFansConnector',
    'KoFiConnector',
    'GumroadConnector',
    'SubstackConnector',
    
    # Legacy Connectors (Backwards Compatibility)
    'DiscordConnector',
    'RedditConnector',
    'TelegramConnector',
    'WhatsAppBusinessConnector',
    'DailymotionConnector',
    'MediumConnector',
    'VimeoConnector',
    'ClubhouseConnector',
    'TwitchConnector',
    
    # Platform Utilities
    'PlatformConnectors',
    'EmergingPlatformConnectors'
]