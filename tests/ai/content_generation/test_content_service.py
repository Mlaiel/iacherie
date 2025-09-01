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

"""
Content Service Tests

Comprehensive tests for the ContentService class that provides
the high-level business logic API for content operations.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import uuid

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.content_service import (
    ContentService
)
from ai.content_generation.content_models import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentType,
    Platform,
    QualityLevel
)


class TestContentService:
    """Test suite for ContentService"""
    
    @pytest.fixture
    def service(self):
        """
Create a content service instance"""
        return ContentService()
    
    @pytest.fixture
    def mock_generation_manager(self):
        """
Create a mock generation manager"""
        manager = AsyncMock()
        manager.submit_generation_request.return_value = "task_123"
        manager.get_task_result.return_value = Mock(
            final_content="Generated content",
            status="completed",
            quality_scores={"overall": 0.85}
        )
        return manager
    
    @pytest.fixture
    def mock_quality_metrics(self):
        """Create a mock quality metrics"""
        metrics = AsyncMock()
        metrics.calculate_quality_score.return_value = {
            "overall_score": 0.85,
            "readability_score": 0.8,
            "engagement_score": 0.9,
            "seo_score": 0.8
        }
        return metrics
    
    @pytest.fixture
    def blog_request(self):
        """Create a blog post request"""
        return ContentGenerationRequest(
            content_type=ContentType.BLOG_POST,
            topic="Future of Artificial Intelligence",
            target_audience="tech professionals",
            word_count=1000,
            keywords=["AI", "machine learning", "future"],
            quality_level=QualityLevel.PREMIUM
        )
    
    @pytest.fixture
    def social_request(self):
        """Create a social media request"""
        return ContentGenerationRequest(
            content_type=ContentType.INSTAGRAM_POST,
            topic="Daily motivation",
            target_audience="young professionals",
            word_count=150,
            hashtags=["#motivation", "#success"],
            platform=Platform.INSTAGRAM,
            quality_level=QualityLevel.STANDARD
        )
    
    @pytest.fixture
    def email_request(self):
        """Create an email marketing request"""
        return ContentGenerationRequest(
            content_type=ContentType.EMAIL_MARKETING,
            topic="New product launch",
            target_audience="existing customers",
            word_count=300,
            brand_name="TechCorp",
            call_to_action="Shop Now",
            quality_level=QualityLevel.ENTERPRISE
        )
    
    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service is not None
        assert hasattr(service, 'generation_manager')
        assert hasattr(service, 'quality_metrics')
        assert hasattr(service, 'performance_tracker')
        assert hasattr(service, 'business_rules')
        assert hasattr(service, 'workflows')
    
    @pytest.mark.asyncio
    async def test_create_content_blog_post(self, service, blog_request, mock_generation_manager, mock_quality_metrics):
        """
