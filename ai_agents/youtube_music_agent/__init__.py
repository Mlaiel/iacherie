"""YouTube Music Agent - Copyright Monitoring System
================================================

Professional YouTube Music integration providing comprehensive API access,
copyright monitoring, and content protection capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""
from .core.youtube_music_engine import YouTubeMusicEngine, YouTubeTrack, YouTubePlaylist
from .core.copyright_monitor import CopyrightMonitor
from .utils.youtube_auth import YouTubeAuthManager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

__all__ = [
    'YouTubeMusicEngine',
    'YouTubeTrack',
    'YouTubePlaylist',
    'CopyrightMonitor', 
    'YouTubeAuthManager'
]

def create_youtube_music_agent(config=None):
    """Factory function to create configured YouTube Music agent"""    return YouTubeMusicEngine(config)

def get_module_info():
    """Get module information and capabilities"""    return {
        "name": "YouTube Music Agent",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "capabilities": [
            "YouTube Music API Integration",
            "Copyright Monitoring & Detection",
            "Content ID Management",
            "Music Discovery & Search",
            "Playlist Management", 
            "Analytics & Insights",
            "DMCA Protection",
            "Revenue Tracking"
        ],
        "supported_formats": [
            "YouTube Video IDs",
            "YouTube Music URLs",
            "Playlist Data",
            "Channel Data",
            "Audio Files for Upload"
        ],
        "integrations": [
            "YouTube Data API v3",
            "YouTube Analytics API",
            "Content ID API",
            "YouTube Music API"
        ]
    }