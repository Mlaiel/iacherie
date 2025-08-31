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

"""Advanced Collaboration & Analytics Prompts Tests
Ultra-professional test suite for Collaboration & Analytics Prompts system

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

from ai.prompts.collaboration_analytics_prompts import (
    CollaborationAnalyticsPrompts, CollaborationType, AnalyticsType, CollaborationStage,
    MetricCategory, CollaborationContext, AnalyticsContext
)


class TestCollaborationAnalyticsPrompts:
    """Ultra-comprehensive test suite for Collaboration & Analytics Prompts"""    
    @pytest.fixture
    async def collaboration_analytics_prompts(self):
        """Create a fresh CollaborationAnalyticsPrompts instance for each test"""        prompts = CollaborationAnalyticsPrompts()
        await prompts.initialize()
        yield prompts
        await prompts.cleanup()
    
    @pytest.fixture
    def sample_music_collaboration_context(self):
        """Create sample music collaboration context for testing"""        return CollaborationContext(
            collaboration_type=CollaborationType.MUSIC_COLLABORATION,
            stage=CollaborationStage.PLANNING,
            participants=[
                {
                    "id": "creator_1",
                    "name": "Fahed Mlaiel",
                    "type": "electronic_producer",
                    "audience_size": 50000,
                    "engagement_rate": 6.5,
                    "platforms": ["spotify", "soundcloud", "youtube"]
                },
                {
                    "id": "creator_2", 
                    "name": "Alex Smith",
                    "type": "vocalist",
                    "audience_size": 75000,
                    "engagement_rate": 8.2,
                    "platforms": ["spotify", "instagram", "tiktok"]
                }
            ],
            project_details={
                "genre": "progressive_house",
                "target_duration": 360,
                "commercial_goals": True,
                "release_timeline": "6_weeks",
                "budget": 5000,
                "revenue_split": "50_50"
            },
            platform_strategy={
                "primary_platforms": ["spotify", "apple_music", "youtube"],
                "promotion_channels": ["instagram", "tiktok", "twitter"],
                "playlist_targeting": ["electronic", "progressive", "dance"],
                "cross_promotion": True
            },
            legal_considerations={
                "copyright_split": "equal",
                "publishing_rights": "shared",
                "sync_licensing": "joint_approval",
                "territorial_rights": "worldwide"
            }
        )
    
    @pytest.fixture
    def sample_performance_analytics_context(self):
        """Create sample performance analytics context for testing"""        return AnalyticsContext(
            analytics_type=AnalyticsType.PERFORMANCE_ANALYTICS,
            time_period={"start": "2024-01-01", "end": "2024-12-31"},
            platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.INSTAGRAM],
            metrics=[
                MetricType.STREAMS,
                MetricType.ENGAGEMENT_RATE,
                MetricType.AUDIENCE_GROWTH,
                MetricType.REVENUE
            ],
            content_data={
                "total_tracks": 24,
                "total_videos": 48,
                "total_posts": 156,
                "content_categories": ["music", "behind_the_scenes", "tutorials"]
            },
            performance_data={
                "spotify": {
                    "monthly_listeners": 45000,
                    "total_streams": 2500000,
                    "playlist_adds": 12500,
                    "monthly_growth": 8.5
                },
                "youtube": {
                    "subscribers": 28000,
                    "total_views": 5600000,
                    "average_view_duration": 65,
                    "subscriber_growth": 12.3
                },
                "instagram": {
                    "followers": 35000,
                    "total_engagements": 450000,
                    "story_completion_rate": 72,
                    "follower_growth": 15.2
                }
            },
            goals={
                "streams_target": 5000000,
                "subscriber_target": 50000,
                "engagement_target": 8.0,
                "revenue_target": 25000
            }
        )
    
    @pytest.fixture
    def sample_brand_partnership_context(self):
        """Create sample brand partnership context for testing"""        return CollaborationContext(
            collaboration_type=CollaborationType.BRAND_PARTNERSHIP,
            stage=CollaborationStage.NEGOTIATION,
            participants=[
                {
                    "id": "creator",
                    "name": "Content Creator",
                    "type": "tech_reviewer",
                    "audience_size": 120000,
                    "engagement_rate": 7.8,
                    "demographics": {
                        "age_range": "25-40",
                        "interests": ["technology", "gadgets", "innovation"],
                        "locations": ["US", "EU", "CA"]
                    }
                },
                {
                    "id": "brand",
                    "name": "TechCorp Inc.",
                    "type": "technology_brand",
                    "industry": "consumer_electronics",
                    "campaign_budget": 50000,
                    "campaign_goals": ["brand_awareness", "product_launch", "sales_conversion"]
                }
            ],
            project_details={
                "campaign_type": "product_review_series",
                "content_deliverables": ["unboxing_video", "review_video", "instagram_posts", "blog_article"],
                "campaign_duration": "8_weeks",
                "exclusivity_period": "3_months",
                "performance_targets": {
                    "total_reach": 500000,
                    "engagement_rate": 6.5,
                    "conversion_rate": 2.0
                }
            },
            platform_strategy={
                "primary_platforms": ["youtube", "instagram"],
                "secondary_platforms": ["twitter", "linkedin"],
                "content_distribution": "staggered_release",
                "hashtag_strategy": "#TechReview #Innovation #TechCorp"
            },
            legal_considerations={
                "disclosure_requirements": "FTC_compliant",
                "content_approval": "brand_review_required",
                "usage_rights": "perpetual_brand_use",
                "territorial_scope": "global"
            }
        )
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_collaboration_analytics_prompts_initialization(self, collaboration_analytics_prompts):
        """Test CollaborationAnalyticsPrompts initialization"""        assert collaboration_analytics_prompts is not None
        assert hasattr(collaboration_analytics_prompts, 'collaboration_templates')
        assert hasattr(collaboration_analytics_prompts, 'analytics_engines')
        assert hasattr(collaboration_analytics_prompts, 'collaboration_matcher')
        assert hasattr(collaboration_analytics_prompts, 'performance_analyzer')
        
        assert isinstance(collaboration_analytics_prompts.collaboration_templates, dict)
        assert isinstance(collaboration_analytics_prompts.analytics_engines, dict)
    
    @pytest.mark.asyncio
    async def test_collaboration_analytics_registry_loading(self, collaboration_analytics_prompts):
        """Test that collaboration analytics registry is properly loaded"""        registry = COLLABORATION_ANALYTICS_REGISTRY
        assert registry is not None
        assert isinstance(registry, dict)
        
        # Check that all collaboration types are represented
        for collab_type in CollaborationType:
            assert collab_type in registry
            
        # Check that all analytics types are represented  
        for analytics_type in AnalyticsType:
            assert analytics_type in registry["analytics_templates"]
    
    # ===== MUSIC COLLABORATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_music_collaboration_planning_prompts(self, collaboration_analytics_prompts, sample_music_collaboration_context):
        """Test music collaboration planning prompts generation"""        result = await collaboration_analytics_prompts.generate_collaboration_prompt(sample_music_collaboration_context)
        
        assert result["success"] is True
        assert "prompt" in result
        assert "metadata" in result
        
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify music collaboration elements
        assert "collaboration" in prompt.lower()
        assert "music" in prompt.lower()
        assert "progressive house" in prompt.lower() or "progressive_house" in prompt.lower()
        assert "fahed mlaiel" in prompt.lower()
        assert "alex smith" in prompt.lower()
        assert "electronic producer" in prompt.lower() or "vocalist" in prompt.lower()
        assert "50000" in prompt or "75000" in prompt  # audience sizes
        assert "6 weeks" in prompt.lower() or "6_weeks" in prompt.lower()
        assert "50_50" in prompt or "equal split" in prompt.lower()
        assert "spotify" in prompt.lower()
        assert "copyright" in prompt.lower()
        
        # Verify metadata
        assert metadata["collaboration_type"] == "music_collaboration"
        assert metadata["stage"] == "planning"
        assert len(metadata["participants"]) == 2
    
    @pytest.mark.asyncio
    async def test_music_collaboration_outreach_prompts(self, collaboration_analytics_prompts):
        """Test music collaboration outreach prompts"""        outreach_context = CollaborationContext(
            collaboration_type=CollaborationType.MUSIC_COLLABORATION,
            stage=CollaborationStage.OUTREACH,
            participants=[
                {
                    "id": "requester",
                    "name": "Aspiring Producer", 
                    "type": "electronic_producer",
                    "audience_size": 5000,
                    "portfolio": ["track1", "track2", "remix1"]
                }
            ],
            project_details={
                "collaboration_proposal": "remix_collaboration",
                "genre": "techno",
                "timeline": "4_weeks",
                "compensation": "revenue_share",
                "creative_direction": "collaborative"
            },
            platform_strategy={
                "target_creators": [
                    {"name": "established_artist", "genre_match": 85, "audience_overlap": 65},
                    {"name": "rising_talent", "genre_match": 92, "audience_overlap": 45}
                ]
            },
            legal_considerations={
                "rights_proposal": "fair_split",
                "credit_requirements": "equal_billing"
            }
        )
        
        result = await collaboration_analytics_prompts.generate_outreach_prompt(outreach_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify outreach elements
        assert "outreach" in prompt.lower() or "collaboration request" in prompt.lower()
        assert "remix" in prompt.lower()
        assert "techno" in prompt.lower()
        assert "4 weeks" in prompt.lower() or "4_weeks" in prompt.lower()
        assert "revenue share" in prompt.lower() or "revenue_share" in prompt.lower()
        assert "portfolio" in prompt.lower()
        assert "fair split" in prompt.lower() or "equal billing" in prompt.lower()
        assert "genre match" in prompt.lower() or "85%" in prompt
    
    # ===== BRAND PARTNERSHIP TESTS =====
    
    @pytest.mark.asyncio
    async def test_brand_partnership_negotiation_prompts(self, collaboration_analytics_prompts, sample_brand_partnership_context):
        """Test brand partnership negotiation prompts generation"""        result = await collaboration_analytics_prompts.generate_collaboration_prompt(sample_brand_partnership_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify brand partnership elements
        assert "brand partnership" in prompt.lower() or "brand" in prompt.lower()
        assert "negotiation" in prompt.lower()
        assert "tech reviewer" in prompt.lower() or "tech_reviewer" in prompt.lower()
        assert "techcorp" in prompt.lower()
        assert "120000" in prompt  # audience size
        assert "50000" in prompt  # campaign budget
        assert "product review" in prompt.lower()
        assert "unboxing" in prompt.lower()
        assert "8 weeks" in prompt.lower() or "8_weeks" in prompt.lower()
        assert "ftc compliant" in prompt.lower() or "ftc_compliant" in prompt.lower()
        assert "500000" in prompt  # reach target
        assert "exclusivity" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_sponsorship_deal_prompts(self, collaboration_analytics_prompts):
        """Test sponsorship deal prompts generation"""        sponsorship_context = CollaborationContext(
            collaboration_type=CollaborationType.SPONSORSHIP_DEAL,
            stage=CollaborationStage.EXECUTION,
            participants=[
                {
                    "id": "influencer",
                    "name": "Lifestyle Influencer",
                    "type": "lifestyle_creator",
                    "audience_size": 200000,
                    "engagement_rate": 9.2,
                    "demographics": {
                        "age_range": "18-34",
                        "gender_split": {"female": 75, "male": 25},
                        "top_locations": ["US", "UK", "CA", "AU"]
                    }
                },
                {
                    "id": "sponsor",
                    "name": "Fashion Brand",
                    "type": "fashion_retailer",
                    "campaign_objective": "seasonal_collection_launch",
                    "target_metrics": ["brand_awareness", "website_traffic", "sales"]
                }
            ],
            project_details={
                "sponsorship_type": "integrated_content",
                "deliverables": ["instagram_posts", "stories", "reels", "blog_feature"],
                "campaign_theme": "summer_collection_2024",
                "content_style": "authentic_lifestyle",
                "posting_schedule": "coordinated_campaign"
            },
            platform_strategy={
                "primary_platforms": ["instagram", "tiktok"],
                "content_mix": {"posts": 4, "stories": 8, "reels": 3},
                "hashtag_strategy": "#SummerVibes #FashionBrand #OOTD",
                "user_generated_content": "encouraged"
            },
            legal_considerations={
                "sponsorship_disclosure": "required",
                "content_guidelines": "brand_approved",
                "performance_guarantees": "engagement_minimums",
                "payment_terms": "milestone_based"
            }
        )
        
        result = await collaboration_analytics_prompts.generate_sponsorship_prompt(sponsorship_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify sponsorship elements
        assert "sponsorship" in prompt.lower()
        assert "lifestyle influencer" in prompt.lower() or "lifestyle_influencer" in prompt.lower()
        assert "fashion brand" in prompt.lower() or "fashion_brand" in prompt.lower()
        assert "200000" in prompt
        assert "9.2" in prompt or "engagement" in prompt.lower()
        assert "integrated content" in prompt.lower() or "integrated_content" in prompt.lower()
        assert "summer collection" in prompt.lower() or "summer_collection" in prompt.lower()
        assert "instagram" in prompt.lower()
        assert "stories" in prompt.lower() and "reels" in prompt.lower()
        assert "disclosure" in prompt.lower()
        assert "milestone" in prompt.lower()
    
    # ===== PERFORMANCE ANALYTICS TESTS =====
    
    @pytest.mark.asyncio
    async def test_performance_analytics_prompts(self, collaboration_analytics_prompts, sample_performance_analytics_context):
        """Test performance analytics prompts generation"""        result = await collaboration_analytics_prompts.generate_analytics_prompt(sample_performance_analytics_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify performance analytics elements
        assert "performance analytics" in prompt.lower() or ("performance" in prompt.lower() and "analytics" in prompt.lower())
        assert "2024-01-01" in prompt or "january" in prompt.lower()
        assert "spotify" in prompt.lower()
        assert "youtube" in prompt.lower() 
        assert "instagram" in prompt.lower()
        assert "45000" in prompt  # monthly listeners
        assert "2500000" in prompt  # total streams
        assert "28000" in prompt  # subscribers
        assert "5600000" in prompt  # total views
        assert "35000" in prompt  # followers
        assert "streams" in prompt.lower()
        assert "engagement rate" in prompt.lower() or "engagement_rate" in prompt.lower()
        assert "growth" in prompt.lower()
        assert "5000000" in prompt  # streams target
        
        # Verify metadata
        assert metadata["analytics_type"] == "performance_analytics"
        assert len(metadata["platforms"]) == 3
        assert len(metadata["metrics"]) == 4
    
    @pytest.mark.asyncio
    async def test_audience_insights_analytics_prompts(self, collaboration_analytics_prompts):
        """Test audience insights analytics prompts"""        audience_context = AnalyticsContext(
            analytics_type=AnalyticsType.AUDIENCE_INSIGHTS,
            time_period={"start": "2024-06-01", "end": "2024-12-01"},
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK],
            metrics=[
                MetricType.DEMOGRAPHICS,
                MetricType.INTERESTS,
                MetricType.BEHAVIOR_PATTERNS,
                MetricType.DEVICE_USAGE
            ],
            content_data={
                "content_categories": ["tech_reviews", "tutorials", "unboxings"],
                "posting_frequency": "3_per_week",
                "content_performance": {
                    "top_performing": ["tutorial_series", "product_comparisons"],
                    "underperforming": ["long_form_reviews"]
                }
            },
            performance_data={
                "youtube": {
                    "demographics": {"18-24": 25, "25-34": 45, "35-44": 20, "45+": 10},
                    "interests": ["technology", "gadgets", "reviews", "gaming"],
                    "watch_time_patterns": "evening_weekend",
                    "device_split": {"mobile": 65, "desktop": 30, "tv": 5}
                },
                "instagram": {
                    "demographics": {"18-24": 35, "25-34": 40, "35-44": 20, "45+": 5},
                    "interests": ["tech", "lifestyle", "innovation", "trends"],
                    "engagement_patterns": "consistent_daily",
                    "story_vs_feed": {"stories": 70, "feed": 30}
                }
            },
            goals={
                "audience_growth_target": 25,
                "engagement_improvement": 15,
                "demographic_expansion": "reach_older_segments"
            }
        )
        
        result = await collaboration_analytics_prompts.generate_audience_insights_prompt(audience_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify audience insights elements
        assert "audience insights" in prompt.lower() or ("audience" in prompt.lower() and "insights" in prompt.lower())
        assert "demographics" in prompt.lower()
        assert "interests" in prompt.lower()
        assert "behavior" in prompt.lower() or "patterns" in prompt.lower()
        assert "25-34" in prompt or "25_34" in prompt
        assert "technology" in prompt.lower()
        assert "evening weekend" in prompt.lower() or "evening_weekend" in prompt.lower()
        assert "mobile" in prompt.lower() and "desktop" in prompt.lower()
        assert "tutorial series" in prompt.lower() or "tutorial_series" in prompt.lower()
        assert "older segments" in prompt.lower() or "older_segments" in prompt.lower()
    
    # ===== COMPETITIVE ANALYTICS TESTS =====
    
    @pytest.mark.asyncio
    async def test_competitive_analytics_prompts(self, collaboration_analytics_prompts):
        """Test competitive analytics prompts generation"""        competitive_context = AnalyticsContext(
            analytics_type=AnalyticsType.COMPETITIVE_ANALYTICS,
            time_period={"start": "2024-01-01", "end": "2024-12-31"},
            platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.APPLE_MUSIC],
            metrics=[
                MetricType.MARKET_SHARE,
                MetricType.ENGAGEMENT_COMPARISON,
                MetricType.CONTENT_STRATEGY,
                MetricType.AUDIENCE_OVERLAP
            ],
            content_data={
                "own_content": {
                    "genre": "electronic",
                    "release_frequency": "monthly",
                    "average_streams": 50000,
                    "playlist_placements": 25
                }
            },
            performance_data={
                "competitors": [
                    {
                        "name": "Competitor A",
                        "similarity_score": 85,
                        "audience_size": 120000,
                        "engagement_rate": 7.2,
                        "content_strategy": "frequent_releases",
                        "strengths": ["playlist_networking", "social_media_presence"],
                        "weaknesses": ["audio_quality", "brand_consistency"]
                    },
                    {
                        "name": "Competitor B", 
                        "similarity_score": 78,
                        "audience_size": 95000,
                        "engagement_rate": 9.1,
                        "content_strategy": "quality_over_quantity",
                        "strengths": ["production_quality", "unique_sound"],
                        "weaknesses": ["marketing", "social_engagement"]
                    }
                ],
                "market_trends": [
                    "lo_fi_electronic_growth",
                    "collaborative_releases_trending", 
                    "short_form_content_dominance"
                ]
            },
            goals={
                "market_position_target": "top_10_percent",
                "competitive_advantage": "production_quality_and_marketing",
                "opportunity_identification": "underserved_niches"
            }
        )
        
        result = await collaboration_analytics_prompts.generate_competitive_analysis_prompt(competitive_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify competitive analytics elements
        assert "competitive" in prompt.lower() or "competition" in prompt.lower()
        assert "market share" in prompt.lower() or "market_share" in prompt.lower()
        assert "competitor a" in prompt.lower()
        assert "competitor b" in prompt.lower()
        assert "85" in prompt or "78" in prompt  # similarity scores
        assert "120000" in prompt or "95000" in prompt  # audience sizes
        assert "playlist networking" in prompt.lower() or "playlist_networking" in prompt.lower()
        assert "production quality" in prompt.lower() or "production_quality" in prompt.lower()
        assert "lo fi" in prompt.lower() or "lo_fi" in prompt.lower()
        assert "collaborative releases" in prompt.lower() or "collaborative_releases" in prompt.lower()
        assert "opportunity" in prompt.lower()
        assert "underserved" in prompt.lower()
    
    # ===== CROSS-PROMOTION TESTS =====
    
    @pytest.mark.asyncio
    async def test_cross_promotion_collaboration_prompts(self, collaboration_analytics_prompts):
        """Test cross-promotion collaboration prompts"""        cross_promo_context = CollaborationContext(
            collaboration_type=CollaborationType.CROSS_PROMOTION,
            stage=CollaborationStage.PLANNING,
            participants=[
                {
                    "id": "creator_1",
                    "name": "Music Producer",
                    "type": "electronic_artist",
                    "audience_size": 40000,
                    "platforms": {"spotify": 25000, "youtube": 15000, "instagram": 12000}
                },
                {
                    "id": "creator_2",
                    "name": "Visual Artist", 
                    "type": "digital_designer",
                    "audience_size": 30000,
                    "platforms": {"instagram": 20000, "behance": 8000, "youtube": 5000}
                }
            ],
            project_details={
                "promotion_type": "mutual_feature",
                "content_exchange": "music_for_visuals",
                "campaign_duration": "4_weeks",
                "success_metrics": ["cross_follower_growth", "engagement_increase", "content_reach"]
            },
            platform_strategy={
                "shared_platforms": ["instagram", "youtube"],
                "unique_platforms": {"creator_1": ["spotify"], "creator_2": ["behance"]},
                "content_plan": {
                    "week_1": "announcement_posts",
                    "week_2": "behind_the_scenes",
                    "week_3": "collaborative_content",
                    "week_4": "results_showcase"
                },
                "hashtag_strategy": "#CreativeCollaboration #MusicVisuals"
            },
            legal_considerations={
                "content_usage_rights": "mutual_approval",
                "attribution_requirements": "prominent_credit",
                "duration_limits": "campaign_specific"
            }
        )
        
        result = await collaboration_analytics_prompts.generate_cross_promotion_prompt(cross_promo_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify cross-promotion elements
        assert "cross promotion" in prompt.lower() or "cross-promotion" in prompt.lower()
        assert "music producer" in prompt.lower() or "music_producer" in prompt.lower()
        assert "visual artist" in prompt.lower() or "visual_artist" in prompt.lower()
        assert "40000" in prompt or "30000" in prompt  # audience sizes
        assert "mutual feature" in prompt.lower() or "mutual_feature" in prompt.lower()
        assert "music for visuals" in prompt.lower() or "music_for_visuals" in prompt.lower()
        assert "4 weeks" in prompt.lower() or "4_weeks" in prompt.lower()
        assert "behance" in prompt.lower()
        assert "behind the scenes" in prompt.lower() or "behind_the_scenes" in prompt.lower()
        assert "mutual approval" in prompt.lower() or "mutual_approval" in prompt.lower()
        assert "prominent credit" in prompt.lower() or "prominent_credit" in prompt.lower()
    
    # ===== REVENUE ANALYTICS TESTS =====
    
    @pytest.mark.asyncio
    async def test_revenue_analytics_prompts(self, collaboration_analytics_prompts):
        """Test revenue analytics prompts generation"""        revenue_context = AnalyticsContext(
            analytics_type=AnalyticsType.REVENUE_ANALYTICS,
            time_period={"start": "2024-01-01", "end": "2024-12-31"},
            platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.DIRECT_SALES],
            metrics=[
                MetricType.TOTAL_REVENUE,
                MetricType.REVENUE_PER_STREAM,
                MetricType.REVENUE_SOURCES,
                MetricType.PROFIT_MARGINS
            ],
            content_data={
                "monetization_methods": ["streaming", "youtube_ads", "merchandise", "licensing"],
                "content_portfolio": {
                    "original_tracks": 18,
                    "remixes": 6,
                    "collaborative_works": 4,
                    "licensed_content": 3
                }
            },
            performance_data={
                "revenue_breakdown": {
                    "streaming": {"amount": 8500, "percentage": 45},
                    "youtube_ads": {"amount": 3200, "percentage": 17},
                    "merchandise": {"amount": 4800, "percentage": 25},
                    "licensing": {"amount": 2500, "percentage": 13}
                },
                "monthly_trends": {
                    "q1": 4200,
                    "q2": 5100,
                    "q3": 4800,
                    "q4": 5900
                },
                "cost_analysis": {
                    "production_costs": 3500,
                    "marketing_spend": 2000,
                    "platform_fees": 1200,
                    "other_expenses": 800
                }
            },
            goals={
                "annual_revenue_target": 25000,
                "profit_margin_target": 65,
                "diversification_goal": "reduce_streaming_dependency",
                "growth_rate_target": 30
            }
        )
        
        result = await collaboration_analytics_prompts.generate_revenue_analytics_prompt(revenue_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify revenue analytics elements
        assert "revenue analytics" in prompt.lower() or ("revenue" in prompt.lower() and "analytics" in prompt.lower())
        assert "monetization" in prompt.lower()
        assert "streaming" in prompt.lower()
        assert "merchandise" in prompt.lower()
        assert "licensing" in prompt.lower()
        assert "8500" in prompt  # streaming revenue
        assert "3200" in prompt  # youtube ads
        assert "4800" in prompt  # merchandise
        assert "45%" in prompt or "45 percent" in prompt.lower()  # streaming percentage
        assert "production costs" in prompt.lower() or "production_costs" in prompt.lower()
        assert "25000" in prompt  # revenue target
        assert "65" in prompt  # profit margin target
        assert "diversification" in prompt.lower()
        assert "reduce streaming dependency" in prompt.lower() or "reduce_streaming_dependency" in prompt.lower()
    
    # ===== COLLABORATION MATCHING TESTS =====
    
    @pytest.mark.asyncio
    async def test_collaboration_matching_prompts(self, collaboration_analytics_prompts):
        """Test collaboration matching and recommendation prompts"""        matching_context = {
            "seeking_creator": {
                "id": "seeker_1",
                "name": "Rising Producer",
                "type": "electronic_producer",
                "audience_size": 15000,
                "genre": "ambient_electronic",
                "collaboration_history": ["remix_project", "ep_collaboration"],
                "looking_for": ["vocalist", "instrumentalist", "visual_artist"],
                "budget_range": "1000_5000",
                "timeline": "flexible"
            },
            "potential_matches": [
                {
                    "id": "match_1",
                    "name": "Indie Vocalist",
                    "type": "vocalist",
                    "audience_size": 22000,
                    "genre_compatibility": 88,
                    "audience_overlap": 35,
                    "collaboration_rating": 9.2,
                    "availability": "available"
                },
                {
                    "id": "match_2", 
                    "name": "Saxophone Player",
                    "type": "instrumentalist",
                    "audience_size": 8000,
                    "genre_compatibility": 92,
                    "audience_overlap": 25,
                    "collaboration_rating": 8.7,
                    "availability": "limited"
                }
            ],
            "matching_criteria": {
                "genre_weight": 40,
                "audience_weight": 30,
                "rating_weight": 20,
                "availability_weight": 10
            }
        }
        
        result = await collaboration_analytics_prompts.generate_matching_prompt(matching_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify matching elements
        assert "collaboration matching" in prompt.lower() or "matching" in prompt.lower()
        assert "rising producer" in prompt.lower() or "rising_producer" in prompt.lower()
        assert "ambient electronic" in prompt.lower() or "ambient_electronic" in prompt.lower()
        assert "indie vocalist" in prompt.lower() or "indie_vocalist" in prompt.lower()
        assert "saxophone player" in prompt.lower() or "saxophone_player" in prompt.lower()
        assert "88%" in prompt or "88 percent" in prompt.lower()  # genre compatibility
        assert "92%" in prompt or "92 percent" in prompt.lower()
        assert "22000" in prompt or "8000" in prompt  # audience sizes
        assert "genre weight" in prompt.lower() or "genre_weight" in prompt.lower()
        assert "availability" in prompt.lower()
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_invalid_collaboration_type_error(self, collaboration_analytics_prompts):
        """Test error handling for invalid collaboration type"""        with pytest.raises(ValueError) or pytest.raises(TypeError):
            invalid_context = CollaborationContext(
                collaboration_type="invalid_collaboration",
                stage=CollaborationStage.PLANNING,
                participants=[],
                project_details={},
                platform_strategy={},
                legal_considerations={}
            )
            await collaboration_analytics_prompts.generate_collaboration_prompt(invalid_context)
    
    @pytest.mark.asyncio
    async def test_missing_participant_data_handling(self, collaboration_analytics_prompts):
        """Test handling of missing participant data"""        minimal_context = CollaborationContext(
            collaboration_type=CollaborationType.MUSIC_COLLABORATION,
            stage=CollaborationStage.DISCOVERY,
            participants=[],  # Empty participants
            project_details={},
            platform_strategy={},
            legal_considerations={}
        )
        
        result = await collaboration_analytics_prompts.generate_collaboration_prompt(minimal_context)
        
        # Should either succeed with guidance or provide helpful error
        if not result["success"]:
            assert "participants" in result["error"].lower() or "missing" in result["error"].lower()
        else:
            assert "guidance" in result["prompt"].lower() or "discovery" in result["prompt"].lower()
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_collaboration_prompt_generation_performance(self, collaboration_analytics_prompts, sample_music_collaboration_context):
        """Test collaboration prompt generation performance"""        # Test single generation performance
        start_time = datetime.now()
        result = await collaboration_analytics_prompts.generate_collaboration_prompt(sample_music_collaboration_context)
        single_duration = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert single_duration < 3.0  # Should complete within 3 seconds
        
        # Test batch generation performance
        contexts = [sample_music_collaboration_context] * 3
        
        start_time = datetime.now()
        results = await collaboration_analytics_prompts.generate_batch_collaboration_prompts(contexts)
        batch_duration = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 3
        assert batch_duration < 8.0  # Should complete within 8 seconds
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_comprehensive_collaboration_workflow(self, collaboration_analytics_prompts):
        """Test comprehensive collaboration workflow integration"""        # Step 1: Discovery and matching
        discovery_result = await collaboration_analytics_prompts.discover_collaboration_opportunities({
            "creator_profile": {
                "type": "music_producer",
                "genre": "electronic",
                "audience_size": 25000,
                "goals": ["audience_growth", "creative_expansion"]
            },
            "collaboration_preferences": {
                "types": ["music_collaboration", "cross_promotion"],
                "partner_criteria": {"min_audience": 10000, "genre_compatibility": 70}
            }
        })
        
        assert discovery_result["success"] is True
        potential_collaborations = discovery_result["opportunities"]
        
        # Step 2: Outreach planning
        selected_opportunity = potential_collaborations[0]
        outreach_context = CollaborationContext(
            collaboration_type=CollaborationType.MUSIC_COLLABORATION,
            stage=CollaborationStage.OUTREACH,
            participants=[
                {"id": "requester", "name": "Music Producer"},
                selected_opportunity["partner_info"]
            ],
            project_details=selected_opportunity["project_proposal"],
            platform_strategy={},
            legal_considerations={}
        )
        
        outreach_result = await collaboration_analytics_prompts.generate_collaboration_prompt(outreach_context)
        assert outreach_result["success"] is True
        
        # Step 3: Project planning
        planning_context = CollaborationContext(
            collaboration_type=CollaborationType.MUSIC_COLLABORATION,
            stage=CollaborationStage.PLANNING,
            participants=outreach_context.participants,
            project_details={
                "confirmed_collaboration": True,
                "timeline": "8_weeks",
                "deliverables": ["original_track", "remix_versions", "music_video"]
            },
            platform_strategy={
                "release_strategy": "coordinated_launch",
                "promotion_plan": "cross_platform"
            },
            legal_considerations={
                "agreements_needed": ["collaboration_agreement", "publishing_split"]
            }
        )
        
        planning_result = await collaboration_analytics_prompts.generate_collaboration_prompt(planning_context)
        assert planning_result["success"] is True
        
        # Step 4: Performance tracking setup
        analytics_context = AnalyticsContext(
            analytics_type=AnalyticsType.PERFORMANCE_ANALYTICS,
            time_period={"start": "project_launch", "duration": "12_weeks"},
            platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.INSTAGRAM],
            metrics=[MetricType.STREAMS, MetricType.ENGAGEMENT_RATE, MetricType.AUDIENCE_GROWTH],
            content_data={"collaborative_project": True},
            performance_data={},
            goals={
                "collaborative_success_metrics": ["combined_audience_growth", "cross_engagement", "revenue_targets"]
            }
        )
        
        analytics_result = await collaboration_analytics_prompts.generate_analytics_prompt(analytics_context)
        assert analytics_result["success"] is True
        
        # Verify workflow coherence
        assert all([
            discovery_result["success"],
            outreach_result["success"],
            planning_result["success"],
            analytics_result["success"]
        ])
        
        # Verify consistency across workflow steps
        outreach_prompt = outreach_result["prompt"]
        planning_prompt = planning_result["prompt"]
        analytics_prompt = analytics_result["prompt"]
        
        assert "music" in outreach_prompt.lower() and "music" in planning_prompt.lower()
        assert "collaboration" in all([p.lower() for p in [outreach_prompt, planning_prompt, analytics_prompt]])
        
        # Step 5: Success measurement and reporting
        success_metrics_result = await collaboration_analytics_prompts.generate_collaboration_success_report({
            "collaboration_id": "test_collaboration",
            "duration": "8_weeks",
            "initial_metrics": discovery_result["baseline_metrics"],
            "final_metrics": {"simulated": "success_data"},
            "goals_achievement": {"audience_growth": 85, "engagement": 92, "revenue": 78}
        })
        
        assert success_metrics_result["success"] is True
        assert "success" in success_metrics_result["report"].lower()
        assert "85%" in success_metrics_result["report"] or "85 percent" in success_metrics_result["report"].lower()
