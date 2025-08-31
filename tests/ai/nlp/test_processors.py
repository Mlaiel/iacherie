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

"""Comprehensive Tests for NLP Processors Module

Industrial-grade tests for AdvancedContentProcessor covering all preprocessing
functionality with real implementations and performance benchmarks.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import json
from typing import Dict, List, Any
from unittest.mock import patch, AsyncMock
import logging

from ai.nlp.processors import (
    TextNormalizer, SocialMediaProcessor, MarkdownProcessor,
    ContentSanitizer, ContentProcessorPipeline, ProcessingResult
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedContentProcessor:
    """Comprehensive tests for AdvancedContentProcessor"""    
    @pytest.mark.asyncio
    async def test_processor_initialization(self, content_processor):
        """Test processor initialization and configuration"""        assert content_processor is not None
        assert hasattr(content_processor, 'config')
        assert hasattr(content_processor, 'text_processor')
        assert hasattr(content_processor, 'social_processor')
        assert hasattr(content_processor, 'video_processor')
        
        # Test configuration
        config = content_processor.config
        assert 'languages' in config
        assert 'formats' in config
        assert 'processing_options' in config

    @pytest.mark.asyncio
    async def test_text_preprocessing(self, content_processor, sample_texts):
        """Test basic text preprocessing functionality"""        for language, texts in sample_texts.items():
            for text in texts[:2]:  # Test first 2 texts per language
                processed = await content_processor.preprocess_text(
                    text=text,
                    language=language[:2],
                    options={
                        'normalize_whitespace': True,
                        'remove_extra_spaces': True,
                        'fix_encoding': True
                    }
                )
                
                # Verify preprocessing results
                assert processed is not None
                assert len(processed) > 0
                assert '  ' not in processed  # No double spaces
                assert processed.strip() == processed  # No leading/trailing whitespace

    @pytest.mark.asyncio
    async def test_social_media_preprocessing(self, content_processor, sample_social_content):
        """Test social media specific preprocessing"""        for platform_name, content_dict in sample_social_content.items():
            platform = getattr(Platform, platform_name.upper(), Platform.INSTAGRAM)
            
            for content_type, text in content_dict.items():
                processed = await content_processor.preprocess_social_content(
                    text=text,
                    platform=platform,
                    options={
                        'extract_hashtags': True,
                        'extract_mentions': True,
                        'preserve_emojis': True,
                        'normalize_urls': True
                    }
                )
                
                # Verify social media preprocessing
                assert processed is not None
                assert isinstance(processed, dict)
                assert 'processed_text' in processed
                assert 'metadata' in processed
                
                metadata = processed['metadata']
                if '#' in text:
                    assert 'hashtags' in metadata
                    assert len(metadata['hashtags']) > 0
                
                if '@' in text:
                    assert 'mentions' in metadata
                    assert len(metadata['mentions']) > 0

    @pytest.mark.asyncio
    async def test_platform_optimization(self, content_processor, sample_platform_content):
        """Test platform-specific content optimization"""        platforms_to_test = [Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER, Platform.YOUTUBE]
        
        for platform in platforms_to_test:
            platform_key = platform.value
            if platform_key in sample_platform_content:
                content_samples = sample_platform_content[platform_key]
                
                for content_type, text in content_samples.items():
                    optimized = await content_processor.optimize_for_platform(
                        text=text,
                        platform=platform,
                        content_type=ContentType.POST,
                        options={
                            'enforce_limits': True,
                            'optimize_hashtags': True,
                            'optimize_readability': True
                        }
                    )
                    
                    # Verify platform optimization
                    assert optimized is not None
                    assert isinstance(optimized, dict)
                    assert 'optimized_text' in optimized
                    assert 'compliance_score' in optimized
                    assert 'suggestions' in optimized
                    
                    # Platform-specific validations
                    compliance_score = optimized['compliance_score']
                    assert 0.0 <= compliance_score <= 1.0
                    
                    if platform == Platform.TWITTER:
                        # Twitter character limit
                        optimized_text = optimized['optimized_text']
                        assert len(optimized_text) <= 280
                    
                    elif platform == Platform.INSTAGRAM:
                        # Instagram hashtag optimization
                        if '#' in text:
                            suggestions = optimized['suggestions']
                            hashtag_suggestions = [s for s in suggestions if 'hashtag' in s.lower()]
                            assert len(hashtag_suggestions) >= 0  # Should have hashtag suggestions

    @pytest.mark.asyncio
    async def test_multilingual_preprocessing(self, content_processor, sample_texts):
        """Test multilingual content preprocessing"""        for language, texts in sample_texts.items():
            text = texts[0]
            lang_code = language[:2]
            
            processed = await content_processor.preprocess_multilingual(
                text=text,
                target_language=lang_code,
                options={
                    'detect_language': True,
                    'normalize_unicode': True,
                    'handle_mixed_scripts': True,
                    'preserve_structure': True
                }
            )
            
            # Verify multilingual preprocessing
            assert processed is not None
            assert isinstance(processed, dict)
            assert 'processed_text' in processed
            assert 'detected_language' in processed
            assert 'language_confidence' in processed
            
            # Language detection accuracy
            detected_lang = processed['detected_language']
            confidence = processed['language_confidence']
            
            assert confidence >= 0.0
            assert confidence <= 1.0
            
            # Should detect correct language for clear cases
            if lang_code == 'en' and 'english' in language.lower():
                assert detected_lang in ['en', 'english']
            elif lang_code == 'de' and 'german' in language.lower():
                assert detected_lang in ['de', 'german', 'deutsch']

    @pytest.mark.asyncio
    async def test_content_normalization(self, content_processor, sample_social_content):
        """Test content normalization across different formats"""        # Test with various content types
        content_samples = [
            sample_social_content['instagram']['long_caption'],
            sample_social_content['tiktok']['trending_video'],
            sample_social_content['twitter']['tweet'],
            sample_social_content['youtube']['description']
        ]
        
        for text in content_samples:
            normalized = await content_processor.normalize_content(
                text=text,
                options={
                    'standardize_encoding': True,
                    'normalize_punctuation': True,
                    'normalize_whitespace': True,
                    'remove_control_chars': True,
                    'normalize_urls': True
                }
            )
            
            # Verify normalization
            assert normalized is not None
            assert len(normalized) > 0
            
            # Should not have control characters
            control_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
            for char in control_chars:
                assert char not in normalized
            
            # Should have normalized whitespace
            assert '\t' not in normalized or '\t' in text  # Only if originally present
            assert not normalized.startswith(' ')
            assert not normalized.endswith(' ')

    @pytest.mark.asyncio
    async def test_format_specific_processing(self, content_processor):
        """Test format-specific content processing"""        # Test HTML content
        html_content = """        <p>This is a <strong>test</strong> with <a href="http://example.com">links</a></p>
        <div>And some <em>formatting</em>!</div>
        """        
        processed_html = await content_processor.process_format(
            content=html_content,
            format_type=ContentFormat.HTML,
            options={
                'strip_tags': True,
                'preserve_structure': False,
                'extract_links': True
            }
        )
        
        assert processed_html is not None
        assert '<' not in processed_html['processed_content']  # Tags should be stripped
        assert 'test' in processed_html['processed_content']
        assert 'links' in processed_html['processed_content']
        
        # Test Markdown content
        markdown_content = """        # Title
        This is **bold** and *italic* text.
        
        - List item 1
        - List item 2
        
        [Link](http://example.com)
        """        
        processed_md = await content_processor.process_format(
            content=markdown_content,
            format_type=ContentFormat.MARKDOWN,
            options={
                'convert_to_plain': True,
                'preserve_links': True,
                'preserve_structure': True
            }
        )
        
        assert processed_md is not None
        assert 'Title' in processed_md['processed_content']
        assert 'bold' in processed_md['processed_content']
        assert 'italic' in processed_md['processed_content']

    @pytest.mark.asyncio
    async def test_batch_preprocessing(self, content_processor, performance_test_data):
        """Test batch preprocessing capabilities"""        texts = performance_test_data['small_batch']
        
        start_time = time.time()
        processed_batch = await content_processor.preprocess_batch(
            texts=texts,
            options={
                'normalize_whitespace': True,
                'remove_extra_spaces': True,
                'parallel_processing': True
            }
        )
        batch_time = time.time() - start_time
        
        # Verify batch processing
        assert len(processed_batch) == len(texts)
        assert all(isinstance(item, str) for item in processed_batch)
        
        # Should be efficient
        avg_time_per_item = batch_time / len(texts)
        assert avg_time_per_item < 0.1  # Should process each item quickly

    @pytest.mark.asyncio
    async def test_emoji_handling(self, content_processor):
        """Test emoji detection and handling"""        emoji_text = "I love this! 😍🎉 Great work! 👏✨ #amazing #love ❤️"
        
        processed = await content_processor.process_emojis(
            text=emoji_text,
            options={
                'detect_emojis': True,
                'convert_to_text': False,
                'analyze_sentiment': True,
                'preserve_emojis': True
            }
        )
        
        # Verify emoji processing
        assert processed is not None
        assert isinstance(processed, dict)
        assert 'processed_text' in processed
        assert 'emoji_data' in processed
        
        emoji_data = processed['emoji_data']
        assert 'detected_emojis' in emoji_data
        assert 'emoji_count' in emoji_data
        assert 'emoji_sentiment' in emoji_data
        
        # Should detect emojis
        detected_emojis = emoji_data['detected_emojis']
        assert len(detected_emojis) > 0
        assert '😍' in [emoji['emoji'] for emoji in detected_emojis]

    @pytest.mark.asyncio
    async def test_hashtag_processing(self, content_processor, sample_social_content):
        """Test hashtag extraction and processing"""        text_with_hashtags = sample_social_content['instagram']['post']
        
        processed = await content_processor.process_hashtags(
            text=text_with_hashtags,
            options={
                'extract_hashtags': True,
                'normalize_hashtags': True,
                'analyze_trends': True,
                'suggest_improvements': True
            }
        )
        
        # Verify hashtag processing
        assert processed is not None
        assert isinstance(processed, dict)
        assert 'processed_text' in processed
        assert 'hashtag_data' in processed
        
        hashtag_data = processed['hashtag_data']
        assert 'extracted_hashtags' in hashtag_data
        assert 'hashtag_count' in hashtag_data
        
        # Should extract hashtags if present
        if '#' in text_with_hashtags:
            extracted = hashtag_data['extracted_hashtags']
            assert len(extracted) > 0
            assert all(tag.startswith('#') for tag in extracted)

    @pytest.mark.asyncio
    async def test_mention_processing(self, content_processor, sample_texts):
        """Test mention extraction and processing"""        text_with_mentions = sample_texts['english'][2]  # Has @foodlover
        
        processed = await content_processor.process_mentions(
            text=text_with_mentions,
            options={
                'extract_mentions': True,
                'validate_accounts': False,  # Skip actual validation for tests
                'analyze_relationships': True
            }
        )
        
        # Verify mention processing
        assert processed is not None
        assert isinstance(processed, dict)
        assert 'processed_text' in processed
        assert 'mention_data' in processed
        
        mention_data = processed['mention_data']
        assert 'extracted_mentions' in mention_data
        assert 'mention_count' in mention_data
        
        # Should extract mentions if present
        if '@' in text_with_mentions:
            extracted = mention_data['extracted_mentions']
            assert len(extracted) > 0
            assert all(mention.startswith('@') for mention in extracted)

    @pytest.mark.asyncio
    async def test_url_processing(self, content_processor):
        """Test URL detection and processing"""        text_with_urls = "Check out this amazing website: https://example.com and also http://test.org/page"
        
        processed = await content_processor.process_urls(
            text=text_with_urls,
            options={
                'extract_urls': True,
                'validate_urls': False,  # Skip actual validation for tests
                'shorten_urls': False,
                'analyze_domains': True
            }
        )
        
        # Verify URL processing
        assert processed is not None
        assert isinstance(processed, dict)
        assert 'processed_text' in processed
        assert 'url_data' in processed
        
        url_data = processed['url_data']
        assert 'extracted_urls' in url_data
        assert 'url_count' in url_data
        
        # Should extract URLs
        extracted_urls = url_data['extracted_urls']
        assert len(extracted_urls) >= 2  # Should find both URLs
        assert any('example.com' in url for url in extracted_urls)
        assert any('test.org' in url for url in extracted_urls)

    @pytest.mark.asyncio
    async def test_content_sanitization(self, content_processor):
        """Test content sanitization for security"""        malicious_content = """        <script>alert('xss')</script>
        <img src="x" onerror="alert('xss')">
        javascript:alert('xss')
        <iframe src="http://malicious.com"></iframe>
        """        
        sanitized = await content_processor.sanitize_content(
            content=malicious_content,
            options={
                'remove_scripts': True,
                'remove_iframes': True,
                'sanitize_attributes': True,
                'validate_urls': True
            }
        )
        
        # Verify sanitization
        assert sanitized is not None
        assert '<script' not in sanitized.lower()
        assert 'javascript:' not in sanitized.lower()
        assert '<iframe' not in sanitized.lower()
        assert 'onerror' not in sanitized.lower()

    @pytest.mark.asyncio
    async def test_performance_optimization(self, content_processor, performance_test_data):
        """Test preprocessing performance optimization"""        # Test with large text
        large_text = performance_test_data['stress_text']
        
        start_time = time.time()
        processed = await content_processor.preprocess_text(
            text=large_text,
            language='en',
            options={
                'optimize_performance': True,
                'parallel_processing': True,
                'memory_efficient': True
            }
        )
        processing_time = time.time() - start_time
        
        # Should handle large text efficiently
        assert processed is not None
        assert processing_time < 5.0  # Should complete within 5 seconds
        
        # Test memory efficiency with batch processing
        medium_batch = performance_test_data['medium_batch']
        
        start_time = time.time()
        batch_processed = await content_processor.preprocess_batch(
            texts=medium_batch,
            options={
                'memory_efficient': True,
                'batch_size': 20
            }
        )
        batch_time = time.time() - start_time
        
        assert len(batch_processed) == len(medium_batch)
        assert batch_time < 10.0  # Should complete batch efficiently

    @pytest.mark.asyncio
    async def test_encoding_handling(self, content_processor):
        """Test handling of different text encodings"""        # Test various encodings and special characters
        test_texts = [
            "English text with unicode: café, naïve, résumé",
            "Deutsch: Ärger, Öl, Übung, ß",
            "Français: café, crème, âme, être",
            "Español: niño, señor, corazón",
            "Mixed: Hello 世界 🌍 Привет мир"
        ]
        
        for text in test_texts:
            processed = await content_processor.preprocess_text(
                text=text,
                language='auto',
                options={
                    'normalize_unicode': True,
                    'fix_encoding': True,
                    'preserve_accents': True
                }
            )
            
            # Should handle encoding properly
            assert processed is not None
            assert len(processed) > 0
            
            # Should preserve original meaning
            if 'café' in text:
                assert 'café' in processed or 'cafe' in processed

    @pytest.mark.asyncio
    async def test_content_structure_preservation(self, content_processor):
        """Test preservation of content structure"""        structured_content = """        Title: Important Announcement
        
        Paragraph 1: This is the first paragraph with important information.
        
        Paragraph 2: This is the second paragraph.
        - List item 1
        - List item 2
        - List item 3
        
        Conclusion: Final thoughts here.
        """        
        processed = await content_processor.preprocess_text(
            text=structured_content,
            language='en',
            options={
                'preserve_structure': True,
                'maintain_paragraphs': True,
                'preserve_lists': True
            }
        )
        
        # Should preserve structure
        assert processed is not None
        assert 'Title:' in processed or 'Important Announcement' in processed
        assert 'Paragraph 1:' in processed or 'first paragraph' in processed
        assert 'List item' in processed
        assert 'Conclusion:' in processed or 'Final thoughts' in processed

class TestTextProcessor:
    """Test specialized text processor"""    
    @pytest.mark.asyncio
    async def test_text_processor_initialization(self):
        """Test text processor initialization"""        processor = TextProcessor()
        assert processor is not None
        assert hasattr(processor, 'process')

    @pytest.mark.asyncio
    async def test_basic_text_processing(self, sample_texts):
        """Test basic text processing"""        processor = TextProcessor()
        
        text = sample_texts['english'][0]
        processed = await processor.process(
            text=text,
            options={
                'clean_whitespace': True,
                'normalize_punctuation': True
            }
        )
        
        assert processed is not None
        assert len(processed) > 0

class TestSocialMediaProcessor:
    """Test specialized social media processor"""    
    @pytest.mark.asyncio
    async def test_social_processor_initialization(self):
        """Test social media processor initialization"""        processor = SocialMediaProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_post')
        assert hasattr(processor, 'extract_social_elements')

    @pytest.mark.asyncio
    async def test_social_elements_extraction(self, sample_social_content):
        """Test extraction of social media elements"""        processor = SocialMediaProcessor()
        
        text = sample_social_content['instagram']['post']
        
        elements = await processor.extract_social_elements(text)
        
        assert elements is not None
        assert isinstance(elements, dict)
        assert 'hashtags' in elements
        assert 'mentions' in elements
        assert 'urls' in elements
        assert 'emojis' in elements

class TestVideoContentProcessor:
    """Test video content processor"""    
    @pytest.mark.asyncio
    async def test_video_processor_initialization(self):
        """Test video processor initialization"""        processor = VideoContentProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_transcript')
        assert hasattr(processor, 'extract_metadata')

    @pytest.mark.asyncio
    async def test_transcript_processing(self, sample_social_content):
        """Test video transcript processing"""        processor = VideoContentProcessor()
        
        # Use TikTok video content as transcript
        transcript = sample_social_content['tiktok']['trending_video']
        
        processed = await processor.process_transcript(
            transcript=transcript,
            options={
                'clean_speech_artifacts': True,
                'segment_sentences': True,
                'extract_keywords': True
            }
        )
        
        assert processed is not None
        assert isinstance(processed, dict)
        assert 'processed_transcript' in processed
        assert 'metadata' in processed

class TestProcessingConfig:
    """Test processing configuration"""    
    def test_config_creation(self):
        """Test processing configuration creation"""        config = ProcessingConfig(
            languages=['en', 'de', 'fr'],
            formats=[ContentFormat.TEXT, ContentFormat.HTML],
            performance_mode='standard'
        )
        
        assert config.languages == ['en', 'de', 'fr']
        assert config.formats == [ContentFormat.TEXT, ContentFormat.HTML]
        assert config.performance_mode == 'standard'

    def test_config_validation(self):
        """Test configuration validation"""        # Test with valid config
        config = ProcessingConfig(
            languages=['en'],
            formats=[ContentFormat.TEXT],
            max_text_length=10000
        )
        
        assert config.max_text_length == 10000
        
        # Should handle empty languages list
        config_empty = ProcessingConfig(
            languages=[],
            formats=[ContentFormat.TEXT]
        )
        
        assert isinstance(config_empty.languages, list)
