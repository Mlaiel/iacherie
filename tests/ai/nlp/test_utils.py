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

"""
Comprehensive Tests for NLP Utils Module

Industrial-grade tests for NLP utility functions, helpers, and shared components
with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, List, Any, Optional
import logging

from ai.nlp.utils import (
    TextCleaner, TextAnalyzer, PlatformValidator, HashGenerator,
    DateTimeUtils, PerformanceUtils, Platform, ContentType, Language,
    TextStats, PlatformLimits, ValidationResult
)

logger = logging.getLogger(__name__)

class TestPlatform:
    """
Test Platform enumeration and utilities"""
    
    def test_platform_enum_values(self):
        """
Test platform enum values"""
        assert Platform.INSTAGRAM.value == 'instagram'
        assert Platform.TWITTER.value == 'twitter'
        assert Platform.LINKEDIN.value == 'linkedin'
        assert Platform.YOUTUBE.value == 'youtube'
        assert Platform.TIKTOK.value == 'tiktok'
        assert Platform.FACEBOOK.value == 'facebook'
    
    def test_platform_from_string(self):
        """
Test creating platform from string"""
        platforms = ['instagram', 'twitter', 'linkedin', 'youtube', 'tiktok']
        
        for platform_str in platforms:
            platform = Platform(platform_str)
            assert platform.value == platform_str
    
    def test_platform_properties(self):
        """
Test platform-specific properties"""
        # Instagram properties
        instagram_props = Platform.INSTAGRAM.get_properties()
        assert 'character_limit' in instagram_props
        assert 'supports_hashtags' in instagram_props
        assert 'supports_mentions' in instagram_props
        assert instagram_props['supports_hashtags'] is True
        
        # Twitter properties
        twitter_props = Platform.TWITTER.get_properties()
        assert twitter_props['character_limit'] == 280
        assert twitter_props['supports_threads'] is True
        
        # LinkedIn properties
        linkedin_props = Platform.LINKEDIN.get_properties()
        assert linkedin_props['professional_platform'] is True
        assert linkedin_props['supports_articles'] is True

class TestLanguage:
    """
Test Language enumeration and utilities"""
    
    def test_language_enum_values(self):
        """
Test language enum values"""
        assert Language.ENGLISH.value == 'english'
        assert Language.GERMAN.value == 'german'
        assert Language.FRENCH.value == 'french'
        assert Language.SPANISH.value == 'spanish'
        assert Language.ITALIAN.value == 'italian'
    
    def test_language_iso_codes(self):
        """
Test language ISO codes"""
        assert Language.ENGLISH.iso_code() == 'en'
        assert Language.GERMAN.iso_code() == 'de'
        assert Language.FRENCH.iso_code() == 'fr'
        assert Language.SPANISH.iso_code() == 'es'
        assert Language.ITALIAN.iso_code() == 'it'
    
    def test_language_from_iso_code(self):
        """
Test creating language from ISO code"""
        test_cases = [
            ('en', Language.ENGLISH),
            ('de', Language.GERMAN),
            ('fr', Language.FRENCH),
            ('es', Language.SPANISH),
            ('it', Language.ITALIAN)
        ]
        
        for iso_code, expected_language in test_cases:
            language = Language.from_iso_code(iso_code)
            assert language == expected_language
    
    def test_language_properties(self):
        """
Test language-specific properties"""
        # English properties
        en_props = Language.ENGLISH.get_properties()
        assert 'writing_direction' in en_props
        assert 'character_encoding' in en_props
        assert en_props['writing_direction'] == 'ltr'
        
        # German properties
        de_props = Language.GERMAN.get_properties()
        assert de_props['has_compound_words'] is True
        assert de_props['case_sensitive'] is True

class TestContentType:
    """
Test ContentType enumeration and utilities"""
    
    def test_content_type_enum_values(self):
        """
Test content type enum values"""
        assert ContentType.POST.value == 'post'
        assert ContentType.STORY.value == 'story'
        assert ContentType.REEL.value == 'reel'
        assert ContentType.THREAD.value == 'thread'
        assert ContentType.ARTICLE.value == 'article'
        assert ContentType.CAPTION.value == 'caption'
    
    def test_content_type_properties(self):
        """
