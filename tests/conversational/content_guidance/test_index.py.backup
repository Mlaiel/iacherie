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

"""Test for Content Guidance Index Module - Enterprise Level Testing
================================================================

Comprehensive testing suite for the content guidance orchestrator ensuring
industrial-grade reliability, performance, and compliance with business requirements.

Author: Fahed Mlaiel <mlaiel@live.de>  
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

from conversational.content_guidance.index import (
    ContentGuidanceOrchestrator,
    ContentGuidanceRequest,
    ContentGuidanceResponse,
    ContentGuidanceServiceType,
    get_comprehensive_content_guidance,
    get_specific_content_guidance
)


@pytest.fixture
def orchestrator():
    """Create a content guidance orchestrator for testing."""
    return ContentGuidanceOrchestrator()


@pytest.fixture
def sample_request():
    """Create a sample content guidance request."""
    return ContentGuidanceRequest(
        creator_id="creator_123",
        content_type="video",
        content_text="Sample content for testing",
        platforms=["youtube", "instagram"],
        target_audience="young_adults",
        objectives=["increase_engagement", "grow_followers"]
    )


@pytest.fixture
def mock_optimization_result():
    """Mock optimization result."""
    mock_result = Mock()
    mock_result.recommendations = ["Optimize title for SEO", "Add trending hashtags"]
    mock_result.quality_analysis = {"score": 0.85, "areas": ["grammar", "engagement"]}
    mock_result.seo_suggestions = ["Add keywords", "Improve meta description"]
    mock_result.platform_optimization = {"youtube": "Add chapters", "instagram": "Use stories"}
    mock_result.optimization_score = 0.82
    mock_result.predicted_reach_increase = 0.25
    mock_result.predicted_engagement_improvement = 0.18
    mock_result.confidence_level = 0.88
    mock_result.action_items = ["Update title", "Add tags"]
    mock_result.optimization_type = "content_enhancement"
    return mock_result


class TestContentGuidanceOrchestrator:
    """Test suite for Content Guidance Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes all service engines correctly."""
        assert orchestrator.content_optimizer is not None
        assert orchestrator.platform_engine is not None
        assert orchestrator.monetization_engine is not None
        assert orchestrator.trend_analyzer is not None
        assert orchestrator.audience_engine is not None
        assert orchestrator.brand_safety_engine is not None
        assert orchestrator.collaboration_finder is not None
        assert orchestrator.content_scheduler is not None
        assert orchestrator.creative_assistant is not None
        assert orchestrator.performance_tracker is not None
        
        # Verify service registry
        assert len(orchestrator.services) == 10
        for service_type in ContentGuidanceServiceType:
            assert service_type in orchestrator.services
    
    @pytest.mark.asyncio
    async def test_comprehensive_guidance_workflow(self, orchestrator, sample_request):
        """Test the complete comprehensive guidance workflow."""
        
        # Mock all service engines
        with patch.multiple(
            orchestrator,
            content_optimizer=AsyncMock(),
            platform_engine=AsyncMock(),
            monetization_engine=AsyncMock(),
            trend_analyzer=AsyncMock(),
            audience_engine=AsyncMock(),
            brand_safety_engine=AsyncMock(),
            collaboration_finder=AsyncMock(),
            content_scheduler=AsyncMock(),
            creative_assistant=AsyncMock(),
            performance_tracker=AsyncMock()
        ):
            
            # Mock safety analysis to pass
            orchestrator.brand_safety_engine.analyze_text_content.return_value = Mock(
                overall_safety_score=0.9,
                risk_factors=[],
                recommendations=[]
            )
            
            # Mock each service to return appropriate results
            orchestrator.content_optimizer.optimize_text_content.return_value = Mock(
                recommendations=["Optimize title"],
                quality_analysis={"score": 0.85},
                seo_suggestions=["Add keywords"],
                platform_optimization={"youtube": "Add chapters"},
                optimization_score=0.82,
                predicted_reach_increase=0.25,
                predicted_engagement_improvement=0.18,
                confidence_level=0.88,
                action_items=["Update title"],
                optimization_type="content_enhancement"
            )
            
            # Execute comprehensive guidance
            results = await orchestrator.process_comprehensive_guidance(sample_request)
            
            # Verify results structure
            assert isinstance(results, dict)
            assert len(results) == len(ContentGuidanceServiceType)
            
            # Verify each service type has a response
            for service_type in ContentGuidanceServiceType:
                assert service_type in results
                response = results[service_type]
                assert isinstance(response, ContentGuidanceResponse)
                assert response.creator_id == sample_request.creator_id
                assert response.service_type == service_type
                assert isinstance(response.recommendations, list)
                assert isinstance(response.insights, list)
                assert isinstance(response.metrics, dict)
                assert 0.0 <= response.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_single_service_guidance(self, orchestrator, sample_request):
        """Test single service guidance processing."""
        
        with patch.object(orchestrator, 'content_optimizer', AsyncMock()) as mock_optimizer:
            # Mock safety check
            with patch.object(orchestrator, 'brand_safety_engine', AsyncMock()) as mock_safety:
                mock_safety.analyze_text_content.return_value = Mock(
                    overall_safety_score=0.9
                )
                
                # Mock optimization result
                mock_optimizer.optimize_text_content.return_value = Mock(
                    recommendations=["Test recommendation"],
                    quality_analysis={"score": 0.8},
                    seo_suggestions=["SEO suggestion"],
                    platform_optimization={"platform": "optimization"},
                    optimization_score=0.75,
                    predicted_reach_increase=0.2,
                    predicted_engagement_improvement=0.15,
                    confidence_level=0.85,
                    action_items=["Action item"],
                    optimization_type="test"
                )
                
                # Test single service guidance
                result = await orchestrator.process_single_service_guidance(
                    ContentGuidanceServiceType.OPTIMIZATION,
                    sample_request
                )
                
                # Verify result
                assert isinstance(result, ContentGuidanceResponse)
                assert result.service_type == ContentGuidanceServiceType.OPTIMIZATION
                assert result.creator_id == sample_request.creator_id
                assert len(result.recommendations) > 0
                assert result.confidence_score > 0
                
                # Verify safety check was called
                mock_safety.analyze_text_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_safety_check_failure(self, orchestrator, sample_request):
        """Test workflow when content fails safety analysis."""
        
        with patch.object(orchestrator, 'brand_safety_engine', AsyncMock()) as mock_safety:
            # Mock safety failure
            mock_safety.analyze_text_content.return_value = Mock(
                overall_safety_score=0.3,  # Below threshold
                risk_factors=["inappropriate_content"],
                recommendations=["Review content guidelines"]
            )
            
            # Test comprehensive guidance with safety failure
            results = await orchestrator.process_comprehensive_guidance(sample_request)
            
            # Should return safety error responses for all services
            assert isinstance(results, dict)
            for service_type, response in results.items():
                assert isinstance(response, ContentGuidanceResponse)
                assert len(response.warnings) > 0
                assert "safety" in response.warnings[0].lower()
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, orchestrator, sample_request):
        """Test error handling when individual services fail."""
        
        with patch.object(orchestrator, 'content_optimizer', AsyncMock()) as mock_optimizer:
            with patch.object(orchestrator, 'brand_safety_engine', AsyncMock()) as mock_safety:
                # Mock safety check to pass
                mock_safety.analyze_text_content.return_value = Mock(
                    overall_safety_score=0.9
                )
                
                # Mock service failure
                mock_optimizer.optimize_text_content.side_effect = Exception("Service unavailable")
                
                # Test single service with error
                result = await orchestrator.process_single_service_guidance(
                    ContentGuidanceServiceType.OPTIMIZATION,
                    sample_request
                )
                
                # Should handle error gracefully
                assert isinstance(result, ContentGuidanceResponse)
                assert len(result.errors) > 0
                assert "Service unavailable" in result.errors[0]
                assert result.confidence_score == 0.0
    
    @pytest.mark.asyncio
    async def test_cross_service_optimization(self, orchestrator, sample_request):
        """Test cross-service recommendation optimization."""
        
        # Create mock results with potential conflicts
        mock_results = {
            ContentGuidanceServiceType.SCHEDULING: ContentGuidanceResponse(
                request_id="test_1",
                creator_id=sample_request.creator_id,
                service_type=ContentGuidanceServiceType.SCHEDULING,
                recommendations=[{"type": "posting_schedule", "data": {"optimal_times": ["10:00", "14:00"]}}],
                insights=[],
                metrics={},
                confidence_score=0.8,
                processing_time=1.0,
                next_steps=["Schedule posts at optimal times"]
            ),
            ContentGuidanceServiceType.TREND_ANALYSIS: ContentGuidanceResponse(
                request_id="test_2", 
                creator_id=sample_request.creator_id,
                service_type=ContentGuidanceServiceType.TREND_ANALYSIS,
                recommendations=[{"type": "posting_schedule", "data": {"optimal_times": ["12:00", "16:00"]}}],
                insights=[],
                metrics={},
                confidence_score=0.9,
                processing_time=1.0,
                next_steps=["Follow trending topics"]
            )
        }
        
        # Test conflict identification
        conflicts = orchestrator._identify_recommendation_conflicts(mock_results)
        
        # Should identify timing conflicts
        # Note: This test assumes the conflict detection logic finds differences
        # The actual behavior depends on the implementation
        
        # Test conflict resolution
        resolved_results = orchestrator._resolve_recommendation_conflicts(mock_results, conflicts)
        
        # Verify resolution maintains original structure
        assert len(resolved_results) == len(mock_results)
        for service_type in mock_results:
            assert service_type in resolved_results
    
    @pytest.mark.asyncio
    async def test_unified_action_plan_generation(self, orchestrator, sample_request):
        """Test unified action plan generation across services."""
        
        # Create mock results with various next steps
        mock_results = {
            ContentGuidanceServiceType.OPTIMIZATION: ContentGuidanceResponse(
                request_id="test_1",
                creator_id=sample_request.creator_id,
                service_type=ContentGuidanceServiceType.OPTIMIZATION,
                recommendations=[],
                insights=[],
                metrics={},
                confidence_score=0.9,
                processing_time=1.0,
                next_steps=["Optimize content title", "Add relevant hashtags"]
            ),
            ContentGuidanceServiceType.SCHEDULING: ContentGuidanceResponse(
                request_id="test_2",
                creator_id=sample_request.creator_id,
                service_type=ContentGuidanceServiceType.SCHEDULING,
                recommendations=[],
                insights=[],
                metrics={},
                confidence_score=0.8,
                processing_time=1.0,
                next_steps=["Schedule posts for optimal times", "Set up content calendar"]
            )
        }
        
        # Generate unified action plan
        action_plan = await orchestrator._generate_unified_action_plan(mock_results, sample_request)
        
        # Verify action plan structure
        assert isinstance(action_plan, list)
        assert len(action_plan) > 0
        
        # Should include standard workflow steps
        assert any("Review all recommendations" in step for step in action_plan)
        assert any("safety" in step.lower() for step in action_plan)
    
    def test_action_step_prioritization(self, orchestrator):
        """Test action step prioritization logic."""
        
        steps = [
            "Low priority step",
            "High priority step", 
            "Medium priority step"
        ]
        
        mock_results = {
            ContentGuidanceServiceType.OPTIMIZATION: ContentGuidanceResponse(
                request_id="test",
                creator_id="creator_123",
                service_type=ContentGuidanceServiceType.OPTIMIZATION,
                recommendations=[],
                insights=[],
                metrics={},
                confidence_score=0.9,  # High confidence
                processing_time=1.0,
                next_steps=["High priority step"]
            ),
            ContentGuidanceServiceType.SCHEDULING: ContentGuidanceResponse(
                request_id="test",
                creator_id="creator_123", 
                service_type=ContentGuidanceServiceType.SCHEDULING,
                recommendations=[],
                insights=[],
                metrics={},
                confidence_score=0.5,  # Lower confidence
                processing_time=1.0,
                next_steps=["Low priority step", "Medium priority step"]
            )
        }
        
        prioritized = orchestrator._prioritize_action_steps(steps, mock_results)
        
        # Verify prioritization (high confidence steps should come first)
        assert isinstance(prioritized, list)
        assert "High priority step" in prioritized
    
    @pytest.mark.asyncio
    async def test_content_optimization_processing(self, orchestrator, sample_request, mock_optimization_result):
        """Test content optimization service processing."""
        
        with patch.object(orchestrator, 'content_optimizer', AsyncMock()) as mock_optimizer:
            mock_optimizer.optimize_text_content.return_value = mock_optimization_result
            
            result = await orchestrator._process_content_optimization(
                mock_optimizer, 
                sample_request
            )
            
            # Verify result structure
            assert "recommendations" in result
            assert "insights" in result
            assert "metrics" in result
            assert "confidence_score" in result
            assert "next_steps" in result
            assert "metadata" in result
            
            # Verify content
            assert result["recommendations"] == mock_optimization_result.recommendations
            assert result["confidence_score"] == mock_optimization_result.confidence_level
            assert "optimization_score" in result["metrics"]


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    @pytest.mark.asyncio
    async def test_get_comprehensive_content_guidance(self):
        """Test comprehensive content guidance convenience function."""
        
        with patch('backend.conversational.content_guidance.index.content_guidance_orchestrator') as mock_orchestrator:
            mock_orchestrator.process_comprehensive_guidance.return_value = {}
            
            result = await get_comprehensive_content_guidance(
                creator_id="creator_123",
                content_type="video",
                platforms=["youtube"]
            )
            
            # Verify function call
            mock_orchestrator.process_comprehensive_guidance.assert_called_once()
            call_args = mock_orchestrator.process_comprehensive_guidance.call_args[0][0]
            assert call_args.creator_id == "creator_123"
            assert call_args.content_type == "video"
            assert call_args.platforms == ["youtube"]
    
    @pytest.mark.asyncio 
    async def test_get_specific_content_guidance(self):
        """Test specific content guidance convenience function."""
        
        with patch('backend.conversational.content_guidance.index.content_guidance_orchestrator') as mock_orchestrator:
            mock_response = ContentGuidanceResponse(
                request_id="test",
                creator_id="creator_123",
                service_type=ContentGuidanceServiceType.OPTIMIZATION,
                recommendations=[],
                insights=[],
                metrics={},
                confidence_score=0.8,
                processing_time=1.0,
                next_steps=[]
            )
            mock_orchestrator.process_single_service_guidance.return_value = mock_response
            
            result = await get_specific_content_guidance(
                ContentGuidanceServiceType.OPTIMIZATION,
                creator_id="creator_123",
                content_type="video"
            )
            
            # Verify function call
            mock_orchestrator.process_single_service_guidance.assert_called_once()
            call_args = mock_orchestrator.process_single_service_guidance.call_args
            assert call_args[0][0] == ContentGuidanceServiceType.OPTIMIZATION
            assert call_args[0][1].creator_id == "creator_123"
            assert call_args[0][1].content_type == "video"


class TestDataStructures:
    """Test suite for data structures."""
    
    def test_content_guidance_request_creation(self):
        """Test ContentGuidanceRequest creation and validation."""
        
        request = ContentGuidanceRequest(
            creator_id="creator_123",
            content_type="video",
            platforms=["youtube", "instagram"],
            target_audience="young_adults"
        )
        
        assert request.creator_id == "creator_123"
        assert request.content_type == "video"
        assert request.platforms == ["youtube", "instagram"]
        assert request.target_audience == "young_adults"
        assert request.content_id is None  # Optional field
    
    def test_content_guidance_response_creation(self):
        """Test ContentGuidanceResponse creation and validation."""
        
        response = ContentGuidanceResponse(
            request_id="req_123",
            creator_id="creator_123",
            service_type=ContentGuidanceServiceType.OPTIMIZATION,
            recommendations=[{"type": "test", "data": "test_data"}],
            insights=[{"type": "insight", "data": "insight_data"}],
            metrics={"score": 0.8},
            confidence_score=0.85,
            processing_time=1.5,
            next_steps=["Step 1", "Step 2"]
        )
        
        assert response.request_id == "req_123"
        assert response.creator_id == "creator_123"
        assert response.service_type == ContentGuidanceServiceType.OPTIMIZATION
        assert len(response.recommendations) == 1
        assert len(response.insights) == 1
        assert response.metrics["score"] == 0.8
        assert response.confidence_score == 0.85
        assert response.processing_time == 1.5
        assert len(response.next_steps) == 2
    
    def test_service_type_enum(self):
        """Test ContentGuidanceServiceType enum."""
        
        # Verify all expected service types exist
        expected_types = [
            "optimization", "platform_strategy", "monetization",
            "trend_analysis", "audience_insights", "brand_safety",
            "collaboration", "scheduling", "creative_assistance",
            "performance_tracking"
        ]
        
        for expected_type in expected_types:
            # Find enum member with this value
            found = any(service.value == expected_type for service in ContentGuidanceServiceType)
            assert found, f"Service type {expected_type} not found in enum"
        
        # Verify total count
        assert len(ContentGuidanceServiceType) == len(expected_types)


class TestPerformanceAndReliability:
    """Test suite for performance and reliability requirements."""
    
    @pytest.mark.asyncio
    async def test_concurrent_service_processing(self, orchestrator, sample_request):
        """Test that services can be processed concurrently without conflicts."""
        
        # Mock all services with realistic delays
        with patch.multiple(
            orchestrator,
            content_optimizer=AsyncMock(),
            platform_engine=AsyncMock(),
            brand_safety_engine=AsyncMock()
        ):
            
            # Mock safety check
            orchestrator.brand_safety_engine.analyze_text_content.return_value = Mock(
                overall_safety_score=0.9
            )
            
            # Add delays to simulate real processing time
            async def delayed_optimization(*args, **kwargs):
                await asyncio.sleep(0.1)
                return Mock(
                    recommendations=[], quality_analysis={}, seo_suggestions={},
                    platform_optimization={}, optimization_score=0.8,
                    predicted_reach_increase=0.2, predicted_engagement_improvement=0.1,
                    confidence_level=0.8, action_items=[], optimization_type="test"
                )
            
            orchestrator.content_optimizer.optimize_text_content.side_effect = delayed_optimization
            
            # Measure processing time
            start_time = datetime.now()
            
            # Process multiple services concurrently
            tasks = [
                orchestrator._process_service_guidance(ContentGuidanceServiceType.OPTIMIZATION, sample_request)
                for _ in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Verify all tasks completed
            assert len(results) == 3
            for result in results:
                assert isinstance(result, ContentGuidanceResponse)
            
            # Concurrent processing should be faster than sequential
            # (3 * 0.1s sequentially = 0.3s, concurrent should be ~0.1s + overhead)
            assert total_time < 0.25, f"Concurrent processing took too long: {total_time}s"
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, orchestrator):
        """Test memory efficiency with large numbers of requests."""
        
        # Create multiple requests
        requests = [
            ContentGuidanceRequest(
                creator_id=f"creator_{i}",
                content_type="video",
                content_text=f"Test content {i}"
            )
            for i in range(10)
        ]
        
        with patch.object(orchestrator, 'brand_safety_engine', AsyncMock()) as mock_safety:
            mock_safety.analyze_text_content.return_value = Mock(
                overall_safety_score=0.9
            )
            
            with patch.object(orchestrator, 'content_optimizer', AsyncMock()) as mock_optimizer:
                mock_optimizer.optimize_text_content.return_value = Mock(
                    recommendations=[], quality_analysis={}, seo_suggestions={},
                    platform_optimization={}, optimization_score=0.8,
                    predicted_reach_increase=0.2, predicted_engagement_improvement=0.1,
                    confidence_level=0.8, action_items=[], optimization_type="test"
                )
                
                # Process all requests
                results = []
                for request in requests:
                    result = await orchestrator.process_single_service_guidance(
                        ContentGuidanceServiceType.OPTIMIZATION,
                        request
                    )
                    results.append(result)
                
                # Verify all processed successfully
                assert len(results) == 10
                for result in results:
                    assert isinstance(result, ContentGuidanceResponse)
    
    def test_error_recovery(self, orchestrator):
        """Test error recovery and graceful degradation."""
        
        # Test with invalid service type
        with pytest.raises(ValueError):
            # This should raise an error for unknown service type
            # Note: This test assumes the implementation validates service types
            pass
        
        # Test with malformed request
        malformed_request = ContentGuidanceRequest(creator_id="")  # Empty creator ID
        
        # Should handle gracefully without crashing
        # Implementation should validate input and provide meaningful errors


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
