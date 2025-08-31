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
Comprehensive Tests for Utility Functions and Helper Components
Testing utility functions, helpers, validators, and common operations

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de

Team Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import base64

from ai.recommendation.utils import (
    ModelManager, HealthChecker, RecommendationValidator
)
from ai.recommendation.models import (
    CreatorProfile, Platform, ContentType, RecommendationRequest
)
from ai.recommendation.exceptions import ValidationError, RecommendationError


class TestDataValidator:
    """Tests for data validation utilities"""
    
    def test_validate_creator_profile(self, data_validator):
        """Test creator profile validation"""
        # Valid profile
        valid_profile = {
            "creator_id": "test_creator_001",
            "display_name": "Test Creator",
            "platforms": ["youtube", "instagram"],
            "followers_count": {"youtube": 10000, "instagram": 5000},
            "content_types": ["video", "image"],
            "genres": ["Music", "Entertainment"]
        }
        
        result = data_validator.validate_creator_profile(valid_profile)
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        
        # Invalid profile - missing required fields
        invalid_profile = {
            "display_name": "Test Creator",
            # Missing creator_id
            "platforms": ["youtube"],
            "followers_count": {"youtube": 10000}
        }
        
        result = data_validator.validate_creator_profile(invalid_profile)
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
        assert any('creator_id' in error for error in result['errors'])
    
    def test_validate_content_data(self, data_validator):
        """Test content data validation"""
        # Valid video content
        valid_video = {
            "title": "Test Video",
            "description": "This is a test video description",
            "duration": 300,  # 5 minutes
            "format": "mp4",
            "resolution": "1920x1080",
            "file_size": 50000000  # 50MB
        }
        
        result = data_validator.validate_content_data(valid_video, ContentType.VIDEO)
        assert result['is_valid'] is True
        
        # Invalid video - missing title
        invalid_video = {
            "description": "This is a test video description",
            "duration": 300,
            "format": "mp4"
        }
        
        result = data_validator.validate_content_data(invalid_video, ContentType.VIDEO)
        assert result['is_valid'] is False
        assert any('title' in error for error in result['errors'])
    
    def test_validate_recommendation_request(self, data_validator):
        """Test recommendation request validation"""
        # Valid request
        valid_request = {
            "creator_id": "test_creator_001",
            "limit": 10,
            "platform_filter": ["youtube", "instagram"],
            "content_type_filter": ["video", "image"],
            "time_horizon": "30d"
        }
        
        result = data_validator.validate_recommendation_request(valid_request)
        assert result['is_valid'] is True
        
        # Invalid request - invalid limit
        invalid_request = {
            "creator_id": "test_creator_001",
            "limit": -5,  # Invalid negative limit
            "platform_filter": ["youtube"]
        }
        
        result = data_validator.validate_recommendation_request(invalid_request)
        assert result['is_valid'] is False
        assert any('limit' in error for error in result['errors'])
    
    def test_validate_metrics_data(self, data_validator):
        """Test metrics data validation"""
        # Valid metrics
        valid_metrics = {
            "views": 100000,
            "likes": 5000,
            "shares": 500,
            "comments": 200,
            "engagement_rate": 0.055,
            "ctr": 0.025,
            "retention_rate": 0.75
        }
        
        result = data_validator.validate_metrics_data(valid_metrics)
        assert result['is_valid'] is True
        
        # Invalid metrics - negative values
        invalid_metrics = {
            "views": -100,  # Invalid negative
            "likes": 5000,
            "engagement_rate": 1.5  # Invalid > 1.0
        }
        
        result = data_validator.validate_metrics_data(invalid_metrics)
        assert result['is_valid'] is False
        assert len(result['errors']) >= 2  # At least 2 errors
    
    def test_validate_platform_constraints(self, data_validator):
        """Test platform-specific constraint validation"""
        # YouTube constraints
        youtube_video = {
            "title": "Test Video",
            "duration": 3600,  # 1 hour
            "file_size": 128000000000,  # 128GB
            "format": "mp4"
        }
        
        result = data_validator.validate_platform_constraints(
            youtube_video, Platform.YOUTUBE, ContentType.VIDEO
        )
        assert result['is_valid'] is False  # Too large file size
        
        # Valid YouTube video
        youtube_video_valid = {
            "title": "Test Video",
            "duration": 600,  # 10 minutes
            "file_size": 100000000,  # 100MB
            "format": "mp4"
        }
        
        result = data_validator.validate_platform_constraints(
            youtube_video_valid, Platform.YOUTUBE, ContentType.VIDEO
        )
        assert result['is_valid'] is True
    
    def test_validate_email_format(self, data_validator):
        """Test email format validation"""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+label@example.org"
        ]
        
        for email in valid_emails:
            assert data_validator.validate_email_format(email) is True
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "test..test@domain.com"
        ]
        
        for email in invalid_emails:
            assert data_validator.validate_email_format(email) is False