Test content type properties"""
        # Post properties
        post_props = ContentType.POST.get_properties()
        assert 'is_ephemeral' in post_props
        assert 'supports_comments' in post_props
        assert post_props['is_ephemeral'] is False
        
        # Story properties
        story_props = ContentType.STORY.get_properties()
        assert story_props['is_ephemeral'] is True
        assert story_props['duration_hours'] == 24
        
        # Thread properties
        thread_props = ContentType.THREAD.get_properties()
        assert thread_props['supports_continuation'] is True

class TestTextProcessor:
    """
Test text processing utilities"""
    
    @pytest.mark.asyncio
    async def test_text_cleaning(self):
        """
Test text cleaning functionality"""
        processor = TextProcessor()
        
        test_cases = [
            {
                'input': '  This is a test with extra   spaces  and\nnewlines\t\t',
                'expected': 'This is a test with extra spaces and newlines',
                'options': {'normalize_whitespace': True}
            },
            {
                'input': 'Text with MIXED case AND inconsistent Formatting',
                'expected': 'text with mixed case and inconsistent formatting',
                'options': {'lowercase': True}
            },
            {
                'input': 'Remove these numbers: 123456 and special chars: !@#$%',
                'expected': 'Remove these numbers:  and special chars: ',
                'options': {'remove_numbers': True, 'remove_special_chars': True}
            }
        ]
        
        for case in test_cases:
            cleaned = await processor.clean_text(
                text=case['input'],
                options=case['options']
            )
            
            assert cleaned == case['expected']
    
    @pytest.mark.asyncio
    async def test_text_tokenization(self):
        """
Test text tokenization"""
        processor = TextProcessor()
        
        test_text = "This is a sample text for tokenization testing."
        
        # Word tokenization
        word_tokens = await processor.tokenize_words(text=test_text)
        expected_words = ['This', 'is', 'a', 'sample', 'text', 'for', 'tokenization', 'testing', '.']
        assert word_tokens == expected_words
        
        # Sentence tokenization
        sentence_text = "First sentence. Second sentence! Third sentence?"
        sentence_tokens = await processor.tokenize_sentences(text=sentence_text)
        assert len(sentence_tokens) == 3
        assert 'First sentence.' in sentence_tokens
        assert 'Second sentence!' in sentence_tokens
        assert 'Third sentence?' in sentence_tokens
    
    @pytest.mark.asyncio
    async def test_text_normalization(self):
        """Test text normalization"""
        processor = TextProcessor()
        
        test_cases = [
            {
                'input': 'café naïve résumé',
                'expected': 'cafe naive resume',
                'options': {'remove_accents': True}
            },
            {
                'input': 'u r gr8! luv ur work 😍',
                'expected': 'you are great! love your work 😍',
                'options': {'expand_contractions': True, 'normalize_slang': True}
            },
            {
                'input': 'Check out https://example.com and email me at test@email.com',
                'expected': 'Check out [URL] and email me at [EMAIL]',
                'options': {'anonymize_urls': True, 'anonymize_emails': True}
            }
        ]
        
        for case in test_cases:
            normalized = await processor.normalize_text(
                text=case['input'],
                options=case['options']
            )
            
            assert normalized == case['expected']
    
    @pytest.mark.asyncio
    async def test_social_media_processing(self):
        """
Test social media specific text processing"""
        processor = TextProcessor()
        
        social_text = "Check out @username's amazing post! #AI #MachineLearning https://example.com 🚀"
        
        # Extract social elements
        social_elements = await processor.extract_social_elements(text=social_text)
        
        assert 'mentions' in social_elements
        assert 'hashtags' in social_elements
        assert 'urls' in social_elements
        assert 'emojis' in social_elements
        
        assert '@username' in social_elements['mentions']
        assert '#AI' in social_elements['hashtags']
        assert '#MachineLearning' in social_elements['hashtags']
        assert 'https://example.com' in social_elements['urls']
        assert '🚀' in social_elements['emojis']
        
        # Clean social text
        cleaned_social = await processor.clean_social_text(
            text=social_text,
            options={
                'preserve_hashtags': True,
                'remove_mentions': True,
                'remove_urls': True,
                'preserve_emojis': True
            }
        )
        
        assert '@username' not in cleaned_social
        assert 'https://example.com' not in cleaned_social
        assert '#AI' in cleaned_social
        assert '🚀' in cleaned_social

class TestDataValidator:
    """Test data validation utilities"""
    
    def test_text_validation(self):
        """
