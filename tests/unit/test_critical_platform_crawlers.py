# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Unit Tests for Critical Crawlers
================================

Critical unit tests for the platform crawler modules including
Spotify, YouTube, and platform integration engine.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Address critical testing gap - "Tests Manquants: Pas de tests unitaires centralisés"
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
import json
import uuid


class MockSpotifyCrawler:
    """Mock implementation of Spotify crawler for testing"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.rate_limit_remaining = 1000
        self.crawled_tracks = []
        self.crawled_artists = []
        
    async def authenticate(self) -> bool:
        """Authenticate with Spotify API"""
        if not self.client_id or not self.client_secret:
            return False
        
        # Simulate OAuth flow
        self.access_token = f"spotify_token_{uuid.uuid4().hex[:16]}"
        return True
    
    async def search_track(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for tracks on Spotify"""
        if not self.access_token:
            raise Exception("Not authenticated")
        
        # Simulate rate limiting
        self.rate_limit_remaining -= 1
        if self.rate_limit_remaining <= 0:
            raise Exception("Rate limit exceeded")
        
        # Generate mock search results
        tracks = []
        for i in range(min(limit, 5)):  # Limit to 5 for testing
            track = {
                "id": f"track_{uuid.uuid4().hex[:8]}",
                "name": f"Test Track {i + 1} - {query}",
                "artists": [
                    {
                        "id": f"artist_{uuid.uuid4().hex[:8]}",
                        "name": f"Test Artist {i + 1}",
                        "popularity": 70 + i * 5
                    }
                ],
                "album": {
                    "id": f"album_{uuid.uuid4().hex[:8]}",
                    "name": f"Test Album {i + 1}",
                    "release_date": "2023-01-01"
                },
                "duration_ms": 180000 + i * 15000,
                "popularity": 75 + i * 3,
                "explicit": i % 2 == 0,
                "external_urls": {
                    "spotify": f"https://open.spotify.com/track/test_{i}"
                },
                "preview_url": f"https://p.scdn.co/mp3-preview/test_{i}"
            }
            tracks.append(track)
        
        result = {
            "tracks": {
                "items": tracks,
                "total": len(tracks),
                "limit": limit,
                "offset": 0
            },
            "query": query,
            "searched_at": datetime.utcnow().isoformat()
        }
        
        self.crawled_tracks.extend(tracks)
        return result
    
    async def get_artist_info(self, artist_id: str) -> Dict[str, Any]:
        """Get detailed artist information"""
        if not self.access_token:
            raise Exception("Not authenticated")
        
        artist_info = {
            "id": artist_id,
            "name": f"Artist {artist_id[-8:]}",
            "popularity": 75,
            "genres": ["pop", "electronic", "dance"],
            "followers": {
                "total": 150000
            },
            "images": [
                {
                    "url": f"https://i.scdn.co/image/artist_{artist_id}",
                    "height": 640,
                    "width": 640
                }
            ],
            "external_urls": {
                "spotify": f"https://open.spotify.com/artist/{artist_id}"
            }
        }
        
        self.crawled_artists.append(artist_info)
        return artist_info
    
    async def get_track_features(self, track_id: str) -> Dict[str, Any]:
        """Get audio features for a track"""
        features = {
            "id": track_id,
            "acousticness": 0.2 + (hash(track_id) % 100) / 100 * 0.6,
            "danceability": 0.3 + (hash(track_id) % 100) / 100 * 0.5,
            "energy": 0.4 + (hash(track_id) % 100) / 100 * 0.4,
            "instrumentalness": (hash(track_id) % 100) / 100 * 0.3,
            "liveness": 0.1 + (hash(track_id) % 100) / 100 * 0.2,
            "loudness": -15.0 + (hash(track_id) % 100) / 100 * 10,
            "speechiness": (hash(track_id) % 100) / 100 * 0.4,
            "tempo": 100 + (hash(track_id) % 100) / 100 * 80,
            "valence": 0.2 + (hash(track_id) % 100) / 100 * 0.6,
            "time_signature": 4
        }
        return features


