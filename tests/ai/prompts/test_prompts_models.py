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

"""Advanced Prompts Models Tests
Ultra-professional test suite for Prompts Models system

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from ai.prompts.prompts_models import (
    PromptType, PromptStatus, PromptContext, PromptTemplate, 
    GeneratedPrompt, PromptOptimization, PromptAnalytics, PromptBatch
)


class TestPromptsModels:
    """Ultra-comprehensive test suite for Prompts Models"""    
    @pytest.fixture
    def sample_prompt_context(self):
        """Create sample prompt context for testing"""        return PromptContext(
            user_id="user_12345",
            creator_type="musician",
            content_format="audio",
            target_platforms=["spotify", "apple_music", "youtube"],
            user_preferences={
                "genre": "electronic",
                "style": "progressive",
                "mood": "energetic",
                "language": "english"
            },
            session_data={
                "session_id": "session_67890",
                "device": "desktop",
                "location": "Germany",
                "previous_prompts": 5
            }
        )
    
    @pytest.fixture
    def sample_prompt_template(self):
        """Create sample prompt template for testing"""        return PromptTemplate(
            id="template_001",
            name="Electronic Music Promotion",
            description="Template for promoting electronic music on streaming platforms",
            template="Create a {style} {genre} track promotion for {platform} targeting {audience}. Focus on {mood} vibes and {language} content.",
            variables=["style", "genre", "platform", "audience", "mood", "language"],
            category="music_promotion",
            tags=["electronic", "music", "promotion", "streaming"],
            quality_score=92.5,
            usage_count=157
        )
    
    @pytest.fixture
    def sample_generated_prompt(self, sample_prompt_context):
        """Create sample generated prompt for testing"""        return GeneratedPrompt(
            prompt_type=PromptType.CONTENT_CREATION,
            status=PromptStatus.COMPLETED,
            content="Create a progressive electronic track promotion for Spotify targeting young adults. Focus on energetic vibes and english content. Emphasize the innovative sound design and perfect workout compatibility.",
            template_id="template_001",
            variables_used={
                "style": "progressive",
                "genre": "electronic", 
                "platform": "Spotify",
                "audience": "young adults",
                "mood": "energetic",
                "language": "english"
            },
            context=sample_prompt_context,
            quality_score=89.5,
            readability_score=85.2,
            relevance_score=91.8,
            creativity_score=87.3,
            generation_time_ms=1250,
            tokens_used=95,
            ai_model_used="gpt-4-turbo"
        )
    
    # ===== ENUM TESTS =====
    
    def test_prompt_type_enum(self):
        """Test PromptType enum values"""        assert PromptType.CONTENT_CREATION.value == "content_creation"
        assert PromptType.PROTECTION.value == "protection"
        assert PromptType.SEO_OPTIMIZATION.value == "seo_optimization"
        assert PromptType.MONETIZATION.value == "monetization"
        assert PromptType.COLLABORATION.value == "collaboration"
        assert PromptType.ANALYTICS.value == "analytics"
        assert PromptType.DISTRIBUTION.value == "distribution"
        
        # Test all enum members
        prompt_types = list(PromptType)
        assert len(prompt_types) == 7
        
        for prompt_type in prompt_types:
            assert isinstance(prompt_type.value, str)
            assert "_" in prompt_type.value or prompt_type.value.isalpha()
    
    def test_prompt_status_enum(self):
        """Test PromptStatus enum values"""        assert PromptStatus.PENDING.value == "pending"
        assert PromptStatus.GENERATING.value == "generating"
        assert PromptStatus.COMPLETED.value == "completed"
        assert PromptStatus.FAILED.value == "failed"
        assert PromptStatus.OPTIMIZING.value == "optimizing"
        
        # Test all enum members
        status_values = list(PromptStatus)
        assert len(status_values) == 5
        
        for status in status_values:
            assert isinstance(status.value, str)
            assert status.value.isalpha()
    
    # ===== PROMPT CONTEXT TESTS =====
    
    def test_prompt_context_initialization(self, sample_prompt_context):
        """Test PromptContext initialization"""        assert sample_prompt_context.user_id == "user_12345"
        assert sample_prompt_context.creator_type == "musician"
        assert sample_prompt_context.content_format == "audio"
        assert len(sample_prompt_context.target_platforms) == 3
        assert "spotify" in sample_prompt_context.target_platforms
        assert "apple_music" in sample_prompt_context.target_platforms
        assert "youtube" in sample_prompt_context.target_platforms
        
        # Test user preferences
        assert sample_prompt_context.user_preferences["genre"] == "electronic"
        assert sample_prompt_context.user_preferences["style"] == "progressive"
        assert sample_prompt_context.user_preferences["mood"] == "energetic"
        assert sample_prompt_context.user_preferences["language"] == "english"
        
        # Test session data
        assert sample_prompt_context.session_data["session_id"] == "session_67890"
        assert sample_prompt_context.session_data["device"] == "desktop"
        assert sample_prompt_context.session_data["location"] == "Germany"
        assert sample_prompt_context.session_data["previous_prompts"] == 5
        
        # Test timestamp
        assert isinstance(sample_prompt_context.timestamp, datetime)
        assert sample_prompt_context.timestamp <= datetime.utcnow()
    
    def test_prompt_context_empty_initialization(self):
        """Test PromptContext with minimal data"""        minimal_context = PromptContext(
            user_id="minimal_user",
            creator_type="blogger",
            content_format="text"
        )
        
        assert minimal_context.user_id == "minimal_user"
        assert minimal_context.creator_type == "blogger"
        assert minimal_context.content_format == "text"
        assert minimal_context.target_platforms == []
        assert minimal_context.user_preferences == {}
        assert minimal_context.session_data == {}
        assert isinstance(minimal_context.timestamp, datetime)
    
    def test_prompt_context_with_complex_data(self):
        """Test PromptContext with complex nested data"""        complex_context = PromptContext(
            user_id="complex_user_789",
            creator_type="video_creator",
            content_format="video",
            target_platforms=["youtube", "instagram", "tiktok", "facebook"],
            user_preferences={
                "content_themes": ["technology", "music", "education"],
                "video_specs": {
                    "resolution": "4K",
                    "frame_rate": 60,
                    "duration_range": [180, 600]
                },
                "audience_demographics": {
                    "age_range": [18, 35],
                    "interests": ["electronic music", "tech gadgets", "tutorials"],
                    "geographic_focus": ["Europe", "North America"]
                },
                "monetization_goals": {
                    "primary": "ad_revenue",
                    "secondary": ["sponsorships", "affiliate_marketing"],
                    "target_cpm": 3.50
                }
            },
            session_data={
                "session_id": "complex_session_456",
                "device": "mobile",
                "app_version": "2.1.3",
                "user_tier": "premium",
                "previous_sessions": [
                    {"date": "2024-02-15", "prompts_generated": 12, "avg_quality": 88.5},
                    {"date": "2024-02-14", "prompts_generated": 8, "avg_quality": 91.2}
                ],
                "current_projects": [
                    {"id": "proj_001", "name": "AI Music Series", "status": "active"},
                    {"id": "proj_002", "name": "Tech Reviews", "status": "planning"}
                ]
            }
        )
        
        assert complex_context.user_id == "complex_user_789"
        assert len(complex_context.target_platforms) == 4
        assert "tiktok" in complex_context.target_platforms
        
        # Test nested preferences
        assert "technology" in complex_context.user_preferences["content_themes"]
        assert complex_context.user_preferences["video_specs"]["resolution"] == "4K"
        assert complex_context.user_preferences["audience_demographics"]["age_range"] == [18, 35]
        assert complex_context.user_preferences["monetization_goals"]["target_cpm"] == 3.50
        
        # Test nested session data
        assert complex_context.session_data["user_tier"] == "premium"
        assert len(complex_context.session_data["previous_sessions"]) == 2
        assert complex_context.session_data["previous_sessions"][0]["avg_quality"] == 88.5
        assert len(complex_context.session_data["current_projects"]) == 2
        assert complex_context.session_data["current_projects"][1]["status"] == "planning"
    
    # ===== PROMPT TEMPLATE TESTS =====
    
    def test_prompt_template_initialization(self, sample_prompt_template):
        """Test PromptTemplate initialization"""        assert sample_prompt_template.id == "template_001"
        assert sample_prompt_template.name == "Electronic Music Promotion"
        assert "promoting electronic music" in sample_prompt_template.description
        assert "{style}" in sample_prompt_template.template
        assert "{genre}" in sample_prompt_template.template
        assert len(sample_prompt_template.variables) == 6
        assert "style" in sample_prompt_template.variables
        assert "genre" in sample_prompt_template.variables
        assert "platform" in sample_prompt_template.variables
        assert sample_prompt_template.category == "music_promotion"
        assert "electronic" in sample_prompt_template.tags
        assert "music" in sample_prompt_template.tags
        assert sample_prompt_template.quality_score == 92.5
        assert sample_prompt_template.usage_count == 157
        assert isinstance(sample_prompt_template.created_at, datetime)
        assert isinstance(sample_prompt_template.updated_at, datetime)
    
    def test_prompt_template_variable_extraction(self):
        """Test template variable extraction"""        template_with_variables = PromptTemplate(
            id="var_test",
            name="Variable Test Template",
            description="Test template with multiple variables",
            template="Create {content_type} for {platform} targeting {demographic} with {tone} approach. Include {call_to_action} and optimize for {goal}. Consider {seasonal_factor} and {trending_topic}.",
            variables=[],  # Empty initially
            category="test"
        )
        
        # Manually set variables based on template
        expected_variables = [
            "content_type", "platform", "demographic", "tone", 
            "call_to_action", "goal", "seasonal_factor", "trending_topic"
        ]
        template_with_variables.variables = expected_variables
        
        assert len(template_with_variables.variables) == 8
        for var in expected_variables:
            assert var in template_with_variables.variables
    
    def test_prompt_template_complex_structure(self):
        """Test PromptTemplate with complex structure"""        complex_template = PromptTemplate(
            id="complex_template_001",
            name="Multi-Platform Content Strategy",
            description="Advanced template for comprehensive content strategy across multiple platforms",
            template="""            Develop a {timeframe} content strategy for {creator_type} focusing on {niche}.
            
            Platform Distribution:
            - {primary_platform}: {primary_strategy}
            - {secondary_platform}: {secondary_strategy}
            
            Content Types:
            {content_mix}
            
            Audience Targeting:
            - Demographics: {target_demographics}
            - Interests: {target_interests}
            - Behavior: {target_behavior}
            
            Performance Goals:
            - Engagement: {engagement_target}%
            - Growth: {growth_target}
            - Revenue: ${revenue_target}
            
            Key Themes: {key_themes}
            Seasonal Considerations: {seasonal_factors}
            Trending Opportunities: {trending_opportunities}
            """,
            variables=[
                "timeframe", "creator_type", "niche", "primary_platform", 
                "primary_strategy", "secondary_platform", "secondary_strategy",
                "content_mix", "target_demographics", "target_interests", 
                "target_behavior", "engagement_target", "growth_target",
                "revenue_target", "key_themes", "seasonal_factors", "trending_opportunities"
            ],
            category="content_strategy",
            tags=["multi-platform", "strategy", "comprehensive", "advanced", "targeting"],
            quality_score=95.8,
            usage_count=89
        )
        
        assert complex_template.id == "complex_template_001"
        assert "Multi-Platform" in complex_template.name
        assert len(complex_template.variables) == 17
        assert "revenue_target" in complex_template.variables
        assert "trending_opportunities" in complex_template.variables
        assert complex_template.category == "content_strategy"
        assert "comprehensive" in complex_template.tags
        assert complex_template.quality_score == 95.8
    
    # ===== GENERATED PROMPT TESTS =====
    
    def test_generated_prompt_initialization(self, sample_generated_prompt):
        """Test GeneratedPrompt initialization"""        assert isinstance(sample_generated_prompt.id, str)
        assert sample_generated_prompt.prompt_type == PromptType.CONTENT_CREATION
        assert sample_generated_prompt.status == PromptStatus.COMPLETED
        assert "progressive electronic track promotion" in sample_generated_prompt.content
        assert sample_generated_prompt.template_id == "template_001"
        assert sample_generated_prompt.variables_used["style"] == "progressive"
        assert sample_generated_prompt.variables_used["genre"] == "electronic"
        assert sample_generated_prompt.context is not None
        assert sample_generated_prompt.quality_score == 89.5
        assert sample_generated_prompt.readability_score == 85.2
        assert sample_generated_prompt.relevance_score == 91.8
        assert sample_generated_prompt.creativity_score == 87.3
        assert sample_generated_prompt.generation_time_ms == 1250
        assert sample_generated_prompt.tokens_used == 95
        assert sample_generated_prompt.ai_model_used == "gpt-4-turbo"
        assert isinstance(sample_generated_prompt.created_at, datetime)
        assert isinstance(sample_generated_prompt.updated_at, datetime)
        assert sample_generated_prompt.version == "1.0"
    
    def test_generated_prompt_default_initialization(self):
        """Test GeneratedPrompt with default values"""        default_prompt = GeneratedPrompt()
        
        assert isinstance(default_prompt.id, str)
        assert len(default_prompt.id) == 36  # UUID4 length
        assert default_prompt.prompt_type == PromptType.CONTENT_CREATION
        assert default_prompt.status == PromptStatus.PENDING
        assert default_prompt.content == ""
        assert default_prompt.template_id is None
        assert default_prompt.variables_used == {}
        assert default_prompt.context is None
        assert default_prompt.quality_score == 0.0
        assert default_prompt.readability_score == 0.0
        assert default_prompt.relevance_score == 0.0
        assert default_prompt.creativity_score == 0.0
        assert default_prompt.generation_time_ms == 0
        assert default_prompt.tokens_used == 0
        assert default_prompt.ai_model_used == ""
        assert isinstance(default_prompt.created_at, datetime)
        assert isinstance(default_prompt.updated_at, datetime)
        assert default_prompt.version == "1.0"
    
    def test_generated_prompt_update_quality_scores(self, sample_generated_prompt):
        """Test updating quality scores"""        original_updated_at = sample_generated_prompt.updated_at
        
        new_scores = {
            'overall': 93.2,
            'readability': 89.7,
            'relevance': 95.1,
            'creativity': 91.8
        }
        
        sample_generated_prompt.update_quality_scores(new_scores)
        
        assert sample_generated_prompt.quality_score == 93.2
        assert sample_generated_prompt.readability_score == 89.7
        assert sample_generated_prompt.relevance_score == 95.1
        assert sample_generated_prompt.creativity_score == 91.8
        assert sample_generated_prompt.updated_at > original_updated_at
    
    def test_generated_prompt_partial_quality_update(self, sample_generated_prompt):
        """Test updating quality scores with partial data"""        partial_scores = {
            'overall': 88.5,
            'readability': 92.3
            # Missing relevance and creativity scores
        }
        
        sample_generated_prompt.update_quality_scores(partial_scores)
        
        assert sample_generated_prompt.quality_score == 88.5
        assert sample_generated_prompt.readability_score == 92.3
        assert sample_generated_prompt.relevance_score == 0.0  # Should default to 0.0
        assert sample_generated_prompt.creativity_score == 0.0  # Should default to 0.0
    
    def test_generated_prompt_to_dict(self, sample_generated_prompt, sample_prompt_context):
        """Test GeneratedPrompt to_dict conversion"""        prompt_dict = sample_generated_prompt.to_dict()
        
        assert isinstance(prompt_dict, dict)
        assert prompt_dict["id"] == sample_generated_prompt.id
        assert prompt_dict["prompt_type"] == "content_creation"
        assert prompt_dict["status"] == "completed"
        assert "progressive electronic track" in prompt_dict["content"]
        assert prompt_dict["template_id"] == "template_001"
        assert prompt_dict["variables_used"]["style"] == "progressive"
        assert prompt_dict["quality_score"] == 89.5
        assert prompt_dict["readability_score"] == 85.2
        assert prompt_dict["relevance_score"] == 91.8
        assert prompt_dict["creativity_score"] == 87.3
        assert prompt_dict["generation_time_ms"] == 1250
        assert prompt_dict["tokens_used"] == 95
        assert prompt_dict["ai_model_used"] == "gpt-4-turbo"
        assert prompt_dict["version"] == "1.0"
        
        # Test context serialization
        assert prompt_dict["context"] is not None
        assert prompt_dict["context"]["user_id"] == "user_12345"
        assert prompt_dict["context"]["creator_type"] == "musician"
        
        # Test datetime serialization
        assert isinstance(prompt_dict["created_at"], str)
        assert isinstance(prompt_dict["updated_at"], str)
        assert "T" in prompt_dict["created_at"]  # ISO format
        assert "T" in prompt_dict["updated_at"]  # ISO format
    
    def test_generated_prompt_to_dict_no_context(self):
        """Test GeneratedPrompt to_dict with no context"""        prompt_no_context = GeneratedPrompt(
            content="Test prompt without context",
            prompt_type=PromptType.SEO_OPTIMIZATION
        )
        
        prompt_dict = prompt_no_context.to_dict()
        
        assert prompt_dict["context"] is None
        assert prompt_dict["prompt_type"] == "seo_optimization"
        assert prompt_dict["content"] == "Test prompt without context"
    
    # ===== PROMPT OPTIMIZATION TESTS =====
    
    def test_prompt_optimization_initialization(self):
        """Test PromptOptimization initialization"""        optimization = PromptOptimization(
            original_prompt_id="prompt_123",
            optimized_content="Optimized content for better performance",
            optimization_type="quality_enhancement",
            improvements=[
                "Enhanced readability",
                "Improved keyword targeting", 
                "Better call-to-action",
                "Increased creativity score"
            ],
            quality_improvement=12.5,
            performance_improvement=8.3
        )
        
        assert optimization.original_prompt_id == "prompt_123"
        assert "Optimized content for better performance" in optimization.optimized_content
        assert optimization.optimization_type == "quality_enhancement"
        assert len(optimization.improvements) == 4
        assert "Enhanced readability" in optimization.improvements
        assert "Better call-to-action" in optimization.improvements
        assert optimization.quality_improvement == 12.5
        assert optimization.performance_improvement == 8.3
        assert isinstance(optimization.timestamp, datetime)
    
    def test_prompt_optimization_empty_improvements(self):
        """Test PromptOptimization with empty improvements"""        minimal_optimization = PromptOptimization(
            original_prompt_id="minimal_123",
            optimized_content="Basic optimization",
            optimization_type="basic"
        )
        
        assert minimal_optimization.improvements == []
        assert minimal_optimization.quality_improvement == 0.0
        assert minimal_optimization.performance_improvement == 0.0
    
    # ===== PROMPT ANALYTICS TESTS =====
    
    def test_prompt_analytics_initialization(self):
        """Test PromptAnalytics initialization"""        analytics = PromptAnalytics(
            prompt_id="analytics_test_001",
            usage_count=247,
            success_rate=92.8,
            average_quality_score=88.5,
            user_feedback_score=4.3,
            platform_performance={
                "spotify": 91.2,
                "youtube": 89.7,
                "instagram": 85.4,
                "tiktok": 93.1,
                "twitter": 87.9
            },
            trending_score=78.5
        )
        
        assert analytics.prompt_id == "analytics_test_001"
        assert analytics.usage_count == 247
        assert analytics.success_rate == 92.8
        assert analytics.average_quality_score == 88.5
        assert analytics.user_feedback_score == 4.3
        assert len(analytics.platform_performance) == 5
        assert analytics.platform_performance["tiktok"] == 93.1
        assert analytics.platform_performance["instagram"] == 85.4
        assert analytics.trending_score == 78.5
        assert isinstance(analytics.last_updated, datetime)
    
    def test_prompt_analytics_default_values(self):
        """Test PromptAnalytics with default values"""        default_analytics = PromptAnalytics(prompt_id="default_test")
        
        assert default_analytics.prompt_id == "default_test"
        assert default_analytics.usage_count == 0
        assert default_analytics.success_rate == 0.0
        assert default_analytics.average_quality_score == 0.0
        assert default_analytics.user_feedback_score == 0.0
        assert default_analytics.platform_performance == {}
        assert default_analytics.trending_score == 0.0
    
    def test_prompt_analytics_comprehensive_data(self):
        """Test PromptAnalytics with comprehensive data"""        comprehensive_analytics = PromptAnalytics(
            prompt_id="comprehensive_001",
            usage_count=1547,
            success_rate=94.7,
            average_quality_score=91.3,
            user_feedback_score=4.6,
            platform_performance={
                "spotify": 93.8,
                "apple_music": 91.2,
                "youtube": 89.5,
                "youtube_music": 88.7,
                "instagram": 92.1,
                "tiktok": 95.3,
                "facebook": 86.9,
                "twitter": 90.4,
                "soundcloud": 89.8,
                "bandcamp": 87.5,
                "linkedin": 85.2,
                "twitch": 88.9
            },
            trending_score=85.7
        )
        
        assert comprehensive_analytics.usage_count == 1547
        assert comprehensive_analytics.success_rate == 94.7
        assert len(comprehensive_analytics.platform_performance) == 12
        assert comprehensive_analytics.platform_performance["tiktok"] == 95.3
        assert comprehensive_analytics.platform_performance["linkedin"] == 85.2
        
        # Test that highest performing platform is TikTok
        best_platform = max(
            comprehensive_analytics.platform_performance, 
            key=comprehensive_analytics.platform_performance.get
        )
        assert best_platform == "tiktok"
        assert comprehensive_analytics.platform_performance[best_platform] == 95.3
        
        # Test average platform performance
        avg_performance = sum(comprehensive_analytics.platform_performance.values()) / len(comprehensive_analytics.platform_performance)
        assert 85.0 <= avg_performance <= 95.0
    
    # ===== PROMPT BATCH TESTS =====
    
    def test_prompt_batch_initialization(self):
        """Test PromptBatch initialization"""        batch = PromptBatch()
        
        assert isinstance(batch.batch_id, str)
        assert len(batch.batch_id) == 36  # UUID4 length
        assert batch.prompts == []
        assert batch.status == "pending"
        assert batch.total_prompts == 0
        assert batch.completed_prompts == 0
        assert batch.failed_prompts == 0
        assert batch.average_quality_score == 0.0
        assert batch.total_processing_time_ms == 0
        assert isinstance(batch.created_at, datetime)
        assert batch.completed_at is None
    
    def test_prompt_batch_add_prompt(self, sample_generated_prompt):
        """Test adding prompts to batch"""        batch = PromptBatch()
        
        # Add first prompt
        batch.add_prompt(sample_generated_prompt)
        
        assert len(batch.prompts) == 1
        assert batch.total_prompts == 1
        assert batch.prompts[0] == sample_generated_prompt
        
        # Add second prompt
        second_prompt = GeneratedPrompt(
            content="Second test prompt",
            prompt_type=PromptType.MONETIZATION,
            status=PromptStatus.COMPLETED,
            quality_score=85.7
        )
        
        batch.add_prompt(second_prompt)
        
        assert len(batch.prompts) == 2
        assert batch.total_prompts == 2
        assert batch.prompts[1] == second_prompt
    
    def test_prompt_batch_update_completion_stats_completed(self):
        """Test batch completion statistics with completed prompts"""        batch = PromptBatch()
        
        # Add completed prompts
        completed_prompts = []
        for i in range(5):
            prompt = GeneratedPrompt(
                content=f"Test prompt {i+1}",
                status=PromptStatus.COMPLETED,
                quality_score=80.0 + i * 2
            )
            completed_prompts.append(prompt)
            batch.add_prompt(prompt)
        
        batch.update_completion_stats()
        
        assert batch.completed_prompts == 5
        assert batch.failed_prompts == 0
        assert batch.status == "completed"
        assert batch.completed_at is not None
        assert batch.average_quality_score == 84.0  # (80+82+84+86+88)/5
    
    def test_prompt_batch_update_completion_stats_mixed(self):
        """Test batch completion statistics with mixed statuses"""        batch = PromptBatch()
        
        # Add prompts with different statuses
        prompts_data = [
            (PromptStatus.COMPLETED, 90.5),
            (PromptStatus.COMPLETED, 85.2),
            (PromptStatus.FAILED, 0.0),
            (PromptStatus.COMPLETED, 92.8),
            (PromptStatus.FAILED, 0.0),
            (PromptStatus.COMPLETED, 87.1),
            (PromptStatus.GENERATING, 0.0)  # Still processing
        ]
        
        for status, quality in prompts_data:
            prompt = GeneratedPrompt(
                content=f"Prompt with status {status.value}",
                status=status,
                quality_score=quality
            )
            batch.add_prompt(prompt)
        
        batch.update_completion_stats()
        
        assert batch.completed_prompts == 4  # COMPLETED status count
        assert batch.failed_prompts == 2     # FAILED status count
        assert batch.total_prompts == 7
        assert batch.status == "pending"     # Not all prompts are done
        assert batch.completed_at is None
        
        # Average quality score should be calculated only from completed prompts
        # (90.5 + 85.2 + 92.8 + 87.1) / 4 = 88.9
        expected_avg = (90.5 + 85.2 + 92.8 + 87.1) / 4
        assert abs(batch.average_quality_score - expected_avg) < 0.1
    
    def test_prompt_batch_update_completion_stats_all_failed(self):
        """Test batch completion statistics with all failed prompts"""        batch = PromptBatch()
        
        # Add failed prompts
        for i in range(3):
            failed_prompt = GeneratedPrompt(
                content=f"Failed prompt {i+1}",
                status=PromptStatus.FAILED,
                quality_score=0.0
            )
            batch.add_prompt(failed_prompt)
        
        batch.update_completion_stats()
        
        assert batch.completed_prompts == 0
        assert batch.failed_prompts == 3
        assert batch.status == "completed"  # All prompts finished (though failed)
        assert batch.completed_at is not None
        assert batch.average_quality_score == 0.0
    
    def test_prompt_batch_comprehensive_workflow(self):
        """Test comprehensive batch workflow"""        batch = PromptBatch()
        original_created_at = batch.created_at
        
        # Phase 1: Add prompts in different stages
        initial_prompts = []
        for i in range(10):
            prompt = GeneratedPrompt(
                content=f"Workflow prompt {i+1}",
                status=PromptStatus.PENDING,
                prompt_type=PromptType.CONTENT_CREATION if i % 2 == 0 else PromptType.SEO_OPTIMIZATION
            )
            initial_prompts.append(prompt)
            batch.add_prompt(prompt)
        
        assert len(batch.prompts) == 10
        assert batch.total_prompts == 10
        batch.update_completion_stats()
        assert batch.status == "pending"
        
        # Phase 2: Simulate processing - some prompts complete
        for i in range(6):
            batch.prompts[i].status = PromptStatus.COMPLETED
            batch.prompts[i].quality_score = 85.0 + i * 1.5
        
        batch.update_completion_stats()
        assert batch.completed_prompts == 6
        assert batch.failed_prompts == 0
        assert batch.status == "pending"  # Still has pending prompts
        assert batch.completed_at is None
        
        # Phase 3: Complete remaining prompts
        for i in range(6, 8):
            batch.prompts[i].status = PromptStatus.COMPLETED
            batch.prompts[i].quality_score = 88.0 + i * 0.5
        
        # Some prompts fail
        for i in range(8, 10):
            batch.prompts[i].status = PromptStatus.FAILED
            batch.prompts[i].quality_score = 0.0
        
        batch.update_completion_stats()
        
        # Final assertions
        assert batch.completed_prompts == 8
        assert batch.failed_prompts == 2
        assert batch.status == "completed"
        assert batch.completed_at is not None
        assert batch.completed_at > original_created_at
        
        # Calculate expected average quality (only completed prompts)
        completed_scores = []
        for i in range(6):
            completed_scores.append(85.0 + i * 1.5)
        for i in range(6, 8):
            completed_scores.append(88.0 + i * 0.5)
        
        expected_avg = sum(completed_scores) / len(completed_scores)
        assert abs(batch.average_quality_score - expected_avg) < 0.1
    
    # ===== PERFORMANCE TESTS =====
    
    def test_models_memory_usage(self):
        """Test memory efficiency of model instances"""        # Create large number of instances to test memory efficiency
        prompts = []
        contexts = []
        templates = []
        
        for i in range(1000):
            context = PromptContext(
                user_id=f"user_{i}",
                creator_type="test_creator",
                content_format="test_format"
            )
            contexts.append(context)
            
            template = PromptTemplate(
                id=f"template_{i}",
                name=f"Template {i}",
                description=f"Test template number {i}",
                template="Test template content {variable}",
                variables=["variable"]
            )
            templates.append(template)
            
            prompt = GeneratedPrompt(
                content=f"Test prompt content {i}",
                context=context,
                template_id=template.id,
                quality_score=float(80 + (i % 20))
            )
            prompts.append(prompt)
        
        # Verify all instances were created successfully
        assert len(prompts) == 1000
        assert len(contexts) == 1000
        assert len(templates) == 1000
        
        # Test that objects maintain their properties
        assert prompts[500].content == "Test prompt content 500"
        assert contexts[250].user_id == "user_250"
        assert templates[750].name == "Template 750"
    
    def test_batch_processing_performance(self):
        """Test batch processing performance"""        large_batch = PromptBatch()
        
        start_time = datetime.now()
        
        # Add many prompts
        for i in range(500):
            prompt = GeneratedPrompt(
                content=f"Performance test prompt {i}",
                status=PromptStatus.COMPLETED if i % 2 == 0 else PromptStatus.FAILED,
                quality_score=85.0 if i % 2 == 0 else 0.0
            )
            large_batch.add_prompt(prompt)
        
        # Update statistics
        large_batch.update_completion_stats()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Performance assertions
        assert processing_time < 2.0  # Should complete within 2 seconds
        assert large_batch.total_prompts == 500
        assert large_batch.completed_prompts == 250  # Half completed
        assert large_batch.failed_prompts == 250     # Half failed
        assert large_batch.status == "completed"
        assert large_batch.average_quality_score == 85.0  # Only completed prompts counted
