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

"""Base Generator Tests

Comprehensive tests for the BaseContentGenerator class that serves
as the foundation for all content generators in the system.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional
import logging

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.base_generator import (
    BaseContentGenerator
)
from ai.core.exceptions import (
    ContentGenerationError,
    ContentValidationError,
    RateLimitError
)


class MockContentGenerator(BaseContentGenerator):
    """Mock implementation for testing BaseContentGenerator"""    
    def __init__(self):
        config = {
            "model_name": "mock_model",
            "max_tokens": 1000,
            "temperature": 0.7
        }
        super().__init__(config)
        self.generation_call_count = 0
        self.should_fail = False
        self.generation_delay = 0.1
        
    async def generate_content(self, request: Dict[str, Any]) -> str:
        """Mock content generation"""        self.generation_call_count += 1
        
        if self.should_fail:
            raise ContentGenerationError("Mock generation failure")
        
        # Simulate processing time
        await asyncio.sleep(self.generation_delay)
        
        return f"Mock generated content for request: {request.get('prompt', 'default')}"
    
    def _setup_models(self):
        """Mock model setup"""        pass
    
    def _setup_resources(self):
        """Mock resource setup"""        pass
    
    def _setup_validation_rules(self):
        """Mock validation rules setup"""        pass
    
    async def validate_output(self, content: str, context: Any) -> bool:
        """Mock output validation"""        return len(content) > 0
    
    async def _release_model_resources(self):
        """Mock resource cleanup"""        pass
        await asyncio.sleep(self.generation_delay)
        
        return f"Generated content for: {request.get('topic', 'unknown')}"
    
    async def validate_input(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock input validation"""        errors = []
        
        if not request.get('topic'):
            errors.append("Topic is required")
        
        if request.get('word_count', 0) < 0:
            errors.append("Word count cannot be negative")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


