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
Comprehensive Tests for NLP Core Module

Industrial-grade tests for AdvancedNLPEngine covering all functionality
with real implementations, performance benchmarks, and edge cases.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - Unauthorized use prohibited 
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import json
from typing import Dict, List, Any
from unittest.mock import patch, AsyncMock
import logging

from ai.nlp.core import AdvancedNLPEngine, NLPTask, NLPResult
from ai.nlp.utils import Platform, Language, ContentType

logger = logging.getLogger(__name__)

class TestAdvancedNLPEngine:
    """Comprehensive tests for AdvancedNLPEngine"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, nlp_engine):
        """Test engine initialization and configuration"""
        assert nlp_engine is not None
        assert hasattr(nlp_engine, 'config')
        assert hasattr(nlp_engine, 'models')
        assert hasattr(nlp_engine, 'pipelines')
        assert hasattr(nlp_engine, 'tokenizers')
        
        # Test configuration validation
        config = nlp_engine.config
        assert 'supported_languages' in config
        assert 'batch_size' in config
        assert 'device' in config
        
        # Verify essential languages are supported
        supported_languages = config['supported_languages']
        essential_languages = ['en', 'de', 'fr', 'es']
        for lang in essential_languages:
            assert lang in supported_languages

    @pytest.mark.asyncio
    async def test_basic_text_processing(self, nlp_engine, sample_texts):
        """Test basic text processing functionality"""
        for language, texts in sample_texts.items():
            for text in texts[:2]:  # Test first 2 texts for each language
                request = NLPRequest(
                    text=text,
                    language=language[:2],  # Convert to language code
                    platform=Platform.INSTAGRAM,
                    content_type=ContentType.POST,
                    processing_mode=ProcessingMode.STANDARD
                )
                
                response = await nlp_engine.process_text(request)
                
                # Verify response structure
                assert isinstance(response, NLPResponse)
                assert response.success is True
                assert response.processed_text is not None
                assert response.language_detected is not None
                assert response.sentiment is not None
                assert response.processing_time > 0
                
                # Verify sentiment analysis
                sentiment = response.sentiment
                assert 'polarity' in sentiment
                assert 'confidence' in sentiment
                assert -1.0 <= sentiment['polarity'] <= 1.0
                assert 0.0 <= sentiment['confidence'] <= 1.0

    @pytest.mark.asyncio
    async def test_multilingual_processing(self, nlp_engine, sample_texts):
        """Test multilingual text processing capabilities"""
        for language, texts in sample_texts.items():
            text = texts[0]
            
            request = NLPRequest(
                text=text,
                language=language[:2],
                platform=Platform.TIKTOK,
                content_type=ContentType.VIDEO,
                processing_mode=ProcessingMode.ENHANCED
            )
            
            response = await nlp_engine.process_text(request)
            
            # Verify language detection
            assert response.language_detected is not None
            detected_lang = response.language_detected
            
            # Should detect correct language (allow some variance)
            expected_lang = language[:2]
            if expected_lang == 'en':
                assert detected_lang in ['en', 'english']
            elif expected_lang == 'de':
                assert detected_lang in ['de', 'german']
            elif expected_lang == 'fr':
                assert detected_lang in ['fr', 'french']
            elif expected_lang == 'es':
                assert detected_lang in ['es', 'spanish']
            
            # Verify multilingual features
            assert response.keywords is not None
            assert len(response.keywords) > 0
            assert response.entities is not None

    @pytest.mark.asyncio
    async def test_platform_specific_processing(self, nlp_engine, sample_platform_content):
        """Test platform-specific content processing"""
        platforms_to_test = [Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER, Platform.YOUTUBE]
        
        for platform in platforms_to_test:
            # Get platform-specific content
            platform_key = platform.value
            if platform_key in sample_platform_content:
                content_samples = sample_platform_content[platform_key]
                
                for content_type, text in content_samples.items():
                    request = NLPRequest(
                        text=text,
                        language='en',
                        platform=platform,
                        content_type=ContentType.POST,
                        processing_mode=ProcessingMode.PLATFORM_OPTIMIZED
                    )
                    
                    response = await nlp_engine.process_text(request)
                    
                    # Verify platform-specific optimization
                    assert response.success is True
                    assert response.platform_suggestions is not None
                    assert response.optimization_score is not None
                    assert 0.0 <= response.optimization_score <= 1.0
                    
                    # Platform-specific validations
                    if platform == Platform.TWITTER:
                        # Twitter has character limits
                        if len(text) > 280:
                            assert 'character_limit' in response.platform_suggestions
                    
                    elif platform == Platform.INSTAGRAM:
                        # Instagram should optimize hashtags
                        if '#' in text:
                            assert 'hashtag_optimization' in response.metadata
                    
                    elif platform == Platform.TIKTOK:
                        # TikTok should focus on trending elements
                        assert 'trending_score' in response.metadata

    @pytest.mark.asyncio
    async def test_processing_modes(self, nlp_engine, sample_texts):
        """Test different processing modes"""
        text = sample_texts['english'][0]
        
        modes_to_test = [
            ProcessingMode.FAST,
            ProcessingMode.STANDARD,
            ProcessingMode.ENHANCED,
            ProcessingMode.COMPREHENSIVE
        ]
        
        processing_times = {}
        
        for mode in modes_to_test:
            request = NLPRequest(
                text=text,
                language='en',
                platform=Platform.INSTAGRAM,
                content_type=ContentType.POST,
                processing_mode=mode
            )
            
            start_time = time.time()
            response = await nlp_engine.process_text(request)
            processing_time = time.time() - start_time
            
            processing_times[mode.value] = processing_time
            
            # Verify basic response structure
            assert response.success is True
            assert response.processed_text is not None
            
            # Mode-specific validations
            if mode == ProcessingMode.FAST:
                # Fast mode should have minimal analysis
                assert response.processing_time < 0.5  # Should be fast
            
            elif mode == ProcessingMode.COMPREHENSIVE:
                # Comprehensive mode should have extensive analysis
                assert response.keywords is not None
                assert response.entities is not None
                assert response.sentiment is not None
                assert response.readability_score is not None
                assert response.seo_recommendations is not None
        
        # Verify processing time progression (generally faster modes should be quicker)
        assert processing_times['fast'] <= processing_times['comprehensive'] * 2

    @pytest.mark.asyncio
    async def test_batch_processing(self, nlp_engine, performance_test_data):
        """Test batch processing capabilities"""
        texts = performance_test_data['small_batch']
        
        requests = [
            NLPRequest(
                text=text,
                language='en',
                platform=Platform.INSTAGRAM,
                content_type=ContentType.POST,
                processing_mode=ProcessingMode.STANDARD
            )
            for text in texts
        ]
        
        start_time = time.time()
        responses = await nlp_engine.process_batch(requests)
        batch_time = time.time() - start_time
        
        # Verify batch processing results
        assert len(responses) == len(requests)
        assert all(response.success for response in responses)
        
        # Batch processing should be efficient
        avg_time_per_item = batch_time / len(texts)
        assert avg_time_per_item < 1.0  # Should process each item in under 1 second

    @pytest.mark.asyncio
    async def test_semantic_analysis(self, nlp_engine, sample_texts):
        """Test semantic analysis capabilities"""
        text = sample_texts['english'][2]  # Text with mentions and hashtags
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'semantic_analysis': True,
                'entity_extraction': True,
                'sentiment_analysis': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Verify semantic analysis results
        assert response.entities is not None
        assert len(response.entities) > 0
        
        # Check for specific entity types
        entity_types = [entity.get('type') for entity in response.entities]
        assert any(entity_type in ['PERSON', 'ORG', 'PRODUCT'] for entity_type in entity_types)
        
        # Verify semantic similarity if implemented
        if hasattr(response, 'semantic_features'):
            assert response.semantic_features is not None

    @pytest.mark.asyncio
    async def test_brand_voice_analysis(self, nlp_engine, sample_social_content):
        """Test brand voice analysis capabilities"""
        instagram_content = sample_social_content['instagram']
        text = instagram_content['post']
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'brand_voice_analysis': True,
                'tone_analysis': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Verify brand voice analysis
        assert response.metadata is not None
        metadata = response.metadata
        
        # Should have tone analysis
        if 'tone_analysis' in metadata:
            tone = metadata['tone_analysis']
            assert 'primary_tone' in tone
            assert 'confidence' in tone
            assert isinstance(tone['primary_tone'], str)
            assert 0.0 <= tone['confidence'] <= 1.0

    @pytest.mark.asyncio
    async def test_collaboration_detection(self, nlp_engine, sample_texts):
        """Test collaboration opportunity detection"""
        # Use text with mentions that might indicate collaborations
        text = sample_texts['english'][2]  # Has @foodlover mention
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'collaboration_detection': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Should detect potential collaborations
        if 'collaboration_opportunities' in response.metadata:
            collab_data = response.metadata['collaboration_opportunities']
            assert isinstance(collab_data, dict)
            
            if 'detected_mentions' in collab_data:
                mentions = collab_data['detected_mentions']
                assert isinstance(mentions, list)

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, nlp_engine, performance_test_data, benchmark_config):
        """Test performance benchmarks"""
        # Test single text processing time
        text = performance_test_data['small_batch'][0]
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.STANDARD
        )
        
        start_time = time.time()
        response = await nlp_engine.process_text(request)
        processing_time = time.time() - start_time
        
        # Verify performance requirements
        max_time = benchmark_config['max_processing_time']
        assert processing_time < max_time, f"Processing took {processing_time:.3f}s, max allowed: {max_time}s"
        
        # Test batch throughput
        batch_texts = performance_test_data['medium_batch'][:20]  # Test with 20 items
        
        requests = [
            NLPRequest(
                text=text,
                language='en',
                platform=Platform.INSTAGRAM,
                content_type=ContentType.POST,
                processing_mode=ProcessingMode.FAST
            )
            for text in batch_texts
        ]
        
        start_time = time.time()
        responses = await nlp_engine.process_batch(requests)
        batch_time = time.time() - start_time
        
        throughput = len(batch_texts) / batch_time
        min_throughput = benchmark_config['throughput_threshold']
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f} items/s, min required: {min_throughput}"

    @pytest.mark.asyncio
    async def test_error_handling(self, nlp_engine):
        """Test error handling and edge cases"""
        # Test empty text
        request = NLPTask(
            content="",
            language='en',
            task_type='analysis'
        )
        
        response = await nlp_engine.process_content(request)
        # Should handle gracefully
        assert response is not None
        
        # Test very long text
        long_text = "This is a very long text. " * 1000
        
        request = NLPTask(
            content=long_text,
            language='en',
            task_type='analysis'
        )
        
        response = await nlp_engine.process_content(request)
        assert response.success is True
        
        # Test invalid language
        request = NLPTask(
            content="Test text",
            language='invalid',
            task_type='analysis'
        )
        
        response = await nlp_engine.process_content(request)
        # Should default to English or auto-detect
        assert response.language_detected in ['en', 'english']

    @pytest.mark.asyncio
    async def test_text_quality_assessment(self, nlp_engine, sample_social_content):
        """Test text quality assessment capabilities"""
        # Test high-quality content
        high_quality_text = sample_social_content['instagram']['long_caption']
        
        request = NLPRequest(
            text=high_quality_text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'quality_assessment': True,
                'readability_analysis': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Should have quality metrics
        assert response.readability_score is not None
        assert 0.0 <= response.readability_score <= 1.0
        
        if 'quality_score' in response.metadata:
            quality_score = response.metadata['quality_score']
            assert 0.0 <= quality_score <= 1.0

    @pytest.mark.asyncio
    async def test_trend_analysis(self, nlp_engine, sample_social_content):
        """Test trend analysis capabilities"""
        tiktok_content = sample_social_content['tiktok']['video']
        
        request = NLPRequest(
            text=tiktok_content,
            language='en',
            platform=Platform.TIKTOK,
            content_type=ContentType.VIDEO,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'trend_analysis': True,
                'hashtag_analysis': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Should identify trending elements
        if 'trending_elements' in response.metadata:
            trending = response.metadata['trending_elements']
            assert isinstance(trending, dict)
            
            if 'hashtags' in trending:
                trending_hashtags = trending['hashtags']
                assert isinstance(trending_hashtags, list)

    @pytest.mark.asyncio
    async def test_content_optimization(self, nlp_engine, sample_platform_content):
        """Test content optimization recommendations"""
        for platform_name, content_dict in sample_platform_content.items():
            if platform_name == 'instagram':
                platform = Platform.INSTAGRAM
            elif platform_name == 'tiktok':
                platform = Platform.TIKTOK
            elif platform_name == 'twitter':
                platform = Platform.TWITTER
            elif platform_name == 'youtube':
                platform = Platform.YOUTUBE
            else:
                continue
            
            # Test first content item
            content_key = next(iter(content_dict.keys()))
            text = content_dict[content_key]
            
            request = NLPRequest(
                text=text,
                language='en',
                platform=platform,
                content_type=ContentType.POST,
                processing_mode=ProcessingMode.PLATFORM_OPTIMIZED,
                options={
                    'optimization_suggestions': True,
                    'platform_compliance': True
                }
            )
            
            response = await nlp_engine.process_text(request)
            
            # Should have optimization suggestions
            assert response.platform_suggestions is not None
            assert response.optimization_score is not None
            
            # Platform-specific optimizations
            suggestions = response.platform_suggestions
            
            if platform == Platform.TWITTER and len(text) > 280:
                assert any('length' in str(suggestion).lower() for suggestion in suggestions)
            
            if platform == Platform.INSTAGRAM and '#' in text:
                # Should analyze hashtag usage
                assert response.metadata is not None

    @pytest.mark.asyncio
    async def test_memory_management(self, nlp_engine, performance_test_data):
        """Test memory management during processing"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large batch
        large_batch = performance_test_data['large_batch'][:100]  # Test with 100 items
        
        requests = [
            NLPRequest(
                text=text,
                language='en',
                platform=Platform.INSTAGRAM,
                content_type=ContentType.POST,
                processing_mode=ProcessingMode.STANDARD
            )
            for text in large_batch
        ]
        
        responses = await nlp_engine.process_batch(requests)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        max_memory_increase = 256  # MB
        assert memory_increase < max_memory_increase, f"Memory increased by {memory_increase:.1f}MB"
        
        # All requests should be processed successfully
        assert len(responses) == len(requests)
        assert all(response.success for response in responses)

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, nlp_engine, sample_texts):
        """Test concurrent processing capabilities"""
        texts = [text for lang_texts in sample_texts.values() for text in lang_texts[:2]]
        
        async def process_single_text(text, lang='en'):
            request = NLPRequest(
                text=text,
                language=lang,
                platform=Platform.INSTAGRAM,
                content_type=ContentType.POST,
                processing_mode=ProcessingMode.STANDARD
            )
            return await nlp_engine.process_text(request)
        
        # Process texts concurrently
        tasks = [process_single_text(text) for text in texts[:10]]  # Test with 10 concurrent tasks
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # Verify all responses
        assert len(responses) == len(tasks)
        assert all(response.success for response in responses)
        
        # Concurrent processing should be efficient
        expected_sequential_time = len(tasks) * 0.1  # Estimate
        efficiency_ratio = expected_sequential_time / concurrent_time
        assert efficiency_ratio > 1.5, f"Concurrency efficiency: {efficiency_ratio:.2f}x"

    @pytest.mark.asyncio
    async def test_content_fingerprinting(self, nlp_engine, sample_texts):
        """Test content fingerprinting for copyright protection"""
        text = sample_texts['english'][0]
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'generate_fingerprint': True,
                'copyright_check': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Should have fingerprint data
        if 'fingerprint' in response.metadata:
            fingerprint_data = response.metadata['fingerprint']
            assert 'content_hash' in fingerprint_data
            assert 'similarity_hash' in fingerprint_data
            assert isinstance(fingerprint_data['content_hash'], str)
            assert len(fingerprint_data['content_hash']) > 0

    @pytest.mark.asyncio
    async def test_engagement_prediction(self, nlp_engine, sample_social_content):
        """Test engagement prediction capabilities"""
        # Test with Instagram post
        text = sample_social_content['instagram']['post']
        
        request = NLPRequest(
            text=text,
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.ENHANCED,
            options={
                'engagement_prediction': True,
                'virality_analysis': True
            }
        )
        
        response = await nlp_engine.process_text(request)
        
        # Should have engagement predictions
        if 'engagement_prediction' in response.metadata:
            engagement = response.metadata['engagement_prediction']
            assert 'predicted_likes' in engagement or 'engagement_score' in engagement
            
            if 'engagement_score' in engagement:
                score = engagement['engagement_score']
                assert 0.0 <= score <= 1.0

