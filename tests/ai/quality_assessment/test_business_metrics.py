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
Business Metrics Analysis Tests

Comprehensive test suite for professional business metrics analysis with advanced ROI calculation,
revenue optimization, audience analytics, and strategic business intelligence validation.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Project Team Specialties:
✅ Lead Dev + AI Developer Architect - Fahed Mlaiel
✅ Senior Backend Developer (Python/FastAPI/Django) - Fahed Mlaiel  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face) - Fahed Mlaiel
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB) - Fahed Mlaiel
✅ Backend Security Specialist - Fahed Mlaiel
✅ Microservices Architect - Fahed Mlaiel
✅ Audio Developer - Fahed Mlaiel
✅ DevOps Engineer - Fahed Mlaiel
✅ AI Prompt Engineer - Fahed Mlaiel

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

ANYONE WHO THINKS OF STEALING THE IDEA, CONCEPT, OR CODE WITHOUT MY PERSONAL, CLEAR, 
AND WRITTEN AUTHORIZATION WILL FACE SEVERE LEGAL CONSEQUENCES.

Contact: Fahed Mlaiel - mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest import TestCase
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ai.quality_assessment.business_metrics import (
    BusinessMetricsAnalyzer,
    BusinessMetricsAnalysis,
    BusinessMetricsProfile,
    AudienceMetrics,
    ContentPerformanceMetrics,
    BusinessGrowthMetrics,
    MonetizationMetrics,
    RevenueStream
)


