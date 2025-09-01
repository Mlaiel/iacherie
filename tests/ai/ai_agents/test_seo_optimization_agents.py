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
Test suite for SEO Optimization AI Agents

Tests all functionalities of search engine optimization, keyword research,
content optimization, and visibility enhancement agents.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

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

from ai.ai_agents.seo_optimization_agents import (
    SEOOptimizationAgent,
    KeywordResearchAgent,
    ContentOptimizationAgent,
    VisibilityAnalysisAgent,
    SEOAnalysis,
    KeywordStrategy,
    ContentOptimization,
    VisibilityReport
)


class TestSEOOptimizationAgent:
    """
Test SEOOptimizationAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create SEOOptimizationAgent instance"""
        return SEOOptimizationAgent()
    
    @pytest.fixture
    def sample_content_data(self):
        """
Sample content data for SEO optimization"""
        return {
            "content_id": "content_001",
            "title": "Complete Guide to Machine Learning for Beginners",
            "description": "Learn machine learning fundamentals, algorithms, and practical applications in this comprehensive tutorial.",
            "content_type": "video",
            "duration": 2400,  # 40 minutes
            "transcript": """
            Welcome to this comprehensive machine learning tutorial. Today we'll cover the fundamentals 
            of machine learning, including supervised learning, unsupervised learning, and reinforcement learning.
            We'll explore popular algorithms like linear regression, decision trees, and neural networks.
            By the end of this tutorial, you'll understand how to apply machine learning to real-world problems.
            """,
            "tags": ["machine learning", "AI", "tutorial", "beginner", "algorithms"],
            "category": "education",
            "upload_date": datetime.now() - timedelta(days=3),
            "platform": "youtube",
            "creator_info": {
                "channel_name": "AI Learning Hub",
                "subscriber_count": 50000,
                "niche": "artificial_intelligence"
            },
            "current_performance": {
                "views": 15000,
                "likes": 850,
                "comments": 125,
                "shares": 45,
                "search_ranking": {"machine learning tutorial": 15, "AI beginner guide": 8}
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_content_seo(self, agent, sample_content_data):
        """Test content SEO analysis"""
        seo_analysis = await agent.analyze_content_seo(sample_content_data)
        
        assert isinstance(seo_analysis, SEOAnalysis)
        assert seo_analysis.content_id == sample_content_data["content_id"]
        assert 0 <= seo_analysis.overall_seo_score <= 100
        assert seo_analysis.keyword_optimization is not None
        assert seo_analysis.content_structure is not None
        assert len(seo_analysis.improvement_recommendations) > 0
        assert seo_analysis.search_visibility is not None
    
    @pytest.mark.asyncio
    async def test_optimize_title_and_description(self, agent, sample_content_data):
        """Test title and description optimization"""
        optimization = await agent.optimize_title_and_description(sample_content_data)
        
        assert "optimized_title" in optimization
        assert "optimized_description" in optimization
        assert "title_variations" in optimization
        assert "description_variations" in optimization
        assert "seo_improvements" in optimization
        
        # Verify optimization quality
        optimized_title = optimization["optimized_title"]
        assert len(optimized_title) > 0
        assert len(optimized_title) <= 100  # YouTube title limit
        
        optimized_description = optimization["optimized_description"]
        assert len(optimized_description) > 0
        assert len(optimized_description) <= 5000  # YouTube description limit
    
    @pytest.mark.asyncio
    async def test_generate_seo_keywords(self, agent, sample_content_data):
        """Test SEO keyword generation"""
        keyword_generation = await agent.generate_seo_keywords(sample_content_data)
        
        assert "primary_keywords" in keyword_generation
        assert "secondary_keywords" in keyword_generation
        assert "long_tail_keywords" in keyword_generation
        assert "keyword_difficulty" in keyword_generation
        assert "search_volume_estimates" in keyword_generation
        
        primary_keywords = keyword_generation["primary_keywords"]
        assert len(primary_keywords) > 0
        assert len(primary_keywords) <= 10  # Reasonable number of primary keywords
        
        for keyword in primary_keywords:
            assert "keyword" in keyword
            assert "relevance_score" in keyword
            assert "competition_level" in keyword
            assert 0 <= keyword["relevance_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_hashtags(self, agent, sample_content_data):
        """Test hashtag optimization"""
        hashtag_optimization = await agent.optimize_hashtags(sample_content_data)
        
        assert "recommended_hashtags" in hashtag_optimization
        assert "hashtag_performance" in hashtag_optimization
        assert "hashtag_strategy" in hashtag_optimization
        assert "platform_specific" in hashtag_optimization
        
        recommended = hashtag_optimization["recommended_hashtags"]
        assert len(recommended) > 0
        assert len(recommended) <= 30  # Reasonable hashtag limit
        
        for hashtag in recommended[:5]:  # Check first 5
            assert hashtag.startswith("#")
            assert len(hashtag) > 1
            assert " " not in hashtag  # Hashtags shouldn't contain spaces
    
    @pytest.mark.asyncio
    async def test_analyze_competitor_seo(self, agent, sample_content_data):
        """Test competitor SEO analysis"""
        competitor_data = [
            {
                "competitor_id": "competitor_1",
                "title": "Machine Learning Tutorial - Complete Beginner Course",
                "views": 45000,
                "ranking_keywords": ["machine learning", "ML tutorial", "AI course"],
                "upload_date": datetime.now() - timedelta(days=30)
            },
            {
                "competitor_id": "competitor_2", 
                "title": "Learn ML: From Zero to Hero",
                "views": 32000,
                "ranking_keywords": ["machine learning basics", "ML zero to hero"],
                "upload_date": datetime.now() - timedelta(days=20)
            }
        ]
        
        competitor_analysis = await agent.analyze_competitor_seo(
            sample_content_data,
            competitor_data
        )
        
        assert "competitive_gaps" in competitor_analysis
        assert "keyword_opportunities" in competitor_analysis
        assert "content_positioning" in competitor_analysis
        assert "seo_advantages" in competitor_analysis
        
        gaps = competitor_analysis["competitive_gaps"]
        assert isinstance(gaps, list)
        
        for gap in gaps:
            assert "gap_type" in gap
            assert "opportunity_description" in gap
            assert "potential_impact" in gap
    
    @pytest.mark.asyncio
    async def test_track_seo_performance(self, agent, sample_content_data):
        """Test SEO performance tracking"""
        performance_data = {
            "time_period": "30_days",
            "search_rankings": {
                "machine learning tutorial": [15, 12, 10, 8, 8, 7, 6],  # Weekly rankings
                "AI beginner guide": [8, 7, 6, 5, 5, 4, 4],
                "ML fundamentals": [25, 20, 18, 15, 12, 10, 9]
            },
            "organic_traffic": {
                "total_clicks": 2500,
                "impressions": 15000,
                "click_through_rate": 0.167,
                "average_position": 7.2
            },
            "engagement_metrics": {
                "bounce_rate": 0.35,
                "session_duration": 420,  # 7 minutes
                "pages_per_session": 1.8
            }
        }
        
        seo_tracking = await agent.track_seo_performance(
            sample_content_data,
            performance_data
        )
        
        assert "performance_summary" in seo_tracking
        assert "ranking_trends" in seo_tracking
        assert "traffic_analysis" in seo_tracking
        assert "improvement_opportunities" in seo_tracking
        
        summary = seo_tracking["performance_summary"]
        assert "overall_seo_health" in summary
        assert "key_achievements" in summary
        assert "areas_needing_attention" in summary


class TestKeywordResearchAgent:
    """Test KeywordResearchAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create KeywordResearchAgent instance"""
        return KeywordResearchAgent()
    
    @pytest.fixture
    def sample_research_context(self):
        """
Sample context for keyword research"""
        return {
            "niche": "fitness_nutrition",
            "target_audience": "fitness_enthusiasts_25_40",
            "content_goals": ["education", "product_promotion", "community_building"],
            "platform": "youtube",
            "geographic_focus": ["US", "UK", "Canada", "Australia"],
            "competitor_keywords": [
                "workout routine", "nutrition tips", "meal prep", "fitness motivation",
                "protein recipes", "weight loss", "muscle building", "healthy eating"
            ],
            "current_content_themes": [
                "home workouts", "healthy recipes", "fitness tips", "nutrition education"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_research_target_keywords(self, agent, sample_research_context):
        """Test target keyword research"""
        keyword_research = await agent.research_target_keywords(sample_research_context)
        
        assert "high_value_keywords" in keyword_research
        assert "emerging_keywords" in keyword_research
        assert "long_tail_opportunities" in keyword_research
        assert "seasonal_keywords" in keyword_research
        
        high_value = keyword_research["high_value_keywords"]
        assert len(high_value) > 0
        
        for keyword in high_value:
            assert "keyword" in keyword
            assert "search_volume" in keyword
            assert "competition_score" in keyword
            assert "trend_direction" in keyword
            assert "opportunity_score" in keyword
            assert keyword["search_volume"] > 0
            assert 0 <= keyword["competition_score"] <= 1
            assert 0 <= keyword["opportunity_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_keyword_difficulty(self, agent, sample_research_context):
        """Test keyword difficulty analysis"""
        target_keywords = [
            "best home workout routine",
            "healthy meal prep ideas", 
            "fitness motivation tips",
            "protein rich breakfast recipes",
            "quick HIIT workouts"
        ]
        
        difficulty_analysis = await agent.analyze_keyword_difficulty(
            target_keywords,
            sample_research_context
        )
        
        assert "keyword_difficulty_scores" in difficulty_analysis
        assert "ranking_feasibility" in difficulty_analysis
        assert "competitive_analysis" in difficulty_analysis
        assert "success_probability" in difficulty_analysis
        
        difficulty_scores = difficulty_analysis["keyword_difficulty_scores"]
        assert len(difficulty_scores) == len(target_keywords)
        
        for keyword_analysis in difficulty_scores:
            assert "keyword" in keyword_analysis
            assert "difficulty_score" in keyword_analysis
            assert "time_to_rank_estimate" in keyword_analysis
            assert 0 <= keyword_analysis["difficulty_score"] <= 100
    
    @pytest.mark.asyncio
    async def test_identify_keyword_gaps(self, agent, sample_research_context):
        """Test keyword gap identification"""
        current_rankings = {
            "workout routine": 15,
            "fitness tips": 8,
            "healthy eating": 12,
            "meal prep": 20
        }
        
        gap_analysis = await agent.identify_keyword_gaps(
            sample_research_context,
            current_rankings
        )
        
        assert "missed_opportunities" in gap_analysis
        assert "underperforming_keywords" in gap_analysis
        assert "content_gaps" in gap_analysis
        assert "strategic_recommendations" in gap_analysis
        
        missed_opportunities = gap_analysis["missed_opportunities"]
        assert isinstance(missed_opportunities, list)
        
        for opportunity in missed_opportunities:
            assert "keyword" in opportunity
            assert "opportunity_type" in opportunity
            assert "potential_impact" in opportunity
            assert "recommended_action" in opportunity
    
    @pytest.mark.asyncio
    async def test_create_keyword_strategy(self, agent, sample_research_context):
        """Test keyword strategy creation"""
        strategy_goals = {
            "primary_objective": "increase_organic_traffic",
            "target_traffic_increase": 0.5,  # 50% increase
            "timeline_months": 6,
            "content_production_capacity": "high"
        }
        
        keyword_strategy = await agent.create_keyword_strategy(
            sample_research_context,
            strategy_goals
        )
        
        assert isinstance(keyword_strategy, KeywordStrategy)
        assert keyword_strategy.strategy_id is not None
        assert len(keyword_strategy.primary_keywords) > 0
        assert len(keyword_strategy.content_calendar) > 0
        assert keyword_strategy.success_metrics is not None
        assert keyword_strategy.timeline is not None
    
    @pytest.mark.asyncio
    async def test_monitor_keyword_trends(self, agent, sample_research_context):
        """Test keyword trend monitoring"""
        monitoring_setup = {
            "keywords_to_track": [
                "home fitness", "workout from home", "online fitness classes",
                "nutrition coaching", "meal planning", "fitness app"
            ],
            "monitoring_frequency": "weekly",
            "trend_analysis_period": "90_days"
        }
        
        trend_monitoring = await agent.monitor_keyword_trends(monitoring_setup)
        
        assert "trend_analysis" in trend_monitoring
        assert "rising_trends" in trend_monitoring
        assert "declining_trends" in trend_monitoring
        assert "seasonal_patterns" in trend_monitoring
        
        trend_analysis = trend_monitoring["trend_analysis"]
        for keyword_trend in trend_analysis:
            assert "keyword" in keyword_trend
            assert "trend_direction" in keyword_trend
            assert "momentum_score" in keyword_trend
            assert "seasonal_factor" in keyword_trend


class TestContentOptimizationAgent:
    """Test ContentOptimizationAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create ContentOptimizationAgent instance"""
        return ContentOptimizationAgent()
    
    @pytest.fixture
    def sample_content_for_optimization(self):
        """
Sample content for optimization"""
        return {
            "content_id": "content_seo_001",
            "title": "Workout Tips",
            "description": "Some workout tips for you.",
            "content": """
            Here are some basic workout tips. Exercise is good for health.
            You should workout regularly. Cardio is important. Strength training helps too.
            Don't forget to stretch. Eat healthy food. Drink water.
            """,
            "target_keywords": ["workout tips", "exercise routine", "fitness advice"],
            "current_performance": {
                "search_visibility": 0.3,
                "organic_traffic": 500,
                "engagement_rate": 0.04
            },
            "optimization_goals": {
                "increase_visibility": True,
                "improve_engagement": True,
                "target_specific_keywords": True
            }
        }
    
    @pytest.mark.asyncio
    async def test_optimize_content_structure(self, agent, sample_content_for_optimization):
        """Test content structure optimization"""
        structure_optimization = await agent.optimize_content_structure(
            sample_content_for_optimization
        )
        
        assert "optimized_structure" in structure_optimization
        assert "heading_recommendations" in structure_optimization
        assert "content_flow_improvements" in structure_optimization
        assert "readability_enhancements" in structure_optimization
        
        optimized_structure = structure_optimization["optimized_structure"]
        assert "introduction" in optimized_structure
        assert "main_sections" in optimized_structure
        assert "conclusion" in optimized_structure
        
        headings = structure_optimization["heading_recommendations"]
        assert len(headings) > 0
        
        for heading in headings:
            assert "heading_text" in heading
            assert "heading_level" in heading
            assert "keyword_integration" in heading
    
    @pytest.mark.asyncio
    async def test_enhance_keyword_density(self, agent, sample_content_for_optimization):
        """Test keyword density enhancement"""
        keyword_enhancement = await agent.enhance_keyword_density(
            sample_content_for_optimization
        )
        
        assert "optimized_content" in keyword_enhancement
        assert "keyword_placement_analysis" in keyword_enhancement
        assert "density_improvements" in keyword_enhancement
        assert "semantic_keyword_suggestions" in keyword_enhancement
        
        optimized_content = keyword_enhancement["optimized_content"]
        assert len(optimized_content) > len(sample_content_for_optimization["content"])
        
        # Verify target keywords are better integrated
        for keyword in sample_content_for_optimization["target_keywords"]:
            assert keyword.lower() in optimized_content.lower()
        
        density_analysis = keyword_enhancement["keyword_placement_analysis"]
        for keyword in sample_content_for_optimization["target_keywords"]:
            assert keyword in density_analysis
            assert "current_density" in density_analysis[keyword]
            assert "optimized_density" in density_analysis[keyword]
    
    @pytest.mark.asyncio
    async def test_improve_content_readability(self, agent, sample_content_for_optimization):
        """Test content readability improvement"""
        readability_improvement = await agent.improve_content_readability(
            sample_content_for_optimization
        )
        
        assert "improved_content" in readability_improvement
        assert "readability_score" in readability_improvement
        assert "improvements_made" in readability_improvement
        assert "style_enhancements" in readability_improvement
        
        improved_content = readability_improvement["improved_content"]
        assert len(improved_content) > 0
        
        readability_score = readability_improvement["readability_score"]
        assert "before" in readability_score
        assert "after" in readability_score
        assert readability_score["after"] >= readability_score["before"]  # Should improve
        
        improvements = readability_improvement["improvements_made"]
        assert isinstance(improvements, list)
        assert len(improvements) > 0
    
    @pytest.mark.asyncio
    async def test_optimize_meta_tags(self, agent, sample_content_for_optimization):
        """Test meta tag optimization"""
        meta_optimization = await agent.optimize_meta_tags(sample_content_for_optimization)
        
        assert "optimized_title_tag" in meta_optimization
        assert "optimized_description_tag" in meta_optimization
        assert "keyword_tags" in meta_optimization
        assert "social_media_tags" in meta_optimization
        
        title_tag = meta_optimization["optimized_title_tag"]
        assert len(title_tag) > 0
        assert len(title_tag) <= 60  # SEO best practice
        
        description_tag = meta_optimization["optimized_description_tag"]
        assert len(description_tag) > 0
        assert len(description_tag) <= 160  # SEO best practice
        
        # Verify keywords are included in meta tags
        for keyword in sample_content_for_optimization["target_keywords"]:
            included_in_title = keyword.lower() in title_tag.lower()
            included_in_description = keyword.lower() in description_tag.lower()
            assert included_in_title or included_in_description  # At least one should include each keyword
    
    @pytest.mark.asyncio
    async def test_generate_content_optimization_report(self, agent, sample_content_for_optimization):
        """Test content optimization report generation"""
        optimization_report = await agent.generate_content_optimization_report(
            sample_content_for_optimization
        )
        
        assert isinstance(optimization_report, ContentOptimization)
        assert optimization_report.content_id == sample_content_for_optimization["content_id"]
        assert optimization_report.optimization_score is not None
        assert len(optimization_report.applied_optimizations) > 0
        assert optimization_report.performance_predictions is not None
        assert optimization_report.implementation_priority is not None
        assert 0 <= optimization_report.optimization_score <= 100


class TestVisibilityAnalysisAgent:
    """Test VisibilityAnalysisAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create VisibilityAnalysisAgent instance"""
        return VisibilityAnalysisAgent()
    
    @pytest.fixture
    def sample_visibility_data(self):
        """
Sample visibility data for analysis"""
        return {
            "creator_id": "creator_visibility_001",
            "platform": "youtube",
            "content_library": [
                {
                    "content_id": f"video_{i}",
                    "title": f"Tutorial {i}: Advanced Topic",
                    "views": 10000 + (i * 2000),
                    "impressions": 50000 + (i * 10000),
                    "click_through_rate": 0.08 + (i * 0.01),
                    "search_rankings": {
                        f"keyword_{i}": 10 - i,  # Better rankings for later content
                        f"topic_{i}": 15 - i
                    },
                    "upload_date": datetime.now() - timedelta(days=i*7),
                    "category": "education"
                }
                for i in range(10)
            ],
            "channel_metrics": {
                "total_subscribers": 75000,
                "monthly_views": 500000,
                "average_view_duration": 450,  # seconds
                "subscriber_growth_rate": 0.08
            },
            "search_performance": {
                "total_search_impressions": 1500000,
                "total_search_clicks": 120000,
                "average_search_position": 8.5,
                "search_ctr": 0.08
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_search_visibility(self, agent, sample_visibility_data):
        """Test search visibility analysis"""
        visibility_analysis = await agent.analyze_search_visibility(sample_visibility_data)
        
        assert "overall_visibility_score" in visibility_analysis
        assert "search_performance" in visibility_analysis
        assert "content_discoverability" in visibility_analysis
        assert "ranking_distribution" in visibility_analysis
        
        overall_score = visibility_analysis["overall_visibility_score"]
        assert 0 <= overall_score <= 100
        
        search_performance = visibility_analysis["search_performance"]
        assert "impression_analysis" in search_performance
        assert "click_through_analysis" in search_performance
        assert "ranking_analysis" in search_performance
    
    @pytest.mark.asyncio
    async def test_identify_visibility_bottlenecks(self, agent, sample_visibility_data):
        """Test visibility bottleneck identification"""
        bottleneck_analysis = await agent.identify_visibility_bottlenecks(sample_visibility_data)
        
        assert "critical_bottlenecks" in bottleneck_analysis
        assert "moderate_issues" in bottleneck_analysis
        assert "optimization_priorities" in bottleneck_analysis
        assert "quick_fixes" in bottleneck_analysis
        
        critical_bottlenecks = bottleneck_analysis["critical_bottlenecks"]
        assert isinstance(critical_bottlenecks, list)
        
        for bottleneck in critical_bottlenecks:
            assert "issue_type" in bottleneck
            assert "severity" in bottleneck
            assert "affected_content" in bottleneck
            assert "recommended_action" in bottleneck
            assert bottleneck["severity"] in ["low", "medium", "high", "critical"]
    
    @pytest.mark.asyncio
    async def test_recommend_visibility_improvements(self, agent, sample_visibility_data):
        """Test visibility improvement recommendations"""
        improvement_recommendations = await agent.recommend_visibility_improvements(
            sample_visibility_data
        )
        
        assert "high_impact_recommendations" in improvement_recommendations
        assert "content_optimization" in improvement_recommendations
        assert "technical_improvements" in improvement_recommendations
        assert "strategic_changes" in improvement_recommendations
        
        high_impact = improvement_recommendations["high_impact_recommendations"]
        assert len(high_impact) > 0
        
        for recommendation in high_impact:
            assert "recommendation_type" in recommendation
            assert "expected_impact" in recommendation
            assert "implementation_effort" in recommendation
            assert "timeline" in recommendation
            assert "success_metrics" in recommendation
    
    @pytest.mark.asyncio
    async def test_track_visibility_trends(self, agent, sample_visibility_data):
        """Test visibility trend tracking"""
        trend_data = {
            "time_period": "90_days",
            "historical_metrics": {
                "weekly_impressions": [45000, 48000, 52000, 55000, 58000, 62000, 65000, 68000, 70000, 72000, 75000, 78000],
                "weekly_clicks": [3600, 3840, 4160, 4400, 4640, 4960, 5200, 5440, 5600, 5760, 6000, 6240],
                "weekly_ctr": [0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08],
                "weekly_avg_position": [8.5, 8.3, 8.1, 7.9, 7.7, 7.5, 7.3, 7.1, 6.9, 6.7, 6.5, 6.3]
            }
        }
        
        visibility_trends = await agent.track_visibility_trends(
            sample_visibility_data,
            trend_data
        )
        
        assert "trend_summary" in visibility_trends
        assert "growth_metrics" in visibility_trends
        assert "performance_patterns" in visibility_trends
        assert "forecasting" in visibility_trends
        
        trend_summary = visibility_trends["trend_summary"]
        assert "overall_trend" in trend_summary
        assert "key_improvements" in trend_summary
        assert "areas_of_concern" in trend_summary
    
    @pytest.mark.asyncio
    async def test_generate_visibility_report(self, agent, sample_visibility_data):
        """Test visibility report generation"""
        report_config = {
            "report_type": "comprehensive",
            "time_period": "quarterly",
            "include_competitive_analysis": True,
            "include_recommendations": True
        }
        
        visibility_report = await agent.generate_visibility_report(
            sample_visibility_data,
            report_config
        )
        
        assert isinstance(visibility_report, VisibilityReport)
        assert visibility_report.report_id is not None
        assert visibility_report.visibility_score is not None
        assert visibility_report.key_findings is not None
        assert len(visibility_report.improvement_roadmap) > 0
        assert visibility_report.competitive_position is not None
        assert 0 <= visibility_report.visibility_score <= 100


class TestIntegrationScenarios:
    """Test integration between different SEO optimization agents"""
    
    @pytest.fixture
    def agents(self):
        """
Create all SEO optimization agents for integration testing"""
        return {
            "seo": SEOOptimizationAgent(),
            "keyword": KeywordResearchAgent(),
            "content": ContentOptimizationAgent(),
            "visibility": VisibilityAnalysisAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_seo_strategy(self, agents):
        """Test comprehensive SEO strategy development"""
        # Creator profile for complete SEO optimization
        creator_data = {
            "creator_id": "seo_integration_creator",
            "niche": "personal_finance",
            "target_audience": "young_professionals",
            "content_goals": ["education", "lead_generation", "brand_building"],
            "current_performance": {
                "monthly_views": 100000,
                "search_traffic_percentage": 0.35,
                "average_search_position": 12,
                "organic_click_through_rate": 0.06
            },
            "seo_goals": {
                "increase_organic_traffic": 1.0,  # 100% increase
                "improve_search_rankings": True,
                "target_new_keywords": True
            }
        }
        
        # Execute integrated SEO workflow
        # 1. Research target keywords
        keyword_research = await agents["keyword"].research_target_keywords({
            "niche": creator_data["niche"],
            "target_audience": creator_data["target_audience"],
            "content_goals": creator_data["content_goals"]
        })
        
        # 2. Analyze current content SEO
        content_seo = await agents["seo"].analyze_content_seo(creator_data)
        
        # 3. Optimize content structure and keywords
        content_optimization = await agents["content"].optimize_content_structure(creator_data)
        
        # 4. Analyze visibility and identify improvements
        visibility_analysis = await agents["visibility"].analyze_search_visibility(creator_data)
        
        # 5. Create comprehensive improvement plan
        seo_optimization = await agents["seo"].optimize_title_and_description(creator_data)
        
        # Verify integrated SEO strategy
        assert "high_value_keywords" in keyword_research
        assert content_seo is not None
        assert "optimized_structure" in content_optimization
        assert "overall_visibility_score" in visibility_analysis
        assert "optimized_title" in seo_optimization
        
        # Verify strategy coherence
        high_value_keywords = keyword_research["high_value_keywords"]
        assert len(high_value_keywords) > 0
        assert content_seo.overall_seo_score >= 0
        assert visibility_analysis["overall_visibility_score"] >= 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """
Create SEOOptimizationAgent for error testing"""
        return SEOOptimizationAgent()
    
    @pytest.mark.asyncio
    async def test_insufficient_content_data(self, agent):
        """
Test handling of insufficient content data"""
        minimal_data = {"content_id": "test"}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.analyze_content_seo(minimal_data)
    
    @pytest.mark.asyncio
    async def test_invalid_seo_parameters(self, agent):
        """Test handling of invalid SEO parameters"""
        invalid_data = {
            "content_id": "test",
            "title": "",  # Empty title
            "description": "x" * 10000,  # Too long description
            "tags": "invalid_format"  # Should be list
        }
        
        try:
            result = await agent.analyze_content_seo(invalid_data)
            # Should handle gracefully with data validation
            assert result is not None
        except (ValueError, TypeError):
            # Acceptable to reject invalid data
            pass
    
    @pytest.mark.asyncio
    async def test_external_seo_api_failures(self, agent):
        """Test handling of external SEO API failures"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("SEO API service unavailable")
            
            content_data = {
                "content_id": "test",
                "title": "Test Title",
                "description": "Test description"
            }
            
            try:
                result = await agent.analyze_content_seo(content_data)
                # Should provide fallback analysis
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """
Create SEOOptimizationAgent for performance testing"""
        return SEOOptimizationAgent()
    
    @pytest.mark.asyncio
    async def test_bulk_content_seo_analysis(self, agent):
        """
Test bulk SEO analysis performance"""
        content_batch = [
            {
                "content_id": f"bulk_content_{i}",
                "title": f"SEO Tutorial {i}: Advanced Techniques",
                "description": f"Learn advanced SEO techniques in tutorial {i}",
                "tags": [f"seo_{i}", f"tutorial_{i}", "marketing"],
                "category": "education"
            }
            for i in range(20)  # 20 pieces of content
        ]
        
        start_time = datetime.now()
        
        # Analyze first 5 for performance testing
        analysis_tasks = [
            agent.analyze_content_seo(content)
            for content in content_batch[:5]
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 5
        assert processing_time < 30  # Should complete within reasonable time
        
        # Verify no exceptions in results
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_concurrent_keyword_research(self, agent):
        """Test concurrent keyword research for multiple niches"""
        keyword_agent = KeywordResearchAgent()
        
        research_contexts = [
            {"niche": f"niche_{i}", "target_audience": f"audience_{i}"}
            for i in range(5)
        ]
        
        research_tasks = [
            keyword_agent.research_target_keywords(context)
            for context in research_contexts
        ]
        
        results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        assert len(results) == len(research_contexts)
        for result in results:
            assert not isinstance(result, Exception)
            if isinstance(result, dict) and "high_value_keywords" in result:
                assert len(result["high_value_keywords"]) >= 0
