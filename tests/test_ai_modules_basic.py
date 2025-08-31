"""
Simple AI Module Tests - Testing our created AI modules
========================================================

Basic tests to verify that the AI modules we've created are working correctly.
This provides a foundation to build upon.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from ai.nlp.core import AdvancedNLPEngine, NLPTask, NLPResult, NLPTaskType
from ai.recommendation.core import RecommendationEngine, RecommendationConfig, RecommendationRequest
from ai.recommendation.models import Platform, ContentType, CreatorProfile
from ai.recommendation.exceptions import RecommendationError, ValidationError


class TestNLPCore:
    """Test the NLP core module."""
    
    @pytest.mark.asyncio
    async def test_nlp_engine_initialization(self):
        """Test NLP engine can be initialized."""
        engine = AdvancedNLPEngine()
        assert not engine.is_initialized
        
        success = await engine.initialize()
        assert success
        assert engine.is_initialized
    
    @pytest.mark.asyncio
    async def test_nlp_task_processing(self):
        """Test NLP task processing."""
        engine = AdvancedNLPEngine()
        await engine.initialize()
        
        task = NLPTask(
            task_id="test_1",
            task_type=NLPTaskType.SENTIMENT_ANALYSIS,
            input_text="This is a great product! I love it."
        )
        
        result = await engine.process_task(task)
        
        assert isinstance(result, NLPResult)
        assert result.task_id == "test_1"
        assert result.task_type == NLPTaskType.SENTIMENT_ANALYSIS
        assert result.success
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_nlp_batch_processing(self):
        """Test NLP batch processing."""
        engine = AdvancedNLPEngine()
        await engine.initialize()
        
        tasks = [
            NLPTask(
                task_id=f"batch_{i}",
                task_type=NLPTaskType.LANGUAGE_DETECTION,
                input_text=f"Sample text {i}"
            )
            for i in range(3)
        ]
        
        results = await engine.process_batch(tasks)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, NLPResult)
            assert result.success


class TestRecommendationCore:
    """Test the recommendation core module."""
    
    @pytest.mark.asyncio
    async def test_recommendation_engine_initialization(self):
        """Test recommendation engine initialization."""
        config = RecommendationConfig()
        engine = RecommendationEngine(config)
        
        assert not engine.is_initialized
        
        success = await engine.initialize()
        assert success
        assert engine.is_initialized
    
    @pytest.mark.asyncio
    async def test_content_recommendations(self):
        """Test content recommendation generation."""
        engine = RecommendationEngine()
        await engine.initialize()
        
        request = RecommendationRequest(
            user_id="test_user_123",
            request_type="content",
            limit=5
        )
        
        response = await engine.get_content_recommendations(request)
        
        assert response.request_id
        assert len(response.recommendations) <= 5
        assert len(response.confidence_scores) == len(response.recommendations)
        assert response.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_filtering(self):
        """Test recommendation filtering."""
        config = RecommendationConfig(min_confidence_threshold=0.7)
        engine = RecommendationEngine(config)
        await engine.initialize()
        
        request = RecommendationRequest(
            user_id="filter_test",
            platform_filter=[Platform.INSTAGRAM, Platform.YOUTUBE]
        )
        
        response = await engine.get_content_recommendations(request)
        
        # Should filter by confidence and platform
        for score in response.confidence_scores:
            assert score >= config.min_confidence_threshold
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test engine health check."""
        engine = RecommendationEngine()
        await engine.initialize()
        
        health = await engine.health_check()
        
        assert health['status'] == 'healthy'
        assert health['initialized'] == True
        assert health['models_loaded'] > 0


class TestRecommendationModels:
    """Test the recommendation models."""
    
    def test_creator_profile_creation(self):
        """Test creator profile creation."""
        profile = CreatorProfile(
            creator_id="creator_123",
            username="test_creator",
            display_name="Test Creator",
            platforms=[Platform.INSTAGRAM, Platform.YOUTUBE],
            content_types=[ContentType.VIDEO, ContentType.IMAGE]
        )
        
        assert profile.creator_id == "creator_123"
        assert profile.username == "test_creator"
        assert len(profile.platforms) == 2
        assert Platform.INSTAGRAM in profile.platforms
    
    def test_creator_profile_metrics(self):
        """Test creator profile metrics."""
        profile = CreatorProfile(
            creator_id="metrics_test",
            username="metrics_creator",
            display_name="Metrics Creator",
            follower_count={
                Platform.INSTAGRAM: 10000,
                Platform.YOUTUBE: 5000
            },
            engagement_rates={
                Platform.INSTAGRAM: 0.05,
                Platform.YOUTUBE: 0.03
            }
        )
        
        total_followers = profile.get_total_followers()
        avg_engagement = profile.get_average_engagement_rate()
        
        assert total_followers == 15000
        assert avg_engagement == 0.04


class TestRecommendationExceptions:
    """Test the recommendation exceptions."""
    
    def test_validation_error(self):
        """Test validation error handling."""
        from ai.recommendation.exceptions import validate_creator_profile
        
        # Test missing required field
        with pytest.raises(ValidationError) as exc_info:
            validate_creator_profile({})
        
        assert "Missing required field" in str(exc_info.value)
        assert exc_info.value.field_name == "creator_id"
    
    def test_recommendation_scores_validation(self):
        """Test recommendation scores validation."""
        from ai.recommendation.exceptions import validate_recommendation_scores
        
        # Valid scores should pass
        valid_scores = [0.9, 0.8, 0.7, 0.6]
        assert validate_recommendation_scores(valid_scores)
        
        # Invalid scores should fail
        with pytest.raises(ValidationError):
            validate_recommendation_scores([1.5, 0.8])  # Score > 1.0
        
        with pytest.raises(ValidationError):
            validate_recommendation_scores([-0.1, 0.8])  # Score < 0.0
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        from ai.recommendation.exceptions import sanitize_user_input
        
        # Clean input should pass through
        clean_input = "This is clean input"
        result = sanitize_user_input(clean_input)
        assert result == clean_input
        
        # Dangerous characters should be removed
        dangerous_input = "Hello <script>alert('xss')</script> World"
        result = sanitize_user_input(dangerous_input)
        assert "<script>" not in result
        assert "Hello" in result
        assert "World" in result


@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI modules."""
    
    @pytest.mark.asyncio
    async def test_nlp_recommendation_integration(self):
        """Test integration between NLP and recommendation engines."""
        # Initialize both engines
        nlp_engine = AdvancedNLPEngine()
        rec_engine = RecommendationEngine()
        
        await nlp_engine.initialize()
        await rec_engine.initialize()
        
        # Process some text with NLP
        nlp_task = NLPTask(
            task_id="integration_test",
            task_type=NLPTaskType.TEXT_CLASSIFICATION,
            input_text="I'm looking for fitness content and workout videos"
        )
        
        nlp_result = await nlp_engine.process_task(nlp_task)
        assert nlp_result.success
        
        # Use NLP result to enhance recommendation request
        rec_request = RecommendationRequest(
            user_id="integration_user",
            parameters={"nlp_insights": nlp_result.result},
            content_type_filter=[ContentType.VIDEO]
        )
        
        rec_response = await rec_engine.get_content_recommendations(rec_request)
        assert len(rec_response.recommendations) > 0
        
        # Verify both engines maintain their state
        nlp_stats = nlp_engine.get_stats()
        rec_analytics = rec_engine.get_analytics()
        
        assert nlp_stats['tasks_processed'] >= 1
        assert rec_analytics['total_requests'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])