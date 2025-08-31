"""
Core module initialization for SoundCloud Agent
"""
from .soundcloud_engine import SoundCloudEngine, SoundCloudTrack, SoundCloudPlaylist, SoundCloudUser
from .intelligent_scraper import IntelligentScraper, ScrapingResult

__all__ = [
    'SoundCloudEngine',
    'SoundCloudTrack',
    'SoundCloudPlaylist',
    'SoundCloudUser',
    'IntelligentScraper',
    'ScrapingResult'
]