"""
Platform Crawlers Module
========================

Enterprise-grade web crawlers for comprehensive social media and content platform monitoring.
Implements industrial surveillance, AI-powered content discovery, violation detection, and 
real-time protection monitoring across 30+ major platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

# Social Media Platforms
from .youtube_crawler import YouTubeCrawler
from .instagram_crawler import InstagramCrawler
from .tiktok_crawler import TikTokCrawler
from .twitter_crawler import TwitterCrawler
from .facebook_crawler import FacebookCrawler
from .linkedin_crawler import LinkedInCrawler
from .pinterest_crawler import PinterestCrawler
from .snapchat_crawler import SnapchatCrawler
from .discord_crawler import DiscordCrawler
from .telegram_crawler import TelegramCrawler
from .whatsapp_crawler import WhatsAppCrawler
from .threads_crawler import ThreadsCrawler
from .mastodon_crawler import MastodonCrawler
from .reddit_crawler import RedditCrawler
from .bereal_crawler import BeRealCrawler

# Streaming & Gaming Platforms
from .twitch_crawler import TwitchCrawler
from .kick_crawler import KickCrawler
from .clubhouse_crawler import ClubhouseCrawler

# Music Platforms
from .spotify_crawler import SpotifyCrawler
from .soundcloud_crawler import SoundCloudCrawler
from .apple_music_crawler import AppleMusicCrawler
from .amazon_music_crawler import AmazonMusicCrawler
from .deezer_crawler import DeezerCrawler
from .youtube_music_crawler import YouTubeMusicCrawler
from .bandcamp_crawler import BandcampCrawler
from .mixcloud_crawler import MixcloudCrawler
from .twine_crawler import TwineCrawler

# Video Platforms
from .vimeo_crawler import VimeoCrawler
from .dailymotion_crawler import DailymotionCrawler
from .rumble_crawler import RumbleCrawler

# Publishing & Content Platforms
from .substack_crawler import SubstackCrawler
from .medium_crawler import MediumCrawler
from .patreon_crawler import PatreonCrawler
from .onlyfans_crawler import OnlyFansCrawler

# Generic & Specialized
from .generic_crawler import GenericWebCrawler

__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# All available platform crawlers
__all__ = [
    # Social Media
    "YouTubeCrawler",
    "InstagramCrawler", 
    "TikTokCrawler",
    "TwitterCrawler",
    "FacebookCrawler",
    "LinkedInCrawler",
    "PinterestCrawler",
    "SnapchatCrawler",
    "DiscordCrawler",
    "TelegramCrawler",
    "WhatsAppCrawler",
    "ThreadsCrawler",
    "MastodonCrawler", 
    "RedditCrawler",
    "BeRealCrawler",
    
    # Streaming & Gaming
    "TwitchCrawler",
    "KickCrawler",
    "ClubhouseCrawler",
    
    # Music Platforms
    "SpotifyCrawler",
    "SoundCloudCrawler",
    "AppleMusicCrawler",
    "AmazonMusicCrawler",
    "DeezerCrawler",
    "YouTubeMusicCrawler",
    "BandcampCrawler",
    "MixcloudCrawler",
    "TwineCrawler",
    
    # Video Platforms
    "VimeoCrawler",
    "DailymotionCrawler",
    "RumbleCrawler",
    
    # Publishing & Content
    "SubstackCrawler",
    "MediumCrawler",
    "PatreonCrawler",
    "OnlyFansCrawler",
    
    # Generic
    "GenericWebCrawler",
]

# Platform categorization for easy access
SOCIAL_MEDIA_CRAWLERS = [
    "YouTubeCrawler", "InstagramCrawler", "TikTokCrawler", "TwitterCrawler",
    "FacebookCrawler", "LinkedInCrawler", "PinterestCrawler", "SnapchatCrawler",
    "DiscordCrawler", "TelegramCrawler", "WhatsAppCrawler", "ThreadsCrawler",
    "MastodonCrawler", "RedditCrawler", "BeRealCrawler"
]

STREAMING_CRAWLERS = [
    "TwitchCrawler", "KickCrawler", "ClubhouseCrawler"
]

MUSIC_CRAWLERS = [
    "SpotifyCrawler", "SoundCloudCrawler", "AppleMusicCrawler", 
    "AmazonMusicCrawler", "DeezerCrawler", "YouTubeMusicCrawler", 
    "BandcampCrawler", "MixcloudCrawler", "TwineCrawler"
]

VIDEO_CRAWLERS = [
    "YouTubeCrawler", "VimeoCrawler", "DailymotionCrawler", "RumbleCrawler"
]

CONTENT_CRAWLERS = [
    "SubstackCrawler", "MediumCrawler", "PatreonCrawler", "OnlyFansCrawler"
]

# Platform configurations and metadata
PLATFORM_METADATA = {
    "youtube": {
        "name": "YouTube",
        "category": "video",
        "api_required": True,
        "rate_limit": "10000/day",
        "content_types": ["video", "audio", "channel", "playlist"]
    },
    "instagram": {
        "name": "Instagram", 
        "category": "social",
        "api_required": True,
        "rate_limit": "200/hour",
        "content_types": ["image", "video", "story", "reel"]
    },
    "tiktok": {
        "name": "TikTok",
        "category": "social",
        "api_required": False,
        "rate_limit": "100/hour",
        "content_types": ["video", "audio", "effect"]
    },
    "twitter": {
        "name": "Twitter/X",
        "category": "social",
        "api_required": True,
        "rate_limit": "300/15min",
        "content_types": ["tweet", "media", "thread"]
    },
    "spotify": {
        "name": "Spotify",
        "category": "music",
        "api_required": True,
        "rate_limit": "100/second",
        "content_types": ["track", "album", "artist", "playlist"]
    },
    # Add more platform metadata as needed
}

def get_crawler_by_platform(platform_name: str):
    """
    Get crawler class by platform name.
    
    Args:
        platform_name: Name of the platform (e.g., 'youtube', 'instagram')
        
    Returns:
        Crawler class for the specified platform
        
    Raises:
        ValueError: If platform is not supported
    """
    crawler_mapping = {
        'youtube': YouTubeCrawler,
        'instagram': InstagramCrawler,
        'tiktok': TikTokCrawler,
        'twitter': TwitterCrawler,
        'facebook': FacebookCrawler,
        'linkedin': LinkedInCrawler,
        'pinterest': PinterestCrawler,
        'snapchat': SnapchatCrawler,
        'discord': DiscordCrawler,
        'telegram': TelegramCrawler,
        'whatsapp': WhatsAppCrawler,
        'threads': ThreadsCrawler,
        'mastodon': MastodonCrawler,
        'reddit': RedditCrawler,
        'bereal': BeRealCrawler,
        'twitch': TwitchCrawler,
        'kick': KickCrawler,
        'clubhouse': ClubhouseCrawler,
        'spotify': SpotifyCrawler,
        'soundcloud': SoundCloudCrawler,
        'apple_music': AppleMusicCrawler,
        'amazon_music': AmazonMusicCrawler,
        'deezer': DeezerCrawler,
        'youtube_music': YouTubeMusicCrawler,
        'bandcamp': BandcampCrawler,
        'mixcloud': MixcloudCrawler,
        'twine': TwineCrawler,
        'vimeo': VimeoCrawler,
        'dailymotion': DailymotionCrawler,
        'rumble': RumbleCrawler,
        'substack': SubstackCrawler,
        'medium': MediumCrawler,
        'patreon': PatreonCrawler,
        'onlyfans': OnlyFansCrawler,
        'generic': GenericWebCrawler,
    }
    
    if platform_name.lower() not in crawler_mapping:
        raise ValueError(f"Platform '{platform_name}' is not supported. "
                        f"Available platforms: {list(crawler_mapping.keys())}")
    
    return crawler_mapping[platform_name.lower()]

def get_supported_platforms():
    """Get list of all supported platform names."""
    return list(PLATFORM_METADATA.keys())

def get_platforms_by_category(category: str):
    """Get platforms filtered by category."""
    return [
        platform for platform, metadata in PLATFORM_METADATA.items()
        if metadata.get("category") == category
    ]

# Platform capabilities matrix
PLATFORM_CAPABILITIES = {
    "youtube": {
        "content_types": ["video", "audio", "thumbnails", "descriptions"],
        "search_features": ["keywords", "channels", "playlists", "trends"],
        "analytics": ["views", "likes", "comments", "engagement"],
        "api_features": ["real_time", "bulk_search", "channel_monitoring"],
        "rate_limits": {"api": 10000, "scraping": 100}
    },
    "instagram": {
        "content_types": ["images", "videos", "stories", "reels"],
        "search_features": ["hashtags", "users", "locations", "trends"],
        "analytics": ["likes", "comments", "saves", "shares"],
        "api_features": ["business_api", "creator_insights"],
        "rate_limits": {"api": 5000, "scraping": 60}
    },
    "tiktok": {
        "content_types": ["videos", "audio", "effects"],
        "search_features": ["hashtags", "sounds", "users", "trends"],
        "analytics": ["views", "likes", "shares", "comments"],
        "api_features": ["research_api", "creator_tools"],
        "rate_limits": {"api": 1000, "scraping": 30}
    },
    "twitter": {
        "content_types": ["tweets", "images", "videos", "spaces"],
        "search_features": ["keywords", "hashtags", "users", "trends"],
        "analytics": ["retweets", "likes", "replies", "impressions"],
        "api_features": ["streaming", "search", "user_timeline"],
        "rate_limits": {"api": 15000, "scraping": 180}
    },
    "facebook": {
        "content_types": ["posts", "images", "videos", "pages"],
        "search_features": ["pages", "groups", "posts", "events"],
        "analytics": ["reactions", "shares", "comments", "reach"],
        "api_features": ["graph_api", "marketing_api"],
        "rate_limits": {"api": 200, "scraping": 50}
    },
    "spotify": {
        "content_types": ["tracks", "albums", "playlists", "podcasts"],
        "search_features": ["artists", "tracks", "albums", "genres"],
        "analytics": ["streams", "saves", "followers", "monthly_listeners"],
        "api_features": ["web_api", "web_playback_sdk"],
        "rate_limits": {"api": 100, "scraping": 10}
    },
    "substack": {
        "content_types": ["newsletters", "articles", "podcasts", "posts"],
        "search_features": ["publications", "authors", "content", "topics"],
        "analytics": ["subscribers", "views", "likes", "comments"],
        "api_features": ["rss_feeds", "publication_discovery"],
        "rate_limits": {"api": 30, "scraping": 30}
    },
    "linkedin": {
        "content_types": ["posts", "articles", "videos", "profiles"],
        "search_features": ["companies", "people", "posts", "jobs"],
        "analytics": ["views", "likes", "comments", "shares"],
        "api_features": ["marketing_api", "company_api"],
        "rate_limits": {"api": 500, "scraping": 30}
    },
    "twitch": {
        "content_types": ["streams", "clips", "videos", "chat"],
        "search_features": ["streamers", "games", "clips", "categories"],
        "analytics": ["viewers", "followers", "subscriptions", "bits"],
        "api_features": ["helix_api", "webhooks"],
        "rate_limits": {"api": 800, "scraping": 40}
    },
    "soundcloud": {
        "content_types": ["tracks", "playlists", "reposts", "comments"],
        "search_features": ["tracks", "users", "playlists", "tags"],
        "analytics": ["plays", "likes", "reposts", "comments"],
        "api_features": ["api_v2", "connect_api"],
        "rate_limits": {"api": 15000, "scraping": 60}
    }
}

def get_platform_crawler(platform: str):
    """Get crawler instance for specific platform."""
    crawler_map = {
        "youtube": YouTubeCrawler,
        "instagram": InstagramCrawler,
        "tiktok": TikTokCrawler,
        "twitter": TwitterCrawler,
        "facebook": FacebookCrawler,
        "spotify": SpotifyCrawler,
        "substack": SubstackCrawler,
        "linkedin": LinkedInCrawler,
        "twitch": TwitchCrawler,
        "soundcloud": SoundCloudCrawler,
        "generic": GenericWebCrawler
    }
    
    if platform not in crawler_map:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return crawler_map[platform]()

def get_supported_platforms():
    """Get list of supported platforms."""
    return list(PLATFORM_CAPABILITIES.keys())

def get_platform_capabilities(platform: str):
    """Get capabilities for specific platform."""
    return PLATFORM_CAPABILITIES.get(platform, {})
