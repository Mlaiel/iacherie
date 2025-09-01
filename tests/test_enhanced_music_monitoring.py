"""Tests for Enhanced Music Platform Copyright Monitoring

Tests the implementation of advanced copyright monitoring across music platforms
as specified in the requirements:
- Spotify: Web API + track monitoring 
- Apple Music: MusicKit + catalog search
- SoundCloud: API + track discovery
- Bandcamp: Web scraping + release tracking  
- Deezer: API + playlist monitoring
- Amazon Music: API + content tracking
- YouTube Music: Specialized copyright monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protection.rights_tracking.usage_monitor import (
    PlatformMonitor, UsageEvent, UsageType, PlatformType,
    _scan_spotify_api, _scan_apple_music_api, _scan_soundcloud_api,
    _scan_deezer_api, _scan_amazon_music_api, _scan_bandcamp_api,
    _scan_youtube_api
)


class TestEnhancedMusicMonitoring:
    """
Test suite for enhanced music platform monitoring"""
    
    @pytest.fixture
    def sample_platform_monitor(self):
        """
Create a sample platform monitor for testing"""
        return PlatformMonitor(
            platform_id="spotify",
            platform_name="Spotify",
            platform_type=PlatformType.STREAMING,
            api_endpoint="https://api.spotify.com/v1",
            api_key="test_key",
            api_secret="test_secret",
            rate_limit_requests_per_minute=100,
            enabled=True
        )
    
    @pytest.fixture  
    def sample_content_id(self):
        """Sample content ID for testing"""
        return "test_track_12345"

    @pytest.mark.asyncio
    async def test_spotify_web_api_monitoring(self, sample_platform_monitor, sample_content_id):
        """Test Spotify Web API + track monitoring functionality"""
        
        # Mock the Spotify crawler to avoid actual API calls
        mock_track = MagicMock()
        mock_track.track_id = "spotify_track_123"
        mock_track.external_urls = {"spotify": "https://open.spotify.com/track/123"}
        mock_track.artists = [{"name": "Test Artist"}]
        mock_track.album = {"name": "Test Album"}
        mock_track.duration_ms = 180000
        mock_track.popularity = 75
        
        with patch('protection.rights_tracking.usage_monitor.SpotifyCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.search_tracks.return_value = [mock_track]
            mock_crawler_class.return_value = mock_crawler
            
            # Test the Spotify API scanning
            events = await _scan_spotify_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "spotify"
            assert events[0].usage_type == UsageType.STREAM
            assert events[0].confidence_score == 0.85
            assert "spotify_web_api" in events[0].metadata["detection_method"]
            assert events[0].metadata["spotify_track_id"] == "spotify_track_123"

    @pytest.mark.asyncio
    async def test_apple_music_musickit_monitoring(self, sample_platform_monitor, sample_content_id):
        """Test Apple Music MusicKit + catalog search functionality"""
        
        sample_platform_monitor.platform_id = "apple_music"
        
        # Mock Apple Music MusicKit engine
        mock_search_result = {
            "type": "songs",
            "id": "apple_song_456", 
            "attributes": {
                "name": "Test Song",
                "artistName": "Test Artist",
                "albumName": "Test Album",
                "isrc": "TEST123456789",
                "url": "https://music.apple.com/song/456"
            }
        }
        
        with patch('protection.rights_tracking.usage_monitor.MusicKitEngine') as mock_engine_class:
            mock_engine = AsyncMock()
            mock_engine.search_catalog.return_value = [mock_search_result]
            mock_engine_class.return_value = mock_engine
            
            # Test Apple Music MusicKit scanning
            events = await _scan_apple_music_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "apple_music"
            assert events[0].confidence_score == 0.88
            assert "apple_musickit_catalog" in events[0].metadata["detection_method"]
            assert events[0].metadata["apple_music_id"] == "apple_song_456"
            assert events[0].metadata["isrc"] == "TEST123456789"

    @pytest.mark.asyncio
    async def test_youtube_music_copyright_monitoring(self, sample_platform_monitor, sample_content_id):
        """Test YouTube Music specialized copyright monitoring"""
        
        sample_platform_monitor.platform_id = "youtube"
        
        # Mock YouTube copyright detection
        mock_detection = MagicMock()
        mock_detection.detected_content = "youtube_video_1234"
        mock_detection.confidence_score = 0.92
        mock_detection.copyright_owner = "Test Music Label"
        mock_detection.match_duration = 45.0
        
        with patch('protection.rights_tracking.usage_monitor.CopyrightMonitor') as mock_monitor_class:
            mock_monitor = AsyncMock()
            mock_monitor.monitor_content.return_value = [mock_detection]
            mock_monitor_class.return_value = mock_monitor
            
            # Test YouTube copyright monitoring
            events = await _scan_youtube_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "youtube"
            assert events[0].confidence_score == 0.92
            assert "youtube_copyright_monitor" in events[0].metadata["detection_method"]
            assert events[0].metadata["copyright_owner"] == "Test Music Label"
            assert events[0].metadata["match_duration"] == 45.0

    @pytest.mark.asyncio
    async def test_soundcloud_api_discovery(self, sample_platform_monitor, sample_content_id):
        """Test SoundCloud API + track discovery functionality"""
        
        sample_platform_monitor.platform_id = "soundcloud"
        
        # Mock SoundCloud track discovery
        mock_track = {
            "id": "soundcloud_123",
            "title": "Test Track",
            "permalink_url": "https://soundcloud.com/user/test-track",
            "playback_count": 1500,
            "duration": 240000,
            "user": {"username": "test_user"}
        }
        
        with patch('protection.rights_tracking.usage_monitor.SoundCloudCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.search_tracks.return_value = [mock_track]
            mock_crawler_class.return_value = mock_crawler
            
            # Test SoundCloud API discovery
            events = await _scan_soundcloud_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "soundcloud"
            assert events[0].usage_type == UsageType.STREAM
            assert events[0].confidence_score == 0.80
            assert "soundcloud_api_discovery" in events[0].metadata["detection_method"]
            assert events[0].view_count == 1500

    @pytest.mark.asyncio
    async def test_deezer_playlist_monitoring(self, sample_platform_monitor, sample_content_id):
        """Test Deezer API + playlist monitoring functionality"""
        
        sample_platform_monitor.platform_id = "deezer"
        
        # Mock Deezer track and chart data
        mock_track_data = {"id": "deezer_789", "title": "Test Deezer Track"}
        mock_track = MagicMock()
        mock_track.track_id = "deezer_789"
        mock_track.track_url = "https://deezer.com/track/789"
        mock_track.artist_name = "Test Artist"
        mock_track.album_title = "Test Album"
        mock_track.isrc = "TEST987654321"
        mock_track.duration = 200
        mock_track.rank = 85
        
        mock_chart_track = {
            "link": "https://deezer.com/chart/456",
            "rank": 10,
            "position": 5,
            "title": "test track",
            "artist": {"name": "test artist"}
        }
        
        with patch('protection.rights_tracking.usage_monitor.DeezerCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.search_tracks.return_value = [mock_track_data]
            mock_crawler._parse_track_data.return_value = mock_track
            mock_crawler.get_charts.return_value = [mock_chart_track]
            mock_crawler_class.return_value = mock_crawler
            
            with patch('protection.rights_tracking.usage_monitor._check_content_similarity') as mock_similarity:
                mock_similarity.return_value = True
                
                # Test Deezer playlist monitoring
                events = await _scan_deezer_api(sample_platform_monitor, sample_content_id)
                
                # Assertions
                assert len(events) >= 1  # At least one from tracks, possibly one from charts
                track_event = events[0]
                assert track_event.platform_id == "deezer"
                assert track_event.confidence_score == 0.82
                assert "deezer_api_playlist_monitoring" in track_event.metadata["detection_method"]

    @pytest.mark.asyncio
    async def test_amazon_music_content_tracking(self, sample_platform_monitor, sample_content_id):
        """Test Amazon Music API + content tracking functionality"""
        
        sample_platform_monitor.platform_id = "amazon_music"
        
        # Mock Amazon Music track data
        mock_track = {
            "asin": "B08ABC123",
            "title": "Test Amazon Track",
            "artist": "Test Artist",
            "album": "Test Album",
            "quality": "HD",
            "regions": ["US", "CA", "UK"],
            "url": "https://music.amazon.com/albums/B08ABC123"
        }
        
        with patch('protection.rights_tracking.usage_monitor.AmazonMusicCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.search_tracks.return_value = [mock_track]
            mock_crawler_class.return_value = mock_crawler
            
            # Test Amazon Music content tracking
            events = await _scan_amazon_music_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "amazon_music"
            assert events[0].confidence_score == 0.85
            assert "amazon_music_api_tracking" in events[0].metadata["detection_method"]
            assert events[0].metadata["amazon_asin"] == "B08ABC123"
            assert events[0].metadata["audio_quality"] == "HD"

    @pytest.mark.asyncio  
    async def test_bandcamp_release_tracking(self, sample_platform_monitor, sample_content_id):
        """Test Bandcamp web scraping + release tracking functionality"""
        
        sample_platform_monitor.platform_id = "bandcamp"
        
        # Mock Bandcamp album and track data
        mock_album = MagicMock()
        mock_album.title = "Test Album"
        mock_album.artist = "Independent Artist"
        mock_album.release_date = datetime.now()
        
        mock_track = MagicMock()
        mock_track.track_id = "bandcamp_track_001"
        mock_track.track_url = "https://artist.bandcamp.com/track/test-track"
        mock_album.tracks = [mock_track]
        
        mock_search_result = {
            "type": "album",
            "url": "https://artist.bandcamp.com/album/test-album",
            "title": "Test Album",
            "artist": "Independent Artist"
        }
        
        with patch('protection.rights_tracking.usage_monitor.BandcampCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.search_music.return_value = [mock_search_result]
            mock_crawler.get_album_details.return_value = mock_album
            mock_crawler_class.return_value = mock_crawler
            
            # Test Bandcamp release tracking
            events = await _scan_bandcamp_api(sample_platform_monitor, sample_content_id)
            
            # Assertions
            assert len(events) == 1
            assert events[0].platform_id == "bandcamp"
            assert events[0].usage_type == UsageType.DOWNLOAD  # Bandcamp focuses on downloads
            assert events[0].confidence_score == 0.80
            assert "bandcamp_scraping_release_tracking" in events[0].metadata["detection_method"]

    def test_platform_support_completeness(self):
        """Test that all required platforms are supported"""
        
        # Verify all required monitoring functions exist
        required_platforms = [
            "youtube", "spotify", "soundcloud", "apple_music", 
            "deezer", "amazon_music", "bandcamp"
        ]
        
        # This test ensures all platforms from the requirements are implemented
        assert len(required_platforms) == 7
        
        # Test that the function names follow the expected pattern
        expected_functions = [
            _scan_youtube_api, _scan_spotify_api, _scan_soundcloud_api,
            _scan_apple_music_api, _scan_deezer_api, _scan_amazon_music_api,
            _scan_bandcamp_api
        ]
        
        for func in expected_functions:
            assert callable(func)
            assert asyncio.iscoroutinefunction(func)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])