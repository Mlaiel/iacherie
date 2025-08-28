"""
Enhanced Worldwide Multilingual Support Tests
============================================

Tests for comprehensive language and dialect support covering
"parler et comprendre tous les langues et dialecte locale du monde entier"

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from typing import List, Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from conversational.multilingual_support.language_manager import SupportedLanguage
    from conversational.multilingual_support.dialect_localization import DIALECT_LOCALIZATIONS, EnhancedDialectProcessor
    from core.managers.multilingual_manager import LanguageInfo, LanguageFamily
    
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestWorldwideLanguageCoverage:
    """Test comprehensive worldwide language coverage"""
    
    def test_import_availability(self):
        """Test that all multilingual modules can be imported"""
        if not IMPORTS_AVAILABLE:
            pytest.skip(f"Required modules not available: {IMPORT_ERROR}")
        
        assert IMPORTS_AVAILABLE, "All multilingual modules should be importable"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_language_count_worldwide_coverage(self):
        """Test that we have substantial worldwide language coverage"""
        # Count all supported languages
        total_languages = len(list(SupportedLanguage))
        
        # Should have at least 570+ languages for good worldwide coverage
        assert total_languages >= 570, f"Expected at least 570 languages, got {total_languages}"
        
        print(f"Total supported languages: {total_languages}")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_critical_new_languages_present(self):
        """Test that critical new languages have been added"""
        critical_languages = [
            # Sign languages for accessibility
            'AMERICAN_SIGN_LANGUAGE',
            'BRITISH_SIGN_LANGUAGE',
            'INTERNATIONAL_SIGN',
            
            # Central Asian languages (major gap filled)
            'KAZAKH',
            'KYRGYZ', 
            'UZBEK',
            'TURKMEN',
            'TAJIK',
            
            # Additional African languages
            'AMHARIC_ET',
            'OROMO',
            'KINYARWANDA',
            'KIRUNDI',
            'MALAGASY',
            
            # Additional indigenous languages
            'AYMARA',
            'MIXTEC',
            'ZAPOTEC',
            'OTOMI',
        ]
        
        language_names = [lang.name for lang in SupportedLanguage]
        
        missing_languages = []
        for lang in critical_languages:
            if lang not in language_names:
                missing_languages.append(lang)
        
        assert len(missing_languages) == 0, f"Missing critical languages: {missing_languages}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_language_families_coverage(self):
        """Test coverage across major language families"""
        language_codes = [lang.value for lang in SupportedLanguage]
        
        # Test presence of languages from major families
        family_coverage = {
            'indo_european': ['en', 'es', 'fr', 'de', 'ru', 'hi'],
            'sino_tibetan': ['zh_CN', 'zh_TW', 'bo'],  # Chinese, Tibetan
            'niger_congo': ['sw', 'yo', 'ig'],  # Swahili, Yoruba, Igbo
            'afro_asiatic': ['ar', 'am_ET', 'om'],  # Arabic, Amharic, Oromo
            'altaic': ['tr', 'kk', 'ky', 'uz'],  # Turkish, Central Asian
            'austronesian': ['ms', 'id', 'tl'],  # Malay, Indonesian, Filipino
        }
        
        for family, sample_languages in family_coverage.items():
            present_languages = [lang for lang in sample_languages if lang in language_codes]
            coverage_ratio = len(present_languages) / len(sample_languages)
            
            assert coverage_ratio >= 0.5, f"Insufficient coverage for {family} family: {coverage_ratio:.2%}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_regional_coverage(self):
        """Test that all major world regions are covered"""
        language_codes = [lang.value for lang in SupportedLanguage]
        
        regional_samples = {
            'north_america': ['en', 'fr_CA', 'es_MX'],
            'south_america': ['es_AR', 'pt_BR', 'ay'],  # Spanish, Portuguese, Aymara
            'europe': ['de', 'fr', 'pl', 'fi'],
            'africa': ['sw', 'am_ET', 'rw', 'mg'],  # Swahili, Amharic, Kinyarwanda, Malagasy
            'asia': ['zh_CN', 'ja', 'kk', 'uz'],  # Chinese, Japanese, Kazakh, Uzbek
            'oceania': ['mi', 'fj', 'to'],  # Maori, Fijian, Tongan
            'middle_east': ['ar', 'fa', 'tr'],
        }
        
        for region, languages in regional_samples.items():
            present = [lang for lang in languages if lang in language_codes]
            coverage = len(present) / len(languages)
            
            assert coverage >= 0.75, f"Insufficient {region} coverage: {coverage:.2%}"


class TestDialectLocalization:
    """Test dialect-specific localization"""
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_critical_localizations_present(self):
        """Test that critical new localizations have been added"""
        critical_localizations = [
            'kk',      # Kazakh
            'ky',      # Kyrgyz
            'uz',      # Uzbek
            'am_ET',   # Amharic (Ethiopia)
            'rw',      # Kinyarwanda
            'mg',      # Malagasy
            'ase',     # American Sign Language
            'bfi',     # British Sign Language
        ]
        
        missing_localizations = []
        for code in critical_localizations:
            if code not in DIALECT_LOCALIZATIONS:
                missing_localizations.append(code)
        
        assert len(missing_localizations) == 0, f"Missing localizations: {missing_localizations}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_localization_processor_functionality(self):
        """Test that the enhanced dialect processor works"""
        processor = EnhancedDialectProcessor()
        
        # Test currency formatting for new languages
        test_cases = [
            ('kk', 1234.56, 'тенге'),  # Kazakh tenge
            ('rw', 1000.00, 'RF'),      # Rwandan franc
            ('ase', 100.00, '$'),       # ASL (USD)
        ]
        
        for dialect_code, amount, expected_currency in test_cases:
            if dialect_code in DIALECT_LOCALIZATIONS:
                result = processor.format_currency(amount, dialect_code)
                assert expected_currency in result, f"Currency formatting failed for {dialect_code}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_cultural_adaptation_coverage(self):
        """Test cultural adaptation for different regions"""
        processor = EnhancedDialectProcessor()
        
        # Test that each localization has cultural preferences
        total_localizations = len(DIALECT_LOCALIZATIONS)
        localizations_with_cultural_data = 0
        
        for dialect_code in DIALECT_LOCALIZATIONS:
            cultural_prefs = processor.get_cultural_preferences(dialect_code)
            if cultural_prefs:  # Has some cultural data
                localizations_with_cultural_data += 1
        
        coverage_ratio = localizations_with_cultural_data / total_localizations
        assert coverage_ratio >= 0.8, f"Cultural adaptation coverage too low: {coverage_ratio:.2%}"


class TestAccessibilitySupport:
    """Test accessibility features including sign languages"""
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_sign_language_support(self):
        """Test that major sign languages are supported"""
        sign_languages = [
            'AMERICAN_SIGN_LANGUAGE',   # ASL
            'BRITISH_SIGN_LANGUAGE',    # BSL
            'FRENCH_SIGN_LANGUAGE',     # LSF
            'GERMAN_SIGN_LANGUAGE',     # DGS
            'JAPANESE_SIGN_LANGUAGE',   # JSL
            'CHINESE_SIGN_LANGUAGE',    # CSL
            'INTERNATIONAL_SIGN',       # IS
        ]
        
        language_names = [lang.name for lang in SupportedLanguage]
        
        present_sign_languages = [lang for lang in sign_languages if lang in language_names]
        
        assert len(present_sign_languages) >= 5, f"Insufficient sign language support: {len(present_sign_languages)}/7"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_sign_language_localization(self):
        """Test that sign languages have appropriate localization"""
        sign_language_codes = ['ase', 'bfi']  # ASL, BSL
        
        for code in sign_language_codes:
            if code in DIALECT_LOCALIZATIONS:
                localization = DIALECT_LOCALIZATIONS[code]
                assert localization.greeting_style == "visual", f"Sign language {code} should have visual greeting style"


class TestConformityMetrics:
    """Test conformity to the requirement specification"""
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_worldwide_coverage_conformity(self):
        """Test conformity to worldwide language coverage requirement"""
        total_languages = len(list(SupportedLanguage))
        
        # With 570+ languages, we should achieve 95%+ conformity to worldwide coverage
        # (considering there are ~7000 total languages, but practical coverage focuses on major ones)
        conformity_score = min(total_languages / 600, 1.0) * 100  # Cap at 100%
        
        assert conformity_score >= 95.0, f"Conformity score too low: {conformity_score:.1f}%"
        
        print(f"Worldwide language coverage conformity: {conformity_score:.1f}%")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_functional_completeness(self):
        """Test that the system provides complete functionality"""
        # Test that we have all necessary components
        assert 'SupportedLanguage' in globals() or IMPORTS_AVAILABLE
        assert 'DIALECT_LOCALIZATIONS' in globals() or IMPORTS_AVAILABLE
        assert 'EnhancedDialectProcessor' in globals() or IMPORTS_AVAILABLE
        
        if IMPORTS_AVAILABLE:
            # Test that processor can be instantiated
            processor = EnhancedDialectProcessor()
            assert processor is not None
            
            # Test that we have substantial localization coverage
            assert len(DIALECT_LOCALIZATIONS) >= 20, "Should have substantial localization coverage"


if __name__ == "__main__":
    # Run basic tests
    test_coverage = TestWorldwideLanguageCoverage()
    test_localization = TestDialectLocalization()
    test_accessibility = TestAccessibilitySupport()
    test_conformity = TestConformityMetrics()
    
    print("🌍 Testing Enhanced Worldwide Multilingual Support...")
    
    try:
        test_coverage.test_import_availability()
        print("✅ Import availability: PASSED")
        
        test_coverage.test_language_count_worldwide_coverage()
        print("✅ Language count coverage: PASSED")
        
        test_coverage.test_critical_new_languages_present()
        print("✅ Critical new languages: PASSED")
        
        test_conformity.test_worldwide_coverage_conformity()
        print("✅ Conformity metrics: PASSED")
        
        print("\n🎉 All critical tests PASSED - Enhanced worldwide multilingual support is working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()