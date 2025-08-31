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
Content Models Tests

Comprehensive tests for Pydantic models and data structures
used in the content generation system.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from pydantic import ValidationError
from enum import Enum

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.content_models import (
    Platform,
    ContentType,
    ContentFormat,
    QualityLevel,
    BrandVoice,
    ContentGenerationRequest,
    ContentOptimizationRequest,
    TemplateRequest,
    PerformanceAnalysisRequest,
    QualityScoreResponse,
    ContentGenerationResponse,
    ContentOptimizationResponse,
    PerformanceMetrics,
    PerformanceInsight,
    PerformanceAnalysisResponse,
    ContentRecommendationsResponse,
    ContentMetadata,
    ABTestConfiguration,
    ContentError,
    BatchContentRequest
)


class TestEnums:
    """Test suite for enum definitions"""
    
    def test_platform_enum(self):
        """Test Platform enum values"""
        assert Platform.INSTAGRAM.value == "instagram"
        assert Platform.TWITTER.value == "twitter"
        assert Platform.LINKEDIN.value == "linkedin"
        assert Platform.TIKTOK.value == "tiktok"
        assert Platform.YOUTUBE.value == "youtube"
        assert Platform.FACEBOOK.value == "facebook"
        assert Platform.PINTEREST.value == "pinterest"
        assert Platform.SNAPCHAT.value == "snapchat"
        assert Platform.THREADS.value == "threads"
        
        # Test enum count
        assert len(Platform) == 9
    
    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.BLOG_POST.value == "blog_post"
        assert ContentType.SOCIAL_POST.value == "social_post"
        assert ContentType.INSTAGRAM_POST.value == "instagram_post"
        assert ContentType.TWITTER_POST.value == "twitter_post"
        assert ContentType.LINKEDIN_POST.value == "linkedin_post"
        assert ContentType.TIKTOK_CAPTION.value == "tiktok_caption"
        assert ContentType.YOUTUBE_DESCRIPTION.value == "youtube_description"
        assert ContentType.EMAIL_MARKETING.value == "email_marketing"
        assert ContentType.NEWSLETTER.value == "newsletter"
        assert ContentType.PRODUCT_DESCRIPTION.value == "product_description"
        assert ContentType.SALES_PAGE.value == "sales_page"
        assert ContentType.LANDING_PAGE.value == "landing_page"
        assert ContentType.AD_COPY.value == "ad_copy"
        assert ContentType.PRESS_RELEASE.value == "press_release"
        assert ContentType.ARTICLE.value == "article"
        
        # Test enum count
        assert len(ContentType) == 15
    
    def test_content_format_enum(self):
        """Test ContentFormat enum values"""
        assert ContentFormat.TEXT.value == "text"
        assert ContentFormat.HTML.value == "html"
        assert ContentFormat.MARKDOWN.value == "markdown"
        assert ContentFormat.JSON.value == "json"
        assert ContentFormat.XML.value == "xml"
        
        # Test enum count
        assert len(ContentFormat) == 5
    
    def test_quality_level_enum(self):
        """Test QualityLevel enum values"""
        assert QualityLevel.BASIC.value == "basic"
        assert QualityLevel.STANDARD.value == "standard"
        assert QualityLevel.PREMIUM.value == "premium"
        assert QualityLevel.ENTERPRISE.value == "enterprise"
        
        # Test enum count
        assert len(QualityLevel) == 4
    
    def test_brand_voice_enum(self):
        """Test BrandVoice enum values"""
        assert BrandVoice.PROFESSIONAL.value == "professional"
        assert BrandVoice.CASUAL.value == "casual"
        assert BrandVoice.FRIENDLY.value == "friendly"
        assert BrandVoice.AUTHORITATIVE.value == "authoritative"
        assert BrandVoice.PLAYFUL.value == "playful"
        assert BrandVoice.INSPIRATIONAL.value == "inspirational"
        
        # Test enum count
        assert len(BrandVoice) == 6


