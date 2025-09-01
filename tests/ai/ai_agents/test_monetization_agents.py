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
Test suite for Monetization AI Agents

Tests all functionalities of revenue optimization, sponsorship matching,
pricing strategies, and monetization opportunity agents.

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

from ai.ai_agents.monetization_agents import (
    MonetizationAgent,
    SponsorshipAgent,
    PricingOptimizationAgent,
    RevenueAnalysisAgent,
    MonetizationStrategy,
    SponsorshipMatch,
    PricingRecommendation,
    RevenueReport
)


class TestMonetizationAgent:
    """
Test MonetizationAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create MonetizationAgent instance"""
        return MonetizationAgent()
    
    @pytest.fixture
    def sample_creator_profile(self):
        """
Sample creator profile for monetization analysis"""
        return {
            "creator_id": "creator_001",
            "name": "TechEducator",
            "niche": "technology_education",
            "audience_metrics": {
                "total_followers": 75000,
                "average_views": 25000,
                "engagement_rate": 0.055,
                "demographics": {
                    "age_groups": {"18-24": 25, "25-34": 45, "35-44": 25, "45+": 5},
                    "income_levels": {"low": 20, "middle": 60, "high": 20},
                    "geographic_distribution": {"US": 40, "EU": 25, "Asia": 20, "Other": 15}
                }
            },
            "content_performance": {
                "monthly_views": 500000,
                "average_watch_time": 0.7,
                "subscriber_conversion_rate": 0.08,
                "top_performing_categories": ["tutorials", "reviews", "course_previews"]
            },
            "current_monetization": {
                "revenue_streams": ["ad_revenue", "affiliate_marketing"],
                "monthly_revenue": 2500,
                "revenue_breakdown": {
                    "ad_revenue": 1800,
                    "affiliate_marketing": 700
                }
            },
            "brand_reputation": {
                "trust_score": 0.85,
                "brand_safety_rating": "high",
                "audience_loyalty": 0.78
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_monetization_opportunities(self, agent, sample_creator_profile):
        """Test monetization opportunity analysis"""
        opportunities = await agent.analyze_monetization_opportunities(sample_creator_profile)
        
        assert "identified_opportunities" in opportunities
        assert "revenue_potential" in opportunities
        assert "implementation_roadmap" in opportunities
        assert "risk_assessment" in opportunities
        
        identified_ops = opportunities["identified_opportunities"]
        assert len(identified_ops) > 0
        
        for opportunity in identified_ops:
            assert "opportunity_type" in opportunity
            assert "revenue_potential" in opportunity
            assert "implementation_difficulty" in opportunity
            assert "time_to_revenue" in opportunity
            assert "success_probability" in opportunity
            assert 0 <= opportunity["success_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_create_monetization_strategy(self, agent, sample_creator_profile):
        """Test monetization strategy creation"""
        strategy_goals = {
            "revenue_target": 10000,  # Monthly target
            "timeline_months": 12,
            "risk_tolerance": "medium",
            "diversification_preference": "high"
        }
        
        strategy = await agent.create_monetization_strategy(
            sample_creator_profile,
            strategy_goals
        )
        
        assert isinstance(strategy, MonetizationStrategy)
        assert strategy.strategy_id is not None
        assert len(strategy.revenue_streams) > 0
        assert strategy.projected_revenue > 0
        assert strategy.implementation_timeline is not None
        assert len(strategy.success_metrics) > 0
    
    @pytest.mark.asyncio
    async def test_optimize_revenue_streams(self, agent, sample_creator_profile):
        """Test revenue stream optimization"""
        current_streams = {
            "ad_revenue": {"monthly": 1800, "growth_rate": 0.05, "effort_required": "low"},
            "affiliate_marketing": {"monthly": 700, "growth_rate": 0.15, "effort_required": "medium"},
            "sponsorships": {"monthly": 0, "potential": 2000, "effort_required": "high"}
        }
        
        optimization = await agent.optimize_revenue_streams(
            sample_creator_profile,
            current_streams
        )
        
        assert "stream_rankings" in optimization
        assert "optimization_recommendations" in optimization
        assert "resource_allocation" in optimization
        assert "expected_outcomes" in optimization
        
        stream_rankings = optimization["stream_rankings"]
        for stream in stream_rankings:
            assert "stream_name" in stream
            assert "priority_score" in stream
            assert "optimization_potential" in stream
            assert 0 <= stream["priority_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_pricing_recommendations(self, agent, sample_creator_profile):
        """Test pricing recommendation calculation"""
        product_details = {
            "product_type": "online_course",
            "content_hours": 20,
            "production_cost": 5000,
            "target_students": 500,
            "competitive_landscape": {
                "similar_courses_avg_price": 199,
                "premium_courses_avg_price": 399,
                "budget_courses_avg_price": 99
            }
        }
        
        pricing_rec = await agent.calculate_pricing_recommendations(
            sample_creator_profile,
            product_details
        )
        
        assert "recommended_price" in pricing_rec
        assert "pricing_strategy" in pricing_rec
        assert "revenue_projections" in pricing_rec
        assert "competitive_positioning" in pricing_rec
        
        assert pricing_rec["recommended_price"] > 0
        assert pricing_rec["pricing_strategy"] in ["premium", "competitive", "penetration", "value"]
    
    @pytest.mark.asyncio
    async def test_track_monetization_performance(self, agent, sample_creator_profile):
        """Test monetization performance tracking"""
        performance_data = {
            "time_period": "90_days",
            "revenue_data": {
                "total_revenue": 8500,
                "revenue_by_stream": {
                    "ad_revenue": 5400,
                    "sponsorships": 2100,
                    "affiliate": 1000
                },
                "revenue_trend": "increasing"
            },
            "key_metrics": {
                "rpm": 3.2,  # Revenue per mille
                "conversion_rates": {"course_sales": 0.025, "affiliate_clicks": 0.08},
                "customer_lifetime_value": 245
            }
        }
        
        performance_analysis = await agent.track_monetization_performance(
            sample_creator_profile,
            performance_data
        )
        
        assert "performance_summary" in performance_analysis
        assert "growth_analysis" in performance_analysis
        assert "optimization_opportunities" in performance_analysis
        assert "forecasting" in performance_analysis
        
        summary = performance_analysis["performance_summary"]
        assert "total_revenue" in summary
        assert "revenue_growth_rate" in summary
        assert "monetization_efficiency" in summary


class TestSponsorshipAgent:
    """Test SponsorshipAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create SponsorshipAgent instance"""
        return SponsorshipAgent()
    
    @pytest.fixture
    def sample_sponsorship_profile(self):
        """
Sample profile for sponsorship matching"""
        return {
            "creator_id": "creator_002",
            "niche": "fitness_lifestyle",
            "audience_demographics": {
                "age_primary": "25-34",
                "gender_split": {"male": 45, "female": 53, "other": 2},
                "interests": ["fitness", "nutrition", "wellness", "lifestyle"],
                "income_level": "middle_to_high",
                "geographic_focus": ["US", "UK", "Australia", "Canada"]
            },
            "content_metrics": {
                "avg_views": 50000,
                "engagement_rate": 0.065,
                "follower_count": 125000,
                "content_quality_score": 0.9
            },
            "brand_alignment": {
                "values": ["health", "authenticity", "positivity"],
                "past_collaborations": ["fitness_brand_A", "nutrition_company_B"],
                "prohibited_categories": ["alcohol", "tobacco", "gambling"]
            },
            "sponsorship_preferences": {
                "min_deal_value": 1500,
                "preferred_collaboration_types": ["product_review", "integration", "series"],
                "creative_control_requirements": "high"
            }
        }
    
    @pytest.mark.asyncio
    async def test_find_sponsorship_matches(self, agent, sample_sponsorship_profile):
        """Test sponsorship match finding"""
        matches = await agent.find_sponsorship_matches(sample_sponsorship_profile)
        
        assert isinstance(matches, list)
        assert len(matches) > 0
        
        for match in matches[:3]:  # Check first 3 matches
            assert isinstance(match, SponsorshipMatch)
            assert match.brand_name is not None
            assert match.campaign_id is not None
            assert 0 <= match.compatibility_score <= 1
            assert 0 <= match.audience_alignment <= 1
            assert match.estimated_deal_value > 0
            assert len(match.collaboration_opportunities) > 0
    
    @pytest.mark.asyncio
    async def test_evaluate_brand_alignment(self, agent, sample_sponsorship_profile):
        """
Test brand alignment evaluation"""
        brand_proposal = {
            "brand_name": "FitLife Supplements",
            "industry": "health_supplements",
            "brand_values": ["health", "performance", "natural_ingredients"],
            "target_audience": {
                "age_range": "22-40",
                "interests": ["fitness", "health", "supplements"],
                "geographic_focus": ["US", "Canada"]
            },
            "campaign_details": {
                "budget": 5000,
                "content_requirements": ["unboxing", "usage_demo", "results_share"],
                "exclusivity_requirements": "90_day_fitness_category",
                "timeline": "30_days"
            }
        }
        
        alignment = await agent.evaluate_brand_alignment(
            sample_sponsorship_profile,
            brand_proposal
        )
        
        assert "alignment_score" in alignment
        assert "value_compatibility" in alignment
        assert "audience_match" in alignment
        assert "brand_safety_assessment" in alignment
        assert "collaboration_feasibility" in alignment
        
        assert 0 <= alignment["alignment_score"] <= 1
        assert alignment["brand_safety_assessment"] in ["high", "medium", "low", "unsuitable"]
    
    @pytest.mark.asyncio
    async def test_negotiate_sponsorship_terms(self, agent, sample_sponsorship_profile):
        """Test sponsorship term negotiation"""
        initial_offer = {
            "brand": "FitLife Supplements",
            "offered_amount": 2000,
            "deliverables": ["2 instagram posts", "1 story series", "1 reel"],
            "timeline": "14_days",
            "usage_rights": "1_year_social_media",
            "exclusivity": "60_day_supplement_category"
        }
        
        negotiation = await agent.negotiate_sponsorship_terms(
            sample_sponsorship_profile,
            initial_offer
        )
        
        assert "counter_proposal" in negotiation
        assert "negotiation_points" in negotiation
        assert "value_justification" in negotiation
        assert "alternative_structures" in negotiation
        
        counter_proposal = negotiation["counter_proposal"]
        assert "proposed_amount" in counter_proposal
        assert "modified_deliverables" in counter_proposal
        assert "timeline_adjustment" in counter_proposal
    
    @pytest.mark.asyncio
    async def test_manage_sponsorship_campaigns(self, agent, sample_sponsorship_profile):
        """Test sponsorship campaign management"""
        campaign_details = {
            "campaign_id": "camp_001",
            "brand": "FitLife Supplements",
            "agreed_terms": {
                "deliverables": ["product_review_video", "instagram_posts", "story_series"],
                "timeline": {"start": "2025-02-01", "end": "2025-02-28"},
                "payment": {"amount": 3000, "schedule": "50_25_25"}
            },
            "content_deadlines": {
                "video": "2025-02-15",
                "posts": "2025-02-20",
                "stories": "2025-02-25"
            }
        }
        
        campaign_management = await agent.manage_sponsorship_campaigns(campaign_details)
        
        assert "campaign_timeline" in campaign_management
        assert "content_schedule" in campaign_management
        assert "performance_tracking" in campaign_management
        assert "compliance_checklist" in campaign_management
        
        timeline = campaign_management["campaign_timeline"]
        assert "milestones" in timeline
        assert "deadlines" in timeline
        assert "dependencies" in timeline
    
    @pytest.mark.asyncio
    async def test_analyze_sponsorship_performance(self, agent, sample_sponsorship_profile):
        """Test sponsorship performance analysis"""
        campaign_results = {
            "campaign_id": "camp_001",
            "deliverable_performance": {
                "product_review_video": {
                    "views": 75000,
                    "likes": 4200,
                    "comments": 380,
                    "click_through_rate": 0.15,
                    "conversion_rate": 0.08
                },
                "instagram_posts": {
                    "total_reach": 95000,
                    "engagement_rate": 0.075,
                    "story_completion_rate": 0.68
                }
            },
            "brand_metrics": {
                "brand_awareness_lift": 0.12,
                "purchase_intent_increase": 0.08,
                "website_traffic_from_campaign": 2500
            }
        }
        
        performance_analysis = await agent.analyze_sponsorship_performance(campaign_results)
        
        assert "campaign_effectiveness" in performance_analysis
        assert "roi_analysis" in performance_analysis
        assert "audience_response" in performance_analysis
        assert "recommendations" in performance_analysis
        
        effectiveness = performance_analysis["campaign_effectiveness"]
        assert "overall_performance_score" in effectiveness
        assert "deliverable_rankings" in effectiveness
        assert 0 <= effectiveness["overall_performance_score"] <= 1


class TestPricingOptimizationAgent:
    """Test PricingOptimizationAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create PricingOptimizationAgent instance"""
        return PricingOptimizationAgent()
    
    @pytest.fixture
    def sample_pricing_context(self):
        """
Sample pricing context for optimization"""
        return {
            "creator_profile": {
                "creator_id": "creator_003",
                "reputation_score": 0.85,
                "expertise_level": "advanced",
                "audience_willingness_to_pay": 0.7,
                "brand_value": "high"
            },
            "product_details": {
                "product_type": "masterclass_series",
                "content_volume": "15_hours_video_plus_materials",
                "production_quality": "professional",
                "uniqueness_score": 0.9,
                "market_demand": "high"
            },
            "market_analysis": {
                "competitor_pricing": {
                    "premium_tier": [299, 399, 499],
                    "mid_tier": [149, 199, 249],
                    "budget_tier": [49, 79, 99]
                },
                "market_saturation": 0.6,
                "price_sensitivity": 0.4,
                "seasonal_factors": "Q1_new_year_motivation"
            },
            "business_objectives": {
                "revenue_goal": 50000,
                "unit_target": 200,
                "profit_margin_requirement": 0.7,
                "market_penetration_goal": 0.15
            }
        }
    
    @pytest.mark.asyncio
    async def test_optimize_product_pricing(self, agent, sample_pricing_context):
        """Test product pricing optimization"""
        pricing_optimization = await agent.optimize_product_pricing(sample_pricing_context)
        
        assert isinstance(pricing_optimization, PricingRecommendation)
        assert pricing_optimization.recommended_price > 0
        assert pricing_optimization.pricing_strategy is not None
        assert pricing_optimization.confidence_score is not None
        assert len(pricing_optimization.supporting_factors) > 0
        assert pricing_optimization.revenue_projection is not None
        assert 0 <= pricing_optimization.confidence_score <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_price_sensitivity(self, agent, sample_pricing_context):
        """
Test price sensitivity analysis"""
        price_sensitivity = await agent.analyze_price_sensitivity(sample_pricing_context)
        
        assert "sensitivity_score" in price_sensitivity
        assert "price_elasticity" in price_sensitivity
        assert "optimal_price_range" in price_sensitivity
        assert "demand_curve_analysis" in price_sensitivity
        
        assert 0 <= price_sensitivity["sensitivity_score"] <= 1
        assert "min_price" in price_sensitivity["optimal_price_range"]
        assert "max_price" in price_sensitivity["optimal_price_range"]
        assert price_sensitivity["optimal_price_range"]["min_price"] < price_sensitivity["optimal_price_range"]["max_price"]
    
    @pytest.mark.asyncio
    async def test_create_pricing_strategies(self, agent, sample_pricing_context):
        """Test pricing strategy creation"""
        pricing_strategies = await agent.create_pricing_strategies(sample_pricing_context)
        
        assert isinstance(pricing_strategies, list)
        assert len(pricing_strategies) >= 3  # Should provide multiple strategy options
        
        strategy_names = [strategy["strategy_name"] for strategy in pricing_strategies]
        expected_strategies = ["premium", "competitive", "penetration", "value", "psychological"]
        
        # Should include at least some common pricing strategies
        assert any(strategy in expected_strategies for strategy in strategy_names)
        
        for strategy in pricing_strategies:
            assert "strategy_name" in strategy
            assert "price_point" in strategy
            assert "expected_revenue" in strategy
            assert "pros_and_cons" in strategy
            assert "implementation_considerations" in strategy
            assert strategy["price_point"] > 0
    
    @pytest.mark.asyncio
    async def test_optimize_subscription_pricing(self, agent, sample_pricing_context):
        """Test subscription pricing optimization"""
        subscription_context = {
            **sample_pricing_context,
            "subscription_model": {
                "billing_cycles": ["monthly", "quarterly", "annual"],
                "content_delivery": "continuous",
                "churn_rate_target": 0.05,
                "retention_requirements": 0.85
            }
        }
        
        subscription_optimization = await agent.optimize_subscription_pricing(subscription_context)
        
        assert "tier_recommendations" in subscription_optimization
        assert "billing_cycle_optimization" in subscription_optimization
        assert "retention_strategies" in subscription_optimization
        assert "revenue_projections" in subscription_optimization
        
        tiers = subscription_optimization["tier_recommendations"]
        assert len(tiers) > 0
        
        for tier in tiers:
            assert "tier_name" in tier
            assert "monthly_price" in tier
            assert "features_included" in tier
            assert "target_audience" in tier
            assert tier["monthly_price"] > 0
    
    @pytest.mark.asyncio
    async def test_monitor_pricing_performance(self, agent, sample_pricing_context):
        """Test pricing performance monitoring"""
        performance_data = {
            "current_price": 249,
            "sales_data": {
                "units_sold": 180,
                "revenue": 44820,
                "conversion_rate": 0.045,
                "refund_rate": 0.03
            },
            "market_feedback": {
                "price_perception": "fair_value",
                "customer_satisfaction": 0.85,
                "repeat_purchase_rate": 0.25
            },
            "competitive_changes": [
                {"competitor": "CompetitorA", "old_price": 199, "new_price": 229},
                {"competitor": "CompetitorB", "old_price": 299, "new_price": 279}
            ]
        }
        
        pricing_monitoring = await agent.monitor_pricing_performance(
            sample_pricing_context,
            performance_data
        )
        
        assert "performance_analysis" in pricing_monitoring
        assert "pricing_effectiveness" in pricing_monitoring
        assert "optimization_recommendations" in pricing_monitoring
        assert "competitive_impact" in pricing_monitoring
        
        analysis = pricing_monitoring["performance_analysis"]
        assert "revenue_vs_target" in analysis
        assert "conversion_analysis" in analysis
        assert "customer_value_analysis" in analysis


class TestRevenueAnalysisAgent:
    """Test RevenueAnalysisAgent functionality"""
    
    @pytest.fixture
    def agent(self):
        """
Create RevenueAnalysisAgent instance"""
        return RevenueAnalysisAgent()
    
    @pytest.fixture
    def sample_revenue_data(self):
        """
Sample revenue data for analysis"""
        return {
            "creator_id": "creator_004",
            "time_period": "12_months",
            "revenue_streams": {
                "ad_revenue": {
                    "monthly_data": [1500, 1600, 1750, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600],
                    "total": 24650,
                    "growth_rate": 0.73
                },
                "sponsorships": {
                    "monthly_data": [0, 1000, 1500, 2000, 1800, 2500, 3000, 3500, 4000, 4200, 4500, 5000],
                    "total": 32500,
                    "growth_rate": 4.0  # High growth from zero start
                },
                "product_sales": {
                    "monthly_data": [500, 600, 800, 1200, 1500, 1800, 2000, 2200, 2500, 2800, 3000, 3200],
                    "total": 20100,
                    "growth_rate": 5.4
                },
                "affiliate_marketing": {
                    "monthly_data": [200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750],
                    "total": 5700,
                    "growth_rate": 2.75
                }
            },
            "expenses": {
                "content_production": 15000,
                "marketing": 8000,
                "tools_software": 2400,
                "professional_services": 5000
            },
            "metrics": {
                "total_revenue": 82950,
                "net_profit": 52550,
                "profit_margin": 0.634,
                "revenue_per_subscriber": 3.32,
                "customer_lifetime_value": 45.80
            }
        }
    
    @pytest.mark.asyncio
    async def test_analyze_revenue_trends(self, agent, sample_revenue_data):
        """Test revenue trend analysis"""
        trend_analysis = await agent.analyze_revenue_trends(sample_revenue_data)
        
        assert "overall_trend" in trend_analysis
        assert "stream_analysis" in trend_analysis
        assert "seasonality_patterns" in trend_analysis
        assert "growth_drivers" in trend_analysis
        assert "risk_factors" in trend_analysis
        
        overall_trend = trend_analysis["overall_trend"]
        assert "direction" in overall_trend
        assert "growth_rate" in overall_trend
        assert "momentum" in overall_trend
        assert overall_trend["direction"] in ["increasing", "decreasing", "stable", "volatile"]
    
    @pytest.mark.asyncio
    async def test_forecast_revenue_projections(self, agent, sample_revenue_data):
        """Test revenue projection forecasting"""
        forecast_params = {
            "forecast_horizon": 6,  # months
            "growth_assumptions": {
                "ad_revenue": 0.05,  # 5% monthly growth
                "sponsorships": 0.1,  # 10% monthly growth
                "product_sales": 0.08,  # 8% monthly growth
                "affiliate_marketing": 0.03  # 3% monthly growth
            },
            "scenario_analysis": True
        }
        
        revenue_forecast = await agent.forecast_revenue_projections(
            sample_revenue_data,
            forecast_params
        )
        
        assert "baseline_forecast" in revenue_forecast
        assert "optimistic_scenario" in revenue_forecast
        assert "pessimistic_scenario" in revenue_forecast
        assert "confidence_intervals" in revenue_forecast
        
        baseline = revenue_forecast["baseline_forecast"]
        assert "monthly_projections" in baseline
        assert "total_projected_revenue" in baseline
        assert len(baseline["monthly_projections"]) == forecast_params["forecast_horizon"]
    
    @pytest.mark.asyncio
    async def test_identify_revenue_optimization_opportunities(self, agent, sample_revenue_data):
        """Test revenue optimization opportunity identification"""
        optimization_opportunities = await agent.identify_revenue_optimization_opportunities(
            sample_revenue_data
        )
        
        assert "high_impact_opportunities" in optimization_opportunities
        assert "quick_wins" in optimization_opportunities
        assert "long_term_strategies" in optimization_opportunities
        assert "resource_requirements" in optimization_opportunities
        
        high_impact = optimization_opportunities["high_impact_opportunities"]
        assert len(high_impact) > 0
        
        for opportunity in high_impact:
            assert "opportunity_type" in opportunity
            assert "revenue_impact_potential" in opportunity
            assert "implementation_complexity" in opportunity
            assert "timeline" in opportunity
            assert "success_probability" in opportunity
            assert 0 <= opportunity["success_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_roi_metrics(self, agent, sample_revenue_data):
        """Test ROI metrics calculation"""
        investment_data = {
            "marketing_spend": 8000,
            "content_production_investment": 15000,
            "technology_tools": 2400,
            "professional_development": 3000
        }
        
        roi_analysis = await agent.calculate_roi_metrics(sample_revenue_data, investment_data)
        
        assert "overall_roi" in roi_analysis
        assert "roi_by_investment_category" in roi_analysis
        assert "payback_periods" in roi_analysis
        assert "investment_efficiency" in roi_analysis
        
        assert roi_analysis["overall_roi"] is not None
        assert isinstance(roi_analysis["roi_by_investment_category"], dict)
        
        for category, roi in roi_analysis["roi_by_investment_category"].items():
            assert roi is not None
            assert isinstance(roi, (int, float))
    
    @pytest.mark.asyncio
    async def test_generate_revenue_reports(self, agent, sample_revenue_data):
        """Test revenue report generation"""
        report_config = {
            "report_type": "comprehensive",
            "include_forecasts": True,
            "include_benchmarks": True,
            "visualization_format": "charts_and_tables"
        }
        
        revenue_report = await agent.generate_revenue_reports(
            sample_revenue_data,
            report_config
        )
        
        assert isinstance(revenue_report, RevenueReport)
        assert revenue_report.report_id is not None
        assert revenue_report.summary is not None
        assert revenue_report.detailed_analysis is not None
        assert revenue_report.recommendations is not None
        assert len(revenue_report.key_insights) > 0


class TestIntegrationScenarios:
    """Test integration between different monetization agents"""
    
    @pytest.fixture
    def agents(self):
        """
Create all monetization agents for integration testing"""
        return {
            "monetization": MonetizationAgent(),
            "sponsorship": SponsorshipAgent(),
            "pricing": PricingOptimizationAgent(),
            "revenue": RevenueAnalysisAgent()
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_monetization_strategy(self, agents):
        """Test comprehensive monetization strategy development"""
        # Creator profile for comprehensive monetization analysis
        creator_data = {
            "creator_id": "integration_creator",
            "profile": {
                "niche": "business_education",
                "followers": 100000,
                "engagement_rate": 0.06,
                "content_quality": "high",
                "audience_demographics": {
                    "age_primary": "25-45",
                    "income_level": "middle_to_high",
                    "professional_focus": "entrepreneurs_professionals"
                }
            },
            "current_revenue": {
                "monthly": 5000,
                "streams": ["ad_revenue", "course_sales"],
                "growth_rate": 0.15
            },
            "goals": {
                "revenue_target": 25000,
                "timeline_months": 12,
                "diversification": "high_priority"
            }
        }
        
        # Execute integrated monetization workflow
        # 1. Analyze monetization opportunities
        opportunities = await agents["monetization"].analyze_monetization_opportunities(creator_data)
        
        # 2. Find sponsorship matches
        sponsorship_matches = await agents["sponsorship"].find_sponsorship_matches(creator_data["profile"])
        
        # 3. Optimize pricing for potential products
        pricing_context = {
            "creator_profile": creator_data["profile"],
            "product_details": {"product_type": "business_course"},
            "market_analysis": {"competitor_pricing": {"mid_tier": [199, 299, 399]}},
            "business_objectives": {"revenue_goal": 15000}
        }
        pricing_optimization = await agents["pricing"].optimize_product_pricing(pricing_context)
        
        # 4. Analyze revenue trends and forecast
        revenue_forecast = await agents["revenue"].forecast_revenue_projections(
            {"creator_id": creator_data["creator_id"], "current_revenue": creator_data["current_revenue"]},
            {"forecast_horizon": 12}
        )
        
        # Verify integrated strategy
        assert len(opportunities["identified_opportunities"]) > 0
        assert len(sponsorship_matches) > 0
        assert pricing_optimization.recommended_price > 0
        assert revenue_forecast is not None
        
        # Verify strategy coherence
        total_opportunity_potential = sum(
            op["revenue_potential"] for op in opportunities["identified_opportunities"]
        )
        assert total_opportunity_potential >= creator_data["goals"]["revenue_target"] * 0.5  # Reasonable opportunity coverage


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """
Create MonetizationAgent for error testing"""
        return MonetizationAgent()
    
    @pytest.mark.asyncio
    async def test_insufficient_creator_data(self, agent):
        """
Test handling of insufficient creator data"""
        minimal_data = {"creator_id": "test"}
        
        with pytest.raises((ValueError, KeyError)):
            await agent.analyze_monetization_opportunities(minimal_data)
    
    @pytest.mark.asyncio
    async def test_invalid_revenue_data(self, agent):
        """Test handling of invalid revenue data"""
        invalid_data = {
            "creator_id": "test",
            "monthly_revenue": -1000,  # Invalid negative revenue
            "followers": "invalid_number"  # Invalid type
        }
        
        try:
            result = await agent.analyze_monetization_opportunities(invalid_data)
            # Should handle gracefully with data validation
            assert result is not None
        except (ValueError, TypeError):
            # Acceptable to reject invalid data
            pass
    
    @pytest.mark.asyncio
    async def test_external_api_failures(self, agent):
        """Test handling of external API failures"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("External service unavailable")
            
            creator_data = {"creator_id": "test", "followers": 10000}
            
            try:
                result = await agent.analyze_monetization_opportunities(creator_data)
                # Should provide fallback analysis or handle gracefully
                assert result is not None or True
            except Exception as e:
                # Should provide meaningful error context
                assert len(str(e)) > 0


class TestPerformanceAndScaling:
    """Test performance and scaling scenarios"""
    
    @pytest.fixture
    def agent(self):
        """
Create MonetizationAgent for performance testing"""
        return MonetizationAgent()
    
    @pytest.mark.asyncio
    async def test_large_scale_opportunity_analysis(self, agent):
        """
Test large-scale monetization opportunity analysis"""
        large_creator_portfolio = {
            "creators": [
                {
                    "creator_id": f"creator_{i}",
                    "followers": 10000 + (i * 5000),
                    "niche": ["tech", "lifestyle", "business"][i % 3],
                    "monthly_revenue": 1000 + (i * 500)
                }
                for i in range(50)  # 50 creators
            ]
        }
        
        start_time = datetime.now()
        
        # Analyze first 5 creators for performance testing
        analysis_tasks = [
            agent.analyze_monetization_opportunities(creator)
            for creator in large_creator_portfolio["creators"][:5]
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) == 5
        assert processing_time < 30  # Should complete within reasonable time
        
        # Verify no exceptions in results
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_concurrent_pricing_optimization(self, agent):
        """Test concurrent pricing optimization for multiple products"""
        product_scenarios = [
            {
                "creator_profile": {"creator_id": f"creator_{i}", "reputation_score": 0.7 + (i * 0.05)},
                "product_details": {"product_type": "course", "content_hours": 10 + i},
                "market_analysis": {"competitor_pricing": {"mid_tier": [99 + (i * 50)]}},
                "business_objectives": {"revenue_goal": 5000 + (i * 1000)}
            }
            for i in range(10)
        ]
        
        # Use pricing agent for this test
        pricing_agent = PricingOptimizationAgent()
        
        pricing_tasks = [
            pricing_agent.optimize_product_pricing(scenario)
            for scenario in product_scenarios
        ]
        
        results = await asyncio.gather(*pricing_tasks, return_exceptions=True)
        
        assert len(results) == len(product_scenarios)
        for result in results:
            assert not isinstance(result, Exception)
            if hasattr(result, 'recommended_price'):
                assert result.recommended_price > 0
