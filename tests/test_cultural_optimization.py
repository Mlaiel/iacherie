"""Tests for Cultural Optimization Features - Ainflue Platform

Test suite for cultural keyword adaptation, local trends integration,
regional platform preferences, and enhanced RTL support.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, time

# Import the modules we're testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.i18n.cultural_keyword_adapter import (
    CulturalKeywordAdapter, 
    KeywordAdaptationType,
    CulturalKeywordResult
)
from core.i18n.regional_platform_preferences import (
    RegionalPlatformPreferences,
    Platform,
    Region,
    PlatformRecommendation
)
from core.i18n.rtl_language_support import (
    RTLLanguageSupport,
    RTLLanguage,
    TextDirection
)


class TestCulturalKeywordAdapter:
    """
Test cultural keyword adaptation functionality"""
    
    @pytest.fixture
    def adapter(self):
        return CulturalKeywordAdapter()
    
    @pytest.mark.asyncio
    async def test_adapt_keywords_culturally_arabic(self, adapter):
        """
Test adapting keywords for Arabic culture"""
        keywords = ["business", "technology", "family"]
        
        results = await adapter.adapt_keywords_culturally(
            keywords=keywords,
            source_culture="EN",
            target_culture="AR",
            platform="instagram",
            region="MENA"
        )
        
        assert len(results) == len(keywords)
        assert all(isinstance(result, CulturalKeywordResult) for result in results)
        
        # Check that Arabic translations are included
        business_result = next(r for r in results if r.original_keyword == "business")
        assert any("أعمال" in keyword for keyword in business_result.adapted_keywords)
    
    @pytest.mark.asyncio
    async def test_cultural_sensitivity_check(self, adapter):
        """Test cultural sensitivity checking"""
        # Test with culturally sensitive content
        keywords = ["alcohol", "gambling"]
        
        results = await adapter.adapt_keywords_culturally(
            keywords=keywords,
            source_culture="EN",
            target_culture="AR",
            region="MENA"
        )
        
        # Should have sensitivity flags
        for result in results:
            assert len(result.cultural_sensitivity_flags) > 0
    
    @pytest.mark.asyncio
    async def test_amazigh_keyword_adaptation(self, adapter):
        """Test Amazigh language keyword adaptation"""
        keywords = ["business", "family"]
        
        results = await adapter.adapt_keywords_culturally(
            keywords=keywords,
            source_culture="EN",
            target_culture="AMAZIGH",
            region="NA"
        )
        
        # Check for Amazigh adaptations
        business_result = next(r for r in results if r.original_keyword == "business")
        assert any("tamdint" in keyword for keyword in business_result.adapted_keywords)
    
    @pytest.mark.asyncio
    async def test_regional_preferences_mena(self, adapter):
        """Test getting regional preferences for MENA"""
        preferences = await adapter.get_regional_keyword_preferences("MENA")
        
        assert preferences.region == "MENA"
        assert "أعمال" in preferences.preferred_terms.get("business", [])
        assert "alcohol" in preferences.avoided_terms
        assert preferences.formal_vs_informal == "formal"
    
    @pytest.mark.asyncio
    async def test_health_check(self, adapter):
        """Test adapter health check"""
        health = await adapter.health_check()
        assert isinstance(health, bool)


class TestRegionalPlatformPreferences:
    """
Test regional platform preferences functionality"""
    
    @pytest.fixture
    def preferences_engine(self):
        return RegionalPlatformPreferences()
    
    @pytest.mark.asyncio
    async def test_get_platform_recommendations_mena(self, preferences_engine):
        """
