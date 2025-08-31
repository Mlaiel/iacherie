"""
Test SEO Optimization Engine

This script demonstrates and tests the SEO Optimization Engine functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_content_seo_optimizer():
    """Test the Content SEO Optimizer"""
    print("Testing Content SEO Optimizer...")
    
    try:
        from seo.optimization import ContentSEOOptimizer, OptimizationLevel
        
        optimizer = ContentSEOOptimizer(OptimizationLevel.ADVANCED)
        
        content = """
        Digital marketing has become essential for businesses in 2025. 
        Companies need to understand social media marketing, content marketing, 
        and search engine optimization to succeed online.
        """
        
        keywords = ["digital marketing", "social media", "SEO"]
        
        result = optimizer.optimize_content(
            content=content,
            target_keywords=keywords,
            platform_type="blog",
            language="en"
        )
        
        print(f"✓ Content optimization score: {result.analysis.optimization_score:.1f}")
        print(f"✓ Readability score: {result.analysis.readability_score:.1f}")
        print(f"✓ Improvements made: {len(result.improvements)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Content SEO Optimizer test failed: {str(e)}")
        return False


def test_keyword_generator():
    """Test the Keyword Generator AI"""
    print("\nTesting Keyword Generator AI...")
    
    try:
        from seo.optimization import KeywordGeneratorAI
        
        generator = KeywordGeneratorAI(language="en", region="US")
        
        result = generator.generate_keywords(
            seed_keywords=["marketing", "business"],
            content="Learn about digital marketing strategies for growing your business online.",
            industry="marketing",
            platform="general",
            max_keywords=50
        )
        
        print(f"✓ Total keywords generated: {result.total_keywords}")
        print(f"✓ Primary keywords: {len(result.primary_keywords)}")
        print(f"✓ Long-tail keywords: {len(result.long_tail_keywords)}")
        print(f"✓ Trending keywords: {len(result.trending_keywords)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Keyword Generator test failed: {str(e)}")
        return False


def test_platform_seo_adapter():
    """Test the Platform SEO Adapter"""
    print("\nTesting Platform SEO Adapter...")
    
    try:
        from seo.optimization import PlatformSEOAdapter, Platform
        
        adapter = PlatformSEOAdapter()
        
        content = "Learn the best marketing strategies to grow your business online."
        keywords = ["marketing", "business growth"]
        
        result = adapter.optimize_for_platform(
            content=content,
            platform=Platform.INSTAGRAM,
            keywords=keywords,
            title="Marketing Guide"
        )
        
        print(f"✓ Platform: {result.platform.value}")
        print(f"✓ SEO score: {result.seo_score:.1f}")
        print(f"✓ Hashtags generated: {len(result.hashtags)}")
        print(f"✓ Recommendations: {len(result.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Platform SEO Adapter test failed: {str(e)}")
        return False


def test_meta_optimizer():
    """Test the Meta Optimizer"""
    print("\nTesting Meta Optimizer...")
    
    try:
        from seo.optimization import MetaOptimizer, ContentType
        
        optimizer = MetaOptimizer(language="en", region="US")
        
        content = "Complete guide to digital marketing strategies for small businesses."
        keywords = ["digital marketing", "small business"]
        
        result = optimizer.optimize_meta_data(
            content=content,
            keywords=keywords,
            title="Digital Marketing Guide",
            url="https://example.com/marketing-guide",
            content_type=ContentType.ARTICLE
        )
        
        print(f"✓ SEO score: {result.seo_score:.1f}")
        print(f"✓ Meta tags created: {len(result.meta_tags)}")
        print(f"✓ Open Graph tags: {len(result.open_graph_tags)}")
        print(f"✓ Schema markup generated: {'@type' in result.schema_markup}")
        
        return True
        
    except Exception as e:
        print(f"✗ Meta Optimizer test failed: {str(e)}")
        return False


def test_hashtag_intelligence():
    """Test the Hashtag Intelligence"""
    print("\nTesting Hashtag Intelligence...")
    
    try:
        from seo.optimization import HashtagIntelligence, Platform
        
        intelligence = HashtagIntelligence(language="en", region="US")
        
        content = "Tips for growing your social media presence and engagement."
        keywords = ["social media", "engagement"]
        
        result = intelligence.generate_hashtag_strategy(
            content=content,
            keywords=keywords,
            target_platforms=[Platform.INSTAGRAM, Platform.TWITTER],
            industry="marketing"
        )
        
        print(f"✓ Total hashtags: {result.total_hashtags}")
        print(f"✓ Strategy score: {result.strategy_score:.1f}")
        print(f"✓ Primary hashtags: {len(result.primary_hashtags)}")
        print(f"✓ Trending hashtags: {len(result.trending_hashtags)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Hashtag Intelligence test failed: {str(e)}")
        return False


def test_multilingual_seo():
    """Test the Multilingual SEO"""
    print("\nTesting Multilingual SEO...")
    
    try:
        from seo.optimization import MultilingualSEO, Language, Region, LocalizationLevel
        
        seo = MultilingualSEO()
        
        content = "Learn digital marketing strategies to grow your business."
        target_markets = [
            (Language.FRENCH, Region.FRANCE),
            (Language.GERMAN, Region.GERMANY)
        ]
        
        result = seo.optimize_for_international_markets(
            content=content,
            title="Marketing Guide",
            description="Complete marketing guide for businesses",
            keywords=["marketing", "business"],
            source_language=Language.ENGLISH,
            target_markets=target_markets,
            base_url="https://example.com",
            localization_level=LocalizationLevel.INTERMEDIATE
        )
        
        print(f"✓ Overall score: {result.overall_score:.1f}")
        print(f"✓ Localized versions: {len(result.localized_versions)}")
        print(f"✓ Hreflang tags: {len(result.hreflang_tags)}")
        print(f"✓ Technical recommendations: {len(result.technical_recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Multilingual SEO test failed: {str(e)}")
        return False


def test_trending_analyzer():
    """Test the Trending Analyzer"""
    print("\nTesting Trending Analyzer...")
    
    try:
        from seo.optimization import TrendingAnalyzer, Platform, TimeFrame
        
        analyzer = TrendingAnalyzer(region="US", industry="marketing")
        
        result = analyzer.analyze_trending_content(
            content="AI and automation are transforming digital marketing",
            keywords=["AI", "automation", "marketing"],
            target_platforms=[Platform.INSTAGRAM, Platform.TWITTER],
            time_frame=TimeFrame.DAY
        )
        
        print(f"✓ Recommendation score: {result.recommendation_score:.1f}")
        print(f"✓ Trending topics: {len(result.trending_topics)}")
        print(f"✓ Emerging trends: {len(result.emerging_trends)}")
        print(f"✓ Platform trends: {len(result.platform_trends)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Trending Analyzer test failed: {str(e)}")
        return False


def test_competitor_intelligence():
    """Test the Competitor Intelligence"""
    print("\nTesting Competitor Intelligence...")
    
    try:
        from seo.optimization import CompetitorIntelligence, AnalysisType
        
        intelligence = CompetitorIntelligence(industry="marketing", region="US")
        
        result = intelligence.analyze_competitive_landscape(
            user_domain="example.com",
            competitors=["hubspot.com", "mailchimp.com"],
            user_keywords=["marketing", "email marketing"],
            analysis_types=[AnalysisType.KEYWORD_GAP, AnalysisType.CONTENT_GAP]
        )
        
        print(f"✓ Analysis score: {result.analysis_score:.1f}")
        print(f"✓ Competitor profiles: {len(result.competitor_profiles)}")
        print(f"✓ Keyword gaps: {len(result.keyword_gaps)}")
        print(f"✓ Content gaps: {len(result.content_gaps)}")
        print(f"✓ Strategic recommendations: {len(result.strategic_recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Competitor Intelligence test failed: {str(e)}")
        return False


def test_seo_performance_tracker():
    """Test the SEO Performance Tracker"""
    print("\nTesting SEO Performance Tracker...")
    
    try:
        from seo.optimization import SEOPerformanceTracker, TimeRange
        
        tracker = SEOPerformanceTracker(
            domain="example.com",
            tracking_keywords=["marketing", "business", "SEO"]
        )
        
        result = tracker.generate_performance_report(
            time_range=TimeRange.MONTH,
            include_competitive=True
        )
        
        print(f"✓ Overall score: {result.overall_score:.1f}")
        print(f"✓ Metric categories: {len(result.metrics)}")
        print(f"✓ Keyword performance: {len(result.keyword_performance)}")
        print(f"✓ Page performance: {len(result.page_performance)}")
        print(f"✓ Alerts generated: {len(result.alerts)}")
        print(f"✓ Recommendations: {len(result.recommendations)}")
        
        return True
        
    except Exception as e:
        print(f"✗ SEO Performance Tracker test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all SEO optimization tests"""
    print("=" * 60)
    print("SEO OPTIMIZATION ENGINE - COMPREHENSIVE TESTING")
    print("=" * 60)
    
    tests = [
        test_content_seo_optimizer,
        test_keyword_generator,
        test_platform_seo_adapter,
        test_meta_optimizer,
        test_hashtag_intelligence,
        test_multilingual_seo,
        test_trending_analyzer,
        test_competitor_intelligence,
        test_seo_performance_tracker
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All SEO Optimization Engine components are working correctly!")
        print("\nFeatures successfully implemented:")
        print("✓ Content SEO Optimizer - AI-powered content optimization")
        print("✓ Platform SEO Adapter - Multi-platform optimization")
        print("✓ Keyword Generator AI - Intelligent keyword research")
        print("✓ Meta Optimizer - Complete meta-data optimization")
        print("✓ Hashtag Intelligence - Smart hashtag generation")
        print("✓ Multilingual SEO - International SEO optimization")
        print("✓ Trending Analyzer - Real-time trend analysis")
        print("✓ Competitor Intelligence - Competitive analysis")
        print("✓ SEO Performance Tracker - Comprehensive performance monitoring")
    else:
        print(f"⚠️  {total - passed} components need attention")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()