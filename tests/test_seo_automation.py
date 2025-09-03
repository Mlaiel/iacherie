"""Test SEO Automation Service - Comprehensive Test Suite

Tests for the automated SEO service components including AMP optimization,
Core Web Vitals optimization, sitemap generation, and orchestration service.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

# Import the modules we're testing
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from seo.optimization.amp_optimizer import AMPOptimizer, ContentType as AMPContentType, AMPValidationResult
from seo.optimization.core_web_vitals_optimizer import CoreWebVitalsOptimizer, OptimizationLevel, WebVitalMetric
from seo.optimization.sitemap_generator import SitemapGenerator, ChangeFrequency, Priority
from seo.automation_service import (
    SEOAutomationService, ContentFormat, OptimizationGoal, 
    ContentData, SEOOptimizationRequest
)


class TestAMPOptimizer:
    """Test suite for AMP Optimizer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.amp_optimizer = AMPOptimizer()
        
    def test_amp_optimizer_initialization(self):
        """Test AMP optimizer initializes correctly"""
        assert self.amp_optimizer.amp_version == "2.0"
        assert "amp-runtime" in self.amp_optimizer.required_scripts
        assert self.amp_optimizer.max_amp_css_size == 75000
        
    def test_convert_to_amp_html(self):
        """Test HTML to AMP conversion"""
        html_content = """
        <img src="test.jpg" width="600" height="400" alt="Test image">
        <video src="test.mp4" controls></video>
        <script>console.log('test');</script>
        """
        
        amp_content = self.amp_optimizer._convert_to_amp_html(html_content)
        
        # Check that img tags are converted to amp-img
        assert '<amp-img' in amp_content
        assert 'layout="responsive"' in amp_content
        
        # Check that video tags are converted to amp-video
        assert '<amp-video' in amp_content
        
        # Check that script tags are removed
        assert '<script>' not in amp_content
        
    def test_generate_amp_page(self):
        """Test complete AMP page generation"""
        result = self.amp_optimizer.generate_amp_page(
            content="<p>Test content with <img src='test.jpg'> image</p>",
            title="Test Article",
            meta_description="Test description",
            canonical_url="https://example.com/test",
            content_type=AMPContentType.ARTICLE,
            author="Test Author",
            published_date="2025-01-01T00:00:00Z",
            image_url="https://example.com/featured.jpg"
        )
        
        # Validate structure
        assert result.amp_html is not None
        assert result.amp_css is not None
        assert result.structured_data is not None
        assert result.validation_result is not None
        
        # Check AMP HTML contains required elements
        assert '⚡' in result.amp_html or 'amp' in result.amp_html
        assert 'charset="utf-8"' in result.amp_html
        assert 'viewport' in result.amp_html
        assert 'rel="canonical"' in result.amp_html
        
    def test_amp_validation(self):
        """Test AMP validation functionality"""
        # Valid AMP HTML
        valid_amp_html = """<!doctype html>
        <html ⚡ lang="en">
        <head>
            <meta charset="utf-8">
            <title>Test</title>
            <link rel="canonical" href="https://example.com">
            <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
        </head>
        <body>Content</body>
        </html>"""
        
        validation_result = self.amp_optimizer._validate_amp_html(valid_amp_html)
        
        assert isinstance(validation_result, AMPValidationResult)
        assert validation_result.performance_score >= 0
        
    def test_mobile_optimization(self):
        """Test mobile-specific optimizations"""
        basic_result = self.amp_optimizer.generate_amp_page(
            content="<p>Test content</p>",
            title="Test",
            meta_description="Test description",
            canonical_url="https://example.com/test",
            content_type=AMPContentType.ARTICLE
        )
        
        optimized_result = self.amp_optimizer.optimize_amp_for_mobile(basic_result)
        
        # Mobile optimization should improve the usability score
        assert optimized_result.mobile_usability_score >= basic_result.mobile_usability_score
        assert optimized_result.performance_metrics["mobile_optimization_applied"] == 1.0