class TestContentNormalizer:
    """Tests for content normalization utilities"""
    
    def test_normalize_text_content(self, content_normalizer):
        """Test text content normalization"""
        raw_text = "  This is a TEST text with MIXED case and   extra spaces!!!   "
        
        normalized = content_normalizer.normalize_text_content(
            raw_text,
            lowercase=True,
            remove_extra_spaces=True,
            remove_emojis=True,
            remove_punctuation=False
        )
        
        expected = "this is a test text with mixed case and extra spaces!"
        assert normalized == expected
    
    def test_normalize_hashtags(self, content_normalizer):
        """Test hashtag normalization"""
        hashtags = ["#Music", "#ELECTRONIC", "#house music", "#Tech-House", "#Progressive"]
        
        normalized = content_normalizer.normalize_hashtags(hashtags)
        
        # Should be lowercase and properly formatted
        assert "#music" in normalized
        assert "#electronic" in normalized
        assert "#housemusic" in normalized  # Spaces removed
        assert "#techhouse" in normalized   # Hyphens removed
        assert "#progressive" in normalized
    
    def test_normalize_creator_data(self, content_normalizer, sample_creator_musician):
        """Test creator data normalization"""
        creator_data = {
            "creator_id": "  TEST_Creator_001  ",
            "display_name": "  John DOE  ",
            "email": "  JOHN.DOE@EXAMPLE.COM  ",
            "genres": ["ELECTRONIC", "house music", "Tech-House"],
            "bio": "This is a creator bio with   extra spaces and MIXED case."
        }
        
        normalized = content_normalizer.normalize_creator_data(creator_data)
        
        assert normalized['creator_id'] == "test_creator_001"
        assert normalized['display_name'] == "John Doe"
        assert normalized['email'] == "john.doe@example.com"
        assert "electronic" in normalized['genres']
        assert "house_music" in normalized['genres']
        assert "tech_house" in normalized['genres']
    
    def test_normalize_metrics_data(self, content_normalizer):
        """Test metrics data normalization"""
        raw_metrics = {
            "views": "10,000",
            "likes": "1.5K",
            "shares": "500",
            "engagement_rate": "5.5%",
            "ctr": "0.025",
            "revenue": "$1,250.50"
        }
        
        normalized = content_normalizer.normalize_metrics_data(raw_metrics)
        
        assert normalized['views'] == 10000
        assert normalized['likes'] == 1500
        assert normalized['shares'] == 500
        assert abs(normalized['engagement_rate'] - 0.055) < 0.001
        assert abs(normalized['ctr'] - 0.025) < 0.001
        assert abs(normalized['revenue'] - 1250.50) < 0.01
    
    def test_normalize_platform_data(self, content_normalizer):
        """Test platform-specific data normalization"""
        platform_data = {
            "platform": "YouTube",
            "channel_url": "  https://www.youtube.com/channel/UC1234567890  ",
            "subscriber_count": "10K",
            "video_count": "150",
            "total_views": "1.2M"
        }
        
        normalized = content_normalizer.normalize_platform_data(
            platform_data, Platform.YOUTUBE
        )
        
        assert normalized['platform'] == "youtube"
        assert normalized['channel_url'] == "https://www.youtube.com/channel/UC1234567890"
        assert normalized['subscriber_count'] == 10000
        assert normalized['video_count'] == 150
        assert normalized['total_views'] == 1200000


