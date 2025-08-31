"""
Advanced Music Platform Copyright Monitoring System
==================================================

Comprehensive monitoring and copyright protection for music platforms including:
- Spotify Web API + track monitoring
- Apple Music MusicKit + catalog search  
- SoundCloud API + track discovery
- Bandcamp web scraping + release tracking
- Deezer API + playlist monitoring
- Amazon Music API + content tracking
- YouTube Music specialized copyright monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .spotify_monitor import SpotifyMusicMonitor
from .apple_music_monitor import AppleMusicMonitor
from .soundcloud_monitor import SoundCloudMonitor
from .bandcamp_monitor import BandcampMonitor
from .deezer_monitor import DeezerMonitor
from .amazon_music_monitor import AmazonMusicMonitor
from .youtube_music_monitor import YouTubeMusicMonitor
from .music_platform_coordinator import MusicPlatformCoordinator

__all__ = [
    'SpotifyMusicMonitor',
    'AppleMusicMonitor', 
    'SoundCloudMonitor',
    'BandcampMonitor',
    'DeezerMonitor',
    'AmazonMusicMonitor',
    'YouTubeMusicMonitor',
    'MusicPlatformCoordinator'
]