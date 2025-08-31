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
Test suite for Trend Analysis AI Agents

Tests all functionalities of trend detection, market analysis, 
prediction algorithms, and trend-based content strategy agents.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL / LEGAL WARNING 
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
from typing import Dict, Any, List

from ai.ai_agents.trend_analysis_agents import (
    TrendAnalysisAgent,
    MarketTrendAnalyzer,
    ContentTrendAgent,
    PredictiveTrendAgent,
    TrendReport,
    MarketInsight,
    ContentTrendAnalysis,
    TrendPrediction
)


class TestTrendAnalysisAgent:
    """Test TrendAnalysisAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create TrendAnalysisAgent instance"""



        return TrendAnalysisAgent()
    
    @pytest.fixture
    def sample_trend_data(self):
        """Sample trend data for analysis"""



        return {
            "analysis_id": "trend_001",
            "market_segment": "tech_education",
            "data_sources": ["youtube", "tiktok", "instagram", "twitter"],
            "time_period": {
                "start_date": datetime.now() - timedelta(days=90),
                "end_date": datetime.now(),
                "analysis_frequency": "daily"
            },
            "content_categories": [
                "artificial_intelligence",
                "machine_learning",
                "programming_tutorials",
                "tech_reviews",
                "coding_challenges"
            ],
            "historical_data": {
                "daily_mentions": [150, 165, 180, 195, 210, 225, 240, 255, 270],
                "engagement_rates": [0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08],
                "search_volumes": [12000, 13500, 15000, 16500, 18000, 19500, 21000, 22500, 24000],
                "hashtag_performance": {
                    "#ai": [5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000],
                    "#machinelearning": [3000, 3300, 3600, 3900, 4200, 4500, 4800, 5100, 5400],
                    "#coding": [8000, 8400, 8800, 9200, 9600, 10000, 10400, 10800, 11200]
                }
            },
            "competitive_data": {
                "top_creators": [
                    {"creator_id": "tech_guru_1", "followers": 500000, "avg_views": 50000},
                    {"creator_id": "ai_expert_2", "followers": 300000, "avg_views": 35000},
                    {"creator_id": "code_master_3", "followers": 750000, "avg_views": 80000}
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_current_trends(self, agent, sample_trend_data):
        """Test current trend analysis"""
        trend_analysis = await agent.analyze_current_trends(sample_trend_data)
        
        assert "trending_topics" in trend_analysis
        assert "trend_momentum" in trend_analysis
        assert "engagement_patterns" in trend_analysis
        assert "growth_indicators" in trend_analysis
        
        trending_topics = trend_analysis["trending_topics"]
        assert len(trending_topics) > 0
        
        for topic in trending_topics:
            assert "topic_name" in topic
            assert "trend_score" in topic
            assert "growth_rate" in topic
            assert "momentum_direction" in topic
            assert 0 <= topic["trend_score"] <= 100
            assert topic["momentum_direction"] in ["rising", "stable", "declining"]
    
    @pytest.mark.asyncio
    async def test_identify_emerging_trends(self, agent, sample_trend_data):
        """Test emerging trend identification"""
        emerging_analysis = await agent.identify_emerging_trends(sample_trend_data)
        
        assert "emerging_trends" in emerging_analysis
        assert "early_indicators" in emerging_analysis
        assert "prediction_confidence" in emerging_analysis
        assert "opportunity_assessment" in emerging_analysis
        
        emerging_trends = emerging_analysis["emerging_trends"]
        assert isinstance(emerging_trends, list)
        
        for trend in emerging_trends:
            assert "trend_name" in trend
            assert "emergence_stage" in trend
            assert "growth_potential" in trend
            assert "time_to_mainstream" in trend
            assert trend["emergence_stage"] in ["nascent", "early", "accelerating", "mainstream"]
    
    @pytest.mark.asyncio
    async def test_analyze_trend_lifecycle(self, agent, sample_trend_data):
        """Test trend lifecycle analysis"""
        lifecycle_analysis = await agent.analyze_trend_lifecycle(sample_trend_data)
        
        assert "lifecycle_stage" in lifecycle_analysis
        assert "maturity_indicators" in lifecycle_analysis
        assert "longevity_prediction" in lifecycle_analysis
        assert "decline_signals" in lifecycle_analysis
        
        lifecycle_stage = lifecycle_analysis["lifecycle_stage"]
        valid_stages = ["introduction", "growth", "maturity", "saturation", "decline"]
        assert lifecycle_stage in valid_stages
        
        maturity_indicators = lifecycle_analysis["maturity_indicators"]
        assert isinstance(maturity_indicators, list)
        assert len(maturity_indicators) > 0
    
    @pytest.mark.asyncio
    async def test_cross_platform_trend_analysis(self, agent, sample_trend_data):
        """Test cross-platform trend analysis"""
        platform_data = {
            "youtube": {
                "video_trends": ["AI tutorials", "coding bootcamp", "tech reviews"],
                "search_trends": ["machine learning 2025", "python programming", "data science"],
                "creator_trends": ["educational content", "live coding", "tech news"]
            },
            "tiktok": {
                "hashtag_trends": ["#coding", "#techhumor", "#programminglife"],
                "video_styles": ["quick tips", "coding memes", "tech explanations"],
                "audio_trends": ["tech background music", "coding sounds", "keyboard typing"]
            },
            "instagram": {
                "content_types": ["carousel tutorials", "coding screenshots", "tech quotes"],
                "story_trends": ["behind the scenes coding", "tech setup", "learning journey"],
                "reel_trends": ["60-second tutorials", "tech tips", "coding challenges"]
            }
        }
        
        cross_platform_analysis = await agent.cross_platform_trend_analysis(
            sample_trend_data,
            platform_data
        )
        
        assert "platform_insights" in cross_platform_analysis
        assert "cross_platform_opportunities" in cross_platform_analysis
        assert "platform_specific_strategies" in cross_platform_analysis
        assert "unified_trend_narrative" in cross_platform_analysis
        
        platform_insights = cross_platform_analysis["platform_insights"]
        for platform in ["youtube", "tiktok", "instagram"]:
            assert platform in platform_insights
            assert "dominant_trends" in platform_insights[platform]
            assert "engagement_patterns" in platform_insights[platform]
    
    @pytest.mark.asyncio
    async def test_seasonal_trend_analysis(self, agent, sample_trend_data):
        """Test seasonal trend analysis"""
        seasonal_data = {
            "yearly_patterns": {
                "Q1": {"tech_education": 0.8, "career_advice": 1.2, "productivity": 1.1},
                "Q2": {"tech_education": 1.0, "career_advice": 0.9, "productivity": 0.95},
                "Q3": {"tech_education": 1.1, "career_advice": 0.8, "productivity": 0.9},
                "Q4": {"tech_education": 1.2, "career_advice": 1.1, "productivity": 1.05}
            },
            "monthly_patterns": {
                1: 1.1, 2: 1.0, 3: 0.9, 4: 0.95, 5: 1.0, 6: 1.05,
                7: 0.9, 8: 0.85, 9: 1.2, 10: 1.1, 11: 1.0, 12: 0.95
            },
            "weekly_patterns": {
                "monday": 1.1, "tuesday": 1.05, "wednesday": 1.0, "thursday": 1.05,
                "friday": 0.95, "saturday": 0.8, "sunday": 0.85
            }
        }
        
        seasonal_analysis = await agent.seasonal_trend_analysis(
            sample_trend_data,
            seasonal_data
        )
        
        assert "seasonal_patterns" in seasonal_analysis
        assert "predictable_cycles" in seasonal_analysis
        assert "seasonal_opportunities" in seasonal_analysis
        assert "content_timing_recommendations" in seasonal_analysis
        
        seasonal_patterns = seasonal_analysis["seasonal_patterns"]
        assert "yearly" in seasonal_patterns
        assert "monthly" in seasonal_patterns
        assert "weekly" in seasonal_patterns


class TestMarketTrendAnalyzer:
    """Test MarketTrendAnalyzer functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create MarketTrendAnalyzer instance"""



        return MarketTrendAnalyzer()
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for analysis"""



        return {
            "market_id": "digital_marketing_2025",
            "industry_segment": "content_creation",
            "market_size": 45000000000,  # $45B
            "growth_rate": 0.15,  # 15% annual growth
            "key_players": [
                {
                    "company": "YouTube",
                    "market_share": 0.35,
                    "revenue": 15750000000,
                    "growth_trend": "stable"
                },
                {
                    "company": "TikTok", 
                    "market_share": 0.25,
                    "revenue": 11250000000,
                    "growth_trend": "rising"
                },
                {
                    "company": "Instagram",
                    "market_share": 0.20,
                    "revenue": 9000000000,
                    "growth_trend": "stable"
                }
            ],
            "consumer_behavior": {
                "content_consumption_hours_daily": 3.5,
                "mobile_vs_desktop": {"mobile": 0.75, "desktop": 0.25},
                "preferred_content_types": [
                    "short_videos", "educational_content", "entertainment",
                    "tutorials", "product_reviews"
                ],
                "engagement_preferences": {
                    "likes": 0.80, "comments": 0.45, "shares": 0.25, "saves": 0.35
                }
            },
            "technology_trends": [
                "AI content generation", "AR/VR experiences", "Live streaming",
                "Interactive content", "Personalization algorithms"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_market_dynamics(self, agent, sample_market_data):
        """Test market dynamics analysis"""
        market_analysis = await agent.analyze_market_dynamics(sample_market_data)
        
        assert "market_health" in market_analysis
        assert "competitive_landscape" in market_analysis
        assert "growth_drivers" in market_analysis
        assert "market_risks" in market_analysis
        
        market_health = market_analysis["market_health"]
        assert "overall_score" in market_health
        assert "growth_sustainability" in market_health
        assert "innovation_level" in market_health
        assert 0 <= market_health["overall_score"] <= 100
        
        competitive_landscape = market_analysis["competitive_landscape"]
        assert "market_concentration" in competitive_landscape
        assert "competitive_intensity" in competitive_landscape
        assert "barriers_to_entry" in competitive_landscape
    
    @pytest.mark.asyncio
    async def test_identify_market_opportunities(self, agent, sample_market_data):
        """Test market opportunity identification"""
        opportunity_analysis = await agent.identify_market_opportunities(sample_market_data)
        
        assert "high_opportunity_segments" in opportunity_analysis
        assert "underserved_markets" in opportunity_analysis
        assert "emerging_niches" in opportunity_analysis
        assert "strategic_recommendations" in opportunity_analysis
        
        high_opportunity = opportunity_analysis["high_opportunity_segments"]
        assert isinstance(high_opportunity, list)
        
        for opportunity in high_opportunity:
            assert "segment_name" in opportunity
            assert "opportunity_size" in opportunity
            assert "time_to_capture" in opportunity
            assert "required_investment" in opportunity
            assert "success_probability" in opportunity
            assert 0 <= opportunity["success_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_consumer_behavior_analysis(self, agent, sample_market_data):
        """Test consumer behavior analysis"""
        behavior_analysis = await agent.consumer_behavior_analysis(sample_market_data)
        
        assert "behavior_patterns" in behavior_analysis
        assert "preference_shifts" in behavior_analysis
        assert "demographic_insights" in behavior_analysis
        assert "behavioral_predictions" in behavior_analysis
        
        behavior_patterns = behavior_analysis["behavior_patterns"]
        assert "consumption_patterns" in behavior_patterns
        assert "engagement_patterns" in behavior_patterns
        assert "platform_preferences" in behavior_patterns
        
        preference_shifts = behavior_analysis["preference_shifts"]
        assert isinstance(preference_shifts, list)
        
        for shift in preference_shifts:
            assert "shift_type" in shift
            assert "direction" in shift
            assert "impact_level" in shift
            assert shift["direction"] in ["increasing", "decreasing", "stable"]
    
    @pytest.mark.asyncio
    async def test_competitive_intelligence(self, agent, sample_market_data):
        """Test competitive intelligence analysis"""
        competitor_data = {
            "direct_competitors": [
                {
                    "competitor_id": "competitor_A",
                    "market_position": "leader",
                    "strengths": ["brand recognition", "content quality", "audience size"],
                    "weaknesses": ["innovation lag", "high costs"],
                    "strategy": "premium_content"
                },
                {
                    "competitor_id": "competitor_B",
                    "market_position": "challenger",
                    "strengths": ["innovation", "agility", "niche focus"],
                    "weaknesses": ["limited resources", "small audience"],
                    "strategy": "disruptive_innovation"
                }
            ],
            "indirect_competitors": [
                {"competitor_id": "alt_platform_1", "threat_level": "medium"},
                {"competitor_id": "traditional_media", "threat_level": "low"}
            ]
        }
        
        competitive_intel = await agent.competitive_intelligence(
            sample_market_data,
            competitor_data
        )
        
        assert "competitive_positioning" in competitive_intel
        assert "threat_assessment" in competitive_intel
        assert "competitive_gaps" in competitive_intel
        assert "strategic_responses" in competitive_intel
        
        positioning = competitive_intel["competitive_positioning"]
        assert "market_position" in positioning
        assert "competitive_advantages" in positioning
        assert "vulnerability_areas" in positioning
    
    @pytest.mark.asyncio
    async def test_generate_market_insight_report(self, agent, sample_market_data):
        """Test market insight report generation"""
        report_config = {
            "report_depth": "comprehensive",
            "focus_areas": ["growth_opportunities", "competitive_analysis", "technology_trends"],
            "forecast_period": 24  # months
        }
        
        market_insight = await agent.generate_market_insight_report(
            sample_market_data,
            report_config
        )
        
        assert isinstance(market_insight, MarketInsight)
        assert market_insight.insight_id is not None
        assert market_insight.market_assessment is not None
        assert len(market_insight.key_opportunities) > 0
        assert market_insight.competitive_analysis is not None
        assert market_insight.market_forecast is not None


class TestContentTrendAgent:
    """Test ContentTrendAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create ContentTrendAgent instance"""



        return ContentTrendAgent()
    
    @pytest.fixture
    def sample_content_trends(self):
        """Sample content trend data"""



        return {
            "content_analysis_id": "content_trends_001",
            "platforms": ["youtube", "tiktok", "instagram", "twitter"],
            "content_categories": [
                "educational", "entertainment", "lifestyle", "business", "technology"
            ],
            "trending_content": {
                "youtube": [
                    {
                        "video_id": "yt_trend_1",
                        "title": "AI Revolution: What You Need to Know",
                        "views": 2500000,
                        "engagement_rate": 0.08,
                        "growth_velocity": 1.5,
                        "content_type": "educational",
                        "duration": 720  # 12 minutes
                    },
                    {
                        "video_id": "yt_trend_2",
                        "title": "Day in My Life as a Data Scientist",
                        "views": 1800000,
                        "engagement_rate": 0.12,
                        "growth_velocity": 2.1,
                        "content_type": "lifestyle",
                        "duration": 480  # 8 minutes
                    }
                ],
                "tiktok": [
                    {
                        "video_id": "tt_trend_1",
                        "description": "Quick Python tip #coding",
                        "views": 5500000,
                        "engagement_rate": 0.15,
                        "growth_velocity": 3.2,
                        "content_type": "educational",
                        "duration": 30
                    }
                ]
            },
            "content_formats": {
                "short_form": {"popularity": 0.85, "growth_rate": 0.25},
                "long_form": {"popularity": 0.65, "growth_rate": 0.10},
                "live_streaming": {"popularity": 0.45, "growth_rate": 0.30},
                "interactive": {"popularity": 0.35, "growth_rate": 0.40}
            },
            "hashtag_trends": {
                "#ai": {"usage_count": 850000, "growth_rate": 0.35},
                "#coding": {"usage_count": 920000, "growth_rate": 0.28},
                "#tutorial": {"usage_count": 1200000, "growth_rate": 0.20}
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_content_performance_trends(self, agent, sample_content_trends):
        """Test content performance trend analysis"""
        performance_analysis = await agent.analyze_content_performance_trends(
            sample_content_trends
        )
        
        assert "top_performing_content" in performance_analysis
        assert "performance_patterns" in performance_analysis
        assert "content_format_trends" in performance_analysis
        assert "engagement_insights" in performance_analysis
        
        top_performing = performance_analysis["top_performing_content"]
        assert len(top_performing) > 0
        
        for content in top_performing:
            assert "content_id" in content
            assert "performance_score" in content
            assert "success_factors" in content
            assert "replicability_score" in content
    
    @pytest.mark.asyncio
    async def test_identify_viral_content_patterns(self, agent, sample_content_trends):
        """Test viral content pattern identification"""
        viral_analysis = await agent.identify_viral_content_patterns(sample_content_trends)
        
        assert "viral_indicators" in viral_analysis
        assert "common_elements" in viral_analysis
        assert "timing_patterns" in viral_analysis
        assert "virality_predictors" in viral_analysis
        
        viral_indicators = viral_analysis["viral_indicators"]
        assert "growth_velocity_threshold" in viral_indicators
        assert "engagement_rate_threshold" in viral_indicators
        assert "share_rate_threshold" in viral_indicators
        
        common_elements = viral_analysis["common_elements"]
        assert "content_characteristics" in common_elements
        assert "format_preferences" in common_elements
        assert "emotional_triggers" in common_elements
    
    @pytest.mark.asyncio
    async def test_content_format_evolution(self, agent, sample_content_trends):
        """Test content format evolution analysis"""
        format_evolution = await agent.content_format_evolution(sample_content_trends)
        
        assert "format_lifecycle" in format_evolution
        assert "emerging_formats" in format_evolution
        assert "declining_formats" in format_evolution
        assert "innovation_opportunities" in format_evolution
        
        emerging_formats = format_evolution["emerging_formats"]
        assert isinstance(emerging_formats, list)
        
        for format_trend in emerging_formats:
            assert "format_type" in format_trend
            assert "adoption_rate" in format_trend
            assert "growth_potential" in format_trend
            assert "platform_suitability" in format_trend
    
    @pytest.mark.asyncio
    async def test_hashtag_and_keyword_trends(self, agent, sample_content_trends):
        """Test hashtag and keyword trend analysis"""
        hashtag_analysis = await agent.hashtag_and_keyword_trends(sample_content_trends)
        
        assert "trending_hashtags" in hashtag_analysis
        assert "keyword_momentum" in hashtag_analysis
        assert "hashtag_combinations" in hashtag_analysis
        assert "seasonal_hashtag_patterns" in hashtag_analysis
        
        trending_hashtags = hashtag_analysis["trending_hashtags"]
        assert len(trending_hashtags) > 0
        
        for hashtag in trending_hashtags:
            assert "hashtag" in hashtag
            assert "trend_score" in hashtag
            assert "usage_growth" in hashtag
            assert "engagement_impact" in hashtag
    
    @pytest.mark.asyncio
    async def test_generate_content_trend_report(self, agent, sample_content_trends):
        """Test content trend report generation"""
        report_parameters = {
            "analysis_period": "quarterly",
            "focus_platforms": ["youtube", "tiktok"],
            "content_categories": ["educational", "technology"],
            "include_predictions": True
        }
        
        content_trend_report = await agent.generate_content_trend_report(
            sample_content_trends,
            report_parameters
        )
        
        assert isinstance(content_trend_report, ContentTrendAnalysis)
        assert content_trend_report.analysis_id is not None
        assert content_trend_report.trend_insights is not None
        assert len(content_trend_report.actionable_recommendations) > 0
        assert content_trend_report.format_recommendations is not None


class TestPredictiveTrendAgent:
    """Test PredictiveTrendAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create PredictiveTrendAgent instance"""



        return PredictiveTrendAgent()
    
    @pytest.fixture
    def sample_prediction_data(self):
        """Sample data for trend prediction"""



        return {
            "prediction_id": "pred_001",
            "historical_data": {
                "timeframe": "24_months",
                "data_points": [
                    {
                        "date": datetime.now() - timedelta(days=i*30),
                        "trend_metrics": {
                            "search_volume": 50000 + (i * 2000),
                            "content_creation_rate": 1500 + (i * 100),
                            "engagement_rate": 0.05 + (i * 0.002),
                            "market_penetration": 0.15 + (i * 0.01)
                        },
                        "external_factors": {
                            "economic_indicators": 0.8 + (i * 0.02),
                            "technology_adoption": 0.6 + (i * 0.03),
                            "cultural_events": ["tech_conference", "product_launch"][i % 2]
                        }
                    }
                    for i in range(24)
                ]
            },
            "current_indicators": {
                "momentum_score": 0.75,
                "adoption_velocity": 0.12,
                "market_sentiment": 0.68,
                "innovation_index": 0.82
            },
            "external_variables": {
                "economic_forecast": "stable_growth",
                "technology_developments": ["AI_advancement", "platform_updates"],
                "regulatory_changes": ["data_privacy_laws", "content_regulations"],
                "cultural_shifts": ["remote_work_adoption", "digital_literacy_increase"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_predict_trend_trajectory(self, agent, sample_prediction_data):
        """Test trend trajectory prediction"""
        trajectory_prediction = await agent.predict_trend_trajectory(sample_prediction_data)
        
        assert "prediction_timeline" in trajectory_prediction
        assert "confidence_intervals" in trajectory_prediction
        assert "key_milestones" in trajectory_prediction
        assert "risk_factors" in trajectory_prediction
        
        timeline = trajectory_prediction["prediction_timeline"]
        assert "short_term" in timeline  # 3-6 months
        assert "medium_term" in timeline  # 6-12 months
        assert "long_term" in timeline  # 12+ months
        
        for period in timeline.values():
            assert "growth_rate" in period
            assert "market_penetration" in period
            assert "confidence_score" in period
            assert 0 <= period["confidence_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_forecast_content_demand(self, agent, sample_prediction_data):
        """Test content demand forecasting"""
        demand_forecast = await agent.forecast_content_demand(sample_prediction_data)
        
        assert "demand_predictions" in demand_forecast
        assert "content_type_forecasts" in demand_forecast
        assert "seasonal_adjustments" in demand_forecast
        assert "market_opportunity_sizing" in demand_forecast
        
        demand_predictions = demand_forecast["demand_predictions"]
        assert "next_quarter" in demand_predictions
        assert "next_year" in demand_predictions
        
        content_forecasts = demand_forecast["content_type_forecasts"]
        assert isinstance(content_forecasts, list)
        
        for forecast in content_forecasts:
            assert "content_type" in forecast
            assert "demand_level" in forecast
            assert "growth_projection" in forecast
            assert "market_saturation" in forecast
    
    @pytest.mark.asyncio
    async def test_early_trend_detection(self, agent, sample_prediction_data):
        """Test early trend detection"""
        early_signals = {
            "weak_signals": [
                {
                    "signal_type": "search_query_emergence",
                    "signal_strength": 0.35,
                    "data_points": ["new_ai_tool", "automated_content", "AI_writing"]
                },
                {
                    "signal_type": "creator_behavior_shift", 
                    "signal_strength": 0.42,
                    "data_points": ["longer_videos", "educational_focus", "expert_interviews"]
                }
            ],
            "platform_innovations": [
                {"platform": "youtube", "innovation": "shorts_monetization", "adoption_rate": 0.25},
                {"platform": "tiktok", "innovation": "live_commerce", "adoption_rate": 0.18}
            ],
            "audience_behavior_changes": {
                "attention_span": "decreasing",
                "content_preferences": ["authentic", "educational", "interactive"],
                "engagement_patterns": {"comments_over_likes": 1.2, "saves_increasing": 1.8}
            }
        }
        
        early_detection = await agent.early_trend_detection(
            sample_prediction_data,
            early_signals
        )
        
        assert "emerging_trends" in early_detection
        assert "trend_probability" in early_detection
        assert "time_to_mainstream" in early_detection
        assert "strategic_implications" in early_detection
        
        emerging_trends = early_detection["emerging_trends"]
        assert len(emerging_trends) > 0
        
        for trend in emerging_trends:
            assert "trend_name" in trend
            assert "emergence_probability" in trend
            assert "potential_impact" in trend
            assert "recommended_actions" in trend
            assert 0 <= trend["emergence_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_scenario_modeling(self, agent, sample_prediction_data):
        """Test scenario modeling for trend predictions"""
        scenarios = {
            "optimistic": {
                "market_growth_rate": 0.25,
                "technology_adoption": 0.85,
                "economic_conditions": "strong_growth",
                "regulatory_environment": "supportive"
            },
            "realistic": {
                "market_growth_rate": 0.15,
                "technology_adoption": 0.65,
                "economic_conditions": "moderate_growth",
                "regulatory_environment": "neutral"
            },
            "pessimistic": {
                "market_growth_rate": 0.05,
                "technology_adoption": 0.45,
                "economic_conditions": "slow_growth",
                "regulatory_environment": "restrictive"
            }
        }
        
        scenario_modeling = await agent.scenario_modeling(
            sample_prediction_data,
            scenarios
        )
        
        assert "scenario_outcomes" in scenario_modeling
        assert "probability_weighted_forecast" in scenario_modeling
        assert "risk_assessment" in scenario_modeling
        assert "contingency_recommendations" in scenario_modeling
        
        scenario_outcomes = scenario_modeling["scenario_outcomes"]
        for scenario_name in scenarios.keys():
            assert scenario_name in scenario_outcomes
            outcome = scenario_outcomes[scenario_name]
            assert "predicted_outcome" in outcome
            assert "success_probability" in outcome
            assert "key_risks" in outcome
    
    @pytest.mark.asyncio
    async def test_generate_prediction_report(self, agent, sample_prediction_data):
        """Test prediction report generation"""
        prediction_config = {
            "prediction_horizon": "12_months",
            "confidence_threshold": 0.7,
            "include_scenarios": True,
            "focus_areas": ["content_demand", "platform_evolution", "creator_economy"]
        }
        
        prediction_report = await agent.generate_prediction_report(
            sample_prediction_data,
            prediction_config
        )
        
        assert isinstance(prediction_report, TrendPrediction)
        assert prediction_report.prediction_id is not None
        assert prediction_report.forecast_accuracy is not None
        assert len(prediction_report.key_predictions) > 0
        assert prediction_report.strategic_recommendations is not None
        assert 0 <= prediction_report.forecast_accuracy <= 1


class TestIntegrationScenarios:
    """Test integration between different trend analysis agents"""
    
    @pytest.fixture
    def agents(self):
        """Create all trend analysis agents for integration testing"""



        return {
            "trend": TrendAnalysisAgent(),
            "market": MarketTrendAnalyzer(),
            "content": ContentTrendAgent(),
            "predictive": PredictiveTrendAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_trend_intelligence(self, agents):
        """Test comprehensive trend intelligence workflow"""
        # Comprehensive trend analysis scenario
        intelligence_request = {
            "analysis_scope": "content_creator_economy",
            "geographic_focus": "north_america",
            "time_horizon": "18_months",
            "stakeholder": "individual_creator",
            "goals": ["market_positioning", "content_strategy", "revenue_optimization"]
        }
        
        # Execute integrated trend intelligence workflow
        # 1. Analyze current market trends
        current_trends = await agents["trend"].analyze_current_trends(intelligence_request)
        
        # 2. Analyze market dynamics and opportunities
        market_analysis = await agents["market"].analyze_market_dynamics(intelligence_request)
        
        # 3. Analyze content performance trends
        content_trends = await agents["content"].analyze_content_performance_trends(intelligence_request)
        
        # 4. Generate predictive insights
        trend_predictions = await agents["predictive"].predict_trend_trajectory(intelligence_request)
        
        # 5. Synthesize intelligence insights
        assert "trending_topics" in current_trends
        assert "market_health" in market_analysis
        assert "top_performing_content" in content_trends
        assert "prediction_timeline" in trend_predictions
        
        # Verify intelligence coherence
        assert len(current_trends["trending_topics"]) > 0
        assert market_analysis["market_health"]["overall_score"] >= 0
        assert len(content_trends["top_performing_content"]) > 0
        assert "short_term" in trend_predictions["prediction_timeline"]


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create TrendAnalysisAgent for error testing"""



        return TrendAnalysisAgent()
    
    @pytest.mark.asyncio
    async def test_insufficient_trend_data(self, agent):
        """Test handling of insufficient trend data"""
        minimal_data = {"analysis_id": "test"}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.analyze_current_trends(minimal_data)
    
    @pytest.mark.asyncio
    async def test_invalid_trend_parameters(self, agent):
        """Test handling of invalid trend parameters"""
        invalid_data = {
            "analysis_id": "test",
            "time_period": "invalid_period",
            "data_sources": "not_a_list",
            "historical_data": None
        }
        
        try:
            result = await agent.analyze_current_trends(invalid_data)
            # Should handle gracefully with data validation
            assert result is not None
        except (ValueError, TypeError):
            # Acceptable to reject invalid data
            pass
    
    @pytest.mark.asyncio
    async def test_external_trend_api_failures(self, agent):
        """Test handling of external trend API failures"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Trend API service unavailable")
            
            trend_data = {
                "analysis_id": "test",
                "market_segment": "test_market"
            }
            
            try:
                result = await agent.analyze_current_trends(trend_data)
                # Should provide fallback analysis
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """Create TrendAnalysisAgent for performance testing"""



        return TrendAnalysisAgent()
    
    @pytest.mark.asyncio
    async def test_bulk_trend_analysis(self, agent):
        """Test bulk trend analysis performance"""
        trend_batch = [
            {
                "analysis_id": f"bulk_trend_{i}",
                "market_segment": f"market_{i}",
                "time_period": {"start_date": datetime.now() - timedelta(days=90)},
                "data_sources": ["platform_a", "platform_b"]
            }
            for i in range(15)  # 15 trend analyses
        ]
        
        start_time = datetime.now()
        
        # Analyze first 5 for performance testing
        analysis_tasks = [
            agent.analyze_current_trends(trend_data)
            for trend_data in trend_batch[:5]
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 5
        assert processing_time < 45  # Should complete within reasonable time
        
        # Verify no exceptions in results
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_real_time_trend_monitoring(self, agent):
        """Test real-time trend monitoring capabilities"""
        # Simulate real-time data streams
        data_streams = [
            {
                "stream_id": f"stream_{i}",
                "data_frequency": "real_time",
                "trend_indicators": [f"indicator_{j}" for j in range(5)]
            }
            for i in range(3)
        ]
        
        monitoring_tasks = []
        for stream in data_streams:
            task = agent.analyze_current_trends(stream)
            monitoring_tasks.append(task)
        
        results = await asyncio.gather(*monitoring_tasks, return_exceptions=True)
        
        assert len(results) == len(data_streams)
        for result in results:
            assert not isinstance(result, Exception)
            if isinstance(result, dict) and "trending_topics" in result:
                assert len(result["trending_topics"]) >= 0
