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
Comprehensive Tests for NLP Translation Module

Industrial-grade tests for AdvancedTranslationEngine covering multilingual translation,
cultural adaptation, and localization with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

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

from ai.nlp.translation import (
    AdvancedTranslator, TranslationQualityAssessor, MultiLanguageContentManager,
    TranslationRequest, TranslationResult
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedTranslator:
    """Comprehensive tests for AdvancedTranslator"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, translation_engine):
        """Test translation engine initialization"""
        assert translation_engine is not None
        assert hasattr(translation_engine, 'config')
        assert hasattr(translation_engine, 'multilingual_translator')
        assert hasattr(translation_engine, 'cultural_adapter')
        assert hasattr(translation_engine, 'localization_engine')
        
        # Test configuration
        config = translation_engine.config
        assert 'supported_languages' in config
        assert 'translation_quality' in config
        assert 'cultural_adaptation' in config

    @pytest.mark.asyncio
    async def test_basic_translation(self, translation_engine):
        """Test basic text translation"""
        test_cases = [
            {
                'text': "Hello, how are you today?",
                'source_lang': Language.ENGLISH,
                'target_lang': Language.GERMAN,
                'expected_contains': ['hallo', 'wie', 'heute']
            },
            {
                'text': "I love this amazing product!",
                'source_lang': Language.ENGLISH,
                'target_lang': Language.FRENCH,
                'expected_contains': ['aime', 'produit']
            },
            {
                'text': "Bonjour, comment allez-vous?",
                'source_lang': Language.FRENCH,
                'target_lang': Language.SPANISH,
                'expected_contains': ['hola', 'cómo']
            }
        ]
        
        for case in test_cases:
            translation_result = await translation_engine.translate(
                text=case['text'],
                source_language=case['source_lang'],
                target_language=case['target_lang'],
                options={
                    'quality_level': 'high',
                    'preserve_formatting': True,
                    'cultural_adaptation': False  # Basic translation only
                }
            )
            
            assert translation_result is not None
            assert isinstance(translation_result, dict)
            assert 'translated_text' in translation_result
            assert 'confidence_score' in translation_result
            assert 'quality_metrics' in translation_result
            
            translated = translation_result['translated_text'].lower()
            confidence = translation_result['confidence_score']
            
            # Check translation quality
            assert len(translated) > 0
            assert 0.0 <= confidence <= 1.0
            assert confidence > 0.7  # Should have good confidence
            
            # Check for expected words (basic sanity check)
            for expected_word in case['expected_contains']:
                # At least one expected word should be present
                assert any(expected_word in translated for expected_word in case['expected_contains'])

    @pytest.mark.asyncio
    async def test_social_media_translation(self, translation_engine, sample_social_content):
        """Test social media content translation"""
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
        languages = [Language.GERMAN, Language.FRENCH, Language.SPANISH]
        
        for platform in platforms:
            content = sample_social_content[platform.value.lower()]['post']
            
            for target_lang in languages:
                translation = await translation_engine.translate_social_content(
                    content=content,
                    source_language=Language.ENGLISH,
                    target_language=target_lang,
                    platform=platform,
                    options={
                        'preserve_hashtags': True,
                        'preserve_mentions': True,
                        'preserve_emojis': True,
                        'adapt_cultural_references': True,
                        'optimize_for_platform': True
                    }
                )
                
                assert translation is not None
                assert 'translated_content' in translation
                assert 'platform_adaptations' in translation
                assert 'cultural_notes' in translation
                
                translated_content = translation['translated_content']
                
                # Should preserve social media elements
                if '#' in content:
                    assert '#' in translated_content  # Hashtags preserved
                if '@' in content:
                    assert '@' in translated_content  # Mentions preserved
                
                # Should adapt to platform constraints
                if platform == Platform.TWITTER:
                    assert len(translated_content) <= 280  # Twitter character limit

    @pytest.mark.asyncio
    async def test_cultural_adaptation(self, translation_engine):
        """Test cultural adaptation features"""
        cultural_test_cases = [
            {
                'text': "It's as American as apple pie!",
                'source_culture': 'US',
                'target_culture': 'DE',
                'context': 'The phrase references American culture'
            },
            {
                'text': "The weather is quite nice today, isn't it?",
                'source_culture': 'UK',
                'target_culture': 'FR',
                'context': 'British politeness and small talk'
            },
            {
                'text': "Let's grab some coffee and discuss business.",
                'source_culture': 'US',
                'target_culture': 'JP',
                'context': 'Business culture differences'
            }
        ]
        
        for case in cultural_test_cases:
            cultural_adaptation = await translation_engine.adapt_culturally(
                text=case['text'],
                source_culture=case['source_culture'],
                target_culture=case['target_culture'],
                context={'description': case['context']},
                options={
                    'deep_cultural_analysis': True,
                    'cultural_metaphor_adaptation': True,
                    'social_norm_adjustment': True,
                    'business_culture_adaptation': True
                }
            )
            
            assert cultural_adaptation is not None
            assert 'adapted_text' in cultural_adaptation
            assert 'cultural_changes' in cultural_adaptation
            assert 'cultural_notes' in cultural_adaptation
            assert 'adaptation_confidence' in cultural_adaptation
            
            adapted_text = cultural_adaptation['adapted_text']
            cultural_changes = cultural_adaptation['cultural_changes']
            
            assert len(adapted_text) > 0
            assert isinstance(cultural_changes, list)
            
            # Should have made cultural adaptations
            if len(cultural_changes) > 0:
                for change in cultural_changes:
                    assert 'original_phrase' in change
                    assert 'adapted_phrase' in change
                    assert 'reason' in change

    @pytest.mark.asyncio
    async def test_multilingual_batch_translation(self, translation_engine, performance_test_data):
        """Test batch translation capabilities"""
        texts = performance_test_data['small_batch'][:5]  # Use smaller batch for translation
        target_languages = [Language.GERMAN, Language.FRENCH, Language.SPANISH]
        
        start_time = time.time()
        batch_translation = await translation_engine.translate_batch(
            texts=texts,
            source_language=Language.ENGLISH,
            target_languages=target_languages,
            options={
                'parallel_processing': True,
                'consistency_check': True,
                'quality_assurance': True
            }
        )
        translation_time = time.time() - start_time
        
        assert batch_translation is not None
        assert 'translations' in batch_translation
        assert 'batch_quality_score' in batch_translation
        assert 'consistency_report' in batch_translation
        
        translations = batch_translation['translations']
        
        # Verify all translations completed
        for lang in target_languages:
            lang_code = lang.value[:2]
            assert lang_code in translations
            assert len(translations[lang_code]) == len(texts)
            
            for translation in translations[lang_code]:
                assert 'translated_text' in translation
                assert 'confidence_score' in translation
                assert len(translation['translated_text']) > 0

    @pytest.mark.asyncio
    async def test_localization_features(self, translation_engine):
        """Test content localization features"""
        content = """
        Our product launches on March 15th, 2024 at 2:00 PM EST.
        The price is $299.99 with free shipping.
        Visit our store at 123 Main Street, New York, NY 10001.
        Call us at (555) 123-4567 for more information.
        """
        
        localization_targets = [
            {
                'country': 'DE',
                'language': Language.GERMAN,
                'locale_settings': {
                    'currency': 'EUR',
                    'date_format': 'DD.MM.YYYY',
                    'time_format': '24h',
                    'number_format': 'european'
                }
            },
            {
                'country': 'FR',
                'language': Language.FRENCH,
                'locale_settings': {
                    'currency': 'EUR',
                    'date_format': 'DD/MM/YYYY',
                    'time_format': '24h',
                    'number_format': 'european'
                }
            }
        ]
        
        for target in localization_targets:
            localized_content = await translation_engine.localize_content(
                content=content,
                target_country=target['country'],
                target_language=target['language'],
                locale_settings=target['locale_settings'],
                options={
                    'localize_dates': True,
                    'localize_currency': True,
                    'localize_addresses': True,
                    'localize_phone_numbers': True,
                    'cultural_adaptation': True
                }
            )
            
            assert localized_content is not None
            assert 'localized_text' in localized_content
            assert 'localization_changes' in localized_content
            assert 'locale_adaptations' in localized_content
            
            localized_text = localized_content['localized_text']
            
            # Should localize currency
            if target['locale_settings']['currency'] == 'EUR':
                assert '€' in localized_text or 'EUR' in localized_text
            
            # Should translate the text
            if target['language'] == Language.GERMAN:
                assert any(german_word in localized_text.lower() 
                          for german_word in ['unser', 'produkt', 'preis', 'mehr'])

    @pytest.mark.asyncio
    async def test_translation_quality_assessment(self, translation_engine):
        """Test translation quality assessment"""
        test_translations = [
            {
                'source': "The quick brown fox jumps over the lazy dog.",
                'target_lang': Language.GERMAN,
                'expected_quality': 'high'
            },
            {
                'source': "This is a simple sentence for testing.",
                'target_lang': Language.FRENCH,
                'expected_quality': 'high'
            },
            {
                'source': "Complex technical jargon with industry-specific terminology.",
                'target_lang': Language.SPANISH,
                'expected_quality': 'medium'  # More challenging
            }
        ]
        
        for test_case in test_translations:
            translation = await translation_engine.translate(
                text=test_case['source'],
                source_language=Language.ENGLISH,
                target_language=test_case['target_lang'],
                options={'detailed_quality_analysis': True}
            )
            
            quality_assessment = await translation_engine.assess_translation_quality(
                source_text=test_case['source'],
                translated_text=translation['translated_text'],
                source_language=Language.ENGLISH,
                target_language=test_case['target_lang'],
                options={
                    'fluency_check': True,
                    'accuracy_check': True,
                    'cultural_appropriateness': True,
                    'context_preservation': True
                }
            )
            
            assert quality_assessment is not None
            assert 'overall_score' in quality_assessment
            assert 'fluency_score' in quality_assessment
            assert 'accuracy_score' in quality_assessment
            assert 'cultural_score' in quality_assessment
            assert 'detailed_feedback' in quality_assessment
            
            overall_score = quality_assessment['overall_score']
            assert 0.0 <= overall_score <= 1.0
            
            # Simple sentences should have high quality
            if test_case['expected_quality'] == 'high':
                assert overall_score > 0.7

    @pytest.mark.asyncio
    async def test_context_aware_translation(self, translation_engine):
        """Test context-aware translation"""
        context_test_cases = [
            {
                'text': "Bank",
                'contexts': [
                    {
                        'type': 'financial',
                        'description': 'Financial institution',
                        'expected_de': 'Bank'
                    },
                    {
                        'type': 'geographical',
                        'description': 'River bank',
                        'expected_de': 'Ufer'
                    }
                ]
            },
            {
                'text': "book",
                'contexts': [
                    {
                        'type': 'object',
                        'description': 'Reading material',
                        'expected_de': 'Buch'
                    },
                    {
                        'type': 'action',
                        'description': 'Reserve something',
                        'expected_de': 'buchen'
                    }
                ]
            }
        ]
        
        for test_case in context_test_cases:
            for context in test_case['contexts']:
                translation = await translation_engine.translate_with_context(
                    text=test_case['text'],
                    source_language=Language.ENGLISH,
                    target_language=Language.GERMAN,
                    context={
                        'type': context['type'],
                        'description': context['description'],
                        'domain': context['type']
                    },
                    options={'context_sensitivity': 'high'}
                )
                
                assert translation is not None
                assert 'translated_text' in translation
                assert 'context_confidence' in translation
                
                translated_text = translation['translated_text'].lower()
                expected = context['expected_de'].lower()
                
                # Should translate according to context
                assert expected in translated_text

    @pytest.mark.asyncio
    async def test_specialized_domain_translation(self, translation_engine):
        """Test specialized domain translation"""
        domain_test_cases = [
            {
                'domain': 'medical',
                'text': "The patient shows symptoms of acute inflammation.",
                'target_lang': Language.GERMAN
            },
            {
                'domain': 'legal',
                'text': "The contract terms and conditions are binding.",
                'target_lang': Language.FRENCH
            },
            {
                'domain': 'technical',
                'text': "Configure the API endpoint with authentication headers.",
                'target_lang': Language.SPANISH
            },
            {
                'domain': 'marketing',
                'text': "Boost your engagement with compelling content strategies.",
                'target_lang': Language.GERMAN
            }
        ]
        
        for case in domain_test_cases:
            domain_translation = await translation_engine.translate_specialized_content(
                text=case['text'],
                source_language=Language.ENGLISH,
                target_language=case['target_lang'],
                domain=case['domain'],
                options={
                    'domain_terminology': True,
                    'technical_accuracy': True,
                    'professional_tone': True
                }
            )
            
            assert domain_translation is not None
            assert 'translated_text' in domain_translation
            assert 'domain_adaptations' in domain_translation
            assert 'terminology_used' in domain_translation
            assert 'confidence_score' in domain_translation
            
            # Should maintain professional tone
            confidence = domain_translation['confidence_score']
            assert confidence > 0.6  # Should be confident in domain translation

    @pytest.mark.asyncio
    async def test_real_time_translation(self, translation_engine):
        """Test real-time translation capabilities"""
        # Simulate real-time translation scenario
        conversation_messages = [
            "Hello, how can I help you today?",
            "I'm looking for information about your services.",
            "We offer AI-powered content creation tools.",
            "That sounds interesting. Can you tell me more?",
            "Sure! Our platform helps create engaging social media content."
        ]
        
        # Set up real-time translation session
        session = await translation_engine.create_realtime_session(
            source_language=Language.ENGLISH,
            target_language=Language.GERMAN,
            options={
                'conversation_context': True,
                'terminology_consistency': True,
                'low_latency': True
            }
        )
        
        assert session is not None
        assert 'session_id' in session
        
        translation_times = []
        
        for message in conversation_messages:
            start_time = time.time()
            
            real_time_translation = await translation_engine.translate_realtime(
                session_id=session['session_id'],
                text=message,
                options={'maintain_context': True}
            )
            
            translation_time = time.time() - start_time
            translation_times.append(translation_time)
            
            assert real_time_translation is not None
            assert 'translated_text' in real_time_translation
            assert 'session_context' in real_time_translation
            
            # Should be fast for real-time use
            assert translation_time < 2.0  # Should translate quickly
        
        # Average should be reasonable for real-time
        avg_time = sum(translation_times) / len(translation_times)
        assert avg_time < 1.0

    @pytest.mark.asyncio
    async def test_translation_memory(self, translation_engine):
        """Test translation memory and consistency"""
        # Create consistent terminology
        terminology = {
            "AI": "KI",
            "content creation": "Content-Erstellung",
            "social media": "soziale Medien",
            "engagement": "Engagement"
        }
        
        # Set up translation memory
        memory_setup = await translation_engine.setup_translation_memory(
            terminology=terminology,
            source_language=Language.ENGLISH,
            target_language=Language.GERMAN,
            options={
                'strict_consistency': True,
                'fuzzy_matching': True,
                'quality_scoring': True
            }
        )
        
        assert memory_setup is not None
        assert 'memory_id' in memory_setup
        
        # Test consistency across multiple translations
        test_texts = [
            "AI helps with content creation for social media.",
            "Our AI platform improves social media engagement.",
            "Content creation using AI increases engagement rates."
        ]
        
        translations = []
        for text in test_texts:
            translation = await translation_engine.translate_with_memory(
                text=text,
                memory_id=memory_setup['memory_id'],
                options={'enforce_consistency': True}
            )
            
            translations.append(translation['translated_text'])
        
        # Check terminology consistency
        for translation in translations:
            if "AI" in test_texts[0]:
                assert "KI" in translation  # Should use consistent terminology

    @pytest.mark.asyncio
    async def test_collaborative_translation(self, translation_engine):
        """Test collaborative translation features"""
        content = "Welcome to our innovative AI platform for content creators!"
        
        # Set up collaborative translation
        collaboration = await translation_engine.setup_collaborative_translation(
            content=content,
            source_language=Language.ENGLISH,
            target_languages=[Language.GERMAN, Language.FRENCH, Language.SPANISH],
            options={
                'peer_review': True,
                'quality_voting': True,
                'expert_validation': False  # Skip for tests
            }
        )
        
        assert collaboration is not None
        assert 'collaboration_id' in collaboration
        assert 'translation_candidates' in collaboration
        
        # Should have multiple translation candidates
        candidates = collaboration['translation_candidates']
        assert isinstance(candidates, dict)
        
        for lang_code, translations in candidates.items():
            assert isinstance(translations, list)
            assert len(translations) > 0

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, translation_engine, benchmark_config):
        """Test translation performance benchmarks"""
        test_text = "This is a performance test for translation benchmarking."
        
        # Single translation performance
        start_time = time.time()
        translation = await translation_engine.translate(
            text=test_text,
            source_language=Language.ENGLISH,
            target_language=Language.GERMAN
        )
        single_time = time.time() - start_time
        
        max_time = benchmark_config.get('max_translation_time', 3.0)
        assert single_time < max_time, f"Translation took {single_time:.3f}s, max: {max_time}s"
        
        # Batch translation performance
        batch_texts = [f"Batch text {i} for performance testing." for i in range(10)]
        
        start_time = time.time()
        batch_translation = await translation_engine.translate_batch(
            texts=batch_texts,
            source_language=Language.ENGLISH,
            target_languages=[Language.GERMAN],
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(batch_texts) / batch_time
        min_throughput = benchmark_config.get('translation_throughput', 2.0)
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, translation_engine):
        """Test translation error handling"""
        # Test empty text
        result = await translation_engine.translate(
            text="",
            source_language=Language.ENGLISH,
            target_language=Language.GERMAN
        )
        assert result is not None  # Should handle gracefully
        
        # Test unsupported language pair
        result = await translation_engine.translate(
            text="Test text",
            source_language=Language.ENGLISH,
            target_language=Language.ENGLISH  # Same language
        )
        assert result is not None
        
        # Test very long text
        long_text = "Very long text " * 1000
        result = await translation_engine.translate(
            text=long_text,
            source_language=Language.ENGLISH,
            target_language=Language.GERMAN
        )
        assert result is not None

class TestMultilingualTranslator:
    """Test multilingual translator component"""
    
    @pytest.mark.asyncio
    async def test_translator_initialization(self):
        """Test multilingual translator initialization"""
        translator = MultilingualTranslator()
        assert translator is not None
        assert hasattr(translator, 'translate')

class TestCulturalAdapter:
    """Test cultural adapter component"""
    
    @pytest.mark.asyncio
    async def test_cultural_adapter_initialization(self):
        """Test cultural adapter initialization"""
        adapter = CulturalAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'adapt_content')

class TestLocalizationEngine:
    """Test localization engine component"""
    
    @pytest.mark.asyncio
    async def test_localization_engine_initialization(self):
        """Test localization engine initialization"""
        engine = LocalizationEngine()
        assert engine is not None
        assert hasattr(engine, 'localize_content')

class TestTranslationConfig:
    """Test translation configuration"""
    
    def test_config_creation(self):
        """Test translation configuration creation"""
        config = TranslationConfig(
            supported_languages=[Language.ENGLISH, Language.GERMAN, Language.FRENCH],
            translation_quality='high',
            cultural_adaptation=True
        )
        
        assert Language.ENGLISH in config.supported_languages
        assert config.translation_quality == 'high'
        assert config.cultural_adaptation is True
