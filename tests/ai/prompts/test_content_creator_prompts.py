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
Advanced Content Creator Prompts Tests
Ultra-professional test suite for Content Creator Prompts system

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
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from ai.prompts.content_creator_prompts import (
    ContentCreatorPrompts, ContentCreatorType, ContentFormat, PromptCategory,
    PromptContext, PersonalizationEngine, get_content_creator_prompts,
    create_prompt_context, CONTENT_CREATOR_PROMPTS_REGISTRY
)


class TestContentCreatorPrompts:
    """
Ultra-comprehensive test suite for Content Creator Prompts"""
    
    @pytest.fixture
    async def content_creator_prompts(self):
        """
Create a fresh ContentCreatorPrompts instance for each test"""
        prompts = ContentCreatorPrompts()
        await prompts.initialize()
        yield prompts
        await prompts.cleanup()
    
    @pytest.fixture
    def sample_musician_context(self):
        """
Create sample musician context for testing"""
        return PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.CREATION,
            user_preferences={
                "genre": "electronic",
                "tempo": 128,
                "key": "C minor",
                "mood": "energetic",
                "instruments": ["synthesizer", "drums", "bass"],
                "duration": 240,
                "style": "progressive house"
            },
            platform_requirements={
                "format": "WAV",
                "sample_rate": 48000,
                "bit_depth": 24,
                "channels": "stereo",
                "loudness": -14
            },
            market_trends={
                "trending_genres": ["electronic", "ambient", "lo-fi"],
                "popular_instruments": ["synthesizer", "guitar", "vocals"],
                "seasonal_preferences": "summer_vibes"
            }
        )
    
    @pytest.fixture
    def sample_blogger_context(self):
        """Create sample blogger context for testing"""
        return PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.CREATION,
            user_preferences={
                "niche": "technology",
                "writing_style": "informative",
                "tone": "professional",
                "word_count": 1500,
                "target_audience": "tech professionals",
                "seo_focus": True
            },
            platform_requirements={
                "format": "markdown",
                "seo_optimized": True,
                "meta_description_length": 160,
                "heading_structure": "h1_h2_h3",
                "image_requirements": "featured_image"
            },
            market_trends={
                "trending_topics": ["AI", "blockchain", "cybersecurity"],
                "popular_keywords": ["artificial intelligence", "machine learning"],
                "content_format_trends": ["how-to", "listicles", "case_studies"]
            }
        )
    
    @pytest.fixture
    def sample_photographer_context(self):
        """Create sample photographer context for testing"""
        return PromptContext(
            creator_type=ContentCreatorType.PHOTOGRAPHER,
            content_format=ContentFormat.IMAGE,
            category=PromptCategory.CREATION,
            user_preferences={
                "style": "portrait",
                "lighting": "natural",
                "composition": "rule_of_thirds",
                "color_palette": "warm_tones",
                "post_processing": "minimal",
                "equipment": "DSLR"
            },
            platform_requirements={
                "resolution": "4K",
                "format": "RAW+JPEG",
                "color_space": "sRGB",
                "metadata": "embedded",
                "watermark": True
            },
            market_trends={
                "trending_styles": ["minimalist", "vintage", "cinematic"],
                "popular_subjects": ["lifestyle", "nature", "urban"],
                "platform_preferences": ["instagram", "pinterest", "behance"]
            }
        )
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_content_creator_prompts_initialization(self, content_creator_prompts):
        """Test ContentCreatorPrompts initialization"""
        assert content_creator_prompts is not None
        assert hasattr(content_creator_prompts, 'prompts_cache')
        assert hasattr(content_creator_prompts, 'personalization_engine')
        assert hasattr(content_creator_prompts, 'base_prompts')
        
        assert isinstance(content_creator_prompts.prompts_cache, dict)
        assert isinstance(content_creator_prompts.personalization_engine, PersonalizationEngine)
        assert isinstance(content_creator_prompts.base_prompts, dict)
    
    @pytest.mark.asyncio
    async def test_prompt_registry_loading(self, content_creator_prompts):
        """
Test that prompt registry is properly loaded"""
        registry = CONTENT_CREATOR_PROMPTS_REGISTRY
        assert registry is not None
        assert isinstance(registry, dict)
        
        # Check that all creator types are represented
        for creator_type in ContentCreatorType:
            assert creator_type in registry
            
        # Check that each creator type has all categories
        for creator_type in ContentCreatorType:
            creator_prompts = registry[creator_type]
            for category in PromptCategory:
                assert category in creator_prompts
    
    # ===== MUSICIAN PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_musician_creation_prompts(self, content_creator_prompts, sample_musician_context):
        """
Test musician creation prompts generation"""
        result = await content_creator_prompts.generate_prompt(sample_musician_context)
        
        assert result["success"] is True
        assert "prompt" in result
        assert "metadata" in result
        
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify musical elements are included
        assert "electronic" in prompt.lower()
        assert "128" in prompt or "tempo" in prompt.lower()
        assert "c minor" in prompt.lower()
        assert "energetic" in prompt.lower()
        assert "synthesizer" in prompt.lower()
        assert "240" in prompt or "duration" in prompt.lower()
        
        # Verify technical specifications
        assert "wav" in prompt.lower() or "48000" in prompt or "24-bit" in prompt.lower()
        
        # Verify metadata
        assert metadata["creator_type"] == "musician"
        assert metadata["content_format"] == "audio"
        assert metadata["category"] == "creation"
    
    @pytest.mark.asyncio
    async def test_musician_protection_prompts(self, content_creator_prompts):
        """Test musician protection prompts"""
        protection_context = PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.PROTECTION,
            user_preferences={
                "protection_level": "enterprise",
                "fingerprinting": "spectral",
                "blockchain_protection": True,
                "monitoring_platforms": ["spotify", "youtube", "soundcloud"]
            },
            platform_requirements={
                "watermark": "inaudible",
                "fingerprint_strength": "high",
                "legal_compliance": "DMCA"
            },
            market_trends={}
        )
        
        result = await content_creator_prompts.generate_prompt(protection_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify protection elements
        assert "protection" in prompt.lower()
        assert "fingerprinting" in prompt.lower() or "spectral" in prompt.lower()
        assert "blockchain" in prompt.lower()
        assert "spotify" in prompt.lower() or "youtube" in prompt.lower()
        assert "watermark" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_musician_monetization_prompts(self, content_creator_prompts):
        """Test musician monetization prompts"""
        monetization_context = PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.MONETIZATION,
            user_preferences={
                "revenue_streams": ["streaming", "licensing", "merchandise"],
                "target_markets": ["europe", "north_america"],
                "pricing_strategy": "premium",
                "distribution_channels": ["spotify", "apple_music", "bandcamp"]
            },
            platform_requirements={
                "royalty_tracking": True,
                "sync_licensing": True,
                "publishing_rights": "managed"
            },
            market_trends={
                "growth_segments": ["streaming", "sync_licensing"],
                "emerging_platforms": ["tiktok", "twitch"]
            }
        )
        
        result = await content_creator_prompts.generate_prompt(monetization_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify monetization elements
        assert "revenue" in prompt.lower() or "monetization" in prompt.lower()
        assert "streaming" in prompt.lower()
        assert "licensing" in prompt.lower()
        assert "spotify" in prompt.lower()
        assert "royalty" in prompt.lower()
    
    # ===== BLOGGER PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_blogger_creation_prompts(self, content_creator_prompts, sample_blogger_context):
        """Test blogger creation prompts generation"""
        result = await content_creator_prompts.generate_prompt(sample_blogger_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify blog elements are included
        assert "technology" in prompt.lower()
        assert "informative" in prompt.lower() or "professional" in prompt.lower()
        assert "1500" in prompt or "word count" in prompt.lower()
        assert "tech professionals" in prompt.lower()
        assert "seo" in prompt.lower()
        
        # Verify format requirements
        assert "markdown" in prompt.lower() or "h1" in prompt.lower() or "heading" in prompt.lower()
        
        # Verify metadata
        assert metadata["creator_type"] == "blogger"
        assert metadata["content_format"] == "text"
    
    @pytest.mark.asyncio
    async def test_blogger_seo_optimization_prompts(self, content_creator_prompts):
        """Test blogger SEO optimization prompts"""
        seo_context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.OPTIMIZATION,
            user_preferences={
                "target_keywords": ["AI content creation", "automated writing", "blog optimization"],
                "search_intent": "informational",
                "competition_level": "medium",
                "content_depth": "comprehensive"
            },
            platform_requirements={
                "title_length": 60,
                "meta_description_length": 160,
                "keyword_density": 2.5,
                "internal_links": 3,
                "external_links": 2
            },
            market_trends={
                "trending_keywords": ["artificial intelligence", "content automation"],
                "search_volume": "high",
                "seasonal_trends": "stable"
            }
        )
        
        result = await content_creator_prompts.generate_prompt(seo_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify SEO elements
        assert "seo" in prompt.lower() or "optimization" in prompt.lower()
        assert "keywords" in prompt.lower()
        assert "ai content creation" in prompt.lower()
        assert "title" in prompt.lower() and "meta" in prompt.lower()
        assert "internal links" in prompt.lower()
    
    # ===== PHOTOGRAPHER PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_photographer_creation_prompts(self, content_creator_prompts, sample_photographer_context):
        """Test photographer creation prompts generation"""
        result = await content_creator_prompts.generate_prompt(sample_photographer_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify photography elements
        assert "portrait" in prompt.lower()
        assert "natural" in prompt.lower() or "lighting" in prompt.lower()
        assert "rule of thirds" in prompt.lower() or "composition" in prompt.lower()
        assert "warm tones" in prompt.lower() or "color" in prompt.lower()
        assert "dslr" in prompt.lower() or "camera" in prompt.lower()
        
        # Verify technical specifications
        assert "4k" in prompt.lower() or "resolution" in prompt.lower()
        assert "raw" in prompt.lower() or "jpeg" in prompt.lower()
        assert "watermark" in prompt.lower()
        
        # Verify metadata
        assert metadata["creator_type"] == "photographer"
        assert metadata["content_format"] == "image"
    
    @pytest.mark.asyncio
    async def test_photographer_portfolio_optimization_prompts(self, content_creator_prompts):
        """Test photographer portfolio optimization prompts"""
        portfolio_context = PromptContext(
            creator_type=ContentCreatorType.PHOTOGRAPHER,
            content_format=ContentFormat.IMAGE,
            category=PromptCategory.OPTIMIZATION,
            user_preferences={
                "portfolio_style": "professional",
                "target_clients": ["corporate", "wedding", "fashion"],
                "showcase_categories": ["portrait", "landscape", "event"],
                "presentation_format": "online_gallery"
            },
            platform_requirements={
                "image_optimization": True,
                "seo_friendly_urls": True,
                "social_sharing": True,
                "mobile_responsive": True
            },
            market_trends={
                "popular_styles": ["cinematic", "natural", "editorial"],
                "client_preferences": ["quick_turnaround", "high_quality"],
                "platform_growth": ["instagram", "pinterest"]
            }
        )
        
        result = await content_creator_prompts.generate_prompt(portfolio_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify portfolio optimization elements
        assert "portfolio" in prompt.lower()
        assert "professional" in prompt.lower()
        assert "corporate" in prompt.lower() or "wedding" in prompt.lower()
        assert "gallery" in prompt.lower()
        assert "seo" in prompt.lower()
        assert "mobile" in prompt.lower() or "responsive" in prompt.lower()
    
    # ===== INFLUENCER PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_influencer_content_strategy_prompts(self, content_creator_prompts):
        """Test influencer content strategy prompts"""
        influencer_context = PromptContext(
            creator_type=ContentCreatorType.INFLUENCER,
            content_format=ContentFormat.MIXED_MEDIA,
            category=PromptCategory.CREATION,
            user_preferences={
                "niche": "lifestyle_tech",
                "audience_size": "50k_followers",
                "engagement_rate": 4.5,
                "posting_frequency": "daily",
                "platforms": ["instagram", "tiktok", "youtube"]
            },
            platform_requirements={
                "content_mix": "70_original_30_curated",
                "hashtag_strategy": True,
                "story_highlights": True,
                "cross_platform_sync": True
            },
            market_trends={
                "trending_formats": ["reels", "stories", "carousels"],
                "peak_engagement_times": ["6pm_8pm", "weekend_mornings"],
                "seasonal_content": "summer_tech_trends"
            }
        )
        
        result = await content_creator_prompts.generate_prompt(influencer_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify influencer elements
        assert "lifestyle" in prompt.lower() or "tech" in prompt.lower()
        assert "50k" in prompt or "followers" in prompt.lower()
        assert "engagement" in prompt.lower()
        assert "instagram" in prompt.lower() or "tiktok" in prompt.lower()
        assert "hashtag" in prompt.lower()
        assert "reels" in prompt.lower() or "stories" in prompt.lower()
    
    # ===== COMEDIAN PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_comedian_performance_prompts(self, content_creator_prompts):
        """Test comedian performance prompts"""
        comedian_context = PromptContext(
            creator_type=ContentCreatorType.COMEDIAN,
            content_format=ContentFormat.VIDEO,
            category=PromptCategory.CREATION,
            user_preferences={
                "comedy_style": "observational",
                "target_audience": "millennials",
                "content_rating": "PG13",
                "performance_length": 5,
                "topics": ["technology", "daily_life", "relationships"]
            },
            platform_requirements={
                "video_format": "vertical",
                "duration": "3_5_minutes",
                "captions": True,
                "thumbnail_optimization": True
            },
            market_trends={
                "trending_topics": ["remote_work", "social_media", "ai_humor"],
                "popular_formats": ["short_form", "storytelling", "impressions"],
                "platform_growth": ["tiktok", "youtube_shorts", "instagram_reels"]
            }
        )
        
        result = await content_creator_prompts.generate_prompt(comedian_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify comedy elements
        assert "comedy" in prompt.lower() or "humor" in prompt.lower()
        assert "observational" in prompt.lower()
        assert "millennials" in prompt.lower()
        assert "technology" in prompt.lower()
        assert "vertical" in prompt.lower() or "short" in prompt.lower()
        assert "captions" in prompt.lower()
    
    # ===== PERSONALIZATION ENGINE TESTS =====
    
    @pytest.mark.asyncio
    async def test_personalization_engine_user_preferences(self, content_creator_prompts):
        """Test personalization engine with user preferences"""
        base_context = PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.CREATION,
            user_preferences={
                "experience_level": "advanced",
                "previous_projects": ["ambient", "electronic", "classical_fusion"],
                "favorite_tools": ["ableton_live", "kontakt", "serum"],
                "collaboration_preference": "solo_work"
            },
            platform_requirements={},
            market_trends={}
        )
        
        result = await content_creator_prompts.generate_personalized_prompt(
            context=base_context,
            user_history=["successful_ambient_track", "viral_electronic_remix"],
            personalization_level="high"
        )
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify personalization elements
        assert "advanced" in prompt.lower() or "experienced" in prompt.lower()
        assert "ambient" in prompt.lower() or "electronic" in prompt.lower()
        assert "ableton" in prompt.lower() or "kontakt" in prompt.lower() or "serum" in prompt.lower()
        assert "solo" in prompt.lower() or "independent" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_personalization_engine_learning_adaptation(self, content_creator_prompts):
        """Test personalization engine learning and adaptation"""
        context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.CREATION,
            user_preferences={"writing_style": "conversational"},
            platform_requirements={},
            market_trends={}
        )
        
        # Simulate user feedback loop
        for i in range(5):
            result = await content_creator_prompts.generate_personalized_prompt(
                context=context,
                user_history=[f"blog_post_{i}"],
                personalization_level="adaptive"
            )
            
            # Simulate user feedback
            await content_creator_prompts.record_user_feedback(
                prompt_id=result.get("prompt_id"),
                user_rating=4.0 + (i * 0.2),  # Improving ratings
                used_suggestions=True,
                completion_time=300 - (i * 30)  # Faster completion
            )
        
        # Get final personalized prompt
        final_result = await content_creator_prompts.generate_personalized_prompt(
            context=context,
            user_history=["recent_successful_post"],
            personalization_level="high"
        )
        
        assert final_result["success"] is True
        # The prompt should be more refined based on learning
        assert "personalization_confidence" in final_result["metadata"]
        assert final_result["metadata"]["personalization_confidence"] > 0.7
    
    # ===== MULTI-FORMAT CONTENT TESTS =====
    
    @pytest.mark.asyncio
    async def test_mixed_media_content_prompts(self, content_creator_prompts):
        """Test mixed media content prompts"""
        mixed_media_context = PromptContext(
            creator_type=ContentCreatorType.YOUTUBER,
            content_format=ContentFormat.MIXED_MEDIA,
            category=PromptCategory.CREATION,
            user_preferences={
                "content_mix": {"video": 60, "audio": 25, "text": 15},
                "production_quality": "professional",
                "target_duration": 15,
                "audience_age": "18_35",
                "content_pillars": ["education", "entertainment", "inspiration"]
            },
            platform_requirements={
                "video_specs": "4K_60fps",
                "audio_specs": "48kHz_stereo",
                "thumbnail_required": True,
                "seo_optimization": True,
                "accessibility_features": True
            },
            market_trends={
                "trending_formats": ["tutorials", "behind_the_scenes", "quick_tips"],
                "engagement_boosters": ["polls", "Q&A", "challenges"],
                "algorithm_preferences": ["high_retention", "frequent_uploads"]
            }
        )
        
        result = await content_creator_prompts.generate_prompt(mixed_media_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify mixed media elements
        assert "video" in prompt.lower() and "audio" in prompt.lower()
        assert "professional" in prompt.lower()
        assert "15" in prompt or "duration" in prompt.lower()
        assert "education" in prompt.lower() or "entertainment" in prompt.lower()
        assert "4k" in prompt.lower() or "60fps" in prompt.lower()
        assert "thumbnail" in prompt.lower()
        assert "seo" in prompt.lower()
    
    # ===== COLLABORATION PROMPTS TESTS =====
    
    @pytest.mark.asyncio
    async def test_collaboration_workflow_prompts(self, content_creator_prompts):
        """Test collaboration workflow prompts"""
        collaboration_context = PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.COLLABORATION,
            user_preferences={
                "collaboration_type": "remote",
                "project_roles": ["composer", "producer", "mixing_engineer"],
                "communication_tools": ["slack", "zoom", "discord"],
                "file_sharing": "google_drive",
                "revision_tracking": True
            },
            platform_requirements={
                "real_time_collaboration": True,
                "version_control": True,
                "comment_system": True,
                "approval_workflow": True
            },
            market_trends={
                "popular_collaboration_tools": ["splice", "bandlab", "sessionwire"],
                "remote_work_growth": "increasing",
                "cross_genre_collaborations": "trending"
            }
        )
        
        result = await content_creator_prompts.generate_prompt(collaboration_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify collaboration elements
        assert "collaboration" in prompt.lower()
        assert "remote" in prompt.lower()
        assert "composer" in prompt.lower() or "producer" in prompt.lower()
        assert "slack" in prompt.lower() or "zoom" in prompt.lower()
        assert "version control" in prompt.lower() or "revision" in prompt.lower()
        assert "real-time" in prompt.lower() or "real time" in prompt.lower()
    
    # ===== ANALYTICS AND OPTIMIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_content_analytics_prompts(self, content_creator_prompts):
        """Test content analytics prompts"""
        analytics_context = PromptContext(
            creator_type=ContentCreatorType.INFLUENCER,
            content_format=ContentFormat.MIXED_MEDIA,
            category=PromptCategory.ANALYTICS,
            user_preferences={
                "metrics_focus": ["engagement_rate", "reach", "conversions"],
                "reporting_frequency": "weekly",
                "benchmark_comparison": True,
                "roi_tracking": True
            },
            platform_requirements={
                "multi_platform_tracking": True,
                "custom_dashboards": True,
                "automated_reports": True,
                "data_export": True
            },
            market_trends={
                "key_performance_indicators": ["story_completion_rate", "save_rate", "share_rate"],
                "emerging_metrics": ["authentic_engagement", "micro_conversions"],
                "platform_algorithm_changes": "frequent"
            }
        )
        
        result = await content_creator_prompts.generate_prompt(analytics_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify analytics elements
        assert "analytics" in prompt.lower() or "metrics" in prompt.lower()
        assert "engagement" in prompt.lower()
        assert "reach" in prompt.lower() or "conversions" in prompt.lower()
        assert "weekly" in prompt.lower() or "reporting" in prompt.lower()
        assert "dashboard" in prompt.lower()
        assert "roi" in prompt.lower() or "return on investment" in prompt.lower()
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_invalid_creator_type_error(self, content_creator_prompts):
        """Test error handling for invalid creator type"""
        invalid_context = PromptContext(
            creator_type="invalid_creator",  # Invalid enum value
            content_format=ContentFormat.TEXT,
            category=PromptCategory.CREATION,
            user_preferences={},
            platform_requirements={},
            market_trends={}
        )
        
        with pytest.raises(ValueError) or pytest.raises(TypeError):
            await content_creator_prompts.generate_prompt(invalid_context)
    
    @pytest.mark.asyncio
    async def test_missing_required_preferences_error(self, content_creator_prompts):
        """Test error handling for missing required preferences"""
        incomplete_context = PromptContext(
            creator_type=ContentCreatorType.MUSICIAN,
            content_format=ContentFormat.AUDIO,
            category=PromptCategory.CREATION,
            user_preferences={},  # Empty preferences
            platform_requirements={},
            market_trends={}
        )
        
        result = await content_creator_prompts.generate_prompt(incomplete_context)
        
        # Should either succeed with defaults or provide helpful error
        assert "success" in result
        if not result["success"]:
            assert "preferences" in result["error"].lower() or "required" in result["error"].lower()
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_prompt_generation_performance(self, content_creator_prompts, sample_musician_context):
        """Test prompt generation performance"""
        # Test single generation performance
        start_time = datetime.now()
        result = await content_creator_prompts.generate_prompt(sample_musician_context)
        single_duration = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert single_duration < 2.0  # Should complete within 2 seconds
        
        # Test batch generation performance
        contexts = [sample_musician_context] * 10
        
        start_time = datetime.now()
        results = await content_creator_prompts.generate_batch_prompts(contexts)
        batch_duration = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 10
        assert batch_duration < 10.0  # Should complete within 10 seconds
        assert batch_duration < single_duration * 10  # Should be more efficient than individual calls
    
    @pytest.mark.asyncio
    async def test_cache_efficiency(self, content_creator_prompts, sample_musician_context):
        """Test caching efficiency for repeated requests"""
        # First generation (no cache)
        start_time = datetime.now()
        result1 = await content_creator_prompts.generate_prompt(
            sample_musician_context, 
            use_cache=True
        )
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second generation (should use cache)
        start_time = datetime.now()
        result2 = await content_creator_prompts.generate_prompt(
            sample_musician_context,
            use_cache=True
        )
        second_duration = (datetime.now() - start_time).total_seconds()
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["prompt"] == result2["prompt"]
        
        # Second call should be significantly faster
        assert second_duration < first_duration * 0.5
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_full_content_creation_workflow(self, content_creator_prompts):
        """Test complete content creation workflow integration"""
        # Step 1: Initial prompt generation
        initial_context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.CREATION,
            user_preferences={
                "topic": "AI in content creation",
                "target_audience": "content creators",
                "word_count": 2000,
                "tone": "expert_friendly"
            },
            platform_requirements={
                "seo_optimized": True,
                "social_shares": True,
                "monetization_ready": True
            },
            market_trends={
                "trending_keywords": ["AI writing", "content automation", "creator tools"]
            }
        )
        
        creation_result = await content_creator_prompts.generate_prompt(initial_context)
        assert creation_result["success"] is True
        
        # Step 2: SEO optimization
        seo_context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.OPTIMIZATION,
            user_preferences={
                "content_draft": creation_result["prompt"],
                "target_keywords": ["AI content creation", "automated writing"],
                "optimization_goals": ["search_ranking", "click_through_rate"]
            },
            platform_requirements={
                "meta_tags": True,
                "structured_data": True,
                "social_media_optimization": True
            },
            market_trends={}
        )
        
        optimization_result = await content_creator_prompts.generate_prompt(seo_context)
        assert optimization_result["success"] is True
        
        # Step 3: Monetization strategy
        monetization_context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.MONETIZATION,
            user_preferences={
                "monetization_methods": ["affiliate_marketing", "sponsored_content", "course_sales"],
                "revenue_goals": "passive_income",
                "audience_size": "10k_monthly_readers"
            },
            platform_requirements={
                "disclosure_compliance": True,
                "tracking_implementation": True,
                "conversion_optimization": True
            },
            market_trends={}
        )
        
        monetization_result = await content_creator_prompts.generate_prompt(monetization_context)
        assert monetization_result["success"] is True
        
        # Step 4: Performance analytics
        analytics_context = PromptContext(
            creator_type=ContentCreatorType.BLOGGER,
            content_format=ContentFormat.TEXT,
            category=PromptCategory.ANALYTICS,
            user_preferences={
                "tracking_metrics": ["page_views", "engagement_time", "conversion_rate"],
                "reporting_schedule": "monthly",
                "improvement_focus": "user_engagement"
            },
            platform_requirements={
                "google_analytics": True,
                "heatmap_tracking": True,
                "a_b_testing": True
            },
            market_trends={}
        )
        
        analytics_result = await content_creator_prompts.generate_prompt(analytics_context)
        assert analytics_result["success"] is True
        
        # Verify workflow coherence
        assert all([
            creation_result["success"],
            optimization_result["success"], 
            monetization_result["success"],
            analytics_result["success"]
        ])
        
        # Verify content consistency across workflow steps
        creation_prompt = creation_result["prompt"]
        optimization_prompt = optimization_result["prompt"]
        
        assert "ai" in creation_prompt.lower() and "ai" in optimization_prompt.lower()
        assert "content creation" in creation_prompt.lower() and "content" in optimization_prompt.lower()