Test text validation"""
        validator = DataValidator()
        
        # Valid text
        valid_result = validator.validate_text(
            text="This is valid text content.",
            constraints={
                'min_length': 5,
                'max_length': 100,
                'allow_empty': False
            }
        )
        
        assert valid_result['is_valid'] is True
        assert len(valid_result['violations']) == 0
        
        # Invalid text (too short)
        invalid_result = validator.validate_text(
            text="Hi",
            constraints={
                'min_length': 10,
                'max_length': 100
            }
        )
        
        assert invalid_result['is_valid'] is False
        assert 'min_length' in str(invalid_result['violations'])
        
        # Invalid text (too long)
        long_text = "A" * 200
        long_result = validator.validate_text(
            text=long_text,
            constraints={'max_length': 100}
        )
        
        assert long_result['is_valid'] is False
        assert 'max_length' in str(long_result['violations'])
    
    def test_platform_content_validation(self):
        """Test platform-specific content validation"""
        validator = DataValidator()
        
        # Twitter content validation
        twitter_text = "This is a tweet that should be under 280 characters for Twitter platform validation."
        
        twitter_validation = validator.validate_platform_content(
            content=twitter_text,
            platform=Platform.TWITTER,
            content_type=ContentType.POST
        )
        
        assert twitter_validation['is_valid'] is True
        
        # Twitter content too long
        long_tweet = "A" * 300  # Over 280 character limit
        
        long_validation = validator.validate_platform_content(
            content=long_tweet,
            platform=Platform.TWITTER,
            content_type=ContentType.POST
        )
        
        assert long_validation['is_valid'] is False
        assert 'character_limit' in str(long_validation['violations'])
    
    def test_language_validation(self):
        """Test language validation"""
        validator = DataValidator()
        
        test_cases = [
            {
                'text': "This is English text.",
                'expected_language': Language.ENGLISH,
                'confidence_threshold': 0.8
            },
            {
                'text': "Das ist deutscher Text.",
                'expected_language': Language.GERMAN,
                'confidence_threshold': 0.8
            },
            {
                'text': "Ceci est du texte français.",
                'expected_language': Language.FRENCH,
                'confidence_threshold': 0.8
            }
        ]
        
        for case in test_cases:
            language_validation = validator.validate_language(
                text=case['text'],
                expected_language=case['expected_language'],
                confidence_threshold=case['confidence_threshold']
            )
            
            assert language_validation['is_valid'] is True
            assert language_validation['detected_language'] == case['expected_language']
            assert language_validation['confidence'] >= case['confidence_threshold']

class TestConfigManager:
    """Test configuration management utilities"""
    
    def test_config_loading(self):
        """
Test configuration loading"""
        config_manager = ConfigManager()
        
        # Test default configuration
        default_config = config_manager.get_default_config()
        
        assert 'nlp_settings' in default_config
        assert 'platform_settings' in default_config
        assert 'performance_settings' in default_config
        
        # Test environment-specific configuration
        prod_config = config_manager.get_config(environment='production')
        dev_config = config_manager.get_config(environment='development')
        
        assert prod_config['performance_settings']['cache_enabled'] is True
        assert dev_config['nlp_settings']['debug_mode'] is True
    
    def test_config_validation(self):
        """
Test configuration validation"""
        config_manager = ConfigManager()
        
        # Valid configuration
        valid_config = {
            'nlp_settings': {
                'default_language': 'english',
                'max_text_length': 10000
            },
            'platform_settings': {
                'supported_platforms': ['instagram', 'twitter']
            }
        }
        
        validation_result = config_manager.validate_config(valid_config)
        assert validation_result['is_valid'] is True
        
        # Invalid configuration
        invalid_config = {
            'nlp_settings': {
                'default_language': 'invalid_language',
                'max_text_length': -1
            }
        }
        
        invalid_result = config_manager.validate_config(invalid_config)
        assert invalid_result['is_valid'] is False
    
    def test_config_merging(self):
        """
