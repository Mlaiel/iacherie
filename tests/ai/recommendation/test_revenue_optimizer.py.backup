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

"""Comprehensive Tests for Revenue Optimization System
Testing revenue optimization, monetization strategies, and financial analytics

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de

Team Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal

from ai.recommendation.revenue_optimizer import (
    RevenueOptimizer, PricingStrategy
)
from ai.recommendation.models import (
    CreatorProfile, Platform, ContentType, RevenueStream,
    RevenueStrategy
)
from ai.recommendation.exceptions import RecommendationError, ValidationError


class TestRevenueOptimizer:
    """Comprehensive tests for the main revenue optimizer"""
    
    @pytest.mark.asyncio
    async def test_optimizer_initialization(self):
        """Test revenue optimizer initialization"""
        optimizer = RevenueOptimizer()
        
        # Test initial state
        assert optimizer.status.name == "INITIALIZING"
        
        # Test initialization
        success = await optimizer.initialize()
        assert success is True
        assert optimizer.status.name == "READY"
        
        # Test components are loaded
        assert optimizer.monetization_analyzer is not None
        assert optimizer.pricing_optimizer is not None
        assert optimizer.sponsorship_matcher is not None
        assert optimizer.ad_revenue_predictor is not None
    
    @pytest.mark.asyncio
    async def test_optimize_revenue_streams(self, revenue_optimizer, sample_creator_musician):
        """Test revenue stream optimization"""
        creator = sample_creator_musician
        
        optimization = await revenue_optimizer.optimize_revenue_streams(
            creator_profile=creator,
            target_revenue_increase=0.25,  # 25% increase
            optimization_horizon=timedelta(days=90)
        )
        
        assert 'current_revenue_analysis' in optimization
        assert 'optimization_strategies' in optimization
        assert 'projected_revenue_increase' in optimization
        assert 'implementation_timeline' in optimization
        assert 'risk_assessment' in optimization
        
        # Test optimization strategies
        strategies = optimization['optimization_strategies']
        assert len(strategies) > 0
        
        for strategy in strategies:
            assert 'strategy_type' in strategy
            assert 'revenue_potential' in strategy
            assert 'implementation_effort' in strategy
            assert 'success_probability' in strategy
            assert 'timeline' in strategy
    
    @pytest.mark.asyncio
    async def test_analyze_monetization_opportunities(self, revenue_optimizer, sample_creator_musician):
        """Test monetization opportunity analysis"""
        creator = sample_creator_musician
        
        opportunities = await revenue_optimizer.analyze_monetization_opportunities(
            creator_profile=creator,
            platforms=creator.platforms
        )
        
        assert len(opportunities) > 0
        
        for opportunity in opportunities:
            assert isinstance(opportunity, MonetizationStrategy)
            assert opportunity.strategy_name
            assert opportunity.platform in creator.platforms
            assert 0 <= opportunity.revenue_potential
            assert 0 <= opportunity.implementation_difficulty <= 1
            assert 0 <= opportunity.success_probability <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_content_pricing(self, revenue_optimizer, sample_creator_musician):
        """Test content pricing optimization"""
        creator = sample_creator_musician
        
        pricing_optimization = await revenue_optimizer.optimize_content_pricing(
            creator_profile=creator,
            content_types=[ContentType.AUDIO, ContentType.VIDEO],
            market_analysis_depth="comprehensive"
        )
        
        assert 'current_pricing_analysis' in pricing_optimization
        assert 'optimal_pricing_strategy' in pricing_optimization
        assert 'price_elasticity_analysis' in pricing_optimization
        assert 'competitor_analysis' in pricing_optimization
        assert 'revenue_projections' in pricing_optimization
        
        # Test pricing recommendations
        pricing_strategy = pricing_optimization['optimal_pricing_strategy']
        for content_type, pricing_data in pricing_strategy.items():
            assert 'recommended_price' in pricing_data
            assert 'price_range' in pricing_data
            assert 'pricing_rationale' in pricing_data
            assert pricing_data['recommended_price'] > 0
    
    @pytest.mark.asyncio
    async def test_predict_revenue_trends(self, revenue_optimizer, sample_creator_musician):
        """Test revenue trend prediction"""
        creator = sample_creator_musician
        
        revenue_predictions = await revenue_optimizer.predict_revenue_trends(
            creator_profile=creator,
            prediction_horizon=timedelta(days=180),
            scenario_analysis=True
        )
        
        assert 'baseline_prediction' in revenue_predictions
        assert 'optimistic_scenario' in revenue_predictions
        assert 'pessimistic_scenario' in revenue_predictions
        assert 'key_factors' in revenue_predictions
        assert 'confidence_intervals' in revenue_predictions
        
        # Test prediction validity
        baseline = revenue_predictions['baseline_prediction']
        optimistic = revenue_predictions['optimistic_scenario']
        pessimistic = revenue_predictions['pessimistic_scenario']
        
        # Logical ordering of scenarios
        assert pessimistic['total_revenue'] <= baseline['total_revenue'] <= optimistic['total_revenue']
    
    @pytest.mark.asyncio
    async def test_optimize_ad_revenue(self, revenue_optimizer, sample_creator_musician):
        """Test advertising revenue optimization"""
        creator = sample_creator_musician
        
        ad_optimization = await revenue_optimizer.optimize_ad_revenue(
            creator_profile=creator,
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            optimization_timeframe=timedelta(days=30)
        )
        
        assert 'current_ad_performance' in ad_optimization
        assert 'optimization_recommendations' in ad_optimization
        assert 'projected_revenue_increase' in ad_optimization
        assert 'optimal_ad_placement' in ad_optimization
        
        # Test ad optimization recommendations
        recommendations = ad_optimization['optimization_recommendations']
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert 'recommendation_type' in rec
            assert 'expected_impact' in rec
            assert 'implementation_steps' in rec
            assert rec['expected_impact'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_revenue_diversification(self, revenue_optimizer, sample_creator_musician):
        """Test revenue diversification analysis"""
        creator = sample_creator_musician
        
        diversification_analysis = await revenue_optimizer.analyze_revenue_diversification(
            creator_profile=creator,
            risk_tolerance=0.7,  # Medium-high risk tolerance
            investment_capacity=5000  # $5000 investment capacity
        )
        
        assert 'current_diversification_score' in diversification_analysis
        assert 'diversification_opportunities' in diversification_analysis
        assert 'risk_analysis' in diversification_analysis
        assert 'implementation_roadmap' in diversification_analysis
        
        # Test diversification score
        current_score = diversification_analysis['current_diversification_score']
        assert 0 <= current_score <= 1
        
        # Test diversification opportunities
        opportunities = diversification_analysis['diversification_opportunities']
        assert len(opportunities) > 0
        
        for opp in opportunities:
            assert 'opportunity_type' in opp
            assert 'revenue_potential' in opp
            assert 'risk_level' in opp
            assert 'investment_required' in opp


class TestMonetizationAnalyzer:
    """Tests for monetization analysis algorithms"""
    
    @pytest.mark.asyncio
    async def test_analyze_current_monetization(self, monetization_analyzer, sample_creator_musician):
        """Test current monetization analysis"""
        creator = sample_creator_musician
        
        analysis = await monetization_analyzer.analyze_current_monetization(creator)
        
        assert 'revenue_streams' in analysis
        assert 'revenue_breakdown' in analysis
        assert 'monetization_efficiency' in analysis
        assert 'growth_opportunities' in analysis
        
        # Test revenue streams analysis
        streams = analysis['revenue_streams']
        total_revenue = sum(stream['monthly_revenue'] for stream in streams)
        assert total_revenue > 0
        
        # Test monetization efficiency
        efficiency = analysis['monetization_efficiency']
        assert 0 <= efficiency <= 1
    
    @pytest.mark.asyncio
    async def test_identify_untapped_revenue_sources(self, monetization_analyzer, sample_creator_musician):
        """Test identification of untapped revenue sources"""
        creator = sample_creator_musician
        
        untapped_sources = await monetization_analyzer.identify_untapped_revenue_sources(
            creator_profile=creator,
            market_analysis=True
        )
        
        assert len(untapped_sources) > 0
        
        for source in untapped_sources:
            assert 'source_type' in source
            assert 'revenue_potential' in source
            assert 'market_size' in source
            assert 'competition_level' in source
            assert 'entry_barriers' in source
            
            # Test potential calculations
            assert source['revenue_potential'] > 0
            assert 0 <= source['competition_level'] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_monetization_trends(self, monetization_analyzer):
        """Test monetization trend analysis"""
        trends = await monetization_analyzer.analyze_monetization_trends(
            industry="Music Content Creation",
            time_period=timedelta(days=365),
            platforms=[Platform.YOUTUBE, Platform.SPOTIFY, Platform.INSTAGRAM]
        )
        
        assert 'trending_monetization_methods' in trends
        assert 'declining_methods' in trends
        assert 'emerging_opportunities' in trends
        assert 'platform_specific_trends' in trends
        
        # Test trending methods
        trending = trends['trending_monetization_methods']
        assert len(trending) > 0
        
        for method in trending:
            assert 'method_name' in method
            assert 'growth_rate' in method
            assert 'adoption_rate' in method
            assert 'success_factors' in method
    
    @pytest.mark.asyncio
    async def test_calculate_lifetime_value(self, monetization_analyzer, sample_creator_musician):
        """Test customer lifetime value calculation"""
        creator = sample_creator_musician
        
        ltv_analysis = await monetization_analyzer.calculate_lifetime_value(
            creator_profile=creator,
            customer_segments=["casual_listeners", "premium_subscribers", "super_fans"],
            prediction_period=timedelta(days=730)  # 2 years
        )
        
        assert len(ltv_analysis) == 3  # One for each segment
        
        for segment_ltv in ltv_analysis:
            assert 'segment' in segment_ltv
            assert 'lifetime_value' in segment_ltv
            assert 'retention_rate' in segment_ltv
            assert 'average_purchase_frequency' in segment_ltv
            assert 'churn_probability' in segment_ltv
            
            # Test LTV calculations
            assert segment_ltv['lifetime_value'] > 0
            assert 0 <= segment_ltv['retention_rate'] <= 1
            assert 0 <= segment_ltv['churn_probability'] <= 1


class TestPricingOptimizer:
    """Tests for pricing optimization algorithms"""
    
    @pytest.mark.asyncio
    async def test_optimize_subscription_pricing(self, pricing_optimizer, sample_creator_musician):
        """Test subscription pricing optimization"""
        creator = sample_creator_musician
        
        pricing_optimization = await pricing_optimizer.optimize_subscription_pricing(
            creator_profile=creator,
            service_tiers=["basic", "premium", "vip"],
            market_research_data=True
        )
        
        assert len(pricing_optimization) == 3  # One for each tier
        
        for tier_pricing in pricing_optimization:
            assert 'tier' in tier_pricing
            assert 'optimal_price' in tier_pricing
            assert 'price_elasticity' in tier_pricing
            assert 'demand_prediction' in tier_pricing
            assert 'revenue_projection' in tier_pricing
            
            # Test pricing logic
            assert tier_pricing['optimal_price'] > 0
            assert tier_pricing['price_elasticity'] < 0  # Should be negative
    
    @pytest.mark.asyncio
    async def test_analyze_price_sensitivity(self, pricing_optimizer, sample_creator_musician):
        """Test price sensitivity analysis"""
        creator = sample_creator_musician
        
        sensitivity_analysis = await pricing_optimizer.analyze_price_sensitivity(
            creator_profile=creator,
            content_type=ContentType.AUDIO,
            price_range=(5, 50),  # $5 to $50
            sample_size=1000
        )
        
        assert 'elasticity_curve' in sensitivity_analysis
        assert 'optimal_price_point' in sensitivity_analysis
        assert 'revenue_maximizing_price' in sensitivity_analysis
        assert 'market_penetration_price' in sensitivity_analysis
        
        # Test price points
        optimal = sensitivity_analysis['optimal_price_point']
        revenue_max = sensitivity_analysis['revenue_maximizing_price']
        penetration = sensitivity_analysis['market_penetration_price']
        
        assert 5 <= optimal <= 50
        assert 5 <= revenue_max <= 50
        assert 5 <= penetration <= 50
        assert penetration <= optimal <= revenue_max
    
    @pytest.mark.asyncio
    async def test_dynamic_pricing_strategy(self, pricing_optimizer, sample_creator_musician):
        """Test dynamic pricing strategy development"""
        creator = sample_creator_musician
        
        dynamic_strategy = await pricing_optimizer.develop_dynamic_pricing_strategy(
            creator_profile=creator,
            demand_factors=["time_of_day", "day_of_week", "seasonal", "event_driven"],
            adjustment_frequency="weekly"
        )
        
        assert 'base_pricing_model' in dynamic_strategy
        assert 'demand_multipliers' in dynamic_strategy
        assert 'adjustment_rules' in dynamic_strategy
        assert 'monitoring_metrics' in dynamic_strategy
        
        # Test demand multipliers
        multipliers = dynamic_strategy['demand_multipliers']
        for factor, multiplier_data in multipliers.items():
            assert factor in ["time_of_day", "day_of_week", "seasonal", "event_driven"]
            assert 'multiplier_range' in multiplier_data
            assert 'trigger_conditions' in multiplier_data
    
    @pytest.mark.asyncio
    async def test_competitor_pricing_analysis(self, pricing_optimizer, sample_creator_musician):
        """Test competitor pricing analysis"""
        creator = sample_creator_musician
        
        competitor_analysis = await pricing_optimizer.analyze_competitor_pricing(
            creator_profile=creator,
            competitor_types=["direct", "indirect", "substitute"],
            analysis_depth="comprehensive"
        )
        
        assert 'competitor_pricing_data' in competitor_analysis
        assert 'market_positioning' in competitor_analysis
        assert 'pricing_gaps' in competitor_analysis
        assert 'competitive_advantages' in competitor_analysis
        
        # Test competitor data
        pricing_data = competitor_analysis['competitor_pricing_data']
        assert len(pricing_data) > 0
        
        for competitor in pricing_data:
            assert 'competitor_type' in competitor
            assert 'pricing_strategy' in competitor
            assert 'price_points' in competitor
            assert 'market_share' in competitor


class TestSponsorshipMatcher:
    """Tests for sponsorship matching algorithms"""
    
    @pytest.mark.asyncio
    async def test_find_sponsorship_opportunities(self, sponsorship_matcher, sample_creator_musician):
        """Test finding sponsorship opportunities"""
        creator = sample_creator_musician
        
        opportunities = await sponsorship_matcher.find_sponsorship_opportunities(
            creator_profile=creator,
            min_deal_value=1000,  # Minimum $1000 deals
            max_results=10
        )
        
        assert len(opportunities) <= 10
        assert all(isinstance(opp, SponsorshipDeal) for opp in opportunities)
        
        for opportunity in opportunities:
            assert opportunity.deal_value >= 1000
            assert opportunity.brand_name
            assert opportunity.campaign_type
            assert 0 <= opportunity.brand_fit_score <= 1
            assert 0 <= opportunity.audience_match_score <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_brand_compatibility(self, sponsorship_matcher, sample_creator_musician):
        """Test brand compatibility calculation"""
        creator = sample_creator_musician
        
        # Mock brand data
        brand_data = {
            "brand_name": "TechFlow Audio",
            "industry": "Music Technology",
            "target_demographics": creator.target_demographics,
            "brand_values": ["innovation", "creativity", "quality"],
            "previous_sponsorships": ["music_producers", "audio_engineers"]
        }
        
        compatibility = await sponsorship_matcher.calculate_brand_compatibility(
            creator_profile=creator,
            brand_data=brand_data
        )
        
        assert 'overall_compatibility' in compatibility
        assert 'demographic_match' in compatibility
        assert 'brand_alignment' in compatibility
        assert 'audience_interest_overlap' in compatibility
        
        # Test compatibility scores
        assert 0 <= compatibility['overall_compatibility'] <= 1
        assert 0 <= compatibility['demographic_match'] <= 1
        assert 0 <= compatibility['brand_alignment'] <= 1
    
    @pytest.mark.asyncio
    async def test_estimate_sponsorship_value(self, sponsorship_matcher, sample_creator_musician):
        """Test sponsorship value estimation"""
        creator = sample_creator_musician
        
        value_estimation = await sponsorship_matcher.estimate_sponsorship_value(
            creator_profile=creator,
            sponsorship_type="product_placement",
            campaign_duration=timedelta(days=30),
            deliverables=["instagram_post", "youtube_video", "story_series"]
        )
        
        assert 'estimated_value' in value_estimation
        assert 'value_breakdown' in value_estimation
        assert 'pricing_factors' in value_estimation
        assert 'negotiation_range' in value_estimation
        
        # Test value estimation
        estimated_value = value_estimation['estimated_value']
        assert estimated_value > 0
        
        # Test value breakdown
        breakdown = value_estimation['value_breakdown']
        total_breakdown = sum(breakdown.values())
        assert abs(total_breakdown - estimated_value) < 0.01 * estimated_value  # Within 1%
    
    @pytest.mark.asyncio
    async def test_optimize_sponsorship_portfolio(self, sponsorship_matcher, sample_creator_musician):
        """Test sponsorship portfolio optimization"""
        creator = sample_creator_musician
        
        portfolio_optimization = await sponsorship_matcher.optimize_sponsorship_portfolio(
            creator_profile=creator,
            target_revenue=10000,  # $10,000 target
            max_sponsorships_per_month=4,
            brand_diversity_requirement=0.7
        )
        
        assert 'recommended_portfolio' in portfolio_optimization
        assert 'revenue_projection' in portfolio_optimization
        assert 'risk_analysis' in portfolio_optimization
        assert 'timeline' in portfolio_optimization
        
        # Test portfolio composition
        portfolio = portfolio_optimization['recommended_portfolio']
        assert len(portfolio) > 0
        
        # Test brand diversity
        brands = set(deal['brand_name'] for deal in portfolio)
        assert len(brands) / len(portfolio) >= 0.7  # 70% brand diversity


class TestAdRevenuePredictor:
    """Tests for advertising revenue prediction"""
    
    @pytest.mark.asyncio
    async def test_predict_ad_revenue(self, ad_revenue_predictor, sample_creator_musician):
        """Test ad revenue prediction"""
        creator = sample_creator_musician
        
        prediction = await ad_revenue_predictor.predict_ad_revenue(
            creator_profile=creator,
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            prediction_horizon=timedelta(days=90)
        )
        
        assert isinstance(prediction, AdRevenuePrediction)
        assert prediction.total_predicted_revenue > 0
        assert len(prediction.platform_breakdown) > 0
        assert prediction.prediction_confidence > 0
        
        # Test platform breakdown
        for platform_data in prediction.platform_breakdown:
            assert 'platform' in platform_data
            assert 'predicted_revenue' in platform_data
            assert 'cpm_estimate' in platform_data
            assert 'impressions_estimate' in platform_data
    
    @pytest.mark.asyncio
    async def test_optimize_ad_placement(self, ad_revenue_predictor, sample_creator_musician):
        """Test ad placement optimization"""
        creator = sample_creator_musician
        
        placement_optimization = await ad_revenue_predictor.optimize_ad_placement(
            creator_profile=creator,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE
        )
        
        assert 'optimal_ad_frequency' in placement_optimization
        assert 'best_placement_positions' in placement_optimization
        assert 'audience_tolerance_analysis' in placement_optimization
        assert 'revenue_impact_prediction' in placement_optimization
        
        # Test ad frequency
        frequency = placement_optimization['optimal_ad_frequency']
        assert frequency['ads_per_video'] > 0
        assert frequency['optimal_spacing'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_cpm_trends(self, ad_revenue_predictor):
        """Test CPM trend analysis"""
        cpm_analysis = await ad_revenue_predictor.analyze_cpm_trends(
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK],
            content_categories=["Music", "Entertainment", "Technology"],
            time_period=timedelta(days=365)
        )
        
        assert len(cpm_analysis) > 0
        
        for platform_analysis in cpm_analysis:
            assert 'platform' in platform_analysis
            assert 'average_cpm' in platform_analysis
            assert 'cpm_trend' in platform_analysis
            assert 'seasonal_variations' in platform_analysis
            
            # Test CPM values
            assert platform_analysis['average_cpm'] > 0
            assert platform_analysis['cpm_trend'] in ['rising', 'stable', 'declining']


class TestRevenueOptimizationPerformance:
    """Performance tests for revenue optimization"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_revenue_optimization_performance(self, benchmark, revenue_optimizer, sample_creator_musician):
        """Benchmark revenue optimization performance"""
        creator = sample_creator_musician
        
        async def optimize_revenue():
            return await revenue_optimizer.optimize_revenue_streams(
                creator_profile=creator,
                target_revenue_increase=0.20,
                optimization_horizon=timedelta(days=60)
            )
        
        result = await benchmark(optimize_revenue)
        assert 'optimization_strategies' in result
    
    @pytest.mark.asyncio
    async def test_batch_pricing_optimization(self, pricing_optimizer, sample_creator_musician, sample_creator_blogger):
        """Test batch pricing optimization performance"""
        creators = [sample_creator_musician, sample_creator_blogger]
        
        start_time = datetime.now()
        
        optimization_results = await pricing_optimizer.optimize_batch_pricing(
            creator_profiles=creators,
            content_types=[ContentType.AUDIO, ContentType.VIDEO, ContentType.TEXT]
        )
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        # Test results
        assert len(optimization_results) == len(creators)
        
        # Test performance
        assert optimization_time < 30.0  # Should complete within 30 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_sponsorship_matching(self, sponsorship_matcher, sample_creator_musician):
        """Test concurrent sponsorship matching"""
        creator = sample_creator_musician
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(3):
            task = sponsorship_matcher.find_sponsorship_opportunities(
                creator_profile=creator,
                min_deal_value=500,
                max_results=5
            )
            tasks.append(task)
        
        # Execute concurrently
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        concurrent_time = (datetime.now() - start_time).total_seconds()
        
        # Test all requests completed successfully
        assert len(results) == 3
        assert all(len(opportunities) > 0 for opportunities in results)
        
        # Test reasonable performance
        assert concurrent_time < 20.0  # Should handle concurrent requests efficiently


class TestRevenueOptimizationEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    @pytest.mark.asyncio
    async def test_optimization_for_low_revenue_creator(self, revenue_optimizer):
        """Test optimization for creators with very low revenue"""
        low_revenue_creator = CreatorProfile(
            creator_id="low_revenue_creator",
            display_name="Starting Creator",
            platforms=[Platform.YOUTUBE],
            followers_count={Platform.YOUTUBE: 500},  # Very small following
            monthly_revenue=50,  # Very low revenue
            content_types=[ContentType.VIDEO]
        )
        
        optimization = await revenue_optimizer.optimize_revenue_streams(
            creator_profile=low_revenue_creator,
            target_revenue_increase=2.0,  # 200% increase (realistic for low baseline)
            optimization_horizon=timedelta(days=120)
        )
        
        # Should still provide optimization strategies
        assert 'optimization_strategies' in optimization
        strategies = optimization['optimization_strategies']
        assert len(strategies) > 0
        
        # Should focus on foundational growth strategies
        strategy_types = [s['strategy_type'] for s in strategies]
        assert any('audience_growth' in st.lower() for st in strategy_types)
        assert any('content_quality' in st.lower() for st in strategy_types)
    
    @pytest.mark.asyncio
    async def test_optimization_with_zero_target_increase(self, revenue_optimizer, sample_creator_musician):
        """Test optimization with zero target increase"""
        creator = sample_creator_musician
        
        with pytest.raises(ValidationError):
            await revenue_optimizer.optimize_revenue_streams(
                creator_profile=creator,
                target_revenue_increase=0,  # Invalid target
                optimization_horizon=timedelta(days=60)
            )
    
    @pytest.mark.asyncio
    async def test_pricing_optimization_with_invalid_range(self, pricing_optimizer, sample_creator_musician):
        """Test pricing optimization with invalid price range"""
        creator = sample_creator_musician
        
        with pytest.raises(ValidationError):
            await pricing_optimizer.analyze_price_sensitivity(
                creator_profile=creator,
                content_type=ContentType.AUDIO,
                price_range=(50, 5),  # Invalid range (max < min)
                sample_size=1000
            )
    
    @pytest.mark.asyncio
    async def test_sponsorship_matching_with_no_budget(self, sponsorship_matcher, sample_creator_musician):
        """Test sponsorship matching with unrealistic budget requirements"""
        creator = sample_creator_musician
        
        # Try to find sponsorships with unrealistically high minimum value
        opportunities = await sponsorship_matcher.find_sponsorship_opportunities(
            creator_profile=creator,
            min_deal_value=1000000,  # $1M minimum (unrealistic)
            max_results=10
        )
        
        # Should return empty list or very few opportunities
        assert len(opportunities) <= 1
    
    @pytest.mark.asyncio
    async def test_revenue_prediction_timeout_handling(self, revenue_optimizer, sample_creator_musician):
        """Test revenue prediction timeout handling"""
        creator = sample_creator_musician
        
        try:
            # Set timeout to test timeout handling
            predictions = await asyncio.wait_for(
                revenue_optimizer.predict_revenue_trends(
                    creator_profile=creator,
                    prediction_horizon=timedelta(days=365),  # Long prediction
                    scenario_analysis=True
                ),
                timeout=45.0  # 45 second timeout
            )
            
            # Should complete within timeout
            assert 'baseline_prediction' in predictions
            
        except asyncio.TimeoutError:
            pytest.fail("Revenue prediction timed out")


