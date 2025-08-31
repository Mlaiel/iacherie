# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Unit tests for crawler engines and platform integrations.

Comprehensive tests for Spotify, YouTube, Instagram, and other
platform crawlers with focus on rate limiting, data extraction,
and error handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

# Mock aiohttp if not available
try:
    import aiohttp
except ImportError:
    aiohttp = MagicMock()

# Import modules under test
try:
    from crawlers.platforms.spotify_crawler import SpotifyCrawler, SpotifyTrack, SpotifyArtist
    from crawlers.platforms.youtube_crawler import YouTubeCrawler, YouTubeVideo
    from crawlers.platforms.instagram_crawler import InstagramCrawler, InstagramPost
    from crawlers.utils.rate_limiter import RateLimiter
    from crawlers.utils.proxy_manager import ProxyManager
    from crawlers.base_crawler import BaseCrawler, CrawlResult
except ImportError as e:
    pytest.skip(f"Crawler modules not available: {e}", allow_module_level=True)


class TestSpotifyCrawler:
    """Test suite for Spotify crawler functionality."""    
    @pytest.fixture
    def spotify_crawler(self):
        """Create Spotify crawler instance."""        config = {
            'client_id': 'test_spotify_client_id',
            'client_secret': 'test_spotify_client_secret',
            'rate_limit': 100,  # requests per minute
            'retry_attempts': 3,
            'timeout': 30
        }
        return SpotifyCrawler(config)
    
    @pytest.fixture
    def mock_spotify_api_response(self):
        """Mock Spotify API response data."""        return {
            'tracks': {
                'items': [
                    {
                        'id': 'track123',
                        'name': 'Test Song',
                        'artists': [{'id': 'artist123', 'name': 'Test Artist'}],
                        'album': {
                            'id': 'album123',
                            'name': 'Test Album',
                            'release_date': '2023-01-01'
                        },
                        'duration_ms': 180000,
                        'popularity': 75,
                        'external_urls': {'spotify': 'https://open.spotify.com/track/track123'}
                    }
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_search_tracks(self, spotify_crawler, mock_spotify_api_response):
        """Test searching for tracks on Spotify."""        with patch.object(spotify_crawler, '_make_api_request') as mock_request:
            mock_request.return_value = mock_spotify_api_response
            
            results = await spotify_crawler.search_tracks('test query', limit=10)
            
            assert len(results) == 1
            assert results[0].track_id == 'track123'
            assert results[0].name == 'Test Song'
            assert results[0].artists[0]['name'] == 'Test Artist'
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_track_details(self, spotify_crawler):
        """Test getting detailed track information."""        track_id = 'track123'
        mock_track_data = {
            'id': track_id,
            'name': 'Detailed Track',
            'artists': [{'id': 'artist456', 'name': 'Detailed Artist'}],
            'album': {'id': 'album456', 'name': 'Detailed Album'},
            'duration_ms': 240000,
            'popularity': 85,
            'audio_features': {
                'danceability': 0.8,
                'energy': 0.9,
                'valence': 0.7
            }
        }
        
        with patch.object(spotify_crawler, '_make_api_request') as mock_request:
            mock_request.return_value = mock_track_data
            
            track = await spotify_crawler.get_track_details(track_id)
            
            assert track.track_id == track_id
            assert track.name == 'Detailed Track'
            assert track.duration_ms == 240000
    
    @pytest.mark.asyncio
    async def test_get_artist_albums(self, spotify_crawler):
        """Test getting albums for an artist."""        artist_id = 'artist123'
        mock_albums_response = {
            'items': [
                {
                    'id': 'album1',
                    'name': 'Album One',
                    'release_date': '2023-01-01',
                    'total_tracks': 12
                },
                {
                    'id': 'album2',
                    'name': 'Album Two',
                    'release_date': '2023-06-01',
                    'total_tracks': 8
                }
            ]
        }
        
        with patch.object(spotify_crawler, '_make_api_request') as mock_request:
            mock_request.return_value = mock_albums_response
            
            albums = await spotify_crawler.get_artist_albums(artist_id)
            
            assert len(albums) == 2
            assert albums[0]['name'] == 'Album One'
            assert albums[1]['total_tracks'] == 8
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, spotify_crawler):
        """Test rate limiting functionality."""        with patch.object(spotify_crawler.rate_limiter, 'acquire') as mock_acquire:
            mock_acquire.return_value = AsyncMock()
            
            with patch.object(spotify_crawler, '_make_api_request') as mock_request:
                mock_request.return_value = {'tracks': {'items': []}}
                
                # Make multiple requests
                tasks = [spotify_crawler.search_tracks('test') for _ in range(5)]
                await asyncio.gather(*tasks)
                
                # Rate limiter should be called for each request
                assert mock_acquire.call_count == 5
    
    @pytest.mark.asyncio
    async def test_error_handling(self, spotify_crawler):
        """Test error handling for API failures."""        with patch.object(spotify_crawler, '_make_api_request') as mock_request:
            mock_request.side_effect = aiohttp.ClientError("API Error")
            
            with pytest.raises(Exception):
                await spotify_crawler.search_tracks('test query')
    
    @pytest.mark.asyncio
    async def test_batch_track_processing(self, spotify_crawler):
        """Test batch processing of multiple tracks."""        track_ids = ['track1', 'track2', 'track3', 'track4', 'track5']
        
        with patch.object(spotify_crawler, 'get_track_details') as mock_details:
            mock_details.side_effect = [
                Mock(track_id=tid, name=f'Track {tid}') for tid in track_ids
            ]
            
            results = await spotify_crawler.get_tracks_batch(track_ids)
            
            assert len(results) == 5
            assert all(result.track_id in track_ids for result in results)


class TestYouTubeCrawler:
    """Test suite for YouTube crawler functionality."""    
    @pytest.fixture
    def youtube_crawler(self):
        """Create YouTube crawler instance."""        config = {
            'api_key': 'test_youtube_api_key',
            'rate_limit': 10000,  # requests per day
            'quota_limit': 1000000,  # quota units per day
            'enable_scraping': True
        }
        return YouTubeCrawler(config)
    
    @pytest.fixture
    def mock_youtube_api_response(self):
        """Mock YouTube API response data."""        return {
            'items': [
                {
                    'id': {'videoId': 'video123'},
                    'snippet': {
                        'title': 'Test Video',
                        'description': 'Test video description',
                        'channelTitle': 'Test Channel',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'thumbnails': {
                            'high': {'url': 'https://img.youtube.com/vi/video123/hqdefault.jpg'}
                        }
                    },
                    'statistics': {
                        'viewCount': '1000000',
                        'likeCount': '50000',
                        'commentCount': '5000'
                    }
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_search_videos(self, youtube_crawler, mock_youtube_api_response):
        """Test searching for videos on YouTube."""        with patch.object(youtube_crawler, '_make_api_request') as mock_request:
            mock_request.return_value = mock_youtube_api_response
            
            results = await youtube_crawler.search_videos('test query', max_results=10)
            
            assert len(results) == 1
            assert results[0].video_id == 'video123'
            assert results[0].title == 'Test Video'
            assert results[0].channel_title == 'Test Channel'
            assert results[0].view_count == 1000000
    
    @pytest.mark.asyncio
    async def test_get_video_details(self, youtube_crawler):
        """Test getting detailed video information."""        video_id = 'video123'
        mock_video_data = {
            'items': [
                {
                    'id': video_id,
                    'snippet': {
                        'title': 'Detailed Video',
                        'description': 'Detailed description',
                        'channelId': 'channel123',
                        'tags': ['tag1', 'tag2', 'tag3']
                    },
                    'contentDetails': {
                        'duration': 'PT3M45S',
                        'definition': 'hd'
                    },
                    'statistics': {
                        'viewCount': '2000000',
                        'likeCount': '100000'
                    }
                }
            ]
        }
        
        with patch.object(youtube_crawler, '_make_api_request') as mock_request:
            mock_request.return_value = mock_video_data
            
            video = await youtube_crawler.get_video_details(video_id)
            
            assert video.video_id == video_id
            assert video.title == 'Detailed Video'
            assert video.duration == 'PT3M45S'
            assert 'tag1' in video.tags
    
    @pytest.mark.asyncio
    async def test_get_channel_videos(self, youtube_crawler):
        """Test getting videos from a specific channel."""        channel_id = 'channel123'
        
        with patch.object(youtube_crawler, 'search_videos') as mock_search:
            mock_search.return_value = [
                Mock(video_id='vid1', title='Video 1'),
                Mock(video_id='vid2', title='Video 2')
            ]
            
            videos = await youtube_crawler.get_channel_videos(channel_id, max_results=50)
            
            assert len(videos) == 2
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scraping_fallback(self, youtube_crawler):
        """Test scraping fallback when API is unavailable."""        with patch.object(youtube_crawler, '_make_api_request') as mock_api:
            mock_api.side_effect = Exception("API quota exceeded")
            
            with patch.object(youtube_crawler, '_scrape_search_results') as mock_scrape:
                mock_scrape.return_value = [
                    Mock(video_id='scraped1', title='Scraped Video 1')
                ]
                
                results = await youtube_crawler.search_videos('test query')
                
                assert len(results) == 1
                assert results[0].video_id == 'scraped1'
                mock_scrape.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_quota_management(self, youtube_crawler):
        """Test API quota management."""        # Mock quota tracking
        youtube_crawler.daily_quota_used = 950000  # Close to limit
        youtube_crawler.quota_limit = 1000000
        
        with patch.object(youtube_crawler, '_check_quota_availability') as mock_quota:
            mock_quota.return_value = False  # Quota exceeded
            
            with patch.object(youtube_crawler, '_scrape_search_results') as mock_scrape:
                mock_scrape.return_value = []
                
                results = await youtube_crawler.search_videos('test query')
                
                # Should fallback to scraping
                mock_scrape.assert_called_once()


class TestInstagramCrawler:
    """Test suite for Instagram crawler functionality."""    
    @pytest.fixture
    def instagram_crawler(self):
        """Create Instagram crawler instance."""        config = {
            'access_token': 'test_instagram_token',
            'rate_limit': 200,  # requests per hour
            'enable_selenium': True,
            'headless': True
        }
        return InstagramCrawler(config)
    
    @pytest.mark.asyncio
    async def test_get_hashtag_posts(self, instagram_crawler):
        """Test getting posts for a hashtag."""        hashtag = 'testhashtag'
        mock_posts = [
            {
                'id': 'post1',
                'caption': 'Test post 1 #testhashtag',
                'media_type': 'IMAGE',
                'media_url': 'https://instagram.com/p/post1/media',
                'timestamp': '2023-01-01T00:00:00+0000'
            },
            {
                'id': 'post2',
                'caption': 'Test post 2 #testhashtag',
                'media_type': 'VIDEO',
                'media_url': 'https://instagram.com/p/post2/media',
                'timestamp': '2023-01-02T00:00:00+0000'
            }
        ]
        
        with patch.object(instagram_crawler, '_get_hashtag_posts_api') as mock_api:
            mock_api.return_value = mock_posts
            
            posts = await instagram_crawler.get_hashtag_posts(hashtag, limit=10)
            
            assert len(posts) == 2
            assert posts[0].post_id == 'post1'
            assert posts[1].media_type == 'VIDEO'
    
    @pytest.mark.asyncio
    async def test_get_user_posts(self, instagram_crawler):
        """Test getting posts from a specific user."""        username = 'testuser'
        
        with patch.object(instagram_crawler, '_selenium_get_user_posts') as mock_selenium:
            mock_selenium.return_value = [
                Mock(post_id='user_post1', caption='User post 1'),
                Mock(post_id='user_post2', caption='User post 2')
            ]
            
            posts = await instagram_crawler.get_user_posts(username, limit=20)
            
            assert len(posts) == 2
            mock_selenium.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_selenium_scraping(self, instagram_crawler):
        """Test Selenium-based scraping functionality."""        with patch('selenium.webdriver.Chrome') as mock_driver:
            mock_driver_instance = Mock()
            mock_driver.return_value = mock_driver_instance
            
            mock_driver_instance.get.return_value = None
            mock_driver_instance.find_elements.return_value = [
                Mock(get_attribute=Mock(return_value='https://instagram.com/p/test1/')),
                Mock(get_attribute=Mock(return_value='https://instagram.com/p/test2/'))
            ]
            
            with patch.object(instagram_crawler, '_extract_post_data') as mock_extract:
                mock_extract.side_effect = [
                    Mock(post_id='test1'),
                    Mock(post_id='test2')
                ]
                
                posts = await instagram_crawler._selenium_scrape_posts('https://instagram.com/explore/tags/test/')
                
                assert len(posts) == 2
                assert posts[0].post_id == 'test1'
    
    @pytest.mark.asyncio
    async def test_rate_limiting_compliance(self, instagram_crawler):
        """Test Instagram rate limiting compliance."""        with patch.object(instagram_crawler.rate_limiter, 'wait_if_needed') as mock_wait:
            mock_wait.return_value = AsyncMock()
            
            with patch.object(instagram_crawler, '_get_hashtag_posts_api') as mock_api:
                mock_api.return_value = []
                
                # Make multiple requests
                for _ in range(3):
                    await instagram_crawler.get_hashtag_posts('test')
                
                # Rate limiter should be respected
                assert mock_wait.call_count >= 3


class TestBaseCrawler:
    """Test suite for base crawler functionality."""    
    @pytest.fixture
    def base_crawler(self):
        """Create base crawler instance."""        config = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout': 30,
            'user_agent': 'AinflueCrawler/1.0'
        }
        return BaseCrawler(config)
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, base_crawler):
        """Test retry mechanism for failed requests."""        with patch.object(base_crawler, '_make_request') as mock_request:
            # First two calls fail, third succeeds
            mock_request.side_effect = [
                aiohttp.ClientError("Connection failed"),
                aiohttp.ClientError("Timeout"),
                Mock(status=200, json=AsyncMock(return_value={'success': True}))
            ]
            
            response = await base_crawler._make_request_with_retry('https://test.com')
            
            assert mock_request.call_count == 3
            assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_user_agent_rotation(self, base_crawler):
        """Test user agent rotation for stealth crawling."""        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        base_crawler.user_agents = user_agents
        
        selected_agents = []
        for _ in range(10):
            agent = base_crawler._get_random_user_agent()
            selected_agents.append(agent)
        
        # Should have variety in selected agents
        assert len(set(selected_agents)) > 1
        assert all(agent in user_agents for agent in selected_agents)
    
    def test_url_validation(self, base_crawler):
        """Test URL validation functionality."""        valid_urls = [
            'https://www.example.com',
            'http://test.com/path',
            'https://subdomain.example.com/path?param=value'
        ]
        
        invalid_urls = [
            'not-a-url',
            'ftp://invalid-protocol.com',
            'https://',
            ''
        ]
        
        for url in valid_urls:
            assert base_crawler._is_valid_url(url) is True
        
        for url in invalid_urls:
            assert base_crawler._is_valid_url(url) is False
    
    @pytest.mark.asyncio
    async def test_response_caching(self, base_crawler):
        """Test response caching functionality."""        url = 'https://api.example.com/data'
        
        with patch.object(base_crawler, '_make_request') as mock_request:
            mock_response = Mock(
                status=200,
                json=AsyncMock(return_value={'data': 'test'})
            )
            mock_request.return_value = mock_response
            
            # First request
            response1 = await base_crawler._cached_request(url, cache_ttl=300)
            
            # Second request should use cache
            response2 = await base_crawler._cached_request(url, cache_ttl=300)
            
            # Only one actual HTTP request should be made
            assert mock_request.call_count == 1
            assert response1 == response2


class TestRateLimiter:
    """Test suite for rate limiting functionality."""    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""        return RateLimiter(max_requests=10, time_window=60)
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, rate_limiter):
        """Test rate limit enforcement."""        # Make requests up to the limit
        for _ in range(10):
            can_proceed = await rate_limiter.acquire()
            assert can_proceed is True
        
        # Next request should be rate limited
        can_proceed = await rate_limiter.acquire()
        assert can_proceed is False
    
    @pytest.mark.asyncio
    async def test_time_window_reset(self, rate_limiter):
        """Test rate limit reset after time window."""        # Fill up the rate limit
        for _ in range(10):
            await rate_limiter.acquire()
        
        # Mock time advancement
        with patch('time.time') as mock_time:
            mock_time.return_value = rate_limiter.window_start + 61  # Beyond window
            
            # Should be able to make requests again
            can_proceed = await rate_limiter.acquire()
            assert can_proceed is True
    
    def test_burst_allowance(self, rate_limiter):
        """Test burst request allowance."""        # Configure burst allowance
        rate_limiter.burst_limit = 15
        
        # Should allow burst up to burst limit
        for _ in range(15):
            can_proceed = rate_limiter.try_acquire()
            assert can_proceed is True
        
        # Beyond burst limit should be denied
        can_proceed = rate_limiter.try_acquire()
        assert can_proceed is False


class TestProxyManager:
    """Test suite for proxy management functionality."""    
    @pytest.fixture
    def proxy_manager(self):
        """Create proxy manager instance."""        proxies = [
            {'host': 'proxy1.com', 'port': 8080, 'protocol': 'http'},
            {'host': 'proxy2.com', 'port': 8080, 'protocol': 'https'},
            {'host': 'proxy3.com', 'port': 3128, 'protocol': 'http'}
        ]
        return ProxyManager(proxies)
    
    def test_proxy_rotation(self, proxy_manager):
        """Test proxy rotation functionality."""        proxies_used = []
        
        for _ in range(6):  # More than number of proxies
            proxy = proxy_manager.get_next_proxy()
            proxies_used.append(proxy)
        
        # Should cycle through proxies
        assert len(set(p['host'] for p in proxies_used)) == 3
    
    @pytest.mark.asyncio
    async def test_proxy_health_check(self, proxy_manager):
        """Test proxy health checking."""        with patch.object(proxy_manager, '_test_proxy_connection') as mock_test:
            mock_test.side_effect = [True, False, True]  # proxy1 ok, proxy2 failed, proxy3 ok
            
            healthy_proxies = await proxy_manager.check_proxy_health()
            
            assert len(healthy_proxies) == 2
            assert healthy_proxies[0]['host'] == 'proxy1.com'
            assert healthy_proxies[1]['host'] == 'proxy3.com'
    
    def test_proxy_failure_handling(self, proxy_manager):
        """Test handling of proxy failures."""        # Mark a proxy as failed
        proxy_manager.mark_proxy_failed('proxy2.com')
        
        # Get next proxy should skip the failed one
        proxy = proxy_manager.get_next_proxy()
        assert proxy['host'] != 'proxy2.com'
        
        # Failed proxy should be retried after cooldown
        with patch('time.time') as mock_time:
            mock_time.return_value = proxy_manager.failure_cooldown + 1
            
            proxy_manager.reset_failed_proxies()
            proxy = proxy_manager.get_proxy_by_host('proxy2.com')
            assert proxy is not None


# Integration tests
class TestCrawlerIntegration:
    """Integration tests for crawler system."""    
    @pytest.mark.asyncio
    async def test_multi_platform_content_discovery(self):
        """Test content discovery across multiple platforms."""        # This would test coordinated crawling across platforms
        pass
    
    @pytest.mark.asyncio
    async def test_content_deduplication(self):
        """Test deduplication of content found across platforms."""        # Test identifying same content on different platforms
        pass
    
    @pytest.mark.asyncio
    async def test_crawler_performance_under_load(self):
        """Test crawler performance under high load."""        # Performance testing for concurrent crawling
        pass


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])