Test configuration merging"""
        config_manager = ConfigManager()
        
        base_config = {
            'setting1': 'value1',
            'setting2': {'nested1': 'nested_value1'}
        }
        
        override_config = {
            'setting2': {'nested2': 'nested_value2'},
            'setting3': 'value3'
        }
        
        merged_config = config_manager.merge_configs(base_config, override_config)
        
        assert merged_config['setting1'] == 'value1'
        assert merged_config['setting2']['nested1'] == 'nested_value1'
        assert merged_config['setting2']['nested2'] == 'nested_value2'
        assert merged_config['setting3'] == 'value3'

class TestCacheManager:
    """
Test caching utilities"""
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """
Test basic cache operations"""
        cache_manager = CacheManager()
        
        # Test cache set and get
        await cache_manager.set('test_key', 'test_value', ttl=60)
        
        cached_value = await cache_manager.get('test_key')
        assert cached_value == 'test_value'
        
        # Test cache expiration
        await cache_manager.set('expire_key', 'expire_value', ttl=1)
        await asyncio.sleep(2)  # Wait for expiration
        
        expired_value = await cache_manager.get('expire_key')
        assert expired_value is None
        
        # Test cache delete
        await cache_manager.set('delete_key', 'delete_value')
        await cache_manager.delete('delete_key')
        
        deleted_value = await cache_manager.get('delete_key')
        assert deleted_value is None
    
    @pytest.mark.asyncio
    async def test_cache_patterns(self):
        """
Test cache patterns and strategies"""
        cache_manager = CacheManager()
        
        # Test cache-aside pattern
        def expensive_operation(key):
            return f"computed_value_for_{key}"
        
        async def get_with_cache(key):
            cached = await cache_manager.get(key)
            if cached is not None:
                return cached
            
            computed = expensive_operation(key)
            await cache_manager.set(key, computed, ttl=300)
            return computed
        
        # First call should compute and cache
        result1 = await get_with_cache('pattern_test')
        assert result1 == 'computed_value_for_pattern_test'
        
        # Second call should return cached value
        result2 = await get_with_cache('pattern_test')
        assert result2 == result1
        
        # Test batch cache operations
        batch_data = {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }
        
        await cache_manager.set_batch(batch_data, ttl=60)
        
        batch_results = await cache_manager.get_batch(['key1', 'key2', 'key3'])
        
        assert batch_results['key1'] == 'value1'
        assert batch_results['key2'] == 'value2'
        assert batch_results['key3'] == 'value3'

class TestPerformanceProfiler:
    """Test performance profiling utilities"""
    
    @pytest.mark.asyncio
    async def test_execution_timing(self):
        """
Test execution timing"""
        profiler = PerformanceProfiler()
        
        # Test function timing
        @profiler.time_execution
        async def sample_async_function():
            await asyncio.sleep(0.1)
            return "completed"
        
        result = await sample_async_function()
        assert result == "completed"
        
        # Get timing statistics
        stats = profiler.get_statistics('sample_async_function')
        assert 'execution_count' in stats
        assert 'total_time' in stats
        assert 'average_time' in stats
        assert stats['execution_count'] == 1
        assert stats['average_time'] >= 0.1
    
    @pytest.mark.asyncio
    async def test_memory_profiling(self):
        """Test memory profiling"""
        profiler = PerformanceProfiler()
        
        # Start memory profiling
        profiler.start_memory_profiling()
        
        # Perform memory-intensive operations
        large_data = ['x' * 1000 for _ in range(1000)]
        
        memory_usage = profiler.get_memory_usage()
        assert 'current_usage' in memory_usage
        assert 'peak_usage' in memory_usage
        assert memory_usage['current_usage'] > 0
        
        # Clean up
        del large_data
        profiler.stop_memory_profiling()
    
    def test_performance_metrics(self):
        """
