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
Advanced SEO & Monetization Prompts Tests
Ultra-professional test suite for SEO & Monetization Prompts system

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

from ai.prompts.seo_monetization_prompts import (
    SEOMonetizationPrompts, SEOStrategy, MonetizationModel, Platform, ContentCategory,
    SEOMonetizationContext, get_seo_monetization_prompts, create_seo_monetization_context,
    SEO_MONETIZATION_REGISTRY
)


class TestSEOMonetizationPrompts:
    """Ultra-comprehensive test suite for SEO & Monetization Prompts"""
    
    @pytest.fixture
    async def seo_monetization_prompts(self):
        """Create a fresh SEOMonetizationPrompts instance for each test"""
        prompts = SEOMonetizationPrompts()
        await prompts.initialize()
        yield prompts
        await prompts.cleanup()
    
    @pytest.fixture
    def sample_blog_seo_context(self):
        """Create sample blog SEO context for testing"""
        return SEOMonetizationContext(
            seo_strategy=SEOStrategy.ADVANCED,
            monetization_models=[MonetizationModel.ADVERTISING, MonetizationModel.AFFILIATE],
            platforms=[Platform.GOOGLE, Platform.BING],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=["AI content creation", "automated blogging", "machine learning writing"],
            competition_analysis={
                "keyword_difficulty": 65,
                "top_competitors": ["competitor1.com", "competitor2.com", "competitor3.com"],
                "content_gaps": ["AI ethics in content", "ROI measurement", "enterprise solutions"],
                "search_volume": 12000
            },
            monetization_goals={
                "monthly_revenue_target": 5000,
                "conversion_rate_target": 2.5,
                "cost_per_acquisition_target": 50,
                "lifetime_value_target": 500
            },
            technical_requirements={
                "page_speed_target": 3.0,
                "mobile_optimization": True,
                "schema_markup": True,
                "ssl_required": True,
                "accessibility_compliance": "WCAG_2.1_AA"
            },
            audience_data={
                "primary_demographics": {"age": "25-45", "location": "US, EU", "interests": ["technology", "AI", "business"]},
                "user_intent": "informational_commercial",
                "device_preferences": {"mobile": 60, "desktop": 35, "tablet": 5},
                "search_behavior": "research_oriented"
            }
        )
    
    @pytest.fixture
    def sample_music_monetization_context(self):
        """Create sample music monetization context for testing"""
        return SEOMonetizationContext(
            seo_strategy=SEOStrategy.CONTENT_SEO,
            monetization_models=[MonetizationModel.LICENSING, MonetizationModel.SUBSCRIPTION, MonetizationModel.MERCHANDISE],
            platforms=[Platform.SPOTIFY, Platform.YOUTUBE, Platform.APPLE_MUSIC],
            content_category=ContentCategory.MUSIC,
            target_keywords=["electronic music production", "AI generated music", "royalty-free tracks"],
            competition_analysis={
                "genre_competition": "moderate",
                "similar_artists": ["artist1", "artist2", "artist3"],
                "market_trends": ["lo-fi beats", "ambient electronic", "AI-human collaborations"],
                "streaming_volume": 50000
            },
            monetization_goals={
                "monthly_streams_target": 100000,
                "revenue_per_stream": 0.004,
                "licensing_deals_target": 5,
                "merchandise_revenue_target": 1000
            },
            technical_requirements={
                "audio_quality": "24-bit/48kHz",
                "metadata_optimization": True,
                "playlist_submission": True,
                "cross_platform_distribution": True
            },
            audience_data={
                "primary_demographics": {"age": "18-35", "location": "global", "music_preferences": ["electronic", "ambient", "experimental"]},
                "listening_patterns": "focus_work_study",
                "platform_preferences": {"spotify": 45, "youtube": 30, "apple_music": 25},
                "engagement_behavior": "playlist_savers"
            }
        )
    
    @pytest.fixture 
    def sample_video_monetization_context(self):
        """Create sample video monetization context for testing"""
        return SEOMonetizationContext(
            seo_strategy=SEOStrategy.ENTERPRISE,
            monetization_models=[MonetizationModel.ADVERTISING, MonetizationModel.SPONSORSHIP, MonetizationModel.CROWDFUNDING],
            platforms=[Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM],
            content_category=ContentCategory.EDUCATION,
            target_keywords=["AI tutorial", "machine learning explained", "tech education"],
            competition_analysis={
                "channel_competition": "high",
                "top_channels": ["channel1", "channel2", "channel3"],
                "content_gaps": ["practical AI implementations", "beginner-friendly tutorials", "real-world case studies"],
                "view_volume": 500000
            },
            monetization_goals={
                "monthly_views_target": 1000000,
                "subscriber_growth_target": 10000,
                "ad_revenue_target": 3000,
                "sponsorship_deals_target": 2
            },
            technical_requirements={
                "video_quality": "4K",
                "thumbnail_optimization": True,
                "end_screen_optimization": True,
                "closed_captions": True,
                "seo_tags": True
            },
            audience_data={
                "primary_demographics": {"age": "20-40", "location": "global", "interests": ["technology", "learning", "career_development"]},
                "viewing_patterns": "evening_weekend",
                "engagement_preferences": {"comments": "high", "likes": "moderate", "shares": "low"},
                "retention_behavior": "tutorial_completers"
            }
        )
    
    # ===== INITIALIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_seo_monetization_prompts_initialization(self, seo_monetization_prompts):
        """Test SEOMonetizationPrompts initialization"""
        assert seo_monetization_prompts is not None
        assert hasattr(seo_monetization_prompts, 'seo_templates')
        assert hasattr(seo_monetization_prompts, 'monetization_strategies')
        assert hasattr(seo_monetization_prompts, 'keyword_research_engine')
        assert hasattr(seo_monetization_prompts, 'competition_analyzer')
        
        assert isinstance(seo_monetization_prompts.seo_templates, dict)
        assert isinstance(seo_monetization_prompts.monetization_strategies, dict)
    
    @pytest.mark.asyncio
    async def test_seo_monetization_registry_loading(self, seo_monetization_prompts):
        """Test that SEO monetization registry is properly loaded"""
        registry = SEO_MONETIZATION_REGISTRY
        assert registry is not None
        assert isinstance(registry, dict)
        
        # Check that all SEO strategies are represented
        for seo_strategy in SEOStrategy:
            assert seo_strategy in registry
            
        # Check that each strategy has monetization models
        for seo_strategy in SEOStrategy:
            strategy_data = registry[seo_strategy]
            assert "monetization_models" in strategy_data
            assert "platforms" in strategy_data
            assert "optimization_techniques" in strategy_data
    
    # ===== BLOG SEO OPTIMIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_blog_advanced_seo_prompts(self, seo_monetization_prompts, sample_blog_seo_context):
        """Test advanced blog SEO prompts generation"""
        result = await seo_monetization_prompts.generate_seo_prompt(sample_blog_seo_context)
        
        assert result["success"] is True
        assert "prompt" in result
        assert "metadata" in result
        
        prompt = result["prompt"]
        metadata = result["metadata"]
        
        # Verify SEO elements are included
        assert "seo" in prompt.lower() or "optimization" in prompt.lower()
        assert "ai content creation" in prompt.lower()
        assert "automated blogging" in prompt.lower()
        assert "machine learning writing" in prompt.lower()
        assert "keyword difficulty" in prompt.lower() or "65" in prompt
        assert "search volume" in prompt.lower() or "12000" in prompt
        assert "schema markup" in prompt.lower()
        assert "mobile optimization" in prompt.lower()
        assert "page speed" in prompt.lower()
        
        # Verify metadata
        assert metadata["seo_strategy"] == "advanced"
        assert metadata["content_category"] == "technology"
        assert len(metadata["target_keywords"]) >= 3
    
    @pytest.mark.asyncio
    async def test_blog_keyword_research_prompts(self, seo_monetization_prompts):
        """Test blog keyword research prompts"""
        keyword_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.CONTENT_SEO,
            monetization_models=[MonetizationModel.AFFILIATE],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=[],  # Empty - need keyword research
            competition_analysis={
                "seed_keywords": ["AI", "content", "automation"],
                "market_size": "large",
                "seasonal_trends": "stable"
            },
            monetization_goals={},
            technical_requirements={},
            audience_data={
                "search_intent": "commercial_investigation",
                "buyer_journey_stage": "consideration"
            }
        )
        
        result = await seo_monetization_prompts.generate_keyword_research_prompt(keyword_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify keyword research elements
        assert "keyword research" in prompt.lower() or "keyword" in prompt.lower()
        assert "seed keywords" in prompt.lower() or "seed_keywords" in prompt.lower()
        assert "commercial investigation" in prompt.lower() or "commercial_investigation" in prompt.lower()
        assert "consideration" in prompt.lower()
        assert "long-tail" in prompt.lower() or "long tail" in prompt.lower()
        assert "search volume" in prompt.lower()
        assert "competition" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_blog_content_optimization_prompts(self, seo_monetization_prompts):
        """Test blog content optimization prompts"""
        content_optimization_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.CONTENT_SEO,
            monetization_models=[MonetizationModel.ADVERTISING],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=["AI content optimization", "SEO automation", "content marketing AI"],
            competition_analysis={
                "top_ranking_content": [
                    {"url": "example1.com", "word_count": 2500, "readability_score": 65},
                    {"url": "example2.com", "word_count": 3000, "readability_score": 70}
                ],
                "content_gap_analysis": ["implementation guides", "case studies", "ROI calculators"]
            },
            monetization_goals={
                "ad_placement_optimization": True,
                "affiliate_integration": True,
                "email_list_building": True
            },
            technical_requirements={
                "target_word_count": 2800,
                "readability_target": "grade_8",
                "internal_links_target": 5,
                "external_links_target": 3,
                "image_alt_text": True
            },
            audience_data={}
        )
        
        result = await seo_monetization_prompts.generate_content_optimization_prompt(content_optimization_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify content optimization elements
        assert "content optimization" in prompt.lower() or "content" in prompt.lower()
        assert "2800" in prompt or "word count" in prompt.lower()
        assert "readability" in prompt.lower() or "grade 8" in prompt.lower()
        assert "internal links" in prompt.lower() or "internal_links" in prompt.lower()
        assert "alt text" in prompt.lower() or "alt_text" in prompt.lower()
        assert "ai content optimization" in prompt.lower()
        assert "case studies" in prompt.lower()
    
    # ===== MUSIC MONETIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_music_streaming_monetization_prompts(self, seo_monetization_prompts, sample_music_monetization_context):
        """Test music streaming monetization prompts generation"""
        result = await seo_monetization_prompts.generate_monetization_prompt(sample_music_monetization_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify music monetization elements
        assert "music" in prompt.lower() or "streaming" in prompt.lower()
        assert "licensing" in prompt.lower()
        assert "spotify" in prompt.lower()
        assert "100000" in prompt or "streams" in prompt.lower()
        assert "0.004" in prompt or "revenue per stream" in prompt.lower()
        assert "playlist" in prompt.lower()
        assert "24-bit" in prompt or "48khz" in prompt.lower()
        assert "metadata" in prompt.lower()
        assert "electronic music production" in prompt.lower()
        
        # Verify platform-specific optimization
        assert "cross-platform" in prompt.lower() or "cross platform" in prompt.lower()
        assert "distribution" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_music_licensing_optimization_prompts(self, seo_monetization_prompts):
        """Test music licensing optimization prompts"""
        licensing_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.TECHNICAL_SEO,
            monetization_models=[MonetizationModel.LICENSING],
            platforms=[Platform.SYNC_LICENSING_PLATFORMS],
            content_category=ContentCategory.MUSIC,
            target_keywords=["royalty-free music", "sync licensing", "commercial music"],
            competition_analysis={
                "licensing_market_size": "growing",
                "average_licensing_fee": 500,
                "popular_genres": ["corporate", "cinematic", "electronic"],
                "client_demands": ["high_quality", "quick_turnaround", "flexible_licensing"]
            },
            monetization_goals={
                "licensing_deals_per_month": 10,
                "average_deal_value": 750,
                "client_retention_rate": 80,
                "portfolio_growth_rate": 20
            },
            technical_requirements={
                "audio_formats": ["WAV", "AIFF", "MP3"],
                "quality_standards": "broadcast_ready",
                "metadata_completeness": 100,
                "version_variations": ["full", "60s", "30s", "15s", "loop"]
            },
            audience_data={
                "target_clients": ["ad_agencies", "film_studios", "video_producers", "podcasters"],
                "project_types": ["commercials", "documentaries", "corporate_videos", "games"],
                "budget_ranges": ["budget", "mid_tier", "premium"]
            }
        )
        
        result = await seo_monetization_prompts.generate_licensing_optimization_prompt(licensing_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify licensing optimization elements
        assert "licensing" in prompt.lower()
        assert "sync" in prompt.lower() or "synchronization" in prompt.lower()
        assert "royalty-free" in prompt.lower() or "royalty free" in prompt.lower()
        assert "broadcast ready" in prompt.lower() or "broadcast_ready" in prompt.lower()
        assert "ad agencies" in prompt.lower() or "ad_agencies" in prompt.lower()
        assert "version variations" in prompt.lower() or "variations" in prompt.lower()
        assert "metadata" in prompt.lower()
        assert "750" in prompt or "deal value" in prompt.lower()
    
    # ===== VIDEO MONETIZATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_youtube_monetization_prompts(self, seo_monetization_prompts, sample_video_monetization_context):
        """Test YouTube monetization prompts generation"""
        result = await seo_monetization_prompts.generate_platform_specific_prompt(
            sample_video_monetization_context, 
            Platform.YOUTUBE
        )
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify YouTube-specific monetization elements
        assert "youtube" in prompt.lower()
        assert "monetization" in prompt.lower() or "revenue" in prompt.lower()
        assert "ad revenue" in prompt.lower() or "ad_revenue" in prompt.lower()
        assert "sponsorship" in prompt.lower()
        assert "1000000" in prompt or "million" in prompt.lower()
        assert "subscriber" in prompt.lower()
        assert "thumbnail" in prompt.lower()
        assert "end screen" in prompt.lower() or "end_screen" in prompt.lower()
        assert "4k" in prompt.lower()
        assert "closed captions" in prompt.lower() or "captions" in prompt.lower()
        
        # Verify audience targeting
        assert "20-40" in prompt or "demographics" in prompt.lower()
        assert "tutorial" in prompt.lower()
        assert "retention" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_video_seo_optimization_prompts(self, seo_monetization_prompts):
        """Test video SEO optimization prompts"""
        video_seo_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.ENTERPRISE,
            monetization_models=[MonetizationModel.ADVERTISING],
            platforms=[Platform.YOUTUBE, Platform.TIKTOK],
            content_category=ContentCategory.EDUCATION,
            target_keywords=["learn AI", "machine learning tutorial", "AI for beginners"],
            competition_analysis={
                "top_videos": [
                    {"title": "AI Explained Simply", "views": 500000, "engagement_rate": 8.5},
                    {"title": "ML Tutorial Series", "views": 750000, "engagement_rate": 12.3}
                ],
                "trending_topics": ["ChatGPT tutorials", "AI art creation", "coding with AI"],
                "optimal_video_length": {"youtube": 900, "tiktok": 60}
            },
            monetization_goals={
                "view_duration_target": 70,
                "click_through_rate_target": 8.0,
                "subscriber_conversion_rate": 3.5
            },
            technical_requirements={
                "video_seo_optimization": True,
                "transcript_optimization": True,
                "hashtag_strategy": True,
                "cross_platform_adaptation": True
            },
            audience_data={
                "search_behavior": "tutorial_focused",
                "preferred_learning_style": "visual_practical",
                "attention_span": {"youtube": "medium", "tiktok": "short"}
            }
        )
        
        result = await seo_monetization_prompts.generate_video_seo_prompt(video_seo_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify video SEO elements
        assert "video seo" in prompt.lower() or "video" in prompt.lower() and "seo" in prompt.lower()
        assert "learn ai" in prompt.lower()
        assert "tutorial" in prompt.lower()
        assert "transcript" in prompt.lower()
        assert "hashtag" in prompt.lower()
        assert "click-through rate" in prompt.lower() or "ctr" in prompt.lower()
        assert "900" in prompt or "15 minutes" in prompt.lower()
        assert "60" in prompt or "tiktok" in prompt.lower()
        assert "engagement" in prompt.lower()
    
    # ===== AFFILIATE MARKETING TESTS =====
    
    @pytest.mark.asyncio
    async def test_affiliate_marketing_prompts(self, seo_monetization_prompts):
        """Test affiliate marketing prompts generation"""
        affiliate_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.ADVANCED,
            monetization_models=[MonetizationModel.AFFILIATE],
            platforms=[Platform.GOOGLE, Platform.BING],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=["best AI tools", "AI software review", "AI productivity tools"],
            competition_analysis={
                "affiliate_competition": "high",
                "commission_rates": {"tier_1": 10, "tier_2": 25, "tier_3": 50},
                "conversion_rates": {"industry_average": 2.3, "top_performers": 8.5},
                "seasonal_trends": "Q4_peak"
            },
            monetization_goals={
                "monthly_affiliate_revenue": 10000,
                "conversion_rate_target": 5.0,
                "email_subscriber_target": 5000,
                "content_engagement_target": 6.5
            },
            technical_requirements={
                "affiliate_link_management": True,
                "disclosure_compliance": True,
                "conversion_tracking": True,
                "a_b_testing": True
            },
            audience_data={
                "buyer_personas": ["tech_professional", "entrepreneur", "content_creator"],
                "purchase_behavior": "research_heavy",
                "trust_factors": ["reviews", "case_studies", "free_trials"],
                "decision_timeline": "2_4_weeks"
            }
        )
        
        result = await seo_monetization_prompts.generate_affiliate_marketing_prompt(affiliate_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify affiliate marketing elements
        assert "affiliate" in prompt.lower()
        assert "commission" in prompt.lower()
        assert "conversion" in prompt.lower()
        assert "best ai tools" in prompt.lower()
        assert "review" in prompt.lower()
        assert "disclosure" in prompt.lower()
        assert "10000" in prompt or "revenue" in prompt.lower()
        assert "5.0" in prompt or "conversion rate" in prompt.lower()
        assert "trust" in prompt.lower()
        assert "case studies" in prompt.lower()
        assert "research heavy" in prompt.lower() or "research_heavy" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_affiliate_disclosure_compliance_prompts(self, seo_monetization_prompts):
        """Test affiliate disclosure compliance prompts"""
        compliance_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.BASIC,
            monetization_models=[MonetizationModel.AFFILIATE],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.GENERAL,
            target_keywords=[],
            competition_analysis={},
            monetization_goals={},
            technical_requirements={
                "ftc_compliance": True,
                "gdpr_compliance": True,
                "disclosure_placement": "prominent",
                "legal_documentation": True
            },
            audience_data={
                "geographic_locations": ["US", "EU", "CA", "AU"],
                "legal_requirements_awareness": "mixed"
            }
        )
        
        result = await seo_monetization_prompts.generate_compliance_prompt(compliance_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify compliance elements
        assert "disclosure" in prompt.lower()
        assert "ftc" in prompt.lower() or "federal trade commission" in prompt.lower()
        assert "gdpr" in prompt.lower()
        assert "compliance" in prompt.lower()
        assert "prominent" in prompt.lower()
        assert "legal" in prompt.lower()
        assert "affiliate" in prompt.lower()
    
    # ===== TECHNICAL SEO TESTS =====
    
    @pytest.mark.asyncio
    async def test_technical_seo_prompts(self, seo_monetization_prompts):
        """Test technical SEO prompts generation"""
        technical_seo_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.TECHNICAL_SEO,
            monetization_models=[MonetizationModel.SUBSCRIPTION],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=["technical seo guide", "site performance optimization"],
            competition_analysis={},
            monetization_goals={},
            technical_requirements={
                "core_web_vitals_optimization": True,
                "schema_markup_implementation": True,
                "site_speed_optimization": True,
                "mobile_first_indexing": True,
                "crawlability_optimization": True,
                "structured_data": True,
                "canonical_urls": True,
                "xml_sitemaps": True,
                "robots_txt_optimization": True
            },
            audience_data={}
        )
        
        result = await seo_monetization_prompts.generate_technical_seo_prompt(technical_seo_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify technical SEO elements
        assert "technical seo" in prompt.lower() or ("technical" in prompt.lower() and "seo" in prompt.lower())
        assert "core web vitals" in prompt.lower() or "core_web_vitals" in prompt.lower()
        assert "schema markup" in prompt.lower() or "schema_markup" in prompt.lower()
        assert "site speed" in prompt.lower() or "site_speed" in prompt.lower()
        assert "mobile first" in prompt.lower() or "mobile_first" in prompt.lower()
        assert "crawlability" in prompt.lower()
        assert "structured data" in prompt.lower() or "structured_data" in prompt.lower()
        assert "canonical" in prompt.lower()
        assert "sitemap" in prompt.lower()
        assert "robots.txt" in prompt.lower() or "robots" in prompt.lower()
    
    # ===== LOCAL SEO TESTS =====
    
    @pytest.mark.asyncio
    async def test_local_seo_prompts(self, seo_monetization_prompts):
        """Test local SEO prompts generation"""
        local_seo_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.LOCAL_SEO,
            monetization_models=[MonetizationModel.ADVERTISING],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.LOCAL_BUSINESS,
            target_keywords=["music studio Berlin", "audio production services", "recording studio near me"],
            competition_analysis={
                "local_competitors": ["studio_a", "studio_b", "studio_c"],
                "google_my_business_optimization": "needed",
                "local_citation_score": 65,
                "review_average": 4.2
            },
            monetization_goals={
                "local_bookings_target": 50,
                "average_booking_value": 300,
                "repeat_customer_rate": 70
            },
            technical_requirements={
                "google_my_business_optimization": True,
                "local_schema_markup": True,
                "nap_consistency": True,
                "local_citations": True,
                "review_management": True
            },
            audience_data={
                "service_area": "Berlin, Germany",
                "target_demographics": {"age": "25-45", "profession": ["musician", "podcaster", "content_creator"]},
                "search_patterns": "location_based"
            }
        )
        
        result = await seo_monetization_prompts.generate_local_seo_prompt(local_seo_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify local SEO elements
        assert "local seo" in prompt.lower() or ("local" in prompt.lower() and "seo" in prompt.lower())
        assert "google my business" in prompt.lower() or "google_my_business" in prompt.lower()
        assert "berlin" in prompt.lower()
        assert "music studio" in prompt.lower()
        assert "near me" in prompt.lower()
        assert "nap" in prompt.lower() or "name address phone" in prompt.lower()
        assert "citations" in prompt.lower()
        assert "review" in prompt.lower()
        assert "local schema" in prompt.lower() or "local_schema" in prompt.lower()
        assert "booking" in prompt.lower()
    
    # ===== MONETIZATION STRATEGY TESTS =====
    
    @pytest.mark.asyncio
    async def test_subscription_model_prompts(self, seo_monetization_prompts):
        """Test subscription model prompts generation"""
        subscription_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.CONTENT_SEO,
            monetization_models=[MonetizationModel.SUBSCRIPTION],
            platforms=[Platform.DIRECT_WEBSITE],
            content_category=ContentCategory.EDUCATION,
            target_keywords=["premium AI course", "subscription learning", "advanced tutorials"],
            competition_analysis={
                "subscription_market": "growing",
                "average_price_points": {"basic": 29, "premium": 99, "enterprise": 299},
                "churn_rates": {"industry_average": 15, "top_performers": 5},
                "feature_comparison": "comprehensive_needed"
            },
            monetization_goals={
                "monthly_recurring_revenue": 50000,
                "subscriber_acquisition_cost": 75,
                "lifetime_value": 800,
                "churn_rate_target": 8
            },
            technical_requirements={
                "subscription_management": True,
                "payment_processing": True,
                "content_gating": True,
                "user_onboarding": True,
                "retention_automation": True
            },
            audience_data={
                "subscription_readiness": "high",
                "price_sensitivity": "moderate",
                "content_consumption_patterns": "regular_engaged",
                "cancellation_reasons": ["price", "lack_of_time", "content_quality"]
            }
        )
        
        result = await seo_monetization_prompts.generate_subscription_strategy_prompt(subscription_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify subscription strategy elements
        assert "subscription" in prompt.lower()
        assert "recurring revenue" in prompt.lower() or "mrr" in prompt.lower()
        assert "churn" in prompt.lower()
        assert "lifetime value" in prompt.lower() or "ltv" in prompt.lower()
        assert "50000" in prompt or "revenue" in prompt.lower()
        assert "75" in prompt or "acquisition cost" in prompt.lower()
        assert "onboarding" in prompt.lower()
        assert "retention" in prompt.lower()
        assert "premium ai course" in prompt.lower()
        assert "content gating" in prompt.lower() or "gating" in prompt.lower()
    
    # ===== PERFORMANCE AND ANALYTICS TESTS =====
    
    @pytest.mark.asyncio
    async def test_seo_analytics_prompts(self, seo_monetization_prompts):
        """Test SEO analytics prompts generation"""
        analytics_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.ADVANCED,
            monetization_models=[MonetizationModel.ADVERTISING, MonetizationModel.AFFILIATE],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=["seo analytics", "performance tracking", "roi measurement"],
            competition_analysis={},
            monetization_goals={
                "organic_traffic_growth": 150,
                "conversion_rate_improvement": 25,
                "revenue_attribution_accuracy": 90
            },
            technical_requirements={
                "google_analytics_4": True,
                "google_search_console": True,
                "conversion_tracking": True,
                "attribution_modeling": True,
                "custom_dashboards": True
            },
            audience_data={
                "analytics_sophistication": "intermediate",
                "reporting_frequency": "weekly",
                "kpi_priorities": ["traffic", "conversions", "revenue"]
            }
        )
        
        result = await seo_monetization_prompts.generate_analytics_prompt(analytics_context)
        
        assert result["success"] is True
        prompt = result["prompt"]
        
        # Verify analytics elements
        assert "analytics" in prompt.lower()
        assert "google analytics" in prompt.lower() or "ga4" in prompt.lower()
        assert "search console" in prompt.lower()
        assert "conversion tracking" in prompt.lower() or "conversion_tracking" in prompt.lower()
        assert "attribution" in prompt.lower()
        assert "dashboard" in prompt.lower()
        assert "kpi" in prompt.lower() or "performance" in prompt.lower()
        assert "roi" in prompt.lower() or "return on investment" in prompt.lower()
        assert "150" in prompt or "growth" in prompt.lower()
    
    # ===== ERROR HANDLING TESTS =====
    
    @pytest.mark.asyncio
    async def test_invalid_seo_strategy_error(self, seo_monetization_prompts):
        """Test error handling for invalid SEO strategy"""
        with pytest.raises(ValueError) or pytest.raises(TypeError):
            invalid_context = SEOMonetizationContext(
                seo_strategy="invalid_strategy",
                monetization_models=[MonetizationModel.ADVERTISING],
                platforms=[Platform.GOOGLE],
                content_category=ContentCategory.TECHNOLOGY,
                target_keywords=[],
                competition_analysis={},
                monetization_goals={},
                technical_requirements={},
                audience_data={}
            )
            await seo_monetization_prompts.generate_seo_prompt(invalid_context)
    
    @pytest.mark.asyncio
    async def test_missing_monetization_goals_handling(self, seo_monetization_prompts):
        """Test handling of missing monetization goals"""
        minimal_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.BASIC,
            monetization_models=[MonetizationModel.ADVERTISING],
            platforms=[Platform.GOOGLE],
            content_category=ContentCategory.GENERAL,
            target_keywords=["general keywords"],
            competition_analysis={},
            monetization_goals={},  # Empty goals
            technical_requirements={},
            audience_data={}
        )
        
        result = await seo_monetization_prompts.generate_monetization_prompt(minimal_context)
        
        # Should succeed with default goals or provide guidance
        assert result["success"] is True
        assert "prompt" in result
        if "warnings" in result:
            assert len(result["warnings"]) > 0
    
    # ===== PERFORMANCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_seo_prompt_generation_performance(self, seo_monetization_prompts, sample_blog_seo_context):
        """Test SEO prompt generation performance"""
        # Test single generation performance
        start_time = datetime.now()
        result = await seo_monetization_prompts.generate_seo_prompt(sample_blog_seo_context)
        single_duration = (datetime.now() - start_time).total_seconds()
        
        assert result["success"] is True
        assert single_duration < 2.5  # Should complete within 2.5 seconds
        
        # Test batch generation performance
        contexts = [sample_blog_seo_context] * 5
        
        start_time = datetime.now()
        results = await seo_monetization_prompts.generate_batch_seo_prompts(contexts)
        batch_duration = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 5
        assert batch_duration < 8.0  # Should complete within 8 seconds
        assert batch_duration < single_duration * 5  # Should be more efficient
    
    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_comprehensive_seo_monetization_workflow(self, seo_monetization_prompts):
        """Test comprehensive SEO and monetization workflow integration"""
        # Step 1: Market research and keyword analysis
        market_research_result = await seo_monetization_prompts.conduct_market_research({
            "industry": "AI tools and software",
            "target_audience": "content creators and marketers",
            "geographic_focus": "US and EU",
            "budget_range": "mid_tier"
        })
        
        assert market_research_result["success"] is True
        
        # Step 2: SEO strategy development
        seo_strategy_context = SEOMonetizationContext(
            seo_strategy=SEOStrategy.ADVANCED,
            monetization_models=[MonetizationModel.AFFILIATE, MonetizationModel.SUBSCRIPTION],
            platforms=[Platform.GOOGLE, Platform.BING],
            content_category=ContentCategory.TECHNOLOGY,
            target_keywords=market_research_result["recommended_keywords"][:5],
            competition_analysis=market_research_result["competition_analysis"],
            monetization_goals={
                "monthly_revenue_target": 15000,
                "organic_traffic_target": 50000,
                "conversion_rate_target": 3.5
            },
            technical_requirements={
                "advanced_seo_features": True,
                "conversion_optimization": True,
                "performance_tracking": True
            },
            audience_data=market_research_result["audience_insights"]
        )
        
        seo_result = await seo_monetization_prompts.generate_seo_prompt(seo_strategy_context)
        assert seo_result["success"] is True
        
        # Step 3: Content strategy development
        content_strategy_result = await seo_monetization_prompts.generate_content_strategy_prompt(seo_strategy_context)
        assert content_strategy_result["success"] is True
        
        # Step 4: Monetization strategy implementation
        monetization_result = await seo_monetization_prompts.generate_comprehensive_monetization_strategy(seo_strategy_context)
        assert monetization_result["success"] is True
        
        # Step 5: Performance tracking setup
        analytics_result = await seo_monetization_prompts.generate_analytics_prompt(seo_strategy_context)
        assert analytics_result["success"] is True
        
        # Verify workflow coherence
        assert all([
            market_research_result["success"],
            seo_result["success"],
            content_strategy_result["success"],
            monetization_result["success"],
            analytics_result["success"]
        ])
        
        # Verify strategy consistency
        seo_prompt = seo_result["prompt"]
        monetization_prompt = monetization_result["prompt"]
        
        # Check that keywords appear in both strategies
        assert any(keyword.lower() in seo_prompt.lower() for keyword in market_research_result["recommended_keywords"][:3])
        assert any(keyword.lower() in monetization_prompt.lower() for keyword in market_research_result["recommended_keywords"][:3])
        
        # Check revenue targets consistency
        assert "15000" in monetization_prompt or "revenue" in monetization_prompt.lower()
        
        # Step 6: Implementation roadmap
        roadmap_result = await seo_monetization_prompts.generate_implementation_roadmap(seo_strategy_context)
        assert roadmap_result["success"] is True
        assert "implementation_phases" in roadmap_result
        assert len(roadmap_result["implementation_phases"]) >= 3
        
        # Verify roadmap includes all key components
        roadmap_phases = roadmap_result["implementation_phases"]
        phase_names = [phase["name"].lower() for phase in roadmap_phases]
        
        assert any("seo" in name for name in phase_names)
        assert any("content" in name for name in phase_names)
        assert any("monetization" in name or "revenue" in name for name in phase_names)
        assert any("analytics" in name or "tracking" in name for name in phase_names)