class TestRevenueDataValidation:
    """Tests for revenue data validation and accuracy"""
    
    @pytest.mark.asyncio
    async def test_revenue_calculation_accuracy(self, monetization_analyzer, sample_creator_musician):
        """Test accuracy of revenue calculations"""
        creator = sample_creator_musician
        
        analysis = await monetization_analyzer.analyze_current_monetization(creator)
        
        # Test revenue breakdown sums correctly
        revenue_breakdown = analysis['revenue_breakdown']
        calculated_total = sum(revenue_breakdown.values())
        
        # Should match within reasonable precision
        expected_total = creator.monthly_revenue
        relative_error = abs(calculated_total - expected_total) / expected_total
        assert relative_error < 0.05  # Within 5% error
    
    @pytest.mark.asyncio
    async def test_pricing_model_consistency(self, pricing_optimizer, sample_creator_musician):
        """Test consistency of pricing models"""
        creator = sample_creator_musician
        
        # Get pricing optimization multiple times
        optimization_1 = await pricing_optimizer.optimize_subscription_pricing(
            creator_profile=creator,
            service_tiers=["basic", "premium"],
            market_research_data=True
        )
        
        optimization_2 = await pricing_optimizer.optimize_subscription_pricing(
            creator_profile=creator,
            service_tiers=["basic", "premium"],
            market_research_data=True
        )
        
        # Prices should be consistent within reasonable bounds
        basic_price_1 = optimization_1[0]['optimal_price']
        basic_price_2 = optimization_2[0]['optimal_price']
        
        price_variance = abs(basic_price_1 - basic_price_2) / basic_price_1
        assert price_variance < 0.1  # Within 10% variance
    
    @pytest.mark.asyncio
    async def test_sponsorship_value_logic(self, sponsorship_matcher, sample_creator_musician):
        """Test logical consistency of sponsorship value calculations"""
        creator = sample_creator_musician
        
        # Estimate values for different campaign durations
        short_campaign = await sponsorship_matcher.estimate_sponsorship_value(
            creator_profile=creator,
            sponsorship_type="product_placement",
            campaign_duration=timedelta(days=7),
            deliverables=["instagram_post"]
        )
        
        long_campaign = await sponsorship_matcher.estimate_sponsorship_value(
            creator_profile=creator,
            sponsorship_type="product_placement",
            campaign_duration=timedelta(days=30),
            deliverables=["instagram_post", "youtube_video", "story_series"]
        )
        
        # Longer campaign with more deliverables should be worth more
        assert long_campaign['estimated_value'] > short_campaign['estimated_value']