class TestMetricsCalculator:
    """Tests for metrics calculation utilities"""
    
    def test_calculate_engagement_rate(self, metrics_calculator):
        """Test engagement rate calculation"""
        # Standard engagement rate
        metrics = {
            "views": 10000,
            "likes": 500,
            "comments": 100,
            "shares": 50
        }
        
        engagement_rate = metrics_calculator.calculate_engagement_rate(metrics)
        expected_rate = (500 + 100 + 50) / 10000  # 0.065
        assert abs(engagement_rate - expected_rate) < 0.001
        
        # Zero views edge case
        zero_views_metrics = {
            "views": 0,
            "likes": 10,
            "comments": 5,
            "shares": 2
        }
        
        engagement_rate = metrics_calculator.calculate_engagement_rate(zero_views_metrics)
        assert engagement_rate == 0.0
    
    def test_calculate_virality_score(self, metrics_calculator):
        """Test virality score calculation"""
        metrics = {
            "views": 100000,
            "shares": 5000,
            "comments": 1000,
            "likes": 8000,
            "growth_rate": 2.5,  # 250% growth
            "time_since_publish": 24  # 24 hours
        }
        
        virality_score = metrics_calculator.calculate_virality_score(metrics)
        
        # Should be between 0 and 1
        assert 0 <= virality_score <= 1
        
        # High engagement and growth should result in high virality
        assert virality_score > 0.5
    
    def test_calculate_content_quality_score(self, metrics_calculator):
        """Test content quality score calculation"""
        quality_metrics = {
            "technical_quality": 0.85,
            "content_relevance": 0.90,
            "audience_engagement": 0.75,
            "production_value": 0.80,
            "originality": 0.95
        }
        
        quality_score = metrics_calculator.calculate_content_quality_score(quality_metrics)
        
        # Should be weighted average
        expected_score = (0.85 * 0.2 + 0.90 * 0.25 + 0.75 * 0.25 + 0.80 * 0.15 + 0.95 * 0.15)
        assert abs(quality_score - expected_score) < 0.01
    
    def test_calculate_roi_metrics(self, metrics_calculator):
        """Test ROI metrics calculation"""
        investment_data = {
            "content_creation_cost": 500.0,
            "promotion_cost": 200.0,
            "time_investment_hours": 20,
            "hourly_rate": 50.0
        }
        
        revenue_data = {
            "ad_revenue": 300.0,
            "sponsorship_revenue": 800.0,
            "product_sales": 400.0,
            "subscription_revenue": 200.0
        }
        
        roi_metrics = metrics_calculator.calculate_roi_metrics(investment_data, revenue_data)
        
        assert 'total_investment' in roi_metrics
        assert 'total_revenue' in roi_metrics
        assert 'roi_percentage' in roi_metrics
        assert 'profit_margin' in roi_metrics
        
        # Total investment = 500 + 200 + (20 * 50) = 1700
        assert roi_metrics['total_investment'] == 1700.0
        
        # Total revenue = 300 + 800 + 400 + 200 = 1700
        assert roi_metrics['total_revenue'] == 1700.0
        
        # ROI = (1700 - 1700) / 1700 = 0%
        assert abs(roi_metrics['roi_percentage']) < 0.01
    
    def test_calculate_trend_metrics(self, metrics_calculator):
        """Test trend metrics calculation"""
        time_series_data = [
            {"date": "2025-01-01", "value": 1000},
            {"date": "2025-01-02", "value": 1200},
            {"date": "2025-01-03", "value": 1100},
            {"date": "2025-01-04", "value": 1400},
            {"date": "2025-01-05", "value": 1600}
        ]
        
        trend_metrics = metrics_calculator.calculate_trend_metrics(time_series_data)
        
        assert 'growth_rate' in trend_metrics
        assert 'volatility' in trend_metrics
        assert 'trend_direction' in trend_metrics
        assert 'momentum' in trend_metrics
        
        # Should show positive growth
        assert trend_metrics['growth_rate'] > 0
        assert trend_metrics['trend_direction'] == 'upward'