class TestCoreWebVitalsOptimizer:
    """Test suite for Core Web Vitals Optimizer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.cwv_optimizer = CoreWebVitalsOptimizer()
        
    def test_cwv_optimizer_initialization(self):
        """Test Core Web Vitals optimizer initializes correctly"""
        assert WebVitalMetric.LARGEST_CONTENTFUL_PAINT in self.cwv_optimizer.web_vitals_thresholds
        assert len(self.cwv_optimizer.optimization_priorities) > 0
        
    def test_analyze_current_performance(self):
        """Test performance analysis"""
        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <img src="large-image.jpg" width="1200" height="800">
            <script src="heavy-script.js"></script>
            <p>Content here</p>
        </body>
        </html>
        """
        
        scores = self.cwv_optimizer._analyze_current_performance(html_content, "")
        
        # Should return scores for all metrics
        metric_types = [score.metric for score in scores]
        assert WebVitalMetric.LARGEST_CONTENTFUL_PAINT in metric_types
        assert WebVitalMetric.FIRST_INPUT_DELAY in metric_types
        assert WebVitalMetric.CUMULATIVE_LAYOUT_SHIFT in metric_types
        
    def test_optimize_core_web_vitals(self):
        """Test complete Core Web Vitals optimization"""
        html_content = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <img src="test.jpg">
            <script src="test.js"></script>
            <p>Test content</p>
        </body>
        </html>
        """
        
        result = self.cwv_optimizer.optimize_core_web_vitals(
            html_content=html_content,
            optimization_level=OptimizationLevel.INTERMEDIATE
        )
        
        # Validate result structure
        assert result.web_vital_scores is not None
        assert result.overall_score >= 0
        assert result.optimized_html is not None
        assert len(result.performance_recommendations) > 0
        
    def test_image_optimization(self):
        """Test image optimization for LCP"""
        html_with_images = '<img src="test.jpg"><img src="test2.jpg">'
        
        optimization = self.cwv_optimizer._optimize_images(
            html_with_images, OptimizationLevel.INTERMEDIATE
        )
        
        if optimization:
            # Should add loading attributes and dimensions
            assert 'loading=' in optimization.optimized_value
            assert 'width=' in optimization.optimized_value
            assert optimization.improvement_estimate > 0
            
    def test_javascript_optimization(self):
        """Test JavaScript optimization for FID"""
        html_with_js = '<script src="test.js"></script><script>console.log("test");</script>'
        
        optimization = self.cwv_optimizer._optimize_javascript(
            html_with_js, OptimizationLevel.INTERMEDIATE
        )
        
        if optimization:
            # Should add defer attribute
            assert 'defer' in optimization.optimized_value
            assert optimization.improvement_estimate > 0


class TestSitemapGenerator:
    """Test suite for Sitemap Generator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.base_url = "https://example.com"
        self.sitemap_generator = SitemapGenerator(self.base_url)
        
    def test_sitemap_generator_initialization(self):
        """Test sitemap generator initializes correctly"""
        assert self.sitemap_generator.base_url == self.base_url
        assert self.sitemap_generator.max_urls_per_sitemap == 50000
        assert 'sitemap' in self.sitemap_generator.namespaces
        
    def test_generate_pages_sitemap(self):
        """Test basic pages sitemap generation"""
        from seo.optimization.sitemap_generator import SitemapEntry
        
        entries = [
            SitemapEntry(
                url="https://example.com/page1",
                last_modified=datetime.now(timezone.utc),
                change_frequency=ChangeFrequency.WEEKLY,
                priority=Priority.HIGH,
                images=[],
                videos=[],
                alternate_urls={"fr": "https://example.com/fr/page1"},
                mobile_url=None
            )
        ]
        
        sitemap_xml = self.sitemap_generator._generate_pages_sitemap(entries)
        
        # Validate XML structure
        assert '<?xml version="1.0"' in sitemap_xml
        assert '<urlset' in sitemap_xml
        assert '<loc>https://example.com/page1</loc>' in sitemap_xml
        assert '<changefreq>weekly</changefreq>' in sitemap_xml
        assert 'hreflang="fr"' in sitemap_xml
        
    def test_comprehensive_sitemap_generation(self):
        """Test complete sitemap generation with all features"""
        content_data = [
            {
                "url": "/article1",
                "type": "article",
                "title": "Test Article",
                "description": "Test description",
                "last_modified": "2025-01-01T00:00:00Z",
                "images": [{"url": "/image1.jpg", "alt": "Test image"}],
                "videos": [{"url": "/video1.mp4", "title": "Test video"}]
            },
            {
                "url": "/product1", 
                "type": "product",
                "title": "Test Product",
                "description": "Product description",
                "last_modified": "2025-01-01T00:00:00Z"
            }
        ]
        
        result = self.sitemap_generator.generate_comprehensive_sitemap(
            content_data=content_data,
            languages=["en", "fr", "de"],
            include_images=True,
            include_videos=True,
            include_mobile=True
        )
        
        # Validate result
        assert result.sitemap_xml is not None
        assert result.sitemap_index_xml is not None
        assert result.stats.total_urls > 0
        assert result.stats.languages_count == 3
        assert len(result.validation_errors) == 0
        
    def test_multilingual_url_generation(self):
        """Test multilingual URL generation"""
        base_url = "https://example.com/article"
        
        fr_url = self.sitemap_generator._generate_language_url(base_url, "fr", {})
        de_url = self.sitemap_generator._generate_language_url(base_url, "de", {})
        
        assert "/fr/" in fr_url
        assert "/de/" in de_url
        assert fr_url != de_url
        
    def test_robots_txt_generation(self):
        """Test robots.txt generation with sitemap references"""
        sitemap_urls = ["/sitemap.xml", "/sitemap-images.xml"]
        
        robots_content = self.sitemap_generator.generate_robots_txt(sitemap_urls)
        
        assert "User-agent: *" in robots_content
        assert "Sitemap: https://example.com/sitemap.xml" in robots_content
        assert "Sitemap: https://example.com/sitemap-images.xml" in robots_content


