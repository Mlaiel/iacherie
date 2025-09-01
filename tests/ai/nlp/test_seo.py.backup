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

"""Comprehensive Tests for NLP SEO Module

Industrial-grade tests for AdvancedSEOOptimizer covering keyword research,
content optimization, ranking analysis, and social media SEO with real implementations.

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

from ai.nlp.seo import (
    SEOOptimizer, SEOTracker, SEOAnalysis, KeywordResearch
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestSEOOptimizer:
    """Comprehensive tests for SEOOptimizer"""
    
    @pytest.mark.asyncio
    async def test_optimizer_initialization(self, seo_optimizer):
        """Test SEO optimizer initialization"""
        assert seo_optimizer is not None
        assert hasattr(seo_optimizer, 'config')
        assert hasattr(seo_optimizer, 'keyword_researcher')
        assert hasattr(seo_optimizer, 'content_optimizer')
        assert hasattr(seo_optimizer, 'ranking_analyzer')
        assert hasattr(seo_optimizer, 'social_seo_optimizer')
        
        # Test configuration
        config = seo_optimizer.config
        assert 'target_languages' in config
        assert 'optimization_level' in config
        assert 'platforms' in config

    @pytest.mark.asyncio
    async def test_keyword_research(self, seo_optimizer):
        """Test keyword research functionality"""
        # Test single keyword research
        primary_keyword = "AI content creation"
        
        keyword_analysis = await seo_optimizer.research_keywords(
            primary_keyword=primary_keyword,
            niche="digital marketing",
            target_audience="content creators",
            language=Language.ENGLISH,
            options={
                'competition_analysis': True,
                'trend_analysis': True,
                'related_keywords': True,
                'long_tail_keywords': True
            }
        )
        
        assert keyword_analysis is not None
        assert isinstance(keyword_analysis, dict)
        assert 'primary_keyword' in keyword_analysis
        assert 'search_volume' in keyword_analysis
        assert 'competition_level' in keyword_analysis
        assert 'difficulty_score' in keyword_analysis
        assert 'related_keywords' in keyword_analysis
        assert 'long_tail_keywords' in keyword_analysis
        
        # Verify keyword data
        assert keyword_analysis['primary_keyword'] == primary_keyword
        assert isinstance(keyword_analysis['search_volume'], (int, str))
        assert keyword_analysis['competition_level'] in ['low', 'medium', 'high']
        assert 0 <= keyword_analysis['difficulty_score'] <= 100
        
        # Test related keywords
        related = keyword_analysis['related_keywords']
        assert isinstance(related, list)
        assert len(related) > 0
        
        for keyword in related[:3]:  # Check first 3
            assert 'keyword' in keyword
            assert 'search_volume' in keyword
            assert 'relevance_score' in keyword

    @pytest.mark.asyncio
    async def test_multilingual_keyword_research(self, seo_optimizer):
        """Test multilingual keyword research"""
        keyword = "influencer marketing"
        languages = [Language.ENGLISH, Language.GERMAN, Language.FRENCH]
        
        multilingual_research = await seo_optimizer.research_multilingual_keywords(
            primary_keyword=keyword,
            target_languages=languages,
            options={
                'localization': True,
                'cultural_adaptation': True,
                'regional_trends': True
            }
        )
        
        assert multilingual_research is not None
        assert isinstance(multilingual_research, dict)
        
        for lang in languages:
            lang_code = lang.value[:2]
            assert lang_code in multilingual_research
            
            lang_data = multilingual_research[lang_code]
            assert 'primary_translation' in lang_data
            assert 'local_keywords' in lang_data
            assert 'cultural_variants' in lang_data
            assert 'search_trends' in lang_data

    @pytest.mark.asyncio
    async def test_content_seo_optimization(self, seo_optimizer, sample_social_content):
        """Test content SEO optimization"""
        content = sample_social_content['instagram']['post']
        target_keywords = ["social media marketing", "content strategy", "engagement"]
        
        optimization_result = await seo_optimizer.optimize_content(
            content=content,
            target_keywords=target_keywords,
            platform=Platform.INSTAGRAM,
            content_type=ContentType.POST,
            options={
                'keyword_density': True,
                'readability_optimization': True,
                'semantic_optimization': True,
                'hashtag_optimization': True
            }
        )
        
        assert optimization_result is not None
        assert isinstance(optimization_result, dict)
        assert 'optimized_content' in optimization_result
        assert 'seo_score' in optimization_result
        assert 'keyword_analysis' in optimization_result
        assert 'optimization_suggestions' in optimization_result
        
        # Verify optimization quality
        seo_score = optimization_result['seo_score']
        assert 0 <= seo_score <= 100
        
        optimized = optimization_result['optimized_content']
        assert len(optimized) > 0
        assert optimized != content  # Should be optimized
        
        # Check keyword analysis
        keyword_analysis = optimization_result['keyword_analysis']
        assert 'keyword_density' in keyword_analysis
        assert 'keyword_placement' in keyword_analysis
        assert 'semantic_keywords' in keyword_analysis

    @pytest.mark.asyncio
    async def test_platform_specific_optimization(self, seo_optimizer):
        """Test platform-specific SEO optimization"""
        base_content = "Discover the power of AI in content creation and marketing automation!"
        
        platforms = [
            Platform.INSTAGRAM,
            Platform.TWITTER,
            Platform.LINKEDIN,
            Platform.YOUTUBE,
            Platform.TIKTOK
        ]
        
        platform_optimizations = {}
        
        for platform in platforms:
            optimization = await seo_optimizer.optimize_for_platform(
                content=base_content,
                platform=platform,
                target_keywords=["AI content", "marketing automation"],
                options={
                    'platform_best_practices': True,
                    'character_optimization': True,
                    'hashtag_strategy': True,
                    'engagement_optimization': True
                }
            )
            
            platform_optimizations[platform.value] = optimization
            
            # Verify platform-specific optimization
            assert optimization is not None
            assert 'optimized_content' in optimization
            assert 'platform_score' in optimization
            assert 'platform_specific_suggestions' in optimization
            
            # Platform-specific checks
            if platform == Platform.TWITTER:
                # Twitter should optimize for character limit
                assert len(optimization['optimized_content']) <= 280
            elif platform == Platform.INSTAGRAM:
                # Instagram should include hashtags
                suggestions = optimization['platform_specific_suggestions']
                assert any('hashtag' in str(s).lower() for s in suggestions)

    @pytest.mark.asyncio
    async def test_hashtag_optimization(self, seo_optimizer):
        """Test hashtag optimization for social media SEO"""
        content = "Just launched our new AI-powered content creation tool!"
        niche = "artificial intelligence"
        
        hashtag_optimization = await seo_optimizer.optimize_hashtags(
            content=content,
            niche=niche,
            platform=Platform.INSTAGRAM,
            options={
                'trending_hashtags': True,
                'niche_hashtags': True,
                'engagement_analysis': True,
                'competition_analysis': True,
                'optimal_count': True
            }
        )
        
        assert hashtag_optimization is not None
        assert 'recommended_hashtags' in hashtag_optimization
        assert 'hashtag_strategy' in hashtag_optimization
        assert 'performance_prediction' in hashtag_optimization
        
        recommended = hashtag_optimization['recommended_hashtags']
        assert isinstance(recommended, list)
        assert len(recommended) > 0
        
        for hashtag in recommended:
            assert isinstance(hashtag, dict)
            assert 'tag' in hashtag
            assert 'popularity' in hashtag
            assert 'competition' in hashtag
            assert 'relevance_score' in hashtag
            
            # Hashtag should start with #
            assert hashtag['tag'].startswith('#')

    @pytest.mark.asyncio
    async def test_competitor_analysis(self, seo_optimizer):
        """Test competitor SEO analysis"""
        target_keywords = ["content marketing", "social media strategy"]
        niche = "digital marketing"
        
        competitor_analysis = await seo_optimizer.analyze_competitors(
            target_keywords=target_keywords,
            niche=niche,
            options={
                'top_competitors': 5,
                'content_analysis': True,
                'keyword_gap_analysis': True,
                'opportunity_identification': True
            }
        )
        
        assert competitor_analysis is not None
        assert 'competitors' in competitor_analysis
        assert 'keyword_gaps' in competitor_analysis
        assert 'opportunities' in competitor_analysis
        assert 'competitive_insights' in competitor_analysis
        
        competitors = competitor_analysis['competitors']
        assert isinstance(competitors, list)
        assert len(competitors) > 0
        
        for competitor in competitors:
            assert 'name' in competitor or 'domain' in competitor
            assert 'seo_strength' in competitor
            assert 'content_strategy' in competitor

    @pytest.mark.asyncio
    async def test_content_readability_optimization(self, seo_optimizer):
        """Test content readability optimization"""
        complex_content = """
        The utilization of artificial intelligence methodologies in contemporary 
        content creation paradigms necessitates comprehensive understanding of 
        algorithmic implementations and their subsequent optimization strategies.
        """
        
        readability_optimization = await seo_optimizer.optimize_readability(
            content=complex_content,
            target_audience="general public",
            reading_level="intermediate",
            options={
                'simplify_language': True,
                'improve_structure': True,
                'enhance_clarity': True,
                'maintain_meaning': True
            }
        )
        
        assert readability_optimization is not None
        assert 'optimized_content' in readability_optimization
        assert 'readability_score' in readability_optimization
        assert 'improvements' in readability_optimization
        
        optimized = readability_optimization['optimized_content']
        original_score = readability_optimization.get('original_readability_score', 0)
        new_score = readability_optimization['readability_score']
        
        # Should improve readability
        assert len(optimized) > 0
        assert new_score >= original_score

    @pytest.mark.asyncio
    async def test_local_seo_optimization(self, seo_optimizer):
        """Test local SEO optimization"""
        content = "Best pizza restaurant in downtown area!"
        location_info = {
            'city': 'Berlin',
            'country': 'Germany',
            'region': 'Europe',
            'coordinates': {'lat': 52.5200, 'lon': 13.4050}
        }
        
        local_optimization = await seo_optimizer.optimize_local_seo(
            content=content,
            location_info=location_info,
            business_type="restaurant",
            options={
                'local_keywords': True,
                'geo_targeting': True,
                'local_citations': True,
                'cultural_adaptation': True
            }
        )
        
        assert local_optimization is not None
        assert 'optimized_content' in local_optimization
        assert 'local_keywords' in local_optimization
        assert 'geo_targeting_suggestions' in local_optimization
        
        optimized = local_optimization['optimized_content']
        assert 'Berlin' in optimized or 'berlin' in optimized.lower()

    @pytest.mark.asyncio
    async def test_seo_performance_tracking(self, seo_optimizer):
        """Test SEO performance tracking and analysis"""
        content = "How to create engaging social media content with AI tools"
        keywords = ["AI content creation", "social media tools"]
        
        # Simulate content publication
        publication_data = {
            'content': content,
            'keywords': keywords,
            'platform': Platform.LINKEDIN.value,
            'publication_date': time.time()
        }
        
        # Track initial performance
        tracking_setup = await seo_optimizer.setup_performance_tracking(
            publication_data=publication_data,
            tracking_options={
                'keyword_rankings': True,
                'engagement_metrics': True,
                'click_through_rates': True,
                'conversion_tracking': False  # Skip for tests
            }
        )
        
        assert tracking_setup is not None
        assert 'tracking_id' in tracking_setup
        assert 'metrics_setup' in tracking_setup
        
        # Simulate performance analysis after some time
        performance_analysis = await seo_optimizer.analyze_performance(
            tracking_id=tracking_setup['tracking_id'],
            time_period='7_days',
            options={'detailed_report': True}
        )
        
        assert performance_analysis is not None
        assert 'keyword_performance' in performance_analysis
        assert 'engagement_metrics' in performance_analysis
        assert 'improvement_suggestions' in performance_analysis

    @pytest.mark.asyncio
    async def test_semantic_seo_optimization(self, seo_optimizer):
        """Test semantic SEO optimization"""
        content = "Tips for better content marketing strategy"
        primary_topic = "content marketing"
        
        semantic_optimization = await seo_optimizer.optimize_semantic_seo(
            content=content,
            primary_topic=primary_topic,
            options={
                'topic_clustering': True,
                'entity_optimization': True,
                'context_enhancement': True,
                'semantic_keywords': True
            }
        )
        
        assert semantic_optimization is not None
        assert 'optimized_content' in semantic_optimization
        assert 'semantic_keywords' in semantic_optimization
        assert 'topic_relevance_score' in semantic_optimization
        assert 'entity_analysis' in semantic_optimization
        
        semantic_keywords = semantic_optimization['semantic_keywords']
        assert isinstance(semantic_keywords, list)
        assert len(semantic_keywords) > 0
        
        relevance_score = semantic_optimization['topic_relevance_score']
        assert 0 <= relevance_score <= 100

    @pytest.mark.asyncio
    async def test_content_gap_analysis(self, seo_optimizer):
        """Test content gap analysis"""
        target_keywords = [
            "AI marketing automation",
            "content personalization",
            "social media analytics"
        ]
        
        gap_analysis = await seo_optimizer.analyze_content_gaps(
            target_keywords=target_keywords,
            current_content=[
                "Introduction to AI in marketing",
                "Basic social media tips"
            ],
            competitor_analysis=True,
            options={
                'opportunity_scoring': True,
                'content_suggestions': True,
                'keyword_opportunities': True
            }
        )
        
        assert gap_analysis is not None
        assert 'content_gaps' in gap_analysis
        assert 'opportunities' in gap_analysis
        assert 'content_recommendations' in gap_analysis
        
        gaps = gap_analysis['content_gaps']
        opportunities = gap_analysis['opportunities']
        
        assert isinstance(gaps, list)
        assert isinstance(opportunities, list)
        
        for gap in gaps:
            assert 'topic' in gap
            assert 'priority_score' in gap
            assert 'potential_traffic' in gap

    @pytest.mark.asyncio
    async def test_voice_search_optimization(self, seo_optimizer):
        """Test voice search optimization"""
        content = "What are the best AI tools for content creation?"
        
        voice_optimization = await seo_optimizer.optimize_for_voice_search(
            content=content,
            target_queries=[
                "What are the best AI content tools?",
                "How to use AI for content creation?",
                "AI tools for social media content"
            ],
            options={
                'conversational_optimization': True,
                'featured_snippet_optimization': True,
                'long_tail_optimization': True,
                'local_voice_search': False
            }
        )
        
        assert voice_optimization is not None
        assert 'optimized_content' in voice_optimization
        assert 'voice_search_score' in voice_optimization
        assert 'conversational_keywords' in voice_optimization
        assert 'featured_snippet_potential' in voice_optimization

    @pytest.mark.asyncio
    async def test_mobile_seo_optimization(self, seo_optimizer):
        """Test mobile SEO optimization"""
        content = "Complete guide to mobile-first content strategy"
        
        mobile_optimization = await seo_optimizer.optimize_for_mobile(
            content=content,
            options={
                'mobile_readability': True,
                'mobile_user_experience': True,
                'mobile_search_behavior': True,
                'amp_optimization': False  # Skip AMP for social content
            }
        )
        
        assert mobile_optimization is not None
        assert 'mobile_optimized_content' in mobile_optimization
        assert 'mobile_seo_score' in mobile_optimization
        assert 'mobile_improvements' in mobile_optimization
        
        mobile_score = mobile_optimization['mobile_seo_score']
        assert 0 <= mobile_score <= 100

    @pytest.mark.asyncio
    async def test_international_seo(self, seo_optimizer):
        """Test international SEO optimization"""
        content = "Global digital marketing trends for 2025"
        target_markets = [
            {'country': 'US', 'language': 'en'},
            {'country': 'DE', 'language': 'de'},
            {'country': 'FR', 'language': 'fr'}
        ]
        
        international_optimization = await seo_optimizer.optimize_international_seo(
            content=content,
            target_markets=target_markets,
            options={
                'hreflang_optimization': True,
                'cultural_adaptation': True,
                'local_search_optimization': True,
                'currency_localization': False  # Not applicable for content
            }
        )
        
        assert international_optimization is not None
        assert 'market_optimizations' in international_optimization
        assert 'hreflang_suggestions' in international_optimization
        assert 'cultural_adaptations' in international_optimization
        
        market_opts = international_optimization['market_optimizations']
        assert len(market_opts) == len(target_markets)
        
        for market_code, optimization in market_opts.items():
            assert 'localized_content' in optimization
            assert 'local_keywords' in optimization
            assert 'cultural_notes' in optimization

    @pytest.mark.asyncio
    async def test_batch_seo_optimization(self, seo_optimizer, performance_test_data):
        """Test batch SEO optimization"""
        contents = performance_test_data['small_batch']
        keywords = ["AI content", "digital marketing", "social media"]
        
        start_time = time.time()
        batch_optimization = await seo_optimizer.optimize_batch_content(
            contents=contents,
            target_keywords=keywords,
            platform=Platform.LINKEDIN,
            options={
                'parallel_processing': True,
                'consistent_optimization': True,
                'batch_keyword_distribution': True
            }
        )
        optimization_time = time.time() - start_time
        
        assert batch_optimization is not None
        assert 'optimized_contents' in batch_optimization
        assert 'batch_seo_score' in batch_optimization
        assert 'optimization_summary' in batch_optimization
        
        optimized_contents = batch_optimization['optimized_contents']
        assert len(optimized_contents) == len(contents)
        
        # Check performance
        items_per_second = len(contents) / optimization_time
        assert items_per_second > 1.0  # Should process at reasonable speed

    @pytest.mark.asyncio
    async def test_error_handling(self, seo_optimizer):
        """Test SEO optimizer error handling"""
        # Test empty content
        result = await seo_optimizer.optimize_content(
            content="",
            target_keywords=["test"],
            platform=Platform.INSTAGRAM
        )
        assert result is not None  # Should handle gracefully
        
        # Test invalid keywords
        result = await seo_optimizer.research_keywords(
            primary_keyword="",
            niche="test"
        )
        assert result is not None
        
        # Test unsupported language
        result = await seo_optimizer.optimize_content(
            content="Test content",
            target_keywords=["test"],
            platform=Platform.INSTAGRAM,
            options={'language': 'unsupported_lang'}
        )
        assert result is not None  # Should default gracefully

class TestKeywordResearcher:
    """Test keyword researcher component"""
    
    @pytest.mark.asyncio
    async def test_keyword_researcher_initialization(self):
        """Test keyword researcher initialization"""
        researcher = KeywordResearcher()
        assert researcher is not None
        assert hasattr(researcher, 'research_keywords')

    @pytest.mark.asyncio
    async def test_trend_analysis(self):
        """Test keyword trend analysis"""
        researcher = KeywordResearcher()
        
        trends = await researcher.analyze_keyword_trends(
            keywords=["AI", "machine learning", "automation"],
            time_period="12_months"
        )
        
        assert trends is not None
        assert isinstance(trends, dict)

class TestContentOptimizer:
    """Test content optimizer component"""
    
    @pytest.mark.asyncio
    async def test_content_optimizer_initialization(self):
        """Test content optimizer initialization"""
        optimizer = ContentOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_content')

class TestRankingAnalyzer:
    """Test ranking analyzer component"""
    
    @pytest.mark.asyncio
    async def test_ranking_analyzer_initialization(self):
        """Test ranking analyzer initialization"""
        analyzer = RankingAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_rankings')

class TestSocialSEOOptimizer:
    """Test social SEO optimizer component"""
    
    @pytest.mark.asyncio
    async def test_social_seo_optimizer_initialization(self):
        """Test social SEO optimizer initialization"""
        optimizer = SocialSEOOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_social_seo')

class TestSEOConfig:
    """Test SEO configuration"""
    
    def test_config_creation(self):
        """Test SEO configuration creation"""
        config = SEOConfig(
            target_languages=['en', 'de', 'fr'],
            optimization_level='advanced',
            platforms=[Platform.INSTAGRAM, Platform.LINKEDIN]
        )
        
        assert 'en' in config.target_languages
        assert config.optimization_level == 'advanced'
        assert Platform.INSTAGRAM in config.platforms