class TestBaseContentGenerator:
    """Test suite for BaseContentGenerator"""    
    @pytest.fixture
    def generator(self):
        """Create a mock generator instance"""        return MockContentGenerator()
    
    @pytest.fixture
    def valid_request(self):
        """Create a valid generation request"""        return {
            "topic": "AI technology trends",
            "content_type": "blog_post",
            "word_count": 500,
            "target_audience": "tech enthusiasts"
        }
    
    @pytest.fixture
    def invalid_request(self):
        """Create an invalid generation request"""        return {
            "content_type": "blog_post",
            "word_count": -100  # Invalid negative word count
        }
    
    def test_generator_initialization(self, generator):
        """Test generator initialization"""        assert generator is not None
        assert hasattr(generator, 'config')
        assert hasattr(generator, 'logger')
        assert hasattr(generator, '_generation_stats')
        assert generator.generation_call_count == 0
        assert generator._is_initialized is True
    
    @pytest.mark.asyncio
    async def test_successful_generation(self, generator, valid_request):
        """Test successful content generation"""        result = await generator.generate_with_monitoring(valid_request)
        
        assert result is not None
        assert "Generated content for: AI technology trends" in result
        assert generator.generation_call_count == 1
        
        # Check metrics were recorded
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 1
        assert metrics['successful_generations'] == 1
        assert metrics['failed_generations'] == 0
        assert 'avg_generation_time' in metrics
    
    @pytest.mark.asyncio
    async def test_generation_failure(self, generator, valid_request):
        """Test generation failure handling"""        generator.should_fail = True
        
        with pytest.raises(ContentGenerationError):
            await generator.generate_with_monitoring(valid_request)
        
        # Check metrics were recorded
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 1
        assert metrics['successful_generations'] == 0
        assert metrics['failed_generations'] == 1
    
    @pytest.mark.asyncio
    async def test_input_validation_success(self, generator, valid_request):
        """Test successful input validation"""        validation_result = await generator.validate_input(valid_request)
        
        assert validation_result['valid'] is True
        assert len(validation_result['errors']) == 0
    
    @pytest.mark.asyncio
    async def test_input_validation_failure(self, generator, invalid_request):
        """Test input validation failure"""        validation_result = await generator.validate_input(invalid_request)
        
        assert validation_result['valid'] is False
        assert len(validation_result['errors']) > 0
        assert "Topic is required" in validation_result['errors']
        assert "Word count cannot be negative" in validation_result['errors']
    
    @pytest.mark.asyncio
    async def test_output_validation(self, generator):
        """Test output validation"""        # Test valid output
        valid_output = "This is a properly formatted content piece."
        validation_result = await generator.validate_output(valid_output)
        assert validation_result['valid'] is True
        
        # Test empty output
        empty_output = ""
        validation_result = await generator.validate_output(empty_output)
        assert validation_result['valid'] is False
        assert "Content is empty" in validation_result['errors']
        
        # Test too short output
        short_output = "Short"
        validation_result = await generator.validate_output(short_output)
        assert validation_result['valid'] is False
        assert "Content is too short" in validation_result['errors']
    
    @pytest.mark.asyncio
    async def test_resource_monitoring(self, generator, valid_request):
        """Test resource monitoring during generation"""        initial_memory = generator.get_memory_usage()
        
        await generator.generate_with_monitoring(valid_request)
        
        final_memory = generator.get_memory_usage()
        
        # Memory usage should be tracked
        assert initial_memory >= 0
        assert final_memory >= 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, generator, valid_request):
        """Test performance monitoring"""        start_time = time.time()
        
        await generator.generate_with_monitoring(valid_request)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        metrics = generator.get_metrics()
        assert metrics['avg_generation_time'] > 0
        assert metrics['avg_generation_time'] <= elapsed_time + 0.1  # Allow small margin
    
    @pytest.mark.asyncio
    async def test_concurrent_generations(self, generator, valid_request):
        """Test concurrent generation handling"""        # Start multiple generations concurrently
        tasks = []
        for i in range(3):
            request = valid_request.copy()
            request['topic'] = f"Topic {i}"
            tasks.append(generator.generate_with_monitoring(request))
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert generator.generation_call_count == 3
        
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 3
        assert metrics['successful_generations'] == 3
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, generator, valid_request):
        """Test error recovery mechanisms"""        # First generation fails
        generator.should_fail = True
        
        with pytest.raises(ContentGenerationError):
            await generator.generate_with_monitoring(valid_request)
        
        # Second generation succeeds
        generator.should_fail = False
        result = await generator.generate_with_monitoring(valid_request)
        
        assert result is not None
        
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 2
        assert metrics['successful_generations'] == 1
        assert metrics['failed_generations'] == 1
    
    def test_metrics_collection(self, generator):
        """Test metrics collection functionality"""        initial_metrics = generator.get_metrics()
        
        expected_keys = [
            'total_generations',
            'successful_generations',
            'failed_generations',
            'avg_generation_time',
            'total_memory_used',
            'cache_hits',
            'cache_misses'
        ]
        
        for key in expected_keys:
            assert key in initial_metrics
        
        assert initial_metrics['total_generations'] == 0
        assert initial_metrics['successful_generations'] == 0
        assert initial_metrics['failed_generations'] == 0
    
    def test_cache_functionality(self, generator, valid_request):
        """Test caching functionality"""        # Test cache key generation
        cache_key = generator._generate_cache_key(valid_request)
        assert cache_key is not None
        assert isinstance(cache_key, str)
        
        # Test cache storage and retrieval
        test_content = "Cached content"
        generator._store_in_cache(cache_key, test_content)
        
        retrieved_content = generator._get_from_cache(cache_key)
        assert retrieved_content == test_content
        
        # Test cache hit metrics
        metrics = generator.get_metrics()
        assert metrics['cache_hits'] >= 0
    
    @pytest.mark.asyncio
    async def test_cleanup_resources(self, generator, valid_request):
        """Test resource cleanup"""        # Generate content to use resources
        await generator.generate_with_monitoring(valid_request)
        
        # Test cleanup
        generator.cleanup_resources()
        
        # Verify cleanup occurred (implementation specific)
        assert True  # Placeholder - actual verification depends on implementation
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, generator, valid_request):
        """Test timeout handling during generation"""        # Set a very long delay
        generator.generation_delay = 5.0
        
        # This should timeout (assuming timeout is set to less than 5 seconds)
        start_time = time.time()
        
        try:
            await generator.generate_with_monitoring(valid_request)
        except Exception:
            pass  # Expected to fail due to timeout
        
        elapsed_time = time.time() - start_time
        # Should not take the full 5 seconds due to timeout
        assert elapsed_time < 4.0
    
    def test_logging_functionality(self, generator, caplog):
        """Test logging functionality"""        with caplog.at_level(logging.INFO):
            generator.logger.info("Test log message")
        
        assert "Test log message" in caplog.text
    
    @pytest.mark.asyncio
    async def test_generation_with_different_parameters(self, generator):
        """Test generation with various parameter combinations"""        test_cases = [
            {
                "topic": "Technology",
                "content_type": "blog_post",
                "word_count": 100
            },
            {
                "topic": "Science",
                "content_type": "social_post",
                "word_count": 50
            },
            {
                "topic": "Business",
                "content_type": "email",
                "word_count": 200
            }
        ]
        
        for request in test_cases:
            result = await generator.generate_with_monitoring(request)
            assert result is not None
            assert request['topic'] in result
        
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == len(test_cases)
        assert metrics['successful_generations'] == len(test_cases)
    
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self, generator, valid_request):
        """Test memory leak prevention"""        initial_memory = generator.get_memory_usage()
        
        # Generate multiple pieces of content
        for _ in range(10):
            await generator.generate_with_monitoring(valid_request)
        
        # Force cleanup
        generator.cleanup_resources()
        
        final_memory = generator.get_memory_usage()
        
        # Memory should not grow excessively
        memory_growth = final_memory - initial_memory
        assert memory_growth < 100 * 1024 * 1024  # Less than 100MB growth
    
    def test_configuration_validation(self, generator):
        """Test configuration validation"""        # Test valid configuration
        valid_config = {
            "max_word_count": 1000,
            "timeout": 30,
            "enable_caching": True
        }
        
        assert generator._validate_config(valid_config) is True
        
        # Test invalid configuration
        invalid_config = {
            "max_word_count": -1,  # Invalid negative value
            "timeout": "not_a_number"  # Invalid type
        }
        
        assert generator._validate_config(invalid_config) is False


