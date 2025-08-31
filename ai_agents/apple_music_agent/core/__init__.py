"""
Core module initialization for Apple Music Agent
"""
from .musickit_engine import MusicKitEngine, AppleMusicTrack, AppleMusicPlaylist, AppleMusicArtist

__all__ = [
    'MusicKitEngine',
    'AppleMusicTrack',
    'AppleMusicPlaylist', 
    'AppleMusicArtist'
]