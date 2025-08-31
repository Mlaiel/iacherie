"""
Test Specialized Crawlers
=========================

Basic tests for the new specialized crawlers implementation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the specialized crawlers
from crawlers.ecommerce_crawler import EcommerceCrawler, EcommerceProduct
from crawlers.educational_crawler import EducationalCrawler, EducationalContent
from crawlers.blog_forum_crawler import BlogForumCrawler, ForumPost, BlogPost
from crawlers.news_crawler import NewsCrawler, NewsArticle
from crawlers.podcast_crawler import PodcastCrawler, PodcastEpisode, Podcast
from crawlers.crawler_manager import CrawlerManager


class TestSpecializedCrawlers:
    """Test suite for specialized crawlers."""
    
    def test_ecommerce_crawler_initialization(self):
        """Test e-commerce crawler initialization."""
        crawler = EcommerceCrawler()
        assert crawler is not None
        assert hasattr(crawler, 'platforms')
        assert 'amazon' in crawler.platforms
        assert 'ebay' in crawler.platforms
        assert len(crawler.derivative_keywords) > 0
    
    def test_educational_crawler_initialization(self):
        """Test educational crawler initialization."""
        crawler = EducationalCrawler()
        assert crawler is not None
        assert hasattr(crawler, 'platforms')
        assert 'coursera' in crawler.platforms
        assert 'udemy' in crawler.platforms
        assert len(crawler.subjects) > 0
        assert len(crawler.content_types) > 0
    
    def test_blog_forum_crawler_initialization(self):
        """Test blog/forum crawler initialization."""
        crawler = BlogForumCrawler()
        assert crawler is not None
        assert hasattr(crawler, 'platforms')
        assert 'reddit' in crawler.platforms
        assert 'medium' in crawler.platforms
        assert len(crawler.mention_patterns) > 0
        assert 'positive' in crawler.sentiment_keywords
    
    def test_news_crawler_initialization(self):
        """Test news crawler initialization."""
        crawler = NewsCrawler()
        assert crawler is not None
        assert hasattr(crawler, 'news_sources')
        assert 'bbc' in crawler.news_sources
        assert 'reuters' in crawler.news_sources
        assert len(crawler.categories) > 0
        assert len(crawler.breaking_keywords) > 0
    
    def test_podcast_crawler_initialization(self):
        """Test podcast crawler initialization."""
        crawler = PodcastCrawler()
        assert crawler is not None
        assert hasattr(crawler, 'platforms')
        assert 'spotify' in crawler.platforms
        assert 'apple_podcasts' in crawler.platforms
        assert len(crawler.categories) > 0
        assert len(crawler.audio_indicators) > 0
    
    def test_crawler_manager_integration(self):
        """Test crawler manager integration with new crawlers."""
        manager = CrawlerManager()
        
        # Check that all specialized crawlers are included
        expected_crawlers = [
            'youtube', 'instagram', 'tiktok', 'twitter', 'facebook',
            'generic', 'ecommerce', 'educational', 'blog_forum', 'news', 'podcast'
        ]
        
        for crawler_name in expected_crawlers:
            assert crawler_name in manager.crawlers
            assert manager.crawlers[crawler_name] is not None
    
    def test_data_structures(self):
        """Test data structure validity."""
        # Test EcommerceProduct
        product = EcommerceProduct(
            product_id="test_123",
            title="Test Product",
            description="Test description",
            price=29.99,
            currency="USD",
            seller="Test Seller",
            platform="amazon",
            product_url="https://example.com/product",
            image_urls=["https://example.com/image.jpg"],
            category="electronics",
            brand="TestBrand",
            availability="in_stock",
            rating=4.5,
            review_count=100,
            tags=["electronics", "gadget"],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        assert product.product_id == "test_123"
        assert product.price == 29.99
        
        # Test EducationalContent
        content = EducationalContent(
            content_id="edu_123",
            title="Test Course",
            description="Test course description",
            content_type="course",
            platform="coursera",
            instructor="Test Instructor",
            institution="Test University",
            subject="computer science",
            level="beginner",
            language="en",
            duration="10 hours",
            url="https://example.com/course",
            thumbnail_url="https://example.com/thumb.jpg",
            enrollment_count=1000,
            rating=4.8,
            price=99.00,
            currency="USD",
            tags=["programming", "python"],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        assert content.content_id == "edu_123"
        assert content.subject == "computer science"
        
        # Test NewsArticle
        article = NewsArticle(
            article_id="news_123",
            title="Test News Article",
            content="Full article content",
            summary="Article summary",
            author="Test Reporter",
            news_outlet="test_news",
            category="technology",
            url="https://example.com/article",
            published_at=datetime.now(),
            last_modified=None,
            featured_image="https://example.com/image.jpg",
            tags=["tech", "innovation"],
            mentions=["Company A", "CEO B"],
            location="San Francisco",
            source_credibility="high",
            language="en",
            sentiment="positive",
            engagement_metrics={"views": 1000, "shares": 50}
        )
        assert article.article_id == "news_123"
        assert article.source_credibility == "high"
    
    def test_crawler_helper_methods(self):
        """Test helper methods in crawlers."""
        # Test e-commerce crawler methods
        ecommerce = EcommerceCrawler()
        assert ecommerce.get_version() == "1.0.0"
        
        # Test price parsing
        price, currency = ecommerce._parse_price("$29.99")
        assert price == 29.99
        assert currency == "USD"
        
        # Test derivative detection
        is_derivative = ecommerce._is_derivative_product("Unofficial Fan Shirt", "Unknown Seller")
        assert is_derivative == True
        
        # Test educational crawler methods
        educational = EducationalCrawler()
        category = educational._determine_content_type("Python Programming Course", "Learn Python", "coursera")
        assert category == "course"
        
        subject = educational._determine_subject("Python Programming", "Learn to code")
        assert subject == "programming"
        
        # Test news crawler methods
        news = NewsCrawler()
        credibility = news.assess_source_credibility("reuters.com")
        assert credibility in ["high", "medium", "low", "unknown"]
        
        # Test podcast crawler methods
        podcast = PodcastCrawler()
        episode_num = podcast._extract_episode_number("Episode 123: Test Title")
        assert episode_num == 123
        
        category = podcast._determine_category("Comedy Show", "Funny podcast")
        assert category == "comedy"


async def test_async_methods():
    """Test async methods of crawlers."""
    # Test e-commerce crawler async methods
    ecommerce = EcommerceCrawler()
    stats = await ecommerce.get_stats()
    assert "version" in stats
    assert "platforms_supported" in stats
    
    # Test educational crawler async methods
    educational = EducationalCrawler()
    stats = await educational.get_stats()
    assert "version" in stats
    assert "platforms_supported" in stats
    
    # Test news crawler async methods
    news = NewsCrawler()
    stats = await news.get_stats()
    assert "version" in stats
    assert "sources_supported" in stats
    
    # Test podcast crawler async methods
    podcast = PodcastCrawler()
    stats = await podcast.get_stats()
    assert "version" in stats
    assert "platforms_supported" in stats


def test_crawler_manager_specialized_methods():
    """Test specialized methods in crawler manager."""
    manager = CrawlerManager()
    
    # Check that manager has the new specialized methods
    assert hasattr(manager, 'search_ecommerce_products')
    assert hasattr(manager, 'search_educational_content')
    assert hasattr(manager, 'search_discussions')
    assert hasattr(manager, 'search_news')
    assert hasattr(manager, 'search_podcasts')
    assert hasattr(manager, 'monitor_brand_violations')
    
    # Test manager stats include specialized crawlers
    stats = manager.get_manager_stats()
    assert "specialized_crawlers" in stats
    specialized = stats["specialized_crawlers"]
    expected_specialized = ["ecommerce", "educational", "blog_forum", "news", "podcast"]
    
    for crawler_type in expected_specialized:
        assert crawler_type in specialized


if __name__ == "__main__":
    # Run basic tests
    test_suite = TestSpecializedCrawlers()
    
    print("Running specialized crawler tests...")
    
    try:
        test_suite.test_ecommerce_crawler_initialization()
        print("✓ E-commerce crawler initialization test passed")
        
        test_suite.test_educational_crawler_initialization()
        print("✓ Educational crawler initialization test passed")
        
        test_suite.test_blog_forum_crawler_initialization()
        print("✓ Blog/forum crawler initialization test passed")
        
        test_suite.test_news_crawler_initialization()
        print("✓ News crawler initialization test passed")
        
        test_suite.test_podcast_crawler_initialization()
        print("✓ Podcast crawler initialization test passed")
        
        test_suite.test_crawler_manager_integration()
        print("✓ Crawler manager integration test passed")
        
        test_suite.test_data_structures()
        print("✓ Data structures test passed")
        
        test_suite.test_crawler_helper_methods()
        print("✓ Helper methods test passed")
        
        test_suite.test_crawler_manager_specialized_methods()
        print("✓ Specialized methods test passed")
        
        # Run async tests
        asyncio.run(test_async_methods())
        print("✓ Async methods test passed")
        
        print("\n🎉 All tests passed successfully!")
        print("\nSpecialized crawlers implementation is working correctly:")
        print("- E-commerce crawler for monitoring derivative products")
        print("- Educational crawler for learning platform content")
        print("- Blog/forum crawler for discussions and mentions")
        print("- News crawler for news monitoring")
        print("- Podcast crawler for audio content tracking")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()