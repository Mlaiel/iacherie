"""
Spotify Crawling Engine
======================

Advanced Spotify crawler for music discovery, artist analytics, and playlist monitoring.
Handles track metadata extraction, playlist analysis, and music trend tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time
import random
import base64
from urllib.parse import urljoin, urlparse, quote

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import SpotifyTrack, SpotifyArtist, SpotifyPlaylist
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SpotifyTrackData:
    """Spotify track data structure"""
    track_id: str
    name: str
    artist_names: List[str]
    artist_ids: List[str]
    album_name: str
    album_id: str
    duration_ms: int
    popularity: int
    explicit: bool
    preview_url: Optional[str]
    external_urls: Dict[str, str]
    spotify_url: str
    isrc: Optional[str]
    release_date: str
    release_date_precision: str
    track_number: int
    disc_number: int
    available_markets: List[str]
    audio_features: Optional[Dict[str, float]]
    genres: List[str]
    acousticness: Optional[float] = None
    danceability: Optional[float] = None
    energy: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    speechiness: Optional[float] = None
    tempo: Optional[float] = None
    valence: Optional[float] = None
    key: Optional[int] = None
    mode: Optional[int] = None


@dataclass
class SpotifyArtistData:
    """Spotify artist data structure"""
    artist_id: str
    name: str
    genres: List[str]
    popularity: int
    followers_count: int
    external_urls: Dict[str, str]
    spotify_url: str
    images: List[Dict[str, Any]]
    related_artists: List[str]
    top_tracks: List[str]
    albums: List[str]
    monthly_listeners: Optional[int] = None
    verified: bool = False
    bio: Optional[str] = None
    social_links: Dict[str, str] = None
    concert_dates: List[Dict] = None


@dataclass
class SpotifyPlaylistData:
    """Spotify playlist data structure"""
    playlist_id: str
    name: str
    description: str
    owner_id: str
    owner_name: str
    public: bool
    collaborative: bool
    followers_count: int
    tracks_count: int
    tracks: List[SpotifyTrackData]
    images: List[Dict[str, Any]]
    external_urls: Dict[str, str]
    spotify_url: str
    snapshot_id: str
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    genre_distribution: Dict[str, int] = None
    popularity_score: float = 0.0
    diversity_score: float = 0.0


class SpotifyCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Spotify crawler engine with comprehensive music data extraction.
    
    Features:
    - Spotify Web API integration
    - Track and artist analytics extraction
    - Playlist analysis and monitoring
    - Audio features analysis
    - Music trend detection
    - Genre classification
    - Rate limiting and caching
    """
    
    def __init__(self, api_credentials: Dict, config: Optional[Dict] = None):
        """Initialize Spotify crawler engine"""
        super().__init__(config)
        self.api_credentials = api_credentials
        self.client = None
        self.session = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=180,  # Spotify API limits
            requests_per_hour=6000,
            requests_per_day=100000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(hours=2),
            max_cache_size=10000
        )
        self._setup_spotify_client()
        self._setup_session()
        self._setup_selenium_driver()
    
    def _setup_spotify_client(self) -> None:
        """Setup Spotify API client"""
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.api_credentials.get('client_id'),
                client_secret=self.api_credentials.get('client_secret')
            )
            
            self.client = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager,
                requests_timeout=10,
                retries=3
            )
            
            # Test authentication
            test_search = self.client.search('test', limit=1, type='track')
            if test_search:
                logger.info("Spotify API client authenticated successfully")
            else:
                raise AuthenticationError("Spotify API authentication failed")
                
        except Exception as e:
            logger.error(f"Failed to setup Spotify client: {e}")
            raise AuthenticationError(f"Spotify API setup failed: {e}")
    
    def _setup_session(self) -> None:
        """Setup HTTP session for web scraping"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://open.spotify.com/',
        })
        logger.info("Spotify HTTP session initialized")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver for web scraping"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized for Spotify")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    async def get_artist_data(self, artist_id: str) -> Optional[SpotifyArtistData]:
        """
        Get comprehensive artist data
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            Artist data or None if not found
        """
        await self.rate_limiter.wait()
        
        cache_key = f"artist_{artist_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Get artist info
            artist = self.client.artist(artist_id)
            if not artist:
                raise ContentNotFoundError(f"Artist {artist_id} not found")
            
            # Get related artists
            related_artists = self.client.artist_related_artists(artist_id)
            related_artist_ids = [a['id'] for a in related_artists['artists'][:10]]
            
            # Get top tracks
            top_tracks = self.client.artist_top_tracks(artist_id)
            top_track_ids = [t['id'] for t in top_tracks['tracks'][:10]]
            
            # Get albums
            albums = self.client.artist_albums(artist_id, album_type='album', limit=20)
            album_ids = [a['id'] for a in albums['items']]
            
            # Get additional data from web scraping if driver available
            monthly_listeners = None
            verified = False
            bio = None
            social_links = {}
            
            if self.driver:
                additional_data = await self._scrape_artist_web_data(artist_id)
                monthly_listeners = additional_data.get('monthly_listeners')
                verified = additional_data.get('verified', False)
                bio = additional_data.get('bio')
                social_links = additional_data.get('social_links', {})
            
            artist_data = SpotifyArtistData(
                artist_id=artist['id'],
                name=artist['name'],
                genres=artist['genres'],
                popularity=artist['popularity'],
                followers_count=artist['followers']['total'],
                external_urls=artist['external_urls'],
                spotify_url=artist['external_urls']['spotify'],
                images=artist['images'],
                related_artists=related_artist_ids,
                top_tracks=top_track_ids,
                albums=album_ids,
                monthly_listeners=monthly_listeners,
                verified=verified,
                bio=bio,
                social_links=social_links
            )
            
            await self.cache_manager.set(cache_key, artist_data)
            return artist_data
            
        except spotipy.SpotifyException as e:
            if e.http_status == 404:
                raise ContentNotFoundError(f"Artist {artist_id} not found")
            elif e.http_status == 429:
                raise RateLimitError("Spotify API rate limit exceeded")
            else:
                raise CrawlerError(f"Spotify API error: {e}")
        except Exception as e:
            logger.error(f"Error getting artist data for {artist_id}: {e}")
            raise CrawlerError(f"Failed to get artist data: {e}")
    
    async def get_track_data(self, track_id: str, include_audio_features: bool = True) -> Optional[SpotifyTrackData]:
        """
        Get comprehensive track data
        
        Args:
            track_id: Spotify track ID
            include_audio_features: Whether to include audio features
            
        Returns:
            Track data or None if not found
        """
        await self.rate_limiter.wait()
        
        cache_key = f"track_{track_id}_{include_audio_features}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Get track info
            track = self.client.track(track_id)
            if not track:
                raise ContentNotFoundError(f"Track {track_id} not found")
            
            # Get audio features if requested
            audio_features = None
            if include_audio_features:
                try:
                    features = self.client.audio_features(track_id)[0]
                    audio_features = features
                except:
                    logger.warning(f"Could not get audio features for track {track_id}")
            
            # Extract artist data
            artist_names = [artist['name'] for artist in track['artists']]
            artist_ids = [artist['id'] for artist in track['artists']]
            
            # Get genres from artist data
            genres = []
            try:
                for artist_id in artist_ids[:3]:  # Limit to first 3 artists
                    artist_data = self.client.artist(artist_id)
                    genres.extend(artist_data['genres'])
                genres = list(set(genres))  # Remove duplicates
            except:
                pass
            
            track_data = SpotifyTrackData(
                track_id=track['id'],
                name=track['name'],
                artist_names=artist_names,
                artist_ids=artist_ids,
                album_name=track['album']['name'],
                album_id=track['album']['id'],
                duration_ms=track['duration_ms'],
                popularity=track['popularity'],
                explicit=track['explicit'],
                preview_url=track['preview_url'],
                external_urls=track['external_urls'],
                spotify_url=track['external_urls']['spotify'],
                isrc=track['external_ids'].get('isrc'),
                release_date=track['album']['release_date'],
                release_date_precision=track['album']['release_date_precision'],
                track_number=track['track_number'],
                disc_number=track['disc_number'],
                available_markets=track['available_markets'],
                audio_features=audio_features,
                genres=genres
            )
            
            # Add audio features to track data if available
            if audio_features:
                track_data.acousticness = audio_features.get('acousticness')
                track_data.danceability = audio_features.get('danceability')
                track_data.energy = audio_features.get('energy')
                track_data.instrumentalness = audio_features.get('instrumentalness')
                track_data.liveness = audio_features.get('liveness')
                track_data.loudness = audio_features.get('loudness')
                track_data.speechiness = audio_features.get('speechiness')
                track_data.tempo = audio_features.get('tempo')
                track_data.valence = audio_features.get('valence')
                track_data.key = audio_features.get('key')
                track_data.mode = audio_features.get('mode')
            
            await self.cache_manager.set(cache_key, track_data)
            return track_data
            
        except spotipy.SpotifyException as e:
            if e.http_status == 404:
                raise ContentNotFoundError(f"Track {track_id} not found")
            elif e.http_status == 429:
                raise RateLimitError("Spotify API rate limit exceeded")
            else:
                raise CrawlerError(f"Spotify API error: {e}")
        except Exception as e:
            logger.error(f"Error getting track data for {track_id}: {e}")
            raise CrawlerError(f"Failed to get track data: {e}")
    
    async def get_playlist_data(self, playlist_id: str, include_tracks: bool = True) -> Optional[SpotifyPlaylistData]:
        """
        Get comprehensive playlist data
        
        Args:
            playlist_id: Spotify playlist ID
            include_tracks: Whether to include track details
            
        Returns:
            Playlist data or None if not found
        """
        await self.rate_limiter.wait()
        
        cache_key = f"playlist_{playlist_id}_{include_tracks}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Get playlist info
            playlist = self.client.playlist(playlist_id)
            if not playlist:
                raise ContentNotFoundError(f"Playlist {playlist_id} not found")
            
            tracks_data = []
            genre_distribution = {}
            
            if include_tracks:
                # Get all tracks (handle pagination)
                tracks = []
                offset = 0
                limit = 100
                
                while True:
                    batch = self.client.playlist_tracks(
                        playlist_id, 
                        offset=offset, 
                        limit=limit,
                        fields='items(track(id,name,artists,album,duration_ms,popularity,explicit,external_urls))'
                    )
                    
                    tracks.extend(batch['items'])
                    
                    if len(batch['items']) < limit:
                        break
                    
                    offset += limit
                    await asyncio.sleep(0.1)  # Small delay between requests
                
                # Process tracks
                for item in tracks:
                    if item['track'] and item['track']['id']:
                        try:
                            track_data = await self.get_track_data(item['track']['id'], include_audio_features=False)
                            if track_data:
                                tracks_data.append(track_data)
                                
                                # Count genres
                                for genre in track_data.genres:
                                    genre_distribution[genre] = genre_distribution.get(genre, 0) + 1
                                    
                        except Exception as e:
                            logger.warning(f"Error processing track {item['track']['id']}: {e}")
                            continue
            
            # Calculate playlist metrics
            popularity_score = 0.0
            diversity_score = 0.0
            
            if tracks_data:
                # Average popularity
                popularity_score = sum(track.popularity for track in tracks_data) / len(tracks_data)
                
                # Genre diversity (Shannon diversity index)
                if genre_distribution:
                    total_genres = sum(genre_distribution.values())
                    diversity_score = -sum(
                        (count / total_genres) * math.log(count / total_genres)
                        for count in genre_distribution.values()
                        if count > 0
                    )
            
            playlist_data = SpotifyPlaylistData(
                playlist_id=playlist['id'],
                name=playlist['name'],
                description=playlist['description'] or "",
                owner_id=playlist['owner']['id'],
                owner_name=playlist['owner']['display_name'] or playlist['owner']['id'],
                public=playlist['public'],
                collaborative=playlist['collaborative'],
                followers_count=playlist['followers']['total'],
                tracks_count=playlist['tracks']['total'],
                tracks=tracks_data,
                images=playlist['images'],
                external_urls=playlist['external_urls'],
                spotify_url=playlist['external_urls']['spotify'],
                snapshot_id=playlist['snapshot_id'],
                genre_distribution=genre_distribution,
                popularity_score=popularity_score,
                diversity_score=diversity_score
            )
            
            await self.cache_manager.set(cache_key, playlist_data)
            return playlist_data
            
        except spotipy.SpotifyException as e:
            if e.http_status == 404:
                raise ContentNotFoundError(f"Playlist {playlist_id} not found")
            elif e.http_status == 429:
                raise RateLimitError("Spotify API rate limit exceeded")
            else:
                raise CrawlerError(f"Spotify API error: {e}")
        except Exception as e:
            logger.error(f"Error getting playlist data for {playlist_id}: {e}")
            raise CrawlerError(f"Failed to get playlist data: {e}")
    
    async def search_tracks(
        self, 
        query: str, 
        limit: int = 50,
        market: str = 'US'
    ) -> List[SpotifyTrackData]:
        """
        Search for tracks
        
        Args:
            query: Search query
            limit: Maximum number of results
            market: Market/country code
            
        Returns:
            List of matching tracks
        """
        await self.rate_limiter.wait()
        
        try:
            results = self.client.search(
                q=query, 
                limit=min(limit, 50), 
                type='track', 
                market=market
            )
            
            tracks_data = []
            for track in results['tracks']['items']:
                track_data = await self.get_track_data(track['id'], include_audio_features=False)
                if track_data:
                    tracks_data.append(track_data)
            
            return tracks_data
            
        except Exception as e:
            logger.error(f"Error searching tracks with query '{query}': {e}")
            raise CrawlerError(f"Track search failed: {e}")
    
    async def search_artists(
        self, 
        query: str, 
        limit: int = 50,
        market: str = 'US'
    ) -> List[SpotifyArtistData]:
        """
        Search for artists
        
        Args:
            query: Search query
            limit: Maximum number of results
            market: Market/country code
            
        Returns:
            List of matching artists
        """
        await self.rate_limiter.wait()
        
        try:
            results = self.client.search(
                q=query, 
                limit=min(limit, 50), 
                type='artist', 
                market=market
            )
            
            artists_data = []
            for artist in results['artists']['items']:
                artist_data = await self.get_artist_data(artist['id'])
                if artist_data:
                    artists_data.append(artist_data)
            
            return artists_data
            
        except Exception as e:
            logger.error(f"Error searching artists with query '{query}': {e}")
            raise CrawlerError(f"Artist search failed: {e}")
    
    async def get_featured_playlists(self, country: str = 'US', limit: int = 50) -> List[SpotifyPlaylistData]:
        """
        Get featured playlists for a country
        
        Args:
            country: Country code
            limit: Maximum number of playlists
            
        Returns:
            List of featured playlists
        """
        await self.rate_limiter.wait()
        
        try:
            featured = self.client.featured_playlists(country=country, limit=min(limit, 50))
            
            playlists_data = []
            for playlist in featured['playlists']['items']:
                playlist_data = await self.get_playlist_data(playlist['id'], include_tracks=False)
                if playlist_data:
                    playlists_data.append(playlist_data)
            
            return playlists_data
            
        except Exception as e:
            logger.error(f"Error getting featured playlists for {country}: {e}")
            return []
    
    async def get_new_releases(self, country: str = 'US', limit: int = 50) -> List[SpotifyTrackData]:
        """
        Get new music releases
        
        Args:
            country: Country code
            limit: Maximum number of releases
            
        Returns:
            List of new tracks from recent albums
        """
        await self.rate_limiter.wait()
        
        try:
            new_releases = self.client.new_releases(country=country, limit=min(limit, 50))
            
            tracks_data = []
            for album in new_releases['albums']['items']:
                # Get tracks from each album
                try:
                    album_tracks = self.client.album_tracks(album['id'])
                    for track in album_tracks['items']:
                        track_data = await self.get_track_data(track['id'], include_audio_features=False)
                        if track_data:
                            tracks_data.append(track_data)
                        
                        if len(tracks_data) >= limit:
                            break
                    
                    if len(tracks_data) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error processing album {album['id']}: {e}")
                    continue
            
            return tracks_data
            
        except Exception as e:
            logger.error(f"Error getting new releases for {country}: {e}")
            return []
    
    async def analyze_audio_features(self, track_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze audio features for multiple tracks
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            Audio features analysis
        """
        await self.rate_limiter.wait()
        
        try:
            # Get audio features in batches of 100 (API limit)
            all_features = []
            for i in range(0, len(track_ids), 100):
                batch_ids = track_ids[i:i+100]
                features_batch = self.client.audio_features(batch_ids)
                all_features.extend([f for f in features_batch if f is not None])
            
            if not all_features:
                return {}
            
            # Calculate statistics
            feature_keys = [
                'acousticness', 'danceability', 'energy', 'instrumentalness',
                'liveness', 'loudness', 'speechiness', 'tempo', 'valence'
            ]
            
            analysis = {}
            for key in feature_keys:
                values = [f[key] for f in all_features if f[key] is not None]
                if values:
                    analysis[key] = {
                        'mean': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'std': self._calculate_std(values)
                    }
            
            # Key and mode distribution
            keys = [f['key'] for f in all_features if f['key'] is not None]
            modes = [f['mode'] for f in all_features if f['mode'] is not None]
            
            analysis['key_distribution'] = {k: keys.count(k) for k in set(keys)}
            analysis['mode_distribution'] = {m: modes.count(m) for m in set(modes)}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audio features: {e}")
            return {}
    
    async def _scrape_artist_web_data(self, artist_id: str) -> Dict[str, Any]:
        """Scrape additional artist data from Spotify web interface"""
        additional_data = {}
        
        try:
            url = f"https://open.spotify.com/artist/{artist_id}"
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            await asyncio.sleep(random.uniform(2, 4))
            
            # Try to get monthly listeners
            try:
                monthly_listeners_element = self.driver.find_element(
                    By.XPATH,
                    "//span[contains(text(), 'monthly listeners')]"
                )
                monthly_listeners_text = monthly_listeners_element.text
                # Extract number from text like "1,234,567 monthly listeners"
                numbers = re.findall(r'[\d,]+', monthly_listeners_text)
                if numbers:
                    monthly_listeners = int(numbers[0].replace(',', ''))
                    additional_data['monthly_listeners'] = monthly_listeners
            except NoSuchElementException:
                pass
            
            # Check if verified
            try:
                self.driver.find_element(
                    By.XPATH,
                    "//span[@title='Verified Artist' or contains(@class, 'verified')]"
                )
                additional_data['verified'] = True
            except NoSuchElementException:
                additional_data['verified'] = False
            
            # Try to get bio/about section
            try:
                bio_element = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'about') or contains(@class, 'bio')]//span"
                )
                additional_data['bio'] = bio_element.text
            except NoSuchElementException:
                pass
            
            # Try to get social links
            try:
                social_links = {}
                social_elements = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@href, 'facebook') or contains(@href, 'twitter') or contains(@href, 'instagram')]"
                )
                for element in social_elements:
                    href = element.get_attribute('href')
                    if 'facebook' in href:
                        social_links['facebook'] = href
                    elif 'twitter' in href:
                        social_links['twitter'] = href
                    elif 'instagram' in href:
                        social_links['instagram'] = href
                
                additional_data['social_links'] = social_links
            except:
                pass
            
        except Exception as e:
            logger.warning(f"Error scraping additional artist data for {artist_id}: {e}")
        
        return additional_data
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
            await self.cache_manager.cleanup()
            logger.info("Spotify crawler engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass


# Import math for std calculation
import math

# Export main class
__all__ = ['SpotifyCrawlerEngine', 'SpotifyTrackData', 'SpotifyArtistData', 'SpotifyPlaylistData']
