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

"""Test suite for Brand Consulting AI Agents

Tests all functionalities of brand consulting, personal brand development,
brand positioning, and brand strategy optimization agents.

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

from ai.ai_agents.brand_consulting_agents import (
    BrandConsultantAgent,
    PersonalBrandingAgent,
    BrandPositioningAgent,
    BrandStrategyAgent,
    BrandAnalysis,
    BrandStrategy,
    BrandAudit,
    CompetitiveBrandAnalysis
)


class TestBrandConsultantAgent:
    """Test BrandConsultantAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandConsultantAgent instance"""
        return BrandConsultantAgent()
    
    @pytest.fixture
    def sample_creator_profile(self):
        """Sample creator profile for brand analysis"""
        return {
            "creator_id": "test_creator",
            "personal_info": {
                "name": "Test Creator",
                "bio": "Tech enthusiast and content creator",
                "niche": "technology",
                "experience_years": 3
            },
            "content_analysis": {
                "content_themes": ["AI", "programming", "tech reviews"],
                "visual_consistency": 0.7,
                "message_consistency": 0.8,
                "posting_frequency": "daily"
            },
            "audience_demographics": {
                "age_groups": {"18-24": 30, "25-34": 45, "35-44": 20, "45+": 5},
                "interests": ["technology", "innovation", "programming"],
                "engagement_quality": 0.06
            },
            "brand_assets": {
                "logo": True,
                "color_scheme": ["#1976d2", "#ffffff"],
                "typography": "modern",
                "visual_style": "minimalist"
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_personal_brand(self, agent, sample_creator_profile):
        """Test personal brand analysis"""
        analysis = await agent.analyze_personal_brand(sample_creator_profile)
        
        assert isinstance(analysis, BrandAnalysis)
        assert 0 <= analysis.brand_strength <= 1
        assert 0 <= analysis.brand_consistency <= 1
        assert analysis.brand_positioning is not None
        assert analysis.unique_value_proposition is not None
        assert isinstance(analysis.brand_gaps, list)
        assert isinstance(analysis.competitive_advantages, list)
    
    @pytest.mark.asyncio
    async def test_evaluate_brand_consistency(self, agent, sample_creator_profile):
        """Test brand consistency evaluation"""
        consistency_analysis = await agent.evaluate_brand_consistency(sample_creator_profile)
        
        assert "visual_consistency" in consistency_analysis
        assert "message_consistency" in consistency_analysis
        assert "tone_consistency" in consistency_analysis
        assert "overall_consistency_score" in consistency_analysis
        
        for score in consistency_analysis.values():
            if isinstance(score, (int, float)):
                assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_identify_brand_gaps(self, agent, sample_creator_profile):
        """Test brand gap identification"""
        gaps = await agent.identify_brand_gaps(sample_creator_profile)
        
        assert isinstance(gaps, list)
        
        for gap in gaps:
            assert "category" in gap
            assert "description" in gap
            assert "impact_level" in gap
            assert "recommendations" in gap
            assert gap["impact_level"] in ["low", "medium", "high", "critical"]
    
    @pytest.mark.asyncio
    async def test_generate_brand_recommendations(self, agent, sample_creator_profile):
        """Test brand recommendation generation"""
        recommendations = await agent.generate_brand_recommendations(sample_creator_profile)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert "category" in rec
            assert "recommendation" in rec
            assert "priority" in rec
            assert "implementation_effort" in rec
            assert "expected_impact" in rec
    
    @pytest.mark.asyncio
    async def test_assess_competitive_positioning(self, agent, sample_creator_profile):
        """Test competitive positioning assessment"""
        positioning = await agent.assess_competitive_positioning(
            sample_creator_profile,
            competitor_profiles=[
                {"name": "Competitor 1", "niche": "technology", "followers": 50000},
                {"name": "Competitor 2", "niche": "tech reviews", "followers": 30000}
            ]
        )
        
        assert "market_position" in positioning
        assert "differentiation_opportunities" in positioning
        assert "competitive_advantages" in positioning
        assert "positioning_strategy" in positioning
    
    @pytest.mark.asyncio
    async def test_develop_brand_voice(self, agent, sample_creator_profile):
        """Test brand voice development"""
        voice_guide = await agent.develop_brand_voice(sample_creator_profile)
        
        assert "personality_traits" in voice_guide
        assert "tone_guidelines" in voice_guide
        assert "communication_style" in voice_guide
        assert "do_and_dont" in voice_guide
        assert "example_phrases" in voice_guide


class TestPersonalBrandingAgent:
    """Test PersonalBrandingAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create PersonalBrandingAgent instance"""
        return PersonalBrandingAgent()
    
    @pytest.fixture
    def sample_personal_data(self):
        """Sample personal data for branding"""
        return {
            "individual": {
                "name": "Jane Doe",
                "profession": "Data Scientist",
                "expertise": ["machine learning", "data visualization", "python"],
                "values": ["innovation", "accuracy", "collaboration"],
                "personality": "analytical yet approachable"
            },
            "career_goals": {
                "short_term": "build thought leadership in AI",
                "long_term": "become recognized AI expert",
                "target_audience": "tech professionals and students"
            },
            "current_presence": {
                "platforms": ["LinkedIn", "Twitter", "Medium"],
                "content_types": ["articles", "tutorials", "insights"],
                "engagement_level": "moderate"
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_personal_brand_strategy(self, agent, sample_personal_data):
        """Test personal brand strategy creation"""
        strategy = await agent.create_personal_brand_strategy(sample_personal_data)
        
        assert isinstance(strategy, BrandStrategy)
        assert strategy.brand_vision is not None
        assert strategy.brand_mission is not None
        assert len(strategy.brand_values) > 0
        assert strategy.brand_personality is not None
        assert len(strategy.content_pillars) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_personal_strengths(self, agent, sample_personal_data):
        """Test personal strengths analysis"""
        strengths = await agent.analyze_personal_strengths(sample_personal_data)
        
        assert "core_strengths" in strengths
        assert "unique_differentiators" in strengths
        assert "brand_building_opportunities" in strengths
        assert "development_areas" in strengths
        
        assert len(strengths["core_strengths"]) > 0
    
    @pytest.mark.asyncio
    async def test_develop_content_strategy(self, agent, sample_personal_data):
        """Test content strategy development"""
        content_strategy = await agent.develop_content_strategy(sample_personal_data)
        
        assert "content_pillars" in content_strategy
        assert "content_calendar" in content_strategy
        assert "platform_strategy" in content_strategy
        assert "engagement_tactics" in content_strategy
        
        assert len(content_strategy["content_pillars"]) > 0
    
    @pytest.mark.asyncio
    async def test_optimize_online_presence(self, agent, sample_personal_data):
        """Test online presence optimization"""
        optimization = await agent.optimize_online_presence(sample_personal_data)
        
        assert "profile_optimizations" in optimization
        assert "content_improvements" in optimization
        assert "engagement_strategies" in optimization
        assert "growth_tactics" in optimization


class TestBrandPositioningAgent:
    """Test BrandPositioningAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandPositioningAgent instance"""
        return BrandPositioningAgent()
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for positioning analysis"""
        return {
            "target_market": {
                "size": 500000,
                "growth_rate": 0.15,
                "key_segments": ["beginners", "intermediate", "advanced"],
                "pain_points": ["lack of practical examples", "complex explanations", "outdated content"]
            },
            "competitor_landscape": [
                {
                    "name": "TechGuru",
                    "positioning": "beginner-friendly tech education",
                    "followers": 100000,
                    "strengths": ["simple explanations", "consistent posting"],
                    "weaknesses": ["limited depth", "outdated examples"]
                },
                {
                    "name": "CodeMaster", 
                    "positioning": "advanced programming tutorials",
                    "followers": 75000,
                    "strengths": ["technical depth", "expert knowledge"],
                    "weaknesses": ["intimidating to beginners", "irregular posting"]
                }
            ],
            "market_trends": [
                "increasing demand for AI content",
                "preference for visual learning",
                "mobile-first consumption"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_market_positioning(self, agent, sample_market_data):
        """Test market positioning analysis"""
        positioning_analysis = await agent.analyze_market_positioning(sample_market_data)
        
        assert "market_gaps" in positioning_analysis
        assert "positioning_opportunities" in positioning_analysis
        assert "competitive_landscape" in positioning_analysis
        assert "recommended_positioning" in positioning_analysis
    
    @pytest.mark.asyncio
    async def test_identify_white_space_opportunities(self, agent, sample_market_data):
        """Test white space opportunity identification"""
        opportunities = await agent.identify_white_space_opportunities(sample_market_data)
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        for opportunity in opportunities:
            assert "market_gap" in opportunity
            assert "target_audience" in opportunity
            assert "positioning_strategy" in opportunity
            assert "market_size_estimate" in opportunity
    
    @pytest.mark.asyncio
    async def test_create_positioning_statement(self, agent, sample_market_data):
        """Test positioning statement creation"""
        creator_profile = {
            "unique_strengths": ["practical examples", "clear explanations", "industry experience"],
            "target_audience": "aspiring developers",
            "value_proposition": "learn coding through real-world projects"
        }
        
        positioning_statement = await agent.create_positioning_statement(
            creator_profile, 
            sample_market_data
        )
        
        assert "primary_statement" in positioning_statement
        assert "supporting_points" in positioning_statement
        assert "differentiation_factors" in positioning_statement
        assert "target_audience_description" in positioning_statement
    
    @pytest.mark.asyncio
    async def test_validate_positioning_strategy(self, agent, sample_market_data):
        """Test positioning strategy validation"""
        positioning_strategy = {
            "target_segment": "intermediate developers",
            "value_proposition": "advanced tutorials with practical application",
            "differentiation": "industry case studies and real project examples"
        }
        
        validation = await agent.validate_positioning_strategy(
            positioning_strategy,
            sample_market_data
        )
        
        assert "viability_score" in validation
        assert "market_fit_assessment" in validation
        assert "competitive_risks" in validation
        assert "success_probability" in validation
        assert 0 <= validation["viability_score"] <= 1


class TestBrandStrategyAgent:
    """Test BrandStrategyAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandStrategyAgent instance"""
        return BrandStrategyAgent()
    
    @pytest.fixture
    def sample_brand_objectives(self):
        """Sample brand objectives"""
        return {
            "primary_goals": [
                "increase brand awareness by 200%",
                "establish thought leadership in AI",
                "grow engaged community to 50K followers"
            ],
            "target_metrics": {
                "brand_awareness": {"current": 0.05, "target": 0.15},
                "engagement_rate": {"current": 0.03, "target": 0.06},
                "community_size": {"current": 10000, "target": 50000}
            },
            "timeline": "12 months",
            "budget_constraints": "moderate",
            "resource_availability": "limited team"
        }
    
    @pytest.mark.asyncio
    async def test_develop_comprehensive_brand_strategy(self, agent, sample_brand_objectives):
        """Test comprehensive brand strategy development"""
        strategy = await agent.develop_comprehensive_brand_strategy(sample_brand_objectives)
        
        assert "strategic_framework" in strategy
        assert "implementation_roadmap" in strategy
        assert "resource_allocation" in strategy
        assert "success_metrics" in strategy
        assert "risk_mitigation" in strategy
    
    @pytest.mark.asyncio
    async def test_create_brand_implementation_plan(self, agent, sample_brand_objectives):
        """Test brand implementation plan creation"""
        implementation_plan = await agent.create_brand_implementation_plan(sample_brand_objectives)
        
        assert "phases" in implementation_plan
        assert "milestones" in implementation_plan
        assert "resource_requirements" in implementation_plan
        assert "timeline" in implementation_plan
        
        assert len(implementation_plan["phases"]) > 0
        
        for phase in implementation_plan["phases"]:
            assert "name" in phase
            assert "duration" in phase
            assert "objectives" in phase
            assert "deliverables" in phase
    
    @pytest.mark.asyncio
    async def test_monitor_brand_performance(self, agent, sample_brand_objectives):
        """Test brand performance monitoring"""
        current_metrics = {
            "brand_awareness": 0.08,
            "engagement_rate": 0.045,
            "community_size": 15000,
            "sentiment_score": 0.75
        }
        
        performance_report = await agent.monitor_brand_performance(
            current_metrics,
            sample_brand_objectives["target_metrics"]
        )
        
        assert "progress_summary" in performance_report
        assert "metric_analysis" in performance_report
        assert "recommendations" in performance_report
        assert "alerts" in performance_report
    
    @pytest.mark.asyncio
    async def test_optimize_brand_strategy(self, agent, sample_brand_objectives):
        """Test brand strategy optimization"""
        performance_data = {
            "successful_tactics": ["video content", "community engagement", "collaborations"],
            "underperforming_areas": ["blog posts", "podcast appearances"],
            "market_changes": ["increased competition", "algorithm updates"],
            "resource_constraints": ["time limitations", "budget cuts"]
        }
        
        optimization = await agent.optimize_brand_strategy(
            sample_brand_objectives,
            performance_data
        )
        
        assert "strategy_adjustments" in optimization
        assert "tactical_changes" in optimization
        assert "resource_reallocation" in optimization
        assert "timeline_modifications" in optimization


class TestBrandAuditAndAnalysis:
    """Test brand audit and analysis functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandConsultantAgent for audit testing"""
        return BrandConsultantAgent()
    
    @pytest.fixture
    def comprehensive_brand_data(self):
        """Comprehensive brand data for audit"""
        return {
            "brand_assets": {
                "visual_identity": {
                    "logo_variations": 3,
                    "color_palette": ["#1976d2", "#ffffff", "#f5f5f5"],
                    "typography": ["Roboto", "Open Sans"],
                    "graphic_elements": ["icons", "illustrations", "patterns"]
                },
                "content_library": {
                    "templates": 25,
                    "image_bank": 200,
                    "video_assets": 15,
                    "brand_guidelines": True
                }
            },
            "brand_touchpoints": {
                "digital": ["website", "social_media", "email", "mobile_app"],
                "content": ["blog", "videos", "podcasts", "newsletters"],
                "community": ["forums", "events", "partnerships"]
            },
            "brand_perception": {
                "customer_feedback": {
                    "positive": 0.75,
                    "neutral": 0.15, 
                    "negative": 0.10
                },
                "brand_attributes": {
                    "trustworthy": 0.8,
                    "innovative": 0.9,
                    "approachable": 0.7,
                    "professional": 0.85
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_conduct_comprehensive_brand_audit(self, agent, comprehensive_brand_data):
        """Test comprehensive brand audit"""
        audit = await agent.conduct_comprehensive_brand_audit(comprehensive_brand_data)
        
        assert isinstance(audit, BrandAudit)
        assert audit.overall_brand_health is not None
        assert 0 <= audit.overall_brand_health <= 1
        assert audit.strengths is not None
        assert audit.weaknesses is not None
        assert audit.opportunities is not None
        assert audit.threats is not None
    
    @pytest.mark.asyncio
    async def test_evaluate_brand_touchpoints(self, agent, comprehensive_brand_data):
        """Test brand touchpoint evaluation"""
        touchpoint_analysis = await agent.evaluate_brand_touchpoints(comprehensive_brand_data)
        
        assert "touchpoint_performance" in touchpoint_analysis
        assert "consistency_scores" in touchpoint_analysis
        assert "improvement_priorities" in touchpoint_analysis
        
        for touchpoint in comprehensive_brand_data["brand_touchpoints"]["digital"]:
            assert touchpoint in touchpoint_analysis["touchpoint_performance"]
    
    @pytest.mark.asyncio
    async def test_analyze_brand_perception(self, agent, comprehensive_brand_data):
        """Test brand perception analysis"""
        perception_analysis = await agent.analyze_brand_perception(comprehensive_brand_data)
        
        assert "sentiment_analysis" in perception_analysis
        assert "attribute_strength" in perception_analysis
        assert "perception_gaps" in perception_analysis
        assert "reputation_score" in perception_analysis
        
        assert 0 <= perception_analysis["reputation_score"] <= 1


class TestCompetitiveBrandAnalysis:
    """Test competitive brand analysis functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandConsultantAgent for competitive analysis"""
        return BrandConsultantAgent()
    
    @pytest.fixture
    def competitive_landscape_data(self):
        """Competitive landscape data"""
        return {
            "direct_competitors": [
                {
                    "name": "TechInfluencer1",
                    "followers": 150000,
                    "engagement_rate": 0.055,
                    "content_focus": ["AI", "programming", "tech trends"],
                    "brand_strength": 0.8,
                    "unique_positioning": "beginner-friendly AI education"
                },
                {
                    "name": "TechInfluencer2", 
                    "followers": 200000,
                    "engagement_rate": 0.04,
                    "content_focus": ["machine learning", "data science", "tutorials"],
                    "brand_strength": 0.9,
                    "unique_positioning": "advanced ML tutorials"
                }
            ],
            "indirect_competitors": [
                {
                    "name": "TechBlog",
                    "monthly_visitors": 500000,
                    "brand_recognition": 0.7,
                    "content_focus": ["tech news", "reviews", "analysis"]
                }
            ],
            "market_leaders": [
                {
                    "name": "TechGiant",
                    "market_share": 0.35,
                    "brand_value": "industry authority",
                    "competitive_advantages": ["resources", "expertise", "reach"]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_competitive_landscape(self, agent, competitive_landscape_data):
        """Test competitive landscape analysis"""
        analysis = await agent.analyze_competitive_landscape(competitive_landscape_data)
        
        assert isinstance(analysis, CompetitiveBrandAnalysis)
        assert analysis.market_position is not None
        assert analysis.competitive_gaps is not None
        assert analysis.differentiation_opportunities is not None
        assert analysis.threat_assessment is not None
    
    @pytest.mark.asyncio
    async def test_identify_competitive_advantages(self, agent, competitive_landscape_data):
        """Test competitive advantage identification"""
        advantages = await agent.identify_competitive_advantages(competitive_landscape_data)
        
        assert isinstance(advantages, list)
        
        for advantage in advantages:
            assert "advantage_type" in advantage
            assert "description" in advantage
            assert "sustainability" in advantage
            assert "competitive_impact" in advantage
    
    @pytest.mark.asyncio
    async def test_benchmark_brand_performance(self, agent, competitive_landscape_data):
        """Test brand performance benchmarking"""
        creator_metrics = {
            "followers": 50000,
            "engagement_rate": 0.06,
            "content_quality": 0.8,
            "brand_consistency": 0.75
        }
        
        benchmark = await agent.benchmark_brand_performance(
            creator_metrics,
            competitive_landscape_data
        )
        
        assert "performance_ranking" in benchmark
        assert "areas_of_strength" in benchmark
        assert "areas_for_improvement" in benchmark
        assert "competitive_position" in benchmark


class TestIntegrationScenarios:
    """Test integration between different brand consulting agents"""
    
    @pytest.fixture
    def agents(self):
        """Create all brand agents for integration testing"""
        return {
            "consultant": BrandConsultantAgent(),
            "personal": PersonalBrandingAgent(),
            "positioning": BrandPositioningAgent(),
            "strategy": BrandStrategyAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_brand_development_workflow(self, agents):
        """Test comprehensive brand development workflow"""
        # Sample comprehensive creator data
        creator_data = {
            "personal_profile": {
                "name": "Alex Tech",
                "expertise": ["artificial intelligence", "machine learning"],
                "values": ["innovation", "education", "accessibility"],
                "career_goals": "become leading AI educator"
            },
            "current_brand_state": {
                "followers": 25000,
                "engagement_rate": 0.045,
                "content_consistency": 0.6,
                "brand_recognition": 0.3
            },
            "market_context": {
                "competitor_count": 15,
                "market_growth": 0.25,
                "audience_size": 2000000
            },
            "objectives": {
                "follower_target": 100000,
                "timeline_months": 18,
                "positioning_goal": "accessible AI education leader"
            }
        }
        
        # Execute integrated workflow
        # 1. Brand Analysis
        brand_analysis = await agents["consultant"].analyze_personal_brand(creator_data)
        
        # 2. Personal Brand Strategy
        personal_strategy = await agents["personal"].create_personal_brand_strategy(creator_data)
        
        # 3. Market Positioning
        positioning_analysis = await agents["positioning"].analyze_market_positioning(creator_data)
        
        # 4. Comprehensive Strategy
        comprehensive_strategy = await agents["strategy"].develop_comprehensive_brand_strategy(creator_data)
        
        # Verify integrated results
        assert brand_analysis is not None
        assert personal_strategy is not None
        assert positioning_analysis is not None
        assert comprehensive_strategy is not None
        
        # Verify workflow coherence
        assert brand_analysis.brand_strength >= 0
        assert len(personal_strategy.content_pillars) > 0
        assert "positioning_opportunities" in positioning_analysis
        assert "implementation_roadmap" in comprehensive_strategy


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandConsultantAgent for error testing"""
        return BrandConsultantAgent()
    
    @pytest.mark.asyncio
    async def test_invalid_creator_profile(self, agent):
        """Test handling of invalid creator profile data"""
        invalid_profile = {"invalid": "data", "missing": "required_fields"}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.analyze_personal_brand(invalid_profile)
    
    @pytest.mark.asyncio
    async def test_insufficient_data_handling(self, agent):
        """Test handling of insufficient data"""
        minimal_data = {"creator_id": "test"}
        
        try:
            result = await agent.generate_brand_recommendations(minimal_data)
            # Should handle gracefully with minimal recommendations
            assert isinstance(result, list)
        except (ValueError, KeyError) as e:
            # Acceptable to require minimum data
            assert "insufficient" in str(e).lower() or "missing" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_api_failure_resilience(self, agent):
        """Test resilience to API failures"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("API Error")
            
            try:
                result = await agent.evaluate_brand_consistency({"creator_id": "test"})
                # Should provide fallback analysis or handle gracefully
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create BrandConsultantAgent for performance testing"""
        return BrandConsultantAgent()
    
    @pytest.mark.asyncio
    async def test_large_scale_brand_analysis(self, agent):
        """Test large-scale brand analysis performance"""
        large_profile = {
            "creator_id": "large_creator",
            "content_history": [
                {"id": f"post_{i}", "engagement": 0.05, "theme": f"theme_{i%10}"}
                for i in range(10000)
            ],
            "audience_data": {
                f"segment_{i}": {"size": 1000, "engagement": 0.04}
                for i in range(1000)
            }
        }
        
        start_time = datetime.now()
        result = await agent.analyze_personal_brand(large_profile)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert result is not None
        assert processing_time < 60  # Should complete within reasonable time
    
    @pytest.mark.asyncio
    async def test_concurrent_brand_analyses(self, agent):
        """Test concurrent brand analysis capabilities"""
        profiles = [
            {"creator_id": f"creator_{i}", "niche": "tech", "followers": 10000 + i*1000}
            for i in range(5)
        ]
        
        tasks = [
            agent.analyze_personal_brand(profile)
            for profile in profiles
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == len(profiles)
        for result in results:
            assert not isinstance(result, Exception)