Test getting platform recommendations for MENA region"""
        recommendations = await preferences_engine.get_platform_recommendations(
            region="MENA",
            content_type="lifestyle",
            target_audience={"age": "25-34", "gender": "mixed"},
            budget=1000.0
        )
        
        assert isinstance(recommendations, PlatformRecommendation)
        assert len(recommendations.recommended_platforms) > 0
        assert Platform.INSTAGRAM in recommendations.recommended_platforms
        assert "MENA" in str(recommendations.content_strategy)
    
    @pytest.mark.asyncio
    async def test_platform_recommendations_na_region(self, preferences_engine):
        """Test platform recommendations for North Africa"""
        recommendations = await preferences_engine.get_platform_recommendations(
            region="NA",
            content_type="cultural_heritage",
            target_audience={"age": "18-35"}
        )
        
        # Should include Facebook for NA region
        assert Platform.FACEBOOK in recommendations.recommended_platforms
        
        # Should have trilingual hashtag strategy
        instagram_hashtags = recommendations.hashtag_recommendations.get(Platform.INSTAGRAM, [])
        assert any("#Amazigh" in tag for tag in instagram_hashtags)
    
    @pytest.mark.asyncio
    async def test_gcc_luxury_focus(self, preferences_engine):
        """Test GCC region luxury content focus"""
        recommendations = await preferences_engine.get_platform_recommendations(
            region="GCC",
            content_type="luxury_lifestyle",
            target_audience={"age": "25-44", "income": "high"}
        )
        
        # Should prioritize Instagram and LinkedIn for GCC
        assert Platform.INSTAGRAM in recommendations.recommended_platforms
        assert Platform.LINKEDIN in recommendations.recommended_platforms
        
        # Should have luxury-focused content strategy
        instagram_strategy = recommendations.content_strategy.get(Platform.INSTAGRAM, "")
        assert "luxury" in instagram_strategy.lower()
    
    @pytest.mark.asyncio
    async def test_regional_analytics(self, preferences_engine):
        """Test getting regional analytics"""
        analytics = await preferences_engine.get_regional_analytics("MENA")
        
        assert analytics["region"] == "MENA"
        assert "platform_rankings" in analytics
        assert "language_preferences" in analytics
        assert "cultural_considerations" in analytics
    
    @pytest.mark.asyncio
    async def test_health_check(self, preferences_engine):
        """Test preferences engine health check"""
        health = await preferences_engine.health_check()
        assert isinstance(health, bool)


class TestEnhancedRTLSupport:
    """
Test enhanced RTL language support"""
    
    @pytest.fixture
    def rtl_support(self):
        return RTLLanguageSupport()
    
    @pytest.mark.asyncio
    async def test_arabic_rtl_detection(self, rtl_support):
        """
Test Arabic RTL text detection"""
        arabic_text = "مرحبا بكم في منصة عين فلو"
        
        direction = await rtl_support.detect_text_direction(arabic_text)
        assert direction == TextDirection.RTL
    
    @pytest.mark.asyncio
    async def test_hebrew_rtl_detection(self, rtl_support):
        """Test Hebrew RTL text detection"""
        hebrew_text = "שלום וברכה לכולם"
        
        direction = await rtl_support.detect_text_direction(hebrew_text)
        assert direction == TextDirection.RTL
    
    @pytest.mark.asyncio
    async def test_amazigh_language_support(self, rtl_support):
        """Test Amazigh/Berber language support"""
        # Test that Amazigh languages are supported
        assert RTLLanguage.AMAZIGH in [lang for lang in RTLLanguage]
        assert RTLLanguage.TAMAZIGHT in [lang for lang in RTLLanguage]
        assert RTLLanguage.KABYLE in [lang for lang in RTLLanguage]
        
        # Test language configurations exist
        assert "ber" in rtl_support.rtl_languages
        assert "tzm" in rtl_support.rtl_languages
        assert "kab" in rtl_support.rtl_languages
    
    @pytest.mark.asyncio
    async def test_tifinagh_script_detection(self, rtl_support):
        """Test Tifinagh script detection for Amazigh"""
        # Tifinagh characters (if available)
        tifinagh_text = "ⵜⴰⵎⴰⵣⵉⵖⵜ"  # Tamazight in Tifinagh
        
        # Should detect as RTL
        direction = await rtl_support.detect_text_direction(tifinagh_text)
        assert direction in [TextDirection.RTL, TextDirection.MIXED]  # May be mixed if fallback
    
    @pytest.mark.asyncio
    async def test_mixed_content_handling(self, rtl_support):
        """Test mixed RTL/LTR content handling"""
        mixed_text = "Welcome مرحبا 123 שלום"
        
        direction = await rtl_support.detect_text_direction(mixed_text)
        assert direction == TextDirection.MIXED
    
    @pytest.mark.asyncio
    async def test_ui_layout_adaptation_arabic(self, rtl_support):
        """Test UI layout adaptation for Arabic"""
        layout_config = {
            "direction": "ltr",
            "text_align": "left",
            "margin": "10px"
        }
        
        adapted_layout = await rtl_support.adapt_ui_layout(
            layout_config=layout_config,
            target_language="ar"
        )
        
        assert adapted_layout["direction"] == "rtl"
        assert adapted_layout["text_align"] == "right"
        assert "rtl-layout" in adapted_layout.get("css_classes", [])
    
    @pytest.mark.asyncio
    async def test_ui_layout_adaptation_amazigh(self, rtl_support):
        """Test UI layout adaptation for Amazigh"""
        layout_config = {
            "direction": "ltr",
            "text_align": "left"
        }
        
        adapted_layout = await rtl_support.adapt_ui_layout(
            layout_config=layout_config,
            target_language="ber"
        )
        
        assert adapted_layout["direction"] == "rtl"
        assert "rtl-ber" in adapted_layout.get("css_classes", [])
    
    @pytest.mark.asyncio
    async def test_health_check(self, rtl_support):
        """Test RTL support health check"""
        health = await rtl_support.health_check()
        assert isinstance(health, bool)


class TestIntegrationScenarios:
    """
