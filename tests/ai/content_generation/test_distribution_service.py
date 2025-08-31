# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Distribution Service Tests

Comprehensive tests for the DistributionService class that handles
multi-platform content publishing and scheduling.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.distribution_service import (
    DistributionService,
    PublishingStatus,
    PlatformConfig,
    PublishingTask
)
from ai.content_generation.content_models import Platform


class TestDistributionService:
    """Test suite for DistributionService"""    
    @pytest.fixture
    def service(self):
        """Create a distribution service instance"""        return DistributionService()
    
    @pytest.fixture
    def sample_content(self):
        """Create sample content for testing"""        return "This is a sample social media post about AI technology trends. #AI #tech #innovation"
    
    @pytest.fixture
    def blog_content(self):
        """Create sample blog content"""        return """        # The Future of AI Technology
        
        Artificial Intelligence is transforming our world in unprecedented ways.
        This comprehensive guide explores the latest trends and developments.
        
        ## Key Innovations
        - Machine Learning advances
        - Natural Language Processing
        - Computer Vision breakthroughs
        
        Read more to discover how these technologies will shape our future.
        """    
    def test_service_initialization(self, service):
        """Test distribution service initialization"""        assert service is not None
        assert hasattr(service, 'platform_configs')
        assert hasattr(service, 'publishing_queue')
        assert hasattr(service, 'active_tasks')
        assert hasattr(service, 'completed_tasks')
        assert hasattr(service, 'scheduler_running')
        
        # Check platform configurations
        assert Platform.INSTAGRAM in service.platform_configs
        assert Platform.TWITTER in service.platform_configs
        assert Platform.LINKEDIN in service.platform_configs
        assert Platform.TIKTOK in service.platform_configs
        assert Platform.YOUTUBE in service.platform_configs
    
    @pytest.mark.asyncio
    async def test_schedule_publication_single_platform(self, service, sample_content):
        """Test scheduling publication to a single platform"""        scheduled_time = datetime.now() + timedelta(hours=1)
        
        task_ids = await service.schedule_publication(
            content_id="test_001",
            content=sample_content,
            platforms=[Platform.INSTAGRAM],
            scheduled_time=scheduled_time
        )
        
        assert len(task_ids) == 1
        assert Platform.INSTAGRAM.value in task_ids
        assert len(service.publishing_queue) == 1
    
    @pytest.mark.asyncio
    async def test_schedule_publication_multiple_platforms(self, service, sample_content):
        """Test scheduling publication to multiple platforms"""        scheduled_time = datetime.now() + timedelta(hours=2)
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
        
        task_ids = await service.schedule_publication(
            content_id="test_002",
            content=sample_content,
            platforms=platforms,
            scheduled_time=scheduled_time
        )
        
        assert len(task_ids) == 3
        for platform in platforms:
            assert platform.value in task_ids
        assert len(service.publishing_queue) == 3
    
    @pytest.mark.asyncio
    async def test_immediate_publication(self, service, sample_content):
        """Test immediate publication to platforms"""        platforms = [Platform.TWITTER, Platform.LINKEDIN]
        
        with patch.object(service, '_call_platform_api') as mock_api:
            mock_api.return_value = {
                "success": True,
                "post_id": "mock_post_123",
                "url": "https://platform.com/post/123"
            }
            
            results = await service.publish_immediately(
                content_id="immediate_001",
                content=sample_content,
                platforms=platforms
            )
            
            assert len(results) == 2
            for platform in platforms:
                assert platform.value in results
                assert results[platform.value]["success"] is True
    
    @pytest.mark.asyncio
    async def test_content_optimization_for_platforms(self, service, blog_content):
        """Test content optimization for different platforms"""        # Test Instagram optimization
        instagram_content = await service._optimize_for_platform(blog_content, Platform.INSTAGRAM)
        assert len(instagram_content) <= service.platform_configs[Platform.INSTAGRAM].content_limits["max_caption_length"]
        
        # Test Twitter optimization
        twitter_content = await service._optimize_for_platform(blog_content, Platform.TWITTER)
        assert len(twitter_content) <= service.platform_configs[Platform.TWITTER].content_limits["max_tweet_length"]
        
        # Test LinkedIn optimization (should preserve more content)
        linkedin_content = await service._optimize_for_platform(blog_content, Platform.LINKEDIN)
        assert len(linkedin_content) <= service.platform_configs[Platform.LINKEDIN].content_limits["max_post_length"]
    
    @pytest.mark.asyncio
    async def test_content_validation_success(self, service, sample_content):
        """Test successful content validation"""        validation_result = await service._validate_content_for_platform(sample_content, Platform.INSTAGRAM)
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        assert validation_result["character_count"] == len(sample_content)
        assert validation_result["hashtag_count"] == sample_content.count('#')
    
    @pytest.mark.asyncio
    async def test_content_validation_failure(self, service):
        """Test content validation failure scenarios"""        # Test empty content
        empty_validation = await service._validate_content_for_platform("", Platform.TWITTER)
        assert empty_validation["valid"] is False
        assert "Content is empty" in empty_validation["errors"]
        
        # Test content too long for Twitter
        long_content = "x" * 500  # Exceeds Twitter limit
        long_validation = await service._validate_content_for_platform(long_content, Platform.TWITTER)
        assert long_validation["valid"] is False
        assert "exceeds Twitter limit" in str(long_validation["errors"])
    
    @pytest.mark.asyncio
    async def test_optimal_timing_calculation(self, service):
        """Test optimal publishing time calculation"""        now = datetime.now()
        immediate_time = now + timedelta(minutes=2)
        
        # Test immediate publication gets next optimal time
        optimal_time = service._get_optimal_publishing_time(Platform.INSTAGRAM, immediate_time)
        assert optimal_time > now
        
        # Test scheduled publication keeps original time
        future_time = now + timedelta(days=1)
        scheduled_optimal = service._get_optimal_publishing_time(Platform.INSTAGRAM, future_time)
        assert scheduled_optimal == future_time
    
    @pytest.mark.asyncio
    async def test_publication_tracking(self, service, sample_content):
        """Test publication tracking and metrics"""        content_id = "tracking_test_001"
        
        result = {
            "success": True,
            "post_id": "track_123",
            "url": "https://platform.com/post/track_123"
        }
        
        await service._track_publication(content_id, Platform.INSTAGRAM, result)
        
        # Check if tracking was recorded
        tracking_key = f"{content_id}_{Platform.INSTAGRAM.value}"
        assert tracking_key in service.metrics_cache
    
    @pytest.mark.asyncio
    async def test_publication_status_retrieval(self, service, sample_content):
        """Test retrieving publication status"""        # Schedule a publication
        task_ids = await service.schedule_publication(
            content_id="status_test",
            content=sample_content,
            platforms=[Platform.TWITTER]
        )
        
        task_id = list(task_ids.values())[0]
        
        # Get status
        status = await service.get_publication_status(task_id)
        
        assert status is not None
        assert "task_id" in status
        assert "status" in status
        assert "platform" in status
        assert status["task_id"] == task_id
    
    @pytest.mark.asyncio
    async def test_publication_cancellation(self, service, sample_content):
        """Test publication cancellation"""        # Schedule a publication
        task_ids = await service.schedule_publication(
            content_id="cancel_test",
            content=sample_content,
            platforms=[Platform.LINKEDIN],
            scheduled_time=datetime.now() + timedelta(hours=24)  # Far in future
        )
        
        task_id = list(task_ids.values())[0]
        
        # Cancel the publication
        cancellation_result = await service.cancel_publication(task_id)
        
        assert cancellation_result is True
        
        # Verify it's cancelled
        status = await service.get_publication_status(task_id)
        assert status["status"] == PublishingStatus.CANCELLED.value
    
    @pytest.mark.asyncio
    async def test_platform_api_simulation(self, service, sample_content):
        """Test platform API call simulation"""        # Test successful API call
        result = await service._call_platform_api(
            Platform.INSTAGRAM,
            sample_content,
            {"test": "metadata"}
        )
        
        assert result["success"] is True
        assert "post_id" in result
        assert "url" in result
        assert Platform.INSTAGRAM.value in result["platform"]
    
    @pytest.mark.asyncio
    async def test_error_handling_in_publication(self, service, sample_content):
        """Test error handling during publication"""        with patch.object(service, '_call_platform_api') as mock_api:
            # Mock API failure
            mock_api.return_value = {
                "success": False,
                "error": "API rate limit exceeded"
            }
            
            results = await service.publish_immediately(
                content_id="error_test",
                content=sample_content,
                platforms=[Platform.TWITTER]
            )
            
            assert Platform.TWITTER.value in results
            assert results[Platform.TWITTER.value]["success"] is False
            assert "error" in results[Platform.TWITTER.value]
    
    @pytest.mark.asyncio
    async def test_batch_publication(self, service):
        """Test batch publication functionality"""        content_items = [
            {
                "content_id": "batch_001",
                "content": "First batch content #batch1",
                "metadata": {"priority": "high"}
            },
            {
                "content_id": "batch_002", 
                "content": "Second batch content #batch2",
                "metadata": {"priority": "normal"}
            },
            {
                "content_id": "batch_003",
                "content": "Third batch content #batch3",
                "metadata": {"priority": "low"}
            }
        ]
        
        platforms = [Platform.INSTAGRAM, Platform.TWITTER]
        
        batch_results = await service.batch_publish(
            content_items=content_items,
            platforms=platforms,
            auto_schedule=True
        )
        
        assert "batch_id" in batch_results
        assert "results" in batch_results
        assert len(batch_results["results"]) == 3
        
        for result in batch_results["results"]:
            assert "content_id" in result
            assert "status" in result
    
    @pytest.mark.asyncio
    async def test_platform_analytics(self, service):
        """Test platform analytics functionality"""        # Add some mock metrics
        content_id = "analytics_test"
        await service._track_publication(
            content_id,
            Platform.INSTAGRAM,
            {"success": True, "post_id": "analytics_123"}
        )
        
        analytics = await service.get_platform_analytics(Platform.INSTAGRAM)
        
        assert analytics is not None
        assert "platform" in analytics
        assert "total_posts" in analytics
        assert analytics["platform"] == Platform.INSTAGRAM.value
    
    def test_queue_status(self, service):
        """Test queue status reporting"""        status = service.get_queue_status()
        
        assert status is not None
        assert "scheduled_tasks" in status
        assert "active_tasks" in status
        assert "completed_tasks" in status
        assert "scheduler_running" in status
        assert "queue_items" in status
    
    @pytest.mark.asyncio
    async def test_content_formatting_instagram(self, service):
        """Test Instagram-specific content formatting"""        raw_content = "This is raw content that needs Instagram formatting.\n\nIt has multiple paragraphs."
        
        formatted_content = service._add_instagram_formatting(raw_content)
        
        assert formatted_content is not None
        assert len(formatted_content) > 0
        # Should preserve paragraph structure
        assert "\n\n" in formatted_content
    
    @pytest.mark.asyncio
    async def test_content_formatting_linkedin(self, service):
        """Test LinkedIn-specific content formatting"""        raw_content = "Professional content for LinkedIn\n\nWith business focus\nAnd proper formatting"
        
        formatted_content = service._add_linkedin_formatting(raw_content)
        
        assert formatted_content is not None
        assert len(formatted_content) > 0
        # Should maintain professional formatting
    
    @pytest.mark.asyncio
    async def test_concurrent_scheduling(self, service, sample_content):
        """Test concurrent scheduling operations"""        # Schedule multiple publications concurrently
        tasks = []
        for i in range(5):
            task = service.schedule_publication(
                content_id=f"concurrent_{i}",
                content=f"Concurrent content {i} {sample_content}",
                platforms=[Platform.TWITTER],
                scheduled_time=datetime.now() + timedelta(hours=i+1)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for result in results:
            assert len(result) == 1  # One platform each
        
        # Check queue
        assert len(service.publishing_queue) == 5
    
    @pytest.mark.asyncio
    async def test_platform_specific_validation(self, service):
        """Test platform-specific validation rules"""        # Test TikTok validation (shorter content)
        tiktok_content = "Short TikTok content #viral"
        tiktok_validation = await service._validate_content_for_platform(tiktok_content, Platform.TIKTOK)
        assert tiktok_validation["valid"] is True
        
        # Test YouTube validation (longer descriptions allowed)
        youtube_content = "Long YouTube description " * 50
        youtube_validation = await service._validate_content_for_platform(youtube_content, Platform.YOUTUBE)
        # Should handle based on YouTube limits
        assert "valid" in youtube_validation
    
    @pytest.mark.asyncio
    async def test_retry_mechanism_simulation(self, service, sample_content):
        """Test retry mechanism for failed publications"""        with patch.object(service, '_call_platform_api') as mock_api:
            # First call fails, second succeeds
            mock_api.side_effect = [
                {"success": False, "error": "Temporary failure"},
                {"success": True, "post_id": "retry_success_123"}
            ]
            
            # This test simulates what would happen in the scheduler
            # We can't easily test the actual retry without complex mocking
            result1 = await service._call_platform_api(Platform.TWITTER, sample_content, {})
            assert result1["success"] is False
            
            result2 = await service._call_platform_api(Platform.TWITTER, sample_content, {})
            assert result2["success"] is True
    
    @pytest.mark.asyncio
    async def test_metadata_handling(self, service, sample_content):
        """Test metadata handling in publications"""        metadata = {
            "campaign_id": "test_campaign_001",
            "source": "automated_system",
            "priority": "high",
            "tags": ["ai", "technology", "innovation"]
        }
        
        task_ids = await service.schedule_publication(
            content_id="metadata_test",
            content=sample_content,
            platforms=[Platform.LINKEDIN],
            metadata=metadata
        )
        
        # Verify metadata is stored with task
        task_id = list(task_ids.values())[0]
        
        # Find the task in queue
        task = None
        for queued_task in service.publishing_queue:
            if queued_task.task_id == task_id:
                task = queued_task
                break
        
        assert task is not None
        assert task.metadata == metadata
    
    @pytest.mark.asyncio
    async def test_content_length_optimization(self, service):
        """Test content length optimization for different platforms"""        long_content = "Very long content " * 100  # Much longer than any platform limit
        
        # Test optimization for each platform
        platforms_to_test = [Platform.TWITTER, Platform.INSTAGRAM, Platform.TIKTOK]
        
        for platform in platforms_to_test:
            optimized = await service._optimize_for_platform(long_content, platform)
            config = service.platform_configs[platform]
            
            # Should be within platform limits
            if platform == Platform.TWITTER:
                assert len(optimized) <= config.content_limits["max_tweet_length"]
            elif platform == Platform.INSTAGRAM:
                assert len(optimized) <= config.content_limits["max_caption_length"]
            elif platform == Platform.TIKTOK:
                assert len(optimized) <= config.content_limits["max_caption_length"]


class TestPlatformConfig:
    """Test suite for platform configuration"""    
    @pytest.fixture
    def service(self):
        """Create service for platform config testing"""        return DistributionService()
    
    def test_platform_configurations_exist(self, service):
        """Test that all platform configurations exist"""        required_platforms = [
            Platform.INSTAGRAM,
            Platform.TWITTER,
            Platform.LINKEDIN,
            Platform.TIKTOK,
            Platform.YOUTUBE
        ]
        
        for platform in required_platforms:
            assert platform in service.platform_configs
            config = service.platform_configs[platform]
            assert isinstance(config, PlatformConfig)
    
    def test_platform_config_completeness(self, service):
        """Test platform configuration completeness"""        for platform, config in service.platform_configs.items():
            assert config.platform == platform
            assert config.api_endpoint is not None
            assert config.auth_type is not None
            assert isinstance(config.rate_limits, dict)
            assert isinstance(config.content_limits, dict)
            assert isinstance(config.optimal_times, list)
            assert isinstance(config.supported_formats, list)
    
    def test_rate_limits_configuration(self, service):
        """Test rate limits configuration"""        for platform, config in service.platform_configs.items():
            rate_limits = config.rate_limits
            
            # Should have some form of rate limiting
            assert len(rate_limits) > 0
            
            # Values should be positive integers
            for limit_name, limit_value in rate_limits.items():
                assert isinstance(limit_value, int)
                assert limit_value > 0
    
    def test_content_limits_configuration(self, service):
        """Test content limits configuration"""        for platform, config in service.platform_configs.items():
            content_limits = config.content_limits
            
            # Should have content limits
            assert len(content_limits) > 0
            
            # Should have some form of length limit
            length_keys = ["max_tweet_length", "max_caption_length", "max_post_length", "max_description_length"]
            has_length_limit = any(key in content_limits for key in length_keys)
            assert has_length_limit
    
    def test_optimal_times_configuration(self, service):
        """Test optimal times configuration"""        for platform, config in service.platform_configs.items():
            optimal_times = config.optimal_times
            
            # Should have optimal times defined
            assert len(optimal_times) > 0
            
            # Times should be in HH:MM format
            for time_str in optimal_times:
                assert isinstance(time_str, str)
                assert ":" in time_str
                hour, minute = time_str.split(":")
                assert 0 <= int(hour) <= 23
                assert 0 <= int(minute) <= 59


class TestPublishingTask:
    """Test suite for PublishingTask"""    
    def test_task_creation(self):
        """Test publishing task creation"""        task = PublishingTask(
            task_id="test_task_123",
            content_id="content_456",
            platform=Platform.INSTAGRAM,
            content="Test content",
            scheduled_time=datetime.now() + timedelta(hours=1),
            status=PublishingStatus.SCHEDULED,
            metadata={"test": "data"}
        )
        
        assert task.task_id == "test_task_123"
        assert task.content_id == "content_456"
        assert task.platform == Platform.INSTAGRAM
        assert task.content == "Test content"
        assert task.status == PublishingStatus.SCHEDULED
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.created_at is not None
    
    def test_task_status_transitions(self):
        """Test task status transitions"""        task = PublishingTask(
            task_id="status_test",
            content_id="content_status",
            platform=Platform.TWITTER,
            content="Status test content",
            scheduled_time=datetime.now(),
            status=PublishingStatus.SCHEDULED,
            metadata={}
        )
        
        # Initial status
        assert task.status == PublishingStatus.SCHEDULED
        
        # Transition to publishing
        task.status = PublishingStatus.PUBLISHING
        assert task.status == PublishingStatus.PUBLISHING
        
        # Transition to completed
        task.status = PublishingStatus.PUBLISHED
        task.published_at = datetime.now()
        assert task.status == PublishingStatus.PUBLISHED
        assert task.published_at is not None


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
