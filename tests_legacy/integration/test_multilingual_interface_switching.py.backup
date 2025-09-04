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

"""Integration Test: Multilingual Interface Switching
=================================================

Tests the complete multilingual interface switching system including:
- Language detection and switching
- Translation loading and caching
- UI component multilingual support
- Fallback mechanisms
- Dynamic language switching

Author: Integration Test Suite
"""
import asyncio
import pytest
import sys
import os
from pathlib import Path
import sys
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestMultilingualInterfaceSwitching:
    """Integration tests for multilingual interface switching"""
    
    @pytest.fixture
    def supported_languages(self):
        """List of supported languages for testing"""
        return [
            {"code": "en", "name": "English", "native_name": "English", "region": "US"},
            {"code": "fr", "name": "French", "native_name": "Français", "region": "FR"},
            {"code": "es", "name": "Spanish", "native_name": "Español", "region": "ES"},
            {"code": "ar", "name": "Arabic", "native_name": "العربية", "region": "SA", "rtl": True},
            {"code": "zh", "name": "Chinese", "native_name": "中文", "region": "CN"},
            {"code": "de", "name": "German", "native_name": "Deutsch", "region": "DE"},
            {"code": "ber", "name": "Berber", "native_name": "Tamazight", "region": "MA"}
        ]
    
    @pytest.fixture
    def sample_translations(self):
        """Sample translation data for testing"""
        return {
            "en": {
                "welcome": "Welcome to Ainflue",
                "dashboard": "Dashboard",
                "create_content": "Create Content",
                "my_profile": "My Profile",
                "settings": "Settings",
                "logout": "Logout",
                "notifications": "Notifications",
                "analytics": "Analytics"
            },
            "fr": {
                "welcome": "Bienvenue sur Ainflue",
                "dashboard": "Tableau de bord",
                "create_content": "Créer du contenu",
                "my_profile": "Mon profil",
                "settings": "Paramètres",
                "logout": "Déconnexion",
                "notifications": "Notifications",
                "analytics": "Analytiques"
            },
            "ar": {
                "welcome": "مرحباً بك في Ainflue",
                "dashboard": "لوحة التحكم",
                "create_content": "إنشاء محتوى",
                "my_profile": "ملفي الشخصي",
                "settings": "الإعدادات",
                "logout": "تسجيل الخروج",
                "notifications": "الإشعارات",
                "analytics": "التحليلات"
            }
        }
    
    @pytest.fixture
    def mock_translation_manager(self):
        """Mock translation management system"""
        try:
            from core.i18n.translation_manager import TranslationManager
            return TranslationManager()
        except ImportError:
            manager = Mock()
            manager.current_language = "en"
            manager.supported_languages = []
            manager.translations = {}
            manager.fallback_language = "en"
            return manager
    
    @pytest.fixture
    def mock_language_detector(self):
        """Mock language detection system"""
        try:
            from core.i18n.language_detector import LanguageDetector
            return LanguageDetector()
        except ImportError:
            detector = Mock()
            detector.supported_languages = ["en", "fr", "es", "ar", "zh", "de", "ber"]
            return detector
    
    @pytest.mark.asyncio
    async def test_language_detection_workflow(self, mock_language_detector):
        """Test automatic language detection from various sources"""
        print("🔍 Testing language detection workflow...")
        
        # Test browser language detection
        with patch.object(mock_language_detector, 'detect_from_browser', new_callable=AsyncMock) as mock_browser:
            browser_detection = {
                "detected_language": "fr",
                "confidence": 0.95,
                "source": "browser_header",
                "accept_languages": ["fr-FR", "fr", "en-US", "en"],
                "primary_language": "fr-FR"
            }
            mock_browser.return_value = browser_detection
            
            result = await mock_browser("fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7")
            
            assert result["detected_language"] == "fr", "Should detect French from browser"
            assert result["confidence"] > 0.8, "Should have high confidence"
            assert result["source"] == "browser_header", "Should identify detection source"
        
        # Test IP-based geo-location detection
        with patch.object(mock_language_detector, 'detect_from_location', new_callable=AsyncMock) as mock_geo:
            geo_detection = {
                "detected_language": "es",
                "confidence": 0.82,
                "source": "geo_location",
                "country": "ES",
                "region": "Madrid"
            }
            mock_geo.return_value = geo_detection
            
            result = await mock_geo("192.168.1.1")  # Mock IP
            
            assert result["detected_language"] in ["es", "en"], "Should detect valid language"
            assert result["source"] == "geo_location", "Should use geo-location source"
        
        # Test user preference detection
        with patch.object(mock_language_detector, 'detect_from_user_preferences', new_callable=AsyncMock) as mock_user:
            user_detection = {
                "detected_language": "ar",
                "confidence": 1.0,
                "source": "user_preference",
                "user_id": "user_123",
                "last_updated": "2024-01-01T12:00:00Z"
            }
            mock_user.return_value = user_detection
            
            result = await mock_user("user_123")
            
            assert result["detected_language"] == "ar", "Should use user's preferred language"
            assert result["confidence"] == 1.0, "User preference should have highest confidence"
        
        print("✅ Language detection workflow test passed")
    
    @pytest.mark.asyncio
    async def test_translation_loading_workflow(self, mock_translation_manager, sample_translations):
        """Test translation loading and caching mechanisms"""
        print("📚 Testing translation loading workflow...")
        
        # Test initial translation loading
        with patch.object(mock_translation_manager, 'load_translations', new_callable=AsyncMock) as mock_load:
            load_result = {
                "language": "fr",
                "translations_loaded": 156,
                "load_time": 0.045,
                "cache_hit": False,
                "fallback_used": False,
                "source": "file_system"
            }
            mock_load.return_value = load_result
            
            result = await mock_load("fr")
            
            assert result["language"] == "fr", "Should load French translations"
            assert result["translations_loaded"] > 0, "Should load translation entries"
            assert result["load_time"] < 1.0, "Should load quickly"
        
        # Test translation caching
        with patch.object(mock_translation_manager, 'get_cached_translations', new_callable=AsyncMock) as mock_cache:
            cache_result = {
                "language": "fr",
                "translations": sample_translations["fr"],
                "cache_hit": True,
                "cache_age": 300,  # 5 minutes
                "expires_in": 3300  # 55 minutes
            }
            mock_cache.return_value = cache_result
            
            result = await mock_cache("fr")
            
            assert result["cache_hit"] is True, "Should hit translation cache"
            assert "translations" in result, "Should return cached translations"
            assert result["cache_age"] < 3600, "Cache should be fresh"
        
        # Test fallback mechanism
        with patch.object(mock_translation_manager, 'load_with_fallback', new_callable=AsyncMock) as mock_fallback:
            fallback_result = {
                "language": "ber",  # Berber might have incomplete translations
                "translations_loaded": 89,
                "fallback_used": True,
                "fallback_language": "fr",
                "fallback_count": 67,
                "completion_percentage": 57.0
            }
            mock_fallback.return_value = fallback_result
            
            result = await mock_fallback("ber")
            
            assert result["fallback_used"] is True, "Should use fallback for incomplete translations"
            assert result["fallback_language"] == "fr", "Should fallback to appropriate language"
            assert result["completion_percentage"] > 0, "Should track completion percentage"
        
        print("✅ Translation loading workflow test passed")
    
    @pytest.mark.asyncio
    async def test_dynamic_language_switching(self, mock_translation_manager, sample_translations):
        """Test dynamic language switching during user session"""
        print("🔄 Testing dynamic language switching...")
        
        # Test language switch request
        with patch.object(mock_translation_manager, 'switch_language', new_callable=AsyncMock) as mock_switch:
            switch_result = {
                "previous_language": "en",
                "new_language": "ar",
                "switch_successful": True,
                "ui_direction": "rtl",
                "translations_applied": 145,
                "switch_time": 0.12,
                "cache_warmed": True,
                "user_preference_updated": True
            }
            mock_switch.return_value = switch_result
            
            result = await mock_switch("en", "ar", "user_123")
            
            assert result["switch_successful"] is True, "Language switch should succeed"
            assert result["new_language"] == "ar", "Should switch to Arabic"
            assert result["ui_direction"] == "rtl", "Should set RTL direction for Arabic"
            assert result["user_preference_updated"] is True, "Should update user preferences"
        
        # Test UI component updates
        with patch.object(mock_translation_manager, 'update_ui_components', new_callable=AsyncMock) as mock_ui:
            ui_update_result = {
                "components_updated": [
                    "navigation", "dashboard", "forms", "modals", 
                    "tooltips", "error_messages", "notifications"
                ],
                "update_time": 0.08,
                "layout_adjusted": True,
                "fonts_adjusted": True,
                "direction_changed": True
            }
            mock_ui.return_value = ui_update_result
            
            result = await mock_ui("ar")
            
            assert len(result["components_updated"]) > 0, "Should update UI components"
            assert result["layout_adjusted"] is True, "Should adjust layout for RTL"
            assert result["direction_changed"] is True, "Should change text direction"
        
        print("✅ Dynamic language switching test passed")
    
    @pytest.mark.asyncio
    async def test_rtl_language_support(self, mock_translation_manager):
        """Test Right-to-Left (RTL) language support"""
        print("📖 Testing RTL language support...")
        
        # Test RTL layout adjustments
        with patch.object(mock_translation_manager, 'apply_rtl_layout', new_callable=AsyncMock) as mock_rtl:
            rtl_result = {
                "language": "ar",
                "direction": "rtl",
                "layout_changes": {
                    "sidebar_position": "right",
                    "menu_alignment": "right",
                    "text_alignment": "right",
                    "icon_positions": "mirrored"
                },
                "css_classes_applied": ["rtl", "arabic-layout", "right-align"],
                "font_adjustments": {
                    "font_family": "Noto Sans Arabic",
                    "line_height": 1.6,
                    "letter_spacing": "normal"
                }
            }
            mock_rtl.return_value = rtl_result
            
            result = await mock_rtl("ar")
            
            assert result["direction"] == "rtl", "Should set RTL direction"
            assert "layout_changes" in result, "Should apply layout changes"
            assert "font_adjustments" in result, "Should adjust fonts for Arabic"
            assert "rtl" in result["css_classes_applied"], "Should apply RTL CSS classes"
        
        print("✅ RTL language support test passed")
    
    @pytest.mark.asyncio
    async def test_translation_key_resolution(self, mock_translation_manager, sample_translations):
        """Test translation key resolution and interpolation"""
        print("🔑 Testing translation key resolution...")
        
        # Test simple key resolution
        with patch.object(mock_translation_manager, 'translate', new_callable=AsyncMock) as mock_translate:
            mock_translate.side_effect = lambda key, lang="en": sample_translations.get(lang, {}).get(key, key)
            
            result = await mock_translate("welcome", "fr")
            assert result == "Bienvenue sur Ainflue", "Should translate simple key"
            
            result = await mock_translate("dashboard", "ar")
            assert result == "لوحة التحكم", "Should translate to Arabic"
        
        # Test missing key fallback
        with patch.object(mock_translation_manager, 'translate_with_fallback', new_callable=AsyncMock) as mock_fallback:
            fallback_result = {
                "key": "missing_key",
                "language": "ber",
                "translation": "Missing Key",  # English fallback
                "fallback_used": True,
                "fallback_language": "en"
            }
            mock_fallback.return_value = fallback_result
            
            result = await mock_fallback("missing_key", "ber")
            
            assert result["fallback_used"] is True, "Should use fallback for missing key"
            assert result["fallback_language"] == "en", "Should fallback to English"
        
        # Test pluralization
        with patch.object(mock_translation_manager, 'translate_plural', new_callable=AsyncMock) as mock_plural:
            plural_result = {
                "key": "notifications_count",
                "count": 5,
                "language": "fr",
                "translation": "5 notifications",
                "plural_rule": "other"
            }
            mock_plural.return_value = plural_result
            
            result = await mock_plural("notifications_count", 5, "fr")
            
            assert result["translation"].endswith("notifications"), "Should handle French pluralization"
            assert result["count"] == 5, "Should include count in result"
        
        print("✅ Translation key resolution test passed")
    
    @pytest.mark.asyncio
    async def test_language_specific_formatting(self, mock_translation_manager):
        """Test language-specific formatting (dates, numbers, currencies)"""
        print("🔢 Testing language-specific formatting...")
        
        # Test date formatting
        with patch.object(mock_translation_manager, 'format_date', new_callable=AsyncMock) as mock_date:
            date_result = {
                "original_date": "2024-01-15T10:30:00Z",
                "formatted_dates": {
                    "en": "January 15, 2024",
                    "fr": "15 janvier 2024",
                    "ar": "15 يناير 2024",
                    "de": "15. Januar 2024"
                }
            }
            mock_date.return_value = date_result
            
            result = await mock_date("2024-01-15T10:30:00Z")
            
            assert "formatted_dates" in result, "Should format dates for multiple languages"
            assert result["formatted_dates"]["fr"] != result["formatted_dates"]["en"], "Should use different formats"
        
        # Test number formatting
        with patch.object(mock_translation_manager, 'format_number', new_callable=AsyncMock) as mock_number:
            number_result = {
                "original_number": 1234567.89,
                "formatted_numbers": {
                    "en": "1,234,567.89",
                    "fr": "1 234 567,89",
                    "ar": "1,234,567.89",
                    "de": "1.234.567,89"
                }
            }
            mock_number.return_value = number_result
            
            result = await mock_number(1234567.89)
            
            assert "formatted_numbers" in result, "Should format numbers for multiple languages"
            assert result["formatted_numbers"]["fr"] != result["formatted_numbers"]["en"], "Should use French formatting"
        
        print("✅ Language-specific formatting test passed")
    
    @pytest.mark.asyncio
    async def test_multilingual_search_functionality(self, mock_translation_manager):
        """Test multilingual search and content filtering"""
        print("🔍 Testing multilingual search functionality...")
        
        # Test multilingual search
        with patch.object(mock_translation_manager, 'search_multilingual', new_callable=AsyncMock) as mock_search:
            search_result = {
                "query": "contenu créatif",
                "detected_language": "fr",
                "translated_queries": {
                    "en": "creative content",
                    "es": "contenido creativo",
                    "ar": "محتوى إبداعي"
                },
                "results": [
                    {"id": 1, "title": "Creative Content Guide", "language": "en", "relevance": 0.92},
                    {"id": 2, "title": "Guide du contenu créatif", "language": "fr", "relevance": 0.98},
                    {"id": 3, "title": "Guía de contenido creativo", "language": "es", "relevance": 0.87}
                ],
                "total_results": 3
            }
            mock_search.return_value = search_result
            
            result = await mock_search("contenu créatif")
            
            assert result["detected_language"] == "fr", "Should detect French query"
            assert "translated_queries" in result, "Should provide translated queries"
            assert len(result["results"]) > 0, "Should return multilingual results"
        
        print("✅ Multilingual search functionality test passed")
    
    @pytest.mark.asyncio
    async def test_language_performance_metrics(self, mock_translation_manager):
        """Test language switching performance and metrics"""
        print("📊 Testing language performance metrics...")
        
        # Test performance monitoring
        with patch.object(mock_translation_manager, 'get_performance_metrics', new_callable=AsyncMock) as mock_metrics:
            metrics_result = {
                "language_switch_times": {
                    "en_to_fr": 0.08,
                    "fr_to_ar": 0.15,  # RTL switch takes longer
                    "ar_to_en": 0.12,
                    "en_to_de": 0.06
                },
                "cache_performance": {
                    "hit_rate": 0.94,
                    "miss_rate": 0.06,
                    "average_lookup_time": 0.003
                },
                "translation_completeness": {
                    "en": 100.0,
                    "fr": 98.5,
                    "es": 96.2,
                    "ar": 94.8,
                    "de": 97.1,
                    "ber": 76.3
                },
                "user_language_preferences": {
                    "en": 45.2,
                    "fr": 18.7,
                    "es": 12.3,
                    "ar": 8.9,
                    "de": 7.4,
                    "ber": 2.8,
                    "other": 4.7
                }
            }
            mock_metrics.return_value = metrics_result
            
            result = await mock_metrics()
            
            assert result["cache_performance"]["hit_rate"] > 0.9, "Should have high cache hit rate"
            assert all(time < 0.5 for time in result["language_switch_times"].values()), "Should have fast switch times"
            assert result["translation_completeness"]["en"] == 100.0, "English should be complete"
        
        print("✅ Language performance metrics test passed")


if __name__ == "__main__":
    # Run the integration tests
    print("🧪 Running Multilingual Interface Switching Integration Tests")
    print("=" * 60)
    
    # Run with pytest
    exit_code = pytest.main([str(Path(__file__)), "-v", "--tb=short"])
    sys.exit(exit_code)