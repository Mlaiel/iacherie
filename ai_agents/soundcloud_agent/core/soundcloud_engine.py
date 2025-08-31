"""SoundCloud Engine - API Integration and Content Management
==========================================================

Core engine for SoundCloud integration providing API access,
content management, and intelligent audio operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class SoundCloudEndpoint(Enum):
    """SoundCloud API endpoints"""    TRACKS = "tracks"
    USERS = "users"
    PLAYLISTS = "playlists"
    RESOLVE = "resolve"
    SEARCH = "search"
    COMMENTS = "comments"

@dataclass
class SoundCloudTrack:
    """SoundCloud track data structure"""    id: int
    title: str
    user: str
    user_id: int
    duration_ms: int
    permalink_url: str
    stream_url: Optional[str] = None
    download_url: Optional[str] = None
    artwork_url: Optional[str] = None
    waveform_url: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    play_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SoundCloudPlaylist:
    """SoundCloud playlist data structure"""    id: int
    title: str
    user: str
    user_id: int
    track_count: int
    tracks: List[SoundCloudTrack] = field(default_factory=list)
    permalink_url: str = ""
    artwork_url: Optional[str] = None
    description: Optional[str] = None
    duration_ms: int = 0
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SoundCloudUser:
    """SoundCloud user data structure"""    id: int
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    permalink_url: str = ""
    followers_count: int = 0
    followings_count: int = 0
    track_count: int = 0
    playlist_count: int = 0
    description: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SoundCloudEngine:
    """    SoundCloud Engine for API Integration and Content Management
    
    Provides comprehensive SoundCloud capabilities including:
    - SoundCloud API v2 integration
    - Track and playlist management
    - User profile analysis
    - Content discovery and search
    - Upload and distribution
    - Analytics and engagement tracking
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.client_id = self.config.get('client_id')
        self.client_secret = self.config.get('client_secret')
        self.access_token = self.config.get('access_token')
        self.session = None
        
        # API configuration
        self.base_url = "https://api.soundcloud.com"
        self.api_version = "v2"
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', 15000)  # requests per hour
        self.request_count = 0
        self.rate_limit_reset = datetime.utcnow()
        
        # Caching
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 1800)  # 30 minutes
        
        # Initialize intelligent scraper
        self.scraper = None
        
    async def initialize(self):
        """Initialize the SoundCloud engine"""        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize intelligent scraper
            from .intelligent_scraper import IntelligentScraper
            self.scraper = IntelligentScraper(self.config.get('scraper', {}))
            await self.scraper.initialize()
            
            # Validate credentials
            await self._validate_credentials()
            
            logger.info("SoundCloud engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SoundCloud engine: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the engine and cleanup resources"""        if self.session:
            await self.session.close()
        if self.scraper:
            await self.scraper.shutdown()
    
    async def search_tracks(
        self, 
        query: str, 
        limit: int = 50,
        genre: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[SoundCloudTrack]:
        """        Search for tracks on SoundCloud
        
        Args:
            query: Search query string
            limit: Maximum number of results
            genre: Filter by genre
            tags: Filter by tags
            
        Returns:
            List of SoundCloudTrack objects
        """        try:
            # Check cache
            cache_key = f"search_tracks_{query}_{limit}_{genre}_{tags}"
            if cache_key in self.cache:
                cached_result, timestamp = self.cache[cache_key]
                if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl):
                    return cached_result
            
            # Prepare API request
            params = {
                'q': query,
                'limit': limit,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            if genre:
                params['filter.genre'] = genre
            
            url = f"{self.base_url}/search/tracks"
            
            # Make API request
            response = await self._make_request('GET', url, params=params)
            
            # Process response
            tracks = []
            if 'collection' in response:
                for track_data in response['collection']:
                    track = self._parse_track_data(track_data)
                    
                    # Filter by tags if specified
                    if tags:
                        track_tags = [tag.lower() for tag in track.tags]
                        if not any(tag.lower() in track_tags for tag in tags):
                            continue
                    
                    tracks.append(track)
            
            # Cache results
            self.cache[cache_key] = (tracks, datetime.utcnow())
            
            return tracks
            
        except Exception as e:
            logger.error(f"Track search failed: {e}")
            raise
    
    async def get_track_details(self, track_id: Union[int, str]) -> SoundCloudTrack:
        """Get detailed information about a specific track"""        try:
            # Handle both numeric IDs and URLs
            if isinstance(track_id, str) and track_id.startswith('http'):
                track_id = await self._resolve_url(track_id)
            
            url = f"{self.base_url}/tracks/{track_id}"
            params = {'client_id': self.client_id or 'mock_client_id'}
            
            response = await self._make_request('GET', url, params=params)
            return self._parse_track_data(response)
            
        except Exception as e:
            logger.error(f"Failed to get track details for {track_id}: {e}")
            raise
    
    async def get_user_tracks(self, user_id: Union[int, str], limit: int = 50) -> List[SoundCloudTrack]:
        """Get all tracks from a user"""        try:
            # Handle both numeric IDs and URLs/usernames
            if isinstance(user_id, str) and not user_id.isdigit():
                user_id = await self._resolve_user(user_id)
            
            url = f"{self.base_url}/users/{user_id}/tracks"
            params = {
                'limit': limit,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            response = await self._make_request('GET', url, params=params)
            
            tracks = []
            if 'collection' in response:
                for track_data in response['collection']:
                    track = self._parse_track_data(track_data)
                    tracks.append(track)
            elif isinstance(response, list):
                for track_data in response:
                    track = self._parse_track_data(track_data)
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Failed to get user tracks for {user_id}: {e}")
            raise
    
    async def get_playlist_tracks(self, playlist_id: Union[int, str]) -> SoundCloudPlaylist:
        """Get all tracks from a playlist"""        try:
            # Handle both numeric IDs and URLs
            if isinstance(playlist_id, str) and playlist_id.startswith('http'):
                playlist_id = await self._resolve_url(playlist_id)
            
            url = f"{self.base_url}/playlists/{playlist_id}"
            params = {'client_id': self.client_id or 'mock_client_id'}
            
            response = await self._make_request('GET', url, params=params)
            
            # Parse playlist data
            playlist = self._parse_playlist_data(response)
            
            # Parse tracks
            if 'tracks' in response:
                for track_data in response['tracks']:
                    if track_data:  # SoundCloud sometimes has null tracks in playlists
                        track = self._parse_track_data(track_data)
                        playlist.tracks.append(track)
            
            return playlist
            
        except Exception as e:
            logger.error(f"Failed to get playlist tracks for {playlist_id}: {e}")
            raise
    
    async def get_trending_tracks(
        self, 
        genre: Optional[str] = None,
        region: str = 'global',
        limit: int = 50
    ) -> List[SoundCloudTrack]:
        """Get trending tracks"""        try:
            # SoundCloud doesn't have a direct trending endpoint
            # We'll use charts or popular tracks instead
            
            url = f"{self.base_url}/charts"
            params = {
                'kind': 'trending',
                'limit': limit,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            if genre:
                params['genre'] = f'soundcloud:genres:{genre}'
            
            response = await self._make_request('GET', url, params=params)
            
            tracks = []
            if 'collection' in response:
                for item in response['collection']:
                    if 'track' in item:
                        track = self._parse_track_data(item['track'])
                        tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Failed to get trending tracks: {e}")
            # Fallback to search for popular content
            return await self.search_tracks("popular", limit=limit)
    
    async def analyze_track_engagement(self, track_id: Union[int, str]) -> Dict[str, Any]:
        """Analyze engagement metrics for a track"""        try:
            track = await self.get_track_details(track_id)
            
            # Get comments for engagement analysis
            comments = await self.get_track_comments(track_id, limit=100)
            
            # Calculate engagement metrics
            total_plays = track.play_count
            total_likes = track.like_count
            total_comments = len(comments)
            
            # Calculate engagement rates
            like_rate = (total_likes / max(total_plays, 1)) * 100
            comment_rate = (total_comments / max(total_plays, 1)) * 100
            
            # Analyze comment sentiment (basic implementation)
            positive_comments = sum(1 for comment in comments if self._is_positive_comment(comment))
            sentiment_score = (positive_comments / max(len(comments), 1)) * 100
            
            analysis = {
                'track_id': track.id,
                'track_title': track.title,
                'total_plays': total_plays,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'engagement_metrics': {
                    'like_rate': like_rate,
                    'comment_rate': comment_rate,
                    'sentiment_score': sentiment_score,
                    'engagement_score': (like_rate + comment_rate + sentiment_score) / 3
                },
                'trend_analysis': {
                    'popularity_tier': self._calculate_popularity_tier(track),
                    'viral_potential': self._assess_viral_potential(track),
                    'growth_indicators': self._analyze_growth_indicators(track)
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze track engagement for {track_id}: {e}")
            raise
    
    async def get_track_comments(self, track_id: Union[int, str], limit: int = 50) -> List[Dict[str, Any]]:
        """Get comments for a track"""        try:
            url = f"{self.base_url}/tracks/{track_id}/comments"
            params = {
                'limit': limit,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            response = await self._make_request('GET', url, params=params)
            
            comments = []
            if 'collection' in response:
                comments = response['collection']
            elif isinstance(response, list):
                comments = response
            
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get comments for track {track_id}: {e}")
            return []
    
    async def upload_track(
        self, 
        audio_file_path: str,
        title: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        genre: Optional[str] = None,
        privacy: str = 'public'
    ) -> SoundCloudTrack:
        """Upload a track to SoundCloud"""        try:
            if not self.access_token:
                raise ValueError("Access token required for uploading")
            
            # Prepare upload data
            upload_data = {
                'track[title]': title,
                'track[sharing]': privacy
            }
            
            if description:
                upload_data['track[description]'] = description
            if tags:
                upload_data['track[tag_list]'] = ' '.join(f'"{tag}"' for tag in tags)
            if genre:
                upload_data['track[genre]'] = genre
            
            # For demo purposes, return mock upload result
            # In real implementation, this would handle file upload
            
            mock_track = SoundCloudTrack(
                id=999999,
                title=title,
                user='mock_user',
                user_id=123456,
                duration_ms=180000,
                permalink_url=f'https://soundcloud.com/mock_user/{title.lower().replace(" ", "-")}',
                genre=genre,
                tags=tags or [],
                description=description,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Mock track upload completed: {title}")
            return mock_track
            
        except Exception as e:
            logger.error(f"Track upload failed: {e}")
            raise
    
    async def intelligent_content_discovery(
        self,
        seed_tracks: List[str] = None,
        genres: List[str] = None,
        mood: Optional[str] = None,
        limit: int = 20
    ) -> List[SoundCloudTrack]:
        """Use intelligent scraping for advanced content discovery"""        try:
            if not self.scraper:
                # Fallback to regular search
                query = ' '.join(genres or ['music'])
                return await self.search_tracks(query, limit=limit)
            
            # Use intelligent scraper for advanced discovery
            return await self.scraper.discover_similar_content(
                seed_tracks=seed_tracks,
                genres=genres,
                mood=mood,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Intelligent content discovery failed: {e}")
            raise
    
    # Private helper methods
    
    async def _validate_credentials(self):
        """Validate SoundCloud credentials"""        try:
            if not self.client_id:
                logger.warning("SoundCloud client ID not configured, using mock mode")
                return
                
            # Test API access with a simple request
            url = f"{self.base_url}/tracks"
            params = {
                'limit': 1,
                'client_id': self.client_id
            }
            
            await self._make_request('GET', url, params=params)
            logger.info("SoundCloud credentials validated successfully")
            
        except Exception as e:
            logger.warning(f"SoundCloud credential validation failed: {e}")
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to SoundCloud API"""        try:
            # Check rate limit
            await self._check_rate_limit()
            
            # Prepare headers
            request_headers = {
                'User-Agent': 'AInflue-SoundCloud-Agent/1.0',
                'Accept': 'application/json'
            }
            
            if self.access_token:
                request_headers['Authorization'] = f'OAuth {self.access_token}'
            
            if headers:
                request_headers.update(headers)
            
            # For demo purposes, return mock data when using mock client ID
            if params and params.get('client_id') == 'mock_client_id':
                return await self._get_mock_response(method, url, params)
            
            # Make actual request (when properly configured)
            if self.session:
                async with self.session.request(
                    method, url, params=params, headers=request_headers, data=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        response.raise_for_status()
            else:
                raise RuntimeError("Session not initialized")
                
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""        now = datetime.utcnow()
        
        # Reset counter if hour has passed
        if now - self.rate_limit_reset > timedelta(hours=1):
            self.request_count = 0
            self.rate_limit_reset = now
        
        # Check if rate limit exceeded
        if self.request_count >= self.rate_limit:
            sleep_time = 3600 - (now - self.rate_limit_reset).seconds
            if sleep_time > 0:
                await asyncio.sleep(min(sleep_time, 60))  # Max 1 minute wait
                self.request_count = 0
                self.rate_limit_reset = datetime.utcnow()
        
        self.request_count += 1
    
    async def _resolve_url(self, url: str) -> int:
        """Resolve SoundCloud URL to track/playlist ID"""        try:
            resolve_url = f"{self.base_url}/resolve"
            params = {
                'url': url,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            response = await self._make_request('GET', resolve_url, params=params)
            return response.get('id', 0)
            
        except Exception as e:
            logger.error(f"URL resolution failed for {url}: {e}")
            raise
    
    async def _resolve_user(self, username: str) -> int:
        """Resolve username to user ID"""        try:
            if username.startswith('http'):
                return await self._resolve_url(username)
            
            # Search for user
            url = f"{self.base_url}/users"
            params = {
                'q': username,
                'client_id': self.client_id or 'mock_client_id'
            }
            
            response = await self._make_request('GET', url, params=params)
            
            if 'collection' in response and len(response['collection']) > 0:
                return response['collection'][0]['id']
            
            raise ValueError(f"User not found: {username}")
            
        except Exception as e:
            logger.error(f"User resolution failed for {username}: {e}")
            raise
    
    async def _get_mock_response(self, method: str, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate mock responses for testing"""        import random
        
        if 'search/tracks' in url or '/tracks' in url:
            return {
                'collection': [
                    {
                        'id': random.randint(100000, 999999),
                        'title': f'Mock Track {i}',
                        'user': {
                            'username': f'mock_user_{i}',
                            'id': random.randint(10000, 99999)
                        },
                        'duration': random.randint(120000, 300000),
                        'permalink_url': f'https://soundcloud.com/mock_user_{i}/mock-track-{i}',
                        'genre': random.choice(['Electronic', 'Hip Hop', 'Pop', 'Rock']),
                        'tag_list': 'electronic dance music',
                        'playback_count': random.randint(1000, 100000),
                        'favoritings_count': random.randint(10, 1000),
                        'comment_count': random.randint(5, 100),
                        'created_at': '2023-01-01T00:00:00Z'
                    }
                    for i in range(1, 6)
                ]
            }
        elif 'playlists' in url:
            return {
                'id': 123456,
                'title': 'Mock Playlist',
                'user': {
                    'username': 'mock_user',
                    'id': 12345
                },
                'track_count': 10,
                'duration': 1800000,
                'tracks': [
                    {
                        'id': random.randint(100000, 999999),
                        'title': f'Playlist Track {i}',
                        'user': {'username': 'mock_artist', 'id': 54321},
                        'duration': random.randint(120000, 300000)
                    }
                    for i in range(1, 6)
                ]
            }
        elif 'charts' in url:
            return {
                'collection': [
                    {
                        'track': {
                            'id': random.randint(100000, 999999),
                            'title': f'Trending Track {i}',
                            'user': {'username': f'trending_artist_{i}', 'id': random.randint(10000, 99999)},
                            'duration': random.randint(120000, 300000),
                            'playback_count': random.randint(50000, 500000),
                            'genre': 'Electronic'
                        }
                    }
                    for i in range(1, 11)
                ]
            }
        
        return {'collection': []}
    
    def _parse_track_data(self, track_data: Dict[str, Any]) -> SoundCloudTrack:
        """Parse track data from SoundCloud API response"""        try:
            user_data = track_data.get('user', {})
            
            return SoundCloudTrack(
                id=track_data.get('id', 0),
                title=track_data.get('title', 'Unknown'),
                user=user_data.get('username', 'Unknown'),
                user_id=user_data.get('id', 0),
                duration_ms=track_data.get('duration', 0),
                permalink_url=track_data.get('permalink_url', ''),
                stream_url=track_data.get('stream_url'),
                download_url=track_data.get('download_url'),
                artwork_url=track_data.get('artwork_url'),
                waveform_url=track_data.get('waveform_url'),
                genre=track_data.get('genre'),
                tags=track_data.get('tag_list', '').split() if track_data.get('tag_list') else [],
                description=track_data.get('description'),
                play_count=track_data.get('playback_count', 0),
                like_count=track_data.get('favoritings_count', 0),
                comment_count=track_data.get('comment_count', 0),
                created_at=self._parse_date(track_data.get('created_at')),
                metadata=track_data
            )
            
        except Exception as e:
            logger.error(f"Failed to parse track data: {e}")
            raise
    
    def _parse_playlist_data(self, playlist_data: Dict[str, Any]) -> SoundCloudPlaylist:
        """Parse playlist data from SoundCloud API response"""        try:
            user_data = playlist_data.get('user', {})
            
            return SoundCloudPlaylist(
                id=playlist_data.get('id', 0),
                title=playlist_data.get('title', 'Unknown'),
                user=user_data.get('username', 'Unknown'),
                user_id=user_data.get('id', 0),
                track_count=playlist_data.get('track_count', 0),
                permalink_url=playlist_data.get('permalink_url', ''),
                artwork_url=playlist_data.get('artwork_url'),
                description=playlist_data.get('description'),
                duration_ms=playlist_data.get('duration', 0),
                created_at=self._parse_date(playlist_data.get('created_at')),
                metadata=playlist_data
            )
            
        except Exception as e:
            logger.error(f"Failed to parse playlist data: {e}")
            raise
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""        if not date_string:
            return None
        
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _is_positive_comment(self, comment: Dict[str, Any]) -> bool:
        """Simple sentiment analysis for comments"""        body = comment.get('body', '').lower()
        positive_words = ['great', 'awesome', 'love', 'amazing', 'good', 'nice', 'excellent', 'fantastic']
        negative_words = ['bad', 'awful', 'hate', 'terrible', 'horrible', 'sucks']
        
        positive_count = sum(1 for word in positive_words if word in body)
        negative_count = sum(1 for word in negative_words if word in body)
        
        return positive_count > negative_count
    
    def _calculate_popularity_tier(self, track: SoundCloudTrack) -> str:
        """Calculate popularity tier based on play count"""        plays = track.play_count
        
        if plays > 1000000:
            return 'viral'
        elif plays > 100000:
            return 'popular'
        elif plays > 10000:
            return 'emerging'
        else:
            return 'niche'
    
    def _assess_viral_potential(self, track: SoundCloudTrack) -> float:
        """Assess viral potential based on engagement metrics"""        if track.play_count == 0:
            return 0.0
        
        like_rate = track.like_count / track.play_count
        comment_rate = track.comment_count / track.play_count
        
        # Simple viral potential calculation
        viral_score = (like_rate * 100 + comment_rate * 1000) * 10
        return min(1.0, viral_score)
    
    def _analyze_growth_indicators(self, track: SoundCloudTrack) -> Dict[str, Any]:
        """Analyze growth indicators for a track"""        return {
            'engagement_velocity': track.like_count + track.comment_count,
            'discovery_potential': 'high' if track.play_count > 1000 else 'medium',
            'viral_indicators': {
                'high_engagement': (track.like_count / max(track.play_count, 1)) > 0.05,
                'active_comments': track.comment_count > 10,
                'recent_activity': track.created_at and (datetime.utcnow() - track.created_at).days < 30 if track.created_at else False
            }
        }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics and status"""        return {
            'initialized': self.session is not None,
            'has_client_id': bool(self.client_id),
            'has_access_token': bool(self.access_token),
            'rate_limit': self.rate_limit,
            'requests_made': self.request_count,
            'cache_size': len(self.cache),
            'scraper_available': self.scraper is not None
        }