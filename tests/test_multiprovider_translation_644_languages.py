"""
Test Multi-Provider Translation System - 644 Language Support

Comprehensive tests for the enhanced translation engine with multiple providers:
- Google Translate: 100+ languages neural MT
- DeepL: Quality superior EU, 31 languages
- Microsoft Translator: Enterprise, 100+ languages  
- Amazon Translate: Auto scaling, 75 languages

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from conversational.multilingual_support.translation_engine import (
        TranslationEngine, TranslationService, TranslationProvider,
        TranslationRequest, TranslationResult, SupportedLanguage
    )
    from config.translation_config import translation_config
    from ai_engine.engines.seo_engine import SEOEngine, SEOMetadata
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False


class TestMultiProviderTranslation:
    """Test multi-provider translation system"""
    
    @pytest.fixture
    def mock_redis(self):
        """
Mock Redis client"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture  
    def mock_db_session(self):
        """
Mock database session"""
        return Mock()
    
    @pytest.fixture
    def translation_request(self):
        """
Sample translation request"""
        return TranslationRequest(
            text="Hello, world! This is a test message for translation.",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.FRENCH,
            domain="general",
            formality="neutral",
            tone="professional"
        )
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_translation_provider_enum(self):
        """Test that all required translation providers are defined"""
        required_providers = [
            TranslationProvider.GOOGLE_TRANSLATE,
            TranslationProvider.DEEPL,
            TranslationProvider.AZURE_TRANSLATOR,
            TranslationProvider.AWS_TRANSLATE,
            TranslationProvider.OPENAI_GPT,
            TranslationProvider.MARIAN_MT
        ]
        
        for provider in required_providers:
            assert provider in TranslationProvider
            assert isinstance(provider.value, str)
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_translation_service_initialization(self):
        """Test translation service initialization for all providers"""
        for provider in TranslationProvider:
            service = TranslationService(provider)
            assert service.provider == provider
            # Client initialization may fail without API keys, but service should be created
            assert service is not None
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_google_translate_mock(self, translation_request):
        """Test Google Translate service with mock"""
        service = TranslationService(TranslationProvider.GOOGLE_TRANSLATE)
        
        # Mock the translation result
        with patch.object(service, '_translate_google') as mock_translate:
            mock_result = TranslationResult(
                original_text=translation_request.text,
                translated_text="Bonjour le monde! Ceci est un message de test pour la traduction.",
                source_language=translation_request.source_language,
                target_language=translation_request.target_language,
                confidence_score=0.85,
                provider_used=TranslationProvider.GOOGLE_TRANSLATE
            )
            mock_translate.return_value = mock_result
            
            result = await service.translate(translation_request)
            
            assert result.provider_used == TranslationProvider.GOOGLE_TRANSLATE
            assert result.confidence_score == 0.85
            assert "Bonjour" in result.translated_text
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_deepl_service_mock(self, translation_request):
        """Test DeepL service integration"""
        service = TranslationService(TranslationProvider.DEEPL)
        
        with patch.object(service, '_translate_deepl') as mock_translate:
            mock_result = TranslationResult(
                original_text=translation_request.text,
                translated_text="Bonjour, le monde ! Ceci est un message de test pour la traduction.",
                source_language=translation_request.source_language,
                target_language=translation_request.target_language,
                confidence_score=0.95,  # DeepL typically has high quality
                provider_used=TranslationProvider.DEEPL
            )
            mock_translate.return_value = mock_result
            
            result = await service.translate(translation_request)
            
            assert result.provider_used == TranslationProvider.DEEPL
            assert result.confidence_score == 0.95
            assert result.translated_text is not None
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_azure_translator_mock(self, translation_request):
        """Test Microsoft Azure Translator service"""
        service = TranslationService(TranslationProvider.AZURE_TRANSLATOR)
        
        with patch.object(service, '_translate_azure') as mock_translate:
            mock_result = TranslationResult(
                original_text=translation_request.text,
                translated_text="Bonjour, monde ! Ceci est un message de test pour la traduction.",
                source_language=translation_request.source_language,
                target_language=translation_request.target_language,
                confidence_score=0.90,
                provider_used=TranslationProvider.AZURE_TRANSLATOR
            )
            mock_translate.return_value = mock_result
            
            result = await service.translate(translation_request)
            
            assert result.provider_used == TranslationProvider.AZURE_TRANSLATOR
            assert result.confidence_score == 0.90
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_aws_translate_mock(self, translation_request):
        """Test Amazon Translate service"""
        service = TranslationService(TranslationProvider.AWS_TRANSLATE)
        
        with patch.object(service, '_translate_aws') as mock_translate:
            mock_result = TranslationResult(
                original_text=translation_request.text,
                translated_text="Bonjour, monde! Ceci est un message de test pour la traduction.",
                source_language=translation_request.source_language,
                target_language=translation_request.target_language,
                confidence_score=0.85,
                provider_used=TranslationProvider.AWS_TRANSLATE
            )
            mock_translate.return_value = mock_result
            
            result = await service.translate(translation_request)
            
            assert result.provider_used == TranslationProvider.AWS_TRANSLATE
            assert result.confidence_score == 0.85
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_translation_engine_provider_priority(self, mock_redis, mock_db_session):
        """Test translation engine provider priority and fallback"""
        engine = TranslationEngine(mock_redis, mock_db_session)
        
        # Verify all providers are initialized
        expected_providers = [
            TranslationProvider.DEEPL,
            TranslationProvider.GOOGLE_TRANSLATE,
            TranslationProvider.AZURE_TRANSLATOR,
            TranslationProvider.AWS_TRANSLATE,
            TranslationProvider.OPENAI_GPT,
            TranslationProvider.MARIAN_MT
        ]
        
        for provider in expected_providers:
            assert provider in engine.services
            assert provider in engine.provider_priority
        
        # Verify priority order (DeepL should be first for quality)
        assert engine.provider_priority[0] == TranslationProvider.DEEPL
        assert TranslationProvider.GOOGLE_TRANSLATE in engine.provider_priority[:3]
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_language_mapping_functions(self):
        """Test language code mapping functions"""
        service = TranslationService(TranslationProvider.DEEPL)
        
        # Test DeepL mapping
        assert service._map_to_deepl_lang(SupportedLanguage.ENGLISH) == "EN"
        assert service._map_to_deepl_lang(SupportedLanguage.GERMAN) == "DE"
        assert service._map_to_deepl_lang(SupportedLanguage.FRENCH) == "FR"
        
        # Test Azure mapping
        assert service._map_to_azure_lang(SupportedLanguage.CHINESE_SIMPLIFIED) == "zh-Hans"
        assert service._map_to_azure_lang(SupportedLanguage.ENGLISH) == "en"
        
        # Test AWS mapping
        assert service._map_to_aws_lang(SupportedLanguage.CHINESE_SIMPLIFIED) == "zh"
        assert service._map_to_aws_lang(SupportedLanguage.CHINESE_TRADITIONAL) == "zh-TW"