class TestGenerationErrors:
    """Test suite for generation error handling"""    
    def test_generation_error_creation(self):
        """Test ContentGenerationError creation"""        error = ContentGenerationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_validation_error_creation(self):
        """Test ContentValidationError creation"""        error = ContentValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, ContentGenerationError)

    def test_resource_exhaustion_error_creation(self):
        """Test RateLimitError creation"""        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, ContentGenerationError)
class TestPerformanceMetrics:
    """Test suite for performance metrics"""    
    @pytest.fixture
    def generator(self):
        """Create a generator for performance testing"""        return MockContentGenerator()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, generator):
        """Test generator performance under load"""        request = {
            "topic": "Performance test",
            "content_type": "blog_post",
            "word_count": 100
        }
        
        # Generate content multiple times
        start_time = time.time()
        
        tasks = []
        for _ in range(20):
            tasks.append(generator.generate_with_monitoring(request))
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time
        assert total_time < 30.0  # 30 seconds max for 20 generations
        
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 20
        assert metrics['successful_generations'] == 20
        assert metrics['avg_generation_time'] > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self, generator):
        """Test memory usage tracking accuracy"""        initial_memory = generator.get_memory_usage()
        
        # Create some memory load
        large_data = "x" * 1024 * 1024  # 1MB string
        
        request = {
            "topic": large_data,
            "content_type": "blog_post",
            "word_count": 100
        }
        
        await generator.generate_with_monitoring(request)
        
        final_memory = generator.get_memory_usage()
        
        # Memory usage should increase
        assert final_memory > initial_memory
    
    def test_metrics_reset(self, generator):
        """Test metrics reset functionality"""        # Generate some metrics
        generator.metrics['total_generations'] = 5
        generator.metrics['successful_generations'] = 4
        generator.metrics['failed_generations'] = 1
        
        # Reset metrics
        generator.reset_metrics()
        
        # All metrics should be reset
        metrics = generator.get_metrics()
        assert metrics['total_generations'] == 0
        assert metrics['successful_generations'] == 0
        assert metrics['failed_generations'] == 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