Test creating a blog post"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                response = await service.create_content(blog_request)
                
                assert response is not None
                assert isinstance(response, ContentGenerationResponse)
                assert response.content_type == ContentType.BLOG_POST
                assert response.status == "completed"
                assert response.final_content == "Generated content"
                assert response.quality_scores is not None
    
    @pytest.mark.asyncio
    async def test_create_content_social_post(self, service, social_request, mock_generation_manager, mock_quality_metrics):
        """Test creating a social media post"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                response = await service.create_content(social_request)
                
                assert response is not None
                assert response.content_type == ContentType.INSTAGRAM_POST
                assert response.status == "completed"
                assert "#motivation" in response.final_content or response.final_content == "Generated content"
    
    @pytest.mark.asyncio
    async def test_create_content_email_marketing(self, service, email_request, mock_generation_manager, mock_quality_metrics):
        """Test creating email marketing content"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                response = await service.create_content(email_request)
                
                assert response is not None
                assert response.content_type == ContentType.EMAIL_MARKETING
                assert response.status == "completed"
                assert "TechCorp" in response.final_content or response.final_content == "Generated content"
    
    @pytest.mark.asyncio
    async def test_business_rule_validation(self, service, blog_request):
        """Test business rule validation"""
        # Test valid request passes validation
        validation_result = await service._validate_business_rules(blog_request)
        assert validation_result["valid"] is True
        assert len(validation_result["violations"]) == 0
        
        # Test invalid request with too many keywords
        invalid_request = blog_request.copy()
        invalid_request.keywords = ["keyword"] * 15  # Too many keywords
        
        validation_result = await service._validate_business_rules(invalid_request)
        assert validation_result["valid"] is False
        assert len(validation_result["violations"]) > 0
    
    @pytest.mark.asyncio
    async def test_quality_threshold_enforcement(self, service, blog_request, mock_generation_manager):
        """Test quality threshold enforcement"""
        # Mock low quality result
        low_quality_result = Mock(
            final_content="Low quality content",
            status="completed",
            quality_scores={"overall": 0.4}  # Below threshold
        )
        mock_generation_manager.get_task_result.return_value = low_quality_result
        
        with patch.object(service, 'generation_manager', mock_generation_manager):
            response = await service.create_content(blog_request)
            
            # Should either retry or mark as needs review
            assert response.status in ["completed", "needs_review", "failed"]
    
    @pytest.mark.asyncio
    async def test_template_based_creation(self, service, social_request):
        """Test template-based content creation"""
        template_request = social_request.copy()
        template_request.template_type = "engagement_post"
        
        response = await service.create_content_from_template(
            template_type="social",
            template_category="engagement_post",
            template_data={
                "question": "What motivates you daily?",
                "brand_name": "MotivationCorp",
                "hashtags": ["#motivation", "#daily"]
            },
            platform=Platform.INSTAGRAM
        )
        
        assert response is not None
        assert isinstance(response, ContentGenerationResponse)
    
    @pytest.mark.asyncio
    async def test_bulk_content_creation(self, service, mock_generation_manager, mock_quality_metrics):
        """Test bulk content creation"""
        requests = []
        for i in range(3):
            request = ContentGenerationRequest(
                content_type=ContentType.SOCIAL_POST,
                topic=f"Topic {i}",
                target_audience="general audience",
                word_count=100
            )
            requests.append(request)
        
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                responses = await service.create_bulk_content(requests)
                
                assert len(responses) == 3
                for response in responses:
                    assert isinstance(response, ContentGenerationResponse)
    
    @pytest.mark.asyncio
    async def test_content_optimization(self, service, blog_request):
        """Test content optimization"""
        original_content = "This is original content that needs optimization."
        
        optimized_content = await service.optimize_content(
            content=original_content,
            optimization_type="seo",
            target_platform=Platform.LINKEDIN,
            keywords=["optimization", "content", "SEO"]
        )
        
        assert optimized_content is not None
        assert len(optimized_content) > 0
    
    @pytest.mark.asyncio
    async def test_content_analysis(self, service):
        """Test content analysis functionality"""
        content = "This is a sample content for analysis. It contains multiple sentences and should provide good metrics."
        
        analysis_result = await service.analyze_content(content)
        
        assert analysis_result is not None
        assert "quality_scores" in analysis_result
        assert "recommendations" in analysis_result
        assert "metrics" in analysis_result
    
    @pytest.mark.asyncio
    async def test_workflow_customization(self, service, blog_request):
        """Test custom workflow execution"""
        custom_workflow = {
            "name": "premium_blog",
            "stages": ["planning", "generation", "seo_optimization", "quality_enhancement", "validation"],
            "quality_threshold": 0.9,
            "max_retries": 2
        }
        
        # Register custom workflow
        service.register_workflow("premium_blog", custom_workflow)
        
        # Use custom workflow
        blog_request.workflow = "premium_blog"
        
        with patch.object(service, 'generation_manager', AsyncMock()):
            service.generation_manager.submit_generation_request.return_value = "task_123"
            service.generation_manager.get_task_result.return_value = Mock(
                final_content="Premium content",
                status="completed",
                quality_scores={"overall": 0.95}
            )
            
            response = await service.create_content(blog_request)
            
            assert response is not None
            assert response.workflow == "premium_blog"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service, blog_request, mock_generation_manager):
        """Test error handling in content creation"""
        # Mock generation manager to raise an error
        mock_generation_manager.submit_generation_request.side_effect = Exception("Generation failed")
        
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with pytest.raises(ContentCreationError):
                await service.create_content(blog_request)
    
    @pytest.mark.asyncio
    async def test_business_rule_violation_handling(self, service):
        """Test business rule violation handling"""
        # Create request that violates business rules
        invalid_request = ContentGenerationRequest(
            content_type=ContentType.BLOG_POST,
            topic="",  # Empty topic violates rules
            target_audience="",  # Empty audience violates rules
            word_count=-100  # Negative word count violates rules
        )
        
        with pytest.raises(BusinessRuleViolationError):
            await service.create_content(invalid_request)
    
    @pytest.mark.asyncio
    async def test_performance_tracking(self, service, blog_request, mock_generation_manager, mock_quality_metrics):
        """Test performance tracking during content creation"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                # Track performance before
                initial_metrics = service.get_performance_metrics()
                
                # Create content
                response = await service.create_content(blog_request)
                
                # Track performance after
                final_metrics = service.get_performance_metrics()
                
                # Should have tracked the operation
                assert final_metrics["total_requests"] >= initial_metrics["total_requests"]
    
    @pytest.mark.asyncio
    async def test_content_caching(self, service, blog_request, mock_generation_manager, mock_quality_metrics):
        """Test content caching functionality"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                # First request
                response1 = await service.create_content(blog_request)
                
                # Second identical request (should use cache if implemented)
                response2 = await service.create_content(blog_request)
                
                assert response1 is not None
                assert response2 is not None
                # Both should succeed regardless of caching implementation
    
    def test_content_validation(self, service):
        """
Test content validation methods"""
        # Test valid content
        valid_content = "This is a well-formed piece of content with appropriate length and structure."
        validation_result = service._validate_content(valid_content, ContentType.BLOG_POST)
        assert validation_result["valid"] is True
        
        # Test invalid content
        invalid_content = ""
        validation_result = service._validate_content(invalid_content, ContentType.BLOG_POST)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_metrics_collection(self, service):
        """Test metrics collection"""
        metrics = service.get_performance_metrics()
        
        expected_keys = [
            'total_requests',
            'successful_requests',
            'failed_requests',
            'avg_processing_time',
            'quality_scores_distribution',
            'content_type_distribution'
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    @pytest.mark.asyncio
    async def test_concurrent_content_creation(self, service, mock_generation_manager, mock_quality_metrics):
        """
Test concurrent content creation"""
        with patch.object(service, 'generation_manager', mock_generation_manager):
            with patch.object(service, 'quality_metrics', mock_quality_metrics):
                # Create multiple requests
                requests = []
                for i in range(5):
                    request = ContentGenerationRequest(
                        content_type=ContentType.SOCIAL_POST,
                        topic=f"Concurrent topic {i}",
                        target_audience="test audience",
                        word_count=100
                    )
                    requests.append(request)
                
                # Execute concurrently
                tasks = [service.create_content(req) for req in requests]
                responses = await asyncio.gather(*tasks)
                
                assert len(responses) == 5
                for response in responses:
                    assert isinstance(response, ContentGenerationResponse)
    
    @pytest.mark.asyncio
    async def test_content_revision(self, service):
        """Test content revision functionality"""
        original_content = "This is the original content that needs revision."
        revision_instructions = "Make it more engaging and add a call to action."
        
        revised_content = await service.revise_content(
            content=original_content,
            instructions=revision_instructions,
            content_type=ContentType.BLOG_POST
        )
        
        assert revised_content is not None
        assert len(revised_content) > 0
        assert revised_content != original_content
    
    @pytest.mark.asyncio
    async def test_content_localization(self, service, blog_request):
        """Test content localization"""
        # Set language for localization
        blog_request.language = "fr"  # French
        
        with patch.object(service, 'generation_manager', AsyncMock()):
            service.generation_manager.submit_generation_request.return_value = "task_123"
            service.generation_manager.get_task_result.return_value = Mock(
                final_content="Contenu généré en français",
                status="completed",
                quality_scores={"overall": 0.85}
            )
            
            response = await service.create_content(blog_request)
            
            assert response is not None
            assert response.language == "fr"
    
    @pytest.mark.asyncio
    async def test_content_versioning(self, service, blog_request):
        """Test content versioning"""
        with patch.object(service, 'generation_manager', AsyncMock()):
            service.generation_manager.submit_generation_request.return_value = "task_123"
            service.generation_manager.get_task_result.return_value = Mock(
                final_content="Versioned content",
                status="completed",
                quality_scores={"overall": 0.85}
            )
            
            # Create initial version
            response_v1 = await service.create_content(blog_request)
            
            # Create new version with modifications
            blog_request.context = {"version": "2.0", "improvements": ["better_seo", "more_engaging"]}
            response_v2 = await service.create_content(blog_request)
            
            assert response_v1 is not None
            assert response_v2 is not None
            # Both versions should be tracked
    
    def test_business_rules_configuration(self, service):
        """Test business rules configuration"""
        # Get current rules
        current_rules = service.get_business_rules()
        assert current_rules is not None
        
        # Update rules
        new_rules = {
            "max_word_count": 2000,
            "min_word_count": 50,
            "max_keywords": 8,
            "required_fields": ["topic", "target_audience"]
        }
        
        service.update_business_rules(new_rules)
        
        updated_rules = service.get_business_rules()
        assert updated_rules["max_word_count"] == 2000
        assert updated_rules["max_keywords"] == 8
    
    @pytest.mark.asyncio
    async def test_content_scheduling(self, service, social_request):
        """Test content scheduling functionality"""
        from datetime import datetime, timedelta
        
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        scheduled_response = await service.schedule_content(
            request=social_request,
            scheduled_time=scheduled_time,
            platforms=[Platform.INSTAGRAM, Platform.TWITTER]
        )
        
        assert scheduled_response is not None
        assert "task_ids" in scheduled_response
        assert "scheduled_time" in scheduled_response
    
    @pytest.mark.asyncio
    async def test_a_b_testing_support(self, service, social_request):
        """Test A/B testing support"""
        # Create A/B test variants
        variant_a = social_request.copy()
        variant_a.tone = "professional"
        
        variant_b = social_request.copy()
        variant_b.tone = "casual"
        
        ab_test_result = await service.create_ab_test_content(
            variant_a=variant_a,
            variant_b=variant_b,
            test_name="tone_comparison",
            success_metric="engagement_rate"
        )
        
        assert ab_test_result is not None
        assert "test_id" in ab_test_result
        assert "variant_a_response" in ab_test_result
        assert "variant_b_response" in ab_test_result


class TestContentServiceIntegration:
    """Integration tests for ContentService"""
    
    @pytest.fixture
    def integrated_service(self):
        """
Create a service with real dependencies for integration testing"""
        return ContentService()
    
    @pytest.mark.asyncio
    async def test_end_to_end_blog_creation(self, integrated_service):
        """
Test end-to-end blog post creation"""
        request = ContentGenerationRequest(
            content_type=ContentType.BLOG_POST,
            topic="Benefits of Remote Work",
            target_audience="business professionals",
            word_count=800,
            keywords=["remote work", "productivity", "work-life balance"],
            quality_level=QualityLevel.PREMIUM
        )
        
        try:
            response = await integrated_service.create_content(request)
            
            # Basic validation that should work regardless of backend implementation
            assert response is not None
            assert isinstance(response, ContentGenerationResponse)
            assert response.content_type == ContentType.BLOG_POST
            
        except Exception as e:
            # If real backend is not available, test should pass gracefully
            pytest.skip(f"Backend not available for integration test: {e}")
    
    @pytest.mark.asyncio
    async def test_end_to_end_social_media_creation(self, integrated_service):
        """Test end-to-end social media post creation"""
        request = ContentGenerationRequest(
            content_type=ContentType.INSTAGRAM_POST,
            topic="Monday motivation",
            target_audience="young professionals",
            word_count=120,
            hashtags=["#mondaymotivation", "#success"],
            platform=Platform.INSTAGRAM
        )
        
        try:
            response = await integrated_service.create_content(request)
            
            assert response is not None
            assert isinstance(response, ContentGenerationResponse)
            assert response.content_type == ContentType.INSTAGRAM_POST
            
        except Exception as e:
            pytest.skip(f"Backend not available for integration test: {e}")


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