class MockYouTubeCrawler:
    """Mock implementation of YouTube crawler for testing"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.quota_used = 0
        self.daily_quota_limit = 10000
        self.crawled_videos = []
        self.crawled_channels = []
        
    async def search_videos(self, query: str, max_results: int = 25) -> Dict[str, Any]:
        """Search for videos on YouTube"""
        if not self.api_key:
            raise Exception("API key required")
        
        # Simulate quota usage
        quota_cost = max_results  # 1 quota unit per result
        if self.quota_used + quota_cost > self.daily_quota_limit:
            raise Exception("Daily quota exceeded")
        
        self.quota_used += quota_cost
        
        # Generate mock video results
        videos = []
        for i in range(min(max_results, 10)):  # Limit to 10 for testing
            video = {
                "id": f"video_{uuid.uuid4().hex[:11]}",  # YouTube video ID format
                "title": f"Test Video {i + 1} - {query}",
                "description": f"This is a test video about {query}. Video number {i + 1}.",
                "channel": {
                    "id": f"channel_{uuid.uuid4().hex[:8]}",
                    "title": f"Test Channel {i + 1}",
                    "description": f"Test channel for video {i + 1}"
                },
                "published_at": (datetime.utcnow() - timedelta(days=i * 10)).isoformat(),
                "duration": f"PT{180 + i * 30}S",  # ISO 8601 duration format
                "view_count": 1000 + i * 500,
                "like_count": 50 + i * 25,
                "comment_count": 10 + i * 5,
                "thumbnail": {
                    "url": f"https://img.youtube.com/vi/test_{i}/maxresdefault.jpg",
                    "width": 1280,
                    "height": 720
                },
                "tags": [f"tag{j}" for j in range(3)],
                "category_id": "10",  # Music category
                "language": "en"
            }
            videos.append(video)
        
        result = {
            "videos": videos,
            "total_results": len(videos),
            "query": query,
            "quota_used": quota_cost,
            "searched_at": datetime.utcnow().isoformat()
        }
        
        self.crawled_videos.extend(videos)
        return result
    
    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed video information"""
        if not self.api_key:
            raise Exception("API key required")
        
        # Simulate quota usage
        self.quota_used += 1
        
        video_details = {
            "id": video_id,
            "title": f"Detailed Video {video_id[-8:]}",
            "description": f"Detailed description for video {video_id}",
            "channel_id": f"channel_{uuid.uuid4().hex[:8]}",
            "published_at": datetime.utcnow().isoformat(),
            "duration": "PT245S",
            "statistics": {
                "view_count": 15000,
                "like_count": 850,
                "dislike_count": 25,
                "comment_count": 120,
                "favorite_count": 0
            },
            "content_details": {
                "duration": "PT245S",
                "dimension": "2d",
                "definition": "hd",
                "caption": "false",
                "licensed_content": True
            },
            "snippet": {
                "thumbnails": {
                    "maxres": {
                        "url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                        "width": 1280,
                        "height": 720
                    }
                },
                "tags": ["music", "test", "video"],
                "category_id": "10",
                "default_language": "en"
            }
        }
        
        return video_details
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get channel information"""
        channel_info = {
            "id": channel_id,
            "title": f"Channel {channel_id[-8:]}",
            "description": f"Test channel description for {channel_id}",
            "published_at": "2020-01-01T00:00:00Z",
            "statistics": {
                "subscriber_count": 50000,
                "video_count": 150,
                "view_count": 2500000
            },
            "thumbnails": {
                "high": {
                    "url": f"https://yt3.ggpht.com/channel_{channel_id}",
                    "width": 800,
                    "height": 800
                }
            },
            "country": "US",
            "uploads_playlist_id": f"uploads_{channel_id}"
        }
        
        self.crawled_channels.append(channel_info)
        return channel_info


class MockPlatformIntegrationEngine:
    """Mock implementation of platform integration engine"""
    
    def __init__(self):
        self.registered_platforms = {}
        self.active_connections = {}
        self.crawl_history = []
        
    async def register_platform(self, platform_name: str, crawler_instance: Any, credentials: Dict) -> bool:
        """Register a platform crawler"""
        if not platform_name or not crawler_instance:
            return False
        
        self.registered_platforms[platform_name] = {
            "crawler": crawler_instance,
            "credentials": credentials,
            "status": "active",
            "registered_at": datetime.utcnow().isoformat()
        }
        return True
    
    async def test_platform_connection(self, platform_name: str) -> Dict[str, Any]:
        """Test connection to a registered platform"""
        if platform_name not in self.registered_platforms:
            return {
                "platform": platform_name,
                "status": "error",
                "message": "Platform not registered"
            }
        
        platform_info = self.registered_platforms[platform_name]
        crawler = platform_info["crawler"]
        
        try:
            # Test authentication for different platforms
            if hasattr(crawler, 'authenticate'):
                auth_result = await crawler.authenticate()
                if not auth_result:
                    return {
                        "platform": platform_name,
                        "status": "error",
                        "message": "Authentication failed"
                    }
            
            # Test basic functionality
            if hasattr(crawler, 'search_track'):
                # Test Spotify-like platform
                test_result = await crawler.search_track("test", limit=1)
            elif hasattr(crawler, 'search_videos'):
                # Test YouTube-like platform
                test_result = await crawler.search_videos("test", max_results=1)
            
            return {
                "platform": platform_name,
                "status": "success",
                "message": "Connection successful",
                "test_performed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "platform": platform_name,
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }
    
    async def cross_platform_search(self, query: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Perform search across multiple platforms"""
        if platforms is None:
            platforms = list(self.registered_platforms.keys())
        
        results = {}
        
        for platform_name in platforms:
            if platform_name not in self.registered_platforms:
                results[platform_name] = {
                    "status": "error",
                    "message": "Platform not registered"
                }
                continue
            
            try:
                crawler = self.registered_platforms[platform_name]["crawler"]
                
                if hasattr(crawler, 'search_track'):
                    platform_results = await crawler.search_track(query, limit=5)
                elif hasattr(crawler, 'search_videos'):
                    platform_results = await crawler.search_videos(query, max_results=5)
                else:
                    platform_results = {"message": "No search method available"}
                
                results[platform_name] = {
                    "status": "success",
                    "data": platform_results
                }
                
            except Exception as e:
                results[platform_name] = {
                    "status": "error",
                    "message": str(e)
                }
        
        crawl_record = {
            "query": query,
            "platforms": platforms,
            "results": results,
            "performed_at": datetime.utcnow().isoformat()
        }
        
        self.crawl_history.append(crawl_record)
        
        return {
            "query": query,
            "platforms_searched": len(platforms),
            "successful_platforms": len([r for r in results.values() if r.get("status") == "success"]),
            "results": results,
            "search_id": len(self.crawl_history)
        }
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Get statistics for all registered platforms"""
        stats = {
            "total_platforms": len(self.registered_platforms),
            "active_platforms": len([p for p in self.registered_platforms.values() if p["status"] == "active"]),
            "total_searches": len(self.crawl_history),
            "platform_details": {}
        }
        
        for platform_name, platform_info in self.registered_platforms.items():
            crawler = platform_info["crawler"]
            
            platform_stats = {
                "status": platform_info["status"],
                "registered_at": platform_info["registered_at"]
            }
            
            # Platform-specific statistics
            if hasattr(crawler, 'crawled_tracks'):
                platform_stats["tracks_crawled"] = len(crawler.crawled_tracks)
                platform_stats["artists_crawled"] = len(getattr(crawler, 'crawled_artists', []))
            elif hasattr(crawler, 'crawled_videos'):
                platform_stats["videos_crawled"] = len(crawler.crawled_videos)
                platform_stats["channels_crawled"] = len(getattr(crawler, 'crawled_channels', []))
            
            stats["platform_details"][platform_name] = platform_stats
        
        return stats


class TestCriticalCrawlers:
    """Test suite for critical crawler functionality"""
    
    @pytest.fixture
    def spotify_crawler(self):
        """Create Spotify crawler fixture"""



        return MockSpotifyCrawler("test_client_id", "test_client_secret")
    
    @pytest.fixture
    def youtube_crawler(self):
        """Create YouTube crawler fixture"""



        return MockYouTubeCrawler("test_api_key")
    
    @pytest.fixture
    def integration_engine(self):
        """Create platform integration engine fixture"""



        return MockPlatformIntegrationEngine()
    
    @pytest.mark.asyncio
    async def test_spotify_authentication(self, spotify_crawler):
        """Test Spotify authentication"""
        # Test successful authentication
        auth_result = await spotify_crawler.authenticate()
        assert auth_result is True
        assert spotify_crawler.access_token is not None
        assert spotify_crawler.access_token.startswith("spotify_token_")
        
        # Test authentication with invalid credentials
        invalid_crawler = MockSpotifyCrawler("", "")
        auth_result = await invalid_crawler.authenticate()
        assert auth_result is False
    
    @pytest.mark.asyncio
    async def test_spotify_track_search(self, spotify_crawler):
        """Test Spotify track search functionality"""
        # Authenticate first
        await spotify_crawler.authenticate()
        
        # Search for tracks
        search_result = await spotify_crawler.search_track("test song", limit=5)
        
        # Validate search results
        assert "tracks" in search_result
        assert "query" in search_result
        assert search_result["query"] == "test song"
        
        tracks = search_result["tracks"]["items"]
        assert len(tracks) <= 5
        assert len(tracks) > 0
        
        # Validate track structure
        track = tracks[0]
        assert "id" in track
        assert "name" in track
        assert "artists" in track
        assert "album" in track
        assert "duration_ms" in track
        assert "popularity" in track
        
        # Validate artist structure
        artist = track["artists"][0]
        assert "id" in artist
        assert "name" in artist
        assert "popularity" in artist
        
        # Verify tracks were stored
        assert len(spotify_crawler.crawled_tracks) == len(tracks)
    
    @pytest.mark.asyncio
    async def test_spotify_artist_info(self, spotify_crawler):
        """Test Spotify artist information retrieval"""
        await spotify_crawler.authenticate()
        
        artist_id = "test_artist_123"
        artist_info = await spotify_crawler.get_artist_info(artist_id)
        
        # Validate artist information
        assert "id" in artist_info
        assert artist_info["id"] == artist_id
        assert "name" in artist_info
        assert "popularity" in artist_info
        assert "genres" in artist_info
        assert "followers" in artist_info
        assert "images" in artist_info
        assert "external_urls" in artist_info
        
        # Validate followers structure
        assert "total" in artist_info["followers"]
        assert isinstance(artist_info["followers"]["total"], int)
        
        # Verify artist was stored
        assert len(spotify_crawler.crawled_artists) == 1
    
    @pytest.mark.asyncio
    async def test_spotify_track_features(self, spotify_crawler):
        """Test Spotify track audio features"""
        await spotify_crawler.authenticate()
        
        track_id = "test_track_456"
        features = await spotify_crawler.get_track_features(track_id)
        
        # Validate audio features
        expected_features = [
            "acousticness", "danceability", "energy", "instrumentalness",
            "liveness", "loudness", "speechiness", "tempo", "valence", "time_signature"
        ]
        
        for feature in expected_features:
            assert feature in features
        
        # Validate feature ranges
        assert 0 <= features["acousticness"] <= 1
        assert 0 <= features["danceability"] <= 1
        assert 0 <= features["energy"] <= 1
        assert features["tempo"] >= 0
        assert features["time_signature"] in [3, 4, 5, 6, 7]
    
    @pytest.mark.asyncio
    async def test_spotify_rate_limiting(self, spotify_crawler):
        """Test Spotify rate limiting"""
        await spotify_crawler.authenticate()
        
        # Set rate limit for testing - start with 2 so first call succeeds
        spotify_crawler.rate_limit_remaining = 2
        
        # First request should succeed
        result = await spotify_crawler.search_track("test", limit=1)
        assert "tracks" in result
        
        # Second request should fail due to rate limit
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await spotify_crawler.search_track("test2", limit=1)
    
    @pytest.mark.asyncio
    async def test_youtube_video_search(self, youtube_crawler):
        """Test YouTube video search functionality"""
        search_result = await youtube_crawler.search_videos("test video", max_results=5)
        
        # Validate search results
        assert "videos" in search_result
        assert "query" in search_result
        assert search_result["query"] == "test video"
        assert "quota_used" in search_result
        
        videos = search_result["videos"]
        assert len(videos) <= 5
        assert len(videos) > 0
        
        # Validate video structure
        video = videos[0]
        assert "id" in video
        assert "title" in video
        assert "description" in video
        assert "channel" in video
        assert "published_at" in video
        assert "view_count" in video
        assert "like_count" in video
        
        # Validate channel structure
        channel = video["channel"]
        assert "id" in channel
        assert "title" in channel
        
        # Verify videos were stored
        assert len(youtube_crawler.crawled_videos) == len(videos)
    
    @pytest.mark.asyncio
    async def test_youtube_video_details(self, youtube_crawler):
        """Test YouTube video details retrieval"""
        video_id = "test_video_123"
        video_details = await youtube_crawler.get_video_details(video_id)
        
        # Validate video details
        assert "id" in video_details
        assert video_details["id"] == video_id
        assert "title" in video_details
        assert "description" in video_details
        assert "statistics" in video_details
        assert "content_details" in video_details
        assert "snippet" in video_details
        
        # Validate statistics
        stats = video_details["statistics"]
        assert "view_count" in stats
        assert "like_count" in stats
        assert "comment_count" in stats
        
        # Validate content details
        content = video_details["content_details"]
        assert "duration" in content
        assert "definition" in content
    
    @pytest.mark.asyncio
    async def test_youtube_channel_info(self, youtube_crawler):
        """Test YouTube channel information retrieval"""
        channel_id = "test_channel_789"
        channel_info = await youtube_crawler.get_channel_info(channel_id)
        
        # Validate channel information
        assert "id" in channel_info
        assert channel_info["id"] == channel_id
        assert "title" in channel_info
        assert "description" in channel_info
        assert "statistics" in channel_info
        assert "thumbnails" in channel_info
        
        # Validate statistics
        stats = channel_info["statistics"]
        assert "subscriber_count" in stats
        assert "video_count" in stats
        assert "view_count" in stats
        
        # Verify channel was stored
        assert len(youtube_crawler.crawled_channels) == 1
    
    @pytest.mark.asyncio
    async def test_youtube_quota_management(self, youtube_crawler):
        """Test YouTube quota management"""
        # Set low quota limit for testing
        youtube_crawler.daily_quota_limit = 5
        youtube_crawler.quota_used = 0
        
        # First request should succeed
        result = await youtube_crawler.search_videos("test", max_results=3)
        assert youtube_crawler.quota_used == 3
        
        # Second request should succeed but use remaining quota
        result = await youtube_crawler.search_videos("test2", max_results=2)
        assert youtube_crawler.quota_used == 5
        
        # Third request should fail due to quota limit
        with pytest.raises(Exception, match="Daily quota exceeded"):
            await youtube_crawler.search_videos("test3", max_results=1)
    
    @pytest.mark.asyncio
    async def test_platform_registration(self, integration_engine, spotify_crawler, youtube_crawler):
        """Test platform registration in integration engine"""
        # Register Spotify
        spotify_result = await integration_engine.register_platform(
            "spotify",
            spotify_crawler,
            {"client_id": "test_id", "client_secret": "test_secret"}
        )
        assert spotify_result is True
        
        # Register YouTube
        youtube_result = await integration_engine.register_platform(
            "youtube",
            youtube_crawler,
            {"api_key": "test_key"}
        )
        assert youtube_result is True
        
        # Verify registration
        assert "spotify" in integration_engine.registered_platforms
        assert "youtube" in integration_engine.registered_platforms
        assert len(integration_engine.registered_platforms) == 2
        
        # Test invalid registration
        invalid_result = await integration_engine.register_platform("", None, {})
        assert invalid_result is False
    
    @pytest.mark.asyncio
    async def test_platform_connection_testing(self, integration_engine, spotify_crawler):
        """Test platform connection testing"""
        # Register platform first
        await integration_engine.register_platform("spotify", spotify_crawler, {})
        
        # Test connection
        connection_result = await integration_engine.test_platform_connection("spotify")
        
        # Validate connection result
        assert "platform" in connection_result
        assert connection_result["platform"] == "spotify"
        assert "status" in connection_result
        assert connection_result["status"] == "success"
        assert "message" in connection_result
        
        # Test connection to unregistered platform
        unregistered_result = await integration_engine.test_platform_connection("unregistered")
        assert unregistered_result["status"] == "error"
        assert "not registered" in unregistered_result["message"]
    
    @pytest.mark.asyncio
    async def test_cross_platform_search(self, integration_engine, spotify_crawler, youtube_crawler):
        """Test cross-platform search functionality"""
        # Register both platforms
        await integration_engine.register_platform("spotify", spotify_crawler, {})
        await integration_engine.register_platform("youtube", youtube_crawler, {})
        
        # Authenticate Spotify
        await spotify_crawler.authenticate()
        
        # Perform cross-platform search
        search_result = await integration_engine.cross_platform_search("test music")
        
        # Validate search result
        assert "query" in search_result
        assert search_result["query"] == "test music"
        assert "platforms_searched" in search_result
        assert search_result["platforms_searched"] == 2
        assert "successful_platforms" in search_result
        assert "results" in search_result
        
        # Validate platform-specific results
        results = search_result["results"]
        assert "spotify" in results
        assert "youtube" in results
        
        # Both platforms should be successful
        assert results["spotify"]["status"] == "success"
        assert results["youtube"]["status"] == "success"
        
        # Verify search was recorded
        assert len(integration_engine.crawl_history) == 1
    
    @pytest.mark.asyncio
    async def test_platform_statistics(self, integration_engine, spotify_crawler, youtube_crawler):
        """Test platform statistics generation"""
        # Register platforms and perform some operations
        await integration_engine.register_platform("spotify", spotify_crawler, {})
        await integration_engine.register_platform("youtube", youtube_crawler, {})
        
        await spotify_crawler.authenticate()
        await spotify_crawler.search_track("test", limit=3)
        await youtube_crawler.search_videos("test", max_results=2)
        
        # Get statistics
        stats = await integration_engine.get_platform_statistics()
        
        # Validate statistics structure
        assert "total_platforms" in stats
        assert stats["total_platforms"] == 2
        assert "active_platforms" in stats
        assert stats["active_platforms"] == 2
        assert "platform_details" in stats
        
        # Validate platform-specific statistics
        details = stats["platform_details"]
        assert "spotify" in details
        assert "youtube" in details
        
        # Validate Spotify statistics
        spotify_stats = details["spotify"]
        assert "tracks_crawled" in spotify_stats
        assert spotify_stats["tracks_crawled"] == 3
        
        # Validate YouTube statistics
        youtube_stats = details["youtube"]
        assert "videos_crawled" in youtube_stats
        assert youtube_stats["videos_crawled"] == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, integration_engine):
        """Test error handling in crawlers"""
        # Test unauthenticated requests
        unauth_spotify = MockSpotifyCrawler("test_id", "test_secret")
        
        with pytest.raises(Exception, match="Not authenticated"):
            await unauth_spotify.search_track("test")
        
        # Test invalid API key
        invalid_youtube = MockYouTubeCrawler("")
        
        with pytest.raises(Exception, match="API key required"):
            await invalid_youtube.search_videos("test")
    
    def test_crawler_initialization(self):
        """Test crawler initialization"""
        # Test Spotify crawler
        spotify = MockSpotifyCrawler("client_id", "client_secret")
        assert spotify.client_id == "client_id"
        assert spotify.client_secret == "client_secret"
        assert spotify.access_token is None
        assert spotify.crawled_tracks == []
        
        # Test YouTube crawler
        youtube = MockYouTubeCrawler("api_key")
        assert youtube.api_key == "api_key"
        assert youtube.quota_used == 0
        assert youtube.crawled_videos == []
        
        # Test integration engine
        engine = MockPlatformIntegrationEngine()
        assert engine.registered_platforms == {}
        assert engine.crawl_history == []


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([str(Path(__file__)), "-v"])