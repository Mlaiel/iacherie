"""Apple Music Agent - MusicKit Integration System
==============================================

Professional Apple Music integration providing comprehensive MusicKit API access,
music catalog management, and intelligent music discovery capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""from .core.musickit_engine import MusicKitEngine, AppleMusicTrack, AppleMusicPlaylist
from .adapters.musickit_adapter import MusicKitAdapter
from .utils.apple_auth import AppleAuthManager

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

__all__ = [
    'MusicKitEngine',
    'AppleMusicTrack', 
    'AppleMusicPlaylist',
    'MusicKitAdapter',
    'AppleAuthManager'
]

def create_apple_music_agent(config=None):
    """Factory function to create configured Apple Music agent"""    return MusicKitEngine(config)

def get_module_info():
    """Get module information and capabilities"""    return {
        "name": "Apple Music Agent",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "capabilities": [
            "MusicKit API Integration",
            "Apple Music Catalog Access",
            "Playlist Management",
            "Music Discovery",
            "User Library Integration",
            "Streaming Analytics",
            "Content Metadata Extraction"
        ],
        "supported_formats": [
            "Apple Music Catalog IDs",
            "MusicKit JSON",
            "Apple Music URLs",
            "Playlist Data"
        ],
        "integrations": [
            "Apple MusicKit JS",
            "Apple Music API",
            "Apple Developer Services",
            "iTunes Store API"
        ]
    }