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

"""Unit tests for YouTube Crawler
Tests for YouTube content surveillance and monitoring functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

from crawlers.youtube_crawler import YouTubeVideoData, YouTubeMonitoringResult


class TestYouTubeCrawler:
    """Test suite for YouTube crawler functionality"""
    
    @pytest.fixture
    def sample_video_data(self):
        """Sample YouTube video data for testing"""
        return YouTubeVideoData(
            video_id="dQw4w9WgXcQ",
            title="Test Video Title",
            description="Test video description",
            channel_id="UC123456789",
            channel_title="Test Channel",
            published_at=datetime.now() - timedelta(days=1),
            view_count=1000000,
            like_count=50000,
            duration="PT3M33S",
            thumbnail_url="https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            tags=["music", "test", "video"],
            category_id="10",
            language="en",
            similarity_score=0.95
        )
    
    @pytest.fixture
    def sample_api_response(self):
        """Sample YouTube API response for testing"""
        return {
            "items": [
                {
                    "id": {"videoId": "dQw4w9WgXcQ"},
                    "snippet": {
                        "title": "Test Video Title",
                        "description": "Test video description",
                        "channelId": "UC123456789",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2025-01-01T12:00:00Z",
                        "thumbnails": {
                            "default": {"url": "https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg"}
                        },
                        "tags": ["music", "test", "video"],
                        "categoryId": "10",
                        "defaultLanguage": "en"
                    },
                    "statistics": {
                        "viewCount": "1000000",
                        "likeCount": "50000"
                    },
                    "contentDetails": {
                        "duration": "PT3M33S"
                    }
                }
            ],
            "pageInfo": {
                "totalResults": 1
            }
        }
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_youtube_video_data_structure(self, sample_video_data):
        """Test YouTubeVideoData dataclass structure"""
        assert sample_video_data.video_id == "dQw4w9WgXcQ"
        assert sample_video_data.title == "Test Video Title"
        assert sample_video_data.channel_id == "UC123456789"
        assert sample_video_data.view_count == 1000000
        assert sample_video_data.like_count == 50000
        assert sample_video_data.similarity_score == 0.95
        assert len(sample_video_data.tags) == 3
        assert "music" in sample_video_data.tags
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_youtube_video_data_defaults(self):
        """Test YouTubeVideoData default values"""
        video_data = YouTubeVideoData(
            video_id="test_id",
            title="Test Title",
            description="Test Description",
            channel_id="test_channel",
            channel_title="Test Channel",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test_url",
            video_url="test_video_url",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.similarity_score == 0.0  # Default value
        assert video_data.detected_segments is None  # Default value
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_youtube_monitoring_result_structure(self, sample_video_data):
        """Test YouTubeMonitoringResult dataclass structure"""
        result = YouTubeMonitoringResult(
            original_content_id="content_123",
            search_query="test query",
            total_results=5,
            potential_violations=[sample_video_data]
        )
        
        assert result.original_content_id == "content_123"
        assert result.search_query == "test query"
        assert result.total_results == 5
        assert len(result.potential_violations) == 1
        assert result.potential_violations[0].video_id == "dQw4w9WgXcQ"
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_youtube_video_url_generation(self, sample_video_data):
        """Test YouTube video URL generation"""
        expected_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert sample_video_data.video_url == expected_url
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_youtube_thumbnail_url_generation(self, sample_video_data):
        """Test YouTube thumbnail URL generation"""
        expected_thumbnail = "https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg"
        assert sample_video_data.thumbnail_url == expected_thumbnail
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_duration_parsing(self):
        """Test YouTube duration format parsing"""
        # PT3M33S = 3 minutes 33 seconds
        duration = "PT3M33S"
        
        # Test that duration is stored correctly
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration=duration,
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.duration == "PT3M33S"
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_large_numbers_handling(self):
        """Test handling of large view/like counts"""
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test", 
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=1_000_000_000,  # 1 billion views
            like_count=50_000_000,     # 50 million likes
            duration="PT1H",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.view_count == 1_000_000_000
        assert video_data.like_count == 50_000_000
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_video_data_serialization(self, sample_video_data):
        """Test YouTubeVideoData serialization to dict"""
        data_dict = sample_video_data.__dict__
        
        assert "video_id" in data_dict
        assert "title" in data_dict
        assert "view_count" in data_dict
        assert data_dict["video_id"] == "dQw4w9WgXcQ"
        assert isinstance(data_dict["view_count"], int)
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_similarity_score_range(self):
        """Test similarity score is within valid range"""
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test", 
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en",
            similarity_score=0.95
        )
        
        assert 0.0 <= video_data.similarity_score <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_invalid_similarity_score(self):
        """Test handling of invalid similarity scores"""
        # Test that we can create video data with invalid scores
        # (validation would happen in the crawler logic)
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test", 
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en",
            similarity_score=1.5  # Invalid score > 1.0
        )
        
        assert video_data.similarity_score == 1.5
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_empty_tags_handling(self):
        """Test handling of empty tags list"""
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],  # Empty tags
            category_id="1",
            language="en"
        )
        
        assert video_data.tags == []
        assert len(video_data.tags) == 0
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_long_description_handling(self):
        """Test handling of very long video descriptions"""
        long_description = "A" * 10000  # 10,000 character description
        
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description=long_description,
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert len(video_data.description) == 10000
        assert video_data.description == long_description
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_unicode_title_handling(self):
        """Test handling of Unicode characters in titles"""
        unicode_title = "测试视频 🎵 مقطع فيديو 🎬 Тест 🎥"
        
        video_data = YouTubeVideoData(
            video_id="test",
            title=unicode_title,
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.title == unicode_title
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_date_handling(self):
        """Test datetime handling in video data"""
        test_date = datetime(2025, 1, 15, 12, 30, 45)
        
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=test_date,
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.published_at == test_date
        assert video_data.published_at.year == 2025
        assert video_data.published_at.month == 1
        assert video_data.published_at.day == 15
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_detected_segments_structure(self):
        """Test detected segments data structure"""
        segments = [
            {
                "start_time": 10.5,
                "end_time": 25.3,
                "similarity": 0.92,
                "type": "audio_match"
            },
            {
                "start_time": 45.0,
                "end_time": 60.0,
                "similarity": 0.88,
                "type": "visual_match"
            }
        ]
        
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=100,
            like_count=10,
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en",
            detected_segments=segments
        )
        
        assert video_data.detected_segments == segments
        assert len(video_data.detected_segments) == 2
        assert video_data.detected_segments[0]["similarity"] == 0.92
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_multiple_violations_in_result(self, sample_video_data):
        """Test monitoring result with multiple potential violations"""
        # Create multiple video data instances
        violations = [sample_video_data]
        
        for i in range(4):  # Add 4 more violations
            violation = YouTubeVideoData(
                video_id=f"violation_{i}",
                title=f"Violation Video {i}",
                description="Potential violation",
                channel_id=f"channel_{i}",
                channel_title=f"Channel {i}",
                published_at=datetime.now() - timedelta(days=i+1),
                view_count=10000 * (i+1),
                like_count=500 * (i+1),
                duration="PT2M",
                thumbnail_url=f"thumbnail_{i}",
                video_url=f"video_url_{i}",
                tags=["violation", "test"],
                category_id="1",
                language="en",
                similarity_score=0.85 + (i * 0.02)
            )
            violations.append(violation)
        
        result = YouTubeMonitoringResult(
            original_content_id="content_123",
            search_query="test content monitoring",
            total_results=5,
            potential_violations=violations
        )
        
        assert len(result.potential_violations) == 5
        assert result.total_results == 5
        
        # Check that violations are sorted by similarity (if implemented)
        for violation in result.potential_violations:
            assert violation.similarity_score >= 0.85
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_zero_engagement_handling(self):
        """Test handling of videos with zero views/likes"""
        video_data = YouTubeVideoData(
            video_id="test",
            title="Test",
            description="Test",
            channel_id="test",
            channel_title="Test",
            published_at=datetime.now(),
            view_count=0,  # Zero views
            like_count=0,  # Zero likes
            duration="PT1M",
            thumbnail_url="test",
            video_url="test",
            tags=[],
            category_id="1",
            language="en"
        )
        
        assert video_data.view_count == 0
        assert video_data.like_count == 0
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_category_id_validation(self):
        """Test category ID handling"""
        valid_categories = ["1", "2", "10", "15", "17", "19", "20", "22", "23", "24", "25", "26", "27", "28"]
        
        for category in valid_categories:
            video_data = YouTubeVideoData(
                video_id="test",
                title="Test",
                description="Test",
                channel_id="test",
                channel_title="Test",
                published_at=datetime.now(),
                view_count=100,
                like_count=10,
                duration="PT1M",
                thumbnail_url="test",
                video_url="test",
                tags=[],
                category_id=category,
                language="en"
            )
            
            assert video_data.category_id == category
    
    @pytest.mark.unit
    @pytest.mark.crawlers
    def test_language_code_handling(self):
        """Test language code handling"""
        language_codes = ["en", "es", "fr", "de", "ja", "ko", "zh", "ar", "hi", "pt"]
        
        for lang_code in language_codes:
            video_data = YouTubeVideoData(
                video_id="test",
                title="Test",
                description="Test",
                channel_id="test",
                channel_title="Test",
                published_at=datetime.now(),
                view_count=100,
                like_count=10,
                duration="PT1M",
                thumbnail_url="test",
                video_url="test",
                tags=[],
                category_id="1",
                language=lang_code
            )
            
            assert video_data.language == lang_code