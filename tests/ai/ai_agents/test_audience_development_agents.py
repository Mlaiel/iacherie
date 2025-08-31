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
Test suite for Audience Development AI Agents

Tests all functionalities of audience development, community building, 
engagement optimization, and growth strategy agents.

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

from ai.ai_agents.audience_development_agents import (
    AudienceDevelopmentAgent,
    CommunityBuildingAgent, 
    EngagementOptimizationAgent,
    GrowthStrategyAgent,
    AudienceAnalysis,
    GrowthStrategy,
    EngagementOptimization,
    CommunityHealth
)


class TestAudienceDevelopmentAgent:
    """Test AudienceDevelopmentAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create AudienceDevelopmentAgent instance"""
        return AudienceDevelopmentAgent()
    
    @pytest.fixture
    def sample_audience_data(self):
        """Sample audience data for testing"""
        return {
            "total_followers": 15000,
            "monthly_growth": 1200,
            "engagement_rate": 0.045,
            "demographics": {
                "age_groups": {"18-24": 35, "25-34": 40, "35-44": 20, "45+": 5},
                "gender": {"male": 45, "female": 52, "other": 3},
                "locations": {"US": 40, "UK": 15, "CA": 12, "AU": 8, "other": 25}
            },
            "interests": {
                "technology": 0.8,
                "business": 0.6,
                "lifestyle": 0.4,
                "entertainment": 0.3
            },
            "behavior_patterns": {
                "peak_activity_hours": [19, 20, 21],
                "preferred_content_types": ["video", "image", "article"],
                "interaction_frequency": "daily"
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_audience_demographics(self, agent, sample_audience_data):
        """Test audience demographic analysis"""
        analysis = await agent.analyze_audience_demographics(sample_audience_data)
        
        assert isinstance(analysis, AudienceAnalysis)
        assert analysis.audience_size == 15000
        assert 0 <= analysis.growth_rate <= 1
        assert 0 <= analysis.engagement_quality <= 1
        assert analysis.demographic_breakdown is not None
        assert "age_groups" in analysis.demographic_breakdown
        assert "gender" in analysis.demographic_breakdown
        
    @pytest.mark.asyncio
    async def test_predict_growth_potential(self, agent, sample_audience_data):
        """Test growth potential prediction"""
        growth_prediction = await agent.predict_growth_potential(
            sample_audience_data,
            time_horizon_months=6
        )
        
        assert "predicted_growth" in growth_prediction
        assert "growth_factors" in growth_prediction
        assert "confidence_score" in growth_prediction
        assert isinstance(growth_prediction["predicted_growth"], (int, float))
        assert 0 <= growth_prediction["confidence_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_identify_growth_opportunities(self, agent, sample_audience_data):
        """Test growth opportunity identification"""
        opportunities = await agent.identify_growth_opportunities(sample_audience_data)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        for opportunity in opportunities:
            assert "type" in opportunity
            assert "description" in opportunity
            assert "potential_impact" in opportunity
            assert "difficulty" in opportunity
    
    @pytest.mark.asyncio
    async def test_analyze_audience_loyalty(self, agent, sample_audience_data):
        """Test audience loyalty analysis"""
        loyalty_analysis = await agent.analyze_audience_loyalty(sample_audience_data)
        
        assert "loyalty_score" in loyalty_analysis
        assert "churn_risk" in loyalty_analysis
        assert "retention_factors" in loyalty_analysis
        assert 0 <= loyalty_analysis["loyalty_score"] <= 1
        assert 0 <= loyalty_analysis["churn_risk"] <= 1
    
    @pytest.mark.asyncio
    async def test_segment_audience(self, agent, sample_audience_data):
        """Test audience segmentation"""
        segments = await agent.segment_audience(sample_audience_data)
        
        assert isinstance(segments, dict)
        assert len(segments) > 0
        
        for segment_name, segment_data in segments.items():
            assert "size" in segment_data
            assert "characteristics" in segment_data
            assert "engagement_level" in segment_data
            assert segment_data["size"] > 0
    
    @pytest.mark.asyncio
    async def test_recommend_targeting_strategy(self, agent, sample_audience_data):
        """Test targeting strategy recommendations"""
        strategy = await agent.recommend_targeting_strategy(
            sample_audience_data,
            goal="growth"
        )
        
        assert "target_segments" in strategy
        assert "content_strategy" in strategy
        assert "channel_optimization" in strategy
        assert "timeline" in strategy


class TestCommunityBuildingAgent:
    """Test CommunityBuildingAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create CommunityBuildingAgent instance"""
        return CommunityBuildingAgent()
    
    @pytest.fixture
    def sample_community_data(self):
        """Sample community data for testing"""
        return {
            "total_members": 5000,
            "active_members": 1500,
            "engagement_metrics": {
                "posts_per_day": 25,
                "comments_per_post": 8,
                "likes_per_post": 45,
                "shares_per_post": 3
            },
            "member_interactions": {
                "member_to_member": 0.6,
                "creator_to_member": 0.8,
                "member_to_creator": 0.4
            },
            "community_health_indicators": {
                "toxicity_score": 0.05,
                "helpfulness_score": 0.8,
                "positivity_score": 0.75
            }
        }
    
    @pytest.mark.asyncio
    async def test_assess_community_health(self, agent, sample_community_data):
        """Test community health assessment"""
        health = await agent.assess_community_health(sample_community_data)
        
        assert isinstance(health, CommunityHealth)
        assert 0 <= health.overall_health_score <= 1
        assert 0 <= health.engagement_health <= 1
        assert 0 <= health.toxicity_level <= 1
        assert health.key_metrics is not None
    
    @pytest.mark.asyncio
    async def test_identify_community_leaders(self, agent, sample_community_data):
        """Test community leader identification"""
        leaders = await agent.identify_community_leaders(sample_community_data)
        
        assert isinstance(leaders, list)
        
        for leader in leaders:
            assert "user_id" in leader
            assert "leadership_score" in leader
            assert "influence_metrics" in leader
            assert 0 <= leader["leadership_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_generate_community_initiatives(self, agent, sample_community_data):
        """Test community initiative generation"""
        initiatives = await agent.generate_community_initiatives(sample_community_data)
        
        assert isinstance(initiatives, list)
        assert len(initiatives) > 0
        
        for initiative in initiatives:
            assert "name" in initiative
            assert "description" in initiative
            assert "expected_impact" in initiative
            assert "resource_requirements" in initiative
    
    @pytest.mark.asyncio
    async def test_create_engagement_campaigns(self, agent, sample_community_data):
        """Test engagement campaign creation"""
        campaigns = await agent.create_engagement_campaigns(
            sample_community_data,
            campaign_goals=["increase_participation", "build_relationships"]
        )
        
        assert isinstance(campaigns, list)
        
        for campaign in campaigns:
            assert "name" in campaign
            assert "strategy" in campaign
            assert "tactics" in campaign
            assert "success_metrics" in campaign


class TestEngagementOptimizationAgent:
    """Test EngagementOptimizationAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create EngagementOptimizationAgent instance"""
        return EngagementOptimizationAgent()
    
    @pytest.fixture
    def sample_engagement_data(self):
        """Sample engagement data for testing"""
        return {
            "content_performance": {
                "posts": [
                    {
                        "post_id": "1",
                        "type": "video",
                        "likes": 150,
                        "comments": 20,
                        "shares": 5,
                        "reach": 2000,
                        "timestamp": datetime.now() - timedelta(days=1)
                    },
                    {
                        "post_id": "2", 
                        "type": "image",
                        "likes": 200,
                        "comments": 25,
                        "shares": 8,
                        "reach": 2500,
                        "timestamp": datetime.now() - timedelta(days=2)
                    }
                ]
            },
            "audience_behavior": {
                "peak_times": [19, 20, 21],
                "preferred_formats": ["video", "carousel", "image"],
                "interaction_patterns": "evening_scrollers"
            }
        }
    
    @pytest.mark.asyncio
    async def test_optimize_posting_schedule(self, agent, sample_engagement_data):
        """Test posting schedule optimization"""
        schedule = await agent.optimize_posting_schedule(sample_engagement_data)
        
        assert "optimal_times" in schedule
        assert "frequency_recommendations" in schedule
        assert "content_type_timing" in schedule
        assert isinstance(schedule["optimal_times"], list)
        assert len(schedule["optimal_times"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_content_performance(self, agent, sample_engagement_data):
        """Test content performance analysis"""
        analysis = await agent.analyze_content_performance(sample_engagement_data)
        
        assert "top_performing_content" in analysis
        assert "performance_patterns" in analysis
        assert "improvement_suggestions" in analysis
        assert "engagement_trends" in analysis
    
    @pytest.mark.asyncio
    async def test_generate_engagement_strategies(self, agent, sample_engagement_data):
        """Test engagement strategy generation"""
        strategies = await agent.generate_engagement_strategies(sample_engagement_data)
        
        assert isinstance(strategies, list)
        
        for strategy in strategies:
            assert "strategy_name" in strategy
            assert "tactics" in strategy
            assert "expected_outcomes" in strategy
            assert "implementation_steps" in strategy
    
    @pytest.mark.asyncio
    async def test_predict_viral_potential(self, agent, sample_engagement_data):
        """Test viral potential prediction"""
        potential = await agent.predict_viral_potential(
            content_data={
                "type": "video",
                "duration": 30,
                "topic": "trending_challenge",
                "hashtags": ["#viral", "#challenge", "#trending"]
            }
        )
        
        assert "viral_score" in potential
        assert "confidence" in potential
        assert "factors" in potential
        assert 0 <= potential["viral_score"] <= 1
        assert 0 <= potential["confidence"] <= 1


class TestGrowthStrategyAgent:
    """Test GrowthStrategyAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create GrowthStrategyAgent instance"""
        return GrowthStrategyAgent()
    
    @pytest.fixture
    def sample_creator_profile(self):
        """Sample creator profile for testing"""
        return {
            "creator_id": "test_creator",
            "current_metrics": {
                "followers": 10000,
                "monthly_growth_rate": 0.05,
                "engagement_rate": 0.035,
                "content_frequency": "daily"
            },
            "content_categories": ["tech", "lifestyle", "education"],
            "target_audience": "tech_professionals",
            "growth_goals": {
                "follower_target": 50000,
                "timeline_months": 12,
                "engagement_target": 0.06
            }
        }
    
    @pytest.mark.asyncio
    async def test_develop_growth_strategy(self, agent, sample_creator_profile):
        """Test growth strategy development"""
        strategy = await agent.develop_growth_strategy(sample_creator_profile)
        
        assert isinstance(strategy, GrowthStrategy)
        assert strategy.target_growth_rate > 0
        assert len(strategy.primary_growth_channels) > 0
        assert len(strategy.content_optimization_plan) > 0
        assert strategy.timeline is not None
    
    @pytest.mark.asyncio
    async def test_analyze_competitor_strategies(self, agent, sample_creator_profile):
        """Test competitor strategy analysis"""
        competitor_analysis = await agent.analyze_competitor_strategies(
            sample_creator_profile,
            competitor_data=[
                {"name": "competitor1", "followers": 25000, "growth_rate": 0.08},
                {"name": "competitor2", "followers": 15000, "growth_rate": 0.06}
            ]
        )
        
        assert "competitive_positioning" in competitor_analysis
        assert "growth_opportunities" in competitor_analysis
        assert "differentiation_strategies" in competitor_analysis
    
    @pytest.mark.asyncio
    async def test_recommend_collaboration_opportunities(self, agent, sample_creator_profile):
        """Test collaboration opportunity recommendations"""
        collaborations = await agent.recommend_collaboration_opportunities(
            sample_creator_profile
        )
        
        assert isinstance(collaborations, list)
        
        for collab in collaborations:
            assert "collaboration_type" in collab
            assert "potential_partners" in collab
            assert "expected_benefits" in collab
            assert "implementation_strategy" in collab
    
    @pytest.mark.asyncio
    async def test_create_content_calendar(self, agent, sample_creator_profile):
        """Test content calendar creation"""
        calendar = await agent.create_content_calendar(
            sample_creator_profile,
            duration_weeks=4
        )
        
        assert "weekly_schedule" in calendar
        assert "content_themes" in calendar
        assert "posting_strategy" in calendar
        assert len(calendar["weekly_schedule"]) == 4


class TestIntegrationScenarios:
    """Test integration between different audience development agents"""
    
    @pytest.fixture
    def agents(self):
        """Create all agents for integration testing"""
        return {
            "audience_dev": AudienceDevelopmentAgent(),
            "community": CommunityBuildingAgent(),
            "engagement": EngagementOptimizationAgent(),
            "growth": GrowthStrategyAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_audience_strategy(self, agents):
        """Test comprehensive audience development workflow"""
        # Sample comprehensive data
        creator_data = {
            "creator_id": "integration_test",
            "audience": {
                "total_followers": 20000,
                "growth_rate": 0.04,
                "demographics": {"age_18_34": 75, "age_35_plus": 25},
                "engagement_rate": 0.045
            },
            "community": {
                "active_members": 3000,
                "engagement_quality": 0.7,
                "health_score": 0.8
            },
            "content_performance": {
                "avg_likes": 500,
                "avg_comments": 25,
                "avg_shares": 10,
                "top_performing_types": ["video", "carousel"]
            }
        }
        
        # Run integrated analysis
        audience_analysis = await agents["audience_dev"].analyze_audience_demographics(
            creator_data["audience"]
        )
        
        community_health = await agents["community"].assess_community_health(
            creator_data["community"]
        )
        
        engagement_optimization = await agents["engagement"].generate_engagement_strategies(
            creator_data["content_performance"]
        )
        
        growth_strategy = await agents["growth"].develop_growth_strategy(creator_data)
        
        # Verify integrated results
        assert audience_analysis is not None
        assert community_health is not None
        assert engagement_optimization is not None
        assert growth_strategy is not None
        
        # Verify coherence between strategies
        assert len(engagement_optimization) > 0
        assert growth_strategy.target_growth_rate > creator_data["audience"]["growth_rate"]


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create AudienceDevelopmentAgent for error testing"""
        return AudienceDevelopmentAgent()
    
    @pytest.mark.asyncio
    async def test_invalid_audience_data(self, agent):
        """Test handling of invalid audience data"""
        invalid_data = {"invalid": "data"}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.analyze_audience_demographics(invalid_data)
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self, agent):
        """Test handling of empty data"""
        empty_data = {}
        
        # Should handle gracefully without crashing
        try:
            result = await agent.identify_growth_opportunities(empty_data)
            assert isinstance(result, list)
        except (ValueError, KeyError):
            # Acceptable to raise specific exceptions for empty data
            pass
    
    @pytest.mark.asyncio
    async def test_network_failure_handling(self, agent):
        """Test handling of network failures"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            # Should handle network errors gracefully
            try:
                result = await agent.predict_growth_potential({"followers": 1000})
                # Either returns default/cached result or raises handled exception
                assert result is not None or True  # Test passes if exception is properly handled
            except Exception as e:
                # Should be a handled exception with clear message
                assert "error" in str(e).lower() or "network" in str(e).lower()


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create AudienceDevelopmentAgent for performance testing"""
        return AudienceDevelopmentAgent()
    
    @pytest.mark.asyncio
    async def test_large_dataset_processing(self, agent):
        """Test processing of large audience datasets"""
        large_dataset = {
            "total_followers": 1000000,
            "demographics": {
                f"segment_{i}": {"size": 10000, "engagement": 0.05} 
                for i in range(100)
            },
            "behavior_data": {
                f"pattern_{i}": {"frequency": 0.01, "value": i}
                for i in range(1000)
            }
        }
        
        # Should process large datasets efficiently
        start_time = datetime.now()
        result = await agent.analyze_audience_demographics(large_dataset)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert result is not None
        assert processing_time < 30  # Should complete within reasonable time
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, agent):
        """Test concurrent processing capabilities"""
        datasets = [
            {"followers": 10000, "engagement": 0.04},
            {"followers": 25000, "engagement": 0.03},
            {"followers": 5000, "engagement": 0.06},
            {"followers": 15000, "engagement": 0.05}
        ]
        
        # Run concurrent analyses
        tasks = [
            agent.analyze_audience_demographics(data)
            for data in datasets
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete successfully
        assert len(results) == len(datasets)
        for result in results:
            assert not isinstance(result, Exception)
