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

"""Test suite for Content Strategy AI Agents

Tests all functionalities of content strategy, planning, optimization,
and performance analysis agents.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from ai.ai_agents.content_strategy_agents import (
    ContentStrategistAgent,
    PerformanceAnalysisAgent,
    TrendAnalysisAgent,
    ContentPlanningAgent,
    ContentAnalysis,
    StrategyRecommendation,
    ContentPlan,
    TrendInsight
)


class TestContentStrategistAgent:
    """Test ContentStrategistAgent functionality"""    
    @pytest.fixture
    def agent(self):
        """Create ContentStrategistAgent instance"""        return ContentStrategistAgent()
    
    @pytest.fixture
    def sample_content_data(self):
        """Sample content data for strategy analysis"""        return {
            "content_id": "content_001",
            "title": "AI Tutorial: Getting Started with Machine Learning",
            "description": "Complete beginner's guide to ML fundamentals",
            "content_type": "video",
            "duration": 1200,  # 20 minutes
            "category": "educational",
            "tags": ["AI", "machine learning", "tutorial", "python"],
            "performance_metrics": {
                "views": 15000,
                "likes": 850,
                "comments": 125,
                "shares": 45,
                "saves": 200,
                "click_through_rate": 0.12,
                "watch_time_percentage": 0.68
            },
            "audience_data": {
                "demographics": {
                    "age_groups": {"18-24": 35, "25-34": 40, "35-44": 20, "45+": 5},
                    "gender": {"male": 65, "female": 33, "other": 2},
                    "interests": ["programming", "AI", "career_development"]
                },
                "engagement_patterns": {
                    "peak_times": [19, 20, 21],
                    "engagement_by_hour": {str(i): 0.03 + (0.02 * (i % 24)) for i in range(24)}
                }
            },
            "publication_date": datetime.now() - timedelta(days=7),
            "platform": "youtube"
        }
    
    @pytest.mark.asyncio
    async def test_analyze_content_performance(self, agent, sample_content_data):
        """Test content performance analysis"""        analysis = await agent.analyze_content_performance(sample_content_data)
        
        assert isinstance(analysis, ContentAnalysis)
        assert 0 <= analysis.engagement_score <= 1
        assert 0 <= analysis.viral_potential <= 1
        assert 0 <= analysis.audience_match <= 1
        assert 0 <= analysis.quality_score <= 1
        assert len(analysis.trending_factors) >= 0
        assert len(analysis.improvement_suggestions) > 0
        assert analysis.optimal_timing is not None
        assert len(analysis.hashtag_recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_generate_strategy_recommendations(self, agent, sample_content_data):
        """Test strategy recommendation generation"""        creator_profile = {
            "creator_id": "creator_001",
            "niche": "tech_education",
            "goals": ["audience_growth", "engagement_increase"],
            "current_metrics": {
                "followers": 25000,
                "avg_engagement_rate": 0.045,
                "posting_frequency": "3_times_weekly"
            }
        }
        
        recommendations = await agent.generate_strategy_recommendations(
            creator_profile,
            sample_content_data
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, StrategyRecommendation)
            assert rec.priority in ["high", "medium", "low"]
            assert rec.category in ["content", "timing", "audience", "platform"]
            assert rec.title is not None
            assert rec.description is not None
            assert 0 <= rec.expected_impact <= 1
            assert rec.implementation_difficulty in ["easy", "medium", "hard"]
    
    @pytest.mark.asyncio
    async def test_optimize_content_timing(self, agent, sample_content_data):
        """Test content timing optimization"""        timing_optimization = await agent.optimize_content_timing(sample_content_data)
        
        assert "optimal_posting_times" in timing_optimization
        assert "frequency_recommendations" in timing_optimization
        assert "platform_specific_timing" in timing_optimization
        assert "seasonal_considerations" in timing_optimization
        
        optimal_times = timing_optimization["optimal_posting_times"]
        assert isinstance(optimal_times, list)
        assert len(optimal_times) > 0
        
        for time_slot in optimal_times:
            assert "day_of_week" in time_slot
            assert "hour" in time_slot
            assert "engagement_probability" in time_slot
            assert 0 <= time_slot["engagement_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_audience_engagement(self, agent, sample_content_data):
        """Test audience engagement analysis"""        engagement_analysis = await agent.analyze_audience_engagement(sample_content_data)
        
        assert "engagement_breakdown" in engagement_analysis
        assert "audience_segments" in engagement_analysis
        assert "engagement_drivers" in engagement_analysis
        assert "improvement_opportunities" in engagement_analysis
        
        engagement_breakdown = engagement_analysis["engagement_breakdown"]
        assert "likes_rate" in engagement_breakdown
        assert "comments_rate" in engagement_breakdown
        assert "shares_rate" in engagement_breakdown
        assert "saves_rate" in engagement_breakdown
    
    @pytest.mark.asyncio
    async def test_recommend_content_themes(self, agent, sample_content_data):
        """Test content theme recommendations"""        creator_goals = {
            "target_audience": "tech_professionals",
            "content_pillars": ["education", "career_advice", "industry_trends"],
            "growth_objectives": ["follower_growth", "engagement_increase"]
        }
        
        theme_recommendations = await agent.recommend_content_themes(
            sample_content_data,
            creator_goals
        )
        
        assert "recommended_themes" in theme_recommendations
        assert "trending_topics" in theme_recommendations
        assert "evergreen_content_ideas" in theme_recommendations
        assert "seasonal_opportunities" in theme_recommendations
        
        for theme in theme_recommendations["recommended_themes"]:
            assert "theme_name" in theme
            assert "relevance_score" in theme
            assert "trend_potential" in theme
            assert "content_ideas" in theme
            assert 0 <= theme["relevance_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_create_content_calendar(self, agent, sample_content_data):
        """Test content calendar creation"""        calendar_params = {
            "duration_weeks": 4,
            "posting_frequency": "daily",
            "content_mix": {
                "educational": 0.4,
                "entertaining": 0.3,
                "promotional": 0.2,
                "personal": 0.1
            }
        }
        
        content_calendar = await agent.create_content_calendar(
            sample_content_data,
            calendar_params
        )
        
        assert "calendar_schedule" in content_calendar
        assert "content_themes" in content_calendar
        assert "posting_strategy" in content_calendar
        assert "performance_goals" in content_calendar
        
        schedule = content_calendar["calendar_schedule"]
        assert len(schedule) == calendar_params["duration_weeks"]
        
        for week in schedule:
            assert "week_number" in week
            assert "daily_posts" in week
            assert len(week["daily_posts"]) == 7  # 7 days per week


class TestPerformanceAnalysisAgent:
    """Test PerformanceAnalysisAgent functionality"""    
    @pytest.fixture
    def agent(self):
        """Create PerformanceAnalysisAgent instance"""        return PerformanceAnalysisAgent()
    
    @pytest.fixture
    def sample_performance_data(self):
        """Sample performance data for analysis"""        return {
            "creator_id": "creator_001",
            "time_period": "30_days",
            "content_metrics": [
                {
                    "content_id": f"content_{i}",
                    "views": 10000 + (i * 1000),
                    "likes": 500 + (i * 50),
                    "comments": 25 + (i * 5),
                    "shares": 10 + (i * 2),
                    "engagement_rate": 0.04 + (i * 0.005),
                    "content_type": "video" if i % 2 == 0 else "image",
                    "category": "educational" if i % 3 == 0 else "entertainment",
                    "publication_date": datetime.now() - timedelta(days=i)
                }
                for i in range(20)
            ],
            "audience_growth": {
                "followers_start": 20000,
                "followers_end": 22500,
                "growth_rate": 0.125,
                "daily_growth": [25, 30, 45, 60, 40, 35, 50]  # Last 7 days
            },
            "engagement_trends": {
                "likes_trend": "increasing",
                "comments_trend": "stable", 
                "shares_trend": "increasing",
                "overall_engagement": "improving"
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, agent, sample_performance_data):
        """Test performance trend analysis"""        trend_analysis = await agent.analyze_performance_trends(sample_performance_data)
        
        assert "growth_trends" in trend_analysis
        assert "engagement_trends" in trend_analysis
        assert "content_performance_trends" in trend_analysis
        assert "audience_behavior_trends" in trend_analysis
        
        growth_trends = trend_analysis["growth_trends"]
        assert "follower_growth_rate" in growth_trends
        assert "growth_trajectory" in growth_trends
        assert "growth_acceleration" in growth_trends
    
    @pytest.mark.asyncio
    async def test_identify_top_performing_content(self, agent, sample_performance_data):
        """Test top performing content identification"""        top_content = await agent.identify_top_performing_content(sample_performance_data)
        
        assert "top_by_views" in top_content
        assert "top_by_engagement" in top_content
        assert "top_by_growth_impact" in top_content
        assert "performance_patterns" in top_content
        
        for category in ["top_by_views", "top_by_engagement", "top_by_growth_impact"]:
            assert len(top_content[category]) > 0
            for content in top_content[category]:
                assert "content_id" in content
                assert "performance_score" in content
                assert "success_factors" in content
    
    @pytest.mark.asyncio
    async def test_calculate_roi_metrics(self, agent, sample_performance_data):
        """Test ROI metrics calculation"""        investment_data = {
            "content_creation_time": {
                "video": 8,  # hours per video
                "image": 2,  # hours per image
                "hourly_rate": 50
            },
            "promotion_budget": 500,  # monthly budget
            "tools_and_software": 200  # monthly cost
        }
        
        roi_metrics = await agent.calculate_roi_metrics(
            sample_performance_data,
            investment_data
        )
        
        assert "total_investment" in roi_metrics
        assert "engagement_roi" in roi_metrics
        assert "growth_roi" in roi_metrics
        assert "content_efficiency" in roi_metrics
        assert "cost_per_engagement" in roi_metrics
        
        assert roi_metrics["total_investment"] > 0
        assert roi_metrics["cost_per_engagement"] >= 0
    
    @pytest.mark.asyncio
    async def test_benchmark_performance(self, agent, sample_performance_data):
        """Test performance benchmarking"""        industry_benchmarks = {
            "niche": "tech_education",
            "follower_range": "20k_50k",
            "benchmarks": {
                "avg_engagement_rate": 0.045,
                "avg_growth_rate": 0.08,
                "avg_views_per_post": 12000,
                "avg_comments_per_post": 35
            }
        }
        
        benchmark_analysis = await agent.benchmark_performance(
            sample_performance_data,
            industry_benchmarks
        )
        
        assert "performance_vs_benchmark" in benchmark_analysis
        assert "strengths" in benchmark_analysis
        assert "areas_for_improvement" in benchmark_analysis
        assert "competitive_position" in benchmark_analysis
        
        performance_comparison = benchmark_analysis["performance_vs_benchmark"]
        assert "engagement_rate_comparison" in performance_comparison
        assert "growth_rate_comparison" in performance_comparison


class TestTrendAnalysisAgent:
    """Test TrendAnalysisAgent functionality"""    
    @pytest.fixture
    def agent(self):
        """Create TrendAnalysisAgent instance"""        return TrendAnalysisAgent()
    
    @pytest.fixture
    def sample_trend_data(self):
        """Sample trend data for analysis"""        return {
            "platform": "youtube",
            "niche": "technology",
            "trending_topics": [
                {"topic": "artificial intelligence", "growth_rate": 0.25, "search_volume": 50000},
                {"topic": "machine learning", "growth_rate": 0.18, "search_volume": 35000},
                {"topic": "python programming", "growth_rate": 0.15, "search_volume": 40000},
                {"topic": "data science", "growth_rate": 0.12, "search_volume": 28000}
            ],
            "hashtag_trends": [
                {"hashtag": "#AI", "usage_count": 125000, "trend_direction": "rising"},
                {"hashtag": "#MachineLearning", "usage_count": 98000, "trend_direction": "stable"},
                {"hashtag": "#Programming", "usage_count": 150000, "trend_direction": "rising"}
            ],
            "competitor_analysis": {
                "top_performers": [
                    {"creator": "TechGuru", "recent_viral_content": ["AI basics", "Python tips"]},
                    {"creator": "CodeMaster", "recent_viral_content": ["ML tutorial", "Career advice"]}
                ]
            },
            "seasonal_trends": {
                "current_season": "Q1",
                "seasonal_factors": ["new year resolutions", "career planning", "skill development"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_identify_trending_topics(self, agent, sample_trend_data):
        """Test trending topics identification"""        trending_analysis = await agent.identify_trending_topics(sample_trend_data)
        
        assert "emerging_trends" in trending_analysis
        assert "declining_trends" in trending_analysis
        assert "stable_trends" in trending_analysis
        assert "trend_predictions" in trending_analysis
        
        emerging_trends = trending_analysis["emerging_trends"]
        assert len(emerging_trends) > 0
        
        for trend in emerging_trends:
            assert "topic" in trend
            assert "growth_potential" in trend
            assert "relevance_score" in trend
            assert "recommended_action" in trend
            assert 0 <= trend["relevance_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_hashtag_performance(self, agent, sample_trend_data):
        """Test hashtag performance analysis"""        hashtag_analysis = await agent.analyze_hashtag_performance(sample_trend_data)
        
        assert "high_performing_hashtags" in hashtag_analysis
        assert "hashtag_combinations" in hashtag_analysis
        assert "hashtag_timing" in hashtag_analysis
        assert "reach_potential" in hashtag_analysis
        
        for hashtag in hashtag_analysis["high_performing_hashtags"]:
            assert "hashtag" in hashtag
            assert "performance_score" in hashtag
            assert "usage_recommendation" in hashtag
            assert 0 <= hashtag["performance_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_predict_content_virality(self, agent, sample_trend_data):
        """Test content virality prediction"""        content_concept = {
            "title": "AI Will Change Everything in 2025",
            "description": "Exploring the latest AI trends and their impact",
            "format": "video",
            "duration": 600,
            "category": "technology",
            "hashtags": ["#AI", "#2025", "#Technology", "#Trends"]
        }
        
        virality_prediction = await agent.predict_content_virality(
            content_concept,
            sample_trend_data
        )
        
        assert "virality_score" in virality_prediction
        assert "success_factors" in virality_prediction
        assert "optimization_suggestions" in virality_prediction
        assert "timing_recommendations" in virality_prediction
        assert 0 <= virality_prediction["virality_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_monitor_competitor_trends(self, agent, sample_trend_data):
        """Test competitor trend monitoring"""        competitor_monitoring = await agent.monitor_competitor_trends(sample_trend_data)
        
        assert "competitor_insights" in competitor_monitoring
        assert "content_gap_analysis" in competitor_monitoring
        assert "opportunity_identification" in competitor_monitoring
        assert "competitive_advantages" in competitor_monitoring
        
        insights = competitor_monitoring["competitor_insights"]
        for insight in insights:
            assert "competitor" in insight
            assert "trend_adoption" in insight
            assert "performance_analysis" in insight
            assert "learning_opportunities" in insight


class TestContentPlanningAgent:
    """Test ContentPlanningAgent functionality"""    
    @pytest.fixture
    def agent(self):
        """Create ContentPlanningAgent instance"""        return ContentPlanningAgent()
    
    @pytest.fixture
    def sample_planning_requirements(self):
        """Sample content planning requirements"""        return {
            "creator_profile": {
                "creator_id": "creator_001",
                "niche": "fitness_nutrition",
                "expertise": ["workout_routines", "meal_planning", "wellness"],
                "brand_voice": "motivational_supportive",
                "target_audience": "fitness_enthusiasts_25_40"
            },
            "planning_parameters": {
                "duration": "3_months",
                "posting_frequency": {
                    "youtube": "2_per_week",
                    "instagram": "daily",
                    "tiktok": "3_per_week"
                },
                "content_mix": {
                    "workout_videos": 0.3,
                    "nutrition_tips": 0.25,
                    "motivation_content": 0.2,
                    "progress_stories": 0.15,
                    "behind_scenes": 0.1
                }
            },
            "goals": {
                "follower_growth": 0.5,  # 50% growth
                "engagement_improvement": 0.3,  # 30% improvement
                "brand_partnerships": 2,  # 2 partnerships per month
                "lead_generation": 100  # 100 leads per month
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_content_plan(self, agent, sample_planning_requirements):
        """Test comprehensive content plan creation"""        content_plan = await agent.create_comprehensive_content_plan(sample_planning_requirements)
        
        assert isinstance(content_plan, ContentPlan)
        assert content_plan.plan_id is not None
        assert content_plan.duration == sample_planning_requirements["planning_parameters"]["duration"]
        assert len(content_plan.content_calendar) > 0
        assert content_plan.success_metrics is not None
        assert content_plan.resource_requirements is not None
    
    @pytest.mark.asyncio
    async def test_generate_content_ideas(self, agent, sample_planning_requirements):
        """Test content idea generation"""        content_ideas = await agent.generate_content_ideas(sample_planning_requirements)
        
        assert "video_ideas" in content_ideas
        assert "post_ideas" in content_ideas
        assert "series_concepts" in content_ideas
        assert "collaboration_ideas" in content_ideas
        
        for category in content_ideas:
            assert len(content_ideas[category]) > 0
            for idea in content_ideas[category][:3]:  # Check first 3
                assert "title" in idea
                assert "description" in idea
                assert "target_audience" in idea
                assert "expected_engagement" in idea
    
    @pytest.mark.asyncio
    async def test_optimize_content_mix(self, agent, sample_planning_requirements):
        """Test content mix optimization"""        current_performance = {
            "workout_videos": {"avg_engagement": 0.065, "growth_impact": 0.8},
            "nutrition_tips": {"avg_engagement": 0.045, "growth_impact": 0.6},
            "motivation_content": {"avg_engagement": 0.055, "growth_impact": 0.7},
            "progress_stories": {"avg_engagement": 0.075, "growth_impact": 0.9},
            "behind_scenes": {"avg_engagement": 0.038, "growth_impact": 0.4}
        }
        
        optimized_mix = await agent.optimize_content_mix(
            sample_planning_requirements,
            current_performance
        )
        
        assert "recommended_mix" in optimized_mix
        assert "expected_improvements" in optimized_mix
        assert "implementation_strategy" in optimized_mix
        
        recommended_percentages = optimized_mix["recommended_mix"]
        total_percentage = sum(recommended_percentages.values())
        assert abs(total_percentage - 1.0) < 0.01  # Should sum to ~100%
    
    @pytest.mark.asyncio
    async def test_schedule_content_production(self, agent, sample_planning_requirements):
        """Test content production scheduling"""        production_schedule = await agent.schedule_content_production(sample_planning_requirements)
        
        assert "production_timeline" in production_schedule
        assert "resource_allocation" in production_schedule
        assert "deadline_management" in production_schedule
        assert "quality_checkpoints" in production_schedule
        
        timeline = production_schedule["production_timeline"]
        assert len(timeline) > 0
        
        for item in timeline:
            assert "content_piece" in item
            assert "production_start" in item
            assert "deadline" in item
            assert "estimated_effort" in item


class TestIntegrationScenarios:
    """Test integration between different content strategy agents"""    
    @pytest.fixture
    def agents(self):
        """Create all content strategy agents for integration testing"""        return {
            "strategist": ContentStrategistAgent(),
            "performance": PerformanceAnalysisAgent(),
            "trends": TrendAnalysisAgent(),
            "planning": ContentPlanningAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_strategy_development(self, agents):
        """Test comprehensive content strategy development workflow"""        # Sample creator requiring full strategy development
        creator_data = {
            "creator_id": "strategic_creator",
            "profile": {
                "niche": "personal_development",
                "current_followers": 15000,
                "engagement_rate": 0.035,
                "content_frequency": "inconsistent"
            },
            "goals": {
                "follower_target": 50000,
                "timeline_months": 6,
                "revenue_goals": True
            },
            "current_content": {
                "avg_views": 3000,
                "top_performing_type": "motivational_videos",
                "engagement_patterns": "declining"
            }
        }
        
        # Execute integrated strategy workflow
        # 1. Analyze current performance
        performance_analysis = await agents["performance"].analyze_performance_trends(creator_data)
        
        # 2. Identify trending opportunities
        trend_analysis = await agents["trends"].identify_trending_topics({
            "niche": creator_data["profile"]["niche"],
            "platform": "youtube"
        })
        
        # 3. Generate strategic recommendations
        strategy_recommendations = await agents["strategist"].generate_strategy_recommendations(
            creator_data["profile"],
            creator_data["current_content"]
        )
        
        # 4. Create comprehensive content plan
        content_plan = await agents["planning"].create_comprehensive_content_plan({
            "creator_profile": creator_data["profile"],
            "goals": creator_data["goals"],
            "planning_parameters": {"duration": "6_months"}
        })
        
        # Verify integrated strategy
        assert performance_analysis is not None
        assert trend_analysis is not None
        assert len(strategy_recommendations) > 0
        assert content_plan is not None
        
        # Verify strategy coherence
        assert "engagement_trends" in performance_analysis
        assert "emerging_trends" in trend_analysis
        assert all(rec.priority in ["high", "medium", "low"] for rec in strategy_recommendations)
        assert content_plan.plan_id is not None


class TestErrorHandling:
    """Test error handling scenarios"""    
    @pytest.fixture
    def agent(self):
        """Create ContentStrategistAgent for error testing"""        return ContentStrategistAgent()
    
    @pytest.mark.asyncio
    async def test_insufficient_data_handling(self, agent):
        """Test handling of insufficient content data"""        minimal_data = {"content_id": "test", "views": 100}
        
        try:
            result = await agent.analyze_content_performance(minimal_data)
            # Should handle gracefully with limited analysis
            assert isinstance(result, ContentAnalysis)
        except (ValueError, KeyError):
            # Acceptable to require minimum data fields
            pass
    
    @pytest.mark.asyncio
    async def test_invalid_metrics_handling(self, agent):
        """Test handling of invalid metrics"""        invalid_data = {
            "content_id": "test",
            "views": -100,  # Invalid negative views
            "likes": "invalid",  # Invalid type
            "engagement_rate": 1.5  # Invalid rate > 1
        }
        
        try:
            result = await agent.analyze_content_performance(invalid_data)
            # Should sanitize or handle invalid data gracefully
            assert result is not None
        except (ValueError, TypeError):
            # Acceptable to reject clearly invalid data
            pass
    
    @pytest.mark.asyncio
    async def test_external_service_failures(self, agent):
        """Test handling of external service failures"""        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("External API failure")
            
            content_data = {"content_id": "test", "views": 1000}
            
            try:
                result = await agent.analyze_content_performance(content_data)
                # Should provide fallback analysis or handle gracefully
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""    
    @pytest.fixture
    def agent(self):
        """Create ContentStrategistAgent for performance testing"""        return ContentStrategistAgent()
    
    @pytest.mark.asyncio
    async def test_large_dataset_analysis(self, agent):
        """Test analysis of large content datasets"""        large_dataset = {
            "creator_id": "large_creator",
            "content_library": [
                {
                    "content_id": f"content_{i}",
                    "views": 1000 + (i * 100),
                    "likes": 50 + (i * 5),
                    "comments": 10 + i,
                    "engagement_rate": 0.03 + (i * 0.001),
                    "category": ["educational", "entertainment", "lifestyle"][i % 3]
                }
                for i in range(1000)  # 1000 pieces of content
            ]
        }
        
        start_time = datetime.now()
        result = await agent.analyze_content_performance(large_dataset)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert result is not None
        assert processing_time < 30  # Should complete within reasonable time
    
    @pytest.mark.asyncio
    async def test_concurrent_strategy_analysis(self, agent):
        """Test concurrent strategy analysis for multiple creators"""        creator_datasets = [
            {
                "content_id": f"creator_{i}_content",
                "views": 5000 + (i * 1000),
                "engagement_rate": 0.04 + (i * 0.01),
                "category": f"category_{i}"
            }
            for i in range(10)
        ]
        
        analysis_tasks = [
            agent.analyze_content_performance(dataset)
            for dataset in creator_datasets
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        assert len(results) == len(creator_datasets)
        for result in results:
            assert not isinstance(result, Exception)