Test performance metrics collection"""
        profiler = PerformanceProfiler()
        
        # Record custom metrics
        profiler.record_metric('api_calls', 1)
        profiler.record_metric('api_calls', 1)
        profiler.record_metric('api_calls', 1)
        
        profiler.record_metric('response_time', 0.5)
        profiler.record_metric('response_time', 0.7)
        profiler.record_metric('response_time', 0.3)
        
        # Get metrics summary
        metrics = profiler.get_metrics_summary()
        
        assert 'api_calls' in metrics
        assert 'response_time' in metrics
        
        api_calls_metrics = metrics['api_calls']
        assert api_calls_metrics['count'] == 3
        assert api_calls_metrics['total'] == 3
        
        response_time_metrics = metrics['response_time']
        assert response_time_metrics['count'] == 3
        assert response_time_metrics['average'] == 0.5

class TestLogger:
    """
Test logging utilities"""
    
    def test_logger_configuration(self):
        """
Test logger configuration"""
        logger_util = Logger('test_nlp_logger')
        
        # Test different log levels
        logger_util.debug("Debug message")
        logger_util.info("Info message")
        logger_util.warning("Warning message")
        logger_util.error("Error message")
        
        # Test structured logging
        logger_util.log_structured({
            'event': 'nlp_processing',
            'text_length': 150,
            'processing_time': 0.8,
            'platform': 'instagram'
        })
        
        # Test performance logging
        logger_util.log_performance({
            'operation': 'sentiment_analysis',
            'duration': 0.5,
            'input_size': 200,
            'success': True
        })
    
    def test_logger_context(self):
        """Test logger context management"""
        logger_util = Logger('test_context_logger')
        
        # Set logging context
        with logger_util.context(user_id='user123', session_id='session456'):
            logger_util.info("Processing request")
            logger_util.debug("Debug info within context")
        
        # Context should be cleared after with block
        logger_util.info("Processing outside context")

class TestErrorHandler:
    """Test error handling utilities"""
    
    @pytest.mark.asyncio
    async def test_error_handling_decorator(self):
        """
Test error handling decorator"""
        error_handler = ErrorHandler()
        
        @error_handler.handle_errors
        async def function_that_might_fail(should_fail=False):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # Test successful execution
        result = await function_that_might_fail(should_fail=False)
        assert result == "success"
        
        # Test error handling
        result = await function_that_might_fail(should_fail=True)
        assert result is None  # Should return None on error by default
        
        # Check error was logged
        error_logs = error_handler.get_error_logs()
        assert len(error_logs) > 0
        assert 'ValueError' in str(error_logs[-1])
    
    def test_error_categorization(self):
        """Test error categorization"""
        error_handler = ErrorHandler()
        
        # Test different error types
        errors = [
            ValueError("Invalid input"),
            TypeError("Type mismatch"),
            ConnectionError("Network error"),
            KeyError("Missing key")
        ]
        
        for error in errors:
            category = error_handler.categorize_error(error)
            
            assert 'error_type' in category
            assert 'severity' in category
            assert 'category' in category
            
            if isinstance(error, ValueError):
                assert category['category'] == 'validation_error'
            elif isinstance(error, ConnectionError):
                assert category['category'] == 'network_error'
    
    def test_error_recovery(self):
        """Test error recovery strategies"""
        error_handler = ErrorHandler()
        
        # Test retry mechanism
        attempt_count = 0
        
        def unreliable_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = error_handler.retry_on_error(
            func=unreliable_function,
            max_retries=3,
            retry_delay=0.1
        )
        
        assert result == "success"
        assert attempt_count == 3
    
    def test_error_reporting(self):
        """Test error reporting"""
        error_handler = ErrorHandler()
        
        # Simulate various errors
        try:
            raise ValueError("Test validation error")
        except ValueError as e:
            error_handler.report_error(e, context={'operation': 'validation'})
        
        try:
            raise ConnectionError("Test connection error")
        except ConnectionError as e:
            error_handler.report_error(e, context={'operation': 'api_call'})
        
        # Get error report
        error_report = error_handler.generate_error_report(time_period='1h')
        
        assert 'total_errors' in error_report
        assert 'error_types' in error_report
        assert 'error_contexts' in error_report
        assert error_report['total_errors'] == 2

class TestUtilsIntegration:
    """Test integration between different utility components"""
    
    @pytest.mark.asyncio
    async def test_complete_text_processing_pipeline(self):
        """