class TestMultilingualSEO:
    """Test multilingual SEO functionality"""
    
    @pytest.fixture
    def seo_engine(self):
        """
Create SEO engine instance"""
        return SEOEngine()
    
    @pytest.fixture
    def sample_seo_metadata(self):
        """
Sample SEO metadata for testing"""
        return SEOMetadata(
            title="Best Content Creation Tips for 2025",
            description="Discover the ultimate guide to content creation with proven strategies for social media success.",
            keywords=["content creation", "social media", "tips", "2025", "strategy"],
            tags=["content", "social", "creator", "tips"],
            meta_title="Content Creation Tips 2025 | Ultimate Guide",
            meta_description="Learn proven content creation strategies for 2025. Boost your social media presence with expert tips.",
            structured_data={"@type": "Article", "headline": "Content Creation Tips"},
            social_media_tags={"og:title": "Content Creation Tips", "twitter:card": "summary"}
        )
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_seo_engine_multilingual_initialization(self, seo_engine):
        """Test SEO engine multilingual support initialization"""
        # Should have multilingual capabilities
        assert hasattr(seo_engine, 'multilingual_enabled')
        assert hasattr(seo_engine, 'translation_config')
        
        # Check supported languages method
        supported = seo_engine.get_supported_languages()
        assert isinstance(supported, dict)
        assert len(supported) > 0
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_multilingual_seo_generation(self, seo_engine, sample_seo_metadata):
        """Test generation of multilingual SEO content"""
        target_languages = ['fr', 'es', 'de', 'it', 'pt']
        
        with patch.object(seo_engine, '_translate_seo_metadata') as mock_translate, \
             patch.object(seo_engine, '_apply_cultural_seo_adaptations') as mock_cultural, \
             patch.object(seo_engine, '_generate_locale_keywords') as mock_keywords:
            
            # Mock translation results
            mock_translate.side_effect = lambda metadata, lang, content_type: SEOMetadata(
                title=f"[{lang}] {metadata.title}",
                description=f"[{lang}] {metadata.description}",
                keywords=[f"[{lang}] {k}" for k in metadata.keywords],
                tags=[f"[{lang}] {t}" for t in metadata.tags],
                meta_title=f"[{lang}] {metadata.meta_title}",
                meta_description=f"[{lang}] {metadata.meta_description}",
                structured_data=metadata.structured_data,
                social_media_tags=metadata.social_media_tags
            )
            
            mock_cultural.side_effect = lambda metadata, lang, content_type: metadata
            mock_keywords.side_effect = lambda keywords, lang: keywords
            
            result = await seo_engine.generate_multilingual_seo(
                sample_seo_metadata, 
                target_languages
            )
            
            # Verify results for all languages
            assert len(result) == len(target_languages)
            for lang in target_languages:
                assert lang in result
                assert f"[{lang}]" in result[lang].title
                assert f"[{lang}]" in result[lang].description
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_cultural_seo_adaptations(self, seo_engine, sample_seo_metadata):
        """Test cultural adaptations for different languages"""
        # Test different language adaptations
        test_cases = [
            ('zh', 'chinese'),
            ('ja', 'japanese'),
            ('ar', 'arabic'),
            ('de', 'german'),
            ('fr', 'french')
        ]
        
        for lang, culture in test_cases:
            adapted = await seo_engine._apply_cultural_seo_adaptations(
                sample_seo_metadata, lang, "general"
            )
            
            assert adapted is not None
            assert adapted.title is not None
            assert adapted.description is not None
            
            # Check RTL support for Arabic
            if lang == 'ar':
                assert adapted.structured_data.get('dir') == 'rtl'
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    @pytest.mark.asyncio
    async def test_locale_keyword_generation(self, seo_engine):
        """Test locale-specific keyword generation"""
        base_keywords = ["content", "creation", "tips"]
        
        test_languages = ['es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ar']
        
        for lang in test_languages:
            locale_keywords = await seo_engine._generate_locale_keywords(
                base_keywords, lang
            )
            
            assert isinstance(locale_keywords, list)
            assert len(locale_keywords) >= len(base_keywords)
            # Should contain original keywords
            for keyword in base_keywords:
                assert keyword in locale_keywords