class TestSEOAutomationService:
    """Test suite for SEO Automation Service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.base_url = "https://example.com"
        self.seo_service = SEOAutomationService(self.base_url)
        
        # Sample content data
        self.sample_content = ContentData(
            content_id="test123",
            title="Test Article Title",
            description="Test article description for SEO optimization",
            content_body="<p>This is test content for SEO optimization testing.</p>",
            content_format=ContentFormat.BLOG,
            author="Test Author",
            published_date=datetime.now(timezone.utc),
            tags=["test", "seo", "optimization"],
            language="en",
            target_keywords=["seo testing", "optimization", "content marketing"],
            canonical_url="https://example.com/test-article",
            images=[{"url": "https://example.com/test.jpg", "alt": "Test image"}],
            videos=[],
            metadata={"category": "technology"}
        )
        
    def test_seo_service_initialization(self):
        """Test SEO automation service initializes correctly"""
        assert self.seo_service.base_url == self.base_url
        assert self.seo_service.meta_optimizer is not None
        assert self.seo_service.amp_optimizer is not None
        assert self.seo_service.core_web_vitals_optimizer is not None
        assert self.seo_service.sitemap_generator is not None
        
    @pytest.mark.asyncio
    async def test_comprehensive_seo_optimization(self):
        """Test complete SEO optimization workflow"""
        request = SEOOptimizationRequest(
            content_data=self.sample_content,
            target_languages=["en", "fr"],
            target_regions=["US", "FR"],
            optimization_goals=[OptimizationGoal.SEARCH_VISIBILITY, OptimizationGoal.MOBILE_PERFORMANCE],
            enable_amp=True,
            enable_multilingual=True,
            enable_core_web_vitals=True,
            enable_sitemap_update=True,
            optimization_level="intermediate"
        )
        
        result = await self.seo_service.optimize_content_seo(request)
        
        # Validate comprehensive result
        assert result.content_id == self.sample_content.content_id
        assert result.optimization_timestamp is not None
        assert result.overall_seo_score >= 0
        assert len(result.recommendations) > 0
        assert result.technical_implementation is not None
        
        # Check individual optimization components
        assert result.optimized_meta_tags is not None
        assert result.meta_seo_score >= 0
        
        # Check performance optimization was applied
        assert result.web_vitals_score >= 0
        assert isinstance(result.performance_improvements, dict)
        
    @pytest.mark.asyncio
    async def test_meta_tags_optimization(self):
        """Test meta tags optimization component"""
        request = SEOOptimizationRequest(
            content_data=self.sample_content,
            target_languages=["en"],
            target_regions=["US"],
            optimization_goals=[OptimizationGoal.SEARCH_VISIBILITY]
        )
        
        result = await self.seo_service.optimize_content_seo(request)
        
        # Meta tags should be optimized
        assert result.optimized_meta_tags is not None
        assert '<title>' in result.optimized_meta_tags
        assert '<meta name="description"' in result.optimized_meta_tags
        assert result.meta_seo_score > 0
        
    @pytest.mark.asyncio
    async def test_amp_optimization(self):
        """Test AMP optimization for mobile content"""
        # Blog content should generate AMP
        blog_content = ContentData(
            content_id="blog123",
            title="Blog Post",
            description="Blog description",
            content_body="<p>Blog content</p>",
            content_format=ContentFormat.BLOG,
            author="Author",
            published_date=datetime.now(timezone.utc),
            tags=["blog"],
            language="en",
            target_keywords=["blog", "content"],
            canonical_url="https://example.com/blog",
            images=[],
            videos=[],
            metadata={}
        )
        
        request = SEOOptimizationRequest(
            content_data=blog_content,
            target_languages=["en"],
            target_regions=["US"],
            optimization_goals=[OptimizationGoal.MOBILE_PERFORMANCE],
            enable_amp=True
        )
        
        result = await self.seo_service.optimize_content_seo(request)
        
        # AMP should be generated for blog content
        assert result.amp_html is not None
        assert result.mobile_usability_score >= 0
        
    @pytest.mark.asyncio
    async def test_batch_optimization(self):
        """Test batch optimization of multiple content pieces"""
        requests = []
        
        for i in range(3):
            content = ContentData(
                content_id=f"test{i}",
                title=f"Test Article {i}",
                description=f"Description {i}",
                content_body=f"<p>Content {i}</p>",
                content_format=ContentFormat.BLOG,
                author="Test Author",
                published_date=datetime.now(timezone.utc),
                tags=["test"],
                language="en",
                target_keywords=["test", "content"],
                canonical_url=f"https://example.com/test{i}",
                images=[],
                videos=[],
                metadata={}
            )
            
            request = SEOOptimizationRequest(
                content_data=content,
                target_languages=["en"],
                target_regions=["US"],
                optimization_goals=[OptimizationGoal.SEARCH_VISIBILITY],
                optimization_level="basic"
            )
            requests.append(request)
        
        results = await self.seo_service.batch_optimize_content(requests)
        
        # Should process all requests
        assert len(results) == 3
        
        # Each result should be valid
        for result in results:
            assert result.content_id.startswith("test")
            assert result.overall_seo_score >= 0
            
    def test_content_format_mapping(self):
        """Test content format to optimization type mapping"""
        # Test various content formats
        video_format = self.seo_service._map_content_format_to_sitemap_type(ContentFormat.VIDEO)
        assert video_format == "video"
        
        blog_format = self.seo_service._map_content_format_to_sitemap_type(ContentFormat.BLOG)
        assert blog_format == "article"
        
        photo_format = self.seo_service._map_content_format_to_sitemap_type(ContentFormat.PHOTO)
        assert photo_format == "image"
        
    def test_optimization_statistics(self):
        """Test optimization statistics tracking"""
        stats = self.seo_service.get_optimization_statistics()
        
        assert "total_optimizations" in stats
        assert "successful_optimizations" in stats
        assert "service_status" in stats
        assert "supported_content_formats" in stats
        assert "available_features" in stats
        
        # Check feature availability
        features = stats["available_features"]
        assert features["meta_optimization"] is True
        assert features["amp_generation"] is True
        assert features["core_web_vitals"] is True
        assert features["multilingual_seo"] is True
        assert features["sitemap_generation"] is True
        
    @pytest.mark.asyncio
    async def test_seo_validation(self):
        """Test SEO implementation validation"""
        test_url = "https://example.com/test-page"
        
        validation_result = await self.seo_service.validate_seo_implementation(test_url)
        
        assert validation_result["url"] == test_url
        assert "validation_timestamp" in validation_result
        assert "meta_tags" in validation_result
        assert "performance" in validation_result
        assert "overall_compliance" in validation_result


# Integration tests
class TestSEOIntegration:
    """Integration tests for SEO automation workflow"""
    
    @pytest.mark.asyncio
    async def test_full_content_creator_workflow(self):
        """Test complete workflow for content creator"""
        # Simulate content creator uploading content
        content_creator_data = ContentData(
            content_id="creator_video_001",
            title="How to Create Amazing Content - Complete Guide",
            description="Learn professional content creation techniques used by top creators on social media platforms.",
            content_body="""
            <h2>Introduction to Content Creation</h2>
            <p>Content creation is an art that combines creativity with strategic thinking...</p>
            <img src="https://example.com/content-creation.jpg" alt="Content creation setup">
            <h3>Key Principles</h3>
            <p>Understanding your audience is crucial for successful content creation...</p>
            <video src="https://example.com/tutorial.mp4" poster="https://example.com/poster.jpg"></video>
            """,
            content_format=ContentFormat.VIDEO,
            author="Professional Creator",
            published_date=datetime.now(timezone.utc),
            tags=["content creation", "tutorial", "social media", "creator tips"],
            language="en",
            target_keywords=["content creation", "social media marketing", "creator economy", "video production"],
            canonical_url="https://ainflue.com/tutorials/content-creation-guide",
            images=[
                {"url": "https://example.com/content-creation.jpg", "alt": "Content creation setup"},
                {"url": "https://example.com/poster.jpg", "alt": "Video thumbnail"}
            ],
            videos=[
                {"url": "https://example.com/tutorial.mp4", "title": "Content Creation Tutorial"}
            ],
            metadata={
                "duration": "PT15M30S",
                "category": "education",
                "difficulty": "beginner",
                "platform_focus": ["youtube", "tiktok", "instagram"]
            }
        )
        
        # Configure SEO optimization for global reach
        seo_request = SEOOptimizationRequest(
            content_data=content_creator_data,
            target_languages=["en", "fr", "de", "es"],
            target_regions=["US", "FR", "DE", "ES"],
            optimization_goals=[
                OptimizationGoal.SEARCH_VISIBILITY,
                OptimizationGoal.MOBILE_PERFORMANCE,
                OptimizationGoal.INTERNATIONAL_REACH,
                OptimizationGoal.CONTENT_DISCOVERY,
                OptimizationGoal.USER_ENGAGEMENT
            ],
            enable_amp=True,
            enable_multilingual=True,
            enable_core_web_vitals=True,
            enable_sitemap_update=True,
            optimization_level="aggressive"
        )
        
        # Initialize SEO automation service
        seo_service = SEOAutomationService("https://ainflue.com")
        
        # Perform comprehensive SEO optimization
        optimization_result = await seo_service.optimize_content_seo(seo_request)
        
        # Validate complete optimization results
        assert optimization_result.content_id == "creator_video_001"
        assert optimization_result.overall_seo_score >= 70  # High quality content should score well
        
        # Check meta optimization
        assert optimization_result.optimized_meta_tags is not None
        assert "content creation" in optimization_result.optimized_meta_tags.lower()
        assert optimization_result.meta_seo_score >= 60
        
        # Check mobile optimization (AMP for video content might not be generated)
        assert optimization_result.mobile_usability_score >= 60
        
        # Check performance optimization
        assert optimization_result.web_vitals_score >= 60
        assert len(optimization_result.performance_improvements) > 0
        
        # Check multilingual support
        assert len(optimization_result.localized_versions) >= 3  # Should have fr, de, es
        assert optimization_result.hreflang_tags is not None
        
        # Check sitemap update
        assert optimization_result.sitemap_updated is True
        assert len(optimization_result.sitemap_urls) > 0
        
        # Check technical implementation
        assert "meta_tags" in optimization_result.technical_implementation
        assert "core_web_vitals" in optimization_result.technical_implementation
        assert "multilingual" in optimization_result.technical_implementation
        assert "sitemap" in optimization_result.technical_implementation
        
        # Validate recommendations are actionable
        assert len(optimization_result.recommendations) > 0
        
        # The recommendations should be relevant to the optimization goals
        recommendation_text = " ".join(optimization_result.recommendations).lower()
        assert any(goal.value.replace("_", " ") in recommendation_text for goal in seo_request.optimization_goals)
        
        print(f"✅ Full workflow test completed successfully!")
        print(f"📊 Overall SEO Score: {optimization_result.overall_seo_score}/100")
        print(f"🔍 Meta SEO Score: {optimization_result.meta_seo_score}/100")
        print(f"📱 Mobile Usability: {optimization_result.mobile_usability_score}/100")
        print(f"⚡ Web Vitals Score: {optimization_result.web_vitals_score}/100")
        print(f"🌍 Languages Supported: {len(optimization_result.localized_versions)}")
        print(f"📋 Recommendations: {len(optimization_result.recommendations)}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])