class TestNLPRequestValidation:
    """Test NLP request validation and edge cases"""
    
    def test_request_creation(self):
        """Test NLP request creation and validation"""
        request = NLPRequest(
            text="Test content",
            language='en',
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            processing_mode=ProcessingMode.STANDARD
        )
        
        assert request.text == "Test content"
        assert request.language == 'en'
        assert request.platform == Platform.INSTAGRAM
        assert request.content_type == ContentType.POST
        assert request.processing_mode == ProcessingMode.STANDARD
        assert isinstance(request.options, dict)
        assert isinstance(request.metadata, dict)

    def test_request_with_options(self):
        """Test request with custom options"""
        options = {
            'sentiment_analysis': True,
            'entity_extraction': True,
            'max_keywords': 10
        }
        
        request = NLPRequest(
            text="Test content with options",
            language='en',
            platform=Platform.TIKTOK,
            content_type=ContentType.VIDEO,
            processing_mode=ProcessingMode.ENHANCED,
            options=options
        )
        
        assert request.options == options
        assert request.options['sentiment_analysis'] is True
        assert request.options['max_keywords'] == 10

class TestNLPResponseValidation:
    """Test NLP response validation and structure"""
    
    def test_response_structure(self):
        """Test response structure and required fields"""
        response = NLPResponse(
            success=True,
            processed_text="Processed content",
            language_detected='en',
            processing_time=0.5
        )
        
        assert response.success is True
        assert response.processed_text == "Processed content"
        assert response.language_detected == 'en'
        assert response.processing_time == 0.5
        assert isinstance(response.metadata, dict)

    def test_response_with_analysis_data(self):
        """Test response with comprehensive analysis data"""
        sentiment = {
            'polarity': 0.7,
            'confidence': 0.9,
            'emotions': ['joy', 'excitement']
        }
        
        keywords = ['test', 'content', 'analysis']
        entities = [
            {'text': 'Test Entity', 'type': 'ORG', 'confidence': 0.8}
        ]
        
        response = NLPResponse(
            success=True,
            processed_text="Analyzed content",
            language_detected='en',
            processing_time=1.2,
            sentiment=sentiment,
            keywords=keywords,
            entities=entities,
            readability_score=0.75,
            optimization_score=0.85
        )
        
        assert response.sentiment == sentiment
        assert response.keywords == keywords
        assert response.entities == entities
        assert response.readability_score == 0.75
        assert response.optimization_score == 0.85