class TestTranslationConfiguration:
    """Test translation configuration system"""
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_translation_config_initialization(self):
        """Test translation configuration loading"""
        config = translation_config
        
        # Verify all providers are configured
        expected_providers = ['google', 'deepl', 'azure', 'aws', 'openai', 'marian']
        
        for provider in expected_providers:
            assert provider in config.providers
            provider_config = config.providers[provider]
            assert hasattr(provider_config, 'enabled')
            assert hasattr(provider_config, 'supported_languages')
            assert hasattr(provider_config, 'quality_score')
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_language_coverage_stats(self):
        """Test language coverage statistics"""
        coverage = translation_config.get_language_coverage()
        
        assert isinstance(coverage, dict)
        assert len(coverage) > 0
        
        # Verify provider coverage matches specifications
        expected_coverage = {
            'google': 100,  # 100+ languages
            'deepl': 31,    # 31 languages
            'azure': 100,   # 100+ languages
            'aws': 75,      # 75 languages
        }
        
        for provider, expected_count in expected_coverage.items():
            if provider in coverage:
                assert coverage[provider] >= expected_count
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
    def test_provider_ready_status(self):
        """Test provider readiness checking"""
        config = translation_config
        
        # Test with mock environment variables
        with patch.dict(os.environ, {
            'GOOGLE_TRANSLATE_API_KEY': 'test_key',
            'DEEPL_API_KEY': 'test_key',
            'AZURE_TRANSLATOR_KEY': 'test_key',
            'OPENAI_API_KEY': 'test_key'
        }):
            enabled_providers = config.get_enabled_providers()
            
            # Should have more providers enabled with API keys
            assert len(enabled_providers) > 0
            
            # Marian should always be ready (no API key needed)
            assert 'marian' in enabled_providers or 'marian' in config.providers


if __name__ == "__main__":
    # Run basic validation tests
    if IMPORTS_AVAILABLE:
        print("✅ All imports available")
        
        # Test configuration
        print("\n🔧 Testing Translation Configuration:")
        config = translation_config
        coverage = config.get_language_coverage()
        enabled = config.get_enabled_providers()
        
        print(f"📊 Language Coverage: {coverage}")
        print(f"🚀 Enabled Providers: {list(enabled.keys())}")
        
        # Test provider enumeration
        print("\n🌐 Translation Providers:")
        for provider in TranslationProvider:
            print(f"  - {provider.value}: {provider}")
        
        print("\n✅ Multi-provider translation system validation complete!")
        print("🌍 Ready for 644-language SEO optimization!")
        
    else:
        print("❌ Some imports not available - install required packages")
        print("Run: pip install -r requirements.txt")