class TestContentRequest:
    """Test suite for ContentGenerationRequest model"""
    
    def test_basic_content_request(self):
        """Test basic content request creation"""
        request = ContentGenerationRequest(
            content_type=ContentType.SOCIAL_POST,
            platform=Platform.INSTAGRAM,
            topic="AI technology trends",
            target_audience="tech enthusiasts",
            tone="professional"
        )
        
        assert request.content_type == ContentType.SOCIAL_POST
        assert request.platform == Platform.INSTAGRAM
        assert request.topic == "AI technology trends"
        assert request.target_audience == "tech enthusiasts"
        assert request.tone == "professional"
        assert request.content_type == ContentType.SOCIAL_POST
        assert request.platform == Platform.INSTAGRAM
        assert request.topic == "AI technology trends"
        assert request.target_audience == "tech enthusiasts"
        assert request.tone == BrandVoice.PROFESSIONAL  # default from Field
        assert request.language == "en"  # default
        assert request.quality_level == QualityLevel.STANDARD  # default
    
    def test_content_request_with_optional_fields(self):
        """Test content request with all optional fields"""
        keywords = ["AI", "technology", "innovation"]
        style_preferences = {"focus_keyword": "AI trends", "meta_description": True}
        
        request = ContentGenerationRequest(
            content_type=ContentType.BLOG_POST,
            topic="Complete guide to AI",
            target_audience="beginners",
            platform=Platform.LINKEDIN,
            tone=BrandVoice.FRIENDLY,
            language="de",
            word_count=1500,
            keywords=keywords,
            hashtags=["#AI", "#technology"],
            style_preferences=style_preferences,
            brand_name="TechCorp",
            call_to_action="Subscribe to our newsletter",
            format=ContentFormat.MARKDOWN,
            quality_level=QualityLevel.PREMIUM
        )
        
        assert request.tone == BrandVoice.FRIENDLY
        assert request.language == "de"
        assert request.word_count == 1500
        assert request.keywords == keywords
        assert request.hashtags == ["#AI", "#technology"]
        assert request.style_preferences == style_preferences
        assert request.brand_name == "TechCorp"
        assert request.call_to_action == "Subscribe to our newsletter"
        assert request.format == ContentFormat.MARKDOWN
        assert request.quality_level == QualityLevel.PREMIUM
    
    def test_content_request_validation_errors(self):
        """Test content request validation errors"""
        # Test missing required fields
        with pytest.raises(ValidationError):
            ContentGenerationRequest()
        
        # Test topic too short
        with pytest.raises(ValidationError):
            ContentGenerationRequest(
                content_type=ContentType.TWITTER_POST,
                topic="hi"  # Too short (min_length=3)
            )


class TestContentResponse:
    """Test suite for ContentGenerationResponse model"""
    
    def test_successful_content_response(self):
        """Test successful content response creation"""
        response = ContentGenerationResponse(
            content_id="content_123",
            content_type=ContentType.SOCIAL_POST,
            status="completed",
            final_content="Generated content here",
            word_count=25,
            character_count=150
        )
        
        assert response.content_id == "content_123"
        assert response.final_content == "Generated content here"
        assert response.status == "completed"
        assert response.word_count == 25
        assert response.character_count == 150
        assert isinstance(response.created_at, datetime)
    
    def test_failed_content_response(self):
        """Test failed content response creation"""
        response = ContentGenerationResponse(
            content_id="content_456",
            content_type=ContentType.BLOG_POST,
            status="failed",
            error="Generation failed due to API limits"
        )
        
        assert response.status == "failed"
        assert response.error == "Generation failed due to API limits"
        assert response.final_content is None
    
    def test_content_response_with_metrics(self):
        """Test content response with quality scores"""
        quality_score = QualityScoreResponse(
            overall_score=0.88,
            readability_score=0.85,
            engagement_score=0.92,
            seo_score=0.78,
            originality_score=0.95,
            technical_score=0.89,
            brand_alignment_score=0.87,
            quality_grade="A-",
            dimension_scores={"clarity": 0.90, "relevance": 0.85},
            improvement_suggestions=["Add more specific examples", "Improve call-to-action"]
        )
        
        response = ContentGenerationResponse(
            content_id="content_789",
            content_type=ContentType.BLOG_POST,
            status="completed",
            final_content="SEO optimized blog post content...",
            word_count=800,
            character_count=5000,
            quality_scores=quality_score
        )
        
        assert response.quality_scores == quality_score
        assert response.quality_scores.readability_score == 0.85
        assert response.quality_scores.overall_score == 0.88