Test complete text processing pipeline"""
        # Initialize components
        processor = TextProcessor()
        validator = DataValidator()
        cache_manager = CacheManager()
        profiler = PerformanceProfiler()
        
        # Test input
        raw_text = "  Check out @user's post about #AI and #MachineLearning! https://example.com 🚀  "
        
        # Complete processing pipeline
        @profiler.time_execution
        async def process_text_pipeline(text):
            # Validate input
            validation = validator.validate_text(text, {'min_length': 1})
            if not validation['is_valid']:
                return None
            
            # Check cache
            cache_key = f"processed_{hash(text)}"
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Process text
            cleaned = await processor.clean_text(text, {'normalize_whitespace': True})
            social_elements = await processor.extract_social_elements(cleaned)
            normalized = await processor.normalize_text(cleaned, {'remove_accents': True})
            
            result = {
                'original': text,
                'cleaned': cleaned,
                'normalized': normalized,
                'social_elements': social_elements
            }
            
            # Cache result
            await cache_manager.set(cache_key, result, ttl=300)
            
            return result
        
        # Process text
        result = await process_text_pipeline(raw_text)
        
        assert result is not None
        assert 'original' in result
        assert 'cleaned' in result
        assert 'normalized' in result
        assert 'social_elements' in result
        
        # Verify social elements extraction
        social_elements = result['social_elements']
        assert '@user' in social_elements['mentions']
        assert '#AI' in social_elements['hashtags']
        assert 'https://example.com' in social_elements['urls']
        assert '🚀' in social_elements['emojis']
        
        # Verify caching worked by running again
        cached_result = await process_text_pipeline(raw_text)
        assert cached_result == result
        
        # Check performance metrics
        stats = profiler.get_statistics('process_text_pipeline')
        assert stats['execution_count'] == 2  # Original + cached call
    
    def test_error_handling_with_logging(self):
        """Test error handling integration with logging"""
        error_handler = ErrorHandler()
        logger_util = Logger('integration_test')
        
        def failing_function():
            raise ValueError("Integration test error")
        
        # Handle error with logging
        try:
            failing_function()
        except Exception as e:
            error_handler.report_error(e, context={'test': 'integration'})
            logger_util.error(f"Handled error: {e}")
        
        # Verify error was properly handled and logged
        error_logs = error_handler.get_error_logs()
        assert len(error_logs) > 0
        
        latest_error = error_logs[-1]
        assert 'ValueError' in str(latest_error)
        assert 'integration' in str(latest_error['context'])

# Performance and stress tests
class TestUtilsPerformance:
    """Test utilities performance under load"""
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """
Test cache performance under load"""
        cache_manager = CacheManager()
        
        # Test cache performance with many operations
        num_operations = 1000
        
        start_time = time.time()
        
        # Batch set operations
        batch_data = {f'key_{i}': f'value_{i}' for i in range(num_operations)}
        await cache_manager.set_batch(batch_data)
        
        # Batch get operations
        keys = [f'key_{i}' for i in range(num_operations)]
        results = await cache_manager.get_batch(keys)
        
        end_time = time.time()
        
        # Verify all operations completed
        assert len(results) == num_operations
        
        # Performance should be reasonable
        total_time = end_time - start_time
        operations_per_second = (num_operations * 2) / total_time  # set + get
        assert operations_per_second > 1000  # Should handle at least 1000 ops/sec
    
    @pytest.mark.asyncio
    async def test_text_processing_performance(self):
        """
Test text processing performance"""
        processor = TextProcessor()
        
        # Generate test data
        test_texts = [f"Sample text {i} for performance testing." for i in range(100)]
        
        start_time = time.time()
        
        # Process all texts
        results = []
        for text in test_texts:
            cleaned = await processor.clean_text(text)
            normalized = await processor.normalize_text(cleaned)
            results.append(normalized)
        
        end_time = time.time()
        
        # Verify processing completed
        assert len(results) == len(test_texts)
        
        # Performance should be reasonable
        total_time = end_time - start_time
        texts_per_second = len(test_texts) / total_time
        assert texts_per_second > 50  # Should process at least 50 texts/sec
