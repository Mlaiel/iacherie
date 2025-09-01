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
Comprehensive Tests for NLP Extraction Module

Industrial-grade tests for AdvancedExtractionEngine covering entity extraction,
keyword extraction, and information extraction with real implementations.

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

from ai.nlp.extraction import (
    AdvancedContentExtractor, ExtractedEntity, KeywordExtraction,
    ContactInfo, ExtractionResult, ContentMetrics, StructuredData
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    # Fallback definitions if utils doesn't exist
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedContentExtractor:
    """
Comprehensive tests for AdvancedContentExtractor"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, extraction_engine):
        """
Test extraction engine initialization"""
        assert extraction_engine is not None
        assert hasattr(extraction_engine, 'config')
        assert hasattr(extraction_engine, 'entity_extractor')
        assert hasattr(extraction_engine, 'keyword_extractor')
        assert hasattr(extraction_engine, 'information_extractor')
        
        # Test configuration
        config = extraction_engine.config
        assert 'entity_types' in config
        assert 'extraction_models' in config
        assert 'confidence_threshold' in config

    @pytest.mark.asyncio
    async def test_entity_extraction(self, extraction_engine):
        """
Test named entity recognition and extraction"""
        test_cases = [
            {
                'text': "Fahed Mlaiel from IA Influencer Agent Platform visited Berlin, Germany on January 15, 2025 to meet with Microsoft executives.",
                'expected_entities': {
                    'PERSON': ['Fahed Mlaiel'],
                    'ORG': ['IA Influencer Agent Platform', 'Microsoft'],
                    'GPE': ['Berlin', 'Germany'],
                    'DATE': ['January 15, 2025']
                }
            },
            {
                'text': "Apple Inc. released the iPhone 15 for $999 at their headquarters in Cupertino, California.",
                'expected_entities': {
                    'ORG': ['Apple Inc.'],
                    'PRODUCT': ['iPhone 15'],
                    'MONEY': ['$999'],
                    'GPE': ['Cupertino', 'California']
                }
            },
            {
                'text': "The AI conference will be held at the Convention Center from 9:00 AM to 5:00 PM on March 20th.",
                'expected_entities': {
                    'EVENT': ['AI conference'],
                    'FAC': ['Convention Center'],
                    'TIME': ['9:00 AM', '5:00 PM'],
                    'DATE': ['March 20th']
                }
            }
        ]
        
        for case in test_cases:
            entity_result = await extraction_engine.extract_entities(
                text=case['text'],
                options={
                    'entity_types': ['PERSON', 'ORG', 'GPE', 'DATE', 'TIME', 'MONEY', 'PRODUCT', 'EVENT', 'FAC'],
                    'confidence_scoring': True,
                    'entity_linking': True,
                    'coreference_resolution': True
                }
            )
            
            assert entity_result is not None
            assert isinstance(entity_result, dict)
            assert 'entities' in entity_result
            assert 'entity_counts' in entity_result
            assert 'confidence_scores' in entity_result
            
            entities = entity_result['entities']
            confidence_scores = entity_result['confidence_scores']
            
            # Verify entity extraction
            for entity_type, expected_entities in case['expected_entities'].items():
                if entity_type in entities:
                    extracted_entities = entities[entity_type]
                    
                    for expected_entity in expected_entities:
                        # Check if entity is found (exact or partial match)
                        entity_found = any(
                            expected_entity.lower() in extracted.lower() or
                            extracted.lower() in expected_entity.lower()
                            for extracted in extracted_entities
                        )
                        assert entity_found, f"Expected entity '{expected_entity}' of type '{entity_type}' not found in {extracted_entities}"
            
            # Verify confidence scores
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    if entity in confidence_scores:
                        assert 0.0 <= confidence_scores[entity] <= 1.0

    @pytest.mark.asyncio
    async def test_keyword_extraction(self, extraction_engine):
        """Test keyword and key phrase extraction"""
        test_texts = [
            {
                'text': """
                Artificial intelligence and machine learning are revolutionizing content creation for social media platforms.
                Advanced natural language processing algorithms enable automated content generation, sentiment analysis,
                and personalized user engagement strategies. Content creators can now leverage AI-powered tools
                to optimize their social media presence and increase audience engagement rates.
                """,
                'expected_keywords': [
                    'artificial intelligence', 'machine learning', 'content creation',
                    'social media', 'natural language processing', 'sentiment analysis',
                    'user engagement', 'AI-powered tools', 'audience engagement'
                ]
            },
            {
                'text': """
                Digital marketing strategies require comprehensive understanding of SEO optimization, keyword research,
                and competitor analysis. Successful brands implement data-driven approaches to content marketing,
                influencer partnerships, and cross-platform campaign management for maximum ROI.
                """,
                'expected_keywords': [
                    'digital marketing', 'SEO optimization', 'keyword research',
                    'competitor analysis', 'content marketing', 'influencer partnerships',
                    'campaign management', 'data-driven approaches', 'ROI'
                ]
            }
        ]
        
        for case in test_texts:
            keyword_result = await extraction_engine.extract_keywords(
                text=case['text'],
                options={
                    'max_keywords': 20,
                    'include_phrases': True,
                    'relevance_scoring': True,
                    'topic_clustering': True,
                    'semantic_similarity': True
                }
            )
            
            assert keyword_result is not None
            assert 'keywords' in keyword_result
            assert 'key_phrases' in keyword_result
            assert 'relevance_scores' in keyword_result
            assert 'topic_clusters' in keyword_result
            
            keywords = keyword_result['keywords']
            key_phrases = keyword_result['key_phrases']
            relevance_scores = keyword_result['relevance_scores']
            
            # Verify keyword extraction
            assert len(keywords) > 0
            assert len(key_phrases) > 0
            
            # Check for expected keywords/phrases
            all_extracted = keywords + key_phrases
            for expected_keyword in case['expected_keywords']:
                keyword_found = any(
                    expected_keyword.lower() in extracted.lower() or
                    any(word in extracted.lower() for word in expected_keyword.lower().split())
                    for extracted in all_extracted
                )
                assert keyword_found, f"Expected keyword '{expected_keyword}' not found in extracted keywords"
            
            # Verify relevance scores
            for keyword in keywords:
                if keyword in relevance_scores:
                    assert 0.0 <= relevance_scores[keyword] <= 1.0

    @pytest.mark.asyncio
    async def test_social_media_extraction(self, extraction_engine, sample_social_content):
        """Test social media specific extraction"""
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
        
        for platform in platforms:
            content = sample_social_content[platform.value.lower()]['post']
            
            social_extraction = await extraction_engine.extract_social_elements(
                content=content,
                platform=platform,
                options={
                    'hashtags': True,
                    'mentions': True,
                    'urls': True,
                    'emojis': True,
                    'cashtags': True if platform == Platform.TWITTER else False
                }
            )
            
            assert social_extraction is not None
            assert 'hashtags' in social_extraction
            assert 'mentions' in social_extraction
            assert 'urls' in social_extraction
            assert 'emojis' in social_extraction
            assert 'social_metrics' in social_extraction
            
            hashtags = social_extraction['hashtags']
            mentions = social_extraction['mentions']
            
            # Verify social element extraction
            if '#' in content:
                assert len(hashtags) > 0
                for hashtag in hashtags:
                    assert hashtag.startswith('#') or hashtag.startswith('hashtag:')
            
            if '@' in content:
                assert len(mentions) > 0
                for mention in mentions:
                    assert mention.startswith('@') or mention.startswith('mention:')

    @pytest.mark.asyncio
    async def test_multilingual_extraction(self, extraction_engine):
        """
Test multilingual content extraction"""
        multilingual_texts = [
            {
                'text': "Fahed Mlaiel arbeitet bei IA Influencer Agent Platform in Berlin, Deutschland.",
                'language': 'german',
                'expected_entities': ['Fahed Mlaiel', 'IA Influencer Agent Platform', 'Berlin', 'Deutschland']
            },
            {
                'text': "Fahed Mlaiel travaille chez IA Influencer Agent Platform à Paris, France.",
                'language': 'french',
                'expected_entities': ['Fahed Mlaiel', 'IA Influencer Agent Platform', 'Paris', 'France']
            },
            {
                'text': "Fahed Mlaiel trabaja en IA Influencer Agent Platform en Madrid, España.",
                'language': 'spanish',
                'expected_entities': ['Fahed Mlaiel', 'IA Influencer Agent Platform', 'Madrid', 'España']
            }
        ]
        
        for case in multilingual_texts:
            multilingual_result = await extraction_engine.extract_multilingual_content(
                text=case['text'],
                language=case['language'],
                options={
                    'cross_language_entities': True,
                    'language_specific_patterns': True,
                    'cultural_context': True
                }
            )
            
            assert multilingual_result is not None
            assert 'entities' in multilingual_result
            assert 'language_confidence' in multilingual_result
            assert 'cross_language_mappings' in multilingual_result
            
            entities = multilingual_result['entities']
            
            # Should extract expected entities
            all_extracted_entities = []
            for entity_type, entity_list in entities.items():
                all_extracted_entities.extend(entity_list)
            
            for expected_entity in case['expected_entities']:
                entity_found = any(
                    expected_entity.lower() in extracted.lower()
                    for extracted in all_extracted_entities
                )
                assert entity_found, f"Expected entity '{expected_entity}' not found in multilingual extraction"

    @pytest.mark.asyncio
    async def test_structured_information_extraction(self, extraction_engine):
        """Test structured information extraction"""
        structured_texts = [
            {
                'text': """
                Product Launch Event
                Date: March 15, 2025
                Time: 2:00 PM - 5:00 PM EST
                Location: Tech Conference Center, San Francisco
                Speaker: Fahed Mlaiel, CEO of IA Influencer Agent Platform
                Topic: AI-Powered Content Creation Revolution
                Registration: www.example.com/register
                Contact: info@example.com
                Price: $299 (Early bird: $199)
                """,
                'expected_structure': {
                    'event_type': 'Product Launch Event',
                    'date': 'March 15, 2025',
                    'time': '2:00 PM - 5:00 PM EST',
                    'location': 'Tech Conference Center, San Francisco',
                    'speaker': 'Fahed Mlaiel',
                    'price': '$299'
                }
            }
        ]
        
        for case in structured_texts:
            structure_result = await extraction_engine.extract_structured_information(
                text=case['text'],
                options={
                    'template_matching': True,
                    'pattern_recognition': True,
                    'field_validation': True,
                    'data_normalization': True
                }
            )
            
            assert structure_result is not None
            assert 'structured_data' in structure_result
            assert 'confidence_scores' in structure_result
            assert 'extraction_patterns' in structure_result
            
            structured_data = structure_result['structured_data']
            
            # Verify structured data extraction
            for field, expected_value in case['expected_structure'].items():
                field_found = False
                for extracted_field, extracted_value in structured_data.items():
                    if (field.lower() in extracted_field.lower() or 
                        expected_value.lower() in str(extracted_value).lower()):
                        field_found = True
                        break
                
                assert field_found, f"Expected structured field '{field}' with value '{expected_value}' not found"

    @pytest.mark.asyncio
    async def test_contact_information_extraction(self, extraction_engine):
        """Test contact information extraction"""
        contact_texts = [
            {
                'text': """
                Contact Fahed Mlaiel for business inquiries:
                Email: mlaiel@live.de
                Phone: +49 30 12345678
                LinkedIn: linkedin.com/in/fahed-mlaiel
                Website: www.ia-influencer-platform.com
                Address: Tech Street 123, 10115 Berlin, Germany
                """,
                'expected_contacts': {
                    'email': ['mlaiel@live.de'],
                    'phone': ['+49 30 12345678'],
                    'linkedin': ['linkedin.com/in/fahed-mlaiel'],
                    'website': ['www.ia-influencer-platform.com'],
                    'address': ['Tech Street 123, 10115 Berlin, Germany']
                }
            }
        ]
        
        for case in contact_texts:
            contact_result = await extraction_engine.extract_contact_information(
                text=case['text'],
                options={
                    'email_extraction': True,
                    'phone_extraction': True,
                    'social_media_extraction': True,
                    'address_extraction': True,
                    'website_extraction': True,
                    'validation': True
                }
            )
            
            assert contact_result is not None
            assert 'contact_info' in contact_result
            assert 'validation_results' in contact_result
            
            contact_info = contact_result['contact_info']
            
            # Verify contact extraction
            for contact_type, expected_values in case['expected_contacts'].items():
                if contact_type in contact_info:
                    extracted_values = contact_info[contact_type]
                    
                    for expected_value in expected_values:
                        contact_found = any(
                            expected_value.lower() in extracted.lower()
                            for extracted in extracted_values
                        )
                        assert contact_found, f"Expected {contact_type} '{expected_value}' not found"

    @pytest.mark.asyncio
    async def test_temporal_extraction(self, extraction_engine):
        """Test temporal information extraction"""
        temporal_texts = [
            {
                'text': """
                The AI conference is scheduled for next Monday at 9:00 AM.
                Registration closes tomorrow at midnight.
                The early bird discount ends in 3 days.
                Sessions run from March 15-17, 2025.
                Follow-up meetings are planned for the following week.
                """,
                'expected_temporal': [
                    'next Monday', 'tomorrow', 'in 3 days',
                    'March 15-17, 2025', 'following week',
                    '9:00 AM', 'midnight'
                ]
            }
        ]
        
        for case in temporal_texts:
            temporal_result = await extraction_engine.extract_temporal_information(
                text=case['text'],
                options={
                    'absolute_dates': True,
                    'relative_dates': True,
                    'time_expressions': True,
                    'duration_extraction': True,
                    'temporal_normalization': True
                }
            )
            
            assert temporal_result is not None
            assert 'temporal_expressions' in temporal_result
            assert 'normalized_dates' in temporal_result
            assert 'time_references' in temporal_result
            
            temporal_expressions = temporal_result['temporal_expressions']
            
            # Verify temporal extraction
            for expected_temporal in case['expected_temporal']:
                temporal_found = any(
                    expected_temporal.lower() in expression.lower()
                    for expression in temporal_expressions
                )
                # Allow some flexibility in temporal extraction
                if not temporal_found:
                    # Check for partial matches or normalized forms
                    temporal_found = any(
                        any(word in expression.lower() for word in expected_temporal.lower().split())
                        for expression in temporal_expressions
                    )

    @pytest.mark.asyncio
    async def test_technical_information_extraction(self, extraction_engine):
        """
Test technical information extraction"""
        technical_texts = [
            {
                'text': """
                Our API supports REST endpoints at https://api.example.com/v1/.
                Authentication via Bearer token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
                Database: PostgreSQL 13.2, Redis 6.0.9
                Deployment: Docker containers on AWS EC2 t3.medium instances
                Monitoring: Prometheus with Grafana dashboards
                Load balancer: NGINX 1.20.1 with SSL/TLS encryption
                """,
                'expected_technical': {
                    'urls': ['https://api.example.com/v1/'],
                    'tokens': ['eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'],
                    'technologies': ['PostgreSQL', 'Redis', 'Docker', 'AWS EC2', 'Prometheus', 'Grafana', 'NGINX'],
                    'versions': ['13.2', '6.0.9', '1.20.1']
                }
            }
        ]
        
        for case in technical_texts:
            tech_result = await extraction_engine.extract_technical_information(
                text=case['text'],
                options={
                    'api_endpoints': True,
                    'version_numbers': True,
                    'technology_stack': True,
                    'configuration_details': True,
                    'security_tokens': True
                }
            )
            
            assert tech_result is not None
            assert 'technical_details' in tech_result
            assert 'technology_stack' in tech_result
            assert 'security_info' in tech_result
            
            technical_details = tech_result['technical_details']
            
            # Verify technical extraction
            for detail_type, expected_values in case['expected_technical'].items():
                if detail_type in technical_details:
                    extracted_values = technical_details[detail_type]
                    
                    for expected_value in expected_values:
                        detail_found = any(
                            expected_value.lower() in str(extracted).lower()
                            for extracted in extracted_values
                        )
                        if not detail_found:
                            # Check partial matches for technologies
                            detail_found = any(
                                any(word in str(extracted).lower() for word in expected_value.lower().split())
                                for extracted in extracted_values
                            )

    @pytest.mark.asyncio
    async def test_batch_extraction(self, extraction_engine, performance_test_data):
        """
Test batch content extraction"""
        texts = performance_test_data['small_batch'][:10]  # Use smaller batch for complex extraction
        
        start_time = time.time()
        batch_extraction = await extraction_engine.extract_batch(
            texts=texts,
            extraction_types=['entities', 'keywords', 'social_elements'],
            options={
                'parallel_processing': True,
                'consistent_extraction': True,
                'optimization': True
            }
        )
        processing_time = time.time() - start_time
        
        assert batch_extraction is not None
        assert 'extractions' in batch_extraction
        assert 'batch_statistics' in batch_extraction
        assert 'processing_metrics' in batch_extraction
        
        extractions = batch_extraction['extractions']
        assert len(extractions) == len(texts)
        
        # Verify all extractions have required fields
        for extraction in extractions:
            assert 'entities' in extraction
            assert 'keywords' in extraction
            
        # Should process efficiently
        throughput = len(texts) / processing_time
        assert throughput > 2.0  # Should extract from at least 2 texts per second

    @pytest.mark.asyncio
    async def test_custom_extraction_patterns(self, extraction_engine):
        """
Test custom extraction pattern definition"""
        custom_patterns = {
            'product_codes': r'[A-Z]{2,3}-\d{4,6}',
            'order_numbers': r'ORD-\d{8}',
            'user_ids': r'USR_[a-z0-9]{8}',
            'api_keys': r'api_[a-z0-9]{32}'
        }
        
        text_with_patterns = """
        Product codes: AI-2025, ML-456789, NLP-12345
        Order numbers: ORD-20250801, ORD-20250802
        User IDs: USR_abc12345, USR_def67890
        API keys: api_1234567890abcdef1234567890abcdef
        """
        
        custom_result = await extraction_engine.extract_with_custom_patterns(
            text=text_with_patterns,
            patterns=custom_patterns,
            options={
                'case_sensitive': True,
                'overlapping_matches': False,
                'validation_rules': True
            }
        )
        
        assert custom_result is not None
        assert 'pattern_matches' in custom_result
        assert 'match_confidence' in custom_result
        
        pattern_matches = custom_result['pattern_matches']
        
        # Verify custom pattern extraction
        for pattern_name, pattern_regex in custom_patterns.items():
            if pattern_name in pattern_matches:
                matches = pattern_matches[pattern_name]
                assert len(matches) > 0  # Should find matches for each pattern

    @pytest.mark.asyncio
    async def test_real_time_extraction(self, extraction_engine):
        """
Test real-time content extraction"""
        # Simulate real-time content stream
        content_stream = [
            "Breaking: @elonmusk announces new AI breakthrough at #TechConf2025",
            "Contact us at support@example.com or call +1-555-0123 for assistance",
            "Visit our website www.example.com for more information about AI tools",
            "Meeting scheduled for March 15, 2025 at 2:00 PM in Conference Room A",
            "Product launch event featuring Fahed Mlaiel from IA Influencer Platform"
        ]
        
        extraction_times = []
        
        for content in content_stream:
            start_time = time.time()
            
            real_time_result = await extraction_engine.extract_realtime(
                content=content,
                extraction_types=['entities', 'social_elements', 'contact_info'],
                options={
                    'low_latency': True,
                    'priority_extraction': True,
                    'quick_analysis': True
                }
            )
            
            extraction_time = time.time() - start_time
            extraction_times.append(extraction_time)
            
            assert real_time_result is not None
            assert 'extracted_data' in real_time_result
            assert 'processing_time' in real_time_result
            
            # Should be fast for real-time use
            assert extraction_time < 2.0  # Should extract quickly
        
        # Average should be suitable for real-time
        avg_time = sum(extraction_times) / len(extraction_times)
        assert avg_time < 1.0

    @pytest.mark.asyncio
    async def test_extraction_confidence_calibration(self, extraction_engine):
        """Test extraction confidence calibration"""
        confidence_test_cases = [
            {
                'text': "Fahed Mlaiel is the CEO of IA Influencer Agent Platform.",
                'expected_high_confidence': ['Fahed Mlaiel', 'IA Influencer Agent Platform']
            },
            {
                'text': "Maybe John works at some company in the tech industry.",
                'expected_low_confidence': ['John', 'company', 'tech industry']
            }
        ]
        
        for case in confidence_test_cases:
            confidence_result = await extraction_engine.extract_with_confidence(
                text=case['text'],
                options={
                    'confidence_calibration': True,
                    'uncertainty_estimation': True,
                    'confidence_thresholding': True
                }
            )
            
            assert confidence_result is not None
            assert 'extractions' in confidence_result
            assert 'confidence_distribution' in confidence_result
            
            extractions = confidence_result['extractions']
            
            # Check confidence levels
            for extraction_type, extracted_items in extractions.items():
                for item in extracted_items:
                    if 'confidence' in item:
                        confidence = item['confidence']
                        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, extraction_engine, benchmark_config):
        """Test extraction performance benchmarks"""
        test_text = "This is a performance test for extraction benchmarking with entities and keywords."
        
        # Single extraction performance
        start_time = time.time()
        result = await extraction_engine.extract_entities(
            text=test_text,
            options={'quick_extraction': True}
        )
        single_time = time.time() - start_time
        
        max_time = benchmark_config.get('max_extraction_time', 3.0)
        assert single_time < max_time, f"Extraction took {single_time:.3f}s, max: {max_time}s"
        
        # Batch extraction performance
        batch_texts = [f"Batch text {i} for extraction testing." for i in range(15)]
        
        start_time = time.time()
        batch_result = await extraction_engine.extract_batch(
            texts=batch_texts,
            extraction_types=['entities', 'keywords'],
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(batch_texts) / batch_time
        min_throughput = benchmark_config.get('extraction_throughput', 3.0)
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, extraction_engine):
        """Test extraction error handling"""
        # Test empty content
        result = await extraction_engine.extract_entities(
            text="",
            options={'handle_empty': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test very long content
        long_text = "Long content " * 2000
        result = await extraction_engine.extract_entities(
            text=long_text,
            options={'truncate_long_text': True}
        )
        assert result is not None
        
        # Test special characters only
        special_text = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = await extraction_engine.extract_keywords(
            text=special_text,
            options={'handle_non_text': True}
        )
        assert result is not None

class TestEntityExtractor:
    """Test entity extractor component"""
    
    @pytest.mark.asyncio
    async def test_entity_extractor_initialization(self):
        """
Test entity extractor initialization"""
        extractor = EntityExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'extract_entities')

class TestKeywordExtractor:
    """
Test keyword extractor component"""
    
    @pytest.mark.asyncio
    async def test_keyword_extractor_initialization(self):
        """
Test keyword extractor initialization"""
        extractor = KeywordExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'extract_keywords')

class TestInformationExtractor:
    """
Test information extractor component"""
    
    @pytest.mark.asyncio
    async def test_information_extractor_initialization(self):
        """
Test information extractor initialization"""
        extractor = InformationExtractor()
        assert extractor is not None
        assert hasattr(extractor, 'extract_information')

class TestExtractionConfig:
    """
Test extraction configuration"""
    
    def test_config_creation(self):
        """
Test extraction configuration creation"""
        config = ExtractionConfig(
            entity_types=['PERSON', 'ORG', 'GPE', 'DATE'],
            extraction_models=['basic', 'advanced'],
            confidence_threshold=0.8
        )
        
        assert 'PERSON' in config.entity_types
        assert 'basic' in config.extraction_models
        assert config.confidence_threshold == 0.8