class TestABTestConfiguration:
    """Test suite for ABTestConfiguration model"""
    
    def test_basic_ab_test_config(self):
        """Test basic A/B test configuration"""
        config = ABTestConfiguration(
            test_id="test_001",
            test_name="CTA Button Test",
            hypothesis="Blue button will increase clicks by 15%",
            variant_a={"button_color": "red", "button_text": "Click Here"},
            variant_b={"button_color": "blue", "button_text": "Click Here"},
            success_metric="click_through_rate"
        )
        
        assert config.test_id == "test_001"
        assert config.test_name == "CTA Button Test"
        assert config.traffic_split == 0.5  # default
        assert config.duration_days == 7  # default
        assert config.status == "draft"  # default
    
    def test_advanced_ab_test_config(self):
        """Test advanced A/B test configuration"""
        config = ABTestConfiguration(
            test_id="test_002",
            test_name="Headlines Test",
            hypothesis="Emotional headline will increase engagement",
            variant_a={"headline": "Professional AI Solutions"},
            variant_b={"headline": "Transform Your Business with AI"},
            traffic_split=0.6,
            duration_days=14,
            success_metric="conversion_rate",
            confidence_level=0.99,
            minimum_sample_size=200,
            status="running"
        )
        
        assert config.traffic_split == 0.6
        assert config.duration_days == 14
        assert config.confidence_level == 0.99
        assert config.minimum_sample_size == 200
        assert config.status == "running"
    
    def test_ab_test_config_validation(self):
        """Test A/B test config validation"""
        # Test invalid traffic split
        with pytest.raises(ValidationError):
            ABTestConfiguration(
                test_id="test_003",
                test_name="Invalid Test",
                hypothesis="Test hypothesis",
                variant_a={"test": "a"},
                variant_b={"test": "b"},
                success_metric="clicks",
                traffic_split=1.5  # Too high
            )
        
        # Test invalid duration
        with pytest.raises(ValidationError):
            ABTestConfiguration(
                test_id="test_004",
                test_name="Invalid Duration Test",
                hypothesis="Test hypothesis",
                variant_a={"test": "a"},
                variant_b={"test": "b"},
                success_metric="clicks",
                duration_days=0  # Invalid
            )


class TestContentMetadata:
    """Test suite for ContentMetadata model"""
    
    def test_content_metadata_creation(self):
        """Test content metadata creation"""
        metadata = ContentMetadata(
            title="AI Content Generation Guide",
            description="Complete guide to AI-powered content creation",
            author="Fahed Mlaiel",
            tags=["ai", "automation", "efficiency"],
            category="Technology",
            meta_title="Ultimate AI Content Guide 2025",
            meta_description="Learn how to create amazing content with AI tools",
            status="published"
        )
        
        assert metadata.title == "AI Content Generation Guide"
        assert metadata.author == "Fahed Mlaiel"
        assert metadata.category == "Technology"
        assert metadata.tags == ["ai", "automation", "efficiency"]
        assert metadata.meta_title == "Ultimate AI Content Guide 2025"
        assert metadata.status == "published"
    
    def test_metadata_version_tracking(self):
        """Test metadata with social media fields"""
        metadata = ContentMetadata(
            title="Social Media Post",
            author="Test Author",
            og_title="Amazing Social Post",
            og_description="This post will go viral",
            og_image="https://example.com/image.jpg",
            canonical_url="https://example.com/post"
        )
        
        assert metadata.og_title == "Amazing Social Post"
        assert metadata.og_description == "This post will go viral"
        assert metadata.og_image == "https://example.com/image.jpg"
        assert metadata.canonical_url == "https://example.com/post"


