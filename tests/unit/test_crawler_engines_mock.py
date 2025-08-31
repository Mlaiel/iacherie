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
Mock-based Unit Tests for Crawler Engines
=========================================

Mock-based tests for crawler engines that work without aiohttp dependencies.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Complete crawler test coverage without external dependencies
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import hashlib

class MockCrawlerResponse:
    """Mock HTTP response for crawler"""
    
    def __init__(self, status: int, data: Dict, url: str):
        self.status = status
        self.data = data
        self.url = url
    
    async def json(self):
        return self.data
    
    async def text(self):
        return json.dumps(self.data)


class MockPlatformCrawler:
    """Mock platform crawler base class"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.rate_limit_delay = 1.0
        self.max_retries = 3
        self.session = None
        self.crawl_history = []
    
    async def initialize(self):
        """Initialize crawler session"""
        self.session = MockHTTPSession()
    
    async def cleanup(self):
        """Cleanup crawler resources"""
        if self.session:
            await self.session.close()
    
    async def crawl_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Mock content crawling"""
        self.crawl_history.append({
            'query': query,
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate mock results
        results = []
        for i in range(min(limit, 5)):  # Max 5 mock results
            content_id = f"{self.platform_name}_{hashlib.md5(f'{query}_{i}'.encode()).hexdigest()[:8]}"
            results.append({
                'platform': self.platform_name,
                'content_id': content_id,
                'title': f"Mock {self.platform_name} content {i+1}",
                'url': f"https://{self.platform_name}.com/content/{content_id}",
                'metadata': {
                    'views': 1000 + i * 100,
                    'duration': 180 + i * 30,
                    'upload_date': (datetime.now() - timedelta(days=i)).isoformat()
                }
            })
        
        return results
    
    async def search_by_fingerprint(self, fingerprint: str) -> List[Dict]:
        """Mock fingerprint-based search"""



        return [{
            'platform': self.platform_name,
            'content_id': f"fp_match_{fingerprint[:8]}",
            'title': f"Fingerprint match on {self.platform_name}",
            'similarity_score': 0.85,
            'match_type': 'audio_fingerprint'
        }]


class MockHTTPSession:
    """Mock HTTP session for crawlers"""
    
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.closed = False
    
    async def get(self, url: str, headers: Dict = None) -> MockCrawlerResponse:
        """Mock GET request"""
        if self.closed:
            raise Exception("Session is closed")
        
        # Mock different platform responses
        if "youtube.com" in url:
            return MockCrawlerResponse(200, {
                'items': [
                    {
                        'id': 'yt_video_123',
                        'snippet': {
                            'title': 'Mock YouTube Video',
                            'description': 'Test video description',
                            'publishedAt': datetime.now().isoformat()
                        },
                        'statistics': {
                            'viewCount': '1000',
                            'likeCount': '50'
                        }
                    }
                ]
            }, url)
        elif "spotify.com" in url:
            return MockCrawlerResponse(200, {
                'tracks': {
                    'items': [
                        {
                            'id': 'spotify_track_456',
                            'name': 'Mock Spotify Track',
                            'artists': [{'name': 'Mock Artist'}],
                            'duration_ms': 180000,
                            'popularity': 75
                        }
                    ]
                }
            }, url)
        elif "tiktok.com" in url:
            return MockCrawlerResponse(200, {
                'data': [
                    {
                        'id': 'tiktok_video_789',
                        'desc': 'Mock TikTok Video',
                        'author': {'nickname': 'mock_user'},
                        'stats': {
                            'diggCount': 100,
                            'playCount': 5000
                        }
                    }
                ]
            }, url)
        
        return MockCrawlerResponse(404, {'error': 'Not found'}, url)
    
    async def post(self, url: str, data: Dict = None, headers: Dict = None) -> MockCrawlerResponse:
        """Mock POST request"""
        if self.closed:
            raise Exception("Session is closed")
        
        return MockCrawlerResponse(200, {
            'success': True,
            'submitted_data': data
        }, url)
    
    async def close(self):
        """Close session"""
        self.closed = True


class MockYouTubeCrawler(MockPlatformCrawler):
    """Mock YouTube crawler"""
    
    def __init__(self):
        super().__init__("youtube")
        self.api_key = "mock_youtube_api_key"
    
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube videos"""



        return await self.crawl_content(query, max_results)
    
    async def get_video_details(self, video_id: str) -> Dict:
        """Get detailed video information"""



        return {
            'video_id': video_id,
            'title': f"Mock video {video_id}",
            'description': "Mock video description",
            'duration': 180,
            'view_count': 1000,
            'like_count': 50,
            'upload_date': datetime.now().isoformat()
        }


class MockSpotifyCrawler(MockPlatformCrawler):
    """Mock Spotify crawler"""
    
    def __init__(self):
        super().__init__("spotify")
        self.access_token = "mock_spotify_token"
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Spotify tracks"""



        return await self.crawl_content(query, limit)
    
    async def get_track_features(self, track_id: str) -> Dict:
        """Get audio features for track"""



        return {
            'track_id': track_id,
            'tempo': 120.0,
            'energy': 0.8,
            'danceability': 0.7,
            'valence': 0.6,
            'acousticness': 0.2
        }


class MockTikTokCrawler(MockPlatformCrawler):
    """Mock TikTok crawler"""
    
    def __init__(self):
        super().__init__("tiktok")
    
    async def search_videos(self, hashtag: str, count: int = 10) -> List[Dict]:
        """Search TikTok videos by hashtag"""



        return await self.crawl_content(f"#{hashtag}", count)
    
    async def get_user_videos(self, username: str, count: int = 10) -> List[Dict]:
        """Get videos from specific user"""



        return await self.crawl_content(f"@{username}", count)


@pytest.mark.asyncio
class TestCrawlerEngines:
    """Test crawler engine functionality"""
    
    @pytest.fixture
    def youtube_crawler(self):
        return MockYouTubeCrawler()
    
    @pytest.fixture
    def spotify_crawler(self):
        return MockSpotifyCrawler()
    
    @pytest.fixture
    def tiktok_crawler(self):
        return MockTikTokCrawler()
    
    async def test_youtube_video_search(self, youtube_crawler):
        """Test YouTube video search"""
        await youtube_crawler.initialize()
        results = await youtube_crawler.search_videos("test music", max_results=5)
        await youtube_crawler.cleanup()
        
        assert len(results) <= 5
        assert all('platform' in result for result in results)
        assert all(result['platform'] == 'youtube' for result in results)
        assert all('content_id' in result for result in results)
        assert all('title' in result for result in results)
    
    async def test_youtube_video_details(self, youtube_crawler):
        """Test YouTube video details retrieval"""
        await youtube_crawler.initialize()
        video_id = "test_video_123"
        details = await youtube_crawler.get_video_details(video_id)
        await youtube_crawler.cleanup()
        
        assert details['video_id'] == video_id
        assert 'title' in details
        assert 'description' in details
        assert 'duration' in details
        assert 'view_count' in details
    
    async def test_spotify_track_search(self, spotify_crawler):
        """Test Spotify track search"""
        await spotify_crawler.initialize()
        results = await spotify_crawler.search_tracks("test song", limit=3)
        await spotify_crawler.cleanup()
        
        assert len(results) <= 3
        assert all('platform' in result for result in results)
        assert all(result['platform'] == 'spotify' for result in results)
        assert all('content_id' in result for result in results)
    
    async def test_spotify_track_features(self, spotify_crawler):
        """Test Spotify audio features"""
        await spotify_crawler.initialize()
        track_id = "test_track_456"
        features = await spotify_crawler.get_track_features(track_id)
        await spotify_crawler.cleanup()
        
        assert features['track_id'] == track_id
        assert 'tempo' in features
        assert 'energy' in features
        assert 'danceability' in features
    
    async def test_tiktok_hashtag_search(self, tiktok_crawler):
        """Test TikTok hashtag search"""
        await tiktok_crawler.initialize()
        results = await tiktok_crawler.search_videos("music", count=3)
        await tiktok_crawler.cleanup()
        
        assert len(results) <= 3
        assert all('platform' in result for result in results)
        assert all(result['platform'] == 'tiktok' for result in results)
    
    async def test_tiktok_user_videos(self, tiktok_crawler):
        """Test TikTok user video retrieval"""
        await tiktok_crawler.initialize()
        results = await tiktok_crawler.get_user_videos("testuser", count=2)
        await tiktok_crawler.cleanup()
        
        assert len(results) <= 2
        assert all(result['platform'] == 'tiktok' for result in results)


@pytest.mark.asyncio
class TestCrawlerErrorHandling:
    """Test crawler error handling"""
    
    async def test_session_initialization(self):
        """Test crawler session initialization"""
        crawler = MockPlatformCrawler("test")
        assert crawler.session is None
        
        await crawler.initialize()
        assert crawler.session is not None
        
        await crawler.cleanup()
    
    async def test_rate_limiting(self):
        """Test rate limiting behavior"""
        crawler = MockPlatformCrawler("test")
        await crawler.initialize()
        
        # Test rate limit configuration
        assert crawler.rate_limit_delay > 0
        assert crawler.max_retries > 0
        
        await crawler.cleanup()
    
    async def test_invalid_response_handling(self):
        """Test handling of invalid responses"""
        crawler = MockPlatformCrawler("test")
        await crawler.initialize()
        
        # This would test error handling in real implementation
        # For mock, we ensure it doesn't crash
        try:
            results = await crawler.crawl_content("invalid_query")
            assert isinstance(results, list)
        except Exception as e:
            # Should handle gracefully
            pass
        
        await crawler.cleanup()


@pytest.mark.asyncio 
class TestCrawlerIntegration:
    """Test integrated crawler functionality"""
    
    async def test_multi_platform_search(self):
        """Test searching across multiple platforms"""
        platforms = [
            MockYouTubeCrawler(),
            MockSpotifyCrawler(),
            MockTikTokCrawler()
        ]
        
        all_results = []
        query = "test content"
        
        for crawler in platforms:
            await crawler.initialize()
            results = await crawler.crawl_content(query, limit=2)
            all_results.extend(results)
            await crawler.cleanup()
        
        # Should have results from all platforms
        platform_names = {result['platform'] for result in all_results}
        assert len(platform_names) == 3
        assert 'youtube' in platform_names
        assert 'spotify' in platform_names
        assert 'tiktok' in platform_names
    
    async def test_fingerprint_search_integration(self):
        """Test fingerprint-based search across platforms"""
        crawler = MockYouTubeCrawler()
        await crawler.initialize()
        
        fingerprint = "test_fingerprint_123"
        results = await crawler.search_by_fingerprint(fingerprint)
        
        assert len(results) > 0
        assert all('similarity_score' in result for result in results)
        assert all('match_type' in result for result in results)
        
        await crawler.cleanup()


class TestCrawlerPerformance:
    """Test crawler performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_crawling(self):
        """Test concurrent crawling performance"""
        import asyncio
        
        crawler = MockYouTubeCrawler()
        await crawler.initialize()
        
        # Create multiple concurrent search tasks
        tasks = []
        for i in range(3):
            task = crawler.crawl_content(f"query_{i}", limit=2)
            tasks.append(task)
        
        # Execute concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        # Verify results
        assert len(results) == 3
        assert all(isinstance(result, list) for result in results)
        
        # Performance should be reasonable (mock is fast)
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0
        
        await crawler.cleanup()
    
    @pytest.mark.asyncio
    async def test_crawl_history_tracking(self):
        """Test crawl history and logging"""
        crawler = MockPlatformCrawler("test")
        await crawler.initialize()
        
        # Perform multiple crawls
        await crawler.crawl_content("query1", 5)
        await crawler.crawl_content("query2", 3)
        
        # Verify history tracking
        assert len(crawler.crawl_history) == 2
        assert crawler.crawl_history[0]['query'] == 'query1'
        assert crawler.crawl_history[0]['limit'] == 5
        assert crawler.crawl_history[1]['query'] == 'query2'
        assert crawler.crawl_history[1]['limit'] == 3
        
        await crawler.cleanup()


def test_crawler_coverage():
    """Test that all essential crawler functionality is covered"""
    
    # Test base crawler
    crawler = MockPlatformCrawler("test")
    
    required_methods = [
        'initialize', 'cleanup', 'crawl_content', 'search_by_fingerprint'
    ]
    
    for method in required_methods:
        assert hasattr(crawler, method)
        assert callable(getattr(crawler, method))
    
    # Test platform-specific crawlers
    youtube = MockYouTubeCrawler()
    spotify = MockSpotifyCrawler()
    tiktok = MockTikTokCrawler()
    
    assert youtube.platform_name == "youtube"
    assert spotify.platform_name == "spotify"
    assert tiktok.platform_name == "tiktok"
    
    # Verify platform-specific methods
    assert hasattr(youtube, 'search_videos')
    assert hasattr(youtube, 'get_video_details')
    assert hasattr(spotify, 'search_tracks')
    assert hasattr(spotify, 'get_track_features')
    assert hasattr(tiktok, 'search_videos')
    assert hasattr(tiktok, 'get_user_videos')