class TestBusinessMetricsAnalyzer(TestCase):
    """Comprehensive test suite for BusinessMetricsAnalyzer with professional business intelligence."""
    
    def setUp(self):
        """Set up test fixtures with comprehensive business data."""
        self.analyzer = BusinessMetricsAnalyzer()
        
        # Sample business data for different creator types
        self.influencer_data = {
            'follower_count': 125000,
            'engagement_rate': 4.2,
            'monthly_revenue': 8500.0,
            'content_frequency': 5.5,  # posts per week
            'platform_distribution': {
                'instagram': 0.45,
                'youtube': 0.30,
                'tiktok': 0.20,
                'twitter': 0.05
            },
            'revenue_streams': {
                'sponsorships': 5500.0,
                'affiliate_marketing': 2000.0,
                'product_sales': 800.0,
                'subscriptions': 200.0
            },
            'demographics': {
                'age_18_24': 0.25,
                'age_25_34': 0.40,
                'age_35_44': 0.20,
                'age_45_plus': 0.15,
                'gender_female': 0.65,
                'gender_male': 0.35
            },
            'geographic_reach': {
                'north_america': 0.45,
                'europe': 0.30,
                'asia': 0.20,
                'other': 0.05
            }
        }
        
        self.musician_data = {
            'follower_count': 75000,
            'engagement_rate': 6.8,
            'monthly_revenue': 12000.0,
            'content_frequency': 3.2,
            'platform_distribution': {
                'spotify': 0.35,
                'youtube': 0.25,
                'instagram': 0.25,
                'tiktok': 0.15
            },
            'revenue_streams': {
                'streaming': 4500.0,
                'live_performances': 6000.0,
                'merchandise': 1200.0,
                'licensing': 300.0
            },
            'demographics': {
                'age_18_24': 0.35,
                'age_25_34': 0.30,
                'age_35_44': 0.25,
                'age_45_plus': 0.10,
                'gender_female': 0.55,
                'gender_male': 0.45
            }
        }
        
        self.business_account_data = {
            'follower_count': 250000,
            'engagement_rate': 2.8,
            'monthly_revenue': 45000.0,
            'content_frequency': 4.0,
            'platform_distribution': {
                'linkedin': 0.40,
                'instagram': 0.30,
                'youtube': 0.20,
                'twitter': 0.10
            },
            'revenue_streams': {
                'consulting': 25000.0,
                'courses': 15000.0,
                'speaking': 3000.0,
                'books': 2000.0
            },
            'demographics': {
                'age_25_34': 0.35,
                'age_35_44': 0.40,
                'age_45_plus': 0.25,
                'gender_female': 0.45,
                'gender_male': 0.55
            }
        }
        
        # Historical performance data
        self.historical_data = {
            'monthly_metrics': [
                {'month': '2024-01', 'followers': 115000, 'revenue': 7200, 'engagement': 4.1},
                {'month': '2024-02', 'followers': 118000, 'revenue': 7800, 'engagement': 4.0},
                {'month': '2024-03', 'followers': 121000, 'revenue': 8100, 'engagement': 4.3},
                {'month': '2024-04', 'followers': 123000, 'revenue': 8300, 'engagement': 4.2},
                {'month': '2024-05', 'followers': 125000, 'revenue': 8500, 'engagement': 4.2}
            ]
        }
        
        # Industry benchmarks
        self.industry_benchmarks = {
            'lifestyle_influencer': {
                'avg_engagement_rate': 3.5,
                'avg_revenue_per_follower': 0.08,
                'avg_growth_rate': 0.15
            },
            'musician': {
                'avg_engagement_rate': 5.2,
                'avg_revenue_per_follower': 0.12,
                'avg_growth_rate': 0.20
            },
            'business_expert': {
                'avg_engagement_rate': 2.1,
                'avg_revenue_per_follower': 0.18,
                'avg_growth_rate': 0.12
            }
        }
    
    @pytest.mark.asyncio
    async def test_comprehensive_business_analysis(self):
        """Test comprehensive business metrics analysis."""
        analysis_result = await self.analyzer.analyze_business_metrics(
            self.influencer_data,
            industry='lifestyle',
            analysis_period='monthly'
        )
        
        # Validate result structure
        self.assertIsInstance(analysis_result, dict)
        self.assertIn('revenue_analysis', analysis_result)
        self.assertIn('roi_calculation', analysis_result)
        self.assertIn('audience_metrics', analysis_result)
        self.assertIn('engagement_analysis', analysis_result)
        self.assertIn('growth_metrics', analysis_result)
        self.assertIn('monetization_analysis', analysis_result)
        self.assertIn('competitive_position', analysis_result)
        self.assertIn('strategic_recommendations', analysis_result)
        
        # Validate revenue analysis
        revenue_analysis = analysis_result['revenue_analysis']
        self.assertIn('total_revenue', revenue_analysis)
        self.assertIn('revenue_streams_breakdown', revenue_analysis)
        self.assertIn('revenue_per_follower', revenue_analysis)
        self.assertIn('growth_projection', revenue_analysis)
        
        # Validate audience metrics
        audience_metrics = analysis_result['audience_metrics']
        self.assertIn('audience_quality_score', audience_metrics)
        self.assertIn('demographic_analysis', audience_metrics)
        self.assertIn('geographic_distribution', audience_metrics)
        self.assertIn('audience_value', audience_metrics)
    
    @pytest.mark.asyncio
    async def test_revenue_analysis_detailed(self):
        """Test detailed revenue analysis functionality."""
        revenue_result = await self.analyzer.analyze_revenue(
            self.influencer_data,
            historical_data=self.historical_data
        )
        
        # Validate revenue analysis structure
        self.assertIsInstance(revenue_result, RevenueAnalysis)
        self.assertIsNotNone(revenue_result.total_monthly_revenue)
        self.assertIsNotNone(revenue_result.revenue_streams)
        self.assertIsNotNone(revenue_result.revenue_per_follower)
        self.assertIsNotNone(revenue_result.revenue_growth_rate)
        self.assertIsNotNone(revenue_result.revenue_diversification)
        
        # Validate revenue calculations
        expected_total = sum(self.influencer_data['revenue_streams'].values())
        self.assertAlmostEqual(revenue_result.total_monthly_revenue, expected_total, places=2)
        
        # Validate revenue per follower
        expected_rpf = expected_total / self.influencer_data['follower_count']
        self.assertAlmostEqual(revenue_result.revenue_per_follower, expected_rpf, places=4)
        
        # Validate revenue streams breakdown
        revenue_streams = revenue_result.revenue_streams
        self.assertEqual(len(revenue_streams), len(self.influencer_data['revenue_streams']))
        
        for stream_name, amount in self.influencer_data['revenue_streams'].items():
            self.assertIn(stream_name, revenue_streams)
            self.assertEqual(revenue_streams[stream_name]['amount'], amount)
            self.assertIn('percentage', revenue_streams[stream_name])
            self.assertIn('growth_potential', revenue_streams[stream_name])
        
        # Validate diversification score
        diversification = revenue_result.revenue_diversification
        self.assertIn('diversification_score', diversification)
        self.assertIn('risk_assessment', diversification)
        self.assertIn('concentration_risk', diversification)
        
        self.assertGreaterEqual(diversification['diversification_score'], 0.0)
        self.assertLessEqual(diversification['diversification_score'], 100.0)
    
    @pytest.mark.asyncio
    async def test_roi_calculation_comprehensive(self):
        """Test comprehensive ROI calculation analysis."""
        # Define investment data
        investment_data = {
            'content_creation_costs': 2500.0,
            'equipment_depreciation': 800.0,
            'marketing_spend': 1200.0,
            'platform_fees': 450.0,
            'time_investment_hours': 120,
            'hourly_rate': 75.0
        }
        
        roi_result = await self.analyzer.calculate_roi(
            self.influencer_data,
            investment_data
        )
        
        # Validate ROI calculation structure
        self.assertIsInstance(roi_result, ROICalculation)
        self.assertIsNotNone(roi_result.total_investment)
        self.assertIsNotNone(roi_result.total_return)
        self.assertIsNotNone(roi_result.roi_percentage)
        self.assertIsNotNone(roi_result.payback_period)
        self.assertIsNotNone(roi_result.profitability_analysis)
        
        # Validate investment calculation
        expected_direct_costs = (
            investment_data['content_creation_costs'] +
            investment_data['equipment_depreciation'] +
            investment_data['marketing_spend'] +
            investment_data['platform_fees']
        )
        expected_time_costs = investment_data['time_investment_hours'] * investment_data['hourly_rate']
        expected_total_investment = expected_direct_costs + expected_time_costs
        
        self.assertAlmostEqual(roi_result.total_investment, expected_total_investment, places=2)
        
        # Validate ROI percentage calculation
        expected_roi = ((roi_result.total_return - roi_result.total_investment) / roi_result.total_investment) * 100
        self.assertAlmostEqual(roi_result.roi_percentage, expected_roi, places=2)
        
        # Validate profitability analysis
        profitability = roi_result.profitability_analysis
        self.assertIn('profit_margin', profitability)
        self.assertIn('break_even_analysis', profitability)
        self.assertIn('efficiency_metrics', profitability)
        
        # ROI should be positive for successful creators
        self.assertGreater(roi_result.roi_percentage, 0.0)
    
    @pytest.mark.asyncio
    async def test_audience_metrics_analysis(self):
        """Test comprehensive audience metrics analysis."""
        audience_result = await self.analyzer.analyze_audience_metrics(self.influencer_data)
        
        # Validate audience metrics structure
        self.assertIsInstance(audience_result, AudienceMetrics)
        self.assertIsNotNone(audience_result.audience_quality_score)
        self.assertIsNotNone(audience_result.demographic_breakdown)
        self.assertIsNotNone(audience_result.geographic_analysis)
        self.assertIsNotNone(audience_result.audience_value_score)
        self.assertIsNotNone(audience_result.growth_potential)
        
        # Validate audience quality score
        self.assertGreaterEqual(audience_result.audience_quality_score, 0.0)
        self.assertLessEqual(audience_result.audience_quality_score, 100.0)
        
        # Validate demographic breakdown
        demographics = audience_result.demographic_breakdown
        self.assertIn('age_distribution', demographics)
        self.assertIn('gender_distribution', demographics)
        self.assertIn('engagement_by_demographic', demographics)
        
        # Age distribution should sum to 1.0
        age_dist = demographics['age_distribution']
        age_total = sum(age_dist.values())
        self.assertAlmostEqual(age_total, 1.0, places=2)
        
        # Gender distribution should sum to 1.0
        gender_dist = demographics['gender_distribution']
        gender_total = sum(gender_dist.values())
        self.assertAlmostEqual(gender_total, 1.0, places=2)
        
        # Validate geographic analysis
        geographic = audience_result.geographic_analysis
        self.assertIn('regional_distribution', geographic)
        self.assertIn('market_penetration', geographic)
        self.assertIn('expansion_opportunities', geographic)
        
        # Validate audience value score
        self.assertGreaterEqual(audience_result.audience_value_score, 0.0)
        self.assertLessEqual(audience_result.audience_value_score, 100.0)
    
    @pytest.mark.asyncio
    async def test_engagement_analysis_detailed(self):
        """Test detailed engagement analysis functionality."""
        engagement_result = await self.analyzer.analyze_engagement(
            self.influencer_data,
            platform_specific=True
        )
        
        # Validate engagement analysis structure
        self.assertIsInstance(engagement_result, EngagementAnalysis)
        self.assertIsNotNone(engagement_result.overall_engagement_rate)
        self.assertIsNotNone(engagement_result.platform_engagement)
        self.assertIsNotNone(engagement_result.engagement_quality)
        self.assertIsNotNone(engagement_result.audience_sentiment)
        self.assertIsNotNone(engagement_result.viral_potential)
        
        # Validate overall engagement rate
        expected_engagement = self.influencer_data['engagement_rate']
        self.assertEqual(engagement_result.overall_engagement_rate, expected_engagement)
        
        # Validate platform-specific engagement
        platform_engagement = engagement_result.platform_engagement
        for platform in self.influencer_data['platform_distribution'].keys():
            self.assertIn(platform, platform_engagement)
            platform_data = platform_engagement[platform]
            self.assertIn('engagement_rate', platform_data)
            self.assertIn('audience_share', platform_data)
            self.assertIn('performance_score', platform_data)
        
        # Validate engagement quality metrics
        quality = engagement_result.engagement_quality
        self.assertIn('genuine_engagement_percentage', quality)
        self.assertIn('engagement_depth', quality)
        self.assertIn('audience_loyalty_score', quality)
        
        # Validate viral potential analysis
        viral = engagement_result.viral_potential
        self.assertIn('virality_score', viral)
        self.assertIn('trending_probability', viral)
        self.assertIn('amplification_factors', viral)
        
        self.assertGreaterEqual(viral['virality_score'], 0.0)
        self.assertLessEqual(viral['virality_score'], 100.0)
    
    @pytest.mark.asyncio
    async def test_growth_metrics_analysis(self):
        """Test growth metrics analysis functionality."""
        growth_result = await self.analyzer.analyze_growth_metrics(
            self.influencer_data,
            historical_data=self.historical_data
        )
        
        # Validate growth metrics structure
        self.assertIsInstance(growth_result, GrowthMetrics)
        self.assertIsNotNone(growth_result.follower_growth_rate)
        self.assertIsNotNone(growth_result.revenue_growth_rate)
        self.assertIsNotNone(growth_result.engagement_growth_rate)
        self.assertIsNotNone(growth_result.growth_sustainability)
        self.assertIsNotNone(growth_result.growth_projections)
        
        # Validate growth rate calculations
        self.assertIsInstance(growth_result.follower_growth_rate, float)
        self.assertIsInstance(growth_result.revenue_growth_rate, float)
        self.assertIsInstance(growth_result.engagement_growth_rate, float)
        
        # Growth rates should be reasonable (not infinity or NaN)
        self.assertFalse(float('inf') in [
            growth_result.follower_growth_rate,
            growth_result.revenue_growth_rate,
            growth_result.engagement_growth_rate
        ])
        
        # Validate growth sustainability analysis
        sustainability = growth_result.growth_sustainability
        self.assertIn('sustainability_score', sustainability)
        self.assertIn('growth_efficiency', sustainability)
        self.assertIn('scalability_assessment', sustainability)
        
        # Validate growth projections
        projections = growth_result.growth_projections
        self.assertIn('3_month_projection', projections)
        self.assertIn('6_month_projection', projections)
        self.assertIn('12_month_projection', projections)
        
        for projection in projections.values():
            self.assertIn('followers', projection)
            self.assertIn('revenue', projection)
            self.assertIn('confidence_interval', projection)
    
    @pytest.mark.asyncio
    async def test_monetization_analysis(self):
        """Test monetization analysis functionality."""
        monetization_result = await self.analyzer.analyze_monetization(
            self.influencer_data,
            industry_benchmarks=self.industry_benchmarks['lifestyle_influencer']
        )
        
        # Validate monetization analysis structure
        self.assertIsInstance(monetization_result, MonetizationAnalysis)
        self.assertIsNotNone(monetization_result.monetization_efficiency)
        self.assertIsNotNone(monetization_result.revenue_optimization)
        self.assertIsNotNone(monetization_result.untapped_potential)
        self.assertIsNotNone(monetization_result.strategy_recommendations)
        
        # Validate monetization efficiency
        efficiency = monetization_result.monetization_efficiency
        self.assertIn('efficiency_score', efficiency)
        self.assertIn('revenue_per_follower_vs_benchmark', efficiency)
        self.assertIn('monetization_rate', efficiency)
        
        self.assertGreaterEqual(efficiency['efficiency_score'], 0.0)
        self.assertLessEqual(efficiency['efficiency_score'], 100.0)
        
        # Validate revenue optimization opportunities
        optimization = monetization_result.revenue_optimization
        self.assertIn('current_optimization_level', optimization)
        self.assertIn('improvement_opportunities', optimization)
        self.assertIn('quick_wins', optimization)
        
        # Validate untapped potential analysis
        potential = monetization_result.untapped_potential
        self.assertIn('potential_revenue_increase', potential)
        self.assertIn('new_revenue_streams', potential)
        self.assertIn('audience_monetization_readiness', potential)
        
        # Validate strategy recommendations
        strategies = monetization_result.strategy_recommendations
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)
        
        for strategy in strategies:
            self.assertIn('strategy_type', strategy)
            self.assertIn('expected_impact', strategy)
            self.assertIn('implementation_difficulty', strategy)
            self.assertIn('timeline', strategy)
    
    @pytest.mark.asyncio
    async def test_competitive_position_analysis(self):
        """Test competitive position analysis functionality."""
        competitive_result = await self.analyzer.analyze_competitive_position(
            self.influencer_data,
            industry='lifestyle',
            competitor_data=[
                {'follower_count': 100000, 'engagement_rate': 3.8, 'revenue': 7000},
                {'follower_count': 150000, 'engagement_rate': 3.2, 'revenue': 9500},
                {'follower_count': 90000, 'engagement_rate': 4.5, 'revenue': 6800}
            ]
        )
        
        # Validate competitive position structure
        self.assertIsInstance(competitive_result, CompetitivePosition)
        self.assertIsNotNone(competitive_result.market_position)
        self.assertIsNotNone(competitive_result.competitive_advantages)
        self.assertIsNotNone(competitive_result.areas_for_improvement)
        self.assertIsNotNone(competitive_result.market_opportunities)
        
        # Validate market position
        position = competitive_result.market_position
        self.assertIn('percentile_ranking', position)
        self.assertIn('market_share_estimate', position)
        self.assertIn('position_classification', position)
        
        # Percentile ranking should be between 0 and 100
        self.assertGreaterEqual(position['percentile_ranking'], 0.0)
        self.assertLessEqual(position['percentile_ranking'], 100.0)
        
        # Position classification should be valid
        valid_classifications = ['market_leader', 'strong_performer', 'average_performer', 'underperformer']
        self.assertIn(position['position_classification'], valid_classifications)
        
        # Validate competitive advantages
        advantages = competitive_result.competitive_advantages
        self.assertIsInstance(advantages, list)
        
        # Validate areas for improvement
        improvements = competitive_result.areas_for_improvement
        self.assertIsInstance(improvements, list)
        
        # Validate market opportunities
        opportunities = competitive_result.market_opportunities
        self.assertIsInstance(opportunities, list)
    
    @pytest.mark.asyncio
    async def test_cross_platform_business_analysis(self):
        """Test business analysis across multiple platforms."""
        platform_results = {}
        
        # Test different creator types
        test_data = {
            'influencer': self.influencer_data,
            'musician': self.musician_data,
            'business': self.business_account_data
        }
        
        for creator_type, data in test_data.items():
            result = await self.analyzer.analyze_business_metrics(
                data,
                industry=creator_type,
                cross_platform=True
            )
            platform_results[creator_type] = result
            
            # Validate cross-platform analysis
            self.assertIn('platform_performance', result)
            platform_performance = result['platform_performance']
            
            for platform in data['platform_distribution'].keys():
                self.assertIn(platform, platform_performance)
                platform_data = platform_performance[platform]
                self.assertIn('revenue_contribution', platform_data)
                self.assertIn('audience_quality', platform_data)
                self.assertIn('growth_potential', platform_data)
        
        # Business accounts should have higher revenue per follower
        business_rpf = platform_results['business']['revenue_analysis']['revenue_per_follower']
        influencer_rpf = platform_results['influencer']['revenue_analysis']['revenue_per_follower']
        self.assertGreater(business_rpf, influencer_rpf)
        
        # Musicians should have higher engagement rates
        musician_engagement = platform_results['musician']['engagement_analysis']['overall_engagement_rate']
        business_engagement = platform_results['business']['engagement_analysis']['overall_engagement_rate']
        self.assertGreater(musician_engagement, business_engagement)
    
    def test_business_metrics_data_models(self):
        """Test business metrics data model validation."""
        # Test RevenueAnalysis model
        revenue_analysis = RevenueAnalysis(
            total_monthly_revenue=8500.0,
            revenue_per_follower=0.068,
            revenue_growth_rate=12.5,
            revenue_streams={
                'sponsorships': {'amount': 5500.0, 'percentage': 64.7},
                'affiliate': {'amount': 2000.0, 'percentage': 23.5}
            }
        )
        
        self.assertEqual(revenue_analysis.total_monthly_revenue, 8500.0)
        self.assertAlmostEqual(revenue_analysis.revenue_per_follower, 0.068, places=3)
        
        # Test serialization
        revenue_dict = revenue_analysis.to_dict()
        self.assertIsInstance(revenue_dict, dict)
        self.assertIn('total_monthly_revenue', revenue_dict)
        
        # Test ROICalculation model
        roi_calc = ROICalculation(
            total_investment=12000.0,
            total_return=18500.0,
            roi_percentage=54.17,
            payback_period=8.5
        )
        
        self.assertEqual(roi_calc.total_investment, 12000.0)
        self.assertEqual(roi_calc.total_return, 18500.0)
        self.assertAlmostEqual(roi_calc.roi_percentage, 54.17, places=2)


if __name__ == '__main__':
    # Run comprehensive business metrics test suite
    pytest.main([str(Path(__file__)), '-v', '--tb=short'])
