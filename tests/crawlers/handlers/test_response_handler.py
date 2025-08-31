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

"""Test Response Handler Module

Tests for API response processing, validation, and normalization.

Author: Fahed Mlaiel (Legal Copyright)
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
Propriété intellectuelle protégée sous toutes juridictions.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime
from typing import Dict, Any

from crawlers.handlers.response_handler import (
    ResponseValidator,
    ResponseNormalizer,
    ResponseProcessor,
    PlatformResponse,
    YouTubeResponse,
    InstagramResponse,
    TikTokResponse,
    TwitterResponse,
    NormalizedResponse,
    ValidationResult,
    ResponseMetadata
)


class TestPlatformResponse:
    """Test suite for platform response models."""
    def test_youtube_response_creation(self):
        """Test YouTube response model."""        response = YouTubeResponse(
            video_id="abc123",
            title="Test Video",
            description="Test Description",
            channel_id="channel123",
            channel_name="Test Channel",
            view_count=1000,
            like_count=50,
            comment_count=10,
            duration="PT5M30S",
            upload_date="2025-01-01T10:00:00Z",
            thumbnails={"default": "https://example.com/thumb.jpg"},
            tags=["test", "video"]
        )
        
        assert response.video_id == "abc123"
        assert response.title == "Test Video"
        assert response.view_count == 1000
        assert len(response.tags) == 2

    def test_instagram_response_creation(self):
        """Test Instagram response model."""        response = InstagramResponse(
            media_id="insta123",
            media_type="photo",
            caption="Test post",
            username="testuser",
            user_id="user123",
            like_count=100,
            comment_count=5,
            timestamp="2025-01-01T12:00:00Z",
            media_url="https://example.com/photo.jpg",
            hashtags=["test", "instagram"]
        )
        
        assert response.media_id == "insta123"
        assert response.media_type == "photo"
        assert response.like_count == 100
        assert len(response.hashtags) == 2

    def test_tiktok_response_creation(self):
        """Test TikTok response model."""        response = TikTokResponse(
            video_id="tiktok123",
            description="Test TikTok",
            username="tiktokuser",
            user_id="tuser123",
            view_count=5000,
            like_count=200,
            share_count=20,
            comment_count=15,
            create_time=1640995200,
            video_url="https://example.com/video.mp4",
            music_info={
                "title": "Test Song",
                "author": "Test Artist"
            },
            hashtags=["tiktok", "test"]
        )
        
        assert response.video_id == "tiktok123"
        assert response.view_count == 5000
        assert response.music_info["title"] == "Test Song"

    def test_twitter_response_creation(self):
        """Test Twitter response model."""        response = TwitterResponse(
            tweet_id="tweet123",
            text="Test tweet content",
            username="twitteruser",
            user_id="twuser123",
            retweet_count=10,
            like_count=25,
            reply_count=3,
            created_at="2025-01-01T15:00:00Z",
            hashtags=["twitter", "test"],
            mentions=["@testuser"],
            media=[{"type": "photo", "url": "https://example.com/image.jpg"}]
        )
        
        assert response.tweet_id == "tweet123"
        assert response.text == "Test tweet content"
        assert len(response.mentions) == 1
        assert len(response.media) == 1


class TestResponseValidator:
    """Test suite for ResponseValidator class."""
    def test_validator_initialization(self):
        """Test validator setup."""        validator = ResponseValidator()
        assert validator.schemas is not None
        assert len(validator.schemas) > 0

    def test_validate_youtube_response(self):
        """Test YouTube response validation."""        validator = ResponseValidator()
        
        valid_data = {
            "video_id": "abc123",
            "title": "Test Video",
            "description": "Test Description",
            "channel_id": "channel123",
            "channel_name": "Test Channel",
            "view_count": 1000,
            "like_count": 50,
            "comment_count": 10,
            "duration": "PT5M30S",
            "upload_date": "2025-01-01T10:00:00Z",
            "thumbnails": {"default": "https://example.com/thumb.jpg"},
            "tags": ["test", "video"]
        }
        
        result = validator.validate("youtube", valid_data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_youtube_response(self):
        """Test validation with invalid YouTube data."""        validator = ResponseValidator()
        
        invalid_data = {
            "video_id": "",  # Invalid empty ID
            "title": "Test Video",
            "view_count": "not_a_number",  # Invalid type
            "upload_date": "invalid_date"  # Invalid date format
        }
        
        result = validator.validate("youtube", invalid_data)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_instagram_response(self):
        """Test Instagram response validation."""        validator = ResponseValidator()
        
        valid_data = {
            "media_id": "insta123",
            "media_type": "photo",
            "caption": "Test post",
            "username": "testuser",
            "user_id": "user123",
            "like_count": 100,
            "comment_count": 5,
            "timestamp": "2025-01-01T12:00:00Z",
            "media_url": "https://example.com/photo.jpg",
            "hashtags": ["test", "instagram"]
        }
        
        result = validator.validate("instagram", valid_data)
        assert result.is_valid

    def test_validate_unsupported_platform(self):
        """Test validation with unsupported platform."""        validator = ResponseValidator()
        
        result = validator.validate("unknown_platform", {})
        assert not result.is_valid
        assert "Unsupported platform" in str(result.errors)

    def test_validate_required_fields(self):
        """Test validation of required fields."""        validator = ResponseValidator()
        
        # Missing required fields
        incomplete_data = {
            "title": "Test Video"
            # Missing video_id, channel_id, etc.
        }
        
        result = validator.validate("youtube", incomplete_data)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_field_types(self):
        """Test validation of field types."""        validator = ResponseValidator()
        
        wrong_types_data = {
            "video_id": 123,  # Should be string
            "title": ["not", "a", "string"],  # Should be string
            "view_count": "not_a_number",  # Should be integer
            "tags": "not_a_list"  # Should be list
        }
        
        result = validator.validate("youtube", wrong_types_data)
        assert not result.is_valid


class TestResponseNormalizer:
    """Test suite for ResponseNormalizer class."""
    def test_normalizer_initialization(self):
        """Test normalizer setup."""        normalizer = ResponseNormalizer()
        assert hasattr(normalizer, 'field_mappings')
        assert 'youtube' in normalizer.field_mappings

    def test_normalize_youtube_response(self):
        """Test YouTube response normalization."""        normalizer = ResponseNormalizer()
        
        youtube_data = YouTubeResponse(
            video_id="abc123",
            title="Test Video",
            description="Test Description",
            channel_id="channel123",
            channel_name="Test Channel",
            view_count=1000,
            like_count=50,
            comment_count=10,
            duration="PT5M30S",
            upload_date="2025-01-01T10:00:00Z",
            thumbnails={"default": "https://example.com/thumb.jpg"},
            tags=["test", "video"]
        )
        
        normalized = normalizer.normalize("youtube", youtube_data)
        
        assert isinstance(normalized, NormalizedResponse)
        assert normalized.platform == "youtube"
        assert normalized.content_id == "abc123"
        assert normalized.title == "Test Video"
        assert normalized.author_name == "Test Channel"
        assert normalized.engagement.views == 1000
        assert normalized.engagement.likes == 50

    def test_normalize_instagram_response(self):
        """Test Instagram response normalization."""        normalizer = ResponseNormalizer()
        
        instagram_data = InstagramResponse(
            media_id="insta123",
            media_type="photo",
            caption="Test post",
            username="testuser",
            user_id="user123",
            like_count=100,
            comment_count=5,
            timestamp="2025-01-01T12:00:00Z",
            media_url="https://example.com/photo.jpg",
            hashtags=["test", "instagram"]
        )
        
        normalized = normalizer.normalize("instagram", instagram_data)
        
        assert normalized.platform == "instagram"
        assert normalized.content_id == "insta123"
        assert normalized.author_name == "testuser"
        assert normalized.engagement.likes == 100
        assert normalized.content_type == "photo"

    def test_normalize_tiktok_response(self):
        """Test TikTok response normalization."""        normalizer = ResponseNormalizer()
        
        tiktok_data = TikTokResponse(
            video_id="tiktok123",
            description="Test TikTok",
            username="tiktokuser",
            user_id="tuser123",
            view_count=5000,
            like_count=200,
            share_count=20,
            comment_count=15,
            create_time=1640995200,
            video_url="https://example.com/video.mp4",
            music_info={"title": "Test Song", "author": "Test Artist"},
            hashtags=["tiktok", "test"]
        )
        
        normalized = normalizer.normalize("tiktok", tiktok_data)
        
        assert normalized.platform == "tiktok"
        assert normalized.content_id == "tiktok123"
        assert normalized.engagement.views == 5000
        assert normalized.engagement.shares == 20

    def test_extract_hashtags(self):
        """Test hashtag extraction and normalization."""        normalizer = ResponseNormalizer()
        
        # Test with text containing hashtags
        text = "This is a test post #testing #social #media"
        hashtags = normalizer._extract_hashtags(text)
        
        assert "testing" in hashtags
        assert "social" in hashtags
        assert "media" in hashtags

    def test_parse_duration(self):
        """Test duration parsing."""        normalizer = ResponseNormalizer()
        
        # YouTube ISO 8601 duration
        duration_seconds = normalizer._parse_duration("PT5M30S")
        assert duration_seconds == 330  # 5*60 + 30

        # Simple seconds
        duration_seconds = normalizer._parse_duration("120")
        assert duration_seconds == 120

    def test_normalize_timestamp(self):
        """Test timestamp normalization."""        normalizer = ResponseNormalizer()
        
        # ISO 8601 format
        timestamp = normalizer._normalize_timestamp("2025-01-01T10:00:00Z")
        assert isinstance(timestamp, datetime)
        
        # Unix timestamp
        timestamp = normalizer._normalize_timestamp(1640995200)
        assert isinstance(timestamp, datetime)


class TestResponseProcessor:
    """Test suite for ResponseProcessor class."""
    def test_processor_initialization(self):
        """Test processor setup."""        processor = ResponseProcessor()
        assert processor.validator is not None
        assert processor.normalizer is not None

    @pytest.mark.asyncio
    async def test_process_youtube_response(self):
        """Test complete YouTube response processing."""        processor = ResponseProcessor()
        
        raw_response = {
            "items": [{
                "id": "abc123",
                "snippet": {
                    "title": "Test Video",
                    "description": "Test Description",
                    "channelId": "channel123",
                    "channelTitle": "Test Channel",
                    "publishedAt": "2025-01-01T10:00:00Z",
                    "tags": ["test", "video"],
                    "thumbnails": {"default": {"url": "https://example.com/thumb.jpg"}}
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "50",
                    "commentCount": "10"
                },
                "contentDetails": {
                    "duration": "PT5M30S"
                }
            }]
        }
        
        result = await processor.process_response("youtube", raw_response)
        
        assert result.success
        assert len(result.normalized_data) == 1
        assert result.normalized_data[0].platform == "youtube"
        assert result.normalized_data[0].content_id == "abc123"

    @pytest.mark.asyncio
    async def test_process_instagram_response(self):
        """Test Instagram response processing."""        processor = ResponseProcessor()
        
        raw_response = {
            "data": [{
                "id": "insta123",
                "media_type": "IMAGE",
                "caption": "Test post",
                "username": "testuser",
                "timestamp": "2025-01-01T12:00:00+0000",
                "media_url": "https://example.com/photo.jpg",
                "like_count": 100,
                "comments_count": 5
            }]
        }
        
        with patch.object(processor, '_extract_instagram_data') as mock_extract:
            mock_extract.return_value = [InstagramResponse(
                media_id="insta123",
                media_type="photo",
                caption="Test post",
                username="testuser",
                user_id="user123",
                like_count=100,
                comment_count=5,
                timestamp="2025-01-01T12:00:00Z",
                media_url="https://example.com/photo.jpg",
                hashtags=["test"]
            )]
            
            result = await processor.process_response("instagram", raw_response)
            
            assert result.success
            assert len(result.normalized_data) == 1

    @pytest.mark.asyncio
    async def test_process_invalid_response(self):
        """Test processing invalid response data."""        processor = ResponseProcessor()
        
        invalid_response = {
            "invalid": "data structure"
        }
        
        result = await processor.process_response("youtube", invalid_response)
        
        assert not result.success
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_process_empty_response(self):
        """Test processing empty response."""        processor = ResponseProcessor()
        
        empty_response = {"items": []}
        
        result = await processor.process_response("youtube", empty_response)
        
        assert result.success
        assert len(result.normalized_data) == 0

    def test_extract_youtube_data(self):
        """Test YouTube data extraction."""        processor = ResponseProcessor()
        
        item = {
            "id": "abc123",
            "snippet": {
                "title": "Test Video",
                "description": "Test Description",
                "channelId": "channel123",
                "channelTitle": "Test Channel",
                "publishedAt": "2025-01-01T10:00:00Z",
                "tags": ["test", "video"],
                "thumbnails": {"default": {"url": "https://example.com/thumb.jpg"}}
            },
            "statistics": {
                "viewCount": "1000",
                "likeCount": "50",
                "commentCount": "10"
            },
            "contentDetails": {
                "duration": "PT5M30S"
            }
        }
        
        youtube_response = processor._extract_youtube_data(item)
        
        assert isinstance(youtube_response, YouTubeResponse)
        assert youtube_response.video_id == "abc123"
        assert youtube_response.title == "Test Video"
        assert youtube_response.view_count == 1000

    def test_extract_instagram_data(self):
        """Test Instagram data extraction."""        processor = ResponseProcessor()
        
        item = {
            "id": "insta123",
            "media_type": "IMAGE",
            "caption": "Test post #instagram #test",
            "username": "testuser",
            "timestamp": "2025-01-01T12:00:00+0000",
            "media_url": "https://example.com/photo.jpg",
            "like_count": 100,
            "comments_count": 5
        }
        
        instagram_response = processor._extract_instagram_data(item)
        
        assert isinstance(instagram_response, InstagramResponse)
        assert instagram_response.media_id == "insta123"
        assert instagram_response.media_type == "photo"
        assert "instagram" in instagram_response.hashtags


class TestIntegration:
    """Integration tests for response handling system."""
    @pytest.mark.asyncio
    async def test_end_to_end_processing(self):
        """Test complete response processing pipeline."""        processor = ResponseProcessor()
        
        # Simulate YouTube API response
        api_response = {
            "kind": "youtube#videoListResponse",
            "items": [
                {
                    "id": "test123",
                    "snippet": {
                        "title": "Integration Test Video",
                        "description": "Testing the complete pipeline",
                        "channelId": "channel123",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2025-01-01T10:00:00Z",
                        "tags": ["integration", "test", "youtube"],
                        "thumbnails": {
                            "default": {"url": "https://example.com/thumb.jpg"}
                        }
                    },
                    "statistics": {
                        "viewCount": "5000",
                        "likeCount": "250",
                        "commentCount": "50"
                    },
                    "contentDetails": {
                        "duration": "PT10M30S"
                    }
                }
            ]
        }
        
        # Process the response
        result = await processor.process_response("youtube", api_response)
        
        # Verify complete processing
        assert result.success
        assert len(result.normalized_data) == 1
        
        normalized = result.normalized_data[0]
        assert normalized.platform == "youtube"
        assert normalized.content_id == "test123"
        assert normalized.title == "Integration Test Video"
        assert normalized.author_name == "Test Channel"
        assert normalized.engagement.views == 5000
        assert normalized.engagement.likes == 250
        assert normalized.engagement.comments == 50
        assert len(normalized.hashtags) == 3
        assert "integration" in normalized.hashtags

    @pytest.mark.asyncio
    async def test_multiple_platform_responses(self):
        """Test processing responses from multiple platforms."""        processor = ResponseProcessor()
        
        # YouTube response
        youtube_response = {
            "items": [{
                "id": "yt123",
                "snippet": {
                    "title": "YouTube Video",
                    "channelTitle": "YT Channel",
                    "publishedAt": "2025-01-01T10:00:00Z"
                },
                "statistics": {"viewCount": "1000"}
            }]
        }
        
        # Instagram response
        instagram_response = {
            "data": [{
                "id": "ig123",
                "caption": "Instagram Post",
                "username": "ig_user",
                "timestamp": "2025-01-01T12:00:00+0000",
                "like_count": 500
            }]
        }
        
        # Process both
        yt_result = await processor.process_response("youtube", youtube_response)
        ig_result = await processor.process_response("instagram", instagram_response)
        
        assert yt_result.success
        assert ig_result.success
        assert yt_result.normalized_data[0].platform == "youtube"
        assert ig_result.normalized_data[0].platform == "instagram"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling in response processing."""        processor = ResponseProcessor()
        
        # Malformed response
        malformed_response = {
            "items": [{
                "invalid_structure": True,
                "missing_required_fields": True
            }]
        }
        
        result = await processor.process_response("youtube", malformed_response)
        
        assert not result.success
        assert len(result.errors) > 0
        assert result.normalized_data == []
        
        # Verify processor can still handle valid responses after error
        valid_response = {
            "items": [{
                "id": "valid123",
                "snippet": {
                    "title": "Valid Video",
                    "channelTitle": "Valid Channel",
                    "publishedAt": "2025-01-01T10:00:00Z"
                },
                "statistics": {"viewCount": "1000"}
            }]
        }
        
        recovery_result = await processor.process_response("youtube", valid_response)
        assert recovery_result.success


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