class TestQualityScoreResponse:
    """Test suite for QualityScoreResponse model"""
    
    def test_quality_score_response_creation(self):
        """Test quality score response creation"""
        response = QualityScoreResponse(
            overall_score=0.875,
            readability_score=0.912,
            engagement_score=0.838,
            seo_score=0.945,
            originality_score=0.987,
            technical_score=0.893,
            brand_alignment_score=0.765,
            quality_grade="A",
            dimension_scores={"clarity": 0.9, "creativity": 0.8},
            improvement_suggestions=["Improve readability", "Add more keywords"]
        )
        
        assert response.overall_score == 0.875
        assert response.readability_score == 0.912
        assert response.engagement_score == 0.838
        assert response.seo_score == 0.945
        assert response.quality_grade == "A"
        assert len(response.improvement_suggestions) == 2
    
    def test_quality_score_response_validation(self):
        """Test quality score response validation"""
        # Test valid score range
        response = QualityScoreResponse(
            overall_score=0.5,
            readability_score=0.75,
            engagement_score=0.6,
            seo_score=0.8,
            originality_score=0.9,
            technical_score=0.7,
            brand_alignment_score=0.65,
            quality_grade="B",
            dimension_scores={"clarity": 0.7},
            improvement_suggestions=[]
        )
        
        assert response.overall_score == 0.5
        assert response.readability_score == 0.75


class TestPerformanceMetrics:
    """Test suite for PerformanceMetrics model"""
    
    def test_performance_metrics_creation(self):
        """Test performance metrics creation"""
        from datetime import datetime, timezone
        
        metrics = PerformanceMetrics(
            content_id="content_123",
            platform=Platform.INSTAGRAM,
            content_type=ContentType.SOCIAL_POST,
            views=1500,
            likes=250,
            shares=45,
            comments=78,
            engagement_rate=0.128,
            reach=2300,
            impressions=4500,
            click_through_rate=0.032,
            conversion_rate=0.021,
            created_at=datetime.now(timezone.utc)
        )
        
        assert metrics.content_id == "content_123"
        assert metrics.platform == Platform.INSTAGRAM
        assert metrics.views == 1500
        assert metrics.likes == 250
        assert metrics.shares == 45
        assert metrics.comments == 78
        assert metrics.engagement_rate == 0.128
        assert metrics.reach == 2300
        assert metrics.impressions == 4500
    
    def test_performance_metrics_optional_fields(self):
        """Test performance metrics with optional fields"""
        from datetime import datetime, timezone
        
        metrics = PerformanceMetrics(
            content_id="content_456",
            platform=Platform.TWITTER,
            content_type=ContentType.SOCIAL_POST,
            views=800,
            likes=120,
            shares=25,
            comments=35,
            engagement_rate=0.085,
            reach=1200,
            impressions=2500,
            created_at=datetime.now(timezone.utc)
        )
        
        assert metrics.content_id == "content_456"
        assert metrics.platform == Platform.TWITTER
        assert metrics.views == 800
        assert metrics.likes == 120
        assert metrics.engagement_rate == 0.085


