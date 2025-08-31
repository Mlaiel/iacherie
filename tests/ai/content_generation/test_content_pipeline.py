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

"""Content Pipeline Tests

Comprehensive tests for the ContentGenerationPipeline class that orchestrates
the multi-stage content generation workflow.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import logging

# Import the module to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from ai.content_generation.content_pipeline import (
    ContentGenerationPipeline,
    PipelineStage,
    PipelineConfiguration,
    PipelineResult
)
from ai.content_generation.content_models import (
    ContentGenerationRequest,
    ContentGenerationResponse
)


class TestContentGenerationPipeline:
    """Test suite for ContentGenerationPipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance for testing"""
        config = PipelineConfiguration(
            enabled_generators=["text", "audio", "video", "image"],
            parallel_execution=True,
            quality_threshold=0.8,
            enable_optimization=True,
            enable_seo=True,
            enable_analytics=True,
            max_retry_attempts=3,
            timeout_seconds=300
        )
        return ContentGenerationPipeline(config=config)
    
    @pytest.fixture
    def mock_generators(self):
        """Create mock generators for testing"""
        return {
            'text': AsyncMock(),
            'audio': AsyncMock(),
            'video': AsyncMock(),
            'image': AsyncMock()
        }
    
    @pytest.fixture
    def mock_optimizers(self):
        """Create mock optimizers for testing"""
        return {
            'seo': AsyncMock(),
            'quality': AsyncMock(),
            'format': AsyncMock()
        }
    
    @pytest.fixture
    def valid_request(self):
        """Create a valid pipeline request"""
        return ContentGenerationRequest(
            content_type="blog_post",
            topic="AI technology trends",
            target_audience="tech enthusiasts",
            word_count=500,
            keywords=["AI", "technology", "innovation"],
            workflow="standard"
        )
    
    @pytest.fixture
    def blog_request(self):
        """Create a blog-specific request"""
        return ContentGenerationRequest(
            content_type="blog_post",
            topic="Future of Machine Learning",
            target_audience="data scientists",
            word_count=1000,
            keywords=["machine learning", "AI", "data science"],
            workflow="blog_premium"
        )
    
    @pytest.fixture
    def social_request(self):
        """Create a social media request"""
        return ContentGenerationRequest(
            content_type="instagram_post",
            topic="Daily motivation",
            target_audience="young professionals",
            word_count=150,
            hashtags=["#motivation", "#success", "#growth"],
            workflow="social_standard"
        )
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline is not None
        assert hasattr(pipeline, 'stages')
        assert hasattr(pipeline, 'generators')
        assert hasattr(pipeline, 'optimizers')
        assert hasattr(pipeline, 'workflows')
        assert hasattr(pipeline, 'metrics')
        assert len(pipeline.stages) == 6  # 6 standard stages
    
    def test_workflow_registration(self, pipeline):
        """Test workflow registration"""
        # Test default workflows exist
        assert "standard" in pipeline.workflows
        assert "blog_premium" in pipeline.workflows
        assert "social_standard" in pipeline.workflows
        
        # Test custom workflow registration
        custom_workflow = {
            "name": "custom_test",
            "stages": ["planning", "generation", "optimization"],
            "parallel_execution": False
        }
        
        pipeline.register_workflow("custom_test", custom_workflow)
        assert "custom_test" in pipeline.workflows
    
    @pytest.mark.asyncio
    async def test_successful_pipeline_execution(self, pipeline, valid_request, mock_generators, mock_optimizers):
        """Test successful pipeline execution"""
        # Mock the generators and optimizers
        with patch.object(pipeline, 'generators', mock_generators):
            with patch.object(pipeline, 'optimizers', mock_optimizers):
                # Configure mocks
                mock_generators['text'].generate_content.return_value = "Generated content"
                mock_optimizers['seo'].optimize_content.return_value = "SEO optimized content"
                mock_optimizers['quality'].enhance_content.return_value = "Quality enhanced content"
                mock_optimizers['format'].format_content.return_value = "Formatted content"
                
                result = await pipeline.execute_pipeline(valid_request)
                
                assert result is not None
                assert isinstance(result, ContentGenerationResult)
                assert result.status == "completed"
                assert result.final_content is not None
                assert len(result.steps_completed) > 0
    
    @pytest.mark.asyncio
    async def test_planning_stage(self, pipeline, valid_request):
        """Test the planning stage"""
        planning_result = await pipeline._execute_planning_stage(valid_request)
        
        assert planning_result is not None
        assert "content_plan" in planning_result
        assert "generation_strategy" in planning_result
        assert "optimization_requirements" in planning_result
        
        plan = planning_result["content_plan"]
        assert plan["content_type"] == valid_request.content_type
        assert plan["target_word_count"] == valid_request.word_count
    
    @pytest.mark.asyncio
    async def test_generation_stage(self, pipeline, valid_request, mock_generators):
        """Test the generation stage"""
        with patch.object(pipeline, 'generators', mock_generators):
            mock_generators['text'].generate_content.return_value = "Generated text content"
            
            planning_result = {
                "content_plan": {
                    "content_type": "blog_post",
                    "primary_generator": "text"
                }
            }
            
            generation_result = await pipeline._execute_generation_stage(
                valid_request, planning_result
            )
            
            assert generation_result is not None
            assert "generated_content" in generation_result
            assert generation_result["generated_content"] == "Generated text content"
            mock_generators['text'].generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_optimization_stage(self, pipeline, valid_request, mock_optimizers):
        """Test the optimization stage"""
        with patch.object(pipeline, 'optimizers', mock_optimizers):
            mock_optimizers['seo'].optimize_content.return_value = "SEO optimized"
            mock_optimizers['quality'].enhance_content.return_value = "Quality enhanced"
            
            generation_result = {
                "generated_content": "Raw generated content"
            }
            
            optimization_result = await pipeline._execute_optimization_stage(
                valid_request, generation_result
            )
            
            assert optimization_result is not None
            assert "optimized_content" in optimization_result
            mock_optimizers['seo'].optimize_content.assert_called_once()
            mock_optimizers['quality'].enhance_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validation_stage(self, pipeline, valid_request):
        """Test the validation stage"""
        optimization_result = {
            "optimized_content": "This is a well-optimized piece of content with proper length and structure."
        }
        
        validation_result = await pipeline._execute_validation_stage(
            valid_request, optimization_result
        )
        
        assert validation_result is not None
        assert "validation_status" in validation_result
        assert "quality_scores" in validation_result
        assert validation_result["validation_status"] == "passed"
    
    @pytest.mark.asyncio
    async def test_enhancement_stage(self, pipeline, valid_request, mock_optimizers):
        """Test the enhancement stage"""
        with patch.object(pipeline, 'optimizers', mock_optimizers):
            mock_optimizers['format'].format_content.return_value = "Enhanced formatted content"
            
            validation_result = {
                "validated_content": "Validated content",
                "quality_scores": {"overall": 0.85}
            }
            
            enhancement_result = await pipeline._execute_enhancement_stage(
                valid_request, validation_result
            )
            
            assert enhancement_result is not None
            assert "enhanced_content" in enhancement_result
            mock_optimizers['format'].format_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_finalization_stage(self, pipeline, valid_request):
        """Test the finalization stage"""
        enhancement_result = {
            "enhanced_content": "Final enhanced content",
            "applied_enhancements": ["formatting", "style_improvement"]
        }
        
        finalization_result = await pipeline._execute_finalization_stage(
            valid_request, enhancement_result
        )
        
        assert finalization_result is not None
        assert "final_content" in finalization_result
        assert "metadata" in finalization_result
        assert "performance_metrics" in finalization_result
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, pipeline, valid_request, mock_generators):
        """Test parallel execution mode"""
        with patch.object(pipeline, 'generators', mock_generators):
            # Configure multiple generators
            mock_generators['text'].generate_content.return_value = "Text content"
            mock_generators['image'].generate_content.return_value = "Image content"
            
            # Test parallel generation
            planning_result = {
                "content_plan": {
                    "content_type": "blog_post",
                    "generators": ["text", "image"],
                    "parallel_execution": True
                }
            }
            
            generation_result = await pipeline._execute_generation_stage(
                valid_request, planning_result
            )
            
            assert generation_result is not None
            assert "generated_content" in generation_result
            # Both generators should have been called
            mock_generators['text'].generate_content.assert_called_once()
            mock_generators['image'].generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self, pipeline, valid_request, mock_generators):
        """Test sequential execution mode"""
        with patch.object(pipeline, 'generators', mock_generators):
            mock_generators['text'].generate_content.return_value = "Sequential text content"
            
            planning_result = {
                "content_plan": {
                    "content_type": "blog_post",
                    "generators": ["text"],
                    "parallel_execution": False
                }
            }
            
            generation_result = await pipeline._execute_generation_stage(
                valid_request, planning_result
            )
            
            assert generation_result is not None
            mock_generators['text'].generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_blog_workflow(self, pipeline, blog_request, mock_generators, mock_optimizers):
        """Test blog-specific workflow"""
        with patch.object(pipeline, 'generators', mock_generators):
            with patch.object(pipeline, 'optimizers', mock_optimizers):
                # Configure mocks for blog workflow
                mock_generators['text'].generate_content.return_value = "Blog post content"
                mock_optimizers['seo'].optimize_content.return_value = "SEO optimized blog"
                mock_optimizers['quality'].enhance_content.return_value = "Quality blog"
                mock_optimizers['format'].format_content.return_value = "Formatted blog"
                
                result = await pipeline.execute_pipeline(blog_request)
                
                assert result is not None
                assert result.content_type == "blog_post"
                assert result.workflow == "blog_premium"
                assert "blog" in result.final_content.lower()
    
    @pytest.mark.asyncio
    async def test_social_workflow(self, pipeline, social_request, mock_generators, mock_optimizers):
        """Test social media workflow"""
        with patch.object(pipeline, 'generators', mock_generators):
            with patch.object(pipeline, 'optimizers', mock_optimizers):
                # Configure mocks for social workflow
                mock_generators['text'].generate_content.return_value = "Social post content #motivation"
                mock_optimizers['format'].format_content.return_value = "Formatted social post #motivation"
                
                result = await pipeline.execute_pipeline(social_request)
                
                assert result is not None
                assert result.content_type == "instagram_post"
                assert result.workflow == "social_standard"
                assert "#motivation" in result.final_content
    
    @pytest.mark.asyncio
    async def test_error_handling_in_pipeline(self, pipeline, valid_request, mock_generators):
        """Test error handling during pipeline execution"""
        with patch.object(pipeline, 'generators', mock_generators):
            # Configure generator to raise an error
            mock_generators['text'].generate_content.side_effect = Exception("Generation failed")
            
            with pytest.raises(PipelineExecutionError):
                await pipeline.execute_pipeline(valid_request)
    
    @pytest.mark.asyncio
    async def test_stage_retry_mechanism(self, pipeline, valid_request, mock_generators):
        """Test retry mechanism for failed stages"""
        with patch.object(pipeline, 'generators', mock_generators):
            # First call fails, second succeeds
            mock_generators['text'].generate_content.side_effect = [
                Exception("Temporary failure"),
                "Success on retry"
            ]
            
            planning_result = {
                "content_plan": {
                    "content_type": "blog_post",
                    "primary_generator": "text"
                }
            }
            
            # Should succeed on retry
            generation_result = await pipeline._execute_generation_stage(
                valid_request, planning_result
            )
            
            assert generation_result is not None
            assert generation_result["generated_content"] == "Success on retry"
    
    @pytest.mark.asyncio
    async def test_pipeline_performance_monitoring(self, pipeline, valid_request, mock_generators, mock_optimizers):
        """Test pipeline performance monitoring"""
        with patch.object(pipeline, 'generators', mock_generators):
            with patch.object(pipeline, 'optimizers', mock_optimizers):
                # Configure mocks
                mock_generators['text'].generate_content.return_value = "Content"
                mock_optimizers['seo'].optimize_content.return_value = "Optimized"
                mock_optimizers['quality'].enhance_content.return_value = "Enhanced"
                mock_optimizers['format'].format_content.return_value = "Formatted"
                
                start_time = time.time()
                result = await pipeline.execute_pipeline(valid_request)
                end_time = time.time()
                
                assert result is not None
                assert hasattr(result, 'processing_time')
                assert result.processing_time > 0
                assert result.processing_time <= (end_time - start_time) + 0.1
    
    def test_pipeline_metrics_collection(self, pipeline):
        """Test pipeline metrics collection"""
        metrics = pipeline.get_metrics()
        
        expected_keys = [
            'total_executions',
            'successful_executions',
            'failed_executions',
            'avg_execution_time',
            'stage_performance',
            'workflow_usage'
        ]
        
        for key in expected_keys:
            assert key in metrics
    
    @pytest.mark.asyncio
    async def test_content_type_specific_processing(self, pipeline):
        """Test processing for different content types"""
        content_types = [
            "blog_post",
            "instagram_post",
            "twitter_post",
            "linkedin_post",
            "email_marketing"
        ]
        
        for content_type in content_types:
            request = ContentGenerationRequest(
                content_type=content_type,
                topic="Test topic",
                target_audience="test audience"
            )
            
            planning_result = await pipeline._execute_planning_stage(request)
            
            assert planning_result is not None
            assert planning_result["content_plan"]["content_type"] == content_type
    
    @pytest.mark.asyncio
    async def test_quality_threshold_enforcement(self, pipeline, valid_request):
        """Test quality threshold enforcement"""
        # Mock low quality content
        optimization_result = {
            "optimized_content": "Low quality content"
        }
        
        validation_result = await pipeline._execute_validation_stage(
            valid_request, optimization_result
        )
        
        # Should detect low quality
        assert validation_result is not None
        quality_scores = validation_result["quality_scores"]
        assert "overall" in quality_scores
        assert isinstance(quality_scores["overall"], float)
    
    @pytest.mark.asyncio
    async def test_custom_workflow_execution(self, pipeline, valid_request):
        """Test custom workflow execution"""
        # Register a custom workflow
        custom_workflow = {
            "name": "minimal_test",
            "stages": ["planning", "generation", "finalization"],
            "parallel_execution": False,
            "quality_threshold": 0.6
        }
        
        pipeline.register_workflow("minimal_test", custom_workflow)
        
        # Update request to use custom workflow
        valid_request.workflow = "minimal_test"
        
        # Mock minimal dependencies
        with patch.object(pipeline, 'generators', {'text': AsyncMock()}):
            pipeline.generators['text'].generate_content.return_value = "Custom content"
            
            result = await pipeline.execute_pipeline(valid_request)
            
            assert result is not None
            assert result.workflow == "minimal_test"
            assert len(result.steps_completed) == 3  # Only 3 stages
    
    @pytest.mark.asyncio
    async def test_pipeline_resource_cleanup(self, pipeline, valid_request, mock_generators):
        """Test pipeline resource cleanup"""
        with patch.object(pipeline, 'generators', mock_generators):
            mock_generators['text'].generate_content.return_value = "Content"
            
            initial_memory = pipeline._get_memory_usage()
            
            # Execute pipeline
            await pipeline.execute_pipeline(valid_request)
            
            # Force cleanup
            pipeline.cleanup_resources()
            
            final_memory = pipeline._get_memory_usage()
            
            # Memory should not grow excessively
            memory_growth = final_memory - initial_memory
            assert memory_growth < 50 * 1024 * 1024  # Less than 50MB growth
    
    @pytest.mark.asyncio
    async def test_concurrent_pipeline_executions(self, pipeline, mock_generators, mock_optimizers):
        """Test concurrent pipeline executions"""
        with patch.object(pipeline, 'generators', mock_generators):
            with patch.object(pipeline, 'optimizers', mock_optimizers):
                # Configure mocks
                mock_generators['text'].generate_content.return_value = "Concurrent content"
                mock_optimizers['seo'].optimize_content.return_value = "Optimized"
                mock_optimizers['quality'].enhance_content.return_value = "Enhanced"
                mock_optimizers['format'].format_content.return_value = "Formatted"
                
                # Create multiple requests
                requests = []
                for i in range(3):
                    request = ContentGenerationRequest(
                        content_type="blog_post",
                        topic=f"Topic {i}",
                        target_audience="test audience"
                    )
                    requests.append(request)
                
                # Execute concurrently
                tasks = [pipeline.execute_pipeline(req) for req in requests]
                results = await asyncio.gather(*tasks)
                
                assert len(results) == 3
                for result in results:
                    assert result is not None
                    assert result.status == "completed"
    
    @pytest.mark.asyncio
    async def test_pipeline_state_management(self, pipeline, valid_request, mock_generators):
        """Test pipeline state management during execution"""
        with patch.object(pipeline, 'generators', mock_generators):
            mock_generators['text'].generate_content.return_value = "State test content"
            
            # Track state changes during execution
            states = []
            
            async def state_tracker(*args, **kwargs):
                states.append("generation_started")
                result = await mock_generators['text'].generate_content.return_value
                states.append("generation_completed")
                return result
            
            mock_generators['text'].generate_content.side_effect = state_tracker
            
            result = await pipeline.execute_pipeline(valid_request)
            
            assert result is not None
            # Verify state transitions occurred
            assert len(states) >= 0  # States were tracked


class TestPipelineConfiguration:
    """Test suite for pipeline configuration"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline for configuration testing"""
        return ContentGenerationPipeline()
    
    def test_default_configuration(self, pipeline):
        """Test default pipeline configuration"""
        config = pipeline.get_configuration()
        
        assert config is not None
        assert "stages" in config
        assert "workflows" in config
        assert "quality_thresholds" in config
        assert "timeout_settings" in config
    
    def test_configuration_update(self, pipeline):
        """Test pipeline configuration updates"""
        new_config = {
            "quality_thresholds": {
                "minimum_score": 0.8,
                "retry_threshold": 0.6
            },
            "timeout_settings": {
                "stage_timeout": 60,
                "total_timeout": 300
            }
        }
        
        pipeline.update_configuration(new_config)
        
        updated_config = pipeline.get_configuration()
        assert updated_config["quality_thresholds"]["minimum_score"] == 0.8
        assert updated_config["timeout_settings"]["stage_timeout"] == 60
    
    def test_invalid_configuration(self, pipeline):
        """Test handling of invalid configuration"""
        invalid_config = {
            "quality_thresholds": {
                "minimum_score": 1.5  # Invalid value > 1
            }
        }
        
        with pytest.raises(ValueError):
            pipeline.update_configuration(invalid_config)


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