class TestCacheManager:
    """Tests for cache management utilities"""
    
    @pytest.mark.asyncio
    async def test_cache_basic_operations(self, cache_manager):
        """Test basic cache operations"""
        # Set and get
        await cache_manager.set("test_key", "test_value", ttl=300)
        value = await cache_manager.get("test_key")
        assert value == "test_value"
        
        # Check existence
        exists = await cache_manager.exists("test_key")
        assert exists is True
        
        # Delete
        await cache_manager.delete("test_key")
        value = await cache_manager.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_complex_data(self, cache_manager):
        """Test caching complex data structures"""
        complex_data = {
            "creator_profile": {
                "id": "creator_001",
                "metrics": [1, 2, 3, 4, 5],
                "nested": {"key": "value"}
            }
        }
        
        await cache_manager.set("complex_key", complex_data, ttl=600)
        retrieved_data = await cache_manager.get("complex_key")
        
        assert retrieved_data == complex_data
        assert retrieved_data["creator_profile"]["id"] == "creator_001"
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, cache_manager):
        """Test cache TTL expiration"""
        # Set with very short TTL
        await cache_manager.set("expiring_key", "expiring_value", ttl=1)
        
        # Should exist immediately
        value = await cache_manager.get("expiring_key")
        assert value == "expiring_value"
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Should be expired
        value = await cache_manager.get("expiring_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_batch_operations(self, cache_manager):
        """Test batch cache operations"""
        # Batch set
        batch_data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        await cache_manager.set_batch(batch_data, ttl=300)
        
        # Batch get
        keys = ["key1", "key2", "key3"]
        values = await cache_manager.get_batch(keys)
        
        assert values["key1"] == "value1"
        assert values["key2"] == "value2"
        assert values["key3"] == "value3"
    
    @pytest.mark.asyncio
    async def test_cache_pattern_operations(self, cache_manager):
        """Test cache pattern operations"""
        # Set multiple keys with pattern
        await cache_manager.set("user:001:profile", "profile1", ttl=300)
        await cache_manager.set("user:002:profile", "profile2", ttl=300)
        await cache_manager.set("user:003:settings", "settings3", ttl=300)
        
        # Find keys by pattern
        profile_keys = await cache_manager.find_keys("user:*:profile")
        assert len(profile_keys) == 2
        assert "user:001:profile" in profile_keys
        assert "user:002:profile" in profile_keys
        
        # Delete by pattern
        await cache_manager.delete_pattern("user:*:profile")
        
        # Verify deletion
        remaining_keys = await cache_manager.find_keys("user:*:profile")
        assert len(remaining_keys) == 0


class TestRateLimiter:
    """Tests for rate limiting utilities"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_basic(self, rate_limiter):
        """Test basic rate limiting"""
        # Configure rate limit: 5 requests per 10 seconds
        limiter_id = "test_basic"
        await rate_limiter.configure(limiter_id, max_requests=5, window_seconds=10)
        
        # First 5 requests should pass
        for i in range(5):
            allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
            assert allowed is True
        
        # 6th request should be rate limited
        allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
        assert allowed is False
    
    @pytest.mark.asyncio
    async def test_rate_limit_different_users(self, rate_limiter):
        """Test rate limiting for different users"""
        limiter_id = "test_users"
        await rate_limiter.configure(limiter_id, max_requests=3, window_seconds=5)
        
        # User 1 makes 3 requests
        for i in range(3):
            allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
            assert allowed is True
        
        # User 1 is now rate limited
        allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
        assert allowed is False
        
        # User 2 should still be allowed
        allowed = await rate_limiter.is_allowed(limiter_id, "user_002")
        assert allowed is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_window_reset(self, rate_limiter):
        """Test rate limit window reset"""
        limiter_id = "test_reset"
        await rate_limiter.configure(limiter_id, max_requests=2, window_seconds=2)
        
        # Make 2 requests
        for i in range(2):
            allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
            assert allowed is True
        
        # 3rd request should be limited
        allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
        assert allowed is False
        
        # Wait for window reset
        await asyncio.sleep(3)
        
        # Should be allowed again
        allowed = await rate_limiter.is_allowed(limiter_id, "user_001")
        assert allowed is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_status_info(self, rate_limiter):
        """Test rate limit status information"""
        limiter_id = "test_status"
        await rate_limiter.configure(limiter_id, max_requests=5, window_seconds=10)
        
        # Make some requests
        for i in range(3):
            await rate_limiter.is_allowed(limiter_id, "user_001")
        
        # Get status
        status = await rate_limiter.get_status(limiter_id, "user_001")
        
        assert 'requests_made' in status
        assert 'requests_remaining' in status
        assert 'window_reset_time' in status
        assert 'is_limited' in status
        
        assert status['requests_made'] == 3
        assert status['requests_remaining'] == 2
        assert status['is_limited'] is False


class TestPerformanceMonitor:
    """Tests for performance monitoring utilities"""
    
    @pytest.mark.asyncio
    async def test_monitor_function_performance(self, performance_monitor):
        """Test function performance monitoring"""
        @performance_monitor.monitor("test_function")
        async def test_function():
            await asyncio.sleep(0.1)  # Simulate work
            return "result"
        
        result = await test_function()
        assert result == "result"
        
        # Get performance metrics
        metrics = await performance_monitor.get_metrics("test_function")
        
        assert 'total_calls' in metrics
        assert 'average_duration' in metrics
        assert 'min_duration' in metrics
        assert 'max_duration' in metrics
        assert 'error_count' in metrics
        
        assert metrics['total_calls'] == 1
        assert metrics['average_duration'] > 0.1
        assert metrics['error_count'] == 0
    
    @pytest.mark.asyncio
    async def test_monitor_memory_usage(self, performance_monitor):
        """Test memory usage monitoring"""
        # Start monitoring
        monitor_id = "memory_test"
        await performance_monitor.start_memory_monitoring(monitor_id)
        
        # Allocate some memory
        large_list = [i for i in range(100000)]
        
        # Stop monitoring
        memory_stats = await performance_monitor.stop_memory_monitoring(monitor_id)
        
        assert 'peak_memory_mb' in memory_stats
        assert 'memory_increase_mb' in memory_stats
        assert 'gc_collections' in memory_stats
        
        assert memory_stats['peak_memory_mb'] > 0
        assert memory_stats['memory_increase_mb'] >= 0
    
    @pytest.mark.asyncio
    async def test_monitor_system_resources(self, performance_monitor):
        """Test system resource monitoring"""
        system_stats = await performance_monitor.get_system_stats()
        
        assert 'cpu_percent' in system_stats
        assert 'memory_percent' in system_stats
        assert 'disk_usage_percent' in system_stats
        assert 'network_io' in system_stats
        
        # All percentages should be valid
        assert 0 <= system_stats['cpu_percent'] <= 100
        assert 0 <= system_stats['memory_percent'] <= 100
        assert 0 <= system_stats['disk_usage_percent'] <= 100
    
    @pytest.mark.asyncio
    async def test_performance_alerts(self, performance_monitor):
        """Test performance alerting"""
        # Configure alert thresholds
        await performance_monitor.configure_alerts({
            "max_response_time": 1.0,  # 1 second
            "max_memory_usage": 100,   # 100 MB
            "max_error_rate": 0.05     # 5%
        })
        
        # Simulate slow function
        @performance_monitor.monitor("slow_function")
        async def slow_function():
            await asyncio.sleep(1.5)  # Exceeds threshold
            return "slow_result"
        
        await slow_function()
        
        # Check for alerts
        alerts = await performance_monitor.get_recent_alerts()
        
        assert len(alerts) > 0
        assert any(alert['type'] == 'response_time' for alert in alerts)


class TestTextProcessor:
    """Tests for text processing utilities"""
    
    def test_extract_keywords(self, text_processor):
        """Test keyword extraction"""
        text = """
        Artificial intelligence and machine learning are transforming the music industry.
        AI-powered recommendation systems help creators discover trending content and
        optimize their creative process for better audience engagement.
        """
        
        keywords = text_processor.extract_keywords(text, max_keywords=10)
        
        assert len(keywords) <= 10
        assert any('artificial intelligence' in kw.lower() for kw in keywords)
        assert any('machine learning' in kw.lower() for kw in keywords)
        assert any('music' in kw.lower() for kw in keywords)
    
    def test_analyze_sentiment(self, text_processor):
        """Test sentiment analysis"""
        positive_text = "This is an amazing and wonderful piece of music!"
        negative_text = "This content is terrible and disappointing."
        neutral_text = "This is a technical documentation about API usage."
        
        # Positive sentiment
        pos_result = text_processor.analyze_sentiment(positive_text)
        assert pos_result['label'] == 'positive'
        assert pos_result['score'] > 0.5
        
        # Negative sentiment
        neg_result = text_processor.analyze_sentiment(negative_text)
        assert neg_result['label'] == 'negative'
        assert neg_result['score'] < -0.1
        
        # Neutral sentiment
        neu_result = text_processor.analyze_sentiment(neutral_text)
        assert neu_result['label'] == 'neutral'
        assert abs(neu_result['score']) < 0.3
    
    def test_extract_entities(self, text_processor):
        """Test named entity extraction"""
        text = """
        Fahed Mlaiel is the lead developer working on AI recommendation systems.
        The project is based in Germany and uses TensorFlow and PyTorch.
        The team focuses on music and entertainment content for YouTube and Spotify.
        """
        
        entities = text_processor.extract_entities(text)
        
        # Should extract person names
        persons = [e for e in entities if e['label'] == 'PERSON']
        assert any('Fahed Mlaiel' in p['text'] for p in persons)
        
        # Should extract locations
        locations = [e for e in entities if e['label'] in ['GPE', 'LOCATION']]
        assert any('Germany' in l['text'] for l in locations)
        
        # Should extract organizations/technologies
        orgs = [e for e in entities if e['label'] in ['ORG', 'PRODUCT']]
        assert any('TensorFlow' in o['text'] for o in orgs)
    
    def test_generate_summary(self, text_processor):
        """Test text summarization"""
        long_text = """
        Artificial intelligence has revolutionized many industries, and the music industry
        is no exception. AI-powered recommendation systems analyze user behavior, content
        features, and trending patterns to suggest relevant music and content to creators
        and listeners. These systems use complex algorithms including collaborative filtering,
        content-based filtering, and deep learning models to understand user preferences.
        
        The recommendation process involves multiple steps: data collection, feature extraction,
        model training, and real-time inference. Content creators benefit from these systems
        by receiving insights about trending topics, optimal posting times, and audience
        preferences. This helps them create more engaging content and grow their following.
        
        Machine learning models continuously learn from user interactions, improving the
        accuracy of recommendations over time. The future of AI in music recommendation
        includes more sophisticated personalization, real-time adaptation, and integration
        with emerging technologies like voice assistants and augmented reality.
        """
        
        summary = text_processor.generate_summary(
            long_text, 
            max_sentences=3,
            extraction_method="abstractive"
        )
        
        assert len(summary) > 0
        assert len(summary) < len(long_text)
        assert 'AI' in summary or 'artificial intelligence' in summary.lower()
    
    def test_detect_language(self, text_processor):
        """Test language detection"""
        english_text = "This is a text written in English language."
        german_text = "Das ist ein Text, der in deutscher Sprache geschrieben wurde."
        french_text = "Ceci est un texte écrit en langue française."
        
        # English detection
        en_result = text_processor.detect_language(english_text)
        assert en_result['language'] == 'en'
        assert en_result['confidence'] > 0.8
        
        # German detection
        de_result = text_processor.detect_language(german_text)
        assert de_result['language'] == 'de'
        assert de_result['confidence'] > 0.8
        
        # French detection
        fr_result = text_processor.detect_language(french_text)
        assert fr_result['language'] == 'fr'
        assert fr_result['confidence'] > 0.8


class TestSecurityUtils:
    """Tests for security utilities"""
    
    def test_hash_data(self, security_utils):
        """Test data hashing"""
        data = "sensitive_data_to_hash"
        
        # SHA256 hash
        hash_sha256 = security_utils.hash_data(data, algorithm="sha256")
        assert len(hash_sha256) == 64  # SHA256 produces 64 character hex string
        
        # MD5 hash
        hash_md5 = security_utils.hash_data(data, algorithm="md5")
        assert len(hash_md5) == 32  # MD5 produces 32 character hex string
        
        # Same data should produce same hash
        hash_again = security_utils.hash_data(data, algorithm="sha256")
        assert hash_sha256 == hash_again
    
    def test_encrypt_decrypt_data(self, security_utils):
        """Test data encryption and decryption"""
        original_data = "This is sensitive information that needs encryption"
        encryption_key = security_utils.generate_key()
        
        # Encrypt data
        encrypted_data = security_utils.encrypt_data(original_data, encryption_key)
        assert encrypted_data != original_data
        assert len(encrypted_data) > 0
        
        # Decrypt data
        decrypted_data = security_utils.decrypt_data(encrypted_data, encryption_key)
        assert decrypted_data == original_data
    
    def test_generate_secure_token(self, security_utils):
        """Test secure token generation"""
        # Generate tokens of different lengths
        token_16 = security_utils.generate_secure_token(16)
        token_32 = security_utils.generate_secure_token(32)
        token_64 = security_utils.generate_secure_token(64)
        
        assert len(token_16) == 32  # 16 bytes = 32 hex characters
        assert len(token_32) == 64  # 32 bytes = 64 hex characters
        assert len(token_64) == 128 # 64 bytes = 128 hex characters
        
        # Tokens should be different
        assert token_16 != token_32 != token_64
        
        # Tokens should be hexadecimal
        assert all(c in '0123456789abcdef' for c in token_16.lower())
    
    def test_validate_jwt_token(self, security_utils):
        """Test JWT token validation"""
        payload = {
            "user_id": "test_user_001",
            "permissions": ["read", "write"],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        secret_key = "test_secret_key"
        
        # Create token
        token = security_utils.create_jwt_token(payload, secret_key)
        assert len(token) > 0
        
        # Validate token
        decoded_payload = security_utils.validate_jwt_token(token, secret_key)
        assert decoded_payload['user_id'] == "test_user_001"
        assert decoded_payload['permissions'] == ["read", "write"]
        
        # Invalid token should fail
        invalid_token = token[:-5] + "xxxxx"  # Corrupt token
        with pytest.raises(Exception):
            security_utils.validate_jwt_token(invalid_token, secret_key)
    
    def test_sanitize_input(self, security_utils):
        """Test input sanitization"""
        # SQL injection attempt
        sql_injection = "'; DROP TABLE users; --"
        sanitized_sql = security_utils.sanitize_input(sql_injection, input_type="sql")
        assert "DROP TABLE" not in sanitized_sql.upper()
        
        # XSS attempt
        xss_attempt = "<script>alert('XSS')</script>"
        sanitized_xss = security_utils.sanitize_input(xss_attempt, input_type="html")
        assert "<script>" not in sanitized_xss
        assert "alert" not in sanitized_xss
        
        # Path traversal attempt
        path_traversal = "../../etc/passwd"
        sanitized_path = security_utils.sanitize_input(path_traversal, input_type="path")
        assert "../" not in sanitized_path


class TestRecommendationUtils:
    """Tests for recommendation-specific utilities"""
    
    def test_calculate_similarity_matrix(self, recommendation_utils):
        """Test similarity matrix calculation"""
        # User-item matrix
        user_item_matrix = np.array([
            [5, 3, 0, 1],
            [4, 0, 0, 1],
            [1, 1, 0, 5],
            [1, 0, 0, 4],
            [0, 1, 5, 4]
        ])
        
        # Calculate user similarity
        user_similarity = recommendation_utils.calculate_similarity_matrix(
            user_item_matrix, similarity_type="cosine"
        )
        
        assert user_similarity.shape == (5, 5)  # 5 users
        assert np.all(np.diag(user_similarity) == 1.0)  # Self-similarity = 1
        assert np.allclose(user_similarity, user_similarity.T)  # Symmetric matrix
    
    def test_apply_collaborative_filtering(self, recommendation_utils):
        """Test collaborative filtering algorithm"""
        # Mock user-item interactions
        interactions = {
            "user_1": {"item_A": 5, "item_B": 3, "item_C": 1},
            "user_2": {"item_A": 4, "item_B": 1, "item_D": 5},
            "user_3": {"item_C": 5, "item_D": 4, "item_E": 3}
        }
        
        recommendations = recommendation_utils.apply_collaborative_filtering(
            interactions, target_user="user_1", num_recommendations=3
        )
        
        assert len(recommendations) <= 3
        for rec in recommendations:
            assert 'item_id' in rec
            assert 'predicted_rating' in rec
            assert 'confidence' in rec
            assert 0 <= rec['predicted_rating'] <= 5
            assert 0 <= rec['confidence'] <= 1
    
    def test_apply_content_based_filtering(self, recommendation_utils):
        """Test content-based filtering algorithm"""
        # Mock item features
        item_features = {
            "item_A": {"genre": "electronic", "tempo": 128, "energy": 0.8},
            "item_B": {"genre": "electronic", "tempo": 130, "energy": 0.9},
            "item_C": {"genre": "rock", "tempo": 120, "energy": 0.7},
            "item_D": {"genre": "pop", "tempo": 125, "energy": 0.6}
        }
        
        # User preferences (liked items)
        user_preferences = ["item_A", "item_B"]
        
        recommendations = recommendation_utils.apply_content_based_filtering(
            item_features, user_preferences, num_recommendations=2
        )
        
        assert len(recommendations) <= 2
        for rec in recommendations:
            assert 'item_id' in rec
            assert 'similarity_score' in rec
            assert 'feature_matches' in rec
            assert 0 <= rec['similarity_score'] <= 1
    
    def test_hybrid_recommendation_fusion(self, recommendation_utils):
        """Test hybrid recommendation fusion"""
        # Collaborative filtering results
        cf_results = [
            {"item_id": "item_A", "score": 0.9, "source": "collaborative"},
            {"item_id": "item_B", "score": 0.7, "source": "collaborative"},
            {"item_id": "item_C", "score": 0.6, "source": "collaborative"}
        ]
        
        # Content-based filtering results
        cb_results = [
            {"item_id": "item_A", "score": 0.8, "source": "content_based"},
            {"item_id": "item_D", "score": 0.9, "source": "content_based"},
            {"item_id": "item_E", "score": 0.7, "source": "content_based"}
        ]
        
        # Fusion with equal weights
        fused_results = recommendation_utils.hybrid_recommendation_fusion(
            [cf_results, cb_results],
            fusion_weights=[0.5, 0.5],
            fusion_method="weighted_average"
        )
        
        assert len(fused_results) > 0
        
        # item_A should have high score (appears in both)
        item_a_result = next((r for r in fused_results if r['item_id'] == 'item_A'), None)
        assert item_a_result is not None
        assert item_a_result['fused_score'] > 0.8
    
    def test_diversity_enhancement(self, recommendation_utils):
        """Test recommendation diversity enhancement"""
        # Homogeneous recommendations (all same genre)
        recommendations = [
            {"item_id": "item_A", "score": 0.9, "features": {"genre": "electronic", "tempo": 128}},
            {"item_id": "item_B", "score": 0.8, "features": {"genre": "electronic", "tempo": 130}},
            {"item_id": "item_C", "score": 0.7, "features": {"genre": "electronic", "tempo": 132}},
            {"item_id": "item_D", "score": 0.6, "features": {"genre": "rock", "tempo": 120}},
            {"item_id": "item_E", "score": 0.5, "features": {"genre": "pop", "tempo": 125}}
        ]
        
        # Enhance diversity
        diverse_recommendations = recommendation_utils.enhance_recommendation_diversity(
            recommendations,
            diversity_factor=0.8,
            feature_weights={"genre": 0.7, "tempo": 0.3}
        )
        
        assert len(diverse_recommendations) == len(recommendations)
        
        # Should have mixed genres
        genres = [rec['features']['genre'] for rec in diverse_recommendations[:3]]
        unique_genres = set(genres)
        assert len(unique_genres) > 1  # Should have more than one genre
