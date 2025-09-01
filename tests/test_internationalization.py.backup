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

"""Comprehensive test suite for Ainflue AI-powered content protection platform.
Tests the internationalization system including Amazigh/Berber language support.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from core.i18n.manager import InternationalizationManager, LanguageScript, LanguageRegion

@pytest.fixture
def i18n_manager():
    """Create an i18n manager instance for testing."""
    return InternationalizationManager()

class TestInternationalizationManager:
    """Test suite for the internationalization manager."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, i18n_manager):
        """Test that the i18n manager initializes with all languages."""
        assert len(i18n_manager.languages) > 350  # Should have 350+ languages
        assert 'en' in i18n_manager.languages
        assert 'fr' in i18n_manager.languages
        assert 'de' in i18n_manager.languages
        assert 'ar' in i18n_manager.languages
    
    @pytest.mark.asyncio
    async def test_amazigh_berber_languages(self, i18n_manager):
        """Test that Amazigh/Berber languages are properly supported."""
        # Test primary Amazigh languages
        amazigh_codes = ['tzm', 'rif', 'shi', 'kab', 'shy', 'mzb', 'thv', 'ttq', 'taq', 'zen']
        
        for code in amazigh_codes:
            assert code in i18n_manager.languages, f"Missing Amazigh language: {code}"
            lang = i18n_manager.languages[code]
            assert lang.script == LanguageScript.TIFINAGH
            assert lang.region == LanguageRegion.AFRICA
    
    @pytest.mark.asyncio
    async def test_north_african_dialects(self, i18n_manager):
        """Test that North African Arabic dialects are supported."""
        # Test some Tunisian dialects
        assert 'ar-TN-tunis' in i18n_manager.languages
        assert 'ar-TN-sfax' in i18n_manager.languages
        
        # Test some Algerian dialects
        assert 'ar-DZ-algiers' in i18n_manager.languages
        assert 'ar-DZ-oran' in i18n_manager.languages
        
        # Test some Moroccan dialects
        assert 'ar-MA-casablanca' in i18n_manager.languages
        assert 'ar-MA-fes' in i18n_manager.languages
        
        # Test Hassaniyya
        assert 'mey' in i18n_manager.languages
    
    @pytest.mark.asyncio
    async def test_language_detection(self, i18n_manager):
        """Test language detection functionality."""
        # Test Arabic text detection
        arabic_text = "مرحبا بكم في عالم الذكاء الاصطناعي"
        detected = await i18n_manager.detect_language(arabic_text)
        assert detected == 'ar'
        
        # Test Tifinagh text detection
        tifinagh_text = "ⴰⵣⵓⵍ ⴼⵍⵍⴰⵡⵏ"  # Amazigh greeting
        detected = await i18n_manager.detect_language(tifinagh_text)
        assert detected == 'tzm'
        
        # Test English text detection
        english_text = "Welcome to AI-powered content protection"
        detected = await i18n_manager.detect_language(english_text)
        assert detected == 'en'
    
    @pytest.mark.asyncio
    async def test_translation_fallback(self, i18n_manager):
        """Test translation fallback mechanism."""
        # Test getting translation for unsupported key
        translation = await i18n_manager.get_translation(
            'test_key', 'tzm', default='Default text'
        )
        assert translation == 'Default text'
        
        # Test fallback chain
        translation = await i18n_manager.get_translation(
            'test_key', 'rif', default='Fallback text'
        )
        assert translation in ['Fallback text', 'test_key']
    
    @pytest.mark.asyncio
    async def test_rtl_language_support(self, i18n_manager):
        """Test right-to-left language support."""
        rtl_languages = i18n_manager.get_rtl_languages()
        
        # Arabic and Hebrew should be RTL
        assert 'ar' in [lang for lang in i18n_manager.languages if i18n_manager.languages[lang].rtl]
        assert 'he' in [lang for lang in i18n_manager.languages if i18n_manager.languages[lang].rtl]
        
        # Check Arabic dialects are RTL
        for lang_code in i18n_manager.languages:
            if lang_code.startswith('ar-'):
                assert i18n_manager.languages[lang_code].rtl
    
    @pytest.mark.asyncio
    async def test_currency_formatting(self, i18n_manager):
        """Test currency formatting for different locales."""
        # Test USD formatting
        formatted = await i18n_manager.format_currency(1234.56, 'USD', 'en')
        assert '1234.56' in formatted
        assert 'USD' in formatted
        
        # Test EUR formatting
        formatted = await i18n_manager.format_currency(1234.56, 'EUR', 'fr')
        assert '1234.56' in formatted
        assert 'EUR' in formatted
    
    @pytest.mark.asyncio
    async def test_number_formatting(self, i18n_manager):
        """Test number formatting for different locales."""
        # Test English number formatting
        formatted = await i18n_manager.format_number(1234567, 'en')
        assert '1,234,567' in formatted
        
        # Test float formatting
        formatted = await i18n_manager.format_number(1234.56, 'en')
        assert '1,234.56' in formatted
    
    def test_language_statistics(self, i18n_manager):
        """Test language statistics functionality."""
        stats = i18n_manager.get_language_statistics()
        
        assert 'total_languages' in stats
        assert 'amazigh_berber_languages' in stats
        assert 'north_african_dialects' in stats
        assert 'tifinagh_script_languages' in stats
        
        # Check we have Amazigh languages
        assert stats['amazigh_berber_languages'] >= 10
        
        # Check we have North African dialects
        assert stats['north_african_dialects'] >= 50
        
        # Check coverage is high
        assert stats['coverage_percentage'] > 90
    
    def test_language_by_region(self, i18n_manager):
        """Test getting languages by region."""
        african_languages = i18n_manager.get_languages_by_region(LanguageRegion.AFRICA)
        
        # Should include Amazigh languages
        amazigh_found = any(lang.code.startswith(('tzm', 'rif', 'shi', 'kab')) for lang in african_languages)
        assert amazigh_found
        
        # Should include Arabic dialects
        arabic_found = any(lang.code.startswith('ar-') for lang in african_languages)
        assert arabic_found
    
    def test_script_support(self, i18n_manager):
        """Test different script support."""
        # Test Tifinagh script languages
        tifinagh_languages = [
            lang for lang in i18n_manager.languages.values() 
            if lang.script == LanguageScript.TIFINAGH
        ]
        assert len(tifinagh_languages) >= 10
        
        # Test Arabic script languages
        arabic_languages = [
            lang for lang in i18n_manager.languages.values() 
            if lang.script == LanguageScript.ARABIC
        ]
        assert len(arabic_languages) >= 50
    
    @pytest.mark.asyncio
    async def test_auto_translation(self, i18n_manager):
        """Test auto-translation functionality."""
        # Test Spanish translation
        translation = await i18n_manager._auto_translate("Hello", "es")
        assert translation == "[ES] Hello"
        
        # Test French translation
        translation = await i18n_manager._auto_translate("Hello", "fr")
        assert translation == "[FR] Hello"
        
        # Test Amazigh translation
        translation = await i18n_manager._auto_translate("Hello", "tzm")
        assert translation == "[TZM] Hello"
    
    def test_language_info_access(self, i18n_manager):
        """Test accessing language information."""
        # Test English language info
        en_info = i18n_manager.get_language_info('en')
        assert en_info is not None
        assert en_info.name == 'English'
        assert en_info.native_name == 'English'
        assert en_info.script == LanguageScript.LATIN
        
        # Test Amazigh language info
        tzm_info = i18n_manager.get_language_info('tzm')
        assert tzm_info is not None
        assert tzm_info.name == 'Central Atlas Tamazight'
        assert tzm_info.script == LanguageScript.TIFINAGH
        assert tzm_info.region == LanguageRegion.AFRICA
    
    def test_supported_languages_list(self, i18n_manager):
        """Test getting list of supported languages."""
        supported = i18n_manager.get_supported_languages()
        
        # Should have many languages
        assert len(supported) > 300
        
        # All should be enabled
        assert all(lang.enabled for lang in supported)
        
        # Should include our critical languages
        codes = [lang.code for lang in supported]
        assert 'en' in codes
        assert 'ar' in codes
        assert 'tzm' in codes  # Amazigh
        assert 'ar-MA-casablanca' in codes  # Moroccan dialect


if __name__ == '__main__':
    # Run tests
    pytest.main([str(Path(__file__)), '-v'])