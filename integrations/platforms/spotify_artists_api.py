"""
Spotify for Artists API Integration
===================================

Complete Spotify for Artists API integration for music analytics and management.
Handles artist data, track analytics, playlist management, and fan insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlencode
import base64

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class SpotifyTrack:
    """Spotify track information"""
    track_id: str
    name: str
    artists: List[str]
    album: str
    duration_ms: int
    popularity: int
    explicit: bool
    external_urls: Dict[str, str]
    preview_url: str = None
    release_date: str = None
    markets: List[str] = None


@dataclass
class SpotifyArtist:
    """Spotify artist information"""
    artist_id: str
    name: str
    genres: List[str]
    popularity: int
    followers: int
    external_urls: Dict[str, str]
    images: List[Dict[str, Any]]
    monthly_listeners: int = 0


@dataclass
class SpotifyAlbum:
    """Spotify album information"""
    album_id: str
    name: str
    album_type: str  # "album", "single", "compilation"
    artists: List[str]
    release_date: str
    total_tracks: int
    external_urls: Dict[str, str]
    images: List[Dict[str, Any]]
    markets: List[str] = None


@dataclass
class SpotifyAnalytics:
    """Spotify analytics data"""
    artist_id: str
    date_range: Dict[str, str]  # {"start": "2024-01-01", "end": "2024-01-31"}
    streams: int = 0
    listeners: int = 0
    followers: int = 0
    monthly_listeners: int = 0
    saves: int = 0
    skips: int = 0
    completion_rate: float = 0.0
    top_countries: List[Dict[str, Any]] = None
    top_cities: List[Dict[str, Any]] = None


class SpotifyArtistsAPI:
    """Spotify for Artists API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://api.spotify.com/v1"
        self.artists_url = "https://generic.wg.spotify.com/s4x-insights-esa/v0"
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("spotify", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("spotify", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{base_url or self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    await self.rate_limiter.record_request("spotify", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 204:
                        return {}
                    elif response.status == 429:
                        retry_after = response.headers.get("Retry-After", 60)
                        raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers, params=params) as response:
                    await self.rate_limiter.record_request("spotify", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    elif response.status == 204:
                        return {}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                async with self.session.request(
                    method, url, json=data, headers=headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("spotify", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Spotify API request failed: {e}")
            raise
            
    async def get_current_user_profile(self, tokens: OAuthTokens) -> Dict[str, Any]:
        """Get current user's Spotify profile"""



        return await self._make_request("GET", "me", tokens)
        
    async def get_artist_info(self, tokens: OAuthTokens, artist_id: str) -> SpotifyArtist:
        """Get artist information"""
        response = await self._make_request("GET", f"artists/{artist_id}", tokens)
        
        artist = SpotifyArtist(
            artist_id=response["id"],
            name=response["name"],
            genres=response.get("genres", []),
            popularity=response.get("popularity", 0),
            followers=response.get("followers", {}).get("total", 0),
            external_urls=response.get("external_urls", {}),
            images=response.get("images", [])
        )
        
        return artist
        
    async def get_artist_albums(
        self,
        tokens: OAuthTokens,
        artist_id: str,
        include_groups: Optional[List[str]] = None,
        market: str = "US",
        limit: int = 20,
        offset: int = 0
    ) -> List[SpotifyAlbum]:
        """Get artist's albums"""
        
        params = {
            "market": market,
            "limit": min(limit, 50),
            "offset": offset
        }
        
        if include_groups:
            params["include_groups"] = ",".join(include_groups)
        else:
            params["include_groups"] = "album,single,compilation"
            
        response = await self._make_request("GET", f"artists/{artist_id}/albums", tokens, params=params)
        
        albums = []
        for item in response.get("items", []):
            album = SpotifyAlbum(
                album_id=item["id"],
                name=item["name"],
                album_type=item["album_type"],
                artists=[artist["name"] for artist in item["artists"]],
                release_date=item["release_date"],
                total_tracks=item["total_tracks"],
                external_urls=item.get("external_urls", {}),
                images=item.get("images", []),
                markets=item.get("available_markets", [])
            )
            albums.append(album)
            
        return albums
        
    async def get_artist_top_tracks(
        self,
        tokens: OAuthTokens,
        artist_id: str,
        market: str = "US"
    ) -> List[SpotifyTrack]:
        """Get artist's top tracks"""
        
        params = {"market": market}
        response = await self._make_request("GET", f"artists/{artist_id}/top-tracks", tokens, params=params)
        
        tracks = []
        for item in response.get("tracks", []):
            track = SpotifyTrack(
                track_id=item["id"],
                name=item["name"],
                artists=[artist["name"] for artist in item["artists"]],
                album=item["album"]["name"],
                duration_ms=item["duration_ms"],
                popularity=item.get("popularity", 0),
                explicit=item.get("explicit", False),
                external_urls=item.get("external_urls", {}),
                preview_url=item.get("preview_url"),
                release_date=item["album"]["release_date"],
                markets=item.get("available_markets", [])
            )
            tracks.append(track)
            
        return tracks
        
    async def get_album_tracks(
        self,
        tokens: OAuthTokens,
        album_id: str,
        market: str = "US",
        limit: int = 20,
        offset: int = 0
    ) -> List[SpotifyTrack]:
        """Get tracks from an album"""
        
        params = {
            "market": market,
            "limit": min(limit, 50),
            "offset": offset
        }
        
        response = await self._make_request("GET", f"albums/{album_id}/tracks", tokens, params=params)
        
        tracks = []
        for item in response.get("items", []):
            track = SpotifyTrack(
                track_id=item["id"],
                name=item["name"],
                artists=[artist["name"] for artist in item["artists"]],
                album="",  # Will be filled from album info if needed
                duration_ms=item["duration_ms"],
                popularity=0,  # Not available in album tracks endpoint
                explicit=item.get("explicit", False),
                external_urls=item.get("external_urls", {}),
                preview_url=item.get("preview_url"),
                markets=item.get("available_markets", [])
            )
            tracks.append(track)
            
        return tracks
        
    async def search(
        self,
        tokens: OAuthTokens,
        query: str,
        search_type: Union[str, List[str]] = "track",
        market: str = "US",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search Spotify catalog"""
        
        if isinstance(search_type, list):
            search_type = ",".join(search_type)
            
        params = {
            "q": query,
            "type": search_type,
            "market": market,
            "limit": min(limit, 50),
            "offset": offset
        }
        
        return await self._make_request("GET", "search", tokens, params=params)
        
    async def get_track_features(
        self,
        tokens: OAuthTokens,
        track_ids: Union[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Get audio features for tracks"""
        
        if isinstance(track_ids, str):
            track_ids = [track_ids]
            
        # Spotify API supports up to 100 track IDs per request
        params = {"ids": ",".join(track_ids[:100])}
        
        response = await self._make_request("GET", "audio-features", tokens, params=params)
        
        return response.get("audio_features", [])
        
    async def get_track_analysis(self, tokens: OAuthTokens, track_id: str) -> Dict[str, Any]:
        """Get detailed audio analysis for a track"""



        return await self._make_request("GET", f"audio-analysis/{track_id}", tokens)
        
    async def get_user_playlists(
        self,
        tokens: OAuthTokens,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's playlists"""
        
        params = {
            "limit": min(limit, 50),
            "offset": offset
        }
        
        if user_id:
            endpoint = f"users/{user_id}/playlists"
        else:
            endpoint = "me/playlists"
            
        response = await self._make_request("GET", endpoint, tokens, params=params)
        
        return response.get("items", [])
        
    async def create_playlist(
        self,
        tokens: OAuthTokens,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
        collaborative: bool = False
    ) -> Dict[str, Any]:
        """Create a new playlist"""
        
        data = {
            "name": name,
            "public": public,
            "collaborative": collaborative
        }
        
        if description:
            data["description"] = description
            
        return await self._make_request("POST", f"users/{user_id}/playlists", tokens, data=data)
        
    async def add_tracks_to_playlist(
        self,
        tokens: OAuthTokens,
        playlist_id: str,
        track_uris: List[str],
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add tracks to a playlist"""
        
        data = {"uris": track_uris}
        
        if position is not None:
            data["position"] = position
            
        return await self._make_request("POST", f"playlists/{playlist_id}/tracks", tokens, data=data)
        
    async def get_playlist_tracks(
        self,
        tokens: OAuthTokens,
        playlist_id: str,
        market: str = "US",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get tracks from a playlist"""
        
        params = {
            "market": market,
            "limit": min(limit, 50),
            "offset": offset,
            "fields": "items(track(id,name,artists,album,duration_ms,popularity,explicit,external_urls))"
        }
        
        response = await self._make_request("GET", f"playlists/{playlist_id}/tracks", tokens, params=params)
        
        return response.get("items", [])
        
    async def get_artist_insights(
        self,
        tokens: OAuthTokens,
        artist_id: str,
        time_filter: str = "medium_term"  # "short_term", "medium_term", "long_term"
    ) -> SpotifyAnalytics:
        """Get artist insights (requires Spotify for Artists access)"""
        
        # Note: This endpoint requires special Spotify for Artists API access
        # This is a placeholder implementation based on available Web API data
        
        artist_info = await self.get_artist_info(tokens, artist_id)
        
        analytics = SpotifyAnalytics(
            artist_id=artist_id,
            date_range={
                "start": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d")
            },
            followers=artist_info.followers,
            monthly_listeners=artist_info.monthly_listeners
        )
        
        return analytics
        
    async def get_recommendations(
        self,
        tokens: OAuthTokens,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20,
        market: str = "US",
        **audio_features
    ) -> List[SpotifyTrack]:
        """Get track recommendations"""
        
        params = {
            "limit": min(limit, 100),
            "market": market
        }
        
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])
            
        # Add audio feature parameters
        for feature, value in audio_features.items():
            if feature.startswith(("min_", "max_", "target_")):
                params[feature] = value
                
        response = await self._make_request("GET", "recommendations", tokens, params=params)
        
        tracks = []
        for item in response.get("tracks", []):
            track = SpotifyTrack(
                track_id=item["id"],
                name=item["name"],
                artists=[artist["name"] for artist in item["artists"]],
                album=item["album"]["name"],
                duration_ms=item["duration_ms"],
                popularity=item.get("popularity", 0),
                explicit=item.get("explicit", False),
                external_urls=item.get("external_urls", {}),
                preview_url=item.get("preview_url"),
                release_date=item["album"]["release_date"]
            )
            tracks.append(track)
            
        return tracks
        
    async def get_available_genre_seeds(self, tokens: OAuthTokens) -> List[str]:
        """Get available genre seeds for recommendations"""
        response = await self._make_request("GET", "recommendations/available-genre-seeds", tokens)
        return response.get("genres", [])
        
    async def get_user_top_items(
        self,
        tokens: OAuthTokens,
        item_type: str = "tracks",  # "artists" or "tracks"
        time_range: str = "medium_term",  # "short_term", "medium_term", "long_term"
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's top artists or tracks"""
        
        params = {
            "time_range": time_range,
            "limit": min(limit, 50),
            "offset": offset
        }
        
        response = await self._make_request("GET", f"me/top/{item_type}", tokens, params=params)
        
        return response.get("items", [])
        
    async def get_recently_played(
        self,
        tokens: OAuthTokens,
        limit: int = 20,
        after: Optional[int] = None,
        before: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get user's recently played tracks"""
        
        params = {"limit": min(limit, 50)}
        
        if after:
            params["after"] = after
        if before:
            params["before"] = before
            
        response = await self._make_request("GET", "me/player/recently-played", tokens, params=params)
        
        return response.get("items", [])
        
    async def follow_artist(self, tokens: OAuthTokens, artist_ids: Union[str, List[str]]) -> bool:
        """Follow artists"""
        
        if isinstance(artist_ids, str):
            artist_ids = [artist_ids]
            
        data = {"ids": artist_ids[:50]}  # Max 50 per request
        
        try:
            await self._make_request("PUT", "me/following", tokens, data=data, params={"type": "artist"})
            logger.info(f"Successfully followed artists: {artist_ids}")
            return True
        except Exception as e:
            logger.error(f"Failed to follow artists: {e}")
            return False
            
    async def unfollow_artist(self, tokens: OAuthTokens, artist_ids: Union[str, List[str]]) -> bool:
        """Unfollow artists"""
        
        if isinstance(artist_ids, str):
            artist_ids = [artist_ids]
            
        data = {"ids": artist_ids[:50]}
        
        try:
            await self._make_request("DELETE", "me/following", tokens, data=data, params={"type": "artist"})
            logger.info(f"Successfully unfollowed artists: {artist_ids}")
            return True
        except Exception as e:
            logger.error(f"Failed to unfollow artists: {e}")
            return False
            
    async def check_following_artists(
        self,
        tokens: OAuthTokens,
        artist_ids: Union[str, List[str]]
    ) -> List[bool]:
        """Check if user follows artists"""
        
        if isinstance(artist_ids, str):
            artist_ids = [artist_ids]
            
        params = {
            "type": "artist",
            "ids": ",".join(artist_ids[:50])
        }
        
        response = await self._make_request("GET", "me/following/contains", tokens, params=params)
        
        return response if isinstance(response, list) else []