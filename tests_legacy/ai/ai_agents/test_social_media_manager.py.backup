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

"""Comprehensive Tests for SocialMediaManagerAgent

Industrial-grade testing for social media management including cross-platform posting,
engagement optimization, hashtag strategies, optimal timing, and audience analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import logging

from ai.ai_agents import (
    SocialMediaManagerAgent,
    AgentConfiguration,
    AgentCapability
)

logger = logging.getLogger(__name__)


class TestSocialMediaManagerAgent:
    """Comprehensive test suite for SocialMediaManagerAgent"""
    
    @pytest.fixture
    def social_media_config(self) -> AgentConfiguration:
        """Social media manager agent configuration"""
        return AgentConfiguration(
            agent_id="social_media_test",
            agent_name="Test Social Media Manager",
            capabilities={
                AgentCapability.platform_posting,
                AgentCapability.engagement_management,
                AgentCapability.hashtag_optimization,
                AgentCapability.cross_platform_sync,
                AgentCapability.audience_analysis,
                AgentCapability.trend_analysis,
                AgentCapability.real_time_processing,
                AgentCapability.performance_analysis
            },
            max_concurrent_tasks=10,
            default_timeout=30,
            custom_settings={
                "auto_posting_enabled": True,
                "engagement_auto_response": True,
                "hashtag_research_depth": "comprehensive",
                "cross_platform_optimization": True,
                "analytics_integration": True,
                "content_scheduling": True
            }
        )
    
    @pytest.fixture
    async def social_agent(self, social_media_config) -> SocialMediaManagerAgent:
        """Initialized social media manager agent"""
        agent = SocialMediaManagerAgent(social_media_config)
        await agent.initialize()
        
        yield agent
        
        await agent.shutdown()
    
    async def test_agent_initialization(self, social_media_config):
        """Test social media manager initialization"""
        agent = SocialMediaManagerAgent(social_media_config)
        
        # Before initialization
        assert not agent.initialized
        assert agent.status.name == "CREATED"
        
        # Initialize
        result = await agent.initialize()
        
        # After initialization
        assert result is True
        assert agent.initialized
        assert agent.status.name == "READY"
        
        # Verify capabilities
        assert agent.has_capability(AgentCapability.platform_posting)
        assert agent.has_capability(AgentCapability.engagement_management)
        assert agent.has_capability(AgentCapability.hashtag_optimization)
        assert agent.has_capability(AgentCapability.cross_platform_sync)
        
        # Verify settings
        assert agent.get_setting("auto_posting_enabled") is True
        assert agent.get_setting("engagement_auto_response") is True
        
        await agent.shutdown()
    
    async def test_platform_posting(self, social_agent, test_social_media_data):
        """Test platform-specific posting"""
        post_request = {
            "task_type": "platform_posting",
            "platform": "instagram",
            "content": {
                "text": "Check out this amazing AI tool! 🚀 #AI #Innovation #TechTrends",
                "image_url": "https://example.com/image.jpg",
                "video_url": None
            },
            "post_type": "feed_post",
            "scheduling": {
                "post_time": "immediate",
                "timezone": "UTC"
            }
        }
        
        result = await social_agent.process_task(post_request)
        
        # Verify successful posting
        assert result["success"] is True
        assert "post_result" in result
        
        post_result = result["post_result"]
        assert "post_id" in post_result
        assert "platform" in post_result
        assert "status" in post_result
        assert "published_at" in post_result
        
        # Verify platform optimization
        assert post_result["platform"] == "instagram"
        assert post_result["status"] in ["published", "scheduled", "pending"]
        
        # Verify content optimization
        assert "optimized_content" in post_result
        optimized = post_result["optimized_content"]
        assert "text" in optimized
        assert "hashtags" in optimized
        
        # Instagram-specific validations
        hashtags = optimized["hashtags"]
        assert len(hashtags) <= 30  # Instagram hashtag limit
        assert all(tag.startswith("#") for tag in hashtags)
    
    async def test_cross_platform_posting(self, social_agent):
        """Test cross-platform content distribution"""
        cross_platform_request = {
            "task_type": "cross_platform_posting",
            "content": {
                "base_text": "Exciting news about AI advancements in content creation!",
                "media": {
                    "image_url": "https://example.com/ai-image.jpg",
                    "video_url": "https://example.com/ai-video.mp4"
                }
            },
            "platforms": ["instagram", "tiktok", "twitter", "linkedin"],
            "optimization_level": "high",
            "scheduling": {
                "strategy": "optimal_timing",
                "timezone": "UTC"
            }
        }
        
        result = await social_agent.process_task(cross_platform_request)
        
        # Verify successful cross-platform posting
        assert result["success"] is True
        assert "platform_results" in result
        
        platform_results = result["platform_results"]
        
        # Should have results for all requested platforms
        assert len(platform_results) == 4
        assert "instagram" in platform_results
        assert "tiktok" in platform_results
        assert "twitter" in platform_results
        assert "linkedin" in platform_results
        
        # Verify each platform result
        for platform, platform_result in platform_results.items():
            assert "post_id" in platform_result
            assert "status" in platform_result
            assert "optimized_content" in platform_result
            assert "scheduled_time" in platform_result
            
            optimized_content = platform_result["optimized_content"]
            
            # Platform-specific optimizations
            if platform == "twitter":
                # Twitter character limit
                assert len(optimized_content["text"]) <= 280
            elif platform == "linkedin":
                # LinkedIn should be more professional
                assert "professional_tone" in optimized_content
            elif platform == "tiktok":
                # TikTok should have trending elements
                assert "trending_hashtags" in optimized_content
            elif platform == "instagram":
                # Instagram should have visual focus
                assert "visual_optimization" in optimized_content
    
    async def test_hashtag_optimization(self, social_agent):
        """Test hashtag research and optimization"""
        hashtag_request = {
            "task_type": "hashtag_optimization",
            "content_topic": "AI and machine learning",
            "platform": "instagram",
            "target_audience": "tech_professionals",
            "campaign_goals": ["reach", "engagement", "brand_awareness"],
            "competitor_analysis": True,
            "trending_analysis": True
        }
        
        result = await social_agent.process_task(hashtag_request)
        
        # Verify successful hashtag optimization
        assert result["success"] is True
        assert "hashtag_strategy" in result
        
        strategy = result["hashtag_strategy"]
        assert "recommended_hashtags" in strategy
        assert "hashtag_categories" in strategy
        assert "performance_predictions" in strategy
        assert "trending_analysis" in strategy
        
        # Verify recommended hashtags
        recommended = strategy["recommended_hashtags"]
        assert "primary" in recommended
        assert "secondary" in recommended
        assert "trending" in recommended
        assert "branded" in recommended
        
        # Verify hashtag categories
        categories = strategy["hashtag_categories"]
        assert "high_volume" in categories
        assert "medium_volume" in categories
        assert "niche" in categories
        
        # Verify performance predictions
        predictions = strategy["performance_predictions"]
        for category in ["primary", "secondary", "trending"]:
            if category in recommended:
                assert category in predictions
                prediction = predictions[category]
                assert "estimated_reach" in prediction
                assert "engagement_rate" in prediction
                assert "competition_level" in prediction
        
        # Verify trending analysis
        trending = strategy["trending_analysis"]
        assert "current_trends" in trending
        assert "emerging_trends" in trending
        assert "trend_longevity" in trending
    
    async def test_optimal_timing_analysis(self, social_agent, test_social_media_data):
        """Test optimal posting time analysis"""
        timing_request = {
            "task_type": "optimal_timing_analysis",
            "platform": "instagram",
            "audience_data": test_social_media_data["audience_data"],
            "content_type": "image_post",
            "analysis_period": "last_30_days",
            "timezone": "UTC"
        }
        
        result = await social_agent.process_task(timing_request)
        
        # Verify successful timing analysis
        assert result["success"] is True
        assert "timing_analysis" in result
        
        analysis = result["timing_analysis"]
        assert "optimal_times" in analysis
        assert "audience_activity" in analysis
        assert "engagement_patterns" in analysis
        assert "recommendations" in analysis
        
        # Verify optimal times
        optimal_times = analysis["optimal_times"]
        assert "daily" in optimal_times
        assert "weekly" in optimal_times
        
        daily_times = optimal_times["daily"]
        assert len(daily_times) > 0
        for time_slot in daily_times:
            assert "time" in time_slot
            assert "engagement_score" in time_slot
            assert "audience_size" in time_slot
        
        # Verify audience activity
        activity = analysis["audience_activity"]
        assert "peak_hours" in activity
        assert "active_days" in activity
        assert "timezone_distribution" in activity
        
        # Verify engagement patterns
        patterns = analysis["engagement_patterns"]
        assert "hourly_engagement" in patterns
        assert "daily_engagement" in patterns
        assert "content_type_performance" in patterns
        
        # Verify recommendations
        recommendations = analysis["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "time" in rec
            assert "reason" in rec
            assert "expected_performance" in rec
    
    async def test_engagement_management(self, social_agent):
        """Test engagement management and response automation"""
        engagement_request = {
            "task_type": "engagement_management",
            "platform": "instagram",
            "post_id": "test_post_123",
            "engagement_data": {
                "comments": [
                    {"id": "c1", "text": "Great content!", "user": "user1", "sentiment": "positive"},
                    {"id": "c2", "text": "How does this work?", "user": "user2", "sentiment": "neutral"},
                    {"id": "c3", "text": "Amazing innovation! 🔥", "user": "user3", "sentiment": "positive"}
                ],
                "mentions": [
                    {"id": "m1", "text": "@brand this is incredible", "user": "user4", "sentiment": "positive"}
                ],
                "direct_messages": [
                    {"id": "dm1", "text": "Can you tell me more about this?", "user": "user5"}
                ]
            },
            "response_strategy": "proactive",
            "brand_voice": "friendly_professional"
        }
        
        result = await social_agent.process_task(engagement_request)
        
        # Verify successful engagement management
        assert result["success"] is True
        assert "engagement_actions" in result
        
        actions = result["engagement_actions"]
        assert "comment_responses" in actions
        assert "mention_responses" in actions
        assert "dm_responses" in actions
        assert "engagement_analytics" in actions
        
        # Verify comment responses
        comment_responses = actions["comment_responses"]
        assert len(comment_responses) > 0
        for response in comment_responses:
            assert "comment_id" in response
            assert "response_text" in response
            assert "response_type" in response
            assert "priority" in response
        
        # Verify mention responses
        mention_responses = actions["mention_responses"]
        assert len(mention_responses) > 0
        for response in mention_responses:
            assert "mention_id" in response
            assert "response_text" in response
            assert "engagement_type" in response
        
        # Verify DM responses
        dm_responses = actions["dm_responses"]
        assert len(dm_responses) > 0
        for response in dm_responses:
            assert "dm_id" in response
            assert "response_text" in response
            assert "response_tone" in response
        
        # Verify engagement analytics
        analytics = actions["engagement_analytics"]
        assert "sentiment_analysis" in analytics
        assert "engagement_rate" in analytics
        assert "response_time" in analytics
        assert "user_satisfaction" in analytics
    
    async def test_audience_analysis(self, social_agent, test_social_media_data):
        """Test audience analysis and segmentation"""
        audience_request = {
            "task_type": "audience_analysis",
            "platform": "instagram",
            "analysis_type": "comprehensive",
            "data_sources": ["followers", "engagement", "content_interaction"],
            "time_period": "last_90_days"
        }
        
        result = await social_agent.process_task(audience_request)
        
        # Verify successful audience analysis
        assert result["success"] is True
        assert "audience_insights" in result
        
        insights = result["audience_insights"]
        assert "demographics" in insights
        assert "interests" in insights
        assert "behavior_patterns" in insights
        assert "engagement_preferences" in insights
        assert "growth_trends" in insights
        
        # Verify demographics
        demographics = insights["demographics"]
        assert "age_distribution" in demographics
        assert "gender_distribution" in demographics
        assert "location_distribution" in demographics
        assert "language_preferences" in demographics
        
        # Verify interests
        interests = insights["interests"]
        assert "top_interests" in interests
        assert "interest_categories" in interests
        assert "interest_evolution" in interests
        
        # Verify behavior patterns
        behavior = insights["behavior_patterns"]
        assert "activity_times" in behavior
        assert "content_preferences" in behavior
        assert "interaction_patterns" in behavior
        assert "platform_usage" in behavior
        
        # Verify engagement preferences
        engagement_prefs = insights["engagement_preferences"]
        assert "content_types" in engagement_prefs
        assert "posting_frequency" in engagement_prefs
        assert "interaction_styles" in engagement_prefs
        
        # Verify growth trends
        growth = insights["growth_trends"]
        assert "follower_growth" in growth
        assert "engagement_growth" in growth
        assert "reach_trends" in growth
    
    async def test_content_scheduling(self, social_agent):
        """Test content scheduling and calendar management"""
        scheduling_request = {
            "task_type": "content_scheduling",
            "platform": "instagram",
            "content_queue": [
                {
                    "content_id": "content_1",
                    "text": "Monday motivation with AI! 💪",
                    "media_url": "https://example.com/monday.jpg",
                    "content_type": "motivational"
                },
                {
                    "content_id": "content_2", 
                    "text": "Tech Tuesday: AI innovations 🤖",
                    "media_url": "https://example.com/tuesday.jpg",
                    "content_type": "educational"
                },
                {
                    "content_id": "content_3",
                    "text": "Wisdom Wednesday insights 💡",
                    "media_url": "https://example.com/wednesday.jpg",
                    "content_type": "insights"
                }
            ],
            "scheduling_strategy": "optimal_engagement",
            "frequency": "daily",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "duration_days": 7
        }
        
        result = await social_agent.process_task(scheduling_request)
        
        # Verify successful scheduling
        assert result["success"] is True
        assert "schedule" in result
        
        schedule = result["schedule"]
        assert "posts" in schedule
        assert "calendar" in schedule
        assert "optimization_metrics" in schedule
        
        # Verify posts scheduling
        posts = schedule["posts"]
        assert len(posts) >= 3  # At least the queued content
        for post in posts:
            assert "content_id" in post
            assert "scheduled_time" in post
            assert "platform" in post
            assert "optimization_score" in post
        
        # Verify calendar
        calendar = schedule["calendar"]
        assert "weekly_distribution" in calendar
        assert "daily_schedule" in calendar
        assert "content_mix" in calendar
        
        # Verify optimization metrics
        optimization = schedule["optimization_metrics"]
        assert "engagement_forecast" in optimization
        assert "reach_estimate" in optimization
        assert "optimal_timing_score" in optimization
    
    async def test_competitor_analysis(self, social_agent):
        """Test competitor analysis and benchmarking"""
        competitor_request = {
            "task_type": "competitor_analysis",
            "platform": "instagram",
            "competitors": [
                {"handle": "@competitor1", "industry": "tech"},
                {"handle": "@competitor2", "industry": "tech"},
                {"handle": "@competitor3", "industry": "ai_tools"}
            ],
            "analysis_metrics": [
                "engagement_rate", "posting_frequency", "content_strategy",
                "hashtag_usage", "growth_rate", "audience_overlap"
            ],
            "time_period": "last_30_days"
        }
        
        result = await social_agent.process_task(competitor_request)
        
        # Verify successful competitor analysis
        assert result["success"] is True
        assert "competitor_insights" in result
        
        insights = result["competitor_insights"]
        assert "individual_analysis" in insights
        assert "comparative_analysis" in insights
        assert "opportunities" in insights
        assert "benchmarks" in insights
        
        # Verify individual analysis
        individual = insights["individual_analysis"]
        assert len(individual) == 3  # Three competitors
        for competitor_handle, analysis in individual.items():
            assert "engagement_metrics" in analysis
            assert "content_strategy" in analysis
            assert "posting_patterns" in analysis
            assert "audience_analysis" in analysis
        
        # Verify comparative analysis
        comparative = insights["comparative_analysis"]
        assert "performance_ranking" in comparative
        assert "strategy_differences" in comparative
        assert "market_positioning" in comparative
        
        # Verify opportunities
        opportunities = insights["opportunities"]
        assert "content_gaps" in opportunities
        assert "engagement_improvements" in opportunities
        assert "hashtag_opportunities" in opportunities
        
        # Verify benchmarks
        benchmarks = insights["benchmarks"]
        assert "industry_averages" in benchmarks
        assert "performance_targets" in benchmarks
        assert "competitive_position" in benchmarks
    
    async def test_crisis_management(self, social_agent):
        """Test social media crisis management"""
        crisis_request = {
            "task_type": "crisis_management",
            "platform": "twitter",
            "crisis_type": "negative_feedback",
            "severity": "medium",
            "incident_data": {
                "trigger_post": "post_123",
                "negative_comments": [
                    {"text": "This doesn't work as advertised", "user": "angry_user1"},
                    {"text": "Terrible customer service", "user": "upset_user2"}
                ],
                "viral_potential": "medium",
                "media_attention": False
            },
            "response_strategy": "proactive_transparent"
        }
        
        result = await social_agent.process_task(crisis_request)
        
        # Verify successful crisis management
        assert result["success"] is True
        assert "crisis_response" in result
        
        response = result["crisis_response"]
        assert "immediate_actions" in response
        assert "response_messages" in response
        assert "monitoring_plan" in response
        assert "escalation_procedures" in response
        
        # Verify immediate actions
        immediate = response["immediate_actions"]
        assert "priority" in immediate
        assert "actions" in immediate
        assert isinstance(immediate["actions"], list)
        
        # Verify response messages
        messages = response["response_messages"]
        assert "public_response" in messages
        assert "private_responses" in messages
        assert "stakeholder_communication" in messages
        
        # Verify monitoring plan
        monitoring = response["monitoring_plan"]
        assert "keywords_to_track" in monitoring
        assert "monitoring_frequency" in monitoring
        assert "escalation_triggers" in monitoring
        
        # Verify escalation procedures
        escalation = response["escalation_procedures"]
        assert "severity_levels" in escalation
        assert "contact_hierarchy" in escalation
        assert "decision_matrix" in escalation
    
    async def test_performance_analytics(self, social_agent, test_social_media_data):
        """Test social media performance analytics"""
        analytics_request = {
            "task_type": "performance_analytics",
            "platform": "instagram",
            "metrics": [
                "engagement_rate", "reach", "impressions", "saves",
                "shares", "comments", "likes", "story_views"
            ],
            "time_period": "last_30_days",
            "content_analysis": True,
            "audience_insights": True,
            "competitor_benchmarking": True
        }
        
        result = await social_agent.process_task(analytics_request)
        
        # Verify successful analytics
        assert result["success"] is True
        assert "analytics_report" in result
        
        report = result["analytics_report"]
        assert "summary_metrics" in report
        assert "content_performance" in report
        assert "audience_insights" in report
        assert "trends_analysis" in report
        assert "recommendations" in report
        
        # Verify summary metrics
        summary = report["summary_metrics"]
        for metric in ["engagement_rate", "reach", "impressions"]:
            assert metric in summary
            metric_data = summary[metric]
            assert "current_value" in metric_data
            assert "previous_period" in metric_data
            assert "change_percentage" in metric_data
        
        # Verify content performance
        content_perf = report["content_performance"]
        assert "top_performing_posts" in content_perf
        assert "content_type_analysis" in content_perf
        assert "posting_time_analysis" in content_perf
        
        # Verify audience insights
        audience = report["audience_insights"]
        assert "growth_metrics" in audience
        assert "engagement_patterns" in audience
        assert "demographic_changes" in audience
        
        # Verify trends analysis
        trends = report["trends_analysis"]
        assert "performance_trends" in trends
        assert "seasonal_patterns" in trends
        assert "prediction_models" in trends
        
        # Verify recommendations
        recommendations = report["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "category" in rec
            assert "recommendation" in rec
            assert "expected_impact" in rec
    
    async def test_concurrent_platform_management(self, social_agent):
        """Test concurrent multi-platform management"""
        platforms = ["instagram", "twitter", "linkedin", "tiktok"]
        tasks = []
        
        # Create concurrent tasks for different platforms
        for platform in platforms:
            task = {
                "task_type": "platform_posting",
                "platform": platform,
                "content": {
                    "text": f"Platform-specific content for {platform}",
                    "hashtags": ["#AI", "#SocialMedia", "#Innovation"]
                },
                "optimization": True
            }
            tasks.append(social_agent.process_task(task))
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all platforms handled successfully
        assert len(results) == 4
        for i, result in enumerate(results):
            assert result["success"] is True
            assert "post_result" in result
            assert result["post_result"]["platform"] == platforms[i]
    
    @pytest.mark.performance
    async def test_social_media_performance(self, social_agent, assert_performance):
        """Test social media management performance"""
        # Test posting performance
        post_task = {
            "task_type": "platform_posting",
            "platform": "instagram",
            "content": {
                "text": "Performance test post",
                "hashtags": ["#test", "#performance"]
            }
        }
        
        result = await social_agent.process_task(post_task)
        assert_performance("platform_posting", max_time=5.0)
        assert result["success"] is True
        
        # Test hashtag optimization performance
        hashtag_task = {
            "task_type": "hashtag_optimization",
            "content_topic": "AI performance",
            "platform": "instagram"
        }
        
        result = await social_agent.process_task(hashtag_task)
        assert_performance("hashtag_optimization", max_time=10.0)
        assert result["success"] is True
    
    async def test_error_handling(self, social_agent):
        """Test error handling in social media management"""
        # Test invalid platform
        invalid_platform_task = {
            "task_type": "platform_posting",
            "platform": "invalid_platform",
            "content": {"text": "test"}
        }
        
        result = await social_agent.process_task(invalid_platform_task)
        assert result["success"] is False
        assert "error" in result
        
        # Test missing content
        missing_content_task = {
            "task_type": "platform_posting",
            "platform": "instagram"
            # Missing content
        }
        
        result = await social_agent.process_task(missing_content_task)
        assert result["success"] is False
        assert "error" in result
        
        # Agent should remain functional
        valid_task = {
            "task_type": "platform_posting",
            "platform": "instagram",
            "content": {"text": "Recovery test"}
        }
        
        result = await social_agent.process_task(valid_task)
        assert result["success"] is True