Test integration scenarios combining multiple features"""
    
    @pytest.fixture
    def cultural_adapter(self):
        return CulturalKeywordAdapter()
    
    @pytest.fixture
    def platform_preferences(self):
        return RegionalPlatformPreferences()
    
    @pytest.fixture
    def rtl_support(self):
        return RTLLanguageSupport()
    
    @pytest.mark.asyncio
    async def test_complete_mena_optimization(self, cultural_adapter, platform_preferences, rtl_support):
        """
Test complete optimization workflow for MENA region"""
        
        # 1. Adapt keywords culturally
        keywords = ["business", "technology", "lifestyle"]
        keyword_results = await cultural_adapter.adapt_keywords_culturally(
            keywords=keywords,
            source_culture="EN",
            target_culture="AR",
            platform="instagram",
            region="MENA"
        )
        
        # 2. Get platform recommendations
        platform_recs = await platform_preferences.get_platform_recommendations(
            region="MENA",
            content_type="business",
            target_audience={"age": "25-35", "language": "arabic"}
        )
        
        # 3. Check RTL support for Arabic content
        arabic_text = "أعمال وتكنولوجيا"
        rtl_direction = await rtl_support.detect_text_direction(arabic_text)
        
        # Verify integration works
        assert len(keyword_results) > 0
        assert len(platform_recs.recommended_platforms) > 0
        assert rtl_direction == TextDirection.RTL
        
        # Verify cultural consistency
        assert any("أعمال" in result.adapted_keywords[0] for result in keyword_results)
        assert Platform.INSTAGRAM in platform_recs.recommended_platforms
    
    @pytest.mark.asyncio
    async def test_amazigh_cultural_workflow(self, cultural_adapter, platform_preferences, rtl_support):
        """Test complete workflow for Amazigh culture"""
        
        # Test Amazigh keyword adaptation
        keywords = ["family", "tradition"]
        amazigh_keywords = await cultural_adapter.adapt_keywords_culturally(
            keywords=keywords,
            source_culture="EN",
            target_culture="AMAZIGH",
            region="NA"
        )
        
        # Test NA region platform preferences
        na_platforms = await platform_preferences.get_platform_recommendations(
            region="NA",
            content_type="cultural_heritage",
            target_audience={"culture": "amazigh"}
        )
        
        # Test Amazigh RTL support
        assert "ber" in rtl_support.rtl_languages
        
        # Verify Amazigh-specific adaptations
        family_result = next(r for r in amazigh_keywords if r.original_keyword == "family")
        assert any("tawacult" in keyword for keyword in family_result.adapted_keywords)


if __name__ == "__main__":
    # Run tests manually for basic validation
    import asyncio
    
    async def run_basic_tests():
        """Run basic tests to validate functionality"""
        print("Running Cultural Optimization Tests...")
        
        # Test Cultural Keyword Adapter
        print("\n1. Testing Cultural Keyword Adapter...")
        adapter = CulturalKeywordAdapter()
        results = await adapter.adapt_keywords_culturally(
            ["business"], "EN", "AR", "instagram", "MENA"
        )
        print(f"✓ Arabic keywords: {results[0].adapted_keywords[:3]}")
        
        # Test Regional Platform Preferences
        print("\n2. Testing Regional Platform Preferences...")
        prefs = RegionalPlatformPreferences()
        recommendations = await prefs.get_platform_recommendations("MENA", "lifestyle", {})
        print(f"✓ MENA platforms: {[p.value for p in recommendations.recommended_platforms[:2]]}")
        
        # Test Enhanced RTL Support
        print("\n3. Testing Enhanced RTL Support...")
        rtl = RTLLanguageSupport()
        direction = await rtl.detect_text_direction("مرحبا بكم")
        print(f"✓ Arabic text direction: {direction.value}")
        
        # Test Amazigh support
        amazigh_langs = [lang for lang in RTLLanguage if "AMAZIGH" in lang.name or lang.name in ["TAMAZIGHT", "KABYLE"]]
        print(f"✓ Amazigh languages supported: {len(amazigh_langs)}")
        
        print("\n✅ All basic tests passed!")
    
    # Run the tests
    asyncio.run(run_basic_tests())