class TestContentOptimizationRequest:
    """Test suite for ContentOptimizationRequest model"""
    
    def test_content_optimization_request_creation(self):
        """Test content optimization request creation"""
        request = ContentOptimizationRequest(
            content="Basic content about AI technology",
            target_platform=Platform.INSTAGRAM,
            optimization_goals=["engagement", "reach", "clarity"],
            current_performance={"views": 100, "likes": 15},
            target_metrics={"engagement_rate": 8.0, "reach": 1000},
            constraints=["max_length: 280", "family_friendly: true"]
        )
        
        assert request.content == "Basic content about AI technology"
        assert request.target_platform == Platform.INSTAGRAM
        assert len(request.optimization_goals) == 3
        assert request.current_performance["views"] == 100
    
    def test_content_optimization_optional_fields(self):
        """Test content optimization request with optional fields"""
        request = ContentOptimizationRequest(
            content="Simple AI guide",
            target_platform=Platform.TWITTER,
            optimization_goals=["engagement"]
        )
        
        assert request.content == "Simple AI guide"
        assert request.target_platform == Platform.TWITTER
        assert len(request.optimization_goals) == 1


class TestTemplateRequest:
    """Test suite for TemplateRequest model"""
    
    def test_template_request_creation(self):
        """Test template request creation"""
        request = TemplateRequest(
            template_type="blog_post",
            content_type=ContentType.BLOG_POST,
            platform=Platform.LINKEDIN,
            variables={"title": "AI Guide", "author": "Fahed Mlaiel"},
            customization_level="advanced",
            output_format=ContentFormat.MARKDOWN
        )
        
        assert request.template_type == "blog_post"
        assert request.content_type == ContentType.BLOG
        assert request.platform == Platform.LINKEDIN
        assert request.variables["title"] == "AI Guide"
        assert request.variables["author"] == "Fahed Mlaiel"
    
    def test_template_request_optional_fields(self):
        """Test template request with optional fields"""
        request = TemplateRequest(
            template_type="social_post",
            content_type=ContentType.SOCIAL_POST,
            platform=Platform.TWITTER,
            variables={"topic": "AI trends"}
        )
        
        assert request.template_type == "social_post"
        assert request.content_type == ContentType.SOCIAL
        assert request.platform == Platform.TWITTER
        assert request.variables["topic"] == "AI trends"


class TestBatchContentRequest:
    """Test suite for BatchContentRequest model"""
    
    def test_batch_content_request_creation(self):
        """Test batch content request creation"""
        individual_requests = [
            {
                "content_type": "social_post",
                "platform": "instagram",
                "topic": "AI topic 1",
                "target_audience": "tech professionals"
            },
            {
                "content_type": "blog",
                "platform": "linkedin", 
                "topic": "AI topic 2",
                "target_audience": "business leaders"
            }
        ]
        
        batch = BatchContentRequest(
            requests=individual_requests,
            batch_settings={"priority": "high", "deadline": "2025-02-01"},
            global_brand_voice=BrandVoice.PROFESSIONAL,
            callback_url="https://example.com/webhook"
        )
        
        assert len(batch.requests) == 2
        assert batch.requests[0]["topic"] == "AI topic 1"
        assert batch.requests[1]["platform"] == "linkedin"
        assert batch.global_brand_voice == BrandVoice.PROFESSIONAL
        assert batch.callback_url == "https://example.com/webhook"
    
    def test_batch_with_settings(self):
        """Test batch with batch settings"""
        batch = BatchContentRequest(
            requests=[{"content_type": "social", "topic": "test"}],
            batch_settings={"auto_optimize": True, "quality_check": True},
            global_brand_voice=BrandVoice.CASUAL
        )
        
        assert len(batch.requests) == 1
        assert batch.batch_settings["auto_optimize"] is True
        assert batch.global_brand_voice == BrandVoice.CASUAL


class TestPerformanceAnalysisRequest:
    """Test suite for PerformanceAnalysisRequest model"""
    
    def test_performance_analysis_request_creation(self):
        """Test performance analysis request creation"""
        request = PerformanceAnalysisRequest(
            content_ids=["content_1", "content_2", "content_3"],
            analysis_types=["engagement", "reach", "conversion"],
            time_period="7d",
            comparison_enabled=True,
            breakdown_by_platform=True
        )
        
        assert len(request.content_ids) == 3
        assert "content_1" in request.content_ids
        assert request.analysis_types == ["engagement", "reach", "conversion"]
        assert request.time_period == "7d"
        assert request.comparison_enabled is True
        assert request.breakdown_by_platform is True
    
    def test_performance_analysis_optional_fields(self):
        """Test performance analysis request with optional fields"""
        request = PerformanceAnalysisRequest(
            content_ids=["content_1"],
            analysis_types=["engagement"]
        )
        
        assert len(request.content_ids) == 1
        assert request.analysis_types == ["engagement"]


