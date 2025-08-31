"""
SoundCloud Agent - API + Intelligent Scraping System
===================================================

Professional SoundCloud integration providing comprehensive API access,
intelligent content scraping, and advanced audio discovery capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""

from .core.soundcloud_engine import SoundCloudEngine, SoundCloudTrack, SoundCloudPlaylist
from .core.intelligent_scraper import IntelligentScraper
from .utils.soundcloud_auth import SoundCloudAuthManager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

__all__ = [
    'SoundCloudEngine',
    'SoundCloudTrack',
    'SoundCloudPlaylist', 
    'IntelligentScraper',
    'SoundCloudAuthManager'
]

def create_soundcloud_agent(config=None):
    """Factory function to create configured SoundCloud agent"""
    return SoundCloudEngine(config)

def get_module_info():
    """Get module information and capabilities"""
    return {
        "name": "SoundCloud Agent",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "capabilities": [
            "SoundCloud API Integration",
            "Intelligent Content Scraping",
            "Track Discovery & Analysis",
            "User Profile Management",
            "Playlist Management",
            "Comment & Engagement Tracking",
            "Upload & Distribution",
            "Real-time Monitoring"
        ],
        "supported_formats": [
            "SoundCloud URLs",
            "Track IDs",
            "User Profiles",
            "Playlist Data",
            "Audio Files (MP3, WAV, FLAC)"
        ],
        "integrations": [
            "SoundCloud API v2",
            "SoundCloud Web Scraping",
            "Audio Processing Libraries",
            "Content Analysis Tools"
        ]
    }