class TestContentGenerationResponse:
    """Test suite for ContentGenerationResponse model"""
    
    def test_content_generation_response_creation(self):
        """Test content generation response creation"""
        response = ContentGenerationResponse(
            content_id="content_123",
            content_type=ContentType.BLOG_POST,
            status="completed",
            final_content="This is the generated blog post content...",
            original_content="Original draft content...",
            workflow="standard_blog_workflow",
            steps_completed=["generate", "review", "optimize"]
        )
        
        assert response.content_id == "content_123"
        assert response.content_type == ContentType.BLOG_POST
        assert response.status == "completed"
        assert response.final_content == "This is the generated blog post content..."
        assert response.original_content == "Original draft content..."
        assert response.workflow == "standard_blog_workflow"
        assert len(response.steps_completed) == 3
    
    def test_content_generation_response_validation(self):
        """Test content generation response validation"""
        # Test with minimal required fields
        response = ContentGenerationResponse(
            content_id="content_456",
            content_type=ContentType.SOCIAL_POST,
            status="in_progress"
        )
        
        assert response.content_id == "content_456"
        assert response.content_type == ContentType.SOCIAL_POST
        assert response.status == "in_progress"
        assert response.final_content is None


class TestContentOptimizationResponse:
    """Test suite for ContentOptimizationResponse model"""
    
    def test_content_optimization_response_creation(self):
        """Test content optimization response creation"""
        response = ContentOptimizationResponse(
            original_content="Basic AI content",
            optimized_content="Enhanced AI content with better engagement and SEO optimization",
            optimization_applied=["seo", "engagement", "readability"],
            improvements_made={"seo_score": 0.85, "readability": 0.9},
            performance_prediction={"engagement_rate": 0.12, "reach": 5000},
            suggestions=["Add more keywords", "Include call-to-action"]
        )
        
        assert response.original_content == "Basic AI content"
        assert "Enhanced AI content" in response.optimized_content
        assert len(response.optimization_applied) == 3
        assert response.improvements_made["seo_score"] == 0.85
        assert response.performance_prediction["reach"] == 5000
        assert len(response.suggestions) == 2
    
    def test_content_optimization_response_validation(self):
        """Test content optimization response validation"""
        response = ContentOptimizationResponse(
            original_content="Simple content",
            optimized_content="Improved content",
            optimization_applied=["basic"],
            improvements_made={},
            performance_prediction={},
            suggestions=[]
        )
        
        assert response.original_content == "Simple content"
        assert response.optimized_content == "Improved content"


class TestContentError:
    """Test suite for ContentError model"""
    
    def test_content_error_creation(self):
        """Test content error creation"""
        error = ContentError(
            error_code="GENERATION_FAILED",
            error_message="Failed to generate content due to API timeout",
            content_id="content_123",
            error_type="api_error",
            retry_count=2,
            context={"model": "gpt-4", "timeout": 30}
        )
        
        assert error.error_code == "GENERATION_FAILED"
        assert "API timeout" in error.error_message
        assert error.content_id == "content_123"
        assert error.error_type == "api_error"
        assert error.retry_count == 2
        assert error.context["model"] == "gpt-4"
    
    def test_content_error_validation(self):
        """Test content error with minimal fields"""
        error = ContentError(
            error_code="VALIDATION_ERROR",
            error_message="Invalid input parameters",
            error_type="validation"
        )
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.error_message == "Invalid input parameters"
        assert error.error_type == "validation"
        assert error.content_id is None


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
